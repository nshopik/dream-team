#!/usr/bin/env python3
"""Warns when an MR/PR description is over its diff budget; always exits 0."""
import argparse
import re
import subprocess
import sys
from pathlib import Path

DIFF_FACTOR = 5
DIFF_FLOOR = 80

# Named keys only: a bare `Word:` opener is ordinary prose.
TRAILER = re.compile(
    r'^(?:closes|fixes|resolves|refs|references|related|see[- ]also'
    r'|signed-off-by|co-authored-by|reviewed-by|acked-by|tested-by'
    r'|reported-by|suggested-by|part-of|change-id|cc|bug):\s'
    r'|^\(cherry picked from', re.I)
FENCE = re.compile(r'^```.*?^```', re.S | re.M)
TABLE = re.compile(r'^[ \t]*\|.*$', re.M)


def strip_trailers(lines):
    end = len(lines)
    while end and (not lines[end - 1].strip() or TRAILER.match(lines[end - 1])):
        end -= 1
    return lines[:end]


def count(text):
    # Fenced blocks and table rows are evidence, not prose; an unterminated fence stays counted.
    text = FENCE.sub(' ', '\n'.join(strip_trailers(text.split('\n'))))
    return len(TABLE.sub(' ', text).split())


def git(*args):
    p = subprocess.run(('git',) + args, capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


def numstat(*args):
    out = git('diff', '--numstat', *args) or ''
    return sum(int(c) for line in out.splitlines()
               for c in line.split('\t')[:2] if c.isdigit())


def diff_lines(base=None):
    """Lines changed against the base plus uncommitted ones; 0 means unmeasurable."""
    refs = (base, f'origin/{base}') if base else ('origin/HEAD', 'main', 'master')
    for ref in refs:
        mb = (git('merge-base', 'HEAD', ref) or '').strip()
        if mb:
            # The description is often written before the last commit lands.
            return numstat(f'{mb}..HEAD') + numstat('HEAD')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('body_file', help="description file, or '-' for stdin")
    ap.add_argument('--base')
    a = ap.parse_args()
    text = (sys.stdin.read() if a.body_file == '-'
            else Path(a.body_file).read_text(encoding='utf-8'))
    n = count(text)
    lines = diff_lines(a.base)
    if not lines:
        print(f'Description: {n} words; diff unmeasurable, no budget.')
        return
    budget = max(DIFF_FLOOR, DIFF_FACTOR * lines)
    print(f'Description: {n} words, diff: {lines} lines, budget: {budget} words.')
    if n > budget:
        print('Over budget: cut parts to what the diff cannot show, '
              'or keep it as a judged override.')


if __name__ == '__main__':
    main()
