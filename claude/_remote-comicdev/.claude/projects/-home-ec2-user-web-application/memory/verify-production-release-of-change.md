---
name: verify-production-release-of-change
description: 変更が本番リリース済みかは、実データが変わった時刻とproductionブランチのデプロイ記録の2段で確認する
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 894881a1-f1dc-4985-9ed0-5a9fddf4ffe6
  modified: 2026-08-20T06:09:32.035Z
---

web-application の変更が本番に出ているかは、次の 2 段で確認する。実データだけだと「その時刻に別の原因で変わった」を排除できない。

**1. 実データが変わった時刻を引く**（Metabase、本番は `database_id=5` = `[comicfesta][production][data]`）

```sql
SELECT count(*) FILTER (WHERE <列> IS NOT NULL) AS filled,
       min(<時刻列>) FILTER (WHERE <列> IS NOT NULL) AS first_filled
FROM <テーブル>;
```

**2. デプロイ記録と突き合わせる**

本番デプロイは master のパイプラインでは行われない。`scripts/deploy_production.sh`（cron が呼ぶ）が `production` ブランチを `staging` から進め、その push でデプロイ用パイプラインが動く。30 分刻みで走る。

```
glab api "projects/comic-festa-group%2Fweb-application/pipelines?ref=production&per_page=8"
glab api "projects/comic-festa-group%2Fweb-application/pipelines/<id>/jobs"
git merge-base --is-ancestor <マージコミット> <パイプラインのsha>
```

デプロイのジョブ名は `deploy_production:on_pipeline`。ジョブの実行区間に実データの変化時刻が入っていれば、その入れ替えによるものと言える（ECS の入れ替え途中から新しいタスクが処理を受けるため、ジョブ完了前に値が変わり始める）。

**Why:** 「値が入り始めた時刻」だけを根拠にすると、リリース以外の原因（別のデプロイ、手動操作、バッチ）を排除できない。逆にパイプラインだけ見ても、その sha に目的のコミットが含まれるかは別に確かめる必要がある。

**How to apply:** リリース待ちを前提にした作業（過去データの埋め戻し、フラグ切替）の前に必ず両方を出す。デプロイ記録を見ていないときは「実データからの推定」と明示する。関連: [[verify-db-values-via-metabase]]
