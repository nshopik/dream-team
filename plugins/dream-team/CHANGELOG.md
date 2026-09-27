# Changelog

All notable changes to this plugin are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/2.0.0/).

## [Unreleased]

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
