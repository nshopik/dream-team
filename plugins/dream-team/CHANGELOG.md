# Changelog

All notable changes to this plugin are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/2.0.0/).

## [Unreleased]

### Changed

- `align-project` keeps the component table to one row per component with its path, and a note
  only where the name and path don't say enough.

## [0.13.0] - 2026-10-01

### Changed

- `align-project` no longer checks for an area document per `area::` label; its project rule
  asks for one reference doc per fact the code and paths don't show.
- `dream-fixer` targets the remote's default branch unless the project `CLAUDE.md` names another,
  and `align-project` no longer requires the project `CLAUDE.md` to name the MR target branch.

## [0.12.2] - 2026-09-30

### Changed

- `dream-fixer` light tier takes doc, comment and help-text rot issues, including comment-only
  edits in gated paths, and skips lab work unless the issue asks for a measurement.

## [0.12.1] - 2026-09-29

### Changed

- `lab-runner` runs at medium effort instead of low.
- `dream-fixer` light path makes the edit inline instead of dispatching a `cavecrew-builder` agent.

## [0.12.0] - 2026-09-29

### Added

- `align-project` checks for one area document per `area::` label and adds the rule that an MR
  updates its area document.
- Milestone descriptions carry bold `Exit:`, `Gate:` and `Depends on:` bullets, and issues in a
  milestone with an open dependency carry the host's waiting label until `milestone-close`
  clears it.
- `jit-context` injects a decision-record rule on the first write under `docs/decisions/`: files
  are named `NNNN-<topic>.md` with a four-digit sequence from `0000`.

### Changed

- The spec template is a project overview with Context, Decision, Consequences, Design and Open
  items sections; it drops Expertise required, Rejected alternatives, Affected files, Testing and
  Out of scope.

### Fixed

- `jit-context` points spec writes at `docs/specs/` instead of `docs/superpowers/specs/`.

## [0.11.0] - 2026-09-28

### Changed

- **Breaking:** milestones are named `M<n>` or `v<major>.<minor>`; `align-project` flags a bare
  integer or `major.minor` milestone.

## [0.10.1] - 2026-09-28

### Changed

- `dream-fixer-loop` runs the nested `/verify` session on Opus at medium effort instead of the
  user's default model and effort.
- `dream-fixer` reports the `/verify` cold-start recipe by its path, not its contents.

## [0.10.0] - 2026-09-28

### Added

- `dream-fixer-loop` runs Claude Code's `/verify` as an opt-in Review gate when the repo's
  `CLAUDE.md` asks for it, and `dream-fixer` puts its evidence in the MR.

## [0.9.1] - 2026-09-28

### Fixed

- `dream-fixer` reports as assumptions only what the implementer had to guess, not a choice that a
  written rule or instruction settles.

## [0.9.0] - 2026-09-28

### Added

- `dream-fixer-loop` runs a Simplify phase before review that applies `ponytail:ponytail-review`
  cuts to a diff with code and reports them in its result.

### Removed

- `dream-fixer` drops its `fix-rounds` argument; the review fix loop always runs at most 3 rounds.

## [0.8.9] - 2026-09-28

### Fixed

- `dream-fixer-loop` fails the verify stage, naming the paths, when an implement or fix agent
  leaves uncommitted edits in the working tree.

## [0.8.8] - 2026-09-28

### Fixed

- `dream-fixer` names a dead reviewer once: a hand-back line whose reason names it gets no
  separate bullet.

## [0.8.7] - 2026-09-28

### Fixed

- `dream-fixer-loop` tells every workflow agent never to push, open or edit an MR/PR, or create,
  comment on or edit an issue; `dream-fixer` step 7 does that.

## [0.8.6] - 2026-09-28

### Fixed

- `dream-fixer` files every adjacent defect it finds as an issue, not only review findings, and
  links each filed issue in its report instead of describing the defect.

## [0.8.5] - 2026-09-28

### Fixed

- `dream-fixer` hand-back report no longer says a reviewer found nothing or that nothing was
  disputed, in a bullet or in the closing line's `<why>` clause.

## [0.8.4] - 2026-09-28

### Fixed

- `dream-fixer-loop` returns the blocking findings its fix rounds resolved as `resolved`, so the
  `dream-fixer` report no longer drops a fixed finding on a hand-back.

## [0.8.3] - 2026-09-27

### Changed

- `dream-fixer` report lists its items as tight bold-labelled bullets under a `**Notes:**` line
  instead of spaced paragraphs.

## [0.8.2] - 2026-09-27

### Fixed

- `dream-fixer` report follows a fixed layout: real assumptions only under `**Assumptions:**`, one
  bold-labelled paragraph per item, including a reviewer that could not check something and the
  check run in its place, and a closing `Work on #<n> is done: <link>` line.
- `dream-fixer-loop` returns `redEvidence` on a hand-back too, so the report no longer claims a
  bug fix's test was never seen failing.

## [0.8.1] - 2026-09-27

### Fixed

- `dream-fixer` lists assumptions under their own heading above the report again, not mixed into
  its bullets.

## [0.8.0] - 2026-09-27

### Added

- `cut-milestones` drafts a version milestone for a stable project's minor release: one headline
  issue plus backlog, gated on standing ROADMAP release criteria, no spec required.
- `milestone-close` checks a version milestone against the ROADMAP release criteria and moves its
  open backlog issues to the next version by default.

## [0.7.3] - 2026-09-27

### Changed

- `dream-fixer` skill text drops restated rationale and duplicate report and lab-work rules.

### Fixed

- `dream-fixer` hands the branch back instead of opening an MR when a reviewer returned nothing
  on every try.
- `dream-fixer` names degraded roster types and dead reviewers in its report.

## [0.7.2] - 2026-09-27

### Changed

- `dream-fixer` reports only what the user must know or act on, leaving out minor findings
  and a clean review.

### Fixed

- `dream-fixer` watches an MR until it is `merged` or `closed`, so GitLab's transient `locked`
  state no longer ends the watch early.

## [0.7.1] - 2026-09-27

### Changed

- `dream-fixer` leaves the merge poll out of its report and sums up a review with no blocking
  finding, dispute or fix round in one sentence.

### Removed

- `dream-fixer-loop` no longer accepts `verifyRounds`; each mechanical gate gets 3 build-fix
  rounds.

## [0.7.0] - 2026-09-27

### Added

- `lab-runner` agent runs lab work with blocking remote commands, on the host the repo's
  `CLAUDE.md` names.

### Changed

- `dream-fixer` sends lab work to `lab-runner`, and there is no lab work when the repo names no
  lab host.

## [0.6.1] - 2026-09-27

### Fixed

- `dream-fixer` starts `dream-fixer-loop` by its plugin name instead of a script path the
  Workflow tool rejected.

## [0.6.0] - 2026-09-27

### Added

- `jit-context.py` tells every session to record corrections in the project's `CLAUDE.local.md`,
  and injects the `CLAUDE.md` editing rules on the first write to one.

## [0.5.0] - 2026-09-27

### Added

- `jit-context.py` hook injects git, forge, changelog, spec, prose and lab conventions the first
  time a session touches each.
- `DREAM_TEAM_OWN_REMOTES` environment variable names the remotes `jit-context.py` treats as
  owned.

## [0.4.0] - 2026-09-27

### Added

- `cut-milestones` skill drafts milestones from a spec, one measurable exit gate each, with the
  dependency order and ROADMAP rows.

## [0.3.0] - 2026-09-26

### Added

- `milestone-close` skill checks a milestone's exit criterion, triages its open issues and checks
  docs against code.
- `branch-guard.py` hook blocks writing a design, spec or plan document on `main` or `master`.
- `changelog-cap.py` hook blocks a CHANGELOG entry longer than one sentence or 40 words.
- Lean-ADR spec template in `reference/spec-template.md`.

## [0.2.0] - 2026-09-26

### Added

- `align-project` skill checks a project against the dream-team flow and files one issue per
  failing check.

## [0.1.0] - 2026-09-26

### Added

- `dream-fixer` skill and `dream-fixer-loop` workflow: one tracker issue to one reviewed MR/PR.
