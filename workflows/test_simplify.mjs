// What build-issue-loop does with each Simplify review and externalReview arg, which lenses review, and the prompt rules agents get, through stub agents; no claude call.
// Usage: node test_simplify.mjs
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor
const body = readFileSync(new URL('build-issue-loop.js', import.meta.url), 'utf8').replace(/^export /m, '')
const args = { issue: '1', branch: 'issue-1', base: 'abc1234', gateCommands: ['true'] }

// Every other reviewer passes, so the run ends after Review or its fix rounds.
// gateFails: gate runs that fail before one passes.
// externalRuns: the external reviewer's replies, the first to its review, the rest to its re-reviews and full-review retries, in call order.
// domainRuns: the same for the domain reviewer, fix-diff reviews included, which passes once they run out. fixes: fix-round replies, then defaults.
// status: the gate's `git status --porcelain` lines; the nth gate run reports head gate<n>. nullOnce: labels whose next call returns null, once per listing.
// throwFor: agent types whose dispatch throws.
async function run(review, cuts, { aspects = ['code'], gateFails = 0, externalReview, externalRuns = [], domainRuns = [], fixes = [], redEvidence = '', status = [], nullOnce = [], throwFor = [] } = {}) {
  const labels = []
  const prompts = {}
  const types = {}
  const schemas = {}
  const nulls = [...nullOnce]
  let gateRuns = 0
  async function agent(prompt, opts) {
    if (throwFor.includes(opts.agentType)) throw new Error('agent dispatch failed')
    if (nulls.includes(opts.label)) { nulls.splice(nulls.indexOf(opts.label), 1); return null }
    const reply = await stub(prompt, opts)
    return reply && { ...reply, friction: ['stub friction'] }
  }
  async function stub(prompt, opts) {
    labels.push(opts.label)
    prompts[opts.label] = prompt
    types[opts.label] = opts.agentType
    schemas[opts.label] = opts.schema
    if (opts.phase === 'Implement') return { committed: true, summary: '', redEvidence }
    if (opts.label.startsWith('build-fix:')) return { committed: true, summary: '' }
    if (opts.phase === 'Gate') return { passed: gateFails-- <= 0, summary: '', changedFiles: [], status, aspects, head: `gate${++gateRuns}` }
    if (opts.label.startsWith('simplify:')) return review
    if (opts.label.startsWith('simplify-fix:')) return cuts
    if (/^(re-)?review:external/.test(opts.label)) return externalRuns.shift()
    if (/^((re-)?review|fixdiff):domain/.test(opts.label) && domainRuns.length) return domainRuns.shift()
    if (opts.label.startsWith('fix:')) return fixes.shift() || { committed: true, addressed: ['external'], disputed: [], summary: '' }
    if (opts.phase === 'Review' || opts.label.startsWith('fixdiff:')) return { summary: '', findings: [] }
    throw new Error(`unexpected agent ${opts.label}`)
  }
  const result = await new AsyncFunction('args', 'agent', 'phase', 'log', 'parallel', body)(
    { ...args, externalReview }, agent, () => {}, () => {}, (fns) => Promise.all(fns.map((f) => f())))
  assert.ok(!JSON.stringify(result).includes('stub friction'), 'friction stays out of the result')
  return { result, labels, prompts, types, schemas }
}

const cut = (tag) => ({ tag, location: 'latency.py:L3', cut: `${tag} cut`, replacement: 'statistics.median' })
const loaded = (findings, net) => ({ skillLoaded: true, findings, net })
const dispute = { finding: 'delete cut', reason: 'main() calls it' }

const verdict = (...findings) => ({ summary: '', findings })
const leanSimplify = { net: 0, applied: [], disputed: [], unhandled: 0 }
const pre = { severity: 'important', description: 'shutdown leaks the lock', file: 'lock.js', preExisting: true }
const worsened = { severity: 'important', description: 'the new retry loop now reaches the unguarded close', file: 'lock.js', preExisting: false }
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
  { name: 'fix stage failure carries pre-existing findings', review: loaded([], 0),
    opts: { domainRuns: [{ summary: '', findings: [worsened, pre] }], fixes: [{ committed: false, addressed: [], disputed: [], summary: 'no-op' }] },
    ok: false, stage: 'fix', fixRan: false, preExisting: [{ ...pre, gate: 'domain' }] },
  { name: 'gate failure after a degraded reviewer', review: loaded([], 0),
    opts: { throwFor: ['dream-team:sre-engineer'], domainRuns: [verdict(worsened)], nullOnce: ['gate:#1:fix1', 'gate:#1:fix1'] },
    ok: false, stage: 'gate', fixRan: false, degraded: ['dream-team:sre-engineer'] },
]

for (const row of rows) {
  const { result, labels } = await run(row.review, row.cuts, row.opts)
  assert.equal(result.ok, row.ok, row.name)
  assert.equal(labels.some((l) => l.startsWith('simplify-fix:')), row.fixRan, `${row.name}: simplify-fix dispatched`)
  assert.deepEqual(result.degraded, row.degraded || [], `${row.name}: degraded`)
  assert.deepEqual(result.untrackedPaths, row.untracked || [], `${row.name}: untrackedPaths`)
  if (row.ok) {
    assert.deepEqual(result.simplify, row.simplify, row.name)
  } else {
    assert.equal(result.stage, row.stage, row.name)
    if (row.preExisting) assert.deepEqual(result.preExisting, row.preExisting, `${row.name}: preExisting`)
  }
  console.log(`PASS ${row.name}`)
}

const lean = loaded([], 0)

const doneWhenCheck = 'The issue\'s `## Done when` section, or on an older issue its `Done when …` paragraph, must hold on this branch'
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
const preexisting = 'An edit that repairs a defect already present on the base commit, one no branch commit caused, is one plain commit in the repo\'s commit convention'
const red = '--- FAIL: TestRotateKeepsN (0.00s)\n    rotate_test.go:41: kept 4 files, want 5'
const extOnce = () => ({ externalReview: cmd, externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, { summary: '', findings: [], resolved: [extFinding] }] })
// The fixer disputes, its re-review dies once, then answers; a second fixer call changes nothing and fails the run.
const deadDispute = () => ({ externalReview: cmd, externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, undefined, undefined, { summary: '', findings: [], resolved: [] }],
  fixes: [{ committed: false, addressed: [], disputed: [dispute], summary: '' }, { committed: false, addressed: [], disputed: [], summary: '' }] })
// Domain passes, then its fix-diff review raises a blocking finding and a nit; its round-2 re-review resolves the finding.
const fixDiffBlocks = () => ({ externalReview: cmd, externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, { summary: '', findings: [], resolved: [extFinding] }],
  domainRuns: [{ summary: '', findings: [] }, { summary: '', findings: [{ ...extFinding, file: 'main.js' }, { severity: 'nit', description: 'rename n', file: 'main.js' }] },
    { summary: '', findings: [], resolved: [{ ...extFinding, file: 'main.js' }] }] })
const promptRows = [
  { name: 'implementer stops at the Done-when checks', label: 'impl:#1', rule: 'stop once each of its checks holds and every gate command is green' },
  { name: 'implementer splits only independent changes', label: 'impl:#1', rule: 'commit each change separately under its own subject' },
  { name: 'gate is read-only and lists its allowed commands', label: 'gate:#1', rule: 'The gate is read-only. Run only the commands written below — `git status`, the gate commands, `git diff`, `git rev-parse` and any aspects pipeline — each once, in order.' },
  { name: 'build-fix commits fixups', label: 'build-fix:#1:r1', rule: fixup, opts: { gateFails: 1 } },
  { name: 'build-fix commits a pre-existing defect plainly', label: 'build-fix:#1:r1', rule: preexisting, opts: { gateFails: 1 } },
  { name: 'simplify-fix commits fixups', label: 'simplify-fix:#1', rule: fixup, schemaNits: false, review: loaded([cut('stdlib')], 4),
    cuts: { committed: true, addressed: ['stdlib cut'], disputed: [], summary: '' } },
  { name: 'fix round commits fixups', label: 'fix:#1:r1', rule: fixup, opts: { externalReview: cmd, externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, { summary: '', findings: [], resolved: [extFinding] }] } },
  { name: 'test lens checks red evidence', label: 'review:dream-team:test-coverage-reviewer', rule: red, opts: { redEvidence: red } },
  { name: 'domain lens skips without a source', label: 'review:domain', rule: 'Either one missing → raise no finding on it and say why in your summary' },
  { name: 'domain lens checks each Done-when bullet', label: 'review:domain', rule: 'check each of its checks on its own by reading, cite what you read, and say in your summary whether each one holds' },
  { name: 'domain lens cites its source', label: 'review:domain', rule: 'cite what you read — file and line' },
  { name: 'retry after a null result checks earlier commits', label: 'impl:#1', rule: 'may already have committed part of it', opts: { nullOnce: ['impl:#1'] } },
  { name: 'lens may rate a question', label: 'review:dream-team:architect-reviewer', rule: 'as question: it goes to the user and never blocks the MR' },
  { name: 'lens marks only a defect the change leaves alone as pre-existing', label: 'review:dream-team:architect-reviewer', rule: 'the change neither introduces, newly reaches nor worsens it', preExistingIn: 'findings' },
  { name: 'lens rates a defect the change worsens like any other', label: 'review:dream-team:architect-reviewer', rule: 'is a normal finding, rated and blocking like any other' },
  { name: 'external reviewer may mark a finding pre-existing', label: 'review:external', rule: 'the change neither introduces, newly reaches nor worsens it', opts: extOnce(), preExistingIn: 'findings' },
  { name: 'fix-diff review raises a defect the fix newly reaches', label: 'fixdiff:dream-team:sre-engineer:r1', rule: 'or on a defect it newly reaches or worsens', opts: extOnce(), preExistingIn: 'findings' },
  { name: 're-review raises a defect the fix newly reaches', label: 're-review:external:r1', rule: 'or on a defect it newly reaches or worsens', opts: extOnce(), preExistingIn: 'added' },
  { name: 'lens reads the diff through git', label: 'review:dream-team:sre-engineer', rule: '`git diff abc1234..HEAD`' },
  { name: 'domain lens reads the diff through git', label: 'review:domain', rule: '`git diff abc1234..HEAD`' },
  { name: 'dead re-review is retried against the fix it missed', label: 're-review:external:r2', rule: `Disputed: ${dispute.finding}`, opts: deadDispute() },
  { name: 'nit fixer fixes only cheap nits', label: 'fix:#1:nits', rule: 'Fix each one that is cheap', schemaNits: false, opts: { domainRuns: [{ summary: '', findings: [{ severity: 'nit', description: 'rename n', file: 'a.js' }] }] } },
  { name: 'fix round carries the nits', label: 'fix:#1:r1', rule: 'Reviewers also raised these nits', schemaNits: true, opts: { externalReview: cmd,
    externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, { summary: '', findings: [], resolved: [extFinding] }],
    domainRuns: [{ summary: '', findings: [{ severity: 'nit', description: 'rename n', file: 'a.js' }] }] } },
  { name: 're-review reads the fix diff', label: 're-review:external:r1', rule: '`git diff gate1..HEAD`', opts: extOnce() },
  { name: 'passed reviewer reviews the fix diff', label: 'fixdiff:dream-team:sre-engineer:r1', rule: '`git diff gate1..HEAD`', opts: extOnce() },
  { name: 'fix-diff nit joins the next fix round', label: 'fix:#1:r2', rule: 'rename n', opts: fixDiffBlocks() },
  { name: 're-review reads the diff through git', label: 're-review:external:r1', rule: '`git diff abc1234..HEAD`', opts: extOnce() },
  { name: 'round-2 fix diff starts at the round-1 fix', label: 'fixdiff:external:r2', rule: '`git diff gate2..HEAD`', opts: fixDiffBlocks() },
  { name: 'round-2 re-review reads the round-2 fix diff', label: 're-review:domain:r2', rule: '`git diff gate2..HEAD`', opts: fixDiffBlocks() },
  { name: 'dead re-review reads the fix it missed', label: 're-review:external:r2', rule: '`git diff gate1..HEAD`', opts: deadDispute() },
  { name: 're-review\'s fix-diff nit joins the nit pass', label: 'fix:#1:nits', rule: 'rename n', opts: {
    domainRuns: [{ summary: '', findings: [{ ...extFinding, file: 'main.js' }] },
      { summary: '', findings: [], resolved: [{ ...extFinding, file: 'main.js' }], added: [{ severity: 'nit', description: 'rename n', file: 'main.js' }] }] } },
]

for (const row of promptRows) {
  const { result, prompts, schemas } = await run(row.review || lean, row.cuts, row.opts)
  assert.equal(result.ok, true, row.name)
  assert.ok(prompts[row.label].includes(row.rule), row.name)
  if ('schemaNits' in row) assert.equal('nits' in schemas[row.label].properties, row.schemaNits, `${row.name}: nits in schema`)
  if (row.preExistingIn) assert.ok('preExisting' in schemas[row.label].properties[row.preExistingIn].items.properties, `${row.name}: preExisting in schema`)
  console.log(`PASS ${row.name}`)
}

const question = { severity: 'question', description: 'should a timeout count as a retry?', file: 'retry.js' }
const nit = { severity: 'nit', description: 'rename n to retries', file: 'retry.js' }
const nitFixed = { committed: true, addressed: [nit.description], disputed: [], summary: '' }
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
  { name: 'reviewer question returned, not fixed', opts: { domainRuns: [verdict(question)] },
    reviewer: false, agents: 0, degraded: [], fixRounds: 0, resolved: [], prompts: [], questions: [{ ...question, gate: 'domain' }] },
  { name: 'nit fixed once after review, not re-reviewed', opts: { domainRuns: [{ summary: '', findings: [nit] }], fixes: [nitFixed] },
    reviewer: false, agents: 0, degraded: [], fixRounds: 0, resolved: [], prompts: [], nitFix: { addressed: [nit.description], disputed: [] },
    labels: ['fix:#1:nits', 'gate:#1:nits'] },
  { name: 'nit rides along with the first fix round, no separate pass',
    opts: { externalReview: cmd, externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, { summary: '', findings: [], resolved: [extFinding] }],
      domainRuns: [{ summary: '', findings: [nit] }], fixes: [{ ...nitFixed, addressed: ['external'], nits: { addressed: [nit.description], disputed: [] } }] },
    reviewer: true, agents: 2, degraded: [], fixRounds: 1, resolved: [{ ...extFinding, gate: 'external', round: 1 }], prompts: ['review:external'],
    nitFix: { addressed: [nit.description], disputed: [] } },
  { name: 'passed reviewer\'s fix-diff finding blocks the next round',
    opts: fixDiffBlocks(),
    reviewer: true, agents: 3, degraded: [], fixRounds: 2, prompts: ['review:external'],
    resolved: [{ ...extFinding, gate: 'external', round: 1 }, { ...extFinding, file: 'main.js', gate: 'domain', round: 2 }],
    nitFix: { addressed: [], disputed: [] }, fixdiff: ['fixdiff:domain:r1', 'fixdiff:external:r2'] },
  { name: 'dead fix-diff review keeps the gate\'s pass', opts: { ...extOnce(), nullOnce: ['fixdiff:domain:r1'] },
    reviewer: true, agents: 2, degraded: [], fixRounds: 1, resolved: [{ ...extFinding, gate: 'external', round: 1 }], prompts: ['review:external'] },
  { name: 'pre-existing finding returned without a fix round', opts: { domainRuns: [verdict(pre)] },
    reviewer: false, agents: 0, degraded: [], fixRounds: 0, resolved: [], prompts: [], preExisting: [{ ...pre, gate: 'domain' }] },
  { name: 'pre-existing nit and question reach neither the nit fixer nor questions',
    opts: { domainRuns: [verdict({ ...nit, preExisting: true }, { ...question, preExisting: true })] },
    reviewer: false, agents: 0, degraded: [], fixRounds: 0, resolved: [], prompts: [],
    preExisting: [{ ...nit, preExisting: true, gate: 'domain' }, { ...question, preExisting: true, gate: 'domain' }] },
  { name: 'pre-existing finding survives the re-review that replaces its gate',
    opts: { domainRuns: [verdict(worsened, pre), { summary: '', findings: [], resolved: [worsened] }] },
    reviewer: false, agents: 0, degraded: [], fixRounds: 1, resolved: [{ ...worsened, gate: 'domain', round: 1 }], prompts: [], preExisting: [{ ...pre, gate: 'domain' }] },
  { name: 'Done-when report survives the re-review that replaces its gate',
    opts: { domainRuns: [{ summary: 'bullet 1 holds', findings: [worsened] }, { summary: 'fixed', findings: [], resolved: [worsened] }] },
    reviewer: false, agents: 0, degraded: [], fixRounds: 1, resolved: [{ ...worsened, gate: 'domain', round: 1 }], prompts: [], doneWhen: 'bullet 1 holds' },
  { name: 'pre-existing finding added on a re-review is returned, not fixed',
    opts: { domainRuns: [verdict(worsened), { summary: '', findings: [], resolved: [worsened], added: [pre] }] },
    reviewer: false, agents: 0, degraded: [], fixRounds: 1, resolved: [{ ...worsened, gate: 'domain', round: 1 }], prompts: [], preExisting: [{ ...pre, gate: 'domain' }] },
  { name: 'prior finding a re-review re-marks pre-existing is returned, not lost',
    opts: { domainRuns: [verdict(worsened), { summary: '', findings: [pre], resolved: [] }] },
    reviewer: false, agents: 0, degraded: [], fixRounds: 1, resolved: [], prompts: [], preExisting: [{ ...pre, gate: 'domain' }] },
  { name: 'pre-existing finding from a fix-diff review is returned, not fixed', opts: { ...extOnce(), domainRuns: [verdict(), verdict(pre)] },
    reviewer: true, agents: 2, degraded: [], fixRounds: 1, resolved: [{ ...extFinding, gate: 'external', round: 1 }], prompts: ['review:external'], preExisting: [{ ...pre, gate: 'domain' }] },
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
  assert.deepEqual(result.questions, row.questions || [], `${row.name}: questions`)
  assert.deepEqual(result.preExisting, row.preExisting || [], `${row.name}: preExisting`)
  for (const f of row.preExisting || []) assert.ok(!Object.keys(prompts).some((l) => /^(fix|re-review):/.test(l) && prompts[l].includes(f.description)), `${row.name}: pre-existing finding kept out of the fix loop`)
  assert.deepEqual(result.nitFix, row.nitFix || null, `${row.name}: nitFix`)
  assert.equal(result.doneWhen, row.doneWhen || '', `${row.name}: doneWhen`)
  assert.deepEqual(labels.filter((l) => l.endsWith(':nits')), row.labels || [], `${row.name}: nit pass`)
  assert.ok(!labels.some((l) => l.startsWith('re-review:')) || row.fixRounds, `${row.name}: no re-review`)
  if (row.fixdiff) assert.deepEqual(labels.filter((l) => /^fixdiff:(domain|external)/.test(l)), row.fixdiff, `${row.name}: fix-diff reviews`)
  console.log(`PASS ${row.name}`)
}

const stuck = { summary: '', findings: [extFinding], resolved: [] }
const handBackRows = [
  { name: 'hand-back carries untracked paths', opts: { status: ['?? coverage.out'], externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, stuck, stuck, stuck] },
    untracked: ['coverage.out'], dead: [] },
  { name: 'dead re-review keeps its findings and is re-reviewed', opts: { externalRuns: [{ ran: true, summary: '', findings: [extFinding] }] },
    untracked: [], dead: ['external'] },
  { name: 'held dispute hands back', opts: { externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, stuck],
    domainRuns: [verdict(question, pre)], fixes: [{ committed: false, addressed: [], disputed: [dispute], summary: '' }] }, untracked: [], dead: [],
    questions: [{ ...question, gate: 'domain' }], preExisting: [{ ...pre, gate: 'domain' }] },
]

for (const row of handBackRows) {
  const { result, labels } = await run(lean, undefined, { externalReview: cmd, ...row.opts })
  assert.equal(result.handBack, true, row.name)
  assert.deepEqual(result.blocking, [{ ...extFinding, gate: 'external' }], `${row.name}: blocking`)
  assert.deepEqual(result.deadReviewers, row.dead, `${row.name}: deadReviewers`)
  assert.deepEqual(result.untrackedPaths, row.untracked, `${row.name}: untrackedPaths`)
  assert.deepEqual(result.questions, row.questions || [], `${row.name}: questions`)
  assert.deepEqual(result.preExisting, row.preExisting || [], `${row.name}: preExisting`)
  assert.ok(!labels.some((l) => l.startsWith('review:external:retry')), `${row.name}: no full-review retry`)
  console.log(`PASS ${row.name}`)
}
