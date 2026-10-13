# CHANGELOG style

Keep the CHANGELOG to [Keep a Changelog 2.0.0](https://keepachangelog.com/en/2.0.0/).

- `## [Unreleased]` accumulates entries as work lands, grouped `### Added` / `Changed` /
  `Deprecated` / `Removed` / `Fixed` / `Security`.
- Release: rename `[Unreleased]` to `[<version>] - <date>` and add a fresh empty one above. CI
  sources the GitLab/GitHub Release description from the section matching the tag, not from
  commits or the tag message.
- Each entry is one plain, complete sentence: enough to understand what was added, changed,
  fixed or removed, no more. No rationale, benchmarks or metric names; those belong in the commit
  body.
- No bold, no `**lead** — clause` shape. `**Breaking:**` and `**Upgrade note:**` are the only
  bold, as entry prefixes.
- Curate: notable changes only. Skip internal refactors, test-only changes and anything with no
  observable effect.
- A breaking change: prefix the entry `**Breaking:**` and name the interface that breaks (CLI,
  API, protocol, config, schema).
- A required operator action on upgrade: prefix the entry `**Upgrade note:**`.
