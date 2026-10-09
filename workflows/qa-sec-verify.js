export const meta = {
  name: 'qa-sec-verify',
  description: 'Confirm or refute qa-sec findings against the code, one agent per batch of 6',
  phases: [{ title: 'Verify', detail: 'read cited code, trace or reproduce each claim' }],
}

// args: { items: object[] (qa-sec merge items), scope: string, model: string, scratch: string }
const VERDICTS = {
  type: 'object',
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          verdict: { type: 'string', enum: ['confirmed', 'refuted', 'unverifiable'] },
          evidence: { type: 'string', description: 'one line: file:line traced, or command and output' },
          severity: { type: 'string', enum: ['🔴', '🟡', '🚀', '🔵'], description: 'the severity the evidence supports' },
        },
        required: ['id', 'verdict', 'evidence', 'severity'],
      },
    },
  },
  required: ['verdicts'],
}

const BATCH = 6
const batches = []
for (let i = 0; i < args.items.length; i += BATCH) batches.push(args.items.slice(i, i + BATCH))

const results = await parallel(batches.map((batch, i) => () =>
  agent(
    `${args.scope}\n\nVerify each finding below against the code. Return one verdict per id.\n\n` +
    '- confirmed: you traced the claim in the cited code or reproduced it. Evidence names the ' +
    'file:line or the command and its output.\n' +
    '- refuted: the code does not do what the finding claims. Evidence names the line that shows it.\n' +
    '- unverifiable: deciding needs a lab host, a real external service, root, or hardware. ' +
    'Evidence says what is needed.\n' +
    `- You may run local tests and small repros in ${args.scratch}. Do not edit, create or delete ` +
    'files in the repository; no ssh, no forge, no external network.\n' +
    '- Judge each finding on its own; a confirmed bug with a wrong fix is still confirmed.\n' +
    '- severity: rate what your evidence shows, not the claim (🔴 bug/security/data loss/crash, ' +
    '🟡 risk/fragile/regression, 🚀 performance, 🔵 nit). A confirmed finding whose real cost is larger ' +
    'or smaller than claimed gets the severity of the real cost; a refuted one keeps its severity.\n\n' +
    JSON.stringify(batch, null, 1),
    { schema: VERDICTS, model: args.model, effort: 'medium', label: `verify-${i + 1}`, phase: 'Verify' })))

const verdicts = results.filter(Boolean).flatMap(r => r.verdicts)
const missing = args.items.map(it => it.id).filter(id => !verdicts.some(v => v.id === id))
if (missing.length) log(`no verdict for: ${missing.join(', ')}`)

return { verdicts, missing }
