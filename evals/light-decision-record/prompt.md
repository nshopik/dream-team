---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the craft-it skill, then answer.

Session so far:
[user] /dream-team:craft-it 214
[assistant] Issue #214, "CI: pin Terraform to 1.9.8". Body: "CI installs Terraform with `terraform_version: ~1.9` in `.github/workflows/terraform.yml`, so a new minor lands in CI before any laptop runs it. A newer minor upgrades the shared state file on its first apply, and laptops on 1.9.8 then refuse that state. Proposal: set `terraform_version: 1.9.8` in `.github/workflows/terraform.yml`. Decided: pin an exact version and upgrade CI and laptops together by hand, not a `~>` constraint; it gets a decision record when built. Done when: the workflow file names `1.9.8` and nothing else changes." The MR target is `main`. No `issue-214-*` branch, worktree or open PR exists. `git config --local --type=bool --get dream-team.own` printed `true`; the repo has `docs/decisions/0001-` through `0003-`, and its `CLAUDE.md` has the `## Doc conventions` block. `docs/CONVENTIONS.md`, in full:
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
CI runs `terraform fmt -check -recursive` and `terraform validate`.


You are the assistant in this session. Take every step through the commit of the edit. You cannot run commands: show the commands you would run, the files you would write, and the commit you would make.
