import json, os, subprocess, sys, tempfile, uuid

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jit-context.py")


def context(tool_input, cwd="/", session=None, *, codex=False, tool_name=None, event="PreToolUse"):
    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    p = subprocess.run([sys.executable, HOOK, *(["--codex"] if codex else [])],
                       text=True, capture_output=True, env=env, check=True,
                       input=json.dumps({"session_id": session or uuid.uuid4().hex, "cwd": cwd,
                                         "tool_input": tool_input, "tool_name": tool_name,
                                         "hook_event_name": event}))
    return json.loads(p.stdout)["hookSpecificOutput"]["additionalContext"] if p.stdout else ""


def repo(own=None):
    d = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", d], check=True)
    if own:
        subprocess.run(["git", "-C", d, "config", "--local", "dream-team.own", own], check=True)
    return d


for upstream in [repo(), repo("false"), repo("maybe")]:
    c = context({"file_path": os.path.join(upstream, "new/x.c")})
    assert "<upstream_repo>" in c and "/dream-team:setup-dream-team" in c, upstream
    for cmd in ["git commit -m x", "gh pr create -t x"]:
        assert "load scope-commit and scope-mr" in context({"command": cmd}, upstream), cmd
for d in [repo("true"), repo("yes"), repo("1"), tempfile.mkdtemp()]:
    c = context({"command": "git commit -m x"}, d)
    assert "<vcs_workflow>" in c and "<upstream_repo>" not in c, d

mine = repo("true")
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
patch = {"command": "*** Begin Patch\n*** Update File: docs.md\n*** Update File: AGENTS.md\n*** End Patch"}
session = uuid.uuid4().hex
assert "Editing AGENTS.md" in context(patch, mine, session, codex=True, tool_name="apply_patch")
assert "<prose_style>" in context(patch, mine, session, codex=True, tool_name="apply_patch")
assert not context(patch, mine, session, codex=True, tool_name="apply_patch")
assert "$dream-team:setup-dream-team" in context(patch, repo(), codex=True, tool_name="apply_patch")
for codex in (False, True):
    notes = context({}, mine, codex=codex, event="SessionStart")
    assert all(term in notes for term in ("AGENTS.local.md", "CLAUDE.local.md", "git check-ignore"))
    for filename in ("AGENTS.md", "CLAUDE.md"):
        assert "<claude_md>" in context({"file_path": filename}, mine, codex=codex)
assert "<vcs_workflow>" in context({"command": "git commit -m x"}, mine, codex=True, tool_name="Bash")
lab = context({"command": "ssh example"}, codex=True, tool_name="Bash")
assert "dream-team:lab-runner" not in lab
role = lab.split("a subagent with the prompt from `", 1)[1].split("`", 1)[0]
assert os.path.isabs(role) and os.path.isfile(role) and role.endswith("lab-runner.md"), role
print("ok")
