---
name: milestone-close
description: >-
  Closes a tracker milestone: checks its exit criterion, triages its open issues, checks docs
  against code. Use when the user asks to close, wrap up or review a milestone — "close milestone
  4", "is M4 done", "wrap up the dogfood milestone".
argument-hint: <milestone id or title>
---

# milestone-close

Read-only until step 5, except step 2's approved gap issues. The user decides every close, move
and filed issue.

## 1. Read the milestone

Milestone description, and its roadmap row when the project has one. No measurable exit
criterion → stop and ask for one; a milestone without one cannot close.

A version milestone's `Gate:` bullet holds its release criteria; check each item there too.

## 2. Check the criterion

Run or read the measurement it names: gate floors, a recorded run, a deployed host. A field-evidence
gate reads its `Evidence:` issue for the deploy, the start date and how to collect.

Not met → report the gap, and propose one issue per gap per `scope-issue`, in this milestone. The
user approves or rejects each; file the approved ones and stop. The milestone stays open.

A failed kill-gate (the criterion names a redesign) gets no gap issues: report it and stop. The
redesign goes back to the spec.

An open headline issue in a version milestone is its own gap; file nothing for it. Past the
ship-by date, the user picks between moving the headline to the next version and a new date.

## 3. Triage open issues

One table: issue, title, proposed action — close (done or obsolete; cite the commit or reason),
move (target milestone from the roadmap), or blocks-close. The user answers in one reply.
In a version milestone, an open backlog issue defaults to move, to the next version.

`Meta:` issues carry no milestone and stay out of the table. List each meta issue with a child in
this milestone; tick the boxes of closed children in its description.

## 4. Docs check

Report drift, fix nothing yet:

- Architecture doc and diagram against the workspace's component list.
- Specs whose decision the code no longer follows → propose a `Superseded by` status line.
- README, `docs/` pages, help text and comments: dispatch `dream-team:docs-reviewer` on the
  milestone's merged diff, from its first-merged MR's merge base to its last-merged MR's merge
  commit.
- Each 🔴/🟡 `docs-reviewer` finding, proposed as a fix; leave its 🔵 findings out. The user
  approves or rejects each.
- Roadmap, when the project has one: status of the milestone's merged work, and the row against
  the criterion result. Feature MRs leave roadmap status to this step.
- Root-cause and behaviour sections of the milestone's merged MRs → each fact a future change must
  respect that the contributor doc lacks, proposed as one line. The user approves or rejects each.
- Each project `CLAUDE.md` and `CLAUDE.local.md` line, proposed as a cut when the path or tool it
  names is gone, a hook or CI enforces it now, a global rule already says it, or a change outside
  the repo could fix the gotcha it works around (a lab host's config, a missing tool, a plugin
  bug), recommending that change. The user approves or rejects each.
- Each other `CLAUDE.local.md` line: proposed as a promotion to `CLAUDE.md` when it holds no
  hostname, IP, internal URL or lab access, otherwise left alone. The user approves or rejects each.

## 5. Apply

The approved closes and moves, through the host's tooling skill; the `Evidence:` issue closes with
the milestone. Docs fixes and the approved facts, `CLAUDE.md` cuts and promotions as one MR;
approved promotions and cuts leave `CLAUDE.local.md` directly, since it is untracked. Then close the
milestone and set its roadmap status, if it has a row. Every milestone whose `Depends on:` is
now all closed is ready: drop the host's waiting label (`workflow::future` on GitLab) from its
open issues.

- Approved `docs-reviewer` fixes → dispatch `dream-team:docs-editor` in drift mode with the merged
  diff and only the pages they name; its edits go in the docs MR.
- The project's `CLAUDE.md` opts in to tagging milestone closes → the docs MR bumps the project
  version to the next pre-1.0 minor (`0.<n>.0`).
- Once that MR merges, tag its merge commit `v0.<n>.0`, the tag message naming the milestone.
- No opt-in line and no `v1.0.0` tag yet → recommend the opt-in in the report, as the one
  `CLAUDE.md` line to add.

## Report back

Criterion result, issues closed, moved and filed, the docs MR link, each approved docs fix
`docs-editor` reported as `skipped:` or under `gaps:`, the tag or the recommended opt-in line.

Proposals from step 2 or 4:

- Number them; ask the user to approve them by number.
- Under each, name what approving it does: an issue filed, a line added, removed or moved to
  `CLAUDE.md`, a page edit in the docs MR, or a fix the user makes outside the repo.
