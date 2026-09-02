---
name: no-auto-review-request-label
description: MR作成時にレビュー依頼ラベルを勝手に付けない。付与はユーザーが手動で行う
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7782553b-3ac9-4488-88be-4e51ab4563d4
---

MR作成時に `Request Code Review(Nuts)` などのレビュー依頼ラベルを勝手に付けない。MR作成は「ブランチ・コミット・push・MR作成（タイトル/説明）」までに留める。

**Why:** レビュー依頼ラベルの付与はレビューを回す合図であり、ユーザーが回す準備が整ったと判断したときに自分で付ける。前回セッションでMR作成時に自動付与し、ユーザーが手動で外す手間が生じた。チーム doc `MR運用ルール.md` のラベル付与手順は「レビュー依頼フロー」の一部であって、MR作成と同時に行う操作ではない。

**How to apply:** glab/create時に `--label` でレビュー依頼ラベルを付けない。明示依頼があった場合のみ付ける。[[no-auto-reply-mr-comments]] と同じ趣旨（レビュー進行はユーザーが手動で行う）。CLAUDE.md「MR作成時の操作」にも記載。
