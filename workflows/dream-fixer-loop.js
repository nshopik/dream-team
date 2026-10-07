export const meta = {
  name: 'dream-fixer-loop',
  description: 'One issue end to end: implement, mechanical gate after every write, ponytail-review simplify pass, pr-review-toolkit reviewers plus one domain reviewer unless args.domainReviewer is none, bounded fix loop',
  phases: [
    { title: 'Implement', detail: 'one specialist writes the change and commits' },
    { title: 'Gate', detail: 'the orchestrator-supplied gate commands with a build-fix loop (sonnet, low); re-runs after every fix agent' },
    { title: 'Simplify', detail: 'ponytail-review cuts, applied or disputed by the implementer; skipped when the diff has no code or ponytail-review is unavailable (opus)' },
    { title: 'Review', detail: 'pr-review-toolkit suite plus one domain reviewer unless args.domainReviewer is none (opus); opt-in /verify gate through a nested claude session, skipped when the diff has no code or claude or its /verify is unavailable; opt-in external review command, its findings checked by one agent' },
    { title: 'Fix', detail: 'blocking findings only; re-review only the reviewers that failed' },
  ],
}

// ---------------------------------------------------------------------------
// Inputs (all from the orchestrator, which already read the issue and branched)
// ---------------------------------------------------------------------------
const A = args || {}
const ISSUE = String(A.issue || '')
const TITLE = String(A.title || '')
const BODY = String(A.body || '')
const NOTES = String(A.notes || '')
const BRANCH = String(A.branch || '')
const BASE = String(A.base || '')
const GATE_COMMANDS = Array.isArray(A.gateCommands) ? A.gateCommands.map(String).filter(Boolean) : []
const VERIFY = A.verify === true
const NO_DOMAIN = A.domainReviewer === 'none'
const EXTERNAL = String(A.externalReview || '')
const FIX_ROUNDS = 3
const VERIFY_ROUNDS = 3

if (!ISSUE || !BRANCH || !BASE || !GATE_COMMANDS.length) {
  throw new Error('dream-fixer-loop: args.issue, args.branch, args.base and args.gateCommands are required')
}
const isGeneric = (t) => !t || t === 'generic'
if (!isGeneric(A.implementer) && A.implementer === A.domainReviewer) {
  throw new Error('dream-fixer-loop: args.domainReviewer must be a different type than args.implementer')
}

// ---------------------------------------------------------------------------
// Schemas
// ---------------------------------------------------------------------------
const FRICTION = { type: 'array', items: { type: 'string' }, description: 'instructions you could not follow, tools you lacked, and workarounds you used; omit when none' }

const IMPL_SCHEMA = {
  type: 'object',
  required: ['committed', 'summary', 'redEvidence'],
  additionalProperties: false,
  properties: {
    friction: FRICTION,
    committed: { type: 'boolean' },
    summary: { type: 'string' },
    redEvidence: { type: 'string', description: 'bug fix: key lines of the new test failing before the fix was applied; empty string when the issue is not a bug fix' },
    assumptions: { type: 'array', items: { type: 'string' }, description: 'anything you had to guess because the issue left it open; a choice a written rule or instruction settles is not an assumption' },
  },
}

// The verify agent is the neutral party that already runs git, so it also
// reports which review aspects the diff touches. Asking the implementer would
// be self-assessment, and a second agent for a `git diff --name-only` is waste.
const VERIFY_SCHEMA = {
  type: 'object',
  required: ['passed', 'summary', 'changedFiles', 'dirtyPaths'],
  additionalProperties: false,
  properties: {
    friction: FRICTION,
    passed: { type: 'boolean', description: 'true only if every command exited 0' },
    summary: { type: 'string' },
    changedFiles: { type: 'array', items: { type: 'string' } },
    dirtyPaths: { type: 'array', items: { type: 'string' }, description: 'paths from `git status --porcelain` taken before the gate ran' },
    aspects: {
      type: 'array',
      description: 'which review aspects this diff touches; only when the prompt asks for them',
      items: { type: 'string', enum: ['tests', 'types', 'code'] },
    },
    failures: {
      type: 'array',
      items: {
        type: 'object',
        required: ['command', 'errorExcerpt'],
        additionalProperties: false,
        properties: {
          command: { type: 'string' },
          errorExcerpt: { type: 'string', description: 'the key error lines, not the whole log' },
        },
      },
    },
  },
}

const BUILD_FIX_SCHEMA = {
  type: 'object',
  required: ['committed', 'summary'],
  additionalProperties: false,
  properties: {
    friction: FRICTION,
    committed: { type: 'boolean' },
    summary: { type: 'string' },
  },
}

// No `passed` field: a verdict passes when it carries no blocking finding.
const VERDICT_SCHEMA = {
  type: 'object',
  required: ['summary', 'findings'],
  additionalProperties: false,
  properties: {
    friction: FRICTION,
    summary: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['severity', 'description'],
        additionalProperties: false,
        properties: {
          severity: { type: 'string', enum: ['critical', 'important', 'minor'] },
          description: { type: 'string' },
          file: { type: 'string' },
        },
      },
    },
  },
}

const EXTERNAL_SCHEMA = {
  ...VERDICT_SCHEMA,
  required: [...VERDICT_SCHEMA.required, 'ran'],
  properties: {
    ...VERDICT_SCHEMA.properties,
    ran: { type: 'boolean', description: 'false when the command is not found or exits non-zero' },
  },
}

const SIMPLIFY_SCHEMA = {
  type: 'object',
  required: ['skillLoaded', 'findings', 'net'],
  additionalProperties: false,
  properties: {
    friction: FRICTION,
    skillLoaded: { type: 'boolean', description: 'false when the ponytail:ponytail-review skill is not available in this session' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['tag', 'location', 'cut', 'replacement'],
        additionalProperties: false,
        properties: {
          tag: { type: 'string', enum: ['delete', 'stdlib', 'native', 'yagni', 'shrink'] },
          location: { type: 'string', description: '<file>:L<line>' },
          cut: { type: 'string' },
          replacement: { type: 'string' },
        },
      },
    },
    net: { type: 'integer', minimum: 0, description: 'the N of the skill\'s `net: -<N> lines possible.`; 0 on `Lean already. Ship.`' },
  },
}

const VERIFY_RUN_SCHEMA = {
  type: 'object',
  required: ['available', 'verdict', 'command', 'output', 'reason', 'recipePath'],
  additionalProperties: false,
  properties: {
    friction: FRICTION,
    available: { type: 'boolean', description: 'false when `claude` is not on PATH or the nested init event does not list verify under slash_commands' },
    verdict: { type: 'string', enum: ['PASS', 'FAIL', 'BLOCKED', 'SKIP'] },
    command: { type: 'string', description: 'the command /verify drove the changed code with' },
    output: { type: 'string', description: 'that command\'s output, trimmed to the key lines' },
    reason: { type: 'string', description: 'the reason /verify gives for its verdict' },
    recipePath: { type: 'string', description: 'path outside the checkout of the .claude/skills/verify/SKILL.md the nested run wrote; empty string when it wrote none' },
  },
}

// Re-reviewers reword findings, so a resolved one is named by the reviewer,
// not diffed out of its prior verdict.
const RE_REVIEW_SCHEMA = {
  ...VERDICT_SCHEMA,
  required: [...VERDICT_SCHEMA.required, 'resolved'],
  properties: {
    ...VERDICT_SCHEMA.properties,
    resolved: { ...VERDICT_SCHEMA.properties.findings, description: 'your prior findings the current branch now fixes' },
  },
}

// A fixer that cannot refuse turns every reviewer opinion into a code change,
// which is how a wrong finding becomes a bug. Disputes go to the orchestrator.
const FIX_SCHEMA = {
  type: 'object',
  required: ['committed', 'addressed', 'disputed', 'summary'],
  additionalProperties: false,
  properties: {
    friction: FRICTION,
    committed: { type: 'boolean' },
    addressed: { type: 'array', items: { type: 'string' } },
    disputed: {
      type: 'array',
      items: {
        type: 'object',
        required: ['finding', 'reason'],
        additionalProperties: false,
        properties: {
          finding: { type: 'string' },
          reason: { type: 'string', description: 'why the finding is wrong, with the evidence that settles it' },
        },
      },
    },
    summary: { type: 'string' },
  },
}

// ---------------------------------------------------------------------------
// Roster
// ---------------------------------------------------------------------------

// review-pr is a command, not a dispatchable type, so its applicability rules
// (commands/review-pr.md:41) live here. Comments and error handling change in
// nearly every diff, so those reviewers always run; only tests and types are
// detected, by the verify agent's greps.
const CODE_REVIEWER = 'pr-review-toolkit:code-reviewer'
const QUALITY_ALWAYS = [
  CODE_REVIEWER,
  'pr-review-toolkit:comment-analyzer',
  'pr-review-toolkit:silent-failure-hunter',
]
const ASPECT_AGENTS = {
  tests: 'pr-review-toolkit:pr-test-analyzer',
  types: 'pr-review-toolkit:type-design-analyzer',
}

const roster = (agentType) => (isGeneric(agentType) ? {} : { agentType })

// A catalog agent carries its own `model:` in its frontmatter, which wins over
// the session's unless the call overrides it — so every verdict and every stage
// that writes code pins Opus, or a fix round would silently run weaker than the
// implementation it is repairing.
const reviewerRoster = (agentType) => ({ ...roster(agentType), model: 'opus' })
const implementerRoster = (agentType) => ({ ...roster(agentType), model: 'opus', effort: 'high' })

// Also holds a missing ponytail-review skill or /verify, so `degraded` reports it.
const MISSING_TYPES = new Set()
const PONYTAIL_REVIEW = 'ponytail:ponytail-review'
const VERIFY_SKILL = 'verify'
const degrade = ({ agentType, ...o }) => o

// An unknown agentType throws at dispatch, before any null-result safety net.
// A disabled plugin is enough to make a real type vanish, so degrade instead
// of failing the run. Every agent call goes through here, which keeps
// `friction` in the journal and out of the result.
async function agentR(prompt, opts) {
  if (opts.agentType && MISSING_TYPES.has(opts.agentType)) opts = degrade(opts)
  let r
  try {
    r = await agent(prompt, opts)
  } catch (e) {
    const msg = String((e && e.message) || e)
    if (!opts.agentType || !msg.includes('not found')) throw e
    if (msg.includes(opts.agentType)) MISSING_TYPES.add(opts.agentType)
    log(`${opts.label}: ${opts.agentType} not dispatchable — retrying generically.`)
    r = await agent(prompt, degrade(opts))
  }
  if (!r) return r
  const { friction, ...rest } = r
  return rest
}

// ---------------------------------------------------------------------------
// Prompts
// ---------------------------------------------------------------------------
const CONTEXT = [
  `Issue #${ISSUE}: ${TITLE}`,
  '',
  BODY,
  ...(NOTES ? ['', 'Orchestrator notes — tracker discussion, decisions the user already made, work that is not yours:', NOTES] : []),
  '',
  `Branch: ${BRANCH} (already created and checked out; work in the repo as it stands).`,
  `Base: ${BASE} — the branch diff is \`git diff ${BASE}..HEAD\`.`,
  'The repo CLAUDE.md files are already in your context — they carry this project\'s conventions and domain rules. Follow them.',
  'Never push, never open or edit an MR/PR, and never create, comment on or edit an issue, whatever the repo context says; the orchestrator does all of that after this workflow.',
].join('\n')

const GATE = [
  'Gate commands — run exactly these, in this order, from the repo root:',
  ...GATE_COMMANDS.map((c) => `  ${c}`),
].join('\n')

const COMMIT_ALL = 'Commit every edit you make as `fixup! <subject of the commit it repairs>`, with that subject copied from `git log`. An edit that repairs two commits is two fixup commits, never a plain commit: stage per path, and stage the hunks of a shared file with a partial patch through `git apply --cached`. Do not bump a version or add a release section: only the implementer\'s commit carries the release.'

const READ_ONLY = 'Read-only: do not edit, stage or commit anything, and do not run the build or the test suite — the gate already ran them, and the other reviewers share this checkout.'

const REVIEW_RULES = [
  READ_ONLY,
  'Judge only lines this diff changed. A pre-existing problem outside the diff is not a finding here.',
  'Rate each finding critical, important or minor. Critical and important block the MR. Minor is a nit that is never auto-fixed, so do not inflate severity to force action.',
].join('\n')

function implPrompt() {
  return [
    CONTEXT,
    '',
    'Implement the smallest change that resolves this issue. Reuse what is already in the repo before writing anything new.',
    'The issue\'s `Done when …` paragraph, when present, is the finish line: stop once it holds and every gate command is green.',
    'Build only what the issue needs: no abstractions for hypothetical requirements, no error handling for cases that cannot happen, no cleanup around the change, no feature flag or back-compat shim.',
    'A bug fix gets a test that reproduces the bug; new behaviour gets a unit or e2e test. Prefer a new case in an existing table-driven test over a new test function.',
    'For a bug fix, write the test first, run it, and keep the key lines of its failing output: return them as redEvidence. Not a bug fix: return an empty string.',
    GATE,
    'Get every gate command green, load the `scope-commit` skill, then commit on the branch in the repo\'s commit convention. Commit once; only when the issue holds independent changes, commit each change separately under its own subject.',
    'If the issue left something genuinely open, implement your best reading and list it in assumptions rather than stopping. A choice that a written rule or instruction settles (CLAUDE.md, a skill, a harness instruction) is not an assumption: leave it out.',
  ].join('\n')
}

function verifyPrompt(after, withAspects) {
  return [
    CONTEXT,
    '',
    after ? `Re-run the mechanical gate after ${after}.` : 'Run the mechanical gate on the current branch state.',
    'Before any gate command, run `git status --porcelain` and report every path it lists as dirtyPaths; do not stage, commit or clean them.',
    GATE,
    'Report pass only if every command exited 0.',
    'Do not review style or design — that is a later stage. Report what the tooling says.',
    `Report changedFiles from \`git diff --name-only ${BASE}..HEAD\`.`,
    ...(withAspects ? [
      'Also report which review aspects the diff touches. Do not judge this by reading — run the commands.',
      `Let D=\`git diff -U0 ${BASE}..HEAD\`. Report an aspect when, and only when, its command produces output:`,
      `  tests - \`git diff --name-only ${BASE}..HEAD | grep -Ei '(^|/)(tests?|spec)/|_(test|spec)\\.|\\.(test|spec)\\.'\`,`,
      '          or D matches `^\\+.*(#\\[test\\]|#\\[cfg\\(test\\)\\]|\\bdef test_|\\bit\\(|\\btest\\()`',
      '  types - D matches `^\\+\\s*(pub )?(struct|enum|trait|type|impl|interface|class|dataclass)\\b`',
      `  code  - \`git diff --name-only ${BASE}..HEAD | grep -Ei '\\.(c|cc|cpp|cs|css|ex|exs|go|h|hpp|html|java|js|jsx|kt|lua|mjs|cjs|php|py|rb|rs|scala|sh|svelte|swift|ts|tsx|vue|zig)$'\``,
      'Adapt the patterns to this repo\'s language if it is not one the patterns cover, keeping them mechanical.',
      'These over-report on purpose. An extra check is cheap; a missing one is silent. Never drop an aspect whose command matched.',
    ] : []),
  ].join('\n')
}

function buildFixPrompt(v, round) {
  return [
    CONTEXT,
    '',
    `The mechanical gate failed (round ${round}). Failures:`,
    (v.failures || []).map((f) => `- ${f.command}: ${f.errorExcerpt}`).join('\n') || `- ${v.summary}`,
    '',
    'Fix the cause, not the symptom. Do not weaken or delete a test to make it pass.',
    'Re-run the failing commands, then commit on the branch.',
    COMMIT_ALL,
  ].join('\n')
}

function simplifyPrompt() {
  return [
    CONTEXT,
    '',
    `Load the ${PONYTAIL_REVIEW} skill with the Skill tool and review the branch diff with it.`,
    'Not available in this session → return skillLoaded false, no findings and net 0. Never review without it.',
    'Return each line the skill writes as one finding, and the N of its `net: -<N> lines possible.` as net.',
    'The skill says `Lean already. Ship.` → return no findings and net 0.',
    READ_ONLY,
  ].join('\n')
}

// The Skill tool refuses /verify (disable-model-invocation); a nested session loads it.
function verifyRunPrompt() {
  return [
    CONTEXT,
    '',
    'Run Claude Code\'s /verify on the branch diff in a nested session from Bash. Do not replicate /verify yourself.',
    '`command -v claude` prints nothing → return available false and verdict SKIP.',
    'Otherwise run this as one Bash call from the repo root, with the Bash tool\'s 600000 ms timeout and no permission flags; shell variables do not survive to the next call, so read the stream later from the directory it prints:',
    `  D=$(mktemp -d) && echo "$D" && claude -p "/verify the changes in ${BASE}..HEAD. Write every capture under $D." --model opus --effort medium --output-format stream-json --verbose > "$D/stream.jsonl"`,
    'The run exits non-zero, times out, or its stream has no final result event → return available true and verdict BLOCKED, with the exit status or the last stream lines as reason.',
    'The init event (type system, subtype init) does not list verify under slash_commands → return available false and verdict SKIP.',
    'Otherwise return available true and, from the run\'s final report: the verdict, the command it drove the changed code with, that command\'s output trimmed to the key lines, and the reason for the verdict.',
    '`git status --porcelain --untracked-files=all -- .claude/skills/verify/SKILL.md` prints `??` → move the file to SKILL.md in the directory the run printed and return that path as recipePath.',
    'It prints ` M` → copy the file to SKILL.md in that directory, return that path as recipePath, and run `git restore -- .claude/skills/verify/SKILL.md`.',
    'It prints nothing → recipePath is an empty string; leave the file alone.',
    'Delete or restore nothing else, and do not edit, stage or commit anything: the other reviewers share this checkout.',
  ].join('\n')
}

function simplifyFixPrompt(findings) {
  return [
    CONTEXT,
    '',
    'An over-engineering review of the branch diff proposes these cuts:',
    findings.map((f) => `- ${f.location}: ${f.tag}: ${f.cut} → ${f.replacement}`).join('\n'),
    '',
    ...APPLY_RULES,
  ].join('\n')
}

const DONE_WHEN = 'The issue\'s `Done when …` paragraph, when present, must hold on this branch: check it by reading and cite what you read. A condition that does not hold is an important finding; one only a build or test run can show is left to the gate.'

function qualityPrompt(agentType, redEvidence) {
  return [
    CONTEXT,
    '',
    `Review the branch diff as ${agentType}, on your own specialty only.`,
    REVIEW_RULES,
    'Anything a linter, typechecker or the test suite would catch is out of scope — that gate already ran and passed.',
    ...(NO_DOMAIN && agentType === CODE_REVIEWER ? [DONE_WHEN] : []),
    ...(redEvidence && agentType === ASPECT_AGENTS.tests ? [
      '',
      'The implementer reports this failing output from the new test, observed before the fix was applied:',
      redEvidence,
      'Check it: the test it names is in the diff, asserts the behaviour the issue describes, and fails for the bug itself — not a compile error, a typo or an unrelated assertion. Evidence that does not hold is an important finding.',
    ] : []),
  ].join('\n')
}

function domainPrompt() {
  return [
    CONTEXT,
    '',
    'Review the branch diff as the domain reviewer.',
    'Your lens is the one the build and test suite cannot check: does this change hold against the rules, reference sources and invariants this project\'s CLAUDE.md sets out, and against the issue it claims to close.',
    DONE_WHEN,
    'Where the project names a reference implementation or spec, check the claim against that source and cite what you read — file and line.',
    REVIEW_RULES,
  ].join('\n')
}

function externalPrompt() {
  return [
    CONTEXT,
    '',
    'Get a second opinion on the branch diff from an external reviewer, then check it.',
    'Run this once, as one Bash call from the repo root:',
    `  set -o pipefail; git diff ${BASE}..HEAD | ${EXTERNAL}`,
    'The command is not found or exits non-zero → return ran false, no findings, and the exit status or error as summary.',
    'It prints nothing, or neither findings nor a no-issues verdict → return ran false, no findings, and its output as summary.',
    'Otherwise return ran true. Check each finding it prints against the code: return only the ones that hold, and drop the rest with the reason in the summary.',
    REVIEW_RULES,
  ].join('\n')
}

function reReviewPrompt(prev, fix, round) {
  return [
    CONTEXT,
    '',
    `Fix round ${round}. You reviewed this branch and did not pass it. Your findings were:`,
    prev.findings.map((f) => `- [${f.severity}] ${f.description}`).join('\n'),
    '',
    'The fixer reports:',
    fix.summary,
    fix.addressed.length ? `Addressed: ${fix.addressed.join('; ')}` : '',
    fix.disputed.length ? `Disputed: ${fix.disputed.map((d) => `${d.finding} — ${d.reason}`).join('; ')}` : '',
    '',
    READ_ONLY,
    'Re-review ONLY your own outstanding findings against the current branch state.',
    'Do not raise new findings unrelated to them — a fresh sweep each round makes this loop never converge.',
    'List under resolved each of your prior findings the current branch now fixes, severity unchanged.',
    'A disputed finding you now agree was wrong is not a fix: drop it, leave it out of resolved, and say so in the summary.',
    'Return only the findings that still stand, severity unchanged.',
  ].join('\n')
}

const APPLY_RULES = [
  'Verify each finding against the code before acting on it. A reviewer can be wrong, and applying a wrong finding is its own bug.',
  'Fix the ones that hold. For any that does not, leave the code alone and return it under disputed with the evidence that settles it.',
  'Do not widen the change beyond these findings.',
  'Re-run the gate commands, then commit on the branch.',
  COMMIT_ALL,
  GATE,
]

function fixPrompt(blocking, disputes, round) {
  return [
    CONTEXT,
    '',
    `Fix round ${round}. Reviewers raised these blocking findings:`,
    blocking.map((f) => `- [${f.severity}] (${f.gate}) ${f.description}${f.file ? ` — ${f.file}` : ''}`).join('\n'),
    ...(disputes.length ? [
      '',
      'Disputes from earlier rounds. The reviewer read each one; a finding still listed above is one the reviewer held:',
      disputes.map((d) => `- (round ${d.round}) ${d.finding} — ${d.reason}`).join('\n'),
    ] : []),
    '',
    'Do not fix minor findings.',
    ...APPLY_RULES,
  ].join('\n')
}

// ---------------------------------------------------------------------------
// Run
// ---------------------------------------------------------------------------
const BLOCKING = new Set(['critical', 'important'])
const blockingOf = (v) => v.findings.filter((f) => BLOCKING.has(f.severity))
// A reviewer that died has judged nothing: it is re-dispatched with its full
// prompt, and never handed to the fixer as a finding.
const deadReviewer = (kind) => ({ dead: true, summary: `${kind} reviewer produced no verdict`, findings: [] })

// The run continues past a writing agent only through this gate, so the head that ships is a gated one.
async function gate(after, tag, withAspects) {
  for (let round = 0; ; round++) {
    const verify = await agentR(verifyPrompt(round ? `build-fix round ${round}` : after, withAspects), {
      label: `gate:#${ISSUE}${tag ? `:${tag}` : ''}${round ? `:r${round}` : ''}`,
      phase: 'Gate',
      schema: VERIFY_SCHEMA,
      model: 'sonnet',
      effort: 'low',
    })
    if (!verify) return { ok: false, reason: 'gate agent returned no result' }
    if (verify.dirtyPaths.length) return { ok: false, reason: `uncommitted edits in the working tree: ${verify.dirtyPaths.join(', ')}`, verify }
    if (verify.passed) return { ok: true, verify }
    if (round === VERIFY_ROUNDS) {
      return { ok: false, reason: `build/test still failing after ${VERIFY_ROUNDS} fix rounds`, verify }
    }
    log(`Gate failed: ${verify.summary}`)
    const bf = await agentR(buildFixPrompt(verify, round + 1), {
      label: `build-fix:#${ISSUE}${tag ? `:${tag}` : ''}:r${round + 1}`,
      phase: 'Gate',
      schema: BUILD_FIX_SCHEMA,
      ...implementerRoster(A.implementer),
    })
    if (!bf) return { ok: false, reason: 'build fixer returned no result', verify }
    if (!bf.committed) return { ok: false, reason: `build fixer committed nothing: ${bf.summary}`, verify }
  }
}

phase('Implement')
const impl = await agentR(implPrompt(), {
  label: `impl:#${ISSUE}`,
  phase: 'Implement',
  schema: IMPL_SCHEMA,
  ...implementerRoster(A.implementer),
})
if (!impl) return { ok: false, stage: 'implement', reason: 'implementer returned no result' }
if (!impl.committed) return { ok: false, stage: 'implement', reason: impl.summary || 'implementer committed nothing' }

phase('Gate')
const first = await gate('', '', true)
if (!first.ok) return { ok: false, stage: 'gate', reason: first.reason, verify: first.verify }
let changedFiles = first.verify.changedFiles

const aspects = new Set(first.verify.aspects || [])
if (impl.redEvidence) aspects.add('tests')

// Must precede Review: a cut made after it ships unreviewed.
let simplify = null
if (aspects.has('code')) {
  phase('Simplify')
  const review = await agentR(simplifyPrompt(), { label: `simplify:#${ISSUE}`, phase: 'Simplify', schema: SIMPLIFY_SCHEMA, model: 'opus' })
  if (!review) return { ok: false, stage: 'simplify', reason: 'simplify reviewer returned no result' }
  if (!review.skillLoaded) {
    MISSING_TYPES.add(PONYTAIL_REVIEW)
    log(`Simplify: ${PONYTAIL_REVIEW} not available — skipped.`)
  } else if (!review.findings.length) {
    simplify = { net: 0, applied: [], disputed: [], unhandled: 0 }
  } else {
    const cuts = await agentR(simplifyFixPrompt(review.findings), {
      label: `simplify-fix:#${ISSUE}`,
      phase: 'Simplify',
      schema: FIX_SCHEMA,
      ...implementerRoster(A.implementer),
    })
    if (!cuts) return { ok: false, stage: 'simplify', reason: 'implementer returned no result on the simplify cuts' }
    if (cuts.addressed.length ? !cuts.committed : !cuts.disputed.length) {
      return { ok: false, stage: 'simplify', reason: `simplify implementer applied nothing it committed and disputed nothing: ${cuts.summary}` }
    }
    const g = await gate('the simplify cuts', 'simplify', false)
    if (!g.ok) return { ok: false, stage: 'gate', reason: g.reason, verify: g.verify }
    changedFiles = g.verify.changedFiles
    const unhandled = Math.max(0, review.findings.length - cuts.addressed.length - cuts.disputed.length)
    simplify = { net: review.net, applied: cuts.addressed, disputed: cuts.disputed, unhandled }
  }
}

// A FAIL is a blocking finding for the fix loop. A re-review is a fresh run on
// the new head; only its PASS resolves a prior FAIL, a run that verified nothing keeps it.
let verifyRun = null
async function runVerify(label, phase, prev) {
  const r = await agentR(verifyRunPrompt(), { label, phase, schema: VERIFY_RUN_SCHEMA, model: 'sonnet', effort: 'low' })
  if (!r) return null
  if (r.available) verifyRun = { ...r, recipePath: r.recipePath || verifyRun?.recipePath || '' }
  else {
    MISSING_TYPES.add(VERIFY_SKILL)
    log(`Review: /verify not available — skipped: ${r.reason}`)
  }
  const verdict = r.available ? r.verdict : 'SKIP'
  const summary = r.available ? `/verify ${verdict}: ${r.reason}` : '/verify not available'
  if (verdict === 'FAIL') {
    return { summary, resolved: [], findings: [{ severity: 'important', description: `/verify FAIL: ${r.reason}\nCommand: ${r.command}\nOutput:\n${r.output}` }] }
  }
  if (!prev) return { summary, findings: [], resolved: [] }
  return verdict === 'PASS'
    ? { summary, findings: [], resolved: prev.findings }
    : { summary, findings: prev.findings, resolved: [] }
}

// Gates are keyed so a fix round re-reviews only the ones that failed: fresh
// reviewers oscillate, inventing a new nit each round and never converging.
const qualityTypes = [...QUALITY_ALWAYS, ...Object.keys(ASPECT_AGENTS).filter((a) => aspects.has(a)).map((a) => ASPECT_AGENTS[a])]
const gates = [
  ...qualityTypes.map((t) => ({ key: t, type: t, prompt: () => qualityPrompt(t, impl.redEvidence) })),
  ...(NO_DOMAIN ? [] : [{ key: 'domain', type: A.domainReviewer, prompt: domainPrompt }]),
  ...(VERIFY && aspects.has('code') ? [{ key: VERIFY_SKILL, run: runVerify }] : []),
  // A re-review does not re-run the command.
  ...(EXTERNAL ? [{ key: 'external', type: 'generic', prompt: externalPrompt, schema: EXTERNAL_SCHEMA }] : []),
]
log(`Review: ${gates.length} reviewers — ${gates.map((g) => g.key).join(', ')}`)

phase('Review')
const state = new Map()
const initial = await parallel(gates.map((g) => () => (g.run
  ? g.run(`review:${g.key}`, 'Review')
  : agentR(g.prompt(), { label: `review:${g.key}`, phase: 'Review', schema: g.schema || VERDICT_SCHEMA, ...reviewerRoster(g.type) }))))
// Minors are kept from full reviews only: a re-review verdict replaces the
// gate's state and lists outstanding findings, so it would drop them.
const minor = []
const record = (g, v) => {
  if (v?.ran === false) {
    MISSING_TYPES.add(g.key)
    log(`Review: external review command failed — skipped: ${v.summary}`)
    v = { ...v, findings: [] }
  }
  state.set(g.key, v || deadReviewer(g.key))
  if (v) minor.push(...v.findings.filter((f) => f.severity === 'minor').map((f) => ({ ...f, gate: g.key })))
}
gates.forEach((g, i) => record(g, initial[i]))

const disputes = []
const resolved = []
const outstanding = () => gates.flatMap((g) => blockingOf(state.get(g.key)).map((f) => ({ ...f, gate: g.key })))
const deadGates = () => gates.filter((g) => state.get(g.key).dead)
const handBack = (reason) => ({
  ok: false,
  stage: 'review',
  reason,
  handBack: true,
  blocking: outstanding(),
  deadReviewers: deadGates().map((g) => g.key),
  degraded: [...MISSING_TYPES],
  redEvidence: impl.redEvidence,
  simplify,
  verifyRun,
  disputes,
  resolved,
  verdicts: Object.fromEntries(state),
})

let round = 0
while (true) {
  const blocking = outstanding()
  const dead = deadGates()
  if (!blocking.length && !dead.length) break
  if (round >= FIX_ROUNDS) {
    return handBack(`${blocking.length} blocking finding(s) and ${dead.length} dead reviewer(s) outstanding after ${FIX_ROUNDS} fix rounds`)
  }
  round++
  phase('Fix')
  const failed = gates.filter((g) => blockingOf(state.get(g.key)).length)
  let fix = null
  if (blocking.length) {
    fix = await agentR(fixPrompt(blocking, disputes, round), {
      label: `fix:#${ISSUE}:r${round}`,
      phase: 'Fix',
      schema: FIX_SCHEMA,
      ...implementerRoster(A.implementer),
    })
    if (!fix) return { ok: false, stage: 'fix', reason: 'fixer returned no result', blocking, disputes, resolved }
    if (!fix.committed && !fix.addressed.length && !fix.disputed.length) {
      return { ok: false, stage: 'fix', reason: `fixer changed nothing and disputed nothing: ${fix.summary}`, blocking, disputes, resolved }
    }
    disputes.push(...fix.disputed.map((d) => ({ ...d, round })))
    const g = await gate(`review-fix round ${round}`, `fix${round}`, false)
    if (!g.ok) return { ok: false, stage: 'gate', reason: g.reason, verify: g.verify, blocking, disputes, resolved }
    changedFiles = g.verify.changedFiles
  }

  const again = await parallel([
    ...failed.map((g) => () => (g.run
      ? g.run(`re-review:${g.key}:r${round}`, 'Fix', state.get(g.key))
      : agentR(reReviewPrompt(state.get(g.key), fix, round), {
        label: `re-review:${g.key}:r${round}`,
        phase: 'Fix',
        schema: RE_REVIEW_SCHEMA,
        ...reviewerRoster(g.type),
      }))),
    ...dead.map((g) => () => g.run ? g.run(`review:${g.key}:retry${round}`, 'Fix') : agentR(g.prompt(), {
      label: `review:${g.key}:retry${round}`,
      phase: 'Fix',
      schema: g.schema || VERDICT_SCHEMA,
      ...reviewerRoster(g.type),
    })),
  ])
  failed.forEach((g, i) => {
    state.set(g.key, again[i] || deadReviewer(g.key))
    if (again[i]) resolved.push(...blockingOf({ findings: again[i].resolved }).map((f) => ({ ...f, gate: g.key, round })))
  })
  dead.forEach((g, i) => record(g, again[failed.length + i]))

  // The same fixer would get the same findings and dispute them again. The
  // orchestrator settles a standing dispute against the source.
  if (fix && !fix.addressed.length && fix.disputed.length && outstanding().length) {
    return handBack('the fixer disputed every finding it was given and the reviewers held')
  }
}

return {
  ok: true,
  issue: ISSUE,
  branch: BRANCH,
  implementer: A.implementer || 'generic',
  reviewers: gates.map((g) => g.key),
  degraded: [...MISSING_TYPES],
  fixRounds: round,
  assumptions: impl.assumptions || [],
  redEvidence: impl.redEvidence,
  changedFiles,
  minorFindings: minor,
  simplify,
  verifyRun,
  disputes,
  resolved,
  summaries: Object.fromEntries(gates.map((g) => [g.key, state.get(g.key).summary])),
}
