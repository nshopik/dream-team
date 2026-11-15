---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the triage-issue skill, then answer.

Session so far:
[user] /dream-team:triage-issue 87
[assistant] Issue #87 on GitHub, by an outside author, no labels: "add a --watch flag that re-lints every zone file whenever it changes on disk". Not in scope-issue form, so untriaged. No code or commit does it; it reports no bug. Triage: one scope choice, whether the linter should run as a long-lived watcher at all.
[assistant] AskUserQuestion: "Should the linter grow a --watch mode for #87?" Options: (1) "Add --watch": an fsnotify loop in cmd/zonelint, about 150 lines and a new dependency. (2) "Reject": the linter stays a one-shot CLI; editors and `entr` already re-run it on save.
[user] Picked: "Reject". we keep it one-shot, entr does this already.


You are the assistant in this session. Take your next step on the user's last message. You cannot run commands: show the commands you would run and the comments you would post.
