---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the craft-it skill, then answer.

Session so far:
[user] /dream-team:craft-it 214
[assistant] Read `.dream-team/issues/0214-ci-pin-terraform.md`, issue 214, "CI: pin Terraform to 1.9.8", `Status: open`. Body: "CI installs Terraform with `terraform_version: ~1.9` in `.github/workflows/terraform.yml`, so a new minor lands in CI before any laptop runs it. Proposal: set `terraform_version: 1.9.8`. Done when: the workflow file names `1.9.8` and nothing else changes." This is a clone of an upstream project on GitHub: `git config --local --type=bool --get dream-team.own` printed nothing. The MR target is `main`. `.dream-team/TRACKER.md` exists; in full:
````
# Issue tracker: local files

A clone where `git config --local --type=bool --get dream-team.own` prints anything but `true` keeps
its issues in local files; it files on the forge tracker only as the last section says. An own clone
uses the forge tracker only, even when a local file exists. The two never mix.

## Home

- `<main>` is the main checkout: the first `worktree` path `git worktree list --porcelain`
  prints. Use it from a worktree too.
- Issues live at `<main>/.dream-team/issues/NNNN-<slug>.md`.
- `NNNN`: four digits, the next free number in that folder, from `0001`.
- `$(git rev-parse --git-common-dir)/info/exclude` has no `/.dream-team/` line → append it before
  the first write.

## When a skill says

- **File an issue:** write a new file in `<main>/.dream-team/issues/`: the title as its first `#`
  line, then a `Status: open` line, then the body in `scope-issue` shape.
- **Read issue `<n>`:** read `<main>/.dream-team/issues/<n zero-padded to four digits>-*.md`.
  - No file matches → stop with "no local issue `<n>`: write it with `scope-issue`, or, if this is
    your own repo, run `setup-dream-team` to mark the clone and use the tracker".
- **Comment:** append the comment under a `## Comments` heading at the end of the file; add the
  heading with the first comment.
- **Close:** set the line to `Status: closed`.
- **Labels, milestones, `Blocked by` checks:** none; skip every step that sets or checks one.
- **Untriaged:** the file is not in `scope-issue` shape → stop with "rewrite issue `<n>` with
  `scope-issue` first".

## The upstream forge

- A commit, MR/PR or anything else pushed cites no local issue: no `Closes` line, no `#<n>`; on
  the forge `#<n>` names an upstream issue.
- An MR/PR → show its description as a draft in chat; push the branch and open the MR/PR only
  once the user confirms.
- The MR/PR merges → close the local issue.
- The user asks for an issue on the upstream tracker → show it as a draft in chat; file it
  upstream only once the user confirms the text.
````
[assistant] The craft-it-loop workflow returned: branch `issue-214-ci-pin-terraform`, one commit "ci: pin Terraform to 1.9.8", gate passed (`terraform fmt -check -recursive`, `terraform validate`), reviewers raised no blocking finding and no nit. Step 6's fold left one commit; `git push -u origin issue-214-ci-pin-terraform` succeeded.


You are the assistant in this session. Take your next step: the MR/PR. You cannot run commands: show the commands you would run and what you would send the user.
