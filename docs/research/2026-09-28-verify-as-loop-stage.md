# /verify as a dream-fixer-loop stage

Scout for #68. Claude Code 2.1.283. Outcome: `/verify` runs as an opt-in Review gate, through a
nested `claude -p "/verify"` session. Follow-up: #69.

## Can a workflow agent load `/verify`?

Not through the Skill tool. The Skill tool refuses it in a headless `claude -p` session, and a
workflow subagent calls the same tool:

```
<tool_use_error>Skill verify cannot be used with Skill tool due to disable-model-invocation.
Ask the user to run /verify themselves — it cannot be invoked via the Skill tool. Do not
replicate this skill's workflow by other means — it is reserved for explicit user
invocation.</tool_use_error>
```

Other routes:

- Read the bundled `SKILL.md` directly: not possible. `/tmp/claude-1000/bundled-skills/2.1.283/
  <hash>/verify/` holds only `examples/cli.md` and `examples/server.md`. The prompt is compiled
  into the binary.
- Our own copy: the prompt is Anthropic's, and this repo is public. A skill written from the
  method alone would need an A/B eval against the built-in before anyone could trust its
  quality. It would also drift from the built-in, which ships with every Claude Code
  release.
- Nested `claude -p "/verify <scope>"` from Bash: works. The headless init event lists `verify`
  under `slash_commands`, and the run follows the skill.

Decision (user): use the nested route, opt-in per repo. A repo that opts in is the user
explicitly invoking `/verify`, which is what `disable-model-invocation` asks for. Cost: one extra
Claude Code session per gate run, counted against the plan's usage limits.

## Answers

- **Placement:** a Review gate. A FAIL becomes a blocking finding, which the fix loop and the
  gate's re-review already handle. A last phase could only hand the branch back. A gate is
  re-run only when it failed, the same as every other reviewer. The mechanical gate still runs
  after every fix commit.
- **Cold-start recipe:** the nested run writes `.claude/skills/verify/SKILL.md`, and the
  dirty-tree gate would fail on it. The gate agent returns the file's contents in its result and
  deletes the file. dream-fixer reports the recipe, and the user commits it outside the issue's
  single commit.
- **Captures:** the gate agent tells the nested run to write every capture under a
  `mktemp -d` directory. The dirty-tree gate catches any leak.
- **BLOCKED:** not a finding. The result carries the verdict and the reason. When the reason
  needs the lab, dream-fixer step 6 runs it as a lab step through `dream-team:lab-runner`. With
  no lab host, the report names the verdict.
- **PASS evidence:** the result carries the command and trimmed output. dream-fixer puts them in
  the MR description.
- **Availability fallback:** the nested run's init event does not list `verify`, or `claude` is
  not on `PATH` → skip the gate and add `verify` to `degraded`, the same path Simplify uses.
- **Skip rules:** off unless the repo opts in. Also off when the diff has no code: docs,
  comments, CI config, test fixtures.
- **This repo:** stays off. Its surface is agent behaviour, and the eval runners under
  `plugins/*/skills/*/evals/` already drive it.
