---
name: jira-cli-create-config-broken
description: jira issue create が共有configのissue typeメタ欠落で失敗する。JIRA_CONFIG_FILEで一時init回避
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4615a64b-2d4a-4f66-9a98-11eeab5a54b5
  modified: 2026-08-10T01:12:20.262Z
---

`~/.config/.jira/.config.yml` は issue type メタデータ（`issue.fields.types`）が欠落しており、そのままだと `jira issue create` が全プロジェクトで `Error: invalid issue types in config` で失敗する（読み取り系 `jira issue list/view` は動く）。

config上は `NUTSAFSBPS: classic / board: scrum` とあるが、実体は next-gen / simple board（`jira project list` / `jira board list` で確認）。

回避策（共有configは変更しない）:
- `JIRA_CONFIG_FILE=/tmp/jira_<proj>.yml jira init --force` で対象プロジェクトの正しいメタデータを一時生成し、その `JIRA_CONFIG_FILE` を指定して create / link を実行する。
- 非対話で通すにはフラグを全部渡す: `--installation cloud --server https://comicfesta.atlassian.net --login s-ando@wwwave.jp --project <KEY> --board <名前>`。`--board` を省くとボード選択で止まる。NUTSKAIZEN はボードが無いため `--board None`。
- 説明文は `--template <file>` で渡す（JIRA記法。見出しは `h2.`）。エピック配下に作るときは `-P <EPIC-KEY>`。

恒久対応するなら共有configを `jira init --force` で再生成する必要がある（未対応）。関連: [[nuts-af-jira-projects-by-provider]]

説明文の変換にも不具合がある。文書中で最初に現れる箇条書きは、先頭項目が直前のブロック（見出しや段落）の末尾に吸収される（`h2. 受け入れ条件` + `* AFと…` → 見出しが `受け入れ条件* AFと…` になる）。`-` と `*` のどちらでも起きる。2つ目以降の箇条書きは正常。回避は箇条書きを使わず段落を空行で並べる。`{{...}}` の等幅記法も日本語と隣接すると崩れるため使わない。REST API で ADF を直接 PUT する回避策は auto mode で拒否された。
