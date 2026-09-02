---
name: nuts-orchestration-in-controller-not-lib
description: Nutsのリクエスト駆動フローのオーケストレーションはcontroller。libにサービスクラスを置かない
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0e01aa5c-8fb6-4170-9542-eb6a084314d5
---

Nuts では同期リクエスト駆動フロー（authorize→capture→register + Spica書込 等）の**オーケストレーションは controller（ユースケース層）が持つ**。lib にオーケストレーション用サービスクラス（`*Settlement`/`*Interactor`/`.call`）を置く設計は存在しない。

**根拠（先例）:**
- `Nuts::Softbank::SubscriptionPayments::CaptureController#capture_payment`: controller が `@sbps_client.capture(...)` を呼び、`ActiveRecord::Base.transaction` でイベント記録＋Spica書込を組み立てる。
- `Api::SubscriptionAgreement::ForcedUnregisterController#create`: 検証→`ensure_*!`→TX{イベント記録+Writer}→レスポンス。Spica書込は Repositories の Writer 委譲。
- controller から lib サービスを `.call` する例は0件。

**lib層の役割（これ以外を置かない）:** Query オブジェクト・プロバイダ電文DTO(param/response/cgi_request)・Repositories(Writer/Reader/Restorer/Factory)・バッチクラス(`lib/.../batches/`)。バッチのフローは lib に置くが、リクエスト駆動フローは controller。

**適用:** controller が fat になる懸念は private メソッド分割で収める（SBPS 同様）。CLAUDE.md のレイヤー「Controller → Model/Resolver → ActiveRecord」と一致。関連: ADR-042（Spica書込はユースケース層=Writer）、[[packwerk-green-hides-spica-dependency]]。MR!16683 で `Nuts::Card::EntrySettlement`(lib) を controller へ移す [must] を出した。
