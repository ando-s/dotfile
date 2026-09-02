---
name: worktree-docker-test-setup
description: worktreeでrspec/rubocopを動かす正しいdocker手順（専用スクリプトを使う）
metadata: 
  node_type: memory
  type: project
  originSessionId: 5a7dd437-762a-4596-a645-c5ae7e9cec48
---

worktreeでテストを動かす時は、自前でcompose project名やボリュームをいじらず専用スクリプトを使う。

**手順:**
1. 既存リモートブランチをworktreeに展開した場合はdetached HEADになるので、まず `git checkout -b <branch>` でローカルブランチ化（スクリプトが `git branch --show-current` を要求するため）
2. `.env` のコピー: EnterWorktree で作った worktree は `.worktreeinclude`（本体repo直下、MR b9834bb578）が `.env` と `docker-compose.override.yml` を自動コピーするので手動cpは不要。手動 `git worktree` で作った場合のみ `cp ../../../.env .env`。
3. `bash scripts/setup-worktree-docker.sh` を実行
   - `docker-compose.override.yml` をworktree用テンプレ`docker-compose.override.yaml.worktree`からコピー生成（共有gemボリューム`spica_shared_gems`、worktree独立ネットワーク`spica_link_<port>`、vite公開停止で本体とのポート衝突回避）。`.worktreeinclude`がコピーした本体のoverride（本体ポート固定）をここで上書きする。
   - `.env` に `HTTP_PORT`(branch hash由来)・`PRIMARY_GIT_DIR` をマーカー区切りで追記
4. 共有gemボリュームが空なら一度だけ移行: `docker run --rm -v web-application_datastore:/from:ro -v spica_shared_gems:/to alpine sh -c "cp -a /from/. /to/"`
5. `docker compose up -d db redis`
6. test DB作成: `docker compose run --rm --no-deps -e RAILS_ENV=test web bundle exec rails db:create db:schema:load`（DBボリュームはworktree独立なので毎回必要）
7. テスト: `docker compose run --rm --no-deps web bundle exec rspec <spec>`（`--no-deps`でvite等を起動せずポート衝突回避）

**ハマりポイント:**
- `.worktreeinclude` が本体の `docker-compose.override.yml`（本体の固定ポートをbind）をworktreeにコピーするため、setupスクリプトを回す前に `docker compose` すると本体の起動中containerとポート衝突する（例: `Bind for 0.0.0.0:5432 failed: port is already allocated`）。必ずsetupスクリプト（worktree用テンプレで上書きし独立ポートにする）を先に実行する。
- compose project名を本体と同じにしてボリューム流用すると、本体のweb containerは本体パスをマウントするためブランチコードを検査できない（[[worktree-verify-branch-code]]）。スクリプトはworktreeパスをマウントしつつ独立ネットワークにするので正しい。
- ドキュメント: `packs/nuts/docs/implementation/git-worktree.md`（Nuts worktree運用ガイド／MR !16378で旧skillから移行）。基盤側Docker詳細は `docs/workflows/docker-worktree.md`。旧 `packs/nuts/.ai/skills/git-worktree/` は廃止。
