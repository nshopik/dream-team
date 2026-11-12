#!/usr/bin/env bash
# Judge eval for tech-debt-triage (#431). Per case: export its commit to a temp dir, no .git,
# run the SKILL.md judge brief headless on its candidates, grade the verdicts with judge.py.
# Pass: every `Act now` case candidate comes back Act now, every other one Later or Skip.
#
# Usage:  ./run.sh [slug ...]                  (no args = every cases/*.json)
#         MODEL=fable OUT=runs/<name> ./run.sh
set -euo pipefail
cd "$(dirname "$0")"
REPO=$(git rev-parse --show-toplevel)
MODEL=${MODEL:-fable}
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
  python3 judge.py prompt "$case" "$tmp/repo" > "$OUT/$slug.prompt.md"
  # Prompt on stdin: --allowed-tools is variadic and swallows a trailing prompt.
  (cd "$tmp/repo" && timeout 30m claude -p --model "$MODEL" --setting-sources project,local \
     --permission-mode dontAsk --allowed-tools Read Grep Glob \
     < "$OUT/$slug.prompt.md" > "$OUT/$slug.md") || echo "$slug: claude exited $?" >&2
  rm -rf "${tmp:?}"
  echo "== $slug ($MODEL)"
  python3 judge.py grade "$case" "$OUT/$slug.md" | tee "$OUT/$slug.grade.txt" || fails=$((fails + 1))
done
echo "results: $OUT"
exit $((fails > 0))
