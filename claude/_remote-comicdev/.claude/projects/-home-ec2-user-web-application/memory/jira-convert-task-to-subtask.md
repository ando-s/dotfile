---
name: jira-convert-task-to-subtask
description: JIRAで課題タイプを変更する手順（bulk move API）とスプリント・親が消える副作用
metadata: 
  node_type: memory
  type: reference
  originSessionId: 2f50af24-57e2-4b0c-be44-5028d9914782
  modified: 2026-08-26T10:45:12.767Z
---

JIRA Cloud（team-managed）で課題タイプを変更する手順。jira-cli には課題タイプ変更機能がなく、`PUT /rest/api/3/issue/{key}` も課題タイプが編集不可（editmeta の `issuetype.operations` が `[]`）で失敗する。

**手段**: `POST /rest/api/3/bulk/issues/move`（非同期、`GET /rest/api/3/bulk/queue/{taskId}` でポーリング）

- `targetToSourcesMapping` のキー形式は `<プロジェクト>,<課題タイプID>,<親のIDまたはキー>`。**親はターゲットがサブタスクのときだけ必須**。タスク・エピックへ移すときは `<プロジェクト>,<課題タイプID>` だけでよい。
- **方向を問わず動く**。サブタスク→タスク、タスク→エピック（階層レベル 0→1）とも成功した。
- 認証は curl が拒否されるため python の urllib で叩く（`JIRA_API_TOKEN` + Basic認証）。

**副作用**

- サブタスクは独自のスプリントを持てず、親のスプリントに強制される。サブタスク化のときに元のスプリント値が親の値へ上書きされ、後から個別設定もできない。
- **サブタスク→タスクへ移すとスプリントが空になる**。親から継承していた値は引き継がれないので、移動後に `customfield_10020` へスプリントIDを整数で PUT して入れ直す。
- **親のリンクも消える**。移動後に `parent` を PUT で張り直す。
- ステータス（完了・進行中）は保持される。

**課題タイプID**

- NATSCREAF: サブタスク 11224
- NUTSSBPSCF: タスク 11186 / バグ 11187 / ストーリー 11188 / エピック 11189 / サブタスク 11190 / カイゼン 11219

**日付フィールド**（NUTSSBPSCF で確認。同名の 開始日 が customfield_10046・10015・10121 と3つあるので editmeta で確かめる）

- 開始日: `customfield_10015`
- 期限: `duedate`

関連: [[jira-cli-create-config-broken]]
