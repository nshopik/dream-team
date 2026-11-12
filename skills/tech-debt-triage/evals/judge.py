#!/usr/bin/env python3
"""Builds the judge prompt for a case, or grades the judge's verdict lines against it.

usage: judge.py prompt <case.json> <repo path>
       judge.py grade <case.json> <verdicts.md> [verdicts.md ...]
"""
import json
from collections import Counter
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / 'SKILL.md'


def prompt(case, repo):
    text = SKILL.read_text()
    brief = re.search(r'Judge brief, verbatim:\n\n```\n(.*?)\n```', text, re.S).group(1)
    lines = [f"{c['id']} | {c['claim']} | {c['location']} | {c['removes']}" for c in case['candidates']]
    print(brief.replace('<repo>', repo) + '\n\n' + '\n'.join(lines))


def grade(case, files):
    runs = [dict(re.findall(r'^\W*(C\d+)\s*\|\s*(Act now|Later|Skip)\s*\|', Path(f).read_text(), re.M))
            for f in files]
    fails, splits = 0, []
    for c in case['candidates']:
        want = {'Act now'} if c['expect'] == 'Act now' else {'Later', 'Skip'}
        vs = [r.get(c['id'], 'none') for r in runs]
        top, n = Counter(vs).most_common(1)[0]
        ok = sum(v in want for v in vs) * 2 > len(vs)
        fails += not ok
        if n < len(vs):
            splits.append(f"{c['id']}: {', '.join(vs)}")
        print(f"{c['id']:<4} {'/'.join(sorted(want)):<11} {top if n * 2 > len(vs) else 'split':<8} "
              f"{'PASS' if ok else 'FAIL'}  ({', '.join(vs)})")
    print(f"{len(case['candidates']) - fails}/{len(case['candidates'])} candidates pass by majority "
          f"of {len(files)} runs")
    for line in splits:
        print(f"split: {line}")
    return fails


if __name__ == '__main__':
    cmd, case, *args = sys.argv[1:]
    case = json.load(open(case))
    if cmd == 'prompt':
        prompt(case, args[0])
    else:
        sys.exit(1 if grade(case, args) else 0)
