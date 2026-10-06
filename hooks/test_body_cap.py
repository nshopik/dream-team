import json, os, re, shlex, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "body-cap.py")
os.environ["CLAUDE_PLUGIN_DATA"] = tempfile.mkdtemp()   # keep real bounce state untouched
SEEN = os.path.join(os.environ["CLAUDE_PLUGIN_DATA"], "body-cap-seen")

def run(cmd):
    p = subprocess.run([sys.executable, HOOK], text=True, capture_output=True,
                       input=json.dumps({"tool_input": {"command": cmd}}))
    if p.returncode:
        return "CRASH", p.stderr.strip().splitlines()[-1]
    out = p.stdout.strip()
    if not out:
        return "ALLOW-SILENT", ""
    return verdict(out)

def verdict(out):
    h = json.loads(out)["hookSpecificOutput"]
    if h.get("permissionDecision") == "deny":
        return "DENY", h["permissionDecisionReason"]
    return "ALLOW+RULES", h["additionalContext"]

def show(name, cmd):
    v, r = run(cmd)
    print(f"{name:34} {v:12} {r.splitlines()[0][:70] if r else ''}")

BODY = "docs: document dedup\n\nCloses #4 - the remaining work is operator-side, not irontap-side."

# 7. MR rubric: a rung rubric stamped as a heading or lead-in denies; prose passes.
def mr(desc):
    return ("glab api -X POST projects/1/merge_requests -f description=- <<'EOF'\n"
            + desc + "\nEOF")

os.path.exists(SEEN) and os.remove(SEEN)
show("rubric heading: look at first", mr("Fixes the leak.\n\n## Look at first\n\nspool.rs."))
show("rubric heading: challenge",     mr("Fixes it.\n\n## Challenge\n\nWe went with X over Y."))
show("rubric lead-in with colon",     mr("Fixes it.\n\nWhere to look first: spool.rs is the spot."))
# A "what it does" content section is endorsed, not a rubric — it passes.
show("what-it-does section passes",    mr("Fixes the leak.\n\n## What it does\n\n- withRecover reports the panic."))
# Prose that merely mentions the words inline (no heading, no `rubric:` lead-in) passes.
show("inline mention passes",         mr("Look at `spool.rs` first for the parking path that\nchanges behavior on restart."))
show("plain prose passes",            mr("Spill replay orders by the filename date, stamped before\nthe first byte, so a stale batch can no longer land last."))

assert run(mr("x.\n\n## Look at first\n\ny."))[0] == "DENY"
assert run(mr("x.\n\n## Challenge\n\ny."))[0] == "DENY"
assert run(mr("x.\n\nWhere to look first: y."))[0] == "DENY"
assert run(mr("x.\n\n## What it does\n\n- y."))[0] == "ALLOW+RULES"
assert run(mr("Look at `spool.rs` first for the parking path."))[0] == "ALLOW+RULES"
assert run(mr("Spill replay orders by the filename date."))[0] == "ALLOW+RULES"
print(f"{'mr rubric detector agrees':34} {'OK':12} 3 deny / 3 pass")

# 8. file flags: `gh --body-file` measures what the file holds.
# Before this, a body passed by file was measured as nothing and posted unchecked.
fd = tempfile.mkdtemp()
def wrote(name, text):
    p = os.path.join(fd, name)
    open(p, "w").write(text)
    return p

big = wrote("big.md", "word " * 400)
rubric = wrote("rubric.md", "Fixes it.\n\n## Look at first\n\nspool.rs.")

show("mr --body-file over cap", f"gh pr create --body-file {big}")
show("mr -F over cap",          f"gh pr create -F {big}")
show("mr --body-file= rubric",  f"gh pr create --body-file={rubric}")
show("gh api -F key=value",     "gh api repos/x/y -F description=@z.md")
show("unreadable file allows",  "gh pr create --body-file /nonexistent/none.md")

assert run(f"gh pr create --body-file {big}")[0] == "DENY"
assert run(f"gh pr create -F {big}")[0] == "DENY"
assert run(f"gh pr create --body-file={rubric}")[0] == "DENY"
# gh api's -F is a raw field, not a file; glab's short flags are the reverse.
assert run("gh api repos/x/y -F description=@z.md")[0] == "ALLOW-SILENT"
assert run("gh pr create --body-file /nonexistent/none.md")[0] == "ALLOW-SILENT"
print(f"{'file-flag bodies measured':34} {'OK':12} 3 deny / 2 pass")

# 9. diff budget: a description that outruns the change it describes bounces once.
# Needs a repo with a known base, so build a throwaway one.
def run_in(cmd, cwd, **payload):
    p = subprocess.run([sys.executable, HOOK], text=True, capture_output=True, cwd=cwd,
                       input=json.dumps({"tool_input": {"command": cmd}, **payload}))
    out = p.stdout.strip()
    if not out:
        return "ALLOW-SILENT", ""
    return verdict(out)

repo = tempfile.mkdtemp()
def git(*a):
    subprocess.run(("git",) + a, cwd=repo, capture_output=True, check=True)
git("init", "-qb", "main")
git("config", "user.email", "t@t"); git("config", "user.name", "t")
open(os.path.join(repo, "f"), "w").write("base\n")
git("add", "f"); git("commit", "-qm", "seed: add f")
git("checkout", "-qb", "topic")
open(os.path.join(repo, "f"), "w").write("base\n" + "line\n" * 19)   # 19 lines added
git("add", "f"); git("commit", "-qm", "f: extend")

# 19 changed lines -> budget max(80, 5*19) = 95 words.
long_body = "gh pr create --body " + json.dumps("word " * 140)
short_body = "gh pr create --body " + json.dumps("word " * 90)
os.path.exists(SEEN) and os.remove(SEEN)
v, r = run_in(long_body, repo)
print(f"{'over diff budget':34} {v:12} {r.splitlines()[0][:70]}")
print(f"{'over budget, re-issued':34} {run_in(long_body, repo)[0]}")
print(f"{'under diff budget':34} {run_in(short_body, repo)[0]}")
print(f"{'outside a repo passes':34} {run_in(long_body, tempfile.mkdtemp())[0]}")

os.path.exists(SEEN) and os.remove(SEEN)
assert run_in(long_body, repo)[0] == "DENY"
assert run_in(long_body, repo)[0] == "ALLOW+RULES"      # unchanged re-issue passes
assert run_in(short_body, repo)[0] == "ALLOW+RULES"
assert run_in(long_body, tempfile.mkdtemp())[0] == "ALLOW+RULES"   # unmeasurable, never blocks
print(f"{'diff budget':34} {'OK':12} 1 deny / 3 pass")

# 10. gates are keyed per gate, so a body that trips two owes a bounce to each.
over_and_rung4 = ("gh pr create --body "
                  + json.dumps("word " * 140 + "The setting is deliberately left out."))
os.path.exists(SEEN) and os.remove(SEEN)
first = run_in(over_and_rung4, repo)
second = run_in(over_and_rung4, repo)
third = run_in(over_and_rung4, repo)
print(f"{'two gates: 1st':34} {first[0]:12} {first[1].splitlines()[0][:60]}")
print(f"{'two gates: 2nd':34} {second[0]:12} {second[1].splitlines()[0][:60]}")
print(f"{'two gates: 3rd':34} {third[0]:12}")
assert first[0] == "DENY" and "deliberately left out" in first[1]
assert second[0] == "DENY" and "budget" in second[1]
assert third[0] == "ALLOW+RULES"
print(f"{'per-gate bounce':34} {'OK':12} 2 deny / 1 pass")

# 10b. commits are the scope-commit skill's job: the hook stays silent on them.
assert run("git commit -F - <<'EOF'\n" + BODY + "\nEOF") == ("ALLOW-SILENT", "")
print(f"{'commit passes silently':34} {'OK':12}")

# 11. issues: scope-issue section rides along under the cap, 500-word cap denies.
under = "gh issue create --title t --body " + json.dumps("word " * 490)
over = "glab issue create -t t -d " + json.dumps("word " * 510)
show("issue under cap", under)
show("issue over cap", over)
v, r = run(under)
assert v == "ALLOW+RULES" and "<issue_style>" in r and "## Proposal" in r
v, r = run(over)
assert v == "DENY" and "over the 500-word ceiling" in r
print(f"{'issue gate':34} {'OK':12} 1 deny / 1 pass")

# 11b. a fenced log is evidence, not prose: it does not count toward the ceiling.
log = "```\n" + "\n".join("word " * 40 for _ in range(10)) + "\n```"
for prefix, want in (("", "ALLOW+RULES"), ("```\n", "DENY")):
    cmd = "gh issue create --title t --body " + shlex.quote("word " * 480 + "\n\n" + prefix + log)
    show("issue with fenced log", cmd)
    v, r = run(cmd)
    assert v == want and ("ceiling" in r) == (want == "DENY")
print(f"{'issue fenced evidence':34} {'OK':12} 400 fenced words free")

# 11c. table rows are measurements too: charging per cell would price the table
# above the paragraph it replaces.
table = "\n".join("| " + " | ".join(["word"] * 6) + " |" for _ in range(20))
for rows, want in ((table, "ALLOW+RULES"), (table.replace("|", " "), "DENY")):
    cmd = "gh issue create --title t --body " + shlex.quote("word " * 480 + "\n\n" + rows)
    show("issue with table", cmd)
    v, r = run(cmd)
    assert v == want and ("ceiling" in r) == (want == "DENY")
print(f"{'issue table rows free':34} {'OK':12} 120 table words free")

# 13. bodies reached indirectly: `$(cat)`, `--input` JSON, `gh api`, heredoc-written files.
words = "word " * 350
md = wrote("desc.md", words)
short = wrote("short.md", "word " * 20)
js = wrote("desc.json", json.dumps({"description": words}))
gh_js = wrote("gh.json", json.dumps({"body": words}))
fresh = os.path.join(fd, "fresh.md")                     # written by the command itself
half = "word " * 200
q = shlex.quote
shapes = [
    ("$(cat) in -f description=", "DENY", f'glab api -X PUT projects/1/merge_requests/9 -f description="$(cat {md})"'),
    ("$(cat) in --body",          "DENY", f'gh pr edit 9 --body "$(cat {md})"'),
    ("$(cat) under cap",   "ALLOW+RULES", f'gh pr edit 9 --body "$(cat {short})"'),
    ("glab api --input json",     "DENY", f"glab api -X PUT projects/1/merge_requests/9 --input {js}"),
    ("gh api --input body key",   "DENY", f"gh api -X PATCH repos/o/r/pulls/9 --input {gh_js}"),
    ("--input non-string value", "ALLOW-SILENT", f"glab api -X PUT projects/1/merge_requests/9 --input {wrote('list.json', json.dumps({'description': ['a', 'b']}))}"),
    ("gh api pulls -f body=",     "DENY", f'gh api -X PATCH repos/o/r/pulls/9 -f body="$(cat {md})"'),
    ("gh api issues -f body=",    "DENY", f"gh api -X PATCH repos/o/r/issues/7 -f body={q('word ' * 550)}"),
    ("heredoc then --body-file",  "DENY", f"cat > {fresh} <<'EOF'\nit's {words}\nEOF\ngh pr edit 9 --body-file {fresh}"),
    ("heredoc then @path",        "DENY", f"cat <<'EOF' > {fresh}\n{words}\nEOF\nglab api projects/1/merge_requests -F description=@{fresh}"),
    ("heredoc appended",          "DENY", f"cat > {fresh} <<'EOF'\n{half}\nEOF\ncat >> {fresh} <<'EOF'\n{half}\nEOF\ngh pr edit 9 --body-file {fresh}"),
    # Comments, reviews and notes are not the description; reads send no body at all.
    ("gh api issue comment", "ALLOW-SILENT", f"gh api repos/o/r/issues/7/comments -f body={q(words)}"),
    ("gh api PR review",     "ALLOW-SILENT", f"gh api repos/o/r/pulls/9/reviews -f body={q(words)}"),
    ("comment naming /pulls", "ALLOW-SILENT", f"gh api repos/o/r/issues/7/comments -f body={q('see /pulls ' + words)}"),
    ("comment quoting PR path", "ALLOW-SILENT", f"gh api repos/o/r/issues/7/comments -f body={q('dup of repos/o/r/pulls/3 ' + words)}"),
    ("glab note naming issues", "ALLOW-SILENT", f"glab api -X POST projects/1/merge_requests/9/notes -f body={q('fixes the issues here ' + 'word ' * 600)}"),
    ("append to existing file",   "DENY", f"cat >> {wrote('draft.md', half)} <<'EOF'\n{'word ' * 150}\nEOF\ngh pr edit 9 --body-file {os.path.join(fd, 'draft.md')}"),
    ("glab MR note",         "ALLOW-SILENT", f"glab api -X POST projects/1/merge_requests/9/notes -f body={q(words)}"),
    ("gh api read piped",    "ALLOW-SILENT", f"gh api repos/o/r/pulls --paginate | python3 - <<'EOF'\n{words}\nEOF"),
    ("gh api search piped",  "ALLOW-SILENT", f"gh api 'search/issues?q=repo:o/r' | python3 - <<'EOF'\n{words}\nEOF"),
    ("PR named in heredoc", "ALLOW-SILENT", "cat > x.py <<'PY'\nprint('gh pr create --body x')\nPY\npython3 x.py"),
    ("earlier heredoc skipped", "ALLOW+RULES", f"cat > n.txt <<'A'\n{words}\nA\ngh pr create --body-file - <<'B'\nshort body\nB"),
    ("commit then PR heredoc", "ALLOW+RULES", "git commit -m 'a: b' && git push && gh pr create --body-file - <<'EOF'\nshort body\nEOF"),
]
for name, want, cmd in shapes:
    show(name, cmd)
    v, r = run(cmd)
    assert v == want and ("-word ceiling" in r) == (want == "DENY"), name
assert not os.path.exists(fresh)
print(f"{'indirect file bodies measured':34} {'OK':12} {len(shapes)} cases")

# sections(): only lowercase-slug `##` headings become sections; any `##` ends one.
import importlib.util
spec = importlib.util.spec_from_file_location("body_cap", HOOK)
body_cap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(body_cap)
for text, want in [
    ("## fill\nx\n## Two words\ny", {"fill": "x"}),
    ("## fill\nx\n## Examples\ny", {"fill": "x"}),
    ("## \nfoo\nbar",               {}),                 # bare heading takes no next line
    ("intro\n## a-b\n body \n",     {"a-b": "body"}),
]:
    assert body_cap.sections(text) == want, (text, body_cap.sections(text))
print(f"{'sections() parse':34} {'OK':12}")

# 14. deny headers live in the hook, prepended outside the style tag.
headers = [
    ("--fill", "glab mr create --fill", "`--fill` writes", "<mr_style>\n- Commit body"),
]
for name, cmd, head, tag in headers:
    v, r = run(cmd)
    assert v == "DENY" and r.startswith(head) and tag in r and "{" not in r, (name, r)
for kind in ("scope-issue", "scope-mr"):
    text = open(os.path.join(HERE, "..", "skills", kind, "SKILL.md")).read()
    assert not re.search(r"\{\w+\}", text) and "re-run" not in text, kind
print(f"{'deny headers in hook':34} {'OK':12} {len(headers)} cases")
