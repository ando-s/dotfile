---
name: nuts-batch-monitoring-stay-as-is
description: nuts のバッチ監視は spica の cdk-spica-batch の仕組みに乗せず現状維持（2026-08-19 判断）
metadata:
  type: project
---

nuts のバッチ監視を spica の受動通知の仕組み（cdk-spica-batch / CloudWatch Alarm）に乗せる検討をし、2026-08-19 に現状維持と判断した。

**Why:**

- 失敗判定の入力が無い。spica の各バッチは自分で `Loggers::Batch.result(name:, result: "FAILURE")` を出し収集 Lambda がそのログを読むが、`packs/nuts/` に `Loggers::Batch` の呼び出しは 0 件で、nuts は `n_batch_sessions` に記録する（status は running/success/warning/failure）
- nuts の `warning`（一部決済失敗・バッチは継続）が spica の SUCCESS/FAILURE の 2 値に写らない。運用で一番見る状態が落ちる
- 走査対象がスケジュールグループ `default` 限定。nuts は別グループ `nuts` なので別チーム管轄の cdk-spica-batch の変更が必要
- STG も監視対象に入る。`Aws::BatchMonitoringPolicy#ignored?` は `default` のバッチ名しか ignore しない

**How to apply:**

- 再検討するなら、乗せられるのは未実行・未完了だけ。nuts のバッチも `rake batch:perform` 経由で開始・終了ログを出すのでアプリ変更なしで判定できる。設定は `packs/nuts/*/config/aws-schedule.yml` に priority / grace_minutes / max_runtime_minutes を足すだけで `Aws::BatchMonitoringPolicy` が説明欄へ埋める
- 未確認: 現行 nuts 監視の実体（RFC 案3 は Redash のクエリとアラート、nuts のドキュメントは Datadog の `nuts-datadog` と Sentry）。nuts のログが spica と同じ CloudWatch ロググループに入るか
- CloudWatch Alarm は判定する側の死活監視の部品であり、これ単体ではバッチ失敗を検知しない
