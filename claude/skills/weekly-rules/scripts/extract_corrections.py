#!/usr/bin/env python3
"""Claude Code の会話記録（~/.claude/projects/*/*.jsonl）から、ユーザーの発言と、その直前の Claude の発言を対にして書き出す。

weekly-rules スキルが呼ぶ。どれが「直した場面」かの判断は Claude が行う。ここでは材料をそろえるだけにする。
weekly-rules 自身のセッションは、自分の出した案を指摘として数えないように除く。
"""

import argparse
import glob
import json
import os
from datetime import datetime, timedelta, timezone

PROJECTS_DIR = os.path.expanduser("~/.claude/projects")
WORK_DIR = os.path.expanduser("~/.claude/weekly-rules")
LAST_RUN = os.path.join(WORK_DIR, "last-run")
SELF_MARKERS = ("/weekly-rules", "<command-name>/weekly-rules</command-name>")
# 直しではない短い返事。材料を小さくするため落とす
APPROVALS = {"うん", "ok", "おk", "おけ", "はい", "お願い", "おねがい", "よろしく", "よろしくお願いします", "いいよ", "y", "yes", "続けて", "進めて"}
SKIP_PREFIXES = ("<system-reminder>", "<task-notification>", "<local-command", "Caveat:",
                 "<bash-input>", "<bash-stdout>", "<bash-stderr>", "<command-", "<artifact-content")


def parse_ts(raw):
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def squash(text, limit):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit] + " …(略)"


def user_text(entry):
    """ユーザーが打った文字列を返す。ツールの結果やシステムの差し込みは None。"""
    if entry.get("type") != "user" or entry.get("isMeta"):
        return None
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, list):
        texts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        if not texts or any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            return None
        content = "\n".join(texts)
    if not isinstance(content, str):
        return None
    stripped = content.strip()
    if not stripped or stripped.startswith(SKIP_PREFIXES):
        return None
    if stripped.lower().rstrip("！!。") in APPROVALS or (len(stripped) <= 2 and stripped.isascii()):
        return None
    return stripped


def assistant_text(entry):
    if entry.get("type") != "assistant":
        return None
    content = (entry.get("message") or {}).get("content")
    if not isinstance(content, list):
        return None
    texts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
    joined = "\n".join(t for t in texts if t.strip())
    return joined or None


def extract(path, since):
    pairs = []
    last_assistant = ""
    cwd = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            cwd = entry.get("cwd") or cwd
            said = assistant_text(entry)
            if said:
                last_assistant = said
                continue
            raw = (entry.get("message") or {}).get("content") if entry.get("type") == "user" else None
            if isinstance(raw, str) and (raw.lstrip().startswith(SELF_MARKERS[0]) or SELF_MARKERS[1] in raw):
                return None, cwd
            typed = user_text(entry)
            if typed is None:
                continue
            ts = parse_ts(entry.get("timestamp"))
            if ts is None or ts < since:
                last_assistant = ""
                continue
            pairs.append((ts, squash(last_assistant, 300), squash(typed, 400)))
            last_assistant = ""
    return pairs, cwd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, help="何日前からを対象にするか。省略時は前回の実行以降、無ければ7日")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    if args.days:
        since = now - timedelta(days=args.days)
    elif os.path.exists(LAST_RUN):
        since = parse_ts(open(LAST_RUN).read().strip()) or now - timedelta(days=7)
    else:
        since = now - timedelta(days=7)

    sessions = []
    for path in glob.glob(os.path.join(PROJECTS_DIR, "*", "*.jsonl")):
        if datetime.fromtimestamp(os.path.getmtime(path), timezone.utc) < since:
            continue
        pairs, cwd = extract(path, since)
        if pairs:
            sessions.append((pairs[0][0], os.path.basename(path), cwd, pairs))
    sessions.sort()

    os.makedirs(WORK_DIR, exist_ok=True)
    out = os.path.join(WORK_DIR, f"pairs_{now.astimezone():%Y%m%d}.md")
    count = 0
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# ユーザーの発言と直前の Claude の発言（{since.astimezone():%Y-%m-%d %H:%M} 以降）\n\n")
        for _, name, cwd, pairs in sessions:
            f.write(f"## {cwd or '?'} / {name}\n\n")
            for ts, before, said in pairs:
                count += 1
                f.write(f"- [{ts.astimezone():%m-%d %H:%M}] ユーザー: {said}\n")
                if before:
                    f.write(f"  - 直前の Claude: {before}\n")
            f.write("\n")

    print(f"pairs_path={out}")
    print(f"since={since.astimezone().isoformat()}")
    print(f"sessions={len(sessions)} pairs={count}")


if __name__ == "__main__":
    main()
