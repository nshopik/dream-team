#!/usr/bin/env python3
"""extract.py over fixture claude -p results and session transcripts.

Usage: python3 test_extract.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
TMPDIR = tempfile.TemporaryDirectory()
TMP = Path(TMPDIR.name)
PROJ = TMP / "config/projects/-src-coredns"
REPORT = "🔴 **Nil-interface panic on a rejected UDP packet** [verified]\n" * 30


def say(text, sidechain=False, at=""):
    return {"type": "assistant", "isSidechain": sidechain, "timestamp": at,
            "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}


def handback(text):
    return {"type": "assistant", "isSidechain": True, "message": {"role": "assistant", "content": [
        {"type": "tool_use", "name": "SubagentHandback", "input": {"message": text}}]}}


def jsonl(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(m) + "\n" for m in lines))


def extract(sid, main, lenses, result, args):
    """Writes one session's transcripts and result.json, runs extract.py, returns its run dir."""
    jsonl(PROJ / f"{sid}.jsonl", main)
    for agent, (kind, lines) in lenses.items():
        sub = PROJ / sid / "subagents"
        jsonl(sub / f"agent-{agent}.jsonl", lines)
        (sub / f"agent-{agent}.meta.json").write_text(json.dumps({"agentType": kind}))
    d = TMP / sid
    d.mkdir()
    (d / "result.json").write_text(result and json.dumps(
        {"session_id": sid, "total_cost_usd": 3.044, "is_error": False, **result}))
    out = subprocess.run([sys.executable, HERE / "extract.py", d, *args],
                         capture_output=True, text=True,
                         env={**os.environ, "CLAUDE_CONFIG_DIR": str(TMP / "config")})
    assert out.returncode == 0, out.stderr
    return d, out.stdout


for sid, main, lenses, result, args, want_stats, want_report, want_lenses, case in [
    ("s-full",
     [say("Launching three lenses."), say("sre lens draft " * 200, sidechain=True), say(REPORT)],
     {"a1": ("dream-team:sre-engineer", [say("Reading the diff.", True), say("sre " * 100, True)]),
      "a2": ("dream-team:architect-reviewer", [handback("arch " * 100)]),
      "a3": ("dream-team:architect-reviewer", [say("arch2 " * 100, True)]),
      "a4": ("Explore", [say("map " * 10, True)])},
     {"result": REPORT}, ["lenses"],
     f"cost=$3.04 report={len(REPORT.strip())} lenses=4\n",
     REPORT.strip() + "\n",
     {"sre-engineer.md": "sre " * 100, "architect-reviewer.md": None, "architect-reviewer-2.md": None},
     "report is the longest main-thread text; lenses come from sidechain text and hand-backs; "
     "an Explore helper is no lens"),
    ("s-ack", [say("Lenses running.", at="2026-10-15T10:00:00Z")],
     {"a1": ("dream-team:sre-engineer", [say("sre " * 100, True, "2026-10-15T10:05:00Z")])},
     {"result": "Lenses running."}, ["lenses"], "early-exit", "Lenses running.\n",
     {"sre-engineer.md": "sre " * 100}, "a main turn that ends before a lens does is an early exit"),
    ("s-short", [say("Explored.", at="2026-10-15T10:06:00Z")],
     {"a1": ("Explore", [say("map " * 10, True, "2026-10-15T10:05:00Z")])},
     {"result": "No findings."}, [], "cost=$3.04 report=28 lenses=1\n",
     "Explored.\n\n---\n\nNo findings.\n", {},
     "a short report after its helper ends is not an early exit; no lenses without the flag"),
    ("s-error", [say(REPORT[:500])], {}, {"subtype": "error_max_turns", "is_error": True}, [],
     "cost=$3.04 report=500 lenses=0 early-exit\n", REPORT[:500].strip() + "\n", {},
     "an error result has no `result` and is an early exit"),
    ("s-crash", [], {}, "", [], "cost=? report=0 lenses=0 early-exit\n", None, {},
     "an empty result.json is an early exit"),
]:
    d, stats = extract(sid, main, lenses, result, args)
    assert want_stats in stats, (case, stats)
    if want_report is not None:
        assert (d / "report.md").read_text() == want_report, (case, (d / "report.md").read_text()[:200])
    got = {p.name: p.read_text() for p in (d / "lenses").glob("*.md")}
    assert set(got) == set(want_lenses), (case, sorted(got))
    for name, text in want_lenses.items():
        assert text is None or got[name] == text + "\n", (case, name, got[name][:80])
    print("PASS", case)
