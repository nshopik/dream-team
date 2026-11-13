---
name: tech-debt-triage
description: >-
  Triages tech debt in a repository: ranks hot-spot paths by co-change and commit counts, has
  dream-team's architect-reviewer list file clusters tied by one structural flaw, has a fresh judge
  subagent on Fable verify each claim in the code and rate it Act now, Later or Skip by a defect
  tier and a co-change interest tier, files the Act now items per scope-issue,
  light-tier ones in one bundle issue, writes an HTML report with one card per Act now item, with
  before/after diagrams where it changes structure, and opens it in the browser. Use when the
  user runs /dream-team:tech-debt-triage or asks for a tech-debt triage, an architecture survey,
  refactor candidates or what to restructure in a codebase.
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
- List the scope's co-changed file pairs over the last 200 commits, one line per pair:

```sh
git log -n 200 --format=%x00 --name-only -- <scope> | python3 -c '
import collections, itertools, sys
skip = {"CHANGELOG.md", ".claude-plugin/plugin.json", "package.json"}
commits = [set(c.split("\n")) - {""} for c in sys.stdin.read().split("\0")]
commits = [c - skip for c in commits if len(c) <= 30]
n = collections.Counter(f for c in commits for f in c)
pairs = collections.Counter(p for c in commits for p in itertools.combinations(sorted(c), 2))
for (a, b), s in pairs.most_common():
    pct = round(200 * s / (n[a] + n[b]))
    if s >= 5 and pct >= 30:
        print(f"{a}, {b} | {s} shared | {pct}%")
'
```

- Add the repository's other version files, which every release touches, and its dependency
  manifests and lockfiles (`go.mod`, `go.sum`, `package-lock.json`, `Cargo.toml`, `Cargo.lock`,
  `pyproject.toml`, `uv.lock`, `poetry.lock`), which every dependency bump touches together, to
  `skip`.
- Rank the scope's files by their summed shared commits across the pair lines, then the rest by
  commits touching them in the last 200 commits; keep the first 15 that still exist and are not
  in `skip`:

```sh
git log -n 200 --format= --name-only -- <scope> | sort | uniq -c | sort -rn
```

## 2. Find

Launch one Agent and wait for its report:

- `subagent_type`: `dream-team:architect-reviewer`.
- `model`: the session model's tier (`opus`, `sonnet`, `haiku` or `fable`), taken from the
  environment section of your system prompt.
- `prompt`: the finder brief below, `<paths>` replaced by the hot-spot paths, one per line, and
  `<pairs>` by the step-1 pair lines, or `none`.

Finder brief, verbatim:

```
Survey these hot-spot paths for structural debt: clusters of one or more files tied by one flaw.
<paths>

Co-change pairs, last 200 commits (both files, commits that changed both, that count as a share of the two files' mean commit count):
<pairs>

Look through four lenses:
- Seam leak: a module reads another's private state or repeats its rule. The same formula, constant or rule on both sides of a language or layer boundary (a test and the code it tests, an exporter and the page that reads its output) is a leak, and copies that disagree are a defect.
- Locality: following one flow means opening many files; one concept is spread across modules.
- Test reach: behaviour no test reaches through the interface, or a test that passes only through an unrelated path, such as an external tool's failure.
- Change coupling: files the pair lines show changing together.
A candidate is a cluster: its files, the flaw that ties them, and the symptoms the flaw causes (a stale doc, a repeated constant, a private-field read) grouped under it. A cluster may be one file when its flaw is in code. A single doc or comment line is never a candidate on its own.
Read only: do not edit, create or delete files; no builds, test runs or network.
Output: one line per cluster and nothing else: `C<n> | <the flaw and the change that fixes it, one sentence> | <file:line, comma-separated> | <symptoms, semicolon-separated>; <shared commits from the cluster's pair lines, or no pair>`.
```

- No candidate lines → say so and stop.

## 3. Judge

Launch one Agent in a fresh context and wait for its verdict lines:

- `subagent_type`: `general-purpose`.
- `model`: `fable`.
- `prompt`: the judge brief below, `<repo>` replaced by the repository path, a blank line, the
  finder's candidate lines, a blank line, `Co-change pairs, last 200 commits:`, then the step-1
  pair lines, or `none`.

- Fable unavailable (the launch errors) → stop and ask the user whether to run the judge on
  `opus` at `effort` `xhigh`.
- On pi → stop and ask the user whether to run the judge as a fresh `worker` on pi's model.

Judge brief, verbatim:

```
You triage technical debt. Debt is code that no longer fits the task it serves. Its principal is the cost of the fix. Its interest is what the code costs while it stays: defects users hit, and time lost on each change to it. Code that changes often charges the most interest; stable code charges little, even when it is ugly. Your job is to pay the debt whose interest exceeds its principal now, schedule the rest, and drop claims that are not debt at all.

Judge the refactor candidates below for the repository at <repo>. Another agent listed them; about half of such claims are overstated or wrong. Verify each claim in the code before you rate it. The co-change pair lines after the candidates give, per file pair, the commits of the last 200 that changed both files, and that count as a share of the two files' mean commit count.
Read only: do not edit, create or delete files; no builds, test runs, forge or network.

For each candidate:
- Read every cited file:line and the callers, tests and docs the claim depends on.
- Rate the change's effect on each pillar: + better, = no change, - worse.
  - quality: does the code deliver what was promised? A change that removes a defect a user or agent hits is +.
  - performance: a veto only. Rate - when the change slows a path that runs often, otherwise =; never +.
  - change cost: the interest a tangled flow charges agents and humans on every read and edit. Count the files and hops one must read to follow or change the flow, before against after.
- Check two tiers:
  - Defect: a named test or consumer gets a wrong result today in the repository's normal setup; cite the line where it diverges.
  - Interest: a pair line names two of the candidate's files with at least 5 shared commits, and the change cuts the files a typical change there must touch from H to H' < H; count H and H' in the code.
- Act now: the claim holds, a tier holds today, and no pillar is -.
- Later: the claim holds, but its tier holds only once other work lands, or only a rare environment triggers its defect and that defect loses data, opens a security hole or causes a crash.
- Skip: the claim does not hold (the code differs on purpose, a test already pins it, it is already done), or neither Act now nor Later holds.
- A new module is no reason to Skip unless it has one adapter, H' is not below H and the Defect tier fails.

Output: one line per candidate and nothing else: `<id> | <Act now, Later or Skip> | Q<+,= or -> P<= or -> C<+,= or -> | <file:line of your evidence> | <evidence, one line>`.
```

- The judge errors or returns no verdict lines → stop and report a judge failure; write no report.
- A candidate with no verdict line → Skip, evidence "not judged".

## 4. File

- List the repository's open issues as `#N title` lines; forge unreachable → file nothing, say so
  in chat.
- An Act now item an open issue covers → file nothing, note `#N` for its report card.
- The other Act now items → load `scope-issue` and file them per it, each item from its claim and
  the judge's evidence.
- Never file a Later or Skip item.

## 5. Report

Write one HTML file to `<scratchpad>/tech-debt-triage-<repo name>.html`, or `/tmp/` when you
have no scratchpad; `<report dir>` below is that directory. Copy the layout and inline CSS of
[report-template.html](report-template.html), never Tailwind or another stylesheet:

- Header: repository name and short SHA, date, scope, candidate count, verdict counts as
  `.legend` badges (Act now and Later as anchors, Skip as a count only), Q/P/C legend.
- Act now: one card per item, in this order: id, short title, issue badge, Q/P/C badge, cited
  file:line list, before/after diagrams, Problem, Fix, then up to three wins of six words at most
  as plain `ul.wins` bullets, no label.
- Issue badge: `b-act` and `#N · filed` for an issue this run filed; `b-cov` and
  `#N · covered by open issue` for one already open.
- Write the short title, Problem, Fix and wins from the finder claim and the judge evidence.
- Act now item that changes call flow, ownership or file placement → before and after
  Mermaid `flowchart TD` diagrams in the card's `.ba` panes.
- Any other Act now item → no diagram.
- Diagram node label: at most two short lines, no rhombus decision nodes.
- Mark the defect in a before diagram with
  `classDef gap stroke:#dc2626,stroke-width:2px`.
- Later: one `ul.list` entry per item: id, Q/P/C, claim, evidence, file:line list.
- Skip: no entries in the report.
- HTML-escape `&`, `<` and `>` in every text value and `<pre class="mermaid">` source.
- Give each diagram a unique id: `c<n>-before`, `c<n>-after`.
- Start every diagram source with this line:

```
%%{init: {"htmlLabels": false, "themeVariables": {"fontSize": "12px"}, "flowchart": {"htmlLabels": false, "curve": "basis", "nodeSpacing": 30, "rankSpacing": 40, "diagramPadding": 8, "padding": 12}}}%%
```

- `mmdc` on `PATH` → `mkdir -p <report dir>/diagrams`, empty it with `rm -f` on its literal
  path plus `/*`, save each diagram as `<report dir>/diagrams/<id>.mmd`, render them with the
  loop below, and inline each SVG in its `.fig` slot; the file then loads no script.
- No Mermaid diagram in the report → skip the loop and the CDN script.
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
