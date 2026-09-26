# Changelog

All notable changes to this plugin are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/2.0.0/).

## [Unreleased]

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
