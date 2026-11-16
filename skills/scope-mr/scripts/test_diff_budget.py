import os, subprocess, sys, tempfile

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diff-budget.py")
tmp = tempfile.mkdtemp()


def run(body, cwd, *args):
    path = os.path.join(tmp, "body.md")
    open(path, "w").write(body)
    p = subprocess.run([sys.executable, SCRIPT, path, *args], cwd=cwd,
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout


repo = tempfile.mkdtemp()
def git(*a):
    subprocess.run(("git",) + a, cwd=repo, capture_output=True, check=True)
def write(text):
    open(os.path.join(repo, "f"), "w").write(text)
git("init", "-qb", "main")
git("config", "user.email", "t@t"); git("config", "user.name", "t")
write("base\n"); git("add", "f"); git("commit", "-qm", "seed: add f")
git("checkout", "-qb", "topic")
write("base\n" + "line\n" * 19); git("add", "f"); git("commit", "-qm", "f: extend")
git("branch", "-q", "dev", "main")

words = lambda n: "word " * n
log = "```\n" + "\n".join(words(40) for _ in range(10)) + "\n```"
table = "\n".join("| " + " | ".join(["word"] * 6) + " |" for _ in range(20))
outside = tempfile.mkdtemp()

# 19 changed lines -> budget max(80, 5*19) = 95 words.
for name, body, cwd, args, want, over in [
    ("under budget",          words(90), repo, (), "90 words, diff: 19 lines, budget: 95", False),
    ("over budget",           words(140), repo, (), "140 words, diff: 19 lines, budget: 95", True),
    ("named base",            words(140), repo, ("--base", "dev"), "diff: 19 lines", True),
    ("base is HEAD",          words(140), repo, ("--base", "topic"), "diff unmeasurable", False),
    ("outside a repo",        words(140), outside, (), "diff unmeasurable", False),
    ("fenced log free",       words(90) + "\n\n" + log, repo, (), "90 words", False),
    ("unterminated fence",    words(90) + "\n\n```\n" + log, repo, (), "491 words", True),
    ("table rows free",       words(90) + "\n\n" + table, repo, (), "90 words", False),
    ("table without pipes",   words(90) + "\n\n" + table.replace("|", " "), repo, (), "210 words", True),
    ("trailers stripped",     words(90) + "\n\nRefs: #4\nCo-authored-by: a <a@b>\n", repo, (), "90 words", False),
    ("prose opener counted",  words(90) + "\n\nDeferred: x y z", repo, (), "94 words", False),
]:
    out = run(body, cwd, *args)
    assert want in out and ("Over budget" in out) == over, (name, out)
    print(f"{name:24} OK")

# Uncommitted work counts: 20 more lines -> 39 lines, budget 195.
write("base\n" + "line\n" * 39)
out = run(words(140), repo)
assert "diff: 39 lines, budget: 195" in out and "Over budget" not in out, out
print(f"{'working tree counted':24} OK")
