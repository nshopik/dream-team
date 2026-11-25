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
    ("s-fork", [], {"a1": ("general-purpose", [say("cr " * 100, True, "2026-10-15T10:05:00Z")])}, {"result": REPORT}, [],
     f"cost=$3.04 report={len(REPORT.strip())} lenses=1\n", REPORT.strip() + "\n", {},
     "a forked-skill run has no main-thread turn; its subagent is not late"),
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


def spawn(name, role):
    return [
        {"type": "response_item", "payload": {"type": "function_call",
            "namespace": "collaboration", "name": "spawn_agent", "call_id": name,
            "arguments": json.dumps({"task_name": name, "agent_type": role})}},
        {"type": "response_item", "payload": {"type": "function_call_output", "call_id": name,
            "output": json.dumps({"task_name": f"/root/{name}"})}},
    ]


def answer(name, text):
    return {"type": "response_item", "payload": {"type": "agent_message", "author": f"/root/{name}",
        "content": [{"type": "input_text",
                     "text": f"Message Type: FINAL_ANSWER\nTask name: /root\nPayload:\n{text}"}]}}


def codex_extract(sid, texts, rollout, lenses=True, complete=True):
    d = TMP / sid
    d.mkdir()
    events = [{"type": "thread.started", "thread_id": sid}]
    events += [{"type": "item.completed", "item": {"type": "agent_message", "text": text}}
               for text in texts]
    if complete:
        events.append({"type": "turn.completed"})
    jsonl(d / "result.json", events)
    if rollout is not None:
        transcript = TMP / "codex/sessions/2026/11/24" / f"rollout-date-{sid}.jsonl"
        if isinstance(rollout, str):
            transcript.parent.mkdir(parents=True, exist_ok=True)
            transcript.write_text(rollout)
        else:
            jsonl(transcript, rollout)
    args = ["lenses"] if lenses else []
    out = subprocess.run([sys.executable, HERE / "extract.py", d, *args, "codex"],
                         capture_output=True, text=True,
                         env={**os.environ, "CODEX_HOME": str(TMP / "codex")})
    return d, out


ARCH = spawn("arch", "dream-team-architect-reviewer")
SRE = spawn("sre", "dream-team-sre-engineer")
HELPER = spawn("explore", "default")
DOMAIN = spawn("domain", "default")
CUSTOM = spawn("lens_custom", "default")
END = {"type": "event_msg", "payload": {"type": "task_complete"}}
ERROR = answer("sre", "Agent errored: tool failed")
RETRY_SRE = [
    {"type": "response_item", "payload": {"type": "function_call",
        "namespace": "collaboration", "name": "followup_task", "call_id": "retry-sre",
        "arguments": json.dumps({"target": "sre"})}},
    {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "retry-sre",
        "output": ""}},
]
for sid, rollout, names, early in [
    ("c-early", [*ARCH, *SRE, answer("arch", "Finding."), END, answer("sre", "Late.")],
     {"arch.md"}, True),
    ("c-failed", [*SRE, ERROR, END], set(), True),
    ("c-helper", [*ARCH, *SRE, *HELPER, *DOMAIN, *CUSTOM, answer("arch", "Finding."),
                  answer("explore", "Helper output."), answer("domain", "Domain finding."),
                  answer("lens_custom", "Custom finding."), ERROR, END],
     {"arch.md", "domain.md", "lens_custom.md"}, False),
    ("c-followup", [*ARCH, *SRE, answer("arch", "Finding."), ERROR, *RETRY_SRE, END],
     {"arch.md"}, True),
    ("c-incomplete", None, set(), True),
]:
    d, out = codex_extract(sid, ["Review."], rollout, complete=sid != "c-incomplete")
    assert out.returncode == 0, (sid, out.stderr)
    assert out.stdout.strip().endswith("early-exit") == early, (sid, out.stdout)
    assert {p.name for p in (d / "lenses").glob("*.md")} == names, sid
    print("PASS Codex", sid)

d, out = codex_extract("c-ack", ["The substantive review report.", "Done."], None, lenses=False)
assert out.returncode == 0 and "early-exit" not in out.stdout, out
assert (d / "report.md").read_text() == "The substantive review report.\n\n---\n\nDone.\n"
print("PASS a plain Codex run keeps the review when a closing acknowledgment follows it")

for sid, rollout, error in [("c-missing", None, "missing Codex rollout"),
                            ("c-malformed", "{broken\n", "Codex extraction failed"),
                            ("c-truncated", ARCH, "incomplete Codex rollout")]:
    _, out = codex_extract(sid, ["Review."], rollout)
    assert out.returncode != 0 and error in out.stderr and "early-exit" not in out.stdout, out
    print("PASS Codex", sid)
