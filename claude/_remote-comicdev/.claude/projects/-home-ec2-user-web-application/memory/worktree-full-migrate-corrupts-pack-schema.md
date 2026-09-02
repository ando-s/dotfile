---
name: worktree-full-migrate-corrupts-pack-schema
description: worktreeで db:drop/create/migrate を回すと pack のテーブルが schema.rb ダンプから欠落することがある
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 379a84ba-d0f4-4632-8b3f-0c6f59ae54b6
---

worktree の docker 環境で `rails db:drop db:create db:migrate` をフルに回して schema.rb を再生成させると、pack（例: `packs/nuts/card`）の一部テーブルが**作成されず schema.rb ダンプから欠落**することがあった。migrate:status は「up」でも実テーブルが primary に無い状態。database.yml が primary + read_replica（同一DBのレプリカ）構成であることが絡むと見られる（機序は未確認）。

**Why:** これに気づかず再生成 schema.rb をコミットすると、既存テーブル定義を消す regression を混入させる（今回 MR!16685 で register_start_events 定義を欠落させ push してしまった）。

**How to apply:**
- migration の挙動確認は、フル migrate ではなく**対象テーブルだけ用意して migration クラスを直接 up/down する隔離テスト**で行う（`Migration#migrate(:up)`/`(:down)`、`to_regclass`・`pg_indexes`・`foreign_keys` で検証）。
- schema.rb は**フル再生成に頼らず**、ブランチ先端の正しい schema.rb を基点に最小差分（renameなら該当テーブル/index/FK ＋ version 行）だけ手で当てる。
- コミット前に必ず `git diff origin/master -- db/schema.rb` で、意図した差分だけかを確認する。

関連: [[worktree-docker-test-setup]] [[worktree-verify-branch-code]] [[migration-state-talk-by-table-existence]]
