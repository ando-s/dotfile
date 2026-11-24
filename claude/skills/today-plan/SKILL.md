---
name: today-plan
description: 今日やるべきことを Todoist・Google カレンダー・Jira・GitLab の対応待ちの MR・Nuts のマイルストーン計画から集め、今日のボード（Artifact）に出す。済んだものも並べるので、日中に呼べば進み具合の整理にもなる。「今日やるべきこと」「今日の予定まとめて」「今日のタスク」「今日の進捗」「今の状況を整理して」「/today-plan」と言われたときに使う。質問せず最後まで進める。
---

# 今日やるべきこと

Todoist・カレンダー・Jira・GitLab・Nuts の計画を読み、今日の予定・優先順位・済んだものを、毎回同じ URL の Artifact「今日のボード」に出す。読むだけで、Todoist・カレンダー・Jira・GitLab は変更しない。

## 集めるもの

| 元 | 取り方 | URL の形 |
| --- | --- | --- |
| Todoist の今日＋期限切れ | `mcp__todoist__find-tasks-by-date`（`startDate: "today"`, `overdueOption: "include-overdue"`, `limit: 50`）。先に `ToolSearch` で `select:mcp__todoist__find-tasks-by-date,mcp__todoist__find-activity,mcp__todoist__user-info,mcp__claude_ai_Google_Calendar__list_events` を読み込む。`hasMore` が true なら `cursor` で続きを取る | `https://app.todoist.com/app/task/<id>` |
| カレンダーの今日 | `mcp__claude_ai_Google_Calendar__list_events`（`startTime`/`endTime` を今日の 00:00:00〜23:59:59、`orderBy: "startTime"`） | 結果の `htmlLink` |
| Jira（自分担当） | `~/.claude/skills/today-plan/scripts/jira_mine.sh`（関わる 12 プロジェクトを回す。`jira issue list -q` は既定プロジェクトの条件が付くので直接使わない）。出力は KEY・状態・期日・題名 | `https://comicfesta.atlassian.net/browse/<KEY>` |
| GitLab の対応待ち MR | `~/.claude/skills/today-plan/scripts/gitlab_required.sh`（`Required(s-ando)` のラベルが付いた開いた MR を comic-festa-group 全体から、更新の古い順に）。出力は種類（`review` = 他の人の MR、`own` = 自分の MR）・参照・著者・題名・URL。Todoist に入れていないので、ここが唯一の元 | 出力の URL |
| Todoist の今日済んだもの | `mcp__todoist__user-info` で自分の ID と今の時刻を取り、`mcp__todoist__find-activity`（`objectType: "task"`, `eventType: "completed"`, `initiatorId`, `dateFrom`/`dateTo` を今日の 00:00〜翌日 00:00 の `+09:00`）。work のプロジェクトの分だけ使う | `https://app.todoist.com/app/task/<objectId>` |
| Nuts の計画で今週に掛かるもの | `~/Documents/nuts/スケジュールの計画/Nuts移行_マイルストーン計画.html` の最新 template の JSON（`class="plan-data"`）を読み、`people[].bars` のうち今日を含む週に開始・終了する帯と、`methods[].switch` が今週の手段。4 の「判断・確認をお願いしたいこと」の箇条書きも拾う | 計画: `https://claude.ai/artifact/LYhTzR1KmusBCA4AFzQram`、ガント: `https://docs.google.com/spreadsheets/d/1PvTSmnE_not_5XseWG6pYBYZBOUXJ6ZHjfEyf2PVy5M` |

今日の日付は `date +%Y-%m-%d` で取る。土日・祝日でも、呼ばれたら同じ手順でまとめる。冒頭に「今日は休み」と書き添える（祝日は `~/.claude/skills/nuts-milestone-plan/scripts/check_holidays.py` の JP_HOLIDAYS を参照）。

## 組み立て

対象は Todoist の work のプロジェクトだけ。private・input・Inbox は載せない。繰り返しでないタスクを、上から順に当てはめて 1 つの列に入れる。

| 列（JSON のキー） | 入れるもの |
| --- | --- |
| 今日中に決める・動かす（`now`） | Jira の課題（期日が近いか進行中）。Todoist は「脳みそ労力高」で、「緊急度高」か「重要度高」があるもの |
| MR の対応待ち（`mr`） | GitLab の `Required(s-ando)` の MR。レビューを先、自分の MR を後に。タグに「レビュー」「自分のMR」と著者（「深川さん」）を付け、題名が「WIP」「作成中」なら `warn` のタグを足す |
| 連絡・確認（`contact`） | Todoist の「脳みそ労力低」で、「緊急度高」か「重要度高」があるもの。「連絡待ちリスト」「検証中リスト」はタグにする |
| 済んだ（`done`） | 今日完了にした work のタスク。`time` は完了の時刻、新しい順 |
| 明日以降に回せそう（`later`） | 緊急度・重要度とも低いもの。期日を動かす候補として、ボードでは畳んで出す |

- 列の中は、期限を過ぎたもの → 時刻のあるものを時刻順 → 時刻のないもの、の順に並べる
- 題名に書かれた締め切りや、Jira・計画の終了日を過ぎているものは、`level: "crit"` と「締め切り 11/22 を過ぎている」のようなタグを付ける。「緊急度高」は `warn` のタグにする
- 題名の Markdown のリンクや URL は外し、言い切りの短い題名に整える。誤字は直す
- `why` には、どう動くかを制約だけで 1 文書く（例「残りは返金・検知。閉じるか期日を動かすかを朝会で決める」）。全部に付けない
- 繰り返しのタスクは「毎日のもの」（`routine`）に、時刻と短い題名で並べる
- 予定（`events`）は自分が辞退した会議を除き、時刻順。出欠が未回答のものは `note` に書く
- Nuts の計画で今週に掛かるもの（`nuts`）は、帯の始まり・終わり、切り替え、人の離任・参加。「判断・確認をお願いしたいこと」から、今日の会議で進められそうなものを 1〜2 件足す
- `note` には休み・祝日の後などの前提を 1 文で書く。土日・祝日なら「今日は休み」

## 出し方

1. 上の内容を、下の形の JSON にして scratchpad に書く
2. `python3 ~/.claude/skills/today-plan/scripts/build_board.py <JSON> <scratchpad>/today-board.html` で HTML にする
3. Artifact で公開する。公開先は毎回同じ `https://claude.ai/artifact/XKBKh28fkmuD7vxmR4DbfD`。別の会話からは、先に `action: "read"` で読み、`url` にこの URL を渡して公開する。`icon` は渡さない
4. チャットには、ボードのリンクと、最初に手を付けるもの 1〜3 件だけを書く（5 行以内）。取れなかった元があれば直し方を 1 行添える

JSON の形（`board/template.html` が読む）:

```json
{
  "date": "2026-11-24", "dateLabel": "11/24（火）", "generatedAt": "10:45",
  "note": "月曜が祝日だったため今週の初日",
  "events": [{"start": "11:00", "end": "11:30", "title": "Nuts朝会", "url": "htmlLink", "note": "出欠が未回答"}],
  "columns": {
    "now": [{"title": "NTMS-42 AF クレカ", "url": "…", "source": "jira", "time": "14:00",
             "tags": ["進行中", {"text": "計画の終了 11/2 を過ぎている", "level": "crit"}],
             "why": "閉じるか期日を動かすかを朝会で決める", "level": "crit"}],
    "mr": [], "contact": [], "done": [], "later": []
  },
  "routine": [{"time": "09:00", "title": "ガントチャート更新"}],
  "nuts": [{"title": "鈴木さんの受け入れ（11/2〜11/27）", "detail": "今週の金曜で終わる", "url": "…"}],
  "links": [{"label": "マイルストーン計画", "url": "https://claude.ai/artifact/LYhTzR1KmusBCA4AFzQram"},
            {"label": "ガントチャート全体", "url": "https://docs.google.com/spreadsheets/d/1PvTSmnE_not_5XseWG6pYBYZBOUXJ6ZHjfEyf2PVy5M"}],
  "missing": [{"source": "Jira", "fix": "jira init で認証し直す"}]
}
```

- `source` は `todoist`・`jira`・`gitlab` のどれか。`level`・タグの `level` は `warn` か `crit`
- `generatedAt` は今の時刻。ボードはこの時刻で、終わった予定と毎日のものを薄く出し、今の位置に線を引く

## 書き方

- 日本語。人は「深川さん」「鈴木さん」「正社員」。自分は「安藤」と書かず主語を省く
- 誇張しない。「至急」「必ず」を使わない。重要度は並び順で示す
