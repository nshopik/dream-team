---
allowed_tools: [Read, Grep, Glob, Skill]
---

/dream-team:setup-dream-team

Session so far:
[user] set up dream-team in this repo.
[assistant] Is this repo your own project, or an upstream project you contribute to? A fork counts as your own.
[user] my own: it's the dnstap collector.
[assistant] Ran `git config --local dream-team.own true`. Read CLAUDE.md: it carries every project rule, including `Version milestones release in flow mode.` The repo has no ROADMAP, no docs/specs/, no component table and no architecture diagram. The tracker has one open milestone, 26.12, due 2026-12-31, its description `- **Exit:** release at the end of December with whatever has merged`, `- **Gate:** CI green on the release commit`, `- **Depends on:** none`. Every label in Label colours exists with its colour. Open issues #12 and #14 are in 26.12, each with a `type::` and an `area::` label and a problem, proposal body, and neither has a blocker.


You are the assistant in this session. Take your next step on the user's last message. You cannot run commands: list every command you would run and every file you would change, then your report to the user.
