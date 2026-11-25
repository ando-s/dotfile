#!/usr/bin/env python3
"""Obsidian の今日の daily と home から、未チェックのタスクを書き出す。読むだけで、ノートは変えない。

使い方: obsidian_todo.py [YYYY-MM-DD]
出力（タブ区切り）: ノート・行番号・親の題名・題名・URL
  - ノートは daily か home
  - 親の題名は、未チェックの項目の下に入れた未チェックの項目のときだけ入る
  - 今日の daily が無いときは「daily が無い」と標準エラーに出し、home だけを書き出す
"""
import datetime
import pathlib
import re
import sys
import urllib.parse

VAULT = pathlib.Path.home() / "Documents" / "obsidian" / "armond"
VAULT_NAME = "armond"
# 「- [ ] 」「* [ ] 」。チェック済み（[x]）と、チェックの無い箇条書きは拾わない
UNCHECKED = re.compile(r"^(?P<indent>[\t ]*)[-*] \[ \] ?(?P<text>.*)$")


def note_url(rel: str) -> str:
    file = rel[:-3] if rel.endswith(".md") else rel
    return f"obsidian://open?vault={VAULT_NAME}&file={urllib.parse.quote(file, safe='')}"


def depth(indent: str) -> int:
    return len(indent.replace("    ", "\t"))


def unchecked(rel: str, kind: str):
    path = VAULT / rel
    if not path.exists():
        return None
    url = note_url(rel)
    parents = []  # (深さ, 題名)
    rows = []
    for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = UNCHECKED.match(line)
        if not m:
            continue
        d = depth(m["indent"])
        text = m["text"].strip()
        while parents and parents[-1][0] >= d:
            parents.pop()
        parent = parents[-1][1] if parents else ""
        parents.append((d, text))
        if text:
            rows.append((kind, str(no), parent, text, url))
    return rows


def main() -> int:
    day = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
    daily = unchecked(f"03_view/daily/{day}.md", "daily")
    if daily is None:
        print(f"daily が無い: 03_view/daily/{day}.md", file=sys.stderr)
        daily = []
    home = unchecked("03_view/home.md", "home") or []
    for row in daily + home:
        print("\t".join(row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
