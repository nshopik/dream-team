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
- Keep `skills/scope-*/evals/` out of git; the eval corpus is local and unpublished.
- Run evals with `--plugin-dir .`; without it they measure the installed plugin cache, not the
  working tree.
- In `hooks/test_body_cap.py`, match an over-cap deny on `-word ceiling`, not `ceiling`; the
  skill text the hook quotes back contains the bare word.
- A cap-exemption test (fenced block, table row) runs through `gh issue create`, not `mr()`; the
  MR path also has a per-diff-line budget that fires first inside this repo.
- Judge a `scope-mr` change on in-repo runs too (`REPO=<checkout>` in `run_baseline.sh`);
  diff-only runs lack the context real sessions read and hide what the skill does there.
