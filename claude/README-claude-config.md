# Claude の設定と記憶の置き場（ローカル / comicdev）

## どちらの設定が読まれるか

セッションを動かしている**マシンの** `~/.claude` と `CLAUDE_CONFIG_DIR` が読まれる。

- Mac で起動したセッション（ssh でリモートのコマンドを叩くだけの場合も含む）: Mac 側の設定だけ
- comicdev で起動したセッション: comicdev 側の設定だけ

ssh でコマンドを流しても、リモートの `~/.claude/CLAUDE.md` や記憶は読まれない。
web-application の作業はコードが comicdev にあるため、記憶が comicdev 側にだけ溜まる。

## 揃え方

`claude/sync-comicdev.sh` で comicdev の `CLAUDE.md` と記憶を取り込む。
取得したものは `claude/_remote-comicdev/` に置き、プロジェクトの記憶へ同名でないものだけ足す。

## 作業場所で内容を分ける

マシンごとに設定を分けるのではなく、次の順で分ける。

1. 全プロジェクト共通: `claude/CLAUDE.md`（`~/.claude/CLAUDE.md` からのリンク）
2. プロファイル単位: `claude/profiles/<名前>/CLAUDE.md`（`CLAUDE_CONFIG_DIR` で選ぶ）。
   web-application を comicdev で扱う決めごとはここに置く
3. リポジトリ単位: リポジトリの `CLAUDE.md`。comicdev の worktree にも同じものが入る

セッションの途中で切り替わるものではないため、「ローカル作業のとき」「リモート作業のとき」で
別の設定を読ませることはできない。作業場所の決めごとは 2 に書き、地の文で場所を指定する。
