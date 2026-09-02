---
name: ask-comments-reply-not-fix
description: "レビューコメントの[ask]は返信で答えるもの。コード修正で対応しない"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: da99aa2a-58eb-4de4-b8b4-8d5924a35126
---

MRレビューコメントが `[ask]`（質問・方針確認）の場合、求められているのは**回答（返信文）**であってコード修正ではない。修正に倒さず、採用方針や理由を返信文として用意する。

`[imo]` / 提案 / 指摘は、必要性を見極めた上でコード修正の対象になりうる。マーカーで対応種別を切り分ける。

**Why:** NUTSAFSBPS-401 の MR16370 で、Factory型チェックの方針を問う `[ask]` に対し、確認せずコード修正を入れてしまった（害はないが筋違い）。

**How to apply:** コメント本文の `[ask]` / `[imo]` 等のマーカーを見て、`[ask]` は返信文のみ用意。修正可否は別途見極める。返信の投稿はユーザーが行う（[[no-auto-reply-mr-comments]]）。
