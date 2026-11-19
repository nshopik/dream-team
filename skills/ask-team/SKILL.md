---
name: ask-team
description: >-
  Answers which Dream Team skill fits the user's situation now: reads the open milestones and
  their issues without an open blocker, or the local `.dream-team/issues/` files in a clone not
  marked own, open MRs/PRs, the current branch and uncommitted changes, then
  recommends one skill from its skill map with why it fits, a ready-to-run command and where it
  sits (the WORKFLOW.md step for a main-flow skill, else its map group: on-ramp, standalone or
  precondition), and starts that skill when the user says to go ahead or asked for the work
  itself. Use when the user runs /dream-team:ask-team or asks "which skill", "what now", "what
  next", "where do I start" or where they stand in the flow.
disable-model-invocation: true
---

# ask-team

## Skill map

Each skill runs alone, in any order, without the tracked flow. A one-off feature in an upstream
project runs `brainstorm`, `scope-issue` to a local issue file, then `craft-it <n>`, with no
milestone.

- **Main flow:** `scope-spec` ([step 0](WORKFLOW.md#0-idea-to-spec-once-per-project)),
  `cut-milestones` ([step 1](WORKFLOW.md#1-spec-to-milestones)), `scope-issue`
  ([step 2](WORKFLOW.md#2-milestone-to-issues)), `craft-it` and `assemble-meta`
  ([step 3](WORKFLOW.md#3-issue-to-mr-the-daily-loop)), `milestone-close`
  ([step 5](WORKFLOW.md#5-milestone-close)), `ship-it` ([step 6](WORKFLOW.md#6-release)).
- **On-ramps:** `brainstorm`, `triage-issue`.
- **Standalone:** `qa-review`, `build-rules`, `scope-commit`, `scope-mr`, `review-bench`,
  `friction`, `ask-team`.
- **Precondition:** `setup-dream-team`.

## 1. Read where the work stands

- `git config --local --type=bool --get dream-team.own` prints `true` → read the open milestones
  and their open issues; keep those whose `Blocked by` lines name no open issue.
- `dream-team.own` prints anything else → look for `.dream-team/` in the main checkout, the first
  `worktree` path `git worktree list --porcelain` prints.
- `dream-team.own` prints anything else, `.dream-team/issues/` holds a file and
  `.dream-team/TRACKER.md` exists → read the open issues there per `.dream-team/TRACKER.md`.
- `dream-team.own` prints anything else and `.dream-team/issues/` holds no file → skip that read.
- `dream-team.own` prints anything else, `.dream-team/issues/` holds a file and
  `.dream-team/TRACKER.md` does not exist → stop with "run `setup-dream-team` first".
- Read the open MRs/PRs, the current branch and its uncommitted changes.

## 2. Pick the skill

- A "what next" or flow question with an open milestone → read [WORKFLOW.md](WORKFLOW.md) and
  pick the step and skill that fit the state.
- Any other question → pick the skill from the skill map that fits it and the state.
- A new or vague idea → `brainstorm`.

## 3. Reply

```
- **Recommendation:** <skill> — <why it fits now>
- **Command:** `<ready-to-run command>`
- **Where:** <WORKFLOW.md step number and title for a main-flow skill, else its map group>
```

## 4. Hand off

- The user says to go ahead, or asked for the work itself → start the recommended skill.
- The recommended skill sets `disable-model-invocation: true` → tell the user to run the command
  themselves.
- Otherwise → recommend only.
