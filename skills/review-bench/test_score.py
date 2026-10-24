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


def score(marks):
    return subprocess.run([sys.executable, HERE / "score.py", LEDGER, marks], capture_output=True, text=True)


out = score(HERE / "testdata/marks.txt")
assert out.returncode == 0, out.stderr
assert out.stdout == """\
ledger v1: 7 findings, weight 26.5, 2 criticals
tier  reviewer  runs  quality     sd  criticals  rejected   $/run
   1  QR           2     86.8    2.7  1.5/2           0.5   $0.56
   2  CR           2     38.7    1.3  0.0/2           1.0   $0.33
   2  SR-5         1     22.6         1.0/2           0.0
   3  GR           1     18.9         0.0/2           0.0
""", out.stdout
print("PASS fixture table")

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
    (Path(TMP.name) / run / "stats.txt").write_text(f"model=opus effort=high {stats}\n")
out = score(bare)
assert "   1  QR           2     18.9   26.7  0.5/2           0.0\n" in out.stdout, out
print("PASS a bare last line with no newline is a scored run; an uncosted run blanks $/run")
