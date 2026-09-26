---
name: cut-milestones
description: >-
  Cut an approved spec into tracker milestones, each behind one measurable exit gate, with the
  dependency order and a ROADMAP table. Use when the user asks to plan, cut, draft or split
  milestones — "cut milestones from the spec", "what are the milestones for v1", "split M4 in
  two". Not for filing a milestone's issues (use scope-issue) or closing one (use
  milestone-close).
argument-hint: <spec path>
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
- A milestone takes a plain integer or a `major.minor` version.
- A split takes the next free numbers, never a letter.
- Work spanning several milestones is a `Meta:` issue per `scope-issue`, not a milestone.

## Numbers

- Thresholds, durations and percentages in a criterion are product decisions.
- Leave each as a placeholder, `<N days>`, `<max SERVFAIL %>`, for the user to set.

## Steps

1. Read the spec and the existing ROADMAP and tracker milestones.
2. Draft each milestone: number, title, exit criterion, gate type, what it depends on.
3. Write the dependency order: which milestones run in parallel, what waits on what.
4. Show the draft to the user. Stop until the user sets every placeholder.
5. Create each milestone through the host's tooling skill, the exit criterion in its
   description.
6. Add one ROADMAP row per milestone, in the same table as existing ones.
7. Report the milestones created and the dependency order.

## ROADMAP row

- Columns: `#`, `Milestone`, `Status`.
- `Milestone` is the title, then `Exit:` and the criterion.
- `Status` starts `not started`. Only `milestone-close` changes it.

A field-evidence milestone gets its `Evidence:` issue when its issues are filed, per
`scope-issue`.
