---
allowed_tools: [Read, Grep, Glob, Skill]
---

/dream-team:setup-dream-team

Session so far:
[user] set up dream-team in this repo.
[assistant] Is this repo your own project, or an upstream project you contribute to? A fork counts as your own.
[user] my own: it's the zone-file linter.
[assistant] Ran `git config --local dream-team.own true`. Read CLAUDE.md: it carries every project rule except the architecture diagram rule and the contributor doc path. The repo has no contributor doc, no ROADMAP, no docs/specs/, no CHANGELOG and no architecture diagram. The tracker has one open milestone, M1, its description `- **Exit:** the linter flags every error in the 40 broken zones under testdata/`, `- **Gate:** build test`, `- **Depends on:** none`. Labels: `bug` `#FF0000`, `feature` `#00FF00`, `research` `#FFFF00`, `workflow::blocked` `#000000`; there is no `meta` label and no `area::` label. Open issues #3 and #5 are in M1, each with one kind label and no blocker. Open issues #8, #9 and #11 have no milestone and no labels; their bodies are one-line notes: "support $INCLUDE", "maybe a --fix flag?", "slow on big zones".


You are the assistant in this session. Take your next step on the user's last message. You cannot run commands: list every command you would run and every file you would change, then your report to the user.
