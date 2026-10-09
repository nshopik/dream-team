#!/usr/bin/env python3
"""Fails on an agent or skill frontmatter value that strict YAML misreads.

usage: python3 test_frontmatter.py
"""
import glob
import re
import sys

bad = []
for path in sorted(glob.glob('agents/*.md') + glob.glob('skills/*/SKILL.md')):
    head = open(path).read().split('---')[1]
    for n, line in enumerate(head.splitlines(), 1):
        m = re.match(r'([\w-]+):\s+(.+)$', line)
        # A plain scalar ends at `: ` or ` #`; quoted and block scalars are safe.
        if m and m.group(2)[0] not in '\'"|>' and re.search(r': | #', m.group(2)):
            bad.append(f'{path}: frontmatter line {n}: `{m.group(1)}` has ": " or " #" in a plain value')
print('\n'.join(bad) or 'PASS frontmatter')
sys.exit(1 if bad else 0)
