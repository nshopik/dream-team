---
name: craft-rules
description: >
  Holds the build rules for a code change: smallest change and reuse first, no speculative
  abstraction or impossible-case error handling, the change placed in the layer that owns the
  invariant, comments, option docs and tests. Use before the first edit when asked to build,
  implement, add, change or fix code, a feature or a bug.
---

# craft-rules

## Scope

- Implement the smallest change that resolves the task.
- Reuse what is already in the repo before writing anything new.
- Add no abstraction for a hypothetical requirement.
- Leave the code around the change as it is: no cleanup.
- Change the code instead of adding a feature flag or a back-compat shim.
- Dedup that keeps the line count roughly flat → do it; it need not shrink the diff.

## Error handling

- Add no error handling or validation for a case that cannot happen; trust internal code and
  framework guarantees.
- Validate at system boundaries only: user input, external APIs.

## Where the change goes

- Trace the entry point through the layers to the one that owns the invariant.
- Put the change where the invariant lives.
- Never force the change into one file or a local patch.
- Before fixing a shared function, grep every caller.

## Comments

These rules cover the comment you are about to write, not only the ones you find.

- Write a comment only for what the code cannot say: a non-obvious constraint, a decision, a
  gotcha.
- Keep a comment to one sentence where one sentence does.
- Never narrate what the next line does.
- Never restate in prose what readable YAML or config already says.
- Give declarative code a header line, not a paragraph.
- Put rationale in the commit body, never in a code comment.
- A workaround needs a paragraph of defence → fix the code instead.

## Option docs

These rules cover README option lists, reference config comments, `--help` strings and the
comment on the option's own field or constant.

- Give a config key, flag or env var its accepted values and its default, and stop there.
- Write no usage scenario, deployment advice, "set this when …" or consequence of leaving it unset.

## Tests

- A bug fix gets a test that reproduces the bug.
- New behaviour or an exported API change gets a unit or e2e test.
- Prefer a new case in an existing table-driven test over a new test function.
- Convert an existing test to table-driven rather than duplicate it.
- Mirror realistic data and behaviour.
- Test through exported APIs where possible.
