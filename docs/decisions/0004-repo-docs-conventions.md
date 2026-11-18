# A repo's doc conventions live in the repo; skills follow them over their own defaults

Superseded by 0008-setup-writes-conventions-doc.md

Skills fixed the paths for decision records, specs and ROADMAP (`docs/decisions/`,
`docs/specs/`); they now take those paths, file naming and record template from what the
project's `CLAUDE.md` or `AGENTS.md` declares, else from an existing records folder (`docs/adr/`,
`doc/adr/`), else their defaults. In an own clone with nothing declared, the first writer creates
`docs/CONVENTIONS.md` and a `CLAUDE.md` pointer line, so dream-team works in repos with older or
upstream layouts and agents without dream-team find the layout. Copying templates into the repo,
as setup-matt-pocock-skills does, was rejected: the copy freezes at setup time and drifts from the
plugin. The decision test and the record landing in the change's commit stay fixed.
