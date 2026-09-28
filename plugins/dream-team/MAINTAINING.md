# Maintaining dream-team

## Pieces and where they live

Rules, in each project `CLAUDE.md`: listed in `align-project`, which checks for them.

Skills:

- `scope-issue` (scope-style plugin): issue shape, including `Scout:`, `Evidence:` and
  `Meta:` issues and `Blocked by` lines.
- `dream-fixer` (dream-team plugin): one issue to one MR, with scout, light and full tiers;
  stops on an open blocker; on a `Meta:` issue, works one open unblocked child.
- `align-project` (dream-team plugin): checks a project against the flow, files one issue per
  failing check.
- `cut-milestones` (dream-team plugin): milestones from a spec, one exit gate each, with the
  dependency order and ROADMAP rows; or one version milestone for a minor release.
- `milestone-close` (dream-team plugin): exit check with gap issues, triage, docs check, facts
  sweep, `CLAUDE.md` cuts and `CLAUDE.local.md` promotions.
- `scope-commit`, `scope-mr`: commit and MR text.

Agents:

- `lab-runner` (dream-team plugin): lab-host work over ssh, every remote command in the
  foreground.

Hooks, in the dream-team and scope-style plugins:

- `jit-context.py` (dream-team): injects git workflow, prose, spec, changelog, lab, forge and
  `CLAUDE.md` rules at first use, `<upstream_repo>` on the first write or commit in a repo with a
  remote outside `DREAM_TEAM_OWN_REMOTES`, and `<project_notes>` at session start.
- `body-cap.py` (scope-style): length caps on commits, MRs and issues.
- `changelog-cap.py` (dream-team): one-sentence CHANGELOG entries.
- `branch-guard.py` (dream-team): no design doc on `main`/`master`.

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
  criteria in ROADMAP. One maintainer defines a release by its feature, not a date.
- Release stays user-triggered ("tag v0.1"), not time-based.
- Milestones are `M<n>`, not a bare integer: "milestone 5" reads badly in prose and collides
  with counts ("all 5 sites"). One generic prefix beats a per-project codename; the repo name
  disambiguates the rare cross-project mention.

## Open items

- `Evidence:` issues use `type::maintenance`; no `type::evidence` label exists.
- Untried in practice: the scout tier and the light tier. The first real use of each is its
  test; fix the skill from what goes wrong.
