---
name: mr-created-as-spica-token
description: MR作成は glab（本人の個人トークン認証）で行う。create_mr.shはspica-token名義になるため使わない
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c4a3fc40-b792-43a9-a9d8-b16a73d2e093
---

MRの作成者は**本人（s-ando）名義**にする。`scripts/gitlab/create_mr.sh` は `.env` の `GITLAB_API_TOKEN`（= `spica-token` サービスアカウント）でAPIを叩くため、作成MRの作成者が spica-token になる（ブランチpushはSSH鍵＝本人なので別）。既存MRの作成者は変更不可。

**Why:** 本人がレビュー依頼者・責任者として表示されるべき。共有アカウント名義だと誰の変更か追えない。CLAUDE.mdの「MR操作: glab」規約とも整合。

**How to apply（根本解決＝採用方針）:**

- `glab` を本人の個人アクセストークン（scope: api）で gitlab.wwwave.info に認証済みにしておく（一度だけ。`glab auth login --hostname gitlab.wwwave.info`、protocolはSSH）。
- **MR作成は `glab mr create`** で行う（本人名義になる）。例:
  `glab mr create --source-branch <branch> --target-branch master --title "<title>" --description "$(cat body.md)"`
- **create_mr.sh はMR作成に使わない**（spica-token名義になる）。get_mr.sh / update_mr.sh / list_mrs.py は作成者に影響しないので可。
- 個人トークンは私が扱わない。glab auth login はユーザーが `!` で実行する。

関連: [[mr-url-bare-line]]
