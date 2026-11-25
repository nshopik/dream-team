---
name: friction
description: >-
  Scans the current session, its subagents and its workflow runs, or with `all` every past
  craft-it-loop run, for agent friction (skill or tool hunting under ~/.claude, denied or
  erroring tool calls, repeated failing commands, forbidden actions, a skill the prompt names but
  the agent skipped, self-reported friction, token and tool-call outliers) and reports each pattern
  with the deterministic check that would stop it or the prompt line it points to; on the current
  session it also lists retro improvement candidates by severity. With `all` it reports only the
  patterns seen in two or more runs. Use when the user runs /dream-team:friction or asks what went
  wrong in this session or keeps going wrong across craft-it runs.
disable-model-invocation: true
---

# friction

## 1. Scan

- No argument → run `python3 <this skill's base directory>/friction.py ${CLAUDE_SESSION_ID}`.
- It prints every hit in this session's transcript, its subagents and the workflow runs it
  started.
- `all` → run `python3 <this skill's base directory>/friction.py all`.
- `all` and the user asks for run times → add `--time`; print its table and stop.
- `all` scans every workflow run not yet in the cache and appends its hits there.
- `all` prints each pattern + role seen in 2 or more runs; one-off hits stay in the cache only.
- Output is only its `scanned …` line → report no friction.
- No friction and `all` → stop.

## 2. Trace each pattern

Pattern names the script prints:

- `claude-dir`: Read/Glob/Grep, or a Bash `find`/`ls`/`cat`, under `~/.claude`.
- `tool-error`: a tool call denied or erroring, other than a plain non-zero exit.
- `repeat-failure`: the same failing Bash command run twice or more by one agent.
- `forbidden`: `ssh`, `git push` or a `gh`/`glab` write by a workflow-run agent, or an edit, a
  Bash tree edit (`sed`/`perl -i`, `git checkout`/`restore`/`stash`, `tee` or a redirect to a path
  outside `/tmp/` and `/dev/`) or a commit by a read-only role.
- `skill-skipped`: an agent whose prompt tells it to load the `build-rules` or `scope-commit`
  skill and whose transcript has no Skill call for it.
- `self-report`: an entry from the agent's `friction` output field.
- `tokens-outlier`, `tools-outlier`: over 2x the role's median over earlier runs.

For each printed pattern:

- Find the prompt that role runs in the `craft-it-loop.js` file in craft-it's base directory:
  `impl` → `implPrompt`, `gate` → `verifyPrompt`, `build-fix` → `buildFixPrompt`,
  `review:domain` → `domainPrompt`, `review:external` → `externalPrompt`,
  other `review:` → `lensPrompt`, `re-review:` → `reReviewPrompt`, `fixdiff:` →
  `fixDiffPrompt`, `fix` → `fixPrompt`.
- `session` or `session:<agent type>` → the skill or agent prompt this session or its subagent ran.
- Name the prompt or skill line the evidence points to: the instruction the agent could not
  follow, or the tool it lacked.
- Read the evidence before blaming a prompt or naming a check; a hook bounce working as designed
  or a long run on a hard issue has neither behind it.
- A permission rule, hook or gate command could stop the pattern → name that check and what it
  stops.
- The pattern needs judgement → name no check.
- The only check is a new hook and no written rule forbids what the agent did → name no check.
- No check and no prompt line behind it → list it as ordinary and offer nothing for it.

## 3. Retro candidates

- `all` → skip this step.
- Read this session's transcript, `~/.claude/projects/*/${CLAUDE_SESSION_ID}.jsonl`, and its
  subagents' under `~/.claude/projects/*/${CLAUDE_SESSION_ID}/subagents/`.
- List each improvement candidate to the agents' environment under one of these categories:
  - **Navigation:** an agent took long to find a file or fact; a navigation pointer would save it.
  - **Automated checks:** a mistake a lint, type check, test, hook or CI job could have caught.
  - **Tool economy:** an expensive tool call a cheaper call or a script could replace.
  - **Steering no-ops:** a CLAUDE.md, skill or prompt line that changed nothing an agent did.
  - **Information access:** information an agent needed and could not reach.
- Rate each candidate high, medium or low by what it cost the session.

## 4. Report

- One bullet per pattern: `- **<pattern> | <role>:** <n> runs (or hits); <evidence>; <target>`.
- A named check → `<target>` is `check: <check>`.
- No check, a prompt line → `<target>` is `<file>:<line>`.
- Ordinary → `<target>` is `ordinary`.
- No argument → after the patterns, one bullet per retro candidate, most severe first:
  `- **<severity> | <category>:** <evidence>; <proposal>`.
- Offer to file one dream-team issue per pattern with a check or a prompt line, for its `<target>`,
  written with `scope-issue`.
- File nothing without the user's yes.
