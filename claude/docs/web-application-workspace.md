# web-application の作業場所と検証

このリポジトリの作業に使う決めごと。プロファイルに関係なく、`~/dev/spica/web-application`
（と comicdev 上の同リポジトリ）を触るときに読む。

**web-application のコード変更・テスト実行は、ssh 先の comicdev で行う。ローカルでは行わない。**

- repo: `/home/ec2-user/web-application`
- そこに worktree を作り、worktree 内で編集・テスト実行する
- ローカルの `/Users/s-ando/dev/spica/web-application` はセッションの cwd として起動するだけ。ここでファイルを編集しない。ローカルに worktree も作らない

ドキュメントだけの変更、読むだけの MR レビューも同じ扱いにする。変更の規模や種類で置き場所を変えない。

## 動作確認

画面の確認・ログの確認・`rails console` も comicdev の worktree で行う。ローカルには実行環境を作らない。

- 画面: worktree の `HTTP_PORT`（`scripts/setup-worktree-docker.sh` が `.env` に生成する）で開く
- ログ: `log/development.log`
- DB とモデルの確認: `docker compose run --rm web bundle exec rails runner` または `rails console`

ステージング・本番のデータ確認は Metabase を使う。ssh は要らない。

## ssh コマンドの叩き方

`comicdev` は ssh_config に `RemoteCommand`（`cd /home/ec2-user/web-application && exec $SHELL -l`）が設定されている。
そのため `ssh comicdev "コマンド"` は `Cannot execute command-line and remote command.` で失敗する。
非対話でコマンドを流すときは `-o RemoteCommand=none` を付ける。

```bash
ssh -T -o RemoteCommand=none -o LogLevel=ERROR comicdev \
  'cd /home/ec2-user/web-application && git status'
```

- `-o RemoteCommand=none`: 設定済みの `RemoteCommand` を無効にする
- `-T`: `requesttty true` による「Pseudo-terminal will not be allocated」の出力を止める
- `-o LogLevel=ERROR`: クライアント側の注意書きを減らす（サーバ側 banner の警告は残るので、出力を読むときは無視する）

ssh が失敗したら、原因を解消して ssh で再実行する。ローカル作業への切り替えは、この失敗の対処に含めない。
ローカルで作業してよいのは、ユーザーがそう指示した場合だけ。

## worktree

- 作成前に comicdev 上で `git worktree list` を実行し、対象ブランチの worktree があれば再利用する
- 作成は comicdev 上の `git worktree` コマンドで行う。**`EnterWorktree` ツールは使わない**（ローカルにしか作れないため）。
  `claude/CLAUDE.md` の「ワークツリー作成は EnterWorktree ツールを使う」は、web-application ではこの文書が優先する
- ブランチ命名・配置・Docker セットアップ手順は repo 側の `packs/nuts/docs/implementation/git-worktree.md` に従う

## 画面への到達

worktree のスタックは 80 番ではなく `.env` の `HTTP_PORT` で待つ。nginx は `VIRTUAL_HOST=localhost` で
起動するため、host が localhost のリクエストは接続元IPの制限で 403 になる。**403 を「届かない」と
読み替えない。**

- 80 番の `nginx-proxy` が Host で振り分ける。公開ホスト名（`sa2.comicdev.iowl.jp`。ALB が https を終端）は
  primary のスタックに向いている
- worktree のポートへ直接送るときは Host ヘッダを付ける

```bash
curl -s -H "Host: sa2.comicdev.iowl.jp" -b "festa_auth_dev=<users.auth_token>" \
  http://localhost:<HTTP_PORT>/subscribed_services/information
```

- ログインは `users.auth_token` の値を `Settings.browser_auth_token_key` の Cookie に入れる
  （開発環境では `festa_auth_dev`）
- ブラウザで通すときは worktree の nginx に公開ホスト名を `VIRTUAL_HOST` として持たせる。
  primary と同じホスト名を同時に割り当てると取り合いになる。手順と注意は
  `~/.claude/projects/-Users-s-ando-dev-spica-web-application/memory/worktree-browser-verify-public-host.md`
- 入会と都度課金の確認ページは申込の前提（コースの指定やセッション）が要る。前提が無いと 302 で入口へ戻る

## 開発環境のデータ

worktree の DB は独立で、`db:seed` だけではユーザーもコースのマスタも入らない。本体の
development DB をボリュームごとコピーすると揃った状態から始められる（同じ記憶ファイルに手順がある）。

## comicdev 側の Claude の記憶

comicdev で動かしたセッションの記憶はローカルのセッションからは読まれない。
`claude/sync-comicdev.sh` で取り込む。整理は `claude/README-claude-config.md`
