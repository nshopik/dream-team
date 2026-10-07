#!/usr/bin/env python3
"""PreToolUse gate: refuse to author a design/spec/plan doc on main/master.

Carries the **Never author or commit a design/spec on `main`/`master`** rule so
CLAUDE.md does not have to. Fires at the moment of authoring rather than at
commit time, which is when the branch is still cheap to create.

Allows silently on anything it cannot confidently parse — a false block is
worse than a missed one.
"""
import json
import os
import re
import subprocess
import sys

# Path shapes that mean "design document", not ordinary source.
DESIGN = re.compile(r"""
    (^|/)(SPEC|DESIGN)\.md$
  | (^|/)docs/(specs|plans|decisions)/
  | (^|/)(specs|plans)/[^/]+\.md$
  | -(design|plan|spec)\.md$
""", re.VERBOSE | re.IGNORECASE)

PROTECTED = {'main', 'master'}

REMINDER = """<branch_guard>
`{path}` is a design/spec/plan document and you are on `{branch}`.

Never author or commit a design, spec, or plan on main/master.

- In-place execution: `git checkout -b <topic>` first, then retry this write.
- Worktree / parallel-agent execution: let the isolation step create the
  branch. A `git checkout -b` in the primary checkout blocks
  `git worktree add -b` and defeats the isolation — prefer the native
  worktree tool over raw `git worktree add`.
</branch_guard>"""


def branch_of(path):
    """Current branch of the repo containing path, or None if not a repo."""
    d = os.path.dirname(os.path.abspath(path)) or '.'
    while not os.path.isdir(d):                 # new file in a new subdir
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent
    try:
        r = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                           cwd=d, capture_output=True, text=True, timeout=3)
    except Exception:
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def main():
    try:
        path = json.load(sys.stdin).get('tool_input', {}).get('file_path', '')
    except Exception:
        return
    if not path or not DESIGN.search(path):
        return
    branch = branch_of(path)
    if branch not in PROTECTED:
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": REMINDER.format(path=path, branch=branch),
        }
    }))


if __name__ == '__main__':
    main()
