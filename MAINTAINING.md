# Maintaining dream-team

## Pieces and where they live

Rules, in each project `CLAUDE.md`: listed in `setup-dream-team`, which checks for them.

Skills:

- `scope-issue`: issue shape, including `Scout:`, `Evidence:` and
  `Meta:` issues and `Blocked by` lines.
- `dream-fixer`: one issue to one MR, with scout, light and full tiers;
  stops on an open blocker; on a `Meta:` issue, works one open unblocked child.
- `setup-dream-team`: checks a project against the flow, fixes the mechanical
  failures directly after one confirm, files one maintenance issue for the other failing checks.
- `cut-milestones`: milestones from a spec, one exit gate each, with the
  dependency order and ROADMAP rows; or one version milestone for a minor release.
- `milestone-close`: exit check with gap issues, triage, docs check, facts
  sweep, `CLAUDE.md` cuts and `CLAUDE.local.md` promotions.
- `scope-commit`, `scope-mr`: commit and MR text.
- `scope-spec`: the project spec and its template.

Agents:

- `architect-reviewer`: read-only design review of a diff or paths.
- `lab-runner`: lab-host work over ssh, every remote command in the
  foreground.
- `performance-engineer`: read-only performance review of a diff or paths.

Hooks:

- `jit-context.py`: injects git workflow, prose, changelog,
  lab, forge and `CLAUDE.md` rules at first use, `<upstream_repo>` on the first write or commit in
  a repo with a remote outside `DREAM_TEAM_OWN_REMOTES`, and `<project_notes>` at session start.
- `body-cap.py`: length caps on MRs and issues.
- `changelog-cap.py`: one-sentence CHANGELOG entries.
- `branch-guard.py`: no design doc on `main`/`master`.

A new hook is added only after its rule has failed once.

## Decisions and rejected options

Origin: one 1332-line spec that was hard to execute in parts. The issue-sized flow replaced it.
Planning stays explicit, at issue size, because you review every plan.

- Facts for the contributor doc are swept once per milestone by `milestone-close`. A prompt on
  every MR was rejected: it asks a question on MRs with nothing to keep.
- A rule comes first; a hook is added only after the rule has failed once.
- No global "issue-sized work gets no spec" rule: it duplicates the scope rules. The unreviewed,
  plan-like September specs came from a skill that has since been rewritten into `dream-fixer`.
- The upstream-repo guard lives in `jit-context.py`, not a tracker skill: that skill loads only
  before the tracker CLI and only on owned remotes, so it fires too late and on the wrong repos.
- A living doc stays small by holding current state only: rationale goes in commits and MRs,
  plans in issues, component internals nowhere beyond one module-doc sentence.
- Retired: the `dream-team` skill, `dream-team-loop` and `dream-team-run`. `dream-fixer`
  replaces them.
- ROADMAP status moved from each feature MR to `milestone-close`: status lags until the close,
  but concurrent MRs stop conflicting on it.
- Issue order comes from `Blocked by` lines, not a board ordering or a separate skill.
- Field evidence gets its own `Evidence:` issue rather than `milestone-close` collecting it
  unannounced: the deploy and its start date are written down before the clock starts.
- Work spanning milestones (full RFC 8914 coverage) is a `Meta:` issue, not a milestone (one
  exit gate cannot cover it) and not a per-item table in the repo (every MR would churn it). A
  closed child shows "(closed)" beside its mention; the box is ticked at `milestone-close`.
- A minor release is scope-based: one headline feature plus backlog, behind standing release
  criteria in the version milestone's `Gate:` bullet. One maintainer defines a release by its
  feature, not a date.
- A ROADMAP is required only when two or more milestones are open or one depends on another. With
  one rolling version milestone each row copied its `Exit:` and its status mirrored its open or
  closed state. Keying on `M<n>` names was rejected: a versioned project can plan several
  headline releases ahead.
- Release stays user-triggered ("tag v0.1"), not time-based. Pre-1.0, a project may opt in to
  a `v0.<n>.0` tag per milestone close: a version a user can find, without a release process.
- Milestones are `M<n>`, not a bare integer: "milestone 5" reads badly in prose and collides
  with counts ("all 5 sites"). One generic prefix beats a per-project codename; the repo name
  disambiguates the rare cross-project mention.
- Parallel milestones show readiness through the waiting label, not ROADMAP: the Board's
  default column is what can start now. `workflow::future`, not `workflow::blocked`: blocked means
  an external gate someone must chase; future clears itself when the dependency closes.
- A parked issue has no milestone and the waiting or blocked label, not a `Future` milestone: a
  milestone with no exit gate fails the naming, exit and ROADMAP checks and never closes. No
  milestone and no `workflow::` label stays the untriaged state the setup check flags.
- `setup-dream-team` files its remaining failing checks as one maintenance issue, not one issue
  per check: they are small tracker and doc edits, and one issue each added a branch, an MR and a
  `dream-fixer` run per edit.
- Issues are the log, docs the reference: a fact the code and paths don't show has one reference
  doc, updated in the MR that changes it. One large spec went stale and hard to skim; a closed
  issue is not a place anyone looks things up.
- No document per `area::` label. Folder names already say where things live; a per-label
  pointer list repeats them and rots on every rename. A topic doc exists only for what is not
  obvious from the tree.
- The component table is optional. Where folder names already say what each component does, a
  table restating them is a pointer list and rots like one. A project that keeps one gives each
  component a row and a note only where the name and path fall short.

## Building agents

Reviewer agents start from a voltagent agent and change only what an eval shows. Evals run in a
local harness kept out of the repo.

- Start from the voltagent body; cut its Communication Protocol, progress and delivery JSON,
  agent-integration list and process checklists (testing, monitoring, culture, capacity).
- Keep the domain keyword lists: they are the cues that give the agent its breadth. A rewrite of
  them into a few condensed rules missed more confirmed findings.
- Never add a rule that filters findings ("never a redesign", "no hot path → no finding", "runs
  once → skip", a mandatory caller chain, "review the diff file by file"); the verify pass gives
  precision.
- Add a line only for a miss seen in an eval, naming the missing concept, not a generic step
  ("read the library source" changed nothing).
- Make a reviewer read-only with its `tools` list plus two hard rules: no build, test, benchmark,
  install or network; no file edits.
- Never give Bash an allow-list of commands; it stops the agent reading library source.
- Never pin `effort:` in a shipped agent; pin it in the eval harness instead.
- Name the agent by role (`performance-engineer`); the role name is a cue too.
- Judge a change by A/B runs of old and new agent in the same run, on real regression commits
  with a later fix as ground truth, on haiku, sonnet and opus, followed by an opus verify pass.
- Score expected findings against the case's fix, not the verify verdict; the verify judge is
  unreliable on micro-performance without real benchmarks.
- Trust only a gap that repeats across runs; one run per case flips.
- Score from each lens's raw report; the merge step can drop findings.
- Hold some cases back, and confirm each prompt change on one of them.
- Before adding lines, run one critique agent over the raw reports of the misses: which line
  suppressed each, which lines to delete, at most 3 additions, each tied to one miss.

## Open items

- `Evidence:` issues use `type::maintenance`; no `type::evidence` label exists.
- Untried in practice: the scout tier and the light tier. The first real use of each is its
  test; fix the skill from what goes wrong.
