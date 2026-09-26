#!/usr/bin/env python3
"""PreToolUse: inject a rule block the first time a session touches its subject.

Holds conventions that only matter in the minority of sessions that reach for
them, so CLAUDE.md does not carry them in every session. Each block is emitted
at most once per session — a sentinel file keyed by session id and rule name.

Adding a rule: append `(name, tool_input field, regex, text[, predicate])` to RULES.
"""
import json
import os
import re
import subprocess
import sys

STATE = '/tmp/claude-jit-context'


CHANGELOG = """<changelog_style>
Editing a CHANGELOG — keep it to Keep a Changelog 2.0.0
(https://keepachangelog.com/en/2.0.0/).

- `## [Unreleased]` accumulates entries as work lands, grouped
  `### Added` / `Changed` / `Deprecated` / `Removed` / `Fixed` / `Security`.
- Release: rename `[Unreleased]` to `[<version>] - <date>`, add a fresh empty
  one above. CI sources the GitLab/GitHub Release description from the section
  matching the tag, not from commits or the tag message.
- Entries are one plain, complete sentence — enough to understand what was
  added/changed/fixed/removed, no more. No rationale, benchmarks, or metric
  names — those belong in the commit body. Kernel/Prometheus density, not blog
  post.
- No bold, no `**lead** — clause` shape (mixing styles): `**Breaking:**` and
  `**Upgrade note:**` are the only bold, as entry prefixes.
- Curate: notable changes only. Skip internal refactors, test-only changes,
  anything with no observable effect. Machines draft, humans decide.
- Breaking changes: prefix the entry `**Breaking:**` and name the interface
  that breaks (CLI, API, protocol, config, schema).
- A required operator action on upgrade: prefix the entry `**Upgrade note:**`.
</changelog_style>"""

VCS = """<vcs_workflow>
About to touch git history or a forge. Feature work complete → push the branch and
open an MR/PR against the default branch (`glab mr create` / `gh pr create`). Don't
merge to the default branch locally; don't leave finished branches unpublished.
Small fixes (typo, one-liner, docs touch-up) may commit directly.

A follow-up fix to an earlier commit amends it (`git commit --amend`) rather than
stacking "fix the fix" — one logical change, one commit; force-push
(`--force-with-lease`) a topic branch under review. Never rewrite history on
`main`/`master` or any other shared branch.
</vcs_workflow>"""

FORGE = """<forge_tooling>
About to run `glab` or `gh`. If a skill covers this repo's forge host, invoke it
before going further: it carries that host's API workarounds and label conventions.
</forge_tooling>"""

LAB = """<lab_host>
About to ssh. If this is a lab / test-lab host, invoke the `lab-host` skill
first — it carries the connection aliases, the subagent-dispatch rule, and the
working-dir layout. The lab host is whichever one the repo names; a project
`CLAUDE.md` naming its own wins. Never carry a hostname over from another
project or a prior session.
</lab_host>"""

PROSE = """<prose_style>
Writing prose to disk — doc, comment, commit body, MR text. Every sentence
states a checkable fact: a file, a number, a behaviour, a decision, a
constraint. Delete any sentence that survives deletion without loss.

Banned outright, these are the leak:
- Meta-commentary on your own work or process — "that's on me", "which is
  the whole point", "my analysis stays boring", "worth noting".
- Metaphor for code or text — "the bones are right", "the voice is yours",
  "load-bearing", "the shape of it".
- Rhythm devices: sentence-initial "And,"/"But,"; a short punchy fragment for
  emphasis; antithesis ("not X, but Y"); rule-of-three lists.
- Reassurance or praise aimed at the reader.
- Abstract nouns standing in for a named thing — say `flushWorker`, not
  "the machinery"; say 500,000 rows, not "the sizing".

Test before saving: could a reader disagree with this sentence on the facts?
If not, it is decoration. Cut it.
</prose_style>"""


TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'reference', 'spec-template.md')

SPEC = f"""<spec_structure>
Writing a design doc / spec (`docs/superpowers/specs/NNNN-<topic>-design.md`, sequential
ADR numbering; the date lives in the document header, not the filename)
— use the lean-ADR template at `{TEMPLATE}`; read it before writing.
This overrides the brainstorming skill's freeform default.

- Header: `**Date:**` + `**Status:**` (`Draft` → `Accepted`, terminal; or
  `Superseded by <spec-file>`). No branch name.
- `## Context`, `## Decision`, `## Consequences` are mandatory. Every other section
  is deleted when it would be empty — never "N/A", never "None at this time".
- `## Consequences` names at least one negative, or it is not finished.
- `## Rejected alternatives`: one bullet each, option then what killed it. Not a
  pros/cons matrix.
- `## Expertise required` goes directly after `## Decision`. A fresh agent reads it
  to pick reviewers and implementers before it has read the Design, so it must be
  above the bulk, not below it.
- One spec lands one feature. Needs two → split it.
Prose rules still apply; they inject on the next file write of the session.
</spec_structure>"""


UPSTREAM = """<upstream_repo>
This repo has a git remote outside the namespaces in `DREAM_TEAM_OWN_REMOTES`: it is
an upstream project, not mine.
- Its CONTRIBUTING, commit style, changelog and tracker conventions override mine
  (scope-commit, scope-mr, Keep a Changelog, vcs workflow).
- Agent notes go in untracked `CLAUDE.local.md` only; never add or edit a
  checked-in `CLAUDE.md`.
- Add no docs, issues, milestones or labels unasked.
- Ask before opening an MR/PR, issue or comment on its forge.
</upstream_repo>"""

# A regex matched against each remote URL; unset disables the upstream rule.
OWN = os.environ.get('DREAM_TEAM_OWN_REMOTES')
OWN = re.compile(OWN, re.I) if OWN else None


def upstream_remote(urls):
    """True if any remote URL is outside my namespaces."""
    return OWN is not None and any(not OWN.search(u) for u in urls)


def is_upstream(payload):
    d = os.path.dirname(payload['tool_input'].get('file_path') or '') or payload.get('cwd') or '.'
    while d and not os.path.isdir(d):           # Write may target a dir not made yet
        d = os.path.dirname(d)
    try:
        out = subprocess.run(['git', '-C', d or '.', 'remote', '-v'],
                             capture_output=True, text=True, timeout=5).stdout
    except Exception:
        return False
    return upstream_remote(line.split()[1] for line in out.splitlines())


RULES = [
    # First: must land before the prose/vcs blocks it overrides. The predicate runs
    # git on every matching call, so a later write into another repo is still checked.
    ('upstream',  'file_path', r'.',                              UPSTREAM, is_upstream),
    ('upstream',  'command',   r'git\s+(commit|push)\b|(?<![\w.-])(glab|gh)\b', UPSTREAM, is_upstream),
    ('changelog', 'file_path', r'(^|/)CHANGELOG(\.[\w-]+)?\.md$', CHANGELOG),
    ('changelog', 'command',   r'CHANGELOG(\.[\w-]+)?\.md',        CHANGELOG),
    ('spec',      'file_path', r'/specs?/.*-design\.md$',           SPEC),
    # Same name as the row above: the sentinel dedupes, so a heredoc/sed write
    # (no file_path field) still gets the block exactly once.
    ('spec',      'command',   r'specs?/[^\s\'"]*-design\.md',        SPEC),
    # Lookbehind lets `sudo glab` / `/usr/bin/glab` match while `myglabthing`
    # and `openssh` do not.
    # First: on `glab`/`gh` this fires once, then falls through to `forge` on the
    # next call — main() skips a rule that already fired this session.
    ('vcs',       'command',   r'git\s+(commit|push)\b|(?<![\w.-])(glab|gh)\b', VCS),
    ('forge',     'command',   r'(?<![\w.-])(glab|gh)\b',          FORGE),
    ('lab',       'command',   r'(?<![\w.-])ssh\b',               LAB),
    # Last: main() returns on first match, so CHANGELOG keeps its own block.
    ('prose',     'file_path', r'.',                              PROSE),
]


def fired(session, name):
    """True if this rule already fired in this session; marks it if not."""
    if not session:
        return True                             # unkeyable → stay quiet
    try:
        os.makedirs(STATE, exist_ok=True)
        flag = os.path.join(STATE, f'{re.sub(r"[^A-Za-z0-9_-]", "", session)}.{name}')
        fd = os.open(flag, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        return False
    except FileExistsError:
        return True
    except Exception:
        return True                             # unwritable state → stay quiet


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    fields = payload.get('tool_input', {})
    for name, field, pattern, text, *when in RULES:
        hit = re.search(pattern, fields.get(field) or '', re.I)
        if hit and all(w(payload) for w in when) and not fired(payload.get('session_id', ''), name):
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": text,
                }
            }))
            return


if __name__ == '__main__':
    main()
