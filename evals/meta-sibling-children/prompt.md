---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the scope-issue skill, then answer.

Session so far:
[user] /dream-team:craft-it 530
[assistant] Issue #530 "Research: why does --fix leave lint errors behind?" is in milestone M4 and research tier. The tracker has no `area::` label. Answered its questions from the code and the 12 fixable zones under testdata/; the findings comment is drafted. Four gaps found, each a runtime change to `zonelint/fixer.py`, none needing a lab host or credentials:
- `--fix` never rewrites `$INCLUDE` files: `fix_zone()` reads only the top file. Fix: call the existing `loader.resolve_includes()` and rewrite each included file in place.
- `--fix` drops trailing comments on rewritten records. Fix: `Record.render()` appends `Record.comment`, which the parser already fills.
- `--fix --dry-run` shows no diff for included files. Fix: diff each file the include rewrite writes; it can only start once the `$INCLUDE` gap above is fixed.
- `--fix` loses the comment on a record it splits in two. Fix: copy `Record.comment` onto the first half; it can only start once the trailing-comment gap above is fixed.
[user] File all four in M4 under one Meta issue.


You are the assistant in this session. Take your next step. You cannot run commands: show the issue text you would file, or the message you would send the user.
