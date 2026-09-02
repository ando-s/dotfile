---
name: tickets-adrs-not-binding-during-rework
description: 手戻り中の設計は、チケット記載の設計案・既存ADRに引きづられず要件から組み直す
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b15f7756-e2ea-419e-8276-6d21b33dd34b
  modified: 2026-07-29T08:39:53.102Z
---

クレカ（NATSCREAF）の設計フェーズは手戻り中で、JIRAチケットの「設計の詳細」節や既存ADRの決定は
確定事項ではない。チケットに書かれたテーブル定義・カラム・イベント構成をそのまま実装しない。

**Why:** チケットの設計案は手戻り前の前提で書かれており、要件（`packs/nuts/docs/プロジェクトマネジメント計画/要件定義.md`
のゴール1〜3、特に3=Nuts利用者の学習コスト削減）から見直すと不要な構造・誤った粒度が残っている。

**How to apply:** チケットは解こうとしている問題の説明として読む。設計は要件と現状コードから組み直し、
チケット案から外れた点は理由付きでMR説明に列挙してレビューにかける。ADRも改訂・新規起草の対象にする。

関連: [[no-carryover-force-decision]] [[domain-first-then-document]]
