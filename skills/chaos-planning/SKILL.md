---
name: chaos-planning
description: >-
  Reviews a launch's failure-experiment plan (chaos plan, game day, resilience tests) for missing
  experiments across infrastructure, application, data, security and hardware faults, and for
  experiments lacking a hypothesis, injection, blast radius or pass criterion; reports the gaps in
  chat and edits nothing unless the user says yes. Use when the user asks to review, check or
  fill gaps in a chaos engineering plan, failure-injection plan, fault-injection plan, game day
  plan or a launch's resilience or failover tests.
---

# chaos-planning

- Never run an experiment or inject a fault.

## 1. Get the plan

- The user named a file path → read it.
- The user named an issue → read it and its comments.
- The user pasted the plan → use the pasted text.
- No plan given → ask for one and stop.

## 2. Read what the plan names

- Read the code, config, runbooks and topology the plan names, and the repo's deploy config.
- Note each component, dependency, data store and host the system has but the plan never
  mentions.

## 3. Check each planned experiment

Every experiment needs four fields:

- **Hypothesis:** the steady state that holds while the fault is active, in a control group and
  an experimental group; RED (rate, errors, duration) for a service, USE (utilization,
  saturation, errors) for a resource.
- **Injection:** the exact fault, where it is injected, and how.
- **Blast radius:** what the fault can reach, and the limit and abort that contain it.
- **Pass criterion:** the observed result that confirms or refutes the hypothesis.
- An experiment missing any of the four → list it with the missing fields.
- Judge the four fields against the two lists below; they are not faults to cover.

Experiment design:

- Hypothesis formulation
- Steady state metrics
- Variable selection
- Blast radius planning
- Safety mechanisms
- Rollback procedures
- Success criteria
- Learning objectives

Blast radius control:

- Environment isolation
- Traffic percentage
- User segmentation
- Feature flags
- Circuit breakers
- Automatic rollback
- Manual kill switches
- Monitoring alerts

## 4. Check coverage

- Walk every fault list below against the system read in step 2.
- A fault the system can suffer that no experiment covers → a missing experiment.
- Skip a fault the system cannot suffer (no database → no replication lag).
- Write each missing experiment with all four fields, specific to the system.

Failure injection strategies:

- Infrastructure failures
- Network partitions
- Service outages
- Database failures
- Cache invalidation
- Resource exhaustion
- Time manipulation
- Dependency failures

Infrastructure chaos:

- Server failures
- Zone outages
- Region failures
- Network latency
- Packet loss
- DNS failures
- Certificate expiry
- Storage failures

Hardware faults:

- Power feed or PSU loss
- Fan failure and overheating
- Disk failure and degraded RAID
- NIC or link down
- Optic or transceiver failure
- Link flap
- Memory ECC errors
- BMC or out-of-band loss
- Clock and NTP drift
- Whole-host power cycle

Application chaos:

- Memory leaks
- CPU spikes
- Thread exhaustion
- Deadlocks
- Race conditions
- Cache failures
- Queue overflows
- State corruption

Data chaos:

- Replication lag
- Data corruption
- Schema changes
- Backup failures
- Recovery testing
- Consistency issues
- Migration failures
- Volume testing

Security chaos:

- Authentication failures
- Authorization bypass
- Certificate rotation
- Key rotation
- Firewall changes
- DDoS simulation
- Breach scenarios
- Access revocation

Advanced techniques:

- Combinatorial failures
- Cascading failures
- Byzantine failures
- Split-brain scenarios
- Data inconsistency
- Performance degradation
- Partial failures
- Recovery storms

## 5. Report

- Report in chat only; write no file.
- One bullet per incomplete experiment: `- **<experiment>:** missing <fields>`.
- One bullet per missing experiment: `- **<experiment>:** hypothesis <…>; injection <…>; blast
  radius <…>; pass <…>`.
- Group the missing experiments under the list name they came from, as a `**<list>:**` line.
- No blank lines between bullets.
- Nothing missing → say so in one line.
- Offer to add the missing experiments and fields to the plan.
- Edit nothing without the user's yes.
