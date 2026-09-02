---
name: af-card-tracking-code-fully-backfilled
description: AFクレカの継続中契約は全件 subscription_tracking_code が埋まり、order_code 起点の契約解決・復元は成立しない
metadata: 
  node_type: memory
  type: project
  originSessionId: b3cfb30d-657a-44f6-a8a7-6ca6c2fd3930
  modified: 2026-08-25T09:16:42.917Z
---

2026-08-25 15時台の埋め戻し（NATSCREAF-147として後付けで起票・完了）で、継続中のAFクレカ契約は全件 `user_anime_subscriptions.subscription_tracking_code` が `sub_` + ULID（30文字）で埋まった。本番実測（2026-08-25）: 継続中 73,656件 / 列が空 0件 / Nutsの契約追跡コードと直接一致 9,783件 / Nutsに契約が無い 63,873件 / 値の重複 0件。会員が復元できない契約 0件。

**Why:** 解約・強制解約の契約解決を「列が空かどうか」や入会決済の `order_code` 一致で組むと、63,873件（継続中の87%）が解決できない。Spicaは常に `sub_` の値を送るため、`order_code` を鍵にする復元Reader（Coreの `ActiveSubscriptionAgreementReader` と同型）では入会決済を引けない。

**How to apply:** クレカの契約解決・復元は `subscription_tracking_code` から継続中の契約を引き、その契約の入会決済を取る。復元契約の契約追跡コードは要求値をそのまま使う（別値だと復元後も直接一致しない）。関連: 入会FF `af_sony_payment_entry_use_nuts` は本番 2026-08-06 17:04 有効化、採番のADR-058形式への切替はNATSCREAF-133、Nuts経由分の形式揃えはNATSCREAF-137（2026-08-21）。[[nutssbpscf65-null-tracking-register-events]] [[verify-db-values-via-metabase]]
