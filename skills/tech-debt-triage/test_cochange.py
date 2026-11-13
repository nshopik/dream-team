#!/usr/bin/env python3
"""Runs SKILL.md step 1's co-change snippet on a synthetic git log stream.
Usage: python3 test_cochange.py"""
import os
import re
import subprocess

SKILL = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SKILL.md')).read()
SNIPPET = re.search(r"python3 -c '\n(.*?)\n'\n```", SKILL, re.S).group(1)

commits = (
    [['a.py', 'b.py', 'CHANGELOG.md']] * 5            # printed: 5 shared; CHANGELOG.md left out
    + [['a.py', 'c.py']] * 4                          # dropped: 4 shared
    + [['a.py', 'b.py'] + [f'x{i}.py' for i in range(29)]]  # dropped: 31 files
    + [['d.py', 'e.py']] * 5 + [['d.py']] * 30        # dropped: 5 shared at 25%
)
log = ''.join('\0\n\n' + '\n'.join(c) + '\n' for c in commits)
out = subprocess.run(['python3', '-c', SNIPPET], input=log, capture_output=True, text=True, check=True).stdout
assert out == 'a.py, b.py | 5 shared | 71%\n', out
print('ok')
