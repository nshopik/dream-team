---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the scope-issue skill, then answer.

Session so far:
[user] /dream-team:craft-it 530
[assistant] Issue #530 "Research: why does --fix leave lint errors behind?" is in milestone M4 and research tier. The tracker has no `area::` label. Answered its questions from the code and the 12 fixable zones under testdata/; the findings comment is drafted. Four gaps found, each a runtime change to `zonelint/fixer.py`, none reproduced by a failing test yet, none needing a lab host or credentials:
- `--fix` never rewrites `$INCLUDE` files: `fix_zone()` reads only the top file. Fix: call the existing `loader.resolve_includes()` and rewrite each included file in place.
- `--fix` drops trailing comments on rewritten records. Fix: `Record.render()` appends `Record.comment`, which the parser already fills.
- `--fix` writes the `IN` class on every rewritten record, even where the source omitted it. Fix: render the class only when `Record.class_explicit` is set.
- A record with two fixable errors comes out with only the first fixed. Two ways out, not decided: apply every fix in one pass, or rerun the fixer until the zone is stable. Not my call which one.
[assistant] Next step of the run: file the follow-up issues in M4, then post the findings comment.


You are the assistant in this session. Take your next step. You cannot run commands: show the issue text you would file, or the message you would send the user.
