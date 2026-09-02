---
name: pending-review-learnings-dedup
description: 【未対応TODO】MR16370マージ後にレビュー学びの重複を追加コミットで整理する
metadata: 
  node_type: memory
  type: project
  originSessionId: 5faefcc2-6052-4047-88cd-231aacca002c
---

**前提**: MR16376（レビュー学び導線、`code-review-patterns.md`へ集約＋スキル導線＋review-update重複マージ手順）は 2026-06-03 master へマージ済み。MR16370（登録capture救済の機能本体）は学び系docを含んだまま凍結中（fukagawaレビュー待ち）。

**問題**: 16370がマージされると、16370と16376が独立に記録した学びが重複・矛盾する（gitコンフリクトはしないが意味的に不整合）。
- `review-update/SKILL.md`: 「rule/pattern/checklistの両方に反映」(16370)と「code-review-patternsに集約、散らさない」(16376)の逆方針が共存
- 単一EXISTS学び: `nuts-query-object.md`(16370) と `code-review-patterns.md`(16376) に二重
- parse学び: `batch-processing.md`(16370) と `code-review-patterns.md`(16376) に二重
- `reliability.md` の単一EXISTS項目も二重

**How to apply（16370マージ後に追加コミットで実施）**: 16376の「具体的学びはcode-review-patterns.mdに集約」方針に統一する。16370由来の以下を削除 — nuts-query-object.mdの単一EXISTS節 / reliability.mdの該当項目 / batch-processing.mdのparse追記 / review-update SKILL.mdの矛盾する「両方に反映」行とrules・patterns行。`packs/nuts/.ai/`を編集し sync-context.py 実行。コミットメッセージに上記の重複解消理由を明記する。関連: [[no-auto-reply-mr-comments]] [[worktree-verify-branch-code]]
