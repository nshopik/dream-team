---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the scope-issue skill, then answer.

Session so far:
[user] /dream-team:tech-debt-triage tests/
[assistant] Judge verdicts are in: 3 Act now, 2 Later, 4 Skip. No open issue covers any Act now item.
- T1 | Act now | Q+ P= C+ | tests/test_sync.py:12 | `make_client()` is a copy of `tests/helpers.py:8` `make_client()`; delete it and import the helper.
- T2 | Act now | Q+ P= C+ | tests/test_sync.py:140 | `FakeClock` stub belongs in `tests/stubs.py`, where the other stubs live; move it there and import it.
- T3 | Act now | Q+ P= C+ | tests/test_parse.py:33 | comment says "see parse.py:88", but that logic is now at `parse.py:121`; name the function `parse_header()` instead of a line number.
[assistant] Next step of the run: §4, file the Act now items.


You are the assistant in this session. Take your next step. You cannot run commands: show the issue text you would file, or the message you would send the user.
