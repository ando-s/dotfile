#!/usr/bin/env bash
# Herdr の別ペインのエージェントを見張り、終わった・止まった・詰まったのいずれかで終了する。
# 状態が working のまま接続切れなどで進まないことがあるため、状態だけでなく画面の変化も見る。
# 使い方: scripts/watch_agent.sh <エージェント名> [詰まったと判断する分数=15] [最長の分数=120]
set -u
agent="$1"
stall_minutes="${2:-15}"
max_minutes="${3:-120}"
interval=60
last_hash=""
unchanged=0

for ((elapsed = 0; elapsed < max_minutes; elapsed++)); do
  status=$(herdr agent get "$agent" 2>/dev/null | python3 -c "import json,sys;r=json.load(sys.stdin)['result'];print(r.get('agent',r).get('agent_status',''))" 2>/dev/null)
  case "$status" in
    idle|done|blocked) echo "result=$status"; exit 0 ;;
    "") echo "result=missing (herdr agent list で探し直す)"; exit 0 ;;
  esac
  screen=$(herdr agent read "$agent" --source visible 2>/dev/null)
  if grep -q -E 'Reconnecting|Stream disconnected' <<<"$screen" && ((unchanged >= 3)); then
    echo "result=disconnected"; exit 0
  fi
  hash=$(printf '%s' "$screen" | shasum | cut -d' ' -f1)
  if [[ "$hash" == "$last_hash" ]]; then
    ((unchanged++))
    if ((unchanged >= stall_minutes)); then echo "result=stalled (${stall_minutes}分画面が変わらない)"; exit 0; fi
  else
    unchanged=0
    last_hash="$hash"
  fi
  sleep "$interval"
done
echo "result=timeout (${max_minutes}分)"
