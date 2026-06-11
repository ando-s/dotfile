#!/usr/bin/env python3
"""Claude Code の会話履歴(jsonl)から、前回レビュー以降の活動ダイジェストを抽出する。

daily-review スキルが呼び出す。全プロジェクト(~/.claude/projects/*/*.jsonl)を横断し、
- ユーザーがタイプした生プロンプト(スキル化・サブエージェント化の主シグナル)
- 実行された bash コマンド(permissions 追加候補の主シグナル)
- ツール使用回数
をセッション単位のダイジェストにまとめてファイル出力する。

Claude はこのダイジェストを読んで改善提案レポートを書く。7MB級の jsonl を直接読ませない。
"""

import argparse
import glob
import json
import os
import re
from collections import Counter
from datetime import datetime, timedelta, timezone

PROJECTS_DIR = os.path.expanduser("~/.claude/projects")
REPORTS_DIR = os.path.expanduser("~/.claude/daily-review/reports")
REPORT_RE = re.compile(r"review_(\d{8})_(\d{6})\.md$")


def latest_report_time():
    """直近レポートのファイル名からタイムスタンプ(UTC)を求める。なければ None。"""
    if not os.path.isdir(REPORTS_DIR):
        return None
    latest = None
    for name in os.listdir(REPORTS_DIR):
        m = REPORT_RE.search(name)
        if not m:
            continue
        try:
            dt = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
        except ValueError:
            continue
        # ファイル名は date +%Y%m%d_%H%M%S（ローカル時刻）で付けられる
        dt = dt.astimezone()
        if latest is None or dt > latest:
            latest = dt
    return latest


def parse_ts(raw):
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def truncate(text, limit):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit] + " …(略)"


def block_to_bash(block):
    """assistant の tool_use ブロックが Bash なら (command, description) を返す。"""
    if block.get("type") != "tool_use" or block.get("name") != "Bash":
        return None
    inp = block.get("input") or {}
    return inp.get("command", ""), inp.get("description", "")


def extract_session(path, since):
    """1ファイルから since 以降のメッセージを抽出。プロジェクト横断のダイジェスト断片を返す。"""
    prompts = []
    bash_cmds = []
    tool_counter = Counter()
    cwd = None
    branch = None
    first_ts = None
    last_ts = None

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts = parse_ts(entry.get("timestamp"))
            if ts is None:
                continue
            if since and ts < since:
                continue

            cwd = entry.get("cwd") or cwd
            branch = entry.get("gitBranch") or branch
            if first_ts is None:
                first_ts = ts
            last_ts = ts

            etype = entry.get("type")
            msg = entry.get("message") or {}
            content = msg.get("content")

            # ユーザーがタイプした生プロンプト
            if etype == "user" and isinstance(content, str) and entry.get("promptSource") == "typed":
                prompts.append((ts, truncate(content, 800)))

            # assistant のツール使用
            if etype == "assistant" and isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "tool_use":
                        name = block.get("name", "?")
                        tool_counter[name] += 1
                        bash = block_to_bash(block)
                        if bash:
                            cmd, desc = bash
                            if cmd:
                                bash_cmds.append((truncate(cmd, 200), desc))

    if not prompts and not bash_cmds and not tool_counter:
        return None

    return {
        "path": path,
        "cwd": cwd,
        "branch": branch,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "prompts": prompts,
        "bash_cmds": bash_cmds,
        "tools": tool_counter,
    }


def render(sessions, since, out_path):
    lines = []
    lines.append("# 会話ダイジェスト（daily-review 入力）\n")
    since_label = since.astimezone().strftime("%Y-%m-%d %H:%M") if since else "（指定なし）"
    lines.append(f"- 抽出基準時刻（これ以降）: {since_label}")
    lines.append(f"- 対象セッション数: {len(sessions)}\n")

    # 全体の bash コマンド頻度（permissions 候補のサマリ）
    all_bash = Counter()
    for s in sessions:
        for cmd, _ in s["bash_cmds"]:
            head = cmd.split()[0] if cmd.split() else cmd
            all_bash[head] += 1
    if all_bash:
        lines.append("## bash コマンド先頭トークン頻度（permissions 候補のヒント）\n")
        for tok, n in all_bash.most_common(30):
            lines.append(f"- `{tok}` × {n}")
        lines.append("")

    for i, s in enumerate(sessions, 1):
        span = ""
        if s["first_ts"] and s["last_ts"]:
            span = f'{s["first_ts"].astimezone():%m-%d %H:%M} → {s["last_ts"].astimezone():%H:%M}'
        lines.append(f"## セッション {i}: {s.get('cwd') or '?'}")
        lines.append(f"- branch: {s.get('branch') or '-'} / 期間: {span}")
        tools = ", ".join(f"{k}×{v}" for k, v in s["tools"].most_common())
        lines.append(f"- ツール使用: {tools or '-'}\n")

        if s["prompts"]:
            lines.append("### ユーザーの指示（typed prompt）")
            for ts, p in s["prompts"]:
                lines.append(f"- [{ts.astimezone():%H:%M}] {p}")
            lines.append("")

        if s["bash_cmds"]:
            lines.append("### 実行された bash コマンド")
            for cmd, desc in s["bash_cmds"]:
                suffix = f"  # {desc}" if desc else ""
                lines.append(f"- `{cmd}`{suffix}")
            lines.append("")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="ISO8601。未指定なら直近レポート、それも無ければ24h前")
    ap.add_argument("--max-files", type=int, default=15)
    ap.add_argument("--out", default=os.path.expanduser("~/.claude/daily-review/digest.md"))
    args = ap.parse_args()

    if args.since:
        since = parse_ts(args.since)
    else:
        since = latest_report_time()
    if since is None:
        since = datetime.now(timezone.utc) - timedelta(days=1)

    files = glob.glob(os.path.join(PROJECTS_DIR, "*", "*.jsonl"))
    # since 以降に更新されたファイルだけを mtime で粗くフィルタし、新しい順に max_files 件
    recent = [(os.path.getmtime(p), p) for p in files
              if datetime.fromtimestamp(os.path.getmtime(p), timezone.utc) >= since]
    recent.sort(reverse=True)
    recent = recent[: args.max_files]

    sessions = []
    for _, path in recent:
        s = extract_session(path, since)
        if s:
            sessions.append(s)
    sessions.sort(key=lambda s: s["last_ts"] or since, reverse=True)

    render(sessions, since, args.out)
    print(f"digest_path={args.out}")
    print(f"since={since.astimezone().isoformat()}")
    print(f"sessions={len(sessions)} scanned_files={len(recent)} total_files={len(files)}")


if __name__ == "__main__":
    main()
