---
name: card-token-name-logging-decision-12-3
description: クレカ設計の決定事項12.3（トークンと名義をログから伏せる）は誤りで、設計側を直す
metadata: 
  node_type: memory
  type: project
  originSessionId: ee0aa15e-01bb-4775-9c57-f11c641720ea
  modified: 2026-08-20T23:32:30.277Z
---

`packs/nuts/docs/card/設計の決定事項.md` の 12.3 は「カードのトークンと名義は、ログとエラー通知の
両方で伏せる」としているが、この決定自体が誤りという判断（s-ando、2026-08-20）。実装を合わせる
のではなく、記述を直す。

**Why:** カード変更 E2E の S26-02 で「ログに平文で残る」を課題として MR !17219 を作ったが、
伏せる必要が無いという判断でクローズした。実装は現状のままでよい。

**How to apply:** 12.3 の記述を実装に合わせて直す。トークンの性質（使い捨てか・有効期限）は
接続仕様書で裏取りしてから根拠として書く（[[escott-sonypayment-primary-source-facts]]）。
なお内部APIでパラメータのフィルタが一切効かない件（[[internal-api-client-skips-parameter-filter]]）は
12.3 とは独立した既存の漏れで、ADR-048 の provider_user_id にも当たる。
