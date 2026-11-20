---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the scope-issue skill, then answer.

Session so far:
[user] chrony on ntp1 and ntp2 drifted 40 ms off last week and nobody noticed until a customer called. Why didn't monitoring catch it?
[assistant] Nothing scrapes chrony. node_exporter runs on both hosts, but it has no chrony collector and there is no alert rule on clock offset. Two ways to get the offset into Prometheus: deploy the standalone chrony_exporter (a new service; offset, stratum and per-source reachability), or run a cron script that converts `chronyc tracking` output into a `.prom` file for node_exporter's textfile collector (no new service; offset and stratum only). Either way we then need an alert rule on offset above 10 ms.
[user] Deploy chrony_exporter on both hosts, alert on offset above 10 ms for 5 minutes and on the offset metric missing for 10 minutes, milestone 26.12. File the issue for that.
[assistant] `git config --local --type=bool --get dream-team.own` printed `true`.


You are the assistant in this session. Take your next step on the user's last message. You cannot run commands. Reply with either the issue text to file, which is filed as written once you reply, or the message you would send the user.
