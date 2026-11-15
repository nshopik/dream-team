---
name: assemble-meta
description: >-
  Takes a tracker Meta issue to one MR/PR: triages the Meta issue and every child before any
  code, asking all open questions in one batch, builds each child up to the gate on one
  integration branch through the assemble-meta-loop workflow, reviews and fixes the whole branch
  once, and opens one MR/PR with one commit per change. Use when the user runs
  /dream-team:assemble-meta or asks to build, work or ship a Meta issue's children together, on one
  branch or as one MR/PR — e.g. "assemble-meta #40", "do Meta #40 in one MR". Not for a single
  issue or a Meta issue whose children are independent (run build-issue per child).
argument-hint: <meta-issue-number>
---

# assemble-meta

One Meta issue per invocation. Read `<base directory>/../build-issue/SKILL.md` first: each
"build-issue step N" below runs as written there, with the Meta issue's number as `<n>`.

You are the orchestrator, as in build-issue: **you do not write the change**. Your only edits
are build-issue's step-5 edits and a step-3 decision record with the files `repo-conventions.md`
adds with it. Lab work is yours, per build-issue.

## 1. Read the Meta issue and its children

- Fetch the Meta issue with build-issue step 1's fetch command; skip its Meta child pick.
- Take every unticked link to an open child issue in its checklist; skip plain-text lines.
- Fetch each child the same way, and note its `Blocked by` issues.
- A child blocked by an open issue that is not a child → leave it and its dependents out, and
  report them.
- A child whose title starts `Research:` → leave it and its dependents out, and report them.
- No child left → report it and stop.

## 2. Triage everything before code

- Triage the Meta issue and every child per build-issue step 2, before step 3.
- Collect every open question first, then ask them in one batch: one `AskUserQuestion` call, or
  several in the same turn past its 4-question limit.
- Questions whose options are not enumerable → list them all in one report and stop.
- Handle each answer per build-issue step 2, on the issue it settles.
- Skip build-issue step 2a: every child runs the workflow.

## 3. Branch

- Run build-issue step 3 for the Meta issue: its worktree branch is the integration branch.
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
  "gateCommands": ["cargo test --workspace"],
  "externalReview": "<command, or leave out>"
}
```

- `children`: every child step 1 kept; `blockedBy` lists only other children's numbers.
- A child's `notes`: its tracker decisions and the step-2 answers that settle it. Optional.
- `notes`, `gateCommands` and `externalReview`: per build-issue step 4.
- Then report per build-issue step 4.

## 5. Judge the result

- **`children`** — each finished child's gated run: `assumptions`, `redEvidence`, `degraded`,
  `untrackedPaths`.
- **`failed`** — each child whose run did not pass the gate, with its `stage` and `reason`; its
  commits and untracked files are reset off the branch.
- **`skipped`** — children not run because a failed child blocks them.
- **`review`** — the one build-issue-loop result for the whole branch, from Simplify on, with the
  Meta issue as its issue.
- `review` is `null` → no child passed the gate, or `stage: 'reset'` left the branch at the
  wrong head or with files left over: hand the branch back.

Otherwise run build-issue step 5 on `review`, its lab work once on the branch head.

## 6. Open the MR/PR

- Run build-issue steps 6 and 7; the fold leaves one commit per change.
- Link `Closes #<child>` for each finished child, in place of build-issue's `Closes #<n>`.
- Link `Closes #<meta>` only when `failed` and `skipped` are empty and step 1 left no child out.

## Report back

Per build-issue's Report back, plus:

- Each finished child's `assumptions` under `**Assumptions:**`, prefixed with `#<child>`.
- Each `failed` child → one `**Failed:**` bullet: the child, its `stage` and `reason`.
- Each `skipped` or step-1 left-out child → one `**Skipped:**` bullet: the child and its open
  blocker or `Research:` title.
