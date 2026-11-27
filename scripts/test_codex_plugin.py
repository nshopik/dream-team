import json
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text())


repo = Path(__file__).resolve().parents[1]
marketplace = read(repo / ".agents/plugins/marketplace.json")
entries = {entry["name"]: entry for entry in marketplace["plugins"]}
plugin_root = repo / entries["dream-team"]["source"]["path"]
codex = read(plugin_root / ".codex-plugin/plugin.json")
claude = read(plugin_root / ".claude-plugin/plugin.json")
assert marketplace["name"] == codex["name"] == "dream-team"

skills = {plugin_root / path for path in codex["skills"]}
assert skills == {
    manifest.parent for manifest in plugin_root.glob("skills/*/SKILL.md")
    if manifest.parent.name not in {"assemble-meta", "friction", "review-bench"}
}
workflow = plugin_root / "skills/craft-it/craft-it-loop.js"
workflows = {plugin_root / path for path in claude["workflows"]}
assert workflows == {workflow, plugin_root / "workflows/assemble-meta-loop.js"}
assert all(path.is_file() for path in workflows)
assert workflow.parent in skills

role_dir = plugin_root / "skills/qa-review/agents"
roles = {plugin_root / path for path in claude["agents"]}
assert role_dir.parent in skills
assert roles == set(role_dir.glob("*.md"))
assert {role.stem for role in roles} == {
    "architect-reviewer", "docs-editor", "docs-reviewer", "lab-runner",
    "performance-engineer", "sre-engineer", "test-coverage-reviewer",
}
for role in ("docs-editor", "docs-reviewer"):
    for ref in ("google-style/contract.md", "google-style/word-list.md", "changelog-style.md"):
        path = role_dir.parent / "references" / ref
        assert path.is_file()
        assert str(path.relative_to(plugin_root)) in (role_dir / f"{role}.md").read_text()

assert codex["version"] == claude["version"] == read(repo / "package.json")["version"]
assert "allow_implicit_invocation: false" in (role_dir / "openai.yaml").read_text()

# Codex hooks mirror the Claude hooks with Codex's root variable, flag and edit tool.
hooks = read(plugin_root / codex["hooks"])["hooks"]
expected = read(plugin_root / "hooks/hooks.json")["hooks"]
for groups in expected.values():
    for group in groups:
        if group.get("matcher") == "Write|Edit":
            group["matcher"] = "^apply_patch$"
        for hook in group["hooks"]:
            hook["command"] = hook["command"].replace("CLAUDE_PLUGIN_ROOT", "PLUGIN_ROOT") + " --codex"
assert hooks == expected, "hooks/codex-hooks.json drifted from hooks/hooks.json"
assert (plugin_root / "hooks/jit-context.py").is_file()
print("PASS Codex plugin assets")
