#!/usr/bin/env bash
# Judge and report evals for tech-debt-triage (#431, #453). Per case: export its commit to a temp dir, no .git,
# run the SKILL.md judge brief headless on its candidates RUNS times, grade the verdicts with
# judge.py. Pass: a majority of runs put each `Act now` candidate at Act now, every other one at
# Later or Skip.
# REPORT=1: run the step-5 report instructions once, ignoring RUNS, on the case's canned
# verdicts instead, and grade the HTML with `judge.py report`. Pass: each candidate with a
# `report` key has a card that meets its step-5 rules, and the HTML has no unbalanced tags.
#
# Usage:  ./run.sh [slug ...]                  (no args = every cases/*.json)
#         MODEL=fable RUNS=3 OUT=runs/<name> ./run.sh
#         REPORT=1 ./run.sh
set -euo pipefail
cd "$(dirname "$0")"
REPO=$(git rev-parse --show-toplevel)
MODEL=${MODEL:-fable}
RUNS=${RUNS:-3}
OUT=${OUT:-runs/$(date +%Y%m%d-%H%M%S)}
mkdir -p "$OUT"; OUT=$(realpath "$OUT")

SLUGS=("$@")
[ ${#SLUGS[@]} -eq 0 ] && mapfile -t SLUGS < <(ls cases | sed 's/\.json$//')
fails=0
for slug in "${SLUGS[@]}"; do
  case=cases/$slug.json
  tmp=$(mktemp -d)
  trap 'rm -rf "${tmp:?}"' EXIT
  commit=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["commit"])' "$case")
  mkdir "$tmp/repo"
  git -C "$REPO" archive "$commit" | tar -x -C "$tmp/repo"
  if [ "${REPORT:-}" = 1 ]; then
    python3 judge.py report-prompt "$case" "$tmp/repo" "$OUT/$slug.html" > "$OUT/$slug.report.prompt.md"
    rm -f "${OUT:?}/${slug:?}.html"
    (cd "$tmp/repo" && timeout 30m claude -p --model "$MODEL" --setting-sources project,local \
       --permission-mode dontAsk --add-dir "$OUT" "$REPO/skills/tech-debt-triage" --allowed-tools Read Write Bash \
       < "$OUT/$slug.report.prompt.md" > "$OUT/$slug.report.md") || echo "$slug report: claude exited $?" >&2
    rm -rf "${tmp:?}"
    echo "== $slug report ($MODEL)"
    python3 judge.py report "$case" "$OUT/$slug.html" | tee "$OUT/$slug.report.txt" || fails=$((fails + 1))
    continue
  fi
  python3 judge.py prompt "$case" "$tmp/repo" > "$OUT/$slug.prompt.md"
  for i in $(seq "$RUNS"); do
    # Prompt on stdin: --allowed-tools is variadic and swallows a trailing prompt.
    (cd "$tmp/repo" && timeout 30m claude -p --model "$MODEL" --setting-sources project,local \
       --permission-mode dontAsk --allowed-tools Read Grep Glob \
       < "$OUT/$slug.prompt.md" > "$OUT/$slug.$i.md") || echo "$slug run $i: claude exited $?" >&2
  done
  rm -rf "${tmp:?}"
  echo "== $slug ($MODEL, $RUNS runs)"
  python3 judge.py grade "$case" $(seq -f "$OUT/$slug.%g.md" "$RUNS") | tee "$OUT/$slug.grade.txt" || fails=$((fails + 1))
done
echo "results: $OUT"
exit $((fails > 0))
