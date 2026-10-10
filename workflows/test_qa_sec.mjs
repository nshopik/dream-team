// How qa-sec-verify batches items and lists missing verdicts, through stub agents; no claude call.
// Usage: node test_qa_sec.mjs
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor
const load = (file) => readFileSync(new URL(file, import.meta.url), 'utf8').replace(/^export /m, '')

const calls = []
async function agent(prompt, opts) {
  calls.push({ prompt, opts })
  return { verdicts: JSON.parse(prompt.slice(prompt.indexOf('[')))
    .filter((it) => it.id !== 'F13')
    .map((it) => ({ id: it.id, verdict: 'confirmed', evidence: 'a.go:1', severity: '🔴' })) }
}
const items = Array.from({ length: 13 }, (_, i) => ({ id: `F${i + 1}`, severity: '🔴', theme: '🛡️ Security', claim: `F${i + 1}`, location: 'a.go:1', status: 'verified', disputed: false, lenses: [], why: '', fix: '' }))
const result = await new AsyncFunction('args', 'agent', 'phase', 'log', 'parallel', load('qa-sec-verify.js'))(
  { items, scope: 'repo', model: 'opus', scratch: '/tmp/x' }, agent, () => {}, () => {}, (fns) => Promise.all(fns.map((f) => f())))
assert.deepEqual(calls.map((c) => c.opts.label), ['verify-1', 'verify-2', 'verify-3'])
assert.deepEqual(calls.map((c) => JSON.parse(c.prompt.slice(c.prompt.indexOf('['))).length), [6, 6, 1])
assert.equal(result.verdicts.length, 12)
assert.deepEqual(result.missing, ['F13'])
console.log('PASS verify batches of 6, missing verdict listed')
