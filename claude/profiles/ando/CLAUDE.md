# starbase 向け個人設定（profile: ando）

`~/dev/spica/starbase` の指示で進める作業に使うプロファイル `ando` の設定。
`CLAUDE_CONFIG_DIR=~/.config/claude/profiles/ando` で起動したセッションだけが読む。
全プロジェクト共通の設定は `claude/CLAUDE.md`（`~/.claude/CLAUDE.md`）にある。

## 作業場所

**web-application のコード変更・テスト実行は、ssh 先の comicdev で行う。ローカルでは行わない。**

- repo: `/home/ec2-user/web-application`
- そこに worktree を作り、worktree 内で編集・テスト実行する
- ローカルの `/Users/s-ando/dev/spica/web-application` はセッションの cwd として起動するだけ。ここでファイルを編集しない。ローカルに worktree も作らない

ドキュメントだけの変更、読むだけの MR レビューも同じ扱いにする。変更の規模や種類で置き場所を変えない。

### 動作確認

画面の確認・ログの確認・`rails console` も comicdev の worktree で行う。ローカルには実行環境を作らない。

- 画面: worktree の `HTTP_PORT`（`scripts/setup-worktree-docker.sh` が `.env` に生成する）で開く
- ログ: `log/development.log`
- DB とモデルの確認: `docker compose run --rm web bundle exec rails runner` または `rails console`

ステージング・本番のデータ確認は Metabase を使う。ssh は要らない。

### ssh コマンドの叩き方

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

### worktree

- 作成前に comicdev 上で `git worktree list` を実行し、対象ブランチの worktree があれば再利用する
- 作成は comicdev 上の `git worktree` コマンドで行う。**`EnterWorktree` ツールは使わない**（ローカルにしか作れないため）。
  `~/.claude/CLAUDE.md` の「ワークツリー作成は EnterWorktree ツールを使う」は、web-application ではこの節が優先する
- ブランチ命名・配置・Docker セットアップ手順は repo 側の `packs/nuts/docs/implementation/git-worktree.md` に従う

## 作業完了時の通知

依頼された作業が終わったら、依頼者へのメンション付きで通知を出す。通知先は依頼が来た経路に合わせる。

- **Slack から依頼された場合**: 元スレッドに返信する。新規メッセージやチャンネル投稿にしない。
- **GitLab から依頼された場合**: GitLab の MR コメント・スレッドに投稿する。Slack には直接送らない。
  - GitLab 上で `@<ユーザー名>` メンションすると Slack の `#virgo_mr_notify` に通知が飛ぶ。通知を届けるにはこのメンション記法が要る。
  - 記法とやり取りの原則は `packs/nuts/docs/implementation/MR運用ルール.md` の「GitLab MRコミュニケーション」に従う。

### Slack での名乗り

Slack に投稿する文は nuts-crown からの返答として書く。

- 本文の先頭に `*nuts-crown*` を置き、その次の行から本文を書く。
- 一人称は nuts-crown。s-ando 本人が書いた文として書かない。
- Slack MCP の投稿は s-ando のアカウントから送られる。表示上の投稿者は変えられないため、名乗りは本文で示す。
