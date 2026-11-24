# 技術広報の定期実行と数値を点検して、結果をテキストで出す。シートには書き込まない。
# スプレッドシートは Claude がコネクタで読み、範囲ごとに <キー>.json として置いたものを読む。
# 読むのは各スプレッドシートの値だけ。人事関連の数値（応募・面談）は読まない。
import datetime as dt
import json
import sys

DASHBOARD = "1382q0DE4_Z5TyVA6LJ_XKT_0Ywj5djKbquHrTN1_YXU"
ZENN = "1bDdbM5oJELx69lf4ARygOBvpGSzV-jBLaYIXMLq6PoM"
NOTE = "1MpUbiXXDdMIZmiYODE94AVrDihmJzL5E6Mnb79bbQys"
JST = dt.timezone(dt.timedelta(hours=9))

# 名前, 許容時間, 実行時刻の説明
JOBS = {
    "dashboard": ("技術広報ダッシュボード（GAS）", 26, "毎日 6時台"),
    "zenn": ("Zenn の PV・いいね（Mac の launchd）", 36, "毎日 9:00"),
    "note": ("note の PV・スキ（Mac の launchd）", 26, "毎日 9:10・21:10"),
    "recruit": ("Zenn→採用サイトの遷移（GAS）", 26, "毎日 7時台"),
}


# 日次のシート（ブログ_日次・GA_日次）は 2023/07/01 から1日1行。直近の行だけを読む
DAILY_BASE = dt.date(2023, 7, 1)
DAILY_DAYS = 45


def daily_rows(sheet, cols, today):
    start = today - dt.timedelta(days=DAILY_DAYS)
    r1, r2 = 2 + (start - DAILY_BASE).days, 2 + (today - DAILY_BASE).days
    return f"{sheet}!A{r1}:{cols}{r2}"


def ranges(today):
    """読む範囲。キーが入力ディレクトリの <キー>.json になる"""
    return {
        "settings": (DASHBOARD, "設定!A:B"),
        "zenn_hist": (ZENN, "更新履歴!A:A"),
        "note_hist": (NOTE, "更新履歴!A:A"),
        "recruit_updated": (ZENN, "採用サイト遷移!G1"),
        "recruit": (ZENN, "採用サイト遷移!A:C"),
        "blog_head": (DASHBOARD, "ブログ_日次!A1:L1"),
        "blog": (DASHBOARD, daily_rows("ブログ_日次", "L", today)),
        "ga_head": (DASHBOARD, "GA_日次!A1:K1"),
        "ga": (DASHBOARD, daily_rows("GA_日次", "K", today)),
        "zenn_data": (ZENN, "data!D:E"),
        "note_date": (NOTE, "data!A:A"),
        "note_pv": (NOTE, "data!E:E"),
        "followers": (DASHBOARD, "フォロワー_記録!A:C"),
        "articles": (DASHBOARD, "記事!A:G"),
    }


INPUT = None


def values(key):
    with open(f"{INPUT}/{key}.json", encoding="utf-8") as f:
        return json.load(f).get("values", [])


def with_head(head_key, key, today):
    """日次のシートの直近の行に見出し行を付ける。行の位置が日付とずれていたら止める"""
    rows = values(key)
    expected = today - dt.timedelta(days=DAILY_DAYS)
    first = parse_d(rows[0][0]) if rows and rows[0] else None
    if first != expected:
        raise SystemExit(f"{key}: 先頭の行の日付が {first}（{expected} のはず）。1日1行の並びが崩れている。DAILY_BASE を見直す")
    return values(head_key)[:1] + rows


def num(v):
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return None


def parse_dt(s):
    for f in ("%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M"):
        try:
            return dt.datetime.strptime(s.strip(), f).replace(tzinfo=JST)
        except ValueError:
            pass
    return None


def parse_d(s):
    try:
        return dt.datetime.strptime(s.strip(), "%Y/%m/%d").date()
    except (ValueError, AttributeError):
        return None


def col(rows, name):
    return rows[0].index(name)


def by_date(rows, date_col, value_col):
    di, vi = col(rows, date_col), col(rows, value_col)
    result = {}
    for r in rows[1:]:
        if len(r) <= max(di, vi):
            continue
        d, v = parse_d(r[di]), num(r[vi])
        if d and v is not None:
            result[d] = result.get(d, 0) + v
    return result


def main():
    now = dt.datetime.now(JST)
    today = now.date()
    problems, notes = [], []

    # ---- 定期実行の最終更新 ----
    settings = dict((r + ["", ""])[:2] for r in values("settings"))
    zenn_hist = values("zenn_hist")
    note_hist = values("note_hist")
    recruit = values("recruit")
    recruit_updated = values("recruit_updated")
    last = {
        "dashboard": parse_dt(settings.get("最終取得日時", "")),
        "zenn": max(filter(None, (parse_dt(r[0]) for r in zenn_hist[1:] if r)), default=None),
        "note": max(filter(None, (parse_dt(r[0]) for r in note_hist[1:] if r)), default=None),
        "recruit": parse_dt(recruit_updated[0][0]) if recruit_updated and recruit_updated[0] else None,
    }
    print("## 定期実行")
    for key, (name, allow, when) in JOBS.items():
        t = last[key]
        if t is None:
            state = "取得できない"
            problems.append(f"{name}: 最終更新を読めない")
            print(f"- {name}: 取得できない（{when}）")
            continue
        hours = (now - t).total_seconds() / 3600
        state = "正常" if hours <= allow else "停止"
        if state == "停止":
            problems.append(f"{name}: 最終更新 {t:%m/%d %H:%M} から {hours:.0f} 時間（許容 {allow} 時間）")
        print(f"- {name}: {state}（最終更新 {t:%m/%d %H:%M}、{hours:.1f} 時間前、{when}）")

    # ---- ダッシュボードの中身 ----
    blog = with_head("blog_head", "blog", today)
    ga = with_head("ga_head", "ga", today)
    zenn_data = values("zenn_data")
    note_data = [[d[0] if d else "", p[0] if p else ""] for d, p in zip(values("note_date"), values("note_pv"))]

    blog_zpv = by_date(blog, "日付", "ZennPV")
    blog_npv = by_date(blog, "日付", "notePV")
    src_zpv = by_date(zenn_data, "PV発生日", "PV数")
    src_npv = by_date(note_data, "日付", "PV数")

    print("\n## ダッシュボードと集計シートの突き合わせ（直近14日）")
    # ダッシュボードは6時台、Zenn・note の取得は9時台なので、ダッシュボードは集計シートより1日遅れる
    lag_ok = {max(src_zpv, default=None), max(src_npv, default=None)}
    for label, dash, src in (("Zenn PV", blog_zpv, src_zpv), ("note PV", blog_npv, src_npv)):
        diffs, missing = [], []
        for i in range(1, 15):
            d = today - dt.timedelta(days=i)
            if d not in src:
                continue
            if d not in dash:
                if d not in lag_ok:
                    missing.append(d)
                continue
            if abs(dash[d] - src[d]) >= 1:
                diffs.append(f"{d:%m/%d} ダッシュボード {dash[d]:.0f} / 集計シート {src[d]:.0f}")
        src_last = max(src, default=None)
        dash_last = max(dash, default=None)
        print(f"- {label}: 集計シートは {src_last:%m/%d} まで、ダッシュボードは {dash_last:%m/%d} まで")
        if missing:
            problems.append(f"{label}: 集計シートにあるのにダッシュボードに無い日 " + "、".join(f"{d:%m/%d}" for d in missing))
        # 直近の日は Zenn が数日かけて値を確定させるため、差は「メモ」に留める
        for x in diffs:
            notes.append(f"{label} の値の差: {x}（ダッシュボードの取得後に集計シートが更新された可能性）")

    ga_dates = [parse_d(r[0]) for r in ga[1:] if r]
    ga_last = max(filter(None, ga_dates), default=None)
    print(f"- GA_日次: {ga_last:%m/%d} まで")
    if ga_last is None or (today - ga_last).days > 2:
        problems.append(f"GA_日次: 最終日が {ga_last}（2日以上前）")

    # ---- 数値のサマリ ----
    def window(series, start, end):
        return sum(series.get(start + dt.timedelta(days=i), 0) for i in range((end - start).days + 1))

    # 確定している日（集計シートの最終日）を基準に、直近7日と前の7日を比べる
    end = min(filter(None, [max(src_zpv, default=None), max(src_npv, default=None)]))
    cur_s, prev_e = end - dt.timedelta(days=6), end - dt.timedelta(days=7)
    prev_s = prev_e - dt.timedelta(days=6)

    zlikes = by_date(blog, "日付", "Zennいいねの増分")
    nsuki = by_date(blog, "日付", "noteスキ")
    visits = by_date(ga, "日付", "採用サイト訪問")
    tech = by_date(ga, "日付", "技術発信からの訪問")
    ai = by_date(ga, "日付", "AI経由の訪問")
    hops = {}
    for r in recruit[1:]:
        d = parse_d(r[0]) if r else None
        if d and len(r) > 2 and num(r[2]) is not None:
            hops[d] = hops.get(d, 0) + num(r[2])

    print(f"\n## 数値（直近7日 {cur_s:%m/%d}〜{end:%m/%d} と、その前の7日）")
    for label, s in (("Zenn PV", src_zpv), ("note PV", src_npv), ("Zenn いいねの増分", zlikes), ("note スキ", nsuki),
                     ("採用サイト訪問（GA）", visits), ("技術発信からの訪問（GA）", tech), ("AI 経由の訪問（GA）", ai),
                     ("Zenn→採用サイトの遷移", hops)):
        a, b = window(s, cur_s, end), window(s, prev_s, prev_e)
        print(f"- {label}: {a:,.0f}（前の7日 {b:,.0f}）")

    zero_days = [d for d in (cur_s + dt.timedelta(days=i) for i in range(7)) if src_zpv.get(d, 0) == 0]
    if zero_days:
        problems.append("Zenn PV が 0 または無い日: " + "、".join(f"{d:%m/%d}" for d in zero_days))

    # GA は計測タグが外れると 0 が続く。前の28日の1日平均が20以上あるのに、直近7日で平均の2割を切る日が2日以上あれば知らせる
    for label, s in (("採用サイト訪問（GA）", visits), ("求人一覧訪問（GA）", by_date(ga, "日付", "求人一覧訪問"))):
        base = [s.get(end - dt.timedelta(days=i), 0) for i in range(7, 35)]
        avg = sum(base) / len(base)
        low = [d for d in (cur_s + dt.timedelta(days=i) for i in range(7)) if s.get(d, 0) < avg * 0.2]
        if avg >= 20 and len(low) >= 2:
            problems.append(f"{label}: 前の28日は1日平均 {avg:.0f} なのに、" + "、".join(f"{d:%m/%d}（{s.get(d, 0):.0f}）" for d in low)
                            + " が平均の2割未満。計測タグや GA の設定を確認")

    top = sorted(src_zpv.items())[-30:]
    if top:
        peak = max(top, key=lambda x: x[1])
        print(f"- 直近30日の Zenn PV の最大: {peak[0]:%m/%d} の {peak[1]:,.0f}")

    fol = values("followers")
    if len(fol) > 1:
        f_last, f_first = fol[-1], fol[1]
        print(f"- フォロワー: Zenn {f_last[1]}、note {f_last[2]}（{f_first[0]} は Zenn {f_first[1]}、note {f_first[2]}）")

    arts = values("articles")
    month = today.strftime("%Y/%m")
    this_month = [r for r in arts[1:] if len(r) > 2 and r[1].startswith(month)]
    print(f"- 今月（{month}）の公開: {len(this_month)} 本")
    for r in this_month:
        print(f"  - {r[1]} {r[0]} {r[3]}「{r[2]}」 いいね・スキ {r[6] if len(r) > 6 else ''}")

    print("\n## 要確認")
    print("\n".join(f"- {p}" for p in problems) if problems else "- なし")
    if notes:
        print("\n## メモ")
        print("\n".join(f"- {n}" for n in notes))
    return 1 if problems else 0


if __name__ == "__main__":
    # python3 check.py ranges      読む範囲を JSON で出す
    # python3 check.py <入力ディレクトリ>  読んだ値（<キー>.json）から点検する
    if sys.argv[1:2] == ["ranges"]:
        print(json.dumps({k: {"spreadsheetId": sid, "range": rng} for k, (sid, rng) in ranges(dt.datetime.now(JST).date()).items()},
                         ensure_ascii=False, indent=1))
        sys.exit(0)
    INPUT = sys.argv[1]
    sys.exit(main())
