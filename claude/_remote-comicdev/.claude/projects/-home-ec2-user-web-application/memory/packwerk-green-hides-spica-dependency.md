---
name: packwerk-green-hides-spica-dependency
description: packwerk成功でもpackage_todo.ymlの新規越境でNuts→Spica依存が入る。レビューでdiffを見る
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0e01aa5c-8fb6-4170-9542-eb6a084314d5
  modified: 2026-07-22T08:13:25.091Z
---

Nuts のMRで「packwerk 0/成功」でも Nuts→Spica 依存が入っていないとは限らない。違反を `package_todo.yml` に記録すると packwerk は通る（許容リスト方式）。

**Why:** MR!16683（クレカ入会 NATSCREAF-1）で `Nuts::Card::EntrySettlement` が `Payment::SonyPayment::EachTimeCharge`/`OrderCode`/`CreditCardError`/`RegisterAccountError`（本体 `lib/payment/sony_payment/*`＝Spica側）を直接参照していたが、`packs/nuts/card/package_todo.yml` に越境参照を記録済みで packwerk は緑だった。最初のレビューでこの依存を見落とした（ユーザー指摘で判明）。

**How to apply:**
- レビュー時は `package_todo.yml` の diff を必ず見る。新規追加された越境参照＝新しい Nuts→Spica 依存。
- クレカ provider は [[nuts-af-jira-projects-by-provider]] の NATSCREAF。決済APIクライアントは **ADR-045 で Nuts 再実装が決定**（選択肢C）。`Payment::SonyPayment::*` を丸ごとラップする案A は「Packwerk境界が崩れる」として却下済み。直接流用は ADR-045 違反として [must]。
- 許容されるのは Settings 参照のみ（`Nuts::SonyPayment::Config` 経由、ADR-040）。API・エラー型・OrderCode は Nuts 側に持つ。
- SBPS 先例: `Nuts::Sbps::SbpsClient` として再実装（`Payment::SoftbankB` をラップしない）。
- 関連: [[nuts-vocabulary-translation-at-wire]]（プロバイダ層の境界）。
- 2026-07-22: この観点をarchitectureチェックリスト（`packs/nuts/.ai/references/checklists/code-review/architecture.md`）のHighに追加（MR!16811）。controller→Spica直接依存の実例はNATSCREAF-42。
