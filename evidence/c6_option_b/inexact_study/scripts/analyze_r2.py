"""Inexact-kernel impact study, revision 2: STORED DATA ONLY (no worlds, builds or battery runs).

Answers Codex's recheck F1, F3, F4 and F5 (docs/reviews/c6_inexact_study_recheck_codex.md):
- a fixed ten-world inventory, with every input hash-checked; a missing or mismatched input fails;
- the full value walk, with grid-error monitors reported apart from every other value;
- signed decision margins evaluated separately for each engine, with the evaluator's own operator and
  moving thresholds, and per-family flip counts and identities;
- pair-level lock and link decisions, recomputed with NumPy through geomind.c4_detect (the detector's
  own clipping), on the stored grid-dt qualification windows and on the rolling-persistence and
  endpoint windows reconstructed from the stored grid-dt operation frames (validated against the
  stored persistence statistics before use);
- a decision-coverage ledger; reconciliation with the revision-1 SUMMARY.json.

Usage (from the repository root):
  .venv/bin/python evidence/c6_option_b/inexact_study/scripts/analyze_r2.py \
      --repo-root . --study-root evidence/c6_option_b/inexact_study
Writes <study-root>/results_r2/<world>.json, SUMMARY_R2.json and RECONCILIATION_R2.json (refuses to overwrite).
"""
import argparse, gzip, hashlib, json, math, re, sys
from pathlib import Path
import numpy as np

WORLDS = ('smoke_0', 'smoke_1', 'development_0', 'development_1', 'development_2', 'development_3',
          'development_4', 'development_5', 'development_6', 'development_7')
# Exact-engine artifact per world, relative to the repository root ({study} = study root).
EXACT = {
    'smoke_0': 'evidence/c6_option_b/reference_smoke_0/world.json.gz',
    'smoke_1': '{study}/raw_worlds/exact_smoke_1.world.json.gz',
    'development_0': 'evidence/c6_option_b/audited_v3_development_0/world.json.gz',
    'development_1': 'evidence/c6_option_b/quiet_session_20261006_161801/worlds/reference_development_1/world.json.gz',
    **{f'development_{k}': '{study}/raw_worlds/exact_development_%d.world.json.gz' % k for k in range(2, 8)},
}
INEXACT = {w: '{study}/raw_worlds/inexact_%s.world.json.gz' % w for w in WORLDS}

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
        kind = 'monitor' if is_monitor(path) else 'other'
        s = out[kind]; s['floats'] += 1
        if not (math.isfinite(a) and math.isfinite(b)):
            if repr(a) != repr(b): out['discrete'].append([path, 'nonfinite %r vs %r' % (a, b)])
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
            out['digests'] += 1; out['digests_changed'] += a != b
        elif a != b: out['discrete'].append([path, 'string differs'])
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
    for (ctx, path, a, b, members), (_, _, c, d, _) in zip(windows(E), windows(I)):
        s = acc(ctx)
        if ctx.startswith('qualification'):
            frames_e = [(path, a, b)]; frames_i = [(path, c, d)]
            wins = [(path, a, b, c, d)]
        else:
            px, pt, ox, ot = a; qx, qt, rx, rt = c
            # Mapping check: operation frame zero is the prefix endpoint.
            map_ok = bool(np.array_equal(px[-1], ox[0]) and np.array_equal(pt[-1], ot[0]))
            # Validate reconstruction against stored grid-0 persistence statistics (exact engine).
            t = int(path.split('/')[2]); cond = path.split('/')[-1]
            stored = E['turns'][t]['conditions'][cond]['persistence_by_dt'][0]
            worst = 0.; m = np.array(members)
            ew = list(persistence_windows(px, pt, ox, ot)); iw = list(persistence_windows(qx, qt, rx, rt))
            for (i, x, th), row in zip(ew, stored):
                locks = D.locked_pairs(th, DET['lock_std'])
                st = D.window_statistics(x, th, m, 1.0, DET['link_factor'], locks)
                worst = max(worst, max(abs(st[k] - row['stats'][k]) for k in row['stats']))
            check = dict(cell=path, prefix_mapping=map_ok, windows=len(ew), max_abs_stat_difference=worst,
                         valid=map_ok and worst == 0.)
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
        for (fp, X, _), (_, Y, _) in zip(frames_e, frames_i):
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


def analyze(D, name, E, I):
    w = dict(bools=0, ints=0, digests=0, digests_changed=0, discrete=[], monitor=new_stats(), other=new_stats())
    walk(E, I, '', w)
    for k in ('monitor', 'other'):
        w[k]['above_1e10'].sort(key=lambda r: -r[3]); w[k]['above_1e10_count'] = len(w[k]['above_1e10'])
    w['discrete_count'] = len(w['discrete']); w['discrete'] = w['discrete'][:50]
    de = list(decisions(E)); di = {p: (m, ok) for _, p, m, ok in decisions(I)}
    fam = {}
    missing = 0
    for f, p, m, ok in de:
        if p not in di: missing += 1; continue
        mi, oki = di[p]
        ctx = context(p)
        s = fam.setdefault(f, dict(count=0, contexts={}, flips=[], closest=None, min_ratio=None, max_change=0.))
        s['count'] += 1; s['contexts'][ctx] = s['contexts'].get(ctx, 0) + 1
        ch = abs(m - mi); s['max_change'] = max(s['max_change'], ch)
        if ok != oki: s['flips'].append(dict(path=p, margin_exact=m, margin_inexact=mi, passes_exact=ok, passes_inexact=oki))
        row = dict(path=p, context=ctx, margin_exact=m, margin_inexact=mi, change=ch, passes=ok,
                   ratio=(abs(m) / ch) if ch else None)
        if s['closest'] is None or abs(m) < abs(s['closest']['margin_exact']): s['closest'] = row
        if ch and (s['min_ratio'] is None or row['ratio'] < s['min_ratio']['ratio']): s['min_ratio'] = row
    for s in fam.values(): s['flip_count'] = len(s['flips'])
    turns = [{k: [te.get(k), ti.get(k)] for k in ('turn', 'operation_eligible', 'physical_outcome', 'first_loss_time', 'witness_tuple', 'controls_passed')}
             for te, ti in zip(E.get('turns', []), I.get('turns', []))]
    outcomes = dict(invalid=[E.get('invalid'), I.get('invalid')], chain_complete=[E.get('chain_complete'), I.get('chain_complete')],
                    enabled_witness=[E.get('enabled_witness'), I.get('enabled_witness')],
                    link_count=[len(E.get('links', [])), len(I.get('links', []))], turns=turns,
                    initial_qualified=[E['initial_source']['qualification']['qualified'], I['initial_source']['qualification']['qualified']])
    return dict(world=name, values=w, decision_families=fam, decisions_unmatched=missing,
                pair_level=pair_level(D, E, I, name), outcomes=outcomes)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--repo-root', type=Path, required=True); ap.add_argument('--study-root', type=Path, required=True)
    a = ap.parse_args()
    repo, study = a.repo_root.resolve(), a.study_root.resolve()
    sys.path.insert(0, str(repo))
    from geomind import c4_detect as D
    out_dir = study / 'results_r2'
    if out_dir.exists() or (study / 'SUMMARY_R2.json').exists(): raise SystemExit('results_r2 exists; never overwrite')
    raw = {r['path']: r for r in json.loads((study / 'RAW_FILES_OUTSIDE_GIT.json').read_text())['files']}
    inventory = {}
    for w in WORLDS:
        pair = {}
        for engine, table in (('exact', EXACT), ('inexact', INEXACT)):
            p = Path(table[w].replace('{study}', str(study)))
            if not p.is_absolute(): p = repo / p
            if not p.is_file(): raise SystemExit('missing input %s' % p)
            h = sha256(p); rel = str(p.relative_to(study)) if study in p.parents else None
            if rel is not None:
                if rel not in raw or raw[rel]['sha256'] != h or raw[rel]['bytes'] != p.stat().st_size:
                    raise SystemExit('raw inventory mismatch %s' % rel)
            pair[engine] = dict(path=str(p.relative_to(repo)), sha256=h, bytes=p.stat().st_size)
        inventory[w] = pair
    out_dir.mkdir()
    results = {}
    for w in WORLDS:
        E = json.load(gzip.open(repo / inventory[w]['exact']['path']))
        I = json.load(gzip.open(repo / inventory[w]['inexact']['path']))
        r = analyze(D, w, E, I); r['inputs'] = inventory[w]
        (out_dir / (w + '.json')).write_text(json.dumps(r, indent=1, default=float) + '\n')
        results[w] = r; del E, I
        print(w, 'done', flush=True)
    summary = summarize(results, study)
    summary['inventory'] = inventory
    (study / 'SUMMARY_R2.json').write_text(json.dumps(summary, indent=1, default=float) + '\n')
    reconcile(summary, study)


def summarize(results, study):
    agg = dict(worlds=len(results), bools=0, ints=0, digests=0, digests_changed=0, discrete_changes=0,
               monitor=dict(floats=0, changed=0, gt_1e10=0, gt_1e8=0, max_abs=0., max_abs_at=None, max_rel=0., max_rel_at=None),
               other=dict(floats=0, changed=0, gt_1e10=0, gt_1e8=0, max_abs=0., max_abs_at=None, max_rel=0., max_rel_at=None),
               decisions_unmatched=0)
    fams = {}; pairs = {}; outcomes_equal = True
    for w, r in results.items():
        v = r['values']
        for k in ('bools', 'ints', 'digests', 'digests_changed'): agg[k] += v[k]
        agg['discrete_changes'] += v['discrete_count']; agg['decisions_unmatched'] += r['decisions_unmatched']
        for kind in ('monitor', 'other'):
            s, t = v[kind], agg[kind]
            for k in ('floats', 'changed', 'gt_1e10', 'gt_1e8'): t[k] += s[k]
            if s['max_abs'] > t['max_abs']: t['max_abs'], t['max_abs_at'] = s['max_abs'], [w, s['max_abs_path'], s['max_abs_values']]
            if s['max_rel'] > t['max_rel']: t['max_rel'], t['max_rel_at'] = s['max_rel'], [w, s['max_rel_path'], s['max_rel_values']]
        for f, s in r['decision_families'].items():
            t = fams.setdefault(f, dict(count=0, contexts={}, flip_count=0, flips=[], closest=None, min_ratio=None, max_change=0.))
            t['count'] += s['count']; t['flip_count'] += s['flip_count']; t['flips'] += [dict(world=w, **x) for x in s['flips']]
            t['max_change'] = max(t['max_change'], s['max_change'])
            for c, n in s['contexts'].items(): t['contexts'][c] = t['contexts'].get(c, 0) + n
            if s['closest'] and (t['closest'] is None or abs(s['closest']['margin_exact']) < abs(t['closest']['margin_exact'])): t['closest'] = dict(world=w, **s['closest'])
            if s['min_ratio'] and (t['min_ratio'] is None or s['min_ratio']['ratio'] < t['min_ratio']['ratio']): t['min_ratio'] = dict(world=w, **s['min_ratio'])
        for c, s in r['pair_level'].items():
            t = pairs.setdefault(c, dict(windows=0, lock_tests=0, lock_flip_count=0, frames=0, link_tests=0, link_flip_count=0,
                                         closest_lock=None, closest_link=None, validation=[]))
            for k in ('windows', 'lock_tests', 'lock_flip_count', 'frames', 'link_tests', 'link_flip_count'): t[k] += s[k]
            t['validation'] += [dict(world=w, **v) for v in s['validation']]
            if s['closest_lock'] and (t['closest_lock'] is None or abs(s['closest_lock']['margin_exact']) < abs(t['closest_lock']['margin_exact'])): t['closest_lock'] = dict(world=w, **s['closest_lock'])
            if s['closest_link'] and (t['closest_link'] is None or abs(s['closest_link']['margin_rel_exact']) < abs(t['closest_link']['margin_rel_exact'])): t['closest_link'] = dict(world=w, **s['closest_link'])
        o = r['outcomes']
        same = all(x[0] == x[1] for k, x in o.items() if k != 'turns') and all(x[0] == x[1] for t in o['turns'] for x in t.values())
        outcomes_equal = outcomes_equal and same
    for t in pairs.values():
        vs = t['validation']
        t['validation_summary'] = dict(cells=len(vs), all_valid=all(v['valid'] for v in vs),
                                       max_abs_stat_difference=max((v['max_abs_stat_difference'] for v in vs), default=None)) if vs else None
    return dict(kind='DIAGNOSTIC_NO_VERDICT_STORED_DATA_ONLY', aggregate=agg, decision_families=fams, pair_level=pairs,
                recorded_outcomes_identical=outcomes_equal, worlds=list(results))


def reconcile(summary, study):
    old = json.loads((study / 'SUMMARY.json').read_text())['aggregate']; a = summary['aggregate']
    floats = a['monitor']['floats'] + a['other']['floats']; changed = a['monitor']['changed'] + a['other']['changed']
    rows = dict(
        floats=[old['floats'], floats], changed=[old['changed'], changed],
        gt_1e10=[old['gt_1e10'], a['monitor']['gt_1e10'] + a['other']['gt_1e10']],
        gt_1e8=[old['gt_1e8'], a['monitor']['gt_1e8'] + a['other']['gt_1e8']],
        max_abs=[old['max_abs'], max(a['monitor']['max_abs'], a['other']['max_abs'])],
        discrete_changes=[old['discrete_changes'], a['discrete_changes']],
        digests_changed=[old['digests_changed'], a['digests_changed']],
        threshold_decision_instances=[old['decisions'], sum(f['count'] for f in summary['decision_families'].values())],
        pair_lock_tests=[old['lock_pairs'], sum(p['lock_tests'] for p in summary['pair_level'].values())],
        pair_link_tests=[old['link_tests'], sum(p['link_tests'] for p in summary['pair_level'].values())])
    note = {'threshold_decision_instances': 'R2 changes the family definitions: causal floor per grid (3 rows instead of 1), paired gain refinement added, '
            'monitor copies under output_check no longer counted, persistence/endpoint rows unchanged',
            'pair_lock_tests': 'R2 adds reconstructed rolling-persistence windows (grid dt)',
            'pair_link_tests': 'R1 counted link tests once per window frame; R2 counts each distinct stored frame once and adds reconstructed persistence frames'}
    out = dict(rows={k: dict(r1=v[0], r2=v[1], equal=v[0] == v[1], note=note.get(k)) for k, v in rows.items()})
    (study / 'RECONCILIATION_R2.json').write_text(json.dumps(out, indent=1, default=float) + '\n')
    print(json.dumps(out, indent=1, default=float))


if __name__ == '__main__':
    main()
