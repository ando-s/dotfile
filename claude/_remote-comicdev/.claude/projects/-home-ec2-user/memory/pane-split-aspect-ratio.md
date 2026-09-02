---
name: pane-split-aspect-ratio
description: Herdrでpaneを追加するとき、分割後の各paneが縦横比1:1に近い見やすい形になる方向を選ぶ
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3ce11da2-768a-433a-aca5-44a0352ac85c
---

Herdr で新しい pane を追加（split）するとき、分割後の各 pane が縦横比おおむね 1:1（正方形に近い）になる方向を選ぶ。細長い・平たい pane を作らない。

**Why:** ユーザーは、縦横比が1:1に近い pane が最も見やすいと明示。極端に narrow な列や短い行は避けたい。

**How to apply:** 分割前に `herdr pane layout --pane "$HERDR_PANE_ID"` で対象 pane の rect(width,height) を見る。
- width > height なら右に分割（`--direction right`）して幅を割り、正方形に近づける。
- height > width なら下に分割（`--direction down`）して高さを割り、正方形に近づける。
- 分割後どちらかが極端に細長くなる場合は、別 tab を提案するなど詰め込みを避ける。

herdrスキルの既定ルール（wide→right, narrow/tall→down）と方向は一致するが、判断基準は「見やすさ＝1:1に近づける」を優先する。
