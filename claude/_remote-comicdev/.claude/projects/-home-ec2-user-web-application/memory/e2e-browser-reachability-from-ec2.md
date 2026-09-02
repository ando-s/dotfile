---
name: e2e-browser-reachability-from-ec2
description: EC2のheadlessブラウザから dev アプリと e-SCOTT テスト環境の両方へ到達できる（2026-08-20 確認）
metadata: 
  node_type: memory
  type: project
  originSessionId: ee0aa15e-01bb-4775-9c57-f11c641720ea
  modified: 2026-08-20T07:32:31.409Z
---

2026-08-20 に Playwright MCP の headless ブラウザで確認した到達性。

- worktree スタックの dev アプリ: `https://sa2.comicdev.iowl.jp`（`APP_HOST_NAME`）へ到達。
  ローカルの listen は 80 のみだが、公開ホスト名側で TLS が終端されている。ルートは 404 で正常
- 決済代行のテスト環境 `https://www.test.e-scott.jp`: TLS 接続でき HTTP 応答が返る（ルートは 4xx）

**Why:** カード決済の E2E はトークン化が決済代行の JS SDK 依存で、HTTP の組み立てでは再現
できない。「EC2 からは決済代行に届かないだろう」という推測でブラウザ経路を諦める判断をしない
ため。

**How to apply:** カード系 E2E のブラウザ通しは Claude 側で実行できる前提で計画する。
`.env` の読取は auto mode で拒否されるので、ホスト名は
`docker inspect <web コンテナ> --format '{{range .Config.Env}}{{println .}}{{end}}'` から取る。
ブラウザ自体が起動しない場合は [[playwright-mcp-browser-install]]。
