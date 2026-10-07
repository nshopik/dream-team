import json, os, subprocess, sys

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "changelog-cap.py")


def verdict(tool_input):
    p = subprocess.run([sys.executable, HOOK], text=True, capture_output=True,
                       input=json.dumps({"tool_input": tool_input}))
    out = p.stdout.strip()
    if not out:
        return "ALLOW"
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"].upper()


def edit(path, new):
    return {"file_path": path, "old_string": "", "new_string": new}


def write(path, content):
    return {"file_path": path, "content": content}


CL = "/repo/CHANGELOG.md"

# clean, terse, one plain sentence — the shape to preserve.
assert verdict(edit(CL, "- `flush_seconds` default raised from 30 to 300.")) == "ALLOW"
assert verdict(edit(CL, "- Bumped `clickhouse-go/v2` to v2.48.0 for the eviction fix.")) == "ALLOW"

# bold lead is the mixed-style rot the rule now bans; only **Breaking:** / **Upgrade note:** may bold.
assert verdict(edit(CL, "- **Default `live_batch_rows` lowered to 500,000** — halves heap.")) == "DENY"
assert verdict(edit(CL, "- **Breaking:** removed the `network` output type.")) == "ALLOW"
assert verdict(edit(CL, "- **Upgrade note:** a Unix-socket drop-in must add `AF_UNIX`.")) == "ALLOW"
assert verdict(edit(CL, "- **Upgrade note:** drop-ins need **AF_UNIX** now.")) == "DENY"

# two sentences — rationale leaking from the MR body. The sharp rot signal.
two = ("- **Replay no longer redials ClickHouse** — the idle cap sat below the open "
       "cap. This bit the HTTP output.")
assert verdict(edit(CL, two)) == "DENY"

# one sentence but a runaway word count (real 94-word history entry, trimmed of a period).
runaway = ("- **Replay (`-r`/`-R`) no longer redials ClickHouse between batches** — the "
           "connection pool's idle cap sat below its open cap so batches past that cap "
           "released their connection to be closed and the next one paid a fresh TCP "
           "handshake and slow-start and this bit the HTTP output seven redials per run "
           "in the lab and zero after while the native driver sets a higher idle cap")
assert verdict(edit(CL, runaway)) == "DENY"

# em-dash/comma clauses and code spans must not read as extra sentences.
assert verdict(edit(CL, "- `-a` is now a deprecated no-op; `-r`/`-R` sniff the zstd magic byte.")) == "ALLOW"

# not a changelog file — never fires.
assert verdict(edit("/repo/README.md", two)) == "ALLOW"

# Write measures only [Unreleased]; frozen release sections with rot are ignored.
frozen_rot = ("## [Unreleased]\n\n### Fixed\n- Clean short line.\n\n"
              "## [2.1.1] - 2026-08-17\n\n### Fixed\n- " + two[2:] + "\n")
assert verdict(write(CL, frozen_rot)) == "ALLOW"

# Write with rot in [Unreleased] is caught.
unrel_rot = "## [Unreleased]\n\n### Fixed\n- " + two[2:] + "\n\n## [2.0.0] - 2026-06-23\n"
assert verdict(write(CL, unrel_rot)) == "DENY"

print("all changelog-cap assertions passed")
