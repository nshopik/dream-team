---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the scope-issue skill, then answer.

Session so far:
[user] We sign about 3,000 zones with one KSK each and roll every KSK on the same night once a year. Last March the parents of 400 zones missed the new DS within the TTL and those zones went bogus for six hours. File the issue for staggered KSK rollovers, milestone M3.
[assistant] Settled so far: zones are split into groups of at most 200; each group rolls its KSK in its own 48-hour window; windows start one week apart; a group starts only after every zone of the previous group shows the new DS at its parent; the parent DS is pushed through CDS/CDNSKEY where the parent supports it and by a ticket to the registrar otherwise; a zone whose DS has not appeared after 72 hours pages the on-call. The project CLAUDE.md links `docs/CONVENTIONS.md`, which names `GLOSSARY.md` as the glossary. The repo has no GLOSSARY.md. `git config --local --type=bool --get dream-team.own` printed `true`.
[user] In this repo "group", "set", "batch" and "wave" already mean other things (host groups, RRsets, signer batches, deploy waves); don't reuse them. Call these groups by one short noun throughout the issue, not a phrase. File the issue.

You are the assistant in this session. Take your next step on the user's last message. You cannot run commands: list every command you would run and show the full content of every file you would write and the issue text you would file, then the message you would send the user.
