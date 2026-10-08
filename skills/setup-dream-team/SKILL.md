---
name: setup-dream-team
description: >-
  Checks a project against the dream-team flow, fixes mechanical failures directly and files one
  maintenance issue for the other failing checks. Not for working an issue (use dream-fixer) or
  closing a milestone (use milestone-close).
disable-model-invocation: true
---

# setup-dream-team

Bringing a project into line is a program, not a change. This skill audits, makes the
**Direct fixes** below after one confirm, and files one issue for the rest. It changes no code and
no docs besides `CLAUDE.md`; the filed issue goes through `dream-fixer`.

## Checks

- Milestones are numbered `M<n>`, or `v<major>.<minor>` for a version milestone.
- Each milestone has a measurable exit criterion in its tracker description.
- A ROADMAP exists, two or more milestones are open, or a `Depends on:` names an open milestone
  → each open milestone has a matching ROADMAP row.
- A milestone gated on field evidence has one open `Evidence:` issue.
- Every open issue has a `type::` label and an `area::` label.
- Every open issue has a milestone, or no milestone and the waiting or blocked label (parked).
- Each milestone description lists `Exit:`, `Gate:` and `Depends on:` as bold bullets.
- An open issue in a milestone carries the waiting label exactly when its milestone has an open
  dependency.
- Every open issue runs context, problem, proposal, per `scope-issue`.
- A `Meta:` issue has no `area::` label and no milestone.
- An issue with an open blocker ends with one `Blocked by #<n>` line per blocker.
- `docs/specs/` holds only specs the code still follows; every other spec carries a
  `Superseded by` line.
- A component table, if the contributor doc has one, matches the code.
- A component table cell says only what the component's name and path don't.
- The architecture diagram matches the code.
- The tracker has the `type::scout` and `type::meta` labels.
- Every label in **Label colours** that the tracker has carries its colour from there.
- The project `CLAUDE.md` carries the meaning of every rule in **Project rules** below.

## Project rules

The project `CLAUDE.md` carries these, in its own words:

- The architecture diagram changes in the same MR as a component or pipeline change.
- Detail the code doesn't show goes in the commit, spec or a topic doc, never in module docs.
- A fact the code and paths don't show has one reference doc, updated in the MR that changes it.
- A project with a ROADMAP: its status changes only at milestone close.
- Ratchet floors rise in the feature MR that earns them.
- A milestone is `M<n>`, or `v<major>.<minor>` for a version milestone.
- A milestone split takes the next free `M<n>`, never a letter.
- The contributor doc path is named.

## Label colours

Values from GitLab's label-picker palette; one colour per `type::` value, one for every `area::`.

| Label | Colour | Description |
|---|---|---|
| `type::bug` | `#D9534F` | |
| `type::feature` | `#44AD8E` | |
| `type::maintenance` | `#5BC0DE` | |
| `type::meta` | `#8E44AD` | A `Meta:` checklist of child issues |
| `type::scout` | `#F0AD4E` | Research with questions and a time box; a note and follow-up issues, no code |
| `area::*` | `#428BCA` | |
| Blocked label (`workflow::blocked` on GitLab) | `#34495E` | |
| Waiting label (`workflow::future` on GitLab) | `#7F8C8D` | |

## Direct fixes

- `CLAUDE.md` lacks a project rule → write it in the file's own words, merged into its existing
  structure.
- The project has neither `CLAUDE.md` nor `AGENTS.md` → create `CLAUDE.md` with the project
  rules.
- The tracker lacks `type::scout` or `type::meta` → create the label with its colour and
  description from **Label colours**.
- A label in **Label colours** has another colour → set its colour from there.
- A milestone description has its exit criterion, gate and dependencies, but not as bold bullets
  → rewrite them as `Exit:`, `Gate:` and `Depends on:` bold bullets.
- An issue lacks the `Blocked by #<n>` line for an open blocker → append one line per missing
  blocker.
- An open issue in a milestone carries the waiting label without an open milestone dependency,
  or lacks it with one → add or remove the label.
- Any other failing check → an item in the maintenance issue (step 13).

## Steps

1. Read the project `CLAUDE.md`, the contributor doc, the ROADMAP and `docs/specs/`.
2. Read the tracker's milestones, labels and open issues through the host's tooling skill.
3. Run every check. Record pass or fail, with the evidence: issue numbers, file and line.
4. Report one line per check to the user before changing or filing anything.
5. All checks pass → say the project is aligned and stop.
6. No direct fix applies → go to step 12.
7. Show one combined draft of every direct fix: the `CLAUDE.md` diff, the labels to create or recolour, the
   waiting labels to add or remove per issue, and each milestone description and issue body
   before and after.
8. Ask for one OK on the draft; a direct fix the user declines becomes an item in the
   maintenance issue.
9. Write the `CLAUDE.md` edit and leave it uncommitted.
10. Make the tracker changes through the host's tooling skill.
11. No other check fails → report the fixes and the uncommitted `CLAUDE.md`, and stop.
12. Ask which milestone takes the maintenance issue, suggesting one.
13. File one `type::maintenance` issue per `scope-issue`, in that milestone, with one item per
    remaining failing check.
14. A check that fails on many items → one item listing them.
15. Report the fixes, the uncommitted `CLAUDE.md` and the filed issue. It is worked through
    `dream-fixer`.
