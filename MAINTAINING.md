# Maintaining dream-team

## Decisions and rejected options

Origin: one 1332-line spec that was hard to execute in parts. The issue-sized flow replaced it.
Planning stays explicit, at issue size, because you review every plan.

- Planning skills adapt an established practice and name it: stage-gate milestones, rolling-wave
  planning, sprints, the weekly review, a WIP limit, an appetite. dream-team does not invent its
  own.
- Facts for the contributor doc are swept once per milestone by `milestone-close`. A prompt on
  every MR was rejected: it asks a question on MRs with nothing to keep.
- A rule comes first; a hook is added only after the rule has failed once.
- In the `qa-review` skill, a lens with no installed agent type fails dispatch and is listed as
  missing; it never falls back to a generic agent. `craft-it-loop` instead retries that lens
  as a generic agent and lists its type in `degraded`.
- No global "issue-sized work gets no spec" rule: it duplicates the scope rules. The unreviewed,
  plan-like September specs came from a skill that has since been rewritten into `craft-it`.
- The upstream-repo guard lives in `jit-context.py`, not a tracker skill: that skill loads only
  before the tracker CLI and only on owned remotes, so it fires too late and on the wrong repos.
- Run `git config --local dream-team.own true` in your clone of this repo; without it every
  session here gets the upstream-repo rules.
- A living doc stays small by holding current state only: rationale goes in commits and MRs,
  plans in issues, component internals nowhere beyond one module-doc sentence.
- Retired: the `dream-team` skill, `dream-team-loop` and `dream-team-run`. `craft-it`
  replaces them.
- ROADMAP status moved from each feature MR to `milestone-close`: status lags until the close,
  but concurrent MRs stop conflicting on it.
- Issue order comes from `Blocked by` lines, not a board ordering or a separate skill.
- Field evidence gets its own `Evidence:` issue rather than `milestone-close` collecting it
  unannounced: the deploy and its start date are written down before the clock starts.
- Work spanning milestones (full RFC 8914 coverage) is a `Meta:` issue, not a milestone (one
  exit gate cannot cover it) and not a per-item table in the repo (every MR would churn it). A
  closed child shows "(closed)" beside its mention; the box is ticked at `milestone-close`.
- A milestone's issues that can run unattended go under one `Meta:` issue set to that milestone,
  so `assemble-meta` ships them as one MR for one review and merge; issues needing a lab run,
  credentials or a product call run through `craft-it`, and `milestone-close` stays the human
  gate before the next milestone.
- A version milestone's release is scope-based by default: one headline feature plus backlog, behind
  standing release criteria in the version milestone's `Gate:` bullet. Its `YY.MM` name is the month
  it targets, not a promise about the API. A project whose `CLAUDE.md` says `Version milestones
  release in flow mode.` releases each version milestone at its due date with whatever has merged,
  behind the same `Gate:` release criteria, its headline an optional target. The style is a
  project choice, independent of the version scheme: Kubernetes and the Linux kernel release on a
  timeline, Kubernetes under SemVer, and CalVer projects can gate on features. Continuous
  delivery, every merge a release with no version milestones, is out of scope.
- Versions are `0.x` before the MVP and CalVer `YY.MM.MICRO` from it on, once the user names
  `<YY.MM>.0` in reply to a release offer: a project that ships often and makes no API promise
  gets nothing from major and minor numbers, and a date says when the release shipped. The form
  stays SemVer-parseable and sorts above any `0.x`. The last release's version, its tag or else
  the version file, picks the scheme, so a SemVer repo past 1.0 stays SemVer until the user names
  a CalVer version.
- A ROADMAP tracks only `M<n>` milestones and `planned` rows: pre-MVP milestones whose exit gates
  depend on each other. After the MVP a CalVer project runs version milestones as a release
  train, and each one's `Exit:`, `Gate:` and `Depends on:` fit in its tracker description, so a
  row only copied them. The old rule, rows whenever two milestones were open, lost: a project
  planning several releases ahead keeps each one's plan in its milestone description.
- Release stays user-approved in both styles: the `milestone-close` report offers the next
  version at every close, `M<n>` and version milestone alike, and releases between closes happen
  through `ship-it`. A milestone close is the release point for most projects; a pre-1.0 opt-in
  line left the rest closing milestones with no release. A yes or a named version runs `ship-it`
  with it as the argument: the bump joins the docs MR while it is open and the tag is pushed once
  the MR merges, one reply for version and tag. No reply releases nothing. The close keeps no
  version rules of its own: its CalVer-after-MVP proposal stopped a SemVer `0.x` close; a scheme
  change or a major release happens when the user names the version.
- This repo pilots a bugfix-only window for 26.12, from 2026-12-15 to its due date.
  - `bug` means a skill or agent did the wrong thing in a real run; a wished-for capability
    goes to the next milestone.
  - At window start, release `YY.MM.0` in place of the flow-mode due-date release, move open
    feature issues to the next milestone, and leave unmerged feature PRs waiting.
  - Release `.1`, `.2` on demand during the window. At close, release any unreleased fix; with no
    fixes `.0` is final.
  - The window always ends at the due date; open bugs move to the next milestone.
  - Testing is free-form real use. At close, add one milestone comment naming what was run and
    which bugs were found.
  - A bug found after close waits for the next `.0`, because a release of main then also ships the
    features merged since.
  - At 26.12 close, read the milestone comment and decide whether to keep the window, change it
    or offer it as a plugin option.
- `milestone-close` asks only for what leaves the docs MR or changes agent rules; drift fixes,
  ROADMAP status, facts and backed spec notes ride in the docs MR, whose review approves them.
  A numbered approval per page edit asked twice for one decision.
- Milestones are `M<n>`, not a bare integer: "milestone 5" reads badly in prose and collides
  with counts ("all 5 sites"). One generic prefix beats a per-project codename; the repo name
  disambiguates the rare cross-project mention.
- Pre-MVP milestones wait as `planned` ROADMAP rows and get their `M<n>` when their dependencies
  close and fewer than 3 `M<n>` milestones are open: creating them all at cut time numbered them
  in cut order, not work order. The cap is a WIP limit that keeps the open milestone list showing
  what is being worked on (the weekly-milestone trial in #349).
- `workflow::future` marks issues that cannot start yet: parked issues, and issues in a milestone
  with an open dependency. The Board's default column is what can start now. `workflow::future`,
  not `workflow::blocked`: blocked means an external gate someone must chase; future clears itself
  when the dependency closes.
- A parked issue has no milestone and `workflow::future` or `workflow::blocked`, not a `Future`
  milestone: a milestone with no exit gate fails the naming and exit checks while any other open
  milestone is numbered, and `milestone-close` stops on it.
- `setup-dream-team` applies the fix for a failing check after one confirm when that fix changes no
  code and the draft can state it, since a filed issue for one label cost a milestone choice and a
  `craft-it` run. It files the
  remaining checks as one maintenance issue, not one issue per check: one issue each added a
  branch, an MR and a `craft-it` run per edit.
- Issues are the log, docs the reference: a fact the code and paths don't show has one reference
  doc, updated in the MR that changes it. One large spec went stale and hard to skim; a closed
  issue is not a place anyone looks things up.
- No document per `area::` label. Folder names already say where things live; a per-label
  pointer list repeats them and rots on every rename. A topic doc exists only for what is not
  obvious from the tree.
- The component table is optional. Where folder names already say what each component does, a
  table restating them is a pointer list and rots like one. A project that keeps one gives each
  component a row and a note only where the name and path fall short.
- `craft-it-loop` reviews with the `qa-review` lenses, not `pr-review-toolkit`: the lenses
  scored as well at about 64% of the cost (#217, #219).
- `performance-engineer` runs in neither lens roster: it added 0-6 points over the other lenses
  at about a fifth of the lens cost (#224). It still ships as an agent.
- `craft-it` picks no implementer or domain reviewer: specialist implementers made no
  difference (#192), and the domain check is a `qa-review` lens (#225).
- `craft-it`'s `subagent-loop.md` restates the control flow of its bundled `craft-it-loop.js`:
  stages, caps and branches. A change to one updates the other in the same MR.
- Claude's manifest registers the workflow and agents directly from the skill folders.
  Skills-only installers copy one folder at a time, so keep these resources inside their
  owning skills.
- No skill reaches another skill's files by a `<base directory>/../` path (decision record
  0009). Use the host's skill lookup to resolve the owning skill. If the host has no skill tool,
  read the advertised `SKILL.md` directly. Repo data lives in `docs/CONVENTIONS.md` or
  `.dream-team/TRACKER.md`, which `setup-dream-team` writes. `test_skill_links.py` fails on a
  cross-skill path. Workflow references sit flat beside their `SKILL.md`. Bundled reviewer prompts
  live in `qa-review/agents/`.
- `.dream-team/TRACKER.md` and `docs/CONVENTIONS.md` are copies of `setup-dream-team`'s
  `tracker-local.md` and `repo-conventions.md` template; a clone keeps its copy until setup runs
  again, so a change to either file gets a CHANGELOG `**Upgrade note:**` to re-run setup.

## Building agents

Reviewer agents start from the closest dream-team agent, a voltagent body from
`VoltAgent/awesome-claude-code-subagents`, or a `pr-review-toolkit` agent, and change only what an
eval shows. Evals run in a local harness kept out of the repo.

- Starting from a voltagent body, cut its Communication Protocol, progress and delivery JSON,
  agent-integration list and process checklists (testing, monitoring, culture, capacity).
- Keep the domain keyword lists: they are the cues that give the agent its breadth. A rewrite of
  them into a few condensed rules missed more confirmed findings.
- Never add a rule that filters findings ("never a redesign", "no hot path → no finding", "runs
  once → skip", a mandatory caller chain, "review the diff file by file"); the verify pass gives
  precision.
- Add a line only for a miss seen in an eval, naming the missing concept, not a generic step
  ("read the library source" changed nothing).
- Keep a reviewer off Edit and Write with `disallowedTools: Edit, Write, NotebookEdit`, never a
  `tools:` allowlist; pi's subagent extension reads `tools:` in its own tool names (#278).
- Count Bash as a reviewer's open write path: only its prompt guards it, and a prompt rule did
  not keep a reviewer off Bash (#229).
- Never pin `effort:` in a shipped agent; pin it in the eval harness instead.
- Name the agent by role (`performance-engineer`); the role name is a cue too.
- Give a qa-review lens its bare name as its focus; a focus line naming some of an agent's
  sections steered it off the rest (#261).
- Reviewed and skipped for the docs agents: voltagent `documentation-engineer`,
  `readme-generator`, `tooling-engineer`.
- Reviewed and skipped for an infra-config lens: voltagent `devops-engineer`; the default lenses
  of that time, `security-audit` included, reported 20 of its 23 confirmed findings (#173).
- Build a skill only for knowledge the model lacks: own conventions, behaviour after the
  training cutoff, internal tools.
- Name a skill in the agent body or brief that needs it; an unnamed skill is not loaded (#191).
- Never build an agent for a broad role (DevOps) or for public platform knowledge (#172, #173).
- Judge a change by A/B runs of old and new agent in the same run, on real regression commits
  with a later fix as ground truth, on haiku, sonnet and opus, followed by an opus verify pass.
- Score expected findings against the case's fix, not the verify verdict; the verify judge is
  unreliable on micro-performance without real benchmarks.
- Trust only a gap that repeats across runs; one run per case flips.
- Score from each lens's raw report; the merge step can drop findings.
- Hold some cases back, and confirm each prompt change on one that contains the concept the
  line names; a held-out case without it shows only no regression.
- Before adding lines, run one critique agent over the raw reports of the misses: which line
  suppressed each, which lines to delete, at most 3 additions, each tied to one miss.

## Open items

- `Evidence:` issues use `maintenance`; no `evidence` label exists.
- Untried in practice: the light tier. Its first real use is its test; fix the skill from what
  goes wrong.
