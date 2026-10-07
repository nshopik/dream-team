---
name: friction
description: >-
  Scans past dream-fixer-loop workflow runs for agent friction (skill or tool hunting under
  ~/.claude, denied or erroring tool calls, repeated failing commands, forbidden actions,
  self-reported friction, token and tool-call outliers) and reports the patterns seen in two or
  more runs with the prompt line each points to. Use when the user runs /dream-team:friction or
  asks what keeps going wrong across dream-fixer runs.
disable-model-invocation: true
---

# friction

## 1. Scan

- Run `python3 <this skill's base directory>/friction.py`.
- The script scans every workflow run not yet in the cache and appends its hits there.
- It prints each pattern + role seen in 2 or more runs; one-off hits stay in the cache only.
- Output is only the `scanned … new runs` line → report no repeated friction and stop.

## 2. Trace each pattern

Pattern names the script prints:

- `claude-dir`: Read/Glob/Grep, or a Bash `find`/`ls`/`cat`, under `~/.claude`.
- `tool-error`: a tool call denied or erroring, other than a plain non-zero exit.
- `repeat-failure`: the same failing Bash command run twice or more by one agent.
- `forbidden`: `ssh`, `git push`, a `gh`/`glab` write, or an edit or commit by a read-only role.
- `self-report`: an entry from the agent's `friction` output field.
- `tokens-outlier`, `tools-outlier`: over 2x the role's median over earlier runs.

For each printed pattern:

- Find the prompt that role runs in `<base directory>/../../workflows/dream-fixer-loop.js`:
  `impl` → `implPrompt`, `gate` → `verifyPrompt`, `build-fix` → `buildFixPrompt`, `simplify` →
  `simplifyPrompt`, `simplify-fix` → `simplifyFixPrompt`, `review:domain` →
  `domainPrompt`, `review:external` → `externalPrompt`, `review:verify` → `verifyRunPrompt`,
  other `review:` → `qualityPrompt`, `re-review:` → `reReviewPrompt`, `fix` →
  `fixPrompt`.
- Name the prompt or skill line the evidence points to: the instruction the agent could not
  follow, or the tool it lacked.
- Read the evidence before blaming a prompt; a hook bounce working as designed or a long run on a
  hard issue has no prompt line behind it.
- No prompt line behind it → list it as ordinary and offer nothing for it.

## 3. Report

- One bullet per pattern: `- **<pattern> | <role>:** <n> runs; <evidence>; <file>:<line>`.
- Offer to file one dream-team issue per pattern that has a prompt line, written with
  `scope-issue`.
- File nothing without the user's yes.
