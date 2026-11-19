#!/usr/bin/env python3
"""Fails on a path from one skill or agent into another skill's files: a
`<base directory>/../<name>/` path, a `](../<name>/` markdown link, a backticked
`../<name>/` path or a `${CLAUDE_PLUGIN_ROOT}/skills/` path. Load the other skill by
name instead; `../../workflows/` paths are allowed. Also fails on a `](x)` link, a
backticked `./x` path or a "`x` file in <skill>'s base directory" mention that names no
file, on a `skills/*/reference/` folder, and on an eval prompt whose inlined
`.dream-team/TRACKER.md` differs from `skills/setup-dream-team/tracker-local.md`.

usage: python3 test_skill_links.py
"""
import os
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

LOCAL = re.compile(r'\]\(([^)#:\s]+)(?:#[^)]*)?\)|`\./([^`\s]+)`')
NAMED = re.compile(r"`([\w.-]+)` file in ([\w-]+)'s base directory")
assert LOCAL.findall('see [w](WORKFLOW.md#1-x) and `./glossary.md`') == [
    ('WORKFLOW.md', ''), ('', 'glossary.md')]
assert NAMED.findall("per the `untriaged.md` file in\n  triage-issue's base directory"
                     .replace('\n  ', ' ')) == [('untriaged.md', 'triage-issue')]

paths = subprocess.run(['git', 'ls-files', 'skills', 'agents'], capture_output=True,
                       text=True, check=True).stdout.split()
assert paths, 'no files listed: run from the repo root'
bad = [f'{p}: reference/ folder: keep the file flat beside SKILL.md'
       for p in paths if re.match(r'skills/[^/]+/reference/', p)]
named = []
for path in paths:
    text = open(path, errors='ignore').read()
    md = path.endswith('.md')
    for n, line in enumerate(text.splitlines(), 1):
        if CROSS.search(line):
            bad.append(f'{path}:{n}: cross-skill path: {line.strip()}')
        for link, dot in LOCAL.findall(line) if md else []:
            if not os.path.exists(os.path.join(os.path.dirname(path), link or dot)):
                bad.append(f'{path}:{n}: no such file: {link or dot}')
    for name, skill in NAMED.findall(re.sub(r'\s+', ' ', text)) if md else []:
        named.append((name, skill))
        if not os.path.exists(f'skills/{skill}/{name}'):
            bad.append(f'{path}: no such file: skills/{skill}/{name}')
if ('untriaged.md', 'triage-issue') not in named:
    bad.append("craft-it's untriaged.md mention no longer matches NAMED: update the pattern")

tracker = open('skills/setup-dream-team/tracker-local.md').read().strip()
for path in subprocess.run(['git', 'ls-files', 'evals/*/prompt.md'], capture_output=True,
                           text=True, check=True).stdout.split():
    for block in re.findall(r'````\n(# Issue tracker: local files\n.*?)\n````',
                            open(path).read(), re.S):
        if block.strip() != tracker:
            bad.append(f'{path}: inlined TRACKER.md differs from tracker-local.md')
print('\n'.join(bad) or 'PASS skill links')
sys.exit(1 if bad else 0)
