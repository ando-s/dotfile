---
name: autonomous-loop-no-decision-stops
description: 定期loop/自律実行では、ユーザー判断を仰いで処理を止めない。事前ポリシーで自動進行させる
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9685c6a8-5683-4b11-b578-78b417952c44
  modified: 2026-07-27T01:01:36.367Z
---

定期実行（loop/cron）や自律タスクでは、「〇〇すると次に進められる」という**ユーザー判断待ちで処理を止めてはいけない**。AskUserQuestion や承認待ちを挟まず、事前に決めた安全ポリシーで自動進行させる。

**Why:** 判断待ちが入るとバックグラウンドの処理がそこで停止し、ループが回らなくなる。ユーザーが常時見ているわけではない。

**How to apply:**
- 判断点は「事前合意した安全ポリシー」に置き換える。曖昧なケースは危険側（削除・変更）に倒さず、スキップして報告に回す。
- 例: worktree定期掃除（cron 火曜9:30、[[git-worktree]]）は「MERGEDかつ未コミット変更なしのものだけ自動削除、それ以外はスキップ」。AskUserQuestion 不使用をcronのpromptに明記。
- 参考: 自律ループの設計（syu-m-5151 のブログ 2026-06-23）。

**関連の限界:** CronCreate は session-only。セッション終了・resume で消え、resumeでも復活しない。loop自己更新cronは7日失効は防げるがセッション落ちには無力。クラウド(schedule)はこのローカル環境のworktreeを見られないため今回の用途では使えない。
