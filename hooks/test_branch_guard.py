import json, os, subprocess, sys, tempfile

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "branch-guard.py")

repo = tempfile.mkdtemp()
subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t",
                "commit", "-q", "--allow-empty", "-m", "init"], check=True)


def denied(rel):
    p = subprocess.run([sys.executable, HOOK], text=True, capture_output=True,
                       input=json.dumps({"tool_input": {"file_path": os.path.join(repo, rel)}}))
    return '"deny"' in p.stdout


for rel, want in [
    ("SPEC.md", True),
    ("docs/specs/0001-x-design.md", True),
    ("docs/decisions/0001-x.md", True),
    ("notes/x-spec.md", True),
    ("docs/plans/x.md", False),
    ("plans/x.md", False),
    ("test-plan.md", False),
    ("src/main.py", False),
]:
    assert denied(rel) == want, rel

subprocess.run(["git", "-C", repo, "switch", "-q", "-c", "topic"], check=True)
assert not denied("docs/specs/0001-x-design.md")
print("ok")
