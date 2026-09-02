---
name: safety-measures-check-repo-precedent
description: 安全策を足す前にrepoの前例を数える。前例が無い足し物はレビューのノイズになるので入れない
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5199b579-bf95-4738-8875-c639b0d56872
  modified: 2026-08-10T05:08:17.919Z
---

移行や運用に安全策を足そうとしたら、先に repo の前例を数える。同じ操作を過去にどう入れてきたかを見て、前例が無い足し物なら入れない。

実例: `user_anime_subscriptions`（65.5万行）と `user_subscriptions`（285万行）への NULL 許容の列追加に `SET LOCAL lock_timeout = '5s'` を入れたが、`users`（635万行・3453 MB）への列追加は 2025/12・2026/04 とも素の `add_column` で、移行 446 個のうち `lock_timeout` を使うものは1つも無かった。より大きいテーブルで何度も素で通してきた操作だったので外した（`def up`/`def down` も `def change` に戻した）。

**Why:** 正しい対策でも、前例が無いと「なぜこの移行だけ特別なのか」をレビュアーが読み解く手間が増える。MR説明もその説明で膨らみ、本題（列を1つ足すだけ）がぼやける。

**How to apply:** 「安全だから足す」で止めず、`grep -rn <対策> db/migrate | wc -l` と、同規模テーブルへの同種の操作を実際に読む。前例が無いなら足さない。足すならその移行だけ特別扱いする理由をコメントに残す。関連: [[reversibility-over-upfront-structure]]（未要件の構造は先回りしない）
