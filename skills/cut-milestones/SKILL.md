---
name: cut-milestones
description: >-
  Cuts an approved spec into tracker milestones, each behind one measurable exit gate, with
  dependency order and a ROADMAP table; or drafts one version milestone for a stable project's
  minor release. Use when the user asks to plan, cut, draft or split milestones — "cut
  milestones from the spec", "what are the milestones for v1", "split M4 in two", "plan 1.3".
  Not for filing a milestone's issues (use scope-issue) or closing one (use
  milestone-close).
argument-hint: <spec path | version>
---

# cut-milestones

Drafts milestones for the user to approve. Creates nothing in the tracker until the user sets
the numbers.

## Rules

- Every milestone has a measurable exit criterion.
- One milestone, one exit gate: a design review, a build test, or field evidence.
- Two gates → two milestones.
- Work deferred to "its own plan" or "before Mn" is a milestone. List it now.
- The first milestone is the cheapest proof the approach works.
- A first milestone that can disprove the approach is a kill-gate: its criterion names the
  redesign on failure.
- Milestones with no dependency between them are listed as parallel.
- The dependency order is written out.
- A milestone is `M<n>`: a capital M and a plain integer, no dash.
- A version milestone is `v<major>.<minor>`.
- A split takes the next free `M<n>`, never a letter.
- Work spanning several milestones is a `Meta:` issue per `scope-issue`, not a milestone.
- An issue in a milestone with an open dependency carries the host's waiting label
  (`workflow::future` on GitLab); an issue in a ready milestone carries none.

## Numbers

- Thresholds, durations and percentages in a criterion are product decisions.
- Leave each as a placeholder, `<N days>`, `<max SERVFAIL %>`, for the user to set.

## Steps

1. Read the spec and the existing ROADMAP and tracker milestones.
2. Draft each milestone: number, title, exit criterion, gate type, what it depends on. A
   dependency that gates only the exit measurement goes in the exit criterion, as "on a commit
   with Mn closed".
3. Write the dependency order: which milestones run in parallel, what waits on what.
4. Show the draft to the user. Stop until the user sets every placeholder.
5. Create each milestone through the host's tooling skill. Its description is three bullets:
   `- **Exit:**`, `- **Gate:**`, `- **Depends on:**` (milestones that must close before work can
   start, or `none`).
6. Add the waiting label to every open issue already in a milestone whose `Depends on:` has an
   open milestone.
7. Add one ROADMAP row per milestone, in the same table as existing ones, when a ROADMAP exists,
   two or more milestones are open, or a `Depends on:` names an open milestone. A new ROADMAP
   gets a row for every open milestone.
8. Report the milestones created and the dependency order.

## ROADMAP row

- Columns: `#`, `Milestone`, `Status`.
- `Milestone` is the title, then `Exit:` and the criterion.
- `Status` starts `not started`. Only `milestone-close` changes it.

A field-evidence milestone gets its `Evidence:` issue when its issues are filed, per
`scope-issue`.

## Version milestone

A minor release of a stable project: one headline feature plus backlog.

- It needs no spec.
- Its exit criterion: the headline issue closed.
- Its `Gate:` bullet holds the release criteria.
- A headline with a spec takes its gate from the spec in place of the issue close.
- The criterion may add a ship-by date, left as a `<ship-by date>` placeholder.
- Backlog issues join the milestone as they are filed and carry no criterion of their own.
- No earlier version milestone to copy the release criteria from → draft them for the user to
  edit: CI green on the release commit, no breaking change in a minor version, upgrade from the
  previous version works.
- Steps 1–3 shrink to: read the tracker milestones, ask the user for the headline issue, draft
  the one milestone.
