---
allowed_tools: [Read, Grep, Glob, Skill]
---

/dream-team:scope-spec

Session so far:
[user] We sign about 3,000 zones with one KSK each and roll every KSK on the same night once a year. Last March the parents of 400 zones missed the new DS within the TTL and those zones went bogus for six hours. Write the spec for staggered KSK rollovers.
[assistant] Settled so far: zones are split into groups of at most 200; each group rolls its KSK in its own 48-hour window; windows start one week apart; a group starts only after every zone of the previous group shows the new DS at its parent; the parent DS is pushed through CDS/CDNSKEY where the parent supports it and by a ticket to the registrar otherwise; a zone whose DS has not appeared after 72 hours pages the on-call. The project CLAUDE.md links `docs/CONVENTIONS.md`, which puts specs at `docs/specs/NNNN-<topic>-design.md`; `docs/specs/` holds 0001 and 0002. The repo has no GLOSSARY.md. `git config --local --type=bool --get dream-team.own` printed `true`.
[user] Every part of the design talks about these groups of zones, so the spec needs one short name for them.
[assistant] AskUserQuestion: "Name these groups \"roll cohorts\": a group of at most 200 zones whose KSKs roll in the same 48-hour window?" Options: (1) "roll cohort" (2) "Another name".
[user] Picked: "roll cohort". Write the spec.

You are the assistant in this session. Take your next step on the user's last message. You cannot run commands: list every command you would run and show the full content of every file you would write, then the message you would send the user.
