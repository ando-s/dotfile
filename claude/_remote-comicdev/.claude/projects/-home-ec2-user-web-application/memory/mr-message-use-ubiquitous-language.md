---
name: mr-message-use-ubiquitous-language
description: MR返信・コメント等チーム向け文面ではプロジェクトのユビキタス言語を使う（平易化での言い換えはしない）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 79b43790-c999-4a2e-993a-c444447756cb
---

MRの返信・コメント・説明などチーム（開発者）向けの文面では、プロジェクトのユビキタス言語（ドメイン用語・確立済みクラス名）をそのまま使う。自分で平易な語に言い換えない。

例（Nuts/SBPS）: RegisterEvent / AuthorizeSuccessEvent / 申込要求・購入要求 / 与信・仮売上・実売上(capture) / トラッキングコード / 継続課金。ADRやコードで使われている語に揃える。

**Why:** 2026-06-24、MR!16595 への返信下書きで「RegisterEvent→登録イベント」「tracking_id→トラッキングID」等とその場の平易語に言い換えたところ「ちゃんとユビキタス言語を使って」と指摘された。チーム内では確立用語の方が正確で誤解が少ない。

**How to apply:** 「平易な言葉で」という指示は2種類を区別する。(1) 英語プロセスジャーゴン・カタカナ造語（backfill, big-bang 等）→ 平易な日本語に直す。(2) ドメイン用語（クラス名・業務語）→ 言い換えず正規のユビキタス言語を使う。ユーザーへのチャット説明では(2)も噛み砕いてよいが、MR文面では正規語。関連: [[plain-language-no-jargon]] [[review-comment-drafting-style]]
