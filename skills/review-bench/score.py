#!/usr/bin/env python3
"""Scores reviewer runs against a findings ledger; see METHODOLOGY.md.

Usage: python3 score.py <ledger.json> <marks.txt>
"""
import json
import random
import re
import statistics
import sys

WEIGHT = {"critical": 10, "important": 4, "performance": 3, "test": 3, "minor": 1}
B = 2000

ledger = json.load(open(sys.argv[1]))
weight = {}
for r in ledger["rows"]:
    w = 0.5 if r["severity"] == "minor" and r["nit"] else WEIGHT[r["severity"]]
    weight[r["id"]] = w * (0.5 if r["plausible"] else 1)
crit = [r["id"] for r in ledger["rows"] if r["severity"] == "critical"]

runs = {}  # run -> {id: best credit across its lenses}
for line in open(sys.argv[2]):
    toks = line.split()
    if not toks or not re.match(r"[A-Z]+\d", toks[0]):
        continue
    m = re.fullmatch(r"([A-Z]+\d+)(\.\S+)?", toks[0])
    if not m:
        sys.exit(f"{toks[0]}: not a <PREFIX><run>[.<lens>] token")
    credit = runs.setdefault(m[1], {})
    for tok in toks[1:]:
        i = tok.rstrip("~")
        if i not in weight:
            sys.exit(f"{toks[0]}: {i} is not in the ledger")
        credit[i] = max(credit.get(i, 0), 0.5 if tok.endswith("~") else 1)
reviewers = {}
for run in runs:
    reviewers.setdefault(re.match(r"[A-Z]+", run)[0], []).append(run)


def run_quality(run, rows):
    return 100 * sum(weight[i] * runs[run].get(i, 0) for i in rows) / sum(weight[i] for i in rows)


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
print(f"{'tier':>4}  {'reviewer':<8}  {'runs':>4}  {'quality':>7}  {'sd':>5}  criticals")
for g in order:
    qs = [run_quality(r, list(weight)) for r in reviewers[g]]
    sd = f"{statistics.stdev(qs):.1f}" if len(qs) > 1 else ""
    c = statistics.mean(sum(runs[r].get(i) == 1 for i in crit) for r in reviewers[g])
    print(f"{tiers[g]:>4}  {g:<8}  {len(qs):>4}  {q[g]:>7.1f}  {sd:>5}  {c:.1f}/{len(crit)}")
