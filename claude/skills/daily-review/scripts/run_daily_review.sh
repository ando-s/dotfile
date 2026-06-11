#!/bin/bash
# 毎朝の daily-review 自動実行用スクリプト。
# Mac の Automator「カレンダーアラーム」アプリ or launchd/cron から呼び出す。
#
# Automator 設定手順（カレンダー連動）:
#   1. Automator.app を開き「カレンダーアラーム」を新規作成
#   2. アクション「シェルスクリプトを実行」を追加
#   3. シェル: /bin/bash / 内容に下記1行を貼る:
#        bash "$HOME/.claude/skills/daily-review/scripts/run_daily_review.sh"
#   4. 保存するとカレンダーに該当イベントが作られるので、毎朝の繰り返し予定にする
#
# 注意: Automator/cron は環境変数が最小なので PATH を明示する。

set -uo pipefail

# claude CLI と node 等が入っているパスを明示的に通す
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

LOG_DIR="$HOME/.claude/daily-review/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/run_$(date +%Y%m%d).log"

{
  echo "===== daily-review 開始: $(date '+%Y-%m-%d %H:%M:%S') ====="

  # 任意のプロジェクトディレクトリで実行（cwd は分析対象に影響しない。スクリプトが全プロジェクト横断する）
  cd "$HOME" || exit 1

  # headless 実行。無人実行なので承認プロンプトで止まらないよう権限スキップ。
  # スキル内の操作は python3 / mkdir / Write(レポート) のみで、破壊的操作は含まない。
  claude -p "/daily-review を実行してレポートを生成して" \
    --dangerously-skip-permissions \
    2>&1

  echo "===== daily-review 終了: $(date '+%Y-%m-%d %H:%M:%S') ====="
  echo "最新レポート:"
  ls -t "$HOME/.claude/daily-review/reports/" 2>/dev/null | head -1
} >>"$LOG_FILE" 2>&1
