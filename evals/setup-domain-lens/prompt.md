---
allowed_tools: [Read, Grep, Glob, Skill]
---

/dream-team:setup-dream-team

Session so far:
[user] set up dream-team in this repo.
[assistant] Is this repo your own project, or an upstream project you contribute to? A fork counts as your own.
[user] my own: it's the RADIUS proxy.
[assistant] Ran `git config --local dream-team.own true`. Read CLAUDE.md, in full:
```
# CLAUDE.md

- Detail the code doesn't show goes in the commit message or a topic doc under docs/, never in package docs.
- A fact the code and paths don't show has one doc under docs/, updated in the MR that changes it.
- Name a new milestone M<n>; a split takes the next free M<n>, never a letter.
- Every Access-Reject the proxy sends carries a Reply-Message attribute.
- Never write a User-Password or Message-Authenticator value to a log.
- Run `go test ./...` before every commit.
```
The repo has no contributor doc, no ROADMAP, no docs/specs/, no CHANGELOG and no architecture diagram. docs/ holds `rfc2865.txt`, the vendored text of RFC 2865, and `proxy-timeouts.md`. The tracker has one open milestone, M1, its description `- **Exit:** the proxy forwards every request in testdata/pcaps/ and answers each one within 3 s`, `- **Gate:** go test ./...`, `- **Depends on:** none`. Every label in Label colours exists with its colour; there is no `area::` label and no `type::` label. Open issues #2 and #4 are in M1, each with one kind label and a problem, proposal body, and neither has a blocker.


You are the assistant in this session. Take your next step on the user's last message. You cannot run commands: list every command you would run and every file you would change, then your report to the user.
