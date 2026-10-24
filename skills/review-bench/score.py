#!/usr/bin/env python3
"""Scores reviewer runs against a findings ledger; see METHODOLOGY.md.

Usage: python3 score.py <ledger.json> <marks.txt>
Reads each run's reviewer, model, effort and cost from <dir of marks.txt>/<run>/stats.txt.
"""
import json
import random
import re
import statistics
import sys
from pathlib import Path

WEIGHT = {"critical": 10, "important": 4, "performance": 3, "test": 3, "minor": 1}
B = 2000

ledger = json.load(open(sys.argv[1]))
weight = {}
for r in ledger["rows"]:
    w = 0.5 if r["severity"] == "minor" and r["nit"] else WEIGHT[r["severity"]]
    weight[r["id"]] = w * (0.5 if r["plausible"] else 1)
crit = [r["id"] for r in ledger["rows"] if r["severity"] == "critical"]

runs = {}  # run -> {id: best credit across its lenses}
rejected = {}  # run -> refuted claims
for line in open(sys.argv[2]):
    m = re.match(r"Rejected \(([^)]*)\)", line)
    if m:
        for run in {t.strip().split(".")[0] for t in m[1].split(",")}:
            rejected[run] = rejected.get(run, 0) + 1
    toks = line.split()
    if not toks or not re.match(r"[A-Za-z0-9-]+-r\d", toks[0]):
        continue
    m = re.fullmatch(r"([A-Za-z0-9-]+-r\d+)(\.\S+)?", toks[0])
    if not m:
        sys.exit(f"{toks[0]}: not a <PREFIX>-r<k>[.<lens>] token")
    credit = runs.setdefault(m[1], {})
    for tok in toks[1:]:
        i = tok.rstrip("~")
        if i not in weight:
            sys.exit(f"{toks[0]}: {i} is not in the ledger")
        credit[i] = max(credit.get(i, 0), 0.5 if tok.endswith("~") else 1)
reviewers = {}
for run in runs:
    reviewers.setdefault(run.rsplit("-r", 1)[0], []).append(run)


def run_quality(run, rows):
    return 100 * sum(weight[i] * runs[run].get(i, 0) for i in rows) / sum(weight[i] for i in rows)


def stats(run):
    f = Path(sys.argv[2]).parent / run / "stats.txt"
    return dict(re.findall(r"(\w+)=(\S+)", f.read_text())) if f.exists() else {}


def cost(run):
    m = re.fullmatch(r"\$([\d.]+)", stats(run).get("cost", ""))
    return float(m[1]) if m else None


def label(g):
    s = stats(reviewers[g][0])
    model = s.get("shown") or s.get("model", "").removeprefix("claude-")
    return g, s.get("reviewer", ""), f"{model}-{s.get('effort', '')}" if model else ""


def mean_quality(rows):
    return {g: statistics.mean(run_quality(r, rows) for r in rs) for g, rs in reviewers.items()}


q = mean_quality(list(weight))
order = sorted(reviewers, key=lambda g: (-q[g], g))
random.seed(1)
boots = [mean_quality(random.choices(list(weight), k=len(weight))) for _ in range(B)]
tier, head, tiers = 1, order[0], {}
for g in order:
    if g != head and sum(b[g] >= b[head] for b in boots) / B < 0.10:
        tier, head = tier + 1, g
    tiers[g] = tier

print(f"ledger v{ledger['version']}: {len(weight)} findings, weight {sum(weight.values()):g}, "
      f"{len(crit)} criticals")
cols = ("prefix", "reviewer", "model")
labels = {g: label(g) for g in order}
w = [max(map(len, c)) for c in zip(cols, *labels.values())]
name = lambda lb: "  ".join(f"{c:<{n}}" for c, n in zip(lb, w))
print(f"{'tier':>4}  {name(cols)}  {'runs':>4}  {'quality':>7}  {'sd':>5}  "
      f"criticals  rejected  {'$/run':>6}")
for g in order:
    qs = [run_quality(r, list(weight)) for r in reviewers[g]]
    sd = f"{statistics.stdev(qs):.1f}" if len(qs) > 1 else ""
    c = statistics.mean(sum(runs[r].get(i) == 1 for i in crit) for r in reviewers[g])
    rej = statistics.mean(rejected.get(r, 0) for r in reviewers[g])
    cs = [cost(r) for r in reviewers[g]]
    usd = f"${statistics.mean(cs):.2f}" if None not in cs else ""
    print(f"{tiers[g]:>4}  {name(labels[g])}  {len(qs):>4}  {q[g]:>7.1f}  {sd:>5}  "
          f"{f'{c:.1f}/{len(crit)}':<9}  {rej:>8.1f}  {usd:>6}".rstrip())
