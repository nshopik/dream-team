---
name: tech-debt-triage
description: >-
  Triages tech debt in a repository: ranks hot-spot paths by git log, has dream-team's
  architect-reviewer list refactor and restructuring candidates under the deletion test, has a
  fresh judge subagent on Fable verify each claim in the code and rate it Act now, Later or Skip
  against quality, performance and change cost, files a scope-issue for each Act now item, writes
  an HTML report with one card per Act now item, with before/after Mermaid diagrams where it
  changes structure, and opens it in the browser. Use when the user runs
  /dream-team:tech-debt-triage or asks for a tech-debt triage, an architecture survey, refactor
  candidates or what to restructure in a codebase.
disable-model-invocation: true
argument-hint: "[path ...]"
---

# tech-debt-triage

On pi, launch every Agent as the pi lines at the top of `<base directory>/../qa-review/SKILL.md`
say.

## 1. Scope

- Paths in `$ARGUMENTS` → they are the scope.
- No paths → follow the "Audit map" section of `<base directory>/../qa-review/SKILL.md`; the
  paths it leaves in scope are the scope.
- Rank the scope's files by commits touching them in the last 200 commits; keep the 15
  most-touched that still exist:

```sh
git log -n 200 --format= --name-only -- <scope> | sort | uniq -c | sort -rn
```

## 2. Find

Launch one Agent and wait for its report:

- `subagent_type`: `dream-team:architect-reviewer`.
- `model`: the session model's tier (`opus`, `sonnet`, `haiku` or `fable`), taken from the
  environment section of your system prompt.
- `prompt`: the finder brief below, `<paths>` replaced by the hot-spot paths, one per line.

Finder brief, verbatim:

```
Survey these hot-spot paths for refactor candidates: deletions, merges, splits and moves.
<paths>

Apply the deletion test to each module, function, rule and doc section: imagine deleting it. Complexity vanishes → a candidate. Complexity reappears across its callers → it earns its place.
Your job is coverage: list every candidate, including uncertain ones; a judge verifies each claim in the code later.
Read only: do not edit, create or delete files; no builds, test runs or network.
Output: one line per candidate and nothing else: `C<n> | <claim, one sentence> | <file:line, comma-separated> | <what the change removes or fixes>`.
```

- No candidate lines → say so and stop.

## 3. Judge

Launch one Agent in a fresh context and wait for its verdict lines:

- `subagent_type`: `general-purpose`.
- `model`: `fable`.
- `prompt`: the judge brief below, `<repo>` replaced by the repository path, a blank line, then
  the finder's candidate lines.

- Fable unavailable (the launch errors) → stop and ask the user whether to run the judge on
  `opus` at `effort` `xhigh`.
- On pi → stop and ask the user whether to run the judge as a fresh `worker` on pi's model.

Judge brief, verbatim:

```
You triage technical debt. Debt is code that no longer fits the task it serves. Its principal is the cost of the fix. Its interest is what the code costs while it stays: defects users hit, and time lost on each change to it. Code that changes often charges the most interest; stable code charges little, even when it is ugly. Your job is to pay the debt whose interest exceeds its principal now, schedule the rest, and drop claims that are not debt at all.

Judge the refactor candidates below for the repository at <repo>. Another agent listed them; about half of such claims are overstated or wrong. Verify each claim in the code before you rate it.
Read only: do not edit, create or delete files; no builds, test runs, forge or network.

For each candidate:
- Read every cited file:line and the callers, tests and docs the claim depends on.
- Rate the change's effect on each pillar: + better, = no change, - worse.
  - quality: does the code deliver what was promised? A change that removes a defect a user or agent hits is +.
  - performance: a veto only. Rate - when the change slows a path that runs often, otherwise =; never +.
  - change cost: the interest a tangled flow charges agents and humans on every read and edit. Count the files and hops one must read to follow or change the flow, before against after.
- Act now: the claim holds, and the change removes a defect in the code today (code, docs and callers disagree, or a result lacks what its consumers read) or deletes a restatement of a source of truth, with no pillar -. A defect the repo's normal setup triggers counts before anyone hits it.
- Later: the claim holds, but the defect is hypothetical (nothing in the code disagrees today), only a rare environment triggers it and it loses no data, opens no security hole and causes no crash without recovery, or the payoff waits on other work.
- Skip: the claim does not hold (the code differs on purpose, a test already pins it, it is already done), or the change adds a concept (a module, type, router, table, file) or adds files or hops to follow a flow without removing a known defect.

Output: one line per candidate and nothing else: `<id> | <Act now, Later or Skip> | Q<+,= or -> P<= or -> C<+,= or -> | <file:line of your evidence> | <evidence, one line>`.
```

- The judge errors or returns no verdict lines → stop and report a judge failure; write no report.
- A candidate with no verdict line → Skip, evidence "not judged".

## 4. File

- List the repository's open issues as `#N title` lines; forge unreachable → file nothing, say so
  in chat.
- An Act now item an open issue covers → file nothing, note `#N` for its report card.
- Each other Act now item → load `scope-issue` and file one issue from its claim and the judge's
  evidence.
- Never file a Later or Skip item.

## 5. Report

Write one HTML file to `<scratchpad>/tech-debt-triage-<repo name>.html`, or `/tmp/` when you
have no scratchpad; `<report dir>` below is that directory. Copy the layout and inline CSS of
[report-template.html](report-template.html), never Tailwind or another stylesheet:

- Header: repository name and short SHA, date, scope, candidate count, verdict counts as
  `.legend` anchor badges, Q/P/C legend.
- Overview diagram: a Mermaid `flowchart TD`, one node per hot-spot source file with a verdict,
  the test files merged into one node, an edge where one file calls into another, dashed from
  the tests node.
- Scope spans more than one directory → one subgraph per directory.
- Colour each overview node by the most urgent verdict citing it, with these lines:

```
classDef act fill:#d1fae5,stroke:#047857,stroke-width:2px
classDef later fill:#fef3c7,stroke:#b45309
```

- Act now: one card per item, in this order: id, short title, issue badge, Q/P/C badge, cited
  file:line list, before/after diagrams, then Problem, Fix, the judge's Evidence and up to
  three Wins bullets of six words at most.
- Issue badge: `b-act` and `#N · filed` for an issue this run filed; `b-cov` and
  `#N · covered by open issue` for one already open.
- Write the short title, Problem, Fix and Wins from the finder claim and the judge evidence.
- Act now item that changes structure (call flow, ownership, file placement) → before and after
  Mermaid `flowchart TD` diagrams in the card's `.ba` panes.
- Any other Act now item → no diagram.
- Diagram node label: at most two short lines, no rhombus decision nodes.
- Mark the defect in a before diagram with
  `classDef gap stroke:#dc2626,stroke-width:2px`.
- Later: one `ul.list` entry per item: id, Q/P/C, claim, evidence, file:line list.
- Skip: the same entries inside the `<details>` element.
- HTML-escape `&`, `<` and `>` in every text value and `<pre class="mermaid">` source.
- Give each diagram a unique id: `overview`, `c<n>-before`, `c<n>-after`.
- Start every diagram source with this line:

```
%%{init: {"htmlLabels": false, "themeVariables": {"fontSize": "12px"}, "flowchart": {"htmlLabels": false, "curve": "basis", "nodeSpacing": 30, "rankSpacing": 40, "diagramPadding": 8, "padding": 12}}}%%
```

- `mmdc` on `PATH` → `mkdir -p <report dir>/diagrams`, empty it with `rm -f` on its literal
  path plus `/*`, save each diagram as `<report dir>/diagrams/<id>.mmd`, render them with the
  loop below, and inline each SVG in its `.fig` slot; the file then loads no script.
- No `mmdc`, or a diagram with no `.svg` after the loop → put that diagram's source in a
  `<pre class="mermaid">` at its slot and end the file with the CDN script below.

```sh
for f in <report dir>/diagrams/*.mmd; do
  s=${f%.mmd}.svg
  mmdc -q -i "$f" -o "$s" -I "$(basename "$f" .mmd)" || continue
  set -- $(grep -om1 'viewBox="[^"]*"' "$s" | tr -c '0-9.\n' ' ')
  perl -0pi -e "s/width=\"100%\"/width=\"${3%.*}\" height=\"${4%.*}\"/;" \
    -e 's/ xmlns[:a-z]*="[^"]*"//g' "$s"
done
```

```html
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.esm.min.mjs';
mermaid.initialize({ startOnLoad: true });
</script>
```

Open the file: `explorer.exe "$(wslpath -w <file>)"` on WSL, `open <file>` on macOS,
`xdg-open <file>` on other Linux; run it in the background and ignore its exit code; none
available → the chat reply's path is enough.

Then reply in chat:

```
- **Report:** <absolute path of the HTML file>
- **Verdicts:** <n> Act now, <n> Later, <n> Skip
- **Filed:** #N <title>, ... (or none)
```
