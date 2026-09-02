---
name: nuts-af-jira-projects-by-provider
description: AF決済のNuts移行はプロバイダ別にJIRAプロジェクトが分かれる（SBPS=NUTSAFSBPS / クレカ=NATSCREAF）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4615a64b-2d4a-4f66-9a98-11eeab5a54b5
---

AF（AnimeFesta / anime_subscription）決済の Nuts 移行は、決済プロバイダごとに JIRA プロジェクトが分かれている。

- **NUTSAFSBPS** — SBPS（ソフトバンクペイメント、softbank2）の移行。board=669。
- **NATSCREAF** — クレジットカード決済（sony_payment、packs/nuts/card）の移行。sony_payment 関連のチケットはこちらに作る。

jira-cli の default project は NUTSAFSBPS なので、クレカ側の操作では `-p NATSCREAF` / `project=NATSCREAF` を明示する。

コード側の対応: SBPS=`packs/nuts/softbank`（provider :sbps）、クレカ=`packs/nuts/card`（sony_payment 再実装、ADR-045）。関連: [[nutsafsbps-details]]
