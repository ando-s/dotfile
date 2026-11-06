#!/usr/bin/env python3
"""依頼から作業の目的と完了の基準を読み取り、herdr のワークスペースに名前を付ける。

名前は「<目的>｜完了:<完了の基準>」の形にする。

- 目的: セッションで最初に決めたものを保存し、以後は変えない。途中で作業が移っても名前の目的は動かさない
  - MR レビューの依頼があれば、最も古い依頼から "Codereview MR !<id>" を使う
  - JIRA のチケットに取り組む依頼があれば、最も古い依頼の課題キーで題名を acli から取り、Haiku が題名を縮めて目的にする
    - 課題キーと題名は保存し、ステータスラインに出す。課題キーだけでは何の作業か分からないため、名前には入れない
  - どちらにも当たらなければ Haiku が最初の依頼から作る
- 完了の基準: その目的に対して、Haiku が最初の依頼と直近の依頼から作る
応答を終えるたびに、今の会話に残っている依頼の並びが前回と違えば完了の基準を付け直す。
Haiku が失敗したときは、目的が決まっていれば目的だけを付け、決まっていなければ名前を変えない。

Stop で動かし、会話記録で今の会話に残っている依頼だけを見る。送信を取り消した依頼は Stop を起こさず、
会話記録では別の枝に残る。応答の途中で止めた依頼は、直後に中断の記録が入る。どちらも名前の元にしない。

今のワークスペースにこのペインしか無いか、前回このセッションが付けた名前のままなら名前を変える。
それ以外でほかのペインもあれば、このペインを新しいワークスペースに移す。
既に同じ名前のワークスペースにいれば何もしない。失敗しても応答は止めない。
会話記録の読み取りと名前の生成は数秒かかるため、切り離した子プロセスで行う。
子プロセスが重なったときは、最後に始めたものだけが名前を付ける。
"""
import hashlib
import json
import os
import re
import subprocess
import sys

STATE_DIR = os.path.expanduser("~/.claude/herdr-sessions/labels")
MIN_PROMPT_CHARS = 8
MAX_PART_CHARS = 18
RECENT_PROMPTS = 3
PROMPT_EXCERPT_CHARS = 600
SEPARATOR = "｜完了:"
LABEL_PROMPT = (
    "herdr のワークスペース名を付ける。下の依頼から、このセッションの作業の目的と完了の基準を読み取り、"
    "次の2行だけを出力する。説明や記号は付けない。\n"
    "目的: <作業の目的。日本語の15文字以内の名詞句>\n"
    "完了: <何ができたら終わりか。日本語の15文字以内。例「MRを作成」「原因を特定」「方針を合意」>\n"
    "目的が既に決まっているときは、目的の行もそのまま出力し、完了の基準はその目的に対して書く。\n"
    "目的が決まっていないときは、最初の依頼から目的を決める。直近の依頼は完了の基準を絞るためだけに使う。\n"
    "チケットの題名があれば、目的はその題名を15文字以内に縮めたものにする。\n\n"
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
TICKET_KEY_ONLY = re.compile(r"[A-Z][A-Z0-9]{3,}-\d+")


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


def review_label(prompt):
    if REVIEW_WORD.search(prompt):
        iid = first_match(MR_ID_PATTERNS, prompt)
        if iid:
            return f"Codereview MR !{iid}"
    return None


def ticket_key(prompt):
    if TICKET_WORD.search(prompt):
        return first_match(TICKET_KEY_PATTERNS, prompt)
    return None


def first_found(finder, prompts):
    for prompt in prompts:
        found = finder(prompt)
        if found:
            return found
    return None


def fetch_ticket(key):
    try:
        result = subprocess.run(
            ["acli", "jira", "workitem", "view", key, "--fields", "summary", "--json"],
            capture_output=True, text=True, timeout=20,
        )
        summary = json.loads(result.stdout)["fields"]["summary"] if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, TypeError):
        summary = None
    return {"key": key, "summary": summary}


def state_path(session_id):
    return os.path.join(STATE_DIR, f"{session_id}.txt")


def read_state(session_id):
    try:
        with open(state_path(session_id)) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def write_state(session_id, **state):
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = state_path(session_id) + f".{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump(state, f, ensure_ascii=False)
    os.replace(tmp, state_path(session_id))


def apply_label(pane_id, label, previous_label=None):
    pane = (herdr("pane", "get", pane_id) or {}).get("pane")
    if not pane:
        return
    workspace = (herdr("workspace", "get", pane["workspace_id"]) or {}).get("workspace")
    if not workspace or workspace.get("label") == label:
        return

    if workspace.get("pane_count") == 1 or (previous_label and workspace.get("label") == previous_label):
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
    """最後の記録から親をたどり、今の会話に残っている依頼を古い順に返す。要約の前の依頼も含め、応答の途中で止めた依頼は除く。"""
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
        # 会話を要約した境目の記録は parentUuid を持たず、要約の前の記録を logicalParentUuid で指す
        last = entries[last].get("parentUuid") or entries[last].get("logicalParentUuid")

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


def excerpt(prompt):
    return prompt.strip()[:PROMPT_EXCERPT_CHARS]


def build_request(prompts, purpose, ticket=None):
    candidates = [
        p for p in prompts
        if not p.lstrip().startswith("/") and len(p.strip()) >= MIN_PROMPT_CHARS
    ]
    if not candidates:
        return None
    first, recent = candidates[0], candidates[1:][-RECENT_PROMPTS:]
    lines = [LABEL_PROMPT]
    if purpose:
        lines.append(f"決まっている目的: {purpose}\n")
    elif ticket and ticket.get("summary"):
        lines.append(f"チケットの題名: {ticket['summary']}\n")
    lines.append(f"最初の依頼:\n{excerpt(first)}\n")
    for i, prompt in enumerate(recent, 1):
        lines.append(f"直近の依頼{i}:\n{excerpt(prompt)}\n")
    return "\n".join(lines)


def clean(text):
    return text.strip().strip("「」\"'`*").strip()[:MAX_PART_CHARS]


def generate_parts(request):
    env = {k: v for k, v in os.environ.items() if not k.startswith("HERDR_")}
    result = subprocess.run(
        ["claude", "-p", "--model", "haiku", "--settings", '{"disableAllHooks":true}'],
        input=request,
        capture_output=True, text=True, timeout=60, env=env, cwd=os.path.expanduser("~"),
    )
    if result.returncode != 0:
        return None, None
    purpose = done = None
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("目的:") or line.startswith("目的："):
            purpose = clean(line[3:])
        elif line.startswith("完了:") or line.startswith("完了："):
            done = clean(line[3:])
    return purpose or None, done or None


def prompts_key(prompts):
    return hashlib.sha256("\0".join(prompts).encode()).hexdigest()


def run_label(session_id, pane_id, transcript_path):
    """切り離した子プロセスで名前を決めて付ける。生成中に新しい子プロセスが始まっていれば何もしない。"""
    prompts = active_prompts(transcript_path)
    if not prompts:
        return
    key = prompts_key(prompts)
    if read_state(session_id).get("key") == key:
        return
    state = read_state(session_id)
    previous_label = state.get("label")
    fixed = state.get("purpose")
    ticket = state.get("ticket")
    if not ticket or not ticket.get("summary"):
        # 課題キーだけを目的にしていた名前も、題名を取って付け直す
        found = first_found(ticket_key, prompts) or (fixed if fixed and TICKET_KEY_ONLY.fullmatch(fixed) else None)
        ticket = fetch_ticket(found) if found else None
    if ticket and fixed == ticket["key"]:
        fixed = None
    fixed = fixed or first_found(review_label, prompts)
    token = f"{os.getpid()}-{key}"
    write_state(session_id, key=key, token=token, label=previous_label, purpose=fixed, ticket=ticket)

    request = build_request(prompts, fixed, ticket)
    generated, done = generate_parts(request) if request else (None, None)
    purpose = fixed or generated or (ticket and ticket["key"])
    if not purpose:
        return
    label = f"{purpose}{SEPARATOR}{done}" if done else purpose

    if read_state(session_id).get("token") != token:
        return
    apply_label(pane_id, label, previous_label)
    write_state(session_id, key=key, token=token, label=label, purpose=purpose, ticket=ticket)


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
