"""POST-HOC, read-only: geometry vs own frequency of the stored units (the 'table'). Not predeclared; changes no verdict."""
import pickle, sys, json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from geomind.c4_detect import radius_of_gyration
HERE = Path(__file__).resolve().parent.parent
pairs = pickle.load(open(HERE/'run/inputs.pkl', 'rb'))
out = {}
for level in (1, 2):
    units = [t for pair in pairs[level] for t in pair]
    n = np.array([len(t['x']) for t in units])
    rg = np.array([radius_of_gyration(t['x']) for t in units])
    rate = np.array([t['isolated_rate'] for t in units])
    omega_mean = np.array([np.mean(t['omega']) for t in units])
    omega_spread = np.array([np.std(t['omega']) for t in units])
    th = np.array([np.std(np.angle(np.exp(1j*(t['th']-np.angle(np.exp(1j*t['th']).mean()))))) for t in units])
    corr = lambda a, b: float(np.corrcoef(a, b)[0, 1]) if np.std(a) > 0 and np.std(b) > 0 else None
    out['level%d' % level] = {
        'units': len(units), 'elements_min_max': [int(n.min()), int(n.max())],
        'radius_of_gyration': [float(rg.min()), float(np.median(rg)), float(rg.max())],
        'own_collective_rate': {'min': float(rate.min()), 'median': float(np.median(rate)), 'max': float(rate.max()),
                                'std': float(rate.std())},
        'intrinsic_omega_mean_abs_max': float(np.abs(omega_mean).max()),
        'intrinsic_omega_spread_inside_unit': [float(omega_spread.min()), float(omega_spread.max())],
        'internal_phase_spread_rad': [float(th.min()), float(np.median(th)), float(th.max())],
        'corr_size_vs_rate': corr(n, rate), 'corr_size_vs_radius': corr(n, rg), 'corr_radius_vs_rate': corr(rg, rate)}
    # how much do units of the same size look alike (identical copies?) -> spread of radius at fixed size
    by = {}
    for k, r in zip(n, rg):
        by.setdefault(int(k), []).append(r)
    out['level%d' % level]['radius_by_size'] = {str(k): {'n': len(v), 'mean': float(np.mean(v)), 'std': float(np.std(v))}
                                               for k, v in sorted(by.items()) if len(v) >= 2}
Path(__file__).with_suffix('.json').write_text(json.dumps(out, indent=1, sort_keys=True))
print(json.dumps(out, indent=1, sort_keys=True))
