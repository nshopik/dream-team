// What build-issue-loop does with each Simplify review and externalReview arg, which lenses review, and the prompt rules agents get, and how assemble-meta-loop runs it per child, through stub agents; no claude call.
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
// throwFor: agent types whose dispatch throws. extra: more loop args.
async function run(review, cuts, { aspects = ['code'], gateFails = 0, externalReview, externalRuns = [], domainRuns = [], fixes = [], redEvidence = '', implement = { committed: true, summary: '' }, status = [], nullOnce = [], throwFor = [], extra = {} } = {}) {
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
    if (opts.phase === 'Implement') return { ...implement, redEvidence }
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
    { ...args, externalReview, ...extra }, agent, () => {}, () => {}, (fns) => Promise.all(fns.map((f) => f())))
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
  { name: 'implementer stops on a failing check', review: loaded([], 0), opts: { implement: { committed: false, summary: 'test fails: p99 412ms' } },
    ok: false, stage: 'implement', reason: 'test fails: p99 412ms', fixRan: false },
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
    if (row.reason) assert.equal(result.reason, row.reason, `${row.name}: reason`)
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
  { name: 'implementer stops when the issue says to', label: 'impl:#1', rule: 'overrides the rule to get every gate command green' },
  { name: 'implementer stops before reversing a recorded decision', label: 'impl:#1', rule: 'reverses a decision an earlier commit body on the branch records is not an assumption' },
  { name: 'gate is read-only and lists its allowed commands', label: 'gate:#1', rule: 'The gate is read-only. Run only the commands written below — `git status`, the gate commands, `git diff`, `git rev-parse` and any aspects pipeline — each once, in order.' },
  { name: 'build-fix commits fixups', label: 'build-fix:#1:r1', rule: fixup, opts: { gateFails: 1 } },
  { name: 'build-fix commits a pre-existing defect plainly', label: 'build-fix:#1:r1', rule: preexisting, opts: { gateFails: 1 } },
  { name: 'simplify-fix commits fixups', label: 'simplify-fix:#1', rule: fixup, schemaNits: false, review: loaded([cut('stdlib')], 4),
    cuts: { committed: true, addressed: ['stdlib cut'], disputed: [], summary: '' } },
  { name: 'fix round commits fixups', label: 'fix:#1:r1', rule: fixup, opts: { externalReview: cmd, externalRuns: [{ ran: true, summary: '', findings: [extFinding] }, { summary: '', findings: [], resolved: [extFinding] }] } },
  { name: 'test lens checks red evidence', label: 'review:dream-team:test-coverage-reviewer', rule: red, opts: { redEvidence: red } },
  { name: 'startAtSimplify test lens checks the red evidence it is given', label: 'review:dream-team:test-coverage-reviewer', rule: red, opts: { extra: { startAtSimplify: true, redEvidence: red } } },
  { name: 'domain lens skips without a source', label: 'review:domain', rule: 'Either one missing → raise no finding on it and say why in your summary' },
  { name: 'domain lens reads the source from CLAUDE.md or AGENTS.md', label: 'review:domain', rule: 'invariant this project\'s CLAUDE.md or AGENTS.md names' },
  { name: 'domain lens checks each Done-when bullet', label: 'review:domain', rule: 'check each of its checks on its own by reading, cite what you read, and say in your summary whether each one holds' },
  { name: 'domain lens cites its source', label: 'review:domain', rule: 'cite what you read — file and line' },
  { name: 'retry after a null result checks earlier commits', label: 'impl:#1', rule: 'may already have committed part of it', opts: { nullOnce: ['impl:#1'] } },
  { name: 'lens may rate a question', label: 'review:dream-team:architect-reviewer', rule: 'as question: it goes to the user unless a re-review answers it, and never blocks the MR' },
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
  { name: 're-review numbers its prior findings', label: 're-review:domain:r1', rule: '2. [question] should a timeout count as a retry?', preExistingIn: 'resolved',
    opts: { domainRuns: [verdict({ severity: 'question', description: 'should a timeout count as a retry?' }, worsened), { summary: '', findings: [], resolved: [{ ...worsened, finding: 1 }] }] } },
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
  if (row.preExistingIn) {
    const item = schemas[row.label].properties[row.preExistingIn].items.properties
    assert.ok('preExisting' in item, `${row.name}: preExisting in schema`)
    assert.equal(item.file.description, 'repo-relative path, e.g. src/main.rs', `${row.name}: file is repo-relative`)
    if (row.preExistingIn === 'resolved') assert.ok(schemas[row.label].properties.resolved.items.required.includes('finding'), `${row.name}: finding required`)
  }
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
  { name: 'question a re-review resolves leaves questions for resolved',
    opts: { domainRuns: [verdict(pre, question, worsened), { summary: '', findings: [], resolved: [{ ...worsened, finding: 1 }, { ...question, finding: 2 }] }] },
    reviewer: false, agents: 0, degraded: [], fixRounds: 1, prompts: [], preExisting: [{ ...pre, gate: 'domain' }],
    resolved: [{ ...worsened, gate: 'domain', round: 1 }, { ...question, gate: 'domain', round: 1 }] },
  { name: 'question reworded in round 1 and resolved in round 2 leaves questions',
    opts: { domainRuns: [verdict(worsened, question), { summary: '', findings: [worsened, { ...question, description: 'does a timeout count as a retry?' }], resolved: [] },
      { summary: '', findings: [], resolved: [{ ...worsened, finding: 1 }, { ...question, finding: 2 }] }] },
    reviewer: false, agents: 0, degraded: [], fixRounds: 2, prompts: [],
    resolved: [{ ...worsened, gate: 'domain', round: 2 }, { ...question, gate: 'domain', round: 2 }] },
  { name: 'question added on a re-review and resolved in the next leaves questions',
    opts: { domainRuns: [verdict(worsened), { summary: '', findings: [worsened], resolved: [], added: [question] },
      { summary: '', findings: [], resolved: [{ ...worsened, finding: 1 }, { ...question, finding: 2 }] }] },
    reviewer: false, agents: 0, degraded: [], fixRounds: 2, prompts: [],
    resolved: [{ ...worsened, gate: 'domain', round: 2 }, { ...question, gate: 'domain', round: 2 }] },
  { name: 'question one reviewer resolves stays for the other that asked it',
    opts: { externalReview: cmd, externalRuns: [{ ran: true, summary: '', findings: [question] }],
      domainRuns: [verdict(worsened, question), { summary: '', findings: [], resolved: [{ ...worsened, finding: 1 }, { ...question, finding: 2 }] }] },
    reviewer: true, agents: 2, degraded: [], fixRounds: 1, prompts: ['review:external'],
    resolved: [{ ...worsened, gate: 'domain', round: 1 }, { ...question, gate: 'domain', round: 1 }], questions: [{ ...question, gate: 'external' }] },
  { name: 'question a re-review neither resolves nor repeats stays in questions',
    opts: { domainRuns: [verdict(worsened, question), { summary: '', findings: [], resolved: [{ ...worsened, finding: 1 }] }] },
    reviewer: false, agents: 0, degraded: [], fixRounds: 1, prompts: [],
    resolved: [{ ...worsened, gate: 'domain', round: 1 }], questions: [{ ...question, gate: 'domain' }] },
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

const loopArgRows = [
  { name: 'stopAfterGate ends the run after the gate', extra: { stopAfterGate: true },
    labels: ['impl:#1', 'gate:#1'], head: 'gate1' },
  { name: 'startAtSimplify skips the implementer', extra: { startAtSimplify: true },
    labels: ['gate:#1', 'simplify:#1', ...lensLabels, 'review:domain'] },
]

for (const row of loopArgRows) {
  const { result, labels } = await run(lean, undefined, { extra: row.extra })
  assert.equal(result.ok, true, row.name)
  assert.deepEqual(labels, row.labels, `${row.name}: agents`)
  assert.equal(result.head, row.head, `${row.name}: head`)
  console.log(`PASS ${row.name}`)
}

{
  const name = 'worktree arg reaches every agent prompt'
  const wt = 'cd /wt/1 &&'
  const every = (extra) => run(loaded([cut('stdlib')], 4), { committed: true, addressed: ['stdlib cut'], disputed: [], summary: '' }, { ...fixDiffBlocks(), gateFails: 1, extra })
  const plain = await every({})
  const { result, prompts } = await every({ worktree: '/wt/1' })
  assert.equal(result.ok, true, name)
  for (const kind of ['impl', 'gate', 'build-fix', 'simplify', 'simplify-fix', 'review', 're-review', 'fixdiff', 'fix']) {
    assert.ok(Object.keys(prompts).some((l) => l.startsWith(`${kind}:`)), `${name}: ${kind} ran`)
  }
  for (const [l, p] of Object.entries(prompts)) assert.ok(p.includes(wt), `${name}: ${l}`)
  assert.ok(!Object.values(plain.prompts).some((p) => p.includes('worktree')), `${name}: no worktree without the arg`)
  console.log(`PASS ${name}`)
}

const metaBody = readFileSync(new URL('assemble-meta-loop.js', import.meta.url), 'utf8').replace(/^export /m, '')
const metaArgs = { meta: { issue: '10', title: 'Meta: rotation', body: 'meta body' }, branch: 'issue-10-rotation', base: 'base0', worktree: '/home/First Last/repo/.claude/worktrees/issue-10-rotation', gateCommands: ['npm test --gate-x'] }
const child = (issue, blockedBy = [], extra = {}) => ({ issue, title: `child ${issue}`, body: `body ${issue}`, blockedBy, ...extra })

// fail: child issues whose loop run fails; conflicts: per child, how many of its landings conflict; slow: per child, its loop's delay in ms.
// stale: per child, how many of its merges leave the tip behind; badWorktree: children whose worktree agent reports the wrong head.
// untracked: per child, the untrackedPaths its run returns.
// reviewFail: the review run fails; red: per child, the redEvidence its run returns; extra: more args.
// events: loop starts and ends and landings in time order; ontos: each landing's rebase target, in landing order.
async function runMeta(children, { fail = [], conflicts = {}, stale = {}, badWorktree = [], untracked = {}, slow = {}, reviewFail = false, red = {}, extra = {} } = {}) {
  const calls = []
  const events = []
  const ontos = []
  const removes = []
  const prompts = {}
  let running = 0
  let maxRunning = 0
  let landing = 0
  let maxLanding = 0
  let tip = metaArgs.base
  async function workflow(name, a) {
    calls.push({ name, ...a })
    if (a.startAtSimplify) return reviewFail ? { ok: false, stage: 'review', issue: a.issue } : { ok: true, issue: a.issue }
    events.push(`start ${a.issue}`)
    maxRunning = Math.max(maxRunning, ++running)
    await new Promise((r) => setTimeout(r, slow[a.issue] || 1))
    running--
    events.push(`end ${a.issue}`)
    const untrackedPaths = untracked[a.issue] || []
    if (fail.includes(a.issue)) return { ok: false, stage: 'gate', reason: 'red', untrackedPaths }
    return { ok: true, issue: a.issue, head: `head${a.issue}`, redEvidence: red[a.issue] || '', untrackedPaths }
  }
  async function agent(prompt, opts) {
    const issue = opts.label.match(/#(\d+)/)[1]
    prompts[opts.label] = prompt
    if (opts.label.startsWith('worktree:')) return { path: `/wt/${issue}`, head: badWorktree.includes(issue) ? 'other' : prompt.match(/worktree add .* (\S+)`/)[1] }
    if (opts.label.startsWith('remove:')) return removes.push(opts.label) && ''
    maxLanding = Math.max(maxLanding, ++landing)
    await new Promise((r) => setTimeout(r, 5))
    landing--
    ontos.push(prompt.match(/`git rebase (\S+)`/)[1])
    if (conflicts[issue] > 0) {
      conflicts[issue]--
      return { landed: false, gated: '', head: '', reason: 'conflict in main.js' }
    }
    if (stale[issue] > 0) {
      stale[issue]--
      return { landed: true, gated: `land${issue}`, head: tip, reason: '' }
    }
    events.push(`land ${issue}`)
    tip = `land${issue}`
    return { landed: true, gated: tip, head: tip, reason: '' }
  }
  const result = await new AsyncFunction('args', 'agent', 'workflow', 'phase', 'log', metaBody)(
    { ...metaArgs, ...extra, children }, agent, workflow, () => {}, () => {})
  return { result, calls, events, ontos, removes, prompts, maxRunning, maxLanding }
}

const before = (events, a, b) => events.indexOf(a) >= 0 && events.indexOf(a) < events.indexOf(b)
const metaRows = [
  { name: 'meta: blocked child starts after its blocker lands, two at once', children: [child('13', ['11']), child('12', [], { notes: 'keep 5' }), child('11')],
    opts: { extra: { externalReview: 'ext-cmd', notes: 'shared' }, red: { 11: 'FAIL a', 13: 'FAIL c' } },
    order: ['11', '12', '13'], bases: ['base0', 'base0', 'land11'], ontos: ['base0', 'land11', 'land12'], ok: true, done: ['11', '12', '13'], failed: [], skipped: [],
    together: ['11', '12'], after: [['land 11', 'start 13']], reviewBody: ['#11', '#12', '#13'],
    kidNotes: { 11: 'shared', 12: 'shared\nkeep 5' }, reviewNotes: 'shared\n#12: keep 5', externalReview: 'ext-cmd', redEvidence: '#11: FAIL a\n#13: FAIL c' },
  { name: 'meta: three independent children, no more than two at once', children: [child('11'), child('12'), child('13')],
    order: ['11', '12', '13'], bases: ['base0', 'base0', 'land11'], ontos: ['base0', 'land11', 'land12'], ok: true, done: ['11', '12', '13'], failed: [], skipped: [],
    together: ['11', '12'], after: [['end 11', 'start 13']], reviewBody: ['#11', '#12', '#13'] },
  { name: 'meta: children land in finish order', children: [child('11'), child('12')], opts: { slow: { 11: 20 } },
    order: ['11', '12'], bases: ['base0', 'base0'], ontos: ['base0', 'land12'], ok: true, done: ['12', '11'], failed: [], skipped: [],
    together: ['11', '12'], reviewBody: ['#11', '#12'] },
  { name: 'meta: older child blocked by a newer one waits for it', children: [child('11', ['12']), child('12')],
    order: ['12', '11'], bases: ['base0', 'land12'], ontos: ['base0', 'land12'], ok: true, done: ['12', '11'], failed: [], skipped: [],
    after: [['land 12', 'start 11']], reviewBody: ['#11', '#12'] },
  { name: 'meta: failed review fails the run', children: [child('11')], opts: { reviewFail: true },
    order: ['11'], bases: ['base0'], ontos: ['base0'], ok: false, reviewStage: 'review', done: ['11'], failed: [], skipped: [], reviewBody: ['#11'] },
  { name: 'meta: failed child drops its branch and its dependents are skipped', children: [child('11'), child('12', ['11']), child('13')], opts: { fail: ['11'] },
    order: ['11', '13'], bases: ['base0', 'base0'], ontos: ['base0'], ok: true, done: ['13'], failed: ['11'], skipped: ['12'], reviewBody: ['#13'] },
  { name: 'meta: blocker outside the children does not hold a child', children: [child('12', ['5'])],
    order: ['12'], bases: ['base0'], ontos: ['base0'], ok: true, done: ['12'], failed: [], skipped: [], reviewBody: ['#12'] },
  { name: 'meta: no child passes, no review', children: [child('11'), child('12', ['11'])], opts: { fail: ['11'] },
    order: ['11'], bases: ['base0'], ontos: [], ok: false, done: [], failed: ['11'], skipped: ['12'] },
  { name: 'meta: landing conflict reruns the child once from the new tip', children: [child('11'), child('12')], opts: { conflicts: { 12: 1 } },
    order: ['11', '12', '12'], bases: ['base0', 'base0', 'land11'], ontos: ['base0', 'land11', 'land11'], ok: true, done: ['11', '12'], failed: [], skipped: [],
    reviewBody: ['#11', '#12'], removes: ['remove:#11', 'remove:#12', 'remove:#12:rerun'] },
  { name: 'meta: second landing failure fails the child and skips its dependents', children: [child('11'), child('12'), child('13', ['12'])], opts: { conflicts: { 12: 2 } },
    order: ['11', '12', '12'], bases: ['base0', 'base0', 'land11'], ontos: ['base0', 'land11', 'land11'], ok: true, done: ['11'], failed: ['12'], failedStage: 'land', skipped: ['13'],
    reviewBody: ['#11'], removes: ['remove:#11', 'remove:#12', 'remove:#12:rerun'] },
  { name: 'meta: a merge that leaves the tip behind is a failed landing', children: [child('11'), child('12')], opts: { stale: { 12: 1 } },
    order: ['11', '12', '12'], bases: ['base0', 'base0', 'land11'], ontos: ['base0', 'land11', 'land11'], ok: true, done: ['11', '12'], failed: [], skipped: [],
    reviewBody: ['#11', '#12'], removes: ['remove:#11', 'remove:#12', 'remove:#12:rerun'] },
  { name: 'meta: a worktree on the wrong head fails the child before its loop', children: [child('11'), child('12', ['11'])], opts: { badWorktree: ['11'] },
    order: [], bases: [], ontos: [], ok: false, done: [], failed: ['11'], failedStage: 'worktree', skipped: ['12'], removes: [] },
  { name: 'meta: a child with untracked files keeps its worktree', children: [child('11'), child('12')], opts: { untracked: { 11: ['coverage.out'] }, fail: ['12'] },
    order: ['11', '12'], bases: ['base0', 'base0'], ontos: ['base0'], ok: true, done: ['11'], failed: ['12'], skipped: [],
    reviewBody: ['#11'], removes: ['remove:#12'], kept: { 11: '/wt/11' } },
]

for (const row of metaRows) {
  const { result, calls, events, ontos, removes, prompts, maxRunning, maxLanding } = await runMeta(row.children, row.opts)
  const kids = calls.filter((c) => c.stopAfterGate)
  const reviews = calls.filter((c) => c.startAtSimplify)
  assert.ok(calls.every((c) => c.name === 'dream-team:build-issue-loop'), `${row.name}: loop`)
  assert.ok(kids.every((c) => c.branch === `${metaArgs.branch}-${c.issue}` && c.worktree === `/wt/${c.issue}`), `${row.name}: child branch and worktree`)
  assert.ok(maxRunning <= 2, `${row.name}: at most two children at once`)
  assert.ok(maxLanding <= 1, `${row.name}: one landing at a time`)
  for (const [l, p] of Object.entries(prompts)) {
    const issue = l.match(/#(\d+)/)[1]
    const kind = l.split(':')[0]
    if (kind === 'land') assert.ok(metaArgs.gateCommands.every((g) => p.includes(g)) && p.includes(`git -C "${metaArgs.worktree}" merge --ff-only ${metaArgs.branch}-${issue}`), `${row.name}: ${l} re-gates and fast-forwards the integration worktree`)
    if (kind === 'remove') assert.ok(p.includes(`git -C "${metaArgs.worktree}" branch -D ${metaArgs.branch}-${issue}`), `${row.name}: ${l} drops the branch`)
    assert.ok(!p.includes('the checkout you start in'), `${row.name}: ${l} names no start directory`)
    if (kind !== 'land') assert.ok(p.includes(`git -C "${metaArgs.worktree}" worktree`), `${row.name}: ${l} runs git in the integration worktree`)
  }
  for (const [i, c] of kids.entries()) {
    const tag = kids.slice(0, i).some((k) => k.issue === c.issue) ? ':rerun' : ''
    assert.ok(prompts[`worktree:#${c.issue}${tag}`].includes(` ${c.base}\``), `${row.name}: #${c.issue}${tag} worktree cut from its base`)
  }
  for (const [id, wt] of Object.entries(row.kept || {})) assert.equal([...result.children, ...result.failed].find((c) => c.issue === id).worktree, wt, `${row.name}: #${id} worktree kept`)
  if (row.together) assert.ok(row.together.every((a) => row.together.every((b) => before(events, `start ${a}`, `end ${b}`))), `${row.name}: ${row.together} run together`)
  for (const [a, b] of row.after || []) assert.ok(before(events, a, b), `${row.name}: ${a} before ${b}`)
  assert.deepEqual(kids.map((c) => c.issue), row.order, `${row.name}: order`)
  assert.deepEqual(kids.map((c) => c.base), row.bases, `${row.name}: bases`)
  assert.deepEqual(ontos, row.ontos, `${row.name}: each landing rebases onto the one before`)
  assert.deepEqual(removes.sort(), row.removes || [...new Set(kids.map((c) => c.issue))].sort().map((i) => `remove:#${i}`), `${row.name}: worktrees removed`)
  assert.ok(kids.every((c) => !c.externalReview), `${row.name}: no externalReview per child`)
  for (const [id, notes] of Object.entries(row.kidNotes || {})) assert.equal(kids.find((c) => c.issue === id).notes, notes, `${row.name}: #${id} notes`)
  assert.equal(result.ok, row.ok, row.name)
  assert.deepEqual(result.children.map((c) => c.issue), row.done, `${row.name}: children`)
  assert.deepEqual(result.failed.map((c) => c.issue), row.failed, `${row.name}: failed`)
  if (row.failedStage) assert.equal(result.failed[0].stage, row.failedStage, `${row.name}: failed stage`)
  assert.deepEqual(result.skipped, row.skipped, `${row.name}: skipped`)
  if (row.reviewBody) {
    assert.equal(reviews.length, 1, `${row.name}: one review`)
    assert.equal(reviews[0].issue, '10', `${row.name}: review issue`)
    assert.equal(reviews[0].base, 'base0', `${row.name}: review base`)
    assert.equal(reviews[0].branch, metaArgs.branch, `${row.name}: review branch`)
    assert.equal(reviews[0].worktree, metaArgs.worktree, `${row.name}: review in the integration worktree`)
    for (const id of ['#11', '#12', '#13']) assert.equal(reviews[0].body.includes(id), row.reviewBody.includes(id), `${row.name}: review body ${id}`)
    if (row.reviewStage) assert.equal(result.review.stage, row.reviewStage, `${row.name}: review stage`)
    if (row.reviewNotes) assert.equal(reviews[0].notes, row.reviewNotes, `${row.name}: review notes`)
    if (row.externalReview) assert.equal(reviews[0].externalReview, row.externalReview, `${row.name}: review externalReview`)
    if (row.redEvidence) assert.equal(reviews[0].redEvidence, row.redEvidence, `${row.name}: review redEvidence`)
  } else {
    assert.equal(reviews.length, 0, `${row.name}: no review`)
  }
  console.log(`PASS ${row.name}`)
}

for (const [name, worktree] of [['missing', ''], ['relative', 'rel/wt']]) {
  await assert.rejects(runMeta([child('11')], { extra: { worktree } }), /args\.worktree/, `meta: ${name} worktree throws`)
  console.log(`PASS meta: ${name} worktree throws`)
}
