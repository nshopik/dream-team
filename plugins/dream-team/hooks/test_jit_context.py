import importlib.util, json, os, subprocess, sys, tempfile, uuid

OWN = r"git\.example\.org[:/]|github\.com[:/]me/"
os.environ["DREAM_TEAM_OWN_REMOTES"] = OWN

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jit-context.py")
spec = importlib.util.spec_from_file_location("jit", HOOK)
jit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jit)

for urls, want in [
    (["git@git.example.org:me/tools.git"], False),
    (["ssh://git@git.example.org:2222/team/tools.git"], False),
    (["https://github.com/me/dotfiles.git"], False),
    (["git@github.com:ME/x.git"], False),
    ([], False),                                               # no remote: local scratch repo
    (["https://github.com/NLnetLabs/unbound.git"], True),
    (["https://github.com/NLnetLabs/unbound.git",               # fork + upstream
      "git@github.com:me/unbound.git"], True),
    (["https://github.com/meandyou/x.git"], True),             # prefix of my name is not me
]:
    assert jit.upstream_remote(urls) == want, urls


def context(tool_input, cwd="/", own=OWN, session=None):
    env = {**os.environ, "DREAM_TEAM_OWN_REMOTES": own}
    p = subprocess.run([sys.executable, HOOK], text=True, capture_output=True, env=env,
                       input=json.dumps({"session_id": session or uuid.uuid4().hex, "cwd": cwd,
                                         "tool_input": tool_input}))
    return json.loads(p.stdout)["hookSpecificOutput"]["additionalContext"] if p.stdout else ""


def repo(remote):
    d = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", d], check=True)
    subprocess.run(["git", "-C", d, "remote", "add", "origin", remote], check=True)
    return d


upstream = repo("https://github.com/NLnetLabs/unbound.git")
assert "<upstream_repo>" in context({"file_path": os.path.join(upstream, "new/x.c")})
assert "<upstream_repo>" in context({"command": "git commit -m x"}, upstream)
assert "<upstream_repo>" not in context({"command": "git commit -m x"}, upstream, own="")

mine = repo("git@github.com:me/x.git")
assert "<prose_style>" in context({"file_path": os.path.join(mine, "x.md")})

assert jit.TEMPLATE in context({"file_path": "/r/docs/specs/0001-x-design.md"})
assert os.path.isfile(jit.TEMPLATE)
assert "<decision_record>" in context({"file_path": "/r/docs/decisions/0003-x.md"})
assert "<decision_record>" in context({"command": "git mv docs/decisions/x.md docs/decisions/0003-x.md"})
s = uuid.uuid4().hex                                           # vcs fires first, forge on the next call
assert "<vcs_workflow>" in context({"command": "gh pr view 1"}, session=s)
assert "<forge_tooling>" in context({"command": "gh pr view 1"}, session=s)
assert "<claude_md>" in context({"file_path": os.path.join(mine, "CLAUDE.local.md")})
assert "<claude_md>" in context({"command": "echo x >> CLAUDE.local.md"})
p = subprocess.run([sys.executable, HOOK], text=True, capture_output=True,
                   input=json.dumps({"hook_event_name": "SessionStart", "session_id": "x"}))
assert "<project_notes>" in json.loads(p.stdout)["hookSpecificOutput"]["additionalContext"]
print("ok")
