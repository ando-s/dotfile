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
ローカル生成物（weekly-rules の材料と案。これらはこのリポジトリの外、
`~/.claude/weekly-rules/` 配下に置かれる）が紛れ込んでいないか確認
すること。

## このリポジトリが実装している主要ワークフロー

- **AI-TDD**（`claude/skills/tdd-orchestrator/` + `claude/agents/tdd-*.md`）:
  `/tdd-orchestrator path/to/plan.md` で起動し、Red→Green→Refactor を
  隔離 agent で1テストずつ直列実行する。詳細は `claude/docs/TDD-with-ai.md`。
- **weekly-rules**（`claude/skills/weekly-rules/`）: 直近1週間の会話から、
  ユーザーが Claude を直した場面を集め、規則の案にしてユーザーと1つずつ決める
  （自動適用はしない）。Todoist の毎週のタスクから `/weekly-rules` で呼ぶ。
- **Codex と Claude Code の分担開発**（`claude/templates/codex-claude/`）:
  新しいプロジェクトに `cp -Rn` でコピーして使う雛形。詳細は
  `claude/docs/codex-claude-workflow.md`。
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
