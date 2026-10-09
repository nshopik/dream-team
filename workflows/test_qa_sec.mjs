// What qa-sec-review does with each lens and each merge reply, and how qa-sec-verify batches items, through stub agents; no claude call.
// Usage: node test_qa_sec.mjs
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor
const load = (file) => readFileSync(new URL(file, import.meta.url), 'utf8').replace(/^export /m, '')

async function run(file, args, stub) {
  const calls = []
  async function agent(prompt, opts) {
    calls.push({ prompt, opts })
    return stub(prompt, opts)
  }
  const result = await new AsyncFunction('args', 'agent', 'phase', 'log', 'parallel', load(file))(
    args, agent, () => {}, () => {}, (fns) => Promise.all(fns.map((f) => f())))
  return { result, calls }
}

const report = '🔴 a.go:1 leak\n🟡 b.go:2 race\n🚀 c.go:3 alloc'
const item = (id) => ({ id, severity: '🔴', theme: '🛡️ Security', claim: id, location: 'a.go:1', status: 'verified', disputed: false, lenses: [], why: '', fix: '' })
const merged = (n) => ({ items: Array.from({ length: n }, (_, i) => item(`F${i + 1}`)), questions: [], blocked: [] })

const lenses = {
  'dream-team:architect-reviewer': 'dream-team:architect-reviewer',
  'pr-review-toolkit:silent-failure-hunter': 'pr-review-toolkit:silent-failure-hunter',
  'security-review': undefined,
  'security-audit': undefined,
}

const reviewRows = [
  { name: 'merge once', merges: [merged(3)], labels: ['merge'], items: 3, blocked: 0 },
  { name: 'merge short, retry fills it', merges: [merged(1), merged(3)], labels: ['merge', 'merge-retry'], items: 3, blocked: 0 },
  { name: 'merge still short', merges: [merged(1), merged(1)], labels: ['merge', 'merge-retry'], items: 1, blocked: 1 },
  { name: 'merge fails twice, no counted findings', report: '### High: a.go:1 leak', merges: [null, null], labels: ['merge', 'merge-retry'], items: 0, blocked: 1 },
]

for (const row of reviewRows) {
  const merges = [...row.merges]
  const { result, calls } = await run('qa-sec-review.js', { scope: 'repo', lenses: Object.keys(lenses), model: 'opus' },
    (prompt, opts) => opts.phase === 'Merge' ? merges.shift() : row.report ?? report)
  const review = calls.filter((c) => c.opts.phase === 'Review')
  for (const [lens, type] of Object.entries(lenses)) {
    assert.equal(review.find((c) => c.opts.label === lens).opts.agentType, type, `${row.name}: ${lens} agentType`)
  }
  assert.ok(review.find((c) => c.opts.label === 'dream-team:architect-reviewer').prompt.includes('package boundaries'), `${row.name}: architect focus`)
  assert.ok(review.find((c) => c.opts.label === 'security-audit').prompt.includes('secrets and credential handling'), `${row.name}: security-audit focus`)
  assert.deepEqual(calls.filter((c) => c.opts.phase === 'Merge').map((c) => c.opts.label), row.labels, row.name)
  assert.equal(result.items.length, row.items, row.name)
  assert.equal(result.blocked.length, row.blocked, row.name)
  if (row.blocked) assert.match(result.blocked[0], /^merge: /, row.name)
  console.log(`PASS ${row.name}`)
}

{
  const { result } = await run('qa-sec-review.js', { scope: 'repo', lenses: ['security-review', 'gone:lens', 'dream-team:architect-reviewer'], model: 'opus' },
    (prompt, opts) => {
      if (opts.agentType === 'gone:lens') throw new Error('Agent type gone:lens not found')
      if (opts.label === 'dream-team:architect-reviewer') return null
      return opts.phase === 'Merge' ? merged(3) : report
    })
  assert.deepEqual(result.missing, ['gone:lens', 'dream-team:architect-reviewer'])
  assert.equal(result.items.length, 3)
  console.log('PASS uninstalled or silent lens listed in missing')
}

const items = Array.from({ length: 13 }, (_, i) => item(`F${i + 1}`))
const { result, calls } = await run('qa-sec-verify.js', { items, scope: 'repo', model: 'opus', scratch: '/tmp/x' },
  (prompt) => ({ verdicts: JSON.parse(prompt.slice(prompt.indexOf('[')))
    .filter((it) => it.id !== 'F13')
    .map((it) => ({ id: it.id, verdict: 'confirmed', evidence: 'a.go:1', severity: '🔴' })) }))
assert.deepEqual(calls.map((c) => c.opts.label), ['verify-1', 'verify-2', 'verify-3'])
assert.deepEqual(calls.map((c) => JSON.parse(c.prompt.slice(c.prompt.indexOf('['))).length), [6, 6, 1])
assert.equal(result.verdicts.length, 12)
assert.deepEqual(result.missing, ['F13'])
console.log('PASS verify batches of 6, missing verdict listed')
