#!/usr/bin/env python3
"""正本の HTML から、Artifact 用（外側の html/head/body を外したもの）を作る。

使い方: python3 -I build_outputs.py <正本.html> <Artifact用の出力先.html>
"""
import sys
from pathlib import Path

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
s = src.read_text(encoding="utf-8")

a = s.index("<title>")
b = s.index("</body>")
body = s[a:b].replace("</head>\n<body>", "")
body = body.replace(
    "<title>Nuts 移行 マイルストーン計画</title>",
    '<title>Nuts 移行 マイルストーン計画</title>\n<meta name="claude:viewport-fit-sides" content="cover">',
    1,
)
dst.write_text(body, encoding="utf-8")

print(f"artifact: {dst}\ntemplates: {s.count('<template data-plan=')}")
