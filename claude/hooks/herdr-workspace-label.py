#!/usr/bin/env python3
"""依頼から作業の対象を読み取り、herdr のワークスペースに名前を付ける。

名前はルールに当たるものを優先し、当たらなければセッションの最初の依頼から作る。

- MR レビューの依頼: "Codereview MR !<id>"
- JIRA のチケットに取り組む依頼: "<課題キー>"（例 "NUTSKAIZEN-856"）
- どちらにも当たらない最初の依頼: Haiku が依頼から作った短い作業名
MR レビューと JIRA の両方に当たるときは MR レビューを優先する。
ルールの名前は応答を終えるたびに直近の依頼で付け直し、作業名はセッションに1回だけ付ける。作業名を付けたあとにルールに当たれば、ルールの名前で上書きする。

Stop で動かし、会話記録で今の会話に残っている依頼だけを見る。送信を取り消した依頼は Stop を起こさず、
会話記録では別の枝に残る。応答の途中で止めた依頼は、直後に中断の記録が入る。どちらも名前の元にしない。

今のワークスペースにこのペインしか無ければ名前を変え、ほかのペインもあればこのペインを新しいワークスペースに移す。
既に同じ名前のワークスペースにいれば何もしない。失敗しても応答は止めない。
会話記録の読み取りと作業名の生成は数秒かかるため、切り離した子プロセスで行う。
"""
import json
import os
import re
import subprocess
import sys

STATE_DIR = os.path.expanduser("~/.claude/herdr-sessions/labels")
GENERIC_MIN_PROMPT_CHARS = 8
GENERIC_MAX_LABEL_CHARS = 20
GENERIC_PROMPT = (
    "herdr のワークスペース名を付ける。次の依頼の作業内容を、日本語の15文字以内の名詞句で1行だけ出力する。"
    "説明や記号は付けない。\n\n依頼: "
)
INTERRUPTED = "[Request interrupted by user]"
# 依頼でない記録（シェルの実行、コマンドの出力、通知）
NON_PROMPT_PREFIXES = ("<bash-", "<local-command", "<task-notification>", "<system-reminder>")
COMMAND_NAME = re.compile(r"<command-name>(.*?)</command-name>", re.DOTALL)
COMMAND_ARGS = re.compile(r"<command-args>(.*?)</command-args>", re.DOTALL)

REVIEW_WORD = re.compile(r"レビュ|review", re.IGNORECASE)
MR_ID_PATTERNS = [
    re.compile(r"/merge_requests/(\d+)"),
    re.compile(r"\bMR\s*!?\s*(\d+)", re.IGNORECASE),
    re.compile(r"!(\d+)\b"),
]

TICKET_WORD = re.compile(
    r"チケット|やりたい|やって|対応|着手|実装|進め|取り組|始め|work on|start", re.IGNORECASE
)
# 課題キーの接頭辞を4文字以上に限り、UTF-8・SHA-256 のような語を拾わない
TICKET_KEY_PATTERNS = [
    re.compile(r"atlassian\.net/browse/([A-Z][A-Z0-9]+-\d+)"),
    re.compile(r"(?<![A-Za-z0-9])([A-Z][A-Z0-9]{3,}-\d+)(?![A-Za-z0-9])"),
]


def herdr(*args):
    result = subprocess.run(["herdr", *args], capture_output=True, text=True, timeout=5)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout).get("result")
    except json.JSONDecodeError:
        return None


def first_match(patterns, text):
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match.group(1)
    return None


def rule_label(prompt):
    if REVIEW_WORD.search(prompt):
        iid = first_match(MR_ID_PATTERNS, prompt)
        if iid:
            return f"Codereview MR !{iid}"
    if TICKET_WORD.search(prompt):
        key = first_match(TICKET_KEY_PATTERNS, prompt)
        if key:
            return key
    return None


def state_path(session_id):
    return os.path.join(STATE_DIR, f"{session_id}.txt")


def read_state(session_id):
    try:
        with open(state_path(session_id)) as f:
            return f.read().strip()
    except OSError:
        return None


def write_state(session_id, kind):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(state_path(session_id), "w") as f:
        f.write(kind)


def apply_label(pane_id, label):
    pane = (herdr("pane", "get", pane_id) or {}).get("pane")
    if not pane:
        return
    workspace = (herdr("workspace", "get", pane["workspace_id"]) or {}).get("workspace")
    if not workspace or workspace.get("label") == label:
        return

    if workspace.get("pane_count") == 1:
        herdr("workspace", "rename", pane["workspace_id"], label)
    else:
        herdr("pane", "move", pane["pane_id"], "--new-workspace", "--label", label, "--focus")


def user_text(entry):
    """人の側の記録なら本文を返す。ツールの結果と内部の記録は None。スラッシュコマンドは入力したときの形に戻す。"""
    if entry.get("type") != "user" or entry.get("isMeta") or entry.get("isCompactSummary"):
        return None
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, list):
        blocks = [b for b in content if isinstance(b, dict)]
        if any(b.get("type") == "tool_result" for b in blocks):
            return None
        content = "\n".join(b.get("text", "") for b in blocks if b.get("type") == "text")
    if not isinstance(content, str) or content.lstrip().startswith(NON_PROMPT_PREFIXES):
        return None
    name = COMMAND_NAME.search(content)
    if name:
        args = COMMAND_ARGS.search(content)
        return f"{name.group(1).strip()} {args.group(1).strip() if args else ''}".strip()
    return content


def active_prompts(transcript_path):
    """最後の記録から親をたどり、今の会話に残っている依頼を古い順に返す。応答の途中で止めた依頼は除く。"""
    entries = {}
    last = None
    with open(transcript_path) as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            uuid = entry.get("uuid")
            if not uuid:
                continue
            entries[uuid] = entry
            if entry.get("type") in ("user", "assistant") and not entry.get("isSidechain"):
                last = uuid

    chain = []
    seen = set()
    while last in entries and last not in seen:
        seen.add(last)
        chain.append(entries[last])
        last = entries[last].get("parentUuid")

    prompts = []
    for entry in reversed(chain):
        text = user_text(entry)
        if text is None:
            continue
        if text.strip() == INTERRUPTED:
            if prompts:
                prompts.pop()
            continue
        prompts.append(text)
    return prompts


def generate_label(prompt):
    env = {k: v for k, v in os.environ.items() if not k.startswith("HERDR_")}
    result = subprocess.run(
        ["claude", "-p", "--model", "haiku", "--settings", '{"disableAllHooks":true}'],
        input=GENERIC_PROMPT + prompt[:2000],
        capture_output=True, text=True, timeout=60, env=env, cwd=os.path.expanduser("~"),
    )
    if result.returncode != 0:
        return None
    lines = [line.strip().strip("「」\"'`*") for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        return None
    return lines[0][:GENERIC_MAX_LABEL_CHARS] or None


def run_label(session_id, pane_id, transcript_path):
    """切り離した子プロセスで名前を決めて付ける。作業名の生成中にルールの名前が付いていれば何もしない。"""
    prompts = active_prompts(transcript_path)
    if not prompts:
        return

    label = rule_label(prompts[-1])
    if label:
        apply_label(pane_id, label)
        write_state(session_id, "rule")
        return

    if read_state(session_id):
        return
    first = next(
        (p for p in prompts
         if not p.lstrip().startswith("/") and len(p.strip()) >= GENERIC_MIN_PROMPT_CHARS),
        None,
    )
    if not first:
        return
    write_state(session_id, "generic-pending")
    label = generate_label(first)
    if label and read_state(session_id) == "generic-pending":
        apply_label(pane_id, label)
        write_state(session_id, "generic")


def main():
    if os.environ.get("HERDR_ENV") != "1" or not os.environ.get("HERDR_PANE_ID"):
        return
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    if payload.get("agent_id"):
        return

    session_id = payload.get("session_id")
    transcript_path = payload.get("transcript_path")
    if not session_id or not transcript_path:
        return
    subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "--label",
         session_id, os.environ["HERDR_PANE_ID"], transcript_path],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


if __name__ == "__main__":
    try:
        if len(sys.argv) == 5 and sys.argv[1] == "--label":
            run_label(sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            main()
    except Exception:
        pass
