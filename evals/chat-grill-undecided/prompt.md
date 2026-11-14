---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the scope-issue skill, then answer.

Session so far:
[user] Last week the canary node in the anycast resolver pool kept announcing 192.0.2.53/32 while its resolver returned SERVFAIL for 20 minutes; a third of the queries in that region failed. I want the canary to stop attracting traffic when it breaches its SLO.
[assistant] The route comes from bird on the canary, which announces the /32 whenever the loopback is up; nothing ties it to resolver health. How a breach should reach the route is open: who evaluates the SLO, how bird learns of the breach, and what the route does if the evaluator itself dies. The repo has no existing pattern for any of it.
[user] Not sure how it should work yet. File the issue for it.


You are the assistant in this session. Take your next step on the user's last message. You cannot run commands: show the issue text you would file, or the message you would send the user.
