#!/usr/bin/env python3
"""PreToolUse gate: reject CHANGELOG entries that rot into MR-body prose.

Fires on Write/Edit of a CHANGELOG*.md. Measures each `-` entry being added and
denies when one runs past a single terse sentence — the rationale/mechanism that
belongs in the commit body or MR leaking up into the changelog line.

Caps are measured from one project's history (2026-08-22): across 45 entries in
the clean pre-rot releases, p90 was 18 words and 0 entries carried a second
sentence; the inflated `[Unreleased]`/`2.1.1` sections reached 94 words with 12
multi-sentence entries. The sentence cap is the sharp discriminator (0 vs 12);
the word cap backstops a runaway single sentence.

The rule prose lives in jit-context.py's <changelog_style> block, injected once
per session on the first CHANGELOG touch. This file only measures and bounces;
the deny message states the violation and the one-line rule.

Allows silently (exit 0) on anything it cannot confidently parse — a false block
is worse than a missed one. On Write it measures only the `[Unreleased]` section,
since shipped release sections are frozen history, not new work.
"""
import json
import re
import sys

CAP_WORDS = 40
CAP_SENTS = 1

RULE = ("A changelog line is one plain, complete sentence — enough to say what "
        "changed, no rationale/benchmarks/metric internals (those go in the commit "
        "body or MR). No bold except a leading `**Breaking:**` or `**Upgrade note:**` prefix. "
        "Rewrite, then re-run.")

CHANGELOG_PATH = re.compile(r'(^|/)CHANGELOG(\.[\w-]+)?\.md$', re.I)
BULLET = re.compile(r'^\s*-\s+\S')
# A `## [x]` release heading; `## [Unreleased]` opens the only editable section.
RELEASE_HEAD = re.compile(r'^##\s+\[([^\]]+)\]')
# `**Breaking:**` or `**Upgrade note:**` as an entry prefix is the only sanctioned bold.
BOLD_PREFIX = re.compile(r'^\s*-\s+\*\*(?:Breaking|Upgrade note):\*\*')
BOLD = re.compile(r'\*\*')


def stray_bold(entry):
    """True if the entry bolds anything but a leading sanctioned prefix."""
    return BOLD.search(BOLD_PREFIX.sub('', entry, count=1)) is not None


def measure(entry):
    """(words, sentences) for one changelog entry line.

    Code spans collapse to one token so `-r`/`-R` does not inflate the count;
    e.g./i.e. are neutralized so their periods do not read as sentence breaks.
    A sentence break is terminal punctuation followed by a capital or opening
    bracket, so an inline clause set off by a comma or em-dash stays one sentence.
    """
    text = re.sub(r'`[^`]*`', 'x', entry.strip())
    text = re.sub(r'\b[ei]\.[eg]\.', 'x', text, flags=re.I)
    words = len(text.split())
    sents = 1 + len(re.findall(r'[.!?]\s+[A-Z(\[“"]', text))
    return words, sents


def unreleased(content):
    """Just the body of the `## [Unreleased]` section of a full file."""
    out, keep = [], False
    for line in content.split('\n'):
        m = RELEASE_HEAD.match(line)
        if m:
            keep = m.group(1).strip().lower() == 'unreleased'
            continue
        if keep:
            out.append(line)
    return '\n'.join(out)


def offenders(lines):
    """(line, words, sentences, reasons) for each entry that violates a rule,
    worst first. reasons names each broken rule for the deny message."""
    hits = []
    for l in lines:
        w, s = measure(l)
        reasons = []
        if s > CAP_SENTS:
            reasons.append(f'{s} sentences')
        if w > CAP_WORDS:
            reasons.append(f'{w} words')
        if stray_bold(l):
            reasons.append('bold')
        if reasons:
            hits.append((l, w, s, reasons))
    hits.sort(key=lambda t: (t[2], t[1]), reverse=True)
    return hits


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    ti = payload.get('tool_input', {})
    path = ti.get('file_path') or ''
    if not CHANGELOG_PATH.search(path):
        return
    # Edit: the added text is new_string. Write: only the Unreleased section is
    # editable; the rest is frozen release history and must not be re-measured.
    if 'new_string' in ti:
        candidate = ti.get('new_string') or ''
    elif 'content' in ti:
        candidate = unreleased(ti.get('content') or '')
    else:
        return
    hits = offenders([l for l in candidate.split('\n') if BULLET.match(l)])
    if not hits:
        return
    worst = hits[:3]
    lines = [f'- {", ".join(r)}: {re.sub(r"`", "", l.strip())[:70]}…'
             for l, w, s, r in worst]
    more = f'\n…and {len(hits) - 3} more.' if len(hits) > 3 else ''
    deny(f'{len(hits)} CHANGELOG entr{"y" if len(hits) == 1 else "ies"} need '
         f'rewriting (cap {CAP_WORDS} words, {CAP_SENTS} sentence, no stray bold):\n'
         + '\n'.join(lines) + more + '\n\n' + RULE)


if __name__ == '__main__':
    main()
