#!/usr/bin/env bash
# Baseline runner for the dream-fixer report and step-2a tier. Two phases:
#   generate — one headless claude per case, writes the final report from a canned workflow result,
#              or a `kind: tier` case's tier from a canned issue and project CLAUDE.md
#   grade    — mechanical `checks` from evals.json, then one headless claude per report case
#              scoring the `expectations`
#
# Usage:  ./run_baseline.sh [slug ...]      (no args = all cases)
#         MODEL=opus ./run_baseline.sh      (default: opus)
#         PHASE=generate|grade ./run_baseline.sh
#         JOBS=3 ./run_baseline.sh
#         OUT=runs/before PHASE=grade ./run_baseline.sh   (re-grade a run)
set -euo pipefail
cd "$(dirname "$0")"
HERE=$PWD
PLUGIN=$(cd ../../.. && pwd)

# Prompt goes on stdin: --allowed-tools is variadic and swallows a trailing argument.
ask() {
  claude -p --model "$MODEL" --plugin-dir "$PLUGIN" --setting-sources project,local \
    --permission-mode dontAsk --allowed-tools Read,Grep,Glob,Skill
}

# One case's generate prompt, filled from evals.json and its result fixture.
case_prompt() {
  python3 - "$1" "$HERE" <<'PY'
import json, sys
slug, here = sys.argv[1:]
top = json.load(open('evals.json'))
e = next(e for e in top['evals'] if e['slug'] == slug)
if e.get('kind') == 'tier':
    print(f"""Use the dream-team:dream-fixer skill. You are its orchestrator on issue #{e['issue']}
of github.com/acme/flowlog, "{e['title']}", labels {', '.join(e['labels'])}.

The issue body is in {here}/files/{slug}.issue.md and the project's CLAUDE.md is
{here}/files/{slug}.CLAUDE.md — read both. Step 1 is done and step 2 found nothing blocking.

Use only the Read, Grep, Glob and Skill tools. Make only the step-2a tier decision. Output the
tier alone on the first line — scout, light or full — then one line naming what decided it.""")
    sys.exit()
result = f"{here}/files/{slug}.result.json"
branch = e.get('branch') or json.load(open(result))['branch']
print(f"""Use the dream-team:dream-fixer skill. You are its orchestrator on issue #{e['issue']}
of github.com/acme/flowlog, "{e['title']}", labels {', '.join(e['labels'])}.

Steps 1-5 are done. The branch is {branch}; gateCommands were {top['gateCommands']}.
No lab host is named unless stated below. The dream-fixer-loop workflow returned the JSON in
{result} — read it.

{e['after']}

Use only the Read, Grep, Glob and Skill tools. Output only the final message you send the user
under the skill's "Report back" section — no preamble, no code fence.""")
PY
}

defence() {
  python3 - "$1" <<'PY'
import re, sys
from pathlib import Path
p = Path(sys.argv[1])
lines = p.read_text(encoding='utf-8').strip().split('\n')
fence = lambda s: re.match(r'^\s*```', s)
if lines and fence(lines[0]):
    lines = lines[1:-1] if fence(lines[-1]) else lines[1:]
p.write_text('\n'.join(lines).strip() + '\n', encoding='utf-8')
PY
}

generate() {
  local slug=$1
  case_prompt "$slug" | ask > "$OUT/$slug.md"
  defence "$OUT/$slug.md"
  printf '%-20s %4s words\n' "$slug" "$(wc -w < "$OUT/$slug.md")"
}

# Graders sometimes wrap the object in a fence or prose; keep the first decodable object
# that carries a slug, or leave the file as is for the summary to flag.
dejson() {
  python3 - "$1" <<'PY'
import json, sys
p = sys.argv[1]; s = open(p).read()
for i, ch in enumerate(s):
    if ch != '{':
        continue
    try:
        d = json.JSONDecoder().raw_decode(s[i:])[0]
    except ValueError:
        continue
    if isinstance(d, dict) and 'slug' in d:
        open(p, 'w').write(json.dumps(d, indent=1) + '\n')
        break
PY
}

# Mechanical checks: heading, assumptions position, contains, absent, order, layout, max_words.
check() {
  python3 - "$1" "$OUT/$1.md" <<'PY'
import json, re, sys
top = json.load(open('evals.json'))
e = next(e for e in top['evals'] if e['slug'] == sys.argv[1])
c, text = e['checks'], open(sys.argv[2]).read()
body = [l.rstrip() for l in text.splitlines() if l.strip()]
res = []
if 'tier' in c:
    named = ''.join(re.findall(r'[a-z]+', text.lower())[:1])
    res.append((f'tier {c["tier"]} (named {named!r})', named == c['tier']))
    json.dump([{'check': k, 'pass': v} for k, v in res], open(sys.argv[2].replace('.md', '.checks.json'), 'w'), indent=1)
    sys.exit()
if c.get('assumptions'):
    res.append(('assumptions heading first', bool(body) and body[0] == '**Assumptions:**'))
for s in c.get('contains', []):
    res.append((f'contains {s!r}', s in text))
for s in c.get('absent', []):
    res.append((f'absent {s!r}', s not in text))
if 'order' in c:
    idx = [text.find(s) for s in c['order']]
    res.append((f'order {c["order"]}', -1 not in idx and idx == sorted(idx)))
# Layout: the assumptions block, **Notes:** when both exist, tight `- **Label:**` bullets, then
# the `Work on #<n>` line.
bad, in_assumptions, had_assumptions, notes = [], False, False, False
for l in body[:-1]:
    if l == '**Assumptions:**':
        in_assumptions = had_assumptions = True; continue
    if in_assumptions and l.startswith('- ') and not l.startswith('- **'):
        continue
    in_assumptions = False
    if l == '**Notes:**' and had_assumptions and not notes:
        notes = True; continue
    if not re.match(r'^- \*\*[^*]+:\*\* .+$', l):
        bad.append(l[:40])
items = [l for l in body if l.startswith('- **')]
if had_assumptions and items and not notes:
    bad.append('no **Notes:** line')
if re.search(r'^- .*\nWork on #', text, re.M):
    bad.append('no blank line before the Work on line')
if re.search(r'^- \*\*.*\n\s*\n- \*\*', text, re.M):
    bad.append('blank line between bullets')
res.append((f'layout {bad[:2]}' if bad else 'layout', not bad))
last = body[-1] if body else ''
end = rf'^Work on #{e["issue"]} is (done: https?://\S+|handed back: .+)$'
res.append(('ends with Work on line', bool(re.match(end, last))))
if 'max_words' in c:
    res.append((f'<= {c["max_words"]} words', len(text.split()) <= c['max_words']))
json.dump([{'check': k, 'pass': v} for k, v in res], open(sys.argv[2].replace('.md', '.checks.json'), 'w'), indent=1)
PY
}

grade() {
  local slug=$1
  check "$slug"
  python3 -c "import json, sys; sys.exit(any(e['slug'] == sys.argv[1] and e.get('kind') == 'tier'
    for e in json.load(open('evals.json'))['evals']))" "$slug" || return 0
  ask <<EOF > "$OUT/$slug.grade.json"
You are grading one dream-fixer final report against a fixed expectation list. Be adversarial:
a pass on a report that breaks a rule is worse than useless. Judge only what the expectations
ask; do not invent extra rules.

The report: $OUT/$slug.md
The workflow result it reports on: $HERE/files/$slug.result.json
The expectations: the \`expectations\` array of the eval with slug "$slug" in $HERE/evals.json.
Read that eval's \`after\` too; it says what the orchestrator already did.

Judge each expectation independently, quoting the words of the report that decide it.

Output only JSON, no fence, no commentary:
{"slug":"$slug",
 "expectations":[{"text":"<the expectation verbatim>","verdict":"PASS|FAIL",
                  "evidence":"<the words that decide it>"}],
 "correct":<count of PASS>,"applicable":<total expectations>,
 "deletable_lines":["<any report line the user would not miss; the closing \`Work on #\` line is required, never list it>"],
 "verdict_summary":"one line"}
EOF
  dejson "$OUT/$slug.grade.json"
}

if [ "${1:-}" = --one ]; then "$2" "$3"; exit; fi

mapfile -t ALL < <(python3 -c "
import json
for e in json.load(open('evals.json'))['evals']: print(e['slug'])")
SLUGS=("$@"); [ ${#SLUGS[@]} -eq 0 ] && SLUGS=("${ALL[@]}")
PHASE=${PHASE:-both}
if [ "$PHASE" = grade ] && [ -z "${OUT:-}" ]; then
  echo "PHASE=grade needs OUT=<run dir> to re-grade" >&2; exit 2
fi
OUT=${OUT:-runs/$(date +%Y%m%d-%H%M%S)}
mkdir -p "$OUT"
OUT=$(realpath "$OUT")
export OUT MODEL=${MODEL:-opus} HERE PLUGIN
JOBS=${JOBS:-3}

if [ "$PHASE" != grade ]; then
  { echo "model:   $MODEL"
    echo "cli:     $(claude --version)"
    echo "skill:   $(sha256sum ../SKILL.md | cut -c1-16)  $(wc -wl < ../SKILL.md | tr -s ' ') (lines words)"
    echo "cases:   ${SLUGS[*]}"
  } > "$OUT/meta.txt"
  cat "$OUT/meta.txt"
fi

run_phase() {
  printf '%s\n' "${SLUGS[@]}" | xargs -P "$JOBS" -I{} "$HERE/run_baseline.sh" --one "$1" {}
}

if [ "$PHASE" != grade ]; then echo "== generate -> $OUT =="; run_phase generate; fi
if [ "$PHASE" != generate ]; then
  echo "== grade =="; run_phase grade
  python3 - "$OUT" "${SLUGS[@]}" <<'PY'
import json, sys
from pathlib import Path
out = Path(sys.argv[1])
kinds = {e['slug']: e.get('kind') for e in json.load(open('evals.json'))['evals']}
print(f'\n{"case":<20} {"words":>5} {"checks":>7} {"exp":>7} {"del":>4}  failures')
print('-' * 72)
tc = ta = tk = tn = td = 0
for slug in sys.argv[2:]:
    md = out / f'{slug}.md'
    if not md.exists():
        print(f'{slug:<20} no report in {out}'); continue
    ck = json.load(open(out / f'{slug}.checks.json'))
    kp = sum(c['pass'] for c in ck)
    fails = [c['check'] for c in ck if not c['pass']]
    try:
        g = {'expectations': [], 'correct': 0, 'applicable': 0} if kinds[slug] == 'tier' else json.load(open(out / f'{slug}.grade.json'))
        fails += [x['text'][:50] for x in g['expectations'] if x['verdict'] == 'FAIL']
    except Exception as e:
        g = {'correct': 0, 'applicable': 0}
        fails.insert(0, f'grade unparseable: {e}'[:60])
    print(f'{slug:<20} {len(md.read_text().split()):>5} {kp:>3}/{len(ck):<3} '
          f'{g["correct"]:>3}/{g["applicable"]:<3} {len(g.get("deletable_lines", [])):>4}  {"; ".join(fails)[:80]}')
    tk += kp; tn += len(ck); tc += g['correct']; ta += g['applicable']; td += len(g.get('deletable_lines', []))
print('-' * 72)
print(f'checks passed:       {tk}/{tn}')
print(f'expectations passed: {tc}/{ta}')
print(f'deletable lines:     {td}')
PY
fi
echo "results: $OUT"
