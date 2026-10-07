#!/usr/bin/env python3
"""friction.py over synthetic workflow runs in a temp HOME.

Usage: python3 test_friction.py
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCRIPT = Path(__file__).with_name("friction.py")
sys.path.insert(0, str(SCRIPT.parent))
import friction  # noqa: E402

home = Path(tempfile.mkdtemp())
aged = [time.time() - 86400]


def transcript(path, calls):
    """Writes an agent transcript making calls: (tool name, input, failed)."""
    lines = []
    for i, (name, inp, failed) in enumerate(calls):
        lines.append({"type": "assistant", "message": {"id": f"m{i}", "role": "assistant", "usage": {"input_tokens": 10, "output_tokens": 5},
                      "content": [{"type": "tool_use", "id": f"t{i}", "name": name, "input": inp}]}})
        lines.append({"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": f"t{i}", "is_error": failed,
             "content": "Exit code 1\nboom" if failed else "ok"}]}})
    path.write_text("\n".join(json.dumps(e) for e in lines) + "\n")


def age(d):
    """Dates a run a day back, keeping runs in the order they were written."""
    aged[0] += 1
    for f in [*d.iterdir(), d]:
        os.utime(f, (aged[0], aged[0]))


def run_dir(run, label, calls, friction=(), fresh=False):
    """Writes one dream-fixer-loop run whose single agent makes calls: (bash command, failed)."""
    d = home / ".claude/projects/-r/sess/subagents/workflows" / run
    d.mkdir(parents=True)
    agent = f"a{run[-3:]}"
    (d / "journal.jsonl").write_text("\n".join(json.dumps(e) for e in [
        {"type": "launched"},
        {"type": "started", "key": "k", "agentId": agent, "label": label, "phase": "Implement"},
        {"type": "result", "key": "k", "agentId": agent, "result": {"committed": True, "summary": "", "friction": list(friction)}},
    ]) + "\n")
    (d / f"agent-{agent}.meta.json").write_text(json.dumps({"agentType": "workflow-subagent", "description": label}))
    transcript(d / f"agent-{agent}.jsonl", [("Bash", {"command": cmd}, failed) for cmd, failed in calls])
    if not fresh:
        age(d)
    return d


def scan():
    p = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, env={**os.environ, "HOME": str(home)})
    assert p.returncode == 0, p.stderr
    return p.stdout


cases = [  # (role, tool, input, patterns)
    ("impl", "Bash", {"command": "ssh jade-lab uptime"}, ["forbidden"]),
    ("impl", "Bash", {"command": "cd x && ssh jade-lab uptime"}, ["forbidden"]),
    ("impl", "Bash", {"command": 'git commit -m "ssh docs"'}, []),
    ("impl", "Bash", {"command": "git push origin main"}, ["forbidden"]),
    ("impl", "Bash", {"command": "gh api repos/o/r/issues -f title=x"}, ["forbidden"]),
    ("impl", "Bash", {"command": "gh api search/issues -X GET -F q=1"}, []),
    ("review:code", "Edit", {"file_path": "/r/a.py"}, ["forbidden"]),
    ("impl", "Edit", {"file_path": "/r/a.py"}, []),
]
for role, tool, inp, want in cases:
    path = home / "case.jsonl"
    transcript(path, [(tool, inp, False)])
    got = [p for p, _ in friction.scan_agent(path, role)[0]]
    assert got == want, (role, tool, inp, got)
print("PASS forbidden actions")

hunt = "find ~/.claude -name SKILL.md"
repeated = ["", "claude-dir | impl | 2 runs | workflow-subagent", f"  - {hunt}",
            "", "self-report | impl | 2 runs | workflow-subagent", "  - no Skill tool"]
steps = [  # (name, runs, first line, printed); a run is (id, label, calls, friction)
    ("one hunt, one one-off failed command", [("wf_a-001", "impl:#7", [(hunt, False)], ["no Skill tool"]), ("wf_b-002", "impl:#8", [("cargo test", True), ("cargo test", True), ("make lint", True)], [])],
     "scanned 2 new runs", []),
    ("the same hunt in a second run", [("wf_c-003", "gate:#9:r1", [(hunt, False)], []), ("wf_d-004", "impl:#9", [(hunt, False)], ["no Skill tool"])],
     "scanned 2 new runs", repeated),
    ("nothing new", [], "scanned 0 new runs", repeated),
    ("a role's third run is no outlier", [("wf_e-005", "gate:#5", [("make", False)], []), ("wf_f-006", "gate:#6", [("make", False)] * 3, [])],
     "scanned 2 new runs", repeated),
    ("its fourth run is", [("wf_g-007", "gate:#7", [("make", False)] * 3, [])], "scanned 1 new runs", repeated),
]

for name, runs, first, printed in steps:
    for run, label, calls, said in runs:
        run_dir(run, label, calls, said)
    out = scan()
    assert out.startswith(first + "; skipped 0 in progress") and out.splitlines()[1:] == printed, f"{name}:\n{out}"
    print(f"PASS {name}")

live = run_dir("wf_h-008", "impl:#10", [("make", False)], fresh=True)
with open(live / "agent-a008.jsonl", "a") as f:
    f.write('{"type": "assis')
assert scan().startswith("scanned 0 new runs; skipped 1 in progress"), "a fresh run is skipped"
age(live)
assert scan().startswith("scanned 1 new runs; skipped 0 in progress"), "it is scanned once it goes quiet"
print("PASS a run still going is scanned later")

cache = [json.loads(line) for line in (home / ".claude/dream-team/friction.jsonl").read_text().splitlines()]
assert sorted(r["run"] for r in cache if r["type"] == "run") == [f"wf_{c}-00{i}" for i, c in enumerate("abcdefgh", 1)]
hits = {(r["pattern"], r["role"], r["evidence"]) for r in cache if r["type"] == "hit"}
assert ("claude-dir", "gate", hunt) in hits and ("repeat-failure", "impl", "cargo test") in hits, hits
outliers = {(r["run"], r["pattern"]) for r in cache if r["type"] == "hit" and r["pattern"].endswith("-outlier")}
assert outliers == {("wf_g-007", "tokens-outlier"), ("wf_g-007", "tools-outlier")}, outliers
print("PASS cache keeps one-offs and every scanned run")
