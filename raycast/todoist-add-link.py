#!/usr/bin/env python3

# @raycast.schemaVersion 1
# @raycast.title Todoist にリンクを登録
# @raycast.mode compact
# @raycast.packageName Todoist
# @raycast.icon 🔗
# @raycast.argument1 { "type": "text", "placeholder": "URL または本文", "optional": true }
# @raycast.description 日付解析を通さずに Todoist へ登録する。URL だけ渡すとページタイトルを引く。

import html
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request

API = "https://api.todoist.com/rest/v2/tasks"
KEYCHAIN_SERVICE = "todoist-api-token"


def read_token():
    result = subprocess.run(
        ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.exit(
            "Keychain にトークンがない。次を実行して登録する:\n"
            f'  security add-generic-password -s {KEYCHAIN_SERVICE} -a "$USER" -w "<API token>"'
        )
    return result.stdout.strip()


def read_clipboard():
    return subprocess.run(["pbpaste"], capture_output=True, text=True).stdout.strip()


def fetch_title(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            body = response.read(200000).decode(charset, errors="replace")
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None
    match = re.search(r"<title[^>]*>(.*?)</title>", body, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return re.sub(r"\s+", " ", html.unescape(match.group(1))).strip() or None


def build_content(raw):
    if not re.fullmatch(r"https?://\S+", raw):
        return raw
    title = fetch_title(raw)
    return f"[{title}]({raw})" if title else raw


def add_task(content, token):
    request = urllib.request.Request(
        API,
        data=json.dumps({"content": content}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def main():
    raw = (sys.argv[1] if len(sys.argv) > 1 else "").strip() or read_clipboard()
    if not raw:
        sys.exit("登録する内容がない")

    content = build_content(raw)
    try:
        task = add_task(content, read_token())
    except urllib.error.HTTPError as error:
        sys.exit(f"Todoist API エラー {error.code}: {error.read().decode('utf-8', 'replace')}")

    print(f"登録: {task['content']}")


if __name__ == "__main__":
    main()
