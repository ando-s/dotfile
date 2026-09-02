#!/usr/bin/env bash
# comicdev の Claude 設定と記憶をローカルへ取り込む。
#
# ローカルで動かすセッションは comicdev の ~/.claude を読まない。逆も同じ。
# 記憶が片側だけに溜まるため、この取り込みで揃える。
#
# 使い方: bash claude/sync-comicdev.sh [pull]
#   pull（既定）: comicdev から取得し、ローカルのプロジェクト記憶へ足す（既にある名前は上書きしない）

set -euo pipefail

REMOTE=comicdev
REMOTE_HOME=/home/ec2-user
STAGE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_remote-comicdev"
LOCAL_MEM="$HOME/.claude/projects/-Users-s-ando-dev-spica-web-application/memory"
REMOTE_MEM="$STAGE/.claude/projects/-home-ec2-user-web-application/memory"

ssh_run() {
  ssh -T -o RemoteCommand=none -o LogLevel=ERROR "$REMOTE" "$@"
}

mkdir -p "$STAGE" "$LOCAL_MEM"

echo "comicdev から取得する"
ssh_run "cd $REMOTE_HOME && tar cz .claude/CLAUDE.md \
  '.claude/projects/-home-ec2-user-web-application/memory' \
  '.claude/projects/-home-ec2-user/memory' 2>/dev/null" > /tmp/remote_claude.tgz
tar xzf /tmp/remote_claude.tgz -C "$STAGE"

copied=0
skipped=0
for f in "$REMOTE_MEM"/*.md; do
  b="$(basename "$f")"
  [ "$b" = "MEMORY.md" ] && continue
  if [ -e "$LOCAL_MEM/$b" ]; then
    skipped=$((skipped + 1))
  else
    cp "$f" "$LOCAL_MEM/$b"
    copied=$((copied + 1))
  fi
done
echo "記憶: 追加 $copied 件 ／ 同名のため据え置き $skipped 件"

echo
echo "CLAUDE.md の差分（左: ローカル ／ 右: comicdev）"
diff "$(dirname "$STAGE")/CLAUDE.md" "$STAGE/.claude/CLAUDE.md" || true

cat <<'MSG'

取り込んだあとにやること

- 据え置きになった同名のファイルは中身を見て手で寄せる
- MEMORY.md の「comicdev 由来」の索引に、追加した記憶の行を足す
- CLAUDE.md の差分は、共通にするものだけ claude/CLAUDE.md へ寄せる。
  作業場所や環境の違いに依存するものは寄せない
MSG
