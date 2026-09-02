---
name: herdr-mac-notification-setup
description: "Herdrの通知はdelivery=\"terminal\"でWezTerm/Ghostty経由のmacOS通知にする（webhookは使わない）"
metadata: 
  node_type: memory
  type: project
  originSessionId: ef091e63-b3f4-493e-b4c1-c767389a75a9
---

リモートEC2上のHerdr/Claudeの通知は、Macのデスクトップ通知で受ける構成にしている。

- 設定: `~/.config/herdr/config.toml` の `[ui.toast] delivery = "terminal"`
- 経路: Herdrが外側端末へOSC 9/777を送出 → Mac側のWezTerm/Ghosttyがデスクトップ通知に変換
- 発火条件: 裏タブ/裏workspaceのClaudeが done(完了)・blocked(入力待ち) になったとき。見ているタブは対象外
- 確認コマンド: `herdr notification show "..." --body "..."`（設定中のdeliveryで送出）

制約・前提:

- **webhook方式は不可**（ユーザーが明示的に拒否）。Claude CodeのStop/NotificationフックでSlackへ飛ばす案は撤去済み
- `delivery="herdr"`(アプリ内popup)は、Herdr画面を見ていないと気づけないため用途に合わない
- `delivery="system"`はEC2がヘッドレスで不可
- 音は鳴らない: EC2にmp3プレイヤー(paplay/pw-play/ffplay/mpg123/mpv)が無い
- moshで接続するとOSC 9/777が転送されず通知は出ない（sshなら届く）
