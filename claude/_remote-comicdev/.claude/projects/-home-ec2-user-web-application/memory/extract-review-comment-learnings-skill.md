---
name: extract-review-comment-learnings-skill
description: レビューコメントから学びを収集してAIドキュメントへ反映する個人運用skill（extract-review-comment-learnings、旧harvest-review-learnings）の所在と設計判断
metadata: 
  node_type: memory
  type: project
  originSessionId: 68c27bd9-42c3-4382-9b6c-8d9ab225c80e
  modified: 2026-08-21T01:14:36.976Z
---

レビューコメント学び収集の skill `extract-review-comment-learnings`（旧名 `harvest-review-learnings`、2026-07-02にリネーム）。当初は**個人運用**（2026-06-12決定、`~/.claude/skills/`）だったが、2026-07-07のMR!16668で**チーム共有化**し `packs/nuts/.ai/skills/extract-review-comment-learnings/` へ移設・マージ済み。個人配下（`~/.claude/skills/`）に残っていた古いコピーは、同名のためチーム側を隠して優先読み込みされていた（手順5が「学びが1件以上ある場合」の旧仕様のまま。チーム側は「毎回・必ず作る」）。2026-08-21に `~/.claude/skills-disabled/` へ退避して解消済み。同名スキルが個人スコープとプロジェクトスコープに両方あると個人側が勝ち、チームの更新が届かない。`skillOverrides` では切り分けられない（キーが名前なので両方無効になる）ため、ディレクトリを `skills/` の外へ移す。導入用 MR !16464 はクローズ済み。`/loop` で定期実行する。

設計判断（変更時は理由を確認すること）:

- 収集対象は **マージ済み** + `Request Code Review(Nuts)` + `AI学び収集済` ラベルなし + **実行日の2週間前以降に作成**（デフォルト。過去分は `--since` 指定）
- 収集済み印はMR単位のラベル `AI学び収集済`（学びの有無を問わず付与。ラベル未作成、skill 初回実行時に作成）
- ラベル付与は `add_labels`（`update_mr.sh --labels` は置換方式なので使わない）
- 学びMRが未マージの間は新規実行をスキップ。ガードは**学びMRのタイトル前方一致**（`docs(nuts): レビューコメントからの学び反映`）で判定する（旧版はブランチ名前方一致だったが、skillリネームでブランチ命名も変わるため2026-07-02にタイトル判定へ変更。タイトルはリネームに影響されず安定）
- 学びの汎用化基準: 問題の構造で書く + 簡略化Good/Bad例1つ + 出典 `!IID`。保存先判断は review-update skill に従う
- 学びの反映先はチームの `packs/nuts/.ai/`（学びMRとしてレビューに出す）。個人運用なのは収集ツール側のみ
- 学びMR用ブランチ名は `feature/extract-review-comment-learnings-YYYYMMDD`（旧 `feature/harvest-review-learnings-YYYYMMDD`）

**週次永久loop運用**（2026-07-02設定）: セッション内CronCreateで毎週月曜9:42に `/loop 1週間に1回 /extract-review-comment-learnings` を実行。発火のたびに自分自身を再CronCreateして継続する自走ループ（[[daily-review-loop-operation]] [[memory-retrospective-operation]]と同方式）。7日失効・セッション終了で消える制約は同じ。当初はclaude.aiのスケジュール済みクラウドエージェント(routine)化も検討したが、個人skill（`~/.claude/skills/`）にクラウド環境からアクセスできない・glabの本人名義認証が引き継がれるか不明という理由で見送り、セッション内loop方式を採用した（skillはその後チーム共有化されたが、session-onlyの運用方針自体は変えていない）。

**/loopのcloud勧誘プロンプトには毎回答えない**: `/loop`スキル側に「間隔が長い/毎日系の文言なら都度AskUserQuestionでcloud化を勧める」仕様が入っているが、本loopで複数回連続して同じ質問をしたところ「再設定済みなら聞かないでよ」と明示指摘された（2026-07-22）。本loopは**session onlyで確定運用**とし、以後この質問はスキップして直接CronCreateへ進む。

関連: [[no-auto-reply-mr-comments]]（収集元MRへの返信・resolveはしない）、[[extract-review-comment-learnings-dedup-check-depth]]
