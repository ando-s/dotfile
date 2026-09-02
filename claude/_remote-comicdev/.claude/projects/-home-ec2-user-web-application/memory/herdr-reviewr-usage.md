---
name: herdr-reviewr-usage
description: herdr-reviewr は開いたときのペインの cwd で対象リポジトリが固定される
metadata: 
  node_type: memory
  type: reference
  originSessionId: 50b60256-444f-4a96-8edc-70427849caa2
  modified: 2026-08-17T09:46:27.918Z
---

herdr のプラグイン `persiyanov.reviewr`（ターミナル内のコードレビュー用サイドバー）を導入済み。herdr 0.7.5 以上が必要で、0.8.0 へ更新して入れた。

**対象リポジトリは、開いた時点でフォーカスしていたペインの `foreground_cwd` で決まる**（`herdr/pane.sh` が `herdr pane list` の live cwd を読む）。ワークツリーを作る前に開くと本体リポジトリを見たままになり、別ブランチの差分が表示される。EnterWorktree ツールで作った場合は `worktree.created` イベントが飛ばないので自動で開き直らない。

**How to apply:** ワークツリーに入ったあとに `herdr plugin action invoke open --plugin persiyanov.reviewr` を呼ぶ。すでに開いているときは先に `close`。開き直したら `herdr pane list --workspace <ws>` で cwd がワークツリーになっているか確認する。

- 操作: `1`/`2`/`3` タブ、`u`/`b`/`t` 差分スコープ（未コミット / ブランチ / 直前ターン）、`v` 選択 → `c` コメント → `s` で同ワークスペースのエージェントへ送信
- コメントはメモリ上のみ。送信前に閉じると消える
- `herdr update` は herdr の外から実行する。セッション内では拒否される（`prefix+q` でデタッチしてから）

関連: [[herdr-pane-claude-agent-workflow]] [[worktree-verify-branch-code]]
