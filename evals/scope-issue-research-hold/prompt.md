---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the scope-issue skill, then answer.

Session so far:
[user] Work on #31, "Research: why resolver CPU rises on the rns hosts every evening". I paste check output as I get it.
[assistant] Read #31: an open `Research:` issue with no comments. `git config --local --type=bool --get dream-team.own` printed `true`. Round 1, Prometheus: cpu user on site1-rns-01 left its baseline at 19:10 and is off at 7 of 9 sites. Hypotheses, ranked: (1) one client prefix sends a query burst; (2) a failing authoritative server stalls recursion; (3) a cron job on the hosts. The check for (1) and (3): the journal on site1-rns-01 around 19:10.
[user] Journal, 19:05-19:15: no cron line in the window; queries from 192.0.2.0/24 go from 40/s to 130/s at 19:09.
[assistant] Round 2: (3) ruled out, no cron line. (1) held: the 192.0.2.0/24 rate triples one minute before the lead. Next check: the request list size over the same window, to test (2).
[user] Request list: flat at 12 through the whole window.


You are the assistant in this session. Take the next step. One check can still run right now: the per-client query rate at the other six affected sites. You cannot run commands: show the commands you would run and the comments you would post.
