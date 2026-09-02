---
name: nuts-words-must-exist-in-ubiquitous-language
description: Nuts の話で使う語はユビキタス言語と突き合わせる。無い語は使わず、必要な概念なら表への追加を提案する
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1302589b-a8b9-4c91-b2ba-64fc0f1d7c2c
  modified: 2026-07-31T08:40:05.464Z
---

Nuts について書く・話すときは、使う語が `packs/nuts/docs/プロジェクトマネジメント計画/ユビキタス言語.md` にあるか確認する。無い語を新しく持ち込まない。必要な概念が表に無ければ、表への追加を提案する。

指摘された実例。

- **口座** — `UserSonyPaymentAccount` を指す言い換え。表に無く、概念なのか実装なのか読み手が判別できない。「Nuts利用者側の会員のレコード」のように何を指すか書く。コードのコメントにも入り込んでいた
- **長寿命** — 定義や説明で使う語ではない。「契約を解約しても会員は残り、契約ごとには作られない」のように何が起きるかを書く

**Why:** ユビキタス言語は概念を扱い、チーム内の認識を統一するためにある。表に無い語をその場で作って使うと、統一の役目が崩れる。

**How to apply:** ドメインの語を書く前に表を引く。実装済みの概念が表に無いことに気づいたら（例: 会員・顧客コードが未掲載だった）、そのまま使わずに追加を提案する。表に載せるのはドメイン用語だけで、実装名は載せない（[[ubiquitous-language-table-scope]]）。言い換え語を作らない点は [[no-canonical-jargon]] と [[plain-language-no-jargon]] と同じ。
