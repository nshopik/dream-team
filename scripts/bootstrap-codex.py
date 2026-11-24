#!/usr/bin/env python3
"""Install Dream Team skills, agent roles, and hooks for the local Codex CLI."""

import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import tempfile
import tomllib


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_ONLY = {"assemble-meta", "friction", "review-bench"}


def atomic_write(path, content):
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as output:
        output.write(content)
    os.replace(output.name, path)


def digest(content):
    return hashlib.sha256(content.encode()).hexdigest()


def install_hooks(codex_home):
    config = (codex_home / "hooks.json").resolve()
    settings = json.loads(config.read_text()) if config.exists() else {}
    events = settings.setdefault("hooks", {})
    defaults = json.loads((ROOT / "hooks" / "hooks.json").read_text())["hooks"]
    command = f"python3 {shlex.quote(str(ROOT / 'hooks' / 'jit-context.py'))} --codex"
    changed = False
    for event, groups in defaults.items():
        entries = events.setdefault(event, [])
        for group in groups:
            if group.get("matcher") == "Write|Edit":
                group["matcher"] = "^apply_patch$"
            group["hooks"][0]["command"] = command
            if group not in entries:
                entries.append(group)
                changed = True
    if changed:
        atomic_write(config, json.dumps(settings, indent=2) + "\n")


def main():
    home = Path.home()
    skills_dir = home / ".agents" / "skills"
    codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex"))
    agents_dir = codex_home / "agents"
    skills = {
        skills_dir / skill.name: skill
        for skill in sorted((ROOT / "skills").iterdir())
        if (skill / "SKILL.md").is_file() and skill.name not in CLAUDE_ONLY
    }
    role_index = agents_dir / ".dream-team-roles.json"
    recorded = json.loads(role_index.read_text()) if role_index.exists() else {}
    roles = {}
    for source in sorted((ROOT / "agents").glob("*.md")):
        _, frontmatter, instructions = source.read_text().split("---", 2)
        name = f"dream-team-{source.stem}"
        description = f"Dream Team {source.stem.replace('-', ' ')}"
        match = re.search(r"^description: (.+)$", frontmatter, re.M)
        if match and match[1][0] not in ">|":
            description = match[1].strip("\"'")
        instructions = instructions.strip().replace("${CLAUDE_PLUGIN_ROOT}", str(ROOT))
        content = (
            f'name = {json.dumps(name)}\n'
            f'description = {json.dumps(description, ensure_ascii=False)}\n'
            f'developer_instructions = {json.dumps(instructions, ensure_ascii=False)}\n'
        )
        tomllib.loads(content)
        roles[agents_dir / f"{name}.toml"] = content

    for target, skill in skills.items():
        if target.is_symlink() and target.resolve() == skill:
            continue
        if target.exists() or target.is_symlink():
            marker = target / ".dream-team-source"
            if target.is_symlink() or not marker.is_file() or marker.read_text() != str(skill):
                raise SystemExit(f"Existing skill conflicts with Dream Team: {target}")
    for target, content in roles.items():
        if target.is_symlink():
            raise SystemExit(f"Existing agent conflicts with Dream Team: {target}")
        if target.exists():
            installed = target.read_text()
            if installed != content and recorded.get(target.name) != digest(installed):
                raise SystemExit(f"Existing agent conflicts with Dream Team: {target}")

    skills_dir.mkdir(parents=True, exist_ok=True)
    agents_dir.mkdir(parents=True, exist_ok=True)
    for target, skill in skills.items():
        with tempfile.TemporaryDirectory(prefix=".dream-team-", dir=skills_dir) as scratch:
            staged = Path(scratch) / "new"
            shutil.copytree(skill, staged, ignore=shutil.ignore_patterns("__pycache__", "evals"))
            (staged / ".dream-team-source").write_text(str(skill))
            if target.name == "craft-it":
                shutil.copyfile(ROOT / "workflows" / "craft-it-loop.js", staged / "craft-it-loop.js")
            previous = Path(scratch) / "previous"
            if target.exists() or target.is_symlink():
                target.rename(previous)
            try:
                staged.rename(target)
            except OSError:
                if previous.exists() or previous.is_symlink():
                    previous.rename(target)
                raise
    for target, content in roles.items():
        if not target.exists() or target.read_text() != content:
            atomic_write(target, content)
        recorded[target.name] = digest(content)
        atomic_write(role_index, json.dumps(recorded, indent=2) + "\n")
    install_hooks(codex_home)
    print(f"Dream Team ready: {len(skills)} skills in {skills_dir}, {len(roles)} roles in {agents_dir}")


if __name__ == "__main__":
    main()
