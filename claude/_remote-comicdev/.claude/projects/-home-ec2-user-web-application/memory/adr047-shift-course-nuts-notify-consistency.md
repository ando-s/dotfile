---
name: adr047-shift-course-nuts-notify-consistency
description: ADR-047申込要求コース移行のNuts↔Spica経路と整合機構（pagecon受け口はNuts、二重課金にならない理由）
metadata: 
  node_type: memory
  type: reference
  originSessionId: abf42075-a36b-4dff-a538-65909a19731d
---

CF SBPS-B のボーナス有コース移行（`cf_sbps_shift_course_use_nuts` ON・申込要求経路）の正しい流れと整合機構。MR!16697 で確認。

**経路（SBPS→Spica直接ではない）**

- Spica `create` → Nuts `submit_free`（`/subscription-agreements/free`、契約を `register_started` で作成・課金対象外）
- SBPS pagecon 結果 → **Nuts `register_free_controller`（申込要求の受け口）**。`register_subscription_request!` が `RegisterEvent` を作成し `subscription_register_success?`＝課金対象 `registerable?` になる
- Nuts `Registrable#create` の `ActiveRecord::Base.transaction` 内で `notify_nuts_merchant` → **Spica `callback_nuts`** へ POST（`status=subscription_register_success`）
- Spica `callback_nuts` → `nuts_shift_entry!`（Spicaトランザクション：`ShiftCourseService#execute!` ＋ `unregister_nuts_old_agreement!`）→ `{status: success/failure}`

**InternalApiClientは実HTTPでなく同一プロセス内ディスパッチ**（`packs/nuts/core/lib/internal_api_client.rb`：`Rack::MockRequest.env_for`＋`Rails.application.routes.call`）。同じ接続＝同じDBトランザクションに乗る。当初「外部HTTPなので巻き戻せない」と言ったのは誤り。

**二重課金にならない理由（当初の「原子性ギャップ」「別コミットの狭いエッジ」指摘はどちらも誤り）**

- `register_free`→通知→`ShiftCourseService`→`shift_course_unregister` は全て1つのDBトランザクション（入れ子は`requires_new`無しで最外に合流）
- ただしRailsは**例外が最外トランザクションを抜けた時だけROLLBACK**。旧解約のraiseは`callback_nuts`がrescueしてfailure返却＝それ単独では巻き戻らない。実際に巻き戻すのは`notify_nuts_merchant`がfailureを見て`MerchantNotificationError`を**再raise**し最外`register_free`を抜ける時（`registrable.rb:35`）
- 実測(Rails 8.0.2, 一時テーブル)で確認：A=rescueし再raiseしない→commit(巻き戻らない) / B=rescue後に最外で再raise→巻き戻る / C=貫通→巻き戻る。**本番はB**
- 巻き戻り後`RegisterEvent`なし＝`register_started`＝継続課金の`EXISTS(RegisterEvent)`(`issue_query.rb`)対象外。旧契約のみ課金で整合

**load-bearing・テスト空白（レビュー指摘候補）**: 上記は`notify`の再raiseに依存。これを外すと実測Aになり二重課金。失敗経路spec(`entry_controller_spec.rb:536`)は`ShiftCourseService`をモックし`callback_nuts`直POST（本番の`register_free`→notify再raise経路を通らない）ためロールバック未検証。`register_free`経由のe2eで「新RegisterEvent/subscription非永続化」をassertするテストが要る。

**責務分担**: 申込要求経路では Nuts `write_to_spica!` は空実装。entry payment 作成は Spica `ShiftCourseService`（ADR-043案C）。`sbps_tracking_id` は冪等キー整合のため Spica へ渡す。

図解: https://claude.ai/code/artifact/521f756a-3356-4031-b064-cde018aca292
