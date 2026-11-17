---
name: setup-dream-team
description: >-
  Marks the user's own clone with a git config key, checks the project against the dream-team
  flow, applies fixes that change no code after one OK, commits its doc edits and files one
  maintenance issue for the other failing checks; in an upstream clone it only keeps
  CLAUDE.local.md out of git. Use when the user asks to set up, audit or align a project with the
  dream-team flow, or to mark a clone as their own. Not for working an issue (use build-issue) or
  closing a milestone (use milestone-close).
disable-model-invocation: true
---

# setup-dream-team

Bringing a project into line is a program, not a change. This skill audits, makes the
**Direct fixes** below after one confirm, commits its doc edits and files one issue for the rest.
It changes no code; the filed issue goes through `build-issue`. It marks an own clone with the
`dream-team.own` key; in an upstream clone it only adds `CLAUDE.local.md` to the git exclude file.

## Checks

- At least one open milestone is numbered `M<n>`, or `YY.MM` for a version milestone
  (`v<major>.<minor>` in a SemVer repo past 1.0) → each open milestone:
  - is numbered in one of those forms.
  - has a measurable exit criterion in its tracker description.
  - lists `Exit:`, `Gate:` and `Depends on:` as bold bullets in its description.
- The project `CLAUDE.md` says `Version milestones release in flow mode.` → a version
  milestone's `Exit:` naming its due date is its exit criterion.
- A ROADMAP exists, two or more `M<n>` milestones are open, or a `Depends on:` names an open
  `M<n>` milestone → each open `M<n>` milestone has a matching ROADMAP row.
- Each ROADMAP row is a tracker milestone, or has status `planned`, no `#` and no tracker
  milestone.
- A ROADMAP with a dependency graph or a `planned` row → the graph has one node per `M<n>` or
  `planned` row and one edge per row's `Depends on:` entry.
- A milestone gated on field evidence has one open `Evidence:` issue.
- Every open issue in an open milestone has exactly one kind label: `bug`, `feature`,
  `maintenance`, `performance`, `research` or `meta`.
- The tracker has an `area::` label → every open non-`Meta:` issue in an open milestone has an
  `area::` label.
- An open issue in a milestone carries `workflow::future` exactly when its milestone has an open
  dependency.
- A `Meta:` issue has no `area::` label, and a milestone only when every open child is in it.
- An issue with an open blocker ends with one `Blocked by #<n>` line per blocker.
- The specs folder holds only specs the code still follows; every other spec carries a
  `Superseded by` line.
- A component table, if the contributor doc has one, matches the code.
- A component table cell says only what the component's name and path don't.
- The repo has an architecture diagram → it matches the code.
- The tracker has every label in **Label colours** except `area::*`.
- The tracker has no `type::` label.
- The project `CLAUDE.md` carries the meaning of every rule in **Project rules** below.
- The project `CLAUDE.md` or `AGENTS.md` names a reference source, or names rules as a review
  invariant; a rule it only states is not one.
- A CHANGELOG's header links the Keep a Changelog version it follows.

## Project rules

The project `CLAUDE.md` carries these, in its own words:

- A project with an architecture diagram: it changes in the same MR as a component or pipeline
  change.
- Detail the code doesn't show goes in the commit, spec or a topic doc, never in module docs.
- A fact the code and paths don't show has one reference doc, updated in the MR that changes it.
- A project with a ROADMAP: its status changes only at milestone close.
- A project with floors: they rise in the feature MR that earns them.
- A project with a CHANGELOG: each entry is one plain sentence on a notable change, with no
  rationale.
- A CHANGELOG entry has no bold except a `**Breaking:**` or `**Upgrade note:**` prefix.
- A project with an open `M<n>`, `YY.MM` (version) or `v<major>.<minor>` (SemVer past 1.0)
  milestone: a new milestone takes only one of these forms that an open milestone already uses.
- A project with open `M<n>` milestones: a split takes the next free `M<n>`, never a letter.
- A project whose version milestones release at their due date: the line
  `Version milestones release in flow mode.`, verbatim.
- A project with a contributor doc: its path is named.

## Label colours

Values from GitLab's label-picker palette, except `wontfix`, which takes GitHub's default. Setup
sets a colour only on a label it creates.

| Label | Colour | Description |
|---|---|---|
| `bug` | `#D9534F` | |
| `feature` | `#44AD8E` | |
| `maintenance` | `#5BC0DE` | |
| `performance` | `#AD4363` | Throughput, CPU, memory or latency work, measured before and after |
| `meta` | `#8E44AD` | A `Meta:` checklist of child issues |
| `research` | `#F0AD4E` | Research with questions; a findings comment and follow-up issues, no code |
| `wontfix` | `#FFFFFF` | This will not be worked on |
| `area::*` | `#428BCA` | |
| `workflow::blocked` | `#34495E` | |
| `workflow::future` | `#7F8C8D` | |
| `workflow::needs-brainstorm` | `#D1D100` | |

## Direct fixes

- `CLAUDE.md` lacks a project rule → write it in the file's own words, merged into its existing
  structure.
- The project has neither `CLAUDE.md` nor `AGENTS.md` → create `CLAUDE.md` with the project
  rules.
- The project `CLAUDE.md` or `AGENTS.md` names no reference source or review invariant →
  draft candidate lines naming, as a review invariant, each rule the file already states that a
  diff can break, and naming each reference source the repo holds, such as a specs folder or a
  vendored standard.
- No such candidate exists → say in that check's step 5 line that build-issue's domain lens has
  nothing to check in this project and that a line naming a reference source or a review
  invariant would give it one, in place of a fix or a maintenance item.
- The tracker lacks a label from **Label colours** → create it with its colour and description.
- The tracker has a `type::<kind>` label, `<kind>` a kind in **Label colours** → swap it for
  `<kind>` on each issue that carries it, then delete the `type::` label.
- Any other `type::` label → an item in the maintenance issue.
- A milestone fails the bold-bullet check, but its description has its exit criterion, gate and
  dependencies → rewrite them as `Exit:`, `Gate:` and `Depends on:` bold bullets.
- An issue lacks the `Blocked by #<n>` line for an open blocker → append one line per missing
  blocker.
- An open issue in a milestone carries `workflow::future` without an open milestone dependency,
  or lacks it with one → add or remove the label.
- Any other failing check whose fix changes no code and the draft can state, tracker edits and
  repo docs included → a direct fix, shown in the step 8 draft.
- A failing check that needs a code change, or a decision the draft cannot state such as a missing
  exit criterion → an item in the maintenance issue (step 14).

## Steps

1. Ask whether the repo is the user's own project or an upstream project; a fork counts as own.
   - Upstream and `git check-ignore CLAUDE.local.md` prints nothing → add `CLAUDE.local.md` to
     the file `git rev-parse --git-path info/exclude` prints.
   - Upstream → write no marker, report whether `CLAUDE.local.md` was added to or already in the
     exclude file, and stop; change nothing else in the repo or its tracker.
   - Own → run `git config --local dream-team.own true`, then go on to step 2.
2. Read the project `CLAUDE.md` or `AGENTS.md`, the contributor doc, the ROADMAP and the specs
   folder, at the paths `<base directory>/../../references/repo-conventions.md` resolves.
3. Read the tracker's milestones, labels, open issues and every issue with a `type::` label
   through the host's tooling skill.
4. Run every check. Record pass or fail, with the evidence: issue numbers, file and line.
5. Report one line per check to the user before changing or filing anything.
6. All checks pass → say the project is aligned and stop.
7. No direct fix applies → go to step 12.
8. Show one combined draft of every direct fix: the `CLAUDE.md` and repo-doc diffs, the labels to
   create, each issue's `type::` to flat kind swap, the `type::` labels to delete, the labels and
   milestone to change per issue, each milestone title,
   milestone description and issue body before and after, and any issue or milestone to create.
9. Ask for one OK on the draft; a direct fix the user declines becomes an item in the
   maintenance issue.
10. Any approved `CLAUDE.md` or repo-doc edit → write them and commit only those files, in one
    commit per `scope-commit`, on the current branch, not pushed.
    - On `main` or `master` with a spec or design doc among those edits → run
      `git checkout -b <topic>` first and name the branch in the report.
11. Make the tracker changes through the host's tooling skill.
    - Create the missing labels before any swap.
    - Delete a `type::` label only after a fresh query shows no issue, open or closed, carries it.
    - A swap fails → keep that `type::` label and report the issue.
12. No failing check is left for the maintenance issue → report the fixes and any commit, and
    stop.
13. Ask which milestone takes the maintenance issue, suggesting one.
14. File one `maintenance` issue per `scope-issue`, in that milestone, with one item per
    remaining failing check.
15. A check that fails on many items → one item listing them.
16. Report the fixes, any commit and the filed issue. It is worked through `build-issue`.
