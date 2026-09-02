---
name: adr-status-convention-removed
description: ADRの承認状態(Status)運用を廃止。テンプレ・既存ADRからStatus節を削除
metadata: 
  node_type: memory
  type: project
  originSessionId: 8ec7fb2a-e90d-42e5-bd84-1e7ee49cd839
---

ADRの承認状態(Status: Proposed/Accepted)運用を廃止した（MR !16721, 2026-07-09）。

**Why:** ADRはマージ時点で可決済みのため、ADR内で承認状態を管理する意味がない。承認はMRのレビューラベル（LGTM等）とマージで表現する（`MR運用ルール.md`）。

**How to apply:**
- 新規ADRに `## Status` 節を作らない。テンプレート `packs/nuts/.ai/references/templates/adr.md` からは既に削除済み。
- ADRの経緯・設計変更の履歴は残す（Statusと経緯ログは別物）。ADR-047は `## 改訂履歴` 節で保持。
- Deprecated/Superseded を示す必要が出たら、置換されたADR冒頭に一文リンクを書く（専用フィールドは設けない）。

関連: [[ubiquitous-language-table-scope]]
