---
name: assemble-meta
description: >-
  Takes a tracker Meta issue to one MR/PR: triages the Meta issue and every child before any
  code, asking all open questions in one batch, builds up to two children at once up to the gate,
  each on its own branch in its own worktree, lands them on one integration branch through the
  assemble-meta-loop workflow, reviews and fixes the whole branch once, and opens one MR/PR with
  one commit per change. Use when the user runs /dream-team:assemble-meta or asks to build, work
  or ship a Meta issue's children together, on one branch or as one MR/PR — e.g.
  "assemble-meta #40", "do Meta #40 in one MR". Not for a single issue (run craft-it).
argument-hint: <meta-issue-number>
---

# assemble-meta

One Meta issue per invocation.

- Before step 1, call the Skill tool with `dream-team:craft-it`; read it as a reference, do not
  run it.
- Each "craft-it step N" below runs as written there, with the Meta issue's number as `<n>`.

You are the orchestrator, as in craft-it: **you do not write the change**. Your only edits
are craft-it's step-5 edits. Lab work is yours, per craft-it.

## 1. Read the Meta issue and its children

- Fetch the Meta issue with craft-it step 1's fetch command; its Meta stop does not apply.
- Take every unticked link to an open child issue in its checklist; skip plain-text lines.
- Fetch each child the same way, and note its `Blocked by` issues.
- A child blocked by an open issue that is not a child → leave it and its dependents out, and
  report them.
- A child whose title starts `Research:` → leave it and its dependents out, and report them.
- No child left → report it and stop.

## 2. Triage everything before code

- Triage the Meta issue and every child per craft-it step 2, before step 3.
- Collect every open question first, then ask them in one batch: one `AskUserQuestion` call, or
  several in the same turn past its 4-question limit.
- Questions whose options are not enumerable → list them all in one report and stop.
- Handle each answer per craft-it step 2, on the issue it settles.
- Skip craft-it step 2a: every child runs the workflow.

## 3. Branch

- Run craft-it step 3 for the Meta issue: its worktree branch is the integration branch.
- Its recorded `HEAD` is the workflow's `base`.

## 4. Run the workflow

Invoke the **Workflow** tool with `name: "dream-team:assemble-meta-loop"` and `args` as a real JSON
object:

```json
{
  "meta": { "issue": "40", "title": "<Meta title>", "body": "<Meta description, verbatim>" },
  "children": [
    { "issue": "41", "title": "<title>", "body": "<description, verbatim>",
      "notes": "<answers for it>", "blockedBy": [] },
    { "issue": "42", "title": "<title>", "body": "<description, verbatim>", "blockedBy": ["41"] }
  ],
  "notes": "<what applies to every child>",
  "branch": "issue-40-slug",
  "base": "<sha from step 3>",
  "worktree": "<absolute path of the step-3 worktree>",
  "gateCommands": ["cargo test --workspace"],
  "externalReview": "<command, or leave out>"
}
```

- `children`: every child step 1 kept; `blockedBy` lists only other children's numbers.
- A child's `notes`: its tracker decisions and the step-2 answers that settle it. Optional.
- Craft-it step 4's decision-record line → put it in the `notes` of the one child the
  decision settles, the first child for a Meta-level decision; never in the top-level `notes`.
- `notes`, `gateCommands` and `externalReview`: per craft-it step 4.
- Then report per craft-it step 4.

## 5. Judge the result

- **`children`** — each finished child's gated run: `assumptions`, `redEvidence`, `degraded`,
  `untrackedPaths`.
- **`failed`** — each child whose run did not pass the gate, whose worktree could not be cut
  (`stage: 'worktree'`), or that failed to land twice (`stage: 'land'`), with its `stage` and
  `reason`; its commits never reach the integration branch.
- **`skipped`** — children not run because a failed child blocks them.
- A child's branch and worktree are dropped once it lands or fails, unless it has `untrackedPaths`:
  then its `worktree` is kept with those files in it; list that path with them.
- **`review`** — the one craft-it-loop result for the whole branch, from Review on, with the
  Meta issue as its issue.
- `review` is `null` → no child passed the gate: hand the branch back.

Otherwise run craft-it step 5 on `review`, its lab work once on the branch head.

## 6. Open the MR/PR

- Run craft-it steps 6 and 7; the fold leaves one commit per change.
- Link `Closes #<child>` for each finished child, in place of craft-it's `Closes #<n>`.
- Link `Closes #<meta>` only when `failed` and `skipped` are empty and step 1 left no child out.

## Report back

Per craft-it's Report back, plus these lines, which count as named there:

- Each finished child's `assumptions` that craft-it's Report back would show, under
  `**Assumptions:**`, prefixed with `#<child>`.
- Each `failed` child → one `**Failed:**` bullet: the child, its `stage` and `reason`.
- Each `skipped` or step-1 left-out child → one `**Skipped:**` bullet: the child and its open
  blocker or `Research:` title.
