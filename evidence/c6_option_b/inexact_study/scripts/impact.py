"""Inexact-kernel impact on one world: exact vs inexact artifacts (diagnostic, no verdict).
Usage: impact.py EXACT_world.json.gz INEXACT_world.json.gz OUT.json
Reports (a) deviation per value family, (b) discrete changes, (c) decision margins vs deviation,
(d) endpoint/outcome values side by side."""
import gzip, json, math, re, sys
import numpy as np

DET = dict(min_size=3, link_factor=1.5, membership_jaccard=0.95, shape_cv=0.05, lock_std=0.1,
           freq_tol=0.01, pattern_tol=0.1, recovery_jaccard=0.9)
CAUSAL = dict(floor=1e-08, vanish_absolute=1e-12, vanish_fraction=0.2, relative_spread=0.1)
NUM = dict(position=0.05, phase=0.05, field=0.05, response=0.001)
HASH = re.compile('[0-9a-f]{64}')
COSTS = {'seconds', 'cpu_seconds', 'peak_rss_bytes', 'memory_measurement', 'native_build'}


def family(path):
    parts = [p for p in path.split('/') if p and not p.isdigit()]
    return '/'.join(parts[-3:])


def walk_diff(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        ka = set(a) - (COSTS if not path else set()); kb = set(b) - (COSTS if not path else set())
        if ka != kb:
            out['discrete'].append((path, 'key inventory differs')); return
        for k in sorted(ka): walk_diff(a[k], b[k], path + '/' + k, out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out['discrete'].append((path, 'length %d vs %d' % (len(a), len(b)))); return
        for i, (x, y) in enumerate(zip(a, b)): walk_diff(x, y, path + '/' + str(i), out)
    elif type(a) is bool or type(b) is bool:
        out['bools'] += 1
        if a is not b: out['discrete'].append((path, 'bool %r vs %r' % (a, b)))
    elif isinstance(a, int) and isinstance(b, int):
        out['ints'] += 1
        if a != b: out['discrete'].append((path, 'int %r vs %r' % (a, b)))
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        out['floats'] += 1
        if not (math.isfinite(a) and math.isfinite(b)):
            if not (a == b or (math.isnan(a) and math.isnan(b))): out['discrete'].append((path, 'nonfinite %r vs %r' % (a, b)))
            return
        e = abs(a - b)
        if e == 0: return
        out['changed'] += 1
        r = e / max(abs(a), abs(b))
        f = out['families'].setdefault(family(path), dict(n=0, max_abs=0., max_rel=0., gt_1e10=0, gt_1e8=0, worst=None))
        f['n'] += 1
        if e > f['max_abs']: f['max_abs'] = e; f['worst'] = path
        f['max_rel'] = max(f['max_rel'], r)
        f['gt_1e10'] += e > 1e-10; f['gt_1e8'] += e > 1e-8
        out['gt_1e10'] += e > 1e-10; out['gt_1e8'] += e > 1e-8
        if e > out['max_abs']: out['max_abs'] = e; out['max_abs_path'] = path
    elif isinstance(a, str) and isinstance(b, str):
        if HASH.fullmatch(a) and HASH.fullmatch(b):
            out['digests'] += 1; out['digests_changed'] += a != b
        else:
            out['strings'] += 1
            if a != b: out['discrete'].append((path, 'string %r vs %r' % (a[:60], b[:60])))
    elif a is None and b is None:
        pass
    else:
        out['discrete'].append((path, 'type %s vs %s' % (type(a).__name__, type(b).__name__)))


def get(d, path):
    for p in path.split('/')[1:]:
        d = d[int(p)] if isinstance(d, list) else d[p]
    return d


def margins(world):
    """Yield (path, kind, statistic value, threshold, signed margin: positive = passes side)."""
    def visit(x, path):
        if isinstance(x, dict):
            st = x.get('stats') if isinstance(x.get('stats'), dict) else None
            if st is not None and 'shape_cv' in st:
                p = path + '/stats'
                yield p + '/membership_jaccard', 'membership_jaccard', st['membership_jaccard'], DET['membership_jaccard'], st['membership_jaccard'] - DET['membership_jaccard']
                yield p + '/shape_cv', 'shape_cv', st['shape_cv'], DET['shape_cv'], DET['shape_cv'] - st['shape_cv']
                yield p + '/lock_std', 'lock_std', st['lock_std'], DET['lock_std'], DET['lock_std'] - st['lock_std']
                yield p + '/freq_change', 'freq_change', st['freq_change'], DET['freq_tol'], DET['freq_tol'] - st['freq_change']
                yield p + '/pattern_change', 'pattern_change', st['pattern_change'], DET['pattern_tol'], DET['pattern_tol'] - st['pattern_change']
            if 'recovery_by_dt' in x:
                for k, r in enumerate(x['recovery_by_dt']):
                    p = path + '/recovery_by_dt/' + str(k)
                    yield p + '/recovery_jaccard', 'recovery_jaccard', r['recovery_jaccard'], DET['recovery_jaccard'], r['recovery_jaccard'] - DET['recovery_jaccard']
                    yield p + '/recovery_pattern_error', 'recovery_pattern_error', r['recovery_pattern_error'], DET['pattern_tol'], DET['pattern_tol'] - r['recovery_pattern_error']
            if 'max_errors' in x and 'scope' in x:
                for k, v in x['max_errors'].items():
                    yield path + '/max_errors/' + k, 'grid_error_' + k, v, NUM[k], NUM[k] - v
            if set(x) == {'g_to_m', 'm_to_g'} and isinstance(x['g_to_m'], dict) and 'intact' in x['g_to_m']:
                for direction in ('g_to_m', 'm_to_g'):
                    it, ab = x[direction]['intact'], x[direction]['ablated']; p = path + '/' + direction
                    lo = min(it)
                    yield p + '/intact_floor', 'causal_floor(log10 ratio)', lo, CAUSAL['floor'], math.log10(lo / CAUSAL['floor']) if lo > 0 else -math.inf
                    yield p + '/intact_spread', 'causal_spread', max(it) - lo, CAUSAL['relative_spread'] * lo, CAUSAL['relative_spread'] * lo - (max(it) - lo)
                    lim = max(CAUSAL['vanish_absolute'], CAUSAL['vanish_fraction'] * lo)
                    yield p + '/ablated', 'causal_ablation', max(ab), lim, lim - max(ab)
            if 'gain_by_dt' in x:
                g = x['gain_by_dt']; e = max(abs(g[0] - g[2]), abs(g[1] - g[2]))
                yield path + '/gain_by_dt', 'response_refinement', e, NUM['response'], NUM['response'] - e
            for k, v in x.items(): yield from visit(v, path + '/' + k)
        elif isinstance(x, list):
            for i, v in enumerate(x): yield from visit(v, path + '/' + str(i))
    yield from visit(world, '')


def windows(world):
    """Qualification windows (grid dt only): yield (path, xs (F,N,2), ths (F,N))."""
    def visit(x, path):
        if isinstance(x, dict):
            if 'qualification_window' in x and 'qualified_states' in x:
                st = x['qualified_states'][0]; ns = len(st['fields_real_imag'])
                flow = np.array(x['qualification_window']); off = 2 * ns
                for c in st['cohorts'][:-1]: off += 3 * len(c['theta']) + 2 * ns
                n = len(st['cohorts'][-1]['theta'])
                yield path, flow[:, off:off + 2 * n].reshape(-1, n, 2), flow[:, off + 2 * n:off + 3 * n]
            for k, v in x.items():
                if k not in ('qualification_window',): yield from visit(v, path + '/' + k)
        elif isinstance(x, list):
            for i, v in enumerate(x): yield from visit(v, path + '/' + str(i))
    yield from visit(world, '')


def pair_quantities(xs, ths):
    """Underlying detector pair decisions: lock circular std vs 0.1 (all pairs) and link distance
    vs 1.5 * median nearest spacing (every frame). Return arrays of signed relative margins."""
    d = ths[:, None, :] - ths[:, :, None]
    lock = np.sqrt(-2 * np.log(np.abs(np.exp(1j * d).mean(0)).clip(1e-300)))
    iu = np.triu_indices(ths.shape[1], 1)
    lock_v = lock[iu]
    link = []
    for X in xs:
        dd = np.linalg.norm(X[:, None, :] - X[None, :, :], axis=-1); np.fill_diagonal(dd, np.inf)
        thr = DET['link_factor'] * np.median(dd.min(1)); link.append((dd[iu], thr))
    return lock_v, link


def main(exact_path, inexact_path, out_path):
    E = json.load(gzip.open(exact_path)); I = json.load(gzip.open(inexact_path))
    out = dict(bools=0, ints=0, floats=0, strings=0, digests=0, digests_changed=0, changed=0,
               gt_1e10=0, gt_1e8=0, max_abs=0., max_abs_path=None, families={}, discrete=[])
    walk_diff(E, I, '', out)
    out['discrete_changes'] = len(out['discrete']); out['discrete'] = out['discrete'][:50]
    rows = []
    for path, kind, value, thr, margin in margins(E):
        try: other = get(I, path)
        except Exception: other = None
        if kind == 'causal_floor(log10 ratio)':
            iv = get(I, path.rsplit('/', 1)[0] + '/intact'); other = min(iv)
        elif kind == 'causal_spread':
            iv = get(I, path.rsplit('/', 1)[0] + '/intact'); other = max(iv) - min(iv)
        elif kind == 'causal_ablation':
            other = max(get(I, path.rsplit('/', 1)[0] + '/ablated'))
        elif kind == 'response_refinement':
            g = other; other = max(abs(g[0] - g[2]), abs(g[1] - g[2]))
        dev = abs(value - other) if isinstance(other, (int, float)) else None
        rows.append(dict(path=path, kind=kind, value=value, threshold=thr, margin=margin,
                         deviation=dev, passes=margin >= 0 if kind != 'causal_floor(log10 ratio)' else margin > 0,
                         margin_over_deviation=(abs(margin) / dev if dev else None)))
    # Underlying pair-level decisions in every qualification window.
    pair = dict(windows=0, lock_pairs=0, link_tests=0, lock_flips=0, link_flips=0,
                closest_lock=None, closest_link=None)
    for (path, xe, te), (_, xi, ti) in zip(windows(E), windows(I)):
        pair['windows'] += 1
        le, linke = pair_quantities(xe, te); li, linki = pair_quantities(xi, ti)
        pair['lock_pairs'] += len(le)
        pair['lock_flips'] += int(np.sum((le <= DET['lock_std']) != (li <= DET['lock_std'])))
        k = int(np.argmin(np.abs(le - DET['lock_std']))); m = abs(le[k] - DET['lock_std']); dv = abs(le[k] - li[k])
        if pair['closest_lock'] is None or m < pair['closest_lock']['margin']:
            pair['closest_lock'] = dict(path=path, margin=float(m), deviation=float(dv), max_window_deviation=float(np.max(np.abs(le - li))))
        for (de, the), (di, thi) in zip(linke, linki):
            pair['link_tests'] += len(de)
            pair['link_flips'] += int(np.sum((de < the) != (di < thi)))
            fe = np.isfinite(de)
            rel = np.abs(de[fe] - the) / the
            k = int(np.argmin(rel)); m = float(rel[k])
            dv = float(abs((de[fe][k] - the) - (di[fe][k] - thi)) / the)
            if pair['closest_link'] is None or m < pair['closest_link']['margin_rel']:
                pair['closest_link'] = dict(path=path, margin_rel=m, deviation_rel=dv)
    finite = [r for r in rows if math.isfinite(r['margin'])]
    by_margin = sorted(finite, key=lambda r: abs(r['margin']))
    with_dev = [r for r in finite if r['deviation']]
    by_ratio = sorted(with_dev, key=lambda r: r['margin_over_deviation'])
    flips = [r for r in rows if r['deviation'] is not None and
             ((r['margin'] >= 0) != ((r['margin'] - (r['deviation'] if r['margin'] >= 0 else -r['deviation'])) >= 0))]
    summ = {}
    for r in finite:
        s = summ.setdefault(r['kind'], dict(n=0, min_abs_margin=math.inf, max_dev=0., min_ratio=math.inf))
        s['n'] += 1; s['min_abs_margin'] = min(s['min_abs_margin'], abs(r['margin']))
        if r['deviation']: s['max_dev'] = max(s['max_dev'], r['deviation']); s['min_ratio'] = min(s['min_ratio'], r['margin_over_deviation'])
    CONT = {'shape_cv', 'lock_std', 'freq_change', 'pattern_change', 'recovery_pattern_error', 'causal_spread',
            'causal_ablation', 'grid_error_position', 'grid_error_phase', 'grid_error_field', 'response_refinement'}
    edges = [1e-12, 1e-10, 1e-8, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
    hist = {str(e): sum(1 for r in finite if r['kind'] in CONT and abs(r['margin']) < e) for e in edges}
    devs = [r['deviation'] for r in finite if r['kind'] in CONT and r['deviation'] is not None and not r['kind'].startswith('grid_error')]
    out['margin_histogram'] = dict(continuous_decisions=sum(1 for r in finite if r['kind'] in CONT), below=hist,
                                   max_decision_stat_deviation=max(devs) if devs else 0.,
                                   max_grid_spread_at_closest=None)
    out['margins'] = dict(decisions=len(rows), by_kind=summ, closest10=by_margin[:10], lowest_ratio10=by_ratio[:10])
    out['pair_level'] = pair
    keys = ('invalid', 'chain_complete', 'enabled_witness')
    out['endpoints'] = {k: [E.get(k), I.get(k)] for k in keys}
    out['endpoints']['link_count'] = [len(E.get('links', [])), len(I.get('links', []))]
    turns = []
    for te, ti in zip(E.get('turns', []), I.get('turns', [])):
        turns.append({k: [te.get(k), ti.get(k)] for k in ('turn', 'operation_eligible', 'physical_outcome', 'first_loss_time', 'witness_tuple', 'controls_passed')})
    out['endpoints']['turns'] = turns
    out['endpoints']['turn_count'] = [len(E.get('turns', [])), len(I.get('turns', []))]
    out['endpoints']['initial_qualified'] = [E['initial_source']['qualification']['qualified'], I['initial_source']['qualification']['qualified']]
    # Horizon: deviation per operation frame (1 s apart, 100 s exposure) per turn and condition.
    horizon = []
    for t, (te, ti) in enumerate(zip(E.get('turns', []), I.get('turns', []))):
        for cond, re_ in te.get('conditions', {}).items():
            fe = np.array(re_['operation_frames']); fi = np.array(ti['conditions'][cond]['operation_frames'])
            dev = np.abs(fe - fi).max(axis=1)
            q = len(dev) // 4
            horizon.append(dict(turn=t + 1, condition=cond, frames=len(dev), first_quarter=float(dev[:q].max()),
                                last_quarter=float(dev[-q:].max()), at_10s=float(dev[min(10, len(dev) - 1)]),
                                at_50s=float(dev[min(50, len(dev) - 1)]), at_end=float(dev[-1])))
    out['horizon'] = horizon
    out['cpu_seconds'] = [E.get('cpu_seconds'), I.get('cpu_seconds')]; out['seconds'] = [E.get('seconds'), I.get('seconds')]
    json.dump(out, open(out_path, 'w'), indent=1, default=float)
    print(json.dumps(dict(world=out_path, max_abs=out['max_abs'], changed=out['changed'], gt_1e10=out['gt_1e10'], gt_1e8=out['gt_1e8'],
                          discrete_changes=out['discrete_changes'], decisions=len(rows),
                          lowest_ratio=by_ratio[0]['margin_over_deviation'] if by_ratio else None,
                          closest=by_margin[0]['margin'] if by_margin else None, pair=pair, endpoints=out['endpoints']), default=float))


if __name__ == '__main__':
    main(*sys.argv[1:4])
