#!/usr/bin/env bash
# Runs reviewers headless on one change, grades each run against <out>/ledger.json, prints scores.
# Usage: run.sh <repo> <base> <head> <reviewers.txt> <out>
#   reviewers.txt: one "<PREFIX>[:lenses] <prompt>" line per reviewer; {base} and {head} expand;
#   :lenses grades each subagent's report as a lens.
#   Env: N runs per reviewer (default 1), reviewer MODEL (opus) and EFFORT (high), P parallel runs
#   (1), PLUGIN_DIR (unset: installed plugins). The grader runs on opus at effort high.
# A rerun skips finished runs and graded runs; delete <out>/<run> to redo a run, its marks.txt to
# regrade it.
set -u
[ $# -eq 5 ] || { sed -n '3,9p' "$0"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$1" && pwd) BASE=$2 HEAD_REF=$3
mkdir -p "$5" && OUT=$(cd "$5" && pwd) && WT=$OUT/.repo
export HERE OUT WT REPO HEAD_REF MODEL=${MODEL:-opus} EFFORT=${EFFORT:-high} \
  PLUGIN_DIR=${PLUGIN_DIR:-}
git -C "$REPO" worktree remove --force "$WT" 2>/dev/null
git -C "$REPO" worktree add -q --detach "$WT" "$HEAD_REF" || exit

# Each run gets its own worktree: Bash can still change files or leave a CLAUDE.local.md that other
# runs would read.
run() {
  local d=$OUT/$1 w=$OUT/$1/repo s rc x
  [ -e "$d/stats.txt" ] && return
  rm -rf "$d" && mkdir -p "$d" || return
  git -C "$REPO" worktree add -qf --detach "$w" "$HEAD_REF" || return
  s=$(date +%s)
  (cd "$w" && CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 claude -p "$2" --model "$MODEL" \
    --effort "$EFFORT" --output-format json --permission-mode auto \
    ${PLUGIN_DIR:+--plugin-dir "$PLUGIN_DIR"} --allowedTools 'Write(//tmp/**)' \
    --disallowedTools Edit NotebookEdit "Write(/$w/**)" 'Bash(gh:*)' 'Bash(git push:*)' \
    'Bash(git commit:*)' 'Bash(git checkout:*)' 'Bash(git reset:*)' 'Bash(git switch:*)' \
    'Bash(git branch:*)' 'Bash(git tag:*)' 'Bash(git update-ref:*)' 'Bash(git stash:*)' \
    > "$d/result.json" 2> "$d/stderr")
  rc=$?
  [ -e "$w/CLAUDE.local.md" ] && mv "$w/CLAUDE.local.md" "$d/leaked.CLAUDE.local.md" &&
    echo "$1: moved a leaked CLAUDE.local.md to $d" >&2
  git -C "$REPO" worktree remove --force "$w"
  x=$(python3 "$HERE/extract.py" "$d" "$3") && [ "$rc" -eq 0 ] || x="${x% early-exit} early-exit"
  echo "model=$MODEL effort=$EFFORT exit=$rc wall=$(( $(date +%s) - s ))s $x" > "$d/stats.txt"
  echo "$1 $(cat "$d/stats.txt")"
}
export -f run

while read -r prefix prompt || [ -n "$prefix" ]; do
  case $prefix in
    ''|'#'*) continue ;;
    *:lenses) lenses=lenses prefix=${prefix%:lenses} ;;
    *) lenses= ;;
  esac
  prompt=${prompt//\{base\}/$BASE} && prompt=${prompt//\{head\}/$HEAD_REF}
  for k in $(seq "${N:-1}"); do printf '%s\0%s\0%s\0' "$prefix-r$k" "$prompt" "$lenses"; done
done < "$4" | xargs -0 -n3 -P"${P:-1}" bash -c 'run "$@"' _

grade() {
  local name=$1 d=$OUT/$1 allow='' mode
  [ -s "$d/marks.txt" ] && return
  # An early exit scores 0 rather than dropping out of the reviewer's mean.
  grep -q early-exit "$d/stats.txt" && { echo "$name" | tee "$d/marks.txt"; return; }
  [ -e "$OUT/ledger.json" ] || echo '{"version": 1, "rows": []}' > "$OUT/ledger.json"
  if python3 -c 'import json, sys; sys.exit(not json.load(open(sys.argv[1])).get("frozen"))' \
    "$OUT/ledger.json"; then
    mode="The ledger is frozen: do not change it. A verified claim outside it is a Candidate line."
  else
    allow="Edit(/$OUT/ledger.json)"
    mode="The ledger is not frozen (warm-up): verify each claim against the code, append a row to
$OUT/ledger.json for each verified claim it lacks, then map the findings. Leave \`version\` as is."
  fi
  claude -p --model opus --effort high --permission-mode dontAsk --add-dir "$OUT" "$HERE" \
    --allowedTools Read Grep Glob 'Bash(git diff:*)' 'Bash(git show:*)' 'Bash(git log:*)' \
    ${allow:+"$allow"} > "$d/grade.txt" 2> "$d/grade.err" \
    <<EOF || { echo "$name: grader failed, see grade.err" >&2; return; }
You grade one run of a code reviewer for a benchmark. Read $HERE/METHODOLOGY.md and follow its
"Ledger file", "Grading a run" and "Marks file" sections.

The change under review is \`git diff $BASE...HEAD\` in the current directory. The ledger is
$OUT/ledger.json. The run is $name: grade each file in $d/lenses/ as lens
$name.<file name without .md>; with no lenses directory, grade $d/report.md as $name.

$mode

Output only the run's marks lines, then its Rejected, Excluded and Candidate lines; no fence, no
commentary.
EOF
  grep -E '^([A-Z0-9-]+-r[0-9]|Rejected|Excluded|Candidate)' "$d/grade.txt" > "$d/marks.txt" ||
    echo "$name: grader wrote no marks lines, see $d/grade.txt" >&2
  cat "$d/marks.txt"
}

(cd "$WT" && for d in "$OUT"/*/stats.txt; do grade "$(basename "$(dirname "$d")")"; done)
git -C "$REPO" worktree remove --force "$WT"
cat "$OUT"/*/marks.txt > "$OUT/marks.txt"
python3 "$HERE/score.py" "$OUT/ledger.json" "$OUT/marks.txt"
