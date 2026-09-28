// What dream-fixer-loop does with each Simplify review and /verify gate reply, through stub agents; no claude call.
// Usage: node test_simplify.mjs
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor
const body = readFileSync(new URL('dream-fixer-loop.js', import.meta.url), 'utf8').replace(/^export /m, '')
const args = { issue: '1', branch: 'issue-1', base: 'HEAD', gateCommands: ['true'] }

// Every other reviewer passes, so the run ends after Review or its fix rounds.
// verifyRuns: the /verify gate's replies, one per run.
async function run(review, cuts, { verify = false, aspects = ['code'], verifyRuns = [] } = {}) {
  const labels = []
  async function agent(prompt, opts) {
    labels.push(opts.label)
    if (opts.phase === 'Implement') return { committed: true, summary: '', redEvidence: '' }
    if (opts.phase === 'Verify') return { passed: true, summary: '', changedFiles: [], dirtyPaths: [], aspects }
    if (opts.label.startsWith('simplify:')) return review
    if (opts.label.startsWith('simplify-fix:')) return cuts
    if (/^(re-)?review:verify/.test(opts.label)) return verifyRuns.shift()
    if (opts.label.startsWith('fix:')) return { committed: true, addressed: ['verify'], disputed: [], summary: '' }
    if (opts.phase === 'Review') return { summary: '', findings: [] }
    throw new Error(`unexpected agent ${opts.label}`)
  }
  const result = await new AsyncFunction('args', 'agent', 'phase', 'log', 'parallel', body)(
    { ...args, verify }, agent, () => {}, () => {}, (fns) => Promise.all(fns.map((f) => f())))
  return { result, labels }
}

const cut = (tag) => ({ tag, location: 'latency.py:L3', cut: `${tag} cut`, replacement: 'statistics.median' })
const loaded = (findings, net) => ({ skillLoaded: true, findings, net })
const dispute = { finding: 'delete cut', reason: 'main() calls it' }

const rows = [
  { name: 'skill missing', review: { skillLoaded: false, findings: [], net: 0 },
    ok: true, simplify: null, degraded: ['ponytail:ponytail-review'], fixRan: false },
  { name: 'lean', review: loaded([], 0),
    ok: true, simplify: { net: 0, applied: [], disputed: [], unhandled: 0 }, degraded: [], fixRan: false },
  { name: 'one applied, one disputed', review: loaded([cut('stdlib'), cut('delete')], 9),
    cuts: { committed: true, addressed: ['stdlib cut'], disputed: [dispute], summary: '' },
    ok: true, simplify: { net: 9, applied: ['stdlib cut'], disputed: [dispute], unhandled: 0 }, degraded: [], fixRan: true },
  { name: 'one dropped', review: loaded([cut('stdlib'), cut('delete')], 9),
    cuts: { committed: true, addressed: ['stdlib cut'], disputed: [], summary: '' },
    ok: true, simplify: { net: 9, applied: ['stdlib cut'], disputed: [], unhandled: 1 }, degraded: [], fixRan: true },
  { name: 'changed nothing, disputed nothing', review: loaded([cut('stdlib')], 4),
    cuts: { committed: false, addressed: [], disputed: [], summary: 'no-op' },
    ok: false, stage: 'simplify', fixRan: true },
  { name: 'applied without a commit', review: loaded([cut('stdlib'), cut('delete')], 9),
    cuts: { committed: false, addressed: ['stdlib cut'], disputed: [dispute], summary: 'forgot' },
    ok: false, stage: 'simplify', fixRan: true },
]

for (const row of rows) {
  const { result, labels } = await run(row.review, row.cuts)
  assert.equal(result.ok, row.ok, row.name)
  assert.equal(labels.some((l) => l.startsWith('simplify-fix:')), row.fixRan, `${row.name}: simplify-fix dispatched`)
  if (row.ok) {
    assert.deepEqual(result.simplify, row.simplify, row.name)
    assert.deepEqual(result.degraded, row.degraded, row.name)
  } else {
    assert.equal(result.stage, row.stage, row.name)
  }
  console.log(`PASS ${row.name}`)
}

const lean = loaded([], 0)
const vrun = (verdict, recipePath = '') => ({ available: true, verdict, command: 'curl -s localhost:8080/health', output: '{"ok":true}', reason: `${verdict} reason`, recipePath })
const unavailable = { available: false, verdict: 'SKIP', command: '', output: '', reason: '', recipePath: '' }
const failFinding = { severity: 'important', gate: 'verify', round: 1,
  description: '/verify FAIL: FAIL reason\nCommand: curl -s localhost:8080/health\nOutput:\n{"ok":true}' }

const verifyRows = [
  { name: 'verify off', opts: {},
    ok: true, verifyRun: null, degraded: [], ran: 0, fixRounds: 0, resolved: [] },
  { name: 'verify on, diff has no code', opts: { verify: true, aspects: [] },
    ok: true, verifyRun: null, degraded: [], ran: 0, fixRounds: 0, resolved: [] },
  { name: 'verify unavailable', opts: { verify: true, verifyRuns: [unavailable] },
    ok: true, verifyRun: null, degraded: ['verify'], ran: 1, fixRounds: 0, resolved: [] },
  { name: 'verify PASS with recipe', opts: { verify: true, verifyRuns: [vrun('PASS', '/tmp/tmp.x/SKILL.md')] },
    ok: true, verifyRun: vrun('PASS', '/tmp/tmp.x/SKILL.md'), degraded: [], ran: 1, fixRounds: 0, resolved: [] },
  { name: 'verify BLOCKED is not a finding', opts: { verify: true, verifyRuns: [vrun('BLOCKED')] },
    ok: true, verifyRun: vrun('BLOCKED'), degraded: [], ran: 1, fixRounds: 0, resolved: [] },
  { name: 'verify FAIL fixed in one round', opts: { verify: true, verifyRuns: [vrun('FAIL'), vrun('PASS')] },
    ok: true, verifyRun: vrun('PASS'), degraded: [], ran: 2, fixRounds: 1, resolved: [failFinding] },
  { name: 'verify FAIL never fixed', opts: { verify: true, verifyRuns: [vrun('FAIL'), vrun('FAIL'), vrun('FAIL'), vrun('FAIL')] },
    ok: false, verifyRun: vrun('FAIL'), degraded: [], ran: 4, resolved: [] },
  { name: 'verify FAIL then BLOCKED keeps the FAIL', opts: { verify: true, verifyRuns: [vrun('FAIL'), vrun('BLOCKED'), vrun('BLOCKED'), vrun('BLOCKED')] },
    ok: false, verifyRun: vrun('BLOCKED'), degraded: [], ran: 4, resolved: [] },
  { name: 'verify FAIL then unavailable keeps the FAIL', opts: { verify: true, verifyRuns: [vrun('FAIL'), unavailable, unavailable, unavailable] },
    ok: false, verifyRun: vrun('FAIL'), degraded: ['verify'], ran: 4, resolved: [] },
]

for (const row of verifyRows) {
  const { result, labels } = await run(lean, undefined, row.opts)
  assert.equal(result.ok, row.ok, row.name)
  assert.equal(labels.filter((l) => /^(re-)?review:verify/.test(l)).length, row.ran, `${row.name}: /verify runs`)
  assert.deepEqual(result.verifyRun, row.verifyRun, row.name)
  assert.deepEqual(result.degraded, row.degraded, row.name)
  assert.deepEqual(result.resolved, row.resolved, row.name)
  if (row.ok) assert.equal(result.fixRounds, row.fixRounds, row.name)
  else assert.equal(result.handBack, true, row.name)
  console.log(`PASS ${row.name}`)
}
