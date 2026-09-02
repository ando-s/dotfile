---
name: verify-db-values-via-metabase
description: 本番DBの実値（フィーチャーフラグ・件数・状態）は Metabase MCP で確認できる。「未確認」で済ませない
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0a8052ae-c02a-4699-a28f-d4b65e37e24e
  modified: 2026-08-04T10:04:33.147Z
---

本番DBの実値を根拠にしたいときは Metabase MCP（`mcp__metabase__execute_sql` 等）で引く。コードだけ読んで「本番の値は未確認」と書いて終わらせない。

例: フィーチャーフラグの実値は `nuts_feature_flags` の `key` / `is_enabled` を引く（`af_sony_payment_entry_use_nuts` 等）。

**Why:** 「FF が OFF なら影響なし」のような結論は、実値を引かないと条件付きの推測にとどまる。Metabase から読めるものを推測のまま残すのは手を抜いているのと同じ。

**How to apply:** 影響範囲の説明で「本番の設定値次第」と書きたくなったら、その場で Metabase を引いて実値を添える。読み取りだけなので確認を待たずに実行してよい。関連: [[nuts-spica-migration-query]]（移行運用のクエリ組み立て）
