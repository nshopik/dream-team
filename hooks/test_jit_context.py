import json, os, subprocess, sys, tempfile, uuid

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jit-context.py")


def context(tool_input, cwd="/", session=None):
    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    p = subprocess.run([sys.executable, HOOK], text=True, capture_output=True, env=env,
                       input=json.dumps({"session_id": session or uuid.uuid4().hex, "cwd": cwd,
                                         "tool_input": tool_input}))
    return json.loads(p.stdout)["hookSpecificOutput"]["additionalContext"] if p.stdout else ""


def repo(marker=None):
    d = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", d], check=True)
    if marker:
        subprocess.run(["git", "-C", d, "config", "--local", "dream-team.upstream", marker],
                       check=True)
    return d


upstream = repo("true")
assert "<upstream_repo>" in context({"file_path": os.path.join(upstream, "new/x.c")})
for cmd in ["git commit -m x", "gh pr create -t x"]:
    assert "load scope-commit and scope-mr" in context({"command": cmd}, upstream), cmd
for d in [repo(), repo("false")]:
    c = context({"command": "git commit -m x"}, d)
    assert "<vcs_workflow>" in c and "<upstream_repo>" not in c, d

mine = repo()
c = context({"file_path": os.path.join(mine, "x.md")})
assert "<prose_style>" in c and "<upstream_repo>" not in c

s = uuid.uuid4().hex                                           # vcs fires first, forge on the next call
assert "<vcs_workflow>" in context({"command": "gh pr view 1"}, session=s)
assert "<forge_tooling>" in context({"command": "gh pr view 1"}, session=s)
assert "<claude_md>" in context({"file_path": os.path.join(mine, "CLAUDE.local.md")})
assert "<claude_md>" in context({"command": "echo x >> CLAUDE.local.md"})
p = subprocess.run([sys.executable, HOOK], text=True, capture_output=True,
                   input=json.dumps({"hook_event_name": "SessionStart", "session_id": "x"}))
start = json.loads(p.stdout)["hookSpecificOutput"]["additionalContext"]
assert "<project_notes>" in start and "<issue_sized>" in start
assert "issue in chat → settle" in start and "during other work" in start
assert "research result for an open issue → post it as a comment on that issue; do not prompt" in start
assert "per-task artifact location" in start
assert "under 8 KB" in context({"file_path": os.path.join(mine, "CLAUDE.md")})
print("ok")
