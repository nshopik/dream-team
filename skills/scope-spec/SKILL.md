---
name: scope-spec
description: >
  Writes a project spec in the repo's specs folder: a date and status header, then context,
  decision, consequences, design and open items. Use when asked to write the spec, the v1 design,
  a design doc, or a cross-cutting design change. Not for feature work (file an issue with
  `scope-issue`) or cutting milestones from a spec (use `cut-milestones`).
disable-model-invocation: true
---

- On Codex, handle each AskUserQuestion step with the host's user-input tool when available.
- On Codex without that tool, ask the same questions in chat and wait for the reply before taking the gated action.

## spec-style

- Read [spec-template.md](spec-template.md) before writing; follow its section order.
- `git config --local --type=bool --get dream-team.own` prints `true` → path and filename: what
  `docs/CONVENTIONS.md` names.
- `dream-team.own` prints `true` and `docs/CONVENTIONS.md` does not exist → stop with "run
  `setup-dream-team` first".
- `dream-team.own` prints anything but `true` → path and filename from the upstream's `CLAUDE.md`,
  `AGENTS.md` or existing specs folder.
- `dream-team.own` prints anything but `true` and none of those names a specs path → write no
  spec.
- Terms: use `GLOSSARY.md` terms; coin none.
- Source: the conversation so far, plus any repo files or notes it names; never re-ask what it
  settles.
- A question the source leaves open → ask it with AskUserQuestion before writing; never guess.
- Write the answers into the spec.
- A Decision or Design point settled in an issue, MR or comment → end it with a link to it.
- A question the user cannot answer yet (needs research, a lab run, someone else) → an
  `## Open items` entry.
- Work that fits one issue → no spec; write its decision into the issue with `scope-issue`.
- The date goes in the header, never the filename.
- Header: `**Date:**` and `**Status:**` lines. No branch name.
- Status: `Draft`, then `Accepted`, which is terminal; or `Superseded by <spec-file>`.
- File lists, test cases, rejected options and milestones → issues, topic docs, decision records
  or the ROADMAP; never the spec.
- Length: aim for about 1,500 words, counted with `wc -w`.
- Draft over 2,000 words → ask with AskUserQuestion which Design subsections to move to a topic
  doc, one option per subsection.
