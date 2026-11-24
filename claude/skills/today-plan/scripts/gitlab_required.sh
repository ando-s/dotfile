#!/bin/bash
# GitLab で自分の対応待ち（Required(s-ando) のラベル）になっている開いた MR を集める。
# 対象は comic-festa-group のグループ全体。
# 出力: 種類<TAB>参照<TAB>著者<TAB>題名<TAB>URL
#   種類: review = 他の人の MR（レビュー）、own = 自分の MR（指摘への対応など）
set -euo pipefail

glab api --hostname gitlab.wwwave.info \
  "groups/comic-festa-group/merge_requests?state=opened&labels=Required(s-ando)&per_page=100&order_by=updated_at&sort=asc" \
  | python3 -c '
import json, sys
for m in json.load(sys.stdin):
    kind = "own" if m["author"]["username"] == "s-ando" else "review"
    print("\t".join([kind, m["references"]["full"], m["author"]["username"], m["title"], m["web_url"]]))
'
