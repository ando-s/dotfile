# starbase 向け個人設定（profile: ando）

`~/dev/spica/starbase` の指示で進める作業に使うプロファイル `ando` の設定。
`CLAUDE_CONFIG_DIR=~/.config/claude/profiles/ando` で起動したセッションだけが読む。
全プロジェクト共通の設定は `claude/CLAUDE.md`（`~/.claude/CLAUDE.md`）にある。
web-application を触るときの決めごとは `claude/docs/web-application-workspace.md`。このプロファイルには書かない。

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
