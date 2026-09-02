---
name: ubiquitous-language-table-scope
description: ユビキタス言語表はドメイン用語限定。掲載基準はStatusでなくコード確定
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8ec7fb2a-e90d-42e5-bd84-1e7ee49cd839
---

`packs/nuts/docs/プロジェクトマネジメント計画/ユビキタス言語.md` の用語表はドメイン用語に限定する。実装・アーキテクチャ用語（Writer/Restorer/Policy/FeatureFlag/BatchSession/UC・RCコントローラー）や環境概念（Nuts環境）は載せない（MR !16721で削除済み）。

**Why:** ユビキタス言語はドメイン（問題領域）の語彙。解決領域の実装・インフラ・アーキ構成要素名はユビキタス言語ではない。混ぜると表が肥大し、ドメインの共有言語という役割がぼやける。

**How to apply:**
- 掲載可否の基準は「ADRのStatus」ではなく **「コードで確定しているか」**。Proposedでもコード実装済みなら載せる（例: 申込要求/register_start）。コード未実装かつ命名未確定は載せない（例: クレカのmember_registered等は確定後）。
- グロッサリー自体が正典。他文書（ADR等）が別の語を使っていても、それを「類語」列や「正規語はX」という注記として記録しない（正規語が存在すると書くこと自体がおかしい、との指摘）。類語列は Nuts 内の真の同義語のみ。ADR側の呼称ずれを直すなら別スコープ。
- プロバイダ固有語はNutsのユビキタス言語に入れない。Nuts共通語に翻訳して載せる。例: SBPS由来の「申込要求」(与信なし)→「無料登録」、「購入要求」(与信あり)→通常の「登録」。コード識別子が固有語（subscription_register_success 等）でも、グロッサリーの日本語はNuts共通語にする。
- プロバイダ固有の識別子（SBPS/au/クレカ）は各プロバイダ用語集へ。本体は共通コア語彙＋Spica対応表に徹する。
- 定義・整理は機械的な追加削除の前に「そもそも何を載せるか」の基準を先に合意する。

関連: [[domain-first-then-document]] [[adr-status-convention-removed]]
