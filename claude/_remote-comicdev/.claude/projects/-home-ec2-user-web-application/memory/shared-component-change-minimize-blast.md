---
name: shared-component-change-minimize-blast
description: 共有部品を変えるときは影響最小を既定にする。模倣元の挙動を共有部品にコピーしない
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 11b37f19-de80-415b-91cc-52da9ebd503e
---

共有部品（複数の呼び出し元が使うstruct・基底クラス等）を変更するときは、**触っていないコードへの影響を最小化する選択肢を既定**にする。常時適用・全体一貫は任意の上積みとして提示する。

**Why:** MR16416で `Nuts::Core::PhaseResult`（4バッチ共有）に skipped を追加した際、参照元の!16415（skip件数を常時表示）の出力をそのまま真似て summary に `skipped=0` を常時付与した。16415の `CaptureEventRestorer` は自前の result_message を持つ専用部品で波及先がない。共有struct との所有構造の差を見ずに、見た目だけコピーした。波及（他3バッチの result_message に `skipped=0` が増える）は認識していたのに、影響の大きい方を既定として提案し、ユーザー指摘で条件付き付与（`skipped>0` のみ）に修正した。

**How to apply:**
- 別MR/別実装の挙動を真似るとき、模倣元と適用先の**所有構造が同じか**（専用部品か共有部品か）を先に確認する。
- 共有部品の変更は **least surprise / 最小波及を既定**に置く。「全体で一貫する」を理由に影響範囲を広げる方を既定にしない。
- 影響範囲を自分で認識したら、それを「許容できるトレードオフ」として広い方に倒さず、狭い方を既定にして広い方を選択肢として出す。

関連: [[plain-language-no-jargon]] [[minimalism-not-skip-tests]]
