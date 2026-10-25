# CLAUDE.md

- Write skill rules as atomic `-` bullets, one condition and one action each; never as prose
  paragraphs.
- Add a skill or agent rule only for a failure seen in a real run or eval; never for a
  hypothetical one.
- Prefer editing or deleting an existing rule over adding a new one.
- Before editing a `SKILL.md` or `agents/*.md` `description:`, apply each of these:
  - Write it in the third person: "Writes …", not "Write …".
  - Say what it does first, then when to use it.
  - Name the key terms a request or command for it would contain.
  - Keep it to 1,024 characters, with no XML tags.
- Before adding a skill or agent, or changing a `SKILL.md`'s other sections or files or an
  `agents/*.md` prompt, read
  https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md and follow it.
- Fix one failure with one rule; never add a rule for adjacent cases the issue did not hit.
- Keep rules out of `README.md`; it points at the skills instead of restating them.
- Run a `skills/*/evals/` runner with `--plugin-dir .`; without the flag it measures the installed
  plugin cache, not the working tree.
- In `hooks/test_body_cap.py`, match an over-cap deny on `-word ceiling`, not `ceiling`; the
  skill text the hook quotes back contains the bare word.
- Judge a `scope-mr` change on in-repo runs too (`REPO=<checkout>` in `run_baseline.sh`);
  diff-only runs lack the context real sessions read and hide what the skill does there.
- Run the hook tests as `python3 <file>` each, never `python3 -m unittest`; they are plain
  scripts and unittest exits 5 with NO TESTS RAN.
- Call a plugin workflow by its prefixed name (`dream-team:<name>`), never by `scriptPath`; skill
  text does not expand `${CLAUDE_PLUGIN_ROOT}`; a plugin agent body does.
- Before editing `CHANGELOG.md`, read `references/changelog-style.md`.
- Fence a chat-output layout in a skill, so the model reproduces its markdown; show example
  skill output in docs or evals as rendered markdown, where a fence hides the bold labels judged.
- Lay out a skill's chat output for a monospace terminal: tight `- **Label:**` bullets, no blank
  lines between items; paragraph spacing wastes fixed-height lines.
- Commit `skills/*/evals/` (cases, fixtures, runner) except `skills/scope-*/evals/`; those and
  `runs/` are ignored.
- Commit top-level `evals/` except `evals/results/`.
- Run the top-level `evals/` cases with
  `claude plugin eval . --trust-plugin --model opus --threshold 0.6`.
- Give a small or pass-through skill or workflow phase stub-agent tests only; add a paid
  headless-claude eval runner only for a large skill or a failure seen in a real run.
- Before changing who does a step in a skill, read the skill's top-level role rules (e.g.
  dream-fixer's "You do not write the change" edit list) and update them in the same change.
- Check skill triggering with `skills/scope-commit/evals/run_trigger.sh` (unnamed prompts); the
  other evals name the skill in the prompt and cannot see a description change. Keep its fixture
  repo consistent with each prompt, or the agent stops before loading any skill.
- In a headless `claude -p` run, pipe the prompt on stdin or put it before `--allowed-tools`; that
  flag is variadic and swallows a trailing prompt ("Input must be provided").
- Keep research findings mined from local session data (workflow journals, run counts) out of the
  repo and its issues; report them in chat only, even when dream-fixer's research tier says to
  post a findings comment.
- Delegate grading of eval reports against a ledger to a subagent (Agent tool); the main session
  only reads the scores and the marks file.
- Cite an outside pull request in commits, PRs, issues and notes in plain words ("unbound pull
  request 1525"), never `#1525`; GitHub links `#N` to this repo.
- Before filing a follow-up issue, list the milestone's open issues; a matching one gets a comment
  with the new evidence, not a new issue (#231 duplicated #226).
- Skip an eval issue's research note when its follow-up issues carry the answers or its gate
  finds nothing to change; post the findings as a comment on the issue and close it, committing
  nothing (#238, #256).
- Start an interactive session in this repo without `--plugin-dir .`; with it, every Write and
  Edit here prompts even in accept-edits mode. Keep the flag for headless evals.
- Give a headless `pi -p` run without piped input `< /dev/null`; under a Claude Bash call it
  waits forever on the harness stdin socket, 0% CPU, empty output.
