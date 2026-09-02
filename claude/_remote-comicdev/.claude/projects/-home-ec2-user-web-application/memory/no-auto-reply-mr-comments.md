---
name: no-auto-reply-mr-comments
description: MRレビューコメントへの返信を勝手に投稿しない（ユーザーが手動で行う）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5faefcc2-6052-4047-88cd-231aacca002c
---

GitLab MR のレビューコメント対応を依頼されても、**コメントスレッドへの返信（note投稿）は勝手にしない**。コード修正・MR説明更新までに留め、返信はユーザーが手動で行う。

**さらに、返信は「明示依頼があっても自分で送信（publish）しない」。** 「返信して」と言われても、作るのはレビュー下書き（start a review / draft）であって投稿ではない。送信・resolve はユーザーが手動で行う。絶対に publish しない。

**Why:** 2026-06-03 のMR!16370対応で、指摘2件にClaudeが自動で返信を投稿したところ「返信はしないで欲しかった、消してほしい」と指示され削除した。2026-06-24、明示依頼でも publish はダメで「絶対下書き」と再指示された（旧ルールの「明示依頼時のみ投稿」が誤り）。

**How to apply:** レビュー指摘対応では (1) コードを修正 (2) テスト追加 (3) 必要ならMR説明を更新、まで。返信は `reply_review_comment` 等で**下書き（start a review）を作るところまで**。`glab api .../discussions/.../notes -X POST`（即時publish）は使わない。送信・resolve はユーザーに委ねる。関連: [[review-comment-drafting-style]] [[ask-comments-reply-not-fix]]
