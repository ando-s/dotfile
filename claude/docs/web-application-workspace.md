# web-application の作業場所と検証

このリポジトリの作業に使う決めごと。プロファイルに関係なく、`~/dev/spica/web-application`
（と comicdev 上の同リポジトリ）を触るときに読む。

**web-application のコード変更・テスト実行は comicdev で行う。ローカルでは行わない。**
**ローカルのセッションから ssh でコマンドを流すのではなく、comicdev で claude を起動して作業させる。**

- repo: `/home/ec2-user/web-application`
- そこに worktree を作り、worktree 内で編集・テスト実行する
- ローカルの `/Users/s-ando/dev/spica/web-application` はセッションの cwd として起動するだけ。ここでファイルを編集しない。ローカルに worktree も作らない

ドキュメントだけの変更、読むだけの MR レビューも同じ扱いにする。変更の規模や種類で置き場所を変えない。

## 作業のはじめ方

Herdr のペインを分割して comicdev に入り、そこで claude を起動してタスクを渡す。

comicdev で起動した claude は、comicdev の `~/.claude/CLAUDE.md` と worktree 配下の `CLAUDE.md`・
`.claude/rules/` を読む。ローカルから ssh でコマンドを流す形ではこれらが読まれず、リポジトリの
決めごとが効かないまま作業することになる。

herdrの構文は版で変わるので、`herdr --help`と`herdr --skill`の出力を読んでから操作する。

1. `test "${HERDR_ENV:-}" = 1` を確認する。Herdr の外なら、この手順は使えないとユーザーに伝えて止める
2. `herdr pane split --current --direction right --no-focus` で兄弟ペインを作り、
   応答の `result.pane.pane_id` を控える（レイアウトが縦長なら `--direction down`）
3. `herdr pane rename <id> "comicdev"` でラベルを付ける
4. `herdr pane run <id> "ssh comicdev"` で入る。ssh_config の `RemoteCommand` が
   `/home/ec2-user/web-application` へ移動する
5. worktree で作業するときは `herdr pane run <id> "cd <worktree のパス>"` で移ってから起動する
6. `herdr pane run <id> "claude"` で対話 TUI を開き、
   `herdr wait agent-status <id> --status idle --timeout 60000` を待つ
7. `herdr pane run <id> "<タスク文>"` でタスクを渡す。完了を待ってから
   `herdr pane read <id> --source recent-unwrapped --lines 120` で結果を読む

タスク文には作業対象のブランチ・MR 番号・成果物の置き場所を書く。ローカルの会話でしか出ていない
前提は、向こうの claude には伝わらない。

ペインの操作の細部:

- 分割の向きは`herdr pane layout --pane "$HERDR_PANE_ID"`で見て、横長なら右、縦長なら下にする
- pane_idは応答のJSONから読む。番号から組み立てない
- claudeは引数でプロンプトを渡さず、非対話のフラグも付けない
- 完了は、背景のタブなら`--status done`、ユーザーが見ているタブなら`--status idle`で待つ
- 追加の指示も`herdr pane run <id> "<指示>"`で渡す
- 隣のペインを読むときは、`herdr pane neighbor --current --direction left`の`result.neighbor.neighbor_pane_id`を取り、`herdr pane read <id> --source recent-unwrapped --lines 300`で読む
- 自分が作っていないペイン・タブ・ワークスペースは閉じない。`herdr server stop`やメインプロセスのkillはしない

「ペインで進めて」と言われたときは、comicdev以外の作業でも、4と5を除いて同じ手順で別のエージェントを立てる。
既定は今のタブ・今の作業ディレクトリの隣のペインで、ワークスペース・タブ・worktreeはユーザーが言ったときだけ作る。

## 動作確認

画面の確認・ログの確認・`rails console` も comicdev の worktree で行う。ローカルには実行環境を作らない。

- 画面: worktree の `HTTP_PORT`（`scripts/setup-worktree-docker.sh` が `.env` に生成する）で開く
- ログ: `log/development.log`
- DB とモデルの確認: `docker compose run --rm web bundle exec rails runner` または `rails console`

ステージング・本番のデータ確認は Metabase を使う。ssh は要らない。

本体の開発環境（`https://sa2.comicdev.iowl.jp/`）は`bash ~/denebola/launch_denebola.sh`で起動する。画面（Next.js）は`~/denebola`、APIは`~/web-application`にある。

- 起動直後の最初のリクエストはNext.jsの初回のコンパイルで30秒以上かかり、タイムアウトすることがある。2回目で通る

## ssh コマンドの叩き方

ローカルから直接 ssh を叩くのは、ペインを立てる前の下調べ（worktree の一覧、ブランチの有無、
`sync-comicdev.sh` の取り込み）に限る。編集・テスト実行・画面確認は comicdev のペインの claude に渡す。

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
- `git worktree remove --force`がdockerの作ったroot所有のファイルで`Permission denied`になっても、gitの登録は外れ、ブランチのロックも解ける。残るのはディスク上のファイルだけ。`git worktree list`と`ls -d <パス>`の両方を見て、「登録は外れた／ファイルは残っている」を分けて報告する。ファイルは`sudo rm -rf <パス>`をユーザーに頼む

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
  primary と同じホスト名を同時に割り当てると取り合いになる。
  - worktreeで`scripts/docker-worktree.sh up`を実行して80番を取り、公開ホスト名で開く。80番を持つ本体のスタックは止まるので、ほかのセッションが使っていないか先に確かめる。戻すときは本体のディレクトリで`docker compose up -d`
  - Coreは`entry_form_url`をhttpsだけ受け付ける。httpのlocalhostでは申込が422になる
  - `APP_HOST_NAME`は公開ホスト名にし、webだけでなくwebpackのサービスにも渡す。webpackの3035番もホストへ公開する。画面のJSの取得先がこの値で決まり、localhostのままでは画面のJSが動かない
  - `.env`は読み書きが許可されていないので、これらは`docker-compose.override.yml`のenvironmentで上書きする
- 入会と都度課金の確認ページは申込の前提（コースの指定やセッション）が要る。前提が無いと 302 で入口へ戻る
- comicdevのヘッドレスブラウザから、公開ホスト名の開発環境と、e-SCOTTのテスト環境（`https://www.test.e-scott.jp`）の両方に届く。カードのE2Eのブラウザ操作は、Claudeが実行できる前提で計画する

## 開発環境のデータ

worktree の DB は独立で、`db:seed` だけではユーザーもコースのマスタも入らない。本体の
development DB をボリュームごとコピーすると揃った状態から始められる。

```bash
docker run --rm -v <primary>_dbdatastore:/from -v <worktree>_dbdatastore:/to alpine cp -a /from/. /to/
```

このコマンドの `cp -a` の引数は、元の記録に無かったものを補った形で、動かしては確かめていない。初めて使うときは、コピー先のボリュームの中身を確かめる。

## comicdevの停止と再開

comicdevはAWSの予定で毎日20:00に止まり、9:00に起動する。止まるとHerdrのサーバーごと終わり、ペインのエージェントとバックグラウンドの処理も終わる。

- 19:55にcronで`herdr server stop`を流し、タブの状態を保存してから止まるようにしている。ログは`~/herdr-logs/server-stop.log`
- 30分以上かかる並列のレビュー・E2E・バッチは、20:00をまたがないように始める。またぐなら、結果をファイルに書くよう最初に指示する
- 朝にHerdrへ繋いだら`herdr-restore`を1回打つ。`~/.claude/herdr-sessions/`に残ったセッションを、タブ名ごとに開き直す
- 途中のセッションは、そのワークツリーで`claude --resume <セッションID>`を起動すると続きから再開できる

## comicdevでのMCPの認証

OAuthのMCP（Datadog・Todoistなど）は、許可した後に`http://localhost:<ポート>/callback?...`へ戻ろうとし、ローカルのブラウザでは接続できない画面になる。

- 接続できない画面のアドレス欄のURLを丸ごとClaudeに貼り、認証を終える
- 古い認証URLで出たcallbackは使えない。毎回出し直したURLで許可する
- DatadogのMCPは、組織の設定で書き込みが無効。読み取りだけ

## 解説資料（explainer）

- 置き場所は`~/explainer-docs/<資料名>/`（web-applicationの外）。Node 24はnvmの`~/.nvm/versions/node/v24.21.0/bin`をPATHに足す。検証は`~/explainer-docs`で`verify-doc.mjs`を流す
- 抜粋の照合元は、ワークツリーでなくコミットから`git archive`で取り出したものに固定する。ワークツリーを消すと検証が壊れる
- 本文のファイル・仕様書・チケットは、コミットを固定したGitLabのURLと行番号、JIRAへのリンクにする
- 資料はJIRAに貼ってチームが読む前提で書く。想定読者に個人名を書かない

## Herdrの設定

- 手元のHerdr UIには、comicdevを保存済みSSHマシン（ラベル`comicdev`、`herdr machine add --label comicdev comicdev-herdr`）として登録してある。サイドバーのcomicdevの下にworkspaceを作れる。キー割り当てはEC2側を使うよう`config-gpui.local.toml`の`[devices.<ID>]`に`keybindings = "server"`を入れてある
- comicdevへは`herdr --remote comicdev-herdr --remote-keybindings server`で繋ぐ。この接続では`[keys]`と`[[keys.command]]`もEC2側の`config.toml`から読まれ、手元の`[keys]`は使われない
- キー割り当ての正本は手元の`config.toml`の`[keys]`以下。`~/.local/bin/herdr-sync-keys`でEC2側へ写してreload-configする。EC2側の`[keys]`は直接編集しない
- `[terminal]`・`[ui]`・`[theme]`・`[experimental]`はサーバー側（EC2）が読む
- 誤ったテーブルに書いた項目は警告なしで捨てられ、`herdr server reload-config`は成功を返す。書く前に`herdr --default-config`で項目の属するテーブルを確かめ、反映は挙動で確かめる
- `herdr agent focus`の対象はタブ名では通らない。`herdr agent rename <ペインID> <名前>`で名前を付けてから指定する
- `herdr update`はherdrの外で実行する（セッション内では拒否される）
- comicdevのHerdrの通知は、`[ui.toast] delivery = "terminal"`でMacの端末へOSC 9/777として送り、端末がデスクトップ通知にする。裏のタブのClaudeが完了か入力待ちになったときに出る。sshなら届き、moshでは届かない。Slackなどのwebhookには送らない

## reviewr

- 対象のリポジトリは、開いた時点でフォーカスしていたペインの作業ディレクトリで決まる。ワークツリーに入ってから`herdr plugin action invoke open --plugin persiyanov.reviewr`で開き直す（開いていれば先に`close`）
- 開き直したら`herdr pane list --workspace <ws>`で作業ディレクトリがワークツリーになっているか確かめる
- コメントは送る前に閉じると消える

## comicdev 側の Claude の設定

comicdev の `~/.claude/CLAUDE.md` はローカルとは別に持ち、自動メモリはオフにしている。
ローカルとの差分は `claude/sync-comicdev.sh` で確かめる。置き場所の分け方は `claude/README-claude-config.md`
