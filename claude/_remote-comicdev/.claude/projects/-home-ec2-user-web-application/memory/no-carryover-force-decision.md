---
name: no-carryover-force-decision
description: 未決事項・持ち越しは残さずユーザーに判断を迫る。planの持ち越し表に逃がさない
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ebbf422d-ad4f-48ff-bb16-b4c6f99f0970
  modified: 2026-07-29T06:24:14.527Z
---

未決事項・持ち越しを見つけたら、plan の「未決事項・持ち越し」表に書いて先送りせず、その場でユーザーに選択肢を出して判断を迫る。

**Why:** 未来に決定を残すと管理・追跡コストが発生する（plan テンプレの原則も「原則はその場で決める」）。Claude が「後続チケットで判断」と書いて逃がすと、決まらないまま残る。2026-07-29 NATSCREAF-76 で、多重度 0..n・3DS が運ぶ ID・現在の契約の決め方を持ち越し表に書いたところ、すべてその場で決められるものだった。

**How to apply:**

- plan の持ち越し表に項目を足す前に、まず AskUserQuestion で選択肢を出す
- 「今決められない理由」が本当に外部要因（他チケットの結果待ち・未確定の外部仕様）かを検査する。単に自分が決めきれないだけなら ask する
- 選択肢には推奨と、選んだ場合の波及（他の決定の前提が崩れないか）を添える
- 関連: [[review-ground-findings-in-behavior]] / [[nuts-design-doc-open-issues-timing]]
