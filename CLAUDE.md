# CLAUDE.md

このファイルは、このリポジトリで作業する Claude Code (claude.ai/code) への
ガイダンスを提供する。

## このリポジトリについて

Claude Code の設定（skill・agent・個人グローバル `CLAUDE.md`）と tmux 設定を
管理する個人用 dotfile リポジトリ。アプリケーションコード・ビルド・テストは
存在しない。このリポジトリの「成果物」は、`~/.claude/` と `~/.tmux.conf` に
symlink されるファイル一式だけである。リポジトリ内の地の文（doc・skill/agent
本文・README）はほぼ日本語で書かれている。

## リポジトリ構成

```
dotfile/
├── claude/
│   ├── CLAUDE.md      # ~/.claude/CLAUDE.md に symlink — 個人グローバル設定。このマシンの全プロジェクトに適用される
│   ├── skills/<name>/SKILL.md   # ディレクトリごと ~/.claude/skills/<name> に symlink
│   ├── agents/<name>.md         # ~/.claude/agents/<name>.md に symlink
│   └── docs/          # 人間向けワークフロー説明（どこにもインストールされない）
├── tmux/.tmux.conf    # ~/.tmux.conf に symlink
└── install.sh         # idempotent な symlink セットアップ
```

**`claude/CLAUDE.md` とこのファイルを混同しないこと。** このファイル
（リポジトリ直下の `/CLAUDE.md`）は、dotfile リポジトリ自体で作業する
Claude Code セッションのために*このリポジトリ*を説明するものである。
`claude/CLAUDE.md` は別物で、ユーザーの個人グローバル指示（回答スタイル、
社内 GitLab のホスト名などの環境固有の前提）を書いたファイルであり、
`~/.claude/CLAUDE.md` に symlink されて*このマシンの他の全プロジェクト*に
適用される。グローバルな振る舞いの変更は `claude/CLAUDE.md` に、この
リポジトリ自体の運用に関する変更はこのファイルに書く。

## コマンド

```bash
bash install.sh
```

idempotent。`claude/skills/*/`・`claude/agents/*.md`・`claude/CLAUDE.md`・
`tmux/.tmux.conf` をそれぞれ `~/.claude/` / `~/.tmux.conf` に symlink する。
既存の非 symlink ファイルや、別のリンク先を指す symlink は上書きせず、
`[WARN]` を出してそのままにする。

lint / test / build コマンドは存在しない。CI もない。

**skill・agent を追加/変更した後は、Claude Code セッションの再起動が必要**。
skill/agent 一覧はセッション起動時に固定されるため、`install.sh` を再実行
しても反映されない。

## 編集の考え方

インストールされる各ファイルは、正本がこのリポジトリ側にある symlink で
ある。編集は必ず `claude/`（または `tmux/`）配下の実体に対して行い、
`~/.claude/...` や `~/.tmux.conf` 側（symlink 先）を直接編集しないこと。
symlink なので実体を触ってもリポジトリの作業ツリーが変わるだけではあるが、
概念上はこのリポジトリを正とし、ここでコミットする。

`.gitignore` は `__pycache__/` のみを除外している。コミット前に、他の
ローカル生成物（daily-review のレポート/ログ/digest。これらはこのリポジトリ
の外、`~/.claude/daily-review/` 配下に置かれる）が紛れ込んでいないか確認
すること。

## skill と agent の違い

- **skill**（`claude/skills/<name>/SKILL.md`）: ユーザー起動またはトリガー
  起動のエントリポイント（`/name`）。メインの会話コンテキストで動く。
- **agent**（`claude/agents/<name>.md`）: `Task` ツールから呼ばれる
  サブエージェント定義。隔離コンテキストで動く。YAML frontmatter
  （`name`・`description`・`model`・`tools`）で権限範囲を絞る。

## このリポジトリが実装している主要ワークフロー

- **AI-TDD**（`claude/skills/tdd-orchestrator/` + `claude/agents/tdd-*.md`）:
  `/tdd-orchestrator path/to/plan.md` で起動し、Red→Green→Refactor を
  隔離 agent で1テストずつ直列実行する。詳細は `claude/docs/TDD-with-ai.md`。
- **daily-review**（`claude/skills/daily-review/`）: Claude Code の会話履歴を
  分析し、改善案を*提案のみ*行う（自動適用はしない）。詳細は
  `claude/docs/daily-review-operations.md`。
- **ouen-message**（`claude/skills/ouen-message/`）: 時間帯に応じた応援
  メッセージを Slack に送る。

各ワークフローの手順・ルールは対応する `SKILL.md` / `docs/` に書かれている
ため、ここでは重複させない。

## このリポジトリで編集する際の規約

- リポジトリ内の地の文は日本語。既存ファイルが英語である場合を除き、
  新規/編集する doc・skill 本文・agent 本文は日本語で書く。
- *このリポジトリで作業する際*に生成するコミットメッセージ・PR 説明・
  設計ドキュメントは、`claude/CLAUDE.md` に書かれたスタイル規約（結論を
  先に・箇条書き中心・ファイルパスやコマンドやコードは地の文に埋め込まず
  別のコードブロックにする）に従う。これらは本来「個人グローバル設定」
  だが、ユーザーは dotfile リポジトリ自体の作業にも適用している。
