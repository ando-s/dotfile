---
name: migration-state-talk-by-table-existence
description: 移行運用のマイグレーション/DB状況は、DBの種類でなく対象テーブルの有無だけで判断・説明する
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 379a84ba-d0f4-4632-8b3f-0c6f59ae54b6
---

マイグレーションが実環境に反映されるか、rename/追加マイグレーションが必要かを判断・説明するときは、**対象テーブルが存在するかどうか**だけで語る。DBの種類（comicfesta/animefesta 等のブランド名やMetabaseのDB id）を持ち出さない。

**Why:** web-application(spica) は単一DBで AF/CF 両方の merchant を扱う（`config/settings.yml` に ComicFesta/AnimeFesta 両設定、`packs/nuts/core/app/models/nuts/core/merchant_code.rb` に AF/CF 両 MerchantCode）。「animefesta のDBは別」という枠で考えると誤る。判断に効くのは旧/新テーブルの有無だけ。

**How to apply:** ガード付き rename マイグレーションの説明は「旧テーブルがある環境だけ rename、新名で作成済み or テーブル無しの環境はスキップ」と、テーブル有無で書く。「どのブランドのDBか」は書かない。

例: MR!16685（[[nutssbpscf65-null-tracking-register-events]] と同じ NATSCREAF-1 クレカ）で create マイグレーションをin-place書き換えしたため、既適用環境に旧テーブル `n_card_subscription_agreement_authorize_start_events` が残存。旧テーブルが存在するときだけ rename する追加マイグレーションで是正。
