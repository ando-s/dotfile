"""文書のリンク切れと、README からたどれない文書を検出する。問題があれば終了コード2。"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SOURCES = [ROOT / 'README.md', ROOT / 'AGENTS.md', *ROOT.glob('docs/**/*.md'), *ROOT.glob('.claude/skills/**/*.md')]
LINK = re.compile(r'\[[^\]]*\]\(([^)\s]+)\)')


def targets(path):
    text = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
    for raw in LINK.findall(text):
        if re.match(r'[a-z]+:', raw) or raw.startswith('#'):
            continue
        yield raw, (path.parent / unquote(raw.split('#')[0])).resolve()


def main():
    problems = []
    for path in SOURCES:
        for raw, target in targets(path):
            if not target.exists():
                problems.append(f'リンク切れ: {path.relative_to(ROOT)} → {raw}')

    reachable, queue = set(), [ROOT / 'README.md']
    while queue:
        path = queue.pop()
        if path in reachable or path.suffix != '.md' or not path.exists():
            continue
        reachable.add(path)
        queue.extend(target if target.is_file() else target / 'README.md' for _, target in targets(path))
    for path in ROOT.glob('docs/**/*.md'):
        if path.resolve() not in reachable:
            problems.append(f'README からたどれない: {path.relative_to(ROOT)}')

    if problems:
        print('\n'.join(problems), file=sys.stderr)
        # Stop フックから呼ばれたときは、直せない問題で終了できなくならないよう2回目は止めない。
        if '--hook' in sys.argv and json.loads(sys.stdin.read() or '{}').get('stop_hook_active'):
            sys.exit(0)
        sys.exit(2)
    print('文書の検査: 問題なし')


if __name__ == '__main__':
    main()
