#!/usr/bin/env python3
"""Fails on a path from one skill or agent into another skill's files: a
`<base directory>/../<name>/` path, a `](../<name>/` markdown link, a backticked
`../<name>/` path or a `${CLAUDE_PLUGIN_ROOT}/skills/` path. Load the other skill by
name instead; `../../workflows/` paths are allowed.

usage: python3 test_skill_links.py
"""
import re
import subprocess
import sys

CROSS = re.compile(r'(<base directory>/|\]\(|`)(\./)?(\.\./)+(?!workflows/)[a-z]'
                   r'|CLAUDE_PLUGIN_ROOT\}/skills/')
assert CROSS.search('<base directory>/../craft-it/SKILL.md')
assert CROSS.search('see [x](../../references/glossary.md)')
assert CROSS.search('read `./../craft-it/SKILL.md`')
assert CROSS.search('${CLAUDE_PLUGIN_ROOT}/skills/craft-it/SKILL.md')
assert not CROSS.search('<base directory>/../../workflows/craft-it-loop.js')

paths = subprocess.run(['git', 'ls-files', 'skills', 'agents'], capture_output=True,
                       text=True, check=True).stdout.split()
assert paths, 'no files listed: run from the repo root'
bad = []
for path in paths:
    for n, line in enumerate(open(path, errors='ignore'), 1):
        if CROSS.search(line):
            bad.append(f'{path}:{n}: cross-skill path: {line.strip()}')
print('\n'.join(bad) or 'PASS skill links')
sys.exit(1 if bad else 0)
