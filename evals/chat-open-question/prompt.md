---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the scope-issue skill, then answer.

Session so far:
[user] chrony on ntp1 and ntp2 drifted 40 ms off last week and nobody noticed until a customer called. Why didn't monitoring catch it?
[assistant] Nothing scrapes chrony. node_exporter runs on both hosts, but its chrony collector is off and there is no alert rule on clock offset. Two ways to get the offset into Prometheus: enable node_exporter's built-in chrony collector (one flag, offset and stratum only), or deploy the standalone chrony_exporter (a new service, but it also exports per-source reachability). Either way we then need an alert rule on offset above 10 ms.
[user] ok, file an issue for that.


You are the assistant in this session. Take your next step on the user's last message. You cannot run commands: show the issue text you would file, or the message you would send the user.
