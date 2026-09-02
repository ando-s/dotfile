---
name: ground-proposals-in-existing-conventions
description: レビューで設計提案する前に、コードベースの既存規約を grep で確認し、外部APIの用語を持ち込まない
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 049bddf3-5dc0-4ccf-b9c2-7508b3af50ff
---

レビューでインターフェースや構造を提案するときは、**先にコードベースで既存の規約を検索し、その語・構造で書く**。外部API（Stripe 等）の用語を思いつきで持ち込まない。

具体例（MR!16637 / クレカ submit の戻り設計）: 「型付きの分岐で揃える」提案に Stripe の `next_action` を持ち込んだが、grep するとコードベースには 0 件。実際には Core が既に `payment_method`（分岐キー）＋ `provider_data`（provider 固有ペイロード）で同じ型付き分岐を実現していた（`Nuts::Core::Api::V1::SubscriptionAgreementsController`）。SBPS の `provider_data` は `{ redirect_http_method, redirect_url }`。

**Why:** 外部語は読み手が共有しておらず、既存の解決策を無視した提案に見える。「揃える」提案自体が既存規約を外す形になり本末転倒。

**How to apply:** 提案する語・構造を `grep` で既存有無を確認 → あればその語で書く → 無ければ「新規に定義する」と明示する。批判的思考の合図として「この語はどこから来た？」を自問する。

[[plain-language-no-jargon]] [[mr-message-use-ubiquitous-language]] [[review-ground-findings-in-behavior]]
