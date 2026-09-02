---
name: herdr-pane-claude-agent-workflow
description: Herdrペインでclaudeエージェントを立てて作業を進める手順（「paneで」と言われた時）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 08798370-e24b-4069-b5c6-309d2c159e40
---

ユーザーが「paneで」「ペインで進めて」と言ったら、Herdr のペインに別エージェントを立てて作業させる。

**Why:** 作業を Herdr のワークスペース/タブ/ペインに整理し、ユーザーが横で進捗を見られる・別エージェントに並行作業を委ねられるようにするため。

**How to apply:**

1. 前提確認: `test "${HERDR_ENV:-}" = 1`。満たさなければ「Herdr外なので不可」と伝えて止める。`herdr`バイナリがCLI。構文は `herdr --help` と各コマンド群（`herdr pane` 等を引数なしで）で確認する。バイナリが正典（バージョンで構文が変わる）。
2. herdr スキル（`~/.claude/skills/herdr`）を読み込んでから操作する。
3. 既定トポロジは**現タブ・現cwdの兄弟ペイン**。ワークスペース/タブ/worktree/別cwdはユーザーが明示した時だけ作る。
4. レイアウト確認 `herdr pane layout --pane "$HERDR_PANE_ID"` → 横長なら右、縦長なら下に分割。ユーザーのフォーカスは呼び出しペインに残す:
   `herdr pane split --current --direction right --no-focus`
5. JSON応答の `result.pane.pane_id` を読む（IDは不透明文字列。番号から組み立てない）。`herdr pane rename <id> "reviewer"` でラベル付け。
6. エージェント起動は素の実行ファイルを渡して対話TUIを開く: `herdr pane run <id> "claude"`（Claude Code。Codexは`codex`、piは`pi`）。引数でプロンプトを渡さない・非対話フラグを付けない。
7. `herdr wait agent-status <id> --status idle --timeout 30000` で待ってから、タスクを `herdr pane run <id> "<タスク文>"` で投入（send-text/send-keysでなくpane runがEnterまで送る）。
8. 完了待ち: 背景タブなら `--status done`、ユーザーが見ているタブなら `--status idle`。読み取りは `herdr pane read <id> --source recent-unwrapped --lines 120`（ログ/transcriptはunwrapped）。
9. 追撃も `herdr pane run <id> "<次の指示>"`。

**安全:** `--no-focus`と`--current`/明示ID。自分が作っていないペイン/タブ/ワークスペース/セッションは閉じない。`herdr server stop`・メインプロセスkillはしない。
