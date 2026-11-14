---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the scope-issue skill, then answer.

Session so far:
[user] Last quarter a `terraform apply` in the staging workspace held the shared state lock for 40 minutes and blocked a prod hotfix. I want to stop sharing state between environments.
[assistant] Two ways: keep one root module with workspaces and give each workspace its own backend through partial config (`-backend-config`), or give each environment its own root module under `envs/<env>/` with its own state file and lock. The second means moving ~120 resources with `terraform state mv` and repeating the provider and backend blocks per environment, but no apply in one environment can ever touch another's state or lock.
[user] Own root module per environment; the isolation is worth the duplication. File the issue for the split, milestone 26.12.


You are the assistant in this session. Take your next step on the user's last message. You cannot run commands: show the files you would write, the issue text you would file, or the message you would send the user.
