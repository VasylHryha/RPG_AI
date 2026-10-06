"""Read trace.json.gz (diagnostic, no verdict): for every strong-path episode (contiguous steps with
any active site having a strong site->O path), report how it ended: the closing element's distance
to O, its phase difference to O, O's held/strong in-lists, and whether roots vanished."""
import gzip, json, math, sys
from pathlib import Path
OUT = Path(__file__).resolve().parent
d = json.load(gzip.open(OUT / 'trace.json.gz'))
S = d['steps']
def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi
def dO(s, i):
    x, y, _ = s['el'][i]; return math.hypot(x - s['O'][0], y - s['O'][1])
rows = []
prev = False
start = None
for k, s in enumerate(S):
    on = bool(s['paths'])
    if on and not prev: start = k
    if prev and not on:
        a = S[k - 1]
        rows.append((start, k))
    prev = on
print('path segments', len(rows), 'total steps with path', sum(bool(s['paths']) for s in S), 'of', len(S))
for a, b in rows[:60]:
    sa, sb = S[b - 1], S[b]
    into = sa['into_O']
    lines = []
    for i in into:
        i = str(i)
        if i in sb['el']:
            lines.append('%s r %.2f->%.2f dphi %.2f->%.2f strong_after %s held_after %s' % (
                i, dO(sa, i), dO(sb, i), wrap(sa['el'][i][2] - sa['O'][2]), wrap(sb['el'][i][2] - sb['O'][2]),
                int(i) in sb['into_O'], int(i) in sb['held_O']))
    print('t %.1f-%.1f (%.1fs) paths %s -> %s roots_before %s roots_after %s | %s' % (
        S[a]['t'], sa['t'], sa['t'] - S[a]['t'], sa['paths'], sb['paths'],
        sorted(sa['roots']), sorted(sb['roots']), ' ; '.join(lines)))
