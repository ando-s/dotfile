#!/usr/bin/env python3
"""依頼から作業の目的と完了の基準を読み取り、herdr のワークスペースに名前を付ける。

名前は「<目的>｜ゴール:<完了の基準>」の形にする。「完了:」は終わったように読めるため使わない。

- 目的: 最初の目的は聞かずに付ける。最初の3件の依頼のあいだは、補足や言い直しで目的が変わったら案を作り、
  応答を終えるのを止めて Claude に承認を聞かせる。承認されたら --set-purpose で変え、断られたら --keep-purpose で以後は案を出さない。
  4件目からは目的を変えず、途中で作業が移っても名前の目的は動かさない
  - ワークスペースの名前が前回このフックが付けたものから変わっていれば、手で付け直したものとみなし、その目的を以後も使う
  - MR レビューの依頼があれば、最も古い依頼の MR の題名を glab から取り、"!<id> <Haiku が題名を縮めたもの>" を使う
    - 題名が取れなければ "!<id>" だけを使う
  - JIRA のチケットに取り組む依頼があれば、最も古い依頼の課題キーで題名を acli から取り、Haiku が題名を縮めて目的にする
    - 課題キーと題名は保存し、ステータスラインに出す。課題キーだけでは何の作業か分からないため、名前には入れない
  - どちらにも当たらなければ Haiku が最初の依頼から作る
- 完了の基準: その目的に対して、Haiku が最初の依頼と直近の依頼から作る
応答を終えるたびに、今の会話に残っている依頼の並びが前回と違えば完了の基準を付け直す。
Haiku が失敗したときは、目的が決まっていれば目的だけを付け、決まっていなければ名前を変えない。

Stop で動かし、会話記録で今の会話に残っている依頼だけを見る。送信を取り消した依頼は Stop を起こさず、
会話記録では別の枝に残る。応答の途中で止めた依頼は、直後に中断の記録が入る。どちらも名前の元にしない。

今のワークスペースにこのペインしか無いか、前回このセッションが付けた名前のままなら名前を変える。
それ以外でほかのペインもあれば何もしない。ペインを別のワークスペースへ移すことはしない。
既に同じ名前のワークスペースにいれば何もしない。失敗しても応答は止めない。
会話記録の読み取りと名前の生成は数秒かかるため、目的の案を出しうるとき以外は切り離した子プロセスで行う。
子プロセスが重なったときは、最後に始めたものだけが名前を付ける。
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

STATE_DIR = os.path.expanduser("~/.claude/herdr-sessions/labels")
MIN_PROMPT_CHARS = 8
PURPOSE_SETTLE_PROMPTS = 3
MAX_PART_CHARS = 18
RECENT_PROMPTS = 3
PROMPT_EXCERPT_CHARS = 600
SEPARATOR = "｜ゴール:"
# 前に使っていた区切り。手で付け直した名前と、前の名前から目的と完了の基準を分けるときにも区切りとして扱う
OLD_SEPARATORS = ("｜完了:", "｜進行中:")


def split_label(label):
    """名前を目的と完了の基準に分ける。区切りが無ければ完了の基準は None。"""
    for separator in (SEPARATOR, *OLD_SEPARATORS):
        if separator in label:
            purpose, done = label.split(separator, 1)
            return purpose.strip(), done
    return label.strip(), None

LABEL_PROMPT = (
    "herdr のワークスペース名を付ける。下の依頼から、このセッションの作業の目的と完了の基準を読み取り、"
    "次の2行だけを出力する。説明や記号は付けない。\n"
    "目的: <作業の目的。日本語の15文字以内の名詞句>\n"
    "完了: <何ができたら終わりか。日本語の15文字以内。例「MRを作成」「原因を特定」「方針を合意」>\n"
    "目的が既に決まっているときは、目的の行もそのまま出力し、完了の基準はその目的に対して書く。\n"
    "今の目的が示されているときは、補足や言い直しで目的そのものが変わったときだけ新しい目的を出し、"
    "変わっていなければ今の目的を一字も変えずに出力する。\n"
    "目的が決まっていないときは、最初の依頼から目的を決める。目的には、依頼が何を得たいか・何をしたいかを書き、"
    "依頼に出てくる語を組み替えて別の意味にしない。直近の依頼が最初の依頼の補足や言い直しなら目的に入れ、"
    "別の作業なら完了の基準を絞るためだけに使う。\n"
    "チケットか MR の題名があれば、目的はその題名を15文字以内に縮めたものにする。"
    "docs(nuts): のような接頭辞と、末尾の (NUTSAUCF-58) のような課題キーは入れない。\n\n"
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


def review_iid(prompt):
    if REVIEW_WORD.search(prompt):
        return first_match(MR_ID_PATTERNS, prompt)
    return None


def fetch_mr(iid):
    """MR の題名を取る。glab は今の作業ディレクトリのリポジトリを見る。"""
    try:
        result = subprocess.run(
            ["glab", "mr", "view", iid, "-F", "json"], capture_output=True, text=True, timeout=20,
        )
        title = json.loads(result.stdout)["title"] if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, TypeError):
        title = None
    return {"iid": iid, "title": title}


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


def set_by_hook(label):
    """どのセッションかがこのフックで付けた名前、または付けようとしている名前なら True。"""
    for path in glob.glob(os.path.join(STATE_DIR, "*.txt")):
        try:
            with open(path) as f:
                state = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(state, dict) and label in (state.get("label"), state.get("pending_label")):
            return True
    return False


def write_state(session_id, **state):
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = state_path(session_id) + f".{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump(state, f, ensure_ascii=False)
    os.replace(tmp, state_path(session_id))


def resolve_pane_id(session_id, pane_id):
    """ペインを別のワークスペースへ移すとペインIDが変わるため、見つからなければセッションIDで引き直す。"""
    if herdr("pane", "get", pane_id):
        return pane_id
    for pane in (herdr("pane", "list") or {}).get("panes", []):
        if (pane.get("agent_session") or {}).get("value") == session_id:
            return pane["pane_id"]
    return pane_id


def report_reference(pane_id, ticket, mr):
    """課題キーかMR番号を、サイドバーの $ref に出す。"""
    ref = (ticket or {}).get("key") or (f"!{mr['iid']}" if (mr or {}).get("iid") else None)
    if not ref:
        return
    pane, _ = current_workspace(pane_id)
    if not pane:
        return
    herdr("pane", "report-metadata", pane["pane_id"], "--source", "herdr-workspace-label", "--token", f"ref={ref}")
    herdr("workspace", "report-metadata", pane["workspace_id"], "--source", "herdr-workspace-label", "--token", f"ref={ref}")


def current_workspace(pane_id):
    pane = (herdr("pane", "get", pane_id) or {}).get("pane")
    if not pane:
        return None, None
    return pane, (herdr("workspace", "get", pane["workspace_id"]) or {}).get("workspace")


def apply_label(pane_id, label, previous_label=None):
    pane, workspace = current_workspace(pane_id)
    if not pane:
        return
    if not workspace or workspace.get("label") == label:
        return

    # ほかのペインと同居しているときは名前を変えない。ペインを別のワークスペースへ移すこともしない
    if workspace.get("pane_count") == 1 or (previous_label and workspace.get("label") == previous_label):
        herdr("workspace", "rename", pane["workspace_id"], label)


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


def candidate_prompts(prompts):
    return [p for p in prompts if not p.lstrip().startswith("/") and len(p.strip()) >= MIN_PROMPT_CHARS]


def build_request(prompts, purpose, ticket=None, current=None, mr=None):
    candidates = candidate_prompts(prompts)
    if not candidates:
        return None
    first, recent = candidates[0], candidates[1:][-RECENT_PROMPTS:]
    lines = [LABEL_PROMPT]
    if purpose:
        lines.append(f"決まっている目的: {purpose}\n")
    elif current:
        lines.append(f"今の目的: {current}\n")
    elif mr and mr.get("title"):
        lines.append(f"MR の題名: {mr['title']}\n")
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


def needs_ask(state, prompts):
    """目的の案を出して承認を聞きうるか。最初の目的が付いていて、まだ固定していない間だけ。"""
    if not state.get("purpose") or state.get("locked"):
        return False
    if state.get("ticket", {}) and state["ticket"].get("summary"):
        return False
    if first_found(review_iid, prompts):
        return False
    return len(candidate_prompts(prompts)) <= PURPOSE_SETTLE_PROMPTS


def run_label(session_id, pane_id, transcript_path, ask=False):
    """名前を決めて付ける。生成中に新しい処理が始まっていれば何もしない。
    ask のときは、目的が変わる案を返し、目的は変えずに完了の基準だけを付け直す。"""
    prompts = active_prompts(transcript_path)
    if not prompts:
        return None
    pane_id = resolve_pane_id(session_id, pane_id)
    key = prompts_key(prompts)
    if read_state(session_id).get("key") == key:
        return None
    state = read_state(session_id)
    previous_label = state.get("label")
    locked = bool(state.get("locked"))
    _, workspace = current_workspace(pane_id)
    shown = (workspace or {}).get("label")
    if previous_label and shown and not set_by_hook(shown):
        # 手で付け直した名前の目的を、以後も使う
        state["purpose"] = split_label(shown)[0]
        previous_label, locked = shown, True
    ticket = state.get("ticket")
    if not ticket or not ticket.get("summary"):
        # 課題キーだけを目的にしていた名前も、題名を取って付け直す
        stored = state.get("purpose")
        found = first_found(ticket_key, prompts) or (stored if stored and TICKET_KEY_ONLY.fullmatch(stored) else None)
        ticket = fetch_ticket(found) if found else None
    current = state.get("purpose")
    if ticket and current == ticket["key"]:
        current = None
    mr = state.get("mr")
    if not mr or not mr.get("title"):
        iid = first_found(review_iid, prompts) or (mr and mr.get("iid"))
        mr = fetch_mr(iid) if iid else None
    mr_prefix = f"!{mr['iid']}" if mr else None
    if mr and not locked and current and not current.startswith(mr_prefix + " "):
        # 前の形の名前（Codereview MR !<id>）は捨てて付け直す
        current = None
    settled = locked or (ticket and ticket.get("summary") and current) or (mr and current) \
        or len(candidate_prompts(prompts)) > PURPOSE_SETTLE_PROMPTS
    fixed = current if settled else None
    token = f"{os.getpid()}-{key}"
    base = dict(key=key, token=token, purpose=state.get("purpose"), ticket=ticket, mr=mr, locked=locked, pane_id=pane_id)
    # 課題と MR を引く間に一覧から名前を変えられていたら、変えた名前を残す
    if read_state(session_id).get("token") != state.get("token"):
        return None
    write_state(session_id, label=previous_label, **base)

    request = build_request(prompts, fixed, ticket, current, mr)
    generated, done = generate_parts(request) if request else (None, None)
    if mr and not fixed:
        generated = f"{mr_prefix} {generated}" if generated else mr_prefix
    purpose = fixed or generated or current or (ticket and ticket["key"])
    if not purpose:
        return None
    proposal = None
    if ask and current and purpose != current and purpose not in state.get("rejected", []):
        proposal, purpose = purpose, current
    label = f"{purpose}{SEPARATOR}{done}" if done else purpose

    if read_state(session_id).get("token") != token:
        return None
    base["purpose"] = purpose
    write_state(session_id, label=previous_label, pending_label=label, **base)
    apply_label(pane_id, label, previous_label)
    report_reference(resolve_pane_id(session_id, pane_id), ticket, mr)
    write_state(session_id, label=label, proposal=proposal, **base)
    return proposal


def set_purpose(session_id, purpose):
    """承認された目的に変え、以後は固定する。完了の基準は今のものを残す。"""
    state = read_state(session_id)
    pane_id = state.get("pane_id")
    previous_label = state.get("label")
    done = split_label(previous_label)[1] if previous_label else None
    label = f"{purpose}{SEPARATOR}{done}" if done else purpose
    # token を変え、裏で名前を作っている途中のフックに、前の目的で書き戻させない
    state.update(purpose=purpose, locked=True, proposal=None, pending_label=label, token=f"set-purpose-{os.getpid()}")
    write_state(session_id, **state)
    if pane_id:
        pane_id = resolve_pane_id(session_id, pane_id)
        apply_label(pane_id, label, previous_label)
    state.update(label=label, pane_id=pane_id)
    write_state(session_id, **state)
    print(f"ワークスペース名を「{label}」にしました")


def keep_purpose(session_id):
    """今の目的のまま固定し、以後は案を出さない。"""
    state = read_state(session_id)
    state.update(locked=True, proposal=None)
    write_state(session_id, **state)
    print(f"目的を「{state.get('purpose')}」のまま固定しました")


ASK_REASON = """ワークスペース名の目的を変える案があります。応答を続ける前に、AskUserQuestion で次の1問だけを聞いてください。
- 質問: ワークスペース名の目的を「{proposal}」に変えますか？（今は「{current}」）
- 選択肢1: 「{proposal}」に変える
- 選択肢2: 「{current}」のまま
答えに応じて、次のどれか1つを Bash で実行し、結果を1行で伝えて終えてください。ほかの作業はしないでください。
- 変える: python3 "$HOME/.claude/hooks/herdr-workspace-label.py" --set-purpose {sid} '{proposal}'
- そのまま: python3 "$HOME/.claude/hooks/herdr-workspace-label.py" --keep-purpose {sid}
- 自由に書かれた目的: python3 "$HOME/.claude/hooks/herdr-workspace-label.py" --set-purpose {sid} '<書かれた目的>'"""


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
    pane_id = os.environ["HERDR_PANE_ID"]
    state = read_state(session_id)
    # 承認を聞いたあとの応答の終わりには、もう一度聞かない
    if not payload.get("stop_hook_active") and needs_ask(state, active_prompts(transcript_path)):
        current = state.get("purpose")
        proposal = run_label(session_id, pane_id, transcript_path, ask=True)
        if proposal:
            reason = ASK_REASON.format(
                proposal=proposal.replace("'", ""), current=current, sid=session_id)
            print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
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
        elif len(sys.argv) == 4 and sys.argv[1] == "--set-purpose":
            set_purpose(sys.argv[2], sys.argv[3].strip()[:MAX_PART_CHARS * 2])
        elif len(sys.argv) == 3 and sys.argv[1] == "--keep-purpose":
            keep_purpose(sys.argv[2])
        else:
            main()
    except Exception:
        pass
