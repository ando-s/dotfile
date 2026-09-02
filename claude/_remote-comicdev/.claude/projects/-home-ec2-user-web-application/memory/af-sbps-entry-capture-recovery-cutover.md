---
name: af-sbps-entry-capture-recovery-cutover
description: AF SBPS 登録capture救済の Nuts/Spica 切替 — FF が握る経路、ロールバック挙動、決済方式ごとの job/app の違い
metadata: 
  node_type: memory
  type: project
  originSessionId: 74bdc28f-9dfb-4bf3-bfb9-63baf3a51714
  modified: 2026-08-07T01:34:51.390Z
---

登録時実売上(capture)リカバリーの Nuts 切替（NUTSAFSBPS-401 / ADR-039）。`scripts/execute-nuts-entry-capture-recovery-production.sh` で StepFunction(Human Approval)経由で本番手動実行する。

**FF `NutsFeatureFlag(af/sbps/entry_capture_recovery)` が Spica↔Nuts のアトミックな排他スイッチ**:
- ON → Nuts バッチ `Nuts::Softbank::Batches::Daily::EntryCaptureRecovery` が救済。Spica は `return if af_sbps_entry_capture_recovery_use_nuts?` で停止（`app/services/payments/anime_subscription/recover_unconfirmed_payment_service.rb:22`）。
- OFF → Nuts は早期 return(no-op)、Spica が救済。両者同時稼働の窓は無い。

**FF が握る Spica 経路は softbank2(=softbank_b) のみで、アプリ(before_action)経路**（`app/controllers/application_controller.rb:23` → `RecoverUnconfirmedPaymentService`）。**ジョブではない**。混同注意: `RecoverTimeoutBillingDemandJob` は softbank **A** 用の非同期ジョブで FF 無関係。`retry_softbank_b_continue_process_job` は継続課金リトライで登録captureとは別物。

**ロールバック**: FF=false で softbank2 のアプリ救済が復活し未処理分をカバー。二重captureしない（Spica対象は `recoverable`=未確定のみ＋60秒 confirmed_at ガード、Nuts capture済みは `write_to_spica!` で confirmed_at 入り→対象外）。**ただし FF は「今後どちらが救済するか」のスイッチで、既に実行された capture(実売上=実課金)は取り消さない**。誤capture防止は事前のプリフライト件数確認で担保。

**注意点**: バッチ対象抽出 `EntryCaptureRecoveryQuery` に LIMIT/dry-run 無し。初回は「Spica既capture済みだが Nuts にイベント無し」の歴史的積み残しも `capture_pending` に含まれ得る（controllerの `spica_captured?` 分岐で SBPS再送せずイベント整合のみ→二重課金にはならないが件数が膨らむ）。GRACE_PERIOD=15分は初期値、本番観測で調整予定。

プリフライト用 read-only 件数確認スクリプト: `scripts/nuts/count-entry-capture-recovery-targets.rb`（未コミット）。

## 救済責務の引き継ぎ範囲（要注意：哲学が逆転）

Spica `RecoverUnconfirmedPaymentService` の `user_anime_payments.recoverable` scope（`app/models/user_anime_payment.rb:64-75`）は 3 つの OR 条件で救済対象を抽出している：

1. `confirmed_at IS NULL` — softbank2 登録では発生しない（`create_for_softbank_b!` で必ず `result[:confirmed_at]` がセットされる）
2. `status IN ('FIX_TIMEOUT', '99')` — capture API 試行済みだが結果不確定で再試行
3. `payment_method_id=5 AND history_label_id=10 AND confirmed_at = first_processed_at` — softbank2+entry で capture API 未実行（success 経路非到達）

**`'99'` は Docomo の未受付 status**（`lib/payment/docomo/config/processing_status.rb:27` / `packs/nuts/plan/20260303-restore-subscription-agreement.md:271`）。SBPS の `res_err_code` は4桁/8桁仕様なので softbank2 経路では原理的に書き込まれない。softbank2 登録で条件2 を実質駆動するのは `FIX_TIMEOUT` だけ。

**初版の Nuts `EntryCaptureRecoveryQuery` は条件3 のみ引き継ぎ**：`capture_pending` = `CaptureSuccessEvent も CaptureFailureEvent も無い`（`subscription_agreement.rb:155-165`）。→ **2026-05-29 に条件2(`FIX_TIMEOUT`) も引き継ぎ済み**（[[capture-recovery-followup-mrs]] 後続MR1 実装）。新 scope `capture_recoverable`（成功なし AND timeout 以外の失敗なし）で timeout 失敗のみの契約も救済対象化。`'99'` は引き継がない（Docomo 専用）。

**重要訂正（要検証だった点）**: 「timeout は `capture_controller.rb` の rescue で一律 `INTERNAL_SERVER_ERROR`」は**誤り**。SBPS の `Timeout::Error` は `SbpsClient.capture` 内で個別 rescue され `CaptureResult.build_error(error_code: TIMEOUT_ERROR)` を返す（`sbps_client.rb:42-46`）→ controller は `build_capture_failure_event(sbps_error_code: result.error_code="timeout_error")` を保存。controller の包括 rescue(`INTERNAL_SERVER_ERROR`)は DB/Spica 書込等の予期せぬ例外専用で、SBPS timeout はそこに到達しない。**よって timeout は recoverable な形(`TIMEOUT_ERROR`)で正しく記録済み**。後続MR1 で「controller に timeout 個別捕捉を追加」する作業は不要だった（クエリ側だけで完結）。

| 観点 | Spica | Nuts (ADR-039 + 補遺) |
|---|---|---|
| timeout 失敗 | 60秒クールダウンで再試行 | `capture_recoverable` で再試行（終了条件なし=Spica踏襲） |
| 確定的失敗 (NG 等) | 同上で再試行 | 対象外（`CaptureFailureEvent` で確定） |
| SBPS 確定済みなのに失敗記録ケース | 再試行で巻き取る | timeout は巻き取る／NG は救済漏れリスク残 |

ADR-039 は Spica の救済を「ブラウザ離脱救済」とだけ捉えており、条件2 の意図を引き継いでいない（補遺で明示する余地あり）。

## 60秒ガードの意味

`recover_unconfirmed_payment_service.rb:16` の `return if @user_payment.confirmed_at && @user_payment.confirmed_at > Time.zone.now.ago(60.seconds)` は二役：

- **短期競合防止**: callback で create された直後（success リダイレクト中）に別タブの before_action が capture を二重発火するレースを抑制
- **長期クールダウン**: NG/`FIX_TIMEOUT` 応答時に `confirmed_at` が試行時刻に書き換わる（`user_payment_service.rb:36-58`）ため、永続エラー時もユーザーあたり最大「60秒に1回」に発火頻度が抑えられる

つまり「毎リクエスト」ではなく「最低60秒間隔で1回」のペースで SBPS API が叩かれる。終了条件は無いが、実運用で `'99'` 永続化シナリオが発生しないため実害ゼロだった。

## 本番切替の実施順序（ADR-039 補遺の記載と逆）

AF 本番作業記録（Google Doc `11y81HNNlWieY0NL8t3HRmoy84X3oLXE2AnZ56MA4B0A`「2026-06-08実売上リカバリー切り替え」）の実施順は:

1. **FF を true にする**（既存停止）→ 2. リストア対象件数確認 → 3. リストア → 4. 完了確認 → 5〜7 単発バッチ実行・確認 → 8 `aws-schedule.yml` の `is_active = true`

記録された理由: 「リストア実施以降に spica 側に新規の実売上リカバリーによるレコード（spica と nuts の同期されてないレコード）が増えないようにするため」。

**ADR-039 補遺「切替フロー上の位置づけ」は「リストア（FF ON の前）→ FF ON」と書いており、実績と逆**。ADR どおりだとリストアと FF ON の間に Spica が救済した契約が Nuts に取り込まれず、`is_active: true` 後にバッチが再 capture する。CF 版（NUTSSBPSCF-63 / MR!16946）レビューで指摘済み。

作業記録の他の要点:
- 対象の `subscription_agreement_id` 一覧を CSV 保存 → リストア後に同じ id で `capture_success_event` の有無を `IN` 句で確認（0行＝完了）
- 「user_id で見ると別契約と混同する。契約単位で見る」
- 切り戻し: FF を false に戻す。Spica 既存ロジックが動き、Nuts バッチは起動するがスキップログを batch session に残す

## `callback_nuts` 経路の特殊事情

Nuts 経由登録（FF `:entry` ON、`anime_subscription/softbank2/entry_controller.rb:104`）では `user.anime_subscription_entry!`（`app/models/user.rb:316-327`）が **`user_anime_payment` を作らない**。Spica 側に payment レコードが残らないため、Spica の `RecoverUnconfirmedPaymentService` は Nuts 経由登録には何もしない（recoverable scope の対象がそもそも存在しない）。

→ Nuts バッチ救済は **Nuts に `SubscriptionAgreement` が存在する** ことが前提。`:entry` OFF 時代に Spica 単独で登録した未確定 payment は Nuts バッチでは原理的に拾えない。`:entry` ON → 残存ゼロ化 → `:entry_capture_recovery` ON の順序が必須。
