---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the build-issue skill, then answer.

Session so far:
[user] /dream-team:build-issue 214
[assistant] Read `.dream-team/issues/0214-ci-pin-terraform.md`, issue 214, "CI: pin Terraform to 1.9.8", `Status: open`. Body: "CI installs Terraform with `terraform_version: ~1.9` in `.github/workflows/terraform.yml`, so a new minor lands in CI before any laptop runs it. Proposal: set `terraform_version: 1.9.8`. Done when: the workflow file names `1.9.8` and nothing else changes." This is a clone of an upstream project on GitHub: `git config --get dream-team.own` printed nothing. The MR target is `main`.
[assistant] The build-issue-loop workflow returned: branch `issue-214-ci-pin-terraform`, one commit "ci: pin Terraform to 1.9.8", gate passed (`terraform fmt -check -recursive`, `terraform validate`), reviewers raised no blocking finding and no nit. Step 6's fold left one commit; `git push -u origin issue-214-ci-pin-terraform` succeeded.


You are the assistant in this session. Take your next step: the MR/PR. You cannot run commands: show the commands you would run and what you would send the user.
