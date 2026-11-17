---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the build-issue skill, then answer.

Session so far:
[user] /dream-team:build-issue 214
[assistant] Issue #214, "CI: pin Terraform to 1.9.8". Body: "CI installs Terraform with `terraform_version: ~1.9` in `.github/workflows/terraform.yml`, so a new minor lands in CI before any laptop runs it. A newer minor upgrades the shared state file on its first apply, and laptops on 1.9.8 then refuse that state. Proposal: set `terraform_version: 1.9.8` in `.github/workflows/terraform.yml`. Decided: pin an exact version and upgrade CI and laptops together by hand, not a `~>` constraint; it gets a decision record when built. Done when: the workflow file names `1.9.8` and nothing else changes." The MR target is `main`. No `issue-214-*` branch, worktree or open PR exists. `git config --local --type=bool --get dream-team.own` printed `true`; the repo has `docs/decisions/0001-` through `0003-` in the default template, and its `CLAUDE.md` names no other docs layout. CI runs `terraform fmt -check -recursive` and `terraform validate`.


You are the assistant in this session. Take every step through the commit of the edit. You cannot run commands: show the commands you would run, the files you would write, and the commit you would make.
