"""Development diagnostic (owner-requested): are level-1 units inside level-2 groups fusing because of
contact with other groups, or intrinsically over the level-3 time span? Same groups as design-gate pass 1,
level 3 (purpose 4300, development entropy 33333), each run ALONE for the same horizon and checked with the
same criterion-6 code. Imports committed code read-only; writes only to the scratchpad."""
import gzip, json, sys, time
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
import numpy as np
ROOT = '/Users/new/RiderProjects/ai_RPG_test'
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + '/tools')
import c6_design_gate as gate
from geomind import c6_experiment as ex, c6_levels as levels, c6_native

class Dummy:
    data = {}
    def step(self, *a, **k): pass
    def write(self): pass
    @contextmanager
    def timed(self, *a, **k):
        yield {}

def alone(args):
    t, = args
    owner = ex.set_factors(t['owner'], gate.PROVISIONAL)
    W = max([30*gate.PROVISIONAL[3]] + [30*c.C for c in levels.descendants(owner) if c.children])
    H = max(100*gate.PROVISIONAL[3], W)
    x, th, om = t['x'], t['th'], t['omega']
    x, th, _ = ex.integrate(x, th, om, H - W, c6_native.simulate)
    x, th, (xs, ths) = ex.integrate(x, th, om, W, c6_native.simulate, .2)
    times = H - W + np.arange(len(xs))*.2
    base = ex.c4_manifest()['detector']
    rows = levels.recursive_validity(owner, xs, ths, times, base, top_C=gate.PROVISIONAL[3], observation_W=W)
    return {'paths': [list(map(list, t['source_paths']))],
            'overlap': [float(r['hull_overlap']) for r in rows], 'dynamic_ok': [bool(r['dynamic']['ok']) for r in rows]}

if __name__ == '__main__':
    start = time.perf_counter()
    rec = json.load(gzip.open(ROOT + '/evidence/c6_design_gate/results.json.gz'))
    fp = [s for s in rec['steps'] if s['name'] == 'formation_pass_1'][0]['values']
    worlds3 = (fp.get('3') or fp.get(3))['raw']
    with ProcessPoolExecutor(8) as pool:
        assigned = gate.bank(pool, 3, 30, 4300, gate.PROVISIONAL, False, Dummy())
        # Verify these are exactly the groups the gate used.
        same = all([list(map(list, t['source_paths'])) for t in assigned[i]] ==
                   [list(map(list, p)) for p in worlds3[i]['part_source_paths']] for i in range(30))
        print('rebuilt groups identical to gate pass 1:', same, flush=True)
        if not same:
            raise SystemExit('mismatch: stop')
        flat = [(i, j, t) for i in range(30) for j, t in enumerate(assigned[i])]
        results = list(pool.map(alone, [(t,) for _, _, t in flat]))
    alone_ov = [v for r in results for v in r['overlap']]
    alone_dyn = [v for r in results for v in r['dynamic_ok']]
    inworld_ov = [u['hull_overlap'] for w in worlds3 for g in w['validity'] for u in g['children']]
    # matched per group
    pairs = []
    for (i, j, _), r in zip(flat, results):
        g = worlds3[i]['validity'][j]
        pairs.append((max(u['hull_overlap'] for u in g['children']), max(r['overlap'])))
    out = {'units_alone': len(alone_ov), 'alone_over_0.2': sum(v > .2 for v in alone_ov),
           'alone_median': float(np.median(alone_ov)), 'alone_dynamic_fail': sum(not v for v in alone_dyn),
           'units_in_world': len(inworld_ov), 'in_world_over_0.2': sum(v > .2 for v in inworld_ov),
           'in_world_median': float(np.median(inworld_ov)),
           'groups': len(pairs), 'groups_failing_alone': sum(b > .2 for _, b in pairs),
           'groups_failing_in_world': sum(a > .2 for a, _ in pairs),
           'groups_fail_in_world_but_not_alone': sum(a > .2 and b <= .2 for a, b in pairs),
           'groups_fail_alone_but_not_in_world': sum(b > .2 and a <= .2 for a, b in pairs),
           'seconds': time.perf_counter() - start}
    json.dump({'summary': out, 'per_group_max_overlap_in_world_vs_alone': pairs, 'raw': results},
              open('/private/tmp/claude-501/-Users-new-RiderProjects-ai-RPG-test/a2ba012a-5e55-4b7e-ab29-4f76eb1d2e49/scratchpad/alone_check.json', 'w'))
    print(json.dumps(out, indent=1))
