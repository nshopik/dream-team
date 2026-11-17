---
allowed_tools: [Read, Grep, Glob, Skill]
---

/dream-team:setup-dream-team

Session so far:
[user] set up dream-team in this repo.
[assistant] Is this repo your own project, or an upstream project you contribute to? A fork counts as your own.
[user] my own: it's the zone-file linter.
[assistant] Ran `git config --local dream-team.own true`. Read CLAUDE.md: it carries every project rule that applies. It names `docs/rfc1035.txt` as the review reference. The repo has no contributor doc, no ROADMAP, no docs/specs/, no CHANGELOG and no architecture diagram. The tracker has one open milestone, M1, its description `- **Exit:** the linter flags every error in the 40 broken zones under testdata/`, `- **Gate:** build test`, `- **Depends on:** none`. Every label in Label colours exists with its colour except the six kind labels; the tracker has `type::bug`, `type::feature`, `type::maintenance`, `type::performance`, `type::research` and `type::meta` instead, and no `area::` label. Open issue #3 in M1 has `type::bug`, open issue #5 in M1 has `type::feature`, closed issue #1 has `type::research`; none has a blocker.


You are the assistant in this session. Take your next step on the user's last message. You cannot run commands: list every command you would run and every file you would change, then your report to the user.
