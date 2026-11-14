export const meta = {
  name: 'build-meta-loop',
  description: 'One Meta issue on one integration branch: build-issue-loop to the gate per child, oldest ready first, then build-issue-loop once from Simplify over the whole branch',
  phases: [
    { title: 'Children', detail: 'build-issue-loop up to the gate per child, one at a time; a child that fails is reset off the branch and its dependents skipped' },
    { title: 'Review', detail: 'build-issue-loop from Simplify over the diff from the base, with the Meta issue and every finished child as the issue' },
  ],
}

// ---------------------------------------------------------------------------
// Inputs (all from the build-meta skill, which already triaged and branched)
// ---------------------------------------------------------------------------
const A = args || {}
const META = A.meta || {}
const CHILDREN = Array.isArray(A.children) ? A.children : []
const BRANCH = String(A.branch || '')
const BASE = String(A.base || '')
const GATE_COMMANDS = Array.isArray(A.gateCommands) ? A.gateCommands.map(String).filter(Boolean) : []
const NOTES = String(A.notes || '')
const LOOP = 'dream-team:build-issue-loop'

if (!META.issue || !CHILDREN.length || !BRANCH || !BASE || !GATE_COMMANDS.length) {
  throw new Error('build-meta-loop: args.meta.issue, args.children, args.branch, args.base and args.gateCommands are required')
}

const RESET_SCHEMA = {
  type: 'object',
  required: ['head', 'status'],
  additionalProperties: false,
  properties: {
    head: { type: 'string', description: 'the sha `git rev-parse HEAD` printed after the reset' },
    status: { type: 'array', items: { type: 'string' }, description: 'the lines `git status --porcelain` printed after the reset; empty when clean' },
  },
}

const ids = new Set(CHILDREN.map((c) => String(c.issue)))
const pending = [...CHILDREN].sort((a, b) => Number(a.issue) - Number(b.issue))
const done = []
const failed = []
const joinNotes = (...n) => n.filter(Boolean).join('\n')

phase('Children')
let tip = BASE
for (;;) {
  const ready = (c) => (c.blockedBy || []).every((b) => !ids.has(String(b)) || done.some((d) => d.issue === String(b)))
  const c = pending.find(ready)
  if (!c) break
  pending.splice(pending.indexOf(c), 1)
  const r = await workflow(LOOP, {
    issue: String(c.issue), title: c.title, body: c.body, notes: joinNotes(NOTES, c.notes),
    branch: BRANCH, base: tip, gateCommands: GATE_COMMANDS, stopAfterGate: true,
  })
  if (r?.ok) {
    done.push(r)
    tip = r.head
    continue
  }
  failed.push({ ...r, issue: String(c.issue) })
  log(`#${c.issue}: ${r?.stage || 'loop'} failed (${r?.reason || 'no result'}) — reset to ${tip}, dependents skipped.`)
  // Scripts have no shell, so an agent drops the failed child's commits.
  const reset = await agent([
    `In the repo checkout on branch ${BRANCH}, run \`git reset --hard ${tip}\`, \`git clean -fd\`, \`git rev-parse HEAD\` and \`git status --porcelain\`.`,
    'Run nothing else; report the sha it printed as head and the status lines as status.',
  ].join('\n'), { label: `reset:#${c.issue}`, phase: 'Children', schema: RESET_SCHEMA, model: 'sonnet', effort: 'low' })
  if (reset?.head !== tip || reset.status?.length) {
    return { ok: false, stage: 'reset', reason: `reset after #${c.issue} left HEAD at ${reset?.head} (want ${tip}), status: ${(reset?.status || []).join('; ') || 'clean'}`, children: done, failed, skipped: pending.map((p) => String(p.issue)), review: null }
  }
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
