export const meta = {
  name: 'assemble-meta-loop',
  description: 'One Meta issue on one integration branch: build-issue-loop to the gate per child, oldest ready first, then build-issue-loop once from Simplify over the whole branch',
  phases: [
    { title: 'Children', detail: 'build-issue-loop up to the gate per child, two at once, each in its own worktree; a child lands by rebase, re-gate and fast-forward in finish order, reruns once when that fails, and a failed child drops its branch and skips its dependents' },
    { title: 'Review', detail: 'build-issue-loop from Simplify over the diff from the base, with the Meta issue and every finished child as the issue' },
  ],
}

// ---------------------------------------------------------------------------
// Inputs (all from the assemble-meta skill, which already triaged and branched)
// ---------------------------------------------------------------------------
const A = args || {}
const META = A.meta || {}
const CHILDREN = Array.isArray(A.children) ? A.children : []
const BRANCH = String(A.branch || '')
const BASE = String(A.base || '')
const WORKTREE = String(A.worktree || '')
const GATE_COMMANDS = Array.isArray(A.gateCommands) ? A.gateCommands.map(String).filter(Boolean) : []
const NOTES = String(A.notes || '')
const LOOP = 'dream-team:build-issue-loop'

if (!META.issue || !CHILDREN.length || !BRANCH || !BASE || !WORKTREE.startsWith('/') || !GATE_COMMANDS.length) {
  throw new Error('assemble-meta-loop: args.meta.issue, args.children, args.branch, args.base, args.worktree (absolute) and args.gateCommands are required')
}

const WORKTREE_SCHEMA = {
  type: 'object',
  required: ['path', 'head'],
  additionalProperties: false,
  properties: {
    path: { type: 'string', description: 'the absolute path the worktree was added at' },
    head: { type: 'string', description: 'the sha `git rev-parse HEAD` printed in the new worktree' },
  },
}

const LAND_SCHEMA = {
  type: 'object',
  required: ['landed', 'gated', 'head', 'reason'],
  additionalProperties: false,
  properties: {
    landed: { type: 'boolean', description: 'true only when the merge fast-forwarded the integration branch' },
    gated: { type: 'string', description: 'the sha `git rev-parse HEAD` printed in the worktree after the rebase; empty when the rebase conflicted' },
    head: { type: 'string', description: 'the sha `git rev-parse HEAD` printed in the integration worktree after the merge; empty when not landed' },
    reason: { type: 'string', description: 'why it did not land: the rebase conflict or the failing gate command and its key error lines; empty when landed' },
  },
}

const LIMIT = 2
const ids = new Set(CHILDREN.map((c) => String(c.issue)))
const pending = [...CHILDREN].sort((a, b) => Number(a.issue) - Number(b.issue))
const done = []
const failed = []
const joinNotes = (...n) => n.filter(Boolean).join('\n')
const cheap = (label) => ({ label, phase: 'Children', model: 'sonnet', effort: 'low' })

let tip = BASE
// One landing at a time, so the tip cannot move between a child's re-gate and its fast-forward.
let landing = Promise.resolve()

async function attempt(c, tag) {
  const issue = String(c.issue)
  const branch = `${BRANCH}-${issue}`
  const base = tip
  // Under .claude/worktrees/, which build-issue already excludes; Claude Code guards writes inside .git.
  const path = `"$(git -C "${WORKTREE}" rev-parse --path-format=absolute --git-common-dir)/../.claude/worktrees/${branch}"`
  const wt = await agent([
    `Run \`git -C "${WORKTREE}" worktree remove --force ${path}\` and \`git -C "${WORKTREE}" worktree prune\`, ignoring their errors: an earlier run may have left that worktree.`,
    `Then run \`git -C "${WORKTREE}" worktree add -B ${branch} ${path} ${base}\`.`,
    `Each path git ignores that is a symlink in ${WORKTREE} → create the same symlink in the new worktree.`,
    'Run nothing beyond these; report the absolute worktree path as path and the sha `git rev-parse HEAD` prints in it as head.',
  ].join('\n'), { ...cheap(`worktree:#${issue}${tag}`), schema: WORKTREE_SCHEMA })
  if (!wt?.path || wt.head !== base) return { ok: false, issue, stage: 'worktree', reason: `worktree agent reported head ${wt?.head || 'none'}, not ${base}` }
  const r = await workflow(LOOP, {
    issue, title: c.title, body: c.body, notes: joinNotes(NOTES, c.notes),
    branch, base, worktree: wt.path, gateCommands: GATE_COMMANDS, stopAfterGate: true,
  })
  const land = r?.ok && await (landing = landing.then(async () => {
    const l = await agent([
      `Land branch ${branch} on the integration branch ${BRANCH}. Start every Bash command in the worktree with \`cd ${wt.path} &&\`.`,
      `In the worktree, run \`git rebase ${tip}\`. It conflicts → run \`git rebase --abort\`, report landed false with the conflicting paths as reason, and stop.`,
      'Report the sha `git rev-parse HEAD` then prints in the worktree as gated.',
      'Then run each of these gate commands in the worktree, in order; one fails → report landed false with it and its key error lines as reason, and stop:',
      ...GATE_COMMANDS.map((g) => `  ${g}`),
      `All pass → run \`git -C "${WORKTREE}" merge --ff-only ${branch}\` and \`git -C "${WORKTREE}" rev-parse HEAD\`, and report landed true with that sha as head.`,
      'Do not edit, fix or commit anything.',
    ].join('\n'), { ...cheap(`land:#${issue}${tag}`), schema: LAND_SCHEMA })
    if (!l) return { landed: false, reason: 'land agent returned no result' }
    // A fast-forward leaves the integration branch on the re-gated sha; anything else did not land.
    if (l.landed && l.head !== l.gated) return { landed: false, reason: `the integration branch is at ${l.head}, not the re-gated ${l.gated}` }
    if (l.landed) tip = l.head
    return l
  }))
  // `--force` would delete the untracked files the gate reported, so their worktree stays.
  const kept = r?.untrackedPaths?.length ? { worktree: wt.path } : {}
  if (!kept.worktree) await agent(`Run \`git -C "${WORKTREE}" worktree remove --force "${wt.path}"\` and \`git -C "${WORKTREE}" branch -D ${branch}\`. Run nothing else.`, cheap(`remove:#${issue}${tag}`))
  if (!r?.ok) return { ...r, ...kept, ok: false, issue }
  if (!land.landed) return { ok: false, issue, stage: 'land', reason: land.reason, ...kept }
  return { ...r, ...kept, head: land.head }
}

async function build(c) {
  let r = await attempt(c, '')
  if (r.stage === 'land') {
    log(`#${c.issue}: landing failed (${r.reason}) — rerunning from ${tip}.`)
    r = await attempt(c, ':rerun')
  }
  if (r.ok) {
    done.push(r)
    return
  }
  failed.push(r)
  log(`#${c.issue}: ${r.stage || 'loop'} failed (${r.reason || 'no result'}) — its branch dropped, dependents skipped.`)
}

phase('Children')
const ready = (c) => (c.blockedBy || []).every((b) => !ids.has(String(b)) || done.some((d) => d.issue === String(b)))
const running = new Set()
for (;;) {
  for (let c; running.size < LIMIT && (c = pending.find(ready));) {
    pending.splice(pending.indexOf(c), 1)
    const p = build(c).then(() => running.delete(p))
    running.add(p)
  }
  if (!running.size) break
  await Promise.race(running)
}
const skipped = pending.map((p) => String(p.issue))

if (!done.length) return { ok: false, stage: 'children', reason: 'no child passed the gate', children: done, failed, skipped, review: null }

phase('Review')
const finished = CHILDREN.filter((c) => done.some((d) => d.issue === String(c.issue)))
const review = await workflow(LOOP, {
  issue: String(META.issue), title: META.title,
  body: [META.body, ...finished.map((c) => `## #${c.issue}: ${c.title}\n\n${c.body}`)].join('\n\n'),
  notes: joinNotes(NOTES, ...finished.filter((c) => c.notes).map((c) => `#${c.issue}: ${c.notes}`)),
  redEvidence: done.filter((d) => d.redEvidence).map((d) => `#${d.issue}: ${d.redEvidence}`).join('\n'),
  branch: BRANCH, base: BASE, gateCommands: GATE_COMMANDS, externalReview: A.externalReview, startAtSimplify: true,
})

return { ok: !!review?.ok, children: done, failed, skipped, review }
