// What dream-fixer-loop does with each Simplify review and externalReview arg, which lenses review, and the prompt rules agents get, through stub agents; no claude call.
// Usage: node test_simplify.mjs
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor
const body = readFileSync(new URL('dream-fixer-loop.js', import.meta.url), 'utf8').replace(/^export /m, '')
const args = { issue: '1', branch: 'issue-1', base: 'HEAD', gateCommands: ['true'], diffFile: '/scratch/issue-1.diff' }

// Every other reviewer passes, so the run ends after Review or its fix rounds.
// gateFails: gate runs that fail before one passes.
// externalRuns: the external reviewer's replies, the first to its review, the rest to its re-reviews and full-review retries, in call order.
// domainRuns: the same for the domain reviewer, which passes once they run out. fixes: fix-round replies, then defaults.
// status: the gate's `git status --porcelain` lines. nullOnce: labels whose first call returns null.
// throwFor: agent types whose dispatch throws.
async function run(review, cuts, { aspects = ['code'], gateFails = 0, diffWritten = true, externalReview, externalRuns = [], domainRuns = [], fixes = [], redEvidence = '', status = [], nullOnce = [], throwFor = [] } = {}) {
  const labels = []
  const prompts = {}
  const types = {}
  const nulls = new Set(nullOnce)
  async function agent(prompt, opts) {
    if (throwFor.includes(opts.agentType)) throw new Error('agent dispatch failed')
    if (nulls.delete(opts.label)) return null
    const reply = await stub(prompt, opts)
    return reply && { ...reply, friction: ['stub friction'] }
  }
  async function stub(prompt, opts) {
    labels.push(opts.label)
    prompts[opts.label] = prompt
    types[opts.label] = opts.agentType
    if (opts.phase === 'Implement') return { committed: true, summary: '', redEvidence }
    if (opts.label.startsWith('build-fix:')) return { committed: true, summary: '' }
    if (opts.phase === 'Gate') return { passed: gateFails-- <= 0, summary: '', changedFiles: [], status, diffWritten, aspects }
    if (opts.label.startsWith('simplify:')) return review
    if (opts.label.startsWith('simplify-fix:')) return cuts
    if (/^(re-)?review:external/.test(opts.label)) return externalRuns.shift()
    if (/^(re-)?review:domain/.test(opts.label) && domainRuns.length) return domainRuns.shift()
    if (opts.label.startsWith('fix:')) return fixes.shift() || { committed: true, addressed: ['external'], disputed: [], summary: '' }
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

const leanSimplify = { net: 0, applied: [], disputed: [], unhandled: 0 }
const rows = [
  { name: 'skill missing', review: { skillLoaded: false, findings: [], net: 0 },
    ok: true, simplify: null, degraded: ['ponytail:ponytail-review'], fixRan: false },
  { name: 'lean', review: loaded([], 0),
    ok: true, simplify: leanSimplify, degraded: [], fixRan: false },
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
  { name: 'diff file not written', review: loaded([], 0), opts: { diffWritten: false },
    ok: false, stage: 'gate', fixRan: false },
  { name: 'untracked path', review: loaded([], 0), opts: { status: ['?? coverage.out'] },
    ok: true, simplify: leanSimplify, degraded: [], untracked: ['coverage.out'], fixRan: false },
  { name: 'modified tracked file', review: loaded([], 0), opts: { status: [' M main.py', '?? coverage.out'] },
    ok: false, stage: 'gate', untracked: ['coverage.out'], fixRan: false },
  { name: 'one null from the implementer and the gate', review: loaded([], 0), opts: { nullOnce: ['impl:#1', 'gate:#1'] },
    ok: true, simplify: leanSimplify, degraded: [], fixRan: false },
  { name: 'simplify review empty', review: null,
    ok: true, simplify: null, degraded: ['ponytail:ponytail-review'], fixRan: false },
  { name: 'agent type fails to dispatch', review: loaded([], 0), opts: { throwFor: ['dream-team:sre-engineer'] },
    ok: true, simplify: leanSimplify, degraded: ['dream-team:sre-engineer'], fixRan: false },
]

for (const row of rows) {
  const { result, labels } = await run(row.review, row.cuts, row.opts)
  assert.equal(result.ok, row.ok, row.name)
  assert.equal(labels.some((l) => l.startsWith('simplify-fix:')), row.fixRan, `${row.name}: simplify-fix dispatched`)
  if (row.ok) {
    assert.deepEqual(result.simplify, row.simplify, row.name)
    assert.deepEqual(result.degraded, row.degraded, row.name)
    assert.deepEqual(result.untrackedPaths, row.untracked || [], `${row.name}: untrackedPaths`)
  } else {
    assert.equal(result.stage, row.stage, row.name)
    if (row.untracked) assert.deepEqual(result.untrackedPaths, row.untracked, `${row.name}: untrackedPaths`)
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
// The fixer disputes, its re-review dies once, then answers; a second fixer call changes nothing and fails the run.
const deadDispute = () => ({ externalReview: cmd, externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, undefined, undefined, { summary: '', findings: [], resolved: [] }],
  fixes: [{ committed: false, addressed: [], disputed: [dispute], summary: '' }, { committed: false, addressed: [], disputed: [], summary: '' }] })
const promptRows = [
  { name: 'implementer splits only independent changes', label: 'impl:#1', rule: 'commit each change separately under its own subject' },
  { name: 'build-fix commits fixups', label: 'build-fix:#1:r1', rule: fixup, opts: { gateFails: 1 } },
  { name: 'simplify-fix commits fixups', label: 'simplify-fix:#1', rule: fixup, review: loaded([cut('stdlib')], 4),
    cuts: { committed: true, addressed: ['stdlib cut'], disputed: [], summary: '' } },
  { name: 'fix round commits fixups', label: 'fix:#1:r1', rule: fixup, opts: { externalReview: cmd, externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, { summary: '', findings: [], resolved: [extFinding] }] } },
  { name: 'test lens checks red evidence', label: 'review:dream-team:test-coverage-reviewer', rule: red, opts: { redEvidence: red } },
  { name: 'domain lens skips without a source', label: 'review:domain', rule: 'Either one missing → raise no finding on it and say why in your summary' },
  { name: 'domain lens cites its source', label: 'review:domain', rule: 'cite what you read — file and line' },
  { name: 'retry after a null result checks earlier commits', label: 'impl:#1', rule: 'may already have committed part of it', opts: { nullOnce: ['impl:#1'] } },
  { name: 'gate writes the diff file', label: 'gate:#1', rule: "git diff HEAD..HEAD > '/scratch/issue-1.diff'" },
  { name: 'lens reads the diff file', label: 'review:dream-team:sre-engineer', rule: 'The branch diff is in `/scratch/issue-1.diff`' },
  { name: 'domain lens reads the diff file', label: 'review:domain', rule: 'The branch diff is in `/scratch/issue-1.diff`' },
  { name: 'dead re-review is retried against the fix it missed', label: 're-review:external:r2', rule: `Disputed: ${dispute.finding}`, opts: deadDispute() },
  { name: 're-review reads the diff file', label: 're-review:external:r1', rule: 'The branch diff is in `/scratch/issue-1.diff`', opts: { externalReview: cmd, externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, { summary: '', findings: [], resolved: [extFinding] }] } },
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
  { name: 'retried reviewer finding goes to the next fix round, not the dispute hand-back',
    opts: { externalReview: cmd, externalRuns: [undefined, undefined, { ran: true, summary: '', findings: [extFinding] }, { summary: '', findings: [], resolved: [extFinding] }],
      domainRuns: [{ summary: '', findings: [{ ...extFinding, file: 'main.js' }] }, { summary: '', findings: [], resolved: [] }],
      fixes: [{ committed: false, addressed: [], disputed: [dispute], summary: '' }] },
    reviewer: true, agents: 4, degraded: [], fixRounds: 2, resolved: [{ ...extFinding, gate: 'external', round: 2 }], prompts: ['review:external', 'review:external:retry1'] },
  { name: 'dead re-review of a dispute is re-reviewed, not handed back or re-fixed', opts: deadDispute(),
    reviewer: true, agents: 4, degraded: [], fixRounds: 2, resolved: [], prompts: ['review:external'] },
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

const stuck = { summary: '', findings: [extFinding], resolved: [] }
const handBackRows = [
  { name: 'hand-back carries untracked paths', opts: { status: ['?? coverage.out'], externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, stuck, stuck, stuck] },
    untracked: ['coverage.out'], dead: [] },
  { name: 'dead re-review keeps its findings and is re-reviewed', opts: { externalRuns: [{ ran: true, summary: '', findings: [extFinding] }] },
    untracked: [], dead: ['external'] },
  { name: 'held dispute hands back', opts: { externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, stuck],
    fixes: [{ committed: false, addressed: [], disputed: [dispute], summary: '' }] }, untracked: [], dead: [] },
]

for (const row of handBackRows) {
  const { result, labels } = await run(lean, undefined, { externalReview: cmd, ...row.opts })
  assert.equal(result.handBack, true, row.name)
  assert.deepEqual(result.blocking, [{ ...extFinding, gate: 'external' }], `${row.name}: blocking`)
  assert.deepEqual(result.deadReviewers, row.dead, `${row.name}: deadReviewers`)
  assert.deepEqual(result.untrackedPaths, row.untracked, `${row.name}: untrackedPaths`)
  assert.ok(!labels.some((l) => l.startsWith('review:external:retry')), `${row.name}: no full-review retry`)
  console.log(`PASS ${row.name}`)
}
