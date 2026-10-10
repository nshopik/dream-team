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
- Run evals with `--plugin-dir .`; without it they measure the installed plugin cache, not the
  working tree.
- In `hooks/test_body_cap.py`, match an over-cap deny on `-word ceiling`, not `ceiling`; the
  skill text the hook quotes back contains the bare word.
- A cap-exemption test (fenced block, table row) runs through `gh issue create`, not `mr()`; the
  MR path also has a per-diff-line budget that fires first inside this repo.
- Judge a `scope-mr` change on in-repo runs too (`REPO=<checkout>` in `run_baseline.sh`);
  diff-only runs lack the context real sessions read and hide what the skill does there.
- Run the hook tests as `python3 <file>` each, never `python3 -m unittest`; they are plain
  scripts and unittest exits 5 with NO TESTS RAN.
- Call a plugin workflow by its prefixed name (`dream-team:<name>`), never by `scriptPath`; skill
  text does not expand `${CLAUDE_PLUGIN_ROOT}`; a plugin agent body does.
- Release a plugin by bumping its `plugin.json` version and CHANGELOG; never tag it or offer a tag.
- Show example skill output as rendered markdown, never inside a code fence; the fence hides the
  bold labels being judged.
- Lay out a skill's chat output for a monospace terminal: tight `- **Label:**` bullets, no blank
  lines between items; paragraph spacing wastes fixed-height lines.
- Commit `skills/*/evals/` (cases, fixtures, runner) except `skills/scope-*/evals/`; those and
  `runs/` are ignored.
- Give a small or pass-through skill or workflow phase stub-agent tests only; add a paid
  headless-claude eval runner only for a large skill or a failure seen in a real run.
- Before changing who does a step in a skill, read the skill's top-level role rules (e.g.
  dream-fixer's "You do not write the change" edit list) and update them in the same change.
- Check skill triggering with `skills/scope-commit/evals/run_trigger.sh` (unnamed prompts); the
  other evals name the skill in the prompt and cannot see a description change. Keep its fixture
  repo consistent with each prompt, or the agent stops before loading any skill.
- In a headless `claude -p` run, pipe the prompt on stdin or put it before `--allowed-tools`; that
  flag is variadic and swallows a trailing prompt ("Input must be provided").
- Pass a dream-fixer-loop roster slot with no specialist as the literal `generic`, never
  `general-purpose`; the workflow rejects an implementer and domain reviewer of the same
  non-`generic` type.
- Keep scout findings mined from local session data (workflow journals, run counts) out of the repo
  and its issues; report them in chat only, even when dream-fixer's scout tier says to commit a
  research note.
