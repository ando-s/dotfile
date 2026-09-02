---
name: e2e-process-changes-need-team-agreement
description: E2Eの進め方（スキル・規約）はAIがMRで変えない。改善メモに残してチーム相談後に反映する
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ee0aa15e-01bb-4775-9c57-f11c641720ea
  modified: 2026-08-20T23:34:39.632Z
---

E2E の進め方に関する気づきは、MR を作らずに E2E のスプレッドシートの改善メモへ書く
（2026-08-20 の指示）。チームに共有して相談してから変更する。

**Why:** 今回 AI が勝手に 2 本の MR を立てた（!17222 の E2E スキル記述、その追記の 1 環境
1 エージェント）。どちらもチームの合意を取っていない提案で、決定として入ると運用が既定化する。

**How to apply:** スキル（`packs/nuts/.ai/skills/e2e-*`）や運用規約の変更は提案として書き出すだけ
にする。反映は s-ando の指示があってから。個別の実装バグ修正の MR はこの制約の対象外
（例: MR !17223 の Faraday のログ出力）。[[one-agent-per-dev-environment]]
