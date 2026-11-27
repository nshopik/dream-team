# Changelog

All notable changes to this plugin are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/2.0.0/).

## [Unreleased]

### Added

- `craft-it` runs on Claude Code without the Workflow tool: the main session dispatches the `craft-it-loop` stages as subagents, runs every `gateCommands` entry itself after each writing agent, and returns the same result.

### Changed

- `setup-dream-team` writes a `docs/CONVENTIONS.md` and a `## Doc conventions` block in an own clone's `CLAUDE.md`, replacing its `Repo layout:` line or the layout lines it declares.
- `craft-it-loop`'s domain lens takes `qa-review`'s domain wording and runs in a project that names no reference source: it names the project's domain, checks the diff against what a change in that domain must get right, and raises as questions what only the owner can settle.
- `build-rules` has a change reuse an existing test helper, mock, stub or fixture, move one it would copy from another test file into a shared test module, and extend an existing test of a path instead of testing it again at another level.
- `scope-mr` pipes the MR/PR description to `diff-budget.py` on stdin (`-` as the file argument) instead of writing it to a temp file first.
- **Breaking:** In an own clone, `craft-it`, `scope-spec`, `cut-milestones` and `milestone-close` take doc paths, naming and the decision-record template from `docs/CONVENTIONS.md` instead of using plugin defaults or writing the file themselves; when it is missing, `scope-spec`, `cut-milestones` and `milestone-close` stop with "run `setup-dream-team` first", and `craft-it` stops only when its issue asks for a decision record and otherwise picks milestones from the tracker only.
- **Breaking:** `setup-dream-team` writes the local tracker rules to `.dream-team/TRACKER.md` in an upstream clone, and `craft-it`, `scope-issue` and `ask-team` read them there, stopping with "run `setup-dream-team` first" when the file is missing, `ask-team` only when `.dream-team/issues/` holds a file.
- **Upgrade note:** Run `setup-dream-team` in each upstream clone that keeps local issues so it writes `.dream-team/TRACKER.md`, and in each own clone, so it writes or updates `docs/CONVENTIONS.md`.
- In a clone not marked own, `craft-it`, `scope-spec`, `cut-milestones` and `milestone-close` take doc paths from the upstream's `CLAUDE.md`, `AGENTS.md` or existing records or specs folder, and write no record, spec or ROADMAP when none names one.
- The `docs/CONVENTIONS.md` template `setup-dream-team` writes adds the glossary path, the `NNNN` numbering rule and the record's optional sections and drops the decision-record test, which `scope-issue` alone applies; `craft-it` writes a record only for a decision its issue says gets one.
- `scope-spec` uses `GLOSSARY.md` terms and coins none; `scope-issue` keeps the glossary rules.
- `brainstorm` ends with the shared understanding and one line naming the next skill, `scope-spec`, `scope-issue` or none, instead of proposing a path and handing off once the user approves it.
- `scope-issue` holds findings on a `Research:` issue while probe rounds still run, then posts one comment with the current state instead of a comment per finding.

### Removed

- **Breaking:** The pi package install, `pi install git:github.com/nshopik/dream-team`, is removed; install the skills on pi with `npx skills add nshopik/dream-team --global`.
- **Breaking:** `craft-it-loop` drops its Simplify phase and the `simplify` result field, going from the gate straight to review, and its `startAtSimplify` argument is renamed `startAtReview`.
- **Breaking:** `craft-it-loop` no longer fixes nits, in a fix round or a pass after review, and drops the `nitFix` result field; it still returns every nit in `nitFindings`, and `craft-it` applies none.

### Fixed

- `scope-issue` reads its glossary rules before it writes an issue, and a reply that proposes a new term holds only the question until the user's OK.
- `scope-issue` loads `brainstorm` with the Skill tool before it asks about an undecided design choice or a done-when check that is not observable.

## [26.11.2] - 2026-11-17

### Added

- The README gains a "Start here" section with one command per situation.
- In a clone not marked own, `scope-issue` writes issues to local `.dream-team/issues/` files, `craft-it` builds from them and `ask-team` reads them.
- The `build-rules` skill holds the build rules for a code change (scope, error handling, where the change goes, comments, option docs, tests); `craft-it-loop`'s implementer, build-fix, simplify-fix, review-fix and nit-fix agents load it before their first edit, and its simplify review judges the diff against it.

### Changed

- **Breaking:** The `build-issue` skill is renamed `craft-it` and its `build-issue-loop` workflow `craft-it-loop`, so the command is `/dream-team:craft-it`.
- **Upgrade note:** Replace `build-issue` with `craft-it` in any `CLAUDE.md`, `CLAUDE.local.md` or `settings.json` line that names the skill or its workflow.
- `ask-team` picks from a skill map that puts every skill in one group (main flow, on-ramp, standalone or precondition), and its reply's `Step:` line becomes `Where:`, naming the `WORKFLOW.md` step for a main-flow skill and the map group for any other.
- A decision record lands in the commit of the change it records: `scope-issue` states the decided choice in the issue and opens no docs MR, `craft-it` no longer stacks the issue branch on a `decision-` branch, and `brainstorm` no longer offers a decision-record path: a settled choice becomes an issue.
- **Upgrade note:** an issue whose decision docs MR opened before this release is finished by hand: merge or close that docs MR and delete its `decision-` branch and worktree.
- `qa-review`'s domain lens runs in every project with a `CLAUDE.md`, `AGENTS.md` or README, names the project's domain, checks the code in scope against what a change in that domain must get right, and raises as questions what only the owner can settle.
- **Breaking:** `/dream-team:friction` with no argument scans only the current session, its subagents and its workflow runs, reports every hit and lists retro improvement candidates by severity; `/dream-team:friction all` runs the cached scan of every past `craft-it-loop` run, and both flag an agent that skipped a `build-rules` or `scope-commit` load its prompt asks for.
- `craft-it-loop` wraps the issue body and the orchestrator notes in `<issue_body>` and `<orchestrator_notes>` tags in every agent prompt, and a workflow line outside the tags wins over the tagged text.

### Removed

- `scope-issue`, `craft-it` and `milestone-close` no longer file light-tier findings as one bundle issue; each finding gets its own issue.
- **Upgrade note:** rewrite an open bundle issue, one with an `## Items` checklist, as one plain issue per item before building it.

### Fixed

- Skills read the `dream-team.own` marker from the clone's local git config as a boolean, as the `jit-context.py` hook does, so a global marker no longer counts and a local `yes` or `1` does.
- `assemble-meta` lands each child inside the Meta issue's worktree, so a run started in the main checkout no longer fast-forwards `main`.

## [26.11.1] - 2026-11-17

### Added

- The `ask-team` skill, run only when named, reads the open milestones, unblocked issues, open MRs/PRs and git state, then recommends the skill that fits now with a ready-to-run command and the `WORKFLOW.md` step behind it; `WORKFLOW.md` moves to `skills/ask-team/WORKFLOW.md`.
- The `brainstorm` skill grills a vague idea in rounds of questions, then states the shared understanding and proposes a path, acting on it only after the user approves it.
- The `assemble-meta` skill takes a Meta issue's children to one MR/PR: it triages them all before any code, builds up to two children at once up to the gate, each on its own branch in its own git worktree, lands each on one integration branch, reviews and fixes the whole branch once, and closes the finished children.
- The `triage-issue` skill checks a legacy or outside-filed issue against the code and rewrites it in `scope-issue` form before it is built.
- An issue `scope-issue` files during other work with open questions gets the `workflow::needs-brainstorm` label, which `build-issue` stops on and `triage-issue` lists, answers with `brainstorm`'s question rounds and removes once none is left open; `setup-dream-team` creates the label.
- `build-issue-loop` takes `stopAfterGate` to end a run after the gate and `startAtSimplify` to start one at Simplify over the diff from `base`, with `redEvidence` handing that run the failing output earlier runs saw.
- `scope-spec` and `scope-issue` use the field-standard word or a plain phrase, ask before coining a term, and record each approved term in a root `GLOSSARY.md`, or as a proposal item when only an issue uses it; only an own clone creates the file, with a pointer line in `CLAUDE.md`, or in `AGENTS.md` when only that exists.
- In an own clone whose `CLAUDE.md` or `AGENTS.md` declares no doc conventions, skills commit the first new decision record, spec or ROADMAP with a `docs/CONVENTIONS.md` and a pointer line in `CLAUDE.md`, or in `AGENTS.md` when only that exists.
- `build-issue-loop` takes `worktree`, a path every agent of the run works and commits in.
- `setup-dream-team` checks that the project `CLAUDE.md` or `AGENTS.md` names a reference source or review invariant for the domain lens, drafts candidate lines for approval when it names none, and reports when the repo offers no candidate.

### Changed

- **Breaking:** The `dream-fixer` skill is renamed `build-issue` and the `dream-fixer-loop` workflow `build-issue-loop`, so the command is `/dream-team:build-issue`.
- **Upgrade note:** Replace `dream-fixer` with `build-issue` in any `CLAUDE.md`, `CLAUDE.local.md` or `settings.json` line that names the skill or its workflow.
- The `<project_notes>` block `jit-context.py` adds at session start asks that each new `CLAUDE.local.md` line end with the condition that retires it.
- `build-issue` given a Meta issue stops and names `assemble-meta` for all its children or `build-issue` on one child, and no longer picks the oldest unblocked child itself.
- **Breaking:** `jit-context.py` adds the upstream-project rules in every git repo whose `dream-team.own` git config is not `true`, and no longer reads the `DREAM_TEAM_OWN_REMOTES` environment variable.
- **Upgrade note:** Run `setup-dream-team` once in each clone of your own project or fork and answer that it is your own.
- **Upgrade note:** Run `/dream-team:setup-dream-team` once in each project to create the `workflow::needs-brainstorm` label.
- **Breaking:** Skills label an issue's kind with one flat tracker label, `bug`, `feature`, `maintenance`, `performance`, `research` or `meta`, in place of `type::*`, name `workflow::blocked`, `workflow::future` and `workflow::needs-brainstorm` on GitHub too, and add `wontfix` to an issue closed as not planned.
- **Upgrade note:** Run `/dream-team:setup-dream-team` once in each project to swap each issue's `type::*` label for its flat kind, delete the `type::*` labels and create the missing ones.
- `qa-review` tells each lens to report every defect it finds, including uncertain or low-severity ones.
- `scope-issue` cites a doc the forge's readers can open by its URL or path, at the claim it backs.
- `scope-issue` draws one Mermaid diagram when the defect or new design is a relationship between 3 or more named modules or paths.
- `milestone-close` ends its report with an offer of the next version; a yes or another version runs `ship-it`, which puts the bump in the docs MR while it is open, else in its own MR, waits for it to merge and pushes the tag without asking, and no reply releases nothing.
- A decision record can carry one Mermaid diagram of at most 12 nodes when the decision relates 3 or more named parts.
- `scope-issue` comments a finding while its direction is open, rewrites only the proposal once it is decided, and supersedes the issue with a new one when the title or problem no longer holds.
- A lab or research result for an open issue is posted on it as a comment without asking.
- `scope-spec` ends each Decision and Design point settled in an issue, MR or comment with a link to it.
- `ship-it` tags the release's merge commit without asking when the user passes the version as its argument.
- `setup-dream-team` applies fixes that change no code after one OK, commits its `CLAUDE.md` and repo-doc edits, and files a maintenance issue only for the rest.
- `scope-issue` and `build-issue` file two or more light-tier findings from one run as one bundle issue, and `build-issue` ships a bundle as one MR with one commit per item.
- `build-issue` and `assemble-meta` settle reviewer questions before the MR/PR opens: the orchestrator answers those the code, the issue, the spec or a project rule settles, asks the user the rest in one dialog, has an agent commit any answer that changes the code, and posts every answer on the issue; the final report no longer has a `**Questions:**` line.
- `build-issue` watches an MR/PR's pipeline once the MR/PR opens, retries an infrastructure flake once, and pushes up to two fixes for a real failure before handing the MR/PR back with a comment.
- `review-bench` weighs every minor ledger row 0.5, no longer reads a row's `nit` field, and holds every minor candidate for the next ledger bump.
- The `build-issue` and `assemble-meta` reports leave out resolved findings and any line the skill does not name, and show an assumption only when it departs from the issue's text or changes observable behaviour.
- `build-issue`'s report at workflow launch describes the change in 1-2 sentences and adds nothing before or after the layout.
- `scope-issue` files two or more unattended, non-research issues in one milestone under one `Meta:` issue set to that milestone, or files one on request with the human-loop issues proposed for the user to confirm, and `assemble-meta` takes a Meta issue whose children are independent.
- `scope-issue` and `build-issue` write a hard-to-reverse design decision to `docs/decisions/` in its own docs MR when it is made, `scope-spec` through `scope-issue`, and `build-issue` stacks the issue branch on that record.
- `scope-issue` ends an issue with a `## Done when` section, one bullet per check, and `build-issue-loop` checks each bullet on its own, reading the old `Done when …` paragraph on older issues; `build-issue` hands the branch back on a check that does not hold and that no fix round resolved.
- `build-issue` given a `Meta:` issue works its oldest open, unticked child with no open blocker, reports each child's open blockers when every one is blocked, and reports no work left when none is open.
- `scope-issue` asks nothing when no question is open, and runs `brainstorm`'s question rounds on a hard-to-reverse design choice whose options are not yet known or a done-when check that is not observable.
- `build-issue` stops on an untriaged issue and says to run `triage-issue #<n>` first.
- `scope-issue` asks before filing an issue whose needed facts run over the 500-word cap, offering a meta issue split or an over-cap filing, and files one found during other work over the cap with its word count in the run's report.
- Skills take the path, file naming and template of decision records, specs and the ROADMAP from the project's `CLAUDE.md` or `AGENTS.md`, else, for decision records only, from an existing records folder such as `docs/adr/`, else from the defaults `docs/decisions/`, `docs/specs/` and `ROADMAP.md`.
- `setup-dream-team` checks milestone names, exit criteria and bold bullets, `area::` labels, the architecture diagram and the contributor doc path only in a repo that uses them, and checks `type::` and `area::` labels only on issues in an open milestone.
- `milestone-close` and `cut-milestones` stop on a milestone not named `M<n>`, `YY.MM` or `v<major>.<minor>` (SemVer past 1.0) and point to `setup-dream-team`.

### Removed

- The `chaos-planning` skill is removed.
- The `branch-guard.py` hook is removed, so a spec or design doc can be written on `main` or `master`.
- The `body-cap.py` hook is removed; `scope-mr` runs `diff-budget.py` on the MR/PR description instead, which warns when the description is over its diff budget, and the 300-word cap, rubric-heading, `--fill` and left-out-item checks are no longer enforced.
- `setup-dream-team` no longer checks label colours, issues with no milestone and no parked label, or the problem, proposal shape of issues.
- The `architect-reviewer` agent no longer checks for behaviour added to one implementation of an interface but missing from the others, a new function that duplicates an existing one, or a derived value updated by hand at each mutation site.

### Fixed

- `build-issue-loop` moves a question a re-review answers from `questions` to `resolved`, and the `build-issue` and `assemble-meta` reports list each distinct question once with every reviewer that asked it.
- `build-issue-loop`'s implementer commits nothing and returns `committed: false` when an issue or note says to stop on a failing check, or when a choice would reverse a decision an earlier commit body on the branch records.
- `build-issue-loop` reviewers give each finding's `file` as a repo-relative path.
- `build-issue-loop` returns `degraded` and `untrackedPaths` on every result, including an implement, gate, simplify or fix stage failure.
- `scope-mr` allows before/after measurements in an MR/PR description, matching `build-issue`, which puts lab numbers there.
- `scope-commit` and the git-context hook say to amend a commit only for a late change the user asks for on an open MR/PR.
- `scope-issue` leaves out chat threads, shared docs, local paths and internal hosts the forge's readers cannot open, and the names of customers and people outside the project.
- `scope-issue` files a Meta child whose only open blockers are its sibling children, with one `Blocked by` line per sibling, so `assemble-meta` takes those children too.
- `review-bench`'s `run.sh` no longer loses a run when parallel runs add their worktrees at once, and prints each run that leaves no `stats.txt` as failed.
- `build-issue` and `assemble-meta` symlink each gitignored input the issue, the Meta issue's children or the project's `CLAUDE.md` or `AGENTS.md` names into the worktree, exclude it from git and name it in the workflow's `notes`, so tests that read it run instead of skipping.
- `setup-dream-team` passes a flow-mode version milestone whose `Exit:` names only its due date, and `cut-milestones` writes a flow-mode `Exit:` with a headline only when the user names one.

## [26.11.0] - 2026-11-10

### Added

- `cut-milestones`, `setup-dream-team` and `milestone-close` support version milestones that close at their due date, with open issues moved to the next version, in a project whose `CLAUDE.md` says `Version milestones release in flow mode.`
- `setup-dream-team` sets a `type::performance` label, when the tracker has one, to colour `#AD4363`.
- The `friction` skill records each agent's and each run's wall clock in minutes, and `--time` prints a table of them per role and per run.

### Changed

- `cut-milestones` writes every pre-MVP milestone as a ROADMAP row with a dependency graph and creates in the tracker only those whose dependencies are closed, leaving the rest as `planned` rows.
- `milestone-close` proposes each `planned` ROADMAP row whose dependencies are closed as a new milestone with the next free `M<n>`.
- `cut-milestones` and `milestone-close` give each new `M<n>` milestone a due date the user sets, and keep at most 3 `M<n>` milestones open, leaving the rest as `planned` rows.
- `setup-dream-team` accepts `planned` ROADMAP rows and checks the dependency graph against the rows.
- `scope-spec` aims for about 1,500 words and, for a draft over 2,000 words, asks the user which Design subsections to move to a topic doc.
- `setup-dream-team` and `cut-milestones` require ROADMAP rows only for `M<n>` milestones and `planned` rows, never for version milestones.
- `dream-fixer` commits a small fix, up to about 50 lines, for a defect found outside the diff on the branch as its own commit, and files an issue only for a defect that needs a decision, a lab check or a design choice.
- `dream-fixer` tells the user the rough time to completion before it dispatches lab work.
- `dream-fixer-loop` passes reviewer nits to the fixer, in a fix round or one pass after review, and the fixer fixes the cheap ones without a re-review.
- `dream-fixer-loop` has each live reviewer review the diff of each fix round that commits, raising new findings only on lines that diff adds or changes or on defects it newly reaches or worsens.
- `dream-fixer` works on each issue in its own git worktree under `.claude/worktrees/`, leaving the main checkout on its branch, and removes the worktree once the MR merges or closes.
- `milestone-close` puts drift fixes, contributor facts, ROADMAP status, backed spec notes and a release a project rule sets straight into the docs MR, and asks approval only for issues, milestones, `CLAUDE.md` and `CLAUDE.local.md` changes and an unsettled release.
- `dream-fixer` posts on the issue the triage answer, its settled disputes and, when it hands a branch back, the branch, open findings, assumptions, questions and lab numbers.
- `dream-fixer` and `scope-issue` put research findings in an issue comment, writing a `docs/research/` note only when the user asks for a file.
- The `friction` skill names the permission rule, hook or gate command that would stop a repeated pattern and offers an issue for that check, keeping the prompt-line offer for a pattern that needs judgement.

### Fixed

- `setup-dream-team` proposes the ratchet-floor rule only for a project with ratchet floors and the milestone-split rule only for one with open `M<n>` milestones, and its milestone-naming rule names only the forms the open milestones use.
- `dream-fixer` commits a fix for a defect already present on the base commit as its own commit, instead of folding it into an unrelated commit on the branch.
- `dream-fixer` amends the folded commit's message whenever it breaks `scope-commit`.
- In a repo with an upstream remote, the context hook tells the agent to still load `scope-commit` and `scope-mr`, and those skills let the upstream subject format and PR template win over their own.
- The body-cap hook measures a `glab api` call on an MR only when it sends a `description=` field or `--input`, so a read piped into a heredoc script is no longer denied.
- The `review-bench` score table shows a row's prefix as its reviewer when another row has the same reviewer and model, such as two reviewers whose prompts start with the same word.
- `dream-fixer-loop` reviewers report a defect the change newly reaches or worsens as a normal finding, and return a pre-existing defect as a non-blocking `preExisting` finding instead of dropping it.
- The `dream-fixer-loop` gate agent runs only the gate commands and the git commands it reports from, and no longer edits files or debugs a failure itself.
- The `friction` skill flags a read-only role that edits the tree through Bash, such as `sed -i`, `git checkout <file>` or a redirect outside `/tmp`.
- The `friction` skill no longer records `ssh`, `git push` or a forge write that only appears inside a heredoc or quoted string in newly scanned runs.
- `milestone-close` holds the docs MR until the user answers the proposals that change `CLAUDE.md`, so one MR carries the docs edits and the approved lines.

## [26.10.0] - 2026-10-28

### Added

- A `review-bench` reviewer line takes optional `effort=` and `shown=` fields after its prefix, `shown=` naming the model an external reviewer runs on, and `run.sh` grades up to `P` runs at once on a frozen ledger.
- The `review-bench` score table names each row by reviewer and model columns instead of its prefix: the reviewer is the prompt's first word without a leading `/` and plugin prefix (such as `qa-review`), and the model is `shown=`, or else `model=` without a leading `claude-`, then `-<effort>`, both read from the prefix's first run's `stats.txt`, where `run.sh` writes a `reviewer=` field.
- `dream-fixer` reviewers can rate a finding as a question, which never blocks the MR or starts a fix round, and the final report lists each one under a Questions label with its reviewer and location.

### Changed

- `ship-it` proposes the next version from the last release's tag or version file: `0.1.0` with neither, the next minor after a `0.x` version or a SemVer version at 1.0 or above, and the next CalVer `YY.MM.MICRO` after a CalVer version.
- `milestone-close` proposes the first CalVer release, in place of the next `0.x` minor, at the close of a milestone with `MVP` in its title.
- `cut-milestones` puts `MVP` in the title of the milestone that completes the MVP and names a version milestone by its target month, such as `26.11`, with the last day of that month as its due date.
- **Upgrade note:** `setup-dream-team` now expects a version milestone named `YY.MM`, or `v<major>.<minor>` only in a SemVer repo past 1.0; in a project's `CLAUDE.md`, replace the `v<major>.<minor>` milestone line with that wording, and in a repo below 1.0 rename open `v<x.y>` milestones.
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
