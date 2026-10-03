"""POST-HOC descriptive analysis of the stored two-body run. NOT predeclared; changes no verdict.
Read-only on run/. Question: are the level-2 results an artifact of scoring both levels in absolute time?"""
import glob, gzip, json, collections
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent.parent
C2 = 3.4

def load(pattern):
    return [json.loads(gzip.open(f).read()) for f in sorted(glob.glob(str(HERE / 'run/runs' / pattern)))]

def wrap(a):
    return (a + np.pi) % (2*np.pi) - np.pi

def slope(t, y, lo, hi):
    m = (t >= lo - 1e-9) & (t <= hi + 1e-9)
    return float(np.polyfit(t[m], y[m], 1)[0])

out = {'note': 'post-hoc, descriptive; predeclared verdicts in run/SUMMARY.json are unchanged'}

# (a) early phase rate at offset pi/2 and position-approach rate at offset 0, per own-level time unit
rows = {}
for level, c in ((1, 1.0), (2, C2)):
    for case in ('phase_halfpi', 'phase0'):
        for gap in (0.6, 1.2):
            recs = [r for r in load('L%d_p*_%s_g%.1f_T200.json.gz' % (level, case, gap))]
            ph, ap, R0, rg = [], [], [], []
            for r in recs:
                s = r['series']; t = np.array(s['t'])
                dth = np.unwrap(np.array(s['dtheta']))
                ph.append(slope(t, dth, 0, 3.0 * c))      # rad per C0 over the first 3 own-level time units
                ap.append(slope(t, np.array(s['R']), 0, 3.0 * c))
                R0.append(s['R'][0]); rg.append(np.mean([s['rg_a'][0], s['rg_b'][0]]))
            rows['L%d|%s|g%.1f' % (level, case, gap)] = {
                'n': len(recs), 'median_phase_rate_per_C0': float(np.median(ph)),
                'phase_rate_per_own_time': float(np.median(ph) * c),
                'median_approach_per_C0': float(np.median(ap)),
                'approach_per_own_time_per_part_radius': float(np.median(ap) * c / np.median(rg))}
out['early_rates'] = rows

# (b) long runs: relative-phase evolution over the level-3 horizon, windows in own-level time
longs = load('L2_p*_natural_g*_T1640.json.gz')
by = collections.defaultdict(list)
for r in longs:
    s = r['series']; t = np.array(s['t']); d = np.array(s['dtheta']); dm = np.array(s['dmin'])
    def cm(lo, hi):
        m = (t >= lo) & (t <= hi); z = np.exp(1j*d[m]).mean()
        return float(np.angle(z)), float(np.sqrt(max(-2*np.log(max(abs(z), 1e-300)), 0)))
    m0, s0 = cm(0, 50 * 1.0)
    mE, sE = cm(1640 - 340, 1640)       # last 100 own-level time units
    by[r['gap']].append({'offset0': abs(float(d[0])), 'end_mean_abs': abs(mE), 'end_std': sE,
                         'locked_end': bool(abs(mE) <= 0.5 and sE <= 0.3),
                         'informative': bool(abs(float(d[0])) >= 1.0),
                         'coupled_end': bool(np.all(dm[t >= 1590] < 3.0))})
long_out = {}
for g, v in sorted(by.items()):
    inf = [x for x in v if x['informative']]
    long_out['%.1f' % g] = {
        'n': len(v), 'n_informative_offset': len(inf),
        'locked_end_among_informative': float(np.mean([x['locked_end'] for x in inf])) if inf else None,
        'locked_end_all': float(np.mean([x['locked_end'] for x in v])),
        'median_offset_start': float(np.median([x['offset0'] for x in v])),
        'median_offset_end': float(np.median([x['end_mean_abs'] for x in v])),
        'coupled_end': float(np.mean([x['coupled_end'] for x in v]))}
out['long_runs_last_340_time_units'] = long_out
Path(HERE / 'posthoc/posthoc_scaling.json').write_text(json.dumps(out, indent=1, sort_keys=True))
print(json.dumps(out, indent=1, sort_keys=True))
