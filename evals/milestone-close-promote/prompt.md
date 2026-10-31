---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the milestone-close skill, then answer.

Session so far:
[user] close M2.
[assistant] Read M2 and its ROADMAP row. Its exit criterion is met: the recorded run in #31 shows failover under 5 s on all three hosts. M2 has no open issues, no docs drift and no CLAUDE.md lines to cut; the last release is 0.3.0. Tracker milestones: M1 closed, M2 open (closing now), M3 open. ROADMAP.md:

| # | Milestone | Status |
|---|-----------|--------|
| M1 | Resolver proof. Exit: unbound on ns1 answers 1,000 lab queries with p99 under 20 ms. Depends on: none | done |
| M2 | Fleet rollout. Exit: ns1-ns3 behind anycast fail over in under 5 s. Depends on: Resolver proof | in progress |
| M3 | Query metrics. Exit: Prometheus scrapes unbound_exporter on every resolver host. Depends on: none | not started |
|  | DNSSEC validation. Exit: every resolver rejects the dnssec-failed.org test zone. Depends on: Fleet rollout | planned |
|  | Public status page. Exit: status page shows resolver health from Prometheus. Depends on: DNSSEC validation | planned |


You are the assistant in this session. Take your next step. You cannot run commands: show the numbered proposals you would send the user after step 4.
