---
name: nutssbpscf65-null-tracking-register-events
description: NUTSSBPSCF-65項目4(MR!16719)の①1709件のNULL trackingは解約済み復元契約でありゲートは④
metadata: 
  node_type: memory
  type: project
  originSessionId: c7a40c39-f474-4cc3-af15-044e32daf53b
---

NUTSSBPSCF-65 項目4（MR!16719、継続課金発行の tracking 取得元を `register_event.sbps_tracking_id` 単一参照へ切替）のマージ前確認で判明した事実。

## ①のNULL tracking 約1709件の正体

- backfill(spica-scripts!651) 後に RegisterEvent.sbps_tracking_id が NULL で残る契約＝!651 の `skipped`。「RegisterEvent あり・AuthorizeSuccessEvent なし」。
- 本番データ確認: 全て **merchant=af**、**capture なし**、**customer_unregister あり（解約済み）**、Nuts の created_at が **2025/11/20〜22 に集中**（一括復元の痕跡）。order_id 先頭の申込日時は 2022〜2025 と広い。
- 現行の復元リーダー(af/cf `subscription_restoration_reader`)は register と同時に authorize も capture も作る。これらは両方無いので、**既解約契約を register＋顧客解約イベントだけで復元した別経路（一括スクリプト、spica-scripts側・実体未確認）**の産物。
- 申込要求(register_free/仮売上なし, ADR-047)は**本番未稼働**なので出所ではない。

## item4 のマージ可否判断

- **ゲートは④＝0件**（authorize を持つ契約で authorize と register の tracking/payment_date が一致）。①の件数はゲートではない。
- 理由: authorize 無し契約の発行 tracking は旧 `authorize_success_event ‖ register_event` も新 `register_event` も同じ NULL を返す。新旧同値＝item4 は挙動を変えない。
- 1709 は全て解約済み＝`active_at` で Issue 対象外・再発行対象外（決済未発行）→ 発行されない。**確認済み: `active_null_tracking`（NULL tracking かつ未解約）=0**。
- **マージ前チェック完了（2026-07-09）: ①=解約済み復元で影響外・②=0・④=0。挙動中立を確認しマージ可。**

## 出所（1709の正体）
- register_event.created_at=元申込日時(2021〜2025/10)に遡及、agreement.created_at=2025/11〜2026/5＝復元の痕跡。現行の復元リーダー(2026-01〜)より前の、既解約af契約を「登録＋解約のみ(authorize/capture無し)」で復元した実装の産物。現行コードにこの形を作る経路は無く、復元バッチも停止済み＝増えないclosedな過去データ。

## NOT NULL化の進め方（2026-07-10 合意）
- 対象2列(sbps_tracking_id/sbps_payment_date)をNOT NULL化。順序: backfill → NOT NULL(!16732) → 参照切替(!16719)。
- 1709はSpica由来backfillで解消（spica-scripts!655、本番実行済み・残NULL=0）。authorize/captureは埋めない（YAGNI＋captureを作ると解約済み契約が手動返金対象になるため）。
- **NOT NULL MR: web-application!16732(Draft)**。change_column_null 2列＋schema版20260710。DBマイグレーション＝人間確認必須。マージ直前に両列NULL=0を再確認。
- 残: !16732マージ → !16719のDraft(`Draft: Draft:`)解除・マージ。!16719は!16732に機能依存なし(順序のみ)。

## レビュー対応（2026-07-14, MR!16719 note_739529）
- 派生MR!16732(NOT NULL)のCIで落ちるテストを!16719側で先行修正するよう依頼。worktreeのテストDBに手動でNOT NULL適用→REDを再現→修正の順で検証（!16719単独ではNOT NULL無しなのでgreenは無意味）。
- 修正① spec setup: `create_register_event!`/`build_register_event`/`RegisterEvent.new` をtrackingなしで永続化していた箇所（issue/entry query af/cf, model scope, resolver, unregister, forced_unregister）に値を補完。登録マーカー用途は`register_event_at`ヘルパ、再構築系はauthorizeと同値。
- 修正② 本番bug: **`active_subscription_agreement_reader`(af/cf)がRegisterEventをtrackingなしでbuild**。resolveで永続化されるためNOT NULL後は強制解約・解約時の契約再構築経路(SBPS契約がNuts未作成のケース)で本番INSERTが失敗する潜在バグ。全呼び出し元がreaderをstubするためテストに出ない。当初MRは「発行されないから変更しない」としていたがNOT NULLは発行有無に無関係。復元リーダー同様authorizeと同値をregisterにも保存。
- **cfはまだ本番未提供**。cf active readerには従来processed_at/tracking_code検証が無く、cf reader specの有効文脈もprocessed_at未設定(nil)。af同形の検証ガードを追加(不整合データでNotNullViolationでなくSpicaDataInconsistencyError)。cf未提供のため挙動変更の実影響なし。
- 検証: softbank全pack 1547 pass(NOT NULL適用下), rubocop/packwerk clean。commit 795f21d1f4(spec)+0b950a7d6f(reader)。MR説明も実態に更新(スコープ外からreader削除)。
- schema.rbはdocker db/rspec実行でローカルPG版ドリフトが繰り返し発生。commit前に必ず`git checkout -- db/schema.rb`。

関連: [[adr047-shift-course-nuts-notify-consistency]]（申込要求フロー）
