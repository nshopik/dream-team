---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the scope-issue skill, then answer.

Session so far:
[user] the leap-second smear test failed again on the arm64 runner. Thread with the logs: https://acme-ops.slack.com/archives/C04NTP/p1730981123 and my notes are in https://docs.google.com/document/d/1xYzNtpSmearNotes/edit
[assistant] I read both. The smear test compares against a 24 h linear smear, but the arm64 build links the old libtz that applies a step at 23:59:60. I copied the failing run's output to /home/kris/scratch/smear-arm64.log. The x86 runner uses the system libtz and passes.
[user] file an issue on the public chrony-smear repo for that: arm64 builds should use the same libtz as x86.


Write the issue for the public chrony-smear repo. Output only the issue title on the first line, then the description.
