---
name: milestone-close
description: >-
  Closes a tracker milestone: checks its exit criterion, triages its open issues, checks docs
  against code and offers a release. Use when the user asks to close, wrap up or review a
  milestone — "close milestone 4", "is M4 done", "wrap up the dogfood milestone".
argument-hint: <milestone id or title>
---

# milestone-close

Read-only until step 5, except step 2's approved gap issues. The user decides every close, move
and filed issue.

- An edit that lands in the docs MR needs no approval: the user reviews it there.
- Ask only for what leaves the docs MR or changes agent rules: issues, closes, moves, milestones,
  `CLAUDE.md` and `CLAUDE.local.md` lines, and a release the project rules do not settle.

## 1. Read the milestone

Milestone description, and its roadmap row if it has one. No measurable exit
criterion → stop and ask for one; a milestone without one cannot close.

A version milestone's `Gate:` bullet holds its release criteria; check each item there too.

## 2. Check the criterion

Run or read the measurement it names: gate floors, a recorded run, a deployed host. A field-evidence
gate reads its `Evidence:` issue for the deploy, the start date and how to collect.

Not met → report the gap, and propose one issue per gap per `scope-issue`, in this milestone. The
user approves or rejects each; file the approved ones and stop. The milestone stays open.

A failed kill-gate (the criterion names a redesign) gets no gap issues: report it and stop. The
redesign goes back to the spec.

Outside flow mode, an open headline issue in a version milestone is its own gap; file nothing for
it. Past the ship-by date, or a `YY.MM` milestone's due date, the user picks between moving the
headline to the next version and a new date. A new date for a `YY.MM` milestone renames it to the
new month and moves its due date to that month's last day.

The project `CLAUDE.md` says `Version milestones release in flow mode.` → a version milestone's
criterion is met at its due date, and an open headline is no gap.

## 3. Triage open issues

One table: issue, title, proposed action — close (done or obsolete; cite the commit or reason),
move (target from the tracker's open milestones and the roadmap's `planned` rows; a `planned`
row target → no milestone and the waiting label), or blocks-close. The user answers in one reply.
In a version milestone, an open backlog issue defaults to move, to the next version; in flow
mode, so does an open headline.

`Meta:` issues carry no milestone and stay out of the table. List each meta issue with a child in
this milestone; tick the boxes of closed children in its description.

## 4. Docs check

Collect the docs-MR edits and the proposals; fix nothing yet.

Docs-MR edits, applied in step 5 without asking:

- Architecture doc and diagram against the workspace's component list.
- Specs whose decision the code no longer follows, recorded on a closed issue or merged MR → a
  `Superseded by` status line. No such record → propose it.
- README, `docs/` pages, help text and comments: dispatch `dream-team:docs-reviewer`, told to
  read the milestone's merged diff with `git diff <base>..<head>`, `<base>` the first-merged MR's
  merge base and `<head>` the last-merged MR's merge commit.
- Each 🔴/🟡 `docs-reviewer` finding, as a fix; leave its 🔵 findings out. A finding you judge
  wrong → drop it and name it in the report.
- Roadmap, when the milestone has a row: status of the milestone's merged work, and the row against
  the criterion result. Feature MRs leave roadmap status to this step.
- Root-cause and behaviour sections of the milestone's merged MRs → each fact a future change must
  respect that the contributor doc lacks, as one line.
- The release, when the project's `CLAUDE.md` or `AGENTS.md` sets the version each close takes:
  `ship-it`'s Bump step. The tag is still offered after the merge.

Proposals, each approved or rejected by the user:

- Each `planned` roadmap row with no tracker milestone of its title, whose every `Depends on:`
  entry is a closed milestone or this one → propose it as a tracker milestone, numbered with the
  next free `M<n>`, with the parked issues that belong to it.
- Each project `CLAUDE.md` and `CLAUDE.local.md` line, proposed as a cut when the path or tool it
  names is gone, its only content is one closed issue's artifacts rather than a gotcha, a hook or
  CI enforces it now, a global rule already says it, or a change outside the repo could fix the
  gotcha it works around (a lab host's config, a missing tool, a plugin bug), recommending that
  change.
- Each other `CLAUDE.local.md` line: proposed as a promotion to `CLAUDE.md` when it holds no
  hostname, IP, internal URL or lab access, otherwise left alone.
- Every close, `M<n>` and version milestone alike, whose version no project rule sets → load
  `ship-it`; propose a release per its Propose step.
- A milestone with `MVP` in its title, in a repo whose last release is `0.x` or none → propose
  this month's `<YY.MM>.0`, the first CalVer release, in place of the next `0.x` minor.
- In a SemVer repo, a `v<x.y>` milestone whose major is above the version file's → warn in the
  release proposal that its name says a major release, naming both versions.

## 5. Apply

The approved closes and moves, through the host's tooling skill; the `Evidence:` issue closes with
the milestone. Step 4's docs-MR edits, the approved `CLAUDE.md` cuts and promotions as one MR;
approved promotions and cuts leave `CLAUDE.local.md` directly, since it is untracked. Then close the
milestone and set its roadmap status, if it has a row. Create each approved `planned` row's
milestone per `cut-milestones` step 5, move its parked issues into it without the waiting label,
then set the row's `#` and its status `not started` in the docs MR. Every milestone whose
`Depends on:` is now all closed is ready: drop the host's waiting label (`workflow::future` on
GitLab) from its open issues.

- `docs-reviewer` fixes → dispatch `dream-team:docs-editor` in drift mode with
  `git diff <base>..<head>` from step 4 and only the pages they name; its edits go in the docs MR.
- Release set by a project rule, or approved → `ship-it` Bump and Tag steps, its bump in the docs
  MR and its tag message naming the milestone; with nothing else in it, the release alone opens
  the MR.

## Report back

Criterion result, issues closed, moved and filed, milestones created, the docs MR link, each
docs fix `docs-editor` reported as `skipped:` or under `gaps:`, the release version and
its tag, or the tag pending the docs MR's merge, or the declined release.

Step 4's docs-MR edits: one bullet in the report, each edit named in the docs MR description;
never numbered as proposals.

Proposals from step 2 or 4:

- Number them; ask the user to approve them by number.
- A cut that waits on a fix outside the repo → one unnumbered **Outside the repo:** line naming
  the fix; propose the cut once the user reports the fix made.
- Under each, name what approving it does: an issue filed, a milestone created, a line added,
  removed or moved to `CLAUDE.md`, or a version bump and CHANGELOG move in the docs MR.
