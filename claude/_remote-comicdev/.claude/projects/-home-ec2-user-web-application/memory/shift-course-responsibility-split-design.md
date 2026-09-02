---
name: shift-course-responsibility-split-design
description: コース移行の決済/サービス責務分離の設計方針（NUTSSBPSCF-68）。Nutsにコース移行機能を持たせず解約+登録の組み合わせにする、移行時は非課金のみ
metadata: 
  node_type: memory
  type: project
  originSessionId: d88741b7-2701-44d6-93e6-a7a0ebd78ecd
  modified: 2026-07-27T09:24:42.914Z
---

NUTSSBPSCF-68（2026-07-27 設計をJIRAコメント id 42285 に記録）で決めた方針。

- **Nutsにコース移行という機能を持たせない**。Nuts利用者が「旧契約の解約」→「新契約の登録（申込要求・非課金）」の順に既存APIを呼ぶ組み合わせで実現する。解約を先にすれば `CancelWriter` の最新entry起点（cf/cancel_writer.rb:16）が旧契約を指すので、専用API `shift_course_unregister` は不要になる
- **`sbps_tracking_id` = `user_payments.tracking_code` の対応は廃止できない**。移行期間中にNuts契約とSpica決済レコードを結ぶ唯一のキーで、登録capture・継続課金の実売上の書き戻しが `find_by!(tracking_code)` で引く（cf/capture_writer.rb:14、cf/subscription_payment_capture_writer.rb:46,57、不在は例外停止）。廃止できるのは通知ペイロードでの受け渡しだけで、それには申込要求経路でも `write_to_spica!` を発火させる必要がある（現状は `authorize_success?` 限定）
- **移行時は非課金のみ**（課金あり経路をNutsに持たせない）。ただし現行CF仕様は2度目以降の移行で移行時課金＋新コースのポイント即時付与なので、サービス仕様の変更として事業側の合意が必要
- コース移行はCFのみ。AF側に移行の仕組みは無い（ユーザー確認済み）
- **ゴールはSpicaが決済テーブルを一切参照しないこと**。決済レコード作成をNutsへ寄せるだけでは足りず、Spica側のDB変更が要る。決済テーブルとサービステーブルは双方向結合（`user_shift_courses`→決済レコードFK 2本／`UserPayment.without_shifting_entry`→`UserShiftCourse`）。コース・金額・名称は `user_subscriptions.point_setting`（course_no=item_id）で代替可、**残るのは決済手段**（`label_no` のみが持つ。AFも同形）

**DB設計の決定（Spica側で完結・Nutsに問い合わせない）**
- 決済手段は `user_subscriptions` / `user_anime_subscriptions` に列追加（新テーブルにしない。行は1対1で結合が増えるだけ／`entry!` が既に pay_method を引数で受けている／退会後も行が残る）
- 契約の注文識別子も同テーブルに `order_code` として列追加（値はSpica発番＝`user_payments.order_code` と同値、nullable）
- `user_shift_courses` の決済レコードFK2本 → 移行元/移行後の会員契約IDに置換。決済レコードが必要な未Nuts化経路（docomo）は会員契約経由で引く
- ボーナス判定は移行元の会員契約のコースから直接取る。**移行記録の `confirmed_at` で置き換えてはいけない**（`confirmed` は `confirmed_at < time` 厳密比較で、新entry自身が比較対象に入り高額移行でもボーナスが出なくなる）
- `without_shifting_entry` + `origin_entry` は削除可（origin_entry は呼び出し元なし＝唯一の決済→サービス逆参照が消える）
- credit/au/docomo/softbankB の4経路を同時に直す（user_shift_courses は共有、Nuts化と独立）

**Why:** ADR-043案C（Spicaが決済レコードを作る暫定措置）の見直し条件に当たる。決済テーブルをサービス判断に使っている箇所が6つあり、うち移行記録の決済レコード外部キーと決済レコード作成が暫定措置。

**How to apply:** 未決は「移行の順序（解約先行なら申込失敗時に契約の無い会員が出る）」「非課金化に伴うポイント付与タイミング」「user_shift_courses の決済レコード外部キーの移行手順」。実装計画の着手前に決める。関連: [[nuts-requirements-provider-agnostic]] [[domain-first-then-document]]
