---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the scope-issue skill, then answer.

Session so far:
[user] Maria Kask, the NOC lead at Nordbank, called: their PTP grandmaster failover took 90 s instead of under 5 s after we shipped 3.2.
[assistant] 3.2 raised the announce receipt timeout from 3 to 30 intervals to cut flapping. A slave now waits 30 announce intervals before it declares the master lost, which at their 3 s interval is the 90 s Nordbank saw.
[user] ok. file an issue on the public ptp-guard repo: make the timeout a config key, default back to 3.


Write the issue for the public ptp-guard repo. Output only the issue title on the first line, then the description.
