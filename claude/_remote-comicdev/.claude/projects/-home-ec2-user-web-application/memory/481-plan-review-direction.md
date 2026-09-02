---
name: 481-plan-review-direction
description: "MR !16401（NUTSAFSBPS-481 plan）レビューで決めた最小構成の方針 — order_id発行イベント＋Metabase検知＋運用責務。[must]下書き作成済み・未送信"
metadata: 
  node_type: memory
  type: project
  originSessionId: b6a518ac-b2d0-426c-ae72-926e105203df
---

NUTSAFSBPS-481（478フォローアップ）の plan MR !16401 レビューで、s-ando が方針を決定（2026-06-12）。

## 決定した方針（plan の3段構えから縮小）

- **コード変更は2点だけ**: ①新採番した order_id を SBPS 送信前に独立トランザクションで記録する「order_id 採番イベント」（英語名 `OrderIdAssigned` 想定）新設 ②`order_id_for_authorize` に「採番イベントがあり対応する成功・失敗イベントが無ければ新採番せずその order_id を再送」の判定追加
- 呼称は「採番」で統一（478コードコメントの既存語）。「発行」は発行時 order_id・決済の再発行（reissue）と被るため使わない
- **イベントのモデリング（s-ando と議論して確定）**: 継続課金版 `AuthorizeStartEvent`（subscription_payment、sent_order_id 保持、送信前に独立コミット）を追加する。ドメイン整理: 一回めの order_id は「発行」（物理は subscription_payment の create、イベント不要）／二回め以降は失敗後の再試行（reauthorize 的）だが新語を立てず authorize イベント族を使い回す。継続課金の authorize イベント族は既に試行ごと has_many（authorize_failure_events）なので start も自然に試行ごと。登録・単発の AuthorizeStartEvent（リンク型・1決済1件・URL保持）とはクラスもテーブルも別で衝突しない。判定式は「start があって対応する結果（success/failure）が無い」＝結果が分からない。新語（採番・attempt・OrderIdAssigned）は不要。制約: このイベントだけ後続と同一トランザクション禁止 — plan に明記要。注意: 下書きの「全送信分の送信記録は不要」は毎送信記録と矛盾して読める — Submit 前に表現確認 or plan レビューで補足
- **全送信の送信記録イベント・通知バッチ（旧 plan Phase 2）は作らない**。検知は Metabase アラート（authorize 未成功×支払日から N 日経過、既存テーブルの SQL）
- **強制解約の保留・復元の仕組みは設けない**。期限内に気付いて対応するのは運用の責務（s-ando 明言）

**Why**: 二重仮売上の経路は「確定エラー履歴→新採番Y送信→成功イベント保存前に中断→次回さらに新採番Z」だけ（初回・同一 order_id 再送の中断は SBPS が重複として弾く）。この経路は Z 成功で正常終了に見えるためアラートで検知できず、コードで防ぐしかない。発行イベントが残れば次回 Y 再送に倒れる。masterの `order_id_for_authorize`（`subscription_payment.rb:202`、478は2026-06-10マージ済み）は失敗イベントしか見ないため、イベントが残らない中断が穴。

## 状態（未完了）

- [must] レビューコメント下書き作成済み（draft id 32577、スレッド b25d54b4... への追記）。**未送信** — s-ando が GitLab で Submit する
- `Commented(s-ando)` ラベル付与済み
- m-kitano による plan 書き直し待ち。MR タイトル・概要も照会API前提のまま要更新（下書きで指摘済み）
- m-kitano は業務委託で Metabase 等の社内ツールを知らない。コメントでは社内ツールは説明を添える／「こちら側で対応するので不要」を明示する（Metabase 設定は s-ando 側の作業）
- worktree `review-mr-16401` 残置（ブランチは 6/9 分岐で478コード未包含、レビュー時は origin/master 参照が必要）

関連: [[capture-recovery-followup-mrs]] [[af-sbps-entry-capture-recovery-cutover]]
