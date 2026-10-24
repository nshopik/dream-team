# Changelog

All notable changes to this plugin are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/2.0.0/).

## [Unreleased]

### Added

- A `review-bench` reviewer line takes optional `effort=` and `shown=` fields after its prefix, `shown=` naming the model an external reviewer runs on, and `run.sh` grades up to `P` runs at once on a frozen ledger.
- The `review-bench` score table names each row by reviewer and model columns instead of its prefix: the reviewer is the prompt's first word without a leading `/` and plugin prefix (such as `qa-review`), and the model is `shown=`, or else `model=` without a leading `claude-`, then `-<effort>`, both read from the prefix's first run's `stats.txt`, where `run.sh` writes a `reviewer=` field.

### Changed

- `review-bench` drops a pull request whose frozen ledger lacks a critical or an important row and picks another.
- `review-bench` skips its one-run check for a reviewer whose prompt and plugin already ran on the pull request, and runs its three runs in one `run.sh` call.
- **Breaking:** a `review-bench` reviewer line requires a `model=` field.
- **Upgrade note:** `review-bench` reviewer prefixes may hold lowercase letters, digits and `-`, such as `qa-opus-4-6`, and a run is named `<prefix>-r<k>`, such as `qa-opus-4-6-r1`; add `model=<model-id>` to every existing reviewer line, since `run.sh` exits 2 without it, and rename the run directories and marks lines of an existing output directory to this form before rescoring it; adding `reviewer=<command>` to each old run's `stats.txt` and replacing a `model=` alias there with its full model ID fills the new reviewer and model columns but is not required.

### Removed

- `review-bench`'s `run.sh` no longer reads a `MODEL` default from the environment.

### Fixed

- `qa-review` treats a SHA or ref in its arguments as the base of the diff to review, not as one commit to review on its own.

## [1.5.0] - 2026-10-21

### Added

- `qa-review` runs its lenses on pi through the `pi-sub-agent` extension; the README shows how to install it.

### Changed

- The reviewer agents keep off Edit, Write and NotebookEdit through `disallowedTools` instead of a `Read, Grep, Glob` allowlist, so they get Bash; `docs-editor` and `lab-runner` drop their `tools:` line and get every tool.

- The `docs-reviewer` agent flags, and the `docs-editor` agent avoids, a name set in code font more than once in one prose paragraph or list item; tables, code blocks and a list item's lead term are exempt.

- The `review-bench` score table shows each reviewer's mean rejected claims and mean cost per run, and its methodology adds a clean-PR case that counts a reviewer's findings graded critical or important on a change with no known defect, minus any the code confirms, as false alarms.

- A `qa-review` of a branch lists findings whose defect already exists at the base ref in a 🟣 Pre-existing section after the questions, each keeping its severity emoji; audit reports are unchanged.

- `qa-review` rates a performance finding 🔴, 🟡 or 🔵 by its cost instead of 🚀, and groups it under a 🚀 Performance theme like the other themes; the verify pass includes it when it is 🔴 or 🟡.

- The session-start project notes rule adds a `CLAUDE.local.md` line only for a mistake or correction a later session would repeat, never for a per-task artifact location; the `CLAUDE.md` editing rule caps each file at 8 KB instead of 500 lines and asks for one fact per line; `milestone-close` proposes cutting a line whose only content is one closed issue's artifacts.

- `scope-issue` opens an issue with an unlabeled problem paragraph that leads with the defect, bolded, then `## Proposal`, replacing the context paragraph and the `## Problem` heading; `setup-dream-team` accepts both shapes.

### Removed

- **Breaking:** The `dream-fixer-loop` workflow no longer takes a `diffFile` arg; its reviewers read the branch diff with `git diff`, as do the reviewers `qa-review`, `dream-fixer` and `milestone-close` dispatch.

- `scope-issue` drops the time box from a `Research:` issue's proposal.

## [1.4.0] - 2026-10-15

### Added

- The `ship-it` skill releases main, with or without a milestone: it proposes the next minor version from the commits and CHANGELOG `[Unreleased]` entries since the last release, bumps each version file and moves those entries under the new version in one MR, and offers a tag on its merge commit unless the project's `CLAUDE.md` forbids tagging; `milestone-close` releases through it.

- The `review-bench` skill benchmarks `qa-review`, and any reviewer you name against it, on one pull request: its `run.sh` runs each reviewer headless, grades every run against a verified findings ledger, and prints a score table.

- A `qa-review` audit of a repository with over about 10K lines of source code maps it by module, leaving out test data, fixtures and docs, and asks which paths to audit.

### Changed

- `milestone-close` offers a release at the next minor version on every milestone close, bumping each version file and renaming the CHANGELOG `[Unreleased]` section in its docs MR, and offers a tag unless the project's `CLAUDE.md` forbids tagging, replacing the pre-1.0 opt-in line, which you can remove from your project's `CLAUDE.md`.

- **Upgrade note:** `setup-dream-team` adds two project rules for CHANGELOG entries, one plain sentence each and bold only for the `**Breaking:**` and `**Upgrade note:**` prefixes; rerun it or add them to your project's `CLAUDE.md` by hand.

- The 🔵 severity is named `nit` instead of `minor`: the `qa-review` report section, the `dream-fixer-loop` severity value and its `nitFindings` result key, formerly `minorFindings`.

- The `docs-reviewer` and `docs-editor` agents read the plugin's CHANGELOG style rules when a CHANGELOG is in their diff or pages.

- The `dream-fixer` research tier posts its findings as a comment on the research issue and closes it without an MR, unless it writes output a later task reuses as a note in `docs/research/`, whose MR closes the issue.

### Removed

- The `changelog-cap` hook and the `jit-context` CHANGELOG style block; the project `CLAUDE.md` carries the entry rules instead.

### Fixed

- `dream-fixer` reads both an issue's description and its comments on GitHub and GitLab.

## [1.3.0] - 2026-10-13

### Changed

- **Upgrade note:** `scope-issue` and `dream-fixer` call a scout issue a research issue: titles start `Research:` instead of `Scout:`, and `setup-dream-team` expects the `type::research` label instead of `type::scout`; retitle open `Scout:` issues and create the label.
- The `qa-review` skill and the `dream-fixer-loop` workflow give the `architect-reviewer` lens its bare name as its focus, like the `sre-engineer` and `test-coverage-reviewer` lenses.
- The `scope-issue` skill puts a small amendment in a new comment and, when it rewrites an issue description, comments why it changed.

### Removed

- The `body-cap` hook no longer checks issue bodies; the `scope-issue` skill carries the issue rules.

### Fixed

- The `dream-fixer-loop` fix stages repair a wrong commit message with an `amend!` commit (`git commit --fixup=reword`), and `dream-fixer` folds its message into the commit it names.
- The `dream-fixer-loop` workflow no longer fails its gate on an untracked file; it returns those paths as `untrackedPaths`, which `dream-fixer` shows the user before it opens the MR.
- The `dream-fixer-loop` workflow retries once any agent that returns no result, and skips Simplify instead of failing when its review still returns nothing.
- The `dream-fixer-loop` workflow runs every call of an agent type as a generic agent once a call of that type throws, and always lists the type in `degraded`, whatever the error says.
- The `dream-fixer-loop` workflow keeps a reviewer's findings when its re-review returns nothing and re-reviews it next round; its dispute hand-back no longer counts findings the fixer was not given.

## [1.2.0] - 2026-10-12

### Added

- A read-only `test-coverage-reviewer` agent reviews a diff or paths for test gaps, and `qa-review` runs it as a lens.

### Changed

- **Breaking:** The `dream-fixer-loop` workflow drops its `domainReviewer` and `domainLens` args and runs a generic domain lens on every review, and `qa-review` runs that lens when a claim in scope is checkable against the project's reference sources.
- **Breaking:** The `dream-fixer-loop` workflow requires a `diffFile` arg, the file its gate writes the branch diff to for the reviewers.
- **Breaking:** The `dream-fixer-loop` workflow drops its `implementer` arg and runs every stage that writes code as a generic agent.
- **Breaking:** The `dream-fixer` skill no longer picks an implementer or a domain reviewer, and its light path runs a `general-purpose` reviewer checking the project's reference sources on every non-docs change.
- **Breaking:** The `architect-reviewer`, `performance-engineer`, `sre-engineer`, `test-coverage-reviewer` and `docs-reviewer` agents no longer have Bash and read the diff from a file that `qa-review`, `dream-fixer`, `milestone-close` and `dream-fixer-loop` write.
- The `architect-reviewer` agent checks who owns and frees each field, which lock guards it, and the invariants background work relies on.
- The `dream-fixer-loop` workflow reviews with the `qa-review` lenses instead of `pr-review-toolkit` agents.
- The `qa-review` skill no longer runs the `performance-engineer` lens.
- The `qa-review` skill skips the `test-coverage-reviewer` lens when every file in scope is docs or config, unless one is CI, build, test-runner or feature-flag config or an agent or skill prompt.
- The `dream-fixer` skill reports the branch, whether an external reviewer runs, and a 1-3 sentence brief of the change when it starts the workflow, instead of the implementer and domain reviewer types.

### Fixed

- The `friction` skill skips a corrupt JSONL line or record anywhere in its cache, journals and transcripts instead of crashing every later run.

## [1.1.0] - 2026-10-10

### Changed

- **Breaking:** The `qa-sec` skill is renamed `qa-review` and drops the `security-review` and `security-audit` lenses; run `/dream-team:qa-review` instead of `/dream-team:qa-sec`.
- The `qa-review` skill runs its lenses as subagents and merges their findings in the main session instead of through the `dream-team:qa-sec-review` workflow, which is removed, and no longer writes a report file.
- The `qa-review` skill's verify pass runs as subagents instead of through the `dream-team:qa-sec-verify` workflow, which is removed.

## [1.0.1] - 2026-10-10

### Fixed

- The `qa-sec` skill no longer states that subagents cannot spawn subagents.

## [1.0.0] - 2026-10-10

### Added

- The `milestone-close` skill runs `docs-reviewer` on the milestone's merged diff in its docs check and has `docs-editor` fix the approved drift in the docs MR.
- The `dream-fixer` skill runs `docs-reviewer` on the branch diff after the workflow and has `docs-editor` fix the drift it finds before the MR opens.
- The `sre-engineer` agent reviews a diff or paths for failure behaviour, read-only, and `qa-sec` runs it as a lens on every review and audit.
- The `chaos-planning` skill reviews a launch's failure-experiment plan and reports missing experiments and experiments lacking a hypothesis, injection, blast radius or pass criterion.

### Changed

- The `docs-editor` and `docs-reviewer` agents run on the caller's model instead of haiku.
- The `docs-editor` agent leaves out edge cases and troubleshooting the brief did not ask for in write mode, and checks a behaviour in a command's own code before writing it for that command in drift mode.

## [0.31.1] - 2026-10-09

### Fixed

- The `architect-reviewer`, `performance-engineer` and `lab-runner` agent descriptions parse as valid YAML.

## [0.31.0] - 2026-10-09

### Added

- A user-invoked `qa-sec` skill reviews a branch or audits a repo with parallel read-only lenses and an opt-in verify pass.

## [0.30.0] - 2026-10-09

### Added

- A read-only `architect-reviewer` agent reviews a diff or paths for design defects.

## [0.29.1] - 2026-10-09

### Changed

- The `performance-engineer` and `lab-runner` descriptions say what each agent does before when to use it.

## [0.29.0] - 2026-10-09

### Added

- A read-only `performance-engineer` agent reviews a diff or paths for performance cost.

## [0.28.0] - 2026-10-08

### Changed

- `dream-fixer-loop` skips a `generic` domain reviewer unless `domainLens` names its check, and
  `dream-fixer` runs no light-path reviewer when the domain reviewer type is `none`.

## [0.27.0] - 2026-10-08

### Added

- `setup-dream-team` checks the `type::`, `area::` and workflow label colours against a fixed scheme
  and recolours or creates labels to match it.

## [0.26.0] - 2026-10-08

### Removed

- `dream-fixer` no longer runs a project specialist domain reviewer when the project's `CLAUDE.md`
  asks for one; it picks a `generic` domain reviewer only for a lens the issue needs, and `none`
  otherwise.
- **Breaking:** `dream-fixer-loop` no longer takes the `verify` arg or returns `verifyRun`;
  `dream-fixer` no longer runs Claude Code's `/verify` as a Review gate.

## [0.25.1] - 2026-10-08

### Changed

- `dream-fixer` reports three or more numbers compared across cases as a table instead of bullets.

## [0.25.0] - 2026-10-08

### Changed

- `dream-fixer` runs a project specialist domain reviewer only when the project's `CLAUDE.md` asks
  dream-fixer for one and names its lens, never for any rule or reference the file sets out.

## [0.24.0] - 2026-10-08

### Changed

- `setup-dream-team` accepts an open issue with no milestone when it carries the waiting or
  blocked label, and checks the waiting label only on issues in a milestone.
- `setup-dream-team` files all remaining failing checks as one maintenance issue instead of one
  issue per check.
- `setup-dream-team` and `cut-milestones` require a ROADMAP only when two or more milestones are
  open or one depends on another, and a version milestone's release criteria live in its `Gate:`
  bullet.

## [0.23.0] - 2026-10-08

### Added

- `scope-spec`, a user-invoked skill (`/dream-team:scope-spec`), writes a project spec in
  `docs/specs/` from the spec template it carries.

### Changed

- `dream-fixer` names a scout's research note `docs/research/YYYY-MM-DD-<slug>.md` and gives it a
  fixed header, a short context and one section per finding.
- `milestone-close` asks the user to approve or reject each proposal by number, and says what
  approving it does, instead of asking which to keep.

### Removed

- `jit-context` no longer injects the spec template on writes to a `docs/specs/` design file.

### Fixed

- `branch-guard` no longer blocks plan files such as `docs/plans/x.md` or `test-plan.md` on
  `main`.
- `dream-fixer-loop`'s nested `/verify` run cannot call ssh and is told to run no lab-only
  command. The gate kills the processes the run leaves alive, reports them in `verifyRun.killed`,
  and moves the recipe file out of the checkout on every outcome.

## [0.22.0] - 2026-10-07

### Added

- `dream-fixer` has the implementer add a decision record to `docs/decisions/`, numbered from
  `0001`, when the change carries a decision that passes the record format's three-part test.

### Removed

- `jit-context` no longer injects a decision-record rule on writes under `docs/decisions/`.

## [0.21.0] - 2026-10-07

### Added

- `friction`, a user-invoked skill (`/dream-team:friction`), reports agent friction repeated
  across past `dream-fixer-loop` runs and offers to file an issue for each pattern.
- `dream-fixer-loop` agents can self-report friction in an optional `friction` output field.

## [0.20.0] - 2026-10-07

### Changed

- `scope-issue` asks the user its open questions before filing an issue requested in chat, and
  still files an issue found during other work without asking.

## [0.19.0] - 2026-10-07

### Changed

- **Breaking:** the `scope-style` plugin is merged into `dream-team`; its skills are now
  `dream-team:scope-commit`, `dream-team:scope-mr` and `dream-team:scope-issue`.
- **Upgrade note:** uninstall `scope-style@dream-team` and reinstall `dream-team@dream-team`.
- The pi package is renamed to `dream-team` and loads every skill.

## [0.18.0] - 2026-10-06

### Added

- `dream-fixer-loop` accepts `domainReviewer: "none"`, which runs no domain reviewer and has
  `code-reviewer` check the issue's `Done when` paragraph instead.

### Changed

- `dream-fixer` runs no domain reviewer when the catalog has no second specialist for the issue,
  unless the project's `CLAUDE.md` asks for a project specialist.
- `dream-fixer` folds the branch by committing the first commit's message from a file, so the
  body-cap hook checks the body that reaches history.

## [0.17.0] - 2026-10-06

### Changed

- **Breaking:** the `align-project` skill is renamed `setup-dream-team`, run as
  `/dream-team:setup-dream-team`, and Claude no longer starts it unprompted.
- `setup-dream-team` fixes missing project rules and labels, milestone bullets, `Blocked by`
  lines and the waiting label directly after one confirm, and files issues only for the other
  failing checks.
- `dream-fixer` uses the tier a project's `CLAUDE.md` sets for an issue instead of its own
  tier criteria.

## [0.16.0] - 2026-10-06

### Added

- A change requested in chat that needs a user decision, contradicts the spec, adds a component, or
  needs a lab check is offered as an issue instead of being edited inline.

## [0.15.1] - 2026-10-05

### Changed

- `dream-fixer-loop` treats the issue's `Done when …` paragraph as the finish line, and the domain
  reviewer checks it.

### Fixed

- `cut-milestones` adds the waiting label to the open issues already in a milestone with an open
  dependency, and puts a dependency that gates only the exit measurement in `Exit:` instead of
  `Depends on:`.

## [0.15.0] - 2026-10-04

### Added

- `milestone-close` proposes cutting a `CLAUDE.md` or `CLAUDE.local.md` line when a change outside
  the repo, such as a lab host's config, could fix its gotcha, and recommends that change.

### Changed

- `milestone-close` judges `CLAUDE.local.md` lines for a cut by the same checks as `CLAUDE.md`
  lines, instead of whether a line still fires.

### Fixed

- The `<project_notes>` rule has a session read `CLAUDE.local.md` before adding a line, so a gotcha
  already there is sharpened instead of repeated.

## [0.14.1] - 2026-10-03

### Changed

- `dream-fixer` calls its step 2 triage, and `dream-fixer-loop` names the `gateCommands` phase
  and its failure stage `Gate`/`gate` instead of `Verify`/`verify`, so "verify" means `/verify`
  only.

### Fixed

- `WORKFLOW.md` describes the light tier as `dream-fixer` runs it since 0.13.2.

## [0.14.0] - 2026-10-03

### Added

- `milestone-close` tags a pre-1.0 milestone close as the next `v0.<n>.0` when the project's
  `CLAUDE.md` opts in, and recommends that opt-in when it is missing.

## [0.13.2] - 2026-10-01

### Changed

- `dream-fixer` light tier takes a small bug fix the orchestrator already reproduced, and every
  light-tier change gets one reviewer: `gdoc-writer` for docs, the domain reviewer otherwise.

## [0.13.1] - 2026-10-01

### Changed

- `align-project` treats the component table as optional; a table that exists matches the code
  and notes only what a component's name and path don't say.

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
