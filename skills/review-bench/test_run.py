#!/usr/bin/env python3
"""run.sh end to end with a stub `claude` on PATH: two reviewer runs on a scratch repo, graded.

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

# Reviewer runs log their argv, then leak a CLAUDE.local.md and edit a.go; QR1 reports, QR2 errors.
# The grader credits a warm-up row it adds to the ledger.
STUB = r'''#!/usr/bin/env python3
import json, os, sys, uuid
from pathlib import Path
log = Path(os.environ["STUB_LOG"])
if "--output-format" not in sys.argv:
    prompt = sys.stdin.read()
    with log.open("a") as f: f.write(json.dumps({"grader": sys.argv, "prompt": prompt}) + "\n")
    ledger = Path(os.environ["STUB_OUT"]) / "ledger.json"
    ledger.write_text(json.dumps({"version": 1, "rows": [{"id": "C1", "finding": "panic",
        "location": "a.go:3", "severity": "critical", "plausible": False, "nit": False}]}))
    print("Graded.\nQR1 C1\nRejected (QR1): b.go races (one goroutine).")
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
if log.read_text().count('"argv"') > 1:
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
(TMP / "reviewers.txt").write_text("# qa-review\nQR:lenses /dream-team:qa-review {base}\n")
env = {**os.environ, "PATH": f"{BIN}:{os.environ['PATH']}", "STUB_LOG": str(TMP / "log"),
       "STUB_OUT": str(OUT), "CLAUDE_CONFIG_DIR": str(TMP / "config"), "N": "2"}

out = subprocess.run(["bash", HERE / "run.sh", REPO, "main", "feat", TMP / "reviewers.txt", OUT],
                     env=env, capture_output=True, text=True)
assert out.returncode == 0, out.stderr
log = [json.loads(line) for line in (TMP / "log").read_text().splitlines()]
runs, graders = [m for m in log if "argv" in m], [m for m in log if "grader" in m]
wts = [str(OUT / r / "repo") for r in ("QR1", "QR2")]

for case, ok in [
    ("each run passes --model and --effort", all(
        "--model opus --effort high" in " ".join(m["argv"]) for m in runs)),
    ("each run sets the background-wait ceiling to 0", all(m["ceiling"] == "0" for m in runs)),
    ("each run allows /tmp writes and denies edits, commits and pushes in the target", all(
        "Write(//tmp/**)" in m["argv"] and {"Edit", f"Write(/{w}/**)", "Bash(git commit:*)",
                                             "Bash(git push:*)"} <= set(m["argv"])
        for m, w in zip(runs, wts))),
    ("{base} expands in the prompt", all("/dream-team:qa-review main" in m["argv"] for m in runs)),
    ("each run works in its own clean worktree at head", [m["cwd"] for m in runs] == wts
     and all(m["a.go"] == "package a\n" for m in runs)),
    ("a leaked CLAUDE.local.md moves into the run directory", all(
        (OUT / r / "leaked.CLAUDE.local.md").exists() for r in ("QR1", "QR2"))),
    ("each run writes its report and stats", all(
        (OUT / r / "report.md").exists() and "wall=" in (OUT / r / "stats.txt").read_text()
        for r in ("QR1", "QR2"))),
    ("an error result is an early exit, scored 0 without a grader",
     "early-exit" in (OUT / "QR2/stats.txt").read_text() and len(graders) == 1
     and (OUT / "QR2/marks.txt").read_text() == "QR2\n"),
    ("the grader runs on opus at effort high, warm-up may edit the ledger", "--model opus --effort high"
     in " ".join(graders[0]["grader"]) and f"Edit(/{OUT}/ledger.json)" in graders[0]["grader"]
     and "not frozen" in graders[0]["prompt"]),
    ("marks keep the marks lines only", (OUT / "QR1/marks.txt").read_text()
     == "QR1 C1\nRejected (QR1): b.go races (one goroutine).\n"),
    ("score.py prints the reviewer's row", "   1  QR           2     50.0" in out.stdout),
    ("the worktrees are removed", len(git("worktree", "list").stdout.splitlines()) == 1),
]:
    assert ok, (case, out.stdout, out.stderr)
    print("PASS", case)

# A rerun on a frozen ledger regrades a run whose marks were deleted, without ledger edits.
ledger = json.loads((OUT / "ledger.json").read_text())
(OUT / "ledger.json").write_text(json.dumps({**ledger, "frozen": True}))
(OUT / "QR1/marks.txt").unlink()
out = subprocess.run(["bash", HERE / "run.sh", REPO, "main", "feat", TMP / "reviewers.txt", OUT],
                     env=env, capture_output=True, text=True)
log = [json.loads(line) for line in (TMP / "log").read_text().splitlines()]
assert out.returncode == 0 and len([m for m in log if "argv" in m]) == 2, out.stderr
assert not any(a.startswith("Edit(") for a in log[-1]["grader"]) and "frozen" in log[-1]["prompt"], log[-1]
print("PASS a rerun skips finished runs; a frozen ledger grades with no ledger edits")
