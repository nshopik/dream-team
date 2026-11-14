---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the build-issue skill, then answer.

Session so far:
[user] /dream-team:build-issue 212
[assistant] Issue #212: a staging `terraform apply` held the shared state lock and blocked a prod hotfix; isolate each environment's state. The MR target is `main`. Triage: one open decision, how to isolate it.
[assistant] AskUserQuestion: "How should #212 isolate environment state?" Options: (1) "Backend per workspace": one root module, partial config per workspace; small diff, but workspaces still share the module and its provider pins. (2) "Root module per environment": `envs/<env>/` each with its own state and lock; moves ~120 resources with `terraform state mv` and repeats the backend block per environment.
[user] Picked: "Root module per environment".


You are the assistant in this session. Take every step up to the step-4 Workflow call. You cannot run commands: show the commands you would run, the files you would write, and the comments you would post.
