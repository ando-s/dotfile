---
name: tech-pr-check
description: 技術広報の状況を確認する。定期実行（Zenn・note の集計、採用サイト遷移、技術広報ダッシュボード）が更新できているか、ダッシュボードと集計シートの数値が合っているか、PV・GA の数値に異常がないかを点検し、技術広報のチャットスペースとドライブ 06_技術広報 の直近の動きをまとめる（チャットスペースは読めない）。「技術広報の状況確認」「ダッシュボード更新できてる？」「数値チェック」「技術広報どうなってる」と言われた時、MT の前に使用。
---

# tech-pr-check

読むだけのスキル。シート・チャット・ドライブには書き込まない。

## 実行

スプレッドシートとドライブは Google のコネクタで読む。

### 数値の点検

1. 読む範囲を出す

```bash
python3 -I ~/.claude/skills/tech-pr-check/scripts/check.py ranges
```

2. 範囲ごとにスプレッドシートのコネクタの `get_values` で読み、返った JSON（`{"values": [...]}`）を `<scratchpad>/tech-pr-check/<キー>.json` に書く。互いに独立なので並べて呼ぶ
3. 点検する

```bash
python3 -I ~/.claude/skills/tech-pr-check/scripts/check.py <scratchpad>/tech-pr-check
```

定期実行の最終更新、ダッシュボードと集計シートの突き合わせ、直近7日と前の7日の数値、今月の公開記事を出す。最後の「要確認」に問題を出す（問題があれば終了コード1）。

- 日次のシート（ブログ_日次・GA_日次）は 2023/07/01 から1日1行の並びを前提に、直近45日の行だけを読む。並びが崩れているとスクリプトが止まるので、そのときは `DAILY_BASE` を見直す
- Zenn の data は記事ごと・日ごとの行で、日付と PV の2列を全部読む。行が増えると読む量も増える

### ドライブの動き

ドライブのコネクタの `search_files` で、06_技術広報 の中で直近に更新されたファイルを探す。日数の既定は7。前回の MT からを見たいときは、MT の日からにする。

```
parentId = '1K4ZNt3EjJ3G4PQQMr8Ly0ossOf64mtts' and modifiedTime > '<日時 RFC 3339>'
```

### チャットスペース

Google Chat を読むコネクタが無いため、読めない。報告には「チャットスペースは未確認」と書き、気になる動きがあればユーザーに貼ってもらう。

## 報告の形

結論を先に、3〜5行で返す。そのあと見出しごとに箇条書き。

1. **⚠️ 要確認**（あるときだけ先頭に）: 「要確認」の各行と、まず見るところ
   - 定期実行が止まっている: `~/gyomu/定期実行の状況/jobs.json` の `check` 欄（ログの場所・GAS の実行数の URL）
   - GA の数値が急に減った: サイトを閉じていた（障害・脆弱性への対応など。2026/10/22〜10/28 は php2shell の影響で採用サイトを閉じていた）、採用サイト側の計測タグ・GA の設定の変更、データの反映待ち（直近2日は GA の値が後から増えることがある）のどれかを、未確認として挙げる。1つに決めつけず、週次レポートのメモ列に理由が書かれていないかも見る
2. **定期実行**: 4件の状態を1行ずつ
3. **数値**: 直近7日と前の7日。大きく動いたものは、原因の候補（記事の公開日、外部での紹介など）を添える。推測は「想定」と書く
4. **ドライブ**: 更新されたファイルを1行ずつ。チャットスペースは未確認と書く
5. 必要なら次にやること

## 前提（読み違えないため）

- ダッシュボードは毎朝6時台、Zenn・note の集計は9時台に動くので、ダッシュボードは集計シートより1日遅れる。これは正常
- Zenn の PV は直近の数日が後から確定するので、突き合わせの差は「メモ」に出す。「要確認」ではない
- note の日別 PV は 2026/10/01 から、Zenn は 2026/09/15 から。それより前の比較はしない
- 応募数・カジュアル面談の件数や結果など、人事関連の数値は扱わない（ダッシュボードにも置かない方針）
- チャットへの返信や投稿は、文面を示して承認を得るまでしない。ドキュメントへの書き込みは、文面をチャットで渡してユーザーが貼る

## 参照先

- 技術広報ダッシュボード: https://docs.google.com/spreadsheets/d/1382q0DE4_Z5TyVA6LJ_XKT_0Ywj5djKbquHrTN1_YXU/edit
- zenn記事PV数: https://docs.google.com/spreadsheets/d/1bDdbM5oJELx69lf4ARygOBvpGSzV-jBLaYIXMLq6PoM/edit
- note記事PV数: https://docs.google.com/spreadsheets/d/1MpUbiXXDdMIZmiYODE94AVrDihmJzL5E6Mnb79bbQys/edit
- 定期実行の状況: https://docs.google.com/spreadsheets/d/1bYLggzIAIObohSe_W2EkHCCX4_6PpT0zMTicKJN-m-k/edit
- チャットスペース: https://chat.google.com/room/AAQAAZENTg8
- ドライブ 06_技術広報: https://drive.google.com/drive/folders/1K4ZNt3EjJ3G4PQQMr8Ly0ossOf64mtts
