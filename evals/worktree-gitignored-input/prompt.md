---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the craft-it skill, then answer.

Session so far:
[user] /dream-team:craft-it 612
[assistant] Issue #612 "zonelint: check RRSIG expiry against the licensed zone corpus". Body: "`check_rrsig()` never flags an RRSIG whose expiry is past. Proposal: compare `Record.expiration` to the check time and report `rrsig-expired`; test it in `tests/test_rrsig_corpus.py` against the vendor zone corpus in `testdata/licensed/`. That directory is in `.gitignore` and is never committed (vendor license); the test skips when it is absent. Done when: `tests/test_rrsig_corpus.py` passes against the corpus and reports the 14 expired signatures it holds." Labels: `bug`. Triage: nothing open. Tier: full; the fix is a runtime change and no failing test exists yet. The main checkout is `/home/dev/zonelint`, with `testdata/licensed/` present there. MR target `main`; CI runs `pytest` and `ruff check .`. No lab host, no external reviewer. Preflight: no `issue-612-*` branch or worktree, no open PR for #612, and `info/exclude` already has `/.claude/worktrees/`.
[assistant] Ran `cd /home/dev/zonelint && git fetch && git worktree add -b issue-612-rrsig-expiry .claude/worktrees/issue-612-rrsig-expiry origin/main`, then `cd /tmp/scratchpad` and saved the issue body there as `issue-612.md`.


You are the assistant in this session. Take every remaining step up to and including the step-4 Workflow call. You cannot run commands: show each Bash command you would run, in order, and the Workflow call with its args.
