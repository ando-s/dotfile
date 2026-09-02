---
name: memory-retrospective-operation
description: メモリーの週次レトロスペクティブ運用。月曜 9:33 JST にセッション内cronで /memory-retrospective を実行し、スキル・ルール昇格候補を提案
metadata: 
  node_type: memory
  type: project
  originSessionId: 290911e0-c6fb-4165-9d9c-c4ccead3965d
---

memory-retrospective（メモリー週次レトロスペクティブ）のセットアップ状況（2026-06-12 導入）:

- スキル実体: `~/.claude/skills/memory-retrospective/SKILL.md`（個人運用、チームの `packs/nuts/.ai/` には載せない）
- 目的: プロジェクトメモリーを週次で棚卸しし、定着した学びをスキル・チームルール・個人CLAUDE.mdへ昇格、陳腐化したメモリーを整理する
- **提案のみ**のレポート型（[[daily-review-loop-operation]] と同じ思想）。昇格の反映・メモリー削除はユーザー承認後
- 定期実行: セッション内 CronCreate（毎週月曜 0:33 UTC = 9:33 JST）。OS cron は使わない（daily-review と同じユーザー指示に従う）
- セッションcronは7日失効のため、実行プロンプト内に次回分の再登録指示を含めている。セッション終了時は消えるので新セッションで再登録が必要
- レポート: `~/.claude/memory-retrospective/reports/retro_YYYYMMDD_HHMMSS.md`。ファイル名が次回の差分抽出（mtime比較）の基準時刻。命名規則を崩さない
- Slack通知は daily-review の `notify_slack.sh` を再利用（@s-ando の DM）
- 全件レトロは `--all` 引数で実行
