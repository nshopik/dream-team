#!/usr/bin/env python3
"""Writes a run's report.md, and with `lenses` its lenses/<lens>.md, from reviewer output and
session transcripts, then prints its cost, report size and subagent count, plus `early-exit` when
the run errored, its report is empty, or its main turn ended before a subagent did.

Usage: python3 extract.py <run-dir> [lenses] [claude|codex]
"""
import json
import os
import sys
from pathlib import Path

d = Path(sys.argv[1])
lenses = "lenses" in sys.argv[2:]
result_path = d / "result.json"


def codex_lenses(thread):
    sessions = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "sessions"
    transcript = next(sessions.rglob(f"rollout-*-{thread}.jsonl"), None)
    if transcript is None:
        raise ValueError(f"missing Codex rollout for thread {thread}")

    roles = {"dream-team-architect-reviewer", "dream-team-sre-engineer",
             "dream-team-test-coverage-reviewer", "dream-team-performance-engineer",
             "dream-team-docs-reviewer"}
    calls, pending, reports = {}, {}, {}
    with transcript.open() as stream:
        for line in stream:
            entry = json.loads(line)
            message = entry["payload"]
            if entry["type"] == "event_msg" and message["type"] == "task_complete":
                return reports, any(pending.values())
            if entry["type"] != "response_item":
                continue
            kind = message["type"]
            if kind == "function_call" and message.get("namespace") == "collaboration":
                if message["name"] in {"spawn_agent", "followup_task"}:
                    calls[message["call_id"]] = (message["name"], json.loads(message["arguments"]))
            elif kind == "function_call_output" and message["call_id"] in calls:
                tool, args = calls.pop(message["call_id"])
                output = message["output"]
                if tool == "spawn_agent":
                    name = args["task_name"]
                    if args.get("agent_type") in roles or name == "domain" or name.startswith("lens-"):
                        # Failed spawns respond with an error instead of a task name.
                        if output.startswith("{") and (task := json.loads(output).get("task_name")):
                            pending[task] = True
                elif not output:
                    target = args["target"]
                    task = target if target.startswith("/") else f"/root/{target}"
                    if task in pending:
                        pending[task] = True
            elif kind == "agent_message":
                task = message["author"]
                if not pending.get(task):
                    continue
                for content in message["content"]:
                    header, _, body = content.get("text", "").partition("\nPayload:\n")
                    if header.startswith("Message Type: FINAL_ANSWER\n"):
                        pending[task] = False
                        if body.strip() and not body.startswith("Agent errored:"):
                            reports[task] = body.strip()
                        break
    raise ValueError(f"incomplete Codex rollout for thread {thread}")


def extract_codex():
    thread, complete, texts = "", False, []
    with result_path.open() as stream:
        for line in stream:
            event = json.loads(line)
            if event["type"] == "thread.started":
                thread = event["thread_id"]
            elif event["type"] == "item.completed" and event["item"]["type"] == "agent_message":
                texts.append(event["item"]["text"].strip())
            elif event["type"] == "turn.completed":
                complete = True
                break
    if not thread:
        raise ValueError("missing thread.started event in Codex output")

    report = max(texts, key=len, default="")
    if texts and texts[-1] not in report:
        report += "\n\n---\n\n" + texts[-1]
    reports, late = codex_lenses(thread) if lenses and complete else ({}, False)
    (d / "report.md").write_text(report + "\n")
    for task, body in reports.items():
        name = task.rsplit("/", 1)[-1]
        (d / "lenses").mkdir(exist_ok=True)
        (d / "lenses" / f"{name}.md").write_text(body + "\n")

    early = not complete or not report or late or (lenses and not reports)
    print(f"cost=? report={len(report)} lenses={len(reports)}" + (" early-exit" if early else ""))


if "codex" in sys.argv[2:]:
    try:
        extract_codex()
    except (OSError, ValueError, KeyError) as error:
        sys.exit(f"Codex extraction failed: {error}")
    sys.exit()

if not result_path.stat().st_size:
    sys.exit(print("cost=? report=0 lenses=0 early-exit"))
run = json.loads(result_path.read_text())
projects = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")) / "projects"


def read(transcript, sidechain=False):
    """The longest assistant text or subagent hand-back in a transcript, and its last timestamp."""
    texts, last = [], ""
    for line in open(transcript):
        m = json.loads(line)
        if m.get("type") != "assistant" or m.get("isSidechain", False) != sidechain:
            continue
        last = max(last, m.get("timestamp", ""))
        for c in m["message"].get("content", []):
            if c.get("type") == "text":
                texts.append(c["text"])
            elif c.get("type") == "tool_use" and c["name"] == "SubagentHandback":
                texts.append(c["input"]["message"])
    return max(texts, key=len, default=""), last


# `result` is only the last message, which can be an ack after the report; an error result lacks it.
report, ended = max((read(t) for t in projects.glob(f"*/{run['session_id']}.jsonl")),
                    key=lambda r: len(r[0]), default=("", ""))
result = run.get("result", "")
if result.strip() not in report:
    report = (report + "\n\n---\n\n" if report.strip() else "") + result
(d / "report.md").write_text(report.strip() + "\n")

late = False
subagents = sorted(projects.glob(f"*/{run['session_id']}/subagents/*.meta.json"))
for meta in subagents:
    text, last = read(meta.with_name(meta.name[: -len(".meta.json")] + ".jsonl"), True)
    late |= bool(ended) and last > ended  # a forked skill has no main-thread turn
    if not lenses:
        continue
    name = json.loads(meta.read_text())["agentType"].split(":")[-1]
    if name == "Explore":  # a code search, not a review lens
        continue
    f, n = d / "lenses" / f"{name}.md", 2
    while f.exists():
        f, n = d / "lenses" / f"{name}-{n}.md", n + 1
    f.parent.mkdir(exist_ok=True)
    f.write_text(text + "\n")

early = run.get("is_error") or not report.strip() or late
print(f"cost=${run.get('total_cost_usd', 0):.2f} report={len(report.strip())} "
      f"lenses={len(subagents)}" + (" early-exit" if early else ""))
