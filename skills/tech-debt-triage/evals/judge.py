#!/usr/bin/env python3
"""Builds the judge prompt for a case, or grades the judge's verdict lines against it.

usage: judge.py prompt <case.json> <repo path>
       judge.py grade <case.json> <verdicts.md>
"""
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / 'SKILL.md'


def prompt(case, repo):
    text = SKILL.read_text()
    brief = re.search(r'Judge brief, verbatim:\n\n```\n(.*?)\n```', text, re.S).group(1)
    lines = [f"{c['id']} | {c['claim']} | {c['location']} | {c['removes']}" for c in case['candidates']]
    print(brief.replace('<repo>', repo) + '\n\n' + '\n'.join(lines))


def grade(case, verdicts):
    got = dict(re.findall(r'^\W*(C\d+)\s*\|\s*(Act now|Later|Skip)\s*\|', Path(verdicts).read_text(), re.M))
    fails = 0
    for c in case['candidates']:
        want = {'Act now'} if c['expect'] == 'Act now' else {'Later', 'Skip'}
        v = got.get(c['id'], 'none')
        ok = v in want
        fails += not ok
        print(f"{c['id']:<4} {'/'.join(sorted(want)):<11} {v:<8} {'PASS' if ok else 'FAIL'}")
    print(f"{len(case['candidates']) - fails}/{len(case['candidates'])} verdicts match")
    return fails


if __name__ == '__main__':
    cmd, case, arg = sys.argv[1:]
    case = json.load(open(case))
    if cmd == 'prompt':
        prompt(case, arg)
    else:
        sys.exit(1 if grade(case, arg) else 0)
