---
name: daily-review-loop-operation
description: daily-review は OS cron ではなくセッション内 /loop（CronCreate）で回す運用。レポート命名が次回の基準時刻になる
metadata: 
  node_type: memory
  type: project
  originSessionId: c150bc7a-6c0b-441b-b1a8-b618ceb71b36
---

daily-review（会話履歴の自己振り返りレポート）のセットアップ状況（2026-06-12 導入）:

- スキル実体: `~/.claude/skills/daily-review/`（SKILL.md + scripts/）。dotfiles 連携なし、直置き
- 定期実行: ユーザー指示により **OS cron は未登録**。セッション内の /loop（CronCreate、毎朝 9:20 JST = 0:20 UTC）で実行する運用
- セッション cron は 7日で自動失効・セッション終了で消える → 新セッションで再開する場合は CronCreate を再登録するか `/loop` を再実行
- 無人実行用 `run_daily_review.sh`（headless claude -p）は予備として残置
- 完了時に Slack 通知（SKILL.md 手順5）: `scripts/notify_slack.sh` が web-application/.env の `SLACK_URL_TOKEN`（legacy incoming webhook、channel上書き可）で @s-ando の DM に送信。チーム channel（#spica_app_log 等）には送らない
- レポート（`~/.claude/daily-review/reports/review_YYYYMMDD_HHMMSS.md`）のファイル名が次回抽出の基準時刻。命名規則を崩さない
- このマシンのシステム時刻は UTC（JST との変換に注意）
