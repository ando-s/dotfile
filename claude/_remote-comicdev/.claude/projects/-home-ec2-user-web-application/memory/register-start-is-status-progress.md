---
name: register-start-is-status-progress
description: "登録開始イベント(RegisterStart)は決済進捗でなく契約状況側の進捗に分類する — s-ando の設計方針（MR !16667 レビュー, 2026-07-02）"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3c8e0a90-05a3-4a92-b024-c8efd073fe8b
---

SBPS 継続課金契約の RegisterStartEvent（旧 AuthorizeStartEvent、MR !16667 で改名）の分類方針。

- s-ando の設計方針: 登録開始は**契約状況（Submitting → Registering → …）側の進捗イベント**であり、登録決済進捗（RegisterPaymentProgress）に置かない
- 根拠: 改名理由そのもの（登録開始は仮売上を意味しない）＋ ADR-047「申込要求は決済イベントを持たない」。決済進捗の導出（latest_register_payment_progress_event）に登録開始イベントが残ると、申込要求経路でも決済進捗が REGISTER_START に動き分類が食い違う
- 影響範囲（移す場合）: `register_started?` の導出元、RegisterPaymentProgress enum、ユビキタス言語・ドメインモデル図（.pu/.svg）の登録決済進捗定義
- MR !16667 に [should] 下書き（draft 33374, payment_status_manageable.rb:9）を作成済み（2026-07-02 時点未送信）。対応先が本MRか申込要求MR（!16595 系）かは m-kitano の回答待ち

関連: [[af-sbps-entry-capture-recovery-cutover]] [[481-plan-review-direction]]
