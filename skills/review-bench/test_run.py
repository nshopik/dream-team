#!/usr/bin/env python3
"""run.sh end to end with a stub `claude` on PATH: two reviewers' runs on a scratch repo, graded.

Usage: python3 test_run.py
"""
import json
import os
import shutil
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
                      "plausible": False}]}))
    time.sleep(0.5)
    with log.open("a") as f:
        f.write(json.dumps({"grader": sys.argv, "prompt": prompt, "t": [t0, time.time()]}) + "\n")
    if name == os.environ.get("STUB_FAIL_GRADE"):
        print(f"Rejected ({name}): no scored line")
        sys.exit()
    if name == "qa-sol-r1":
        lenses = Path(os.environ["STUB_OUT"]) / name / "lenses"
        assert f"grade each file in {lenses}/" in prompt
        assert {p.name: p.read_text() for p in lenses.glob("*.md")} == {
            "lens_architect.md": "Raw architect finding.\n"}
        print(f"{name}.architect C1")
        sys.exit()
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
if os.getcwd().endswith("-r2"):
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
    "# qa-review\nqa-opus-4-6:lenses model=claude-opus-4-6 /dream-team:qa-review {base}\n"
    "vllm effort=max model=claude-opus-5 shown=qwen3-coder /vllm-review {base}..{head}\n")
env = {**os.environ, "PATH": f"{BIN}:{os.environ['PATH']}", "STUB_LOG": str(TMP / "log"),
       "STUB_OUT": str(OUT), "CLAUDE_CONFIG_DIR": str(TMP / "config"), "N": "2", "P": "2",
       "EFFORT": "low"}
RUNS = ["qa-opus-4-6-r1", "qa-opus-4-6-r2", "vllm-r1", "vllm-r2"]
overlap = lambda g: max(m["t"][0] for m in g) < min(m["t"][1] for m in g)

out = subprocess.run(["bash", HERE / "run.sh", REPO, "main", "feat", TMP / "reviewers.txt", OUT],
                     env=env, capture_output=True, text=True)
assert out.returncode == 0, out.stderr
log = [json.loads(line) for line in (TMP / "log").read_text().splitlines()]
runs = sorted((m for m in log if "argv" in m), key=lambda m: m["cwd"])
graders = [m for m in log if "grader" in m]
wts = [str(OUT / r / r) for r in RUNS]

for case, ok in [
    ("each run passes its line's prompt with {base} and {head} expanded, model and effort, else "
     "EFFORT", [" ".join(m["argv"]).split(" --output-format")[0].split("-p ")[1] for m in runs] == [
        "/dream-team:qa-review main --model claude-opus-4-6 --effort low"] * 2
        + ["/vllm-review main..feat --model claude-opus-5 --effort max"] * 2),
    ("each run's stats show its command name, model, effort and shown=", [
        (OUT / r / "stats.txt").read_text().split(" exit=")[0] for r in RUNS] == [
        "reviewer=qa-review model=claude-opus-4-6 effort=low"] * 2
        + ["reviewer=vllm-review model=claude-opus-5 effort=max shown=qwen3-coder"] * 2),
    ("each run sets the background-wait ceiling to 0", all(m["ceiling"] == "0" for m in runs)),
    ("each run allows /tmp writes and denies edits, commits and pushes in the target", all(
        "Write(//tmp/**)" in m["argv"] and {"Edit", f"Write(/{w}/**)", "Bash(git commit:*)",
                                             "Bash(git push:*)"} <= set(m["argv"])
        for m, w in zip(runs, wts))),
    ("each run works in its own clean worktree at head, named after the run",
     [m["cwd"] for m in runs] == wts
     and all(m["a.go"] == "package a\n" for m in runs)),
    ("a leaked CLAUDE.local.md moves into the run directory", all(
        (OUT / r / "leaked.CLAUDE.local.md").exists() for r in RUNS)),
    ("each run writes its report and stats", all(
        (OUT / r / "report.md").exists() and "wall=" in (OUT / r / "stats.txt").read_text()
        for r in RUNS)),
    ("an error result is an early exit, scored 0 without a grader",
     "early-exit" in (OUT / "qa-opus-4-6-r2/stats.txt").read_text() and len(graders) == 2
     and (OUT / "qa-opus-4-6-r2/marks.txt").read_text() == "qa-opus-4-6-r2\n"),
    ("a warm-up ledger grades one run at a time under P=2", not overlap(graders)),
    ("the grader runs on opus at effort high, warm-up may edit the ledger", "--model opus --effort high"
     in " ".join(graders[0]["grader"]) and f"Edit(/{OUT}/ledger.json)" in graders[0]["grader"]
     and "not frozen" in graders[0]["prompt"]),
    ("marks keep the marks lines only", (OUT / "qa-opus-4-6-r1/marks.txt").read_text()
     == "qa-opus-4-6-r1 C1\nRejected (qa-opus-4-6-r1): b.go races (one goroutine).\n"),
    ("score.py prints each reviewer's command and model in columns as wide as the widest",
     "tier  reviewer     model            runs  quality     sd  criticals  rejected"
     "   $/run\n"
     "   1  qa-review    opus-4-6-low        2     50.0   70.7  0.5/1           0.5"
     "   $0.75\n"
     "   1  vllm-review  qwen3-coder-max     2     50.0   70.7  0.5/1           0.5"
     "   $0.75\n" in out.stdout),
    ("the worktrees are removed", len(git("worktree", "list").stdout.splitlines()) == 1),
]:
    assert ok, (case, out.stdout, out.stderr)
    print("PASS", case)

# A rerun on a frozen ledger regrades runs whose marks were deleted, in parallel, without ledger
# edits.
ledger = json.loads((OUT / "ledger.json").read_text())
(OUT / "ledger.json").write_text(json.dumps({**ledger, "frozen": True}))
(OUT / "qa-opus-4-6-r1/marks.txt").unlink()
(OUT / "vllm-r1/marks.txt").unlink()
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

codex = BIN / "codex"
codex.write_text(r'''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
assert sys.argv[1:] == ["-a", "never", "exec", "--json", "--sandbox", "read-only",
                       "--model", "gpt-6.2-sol", "-c", 'model_reasoning_effort="high"', "-"]
name = Path.cwd().name
prompt = sys.stdin.read().strip()
assert prompt == ("/plain-review main..feat" if name == "plain-sol-r1" else "/qa-review main..feat")
assert Path("a.go").read_text() == "package a\n"
thread = f"codex-{name}"
print(json.dumps({"type": "thread.started", "thread_id": thread}))
print(json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "Merged."}}))
print(json.dumps({"type": "turn.completed"}))
if name == "plain-sol-r1":
    sys.exit()
transcript = Path(os.environ["CODEX_HOME"]) / "sessions/2026/11/24" / f"rollout-date-{thread}.jsonl"
if os.environ.get("STUB_MISSING_ROLLOUT"):
    transcript = transcript.with_suffix(".pending")
transcript.parent.mkdir(parents=True, exist_ok=True)
answers = [("lens_sre", "default", "Agent errored: tool failed")]
if name != "failed-sol-r1":
    answers.append(("lens_architect", "default", "Raw architect finding."))
with transcript.open("w") as rollout:
    for task, role, answer in answers:
        for event in [
            {"type": "function_call", "namespace": "collaboration", "name": "spawn_agent",
             "call_id": task, "arguments": json.dumps({"task_name": task, "agent_type": role})},
            {"type": "function_call_output", "call_id": task,
             "output": json.dumps({"task_name": f"/root/{task}"})},
            {"type": "agent_message", "author": f"/root/{task}",
             "content": [{"type": "input_text", "text": f"Message Type: FINAL_ANSWER\nTask name: /root\n"
                          f"Sender: /root/{task}\nPayload:\n{answer}"}]},
        ]:
            print(json.dumps({"type": "response_item", "payload": event}), file=rollout)
    print(json.dumps({"type": "event_msg", "payload": {"type": "task_complete"}}), file=rollout)
''')
codex.chmod(0o755)
with (TMP / "reviewers.txt").open("a") as reviewers:
    reviewers.write("qa-sol:lenses runner=codex model=gpt-6.2-sol effort=high /qa-review {base}..{head}\n")
    reviewers.write("fresh-claude model=claude-opus-5 /fresh-review {base}\n")
    reviewers.write("plain-sol runner=codex model=gpt-6.2-sol effort=high /plain-review {base}..{head}\n")
    reviewers.write("failed-sol:lenses runner=codex model=gpt-6.2-sol effort=high /qa-review {base}..{head}\n")
command = ["bash", HERE / "run.sh", REPO, "main", "feat", TMP / "reviewers.txt", OUT]
codex_env = {**env, "CODEX_HOME": str(TMP / "codex"), "N": "1"}
out = subprocess.run(command, env=codex_env, capture_output=True, text=True)
run = OUT / "qa-sol-r1"
assert out.returncode == 0, out.stderr
assert (run / "report.md").read_text() == "Merged.\n", (run / "stderr").read_text()
assert (run / "lenses/lens_architect.md").read_text() == "Raw architect finding.\n"
assert (run / "marks.txt").read_text() == "qa-sol-r1.architect C1\n"
assert "cost=? report=7 lenses=1" in (run / "stats.txt").read_text()
log = [json.loads(line) for line in (TMP / "log").read_text().splitlines()]
assert any("/fresh-review main" in entry.get("argv", []) for entry in log)
assert (OUT / "plain-sol-r1/marks.txt").read_text().startswith("plain-sol-r1 C1\n")
assert (OUT / "failed-sol-r1/marks.txt").read_text() == "failed-sol-r1\n"
assert all("The run is failed-sol-r1:" not in entry.get("prompt", "") for entry in log)
print("PASS mixed runner defaults, raw lens grading, plain Codex grading and early exits")

with (TMP / "reviewers.txt").open("a") as reviewers:
    reviewers.write("retry-sol:lenses runner=codex model=gpt-6.2-sol effort=high /qa-review {base}..{head}\n")
retry = OUT / "retry-sol-r1"
combined = (OUT / "marks.txt").read_bytes()
out = subprocess.run(command, env={**codex_env, "STUB_MISSING_ROLLOUT": "1"},
                     capture_output=True, text=True)
assert out.returncode != 0 and "retry-sol-r1: extraction failed" in out.stderr, out
assert "missing Codex rollout" in (retry / "extract.err").read_text()
assert not (retry / "stats.txt").exists() and not (retry / "marks.txt").exists()
assert (OUT / "marks.txt").read_bytes() == combined
pending = next((TMP / "codex/sessions").rglob("rollout-date-codex-retry-sol-r1.pending"))
pending.rename(pending.with_suffix(".jsonl"))
out = subprocess.run(command, env={**codex_env, "STUB_MISSING_ROLLOUT": "1"},
                     capture_output=True, text=True)
assert out.returncode == 0 and (retry / "marks.txt").is_file(), out.stderr
assert not pending.exists(), "retry launched the reviewer again"
print("PASS extraction failures leave scores intact and reuse saved reviewer output on retry")

combined = (OUT / "marks.txt").read_bytes()
(run / "marks.txt").unlink()
out = subprocess.run(command, env={**codex_env, "STUB_FAIL_GRADE": "qa-sol-r1"},
                     capture_output=True, text=True)
assert out.returncode != 0 and "qa-sol-r1: grader wrote no scored line" in out.stderr, out
assert not (run / "marks.txt").exists() and "tier " not in out.stdout
assert (OUT / "marks.txt").read_bytes() == combined
print("PASS grading failure cannot publish a partial score table")

# A run whose worktree add fails is printed as failed.
GITBIN = TMP / "gitbin"
GITBIN.mkdir()
(GITBIN / "git").write_text(
    f'#!/bin/sh\ncase "$*" in *"worktree add"*vllm-r2*) exit 1 ;; esac\nexec {shutil.which("git")} "$@"\n')
(GITBIN / "git").chmod(0o755)
shutil.rmtree(OUT / "vllm-r2")
out = subprocess.run(["bash", HERE / "run.sh", REPO, "main", "feat", TMP / "reviewers.txt", OUT],
                     env={**env, "PATH": f"{GITBIN}:{env['PATH']}"}, capture_output=True, text=True)
assert "vllm-r2: failed, no stats.txt" in out.stderr, out
print("PASS a run that leaves no stats.txt is printed as failed")

# A bad reviewers file fails before any run starts and leaves the output directory alone.
(TMP / "kept").mkdir()
(TMP / "kept/ledger.json").write_text("{}")
for case, lines, err in [
    ("a line without model= fails, even after a valid line",
     "qa-high:lenses model=claude-opus-4-8 /dream-team:qa-review {base}\n"
     "qa-max:lenses effort=max /dream-team:qa-review {base}\n", "qa-max: no model= field"),
    ("a file with no reviewer lines fails", "# none\n\n", "no reviewer lines"),
    ("an unknown runner fails", "qa-high runner=unknown model=model prompt\n", "unknown runner=unknown"),
]:
    (TMP / "bad.txt").write_text(lines)
    out = subprocess.run(["bash", HERE / "run.sh", REPO, "main", "feat", TMP / "bad.txt",
                          TMP / "kept"], env=env, capture_output=True, text=True)
    assert out.returncode == 2 and err in out.stderr, (case, out)
    assert [p.name for p in (TMP / "kept").iterdir()] == ["ledger.json"], (case, out)
    print("PASS", case)
