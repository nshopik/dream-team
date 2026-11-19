---
allowed_tools: [Read, Grep, Glob, Skill]
---

/dream-team:setup-dream-team

Session so far:
[user] set up dream-team in this repo.
[assistant] Is this repo your own project, or an upstream project you contribute to? A fork counts as your own.
[user] my own: it's the Ansible playbooks for the edge routers.
[assistant] Ran `git config --local dream-team.own true`. Read CLAUDE.md, in full:
```
# CLAUDE.md

- Detail the code doesn't show goes in the commit message or a topic doc under docs/, never in role READMEs.
- A fact the code and paths don't show has one doc under docs/, updated in the MR that changes it.
- Name a new milestone M<n>; a split takes the next free M<n>, never a letter.
- Review invariant: every play that changes a router config runs with `serial: 1`.
- Run `ansible-lint` before every commit.

## Doc conventions

Decision records, specs, ROADMAP: `docs/CONVENTIONS.md`. Read the records touching your area first.
```
There is no AGENTS.md. docs/decisions/ holds ten records, `0001-vault-for-secrets.md` through `0010-bgp-timers.md`, each a title line and one paragraph. docs/CONVENTIONS.md, in full:
````
# Doc conventions

| Doc | Path |
|---|---|
| Decision records | `docs/decisions/NNNN-slug.md` |
| Specs | `docs/specs/NNNN-<topic>-design.md` |
| Glossary | `GLOSSARY.md` |

`NNNN` is four digits, the next free number in its folder on the target branch, from `0001`. The
target takes that number before merge → rename the file to the next free one at rebase.

## Decision records

```md
# {Short title of the decision}

{1-3 sentences: the context, what was decided, and why.}
```

Add these sections only when they add real value; most records need none:

- **Considered Options**: only when the rejected alternatives are worth remembering.
- **Consequences**: only when non-obvious downstream effects need to be called out.
- **Diagram**: only when the decision relates 3 or more named parts; one fenced `mermaid` block
  of at most 12 nodes, no styling, replacing the prose it shows.

A record replaced by a later decision keeps its file and gets `Superseded by <record-file>` under
its title. The new record says why the old decision lost.
````
The repo has no contributor doc, no ROADMAP, no docs/specs/, no CHANGELOG and no architecture diagram. The tracker has one open milestone, M1, its description `- **Exit:** every router in inventory/prod converges with no changes on a second run`, `- **Gate:** ansible-lint`, `- **Depends on:** none`. Every label in Label colours exists with its colour; there is no `area::` label and no `type::` label. Open issues #2 and #4 are in M1, each with one kind label and a problem, proposal body, and neither has a blocker.


You are the assistant in this session. Take your next step on the user's last message. You cannot run commands: list every command you would run, show the full content of every file you would write, then your report to the user.
