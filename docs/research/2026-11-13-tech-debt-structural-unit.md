# The unit of structural tech debt

**Date:** 2026-11-13 · **Issues:** #468, #448, #456

This note sets what `tech-debt-triage` should report, as shipped at main `5b7bd42`. A real run on a
15-file Go package gave 8 Act now items, all stale doc lines and comments. An architecture review
of the same package found 5 structural candidates. Co-change counts below come from the last 200
non-merge commits of this repo at `5b7bd42`.

## The unit is a file cluster and the flaw that ties it, not a line

Structural debt lives in groups of files, so the report item is the group. Ernst et al. surveyed
1,831 practitioners: architectural decisions are the largest source of debt, and code-level tools
do not track it. Xiao, Cai and Kazman define an architectural debt as an anchor file plus the files
tied to it by a flawed relation (hub, anchor-submissive, anchor-dominant, modularity violation).
They measure its interest as the bug-fix churn of the whole group. Modularity violations, files
that co-change with no structural dependency, cost the most. Kruchten, Nord and Ozkaya record a
debt item with its consequences if left; a one-line nit has no consequence a backlog owner weighs.

An item is therefore: the cluster's files, the flaw that ties them (a leaking seam, a rule in
several places, behaviour tests cannot reach), the symptoms grouped under it (stale doc, repeated
constant, private-field read), and its tier evidence below. The Go run split 4 such items into
one-line symptoms and the judge dropped each piece alone.

## Finder brief: four lenses, one line per cluster

The finder should look for clusters through four lenses and give up coverage of single lines:

- Seam leak (Feathers, Ousterhout's information leakage): a module reads another's private state
  or repeats its rule. Example from the Go run: a prober reads the state machine's private fail
  counter and repeats its withdraw threshold.
- Locality: following one flow means opening many files; one concept is spread across modules.
- Test reach (Feathers: a seam is where behaviour can be changed for a test): behaviour no test
  reaches through the interface, or a test that passes through an unrelated path. Example: a test
  that passes only through an external tool's failure path.
- Change coupling (Tornhill; Mo et al.'s implicit cross-module dependency): files that change in
  the same commits. Give the finder the counts; it cannot compute them read-only.

Output: one line per cluster with its files, flaw, grouped symptoms and co-change count. A single
doc or comment line is not a candidate on its own. Tracked in #472.

Step 1's hot-spot rank by change count alone puts doc files first. Tornhill ranks by change
frequency weighted by complexity, and change coupling by pairs. Use code-maat's defaults as the
start: at least 5 shared commits, at least 30% coupling, commits of 30 files or fewer. On this repo
they give 32 pairs; the top ones are process coupling, not design:

| Pair | Shared | Coupling |
|---|---|---|
| CHANGELOG.md, skills/dream-fixer/SKILL.md | 34 | 41% |
| .claude-plugin/plugin.json, package.json | 18 | 100% |
| workflows/dream-fixer-loop.js, workflows/test_simplify.mjs | 17 | 85% |
| skills/dream-fixer/reference/workflow-result.md, workflows/dream-fixer-loop.js | 10 | 59% |
| skills/review-bench/METHODOLOGY.md, skills/review-bench/SKILL.md | 9 | 75% |

Leave out files every change touches by policy (CHANGELOG, version files) before ranking.

## Severity: two tiers, each a read-only check

Each verdict must rest on a check the judge can run by reading:

- **Defect:** a named test or consumer gets a wrong result today, cited at the line where it
  diverges.
- **Interest:** the cluster co-changed in at least K of the last 200 commits, and the files a
  typical change in it must touch fall from H to H' < H.
- Below both tiers: not reported.

Either tier → Act now. A tier that holds only once other work lands → Later. Neither → Skip, and
the report leaves it out. This replaces "hypothetical defect → Later", which sent the Go run's top
structural candidate to Later: a change-cost item now earns Act now through the Interest tier
alone. Start K at 5, code-maat's default; calibrate K and the H drop on the #470 cases. Tracked
in #471.

## Judge: allow a new module when it removes knowledge callers carry

Replace the Skip for a change that "adds a concept" with Ousterhout's test: a deep module adds a
name but removes what callers must know. Skip a new module only when it has one adapter (a
hypothetical seam, in the codebase-design vocabulary) and H' is not below H. Tracked in #471.

## Nits leave tech-debt-triage

A nit is an item below both tiers; qa-review, docs-reviewer and ponytail-audit catch it at diff
time, so the triage reports nothing for it and needs no batch. A doc restatement is not a nit by
file type: METHODOLOGY.md and SKILL.md in review-bench co-changed 9 times at 75%, so the
restatement meets the Interest tier. This reverses the #459 rule that a stale doc line stays Act
now, and answers #456: no batch issue and no apply step.

## Eval cases

Relabel `dream-team-66a2f62` against the tiers, and add fixtures that the code settles. Tracked in
#470.

| Case | Now | Tier | New |
|---|---|---|---|
| C2 stage-failure results omit `degraded` | Act now | Defect: dream-fixer reads it | Act now |
| C4 MAINTAINING restates README | Act now | Interest: 23 shared, 55% | Act now |
| C7 METHODOLOGY restates SKILL | Act now | Interest: 9 shared, 75% | Act now |
| C11 stale jit-context docstring | Act now | neither | Skip |
| Fixture: prober reads private fail counter | none | Interest or Defect | Act now |
| Fixture: test passes via external tool failure | none | Defect | Act now |
| Fixture: stale comment in each fixture | none | neither | Skip |

C4 and C7 hold only when the judge prompt carries the co-change counts.

## Open: calibrated K and H drop

The starting K of 5 is code-maat's default, not measured on triage runs. #470 supplies the cases;
#471 calibrates against them.

## Ruled out

- Change count alone as the hot-spot rank: a doc file outranks a coupled code cluster.
- A finder candidate cap: the unit change removes the one-line flood; #455 rejected a cap.
- A batch issue for mechanical items (#456): items below both tiers are not reported.

## Sources

- [Ernst et al., Measure It? Manage It? Ignore It?, FSE 2015](https://sei.cmu.edu/library/measure-it-manage-it-ignore-it-software-practitioners-and-technical-debt)
- [Xiao, Cai, Kazman et al., Identifying and Quantifying Architectural Debt, ICSE 2016](https://personal.stevens.edu/~lxiao6/papers/ICSE-16-Debt.pdf)
- [Mo, Cai, Kazman, Xiao, Hotspot Patterns, WICSA 2015](https://apps.dtic.mil/sti/pdfs/ADA621415.pdf)
- [Kruchten, Nord, Ozkaya, Managing Technical Debt](https://www.oreilly.com/library/view/managing-technical-debt/9780135646052)
- [Tornhill, Change Coupling](https://codescene.com/blog/change-coupling-visualize-the-cost-of-change)
- [code-maat](https://github.com/adamtornhill/code-maat)
- Ousterhout, A Philosophy of Software Design, 2nd ed., chapters 4 and 5.
- Feathers, Working Effectively with Legacy Code, chapter 4.
