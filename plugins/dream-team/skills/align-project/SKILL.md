---
name: align-project
description: >-
  Check a project against the dream-team flow and file one issue per failing check. Use when the
  user asks to bring a project into the dream-team flow, align it, upgrade it to the workflow, or
  asks whether a project is ready for dream-fixer — "align this repo", "is this project aligned",
  "move this project onto the dream-team flow". Not for working an issue (use dream-fixer) or
  closing a milestone (use milestone-close).
---

# align-project

Bringing a project into line is a program, not a change. This skill audits and files issues. It
changes no code, no docs and no tracker settings; the filed issues go through `dream-fixer`.

## Checks

- Milestones are numbered `M<n>`, or `v<major>.<minor>` for a version milestone.
- Each milestone has a measurable exit criterion in its tracker description.
- Each milestone has a matching ROADMAP row.
- A milestone gated on field evidence has one open `Evidence:` issue.
- Every open issue has a `type::` label, an `area::` label and a milestone.
- Each milestone description lists `Exit:`, `Gate:` and `Depends on:` as bold bullets.
- An open issue carries the waiting label exactly when its milestone has an open dependency.
- Every open issue runs context, problem, proposal, per `scope-issue`.
- A `Meta:` issue has no `area::` label and no milestone.
- An issue with an open blocker ends with one `Blocked by #<n>` line per blocker.
- `docs/specs/` holds only specs the code still follows; every other spec carries a
  `Superseded by` line.
- The component table in the contributor doc matches the code.
- Each `area::` label has one area section, in a shared area document or split into its own file.
- The contributor doc links every area document.
- No section of a shared area document runs over 100 lines.
- The architecture diagram matches the code.
- The tracker has the `type::scout` and `type::meta` labels.
- The project `CLAUDE.md` carries every rule in **Project rules** below.

## Project rules

The project `CLAUDE.md` carries these, in its own words:

- The architecture diagram changes in the same MR as a component or pipeline change.
- The component table in the contributor doc changes in the same MR, one row per component.
- Detail beyond a table row goes in the commit, spec or area document, never in module docs.
- An MR updates the area section of its issue's `area::` label in the same MR.
- ROADMAP status changes only at milestone close.
- Ratchet floors rise in the feature MR that earns them.
- A milestone is `M<n>`, or `v<major>.<minor>` for a version milestone.
- A milestone split takes the next free `M<n>`, never a letter.
- The contributor doc path is named.

## Steps

1. Read the project `CLAUDE.md`, the contributor doc, the ROADMAP and `docs/specs/`.
2. Read the tracker's milestones, labels and open issues through the host's tooling skill.
3. Run every check. Record pass or fail, with the evidence: issue numbers, file and line.
4. Report one line per check to the user before filing anything.
5. All checks pass → say the project is aligned and stop.
6. Ask which milestone takes the alignment issues.
7. File one issue per failing check, per `scope-issue`, in that milestone.
8. A check that fails on many items → one issue listing them, not one issue per item.
9. Report the filed issues. They are worked through `dream-fixer`, one at a time.
