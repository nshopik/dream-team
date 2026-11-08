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


def transcript(path, calls, start=0):
    """Writes an agent transcript making calls: (tool name, input, failed), one entry a minute from 13:start."""
    lines = []
    for i, (name, inp, failed) in enumerate(calls):
        lines.append({"type": "assistant", "timestamp": f"2026-10-25T13:{start + 2 * i:02}:00.000Z", "message": {"id": f"m{i}", "role": "assistant", "usage": {"input_tokens": 10, "output_tokens": 5},
                      "content": [{"type": "tool_use", "id": f"t{i}", "name": name, "input": inp}]}})
        lines.append({"type": "user", "timestamp": f"2026-10-25T13:{start + 2 * i + 1:02}:00.000Z", "message": {"role": "user", "content": [
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
        {"type": "started"},
        {"type": "result"},
        {"type": "result", "agentId": "a-text", "result": "plain-text handback"},
        {"type": "started", "key": "k", "agentId": agent, "label": label, "phase": "Implement"},
        {"type": "result", "key": "k", "agentId": agent, "result": {"committed": True, "summary": "", "friction": list(friction)}},
    ]) + "\n")
    (d / f"agent-{agent}.meta.json").write_text(json.dumps({"agentType": "workflow-subagent", "description": label}))
    transcript(d / f"agent-{agent}.jsonl", [("Bash", {"command": cmd}, failed) for cmd, failed in calls])
    if not fresh:
        age(d)
    return d


def scan(*args):
    p = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env={**os.environ, "HOME": str(home)})
    assert p.returncode == 0, p.stderr
    return p.stdout


cases = [  # (role, tool, input, patterns)
    ("impl", "Bash", {"command": "ssh jade-lab uptime"}, ["forbidden"]),
    ("impl", "Bash", {"command": "cd x && ssh jade-lab uptime"}, ["forbidden"]),
    ("impl", "Bash", {"command": 'git commit -m "ssh docs"'}, []),
    ("impl", "Bash", {"command": "git push origin main"}, ["forbidden"]),
    ("impl", "Bash", {"command": 'git commit -m "docs: run git push"'}, []),
    ("impl", "Bash", {"command": "cat > /tmp/b.md <<'EOF'\ngit push\nssh jade-lab\nEOF"}, []),
    ("impl", "Bash", {"command": "cat > /tmp/b.md <<'EOF'\nssh jade-lab\nEOF\ngit push"}, ["forbidden"]),
    ("impl", "Bash", {"command": "gh api repos/o/r/issues -f title=x"}, ["forbidden"]),
    ("impl", "Bash", {"command": "gh api search/issues -X GET -F q=1"}, []),
    ("review:code", "Edit", {"file_path": "/r/a.py"}, ["forbidden"]),
    ("fixdiff:domain:r1", "Edit", {"file_path": "/r/a.py"}, ["forbidden"]),
    ("impl", "Edit", {"file_path": "/r/a.py"}, []),
    ("gate", "Bash", {"command": "sed -i 's/a/b/' src/a.py"}, ["forbidden"]),
    ("gate", "Bash", {"command": "sed --in-place 's/a/b/' src/a.py"}, ["forbidden"]),
    ("gate", "Bash", {"command": "perl -pi -e 's/a/b/' src/a.py"}, ["forbidden"]),
    ("gate", "Bash", {"command": "git checkout src/b.py"}, ["forbidden"]),
    ("gate", "Bash", {"command": "git checkout -- src/b.py"}, ["forbidden"]),
    ("gate", "Bash", {"command": "git restore src/b.py"}, ["forbidden"]),
    ("review:code", "Bash", {"command": "git stash"}, ["forbidden"]),
    ("review:code", "Bash", {"command": "git stash list; git stash show -p"}, []),
    ("gate", "Bash", {"command": "git -C /r checkout src/b.py"}, ["forbidden"]),
    ("review:code", "Bash", {"command": "sed -n '1,40p' src/a.py | grep -i foo"}, []),
    ("review:code", "Bash", {"command": "python3 - <<'EOF'\nprint(1 > 0)\nEOF"}, []),
    ("gate", "Bash", {"command": "git commit -m x"}, ["forbidden"]),
    ("gate", "Bash", {"command": "make 2>&1 | tee build.log"}, ["forbidden"]),
    ("gate", "Bash", {"command": "echo x >> notes.md"}, ["forbidden"]),
    ("impl", "Bash", {"command": "sed -i 's/a/b/' src/a.py && git checkout src/b.py"}, []),
    ("review:code", "Bash", {"command": "make test 2>&1 | tee /tmp/out >&2; ls x 2>/dev/null > /tmp/ls"}, []),
    ("review:code", "Bash", {"command": "awk '$1 > 5' a.txt; grep -n 'git stash' b.md"}, []),
    ("simplify", "Bash", {"command": "cat > src/a.py <<'EOF'\nx = 1\nEOF"}, ["forbidden"]),
]
for role, tool, inp, want in cases:
    path = home / "case.jsonl"
    transcript(path, [(tool, inp, False)])
    got = [p for p, _ in friction.scan_agent(path, role)[0]]
    assert got == want, (role, tool, inp, got)
print("PASS forbidden actions")

transcript(path, [("Bash", {"command": "git push"}, False)] * 2)
lines = path.read_text().splitlines()
keyless = json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use"}]}})
path.write_text("\n".join([*lines[:2], '{"type": "assis', keyless, *lines[2:]]) + "\n")
with open(path, "ab") as f:
    f.write('{"type": "assistant", "x": "\u2014'.encode()[:-1])  # torn mid-character
assert [p for p, _ in friction.scan_agent(path, "impl")[0]] == ["forbidden"] * 2
print("PASS a bad transcript line is skipped")

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

# A run killed mid-append leaves an unterminated line that the next append joins.
cache_path = home / ".claude/dream-team/friction.jsonl"
lines = cache_path.read_text().splitlines()
i = next(i for i, line in enumerate(lines) if i and '"stats"' in line)
cache_path.write_text("\n".join([*lines[:i], '{"type": "ru' + lines[i], *lines[i + 1:]]) + "\n")
out = scan()
assert out.startswith("scanned 0 new runs; skipped 0 in progress") and out.splitlines()[1:] == repeated, out
print("PASS a bad cache line is skipped")

# A killed append leaves the tail unterminated; the next run's records must not join it.
cache_path.write_text(cache_path.read_text() + '{"type": "hi')
run_dir("wf_i-009", "impl:#11", [("make", False)])
assert scan().startswith("scanned 1 new runs"), "the new run is scanned"
assert scan().startswith("scanned 0 new runs"), "and not again"
assert any(r["type"] == "stats" and r["run"] == "wf_i-009" for r in friction.read_jsonl(cache_path)), "its first record is kept"
print("PASS a torn cache tail does not eat the next run")

# A run cached before stats carried minutes is left out of the table.
with open(cache_path, "a") as f:
    f.write(json.dumps({"type": "stats", "run": "wf_old", "role": "gate", "agentType": "", "tokens": 1, "tools": 1}) + "\n")
    f.write(json.dumps({"type": "run", "run": "wf_old", "date": "2026-10-01"}) + "\n")
# Two agents, the second starting ten minutes in: the run spans first start to last end.
late = run_dir("wf_l-012", "impl:#13", [("make", False)])
with open(late / "journal.jsonl", "a") as f:
    f.write(json.dumps({"type": "started", "agentId": "a-late", "label": "re-review:code:r1"}) + "\n")
transcript(late / "agent-a-late.jsonl", [("Bash", {"command": "make"}, False)], start=10)
age(late)
assert scan("--time").splitlines()[1:] == [
    "",
    "| role | runs | agents | min | P10 | Q1 | median | Q3 | P90 | max |",
    "|---|---|---|---|---|---|---|---|---|---|",
    "| gate | 4 | 4 | 1.0 | 1.0 | 1.0 | 3.0 | 5.0 | 5.0 | 5.0 |",
    "| impl | 5 | 5 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |",  # wf_b-002 lost its stats to the bad line
    "| whole run | 10 | 10 | 1.0 | 1.0 | 1.0 | 1.0 | 5.0 | 5.6 | 11.0 |",  # wf_l-012 spans 13:00 to 13:11
    "| re-review:code | 1 | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |",
], scan("--time")
print("PASS --time tables minutes per role and per run")

# A crash on one run keeps the runs scanned before it.
home = Path(tempfile.mkdtemp())
friction.HOME, friction.CACHE = home, home / "cache.jsonl"
for run in ("wf_j-010", "wf_k-011"):
    run_dir(run, "impl:#12", [("make", False)])
scan_run, calls = friction.scan_run, []
def crash_second(*args):
    calls.append(args)
    if len(calls) == 2:
        raise RuntimeError("killed")
    return scan_run(*args)
friction.scan_run = crash_second
try:
    friction.main()
except RuntimeError:
    pass
kept = {r["run"] for r in friction.read_jsonl(friction.CACHE) if r["type"] == "run"}
assert "wf_j-010" in kept and "wf_k-011" not in kept, kept
print("PASS a crash keeps the runs scanned before it")
