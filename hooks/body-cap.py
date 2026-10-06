#!/usr/bin/env python3
"""PreToolUse gate: over-long bodies, descriptions that outrun the diff they
describe, `--fill` MRs, and MR descriptions that stamp a rung rubric as a
heading/lead-in. Text passed by file is measured the same as
text on the flag.

Reads the hook payload on stdin. Allows silently (exit 0, no output) on anything
it cannot confidently parse — a false block is worse than a missed one.

All rules live in the `scope-mr` and `scope-issue` skills, not here: this file
detects and measures, then quotes back the matching `## <id>` section of the skill for
that kind. Rule edits go to the skill; only detection logic, the caps and deny headers belong here.

Caps derive from measured baselines; the commit that sets a cap records its derivation.
"""
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

CAPS = {'mr': 300, 'issue': 500}

SKILLS_DIR = Path(__file__).resolve().parent.parent / 'skills'
SKILL = {'mr': 'scope-mr', 'issue': 'scope-issue'}
FALLBACK = 'Follow Scoped Commits — https://scopedcommits.com/'

# Prepended to the style block when the body is also over the ceiling. The style
# block itself ships on every body — the content rules apply at any length, and
# gating them behind the ceiling is how a short body made entirely of restatement
# and verification output reaches history unchallenged.
OVER_CAP = "{what} is {n} words — over the {cap}-word ceiling. Rewrite it, then re-run.\n\n"

FILL = ("`--fill` writes the description from the commit message. Drop it, pass the "
        "description explicitly (`--description`, `-f description=`), then re-run.\n\n")


def sections(text):
    """`## id` headings of a markdown document mapped to their body text.

    Any `##` closes the open section; only lowercase-slug ones are kept, so prose
    headings (`## Examples`) end a section without becoming one.
    """
    parts = re.split(r'^##[ \t]+(.*?)[ \t]*$', text, flags=re.M)
    return {k: v.strip() for k, v in zip(parts[1::2], parts[2::2])
            if re.fullmatch(r'[a-z-]+', k)}


def reminder(kind, section):
    """That kind's skill section, wrapped in its style tag."""
    path = SKILLS_DIR / SKILL[kind] / 'SKILL.md'
    try:
        body = sections(path.read_text(encoding='utf-8'))[section]
    except Exception:
        body = FALLBACK
    tag = f'{kind}_style'
    return f'<{tag}>\n{body}\n</{tag}>'


FILL_FLAGS = {'--fill', '--fill-first', '--fill-verbose'}


def uses_fill(cmd):
    """True when --fill is passed as a flag, not merely quoted inside one.

    Call with heredoc bodies already excised: prose about `--fill` is data, and
    denying on it blocks the very description that explains the rule.
    """
    try:
        return bool(FILL_FLAGS.intersection(shlex.split(cmd)))
    except ValueError:
        return False


# `gh api` on a PR/issue itself, only when it sends a body: a read piped into
# `python3 - <<EOF` would otherwise have its script measured as the description.
# The path must be the first argument, or a path quoted in a comment body matches.
# The `(?![/\w])` guards keep sub-resources (comments, notes) out of both forges.
GH_API = (r'\bgh\s+api'
          r'(?=[^\n|;&]*\s(?:-[fF]|--(?:raw-)?field)\s+[\'"]?body=|[^\n|;&]*\s--input\s)'
          r'(?:\s+(?:-X|--method)[\s=]\w+|\s+--[\w-]+)*'
          r'\s+[\'"]?/?repos/[^\s\'"]+/{}(?:/\d+)?[\'"]?(?=\s|$)')

MR_CMD = re.compile(r'\bglab\b(?:[^\n|;&]*\bmerge_requests(?:/\d+)?(?![/\w])'
                    r'|\s+mr\s+(?:create|update|edit)\b)'
                    r'|\bgh\b\s+pr\s+(?:create|edit)\b'
                    r'|' + GH_API.format('pulls'))

ISSUE_CMD = re.compile(r'\bglab\b(?:[^\n|;&]*\bissues(?:/\d+)?(?![/\w])'
                       r'|\s+issue\s+(?:create|update|edit)\b)'
                       r'|\bgh\b\s+issue\s+(?:create|edit)\b'
                       r'|' + GH_API.format('issues'))

# Rung-4 leaders, bounced once in an MR: "deliberately left out" is the one line
# that reliably smuggles unrelated findings into an MR. The explicit phrases are
# specific enough to match anywhere in the prose; the bare "unchanged:"-style
# ones only lead a line, where prose that merely mentions the word cannot reach
# them.
# The prescriptive set is the same smuggling in forward-looking grammar: work
# the diff does not contain, written as an instruction rather than as an
# omission ("a contact point still needs to exist before this delivers").
RUNG4 = re.compile(r"""\b deliberately \s+ (?:unchanged|left|omitted|out)
                     | \b left \s+ (?:as[- ]is|alone|untouched)
                     | \b out \s+ of \s+ scope \s*:
                     | ^\W{0,4} (?:not \s+)? (?:changed|touched|addressed|unchanged
                                       |deferred|postponed)
                       \s*:
                     | \b (?:still \s+ )? needs? \s+ to \s+ be \b
                     | \b still \s+ (?:needs?|requires?|required) \b
                     | \b needs? \s+ to \s+ (?:exist|happen|land|follow)
                     | \b must \s+ (?:first|still|be \s+ (?:created|configured|set))
                     | \b before \s+ this \s+ (?:works|delivers|takes \s+ effect)
                     """, re.X | re.I | re.M)

RUNG4_CONFIRM = ("This MR description claims something was deliberately left out — "
                 "bounced once so the boundary below gets applied. Re-run the same "
                 "command unchanged to pass; otherwise move the item to an issue.\n\n")

# A description that outruns the change it describes is restating the diff. The
# 300-word cap cannot see that: 175 words over a 23-line diff sits well under it.
# Budget scales with the diff; the floor keeps a one-line fix writable.
DIFF_FACTOR = 5
DIFF_FLOOR = 80

OVER_DIFF = ("MR description is {n} words against a {lines}-line diff, over the "
             "{allow}-word budget for a change that size — bounced once so the "
             "judgment gets made. Re-run the same command unchanged to pass; "
             "otherwise cut it to what the diff cannot show.\n\n")


# `cd <path> && glab …` is the shape of every cross-repo forge command. The hook
# runs in the session cwd, so without this the diff budget silently measures the
# wrong repo — and a clean session repo reads as 0 lines, disabling the check.
CD_PREFIX = re.compile(r"""(?:^|[;&|]|\bdo\b|\bthen\b)\s*
                           cd \s+ (?: '([^']+)' | "([^"]+)" | ([^\s;&|]+) )""",
                       re.X)


def cmd_cwd(cmd, at):
    """Directory the forge command runs in: the last `cd` preceding it."""
    path = None
    for m in CD_PREFIX.finditer(cmd, 0, at):
        path = next(g for g in m.groups() if g is not None)
    if not path or path.startswith('-'):
        return None
    path = os.path.expanduser(os.path.expandvars(path))
    return path if os.path.isdir(path) else None


def diff_lines(cwd=None):
    """Lines changed on this branch against its base, or None if unmeasurable."""
    def git(*args):
        try:
            p = subprocess.run(('git',) + args, capture_output=True, text=True,
                               timeout=5, cwd=cwd)
        except (OSError, subprocess.SubprocessError):
            return None
        return p.stdout if p.returncode == 0 else None

    def numstat(*args):
        out = git('diff', '--numstat', *args)
        if out is None:
            return None
        return sum(int(c) for line in out.splitlines()
                   for c in line.split('\t')[:2] if c.isdigit())

    base = None
    for ref in ('origin/HEAD', 'main', 'master'):
        out = git('merge-base', 'HEAD', ref)
        if out and out.strip():
            base = out.strip()
            break
    if not base:
        return None
    committed = numstat(f'{base}..HEAD')
    if committed is None:
        return None
    # An MR is often written before the last commit lands, so the committed
    # range alone reads 0 and every description falls back to the floor. The
    # working tree against HEAD is disjoint from that range; summing them sizes
    # the change the description actually covers.
    return committed + (numstat('HEAD') or 0)

# Rung rubrics stamped as a heading or lead-in. The scope-mr ladder decides what
# to write; naming the rung in the text ("## Look at first", "Decision worth
# challenging:") is the tell the writer stamped the rubric instead of the fact.
# Curated to the skill's own offender list (## mr-style, Never). A content section
# ("## What it does", bullets) is endorsed there, so it is deliberately absent
# here; only the where-to-look and challenge rubrics are banned.
_RUBRIC = (r'look\s+at\s+first'
           r'|where\s+to\s+look(?:\s+first)?'
           r'|(?:a\s+)?decision\s+worth\s+challenging'
           r'|what\s+to\s+challenge'
           r'|challenges?'
           r'|blast\s+radius'
           r'|riskiest\s+part')
MR_RUBRIC = re.compile(
    rf'^\s*#{{1,6}}\s+(?:{_RUBRIC})\s*:?\s*$'        # markdown heading form
    rf'|^\s*(?:[-*]\s+)?(?:{_RUBRIC})\s*:\s',        # lead-in "Rubric: ..." form
    re.I | re.M)

RUBRIC_DENY = ("This MR description names a rung rubric as a heading or lead-in "
               "({hit!r}) — the ladder picks what to write, it never appears in the "
               "text. Rewrite as prose, then re-run.\n\n")

# Never /tmp: a predictable path there can be pre-created as a symlink.
# CLAUDE_PLUGIN_DATA survives plugin updates; the plugin root does not.
SEEN_FILE = Path(os.environ.get('CLAUDE_PLUGIN_DATA')
                 or Path.home() / '.claude' / '.cache') / 'body-cap-seen'


def seen(body, gate):
    """True if this exact body was bounced by this gate before. Records it either way.

    Keyed per gate: a body that trips two of them owes a bounce to each, or the
    re-issue that answers the first silently clears the rest.

    Any I/O failure reports the body as already seen: the gate must never crash
    or nag twice over its own bookkeeping.
    """
    digest = hashlib.sha256(
        (gate + '\n' + '\n'.join(body).strip()).encode()).hexdigest()[:16]
    try:
        prior = SEEN_FILE.read_text(encoding='utf-8').split() \
            if SEEN_FILE.exists() else []
        if digest in prior:
            return True
        SEEN_FILE.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        SEEN_FILE.write_text('\n'.join(prior + [digest]), encoding='utf-8')
    except OSError:
        return True                             # cannot remember — do not nag twice
    return False


def classify(cmd, spans):
    """(kind, offset) of the MR/issue-writing command, or (None, None).

    Matches inside a heredoc body are skipped: that text is data, not shell — a
    script or payload that merely mentions `gh pr create` is not one.
    """
    def first_outside(pattern):
        # Both ends: a match that starts on the command line and reaches into a
        # heredoc body is still reading data as shell.
        return next((m.start() for m in pattern.finditer(cmd)
                     if not any(s <= m.start() < e or s < m.end() <= e
                                for s, e, _ in spans)), None)

    at = first_outside(MR_CMD)
    if at is not None:
        return 'mr', at
    at = first_outside(ISSUE_CMD)
    return ('issue', at) if at is not None else (None, None)


# [^\n]* after the delimiter: a heredoc opener may be followed by more of the
# command (`gh pr create --body-file - <<'MSG' && gh pr view`). Requiring the newline to
# follow the delimiter directly made those bodies invisible, and an unmeasured
# body is allowed silently — the gate failed open.
HEREDOC = re.compile(
    r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1[^\n]*\n(.*?)\n\s*\2\b",
    re.DOTALL)


def without_heredocs(cmd, spans):
    """cmd with every heredoc body blanked out, leaving only shell text."""
    out = list(cmd)
    for start, end, _ in spans:
        out[start:end] = ' ' * (end - start)
    return ''.join(out)


def heredoc_body(spans, after):
    """The first heredoc opened after `after` — the one the command at that
    offset consumes. A command may carry several (`cat <<A` … `gh pr create <<B`);
    taking the first in the string measures the wrong text."""
    return next((body for start, _, body in spans if start > after), None)


# Target of a redirect or `tee` on a heredoc's opener line; group 1 marks an append.
WRITES = re.compile(r"""(>>|\btee\s+-a\s|>|\btee\s)\s*(['"]?)([^\s'"<>;&|]+)\2""")

# Path as typed -> heredoc body, for files this command writes itself (not yet on
# disk when the hook runs). `./f.md` and `f.md` do not match.
WRITTEN = {}


def remember_writes(cmd, spans):
    for start, _, body in spans:
        line_start = cmd.rfind('\n', 0, start) + 1
        for m in WRITES.finditer(cmd, line_start, cmd.find('\n', start)):
            if m.group(1) == '>>' or '-a' in m.group(1):
                body = file_text(m.group(3)) + '\n' + body
            WRITTEN[m.group(3)] = body


def file_text(path):
    """Text of `path`: a file this command writes by heredoc, else disk.
    Unreadable or stdin measures as nothing, the same as a command that carries
    no text at all."""
    if path == '-':
        return ''
    if path in WRITTEN:
        return WRITTEN[path]
    try:
        return Path(path).read_text(encoding='utf-8', errors='replace')
    except OSError:
        return ''


CAT_SUB = re.compile(r"""\$\(\s*cat\s+(['"]?)([^\s'"()]+)\1\s*\)""")


def expand(value):
    """A flag value that is exactly `$(cat <path>)` carries that file's text."""
    m = CAT_SUB.fullmatch(value)
    return file_text(m.group(2)) if m else value


def input_text(path):
    """`gh|glab api --input <file>`: the description or body key of its JSON."""
    try:
        data = json.loads(file_text(path))
    except ValueError:
        return ''
    if not isinstance(data, dict):
        return ''
    text = data.get('description') or data.get('body')
    return text if isinstance(text, str) else ''


def flag_text(cmd, field):
    """Pull the message/description out of explicit flags. `field` is the API
    key that carries it: `body=` on GitHub, where GitLab's `body=` is a note."""
    try:
        parts = shlex.split(cmd)
    except ValueError:
        return None
    out, i = [], 0
    while i < len(parts):
        p = parts[i]
        nxt = parts[i + 1] if i + 1 < len(parts) else None
        # `gh|glab api -F key=@file` expands the @path itself, so the
        # value carries the file rather than the text.
        if p in ('-F', '-f', '--field', '--raw-field') and nxt is not None \
                and nxt.startswith(field):
            v = nxt.split('=', 1)[1]
            out.append(file_text(v[1:]) if v.startswith('@') else expand(v))
            i += 2; continue
        if p == '--input' and nxt is not None:
            out.append(input_text(nxt)); i += 2; continue
        # gh -F body.md. A value carrying '=' is `gh api -F key=value`, whose
        # short flags are the reverse of glab's, not a file.
        if p in ('-F', '--body-file') and nxt is not None and '=' not in nxt:
            out.append(file_text(nxt)); i += 2; continue
        if p.startswith('--body-file='):
            out.append(file_text(p.split('=', 1)[1])); i += 1; continue
        if p in ('-f', '--field', '--raw-field') and nxt is not None:
            i += 2; continue
        if p in ('-d', '--description', '-b', '--body') and nxt is not None:
            out.append(expand(nxt)); i += 2; continue
        if p.startswith('--description=') or p.startswith('--body='):
            out.append(expand(p.split('=', 1)[1]))
        i += 1
    return '\n\n'.join(out) if out else None


# Named keys only. A bare `Word:` opener is ordinary prose — "Deferred:",
# "Note:" — and treating it as a trailer silently drops the line from the count.
TRAILER = re.compile(
    r'^(?:closes|fixes|resolves|refs|references|related|see[- ]also'
    r'|signed-off-by|co-authored-by|reviewed-by|acked-by|tested-by'
    r'|reported-by|suggested-by|part-of|change-id|cc|bug):\s'
    r'|^\(cherry picked from', re.I)
FENCE = re.compile(r'^```.*?^```', re.S | re.M)
TABLE = re.compile(r'^[ \t]*\|.*$', re.M)


def strip_trailers(lines):
    end = len(lines)
    while end and (not lines[end - 1].strip() or TRAILER.match(lines[end - 1])):
        end -= 1
    return lines[:end]


def count(lines):
    # A pasted log, trace or config dump is evidence, not prose: across 484 maintainer
    # issues it carries 32% of the words. An unterminated fence stays counted.
    # Table rows are measurements for the same reason, and charging per cell would
    # price the tabular form above the paragraph it replaces.
    text = FENCE.sub(' ', '\n'.join(strip_trailers(lines)))
    return len(TABLE.sub(' ', text).split())


def main():
    try:
        payload = json.load(sys.stdin)
        cmd = payload.get('tool_input', {}).get('command', '')
    except Exception:
        return
    # Start is at the `<<`.
    spans = [(m.start(), m.end(), m.group(3)) for m in HEREDOC.finditer(cmd)]
    kind, at = classify(cmd, spans)
    if not kind:
        return
    # A denied call runs none of the command. Re-issuing only the PR half of
    # `git push && gh pr create` then runs it without the push before it.
    chained = ('\n\nNothing in this command ran: the steps chained before '
               'it did not happen either.\n') if re.search(r'[;&|]', cmd[:at]) else ''

    def deny(reason):
        emit(permissionDecision="deny", permissionDecisionReason=reason + chained)

    # Checked before the text lookup: --fill puts no description on the command
    # line, so there is nothing for the ceiling check to measure.
    if kind == 'mr' and uses_fill(without_heredocs(cmd, spans)):
        return deny(FILL + reminder('mr', 'fill'))
    remember_writes(cmd, spans)
    # Heredocs blanked: a body shlex cannot split (an apostrophe) hides every flag.
    field = 'body=' if cmd.startswith('gh', at) else 'description='
    shell = without_heredocs(cmd, spans)
    text = heredoc_body(spans, at) or flag_text(shell, field)
    if not text:
        return                                  # editor-based, etc.
    body = text.split('\n')
    n = count(body)
    if not n:
        return
    cap = CAPS[kind]
    over = '' if n <= cap else OVER_CAP.format(
        what={'mr': 'MR description', 'issue': 'Issue description'}[kind],
        n=n, cap=cap)
    out = reminder(kind, f'{kind}-style')
    if over:
        return deny(over + out)
    if kind == 'mr':
        m = MR_RUBRIC.search('\n'.join(strip_trailers(body)))
        if m:
            return deny(RUBRIC_DENY.format(hit=m.group(0).strip()) + out)
        if RUNG4.search('\n'.join(body)) and not seen(body, 'rung4'):
            return deny(RUNG4_CONFIRM + reminder('mr', 'rung-four'))
        lines = diff_lines(cmd_cwd(cmd, at))
        budget = (max(DIFF_FLOOR, DIFF_FACTOR * lines) if lines is not None
                  else None)
        if budget and n > budget and not seen(body, 'budget'):
            return deny(OVER_DIFF.format(n=n, lines=lines, allow=budget) + out)
    emit(additionalContext=out)


# PreToolUse plain stdout never reaches the model; only hookSpecificOutput does.
def emit(**fields):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", **fields}}))


if __name__ == '__main__':
    main()
