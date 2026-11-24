#!/bin/bash
# 今週に掛かる Jira の課題を集める。
# - NTMS（マイルストーン）は担当者が空なので、期日が近い（既定: 今日から 4 日以内）か進行中のものを全部
# - ほかのプロジェクトは、自分が担当で、期日が近いか進行中のもの
# jira CLI は -q の JQL に既定プロジェクトの条件を足すので、プロジェクトごとに回す。
# 使い方: jira_mine.sh [YYYY-MM-DD]   出力: プロジェクト<TAB>KEY<TAB>状態<TAB>題名
set -euo pipefail

until="${1:-$(date -v+4d +%Y-%m-%d 2>/dev/null || date -d '+4 days' +%Y-%m-%d)}"
cond="statusCategory != Done AND (duedate <= \"$until\" OR status = \"進行中\")"

list() {
  local p="$1" q="$2"
  jira issue list -p "$p" -q "$q" --plain --columns key,status,summary --no-headers 2>/dev/null \
    | grep -v '^\s*$' | sed "s/^/$p\t/" || true
}

list NTMS "$cond"
for p in NUTSAFSBPS NATSCREAF NUTSDCMAF NUTSAUAF NUTSKAIZEN NUTSAUCF NUTSSBPSCF NATSCRECF NUTSDCCF NUTSATNCF NUTSPPCF; do
  list "$p" "assignee = currentUser() AND $cond"
done
