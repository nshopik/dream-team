#!/usr/bin/env python3
"""Scans unscanned dream-fixer-loop workflow runs for agent friction, caches every hit, and
prints the patterns seen in two or more runs.
"""
import json
import re
import statistics
import time
from collections import defaultdict
from pathlib import Path

HOME = Path.home()
CACHE = HOME / ".claude" / "dream-team" / "friction.jsonl"
RUNS = "projects/*/*/subagents/workflows/wf_*"
CLAUDE_DIR = (str(HOME / ".claude"), "~/.claude", "$HOME/.claude")
READ_ONLY = re.compile(r"^(review:|re-review:|gate$|simplify$)")
WRITES = ("Edit", "Write", "NotebookEdit", "MultiEdit")
FORBIDDEN = re.compile(
    r"(^|[;&|(\n])\s*ssh\s|\bgit\s+push\b"
    r"|\b(gh|glab)\s+(pr|mr|issue|release)\s+(create|edit|comment|close|merge|reopen|note|update|delete)\b"
    r"|\bgh\s+api\b(?!.*-X\s*GET).*(-X\s*(POST|PATCH|PUT|DELETE)|\s-[fF]\s)"
)
OUTLIER_FACTOR = 2  # twice the role's median
OUTLIER_MIN_RUNS = 3  # prior runs of a role before its median means anything
ACTIVE_SECONDS = 600  # a run with a file this fresh may still be going; journals have no end event


def role_of(label):
    return re.sub(r":(r|retry)\d+$", "", re.sub(r":#.*$", "", label))


def read_jsonl(path):
    with open(path) as f:
        lines = [line for line in f if line.strip()]
    try:
        tail = [json.loads(lines[-1])] if lines else []
    except json.JSONDecodeError:  # a half-written last line
        tail = []
    return [json.loads(line) for line in lines[:-1]] + tail


def scan_agent(path, role):
    """Returns (hits, tokens, tool calls) for one agent transcript."""
    hits, uses, usage, failed = [], {}, {}, defaultdict(int)
    for e in read_jsonl(path):
        msg = e.get("message") or {}
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        if e.get("type") == "assistant":
            usage[msg.get("id")] = msg.get("usage") or {}
        for b in content:
            if b.get("type") == "tool_use":
                uses[b["id"]] = b
                name, inp = b["name"], b.get("input") or {}
                cmd = inp.get("command", "") if name == "Bash" else ""
                target = " ".join(str(inp.get(k, "")) for k in ("file_path", "path", "pattern"))
                if name in ("Read", "Glob", "Grep") and any(d in target for d in CLAUDE_DIR):
                    hits.append(("claude-dir", f"{name} {target.strip()}"))
                if re.search(r"\b(find|ls|cat)\b", cmd) and any(d in cmd for d in CLAUDE_DIR):
                    hits.append(("claude-dir", cmd))
                if FORBIDDEN.search(cmd):
                    hits.append(("forbidden", cmd))
                if READ_ONLY.match(role) and (name in WRITES or re.search(r"\bgit\s+commit\b", cmd)):
                    hits.append(("forbidden", f"{name} {inp.get('file_path') or cmd}"))
            elif b.get("type") == "tool_result" and b.get("is_error"):
                use = uses.get(b.get("tool_use_id"), {})
                body = b.get("content")
                if isinstance(body, list):
                    body = " ".join(c.get("text", "") for c in body if isinstance(c, dict))
                if use.get("name") == "Bash":
                    cmd = use["input"].get("command", "")
                    failed[cmd] += 1
                    if failed[cmd] == 2:
                        hits.append(("repeat-failure", cmd))
                # A plain non-zero exit is ordinary work; only a repeat of it is friction.
                if not str(body).startswith("Exit code"):
                    hits.append(("tool-error", f"{use.get('name', '?')}: {body}"))
    tokens = sum(
        u.get(k, 0) or 0
        for u in usage.values()
        for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
    )
    return hits, tokens, len(uses)


def scan_run(run_dir, date, stats):
    """Returns the cache records for one run; stats holds prior per-role values and grows."""
    journal = read_jsonl(run_dir / "journal.jsonl")
    labels = {e["agentId"]: e["label"] for e in journal if e["type"] == "started"}
    run = run_dir.name
    records = [{"type": "run", "run": run, "date": date}]
    if not any(re.match(r"(impl|gate):#", label) for label in labels.values()):
        return records
    friction = {e["agentId"]: (e.get("result") or {}).get("friction") or [] for e in journal if e["type"] == "result"}
    new_stats = []
    for agent_id, label in labels.items():
        path = run_dir / f"agent-{agent_id}.jsonl"
        if not path.exists():
            continue
        role = role_of(label)
        meta = run_dir / f"agent-{agent_id}.meta.json"
        agent_type = json.loads(meta.read_text()).get("agentType", "") if meta.exists() else ""
        hits, tokens, tools = scan_agent(path, role)
        hits += [("self-report", f) for f in friction.get(agent_id, [])]
        prior = stats[role]
        if len({p[0] for p in prior}) >= OUTLIER_MIN_RUNS:
            for kind, value, i in (("tokens", tokens, 1), ("tools", tools, 2)):
                median = statistics.median(p[i] for p in prior)
                if value > OUTLIER_FACTOR * median:
                    hits.append((f"{kind}-outlier", f"{value} {kind} vs role median {median:g}"))
        new_stats.append((role, (run, tokens, tools)))
        records.append({"type": "stats", "run": run, "date": date, "role": role, "agentType": agent_type,
                        "tokens": tokens, "tools": tools})
        records += [{"type": "hit", "run": run, "date": date, "pattern": p, "role": role,
                     "agentType": agent_type, "evidence": " ".join(str(ev).split())[:160]} for p, ev in hits]
    for role, row in new_stats:
        stats[role].append(row)
    return records


def main():
    cache = read_jsonl(CACHE) if CACHE.exists() else []
    seen = {r["run"] for r in cache if r["type"] == "run"}
    stats = defaultdict(list)
    for r in cache:
        if r["type"] == "stats":
            stats[r["role"]].append((r["run"], r["tokens"], r["tools"]))
    unseen = [p for p in (HOME / ".claude").glob(RUNS) if p.name not in seen and (p / "journal.jsonl").exists()]
    active = [p for p in unseen if max(f.stat().st_mtime for f in [p, *p.iterdir()]) > time.time() - ACTIVE_SECONDS]
    runs = sorted((p.stat().st_mtime, p) for p in unseen if p not in active)
    new = []
    for mtime, run_dir in runs:
        new += scan_run(run_dir, time.strftime("%Y-%m-%d", time.localtime(mtime)), stats)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE, "a") as f:
        f.writelines(json.dumps(r) + "\n" for r in new)

    groups = defaultdict(list)
    for r in cache + new:
        if r["type"] == "hit":
            groups[(r["pattern"], r["role"])].append(r)
    print(f"scanned {len(runs)} new runs; skipped {len(active)} in progress; cache {CACHE}")
    for (pattern, role), hits in sorted(groups.items(), key=lambda g: -len({h["run"] for h in g[1]})):
        run_ids = {h["run"] for h in hits}
        if len(run_ids) < 2:
            continue
        types = ", ".join(sorted({h["agentType"] for h in hits if h["agentType"]}))
        print(f"\n{pattern} | {role} | {len(run_ids)} runs | {types}")
        for ev in list(dict.fromkeys(h["evidence"] for h in reversed(hits)))[:3]:
            print(f"  - {ev}")


if __name__ == "__main__":
    main()
