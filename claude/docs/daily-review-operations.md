# daily-review 運用ガイド

Claude Code の会話履歴を毎朝自動分析し、スキル化・サブエージェント化・CLAUDE.md改善・
permissions追加の候補をレポートとして受け取り、採用したものだけ反映して Claude を育てる運用。

参考: https://zenn.dev/wwwave/articles/15a92d77ad40d7

## 構成

| 役割 | 場所 |
|------|------|
| スキル本体 | `claude/skills/daily-review/SKILL.md` |
| 会話履歴の抽出 | `claude/skills/daily-review/scripts/extract_conversations.py` |
| 無人実行ラッパー | `claude/skills/daily-review/scripts/run_daily_review.sh` |
| ダイジェスト（中間生成物） | `~/.claude/daily-review/digest.md` |
| レポート出力先 | `~/.claude/daily-review/reports/review_YYYYMMDD_HHMMSS.md` |
| 実行ログ | `~/.claude/daily-review/logs/run_YYYYMMDD.log` |

分析対象は全プロジェクト横断（`~/.claude/projects/*/*.jsonl`、新しい順に最大15ファイル）。
分析の基準時刻は「直近レポートのファイル名」から自動決定するため、**レポートの命名規則を崩さないこと**。

## 1日の流れ

1. **朝（自動）**: Automator カレンダーアラームが `run_daily_review.sh` を起動
   → headless Claude（`claude -p`）が `/daily-review` を実行 → レポート出力
2. **朝イチ（人間・5〜10分）**: レポートを読み、提案の採否を判断
3. **採用分の反映**: Claude に依頼して実施（スキル作成・CLAUDE.md追記・permissions追加等）
4. **日中**: 普段どおり作業 → 会話履歴が蓄積 → 翌朝の分析対象になる

セッション内でレポートの確認を定期化する場合は `/loop` を使う:

```
/loop ~/.claude/daily-review/reports/ に未確認の新しいレポートがあれば読んで要点を提示して
```

## セットアップ（新マシン）

1. リポジトリ直下で `./install.sh` を実行（skills/agents/CLAUDE.md のシンボリックリンクを作成）
2. Automator.app で「カレンダーアラーム」を新規作成し、「シェルスクリプトを実行」に以下を設定:

   ```bash
   bash "$HOME/.claude/skills/daily-review/scripts/run_daily_review.sh"
   ```

3. 保存時にカレンダーへ作られるイベントを毎朝の繰り返し予定に変更

## 運用ルール

- **採否は必ず人間が判断する**。スキルは提案のみで、settings.json や CLAUDE.md を自動編集しない
- 採用した改善は dotfile 管理下のファイルに反映し、コミットして同期する
- レポート・ログ・digest はローカル生成物なので dotfile にはコミットしない

## ⚠️ 注意点

- `run_daily_review.sh` は無人実行のため `--dangerously-skip-permissions` を使う。
  スキルの操作範囲（python3 / mkdir / レポートWrite）を超える変更を SKILL.md に加える場合は、このフラグの妥当性を再評価すること
- レポートのファイル名タイムスタンプは**ローカル時刻**。抽出スクリプトもローカル時刻として解釈する（UTC扱いにすると基準時刻が9時間ズレて取りこぼす）

## トラブルシュート

- レポートが生成されない → 当日の実行ログを確認。`claude` の認証切れ・PATH 不足が典型
- 「前回以降の活動なし」が続く → レポートファイル名の改変や手動作成で基準時刻が未来に飛んでいないか確認
- 手動で即実行したい → 対話セッションで `/daily-review`、または `run_daily_review.sh` を直接実行
