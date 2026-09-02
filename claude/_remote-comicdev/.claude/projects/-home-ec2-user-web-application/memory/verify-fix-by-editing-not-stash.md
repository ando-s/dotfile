---
name: verify-fix-by-editing-not-stash
description: 修正を外して落ちるか確かめるときはstashを使わず直接編集して戻す。空stash pushの直後のpopは他セッションのstashを取る
metadata:
  type: feedback
---

テストが修正を実際に検証しているか（外すと落ちるか）を確かめるときは、`git stash` を使わずに対象ファイルを直接編集し、`git checkout -- <file>` で戻す。

**Why:** stash スタックは本体repoと全ワークツリーで共有されている。修正をコミット済みの状態で `git stash push <file>` を打つと保存対象が無いためエントリが作られず（エラーにもならない）、続く `git stash pop` が他セッションのスタックの先頭を取り出して worktree に混ぜてしまう。実際に別ブランチの yarn.lock 変更と未追跡ファイルを引き込んだ。

**How to apply:** 検証は「編集 → rspec → `git checkout -- <file>`」の3手で行う。誤って pop した場合は `git fsck --unreachable` で該当のstashコミットを探し、`git stash store -m "<元のメッセージ>" <sha>` で戻したうえで、混ざった変更を `git checkout --` と `git clean -fd <path>` で取り除く。

関連: [[worktree-verify-branch-code]]
