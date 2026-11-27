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

- An edit that lands in the docs MR needs no approval: the user reviews it there, once step 5
  opens the MR.
- Ask only for what leaves the docs MR or changes agent rules: issues, closes, moves, milestones,
  `AGENTS.md` or `CLAUDE.md` and corresponding local notes, and the release offer.

- Without named Dream Team agents → dispatch per the host lines at the top of qa-review's
  advertised `SKILL.md`.
- Without named Dream Team agents → use the `role-fallback.md` file in qa-review's base
  directory, beside its advertised `SKILL.md`.

## 1. Read the milestone

- The milestone is not numbered `M<n>`, `YY.MM` or `v<major>.<minor>` with a major of 1 or
  above → stop and tell the user the repo may not be set up for dream-team, naming
  `setup-dream-team`; check, propose or preview no later step.

Milestone description, and its roadmap row if it has one. No measurable exit
criterion → stop and ask for one; a milestone without one cannot close.

- `git config --local --type=bool --get dream-team.own` prints `true` → the ROADMAP and specs
  folder are at the paths `docs/CONVENTIONS.md` names.
- `dream-team.own` prints `true` and `docs/CONVENTIONS.md` does not exist → stop with "run
  `setup-dream-team` first".
- `dream-team.own` prints anything but `true` → take those paths from the upstream's
  `CLAUDE.md`, `AGENTS.md` or existing records folder.
- `dream-team.own` prints anything but `true` and none of those names a ROADMAP path → write no
  ROADMAP.

A version milestone's `Gate:` bullet holds its release criteria; check each item there too.

## 2. Check the criterion

- Run or read the measurement the criterion names: gate floors, a recorded run, a deployed host.
- A field-evidence gate → read its `Evidence:` issue for the deploy, the start date and how to
  collect.
- The project `AGENTS.md` or `CLAUDE.md` says `Version milestones release in flow mode.` → a version milestone's
  criterion is met at its due date, and an open headline is no gap.
- Outside flow mode, an open headline issue in a version milestone → it is its own gap; file
  nothing for it.
- That headline still open past the ship-by date, or a `YY.MM` milestone's due date → the user
  picks between moving the headline to the next version and a new date.
- A new date for a `YY.MM` milestone → rename it to the new month and move its due date to that
  month's last day.

Criterion not met:

- A failed kill-gate (the criterion names a redesign) → report it and stop, with no gap issues;
  the redesign goes back to the spec.
- Any other gap → report it and propose the gap issues per `scope-issue`, in this milestone.
- The user approves or rejects each; file the approved ones and stop.
- The milestone stays open.

## 3. Triage open issues

- One table: issue, title, proposed action: close, move or blocks-close.
- Close → the issue is done or obsolete; cite the commit or reason.
- Move → the target comes from the tracker's open milestones and the roadmap's `planned` rows.
- A `planned` row target → no milestone and `workflow::future`.
- In a version milestone, an open backlog issue defaults to move, to the next version; in flow
  mode, so does an open headline.
- The user answers in one reply.
- `Meta:` issues stay out of the table.
- List each meta issue with a child in this milestone; tick the boxes of closed children in its
  description.
- A `Meta:` issue set to this milestone with an open child → it moves with that child.

## 4. Docs check

Collect the docs-MR edits and the proposals; fix nothing yet.

Docs-MR edits, applied in step 5 without asking:

- Architecture doc and diagram against the workspace's component list.
- Specs in the specs folder whose decision the code no longer follows, recorded on a closed issue
  or merged MR → a `Superseded by` status line. No such record → propose it.
- README, `docs/` pages, help text and comments: dispatch `dream-team:docs-reviewer`, told to
  read the milestone's merged diff with `git diff <base>..<head>`, `<base>` the first-merged MR's
  merge base and `<head>` the last-merged MR's merge commit.
- Each 🔴/🟡 `docs-reviewer` finding, as a fix; leave its 🔵 findings out. A finding you judge
  wrong → drop it and name it in the report.
- Roadmap, when the milestone has a row: status of the milestone's merged work, and the row against
  the criterion result. Feature MRs leave roadmap status to this step.
- Root-cause and behaviour sections of the milestone's merged MRs → each fact a future change must
  respect that the contributor doc lacks, as one line.

Proposals, each approved or rejected by the user:

- Each `planned` roadmap row with no tracker milestone of its title, whose every `Depends on:`
  entry is a closed milestone or this one → propose it as a tracker milestone, numbered with the
  next free `M<n>`, with a `<due date>` and the parked issues that belong to it, in ROADMAP order
  until 3 `M<n>` milestones would be open, this one not counted; it is approved only once the user
  sets its `<due date>`.
- Each project `AGENTS.md`, `CLAUDE.md`, `AGENTS.local.md`, or `CLAUDE.local.md` line, proposed as a cut when the path or tool it
  names is gone, its only content is one closed issue's artifacts rather than a gotcha, a hook or
  CI enforces it now, a global rule already says it, or a change outside the repo could fix the
  gotcha it works around (a lab host's config, a missing tool, a plugin bug), recommending that
  change.
- Each other `AGENTS.local.md` or `CLAUDE.local.md` line: proposed as a promotion to its matching `AGENTS.md` or `CLAUDE.md` when it holds no
  hostname, IP, internal URL or lab access, otherwise left alone.

## 5. Apply

Before any other step 5 action:

- At least one numbered proposal changes `AGENTS.md` or `CLAUDE.md` (a cut from it or a promotion) → send the
  held report per Report back, and wait for the user's one reply.
- No such proposal → do not wait for answers; carry on with the rest of step 5 and open the docs
  MR once its edits are committed.
- A proposal the user rejects changes nothing; the docs-MR edits still land in the MR.

Then, in order:

1. Make the approved closes and moves through the host's tooling skill.
   - An obsolete close is not planned and adds `wontfix`.
   - The `Evidence:` issue closes with the milestone.
2. Put step 4's docs-MR edits, the approved `Superseded by` lines and the approved `AGENTS.md` or `CLAUDE.md`
   cuts and promotions in one MR.
   - `docs-reviewer` fixes → dispatch `dream-team:docs-editor` in drift mode with
     `git diff <base>..<head>` from step 4 and only the pages they name; its edits go in the
     docs MR.
3. Apply the approved promotions and cuts to the corresponding ignored `AGENTS.local.md` or `CLAUDE.local.md` directly.
4. Close the milestone and set its roadmap status, if it has a row.
5. Each approved `planned` row → create its milestone per `cut-milestones` step 5, move its
   parked issues into it without `workflow::future`, then set the row's `#` and its status
   `not started` in the docs MR.
6. Each milestone whose `Depends on:` is now all closed is ready → drop `workflow::future` from
   its open issues.

## Report back

Criterion result, issues closed, moved and filed, milestones created, the docs MR link, each
docs fix `docs-editor` reported as `skipped:` or under `gaps:`, and one `**Release:**` bullet:
an offer naming the current and next version by `ship-it` step 1, asking for a yes or another
version.

- A yes or a version in reply → run `ship-it` with that version as its argument, from this
  milestone's offer.
- No reply → no release; nothing waits.

A numbered proposal that changes `AGENTS.md` or `CLAUDE.md` is unanswered → send only the held report: criterion
result, step 4's docs-MR edits and the proposals below, with no docs MR link. After step 5 applies
the user's reply, send the full report above, with the link.

Step 4's docs-MR edits: one bullet in the report, each edit named in the docs MR description, or
in the bullet in a held report; never numbered as proposals.

Proposals from step 2 or 4:

- Number them; ask the user to approve them by number.
- A cut that waits on a fix outside the repo → one unnumbered **Outside the repo:** line naming
  the fix; propose the cut once the user reports the fix made.
- Under each, name what approving it does: an issue filed, a milestone created, a line added,
  removed or moved to `AGENTS.md` or `CLAUDE.md`, or a `Superseded by` line in the docs MR.
