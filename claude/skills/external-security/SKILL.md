---
name: external-security
description: 前の営業日の 9:30 以降のセキュリティの情報（依存の gem・npm の脆弱性、Ruby・Rails・GitLab・AWS の告知、パッケージを使った攻撃、障害）を集め、業務に関係があるか・何をするかをチャットに出す。「セキュリティ情報」「/external-security」と言われたときに使う。
---

# セキュリティ情報

セキュリティの情報を調べ、s-ando の業務に関係があるか、あるなら何をするかが一目で分かる形で、チャットに出す。質問せず最後まで進める。

## 営業日と見る期間

- 今日の日付は `TZ=Asia/Tokyo date +%Y-%m-%d` で取る
- 営業日は、土日と日本の祝日・振替休日を除いた日。祝日は `~/.claude/skills/nuts-milestone-plan/scripts/check_holidays.py` の JP_HOLIDAYS で確かめる。一覧に今日の年が無ければ自分の知識で判断し、その旨を最後に書く
- 見る期間: 前の営業日の 9:30（日本時間）から今回の実行まで。ユーザーが期間を指定したらそれに従う

## s-ando の業務（関係の判断に使う）

s-ando は決済基盤 Nuts（web-application の `packs/nuts/`）の開発者。次の実物を毎回確かめてから判断する。推測で「関係あり」にしない。

- web-application: `~/dev/spica/web-application`
  - Ruby: `Dockerfile-production` の `FROM` 行と `Gemfile.lock` の `RUBY VERSION`
  - gem: `Gemfile.lock`（Rails を含む）。件の gem が入っているか、入っていればバージョンが影響範囲か
  - npm: `package.json` と `yarn.lock` または `package-lock.json`
- 社内の GitLab（自前のサーバー）: `glab api version --hostname gitlab.wwwave.info` でバージョン
- 使っているもの: Slack、Google Workspace、Claude Code、Codex、MCP、Sentry、Datadog、Metabase、決済代行（SBPS、SonyPayment の e-SCOTT、auかんたん決済、ドコモ払い）

判断の基準:

- 対応が要る: 使っているもののバージョンが影響範囲に入っている、または使い方が条件に当たりうる
- 関係ない: 使っていない、または修正済みのバージョンを使っている
- 確かめきれないもの（使い方の条件が分からない等）は「対応が要る」に入れ、やることに「〇〇を確かめる」と書く

## 目的と取り方

目的ごとに取り方を分ける。上から順に行う。

1. 依存している gem と npm の脆弱性を漏れなく拾う。gem の脆弱性はニュースになりにくいので、記事を探さずに lock ファイルを脆弱性DBと照合する
2. Ruby・Rails・GitLab・AWS の本体の脆弱性を、公式の告知で拾う
3. 1と2で拾えない件（パッケージを使った攻撃、悪用が確認された件、障害）を、ニュースと X の反応で補う

### 1. lock ファイルの照合

`~/.slack/dep-audit.sh` を実行する。Gemfile.lock を bundler-audit（ruby-advisory-db）で、yarn.lock を yarn audit で照合し、前回の実行から新しく当たった件だけを出す。

- 1行目 `NEW <件数>` の後に、新しい件が TSV（種別・名前・使っている版・重さ・直る版・題名・URL・ID）で並ぶ
- 最後の行 `TOTAL <gemの件数> <npmの件数>` は、今回当たった全件の数
- `ERROR` で始まる行が標準エラーに出たら、照合に失敗している。「読めなかったページ」に書く

新しい件は、すべて「対応が要る」に入れる。関係する理由には使っている版と直る版を、やることには「<名前> を <直る版> に上げる」を書く。同じ gem の件はまとめて1件にする。

照合で当たった件は、2と3で同じ件を見つけても重ねて載せない。

### 2・3. 読むもの

まず次のページを直接読む（検索より優先する）:

- Rails のセキュリティの告知: https://discuss.rubyonrails.org/c/security-announcements/9
- Ruby の告知: https://www.ruby-lang.org/en/security/
- GitLab のパッチリリース: https://about.gitlab.com/releases/categories/releases/ （社内の GitLab の版より新しいセキュリティの修正が出ていれば「対応が要る」）
- AWS のセキュリティ情報: https://aws.amazon.com/security/security-bulletins/
- パッケージを使った攻撃の報告: https://socket.dev/blog
- 悪用が確認された脆弱性の一覧: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- 日本の脆弱性情報: https://jvn.jp/ と https://www.jpcert.or.jp/
- 障害情報: https://health.aws.amazon.com/health/status 、https://status.cloud.google.com 、https://status.gitlab.com 、https://slack-status.com 、https://www.google.com/appsstatus/dashboard/
- Claude Code の更新: https://code.claude.com/docs/en/changelog （セキュリティの修正だけ拾う）

次に、X 上の反応を grok CLI で集める:

```
grok -p "直近の期間（<見る期間>）に X で話題になったセキュリティの件を、Ruby・Rails・npm・GitLab・Slack・AIエージェント・決済の順に挙げ、各件の元の発表の URL を添えて" --output-format plain
```

- grok で見つけた件は、公式の発表か元の記事で裏を取れたものだけ載せる
- 足りない区分だけ Web 検索で補う。公開日を記事の中で確かめてから載せる

## 書き方

- 一読で「関係あるか」「何をするか」が分かることを優先する。件の詳しい説明は書かず、リンクに任せる
- 事実だけを書き、「危険」「致命的」などの強調語を使わない。確認できないことは「未確認」と書く
- Markdown で書く。リンクは `[見出し](URL)`

## 返答の形

1. 1行目: 「セキュリティ情報 YYYY-MM-DD（対象期間）　対応が要るもの N件」
2. 「対応が要るもの」: 1件ずつ、次の3行で書く。無ければ「対応が要るものなし」の1行だけにする
   - **件名** と参照のリンク1つ
   - 関係する理由: 確かめた実物とその値（例: Dockerfile-production が ruby:3.4.11、影響は 3.4.12 未満）を1文で
   - やること: 番号付きで1〜3個。誰が何をするかが分かる動詞で書く
3. 「関係ないもの」: 1件1行で `[件名](URL)` と、関係ない理由を10字ほどで（例: 使っていない、19.4.2 で修正済み）
4. 「lock ファイルの照合」: `TOTAL` の値を「残っている件 gem N件・npm N件（新しい件を含む）」の1行で書く
5. 「読めなかったページ」: 接続できなかった URL と、照合の失敗（無ければ書かない）
6. 祝日を自分の知識で判断したときは、その旨
