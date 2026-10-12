# dotfile

個人用のドットファイル管理（Claude Code 設定・tmux 設定）。

## 構成

```
dotfile/
├── claude/
│   ├── CLAUDE.md     # ~/.claude/CLAUDE.md に symlink（個人グローバル設定）
│   ├── skills/       # ~/.claude/skills/ に symlink される
│   ├── agents/       # ~/.claude/agents/ に symlink される
│   ├── docs/         # ワークフロー説明（人間向け）
│   └── templates/    # プロジェクトにコピーして使う雛形（install.sh では入れない）
├── tmux/
│   └── .tmux.conf    # ~/.tmux.conf に symlink される
└── install.sh        # symlink セットアップ（idempotent）
```

## セットアップ

```bash
bash install.sh
```

Claude Code 起動中の場合は **再起動**（agent / skill list は起動時固定）。

## 含まれるもの

### 個人グローバル設定

- `claude/CLAUDE.md` — 全プロジェクト共通の個人的好み（コミュニケーションスタイル・開発方針）

### AI-TDD ワークフロー

- skill: `tdd-orchestrator` — Red→Green→Refactor を隔離 agent で直列実行
- agent: `tdd-test-writer` — Red 専用
- agent: `tdd-implementer` — Green 専用
- agent: `tdd-refactorer` — Refactor 専用
- doc: `claude/docs/TDD-with-ai.md` — ワークフロー全体の説明

詳細・運用方針: `claude/docs/TDD-with-ai.md`

### Codex と Claude Code の分担開発

- doc: `claude/docs/codex-claude-workflow.md` — 役割分担、Herdr での依頼と見届け、文書の置き場所、方針変更の手順、確認の分け方
- template: `claude/templates/codex-claude/` — `AGENTS.md`、`CLAUDE.md`、スキル（`delegate-to-codex`・`decision-change`）、文書チェックの Stop フック、`docs/` の雛形

導入: `cp -Rn ~/dev/dotfile/claude/templates/codex-claude/. <プロジェクト>` の後、`<project>` などの置き換え（手順は doc の末尾）

### tmux 設定

- `tmux/.tmux.conf` — `~/.tmux.conf` に symlink される
