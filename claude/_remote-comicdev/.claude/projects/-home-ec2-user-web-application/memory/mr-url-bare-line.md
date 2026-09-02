---
name: mr-url-bare-line
description: MR作成後は素のURLを単独行で出力する（コピー・クリックしやすくするため）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7fef4f2f-b3da-4ccc-9ce6-c296144af2cb
---

MR（マージリクエスト）を作成したら、その URL を**他の文字を含めず単独行で**出力する。`[text](url)` 形式やカッコ書き・末尾句点を付けない。

**Why:** ユーザーがURLをコピーするのが手間。素のURL1行ならターミナルでクリック／ドラッグ選択しやすい。

**How to apply:** MR作成の直後に、報告文とは別に URL だけの行を1つ置く。個人グローバル設定に PostToolUse(Bash) フック `~/.claude/hooks/notify-url.py`（旧 mr-url.py を汎用化・改名）を登録済み。検知対象は次の通り:

- MR作成: `glab mr create` / `git push -o merge_request.create` / `push_merge_request.sh` 等のラッパー（git push出力の「View merge request for」マーカーでゲート）/ `scripts/gitlab/create_mr.sh`（web_url入りJSON）。`glab mr view`・`update_mr.sh` 等の閲覧・更新は拾わない
- レビュー下書きコメント: `glab api -X POST .../draft_notes`。下書きは web_url を持たないため対象MRページURLを git remote から構築。指摘ごとに複数POSTされるので session_id 単位で既出URLを除外（`~/.claude/.url-hook-state/`）

オープナーがあれば開く（このEC2は headless なので出力のみ）。フックと私の出力の二重保険。
