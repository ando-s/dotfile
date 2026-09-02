---
name: nuts-dualwrite-writer-transitional
description: Nuts dual-writeパターンで副作用がトランザクション内・write_to_spica!前に置かれるのが許容される理由
metadata: 
  node_type: memory
  type: project
  originSessionId: d552606f-62a8-4641-abaa-ecf11b79bc24
---

Nuts dual-writeパターン（ADR-042/047, SBPS・au共通）のレビュー判断。

register系Controllerは1トランザクション内で `record/register!` → `notify_nuts_merchant`（=Spica callback。契約作成＋メール/広告/入会ボーナス等の副作用） → `write_to_spica!`（会員決済 `UserAnimePayment` のdual-write）を実行する。副作用がトランザクション内かつ `write_to_spica!` より前に置かれる。

**Why 許容:**
- notify到達＝Nuts側 register!（ContBill/authorize）成功＝決済成立済み。通知時点でメール送信は実態と矛盾しない。
- `write_to_spica!` 失敗で巻き戻るのはSpica側の記録（会員決済レコード）だけ。実課金は成立済みで、取りこぼしはリカバリで埋める対象。
- `write_to_spica!`（Writerのdual-write）は暫定。将来削除され、最終形では notify（Nuts利用者側＝Spica callback）が終端処理になるため、「副作用がwrite_to_spica!より前」の窓は構造上消える。
- SBPS softbank2で既に本番稼働（同一構造）。au固有の欠陥ではない。

**残る論点（未対応でOK）:** マイクロサービス化後、notifyのレスポンス（Spica→Nuts）タイムアウト時の成否不定。プロセス内呼び出し（InternalApiClient）の現状では起きない。コード中のNOTE（Nutsから送られてきたことの検証）と合わせマイクロサービス化時に扱う。

関連: [[worktree-mr-review-flow]]
