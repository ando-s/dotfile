#!/usr/bin/env bash
# comicdev の CLAUDE.md を取り込み、ローカルとの差分を出す。
#
# ローカルで動かすセッションは comicdev の ~/.claude を読まない。逆も同じ。
# どちらも自動メモリはオフにしているので、取り込むのは CLAUDE.md だけ。
#
# 使い方: bash claude/sync-comicdev.sh

set -euo pipefail

REMOTE=comicdev
REMOTE_HOME=/home/ec2-user
STAGE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_remote-comicdev"

ssh_run() {
  ssh -T -o RemoteCommand=none -o LogLevel=ERROR "$REMOTE" "$@"
}

mkdir -p "$STAGE"

echo "comicdev から取得する"
mkdir -p "$STAGE/.claude"
ssh_run "cat $REMOTE_HOME/.claude/CLAUDE.md" > "$STAGE/.claude/CLAUDE.md.new"
test -s "$STAGE/.claude/CLAUDE.md.new"
mv "$STAGE/.claude/CLAUDE.md.new" "$STAGE/.claude/CLAUDE.md"

echo
echo "CLAUDE.md の差分（左: ローカル ／ 右: comicdev）"
diff "$(dirname "$STAGE")/CLAUDE.md" "$STAGE/.claude/CLAUDE.md" || true

cat <<'MSG'

取り込んだあとにやること

- CLAUDE.md の差分は、共通にするものだけ claude/CLAUDE.md へ寄せる。
  作業場所や環境の違いに依存するものは寄せない
MSG
