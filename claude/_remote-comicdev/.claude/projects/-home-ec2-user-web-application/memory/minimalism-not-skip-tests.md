---
name: minimalism-not-skip-tests
description: 「必要最小限」をテストを書かない口実にしない。境界値・分岐は入れる
metadata: 
  node_type: memory
  type: feedback
  originSessionId: da99aa2a-58eb-4de4-b8b4-8d5924a35126
---

`必要最小限` / YAGNI を理由に、価値あるテストを反射的に見送らない。最小限が抑えるのは冗長な Arrange・無意味なモック・重複ケースであり、振る舞いのカバレッジではない。

境界値（`<`/`<=` 境界等）・分岐網羅は価値が高い。特に決済等のクリティカルなロジックはテストを厚くする方へ倒す。レビュアーのテスト追加提案（[imo]等）は、既存テストで同じ回帰を検出できないなら入れる。

**Why:** MR16370で reviewer の境界テスト提案を「細かすぎ/必要最小限」で一度見送ったが、回帰検出価値ありとして全て入れ直した。

**How to apply:** テスト採否は「既存で回帰検出できるか」「境界・分岐をpinするか」で判断。最小限を口実に見送らない。詳細パターンは code-review-patterns.md「レビューのテスト追加提案を最小限で反射的に見送らない」。関連: [[ask-comments-reply-not-fix]]
