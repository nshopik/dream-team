---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the scope-issue skill, then answer.

Session so far:
[user] chrony on ntp1 and ntp2 drifted 40 ms off last week and nobody noticed until a customer called. Why didn't monitoring catch it?
[assistant] Nothing scrapes chrony. node_exporter runs on both hosts, but its chrony collector is off and there is no alert rule on clock offset. Two ways to get the offset into Prometheus: enable node_exporter's built-in chrony collector (one flag, offset and stratum only), or deploy the standalone chrony_exporter (a new service, but it also exports per-source reachability). Either way we then need an alert rule on offset above 10 ms.
[user] Enable the built-in collector, alert on offset above 10 ms for 5 minutes. File the issue for that.
[assistant] This is a clone of an upstream project: `git config --get dream-team.own` printed nothing. `.dream-team/issues/` holds `0001-ntp-pool-size.md`; `.git/info/exclude` has no `/.dream-team/` line.


You are the assistant in this session. Take your next step on the user's last message. You cannot run commands: show the commands you would run, the files you would write and the message you would send the user.
