# Voltagent agents dream-fixer relies on

**Date:** 2026-10-09 · **Issues:** #190

Source: the subagent `meta.json` of every `dream-fixer-loop` run under
`~/.claude/projects/*/*/subagents/workflows/wf_*`, read by label (`impl:#<n>`,
`review:domain`). 335 runs on 321 issues in 9 repos, 2026-09-21 to 2026-10-09; `workflow-subagent`
and `general-purpose` count as `generic`.

## Voltagent agents implemented 310 of 335 runs

Language agents took 281 runs (84%), each picked by the repo's language.

| Implementer | Runs | Repos |
|---|---|---|
| `voltagent-lang:rust-engineer` | 222 | anyzone-rs, irontap |
| `voltagent-lang:golang-pro` | 38 | dnstap2clck, ixdnssla, resolver-v4 |
| `voltagent-infra:devops-engineer` | 19 | ntp-ix, anyzone-rs, 3 others |
| `voltagent-lang:python-pro` | 12 | dream-team, ubx-exporter, others |
| `voltagent-lang:javascript-pro` | 9 | dream-team |
| other voltagent, 1-2 runs each | 10 | see the next section |
| `generic` | 24 | dream-team, resolver-v4, ntp-ix |
| `doc-writer` | 1 | anyzone-rs |

## Domain review ran as `generic` in 234 of 335 runs

Voltagent types took 69 runs, `none` 14, and other plugins 18 (`feature-dev:code-reviewer` 9,
`gdoc-writer` 4, `pr-review-toolkit:code-reviewer` 3, `dream-team:performance-engineer` 1,
`claude` 1).

| Domain reviewer | Runs |
|---|---|
| `voltagent-qa-sec:performance-engineer` | 16 |
| `voltagent-infra:sre-engineer` | 9 |
| `voltagent-lang:golang-pro` | 7 |
| `voltagent-qa-sec:code-reviewer` | 5 |
| `voltagent-infra:network-engineer` | 5 |
| `voltagent-dev-exp:refactoring-specialist` | 5 |
| other voltagent, 1-3 runs each | 22 |

## No voltagent pick needs its own agent or skill

Every pick maps to an existing dream-team agent, to `generic`, or to `none`. The language
implementers rest on #172 and #193: on opus, voltagent language keyword lists added no hits over
`pr-review-toolkit:code-reviewer`, and the implementer runs behind a build-and-test gate. The
broad-role and platform picks rest on the `MAINTAINING.md` rule against agents for a broad role
or for public platform knowledge.

Picks by outcome, as role and runs:

- **`generic` implementer:** `rust-engineer` 222 (Rust resolver port, dnstap pipeline),
  `golang-pro` 38 (Go services, ClickHouse writer), `devops-engineer` 19 (CI, Ansible roles,
  install scripts, OpenWrt build), `python-pro` 12 and `javascript-pro` 9 (eval runners, hooks,
  workflow JS, an exporter), and 1-2 runs each of `performance-engineer`, `sre-engineer`,
  `readme-generator`, `documentation-engineer`, `network-engineer`, `build-engineer`,
  `tooling-engineer`.
- **`dream-team:performance-engineer`:** voltagent `performance-engineer`, domain 16 (hot-path
  cost, perf-gate harness).
- **`dream-team:sre-engineer`:** voltagent `sre-engineer`, domain 9 (exporters, alert rules, unit
  restarts, dashboards).
- **`dream-team:architect-reviewer`:** voltagent `architect-reviewer`, domain 2 (spec and
  contributor docs); `refactoring-specialist` domain 5 when the diff collapses layers.
- **`docs-reviewer`:** `documentation-engineer` and `technical-writer`, domain 6 (skill and README
  text).
- **`generic` + `domainLens`:** `golang-pro` domain 7 (irontap rows against the Go miekg
  reference), `database-administrator` domain 2 (ClickHouse inserts and schema tests).
- **`none`:** `code-reviewer` domain 5 (the quality panel runs `pr-review-toolkit:code-reviewer`),
  `test-automator` 3 (`pr-test-analyzer` runs on test diffs), `deployment-engineer` 2 and
  `devops-engineer` 1 (#173), `cli-developer` 2, `git-workflow-manager` 1, the other
  `refactoring-specialist` runs.
- **`none`, or `generic` + `domainLens` when a claim is checkable:** `network-engineer` domain 5
  (IPv6 upstreams, NIC firmware, BIRD, ACLs), `security-engineer` and `security-auditor` domain 3
  (socket race, unit hardening, sudoers).

All 17 code-reviewer domain picks (voltagent, `feature-dev`, `pr-review-toolkit`) ran on or
before 2026-10-06, each duplicating the quality panel's `pr-review-toolkit:code-reviewer`; none
ran after the 2026-10-08 rule that sets `none` when no claim is checkable.

## Ruled out

- Fix rounds per implementer type as a quality signal: each language type runs only on repos in
  its language, so a difference measures the repo, not the agent.
- A new implementer A/B: #193 closed it as a likely tie.
