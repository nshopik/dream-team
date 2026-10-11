// What dream-fixer-loop does with each Simplify review and externalReview arg, which lenses review, and the prompt rules agents get, through stub agents; no claude call.
// Usage: node test_simplify.mjs
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor
const body = readFileSync(new URL('dream-fixer-loop.js', import.meta.url), 'utf8').replace(/^export /m, '')
const args = { issue: '1', branch: 'issue-1', base: 'HEAD', gateCommands: ['true'] }

// Every other reviewer passes, so the run ends after Review or its fix rounds.
// gateFails: gate runs that fail before one passes.
// externalRuns: the external reviewer's replies, the first to its review, the rest to its re-reviews.
async function run(review, cuts, { aspects = ['code'], gateFails = 0, externalReview, externalRuns = [], redEvidence = '' } = {}) {
  const labels = []
  const prompts = {}
  const types = {}
  async function agent(prompt, opts) {
    const reply = await stub(prompt, opts)
    return reply && { ...reply, friction: ['stub friction'] }
  }
  async function stub(prompt, opts) {
    labels.push(opts.label)
    prompts[opts.label] = prompt
    types[opts.label] = opts.agentType
    if (opts.phase === 'Implement') return { committed: true, summary: '', redEvidence }
    if (opts.label.startsWith('build-fix:')) return { committed: true, summary: '' }
    if (opts.phase === 'Gate') return { passed: gateFails-- <= 0, summary: '', changedFiles: [], dirtyPaths: [], aspects }
    if (opts.label.startsWith('simplify:')) return review
    if (opts.label.startsWith('simplify-fix:')) return cuts
    if (/^(re-)?review:external/.test(opts.label)) return externalRuns.shift()
    if (opts.label.startsWith('fix:')) return { committed: true, addressed: ['external'], disputed: [], summary: '' }
    if (opts.phase === 'Review') return { summary: '', findings: [] }
    throw new Error(`unexpected agent ${opts.label}`)
  }
  const result = await new AsyncFunction('args', 'agent', 'phase', 'log', 'parallel', body)(
    { ...args, externalReview }, agent, () => {}, () => {}, (fns) => Promise.all(fns.map((f) => f())))
  assert.ok(!JSON.stringify(result).includes('stub friction'), 'friction stays out of the result')
  return { result, labels, prompts, types }
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

const doneWhenCheck = 'The issue\'s `Done when …` paragraph, when present, must hold on this branch'
const lensLabels = ['architect-reviewer', 'sre-engineer', 'test-coverage-reviewer'].map((l) => `review:dream-team:${l}`)
{
  const name = 'domain lens'
  const { result, labels, prompts, types } = await run(lean, undefined)
  assert.equal(result.ok, true, name)
  assert.ok(labels.includes('review:domain'), `${name}: review:domain dispatched`)
  assert.equal(types['review:domain'], undefined, `${name}: domain lens is generic`)
  assert.deepEqual(labels.filter((l) => l.startsWith('review:dream-team:')), lensLabels, `${name}: lenses dispatched`)
  assert.ok(!labels.some((l) => l.includes('pr-review-toolkit:')), `${name}: no pr-review-toolkit agent`)
  assert.ok(!prompts['review:dream-team:architect-reviewer'].includes(doneWhenCheck), `${name}: architect Done-when check`)
  assert.ok(prompts['review:domain'].includes(doneWhenCheck), `${name}: domain Done-when check`)
  console.log(`PASS ${name}`)
}

const cmd = 'vllm-review --stdin'
const extFinding = { severity: 'important', description: 'off-by-one in the retry count', file: 'retry.js' }
const fixup = 'as `fixup! <subject of the commit it repairs>`'
const red = '--- FAIL: TestRotateKeepsN (0.00s)\n    rotate_test.go:41: kept 4 files, want 5'
const promptRows = [
  { name: 'implementer splits only independent changes', label: 'impl:#1', rule: 'commit each change separately under its own subject' },
  { name: 'build-fix commits fixups', label: 'build-fix:#1:r1', rule: fixup, opts: { gateFails: 1 } },
  { name: 'simplify-fix commits fixups', label: 'simplify-fix:#1', rule: fixup, review: loaded([cut('stdlib')], 4),
    cuts: { committed: true, addressed: ['stdlib cut'], disputed: [], summary: '' } },
  { name: 'fix round commits fixups', label: 'fix:#1:r1', rule: fixup, opts: { externalReview: cmd, externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, { summary: '', findings: [], resolved: [extFinding] }] } },
  { name: 'test lens checks red evidence', label: 'review:dream-team:test-coverage-reviewer', rule: red, opts: { redEvidence: red } },
  { name: 'domain lens skips without a source', label: 'review:domain', rule: 'Either one missing → raise no finding on it and say why in your summary' },
  { name: 'domain lens cites its source', label: 'review:domain', rule: 'cite what you read — file and line' },
]

for (const row of promptRows) {
  const { result, prompts } = await run(row.review || lean, row.cuts, row.opts)
  assert.equal(result.ok, true, row.name)
  assert.ok(prompts[row.label].includes(row.rule), row.name)
  console.log(`PASS ${row.name}`)
}

const externalRows = [
  { name: 'external review unset', opts: {},
    reviewer: false, agents: 0, degraded: [], fixRounds: 0, resolved: [], prompts: [] },
  { name: 'external blocking finding fixed in one round',
    opts: { externalReview: cmd, externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, { summary: '', findings: [], resolved: [extFinding] }] },
    reviewer: true, agents: 2, degraded: [], fixRounds: 1, resolved: [{ ...extFinding, gate: 'external', round: 1 }], prompts: ['review:external'] },
  { name: 'external command fails',
    opts: { externalReview: cmd, externalRuns: [{ ran: false, summary: 'exit 127', findings: [] }] },
    reviewer: true, agents: 1, degraded: ['external'], fixRounds: 0, resolved: [], prompts: ['review:external'] },
]

for (const row of externalRows) {
  const { result, labels, prompts } = await run(lean, undefined, row.opts)
  assert.equal(result.ok, true, row.name)
  assert.equal(result.reviewers.includes('external'), row.reviewer, `${row.name}: reviewers`)
  assert.equal(labels.filter((l) => l.includes(':external')).length, row.agents, `${row.name}: external agents`)
  assert.deepEqual(Object.keys(prompts).filter((l) => prompts[l].includes(`| ${cmd}`) && prompts[l].includes('set -o pipefail;')), row.prompts, `${row.name}: command runs`)
  assert.deepEqual(result.degraded, row.degraded, row.name)
  assert.equal(result.fixRounds, row.fixRounds, row.name)
  assert.deepEqual(result.resolved, row.resolved, row.name)
  console.log(`PASS ${row.name}`)
}
