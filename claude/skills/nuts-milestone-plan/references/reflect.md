# 反映の手順（コマンド）

一時ファイルは `$CLAUDE_JOB_DIR/tmp`（無ければ `/tmp` 配下の作業ディレクトリ）に置く。スプレッドシートの読み書きは Google スプレッドシートのコネクタ（`get_values`・`update_values`・`append_values`）で行う。

## HTML の検査と配布

正本: `~/Documents/nuts/スケジュールの計画/Nuts移行_マイルストーン計画.html`

1. 描画の確認（ブラウザは file:// を開けないので playwright を使う。別プロジェクトの node_modules を借りる）

```bash
NODE_PATH=/Users/s-ando/gyomu/zenn_集計/node_modules node scripts/check_render.js "<正本のパス>"
```

`bars`・`keyedBars`・`matrixHits`・`items` の件数、帯・図・項目一覧を押したときのパネルの題名、根拠タブで見える見出し、`phone overflow: false`、`errors: []` を見る。

2. Artifact 用ファイルと Downloads 用コピーを作る

```bash
python3 -I scripts/build_outputs.py "<正本のパス>" "<一時ディレクトリ>/milestone-plan.html"
```

Artifact 用は外側の `<!doctype>/<html>/<head>/<body>` を外し、`<title>` の直後に `<meta name="claude:viewport-fit-sides" content="cover">` を足したもの。これを `Artifact` ツールで `file_path` に渡して公開する（URL は https://claude.ai/artifact/LYhTzR1KmusBCA4AFzQram。同じ会話で公開済みでなければ `url` を渡し、先に `action: read` で読む）。

3. Drive の HTML（`1ztkBn8xCwtmb5zq8Xi0mJgKOQTpGLauj`、共有ドライブ）を差し替える

コネクタは既存ファイルの中身を差し替えられないので、同じ名前で作り直す（2026-11-02 からこの方式）。

正本が大きいとき（目安 100KB 超。時点が 3 つ以上）は、`create_file` に全文を載せられない（出力の上限）。そのときは作り直さず、`build_outputs.py` が置く `~/Downloads/Nuts移行_マイルストーン計画.html` を、ユーザーがドライブのフォルダの同名ファイルにドラッグして置き換える（ID は変わらない）。返答でそのことを伝える。

1. 正本を `Read`（`allow_large`）で読み、Google ドライブのコネクタ `create_file` に `title: "Nuts移行_マイルストーン計画.html"`、`parentId: 1AATSM5Qp43O4RimEHg9zxrDAzDuwoXFn`、`contentMimeType: text/html`、`disableConversionToGoogleType: true`、`textContent: <正本の全文>` で作る。返ってきた `fileSize` が正本の `wc -c` と同じことを確かめる
2. 古いファイルを `trash_file` でゴミ箱へ移す
3. 新しい `id` を、この文書の見出し 3 と SKILL.md の「場所」の表に書き換える（`sed -i '' 's/<旧ID>/<新ID>/g'`）。README（Google ドキュメント）と HTML の運用方法はファイル名とフォルダで指しているので直さない

## Jira（NTMS の開始日・期日）

現在値の確認（`jira issue list --raw` はカスタム項目を返さないので 1 件ずつ `view`）。

```bash
jira issue view NTMS-37 --raw | python3 -I -c 'import sys,json; f=json.load(sys.stdin)["fields"]; print(f.get("customfield_10015"), "->", f.get("duedate"))'
```

更新は `mcp__jira__update_issue`（`issueKey`, `startDate`, `dueDate`。`null` で消す）。題名の変更が自動モードで止められたら `jira issue edit KEY -s "<題名>" --no-input`。削除は `mcp__jira__delete_issue`（子課題・リンクが無いことを `view --raw` で確かめてから、ユーザーの明示の指示があるときだけ）。

Jira に書くのは見積もりの日付だけ。リスクは `_メモ` と方針行に書く。

## エピック（決済手段ごと）

マイルストーンの枠（担当・期間）が決まったら、決済手段固有のエピック（登録・解約・手動強制解約・コース移行・継続課金決済・都度課金・返金）に開始日・期日を置く。運用系（レポート・検知・問い合わせ・障害対応）は具体化するまで置かない。

- 各プロジェクトのエピックと子は `mcp__jira__get_issues_by_project`（期限・親・SP が取れる）で集める。プロジェクト: NUTSAUCF / NUTSSBPSCF / NATSCRECF / NUTSDCCF / NUTSATNCF / NUTSPPCF
- 順序は AF の実績（登録 → 解約・強制解約 → 都度課金 → コース移行 → 継続課金 → 返金）。コース移行は継続課金決済の切替と同時かそれより前。継続課金決済の切替は、その手段の月次の課金（1 日固定の手段は翌月 1 日）に間に合う日に置く
- 長さは枠を割って置くだけでは検査にならない。独立した物差しとして AF の実績（NATSCREAF・NUTSDCMAF・NUTSAUAF・NUTSAFSBPS のエピックの開始→期日）で積み上げ、枠と比べる。切替だけの機能は AF の半分、CF にしか無い機能（都度課金・コース移行）は新規として見る。枠より大きい手段は、人に分ける・約束を後ろに置くの案を出す
- 2026-10-22 の結果: PayPay は余裕、d払い・SBPS は余裕なし、クレカ・atone は枠より大きい。鈴木さんはクレカ（都度課金・コース移行込み、11/4〜2/26）から入り、PayPay（au の都度課金の土台の上に作る）を後にした
- 順序を組み替えたときは、コース移行が継続課金決済の切替より前にあるか、新規実装が依存する土台（au の都度課金）が先にできているかを見る
- 親の無いタスク（カットオーバー・STG デバッグなど）は `parentKey` でエピックにぶら下げる（ガント：エピックで「（エピックなし）」に落ちないように）
- 統合シートの「プロジェクト」シートで、その手段の行の「有効」を TRUE にする（BOARD_ID・ISSUE_TYPES は空で既定）。`設定` の `RANGE_TO:エピック` が期間を覆っているか見る
- HTML の JSON の `epics` にキーごとの `[エピック, 期間]` を書く（パネルの末尾に出る）

## `_方針`（週の方針行）

- キーは `週:yyyy-MM-dd`、週は **火曜始まり**（例 2027-06-15 は火曜。6/14 で書くと別の週になる）。区間は `M/d〜M/d`
- 列は A=キー、B=区間、C=文。1 行目は見出し
- HTML には方針行の文を置かない。計画のページ（担当・期間・順序の理由・4 の表）から週ごとの文を作り、ユーザーに見せてから書く。11/3 の週は既存文「業務委託受け入れ準備」を先頭に残す
- 既存の行を読んでから、同じキーの行は上書き、無いキーは追記する。古い週の行を消さない

- 読む: `get_values`（spreadsheetId `1PvTSmnE_not_5XseWG6pYBYZBOUXJ6ZHjfEyf2PVy5M`、range `_方針!A1:C60`）
- 書く: `update_values`（range は例 `_方針!A12:C20`、値はそのまま入れる RAW）

## `_メモ`（KEY ごとのメモ）

- 列は A=KEY、B=本文。KEY はエピックキーか、プロジェクトの見出しなら表示名（「マイルストーン」）
- 1 つの KEY のメモは「その日に決めたこと」を `M/D` の見出し 1 つにまとめ、2〜3 文に収める（担当・期間・順序の理由・未決）。同じ日に何度も見直したときは追記せず、その日の段落を書き直す。前の日の段落は残す。文は句点ごとに改行する（`re.split(r'(?<=。)', text)`）
- 書くのは担当・期間の根拠・リスク・未確認。前の案で書いた段落が今の案と矛盾するなら、その段落は消してよい
- 無い KEY は `values append`（`insertDataOption: INSERT_ROWS`）で足す
- 「ガント：エピック」「ガント：タスク単位」の見出し行にも同じ方針を出すため、NTMS のメモを対応するプロジェクトの表示名キーに写す（先頭に `【マイルストーン NTMS-xx】`）。対応: CF au←39、CF SBPS←35、AF d払い←36、AF SonyPayment←42、CF d払い←37、CF SonyPayment←43、CF Atone←44、CF PayPay←45。表示名は「プロジェクト」シートの列と一致させる。NTMS 側を書き換えたら写し直す（自動では連動しない）

- 読む: `get_values`（range `_メモ!A1:B120`）
- 書く: 既存の行は `update_values`（range は例 `_メモ!A37:B51`、RAW）。無い KEY は `append_values`（range `_メモ!A1:B`、RAW、行を挿入する指定）

## `_計画`（プロジェクト見出しの計画行）

ガントの各シートのプロジェクト見出しの下の「計画」行（開始・終了）は `_計画` シートに `#表示名` のキーで保存され、描き直すとそこから出る。列は KEY・番号・開始・終了・固定日。見直しのたびに番号を +1 した行を `values append` で足す（前の行は固定した計画として残る）。

- マイルストーン: `#マイルストーン` = 移行全体（例 2026-10-13〜2027-06-30）
- 決済手段のプロジェクト: `#CF SBPS` など、NTMS のエピックと同じ期間
- 深川さんが自分で置いた `#CF au` のような行は上書きしない（詳細計画の持ち主が直す）
- 描き直す前にシートの見出し行に直接書いてもよいが、保存の操作で `_計画` に写るのはシート側の値なので、両方を揃えておく

## `設定`

`RANGE_TO:マイルストーン`（B18 付近）を約束の日に合わせる（例 `2027-06-30`）。行は `設定!A1:C40` を読んで探す。

## 計画文書の MR（web-application）

ローカルで編集しない。Herdr のペインを右に割って comicdev に入り、worktree で claude を起動して指示書を渡す（`~/dev/dotfile/claude/docs/web-application-workspace.md`）。

1. `herdr pane split --current --direction right --no-focus` → `pane_id` を控える → `herdr pane rename <id> comicdev` → `herdr pane run <id> "ssh comicdev"`
2. `herdr pane run <id> "git fetch -q origin && git worktree add ../web-application-<用途> -b nuts/docs/<TICKET>-<slug> origin/master && cd ../web-application-<用途> && claude"`。既存ブランチなら `cd` だけ
3. 指示書を Markdown に書いて `scp -o RemoteCommand=none <file> comicdev:/home/ec2-user/<name>.md` で置き、`herdr pane run <id> "<path> を読んでそのとおりに進めてください"`
4. 完了待ちは `herdr pane wait-output <id> --regex '<報告に出る語>' --source visible --timeout 900000`。指示文に同じ語があると即時に一致するので、報告だけに出る語にする。確実なのは ssh で `git fetch && git rev-parse origin/<branch>` を 30 秒おきに見るループ
5. 指示書に書くこと: 対象ファイル、決定の内容と理由（制約だけ）、書き換える箇所、書き方、コミット文、MR の作り方。**ラベル（`Request Code Review(Nuts)` など）とレビュアーは付けない**。説明の末尾は `🤖 Generated with [Claude Code](https://claude.com/claude-code)`

ペインが消えていたら `herdr pane read` が `pane_not_found` を返す。立て直して指示を渡し直す（worktree は残っている）。

## 描き直しの案内

`_メモ`・Jira を直接書いたので、ガント：マイルストーンのシートはメニューから描き直すまで古い。描き直す前にシート側で保存の操作をすると、シートに無いメモが消える可能性があることも伝える。
