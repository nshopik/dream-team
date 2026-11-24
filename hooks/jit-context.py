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

CODEX = sys.argv[1:] == ['--codex']
STATE = '/tmp/codex-jit-context' if CODEX else '/tmp/claude-jit-context'
GUIDANCE = r'(?:AGENTS|CLAUDE)(?:\.local)?\.md'


VCS = """<vcs_workflow>
About to touch git history or a forge. Feature work complete → push the branch and
open an MR/PR against the default branch (`glab mr create` / `gh pr create`). Don't
merge to the default branch locally; don't leave finished branches unpublished.
Small fixes (typo, one-liner, docs touch-up) may commit directly.

One logical change, one commit: a follow-up fix folds into the commit it repairs
before merge, never a "fix the fix" commit.
A late change the user asks for on an open MR/PR — an answer to a question, a
missed design tweak — amends the commit it changes (`git commit --amend`);
force-push (`--force-with-lease`). Never rewrite history on `main`/`master` or
any other shared branch.
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


NOTES = """<project_notes>
You make a mistake or get corrected, and a later session in this repo would repeat it
(a wrong command, a path or environment trap, a tool quirk) → add one imperative line
to the ignored `AGENTS.local.md` or `CLAUDE.local.md` matching the project’s
`AGENTS.md` or `CLAUDE.md`, and name the line in your summary. Before writing,
use `git check-ignore` on the selected file and add its root-relative path to
the file named by `git rev-parse --git-path info/exclude` if needed. End the line with the condition
that retires it: a tool or plugin version, a fix, a closed issue. Read the file first; a line
that already covers it gets sharpened, not repeated. A per-task artifact location
(harness copy, scratch directory, built binary, results file) never gets a line. A fact
about how the system works goes in the contributor doc instead.
</project_notes>"""

ISSUE_SIZED = """<issue_sized>
A change requested in chat is issue-sized when it needs a user decision, contradicts the spec,
adds a component, or needs a lab check.
- Issue-sized → give your assessment, then offer to file it with `scope-issue`; edit nothing.
- User asked for the issue in chat → settle its open questions, milestone included, by the
  `scope-issue` Open questions tiers before filing; write the answers into the issue.
- Issue found during other work (craft-it, a review, a lab check) → do not prompt; list the
  open questions as open items in the proposal, or file a `Research:` issue.
- Issue found during other work, not a `Research:` issue, open items in its proposal → add the
  `workflow::needs-brainstorm` label.
- Lab or research result for an open issue → post it as a comment on that issue; do not prompt.
- Smaller → make the change inline.
</issue_sized>"""

CLAUDE_MD = """<claude_md>
Editing AGENTS.md, CLAUDE.md, or their local notes.
- Put a correction or gotcha in the matching untracked `AGENTS.local.md` or
  `CLAUDE.local.md`, one imperative line. The user promotes it to the matching
  tracked file. Wait for the user before adding a line to the tracked file.
- Keep the line specific to this repo. General advice belongs in the user’s
  global `AGENTS.md` or `CLAUDE.md`.
- A fix that is a workflow goes in a skill in the host’s skill directory.
- Use `git check-ignore` before writing local notes. Add the notes file’s
  root-relative path to `git rev-parse --git-path info/exclude` if needed.
- Keep hostnames, IPs, internal URLs and lab access in ignored local notes.
- One fact per bullet.
- Keep each file under 8 KB. Move an outgrown section to a subdirectory
  `AGENTS.md`, `CLAUDE.md`, or a skill.
</claude_md>"""

UPSTREAM = """<upstream_repo>
This clone is not marked own (`dream-team.own` is not `true`): it is an upstream
project, not mine. Ask me to run `/dream-team:setup-dream-team` once here: it
writes the local tracker rules, or marks the clone own if it is mine.
- Its CONTRIBUTING, commit style, changelog and tracker conventions win where they
  conflict with mine (scope-commit, scope-mr, vcs workflow).
- Still load scope-commit and scope-mr; apply each rule upstream does not set.
- Agent notes go in ignored `AGENTS.local.md` or `CLAUDE.local.md`. Ask before
  adding or editing a checked-in `AGENTS.md` or `CLAUDE.md`.
- Add no docs to the repo, or issues, milestones or labels on its forge,
  unasked.
- Ask before opening an MR/PR, issue or comment on its forge.
</upstream_repo>"""

def is_upstream(payload):
    cwd = payload.get('cwd') or '.'
    path = payload['tool_input'].get('file_path') or ''
    d = os.path.dirname(os.path.join(cwd, path)) if path else cwd
    while d and not os.path.isdir(d):           # Write may target a dir not made yet
        d = os.path.dirname(d)
    try:
        p = subprocess.run(['git', '-C', d or '.', 'config', '--local', '--type=bool', '--get',
                            'dream-team.own'],
                           capture_output=True, text=True, timeout=5)
    except Exception:
        return False
    return 'inside a git repository' not in p.stderr and p.stdout.strip() != 'true'


# Lookbehind lets `sudo glab` / `/usr/bin/glab` match while `myglabthing`
# and `openssh` do not.
FORGE_CMD = r'(?<![\w.-])(glab|gh)\b'
PUBLISH_CMD = r'git\s+(commit|push)\b|' + FORGE_CMD

RULES = [
    # First: must land before the prose/vcs blocks it overrides. The predicate runs
    # git on every matching call, so a later write into another repo is still checked.
    ('upstream',  'file_path', r'.',                              UPSTREAM, is_upstream),
    ('upstream',  'command',   PUBLISH_CMD,                       UPSTREAM, is_upstream),
    # Paired file_path/command rows share a name: the sentinel dedupes, so a heredoc/sed
    # write (no file_path field) still gets the block exactly once.
    ('claude_md', 'file_path', rf'(^|/){GUIDANCE}$',       CLAUDE_MD),
    ('claude_md', 'command',   GUIDANCE,             CLAUDE_MD),
    # First: on `glab`/`gh` this fires once, then falls through to `forge` on the
    # next call — main() skips a rule that already fired this session.
    ('vcs',       'command',   PUBLISH_CMD,                       VCS),
    ('forge',     'command',   FORGE_CMD,                         FORGE),
    ('lab',       'command',   r'(?<![\w.-])ssh\b',               LAB),
    # Last: main() returns on first match, so CLAUDE.md keeps its own block.
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
    if CODEX:
        text = (text.replace('/dream-team:setup-dream-team', '$setup-dream-team')
                .replace('dream-team:lab-runner', 'dream-team-lab-runner'))
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
    inputs = [fields]
    if CODEX and payload.get('tool_name') == 'apply_patch':
        inputs = [{'file_path': path} for path in re.findall(
            r'^\*\*\* (?:(?:Add|Update|Delete) File|Move to): (.+)$',
            fields.get('command', ''), re.M,
        )]
    for name, field, pattern, text, *when in RULES:
        for tool_input in inputs:
            hit = re.search(pattern, tool_input.get(field) or '', re.I)
            if hit and all(w({**payload, 'tool_input': tool_input}) for w in when):
                if not fired(payload.get('session_id', ''), name):
                    emit('PreToolUse', text)
                    return
                break


if __name__ == '__main__':
    main()
