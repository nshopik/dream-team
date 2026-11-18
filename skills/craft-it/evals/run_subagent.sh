#!/usr/bin/env bash
# One headless craft-it step 4 with the Workflow tool disallowed, on a fixture repo whose issue
# (files/subagent.issue.md) adds an `h` unit and never names the 24-hour cap docs/format.md
# sets, then mechanical checks on the transcript and the result: a green main-session gate after
# every writing agent, one parallel review dispatch, a fix round that ran and ended, and the
# documented result fields.
#
# Usage:  ./run_subagent.sh            (MODEL=opus, OUT=runs/subagent-<timestamp>)
#         OUT=runs/subagent-x PHASE=check ./run_subagent.sh   (re-check a run)
set -euo pipefail
cd "$(dirname "$0")"
HERE=$PWD
PLUGIN=$(cd ../../.. && pwd)
MODEL=${MODEL:-opus}
GATE='python3 test_duration.py'
OUT=${OUT:-runs/subagent-$(date +%Y%m%d-%H%M%S)}
mkdir -p "$OUT"
OUT=$(realpath "$OUT")
REPO=$OUT/repo

if [ "${PHASE:-both}" != check ]; then
  [ -e "$REPO" ] && { echo "$REPO exists; pick a new OUT or PHASE=check" >&2; exit 1; }
  cp -r files/subagent-repo "$REPO"
  git -C "$REPO" init -q -b main
  git -C "$REPO" config user.name eval
  git -C "$REPO" config user.email eval@example.com
  git -C "$REPO" config dream-team.own true
  git -C "$REPO" add -A
  git -C "$REPO" commit -qm 'duration: parse s and m units'
  git -C "$REPO" checkout -qb issue-3-hours
  BASE=$(git -C "$REPO" rev-parse HEAD)
  echo "model: $MODEL  cli: $(claude --version)  repo: $REPO" | tee "$OUT/meta.txt"
  # Prompt goes on stdin: --allowed-tools and --disallowed-tools are variadic.
  (cd "$REPO" && timeout 3h claude -p --model "$MODEL" --plugin-dir "$PLUGIN" \
    --setting-sources project,local --permission-mode dontAsk \
    --allowed-tools Bash,Read,Edit,Write,Glob,Grep,Agent,Skill --disallowed-tools Workflow \
    --add-dir "$OUT" "$PLUGIN" --output-format stream-json --verbose \
    > "$OUT/transcript.jsonl") <<EOF || echo "claude exited $?"
Use the dream-team:craft-it skill. You are its orchestrator on issue #3 of
github.com/acme/tinytime, "duration: add an h unit", labels enhancement.

Steps 1-3 are done. The issue body is in $HERE/files/subagent.issue.md. Triage found nothing
blocking and the tier is full. The worktree is $REPO, on branch issue-3-hours, base $BASE.
gateCommands: ["$GATE"]. No external reviewer and no lab host.

Run step 4. Once it has its result object, also write it to $OUT/result.json, then stop: do not
run step 5 on, push, open a PR or touch the tracker.
EOF
fi

python3 - "$OUT" "$GATE" <<'PY'
import json, re, sys
out, gate = sys.argv[1:]
calls, results = [], {}
for line in open(f'{out}/transcript.jsonl'):
    try:
        e = json.loads(line)
    except ValueError:  # a killed run leaves a truncated last line
        continue
    content = (e.get('message') or {}).get('content')
    if e.get('parent_tool_use_id') or not isinstance(content, list):
        continue
    if e.get('type') == 'assistant':
        calls += [dict(b, msg=e['message'].get('id')) for b in content if b.get('type') == 'tool_use']
    elif e.get('type') == 'user':
        results.update({b['tool_use_id']: b for b in content if b.get('type') == 'tool_result'})
agents = [i for i, c in enumerate(calls) if c['name'] in ('Agent', 'Task')]
label = lambda i: calls[i]['input'].get('description', '')
red = lambda i: results.get(calls[i]['id'], {}).get('is_error', False)


def verdict(i):
    r = results.get(calls[i]['id'], {}).get('content', '')
    text = r if isinstance(r, str) else ' '.join(x.get('text', '') for x in r if isinstance(x, dict))
    try:
        return json.loads(re.findall(r'```json\s*(\{.*?\})\s*```', text, re.S)[-1])
    except (IndexError, ValueError):
        return {}


writers = [i for i in agents if re.match(r'(impl|build-fix|fix):', label(i))]
res = [('Workflow tool never called', not any(c['name'] == 'Workflow' for c in calls)),
       (f'writing agents dispatched ({len(writers)})', bool(writers))]
for i in writers:
    nxt = next((j for j in agents if j > i), len(calls))
    if nxt < len(calls) and label(nxt) == label(i):
        continue  # redispatched under the malformed-block rule
    runs = [k for k in range(i + 1, nxt)
            if calls[k]['name'] == 'Bash' and gate in calls[k]['input'].get('command', '')]
    to_fixer = nxt < len(calls) and label(nxt).startswith('build-fix:')
    res.append((f'main-session green gate after {label(i)}',
                bool(runs) and (to_fixer or not red(runs[-1]))))
full = lambda i: re.fullmatch(r'review:.+', label(i)) and not re.search(r':retry\d+$', label(i))
reviews = list({label(i): i for i in reversed([i for i in agents if full(i)])}.values())
res.append((f'reviewers dispatched in one message ({len(reviews)})',
            len(reviews) > 1 and len({calls[i]['msg'] for i in reviews}) == 1))
seeded = any(f.get('severity') in ('critical', 'important') and not f.get('preExisting')
             for i in reviews for f in verdict(i).get('findings', []))
res.append(('seed: first review raised a blocking finding (the fixture, not the skill)', seeded or None))
try:
    r = json.load(open(f'{out}/result.json'))
except (OSError, ValueError) as e:
    r = {}
    res.append((f'result.json readable ({e})', False))
fixes = [i for i in writers if re.fullmatch(r'fix:#\d+:r\d+', label(i))]
n = fixes and label(fixes[-1]).rsplit(':r', 1)[1]
res.append((f'fix rounds dispatched ({len(fixes)})', bool(fixes) if seeded else None))
res.append(('fix-diff-only re-review after the last fix round', bool(fixes)
            and any(j > fixes[-1] and re.fullmatch(rf're-review:.+:r{n}', label(j)) for j in agents)
            and not any(j > fixes[0] and full(j) for j in agents) if seeded else None))
res.append(('fix loop ended', (r.get('ok') is True and r.get('fixRounds', 0) >= 1)
            or r.get('handBack') is True if seeded and r else None))
if r:
    common = ['redEvidence', 'disputes', 'resolved', 'questions', 'preExisting']
    keys = ['ok', 'degraded', 'untrackedPaths'] + (
        common + ['issue', 'branch', 'reviewers', 'fixRounds', 'assumptions', 'changedFiles',
                  'nitFindings', 'nitFix', 'summaries', 'doneWhen'] if r.get('ok')
        else ['stage', 'reason'] + (common + ['handBack', 'blocking', 'deadReviewers', 'verdicts']
                                    if r.get('handBack') else []))
    missing = [k for k in keys if k not in r]
    res.append((f'result fields{" missing " + str(missing) if missing else ""}', not missing))
json.dump([{'check': k, 'pass': v} for k, v in res], open(f'{out}/checks.json', 'w'), indent=1)
for k, v in res:
    print(f'{"SKIP" if v is None else "PASS" if v else "FAIL"}  {k}')
print(f'checks passed: {sum(v is True for _, v in res)}/{sum(v is not None for _, v in res)}'
      f'{"" if seeded else " (incomplete: fix loop not exercised)"}  results: {out}')
PY
