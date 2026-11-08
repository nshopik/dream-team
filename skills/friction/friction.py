#!/usr/bin/env python3
"""Scans unscanned dream-fixer-loop workflow runs for agent friction, caches every hit, and
prints the patterns seen in two or more runs, or with --time each role's wall clock in minutes.
"""
import json
import re
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

HOME = Path.home()
CACHE = HOME / ".claude" / "dream-team" / "friction.jsonl"
RUNS = "projects/*/*/subagents/workflows/wf_*"
CLAUDE_DIR = (str(HOME / ".claude"), "~/.claude", "$HOME/.claude")
READ_ONLY = re.compile(r"^(review:|re-review:|fixdiff:|gate$|simplify$)")
WRITES = ("Edit", "Write", "NotebookEdit", "MultiEdit")
# ponytail: TREE_EDIT and FORBIDDEN match with quoted strings and heredoc bodies blanked, so `> "$f"`, `bash -c "git push"` and a stray apostrophe's span are missed; parse with bashlex if that matters.
TREE_EDIT = re.compile(
    r"\bgit(\s+-[Cc]\s+\S+)*\s+(commit|checkout|restore|stash(?!\s+(list|show)\b))\b|\b(sed|perl)\b[^|;&\n]*\s-(\w*i\b|-in-place)"
    r"|(\btee\s+(-\w+\s+)*|>>?\s*)(?!&|/dev/|/tmp/)[\w~$./-]"
)
QUOTED = re.compile(r"'[^']*'|\"(\\.|[^\"\\])*\"")
HEREDOC = re.compile(r"""<<-?\s*['"]?(\w+)['"]?(.*?\n).*?^\s*\1$""", re.S | re.M)
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
    records = []
    with open(path, "rb") as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except ValueError:  # blank, half-written, or torn mid-character
                pass
    return records


def minutes(start, end):
    return round((end - start).total_seconds() / 60, 1)


def scan_agent(path, role):
    """Returns (hits, tokens, tool calls, (first, last) timestamp or None) for one agent transcript."""
    hits, uses, usage, failed, stamps = [], {}, {}, defaultdict(int), []
    for e in read_jsonl(path):
        if "timestamp" in e:
            stamps.append(datetime.fromisoformat(e["timestamp"]))
        msg = e.get("message") or {}
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        if e.get("type") == "assistant":
            usage[msg.get("id")] = msg.get("usage") or {}
        for b in content:
            if b.get("type") == "tool_use" and "id" in b and "name" in b:
                uses[b["id"]] = b
                name, inp = b["name"], b.get("input") or {}
                cmd = inp.get("command", "") if name == "Bash" else ""
                target = " ".join(str(inp.get(k, "")) for k in ("file_path", "path", "pattern"))
                if name in ("Read", "Glob", "Grep") and any(d in target for d in CLAUDE_DIR):
                    hits.append(("claude-dir", f"{name} {target.strip()}"))
                if re.search(r"\b(find|ls|cat)\b", cmd) and any(d in cmd for d in CLAUDE_DIR):
                    hits.append(("claude-dir", cmd))
                bare = QUOTED.sub("''", HEREDOC.sub(r"\2", cmd))
                if FORBIDDEN.search(bare):
                    hits.append(("forbidden", cmd))
                if READ_ONLY.match(role) and (name in WRITES or TREE_EDIT.search(bare)):
                    hits.append(("forbidden", f"{name} {inp.get('file_path') or cmd}"))
            elif b.get("type") == "tool_result" and b.get("is_error"):
                use = uses.get(b.get("tool_use_id"), {})
                body = b.get("content")
                if isinstance(body, list):
                    body = " ".join(c.get("text", "") for c in body if isinstance(c, dict))
                if use.get("name") == "Bash":
                    cmd = (use.get("input") or {}).get("command", "")
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
    return hits, tokens, len(uses), (min(stamps), max(stamps)) if stamps else None


def scan_run(run_dir, date, stats):
    """Returns the cache records for one run; stats holds prior per-role values and grows."""
    journal = read_jsonl(run_dir / "journal.jsonl")
    labels = {e["agentId"]: e["label"] for e in journal if e.get("type") == "started" and "agentId" in e and "label" in e}
    run = run_dir.name
    records, marker = [], {"type": "run", "run": run, "date": date}  # written last: a run counts once all of it is cached
    if not any(re.match(r"(impl|gate):#", label) for label in labels.values()):
        return [marker]
    friction = {e["agentId"]: e["result"].get("friction") or [] for e in journal
                if e.get("type") == "result" and "agentId" in e and isinstance(e.get("result"), dict)}
    new_stats, spans = [], []
    for agent_id, label in labels.items():
        path = run_dir / f"agent-{agent_id}.jsonl"
        if not path.exists():
            continue
        role = role_of(label)
        meta = run_dir / f"agent-{agent_id}.meta.json"
        agent_type = json.loads(meta.read_text()).get("agentType", "") if meta.exists() else ""
        hits, tokens, tools, span = scan_agent(path, role)
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
        if span:
            records[-1]["minutes"] = minutes(*span)
            spans.append(span)
        records += [{"type": "hit", "run": run, "date": date, "pattern": p, "role": role,
                     "agentType": agent_type, "evidence": " ".join(str(ev).split())[:160]} for p, ev in hits]
    for role, row in new_stats:
        stats[role].append(row)
    if spans:
        marker["minutes"] = minutes(min(s[0] for s in spans), max(s[1] for s in spans))
    return records + [marker]


def print_times(records):
    """Prints a markdown table of minutes per role and per whole run, slowest median first."""
    groups = defaultdict(list)
    for r in records:
        if "minutes" in r and r["type"] in ("stats", "run"):
            groups[r.get("role", "whole run")].append(r)
    rows = []
    for role, rs in groups.items():
        m = sorted(r["minutes"] for r in rs)
        q = statistics.quantiles(m * 2 if len(m) == 1 else m, n=20, method="inclusive")  # 5% steps; one value raises before 3.13
        rows.append((role, len({r["run"] for r in rs}), len(rs), [m[0], q[1], q[4], q[9], q[14], q[17], m[-1]]))
    print("\n| role | runs | agents | min | P10 | Q1 | median | Q3 | P90 | max |")
    print("|---" * 10 + "|")
    for role, runs, agents, values in sorted(rows, key=lambda row: -row[3][3]):
        print(f"| {role} | {runs} | {agents} | " + " | ".join(f"{v:.1f}" for v in values) + " |")


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
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    if CACHE.exists() and not CACHE.read_bytes().endswith(b"\n"):  # a killed append's tail
        with open(CACHE, "a") as f:
            f.write("\n")
    for mtime, run_dir in runs:
        records = scan_run(run_dir, time.strftime("%Y-%m-%d", time.localtime(mtime)), stats)
        with open(CACHE, "a") as f:
            f.writelines(json.dumps(r) + "\n" for r in records)
        new += records

    print(f"scanned {len(runs)} new runs; skipped {len(active)} in progress; cache {CACHE}")
    if "--time" in sys.argv[1:]:
        print_times(cache + new)
        return
    groups = defaultdict(list)
    for r in cache + new:
        if r["type"] == "hit":
            groups[(r["pattern"], r["role"])].append(r)
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
