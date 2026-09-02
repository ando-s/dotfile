---
name: draft-note-put-drops-position
description: GitLab draft noteをPUTでnoteだけ更新するとposition(行紐付け)が消える
metadata: 
  node_type: memory
  type: reference
  originSessionId: f58cab09-8082-445c-a464-b31adbf6a60b
---

GitLab の `PUT projects/:id/merge_requests/:iid/draft_notes/:id` で `note` だけ送ると、inline下書きの `position`（`new_path`/`new_line` の行紐付け）が null に落ち、全体コメント化する。

**How to apply:** マーカー変更や本文修正で既存inline下書きを更新するときは、作成時と同じ `position` オブジェクト（base_sha/start_sha/head_sha/new_path/old_path/new_line）を毎回PUTボディに含める。更新後は `draft_notes/:id` を単体GETして `position.new_line` が残っているか確認する。関連: [[mr-url-bare-line]]、post_review_comment スキル。

POSTでの新規作成も同様: `glab api -f "position[new_path]=..."` のフォーム形式ではpositionが無視され全体コメント化する（エラーは出ない）。`-H "Content-Type: application/json" --input <jsonファイル>` でpositionをネストしたJSONボディを送ると行紐付きで作成できる（2026-07-02 MR!16637で確認）。
