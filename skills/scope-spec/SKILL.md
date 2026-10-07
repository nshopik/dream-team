---
name: scope-spec
description: >
  Writes a project spec in `docs/specs/`: a date and status header, then context, decision,
  consequences, design and open items. Use when asked to write the spec, the v1 design, a design
  doc, or a cross-cutting design change. Not for feature work (file an issue with `scope-issue`)
  or cutting milestones from a spec (use `cut-milestones`).
disable-model-invocation: true
---

## spec-style

- Read [spec-template.md](spec-template.md) before writing; follow its section order.
- Source: the conversation so far, plus any repo files or notes it names; never re-ask what it
  settles.
- A question the source leaves open → ask it with AskUserQuestion before writing; never guess.
- Write the answers into the spec.
- A question the user cannot answer yet (needs research, a lab run, someone else) → an
  `## Open items` entry.
- Work that fits one issue → no spec; write the decision into the issue with `scope-issue`.
- Filename: `docs/specs/NNNN-<topic>-design.md`.
- `NNNN`: four digits, sequential, starting at `0001`.
- The date goes in the header, never the filename.
- Header: `**Date:**` and `**Status:**` lines. No branch name.
- Status: `Draft`, then `Accepted`, which is terminal; or `Superseded by <spec-file>`.
- File lists, test cases, rejected options and milestones → issues, topic docs,
  `docs/decisions/` or the ROADMAP; never the spec.
