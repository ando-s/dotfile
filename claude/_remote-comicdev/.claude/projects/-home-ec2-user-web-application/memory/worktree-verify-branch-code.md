---
name: worktree-verify-branch-code
description: worktree作業中の検証は本体リポジトリ(master)でなくブランチのコードに対して行う
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5faefcc2-6052-4047-88cd-231aacca002c
---

git worktree で作業しているとき、検証（rspec / rubocop / packwerk）を本体リポジトリ（`/home/ec2-user/web-application`、通常 master）の docker で実行すると、**worktreeのブランチ変更ではなく master のコードを検査**してしまう。ローカルは常に「緑」に見え、push後のCIで初めて失敗が露見する。

**Why:** 2026-06-03 のMR16370で、検証を `cd /home/ec2-user/web-application`（master）で実行し続け、ブランチのrubocopオフェンス・テスト失敗を一度も検出できないままpushを繰り返した。「bundle exec vs bare rubocop の差」と誤診したが、実際は検査対象がmasterだっただけ。

**How to apply:** worktree作業の検証は必ずブランチのコードに対して行う。手段: (1) worktree内でdocker実行（ただし `.env` 欠如・viteのポート衝突に注意。`docker compose up -d db redis` で必要サービスのみ起動し `--no-deps` で実行）、(2) gem/db が本体側にしか無い場合は worktree の変更ファイルを本体へ一時 `cp` → 検証 → `git checkout HEAD -- <files>` で復元。CIコマンドと一致させる（CIは `docker compose run --rm --no-deps web rubocop -P`＝bundle exec無し）。関連: [[nutsafsbps-details]]
