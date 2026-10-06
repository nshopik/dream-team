#!/usr/bin/env python3
"""Runs SKILL.md step 7's change count and autosquash fold on a scratch repo with two changes and
their fixups. Usage: python3 test_fold.py"""
import os
import re
import subprocess
import tempfile

SKILL = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SKILL.md')).read()
BLOCKS = re.findall(r'```sh\n(.*?)```', SKILL, re.S)
COUNT = next(b for b in BLOCKS if 'grep -vc' in b)
FOLD = next(b for b in BLOCKS if '--autosquash' in b)

env = {**os.environ, 'GIT_EDITOR': 'false'}


def sh(cmd, check=True):
    r = subprocess.run(['bash', '-ec', cmd], cwd=repo, env=env, capture_output=True, text=True)
    assert r.returncode == 0 or not check, r.stderr
    return r.stdout.strip() if check else r.returncode


def scratch(commits):
    global repo
    repo = tempfile.mkdtemp()
    sh('git init -q && git config user.name t && git config user.email t@t'
       ' && git commit -q --allow-empty -m "repo: start"')
    base = sh('git rev-parse HEAD')
    for subject, name, text in commits:
        with open(os.path.join(repo, name), 'a') as f:
            f.write(text)
        sh(f"git add -A && git commit -q -m '{subject}'")
    return base


base = scratch([('a: add', 'a.py', 'a = 1\n'), ('b: add', 'b.py', 'b = 1\n'),
                ('fixup! a: add', 'a.py', 'a += 1\n'), ('fixup! a: add', 'a.py', 'a += 2\n'),
                ('fixup! b: add', 'b.py', 'b += 1\n')])
assert sh(COUNT.replace('<base>', base)) == '2'
sh(FOLD.replace('<base>', base))
assert sh(f'git log --reverse --format=%s {base}..HEAD').split('\n') == ['a: add', 'b: add']
assert sh('git show --format= --name-only HEAD~1') == 'a.py'
assert sh('git show HEAD~1:a.py') == 'a = 1\na += 1\na += 2'
assert sh('git show --format= --name-only HEAD') == 'b.py'
print('PASS autosquash fold keeps one commit per change')

base = scratch([('a: add', 'a.py', 'a = 1\n'), ('b: add', 'b.py', 'b = 1\n'),
                ('fixup! a: adds', 'a.py', 'a += 1\n')])
assert sh(FOLD.replace('<base>', base), check=False) != 0
print('PASS autosquash fold fails on a fixup that names no commit')
