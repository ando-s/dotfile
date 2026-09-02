---
name: nuts-vocabulary-translation-at-wire
description: Nutsの語彙変換点は外部システムへの電文組み立て点。プロバイダ層の公開I/Fも共通語彙で通す
metadata: 
  node_type: memory
  type: project
  originSessionId: 2bcb7a51-3c12-411f-8e0e-1085c9dd205f
---

Nuts の語彙の変換点は「パック境界（Card↔SonyPayment 等）」ではなく「外部システムへの送信・受信点（電文組み立て・レスポンス解釈）」。Core / Card / SonyPayment（Nuts内のプロバイダ層）まで共通語彙で通し、ベンダー語（e-scott の会員情報登録取引 / 4Mem*、SBPS の cust_code 等）は API クライアントの request/response 変換にのみ現れる。

**Why:** Nuts のプロバイダ層（Nuts::SonyPayment）と外部システム（e-scott）は別物。他のクレカ代行への抽象化を見据え、代行の容れ物概念（会員等）に内側の語彙を引っ張られないため。MR!16637 レビュー（2026-07-02）で s-ando が整理。

**How to apply:**

- 前例: `Nuts::Sbps::SbpsClient` の公開 I/F は authorize / capture / customer の共通語彙、`cust_code` / `sps_hashcode` は `api_client/*/request.rb` と xml のみ
- 共通語彙にできないプロバイダ固有概念（EncryptValue、kaiin_pass 等）だけ `sbps_tracking_id` 同様にプロバイダ接頭辞付きで公開 I/F に出してよい
- カード（Sony Payment）: e-scott の「会員」は実質カード保管（4MemAdd の登録内容は kaiin_id + Token のみ）。Card 層の資源名は「登録済みカード（registered_card）」。会員 API の各操作（add/del/chg）は契約操作の受け口（token / unregister / カード変更）の実装の一段で、HTTP 層に会員 CRUD は作らない
- 関連: [[mr-message-use-ubiquitous-language]]
