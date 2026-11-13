# 3. Alert on withdrawals, not on probe failures

Status: accepted

## Context

A single failed probe is noise: the state machine absorbs it. An operator needs to know when a
prefix actually leaves the routing table, and when one flaps.

## Decision

Export `watchdog_withdrawals_total{af}` and `watchdog_probes_total{af,result}`. Page on
`increase(watchdog_withdrawals_total[10m]) > 2` per address family; graph the probe failure ratio
from `watchdog_probes_total` but do not page on it.

## Consequences

The prober must count a withdrawal exactly once per flip to down.
