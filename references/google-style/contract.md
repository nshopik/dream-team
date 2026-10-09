# gdoc-writer contract

The style contract for gdoc-writer output.

## Contents

- Scope and precedence
- The voice
- The rules that change most writing
- Structure and formatting
- Density
- Length
- Perishable detail
- Accessible, global, inclusive
- References
- Before you call a document done

## Scope and precedence

This governs **documents** - files written for a reader. It does not govern chat replies,
commit messages, or MR descriptions; other conventions own those.

A project's `CLAUDE.md`, an existing house style, or a direct instruction from the user
outranks everything here. Where a repo bans something Google permits (em dashes are the
common one), the repo wins. Match the surrounding document before you match this guide.

## The voice

Aim for a knowledgeable friend who understands what the reader is trying to do. Casual and
natural, not pedantic, not pushy. Clear beats charming. The failure mode to watch for is the stiff,
promotional register - `The API documented by this page may enable the acquisition of
information pertaining to user preferences` for `This API lets you collect data about what
your users like`.

Avoid: buzzwords, cutesiness, pop-culture references, exclamation points, figurative
language, `please` in instructions, `simply` / `easily` / `just` / `quickly`, `let's do X`,
and starting every sentence the same way.

## The rules that change most writing

**Second person.** Address the reader as *you*. Use *we* only for the organization
authoring the doc. Reserve *user* for the user of the software your reader is building.
Decide who *you* is (developer? operator?) and stay consistent.

**Imperative for instructions.** `Click Submit.` The *you* is implied.

**Active voice.** Make clear who performs the action. Passive is acceptable to keep focus
on an object, or when the actor is genuinely unknown.

**Present tense.** `The server sends an acknowledgment`, not `will send`. Future tense is
right only for something that genuinely happens later (`the file is archived the next time
the backup runs`). Avoid hypothetical *would*.

**Timeless.** `now`, `currently`, `new`, `latest`, `soon`, `at present`, `eventually`,
`does not yet` either say nothing or go stale. Describe how the thing works, not how it
changed. Release notes and blog posts are the exception. If you must say *new*, give the
version or date.

**No pre-announcing.** Don't document unreleased features or roadmaps.

**Conditions before instructions.**

> To delete the document, click **Delete**.
> ~~Click **Delete** if you want to delete the document.~~

**Prescriptive, not a menu.** Recommend a path. When several approaches exist, say which
one to take and why.

**Say *must*, *can*, or *might* - not *should*.** *Should* leaves the reader unsure whether
an action is required. Required → *must* or an imperative. Recommended → *we recommend*.
Optional → *can*. Possible outcome → *might*. Describing actual state → say who sets the
value, not that it "should be" the value.

**No excessive claims.** Skip superlatives (*best*, *fastest*, *simplest*, *always*,
*never*) and unqualified *ensure* / *guarantee* / *prevents*; write *helps prevent* and
*designed for*. Cite the source of any performance or cost number.

**No anthropomorphism.** Software doesn't see, know, want, or try. `A Delimiter object
specifies where to split a string`.

**Jargon: write around it, or define it once.** If the term earns its place (readers search
for it), define it in parentheses on first use or link a trusted definition. Otherwise say
the plain thing: *review what worked* over *hold a post-mortem*.

**Paragraphs: one idea, most important part first.** Past 5-6 sentences, a paragraph is
usually carrying two ideas. Don't lengthen sentences to shorten paragraphs.

## Structure and formatting

- **Sentence case** for every title and heading. Headings say what the section contains -
  they are not clever, and they are not promises.
- **Descriptive link text.** Link the thing being linked to, never `here` or `this link`.
  Put the introduction first: `For more information, see X.`
- **Numbered lists for sequences; bulleted lists for everything else; description lists for
  pairs.** Keep items parallel in grammar. Introduce every list with a sentence ending in a
  colon.
- **Procedures:** one action per step, location before action (`In the console, go to X`,
  then `Click Y`), and a stated goal when a step's purpose isn't obvious.
- **Tables** for data with more than one dimension; a list handles one dimension better.
- **Bold** for UI element names. Italics for a term being defined, once.
- **Serial comma.** Unambiguous date formats (`January 5, 2026`, not `1/5/26`).
- **Placeholders** in `UPPERCASE_WITH_UNDERSCORES`, and explain each one below the snippet.
- **Notices** (`Note`, `Caution`, `Warning`) carry information the reader needs but that
  doesn't fit the flow. If the reader always needs it, put it in the prose instead.
- **Fictional examples:** `example.com`, `192.0.2.0/24`, `555-0100` numbers. Never a real
  person, company, or address.

## Density

Emphasis is a budget, not a decoration.

**Readers skim first and read second.** Claim in the first sentence, qualification after
it, never the reverse.

**Bold the claim, not the keyword.** One bolded phrase per paragraph at most, carrying the
sentence a skimmer must land on - three bolded nouns in a paragraph mark nothing. Bend it
for tables, never for prose or bullets: a table is a scan target by construction and needs
no bold at all.

**Code font for identifiers only.** A file, path, command, config key, label, version, or
symbol. Not for emphasis, not for ordinary nouns: every backtick that isn't a real
identifier costs the ones that are.

## Length

**Budget the document before writing it.** An issue digests in two minutes - about 500 words,
enough for context, problem, and next action. A reference or design doc runs wider but not
without limit: under 200 lines stays light reading, and past ~2,000 words a reader starts
skipping instead of skimming. These are targets to write toward, not caps to trim good content
against.

**Less is more.** A section that can lose a sentence without losing a fact loses the
sentence.

**Cut what the reader already has.** A sentence that repeats what the file paths, the diff,
or common knowledge of the tool already shows is cut. Reviewing: flag each one as a cut.

## Perishable detail

A figure nobody re-checks is worse than no figure: the reader trusts it.

**Ask what invalidates it.** If a rerun, release, redeploy, or the next commit changes the
number, it is perishable: profile shares, row counts, current versions, prices, owner names,
"as of today" state, screenshots of a UI still moving.

**Perishable data belongs in the artifact that produced it** - a profile, dashboard, ticket,
commit body, test run. The document keeps the conclusion and says where to regenerate the
evidence.

**A figure recording a decision already taken does not expire.** The A/B that justified an
architecture, the measured reason a default is what it is, the limit a contract promises.
The test is not *is it a number*, it is *what makes it wrong*.

**Reviewing: name it and propose the cut** - which passage, what invalidates it, where the
evidence belongs, what one-line conclusion stays behind. Accurate today is not a reason to
keep it.

## Accessible, global, inclusive

These three pull in the same direction: plain, literal, consistent language.

- Short sentences, simple words, primary meanings. Skip phrasal verbs (`submit` over `send
  in`) and idiom - a global reader and a machine translator both lose them.
- Keep helper words that grammar allows you to drop (`that`, `the`, an explicit relative
  pronoun). They cost nothing and remove ambiguity.
- One term per concept, every time. Synonym variety is a virtue in prose and a defect here.
- Alt text on every image; never carry meaning in color, position, or an icon alone. Don't
  write `see the diagram below` - position is meaningless to a screen reader.
- Gender-neutral by default: *they*, or rewrite. No ableist or violent metaphors.
- Vary the names, pronouns, and roles in examples.

## References

Verbatim guide text in this directory. Grep one when the question is in it; never read one end
to end.

| File | Read it for |
|---|---|
| `word-list.md` | Any single term: *sign in* or *log in*, *allowlist* or *whitelist*. ~700 entries, 120 KB. Entries start at the left margin: `grep -i -A6 '^TERM' word-list.md`. |

## Before you call a document done

Reread once for: unclear actor, banned words, a heading or link that doesn't say what's
behind it, two-idea paragraphs, term drift, stray bold or backticks, perishable figures.
Then the word count against the budget.
