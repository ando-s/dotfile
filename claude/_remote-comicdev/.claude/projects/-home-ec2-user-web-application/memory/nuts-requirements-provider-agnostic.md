---
name: nuts-requirements-provider-agnostic
description: Nutsの要件定義はプロバイダ非依存で書く。決済代行固有の仕組みは実現方法であって要件ではない
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 01973cbb-fe70-48eb-b20d-0df0c2209948
---

Nutsの要件定義（`packs/nuts/docs/プロジェクトマネジメント計画/要件定義.md`）は**Nutsの要件**であって、特定の決済代行（Sony Payment等）の仕様書ではない。要件は「何が必要か」をプロバイダ非依存で書く。

**Why:** 特定プロバイダの仕様に寄せて要件を書くと、別の決済代行に切り替えた時に要件ごと作り直しになる。Nuts Coreはプロバイダ非依存（[[nuts-vocabulary-translation-at-wire]]）。

**How to apply:**
- 要件本文にプロバイダ固有語（例: Sonyの洗替使用区分・会員登録電文・取引種別1Check・K79・結果ファイル名`CardDB_*.sln`・接続仕様書の表番号）を出さない。
- 固有の実現方法は【クレカ】等の差分メモに最小限で（「実現は決済代行のカード有効性確認」程度）。
- プロバイダの自動挙動に要件を依存させない。例: 「洗替NGカードで継続課金がK79で自動失敗」はSony固有。Nuts要件は「無効カードでの継続課金は失敗として扱い、リトライ・強制解約・通知につなぐ」と一般化する。
- 責務は Nuts提供（仕様・機能・サーバAPI）と Nuts利用者（画面・実行タイミング・通知可否・対象選定）で分けて書く。

MR!16720で、有効性チェック・洗替の要件を当初Sony固有に踏み込んで書き、指摘を受けてプロバイダ非依存に修正した（コミット d5c3892c0c）。
