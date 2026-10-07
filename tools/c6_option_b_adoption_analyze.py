"""Decision 0032 stored-world analyzer, derived from study R3.
N3: explicit causal lengths/nonnegativity and selection token uniqueness.
N4: count every nonfinite leaf independently per engine; reject matching NaN/Inf.
Preserves R3 coverage limits; never simulates or changes historical receipts.
"""
import argparse, gzip, hashlib, json, math, re, sys
from pathlib import Path
import numpy as np

EXPECTED_DEPENDENCIES = {  # the evaluators this analysis imports or reproduces
    'geomind/c4_detect.py': 'ba7fd94efc0edf028df137dc617666c9b8540b914ab4fca1ce793c84d78aacb8',
    'geomind/c4_model.py': '4fafc161b65914a44dccaca6caefb59a5154079f17f564b4cdc4d44f58c59d33',
    'geomind/c6_r4_field_analysis.py': 'c38cd9878a0f84b5cc6be4aaf0f38a356db650f4e4bb5a4be2757cb0cfff1852',
    'geomind/c6_r4_integrity.py': '8e3af230381d1294bd22d74c4c91b99f64116a86b6d56310533ff610cb60602d',
    'geomind/c6_r4_field_protocol.py': '6a1671be6e810b6666c43b0dc77a71004c0140fc5d7c2113eff1009cc1ecb8f0',
    'geomind/c6_r4_field_assay.py': '1a246728e63c304d633c0f6bdb9d625017389953bf7602ecc61025466aceb3dd',
    'geomind/c6_r4_field.py': 'ee3c775b918f165add8820a253ff87d190b2ec399f56219dcd5030abbf53e4fb',
    'experiments/c6_r4_protocol.json': '559a7638e60c3eeabec3b1a4e25b1f5c6557f32f4f98b1e8430398dba1ec7aab',
    'tools/build_c6_r4.py': '6d25aca638b73194ca656b9df58a0f53615f4a98d163e3780aeedb456452ec6b',  # imported (not run) by c6_r4_field
}
EXPECTED_NUMPY = '2.0.2'
# Physical-state digests that legitimately change with any last-bit change (tools/c6_option_b_compare.py HASH_KEYS).
PHYSICAL_HASH_KEYS = {'identity','initial_identity','initial_ids','qualified_ids','before_ids','after_ids',
    'end_ids','start_ids','operation_end_ids','snapshot_ids','snapshot','introduced_ids','next_operation_ids','source_trace_hash_by_dt'}
DET = dict(min_size=3, link_factor=1.5, membership_jaccard=0.95, shape_cv=0.05, lock_std=0.1,
           freq_tol=0.01, pattern_tol=0.1, recovery_jaccard=0.9)
CAUSAL = dict(floor=1e-08, vanish_absolute=1e-12, vanish_fraction=0.2, relative_spread=0.1)
NUM = dict(position=0.05, phase=0.05, field=0.05, response=0.001)
WINDOW = 30
HASH = re.compile('[0-9a-f]{64}')
COSTS = {'seconds', 'cpu_seconds', 'peak_rss_bytes', 'memory_measurement', 'native_build'}


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------------------------------------------------------- value walk (F4)
def is_monitor(path):
    return '/max_errors/' in path


def walk(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        ka = set(a) - (COSTS if not path else set()); kb = set(b) - (COSTS if not path else set())
        if ka != kb:
            out['discrete'].append([path, 'key inventory differs']); return
        for k in sorted(ka): walk(a[k], b[k], path + '/' + k, out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out['discrete'].append([path, 'length %d vs %d' % (len(a), len(b))]); return
        for i, (x, y) in enumerate(zip(a, b)): walk(x, y, path + '/' + str(i), out)
    elif type(a) is bool or type(b) is bool:
        out['bools'] += 1
        if a is not b: out['discrete'].append([path, 'bool %r vs %r' % (a, b)])
    elif isinstance(a, int) and isinstance(b, int):
        out['ints'] += 1
        if a != b: out['discrete'].append([path, 'int %r vs %r' % (a, b)])
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if type(a) != type(b): out['discrete'].append([path, 'numeric type differs'])
        kind = 'monitor' if is_monitor(path) else 'other'
        s = out[kind]; s['floats'] += 1
        if not (math.isfinite(a) and math.isfinite(b)):
            out['discrete'].append([path, 'nonfinite %r vs %r' % (a, b)])
            return
        e = abs(a - b)
        if e == 0: return
        s['changed'] += 1; s['gt_1e10'] += e > 1e-10; s['gt_1e8'] += e > 1e-8
        if e > s['max_abs']: s['max_abs'], s['max_abs_path'], s['max_abs_values'] = e, path, [a, b]
        rel = e / max(abs(a), abs(b))
        if rel > s['max_rel']: s['max_rel'], s['max_rel_path'], s['max_rel_values'] = rel, path, [a, b]
        if e > 1e-10: s['above_1e10'].append([path, a, b, e, rel])
    elif isinstance(a, str) and isinstance(b, str):
        if HASH.fullmatch(a) and HASH.fullmatch(b):
            if PHYSICAL_HASH_KEYS & set(path.split('/')):
                out['digests'] += 1; out['digests_changed'] += a != b
            else:
                out['semantic_digests'] += 1
                if a != b: out['discrete'].append([path, 'semantic identity digest differs'])
        else:
            out['strings'] += 1
            if a != b: out['discrete'].append([path, 'string differs'])
    elif a is None and b is None:
        pass
    else:
        out['discrete'].append([path, 'type %s vs %s' % (type(a).__name__, type(b).__name__)])


def new_stats():
    return dict(floats=0, changed=0, gt_1e10=0, gt_1e8=0, max_abs=0., max_abs_path=None, max_abs_values=None,
                max_rel=0., max_rel_path=None, max_rel_values=None, above_1e10=[])


# ---------------------------------------------------------------- signed margins (F1, F3)
def context(path):
    if path.startswith('/checks/'): return 'world check list'
    for key, name in (('/persistence_by_dt/', 'rolling persistence'), ('/endpoint_qualification/', 'endpoint qualification'),
                      ('/before_formation/', 'before-formation qualification'), ('/episodes/', 'post-operation qualification'),
                      ('/initial_source/', 'initial source qualification'), ('/source/', 'operation source (copy of qualification)'),
                      ('/response/', 'operation response descriptor'), ('/before_response', 'before-response descriptor')):
        if key in path: return name
    return 'other'


def decisions(world):
    """Yield (family, path, margin, passes) evaluated with the evaluator's operator; margin >= 0 is the
    passing side except where the operator is strict (passes then needs margin > 0)."""
    def ge(v, t): return v - t, v - t >= 0
    def le(v, t): return t - v, v <= t

    def visit(x, path):
        if isinstance(x, dict):
            st = x.get('stats') if isinstance(x.get('stats'), dict) else None
            if st is not None and 'shape_cv' in st:
                p = path + '/stats'
                yield ('membership_jaccard >= 0.95', p + '/membership_jaccard', *ge(st['membership_jaccard'], DET['membership_jaccard']))
                yield ('shape_cv <= 0.05', p + '/shape_cv', *le(st['shape_cv'], DET['shape_cv']))
                yield ('lock_std <= 0.1 (group)', p + '/lock_std', *le(st['lock_std'], DET['lock_std']))
                yield ('freq_change <= 0.01', p + '/freq_change', *le(st['freq_change'], DET['freq_tol']))
                yield ('pattern_change <= 0.1', p + '/pattern_change', *le(st['pattern_change'], DET['pattern_tol']))
            if 'recovery_by_dt' in x:
                for k, r in enumerate(x['recovery_by_dt']):
                    p = path + '/recovery_by_dt/%d' % k
                    yield ('recovery_jaccard >= 0.9', p + '/recovery_jaccard', *ge(r['recovery_jaccard'], DET['recovery_jaccard']))
                    yield ('recovery_pattern_error <= 0.1', p + '/recovery_pattern_error', *le(r['recovery_pattern_error'], DET['pattern_tol']))
            if 'max_errors' in x and 'scope' in x and path.startswith('/checks/'):
                for k, v in x['max_errors'].items():
                    yield ('grid error %s <= 0.05' % k, path + '/max_errors/' + k, *le(v, NUM[k]))
            if set(x) == {'g_to_m', 'm_to_g'} and isinstance(x['g_to_m'], dict) and 'intact' in x['g_to_m']:
                for direction in ('g_to_m', 'm_to_g'):
                    it, ab = x[direction]['intact'], x[direction]['ablated']; p = path + '/' + direction
                    for k, v in enumerate(it):  # strict: intact > floor, per grid
                        yield ('causal intact > 1e-8 (per grid, strict)', p + '/intact/%d' % k, v - CAUSAL['floor'], v > CAUSAL['floor'])
                    lo = min(it); spread = max(it) - lo; lim = CAUSAL['relative_spread'] * lo
                    yield ('causal spread <= 0.1*min(intact) (moving)', p + '/spread', lim - spread, not spread > lim)
                    alim = max(CAUSAL['vanish_absolute'], CAUSAL['vanish_fraction'] * lo)
                    yield ('causal ablation <= max(1e-12, 0.2*min(intact)) (moving)', p + '/ablated', alim - max(ab), not max(ab) > alim)
            if 'gain_by_dt' in x and 'per_probe_by_dt' in x:
                g = x['gain_by_dt']; e = max(abs(g[0] - g[2]), abs(g[1] - g[2]))
                yield ('descriptor gain refinement <= 0.001', path + '/gain_by_dt', NUM['response'] - e, not e > NUM['response'])
            for k, v in x.items():
                if k not in ('qualification_window', 'operation_frames', 'raw', 'introduced_states', 'qualified_states',
                             'operation_end_states', 'after_states'):
                    yield from visit(v, path + '/' + k)
        elif isinstance(x, list):
            for i, v in enumerate(x): yield from visit(v, path + '/' + str(i))
    yield from visit(world, '')
    # Paired gain refinement (protocol operation(): only for operation-eligible cells).
    for t, cell in enumerate(world.get('turns', [])):
        if not cell.get('operation_eligible'): continue
        gi = np.array(cell['response']['intact']['gain_by_dt'])
        for control in ('no_r', 'no_backreaction'):
            diff = gi - np.array(cell['response'][control]['gain_by_dt'])
            e = float(np.max(np.abs(diff[:2] - diff[2])))
            yield ('paired gain refinement <= 0.001', '/turns/%d/response/intact-%s' % (t, control), NUM['response'] - e, not e > NUM['response'])


# ---------------------------------------------------------------- pair-level decisions (F1, F3)
def cohort_slice(state, flow):
    ns = len(state['fields_real_imag']); off = 2 * ns
    for c in state['cohorts'][:-1]: off += 3 * len(c['theta']) + 2 * ns
    n = len(state['cohorts'][-1]['theta'])
    flow = np.asarray(flow)
    return flow[:, off:off + 2 * n].reshape(-1, n, 2), flow[:, off + 2 * n:off + 3 * n]


def lock_values(D, ths):
    """Circular std per pair with the detector's own clipping (c4_detect.circular_std)."""
    std = D.circular_std(ths[:, None, :] - ths[:, :, None], 0)
    iu = np.triu_indices(ths.shape[1], 1)
    return std[iu]


def link_values(X):
    d = np.linalg.norm(X[:, None, :] - X[None, :, :], axis=-1); np.fill_diagonal(d, np.inf)
    thr = DET['link_factor'] * np.median(d.min(1)); iu = np.triu_indices(len(X), 1)
    return d[iu], thr


def windows(world):
    """Yield (context, path, xs, ths, members_or_None) for every grid-dt window reconstructible from stored data."""
    def records(x, path):
        if isinstance(x, dict):
            if 'qualification_window' in x and 'qualified_states' in x:
                yield path, x
            for k, v in x.items():
                if k not in ('qualification_window', 'operation_frames'): yield from records(v, path + '/' + k)
        elif isinstance(x, list):
            for i, v in enumerate(x): yield from records(v, path + '/' + str(i))
    for path, rec in records(world, ''):
        xs, ths = cohort_slice(rec['qualified_states'][0], rec['qualification_window'])
        yield 'qualification window (grid dt)', path, xs, ths, None
    # Rolling persistence (and the endpoint window, which is its last window) per turn and condition.
    prefixes = [world.get('initial_source')] + [t['episodes']['intact'][0] if t.get('episodes') else None for t in world.get('turns', [])]
    for t, cell in enumerate(world.get('turns', [])):
        source = prefixes[t]
        if source is None: continue
        members = cell['source']['selected_members']
        for cond, rec in cell['conditions'].items():
            px, pt = cohort_slice(source['qualified_states'][0], source['qualification_window'])
            ox, ot = cohort_slice(rec['operation_end_states'][0], rec['operation_frames'])
            yield ('rolling persistence (grid dt, reconstructed)', '/turns/%d/conditions/%s' % (t, cond),
                   (px, pt, ox, ot), None, members)


def persistence_windows(px, pt, ox, ot):
    xs = np.concatenate((px[-WINDOW - 1:-1], ox)); ths = np.concatenate((pt[-WINDOW - 1:-1], ot))
    for i in range(len(ox)):
        yield i, xs[i:i + WINDOW + 1], ths[i:i + WINDOW + 1]


def pair_level(D, E, I, world_name):
    out = {}
    def acc(ctx):
        return out.setdefault(ctx, dict(windows=0, lock_tests=0, lock_flips=[], frames=0, link_tests=0, link_flips=[],
                                        closest_lock=None, closest_link=None, validation=[]))
    we, wi = list(windows(E)), list(windows(I))
    # N2: inventories must match exactly before pairing (no zip truncation).
    if [(r[0], r[1]) for r in we] != [(r[0], r[1]) for r in wi]:
        raise SystemExit('window inventory differs between engines in ' + world_name)
    for (ctx, path, a, b, members), (_, _, c, d, members_i) in zip(we, wi):
        s = acc(ctx)
        if members != members_i: raise SystemExit('persistence members differ between engines at ' + path)
        if ctx.startswith('qualification'):
            frames_e = [(path, a, b)]; frames_i = [(path, c, d)]
            wins = [(path, a, b, c, d)]
        else:
            px, pt, ox, ot = a; qx, qt, rx, rt = c
            t = int(path.split('/')[2]); cond = path.split('/')[-1]; m = np.array(members)
            ew = list(persistence_windows(px, pt, ox, ot)); iw = list(persistence_windows(qx, qt, rx, rt))
            check = dict(cell=path)
            # N2: validate BOTH engines: prefix mapping (operation frame zero is the prefix endpoint) and
            # reproduction of that engine's own stored grid-0 persistence statistics, window by window.
            for tag, W, (fx, ft, gx, gt) in (('exact', E, a), ('inexact', I, c)):
                stored = W['turns'][t]['conditions'][cond]['persistence_by_dt'][0]
                wins_ = list(persistence_windows(fx, ft, gx, gt))
                if len(wins_) != len(stored): raise SystemExit('persistence window count mismatch at %s (%s)' % (path, tag))
                worst = 0.
                for (i, x, th), row in zip(wins_, stored):
                    locks = D.locked_pairs(th, DET['lock_std'])
                    st = D.window_statistics(x, th, m, 1.0, DET['link_factor'], locks)
                    worst = max(worst, max(abs(st[k] - row['stats'][k]) for k in row['stats']))
                check[tag] = dict(prefix_mapping=bool(np.array_equal(fx[-1], gx[0]) and np.array_equal(ft[-1], gt[0])),
                                  windows=len(wins_), max_abs_stat_difference=worst)
            if len(ew) != len(iw): raise SystemExit('window count differs between engines at ' + path)
            check['windows'] = len(ew)
            check['valid'] = all(check[k]['prefix_mapping'] and check[k]['max_abs_stat_difference'] == 0. for k in ('exact', 'inexact'))
            s['validation'].append(check)
            if not check['valid']:
                check['note'] = 'reconstruction does not reproduce stored statistics; cell not counted'
                continue
            wins = [('%s/window/%d' % (path, i), x, th, y, tj) for (i, x, th), (_, y, tj) in zip(ew, iw)]
            frames_e = [('%s/frame/%d' % (path, k), np.concatenate((px[-WINDOW - 1:-1], ox))[k:k + 1], None) for k in range(WINDOW + len(ox))]
            frames_i = [('%s/frame/%d' % (path, k), np.concatenate((qx[-WINDOW - 1:-1], rx))[k:k + 1], None) for k in range(WINDOW + len(rx))]
        for wpath, x, th, y, tj in wins:
            s['windows'] += 1
            le, li = lock_values(D, th), lock_values(D, tj)
            s['lock_tests'] += len(le)
            pe, pi = le <= DET['lock_std'], li <= DET['lock_std']
            for k in np.flatnonzero(pe != pi): s['lock_flips'].append([wpath, int(k), float(le[k]), float(li[k])])
            k = int(np.argmin(np.abs(le - DET['lock_std'])))
            cand = dict(path=wpath, pair_index=k, exact=float(le[k]), inexact=float(li[k]),
                        margin_exact=float(DET['lock_std'] - le[k]), margin_inexact=float(DET['lock_std'] - li[k]),
                        change=float(abs(le[k] - li[k])))
            if s['closest_lock'] is None or abs(cand['margin_exact']) < abs(s['closest_lock']['margin_exact']): s['closest_lock'] = cand
        if len(frames_e) != len(frames_i): raise SystemExit('frame inventory differs at ' + path)
        for (fp, X, _), (_, Y, _) in zip(frames_e, frames_i):
            if len(X) != len(Y): raise SystemExit('frame count differs at ' + fp)
            for xf, yf in zip(X, Y):
                s['frames'] += 1
                de, te = link_values(xf); di, ti = link_values(yf)
                s['link_tests'] += len(de)
                pe, pi = de < te, di < ti
                for k in np.flatnonzero(pe != pi): s['link_flips'].append([fp, int(k)])
                rel_e = (te - de) / te; rel_i = (ti - di) / ti
                k = int(np.argmin(np.abs(rel_e)))
                cand = dict(path=fp, pair_index=k, margin_rel_exact=float(rel_e[k]), margin_rel_inexact=float(rel_i[k]),
                            change_rel=float(abs(rel_e[k] - rel_i[k])))
                if s['closest_link'] is None or abs(cand['margin_rel_exact']) < abs(s['closest_link']['margin_rel_exact']): s['closest_link'] = cand
    for s in out.values():
        s['lock_flip_count'] = len(s['lock_flips']); s['link_flip_count'] = len(s['link_flips'])
        s['lock_flips'] = s['lock_flips'][:50]; s['link_flips'] = s['link_flips'][:50]
    return out


def qualification_records(world):
    """Yield (path, qualification dict, final grid states, perturbations or None) for every stored
    qualification evaluation: qualify_episode records and operation endpoint qualifications."""
    def visit(x, path):
        if isinstance(x, dict):
            if isinstance(x.get('qualification'), dict) and 'qualified_states' in x:
                yield path + '/qualification', x['qualification'], x['qualified_states'], x.get('perturbations')
            if isinstance(x.get('endpoint_qualification'), dict) and 'operation_end_states' in x:
                yield path + '/endpoint_qualification', x['endpoint_qualification'], x['operation_end_states'], None
            for k, v in x.items():
                if k not in ('qualification_window', 'operation_frames', 'raw'): yield from visit(v, path + '/' + k)
        elif isinstance(x, list):
            for i, v in enumerate(x): yield from visit(v, path + '/' + str(i))
    yield from visit(world, '')


def guards(D, world):
    """R2-F1 guards evaluated on stored data. Yield (family, path, margin, passes)."""
    for k, chk in enumerate(world.get('checks', [])):
        for c, L in enumerate(chk.get('normalization_sizes', [])):
            yield ('GridSet normalization: cohort radius of gyration > 0 (finite)', '/checks/%d/normalization_sizes/%d' % (k, c),
                   L, bool(np.isfinite(L) and L > 0))
    unassessed_perturbations = 0
    for path, q, states, pert in qualification_records(world):
        rows = q.get('candidates', [])
        for r, row in enumerate(rows):
            m = np.array(row['members']); rp = '%s/candidates/%d' % (path, r)
            yield ('candidate minimum size: members >= 3 (integer)', rp + '/size', len(m) - DET['min_size'], len(m) >= DET['min_size'])
            for g, st in enumerate(states):
                X = np.array(st['cohorts'][-1]['x'])[m]
                rg = D.radius_of_gyration(X); sp = float(np.median(D.nn_spacing(X)))
                yield ('candidate geometry: radius of gyration > 0 (final state, each grid, grid-0 members)', rp + '/grid/%d/rg' % g, rg, rg > 0)
                yield ('candidate geometry: median nearest spacing > 0 (final state, each grid, grid-0 members)', rp + '/grid/%d/spacing' % g, sp, sp > 0)
                if 'recovery_by_dt' in row:
                    yield ('recovery kick: median member spacing > 0 (each grid)', rp + '/grid/%d/kick_spacing' % g, sp, bool(np.isfinite(sp) and sp > 0))
            if 'recovery_by_dt' in row:
                if pert is None:
                    unassessed_perturbations += 1; continue
                dx = np.array(pert['position'])[m]; norm = float(np.sqrt(np.mean(np.sum(dx * dx, axis=1))))
                yield ('recovery position-probe norm > 0', rp + '/position_norm', norm, norm > 0)
                d = np.array(pert['phase'])[m]; d = d - d.mean(); norm = float(np.sqrt(np.mean(d * d)))
                yield ('recovery phase-probe norm > 0 (normalize_phase)', rp + '/phase_norm', norm, norm > 0)
        if q.get('causal'):
            sel = np.array(q['selected_members'])
            if pert is not None:
                d = np.array(pert['probe'])[sel]; d = d - d.mean(); norm = float(np.sqrt(np.mean(d * d)))
                yield ('causal phase-probe norm > 0 (normalize_phase)', path + '/causal/probe_norm', norm, norm > 0)
            else:
                unassessed_perturbations += 1
            for direction in ('g_to_m', 'm_to_g'):
                values=q['causal'][direction];it=values['intact'];ab=values['ablated']
                base=path+'/causal/'+direction
                yield ('causal input lengths: intact and ablated each have 3 grids', base+'/lengths', 0., len(it)==3 and len(ab)==3)
                yield ('causal inputs nonnegative and finite: >= 0', base+'/nonnegative', min(it+ab,default=-1.),
                       bool(it+ab) and bool(np.isfinite(it+ab).all()) and min(it+ab)>=0)
                if len(it)!=3 or len(ab)!=3:continue
                dec = [v > CAUSAL['floor'] for v in it]
                yield ('causal grid agreement: per-grid floor decisions identical', path + '/causal/' + direction + '/agreement',
                       min(abs(v - CAUSAL['floor']) for v in it), len(set(dec)) == 1)
        # Discrete selection, recomputed from stored rows and tokens (select_accepted), compared with the stored choice.
        accepted = [row for row in rows if row.get('accepted')]
        tokens = states[0]['cohorts'][-1]['tokens']
        yield ('selection tokens unique: no duplicate priorities', path+'/tokens_unique', 0., len(set(tokens))==len(tokens))
        chosen = min(accepted, key=lambda r: (-len(r['members']), tuple(sorted(tokens[i] for i in r['members'])))) if accepted else None
        stored = q.get('selected_members')
        yield ('selection: recomputed select_accepted equals stored selected_members', path + '/selection', 0,
               (chosen['members'] if chosen else None) == stored)
    # Grid-agreement composites derivable from stored per-grid values.
    for path, q, states, pert in qualification_records(world):
        for r, row in enumerate(q.get('candidates', [])):
            if 'recovery_by_dt' not in row: continue
            rec = row['recovery_by_dt']
            ok = [x['recovery_jaccard'] >= DET['recovery_jaccard'] and x['recovery_pattern_error'] <= DET['pattern_tol'] for x in rec]
            margin = min(min(abs(x['recovery_jaccard'] - DET['recovery_jaccard']), abs(DET['pattern_tol'] - x['recovery_pattern_error'])) for x in rec)
            yield ('recovery grid agreement: per-grid recovered decisions identical', '%s/candidates/%d/recovery_agreement' % (path, r), margin, len(set(ok)) == 1)
    crit = (('membership_jaccard', 'ge', 'membership_jaccard'), ('shape_cv', 'le', 'shape_cv'), ('lock_std', 'le', 'lock_std'),
            ('freq_change', 'le', 'freq_tol'), ('pattern_change', 'le', 'pattern_tol'))
    for t, cell in enumerate(world.get('turns', [])):
        for cond, rec in cell['conditions'].items():
            grids = rec['persistence_by_dt']; masks = []; margin = math.inf
            for rows in grids:
                mask = []
                for row in rows:
                    st = row['stats']; ok = True
                    for key, op, thr in crit:
                        m_ = st[key] - DET[thr] if op == 'ge' else DET[thr] - st[key]
                        ok = ok and m_ >= 0; margin = min(margin, abs(m_))
                    if ok != row['passed']: raise SystemExit('stored persistence pass flag disagrees with its statistics at turn %d %s' % (t, cond))
                    mask.append(ok)
                masks.append(mask)
            yield ('persistence grid agreement: per-grid window masks identical', '/turns/%d/conditions/%s/persistence_agreement' % (t, cond),
                   margin, masks[1:] == [masks[0], masks[0]])
    yield ('_unassessed_perturbation_contexts', '', unassessed_perturbations, True)


def stored_record_validation(A, world):
    """Run c6_r4_field_analysis.validate_world on the stored world (validation of stored records only;
    no simulation). Count publication_valid calls and their results."""
    calls = []
    original = A.publication_valid
    def counting(q, expected=None):
        ok = original(q, expected); calls.append(bool(ok)); return ok
    A.publication_valid = counting
    try:
        try:
            A.validate_world(world); result = 'PASS'
        except Exception as error:
            result = '%s: %s' % (type(error).__name__, error)
    finally:
        A.publication_valid = original
    return dict(validate_world=result, publication_valid_calls=len(calls), publication_valid_true=sum(calls),
                chain_checked=bool(world.get('chain_complete')))


def pair_families(name, gen_e, gen_i):
    de = list(gen_e); di = {p: (m, ok) for _, p, m, ok in gen_i}
    if len(di) != len(de): raise SystemExit('decision inventory differs between engines in ' + name)
    fam = {}
    for f, p, m, ok in de:
        if p not in di: raise SystemExit('decision %s missing in inexact engine (%s)' % (p, name))
        mi, oki = di[p]; ctx = context(p)
        s = fam.setdefault(f, dict(count=0, contexts={}, flips=[], failing_both=0, closest=None, min_ratio=None, max_change=0.))
        s['count'] += 1; s['contexts'][ctx] = s['contexts'].get(ctx, 0) + 1
        ch = abs(m - mi); s['max_change'] = max(s['max_change'], ch); s['failing_both'] += (not ok and not oki)
        if ok != oki: s['flips'].append(dict(path=p, margin_exact=m, margin_inexact=mi, passes_exact=ok, passes_inexact=oki))
        row = dict(path=p, context=ctx, margin_exact=m, margin_inexact=mi, change=ch, passes=ok, ratio=(abs(m) / ch) if ch else None)
        if s['closest'] is None or abs(m) < abs(s['closest']['margin_exact']): s['closest'] = row
        if ch and (s['min_ratio'] is None or row['ratio'] < s['min_ratio']['ratio']): s['min_ratio'] = row
    for s in fam.values(): s['flip_count'] = len(s['flips'])
    return fam


def analyze(D, A, name, E, I):
    w = dict(bools=0, ints=0, strings=0, digests=0, digests_changed=0, semantic_digests=0, discrete=[], monitor=new_stats(), other=new_stats())
    walk(E, I, '', w)
    w['nonfinite_counts']={'exact':count_nonfinite(E),'inexact':count_nonfinite(I)}
    for k in ('monitor', 'other'):
        w[k]['above_1e10'].sort(key=lambda r: -r[3]); w[k]['above_1e10_count'] = len(w[k]['above_1e10'])
    w['discrete_count'] = len(w['discrete']); w['discrete'] = w['discrete'][:50]
    fam = pair_families(name, decisions(E), decisions(I))
    ge, gi = list(guards(D, E)), list(guards(D, I))
    unassessed = [g for g in ge if g[0].startswith('_')][0][2]
    guard_fam = pair_families(name, (g for g in ge if not g[0].startswith('_')), (g for g in gi if not g[0].startswith('_')))
    turns = [{k: [te.get(k), ti.get(k)] for k in ('turn', 'operation_eligible', 'physical_outcome', 'first_loss_time', 'witness_tuple', 'controls_passed')}
             for te, ti in zip(E.get('turns', []), I.get('turns', []))]
    outcomes = dict(invalid=[E.get('invalid'), I.get('invalid')], chain_complete=[E.get('chain_complete'), I.get('chain_complete')],
                    enabled_witness=[E.get('enabled_witness'), I.get('enabled_witness')],
                    link_count=[len(E.get('links', [])), len(I.get('links', []))], turns=turns,
                    initial_qualified=[E['initial_source']['qualification']['qualified'], I['initial_source']['qualification']['qualified']])
    return dict(world=name, values=w, decision_families=fam, guard_families=guard_fam,
                guard_contexts_without_stored_perturbations=unassessed,
                stored_record_validation=dict(exact=stored_record_validation(A, E), inexact=stored_record_validation(A, I)),
                pair_level=pair_level(D, E, I, name), outcomes=outcomes)


def merge_families(results, key):
    fams = {}
    for w, r in results.items():
        for f, s in r[key].items():
            t = fams.setdefault(f, dict(count=0, contexts={}, flip_count=0, flips=[], failing_both=0, closest=None, min_ratio=None, max_change=0.))
            t['count'] += s['count']; t['flip_count'] += s['flip_count']; t['flips'] += [dict(world=w, **x) for x in s['flips']]
            t['failing_both'] += s['failing_both']; t['max_change'] = max(t['max_change'], s['max_change'])
            for c, n in s['contexts'].items(): t['contexts'][c] = t['contexts'].get(c, 0) + n
            if s['closest'] and (t['closest'] is None or abs(s['closest']['margin_exact']) < abs(t['closest']['margin_exact'])): t['closest'] = dict(world=w, **s['closest'])
            if s['min_ratio'] and (t['min_ratio'] is None or s['min_ratio']['ratio'] < t['min_ratio']['ratio']): t['min_ratio'] = dict(world=w, **s['min_ratio'])
    return fams


def summarize(results):
    agg = dict(worlds=len(results), bools=0, ints=0, strings=0, digests=0, digests_changed=0, semantic_digests=0, discrete_changes=0,
               monitor=dict(floats=0, changed=0, gt_1e10=0, gt_1e8=0, max_abs=0., max_abs_at=None, max_rel=0., max_rel_at=None),
               other=dict(floats=0, changed=0, gt_1e10=0, gt_1e8=0, max_abs=0., max_abs_at=None, max_rel=0., max_rel_at=None),
               guard_contexts_without_stored_perturbations=0,nonfinite_counts={'exact':0,'inexact':0})
    pairs = {}; outcomes_equal = True; validation = {}
    for w, r in results.items():
        v = r['values']
        for engine,count in v['nonfinite_counts'].items():agg['nonfinite_counts'][engine]+=count
        for k in ('bools', 'ints', 'strings', 'digests', 'digests_changed', 'semantic_digests'): agg[k] += v[k]
        agg['discrete_changes'] += v['discrete_count']
        agg['guard_contexts_without_stored_perturbations'] += r['guard_contexts_without_stored_perturbations']
        for kind in ('monitor', 'other'):
            s, t = v[kind], agg[kind]
            for k in ('floats', 'changed', 'gt_1e10', 'gt_1e8'): t[k] += s[k]
            if s['max_abs'] > t['max_abs']: t['max_abs'], t['max_abs_at'] = s['max_abs'], [w, s['max_abs_path'], s['max_abs_values']]
            if s['max_rel'] > t['max_rel']: t['max_rel'], t['max_rel_at'] = s['max_rel'], [w, s['max_rel_path'], s['max_rel_values']]
        for c, s in r['pair_level'].items():
            t = pairs.setdefault(c, dict(windows=0, lock_tests=0, lock_flip_count=0, frames=0, link_tests=0, link_flip_count=0,
                                         closest_lock=None, closest_link=None, validation=[]))
            for k in ('windows', 'lock_tests', 'lock_flip_count', 'frames', 'link_tests', 'link_flip_count'): t[k] += s[k]
            t['validation'] += [dict(world=w, **x) for x in s['validation']]
            if s['closest_lock'] and (t['closest_lock'] is None or abs(s['closest_lock']['margin_exact']) < abs(t['closest_lock']['margin_exact'])): t['closest_lock'] = dict(world=w, **s['closest_lock'])
            if s['closest_link'] and (t['closest_link'] is None or abs(s['closest_link']['margin_rel_exact']) < abs(t['closest_link']['margin_rel_exact'])): t['closest_link'] = dict(world=w, **s['closest_link'])
        o = r['outcomes']
        outcomes_equal = outcomes_equal and all(x[0] == x[1] for k, x in o.items() if k != 'turns') and all(x[0] == x[1] for t in o['turns'] for x in t.values())
        validation[w] = r['stored_record_validation']
    for t in pairs.values():
        vs = t.pop('validation')
        t['validation_summary'] = dict(cells=len(vs), all_valid=all(v['valid'] for v in vs), engines_validated=['exact', 'inexact'],
            max_abs_stat_difference=max((max(v['exact']['max_abs_stat_difference'], v['inexact']['max_abs_stat_difference']) for v in vs), default=None)) if vs else None
    return dict(kind='DIAGNOSTIC_NO_VERDICT_STORED_DATA_ONLY', aggregate=agg, decision_families=merge_families(results, 'decision_families'),
                guard_families=merge_families(results, 'guard_families'), pair_level=pairs,
                stored_record_validation=validation, recorded_outcomes_identical=outcomes_equal, worlds=list(results))


def count_nonfinite(value):
    if isinstance(value,dict):return sum(count_nonfinite(v) for v in value.values())
    if isinstance(value,list):return sum(count_nonfinite(v) for v in value)
    return int(isinstance(value,float) and not math.isfinite(value))


def contract(result):
    v=result['values'];reasons=[]
    if v['discrete_count']:reasons.append('discrete values differ')
    if any(v['nonfinite_counts'].values()):reasons.append('nonfinite stored values')
    if v['monitor']['gt_1e8'] or v['other']['gt_1e8']:reasons.append('absolute float difference exceeds 1e-8')
    for group in ('decision_families','guard_families'):
        for name,row in result[group].items():
            if row['flip_count']:reasons.append('predicate flip: '+name)
            if group=='guard_families' and row['failing_both']:reasons.append('invalid guard in both engines: '+name)
    for name,row in result['pair_level'].items():
        if row['lock_flip_count'] or row['link_flip_count']:reasons.append('pair decision flip: '+name)
        if any(not x['valid'] for x in row['validation']):reasons.append('invalid reconstructed persistence: '+name)
    for engine,row in result['stored_record_validation'].items():
        if row['validate_world']!='PASS' or row['publication_valid_calls']!=row['publication_valid_true']:
            reasons.append('stored record validation failed: '+engine)
    return dict(passed=not reasons,reasons=reasons,absolute_tolerance=1e-8)


def analyze_paths(name, exact, candidate):
    # Pin the evaluator inventory BEFORE importing the validation/detection code.
    root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
    for rel,expected in EXPECTED_DEPENDENCIES.items():
        if sha256(root/rel)!=expected:raise RuntimeError('analysis dependency mismatch: '+rel)
    if np.__version__!=EXPECTED_NUMPY:raise RuntimeError('analysis NumPy mismatch')
    proto=json.loads((root/'experiments/c6_r4_protocol.json').read_text())
    if ({k:proto['detector'][k] for k in DET}!=DET or {k:proto['causal'][k] for k in CAUSAL}!=CAUSAL or
        {k:proto['numerics'][k] for k in NUM}!=NUM or proto['window']!=WINDOW or proto['frame_dt']!=1.):
        raise RuntimeError('analysis protocol constants mismatch')
    from geomind import c4_detect as D, c6_r4_field_analysis as A
    E=json.load(gzip.open(exact));I=json.load(gzip.open(candidate))
    result=analyze(D,A,name,E,I);result['contract']=contract(result)
    result['inputs']={engine:dict(path=str(path),sha256=sha256(path),bytes=path.stat().st_size)
                      for engine,path in (('exact',exact),('inexact',candidate))}
    result['dependencies']=EXPECTED_DEPENDENCIES
    result['analyzer_sha256']=sha256(Path(__file__))
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--exact',type=Path,required=True);ap.add_argument('--candidate',type=Path,required=True)
    ap.add_argument('--world',required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    result=analyze_paths(args.world,args.exact,args.candidate)
    with args.output.open('x') as stream:json.dump(result,stream,indent=2,allow_nan=False)
    raise SystemExit(0 if result['contract']['passed'] else 1)
