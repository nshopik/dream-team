#!/usr/bin/env bash
# Runs reviewers headless on one change, grades each run against <out>/ledger.json, prints scores.
# Usage: run.sh <repo> <base> <head> <reviewers.txt> <out>
#   reviewers.txt: one "<PREFIX>[:lenses] model=<model-id> [runner=<r>] [effort=<e>] [shown=<name>] <prompt>"
#   line per reviewer; runner=claude (default) or codex; {base} and {head} expand;
#   :lenses grades each subagent's report as a lens;
#   shown= replaces model= in the score table's model column.
#   Env: N runs per reviewer (default 1), reviewer EFFORT (high) for a line without effort=, P
#   parallel runs and, on a frozen ledger, parallel grades (default 1), PLUGIN_DIR (Claude only,
#   unset: installed plugins). The grader runs on opus at effort high.
# A rerun skips finished runs and graded runs; delete <out>/<run> to redo a run, its marks.txt to
# regrade it.
set -u
[ $# -eq 5 ] || { sed -n '3,11p' "$0"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$1" && pwd) BASE=$2 HEAD_REF=$3

kv='^(model|runner|effort|shown)=([^ ]+) +(.*)' jobs=()
while read -r prefix prompt || [ -n "$prefix" ]; do
  case $prefix in
    ''|'#'*) continue ;;
    *:lenses) lenses=lenses prefix=${prefix%:lenses} ;;
    *) lenses= ;;
  esac
  model= runner=claude effort=${EFFORT:-high} shown=
  while [[ $prompt =~ $kv ]]; do
    printf -v "${BASH_REMATCH[1]}" %s "${BASH_REMATCH[2]}" && prompt=${BASH_REMATCH[3]}
  done
  [ "$model" ] || { echo "$4: $prefix: no model= field" >&2; exit 2; }
  case $runner in
    claude|codex) ;;
    *) echo "$4: $prefix: unknown runner=$runner" >&2; exit 2 ;;
  esac
  prompt=${prompt//\{base\}/$BASE} && prompt=${prompt//\{head\}/$HEAD_REF}
  cmd=$prefix && [[ $prompt == /* ]] && cmd=${prompt%% *} && cmd=${cmd#/} && cmd=${cmd##*:}
  for k in $(seq "${N:-1}"); do
    jobs+=("$prefix-r$k" "$prompt" "$lenses" "$model" "$effort"
           "reviewer=$cmd model=$model effort=$effort${shown:+ shown=$shown}" "$runner")
  done
done < "$4"
[ ${#jobs[@]} -gt 0 ] || { echo "$4: no reviewer lines" >&2; exit 2; }

mkdir -p "$5" && OUT=$(cd "$5" && pwd) && WT=$OUT/.repo
export HERE OUT WT REPO BASE HEAD_REF PLUGIN_DIR=${PLUGIN_DIR:-}
git -C "$REPO" worktree remove --force "$WT" 2>/dev/null
git -C "$REPO" worktree add -q --detach "$WT" "$HEAD_REF" || exit
trap 'git -C "$REPO" worktree remove --force "$WT"' EXIT

review() {
  case $1 in
    codex)
      codex -a never exec --json --sandbox read-only --model "$3" \
        -c "model_reasoning_effort=\"$4\"" - <<< "$2"
      ;;
    claude)
      CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 claude -p "$2" --model "$3" \
        --effort "$4" --output-format json --permission-mode auto \
        ${PLUGIN_DIR:+--plugin-dir "$PLUGIN_DIR"} --allowedTools 'Write(//tmp/**)' \
        --disallowedTools Edit NotebookEdit "Write(/$PWD/**)" 'Bash(gh:*)' 'Bash(git push:*)' \
        'Bash(git commit:*)' 'Bash(git checkout:*)' 'Bash(git reset:*)' 'Bash(git switch:*)' \
        'Bash(git branch:*)' 'Bash(git tag:*)' 'Bash(git update-ref:*)' 'Bash(git stash:*)'
      ;;
  esac
}

# Each run gets its own worktree: Bash can still change files or leave a CLAUDE.local.md that other
# runs would read.
run() {
  local d=$OUT/$1 w=$OUT/$1/$1 s rc wall x
  [ -e "$d/stats.txt" ] && return
  if [ -s "$d/review-status.txt" ]; then
    read -r rc wall < "$d/review-status.txt" || return 1
  else
    rm -rf "$d" && mkdir -p "$d" || return
    git -C "$REPO" worktree add -qf --detach "$w" "$HEAD_REF" ||
      { echo "$1: failed, no stats.txt" >&2; return 1; }
    s=$(date +%s)
    (cd "$w" && review "$7" "$2" "$4" "$5") > "$d/result.json" 2> "$d/stderr"
    rc=$?
    wall=$(( $(date +%s) - s ))s
    [ -e "$w/CLAUDE.local.md" ] && mv "$w/CLAUDE.local.md" "$d/leaked.CLAUDE.local.md" &&
      echo "$1: moved a leaked CLAUDE.local.md to $d" >&2
    git -C "$REPO" worktree remove --force "$w"
    printf '%s %s\n' "$rc" "$wall" > "$d/review-status.txt" || return 1
  fi
  if ! x=$(python3 "$HERE/extract.py" "$d" "$3" "$7" 2>"$d/extract.err"); then
    if [ "$rc" -eq 0 ]; then
      echo "$1: extraction failed, see $d/extract.err" >&2
      return 1
    fi
    x="cost=? report=0 lenses=0"
  fi
  [ "$rc" -eq 0 ] || x="${x% early-exit} early-exit"
  echo "$6 exit=$rc wall=$wall $x" > "$d/stats.txt" || return 1
  echo "$1 $(cat "$d/stats.txt")"
}
export -f run review
printf '%s\0' "${jobs[@]}" | xargs -0 -n7 -P"${P:-1}" bash -c 'run "$@"' _ || exit 1

has_mark() {
  awk -v run="$1" '$1 == run || index($1, run ".") == 1 {found=1} END {exit !found}'
}

grade() {
  local name=$1 d=$OUT/$1 allow='' mode marks
  [ -s "$d/marks.txt" ] && has_mark "$name" < "$d/marks.txt" && return
  # An early exit scores 0 rather than dropping out of the reviewer's mean.
  grep -q early-exit "$d/stats.txt" && { echo "$name" | tee "$d/marks.txt"; return; }
  if [ "$FROZEN" ]; then
    mode="The ledger is frozen: do not change it. A verified claim outside it is a Candidate line."
  else
    allow="Edit(/$OUT/ledger.json)"
    mode="The ledger is not frozen (warm-up): verify each claim against the code, append a row to
$OUT/ledger.json for each verified claim it lacks, then map the findings. Leave \`version\` as is."
  fi
  claude -p --model opus --effort high --permission-mode dontAsk --add-dir "$OUT" "$HERE" \
    --allowedTools Read Grep Glob 'Bash(git diff:*)' 'Bash(git show:*)' 'Bash(git log:*)' \
    ${allow:+"$allow"} > "$d/grade.txt" 2> "$d/grade.err" \
    <<EOF || { echo "$name: grader failed, see $d/grade.err" >&2; return 1; }
You grade one run of a code reviewer for a benchmark. Read $HERE/METHODOLOGY.md and follow its
"Ledger file", "Grading a run" and "Marks file" sections.

The change under review is \`git diff $BASE...HEAD\` in the current directory. The ledger is
$OUT/ledger.json. The run is $name: grade each file in $d/lenses/ as lens
$name.<file name without .md>; with no lenses directory, grade $d/report.md as $name.

$mode

Output only the run's marks lines, then its Rejected, Excluded and Candidate lines; no fence, no
commentary.
EOF
  marks=$(grep -E '^([A-Za-z0-9-]+-r[0-9]|Rejected|Excluded|Candidate)' "$d/grade.txt")
  has_mark "$name" <<< "$marks" ||
    { echo "$name: grader wrote no scored line, see $d/grade.txt" >&2; return 1; }
  printf '%s\n' "$marks" > "$d/marks.pending" &&
    mv "$d/marks.pending" "$d/marks.txt" && cat "$d/marks.txt"
}

[ -e "$OUT/ledger.json" ] || echo '{"version": 1, "rows": []}' > "$OUT/ledger.json"
# Warm-up graders append to the shared ledger, so only a frozen one grades in parallel.
python3 -c 'import json, sys; sys.exit(not json.load(open(sys.argv[1])).get("frozen"))' \
  "$OUT/ledger.json" && FROZEN=1 GP=${P:-1} || FROZEN= GP=1
export FROZEN && export -f grade has_mark
(cd "$WT" && for d in "$OUT"/*/stats.txt; do printf '%s\0' "$(basename "$(dirname "$d")")"; done |
  xargs -0 -n1 -P"$GP" bash -c 'grade "$1"' _) || exit 1
marks=()
for stats in "$OUT"/*/stats.txt; do
  marks+=("${stats%/*}/marks.txt")
done
cat "${marks[@]}" > "$OUT/marks.txt" || exit 1
python3 "$HERE/score.py" "$OUT/ledger.json" "$OUT/marks.txt"
