---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the scope-issue skill, then answer.

Session so far:
[user] the GNSS receiver on the roof of our Tartu office stopped reporting position after last night's firmware update. Ops tracks it as acme/private-ops#41.
[assistant] The receiver switched to multi-constellation mode and now sends $GNGGA; the parser only accepted $GPGGA and dropped every sentence. Fixed on branch gga-any-talker.
[user] what bugs me more: the dashboard kept showing the 23:10 fix as current until someone looked at 09:00. Nobody got alerted for ten hours.
[assistant] The dashboard reads the last stored fix and never looks at its timestamp. The serial reader logs nothing when parse_gga returns None, so a dropped sentence is silent too. There is no alert rule on fix age.
[user] file an issue on the public gnss-mon repo for that: the dashboard should flag a fix older than 60 s and alert after 5 min.


Write the issue for the public gnss-mon repo. Output only the issue title on the first line, then the description.
