---
name: capture-recovery-followup-mrs
description: AF SBPS 登録capture救済 Nuts 切替の後続作業 — MR-16324 の状態、timeout 救済追加と Spica 既capture済み復元スクリプトの方針
metadata: 
  node_type: memory
  type: project
  originSessionId: bba46e40-454a-42ef-b85a-97dae48fcee1
---

登録時実売上リカバリー Nuts 切替（NUTSAFSBPS-401 / ADR-039）の後続作業ハンドオフ。前提は [[af-sbps-entry-capture-recovery-cutover]] を参照。

## 後続MR 3: リカバリー対象期間に下限＋外部指定（MR-16370, Draft, 2026-06-02）

ブランチ `nuts/feature/NUTSAFSBPS-401-entry-capture-recovery-lower-bound`（worktree同名、master起点）。Draft + `Request Code Review(Nuts)`。残: 人間レビュー（決済クリティカル）。

**Why**: `EntryCaptureRecoveryQuery` の時間条件が上限（time−GRACE）のみで遡及下限なし→何日前の未capture契約も対象化。SBPS売上確定期限（購入要求処理日を含む60日後まで／取消も同60日・返金は確定日含む400日）を超えた仮売上は capture 不可。

**実装**:
- `authorize_succeeded_after` scope 新設。対象 = `下限〜上限`。上限=`min(date_to, time−GRACE_PERIOD)`、下限=`date_from || time−DEFAULT_LOOKBACK(=1週間)`
- `date_from`/`date_to` をバッチ引数（日単位、beginning/end_of_day丸め）で外部指定可。Factory→Controller→Query へ伝搬（Factoryは entry_capture_recovery のみ date を渡す分岐）
- 上限ガード: `date_from < time−MAX_LOOKBACK(=60日)` で ArgumentError
- GRACE は date_to 指定有無によらず常にクランプ（同期capture競合防止はバイパス不可）。手動起動で date_to が直近15分に丸ごと入ると0件になる点だけ注意
- controller が有効窓 `lower..upper` を info ログ
- 起動スクリプト production/staging に任意 date_from/date_to（位置引数4,5番目）追加。ADR-039 補遺追記
- test 148 examples green / rubocop / packwerk clean

**設計判断（ユーザー確認済み）**: 下限値はSBPS仕様準拠で60日上限ガード（弾く方式）。既定窓は毎時起動前提で1週間。期間指定は「絶対日付（date_from/date_to）」を採用（lookback_days相対案から変更）。

## MR-16324（spica_captured? 削除）の状態

- ブランチ: `nuts/feature/remove-spica-captured-check`
- 直近コミット: `41afeeb751 doc(nuts): FF切替の制約セクションを復活し Nuts→Spica 手順の表記漏れを修正`（worktree `capture-recovery-research` 内）
- レビュー対応: fukagawa の 2 件（[nits]「を OFF」抜け / [ask] 制約セクション削除）を反映済み
- 残作業: 本人が push + コメント返信。コメント返信のニュアンスは「制約セクション削除は意図的でなく、`entry_capture_recovery` 追記の流れで巻き込まれた。指摘通り復活。今後の検討の構造的ガードが入るまで運用ルールで明文化」

## 後続MR 1: capture timeout 救済の Nuts 追加 — ✅ MR 作成済み（2026-05-29）

**MR-16335**（Draft, `Request Code Review(Nuts)` ラベル付）: https://gitlab.wwwave.info/comic-festa-group/web-application/-/merge_requests/16335 。ブランチ `nuts/feature/entry-capture-recovery-timeout`（worktree `entry-capture-recovery-timeout`、**master 起点**。編集ファイルは MR-16324 と非競合なので独立進行可）。テスト 75 examples 0 failures / rubocop clean（packs/nuts 340 files）。plan: `packs/nuts/plan/20260529-entry-capture-recovery-timeout.md`。残: 人間レビュー（決済整合性クリティカル）。

**Why**: 初版 `EntryCaptureRecoveryQuery` は Spica `recoverable` 条件3（capture API 未試行）のみ引き継ぎ、条件2 `FIX_TIMEOUT` 再試行が漏れていた。SBPS で売上立ってるのに timeout 応答 → Nuts に `CaptureFailureEvent` 記録 → 救済漏れリスク。

**実装した変更**（クエリ側だけで完結。当初想定の controller 変更は**不要だった**）:
- `subscription_agreement.rb` に scope `capture_recoverable` 追加 = `CaptureSuccessEvent 無し AND (sbps_error_code != TIMEOUT_ERROR の CaptureFailureEvent 無し)`。NOT EXISTS 2本。`capture_pending` は他 caller（capture_query/forced_unregister_query）のため温存。
- `EntryCaptureRecoveryQuery#call` の `.capture_pending` → `.capture_recoverable`
- spec: query spec / scope spec 双方に「timeout のみ→抽出」「非timeout→除外」「混在→除外」ケース追加
- ADR-039 に「補遺: capture timeout を救済対象に追加（2026-05-29）」セクション追加
- **当初メモの「`capture_controller.rb` の rescue で Timeout 個別捕捉を追加」は不要**: timeout は既に `SbpsClient.capture` 内で `TIMEOUT_ERROR` として記録される（[[af-sbps-entry-capture-recovery-cutover]] の重要訂正参照）

**諦め条件（終了条件）**: ユーザー判断で**設けない（Spica踏襲）**に決定。再 capture が成功/確定失敗で自然収束。永続 timeout 観測時に別途検討、と ADR-039 補遺に明記済み。

**worktree でのテスト実行tip**: setup-worktree-docker.sh は重い＆`.env`(symlink注意)を書換える。primary の stack が起動中なら worktree dir から `docker compose -p web-application run --rm web bundle exec rspec <spec>` で primary の db/redis/gems volume を共有しつつ worktree コードをマウントして実行できる（`.env` は primary を symlink）。

## 後続MR 2: Spica 既capture済み・Nuts 未capture プールの復元（管理画面方式で実装済み）

**Why**: MR-16324 で Nuts バッチから `spica_captured?` 検知を削除したため、FF 切替前に「Spica で確定済み・Nuts に CaptureSuccessEvent 無し」レコードを復元しないと、切替後に Nuts バッチが SBPS に再 capture リクエストして二重課金リスク。既存「Spicaからの契約復元」バッチは既存契約 skip 設計のため利用不可。

**実装方針（2026-05-29 確定・実装）**: スクリプトではなく **既存 admin 復元パターン（`agreement_restorations`）踏襲の管理画面**。dry-run は不要（ユーザー判断、冪等性 + precise predicate で担保）。worktree `worktree-admin-real-sales-restore` で実装、RSpec(21)/Rubocop/Packwerk green。未コミット。

実装ファイル:
- Restorer: `packs/nuts/softbank/lib/nuts/repositories/spica/af/capture_event_restorer.rb`（`Nuts::Repositories::Spica::Af::CaptureEventRestorer`。Spica 突合 + `CaptureSuccessEvent` INSERT。`Nuts::Core::Logger`/`UserAnimePayment` 参照は package_todo.yml 追記済み）
- Job: `app/jobs/nuts/restore_capture_event_job.rb`（`Nuts::RestoreCaptureEventJob`、`BATCH_NAME="restore_capture_event"`）
- Controller: `app/controllers/admins/nuts/capture_event_restorations_controller.rb`（admin_key + IP制限、merchant=af のみ、perform_later → BatchSession 追跡）
- routes: `config/routes/admin.rb` の `namespace :nuts` に `capture_event_restorations`、ダッシュボード `app/views/admins/nuts/show.html.erb` にカード追加 + View 3点

要点:
- 対象抽出: Nuts 起点 `SubscriptionAgreement.where(merchant_code: af).authorize_succeeded.capture_pending` → (customer_code.to_i=user_id, authorize_success_event.sbps_tracking_id=tracking_code) で Spica `user_anime_payments` を一括突合
- **実売上済み判定 = `confirmed_at != first_processed_at`**（status IS NULL, payment_method_id=5, history_label_id=10）。`confirmed_at = first_processed_at`（同じ時間のまま）は実売上未実施＝誤救済防止の核。削除済み `CaptureStateReader#captured?` の `confirmed_at.present?` は softbank2 で常に true になり信頼できないため不採用
- 動作: `agreement.build_capture_success_event.save!` のみ。SBPS API 叩かない、Spica 変更しない
- `not_unregistered`/GRACE_PERIOD は非適用（歴史的整合操作。実課金しないので競合・解約懸念なし）
- 冪等性: CaptureSuccessEvent UNIQUE + 実行直前 reload + presence 再チェック

## 切替フロー（最終形）

1. MR-16324 マージ・デプロイ（aws-schedule は `is_active: false`）
2. timeout 救済 MR マージ・デプロイ（後続MR 1）
3. 手動復元スクリプト実行（後続MR 2、dry-run → 本実行）
4. `entry_capture_recovery` FF ON
5. 登録時実売上リカバリーバッチを単発実行・動作確認
6. aws-schedule を `is_active: true` に変更してデプロイ、定期実行開始
7. SBPS 管理画面で実売上漏れ確認、漏れあれば手動実売上
