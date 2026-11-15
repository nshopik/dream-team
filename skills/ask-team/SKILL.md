---
name: ask-team
description: >-
  Answers which Dream Team step or skill fits the user's situation now: reads the open milestones,
  their issues without an open blocker, open MRs/PRs, the current branch and uncommitted changes,
  then recommends one skill with why it fits, a ready-to-run command and the WORKFLOW.md step that
  backs it, and starts that skill when the user says to go ahead or asked for the work itself. Use
  when the user runs /dream-team:ask-team or asks "which skill", "what now", "what next" or where
  they stand in the flow.
disable-model-invocation: true
---

# ask-team

## 1. Read where the work stands

- Read the open milestones and their open issues; keep those whose `Blocked by` lines name no open
  issue.
- Read the open MRs/PRs, the current branch and its uncommitted changes.

## 2. Pick the step

- Read [WORKFLOW.md](WORKFLOW.md) and pick the step and skill that fit the question and the state.
- A new or vague idea → `brainstorm`.

## 3. Reply

```
- **Recommendation:** <skill> — <why it fits now>
- **Command:** `<ready-to-run command>`
- **Step:** <WORKFLOW.md step number and title>
```

## 4. Hand off

- The user says to go ahead, or asked for the work itself → start the recommended skill.
- The recommended skill sets `disable-model-invocation: true` → tell the user to run the command
  themselves.
- Otherwise → recommend only.
