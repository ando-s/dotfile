---
name: herdr-config-misplaced-keys-silent
description: Herdr設定が黙って効かない2原因（誤配置キー／remote接続ではキー割り当ては接続元マシン側）
metadata: 
  node_type: memory
  type: reference
  originSessionId: aac44237-9762-45f6-95ad-bbfd7f276b19
  modified: 2026-08-07T01:31:02.869Z
---

Herdr の設定変更が反映されないのに、`herdr server reload-config` は `status: applied` かつ diagnostics 空を返す。原因は2つある（いずれも 2026-08-07 に実機で確認）。

## 1. remote 接続では `[keys]` はEC2側で効かない

このEC2への接続は `herdr --remote` で、EC2側にあるのはサーバーと `remote-client-bridge` だけ。TUI と**キー入力の解釈は接続元マシン側の herdr** が持つ。

- `[keys]` — 接続元マシンの `~/.config/herdr/config.toml` に書く。EC2側に書いても無効
- `[terminal]` `[experimental]` `[ui]` `[theme]` — サーバー側（EC2）が読む。画面はサーバーが描いて送るため UI 系もこちら

判定に使った手順: `[[keys.command]]` で `key = "f9"`, `type = "shell"`, `command = "touch <目印>"` を仕込み、F9 を押して目印ファイルができるかを見る。できなければキー割り当てが1つも読まれていない。

`ps -eo pid,args | grep herdr` に `remote-client-bridge` があり、TUI プロセスが無ければ remote 接続。

## 2. 誤ったテーブルに書いた項目は無警告で捨てられる

`new_cwd` をファイル先頭のテーブル外に置いていたため読まれず、新規ペインは既定の継承（`follow`）で動いていた。`[terminal]` の下へ移して初めて効いた。

**How to apply:**

- 項目を書き足す前に `herdr --default-config` で所属テーブルを確認する
- reload-config の成功は反映の根拠にならない。必ず挙動で裏取りする
- `new_cwd` の確認: 別ディレクトリのペインから `herdr pane split <pane_id> --direction down --no-focus`（`--cwd` を付けない）を実行し、返る `cwd` を見る。確認後は `herdr pane close`

## エージェント指定の注意

`herdr agent focus <対象>` の対象はタブ名では通らない。エージェント名・ペインID（`w6:pS`）・ターミナルIDのいずれか。既定では全部 `claude` で一意にならないため、`herdr agent rename <ペインID> <名前>` で名前を付けると通るようになる。

関連: [[herdr-pane-claude-agent-workflow]]
