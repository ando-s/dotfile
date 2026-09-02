---
name: worktree-browser-verify-public-host
description: worktree でブラウザ通し確認するときは公開ホスト（80番）が必須で、APP_HOST_NAME は webpack にも渡し 3035 を公開する
metadata: 
  node_type: memory
  type: project
  originSessionId: a67f2e1d-a319-4448-abb5-4aef230e42b7
  modified: 2026-07-31T07:57:38.899Z
---

worktree のコードをブラウザで通し確認するときは `scripts/docker-worktree.sh up` で80番を取り、公開ホスト（`sa2.comicdev.iowl.jp` 等、ALB が https を終端して EC2 の80番へ流す）で開く。`setup-worktree-docker.sh` の既定（`APP_HOST_NAME=localhost` / 高ポート）では通らない点が2つある。

- Nuts の Core は `entry_form_url` を https のみ許可する（`packs/nuts/core/app/controllers/nuts/core/api/v1/subscription_agreements_controller.rb`）。http の localhost では申込が 422 になる
- `APP_HOST_NAME` は web だけでなく **webpack サービスにも渡す**。遅延読み込みするチャンクの取得先（publicPath）がこの値で決まり、localhost のままだと画面の JS が動かない。さらに webpack の 3035番を host へ公開する（ブラウザが `https://<host>:3035` から読む）

`.env` は読み書きが許可されていないため、これらは `docker-compose.override.yml`（`setup-worktree-docker.sh` が生成するファイル）の environment で上書きする。

`docker-worktree.sh up` は80番を持つ本体スタックを `docker compose down` するので、他のセッションが使っていないか先に確認する。戻すのは本体ディレクトリで `docker compose up -d`。

開発環境の DB は worktree ごとに独立で空なので、本体の development DB をボリュームごとコピー（`docker run --rm -v <primary>_dbdatastore:/from -v <worktree>_dbdatastore:/to alpine cp -a`）すると、ユーザーやコースマスタが揃った状態から始められる。関連: [[worktree-docker-test-setup]] / [[worktree-verify-branch-code]]
