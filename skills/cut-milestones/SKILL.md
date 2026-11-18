---
name: cut-milestones
description: >-
  Cuts an approved spec into ROADMAP milestones, each behind one measurable exit gate, with a
  dependency graph, and creates in the tracker only those ready to start, at most 3 open at once;
  or drafts one version milestone, named by its target month, for a release after the MVP. Use
  when the user asks to plan, cut, draft or split milestones — "cut milestones from the spec",
  "what are the milestones for the MVP", "split M4 in two", "plan 26.11", "plan 1.3". Not for
  filing a milestone's issues (use scope-issue) or closing one (use milestone-close).
argument-hint: <spec path | version>
---

# cut-milestones

Drafts milestones for the user to approve. Creates nothing in the tracker until the user sets
the numbers.

- An open tracker milestone is not numbered `M<n>`, `YY.MM` or `v<major>.<minor>` (SemVer past
  1.0) → stop before drafting and tell the user the repo may not be set up for dream-team, naming
  `setup-dream-team`.

## Rules

- Every milestone has a measurable exit criterion.
- One milestone, one exit gate: a design review, a build test, or field evidence.
- Two gates → two milestones.
- Work deferred to "its own plan" or "before Mn" is a ROADMAP row. List it now.
- The first milestone is the cheapest proof the approach works.
- A first milestone that can disprove the approach is a kill-gate: its criterion names the
  redesign on failure.
- Milestones with no dependency between them are listed as parallel.
- The dependency graph is drawn as a mermaid flowchart below the ROADMAP table.
- A milestone is `M<n>`: a capital M and a plain integer, no dash.
- A milestone is created in the tracker only once every milestone in its `Depends on:` is closed
  and fewer than 3 `M<n>` milestones are open; until then it is a `planned` ROADMAP row, named by
  its title.
- A version milestone is its target month `YY.MM` with no leading zero, such as `26.11` or `27.5`;
  in a SemVer repo past 1.0, `v<major>.<minor>`.
- The milestone that completes the MVP carries `MVP` in its title.
- A split takes the next free `M<n>`, never a letter.
- Work spanning several milestones is a `Meta:` issue per `scope-issue`, not a milestone.
- An issue in a milestone with an open dependency carries `workflow::future`; an issue in a ready
  milestone carries none.

## Numbers

- Thresholds, durations and percentages in a criterion are product decisions.
- Leave each as a placeholder, `<N days>`, `<max SERVFAIL %>`, for the user to set.

## Steps

1. Read the spec, the existing ROADMAP and the tracker milestones; the ROADMAP's path is what
   `<base directory>/../setup-dream-team/repo-conventions.md` resolves.
2. Draft each milestone: title, exit criterion, gate type, what it depends on, and for each to be
   created now a `<due date>` placeholder, 2–4 weeks out (the appetite). A
   dependency that gates only the exit measurement goes in the exit criterion, as "on a commit
   with Mn closed".
3. Draw the dependency graph: which milestones run in parallel, what waits on what.
4. Show the draft to the user. Stop until the user sets every placeholder.
5. Create each milestone whose dependencies are all closed, in draft order until 3 `M<n>`
   milestones are open, through the host's tooling skill, numbered with the next free `M<n>`, and
   for an `M<n>` milestone with the due date the user set as its tracker due date. Its
   description is three bullets:
   `- **Exit:**`, `- **Gate:**`, `- **Depends on:**` (milestones that must close before work can
   start, or `none`).
6. Add `workflow::future` to every open issue already in a milestone whose `Depends on:` has an
   open milestone.
7. Add one ROADMAP row per `M<n>` milestone, created or `planned`, in the same table as existing
   ones, when a ROADMAP exists, a row is `planned`, two or more `M<n>` milestones are open, or a
   `Depends on:` names an open `M<n>` milestone. A new ROADMAP gets a row for every open `M<n>`
   milestone and `planned` row.
8. Below a ROADMAP table with `M<n>` or `planned` rows, keep the dependency graph as a mermaid
   flowchart: one node per such row, labelled with its title, one edge per `Depends on:` entry.
9. Report the milestones created, the `planned` rows and the dependency graph.

## ROADMAP row

- Columns: `#`, `Milestone`, `Status`.
- `#` is the tracker `M<n>`, empty in a `planned` row.
- `Milestone` is the title, then `Exit:` and the criterion, then `Depends on:` and the titles of
  the milestones it waits on, or `none`.
- `Status` starts `not started` in a created milestone's row and `planned` in the others. Only
  `milestone-close` changes it.

A field-evidence milestone gets its `Evidence:` issue when its issues are filed, per
`scope-issue`.

## Version milestone

A release after the MVP: one headline feature, optional in flow mode, plus backlog.

- It needs no spec.
- Outside flow mode, its exit criterion: the headline issue closed.
- The project `CLAUDE.md` says `Version milestones release in flow mode.` → its `Exit:` is its
  due date, plus a headline as a target only when the user names one.
- Its `Gate:` bullet holds the release criteria.
- Outside flow mode, a headline with a spec takes its gate from the spec in place of the issue
  close.
- A `YY.MM` milestone gets the last day of its month as its tracker due date: `26.11` → 2026-11-30.
- A `v<major>.<minor>` milestone's criterion may add a ship-by date, left as a `<ship-by date>`
  placeholder; in flow mode the ship-by date is required and becomes its tracker due date.
- Backlog issues join the milestone as they are filed and carry no criterion of their own.
- No earlier version milestone to copy the release criteria from → draft them for the user to
  edit: CI green on the release commit, upgrade from the previous version works, and in a
  SemVer repo no breaking change in a minor version.
- Steps 1–3 shrink to: read the tracker milestones; outside flow mode, ask the user for the
  headline issue; draft the one milestone.
