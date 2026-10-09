export const meta = {
  name: 'qa-sec-review',
  description: 'Parallel read-only lens review (dream-team agents, security-review skill), merged and deduped by a cheaper agent',
  phases: [
    { title: 'Review', detail: 'one agent per lens' },
    { title: 'Merge', detail: 'dedup across lenses', model: 'sonnet' },
  ],
}

// args: { scope: string, lenses: string[], model: string, openIssues?: string }
const FOCUS = {
  'security-review':
    'run the `security-review` skill with the Skill tool on this scope, then report its findings ' +
    'in the output format below.',
  'security-audit':
    'secrets and credential handling, file/socket permissions, exposed debug or metrics endpoints, ' +
    'TLS options, CI supply-chain hygiene, service-unit hardening, pinned dependencies with known CVEs.',
  'architect-reviewer':
    'package boundaries and coupling, data-flow and delivery guarantees (loss, duplication), ' +
    'backpressure, documented contracts and where docs and code disagree.',
  'performance-engineer':
    'hot-path allocations, GC pressure, lock contention, I/O buffering, batch sizing. Trace the code; ' +
    'the verify pass does the measuring.',
}

const RULES = [
  'Do not edit, create or delete files in the repository. Do not commit, push, or touch any forge or lab host.',
  'Read only: no builds, test runs, benchmarks, profiles or experiments.',
  'Output: findings only, ranked most severe first. Each finding: one emoji prefix ' +
    '(🔴 bug/security/data loss/crash, 🟡 risk/fragile/regression, 🚀 performance, 🔵 nit, ❓ genuine question), ' +
    '`file:line`, why, fix. Mark each [verified] (traced in code) or [suspected].',
  'No praise, no codebase summary. If a step could not run (tool missing, blocked), say so in one line.',
].join('\n')

const reports = await parallel(args.lenses.map(lens => () =>
  agent(`${args.scope}\n\nYour lens: ${FOCUS[lens.split(':').pop()] || lens}\n\n${RULES}`, {
    // A lens with `:` names its agent type; any other runs on the default workflow agent.
    ...(lens.includes(':') ? { agentType: lens } : {}),
    // Run every lens on the session model, overriding any model its agent file pins.
    model: args.model,
    label: lens,
    phase: 'Review',
  }).then(text => ({ lens, text }))
    // An agent type that is not installed throws at dispatch; list that lens in `missing` instead.
    .catch(e => { log(`${lens}: ${(e && e.message) || e}`); return null })))

const got = reports.filter(r => r && r.text)
const missing = args.lenses.filter(l => !got.some(r => r.lens === l))
if (missing.length) log(`no report from: ${missing.join(', ')}`)

const ITEMS = {
  type: 'object',
  properties: {
    items: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'F1, F2, ... in ranked order' },
          severity: { type: 'string', enum: ['🔴', '🟡', '🚀', '🔵'] },
          theme: {
            type: 'string',
            enum: ['🛡️ Security', '💾 Reliability / data loss', '🏗️ Architecture / contracts',
              '🧪 Tests / CI', '⚙️ Ops / config / deploy', '📝 Docs drift / writing'],
          },
          claim: { type: 'string' },
          location: { type: 'string', description: 'file:line, comma-separated if several' },
          status: { type: 'string', enum: ['verified', 'suspected'] },
          disputed: { type: 'boolean', description: 'one lens marked it verified, another suspected' },
          lenses: { type: 'array', items: { type: 'string' } },
          why: { type: 'string', description: 'evidence kept from the reports: repro numbers, log lines' },
          fix: { type: 'string' },
          coveredBy: { type: 'string', description: '#N of an open issue, or empty' },
        },
        required: ['id', 'severity', 'theme', 'claim', 'location', 'status', 'disputed', 'lenses', 'why', 'fix'],
      },
    },
    questions: { type: 'array', items: { type: 'string' } },
    blocked: { type: 'array', items: { type: 'string' }, description: 'lens: what could not run' },
  },
  required: ['items', 'questions', 'blocked'],
}

phase('Merge')
const MERGE_PROMPT =
  `Merge these ${got.length} review reports into one deduplicated list, ranked most severe first.\n\n` +
  '- Same defect reported by several lenses → one item; list every lens that found it; keep the ' +
  'strongest evidence (verified beats suspected; keep repro numbers and log lines in `why`). ' +
  'Set `disputed` when one lens marked it verified and another suspected.\n' +
  '- Never drop a finding. Never soften a severity; on disagreement take the higher one.\n' +
  '- ❓ findings go to `questions`, not `items`.\n' +
  (args.openIssues
    ? `- A finding already covered by an open tracker issue → keep it, set coveredBy to "#N".\nOpen issues:\n${args.openIssues}\n`
    : '') +
  '- `blocked`: lenses that reported a blocked or incomplete run, with what did not run.\n\n' +
  got.map(r => `=== ${r.lens} ===\n${r.text}`).join('\n\n')
const merge = label => agent(MERGE_PROMPT, { schema: ITEMS, model: 'sonnet', effort: 'medium', label, phase: 'Merge' })

// Dedup joins findings across lenses, so fewer items than one lens's own findings means the merge dropped some.
const countFindings = text => (text.match(/^\s*(?:\d+\.\s*|[-*]\s*)?(?:\*\*)?(?:🔴|🟡|🚀|🔵)/gmu) || []).length
const floor = Math.max(0, ...got.map(r => countFindings(r.text)))
const short = m => !m || m.items.length < floor

let merged = got.length === 0 ? { items: [], questions: [], blocked: [] } : await merge('merge')
if (got.length && short(merged)) {
  log(`merge returned ${merged ? merged.items.length : 0} items, below one lens's ${floor} findings; merging again`)
  const again = await merge('merge-retry')
  if (again && (!merged || again.items.length > merged.items.length)) merged = again
  if (short(merged)) {
    merged = merged || { items: [], questions: [], blocked: [] }
    merged.blocked.push(`merge: ${merged.items.length} items, below one lens's ${floor} findings; read the raw reports`)
  }
}

return { ...merged, raw: got, missing }
