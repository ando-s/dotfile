---
name: force-push-user-runs-it
description: force-pushが必要な時はClaudeは実行せず、ユーザーが自分の手元でコマンドを打つ
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c7a40c39-f474-4cc3-af15-044e32daf53b
---

force-push は feature ブランチであっても Claude は実行しない。必要な時はユーザーが自分の手元（自分のチェックアウト）でコマンドを打つ。

**Why:** ユーザーの明示方針（2026-07-13）。force-push は常にユーザー側で行う。

**How to apply:**
- ブランチ履歴の置き換え（rebase / reset して上書き等）が要る場合、Claude はクリーンな内容を用意し（必要なら temp ブランチへ通常 push）、**force-push するコマンドをユーザーに渡す**。実行はユーザー。
- force 不要な操作（MRの target 変更・description 更新等の API 操作、通常 push、新規ブランチ push）は Claude が実施してよい。
- 例: 派生MR化で16732を16719先端起点へ組み直す際、clean内容をtempブランチにpushし、`git push --force-with-lease` の1行をユーザーに渡す。
