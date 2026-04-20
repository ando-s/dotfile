# dotfile

個人用の Claude Code 設定（skills / agents / docs）。

## 構成

```
dotfile/
├── claude/
│   ├── skills/       # ~/.claude/skills/ に symlink される
│   ├── agents/       # ~/.claude/agents/ に symlink される
│   └── docs/         # ワークフロー説明（人間向け）
└── install.sh        # symlink セットアップ（idempotent）
```

## セットアップ

```bash
bash install.sh
```

Claude Code 起動中の場合は **再起動**（agent / skill list は起動時固定）。

## 含まれるもの

### AI-TDD ワークフロー

- skill: `tdd-orchestrator` — Red→Green→Refactor を隔離 agent で直列実行
- agent: `tdd-test-writer` — Red 専用
- agent: `tdd-implementer` — Green 専用
- agent: `tdd-refactorer` — Refactor 専用
- doc: `claude/docs/TDD-with-ai.md` — ワークフロー全体の説明

詳細・運用方針: `claude/docs/TDD-with-ai.md`
