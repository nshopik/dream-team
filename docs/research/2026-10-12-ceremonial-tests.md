# test-coverage-reviewer and ceremonial tests

**Date:** 2026-10-12 · **Issues:** #236

This note checks whether test-coverage-reviewer flags tests that run and pass but would not fail
on a plausible bug. Two CoreDNS cases from the Rust and Go sweep get one extra commit each with
four such tests, one per shape: a mock that echoes its configured value, a no-error-only check,
inputs that never reach the code the test names, and a copy of existing cases. c1 is g2 (rewrite
EDNS0 `revert`) plus `plugin/rewrite/edns0_revert_test.go`. c2 is g1 (proxyproto) plus
`plugin/pkg/proxyproto/proxyproto_test.go` and `plugin/proxyproto/allow_test.go`; c2 also adds one
real test, `TestReadFromUsesProxySource`. The lens is dream-team `a08bf83`, run alone, headless
`claude -p` on Opus at effort high, 3 runs per case, $3.99 in total. Each injected test passed
every one-line mutant aimed at its path; a subagent graded the reports against that ledger.

## The lens flags every ceremonial test in every run

It flags all four shapes in 3 of 3 runs on each case, 24 of 24, and credits none as coverage.
Each flag says why the test does not protect the behaviour, for example "calls a fake rule that
just returns what it was given. No production code runs." and "passes a plain *net.UDPAddr, so
the *Addr unwrap branch never runs". It also flags weak checks in the upstream tests, which nobody
injected:

- c1 `TestRewriteEDNS0Revert` appends `fromOpts` to the response after `ServeDNS` and asserts a
  `SetDo` value it set itself: 3 of 3 runs.
- c1 `TestEdns0MultiRule` NSID revert rows pass with or without revert: 3 of 3 runs. Dropping
  the NSID replace-revert response rule passes every test in the package.
- c2 `TestSetup` checks only that a policy is set, not which one: 3 of 3 runs.

## The lens names the break a kept test catches when that test covers the change

On c1 every run says which existing test fails for which break in the revert path, and each
claim matches a mutant: `TestEdns0MultiRule` fails on all three revert mutants,
`TestRewriteEDNS0Revert` on two. A one-line break the test would miss comes with 8 of the 12 c2
flags and 3 of the 12 c1 flags. On c2 no run names a break that the real
`TestReadFromUsesProxySource` catches; two runs name a gap next to it. The lens does this without
a prompt line asking for it.

## No test-coverage-reviewer change

The lens misses no shape, so the proposed "name a break for every added test" line was not run on
a second case or on unbound pull request 1525, and no change issue is filed.

## Ruled out

- A prompt line for ceremonial tests: no miss to fix on either case.
