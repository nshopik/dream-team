#!/usr/bin/env python3
"""run.sh end to end with a stub `claude` on PATH: two reviewers' runs on a scratch repo, graded.

Usage: python3 test_run.py
"""
import json
import os
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
TMPDIR = tempfile.TemporaryDirectory()
TMP = Path(TMPDIR.name)
OUT, REPO, BIN = TMP / "out", TMP / "repo", TMP / "bin"

# Reviewer runs log their argv, then leak a CLAUDE.local.md and edit a.go; an -r1 run reports, an
# -r2 run errors.
# The grader logs its start and end, credits the run with C1 and adds C1 to a warm-up ledger.
STUB = r'''#!/usr/bin/env python3
import json, os, re, sys, time, uuid
from pathlib import Path
log = Path(os.environ["STUB_LOG"])
if "--output-format" not in sys.argv:
    t0, prompt = time.time(), sys.stdin.read()
    name = re.search(r"The run is (\S+):", prompt)[1]
    if "not frozen" in prompt:
        (Path(os.environ["STUB_OUT"]) / "ledger.json").write_text(json.dumps({"version": 1,
            "rows": [{"id": "C1", "finding": "panic", "location": "a.go:3", "severity": "critical",
                      "plausible": False, "nit": False}]}))
    time.sleep(0.5)
    with log.open("a") as f:
        f.write(json.dumps({"grader": sys.argv, "prompt": prompt, "t": [t0, time.time()]}) + "\n")
    print(f"Graded.\n{name} C1\nRejected ({name}): b.go races (one goroutine).")
    sys.exit()
with log.open("a") as f:
    f.write(json.dumps({"argv": sys.argv, "cwd": os.getcwd(), "a.go": Path("a.go").read_text(),
                        "ceiling": os.environ.get("CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS")}) + "\n")
Path("CLAUDE.local.md").write_text("answers\n")
Path("a.go").write_text("package b\n")
sid = str(uuid.uuid4())
t = Path(os.environ["CLAUDE_CONFIG_DIR"]) / "projects/p" / f"{sid}.jsonl"
t.parent.mkdir(parents=True, exist_ok=True)
t.write_text(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "x"}]}}) + "\n")
if os.getcwd().endswith("-r2/repo"):
    print(json.dumps({"session_id": sid, "subtype": "error_max_turns", "is_error": True}))
    sys.exit(1)
print(json.dumps({"session_id": sid, "result": "x", "total_cost_usd": 1.5}))
'''

BIN.mkdir()
(BIN / "claude").write_text(STUB)
(BIN / "claude").chmod(0o755)
git = lambda *a: subprocess.run(["git", "-C", REPO, *a], check=True, capture_output=True)
REPO.mkdir()
git("init", "-q", "-b", "main")
git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base")
git("switch", "-q", "-c", "feat")
(REPO / "a.go").write_text("package a\n")
git("add", "a.go")
git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "feat")
(TMP / "reviewers.txt").write_text(
    "# qa-review\nQA-opus-4-6:lenses model=claude-opus-4-6 /dream-team:qa-review {base}\n"
    "QA-max:lenses effort=max model=claude-opus-5 /dream-team:qa-review {base}\n")
env = {**os.environ, "PATH": f"{BIN}:{os.environ['PATH']}", "STUB_LOG": str(TMP / "log"),
       "STUB_OUT": str(OUT), "CLAUDE_CONFIG_DIR": str(TMP / "config"), "N": "2", "P": "2",
       "EFFORT": "low"}
RUNS = ["QA-max-r1", "QA-max-r2", "QA-opus-4-6-r1", "QA-opus-4-6-r2"]
overlap = lambda g: max(m["t"][0] for m in g) < min(m["t"][1] for m in g)

out = subprocess.run(["bash", HERE / "run.sh", REPO, "main", "feat", TMP / "reviewers.txt", OUT],
                     env=env, capture_output=True, text=True)
assert out.returncode == 0, out.stderr
log = [json.loads(line) for line in (TMP / "log").read_text().splitlines()]
runs = sorted((m for m in log if "argv" in m), key=lambda m: m["cwd"])
graders = [m for m in log if "grader" in m]
wts = [str(OUT / r / "repo") for r in RUNS]

for case, ok in [
    ("each run passes its line's model and effort, else MODEL and EFFORT", [
        " ".join(m["argv"]).split(" --output-format")[0].split("-p ")[1] for m in runs] == [
        "/dream-team:qa-review main --model claude-opus-5 --effort max"] * 2
        + ["/dream-team:qa-review main --model claude-opus-4-6 --effort low"] * 2),
    ("each run's stats show its model and effort", [
        (OUT / r / "stats.txt").read_text().split(" exit=")[0] for r in RUNS] == [
        "model=claude-opus-5 effort=max"] * 2 + ["model=claude-opus-4-6 effort=low"] * 2),
    ("each run sets the background-wait ceiling to 0", all(m["ceiling"] == "0" for m in runs)),
    ("each run allows /tmp writes and denies edits, commits and pushes in the target", all(
        "Write(//tmp/**)" in m["argv"] and {"Edit", f"Write(/{w}/**)", "Bash(git commit:*)",
                                             "Bash(git push:*)"} <= set(m["argv"])
        for m, w in zip(runs, wts))),
    ("{base} expands in the prompt", all("/dream-team:qa-review main" in m["argv"] for m in runs)),
    ("each run works in its own clean worktree at head", [m["cwd"] for m in runs] == wts
     and all(m["a.go"] == "package a\n" for m in runs)),
    ("a leaked CLAUDE.local.md moves into the run directory", all(
        (OUT / r / "leaked.CLAUDE.local.md").exists() for r in RUNS)),
    ("each run writes its report and stats", all(
        (OUT / r / "report.md").exists() and "wall=" in (OUT / r / "stats.txt").read_text()
        for r in RUNS)),
    ("an error result is an early exit, scored 0 without a grader",
     "early-exit" in (OUT / "QA-opus-4-6-r2/stats.txt").read_text() and len(graders) == 2
     and (OUT / "QA-opus-4-6-r2/marks.txt").read_text() == "QA-opus-4-6-r2\n"),
    ("a warm-up ledger grades one run at a time under P=2", not overlap(graders)),
    ("the grader runs on opus at effort high, warm-up may edit the ledger", "--model opus --effort high"
     in " ".join(graders[0]["grader"]) and f"Edit(/{OUT}/ledger.json)" in graders[0]["grader"]
     and "not frozen" in graders[0]["prompt"]),
    ("marks keep the marks lines only", (OUT / "QA-opus-4-6-r1/marks.txt").read_text()
     == "QA-opus-4-6-r1 C1\nRejected (QA-opus-4-6-r1): b.go races (one goroutine).\n"),
    ("score.py prints each reviewer's row, named by its code, under a header as wide",
     "tier  reviewer     runs  quality     sd  criticals  rejected   $/run\n"
     "   1  QA-max          2     50.0   70.7  0.5/1           0.5   $0.75\n"
     "   1  QA-opus-4-6     2     50.0   70.7  0.5/1           0.5   $0.75\n" in out.stdout),
    ("the worktrees are removed", len(git("worktree", "list").stdout.splitlines()) == 1),
]:
    assert ok, (case, out.stdout, out.stderr)
    print("PASS", case)

# A rerun on a frozen ledger regrades runs whose marks were deleted, in parallel, without ledger
# edits.
ledger = json.loads((OUT / "ledger.json").read_text())
(OUT / "ledger.json").write_text(json.dumps({**ledger, "frozen": True}))
(OUT / "QA-opus-4-6-r1/marks.txt").unlink()
(OUT / "QA-max-r1/marks.txt").unlink()
out = subprocess.run(["bash", HERE / "run.sh", REPO, "main", "feat", TMP / "reviewers.txt", OUT],
                     env=env, capture_output=True, text=True)
log = [json.loads(line) for line in (TMP / "log").read_text().splitlines()]
regrades = [m for m in log if "grader" in m][2:]
assert out.returncode == 0 and len([m for m in log if "argv" in m]) == 4, out.stderr
assert len(regrades) == 2 and all(not any(a.startswith("Edit(") for a in m["grader"])
                                  and "not frozen" not in m["prompt"] for m in regrades), regrades
print("PASS a rerun skips finished runs; a frozen ledger grades with no ledger edits")
assert overlap(regrades), regrades
print("PASS a frozen ledger grades runs in parallel under P=2")
