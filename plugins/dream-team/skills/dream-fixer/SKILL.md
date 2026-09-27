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
argument-hint: <issue-number> [fix-rounds]
---

# dream-fixer

One issue per invocation. If the user names several, do them one at a time.

You are the orchestrator. You read, gate, roster, branch and ship. **You do not write the change** —
the workflow's implementer does. Everything between the branch and the MR happens in dispatched
agents. Your only edits are step 6's settled disputes and minor findings, which step 7 gates, and a
scout issue's research note (step 2a).

**Lab work is yours, not the workflow's.** Workflow agents never ssh to a lab host. Anything the
issue or the repo's `CLAUDE.md` needs run on a lab host — a measurement the issue asks for, a test
that needs root, a perf gate — you dispatch after the workflow returns (step 6), through
`dream-team:lab-runner`. No lab host named → there is no lab work. Say so in the workflow's `notes`
so the implementer does not try, and does not report it as an assumption.

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

Scout tier when the title starts `Scout:` (below). Otherwise light tier when all hold; otherwise
full (step 3 on):

- No runtime behaviour change: docs, comments, CI config, test fixtures, or a rename.
- The proposal names the exact edit; no design choice left.
- Not a bug fix — a bug fix needs a test seen failing, which only the full loop checks.
- Touches no path the project's `CLAUDE.md` puts under a parity or perf gate.

Light path: step 4, then one `caveman:cavecrew-builder` agent (`general-purpose` when that type is
not in your Agent list) with the issue body, then every
`gateCommands` entry yourself, then step 7. No workflow, no reviewers. Diff outgrows the criteria →
`git reset --hard <base>` and run the full loop. Report the tier and the criterion that allowed it.

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

Then `git fetch` and branch from the fetched tip of the branch the project's `CLAUDE.md` names as
the MR target: `git switch -c issue-<n>-<slug> origin/<target>`. Never work on `master`/`main`.
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
  "fixRounds": 3
}
```

- `notes`: decisions made in the tracker discussion, the answer the user gave at the step-2 gate,
  and the lab work the implementer must leave alone. Optional.
- `gateCommands`: the build, test and lint commands the repo's CI config runs that also run in this
  checkout — CI config first, `CLAUDE.md` and README second. The mechanical gate runs exactly
  these after the implementation and after every fix commit. Leave out lab work. Required.
- `fixRounds` (default 3, the skill's second argument) is the review fix-loop budget.

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
    back. When the user wants more rounds, relaunch with `resumeFromRunId: <runId>` and the same
    args except a higher `fixRounds`: finished stages return from cache and only the new rounds
    run. Same session only. Change no other arg. Never relaunch without `resumeFromRunId`.
  - *The fixer disputed every finding and the reviewers held.* Settle each entry in `disputes`
    yourself, per the `disputes` bullet below. With every entry in `blocking` settled and
    `deadReviewers` empty, carry on to the lab steps and step 7; otherwise hand the branch back.
  - `deadReviewers` non-empty → those reviewers returned nothing on every try. Do not open the MR;
    hand the branch back.
- **`ok: false` otherwise** — the implement, verify or fix stage failed. Report the reason; the
  branch is where the agent left it.
- **`degraded`** — roster types that were not dispatchable and ran as a generic agent instead.
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

Findings outside the diff are not this MR's job. File each as an issue before the session ends, per
the repo's own rules.

Every issue you open gets the milestone it belongs to, set at creation. Pick it from the repo's
roadmap milestone table (`ROADMAP.md` or `docs/ROADMAP.md`); no roadmap → the tracker's open
milestones. None clearly fits → ask.

## 7. Open the MR/PR

Commit anything you changed in step 6. If you changed anything, run every `gateCommands` entry on
the new head yourself and carry on only when all exit 0; a red gate is a failed verify.

Fold the branch to one commit. The workflow leaves the implementer's commit plus one per build-fix
and fix round, and one issue is one commit:

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

- Open with every entry of `assumptions` as its own list under a `**Assumptions:**` heading.
- Put nothing else under that heading.
- Every other item is one bullet with a bold label, e.g. `**Dispute accepted:**`, `**Lab:**`.
- No blank line between bullets.
- Assumptions above the bullets → put a `**Notes:**` line between them.
- End with one plain line, after a blank line: `Work on #<n> is done: <MR/PR link>`.
- No MR/PR → end with `Work on #<n> is handed back: <branch> — <why>`.
- Name each `degraded` roster type and each dead reviewer.
- Name each dispute you settled, which way, and why.
- Name each `resolved` entry, one line each.
- Say so when `redEvidence` is empty on a bug fix.
- Give a lab step one line: its measured numbers, or its verdict when it measured none.
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
