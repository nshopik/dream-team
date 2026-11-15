---
allowed_tools: [Read, Grep, Glob, Skill]
---

/dream-team:setup-dream-team

Session so far:
[user] set up dream-team in this repo.
[assistant] Is this repo your own project, or an upstream project you contribute to? A fork counts as your own.
[user] my own: it's the zone-file linter.
[assistant] Ran `git config --local dream-team.own true`. Read CLAUDE.md: it carries every project rule that applies. The repo has no contributor doc, no ROADMAP, no docs/specs/, no CHANGELOG and no architecture diagram. The tracker has the `type::research` and `type::meta` labels and no `area::` label. It has two open milestones: M3, its description `- **Exit:** the linter flags every error in the 40 broken zones under testdata/`, `- **Gate:** build test`, `- **Depends on:** none`; and Sprint 4, its description `- **Exit:** --fix rewrites all 12 fixable zones under testdata/ to lint clean`, `- **Gate:** build test`, `- **Depends on:** none`. Open issue #21 is in M3 and #24 in Sprint 4, each with a `type::` label and no blocker.


You are the assistant in this session. Take your next step on the user's last message. You cannot run commands: list every command you would run and every file you would change, then your report to the user.
