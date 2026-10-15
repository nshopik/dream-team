#!/usr/bin/env python3
"""Writes a run's report.md, and with `lenses` its lenses/<lens>.md, from its claude -p result and
session transcripts, then prints its cost, report size and subagent count, plus `early-exit` when
the run errored, its report is empty, or its main turn ended before a subagent did.

Usage: python3 extract.py <run-dir> [lenses]
"""
import json
import os
import sys
from pathlib import Path

d = Path(sys.argv[1])
if not (d / "result.json").stat().st_size:
    sys.exit(print("cost=? report=0 lenses=0 early-exit"))
run = json.loads((d / "result.json").read_text())
projects = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")) / "projects"


def read(transcript, sidechain=False):
    """The longest assistant text or subagent hand-back in a transcript, and its last timestamp."""
    texts, last = [], ""
    for line in open(transcript):
        m = json.loads(line)
        if m.get("type") != "assistant" or m.get("isSidechain", False) != sidechain:
            continue
        last = max(last, m.get("timestamp", ""))
        for c in m["message"].get("content", []):
            if c.get("type") == "text":
                texts.append(c["text"])
            elif c.get("type") == "tool_use" and c["name"] == "SubagentHandback":
                texts.append(c["input"]["message"])
    return max(texts, key=len, default=""), last


# `result` is only the last message, which can be an ack after the report; an error result lacks it.
report, ended = max((read(t) for t in projects.glob(f"*/{run['session_id']}.jsonl")),
                    key=lambda r: len(r[0]), default=("", ""))
result = run.get("result", "")
if result.strip() not in report:
    report += "\n\n---\n\n" + result
(d / "report.md").write_text(report.strip() + "\n")

late = False
subagents = sorted(projects.glob(f"*/{run['session_id']}/subagents/*.meta.json"))
for meta in subagents:
    text, last = read(meta.with_name(meta.name[: -len(".meta.json")] + ".jsonl"), True)
    late |= last > ended
    if sys.argv[2:] != ["lenses"]:
        continue
    name = json.loads(meta.read_text())["agentType"].split(":")[-1]
    if name == "Explore":  # a code search, not a review lens
        continue
    f, n = d / "lenses" / f"{name}.md", 2
    while f.exists():
        f, n = d / "lenses" / f"{name}-{n}.md", n + 1
    f.parent.mkdir(exist_ok=True)
    f.write_text(text + "\n")

early = run.get("is_error") or not report.strip() or late
print(f"cost=${run.get('total_cost_usd', 0):.2f} report={len(report.strip())} "
      f"lenses={len(subagents)}" + (" early-exit" if early else ""))
