#!/usr/bin/env python3
"""PreToolUse: inject a rule block the first time a session touches its subject.
SessionStart: inject the <project_notes> block.

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
About to ssh. If this is a lab / test-lab host, dispatch `dream-team:lab-runner`
instead of running ssh here; it picks the host from the repo's CLAUDE.md. Never
carry a hostname over from another project or a prior session.
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
Writing a spec (`docs/specs/NNNN-<topic>-design.md`, sequential numbering; the date
lives in the document header, not the filename)
— use the template at `{TEMPLATE}`; read it before writing.

- Header: `**Date:**` + `**Status:**` (`Draft` → `Accepted`, terminal; or
  `Superseded by <spec-file>`). No branch name.
- Sections: `## Context`, `## Decision`, `## Consequences`, `## Design`,
  `## Open items`. An empty one is deleted — never "N/A", never "None at this time".
- No per-change detail: file lists, test cases, rejected options and milestones go in
  issues, topic docs, `docs/decisions/` or the ROADMAP.
Prose rules still apply; they inject on the next file write of the session.
</spec_structure>"""


NOTES = """<project_notes>
You make a mistake, get corrected, or find something about this repo that is not
written down → add one imperative line to its `CLAUDE.local.md` and name the line in
your summary. Read the file first; a line that already covers it gets sharpened, not
repeated. A fact about how the system works goes in the contributor doc instead.
</project_notes>"""

ISSUE_SIZED = """<issue_sized>
A change requested in chat is issue-sized when it needs a user decision, contradicts the spec,
adds a component, or needs a lab check.
- Issue-sized → give your assessment, then offer to file it with `scope-issue`; edit nothing.
- User asked for the issue in chat → ask its open questions, milestone included, with
  AskUserQuestion before filing; write the answers into the issue.
- Issue found during other work (dream-fixer, a review, a lab check) → do not prompt; list the
  open questions as open items in the proposal, or file a `Scout:` issue.
- Smaller → make the change inline.
</issue_sized>"""

CLAUDE_MD = """<claude_md>
Editing a CLAUDE.md or CLAUDE.local.md.
- A correction or gotcha goes in the untracked `CLAUDE.local.md`, one imperative
  line. The user promotes lines to the tracked `CLAUDE.md`; never add one there unasked.
- Keep a line specific to this repo; general advice belongs in the user's global
  CLAUDE.md.
- A fix that is a workflow, not a rule → a skill in `.claude/skills/`, linked from
  `CLAUDE.local.md`.
- `git check-ignore CLAUDE.local.md` prints nothing → add it to `.git/info/exclude`
  before writing.
- Hostnames, IPs, internal URLs and lab access go in `CLAUDE.local.md` only, never in
  a tracked file.
- Keep each file under 500 lines; move an outgrown section to a subdirectory
  `CLAUDE.md` or a skill.
</claude_md>"""

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


# Lookbehind lets `sudo glab` / `/usr/bin/glab` match while `myglabthing`
# and `openssh` do not.
FORGE_CMD = r'(?<![\w.-])(glab|gh)\b'
PUBLISH_CMD = r'git\s+(commit|push)\b|' + FORGE_CMD

RULES = [
    # First: must land before the prose/vcs blocks it overrides. The predicate runs
    # git on every matching call, so a later write into another repo is still checked.
    ('upstream',  'file_path', r'.',                              UPSTREAM, is_upstream),
    ('upstream',  'command',   PUBLISH_CMD,                       UPSTREAM, is_upstream),
    ('changelog', 'file_path', r'(^|/)CHANGELOG(\.[\w-]+)?\.md$', CHANGELOG),
    ('changelog', 'command',   r'CHANGELOG(\.[\w-]+)?\.md',        CHANGELOG),
    ('spec',      'file_path', r'/specs?/.*-design\.md$',           SPEC),
    # Same name as the row above: the sentinel dedupes, so a heredoc/sed write
    # (no file_path field) still gets the block exactly once.
    ('spec',      'command',   r'specs?/[^\s\'"]*-design\.md',        SPEC),
    ('claude_md', 'file_path', r'(^|/)CLAUDE(\.local)?\.md$',       CLAUDE_MD),
    ('claude_md', 'command',   r'CLAUDE(\.local)?\.md',             CLAUDE_MD),
    # First: on `glab`/`gh` this fires once, then falls through to `forge` on the
    # next call — main() skips a rule that already fired this session.
    ('vcs',       'command',   PUBLISH_CMD,                       VCS),
    ('forge',     'command',   FORGE_CMD,                         FORGE),
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
    except Exception:                           # already fired, or unwritable state
        return True


def emit(event, text):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    if payload.get('hook_event_name') == 'SessionStart':
        emit('SessionStart', NOTES + '\n\n' + ISSUE_SIZED)
        return
    fields = payload.get('tool_input', {})
    for name, field, pattern, text, *when in RULES:
        hit = re.search(pattern, fields.get(field) or '', re.I)
        if hit and all(w(payload) for w in when) and not fired(payload.get('session_id', ''), name):
            emit('PreToolUse', text)
            return


if __name__ == '__main__':
    main()
