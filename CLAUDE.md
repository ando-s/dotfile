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

### AI-TDD（`tdd-orchestrator` skill + 3 agent）

背景・根拠の全文は `claude/docs/TDD-with-ai.md` にある。核となる考え方は、
各フェーズの AI に必要最小限しか見せないことで、既存コードに「引きずられ」
たり、現在のテストより先の実装を見越したりできないようにすること。

- `tdd-orchestrator`（skill、`disable-model-invocation: true`、
  `/tdd-orchestrator path/to/plan.md` で明示的に起動）: 人間が書いた
  `plan.md` を読み、`Task` ツール経由で Red → Green → Refactor を1項目ずつ
  直列実行し、`plan.md` を更新していく。
- `tdd-test-writer`（agent、Red 担当）: 失敗するテストを1つだけ書く。
  実装ファイル本体や他のテスト項目は読めない。
- `tdd-implementer`（agent、Green 担当）: そのテストを通す最小実装のみを
  書く。他のテスト/実装ファイル全体を読んだり、依頼外の機能を追加したり
  できない。
- `tdd-refactorer`（agent、Refactor 担当）: 直前の実装を振る舞いを変えずに
  改善する、または「変更なし」と明示して終える。

orchestrator が強制するルール: 1サイクル1テスト、同一テストで Green が
3回連続失敗したら人間にエスカレーション、「テストを削除/skip して通す」
という兆候が出たら即エスカレーション、`plan.md` のテスト一覧は先読みせず
上から順に消化する。`plan.md` は AI が生成するのではなく人間が書き、
対象機能のあるプロジェクト側に置く（このリポジトリには置かない）。

### daily-review（`claude/skills/daily-review/`）

Claude Code 自身の会話履歴（全プロジェクト横断の
`~/.claude/projects/*/*.jsonl`）を分析し、新しい skill・subagent・
`CLAUDE.md` への追記・`settings.json` の permissions 追加を*提案のみ*行う
（自動適用はしない）。詳細と Automator/cron のセットアップ手順は
`claude/docs/daily-review-operations.md` を参照。

- `scripts/extract_conversations.py` は生の jsonl が巨大すぎて直接読めない
  ため、圧縮したダイジェスト（`~/.claude/daily-review/digest.md`）を生成
  する。基準時刻（since）は既定で直近レポートのファイル名タイムスタンプ
  （ローカル時刻。UTC ではない — ハマりどころとして明記されている）から
  決まる。レポートファイル名を `review_YYYYMMDD_HHMMSS.md` の命名規則から
  外すと、この基準時刻の取得が壊れる。
- `scripts/run_daily_review.sh` は無人実行用のエントリポイント
  （`claude -p ... --dangerously-skip-permissions`）で、カレンダーアラーム
  や cron から起動される想定。skill の操作範囲が python3/mkdir/date/
  echo/レポート Write を超えて拡張される場合は、
  `--dangerously-skip-permissions` の妥当性を再評価すること。
- レポート/ログ/digest はローカルの生成物（`~/.claude/daily-review/` 配下）
  であり、このリポジトリには絶対にコミットしない。

### ouen-message（`claude/skills/ouen-message/`）

`~/.slack/send-ouen.sh`（このリポジトリ外のスクリプト）経由で、時間帯に
応じた応援メッセージを Slack に送る。トーン・文面のルールは `SKILL.md`
内で時間帯テーブルとして定義されている。

## このリポジトリで編集する際の規約

- リポジトリ内の地の文は日本語。既存ファイルが英語である場合を除き、
  新規/編集する doc・skill 本文・agent 本文は日本語で書く。
- *このリポジトリで作業する際*に生成するコミットメッセージ・PR 説明・
  設計ドキュメントは、`claude/CLAUDE.md` に書かれたスタイル規約（結論を
  先に・箇条書き中心・ファイルパスやコマンドやコードは地の文に埋め込まず
  別のコードブロックにする）に従う。これらは本来「個人グローバル設定」
  だが、ユーザーは dotfile リポジトリ自体の作業にも適用している。
