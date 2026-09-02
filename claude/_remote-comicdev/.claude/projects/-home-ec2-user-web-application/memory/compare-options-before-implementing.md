---
name: compare-options-before-implementing
description: 指摘や依頼が来ても即着手せず、選択肢を洗い出して比較してから着手する
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 02ef7b61-1253-48a9-9925-26e0a978801e
  modified: 2026-08-10T04:13:20.317Z
---

指摘・依頼を受けたとき、すぐ実装に入らない。取りうる選択肢を洗い出し、影響範囲・再発性・レビュー負荷を比較したうえで着手対象を決める。

**Why:** 目の前の指摘に沿って動くと、より効果の大きい問題を後回しにする。CodeRabbit の指摘でspec1ファイルをrequest spec化した際、実際に優先すべきだったのは「規約ファイルが CodeRabbit の設定に未登録で、規約の除外条件が届いていない」という全MRに効く問題と、repo内ドキュメントの誤記だった。前提（規約の原典・既存の変換手順・技術的事実）を確認する前に着手したため、誤った前提に沿う変換をしてやり直しになった。

**How to apply:** 着手前に、(1) 指示の原典を repo 内で特定する（[nuts-words-must-exist-in-ubiquitous-language]] と同じく推測で済ませない）、(2) 選択肢を3つ程度に整理して影響範囲と再発性で並べる、(3) 推奨を示して判断を仰ぐ。作業の途中で前提が崩れたら、その場で止めて選択肢の比較に戻る。関連: [[no-carryover-force-decision]]、[[review-ground-findings-in-behavior]]
