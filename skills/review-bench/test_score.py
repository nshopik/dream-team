#!/usr/bin/env python3
"""score.py over the fixture ledger, marks and run stats in testdata/.

Usage: python3 test_score.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
TMP = tempfile.TemporaryDirectory()
LEDGER = HERE / "testdata/ledger.json"


def score(marks, ledger=LEDGER):
    return subprocess.run([sys.executable, HERE / "score.py", ledger, marks], capture_output=True, text=True)


out = score(HERE / "testdata/marks.txt")
assert out.returncode == 0, out.stderr
assert out.stdout == """\
ledger v1: 7 findings, weight 26, 2 criticals
tier  reviewer     model             runs  quality     sd  criticals  rejected   $/run
   1  qa-review    opus-4-8-high        2     87.5    1.4  1.5/2           0.5   $0.56
   2  code-review  opus-4-8-high        2     38.5    0.0  0.0/2           1.0   $0.33
   2                                    1     21.2         1.0/2           0.0
   3  vllm-review  qwen3-coder-high     1     17.3         0.0/2           0.0   $0.12
""", out.stdout
print("PASS fixture table: shown= replaces the model; a run without stats blanks its labels")

for marks, want, case in [
    ("QR-r1.arch C1 C9~\n", "QR-r1.arch: C9 is not in the ledger", "an ID outside the ledger fails"),
    ("QR-r1:arch C1\n", "QR-r1:arch: not a <PREFIX>-r<k>[.<lens>] token", "a malformed run token fails"),
]:
    bad = Path(TMP.name) / "marks.txt"
    bad.write_text(marks)
    out = score(bad)
    assert out.returncode != 0 and want in out.stderr, out
    print("PASS", case)

bare = Path(TMP.name) / "marks.txt"
bare.write_text("QR-r1 C1\nQR-r2")
for run, stats in [("QR-r1", "exit=0 wall=118s cost=$0.53 report=5644 lenses=1"),
                   ("QR-r2", "exit=1 wall=3s cost=? report=0 lenses=0 early-exit")]:
    (Path(TMP.name) / run).mkdir()
    (Path(TMP.name) / run / "stats.txt").write_text(
        f"reviewer=qa-review model=claude-opus-4-8 effort=high {stats}\n")
out = score(bare)
row = "   1  qa-review  opus-4-8-high     2     19.2   27.2  0.5/2           0.0\n"
assert row in out.stdout, out
print("PASS a bare last line with no newline is a scored run; an uncosted run blanks $/run")

minor = Path(TMP.name) / "minor"
minor.mkdir()
(minor / "ledger.json").write_text('{"version": 1, "rows": ['
    '{"id": "C1", "severity": "critical", "plausible": false},'
    '{"id": "N1", "severity": "minor", "plausible": false}]}')
(minor / "marks.txt").write_text("QR-r1 N1\n")
out = score(minor / "marks.txt", minor / "ledger.json")
assert "2 findings, weight 10.5," in out.stdout and "     4.8  " in out.stdout, out
print("PASS a minor row weighs 0.5")

same = Path(TMP.name) / "same"
same.mkdir()
(same / "marks.txt").write_text("LP-a-r1 C1\nLP-b-r1\nLP-c-r1\n")
for run, model in [("LP-a-r1", "opus-5-5"), ("LP-b-r1", "opus-5-5"), ("LP-c-r1", "opus-4-8")]:
    (same / run).mkdir()
    (same / run / "stats.txt").write_text(f"reviewer=Dispatch model=claude-{model} effort=high\n")
out = score(same / "marks.txt")
for row in ("  LP-a      opus-5-5-high", "  LP-b      opus-5-5-high", "  Dispatch  opus-4-8-high"):
    assert row in out.stdout, out
print("PASS rows that would print the same reviewer and model show their prefixes")
