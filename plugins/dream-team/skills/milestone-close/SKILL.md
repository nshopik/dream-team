---
name: milestone-close
description: >-
  Close out one tracker milestone: check its exit criterion, triage its open issues, check docs
  against code. Use when the user asks to close, wrap up or review a milestone — "close milestone
  4", "is M4 done", "wrap up the dogfood milestone".
argument-hint: <milestone id or title>
---

# milestone-close

Read-only until step 5, except step 2's approved gap issues. The user decides every close, move
and filed issue.

## 1. Read the milestone

Milestone description and the project roadmap row. No measurable exit criterion → stop and ask
for one; a milestone without one cannot close.

## 2. Check the criterion

Run or read the measurement it names: gate floors, a recorded run, a deployed host. A field-evidence
gate reads its `Evidence:` issue for the deploy, the start date and how to collect.

Not met → report the gap, and propose one issue per gap per `scope-issue`, in this milestone. The
user keeps or drops each; file the kept ones and stop. The milestone stays open.

A failed kill-gate (the criterion names a redesign) gets no gap issues: report it and stop. The
redesign goes back to the spec.

## 3. Triage open issues

One table: issue, title, proposed action — close (done or obsolete; cite the commit or reason),
move (target milestone from the roadmap), or blocks-close. The user answers in one reply.

`Meta:` issues carry no milestone and stay out of the table. List each meta issue with a child in
this milestone; tick the boxes of closed children in its description.

## 4. Docs check

Report drift, fix nothing yet:

- Architecture doc and diagram against the workspace's component list.
- Specs whose decision the code no longer follows → propose a `Superseded by` status line.
- Roadmap: status of the milestone's merged work, and the row against the criterion result. Feature
  MRs leave roadmap status to this step.
- Root-cause and behaviour sections of the milestone's merged MRs → each fact a future change must
  respect that the contributor doc lacks, proposed as one line. The user keeps or drops each.
- Project `CLAUDE.md` lines that no longer fire — the path or tool is gone, a hook or CI enforces
  it now, or a global rule already says it — each proposed as a cut. The user keeps or drops each.
- Each `CLAUDE.local.md` line: proposed as a cut when it no longer fires, as a promotion to
  `CLAUDE.md` when it holds no hostname, IP, internal URL or lab access, otherwise left alone. The
  user decides each.

## 5. Apply

The approved closes and moves, through the host's tooling skill; the `Evidence:` issue closes with
the milestone. Docs fixes, kept facts, approved `CLAUDE.md` cuts and promotions as one MR; approved
promotions and cuts leave `CLAUDE.local.md` directly, since it is untracked. Then close the
milestone and set the roadmap status.

## Report back

Criterion result, issues closed, moved and filed, the docs MR link.
