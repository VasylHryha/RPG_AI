"""POST-HOC, read-only: which part of criterion 5 fails for stored R2-gate candidates? Not predeclared; changes no verdict."""
import gzip, json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[4]
d = json.load(gzip.open(ROOT / 'evidence/c6_r2_design_gate/results.json.gz'))
thr = {'jaccard': 0.9, 'pattern': 0.1}   # frozen C4 recovery thresholds (c4 manifest detector)
out = {'note': 'post-hoc, descriptive, stored development data (entropy 33333); thresholds are the frozen detector values'}
for st in d['steps']:
    if not st['name'].startswith('formation_pass'):
        continue
    for lvl in ('2', '3'):
        rec = []
        for row in st['values'][lvl]['raw']:
            for c in row['candidates']:
                if '5_recovery' in c['failed']:
                    s = c['stats']
                    rec.append({'jac': min(s['recovery_original_to_control'], s['recovery_original_to_kicked'],
                                           s['recovery_control_to_kicked']),
                                'pat': s['recovery_pattern_error'],
                                'only_recovery': c['failed'] == ['5_recovery']})
        if not rec:
            continue
        jac_fail = [r['jac'] < thr['jaccard'] for r in rec]
        pat_fail = [r['pat'] > thr['pattern'] for r in rec]
        out['%s|level%s' % (st['name'], lvl)] = {
            'candidates_failing_recovery': len(rec),
            'membership_fails': int(sum(jac_fail)), 'pattern_fails': int(sum(pat_fail)),
            'membership_only': int(sum(j and not p for j, p in zip(jac_fail, pat_fail))),
            'pattern_only': int(sum(p and not j for j, p in zip(jac_fail, pat_fail))),
            'both': int(sum(j and p for j, p in zip(jac_fail, pat_fail))),
            'median_min_jaccard': float(np.median([r['jac'] for r in rec])),
            'median_pattern_error': float(np.median([r['pat'] for r in rec])),
            'only_recovery_failing': int(sum(r['only_recovery'] for r in rec))}
Path(__file__).with_suffix('.json').write_text(json.dumps(out, indent=1, sort_keys=True))
print(json.dumps(out, indent=1, sort_keys=True))
