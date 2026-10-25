---
name: milestone-close
description: >-
  Closes a tracker milestone: checks its exit criterion, triages its open issues, checks docs
  against code and offers a minor release. Use when the user asks to close, wrap up or review a
  milestone — "close milestone 4", "is M4 done", "wrap up the dogfood milestone".
argument-hint: <milestone id or title>
---

# milestone-close

Read-only until step 5, except step 2's approved gap issues. The user decides every close, move
and filed issue.

The project instructions are defined in `<base directory>/../../references/project-instructions.md`.

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

Report drift and propose the release, fix nothing yet:

- Architecture doc and diagram against the workspace's component list.
- Specs whose decision the code no longer follows → propose a `Superseded by` status line.
- README, `docs/` pages, help text and comments: dispatch `dream-team:docs-reviewer`, told to
  read the milestone's merged diff with `git diff <base>..<head>`, `<base>` the first-merged MR's
  merge base and `<head>` the last-merged MR's merge commit.
- Each 🔴/🟡 `docs-reviewer` finding, proposed as a fix; leave its 🔵 findings out. The user
  approves or rejects each.
- Roadmap, when the project has one: status of the milestone's merged work, and the row against
  the criterion result. Feature MRs leave roadmap status to this step.
- Root-cause and behaviour sections of the milestone's merged MRs → each fact a future change must
  respect that the contributor doc lacks, proposed as one line. The user approves or rejects each.
- Each line of the project instructions and of `CLAUDE.local.md`, proposed as a cut when the path
  or tool it names is gone, its only content is one closed issue's artifacts rather than a gotcha,
  a hook or CI enforces it now, a global rule already says it, or a change outside the repo could
  fix the gotcha it works around (a lab host's config, a missing tool, a plugin bug), recommending
  that change. The user approves or rejects each.
- Each other `CLAUDE.local.md` line: proposed as a promotion to the project instructions, in the
  file that reference names for writes, when it holds no hostname, IP, internal URL or lab access,
  otherwise left alone. The user approves or rejects each.
- Every close, `M<n>` and `v<x.y>` alike → load `ship-it`; propose a release per its Propose step.
- A `v<x.y>` milestone whose major is above the version file's → warn in the release proposal
  that its name says a major release, naming both versions.

## 5. Apply

The approved closes and moves, through the host's tooling skill; the `Evidence:` issue closes with
the milestone. Docs fixes and the approved facts, project instructions cuts and promotions as one
MR; approved promotions and cuts leave `CLAUDE.local.md` directly, since it is untracked. Then
close the milestone and set its roadmap status, if it has a row. Every milestone whose
`Depends on:` is now all closed is ready: drop the host's waiting label (`workflow::future` on
GitLab) from its open issues.

- Approved `docs-reviewer` fixes → dispatch `dream-team:docs-editor` in drift mode with
  `git diff <base>..<head>` from step 4 and only the pages they name; its edits go in the docs MR.
- Approved release → `ship-it` Bump and Tag steps, its bump in the docs MR and its tag message
  naming the milestone; with nothing else approved, the release alone opens the MR.

## Report back

Criterion result, issues closed, moved and filed, the docs MR link, each approved docs fix
`docs-editor` reported as `skipped:` or under `gaps:`, the release version and its tag, or the
tag pending the docs MR's merge, or the declined release.

Proposals from step 2 or 4:

- Number them; ask the user to approve them by number.
- Under each, name what approving it does: an issue filed, a line added, removed or moved to
  the project instructions, a page edit in the docs MR, a version bump and CHANGELOG move in the
  docs MR, or a fix the user makes outside the repo.
