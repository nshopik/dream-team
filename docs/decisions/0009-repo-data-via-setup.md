# Repo data lives in the repo; each behaviour rule has one owning skill

Skills read doc paths, naming and the record template from `docs/CONVENTIONS.md`, and a clone not
marked own reads its local tracker rules from `.dream-team/TRACKER.md`; `setup-dream-team` writes
both, and a skill that needs either stops with "run `setup-dream-team` first" when it is missing.
Each behaviour rule has one owning skill, and no skill reaches another skill's files by a
`<base directory>/../` path, which broke silently when a file moved (#633); it loads that skill
with the Skill tool first. This supersedes 0008, whose first-writer fallback kept plugin defaults
as a second home for repo data.

## Considered Options

- Shared references as non-invocable skills loaded by name (pull request 635): each costs a
  description in every session, and the "load as a reference" wording loaded `craft-it` in 1 of
  8 eval runs.
