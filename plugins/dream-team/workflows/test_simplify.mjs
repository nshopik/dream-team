// What dream-fixer-loop does with each Simplify review reply, through stub agents; no claude call.
// Usage: node test_simplify.mjs
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor
const body = readFileSync(new URL('dream-fixer-loop.js', import.meta.url), 'utf8').replace(/^export /m, '')
const args = { issue: '1', branch: 'issue-1', base: 'HEAD', gateCommands: ['true'] }

// Every reviewer passes, so the run ends after Review.
async function run(review, cuts) {
  const labels = []
  async function agent(prompt, opts) {
    labels.push(opts.label)
    if (opts.phase === 'Implement') return { committed: true, summary: '', redEvidence: '' }
    if (opts.phase === 'Verify') return { passed: true, summary: '', changedFiles: [], dirtyPaths: [], aspects: ['code'] }
    if (opts.label.startsWith('simplify:')) return review
    if (opts.label.startsWith('simplify-fix:')) return cuts
    if (opts.phase === 'Review') return { summary: '', findings: [] }
    throw new Error(`unexpected agent ${opts.label}`)
  }
  const result = await new AsyncFunction('args', 'agent', 'phase', 'log', 'parallel', body)(
    args, agent, () => {}, () => {}, (fns) => Promise.all(fns.map((f) => f())))
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
