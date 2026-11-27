---
name: craft-it
description: >-
  Takes one issue from its number to an open MR/PR: reads it from the tracker, or from a local
  issue file in a clone not marked own, triages it, runs the craft-it-loop workflow, and opens
  the MR/PR from the result. Use when the user points at an issue by number and asks to work on,
  take, pick up, handle, do or close it — e.g. "work on #42", "do GL-88 end to end". Not for
  vague feature ideas with no issue (use brainstorm), and not for reviewing an existing PR (use
  qa-review).
argument-hint: <issue-number>
---

# craft-it

One issue per invocation. If the user names several, do them one at a time.

Spell `<scratchpad>` as your scratchpad directory's literal path.

You are the orchestrator. You read, triage, branch and ship. **You do not write the change** — the
workflow's implementer does. Everything between the issue branch and the MR happens in dispatched
agents, except the subagent loop's gate runs, which are yours. Your only edits are step 5's
settled disputes and small adjacent fixes, which step 6 reruns `gateCommands` on, a
light-tier issue's edit with its decision record, and a research note the user asks for (step
2a).

**Lab work is yours, not the workflow's.** Loop agents, from the workflow or the subagent loop,
never ssh to a lab host. Anything the issue or the repo's `CLAUDE.md` or `AGENTS.md` needs run on
a lab host — a measurement the issue asks for, a test that needs root, a perf gate — you dispatch
after the workflow returns (step 5), through `dream-team:lab-runner`. A light-tier issue has lab work only when it asks for a
measurement or its bug reproduces there (step 2a). No lab host named → there is no lab work. Say
so in the workflow's `notes` so the implementer does not try, and does not report it as an
assumption.

- `git config --local --type=bool --get dream-team.own` prints anything but `true` → read, triage,
  comment on, file and close issues, and push and open the MR/PR, per `.dream-team/TRACKER.md` in
  the main checkout (step 3).
- `dream-team.own` prints anything but `true` and that file does not exist → stop with "run
  `setup-dream-team` first".
- `dream-team.own` prints anything but `true` → write in the workflow's `notes`: "commits cite
  no issue: no `Closes` line, no `#<n>`".
- `dream-team.own` prints `true` → take the decision-record and ROADMAP paths, their naming and
  the record template from `docs/CONVENTIONS.md`.
- `dream-team.own` prints anything but `true` → take them from the upstream's `CLAUDE.md`,
  `AGENTS.md` or existing records folder.
- `dream-team.own` prints anything but `true` and none of those names a records path → write no
  record.

- When the host supplies no scratchpad → create one temporary directory for this run.
- For an AskUserQuestion step → use the host's user-input tool when available.
- Without a user-input tool → ask the same questions in chat and wait for the reply.

## Harness tools

- On Claude Code without Workflow → read [Claude Code tools](claude-code-tools.md).
- On Codex CLI → read [Codex CLI tools](codex-tools.md).
- On pi → read [pi tools](pi-tools.md).
- On OpenCode → read [OpenCode tools](opencode-tools.md).
- On another harness without a skill loader → read the advertised `SKILL.md` for skill lookup.
- Without a named Dream Team role → use the `role-fallback.md` file in qa-review's base
  directory, beside its advertised `SKILL.md`.
- For a reviewer outside Claude Code → dispatch per the host lines at the top of qa-review's
  advertised `SKILL.md`.

## 1. Read the issue

Fetch body, title, labels and discussion — `gh issue view <n> --json title,body,labels,comments`,
`glab issue view <n> --comments --output json -P 100`, or whatever the host's tooling skill says to
use instead.

- A `Meta:` issue is not a work item → stop with "run `assemble-meta #<n>` for all its children,
  or `craft-it #<child>` for one".

## 2. Triage: is this actionable without the user?

Fail *before* code is written on a guess, not after.

- `dream-team.own` prints `true` → load `triage-issue` as a reference without running it.
- `dream-team.own` prints `true` and the issue is untriaged per the `untriaged.md` file in
  triage-issue's base directory → stop with "run `triage-issue #<n>` first".
- The issue has the `workflow::needs-brainstorm` label → stop
  with "run `triage-issue #<n>` first".
- The issue says a decision gets a decision record, `dream-team.own` prints `true` and
  `docs/CONVENTIONS.md` does not exist → stop with "run `setup-dream-team` first".

Triage blocks on:

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
  description. Handle the answer as below, then carry straight on to step 3.
  Deferring the issue is an option when its tracker state says it is not due yet.
- **The options are not enumerable** — a missing acceptance criterion, a credential you don't
  have, an intent only the user knows: report what is blocking in prose and stop.

Never open a dialog whose options you had to invent to fill the slots.

The answer:

- Post it as a comment on the issue.
- Changes the work remaining → write it into the proposal and its `## Done when` section, or
  into a new issue that supersedes this one when the title or problem no longer holds
  (`scope-issue` Updates and Decisions).

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
- The issue says a decision gets a decision record, it has none yet and the top of this skill
  gives a record path → write the record at that path, in that template, in the edit's commit.
- Run every `gateCommands` entry.
- Dispatch one reviewer with the issue and the base, told to read the diff with `git diff <base>`,
  its type picked below.
- A blocking finding → fix it inline and rerun `gateCommands`, or hand the branch back.
- A bug fix → rerun the reproduction on the branch head and see it pass.
- Run lab work only for that rerun or a measurement the issue asks for, per step 5's lab steps.
- Run step 5's docs drift check, unless the reviewer was `dream-team:docs-reviewer`.
- Settle the reviewer's questions per step 5.
- The diff outgrows the criteria → `git reset --hard <base>` and run the full loop.
- Open the MR per step 6.
- Report the tier and the criterion that allowed it.

Light-path reviewer type:

- Docs, comments, help or usage text only → `dream-team:docs-reviewer`.
- Anything else → `general-purpose`, told to check the diff against the reference sources and
  invariants the project's `CLAUDE.md` or `AGENTS.md` names, with the failing evidence for a bug
  fix.

Research tier: no workflow, no code. Answer the proposal's questions yourself, then:

- File the gaps per `scope-issue`, each issue with its milestone (step 5).
- The user asks for a file → write the findings as a note in the format below, commit it on the
  step-3 branch, and open the MR per step 6 with `Closes #<n>`.
- Post every finding not in a note as one comment on the research issue, in the format below, the
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

Run this step from the main checkout, the first `worktree` path `git worktree list --porcelain`
prints; `cd` there first.

Stop and ask whether to continue that work or start over when any holds:

- A branch `issue-<n>-*` exists locally or on the remote.
- A path `.claude/worktrees/issue-<n>-*` exists.
- An open MR/PR references the issue.

Then `git fetch` and add a worktree on a new branch from the fetched tip of the MR target, the
remote's default branch unless the project's `CLAUDE.md` or `AGENTS.md` names another:
`git worktree add -b issue-<n>-<slug> .claude/worktrees/issue-<n>-<slug> origin/<target>`.

- `$(git rev-parse --git-common-dir)/info/exclude` has no `.claude/worktrees/` line → append
  `/.claude/worktrees/` before the `worktree add`.
- A gitignored path the issue, the Meta issue's children, `CLAUDE.md` or `AGENTS.md` names as an
  input → after the `worktree add`, symlink it from the main checkout to the same path in the
  worktree.
- `$(git rev-parse --git-common-dir)/info/exclude` has no line for a linked path → append the
  path, with no trailing slash.
- `cd` into the worktree.
- Run `cd <worktree's absolute path>` as the Bash call right before the Workflow call or
  subagent-loop stage 1.
- Never work on `master`/`main`.
- Record `git rev-parse HEAD` in the worktree — it is the workflow's `base`.

## 4. Run the workflow

- **Workflow** tool in this session → invoke it with `name: "dream-team:craft-it-loop"` and `args`
  as a real JSON object (never a stringified one).
- No Workflow tool → run the loop yourself with the same `args`, per
  [`subagent-loop.md`](subagent-loop.md).

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
- Each path step 3 linked → name it in `notes` with "never commit or modify it".
- The issue, or a step-2 answer written into it, says a decision gets a decision record, it has
  none yet and the top of this skill gives a record path → name the decision in `notes` with the
  absolute path of `docs/CONVENTIONS.md`, or of the upstream file or folder the path came from,
  and tell the implementer to add its record per that source, in the same commit as the change.
- `gateCommands`: the build, test and lint commands the repo's CI config runs that also run in this
  checkout — CI config first, `CLAUDE.md`, `AGENTS.md` and README second. The mechanical gate
  runs exactly these after the implementation and after every fix commit. Leave out lab work.
  Required.
- `externalReview`: a shell command that reads a diff on stdin and prints findings, then a last
  line of `VERDICT: CLEAN` or `VERDICT: FINDINGS`. Default unset.
- The opt-in is an `External reviewer:` line in `AGENTS.md` or `CLAUDE.md`.
- Include the global and project `AGENTS.md` or `CLAUDE.md` and the corresponding ignored local
  notes when resolving the opt-in.
- The project's line and the global one disagree → the project's wins, including a project line
  that turns it off.
- The selected opt-in reads `External reviewer: codex` on any host but Codex CLI → set
  `externalReview` to the first command below.
- The selected opt-in reads `External reviewer: codex` on Codex CLI → set `externalReview` to the
  second command below.
- The selected opt-in supplies a custom shell command → set `externalReview` to that command.

```sh
codex --ask-for-approval never exec --sandbox read-only --ephemeral \
  'Review the diff on stdin. Tag each finding [critical], [important], [nit] or [question]
  and give its file and line. End with the last line exactly VERDICT: CLEAN or VERDICT: FINDINGS.'
```

```sh
claude -p 'Review the diff on stdin. Tag each finding [critical], [important], [nit] or [question]
  and give its file and line. End with the last line exactly VERDICT: CLEAN or VERDICT: FINDINGS.' \
  --strict-mcp-config --setting-sources project --disable-slash-commands --tools Read,Grep,Glob
```

Then report, before the workflow returns or subagent-loop stage 1 starts:

- Two bullets, the label in bold: the branch, and whether `externalReview` is set.
- After them, 1-2 sentences on what the change builds, from the issue.
- Nothing before the bullets or after the sentences.

Layout:

```
- **Branch:** `issue-42-slug`
- **External reviewer:** `yes`|`no`

<1-2 sentences: what the change builds.>
```

## 5. Judge the result

The loop's result, the Workflow return or `<scratchpad>/craft-it-result.json`, is structured,
not final. Once you have it, read
[`workflow-result.md`](workflow-result.md): what each result field means and
what to do with it.

- **Lab steps** — once the result is `ok`, run the lab work on the branch head. Treat a lab failure
  like a red `gateCommands` run: fix it before the MR, or hand the branch back. Put measured
  numbers in the MR description, or in the hand-back comment when no MR opens.
- Before dispatching `dream-team:lab-runner`, tell the user its rough time to completion, from
  the run count and each run's expected length.
- Post the disputes you settle, each with which way and why, in one comment on the issue.

Docs drift, once the result is `ok`:

- Dispatch `dream-team:docs-reviewer`, told to read the diff with `git diff <base>..HEAD`, before
  your other step-5 edits.
- Make those edits while it runs.
- A 🔴/🟡 finding you judge wrong → drop it, as a settled dispute.
- 🔴/🟡 findings left → after your edits, dispatch `dream-team:docs-editor` in drift mode with
  `git diff <base>..HEAD` and only the pages they name.
- 🔵 findings → take no action.
- ❓ findings → settle them with the result's questions, below.
- The editor's edits are step-5 changes: step 6 commits and gates them.

Questions — `questions`, `preExisting` entries with severity `question`, and the docs reviewer's
❓ findings — on a result that carries on to step 6, settle each before step 6:

- The code, the issue, the spec or a project rule settles it → answer it yourself and drop it.
- Ask the rest per step 2's reading, enumerable and non-enumerable rules, in one batch: one
  `AskUserQuestion` call, or several in the same turn past its 4-question limit.
- A question with no enumerable options → stop before any comment or push; the user's reply
  resumes these steps as its answer.
- An answer that changes the code → once `dream-team:docs-editor` has returned, commit your
  step-5 edits per step 6, then dispatch one `general-purpose` agent with the answer, the worktree
  path and the base, told to make the change and commit only its own edit as
  `fixup! <subject of the commit it changes>`.
- No new `fixup!` in `git log <base>..HEAD` once it returns → hand the branch back, the question
  open.
- An answer that is issue-sized → file it per `scope-issue`, as below; the MR/PR goes ahead.
- Post every question, with its answer and who gave it, in one comment on the issue.
- A hand-back asks nothing.

Adjacent defects — anything found outside the diff or returned in `preExisting`:

- A small fix with no open decision, no lab check and no design choice (docs drift, a config
  string, under ~50 lines) → commit it on the branch as its own change, never a `fixup!`.
- Any other research finding, review-panel survivor outside the diff or in `preExisting`, bug hit
  running evals or `gateCommands`, or spec consequence nobody owns → file it per `scope-issue`
  before the session ends, and per the repo's own rules.
- The finding is a nit → file nothing.
- Filed → never leave the finding in the MR description or the chat summary.
- Filing fails or yields no issue link → name the defect in the report as unfiled, with the reason.

Every issue you open gets the milestone it belongs to, set at creation, and `workflow::future`
when that milestone has an open dependency. Pick the milestone from the tracker's open
milestones and the `planned` rows of the repo's ROADMAP, at the path the top of this skill gives.
A `planned` row fits best → no milestone and `workflow::future`. None clearly fits → ask.

- The top of this skill gives no ROADMAP path → pick from the tracker's open milestones only.

## 6. Open the MR/PR

Commit anything else you changed in step 5 as `fixup! <subject of the commit it repairs>`, one
fixup per commit an edit repairs. If you or step 5's agent changed anything, run every
`gateCommands` entry on the new head yourself and carry on only when all exit 0. A red run → fix
it, or hand the branch back.

Fold the branch to one commit per change. The implementer commits once per independent change;
build-fix and fix rounds add `fixup! <subject>` and `amend! <subject>` commits, and a plain
commit for a defect already on the base commit. Count the changes:

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

Link the issue so it auto-closes (`Closes #<n>`). Write the description per `scope-mr`.

## 7. Watch the MR/PR

Once the MR/PR is open, start a Bash `run_in_background` poll that exits on a final state,
`merged` or `closed`, or when the pipeline for the MR/PR head finishes — never on "not open":
GitLab reports a transient `locked` while it merges. Poll every 30s through the host's tooling
skill, e.g.:

```sh
h=$(git rev-parse HEAD)
until s=$(glab api "projects/<p>/merge_requests/<iid>" | jq -r .state) &&
      p=$(glab api "projects/<p>/merge_requests/<iid>/pipelines" |
        jq -r --arg h "$h" 'map(select(.sha == $h))[0].status')
      [ "$s" = merged ] || [ "$s" = closed ] || [ "$p" = success ] || [ "$p" = failed ]; do
  sleep 30
done
echo "$s $p"
```

- GitHub → state from `gh pr view <n> --json state`, pipeline from `gh run list --commit "$h"
  --json status,conclusion`: finished once it lists runs and all are `completed`, failed when one
  concludes `failure`.

Give the report (below) without waiting for the poll, and leave the poll out of it. When it
exits:

- **Pipeline passed** → restart the poll on `merged` or `closed` only.
- **Pipeline failed** → read the failing job's log with the `ci-logs` skill if present, else the
  host's tooling skill; judge it a real failure or an infrastructure flake (runner, network or
  registry, not the code).
- A flake → retry that job once (`glab api -X POST projects/<p>/jobs/<id>/retry`, `gh run rerun
  --job <job-id>`); a retry does not count as a fix push.
- After the retry → wait until the head pipeline no longer reads `failed`, then restart the poll.
- The retried job fails again → handle it as real.
- A real failure → dispatch one `general-purpose` agent with the failing log excerpt, the worktree
  path, the base and `gateCommands`, told to make the smallest fix, run every `gateCommands` entry
  and commit it as `fixup! <subject of the commit it repairs>`.
- Its `fixup!` committed with `gateCommands` green → fold per step 6, `git push
  --force-with-lease`, and restart the poll.
- A real failure after 2 fix pushes, or an agent that commits no green fix → stop fixing, post a
  CI hand-back comment on the MR/PR with the failing job link, and restart the poll on `merged` or
  `closed` only.
- Review comments on the MR/PR → leave them to the user.

- **Merged** → `cd` to the main checkout (step 3), run the block below, then check the issue
  closed. Report one line: new `<target>` head, worktree and branch deleted, issue state.
- The main checkout is not on `<target>`, or its `git status --porcelain` prints anything → run
  `git fetch` in place of `git pull --ff-only`, and say so in the report.
- The block fails → report the git error; leave the worktree and the branch.
- **Closed unmerged** → `cd` to the main checkout, `git worktree remove
  .claude/worktrees/issue-<n>-<slug>`, report it; leave the branch.

```sh
git worktree remove .claude/worktrees/issue-<n>-<slug> &&
  git pull --ff-only && git branch -d issue-<n>-<slug>
```

## Report back

The report carries only what the user must know or act on.

- Open with each `assumptions` entry that departs from the issue's text or changes behaviour a
  user or caller can observe, and that no written rule or instruction settles, as its own list
  under a `**Assumptions:**` heading.
- Put nothing else under that heading.
- An assumption a step-5 question settled → leave it out.
- Add no line that this skill does not name.
- Every other item is one bullet with a bold label, e.g. `**Dispute accepted:**`, `**Lab:**`.
- Three or more numbers compared across cases (variants, runs, before/after) → one table, a row
  per case, under its bold label; never a bullet.
- No blank line between bullets.
- Assumptions above the bullets → put a `**Notes:**` line between them.
- End with one plain line, after a blank line: `Work on #<n> is done: <MR/PR link>`.
- Research issue closed by its findings comment → end with `Work on #<n> is done: <comment link>`.
- No MR/PR, and not a closed research issue → first post one comment on the issue: the branch,
  the open blocking findings, the assumptions the report shows, the open questions with their
  reviewers and locations, the lab numbers when lab work ran, and the `<why>`.
- Then end with `Work on #<n> is handed back: <branch> in
  .claude/worktrees/issue-<n>-<slug> — <why> (<hand-back comment link>)`.
- Name each `degraded` entry, and each dead reviewer the hand-back `<why>` does not name.
- No MR/PR and `untrackedPaths` non-empty → list them under one bold label.
- Name each dispute you settled, which way, and why.
- Name each adjacent fix committed on the branch by its subject, one line each.
- Name each issue filed for an adjacent defect by its link, one line each, never the defect itself.
- Name each adjacent defect that could not be filed, and why, one line each.
- A decision record the branch adds in a clone not marked own → one `**Conventions:**` bullet:
  the path, naming and the upstream file or folder they came from.
- Say so when `redEvidence` is empty on a bug fix.
- Give a lab step one line: its verdict, or its numbers when there are fewer than three.
- Give each pipeline failure step 7 acts on one `**Pipeline:**` line in a follow-up message: the
  job, real or flake, and the fix commit.
- Name each reviewer that could not check something, and the check you ran in its place.
- Stopped at triage or on a step-5 question → say what is blocking and stop there.
- Leave out nits and reviewer verdicts with no finding.
- Leave out `gateCommands` entries that passed and a summary of the change: the MR carries it.
- Leave out a present `redEvidence` and lab work that did not run.
- A review with no blocking finding, no dispute and no fix round gets no line.
- Handed back → no line saying a reviewer found nothing or that nothing was disputed.
- The hand-back `<why>` clause names only what blocks; it never adds that other reviewers, rounds
  or disputes came back clean.

- Use the layout below as the complete report.
- Omit empty sections and inapplicable bullets.
- Keep the applicable closing line even when it is the only line.

```
**Assumptions:**
- <assumption>

**Notes:**
- **Conventions:** <path, naming> (<source>)
- **Dispute accepted:** <finding> — <why>
- **Lab:** <verdict>

**Lab, master vs branch:**

| Run | master | branch |
|---|---|---|
| <case> | <number> | <number> |

Work on #<n> is done: <MR/PR link>
```
