---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the cut-milestones skill, then answer.

Session so far:
[user] The spec for the DNS resolver project is approved (docs/specs/resolver.md). It has three stages:
- Resolver proof: unbound on ns1 answers 1,000 queries from the lab client with a p99 under 20 ms. Depends on nothing.
- Fleet rollout: unbound on ns1, ns2 and ns3 behind anycast, with failover under 5 s when one host stops. Depends on Resolver proof.
- Query metrics: unbound_exporter on every resolver host, scraped by Prometheus, with a dashboard of query rate and cache hit ratio. Depends on nothing.
The tracker has no milestones yet and the repo has no ROADMAP. Every placeholder is settled; the draft above is approved.
[user] cut the milestones.


You are the assistant in this session. Take your next step on the user's last message. You cannot run commands: show the tracker milestones you would create and the ROADMAP.md you would write.
