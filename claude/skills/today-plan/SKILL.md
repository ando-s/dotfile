---
name: today-plan
description: 今日やるべきことを Todoist・Google カレンダー・Jira・GitLab の対応待ちの MR・Nuts のマイルストーン計画から集め、URL 付きでチャットに出す。「今日やるべきこと」「今日の予定まとめて」「今日のタスク」「/today-plan」と言われたときに使う。質問せず最後まで進める。
---

# 今日やるべきこと

Todoist・カレンダー・Jira・GitLab・Nuts の計画を読み、今日の予定と優先順位をチャットの返答 1 つにまとめる。読むだけで、Todoist・カレンダー・Jira・GitLab は変更しない。

## 集めるもの

| 元 | 取り方 | URL の形 |
| --- | --- | --- |
| Todoist の今日＋期限切れ | `mcp__todoist__find-tasks-by-date`（`startDate: "today"`, `overdueOption: "include-overdue"`, `limit: 50`）。先に `ToolSearch` で `select:mcp__todoist__find-tasks-by-date,mcp__claude_ai_Google_Calendar__list_events` を読み込む | `https://app.todoist.com/app/task/<id>` |
| カレンダーの今日 | `mcp__claude_ai_Google_Calendar__list_events`（`startTime`/`endTime` を今日の 00:00:00〜23:59:59、`orderBy: "startTime"`） | 結果の `htmlLink` |
| Jira（自分担当） | `~/.claude/skills/today-plan/scripts/jira_mine.sh`（関わる 12 プロジェクトを回す。`jira issue list -q` は既定プロジェクトの条件が付くので直接使わない）。出力は KEY・状態・期日・題名 | `https://comicfesta.atlassian.net/browse/<KEY>` |
| GitLab の対応待ち MR | `~/.claude/skills/today-plan/scripts/gitlab_required.sh`（`Required(s-ando)` のラベルが付いた開いた MR を comic-festa-group 全体から、更新の古い順に）。出力は種類（`review` = 他の人の MR、`own` = 自分の MR）・参照・著者・題名・URL。Todoist に入れていないので、ここが唯一の元 | 出力の URL |
| Nuts の計画で今週に掛かるもの | `~/Documents/nuts/スケジュールの計画/Nuts移行_マイルストーン計画.html` の最新 template の JSON（`class="plan-data"`）を読み、`people[].bars` のうち今日を含む週に開始・終了する帯と、`methods[].switch` が今週の手段。4 の「判断・確認をお願いしたいこと」の箇条書きも拾う | 計画: `https://claude.ai/artifact/LYhTzR1KmusBCA4AFzQram`、ガント: `https://docs.google.com/spreadsheets/d/1PvTSmnE_not_5XseWG6pYBYZBOUXJ6ZHjfEyf2PVy5M` |

今日の日付は `date +%Y-%m-%d` で取る。土日・祝日でも、呼ばれたら同じ手順でまとめる。冒頭に「今日は休み」と書き添える（祝日は `~/.claude/skills/nuts-milestone-plan/scripts/check_holidays.py` の JP_HOLIDAYS を参照）。

## 組み立て

Todoist のタスクは次で分ける。

- **今日中に決める・動かす**: 繰り返しでなく、ラベルに「緊急度高」か「重要度高」があるもの。Jira の期日が今日のもの。Nuts の帯が今週に始まる・終わるもの（受け入れ・切替・期日）
- **MR の対応待ち**: GitLab の `Required(s-ando)` の MR。レビュー（他の人の MR）を先、自分の MR（指摘への対応など）を後に並べる。1 行に `!番号`・題名・著者を書く（例「[!18174 コース移行の設計](URL)（深川さん）」）。題名が「WIP」「作成中」のものはその旨を添える。0 件なら節ごと省く
- **連絡・確認**: 繰り返しでなく、「脳みそ労力低」のもの。「連絡待ちリスト」「検証中リスト」はその旨を添える
- **毎日のもの**: 繰り返しのタスク。1 行にまとめる（題名だけ、URL は付けない）
- 私用（project が仕事でないもの、「朝にピアノ」など）は載せない

会議は時刻順に 1 行。Nuts の未決（判断・確認をお願いしたいこと）は、会議で進められそうなものを 1〜2 件だけ添える。

## 返答の形（Markdown）

```
**11/2（月）今日やるべきこと**

**予定**: 9:30 [全社朝礼](htmlLink) → 10:30 [Nuts朝会](htmlLink) → 15:30 [振り返り MT](htmlLink)

**今日中に決める・動かす**
1. [NTMS-42 AF クレカ](jira) の期日が今日。残りは返金・検知。閉じるか期日を動かすか朝会で決める
2. [肥沼さんの草案を何パターンか書く](todoist)（12:30）

**MR の対応待ち**
- レビュー: [!18174 コース移行の共通の設計](URL)（深川さん）、[!18265 d払い解約の Writer](URL)（鈴木さん）
- 自分の MR: [!18020 カードの設計の決定事項 11.7](URL)

**連絡・確認**
- [渡邉さんに AI エージェントの OKR を聞く MT を設定する](todoist)
- [澤野さんの業務委託の状況を確認する](todoist)（連絡待ち）

**毎日のもの**: ガントチャート更新、メール、朝会の資料とタスク、カイゼン 2 件、Obsidian の振り返り

計画: [マイルストーン計画](https://claude.ai/artifact/LYhTzR1KmusBCA4AFzQram) ／ [ガントチャート全体](https://docs.google.com/spreadsheets/d/1PvTSmnE_not_5XseWG6pYBYZBOUXJ6ZHjfEyf2PVy5M)
```

- 40 行以内。項目は 1〜2 文、理由は制約だけ（「期日が今日」「明日は祝日」）
- 取れなかった元（認証切れなど）があれば、最後に何が取れなかったかと直し方を 1 行ずつ添える

## 書き方

- 日本語。人は「深川さん」「鈴木さん」「正社員」。自分は「安藤」と書かず主語を省く
- 誇張しない。「至急」「必ず」を使わない。重要度は並び順で示す
