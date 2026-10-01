---
name: dream-fixer
description: >-
  Take one tracker issue from "here's the number" to "MR is open": read it, gate it, run the
  dream-fixer-loop workflow, and open the MR/PR from the result. Use whenever the user points at an
  issue by number and asks to work on / take / handle / do / close it — e.g. "work on #42", "take
  issue 123", "do GL-88 end to end", "pick up that issue and open an MR". Triggers on an issue
  number plus intent to resolve it, even when the user doesn't spell out the review or MR steps.
  Not for vague feature ideas with no issue (use brainstorming), and not for reviewing an existing
  PR (use review-pr).
argument-hint: <issue-number>
---

# dream-fixer

One issue per invocation. If the user names several, do them one at a time.

You are the orchestrator. You read, gate, roster, branch and ship. **You do not write the change** —
the workflow's implementer does. Everything between the branch and the MR happens in dispatched
agents. Your only edits are step 6's settled disputes and minor findings, which step 7 gates, a
light-tier issue's edit, and a scout issue's research note (step 2a).

**Lab work is yours, not the workflow's.** Workflow agents never ssh to a lab host. Anything the
issue or the repo's `CLAUDE.md` needs run on a lab host — a measurement the issue asks for, a test
that needs root, a perf gate — you dispatch after the workflow returns (step 6), through
`dream-team:lab-runner`. A light-tier issue has lab work only when it asks for a measurement,
its bug reproduces there, or it takes the infra path (step 2a). No lab host named → there is no
lab work. Say so in the workflow's `notes` so the implementer does not try, and does not report it
as an assumption.

## 1. Read the issue

Fetch body, title, labels and discussion — `gh issue view <n> --comments`, `glab issue view <n>
--comments`, or whatever the host's tooling skill says to use instead.

A `Meta:` issue is not a work item. Pick an open child from its checklist with no open blocker,
say which, and run the rest of this skill on that child. None left → report it and stop.

## 2. Gate: is this actionable without the user?

Fail *before* code is written on a guess, not after. An open decision is anything the issue
leaves to a guess: which screen or endpoint, what happens on failure, whether it needs a
migration, a public API or schema change, product copy or acceptance criteria. Two more cases
block here: a credential, environment or access you don't have, and a `Blocked by #<n>` line
naming an open issue.

Say exactly what is blocking and what you need. Don't half-build around the gap.

A blocked gate is not the end of the turn. Do the reading that makes the choice answerable — what
each option costs, how many call sites it touches, what the reference source does — then:

- **The options are enumerable** — two or three concrete paths, and the user's pick is the only
  thing missing: put them in an **AskUserQuestion** dialog, one option per path, cost in the
  description. Take the answer and carry straight on to step 3. Deferring the issue is an option
  when its tracker state says it is not due yet.
- **The options are not enumerable** — a missing acceptance criterion, a credential you don't
  have, an intent only the user knows: report what is blocking in prose and stop.

Never open a dialog whose options you had to invent to fill the slots.

## 2a. Tier

Scout tier when the title starts `Scout:` (below). Otherwise light tier when the small-change or
the infra criteria all hold; otherwise full (step 3 on).

Small-change criteria:

- No runtime behaviour change: docs, comments, help or usage text, CI config, test fixtures, or a
  rename. Or a bug fix you reproduced yourself before the edit: a lab probe or a test seen failing.
- The proposal names the exact edit, or the diff changes only docs, comments or help or usage
  text to match the code; no design choice left.
- A bug fix's edit copies a pattern the repo already uses, in under ~50 lines in one module.
- Touches no path the project's `CLAUDE.md` puts under a parity or perf gate, unless the change
  there is comments only.

Infra criteria:

- The project's `CLAUDE.md` opts in to the infra light tier, and it or `CLAUDE.local.md` names a
  lab host.
- The change is infrastructure as code: config-management roles, templates, inventory vars, or
  alert rules.
- The issue names every component the change touches.
- No design choice is left once the issue, its discussion and the step-2 answers are read.
- Changes no SPEC or contract and no path shared with another independently deployed system.
- Adds no runtime dependency between systems.

Light path: step 4, then make the edit inline, then every `gateCommands` entry. Infra path → run
the lab steps now: converge, a second check run showing no changes, then the issue's done-check.
Then dispatch the reviewers with the issue and the diff:

- Docs, comments, help or usage text only → `gdoc-writer`, review-only.
- Infra path → the step-3 domain reviewer and `pr-review-toolkit:silent-failure-hunter`, in
  parallel, with the lab output.
- Anything else → the step-3 domain reviewer type, with the failing evidence for a bug fix.
- Type not in the catalog → `generic`.

A blocking finding → fix it inline and rerun the gates, or hand the branch back. A bug fix → rerun
the reproduction on the branch head and see it pass. An infra fix → rerun the lab steps. Other lab
work only for that rerun or a measurement the issue asks for, per step 6's lab steps. Then step 7.
No workflow. Diff outgrows the small-change criteria → `git reset --hard <base>` and run the full
loop. Infra edit needs a file or component the issue does not name → the same. Report the tier
and the criterion that allowed it.

Scout tier: no workflow, no code; the research note is the one change you write. Answer the
proposal's questions yourself within its time box. Write the answers as a note in the repo's
research docs, file one issue per gap per `scope-issue` with its milestone (step 6), then commit
the note on the step-4 branch and open the MR per step 7 with `Closes #<n>`, the follow-up issues
linked.

## 3. Pick the roster

Two slots, both from the Agent tool list in your context — that list is the catalog, and a type not
in it fails at dispatch.

- **Implementer**: the specialist whose domain matches the issue. No obvious fit → `generic`. The
  type must have Bash: it commits and runs tests. A fitting specialist without Bash → make it the
  domain reviewer and implement with `generic`.
- **Domain reviewer**: the lens the build and test suite cannot check — the project's own rules,
  reference sources and invariants. **MUST be a different type than the implementer**; if the
  catalog has no second specialist for the domain, use `generic`.

Override the pick when you know better than the catalog descriptions.

The quality reviewers are not your choice: the workflow picks them.

## 4. Preflight and branch

Stop and report when either holds:

- `git status --porcelain` prints anything. The workflow's agents commit in this checkout.
- A branch `issue-<n>-*` exists locally or on the remote, or an open MR/PR references the issue.
  Ask whether to continue that work or start over.

Then `git fetch` and branch from the fetched tip of the MR target, the remote's default branch
unless the project's `CLAUDE.md` names another: `git switch -c issue-<n>-<slug> origin/<target>`.
Never work on `master`/`main`.
Record `git rev-parse HEAD` — it is the workflow's `base`.

## 5. Run the workflow

Invoke the **Workflow** tool with `name: "dream-team:dream-fixer-loop"` and `args` as a real JSON
object (never a stringified one):

```json
{
  "issue": "42",
  "title": "<issue title>",
  "body": "<issue description, verbatim>",
  "notes": "<what the description does not carry>",
  "branch": "issue-42-slug",
  "base": "<sha from step 4>",
  "gateCommands": ["cargo build --workspace", "cargo test --workspace", "cargo clippy --workspace"],
  "implementer": "<catalog type or generic>",
  "domainReviewer": "<catalog type or generic>",
  "verify": false
}
```

- `notes`: decisions made in the tracker discussion, the answer the user gave at the step-2 gate,
  and the lab work the implementer must leave alone. Optional.
- `gateCommands`: the build, test and lint commands the repo's CI config runs that also run in this
  checkout — CI config first, `CLAUDE.md` and README second. The mechanical gate runs exactly
  these after the implementation and after every fix commit. Leave out lab work. Required.
- `verify`: `true` or `false`; runs Claude Code's `/verify` as a Review gate. Default `false`.
- The repo's `CLAUDE.md` opts in to `/verify` → set `verify` to `true`.

Report the branch, the implementer and the domain reviewer by type name, no prose — the roster is
the one thing the user cannot read off `/workflows`. Three lines, the label in bold:

```
- **Branch:** `issue-42-slug`
- **Implementer:** `<type>`
- **Domain reviewer:** `<type>`
```

## 6. Judge the result

The workflow returns structured, not final. Read it and decide:

- **`ok: false` with `handBack: true`** — blocking findings survived. `reason` says which case:
  - *Fix rounds ran out.* Do not open an MR. Report the outstanding findings and hand the branch
    back.
  - *The fixer disputed every finding and the reviewers held.* Settle each entry in `disputes`
    yourself, per the `disputes` bullet below. With every entry in `blocking` settled and
    `deadReviewers` empty, carry on to the lab steps and step 7; otherwise hand the branch back.
  - `deadReviewers` non-empty → those reviewers returned nothing on every try. Do not open the MR;
    hand the branch back.
- **`ok: false` otherwise** — the implement, verify, simplify or fix stage failed. Report the
  reason; the branch is where the agent left it.
- **`degraded`** — roster types that were not dispatchable and ran as a generic agent instead,
  `ponytail:ponytail-review` when that skill was missing and the Simplify phase was skipped, and
  `verify` when `claude` or its `/verify` was missing and the `/verify` gate was skipped.
- **`simplify`** — the over-engineering cuts made before review: `applied`, `disputed` with the
  implementer's reason, and `net`, the review's estimate of lines that could go. Put applied cuts in
  the MR description, and `net` only when nothing was disputed; treat a disputed cut like a minor
  finding. `unhandled` counts cuts the implementer neither applied nor disputed; above 0 → say so in
  the MR description. `null` → the phase was skipped.
- **`verifyRun`** — the last `/verify` gate run: `verdict`, `command`, `output`, `reason`,
  `recipePath`. `null` → the gate did not run, or was skipped (see `degraded`). A FAIL was a blocking finding for the fix loop.
  - `PASS` → put its `command` and `output` in the MR description.
  - `BLOCKED` and its `reason` needs the lab → run it as a lab step through `dream-team:lab-runner`.
  - `BLOCKED` otherwise → name the verdict and its `reason` in the report.
  - `SKIP` → name the verdict and its `reason` in the report.
  - `recipePath` non-empty → never commit the recipe on the branch; report its path for the user
    to copy to `.claude/skills/verify/SKILL.md` and commit separately.
- **`disputes`** — the fixer refused a finding and gave evidence. Check it yourself. The fixer may
  be right; it may also be rationalizing. Apply the fix or accept the dispute.
- **`resolved`** — blocking findings a fix round fixed, each with its gate and round.
- **`minorFindings`** — never auto-fixed. Apply the ones worth applying, drop the rest.
- **`assumptions`** — anything the implementer had to invent.
- **`redEvidence`** — the new test's failing output from before the fix; the test reviewer checked
  it. Empty on a bug-fix issue means nobody saw the test fail.
- **Lab steps** — once the result is `ok`, run the lab work on the branch head. A lab failure is a
  failed verify: fix it before the MR, or hand the branch back. Put measured numbers in the MR
  description.

Adjacent defects — anything found outside the diff:

- A scout finding, a review-panel survivor outside the diff, a bug hit running evals or gates, or
  a spec consequence nobody owns → file it as an issue before the session ends, per the repo's
  own rules.
- The finding is a minor nit → file nothing.
- Filed → never leave the finding in the MR description or the chat summary.
- Filing fails or yields no issue link → name the defect in the report as unfiled, with the reason.

Every issue you open gets the milestone it belongs to, set at creation, and the host's waiting
label when that milestone has an open dependency. Pick the milestone from the repo's
roadmap milestone table (`ROADMAP.md` or `docs/ROADMAP.md`); no roadmap → the tracker's open
milestones. None clearly fits → ask.

## 7. Open the MR/PR

Commit anything you changed in step 6. If you changed anything, run every `gateCommands` entry on
the new head yourself and carry on only when all exit 0; a red gate is a failed verify.

Fold the branch to one commit. The workflow leaves the implementer's commit plus one for any
simplify cuts and one per build-fix and fix round, and one issue is one commit:

```sh
OLD=$(git rev-parse HEAD)
FIRST=$(git rev-list --reverse <base>..HEAD | head -1)
git reset --soft <base> && git commit -C "$FIRST"
git diff --quiet "$OLD" HEAD
```

Last line non-zero → stop and report: the fold changed the tree. Amend the message when the fix
rounds changed what the commit does.

Then push and open the MR/PR against the branch the project's `CLAUDE.md` names.

Link the issue so it auto-closes (`Closes #<n>`). Write the description review-facing; a `scope-mr`
skill, if present, is the source of truth for it.

## 8. Watch the MR/PR

Once the MR/PR is open, start a Bash `run_in_background` poll that exits on a final state,
`merged` or `closed` — never on "not open": GitLab reports a transient `locked` while it merges.
Poll every 30s through the host's tooling skill, e.g.:

```sh
until s=$(glab api "projects/<p>/merge_requests/<iid>" | jq -r .state)
      [ "$s" = merged ] || [ "$s" = closed ]; do
  sleep 30
done
```

Give the report (below) without waiting for the poll, and leave the poll out of it. When it
exits:

- **Merged** → `git switch <target> && git pull --ff-only && git branch -d issue-<n>-<slug>`,
  then check the issue closed. Report one line: new `<target>` head, branch deleted, issue state.
- **Closed unmerged** → report it; leave the branch.

## Report back

The report carries only what the user must know or act on.

- Open with every `assumptions` entry that no written rule or instruction settles, as its own list
  under a `**Assumptions:**` heading.
- Put nothing else under that heading.
- Every other item is one bullet with a bold label, e.g. `**Dispute accepted:**`, `**Lab:**`.
- No blank line between bullets.
- Assumptions above the bullets → put a `**Notes:**` line between them.
- End with one plain line, after a blank line: `Work on #<n> is done: <MR/PR link>`.
- No MR/PR → end with `Work on #<n> is handed back: <branch> — <why>`.
- Name each `degraded` roster type, and each dead reviewer the hand-back `<why>` does not name.
- Name each dispute you settled, which way, and why.
- Name each `resolved` entry, one line each.
- Name each issue filed for an adjacent defect by its link, one line each, never the defect itself.
- Name each adjacent defect that could not be filed, and why, one line each.
- Say so when `redEvidence` is empty on a bug fix.
- Give a lab step one line: its measured numbers, or its verdict when it measured none.
- Give a `verifyRun` SKIP, or a BLOCKED that no lab step ran, one line: the verdict and its `reason`.
- Give a non-empty `verifyRun.recipePath` one `**Verify recipe:**` bullet: the path only, never
  the contents.
- Name each reviewer that could not check something, and the check you ran in its place.
- Stopped at the gate → say what is blocking and stop there.
- Leave out minor findings, applied or dropped, and reviewer verdicts with no finding.
- Leave out gate commands that passed and a summary of the change: the MR carries it.
- Leave out a present `redEvidence` and lab work that did not run.
- A review with no blocking finding, no dispute and no fix round gets no line.
- Handed back → no line saying a reviewer found nothing or that nothing was disputed.
- The hand-back `<why>` clause names only what blocks; it never adds that other reviewers, rounds
  or disputes came back clean.

Layout, with sections that have nothing to report left out:

```
**Assumptions:**
- <assumption>

**Notes:**
- **Dispute accepted:** <finding> — <why>
- **Lab:** <measured numbers>

Work on #<n> is done: <MR/PR link>
```
