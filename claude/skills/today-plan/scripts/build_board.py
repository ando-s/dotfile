#!/usr/bin/env python3
"""今日のボードの JSON をひな形に流し込み、Artifact に出す HTML を書く。

使い方: build_board.py <data.json> <out.html>
"""
import json
import pathlib
import sys

TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "board" / "template.html"
REQUIRED = ("date", "dateLabel", "generatedAt", "columns")


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    lacking = [k for k in REQUIRED if k not in data]
    if lacking:
        print(f"足りない項目: {', '.join(lacking)}", file=sys.stderr)
        return 1
    # </script> で JSON の埋め込みが閉じないよう、< を逃がす
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/", payload)
    pathlib.Path(sys.argv[2]).write_text(html, encoding="utf-8")
    counts = {k: len(v) for k, v in data["columns"].items()}
    print(f"書き出し: {sys.argv[2]} {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
