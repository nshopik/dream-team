#!/usr/bin/env python3
"""Runs SKILL.md step 6's change count and both folds on scratch repos with fixup! and amend!
commits. Usage: python3 test_fold.py"""
import os
import re
import subprocess
import tempfile

SKILL = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SKILL.md')).read()
BLOCKS = re.findall(r'```sh\n(.*?)```', SKILL, re.S)
COUNT = next(b for b in BLOCKS if 'grep -Evc' in b)
FOLD = next(b for b in BLOCKS if '--autosquash' in b)
FOLD_ONE = next(b for b in BLOCKS if 'reset --soft' in b)

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
    shas = {}
    for subject, name, text in commits:
        if subject.startswith('amend! '):
            # The fix stages' reword: --fixup=reword takes no -m, so an editor writes the message.
            with open(os.path.join(repo, '.git', 'reword-msg'), 'w') as f:
                f.write(f'{subject}\n\n{text}')
            sh("GIT_EDITOR='cp .git/reword-msg' git commit -q --cleanup=whitespace"
               f" --fixup=reword:{shas[subject[7:]]}")
            continue
        with open(os.path.join(repo, name), 'a') as f:
            f.write(text)
        sh(f"git add -A && git commit -q -m '{subject}'")
        shas[subject] = sh('git rev-parse HEAD')
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

base = scratch([('a: add', 'a.py', 'a = 1\n'), ('b: add', 'b.py', 'b = 1\n')])
sh("git commit -q --allow-empty -m 'amend! a: adds' -m 'a: reword'")
assert sh(FOLD.replace('<base>', base), check=False) != 0
print('PASS autosquash fold fails on an amend that names no commit')

for fold, changes in ((FOLD, ['a: add', 'b: add']), (FOLD_ONE, ['a: add'])):
    commits = [(c, c[0] + '.py', c[0] + ' = 1\n') for c in changes]
    base = scratch(commits + [('fixup! a: add', 'a.py', 'a += 1\n'),
                              ('amend! a: add', None, 'a: draft\n'),
                              ('amend! a: add', None, 'a: reword\n\n#1 changed it.\n')])
    assert sh(COUNT.replace('<base>', base)) == str(len(changes))
    sh(fold.replace('<base>', base).replace('<scratchpad>', repo + '/.git'))
    assert sh(f'git rev-list --count {base}..HEAD') == str(len(changes))
    first = sh(f'git rev-list --reverse {base}..HEAD').split()[0]
    assert sh(f'git log -1 --format=%B {first}') == 'a: reword\n\n#1 changed it.'
    assert sh(f'git show {first}:a.py') == 'a = 1\na += 1'
    print(f'PASS {len(changes)}-change fold takes the amend! message')
