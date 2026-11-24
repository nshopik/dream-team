"""Exercise install and upgrade in an isolated Codex home."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib


ROOT = Path(__file__).resolve().parents[1]
ROLE = "dream-team-architect-reviewer"


with tempfile.TemporaryDirectory() as tmp:
    scratch = Path(tmp)
    source = scratch / "source"
    for directory in ("scripts", "skills", "agents", "hooks", "workflows"):
        shutil.copytree(ROOT / directory, source / directory,
                        ignore=shutil.ignore_patterns("__pycache__", "evals"))
    codex = scratch / "codex"
    codex.mkdir()
    home = scratch / "home"
    hooks = scratch / "managed-hooks.json"
    existing = {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "existing"}]}]}}
    hooks.write_text(json.dumps(existing))
    (codex / "hooks.json").symlink_to(hooks)
    env = {**os.environ, "CODEX_HOME": str(codex)}
    bootstrap = source / "scripts/bootstrap-codex.py"
    install = [sys.executable, "-c",
               "from pathlib import Path; import runpy, sys; "
               "Path.home = classmethod(lambda cls: cls(sys.argv[2])); "
               "runpy.run_path(sys.argv[1], run_name='__main__')", str(bootstrap), str(home)]
    subprocess.run(install, env=env, check=True)
    assert (codex / "hooks.json").is_symlink()
    first = hooks.read_bytes()
    subprocess.run(install, env=env, check=True)
    assert hooks.read_bytes() == first
    events = json.loads(first)["hooks"]
    assert events["SessionStart"][0] == existing["hooks"]["SessionStart"][0]
    command = next(g["hooks"][0]["command"] for g in events["PreToolUse"]
                   if g["matcher"] == "^apply_patch$")
    patch = {"hook_event_name": "PreToolUse", "tool_name": "apply_patch",
             "session_id": Path(tmp).name, "cwd": tmp,
             "tool_input": {"command": "*** Update File: AGENTS.md"}}
    response = subprocess.check_output(command, shell=True, input=json.dumps(patch), text=True)
    assert "Editing AGENTS.md" in json.loads(response)["hookSpecificOutput"]["additionalContext"]

    skills = home / ".agents/skills"
    assert (skills / "craft-it/craft-it-loop.js").read_bytes() == (source / "workflows/craft-it-loop.js").read_bytes()
    assert "allow_implicit_invocation: false" in (skills / "qa-review/agents/openai.yaml").read_text()
    assert not (skills / "assemble-meta").exists()
    obsolete = skills / "craft-it/obsolete.md"
    obsolete.write_text("stale")
    role_source = source / "agents/architect-reviewer.md"
    role_source.write_text(role_source.read_text() + "\nReview marker for upgrade.\n")
    subprocess.run(install, env=env, check=True)
    assert not obsolete.exists()
    role_file = codex / "agents" / f"{ROLE}.toml"
    assert "Review marker for upgrade." in tomllib.loads(role_file.read_text())["developer_instructions"]

    role_file.write_text(role_file.read_text() + "# user customization\n")
    assert subprocess.run(install, env=env, capture_output=True).returncode != 0
    assert role_file.read_text().endswith("# user customization\n")

print("PASS Codex bootstrap")
