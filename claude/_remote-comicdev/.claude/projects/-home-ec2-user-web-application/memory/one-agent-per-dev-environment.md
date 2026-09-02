---
name: one-agent-per-dev-environment
description: 1つの開発環境を触るエージェントは1つに限る案（未決定・チーム相談待ち）
metadata: 
  node_type: memory
  type: project
  originSessionId: ee0aa15e-01bb-4775-9c57-f11c641720ea
  modified: 2026-08-20T23:34:29.883Z
---

同じ開発環境に対して並行して複数のエージェントを動かさない、という案（2026-08-20 時点で**未決定**。
s-ando がチームに共有して相談してから決める）。決まったものとして扱わない。

**Why:** カード変更 E2E で実害が出た。80 番と 3035 番の取り合いでスタックが落ち、片方が本体repo で
`docker compose run` を打ってもう片方の nginx を落とした。同じ項目（S24-01）を 2 つのペインが
二重に調べ、細部の異なる報告が 2 つ残った（一方は React、実際は Vue）。テストデータの書き換えが
交錯すると結果を再現できない。

**How to apply:** E2E の進め方は AI が MR で変えない。気づきは E2E のスプレッドシートの改善メモに
残し、チームで相談してから反映する（MR !17222 はこの方針でクローズ、ブランチ
`nuts/docs/e2e-skill-current-state` は残置）。[[worktree-docker-test-setup]]
