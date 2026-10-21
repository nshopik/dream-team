#!/usr/bin/env python3
"""Fails on an agent or skill frontmatter value that strict YAML misreads, or on a reviewer
agent that is not kept off Edit and Write by a `disallowedTools` line.

usage: python3 test_frontmatter.py
"""
import glob
import re
import sys

WRITERS = {'agents/docs-editor.md', 'agents/lab-runner.md'}
bad = []
for path in sorted(glob.glob('agents/*.md') + glob.glob('skills/*/SKILL.md')):
    head = open(path).read().split('---')[1]
    for n, line in enumerate(head.splitlines(), 1):
        m = re.match(r'([\w-]+):\s+(.+)$', line)
        # A plain scalar ends at `: ` or ` #`; quoted and block scalars are safe.
        if m and m.group(2)[0] not in '\'"|>' and re.search(r': | #', m.group(2)):
            bad.append(f'{path}: frontmatter line {n}: `{m.group(1)}` has ": " or " #" in a plain value')
    lines = head.splitlines()
    if not path.startswith('agents/'):
        continue
    # pi's subagent extension reads only `tools:`, in its own lowercase names.
    if any(l.startswith('tools:') for l in lines):
        bad.append(f'{path}: an agent needs no `tools:` line')
    if path not in WRITERS and 'disallowedTools: Edit, Write, NotebookEdit' not in lines:
        bad.append(f'{path}: a reviewer needs `disallowedTools: Edit, Write, NotebookEdit`')
print('\n'.join(bad) or 'PASS frontmatter')
sys.exit(1 if bad else 0)
