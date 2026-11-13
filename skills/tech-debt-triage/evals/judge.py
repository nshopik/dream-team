#!/usr/bin/env python3
"""Builds the judge prompt for a case, or grades the judge's verdict lines against it; or builds
the step-5 report prompt from the case's canned verdicts, or grades the HTML report against it.

usage: judge.py prompt <case.json> <repo path>
       judge.py grade <case.json> <verdicts.md> [verdicts.md ...]
       judge.py report-prompt <case.json> <repo path> <report.html>
       judge.py report <case.json> <report.html>
"""
import json
from collections import Counter
from datetime import date
from html.parser import HTMLParser
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / 'SKILL.md'


def prompt(case, repo):
    text = SKILL.read_text()
    brief = re.search(r'Judge brief, verbatim:\n\n```\n(.*?)\n```', text, re.S).group(1)
    lines = [f"{c['id']} | {c['claim']} | {c['location']} | {c['removes']}" for c in case['candidates']]
    print(brief.replace('<repo>', repo) + '\n\n' + '\n'.join(lines))


def grade(case, files):
    runs = [dict(re.findall(r'^\W*(C\d+)\s*\|\s*(Act now|Later|Skip)\s*\|', Path(f).read_text(), re.M))
            for f in files]
    fails, splits = 0, []
    for c in case['candidates']:
        want = {'Act now'} if c['expect'] == 'Act now' else {'Later', 'Skip'}
        vs = [r.get(c['id'], 'none') for r in runs]
        top, n = Counter(vs).most_common(1)[0]
        ok = sum(v in want for v in vs) * 2 > len(vs)
        fails += not ok
        if n < len(vs):
            splits.append(f"{c['id']}: {', '.join(vs)}")
        print(f"{c['id']:<4} {'/'.join(sorted(want)):<11} {top if n * 2 > len(vs) else 'split':<8} "
              f"{'PASS' if ok else 'FAIL'}  ({', '.join(vs)})")
    print(f"{len(case['candidates']) - fails}/{len(case['candidates'])} candidates pass by majority "
          f"of {len(files)} runs")
    for line in splits:
        print(f"split: {line}")
    return fails


def report_prompt(case, repo, html):
    step = re.search(r'## 5\. Report\n\n(.*?)\nOpen the file', SKILL.read_text(), re.S).group(1)
    step = re.sub(r'`<scratchpad>/.*?that directory\.', f'`{html}`; `<report dir>` below is `{Path(html).parent}`.',
                  step, flags=re.S)
    step = step.replace('(report-template.html)', f'({SKILL.parent / "report-template.html"})')
    issues = [f"{c['id']}: #{c['issue']} {'filed this run' if c['filed'] else 'covered by an open issue'}"
              for c in case['candidates'] if 'issue' in c]
    print(f"Run step 5 of the tech-debt-triage skill for the repository at {repo}: {case['repo']} "
          f"@ {case['commit']}, {date.today()}, scope: whole repository. Steps 1 to 4 are done; "
          f"their results are below. Write the report and nothing else.\n\n"
          f"Finder candidate lines:\n" + '\n'.join(
              f"{c['id']} | {c['claim']} | {c['location']} | {c['removes']}" for c in case['candidates']) +
          "\n\nJudge verdict lines:\n" + '\n'.join(c['verdict'] for c in case['candidates']) +
          f"\n\nIssues, at {case['forge']}/issues/<N>:\n" + '\n'.join(issues) + '\n\n' + step)


VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}


class Report(HTMLParser):
    """Collects, per Act now card, what the step-5 rules constrain, and tags left unbalanced."""

    def __init__(self):
        super().__init__()
        self.stack, self.cards, self.errors, self.loose = [], {}, [], 0

    def inside(self, cls):
        return any(cls in c for _, c, _ in self.stack)

    def card(self):
        return next((self.cards[i] for t, _, i in self.stack if t == 'article' and i in self.cards), None)

    def handle_starttag(self, tag, attrs):
        a, card = dict(attrs), self.card()
        cls = (a.get('class') or '').split()
        if tag == 'article' and 'card' in cls:
            self.cards[a.get('id')] = {'dt': [], 'wins': 0, 'ba': 0, 'panes': 0, 'files': 0, 'diagrams': 0,
                                       'ids': set(), 'dup': '', 'dup_tags': set()}
        elif card is not None:
            card['ids'].add(a.get('id'))
            card['ba'] += 'ba' in cls
            card['panes'] += 'pane' in cls
            card['files'] += 'files' in cls and not self.inside('pane')
            card['wins'] += tag == 'li' and self.inside('wins')
            if self.inside('dup'):
                card['dup_tags'].add(tag)
        if (tag == 'svg' and not any(t == 'svg' for t, _, _ in self.stack)) or (tag == 'pre' and 'mermaid' in cls):
            if card is None:
                self.loose += 1
            else:
                card['diagrams'] += 1
        if tag not in VOID:
            self.stack.append((tag, cls, a.get('id')))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
            return
        self.errors.append(f"</{tag}> closes <{self.stack[-1][0] if self.stack else 'nothing'}>")
        while any(t == tag for t, _, _ in self.stack) and self.stack.pop()[0] != tag:
            pass

    def handle_data(self, data):
        card = self.card()
        if card is None:
            return
        if self.stack and self.stack[-1][0] == 'dt':
            card['dt'].append(data.strip())
        if self.inside('dup'):
            card['dup'] += data


def report(case, html):
    r = Report()
    r.feed(Path(html).read_text())
    r.close()
    fails = 0
    for c in (c for c in case['candidates'] if 'report' in c):
        card, n, bad = r.cards.get(c['id']), c['id'][1:].lower(), []
        if card is None:
            bad.append('no card')
        else:
            bad += [f'{d} row' for d in card['dt'] if d in ('Evidence', 'Wins')]
            bad += [f"{card['wins']} wins"] * (card['wins'] > 3)
            if c['report'] == 'structural':
                bad += [f'no c{n}-{s} diagram' for s in ('before', 'after') if f'c{n}-{s}' not in card['ids']]
            else:
                bad += [f"{card['diagrams']} diagrams"] * (card['diagrams'] > 0)
            if c['report'] == 'restatement':
                bad += [f"{card['panes']} copy panes"] * (card['panes'] < 2)
                bad += ['card-level file list'] * (card['files'] > 0)
                bad += [f"unescaped <{t}> in a copy" for t in sorted(card['dup_tags'] - {'span'})]
                bad += [f"no {c.get('dup')} in a copy"] * (c.get('dup', '') not in card['dup'])
            if c['report'] == 'none':
                bad += [f"{card['ba']} .ba panes"] * (card['ba'] > 0)
        fails += bool(bad)
        print(f"{c['id']:<4} {c['report']:<11} {'FAIL' if bad else 'PASS'}  {'; '.join(bad)}".rstrip())
    for line in [f'{r.loose} diagrams outside the Act now cards'] * (r.loose > 0) + r.errors + \
            [f'<{t}> never closed' for t, _, _ in r.stack]:
        fails += 1
        print(f'FAIL  {line}')
    return fails


if __name__ == '__main__':
    cmd, case, *args = sys.argv[1:]
    case = json.load(open(case))
    if cmd == 'prompt':
        prompt(case, args[0])
    elif cmd == 'report-prompt':
        report_prompt(case, *args)
    elif cmd == 'report':
        sys.exit(1 if report(case, args[0]) else 0)
    else:
        sys.exit(1 if grade(case, args) else 0)
