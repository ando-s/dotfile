---
name: playwright-mcp-browser-install
description: Playwright MCP が動かない主因は @playwright/mcp が要求するブラウザ未インストール。install-browser で解消する
metadata: 
  node_type: memory
  type: project
  originSessionId: ee0aa15e-01bb-4775-9c57-f11c641720ea
  modified: 2026-08-20T07:32:23.840Z
---

`.mcp.json` の playwright は `--browser=chromium` 指定だが、`@playwright/mcp@latest` は
chrome-for-testing の特定ビルド（例: chromium-1237）を要求する。キャッシュに古いビルド
（1217/1232 等）しか無いと、ツール呼び出し時に "Browser ... is not installed; expected
executable at ~/.cache/ms-playwright/chromium-1237/..." で失敗する。

**Why:** MCP 側が要求するビルド番号は `@playwright/mcp` の更新で上がるため、以前動いていた
環境でも突然この状態になる。「Playwright MCP が使えない」と結論づける前にこのエラーを見る。

**How to apply:** `npx @playwright/mcp@latest install-browser chrome-for-testing` を実行して
から再度ツールを呼ぶ。ブラウザが起動すれば原因はこれ。到達性は
[[e2e-browser-reachability-from-ec2]] を参照。
