---
name: dream-fixer
description: >-
  Takes one tracker issue from its number to an open MR/PR: reads and triages it, runs the
  dream-fixer-loop workflow, and opens the MR/PR from the result. Use when the user points at an
  issue by number and asks to work on, take, pick up, handle, do or close it — e.g. "work on
  #42", "do GL-88 end to end". Not for vague feature ideas with no issue (file one with
  scope-issue), and not for reviewing an existing PR (use qa-review).
argument-hint: <issue-number>
---

# dream-fixer

One issue per invocation. If the user names several, do them one at a time.

Spell `<scratchpad>` as your scratchpad directory's literal path.

You are the orchestrator. You read, triage, branch and ship. **You do not write the change** — the
workflow's implementer does. Everything between the branch and the MR happens in dispatched
agents. Your only edits are step 5's settled disputes and nits, which step 6 reruns
`gateCommands` on, a light-tier issue's edit, and a research issue's reusable note (step 2a).

**Lab work is yours, not the workflow's.** Workflow agents never ssh to a lab host. Anything the
issue or the repo's `CLAUDE.md` or `AGENTS.md` needs run on a lab host — a measurement the issue
asks for, a test that needs root, a perf gate — you dispatch after the workflow returns (step 5),
through `dream-team:lab-runner`. A light-tier issue has lab work only when it asks for a
measurement or its bug reproduces there (step 2a). No lab host named → there is no lab work. Say
so in the workflow's `notes` so the implementer does not try, and does not report it as an
assumption.

## 1. Read the issue

Fetch body, title, labels and discussion — `gh issue view <n> --json title,body,labels,comments`,
`glab issue view <n> --comments --output json -P 100`, or whatever the host's tooling skill says to
use instead.

A `Meta:` issue is not a work item. Pick an open child from its checklist with no open blocker,
say which, and run the rest of this skill on that child. None left → report it and stop.

## 2. Triage: is this actionable without the user?

Fail *before* code is written on a guess, not after. Triage blocks on:

- An open decision: anything the issue leaves to a guess — which screen or endpoint, what happens
  on failure, whether it needs a migration, a public API or schema change, product copy or
  acceptance criteria.
- A credential, environment or access you don't have.
- A `Blocked by #<n>` line naming an open issue.

Blocked at triage:

- Say exactly what is blocking and what you need.
- Don't half-build around the gap.
- Don't end the turn yet: do the reading that makes the choice answerable — what each option
  costs, how many call sites it touches, what the reference source does.

Then:

- **The options are enumerable** — two or three concrete paths, and the user's pick is the only
  thing missing: put them in an **AskUserQuestion** dialog, one option per path, cost in the
  description. Take the answer and carry straight on to step 3. Deferring the issue is an option
  when its tracker state says it is not due yet.
- **The options are not enumerable** — a missing acceptance criterion, a credential you don't
  have, an intent only the user knows: report what is blocking in prose and stop.

Never open a dialog whose options you had to invent to fill the slots.

## 2a. Tier

A tier the project's `CLAUDE.md` or `AGENTS.md` sets for the issue overrides the criteria below.

Research tier when the title starts `Research:` (below). Otherwise light tier when all hold;
otherwise full (step 3 on):

- No runtime behaviour change: docs, comments, help or usage text, CI config, test fixtures, or a
  rename. Or a bug fix you reproduced yourself before the edit: a lab probe or a test seen failing.
- The proposal names the exact edit, or the diff changes only docs, comments or help or usage
  text to match the code; no design choice left.
- A bug fix's edit copies a pattern the repo already uses, in under ~50 lines in one module.
- Touches no path the project's `CLAUDE.md` or `AGENTS.md` puts under a parity or perf gate,
  unless the change there is comments only.

Light path, no workflow:

- Branch per step 3.
- Make the edit inline.
- Run every `gateCommands` entry.
- Dispatch one reviewer with the issue and the base, told to read the diff with `git diff <base>`,
  its type picked below.
- A blocking finding → fix it inline and rerun `gateCommands`, or hand the branch back.
- A bug fix → rerun the reproduction on the branch head and see it pass.
- Run lab work only for that rerun or a measurement the issue asks for, per step 5's lab steps.
- Run step 5's docs drift check, unless the reviewer was `dream-team:docs-reviewer`.
- The diff outgrows the criteria → `git reset --hard <base>` and run the full loop.
- Open the MR per step 6.
- Report the tier and the criterion that allowed it.

Light-path reviewer type:

- Docs, comments, help or usage text only → `dream-team:docs-reviewer`.
- Anything else → `general-purpose`, told to check the diff against the reference sources and
  invariants the project's `CLAUDE.md` or `AGENTS.md` names, with the failing evidence for a bug
  fix.

Research tier: no workflow, no code. Answer the proposal's questions yourself, then:

- File one issue per gap per `scope-issue` with its milestone (step 5).
- Output a later task reuses (a baseline table, a rubric, a case list) → write that output as a
  note in the format below, commit it on the step-3 branch, and open the MR per step 6 with
  `Closes #<n>`.
- Post the other findings as one comment on the research issue, in the format below, the
  follow-up issues and any MR linked.
- No note → close the issue; skip step 3 and steps 6-7.

Findings format:

- A note's path: `docs/research/YYYY-MM-DD-<slug>.md`. A comment has no path line.
- Header: the title, then `**Date:** <date> · **Issues:** #<n>`.
- Context: 1-3 sentences on the setup and the versions or commits measured.
- One `##` per finding, named by its claim or topic; the answer in its first sentence.
- A finding left unresolved → `## Open: <claim>`, naming the issue that tracks it.
- Dead ends → one `## Ruled out` list.

## 3. Preflight and branch

Stop and report when either holds:

- `git status --porcelain` prints anything. The workflow's agents commit in this checkout.
- A branch `issue-<n>-*` exists locally or on the remote, or an open MR/PR references the issue.
  Ask whether to continue that work or start over.

Then `git fetch` and branch from the fetched tip of the MR target, the remote's default branch
unless the project's `CLAUDE.md` or `AGENTS.md` names another:
`git switch -c issue-<n>-<slug> origin/<target>`.
Never work on `master`/`main`.
Record `git rev-parse HEAD` — it is the workflow's `base`.

## 4. Run the workflow

Invoke the **Workflow** tool with `name: "dream-team:dream-fixer-loop"` and `args` as a real JSON
object (never a stringified one):

```json
{
  "issue": "42",
  "title": "<issue title>",
  "body": "<issue description, verbatim>",
  "notes": "<what the description does not carry>",
  "branch": "issue-42-slug",
  "base": "<sha from step 3>",
  "gateCommands": ["cargo build --workspace", "cargo test --workspace", "cargo clippy --workspace"],
  "externalReview": "<command, or leave out>"
}
```

- `notes`: decisions made in the tracker discussion, the answer the user gave at step-2 triage,
  and the lab work the implementer must leave alone. Optional.
- The change carries a decision that passes the test in
  [`reference/decision-record.md`](reference/decision-record.md) → name the decision in `notes`
  with that file's absolute path, and tell the implementer to add its record to `docs/decisions/`
  in that format, in the same commit as the change.
- `gateCommands`: the build, test and lint commands the repo's CI config runs that also run in this
  checkout — CI config first, `CLAUDE.md`, `AGENTS.md` and README second. The mechanical gate
  runs exactly these after the implementation and after every fix commit. Leave out lab work.
  Required.
- `externalReview`: a shell command that reads a diff on stdin and prints findings. Default unset.
- A `CLAUDE.md` the session loads — global, the project's, or its `CLAUDE.local.md` — opts in to an
  external reviewer → set `externalReview` to the command it names.
- The project's line and the global one disagree → the project's wins, including a project line
  that turns it off.

Then report, before the workflow returns:

- Two bullets, the label in bold: the branch, and whether `externalReview` is set.
- After them, 1-3 sentences on what the change builds, from the issue.

Layout:

```
- **Branch:** `issue-42-slug`
- **External reviewer:** `yes`|`no`

<1-3 sentences: what the change builds.>
```

## 5. Judge the result

The workflow returns structured, not final. Once it returns, read
[`reference/workflow-result.md`](reference/workflow-result.md): what each result field means and
what to do with it.

- **Lab steps** — once the result is `ok`, run the lab work on the branch head. Treat a lab failure
  like a red `gateCommands` run: fix it before the MR, or hand the branch back. Put measured
  numbers in the MR description.
- Before dispatching `dream-team:lab-runner`, tell the user its rough time to completion, from
  the run count and each run's expected length.

Docs drift, once the result is `ok`:

- Dispatch `dream-team:docs-reviewer`, told to read the diff with `git diff <base>..HEAD`, before
  your other step-5 edits.
- Make those edits while it runs.
- A 🔴/🟡 finding you judge wrong → drop it, as a settled dispute.
- 🔴/🟡 findings left → after your edits, dispatch `dream-team:docs-editor` in drift mode with
  `git diff <base>..HEAD` and only the pages they name.
- 🔵 findings → treat as nits.
- The editor's edits are step-5 changes: step 6 commits and gates them.

Adjacent defects — anything found outside the diff:

- A small fix with no open decision, no lab check and no design choice (docs drift, a config
  string, under ~20 lines) → commit it on the branch as its own change, never a `fixup!`.
- Any other research finding, review-panel survivor outside the diff, bug hit running evals or
  `gateCommands`, or spec consequence nobody owns → file it as an issue before the session
  ends, per the repo's own rules.
- The finding is a nit → file nothing.
- Filed → never leave the finding in the MR description or the chat summary.
- Filing fails or yields no issue link → name the defect in the report as unfiled, with the reason.

Every issue you open gets the milestone it belongs to, set at creation, and the host's waiting
label when that milestone has an open dependency. Pick the milestone from the tracker's open
milestones and the `planned` rows of the repo's roadmap (`ROADMAP.md` or `docs/ROADMAP.md`). A
`planned` row fits best → no milestone and the waiting label. None clearly fits → ask.

## 6. Open the MR/PR

Commit anything else you changed in step 5 as `fixup! <subject of the commit it repairs>`, one
fixup per commit an edit repairs. If you changed anything, run every `gateCommands` entry on the new
head yourself and carry on only when all exit 0. A red run → fix it, or hand the branch back.

Fold the branch to one commit per change. The implementer commits once per independent change;
the simplify cuts, build-fix and fix rounds add `fixup! <subject>` and `amend! <subject>`
commits, and a plain commit for a defect already on the base commit. Count the changes:

```sh
git log --format=%s <base>..HEAD | grep -Evc '^(fixup|amend)! '
```

More than `1` → fold each `fixup!` and `amend!` commit into the commit it names:

```sh
OLD=$(git rev-parse HEAD) && echo "$OLD" &&
  git -c sequence.editor=: rebase -i --autosquash <base> &&
  git diff --quiet "$OLD" HEAD &&
  ! git log --format=%s <base>..HEAD | grep -Eq '^(fixup|amend)! '
```

- Rebase stops on a conflict → `git rebase --abort`, fold to one commit as below, and say so in
  the report.
- After that fallback → amend the fold commit to add every other change's subject.
- A `fixup!` or `amend!` commit survives the rebase → `git reset --hard <the sha it printed>`,
  then stop and report its subject.

`1` → fold onto the last `amend!` commit's body, or else the first commit's message, in one Bash
call:

```sh
OLD=$(git rev-parse HEAD) && echo "$OLD" &&
  F=$(git rev-list --reverse <base>..HEAD | head -1) && [ -n "$F" ] &&
  A=$(git log --format='%H %s' <base>..HEAD | awk '$2 == "amend!" { print $1; exit }') &&
  { if [ -n "$A" ]; then git log -1 --format=%b "$A"; else git log -1 --format=%B "$F"; fi; } \
    > <scratchpad>/fold-msg &&
  git reset --soft <base> && git commit -F <scratchpad>/fold-msg &&
  git diff --quiet "$OLD" HEAD
```

- Load `scope-commit` before the fold commit or an amend.
- Amend the message when it breaks `scope-commit` or the fix rounds changed what the commit does.

After either fold, `git diff --quiet "$OLD" HEAD` non-zero → stop and report: the fold changed the
tree.

- `untrackedPaths` non-empty → list them to the user before you push.

Then push and open the MR/PR against the branch the project's `CLAUDE.md` or `AGENTS.md` names.

Link the issue so it auto-closes (`Closes #<n>`). Write the description review-facing; a `scope-mr`
skill, if present, is the source of truth for it.

## 7. Watch the MR/PR

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
- Three or more numbers compared across cases (variants, runs, before/after) → one table, a row
  per case, under its bold label; never a bullet.
- No blank line between bullets.
- Assumptions above the bullets → put a `**Notes:**` line between them.
- End with one plain line, after a blank line: `Work on #<n> is done: <MR/PR link>`.
- Research issue closed by its findings comment → end with `Work on #<n> is done: <comment link>`.
- Otherwise no MR/PR → end with `Work on #<n> is handed back: <branch> — <why>`.
- Name each `degraded` roster type, and each dead reviewer the hand-back `<why>` does not name.
- No MR/PR and `untrackedPaths` non-empty → list them under one bold label.
- Name each dispute you settled, which way, and why.
- Name each `resolved` entry, one line each.
- List each `questions` entry as a sub-bullet of one `**Questions:**` bullet, with its reviewer and
  location.
- Name each adjacent fix committed on the branch by its subject, one line each.
- Name each issue filed for an adjacent defect by its link, one line each, never the defect itself.
- Name each adjacent defect that could not be filed, and why, one line each.
- Say so when `redEvidence` is empty on a bug fix.
- Give a lab step one line: its verdict, or its numbers when there are fewer than three.
- Name each reviewer that could not check something, and the check you ran in its place.
- Stopped at triage → say what is blocking and stop there.
- Leave out nits, applied or dropped, and reviewer verdicts with no finding.
- Leave out `gateCommands` entries that passed and a summary of the change: the MR carries it.
- Leave out a present `redEvidence` and lab work that did not run.
- A review with no blocking finding, no question, no dispute and no fix round gets no line.
- Handed back → no line saying a reviewer found nothing or that nothing was disputed.
- The hand-back `<why>` clause names only what blocks; it never adds that other reviewers, rounds
  or disputes came back clean.

Layout, with sections that have nothing to report left out:

```
**Assumptions:**
- <assumption>

**Notes:**
- **Dispute accepted:** <finding> — <why>
- **Lab:** <verdict>
- **Questions:**
  - <question> — <reviewer>[, <file>]

**Lab, master vs branch:**

| Run | master | branch |
|---|---|---|
| <case> | <number> | <number> |

Work on #<n> is done: <MR/PR link>
```
