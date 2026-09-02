---
name: mr-review-watch-loop
description: Request Code Review(Nuts)+Required(s-ando)両ラベルMRの監視loop。平日9-18時JST15分ごと、Slack DM通知、自己更新cronで永久化
metadata: 
  node_type: memory
  type: project
  originSessionId: 072706ef-f525-44f8-bff1-2445d26c2f96
  modified: 2026-07-27T01:00:56.727Z
---

レビュー依頼MRの監視loop（2026-07-02開始、バックグラウンドジョブ 072706ef のセッション内で稼働）。

- 対象: `Request Code Review(Nuts)` と `Required(s-ando)` の両ラベルが付いた open MR
- 検知したら Slack の @s-ando 宛DMに通知（[[daily-review-loop-operation]] と同じ webhook 経由の `notify_slack.sh` を流用）
- チェックスクリプト: ジョブtmpディレクトリの `mr-watch-check.sh`（状態ファイルで通知済み管理。初回はベースライン記録のみ）
- スケジュール: 平日 JST 9:02〜17:47 の15分ごと＋18:02 の締め1回（サーバーはUTCなので cron は `0-8時` と `9時`）
- 永久化: cron は7日失効のため、6日ごとの one-shot「自己更新」ジョブが監視2本と次回更新ジョブを再作成する。手順書はジョブtmpの `mr-watch-renew.md`
- セッション（ジョブ）が削除されると停止する。止める時は CronList で監視2本＋更新1本を CronDelete
- 定期チェックの報告は「対象N件・新規通知M件」の事実のみ。判断待ち・誘導の文言（「次に進められる」等）を入れない（loopが止まるため）。新規通知時のみMR番号・URLを添える
