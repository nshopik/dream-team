---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the scope-issue skill, then answer.

Session so far:
[user] /dream-team:qa-review audit tests/
[assistant] Verified findings, 3 confirmed. No open issue covers any of them.
- 🔵 tests/test_sync.py:12 — `make_client()` is a copy of `tests/helpers.py:8` `make_client()`; delete it and import the helper.
- 🔵 tests/test_sync.py:140 — `FakeClock` stub belongs in `tests/stubs.py`, where the other stubs live; move it there and import it.
- 🔵 tests/test_parse.py:33 — comment says "see parse.py:88", but that logic is now at `parse.py:121`; name the function `parse_header()` instead of a line number.
[user] file them


You are the assistant in this session. Take your next step. You cannot run commands: show the issue text you would file, or the message you would send the user.
