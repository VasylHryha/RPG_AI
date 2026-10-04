"""Experiment 0e: replacement and connection, two-piece (SPECIFICATION_0E.md, PROPOSAL_0E.md). Exploratory; NOT a milestone, NOT C6 evidence.

    python evidence/tactical_composition_demo/ze_run.py --write-spec   # once, before the registration commit
    python evidence/tactical_composition_demo/ze_run.py --smoke        # reduced run, own entropy, own directory
    python evidence/tactical_composition_demo/ze_run.py --run          # the single recorded run (refuses if the load is above the registered threshold)

Task: revision V3 of `tactics_e2.py` (selected by the fixed rule of dev_0e step 4). Every gate the specification names is enforced here.
"""
import argparse
import hashlib
import json
import os
import secrets
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import tactics as T  # noqa: E402
import tactics_e2 as T2  # noqa: E402
import zd_models as Z  # noqa: E402
import ze_core as E  # noqa: E402
import ze_flat as F  # noqa: E402
from tcd_common import harness  # noqa: E402
from tcd_common.fileio import stream, write_json  # noqa: E402

OPP = ('rush', 'kiter')
RUN_DIRS = ('run_0e', 'smoke_run_0e')
FILES = ('PROPOSAL_0E.md', 'SPECIFICATION_0E.md', 'SPEC_0E.json', 'ze_run.py', 'ze_core.py', 'ze_flat.py', 'tactics_e2.py', 'test_ze.py', 'test_ze_run.py',
         'zd_models.py', 'tactics.py', 'tcd_common/__init__.py', 'tcd_common/fileio.py', 'tcd_common/supervise.py', 'tcd_common/harness.py',
         'dev_0e/DEV_SPEC.json', 'dev_0e/README.md', 'dev_0e/step4_results.json', 'dev_0e/step5_results.json')
BASE = {
    'seeds': 30, 'workers': 8, 'soft_cap': 7200.0, 'hard_cap': 7500.0, 'eval_cap': 600.0, 'max_load_1min': 20.0,
    'task': 'V3', 'train_episodes': 600, 'test_episodes': 100, 'n_states': 3000, 'episodes': 300,
    'L_recipe': {'hidden': 16, 'lr': 0.001, 'wd': 0.0001, 'steps': 32000}, 'J_recipe': {'hidden': 64, 'lr': 0.003, 'wd': 0.001, 'steps': 16000},
    'Fp_recipe': {'head': 'perslot', 'hidden': 32, 'depth': 2, 'lr': 0.003, 'wd': 0.0001, 'steps': 32000},
    'Fflat_recipe': {'head': 'mse', 'hidden': 128, 'depth': 2, 'lr': 0.003, 'wd': 0.0001, 'steps': 32000},
    'ref_distance': None, 'alpha': 0.0125,
    'bars': {'headroom': 0.15, 'headroom_per_opponent': 0.10, 'necessity': 0.03, 'aim_admissible': 0.85, 'move_success': 0.90, 'move_stratum': 0.85,
             'replace_oracle': -0.05, 'replace_J': -0.03, 'cut_raw': 0.02, 'cut_norm': 0.05, 'directed': 0.10, 'function': 0.03, 'repeat_gain': 0.10,
             'repeat_share': 0.80, 'iqr': 0.05, 'fault_abs': 0.03, 'fault_rel': 0.03, 'baseline_gate': 0.03, 'stronger': 0.03},
    'small_faults_abs': [['noise', 0.02], ['wrongfrac', 0.01]], 'small_faults_rel': [['scale', 0.9], ['scale', 1.1]],
    'dose_faults': [['noise', 0.05], ['noise', 0.10], ['wrongfrac', 0.05], ['wrongfrac', 0.10], ['scale', 0.5], ['scale', 2.0]],
    'cuts': ['default', 'wrong', 'zero'], 'require_counts': True, 'min_unique_best': 100, 'min_stratum': 30, 'resamples_note': 'no bootstrap in verdicts: exact order-statistic and Clopper-Pearson intervals only'}
SMOKE = {'seeds': 3, 'workers': 3, 'soft_cap': 1200.0, 'hard_cap': 1400.0, 'eval_cap': 120.0, 'train_episodes': 30, 'test_episodes': 10, 'n_states': 500,
         'episodes': 3, 'steps_cap': 200, 'require_counts': False}


# ---------------------------------------------------------------- one seed

def recipe(cfg, key):
    r = dict(cfg[key])
    if cfg.get('steps_cap'):
        r['steps'] = min(r['steps'], cfg['steps_cap'])
    return r


def cell_assemblies(cfg, L, J, Fp):
    O_a, O_m = E.AimOracle(T2.doctrine_scores_batch(cfg['task'])), E.MoveOracle()
    La, Lm, Ja, Jm = E.AimWired(L, 'L'), E.MoveWired(L, 'L'), E.AimWired(J, 'J'), E.MoveWired(J, 'J')
    W = lambda k, v=None: E.Wire(k, v, cfg['ref_distance'])
    c = {'OO': E.Assembly(O_a, O_m), 'LO': E.Assembly(La, O_m), 'OL': E.Assembly(O_a, Lm), 'LL': E.Assembly(La, Lm),
         'JJ': E.Assembly(Ja, Jm), 'JL': E.Assembly(Ja, Lm), 'LJ': E.Assembly(La, Jm),
         'DO': E.Assembly(E.AimNearest(), O_m), 'OD': E.Assembly(O_a, E.MoveApproach()), 'OO|default': E.Assembly(O_a, O_m, W('default')),
         'FhO': E.Assembly(E.AimFlatOutput(Fp, 'Fh'), O_m), 'OFh': E.Assembly(O_a, E.MoveFlatOutput(Fp, 'Fh'))}
    for k in cfg['cuts']:
        c['LL|'+k] = E.Assembly(La, Lm, W(k))
    for k, v in cfg['small_faults_abs']+cfg['small_faults_rel']+cfg['dose_faults']:
        c['LL|%s_%g' % (k, v)] = E.Assembly(La, Lm, W(k, v))
    for k, v in cfg['small_faults_rel']+cfg['small_faults_abs']:
        c['OO|%s_%g' % (k, v)] = E.Assembly(O_a, O_m, W(k, v))
    fixed_only = {'LL|reverse': E.Assembly(La, Lm, W('reverse')), 'LL|relabel': E.Assembly(La, Lm, W('relabel')), 'LL|sham': E.Assembly(La, Lm, W('sham')),
                  'OO|reverse': E.Assembly(O_a, O_m, W('reverse'))}
    return c, fixed_only


def flat_policy(m):
    def make(rng):
        def policy(own, enemies):
            A = Z.Arrays({'own': own[None], 'enemies': enemies[None]})
            ch, st = m.act(A)
            return st[0], int(ch[0]), False
        return policy
    return make


def weights_of(model):
    if hasattr(model, 'scorer'):
        out = {'scorer_%d' % i: p for i, p in enumerate(model.scorer.params())}
        out.update({'head_%d' % i: p for i, p in enumerate(model.head.params())})
        for k in ('xa', 'ya', 'xm', 'ym'):
            out[k+'_m'], out[k+'_s'] = getattr(model, k).m, getattr(model, k).s
    else:
        out = {'net_%d' % i: p for i, p in enumerate(model.net.params())}
        for k in ('xs', 'ss', 'ms'):
            if hasattr(model, k):
                out[k+'_m'], out[k+'_s'] = getattr(model, k).m, getattr(model, k).s
    return out


def run_seed(cfg, entropy, seed):
    t0 = time.time()
    task = cfg['task']
    wf, mixes = T2.world_fn(task), T2.MIXES
    tr = T2.collect(task, stream(entropy, 1, seed), cfg['train_episodes'])
    te = T2.collect(task, stream(entropy, 2, seed), cfg['test_episodes'])
    A_tr, A_te = Z.Arrays(tr, T2.labels(task, tr)), Z.Arrays(te, T2.labels(task, te))
    if A_tr.n < cfg['n_states']:
        raise ValueError('training pool has %d states, fewer than the registered %d' % (A_tr.n, cfg['n_states']))
    idx = stream(entropy, 4, seed).permutation(A_tr.n)[:cfg['n_states']]
    L = Z.fit_composed(A_tr, idx, recipe(cfg, 'L_recipe'), stream(entropy, 3, seed, 1))
    J = Z.fit_s1(A_tr, idx, recipe(cfg, 'J_recipe'), stream(entropy, 3, seed, 2))
    Fp = F.FlatPlus('perslot').fit(A_tr, idx, recipe(cfg, 'Fp_recipe'), stream(entropy, 3, seed, 3))
    Ff = F.FlatPlus('mse').fit(A_tr, idx, recipe(cfg, 'Fflat_recipe'), stream(entropy, 3, seed, 4))
    h = hashlib.sha256()
    h.update(np.ascontiguousarray(te['own']).tobytes())
    h.update(np.ascontiguousarray(te['enemies']).tobytes())
    out = {'seed': seed, 'train_states': int(A_tr.n), 'test_states': int(A_te.n), 'test_digest': h.hexdigest(), 'fit_seconds': time.time()-t0,
           'params': {'L': L.n_params, 'J': J.n_params, 'Fp': Fp.n_params, 'Fflat': Ff.n_params}, 'oracle_queries': {'J': J.oracle_queries, 'Fp': Fp.oracle_queries},
           'prequal': {}, 'fixed': {}, 'play': {}, 'applied': {}}
    rows = np.arange(A_te.n)
    for name, model in (('L', L), ('J', J)):
        aim, move = E.AimWired(model, name), E.MoveWired(model, name)
        ch = aim.choose(A_te)
        a = E.joint3(ch, E.MoveOracle().step(A_te, A_te.REL[rows, ch]), A_te)
        m = E.move_alone(move, A_te)
        out['prequal'][name] = {'aim_admissible': a['a_target_admissible'], 'n_unique_best': a['n_unique_best'], 'move_success': m['a_joint'],
                                'hold': m['a_hold'], 'approach': m['a_approach'], 'backoff': m['a_backoff'], 'n_hold': m['n_hold'], 'n_approach': m['n_approach'],
                                'n_backoff': m['n_backoff']}
    if cfg['require_counts']:
        p = out['prequal']['L']
        if p['n_unique_best'] < cfg['min_unique_best'] or min(p['n_hold'], p['n_approach'], p['n_backoff']) < cfg['min_stratum']:
            raise ValueError('test pool of seed %d is undersized: %s' % (seed, {k: p[k] for k in ('n_unique_best', 'n_hold', 'n_approach', 'n_backoff')}))
    cells, fixed_only = cell_assemblies(cfg, L, J, Fp)
    for code, (name, asm) in enumerate(list(cells.items())+list(fixed_only.items())):
        ch, st, applied = asm.act(A_te, stream(entropy, 9, seed, code))
        out['fixed'][name] = E.joint3(ch, st, A_te)
        out['applied'][name] = float(applied.mean())
    for name, m in (('Fp', Fp), ('Fflat', Ff)):
        out['fixed'][name] = E.joint3(*m.act(A_te), A_te)
    t1 = time.time()
    policies = {'R': lambda rng: T.rush_policy, 'Fp': flat_policy(Fp), 'Fflat': flat_policy(Ff)}
    policies.update({name: asm.policy for name, asm in cells.items()})
    for name, make in policies.items():
        for opp in OPP:
            out['play']['%s_%s' % (name, opp)] = E.play_cell(make, opp, entropy, seed, cfg['episodes'], world_fn=wf, mixes=mixes)
    if cfg.get('run_dir'):
        d = Path(cfg['run_dir'])/'models'
        d.mkdir(parents=True, exist_ok=True)
        for name, m in (('L', L), ('J', J), ('Fp', Fp), ('Fflat', Ff)):
            tmp = d/('seed_%02d_%s.npz.tmp' % (seed, name))
            with open(tmp, 'wb') as f:
                np.savez_compressed(f, **weights_of(m))
            tmp.replace(d/('seed_%02d_%s.npz' % (seed, name)))
    out['play_seconds'] = time.time()-t1
    out['seconds'] = time.time()-t0
    return out


def seed_job(args):
    cfg, entropy, seed = args
    try:
        return run_seed(cfg, entropy, seed)
    except Exception as error:  # noqa: BLE001 - recorded, never silently dropped
        return {'status': 'ERROR', 'seed': seed, 'error': repr(error)}


# ---------------------------------------------------------------- the registered verdict rules (SPECIFICATION_0E.md section 4)

def W(r, cell):
    return float(np.mean([r['play']['%s_%s' % (cell, o)]['score'] for o in OPP]))


def Wo(r, cell, opp):
    return float(r['play']['%s_%s' % (cell, opp)]['score'])


def Fid(r, cell):
    return float(r['fixed'][cell]['a_joint'])


def paired(rows, f):
    return np.array([f(r) for r in sorted(rows, key=lambda r: r['seed'])], float)


def interval(x, a):
    lo, hi, _ = E.median_interval(x, a)
    return {'median': float(np.median(x)), 'lo': lo, 'hi': hi, 'n': int(len(x))}


def component(name, x, a, m, kind, t):
    """One predicate on per-seed values x: kind 'above' (x > t) or 'below' (x < t). Positive test at error a; negative witness at a/m (within-claim Bonferroni)."""
    pos = interval(x, a)
    neg = interval(x, a/m)
    if kind == 'above':
        passed, witness = pos['lo'] > t, neg['hi'] < t
    else:
        passed, witness = pos['hi'] < t, neg['lo'] > t
    return {'name': name, 'kind': kind, 'threshold': t, 'interval': pos, 'negative_interval': neg, 'passed': bool(passed), 'negative_witness': bool(witness)}


def compound(components):
    if all(c['passed'] for c in components):
        return 'SUPPORTED'
    if any(c['negative_witness'] for c in components):
        return 'REFUTED'
    return 'INDETERMINATE'


def evaluate(rows, cfg):
    a, b = cfg['alpha'], cfg['bars']
    out = {'alpha_per_claim': a, 'seeds': len(rows)}
    # ---- gates (each at the claim error)
    D = paired(rows, lambda r: W(r, 'OO')-W(r, 'R'))
    Dint = interval(D, a)
    head_opp = {o: interval(paired(rows, lambda r, o=o: Wo(r, 'OO', o)-Wo(r, 'R', o)), a) for o in OPP}
    headroom_ok = Dint['lo'] > b['headroom'] and all(v['lo'] > b['headroom_per_opponent'] for v in head_opp.values())
    nec = {k: interval(paired(rows, lambda r, c=c: W(r, 'OO')-W(r, c)), a) for k, c in (('aim', 'DO'), ('connection', 'OO|default'), ('move', 'OD'))}
    nec_ok = {k: v['lo'] > b['necessity'] for k, v in nec.items()}
    base = {}
    for name in ('Fp', 'Fflat'):
        g = interval(paired(rows, lambda r, n=name: W(r, n)-W(r, 'R')), a)
        go = {o: interval(paired(rows, lambda r, n=name, o=o: Wo(r, n, o)-Wo(r, 'R', o)), a) for o in OPP}
        base[name] = {'gain_over_rush': g, 'per_opponent': go, 'qualified': bool(g['lo'] > b['baseline_gate'] and all(v['lo'] > 0 for v in go.values()))}
    out['gates'] = {'headroom_D': Dint, 'headroom_per_opponent': head_opp, 'headroom_ok': bool(headroom_ok), 'teacher_necessity': nec,
                    'teacher_necessity_ok': {k: bool(v) for k, v in nec_ok.items()}, 'baselines': base}
    Dhalf = interval(D, a/2)

    def norm(x):
        num = interval(x, a/2)
        rb = E.ratio_bounds((num['lo'], num['hi']), (Dhalf['lo'], Dhalf['hi']))
        return None if rb is None else {'lo': rb[0], 'hi': rb[1], 'median_ratio': float(np.median(x))/Dint['median']}
    # ---- A. replacement
    comps = []
    pre = lambda key, name: paired(rows, lambda r: r['prequal'][name][key])
    for name in ('L',):
        comps.append(('prequal AIM admissible (%s)' % name, pre('aim_admissible', name), 'above', b['aim_admissible']))
        comps.append(('prequal MOVE success (%s)' % name, pre('move_success', name), 'above', b['move_success']))
        for s in ('hold', 'approach', 'backoff'):
            comps.append(('prequal MOVE %s (%s)' % (s, name), pre(s, name), 'above', b['move_stratum']))
    for cell in ('LO', 'OL', 'LL'):
        comps.append(('win %s-OO' % cell, paired(rows, lambda r, c=cell: W(r, c)-W(r, 'OO')), 'above', b['replace_oracle']))
        for o in OPP:
            comps.append(('win %s-OO vs %s' % (cell, o), paired(rows, lambda r, c=cell, o=o: Wo(r, c, o)-Wo(r, 'OO', o)), 'above', b['replace_oracle']))
        comps.append(('fidelity %s-OO' % cell, paired(rows, lambda r, c=cell: Fid(r, c)-Fid(r, 'OO')), 'above', b['replace_oracle']))
    for cell in ('JL', 'LJ'):
        comps.append(('win %s-JJ' % cell, paired(rows, lambda r, c=cell: W(r, c)-W(r, 'JJ')), 'above', b['replace_J']))
        comps.append(('fidelity %s-JJ' % cell, paired(rows, lambda r, c=cell: Fid(r, c)-Fid(r, 'JJ')), 'above', b['replace_J']))
    cA = [component(n, x, a, len(comps), k, t) for n, x, k, t in comps]
    out['A_replacement'] = {'components': cA, 'verdict': compound(cA)}
    # ---- B1. useful connection (requires the connection-necessity gate and the directed sensitivity control)
    comps = []
    for c in cfg['cuts']:
        comps.append(('win LL - LL|%s' % c, paired(rows, lambda r, c=c: W(r, 'LL')-W(r, 'LL|'+c)), 'above', b['cut_raw']))
    comps.append(('directed control: fidelity LL - LL|reverse', paired(rows, lambda r: Fid(r, 'LL')-Fid(r, 'LL|reverse')), 'above', b['directed']))
    cB1 = [component(n, x, a, len(comps)+len(cfg['cuts']), k, t) for n, x, k, t in comps]
    normd = {}
    for c in cfg['cuts']:
        nb = norm(paired(rows, lambda r, c=c: W(r, 'LL')-W(r, 'LL|'+c)))
        ok = nb is not None and nb['lo'] > b['cut_norm']
        normd[c] = nb
        cB1.append({'name': 'normalized win gain over LL|%s' % c, 'kind': 'above', 'threshold': b['cut_norm'], 'interval': nb, 'passed': bool(ok),
                    'negative_witness': bool(nb is not None and nb['hi'] < b['cut_norm'])})
    v = compound(cB1)
    if not nec_ok['connection'] or not headroom_ok:
        v = 'INDETERMINATE (gate: %s)' % ('connection necessity' if not nec_ok['connection'] else 'headroom')
    out['B1_useful_connection'] = {'components': cB1, 'verdict': v}
    # ---- B2. stable within the tested envelope
    comps = [('function: win LL - R', paired(rows, lambda r: W(r, 'LL')-W(r, 'R')), 'above', b['function'])]
    for k, val in cfg['small_faults_abs']:
        cell = 'LL|%s_%g' % (k, val)
        comps.append(('win loss under %s' % cell, paired(rows, lambda r, c=cell: W(r, 'LL')-W(r, c)), 'below', b['fault_abs']))
        comps.append(('fidelity loss under %s' % cell, paired(rows, lambda r, c=cell: Fid(r, 'LL')-Fid(r, c)), 'below', b['fault_abs']))
    for k, val in cfg['small_faults_rel']:
        lc, oc = 'LL|%s_%g' % (k, val), 'OO|%s_%g' % (k, val)
        comps.append(('win loss under %s minus the teacher\'s' % lc, paired(rows, lambda r, lc=lc, oc=oc: (W(r, 'LL')-W(r, lc))-(W(r, 'OO')-W(r, oc))), 'below', b['fault_rel']))
        comps.append(('fidelity loss under %s minus the teacher\'s' % lc, paired(rows, lambda r, lc=lc, oc=oc: (Fid(r, 'LL')-Fid(r, lc))-(Fid(r, 'OO')-Fid(r, oc))), 'below', b['fault_rel']))
    m2 = len(comps)+2
    cB2 = [component(n, x, a, m2, k, t) for n, x, k, t in comps]
    gains = paired(rows, lambda r: W(r, 'LL')-W(r, 'R'))
    k_succ = int((gains > b['repeat_gain']).sum())
    cp, cpn = E.clopper_pearson(k_succ, len(gains), a), E.clopper_pearson(k_succ, len(gains), a/m2)
    cB2.append({'name': 'share of seeds with W(LL)-W(R) > %g' % b['repeat_gain'], 'kind': 'above', 'threshold': b['repeat_share'], 'interval': {'k': k_succ, 'n': len(gains), 'lo': cp[0], 'hi': cp[1]},
                'passed': bool(cp[0] > b['repeat_share']), 'negative_witness': bool(cpn[1] < b['repeat_share'])})
    wll = paired(rows, lambda r: W(r, 'LL'))
    iq, iqn = E.iqr_bounds(wll, a), E.iqr_bounds(wll, a/m2)
    cB2.append({'name': 'IQR of W(LL) across seeds', 'kind': 'below', 'threshold': b['iqr'], 'interval': {'lo': iq[0], 'hi': iq[1]},
                'passed': bool(iq[1] < b['iqr']), 'negative_witness': bool(iqn[0] > b['iqr'])})
    out['B2_stable_within_envelope'] = {'components': cB2, 'verdict': compound(cB2)}
    # ---- B3. stronger than the qualified conventional baseline
    comps = [('win LL - Fp', paired(rows, lambda r: W(r, 'LL')-W(r, 'Fp')), 'above', b['stronger'])]
    cB3 = [component(n, x, a, 1, k, t) for n, x, k, t in comps]
    v3 = compound(cB3) if base['Fp']['qualified'] else 'INDETERMINATE (gate: conventional baseline not qualified)'
    out['B3_stronger_than_conventional'] = {'components': cB3, 'verdict': v3,
                                            'secondary_iqr_difference_note': 'reported descriptively', 'flat_family': {
                                                'qualified': base['Fflat']['qualified'], 'win_LL_minus_Fflat': interval(paired(rows, lambda r: W(r, 'LL')-W(r, 'Fflat')), a)}}
    # ---- descriptive
    cells = sorted({k.rsplit('_', 1)[0] for k in rows[0]['play']})
    out['descriptive'] = {
        'win_by_cell': {c: {'all': float(np.median(paired(rows, lambda r, c=c: W(r, c)))), **{o: float(np.median(paired(rows, lambda r, c=c, o=o: Wo(r, c, o)))) for o in OPP}} for c in cells},
        'outcomes_by_cell': {c: {k: int(sum(r['play']['%s_%s' % (c, o)][k] for r in rows for o in OPP)) for k in ('win', 'loss', 'draw', 'timeout')} for c in cells},
        'fidelity_by_cell': {c: {k: float(np.median(paired(rows, lambda r, c=c, k=k: r['fixed'][c][k] if r['fixed'][c][k] is not None else np.nan))) for k in
                                 ('a_joint', 'a_macro', 'a_hold', 'a_approach', 'a_backoff', 'a_target_admissible')} for c in rows[0]['fixed']},
        'normalized_cut_gains': normd, 'headroom_D_median': Dint['median'], 'params': rows[0]['params'], 'oracle_queries': rows[0]['oracle_queries'],
        'seconds_per_seed': float(np.median([r['seconds'] for r in rows])),
        'note': 'every interval in a verdict is an exact order-statistic (medians) or Clopper-Pearson (shares) interval at the claim error 0.0125; unadjusted across claims'}
    out['endpoint_coverage'] = {k: 'evaluated' for k in ('gates', 'A_replacement', 'B1_useful_connection', 'B2_stable_within_envelope', 'B3_stronger_than_conventional', 'descriptive')}
    return out


# ---------------------------------------------------------------- specification and the run

def write_spec():
    path = HERE/'SPEC_0E.json'
    if path.exists():
        raise SystemExit('SPEC_0E.json already exists; the entropy is generated once')
    step5 = json.loads((HERE/'dev_0e'/'step5_results.json').read_text())
    cfg = dict(BASE)
    cfg['ref_distance'] = float(step5['ref_distance'])
    if step5['selected'] != cfg['Fp_recipe']:
        raise SystemExit('the registered conventional baseline differs from the development selection')
    write_json(path, {'note': 'Generated once by --write-spec; settings from dev_0e (README).', 'entropy': secrets.randbits(96), 'smoke_entropy': secrets.randbits(96),
                      'config': cfg, 'smoke_overrides': SMOKE})
    print('wrote', path)


def main_run(smoke):
    spec = json.loads((HERE/'SPEC_0E.json').read_text())
    load = os.getloadavg()[0]
    if not smoke and load > spec['config']['max_load_1min']:
        raise SystemExit('one-minute load %.1f is above the registered start threshold %.1f: not starting' % (load, spec['config']['max_load_1min']))
    return harness.run_experiment(spec_path=HERE/'SPEC_0E.json', here=HERE, root=ROOT, files=FILES, run_dirs=RUN_DIRS, run_name=RUN_DIRS[1] if smoke else RUN_DIRS[0],
                                  seed_job=seed_job, evaluate=evaluate, smoke=smoke)[0]


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write-spec', action='store_true')
    group.add_argument('--run', action='store_true')
    group.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    if args.write_spec:
        write_spec()
    else:
        sys.exit(main_run(args.smoke))


if __name__ == '__main__':
    main()
