"""Experiment 0d Part A: structure versus composition (SPECIFICATION_0D.md, PROPOSAL_0D.md revision 2). Exploratory; NOT a milestone, NOT C6 evidence.

    python evidence/tactical_composition_demo/zd_run.py --write-spec   # once, before the registration commit
    python evidence/tactical_composition_demo/zd_run.py --smoke        # reduced run, own entropy, own directory
    python evidence/tactical_composition_demo/zd_run.py --run          # the single recorded run

The only way to run work is --run / --smoke, which create the exclusive run directory (the one-shot latch) through tcd_common.harness.
"""
import argparse
import hashlib
import json
import secrets
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import tactics as T  # noqa: E402
import zd_models as Z  # noqa: E402
from tcd_common import harness, metrics, stats  # noqa: E402
from tcd_common.fileio import atomic_write, stream, write_json  # noqa: E402

MODELS = ('F0', 'F1', 'F2', 'C', 'S1')
CODE = {'F0': 0, 'F1': 1, 'F2': 2, 'C': 3, 'S1': 4}
OPPONENTS = ('rush', 'kiter')
OPP_CODE = {'rush': 0, 'kiter': 1}
POLICIES = ('teacher', 'rush', 'F0', 'F*', 'C', 'S1')
STRATA = ('hold', 'moving', 'backoff')
RECORDED_F0 = {'hidden': 15, 'lr': 0.003, 'wd': 0.0, 'steps': 8000}
RUN_DIRS = ('run_0d', 'smoke_run_0d')
FILES = ('PROPOSAL_0D.md', 'SPECIFICATION_0D.md', 'SPEC_0D.json', 'zd_run.py', 'zd_models.py', 'test_zd.py', 'tactics.py',
         'tcd_common/__init__.py', 'tcd_common/fileio.py', 'tcd_common/stats.py', 'tcd_common/metrics.py', 'tcd_common/supervise.py', 'tcd_common/harness.py',
         'tcd_common/test_common.py', 'dev_0d/DEV_SPEC.json', 'dev_0d/tuned2.json', 'dev_0d/gates_results.json', 'dev_0d/README.md')

BASE_CONFIG = {
    'seeds': 30, 'workers': 8, 'soft_cap': 3600.0, 'hard_cap': 3900.0, 'eval_cap': 300.0,
    'train_episodes': 600, 'test_episodes': 100, 'n_primary': 3000, 'n_extra': [1000, 9000], 'win_episodes': 200,
    'f_star': 'F1', 'hps': {}, 'delta_eq': 0.03, 'delta_sup': 0.06, 'resamples': 4000, 'angle_deg': 10.0, 'min_stratum': 30,
    'require_strata': True, 'c_adequate': None, 'c_adequate_basis': 'dev gates', 's1_adequate': None, 's1_adequate_basis': 'dev gates'}
SMOKE = {'seeds': 2, 'workers': 2, 'soft_cap': 900.0, 'hard_cap': 1100.0, 'eval_cap': 120.0, 'train_episodes': 40, 'test_episodes': 10, 'n_primary': 300, 'n_extra': [150, 450],
         'win_episodes': 4, 'hps_step_cap': 300, 'require_strata': False}


# ---------------------------------------------------------------- one seed

def seed_digest(pool):
    h = hashlib.sha256()
    h.update(np.ascontiguousarray(pool['own']).tobytes())
    h.update(np.ascontiguousarray(pool['enemies']).tobytes())
    return h.hexdigest()


def hp_for(cfg, name):
    hp = dict(RECORDED_F0 if name == 'F0' else cfg['hps'][name])
    if cfg.get('hps_step_cap'):
        hp['steps'] = min(hp['steps'], cfg['hps_step_cap'])
    return hp


def flatten(prefix, r):
    out = {}
    for k in ('a_joint', 'a_target_admissible', 'a_step_given_admissible', 'step_angle_median_moving_deg', 'aim_alone_agree_corrected', 'move_alone_joint_on_teacher_target',
              'independent_prediction', 'connection_gap', 'n_multi'):
        out['%s_%s' % (k, prefix)] = r[k]
    for s in STRATA:
        out['a_joint_stratum_%s_%s' % (s, prefix)] = r['strata'].get('a_joint_stratum_'+s)
        out['n_stratum_%s_%s' % (s, prefix)] = r['strata'].get('n_stratum_'+s)
    return out


def score_model(model, A):
    """Pieces alone, then connected (the same decomposition as the development scripts)."""
    pool, lab = A.pool, A.lab
    chosen, step = model.act(A)
    joint = metrics.joint_action(chosen, step, pool, lab, angle_deg=A_ANGLE[0], min_stratum=A_MIN[0])
    agree = metrics.agreement(chosen, pool, lab)
    told = model.step_for(A, A.target)
    move_alone = metrics.joint_action(A.target, told, pool, lab, angle_deg=A_ANGLE[0], min_stratum=A_MIN[0])
    independent = joint['a_target_admissible']*move_alone['a_joint']
    return {'a_joint': joint['a_joint'], 'a_target_admissible': joint['a_target_admissible'], 'a_step_given_admissible': joint['a_step_given_admissible'],
            'step_angle_median_moving_deg': joint['step_angle_median_moving_deg'], 'aim_alone_agree_corrected': agree['agree_corrected_multi'],
            'move_alone_joint_on_teacher_target': move_alone['a_joint'], 'independent_prediction': independent, 'connection_gap': joint['a_joint']-independent,
            'n_multi': joint['n_multi'], 'strata': {k: joint[k] for k in joint if k.startswith('a_joint_stratum_') or k.startswith('n_stratum_')},
            'strata_adequate': joint['strata_adequate']}


A_ANGLE, A_MIN = [10.0], [30]   # set from the configuration at the start of each seed


def weights_of(model):
    """Everything needed to recompute a model's predictions later: weights and the frozen standardizers."""
    if hasattr(model, 'scorer'):
        arrays = {'scorer_%d' % i: p for i, p in enumerate(model.scorer.params())}
        arrays.update({'head_%d' % i: p for i, p in enumerate(model.head.params())})
        for name in ('xa', 'ya', 'xm', 'ym'):
            arrays[name+'_m'], arrays[name+'_s'] = getattr(model, name).m, getattr(model, name).s
    elif hasattr(model.net, 'params'):
        arrays = {'net_%d' % i: p for i, p in enumerate(model.net.params())}
        for name in ('xs', 'ys'):
            arrays[name+'_m'], arrays[name+'_s'] = getattr(model, name).m, getattr(model, name).s
    else:
        arrays = {'net_%d' % i: p for i, p in enumerate(model.net.W+model.net.b)}
        arrays.update({'mx': model.net.mx, 'sx': model.net.sx, 'my': model.net.my, 'sy': model.net.sy})
    return arrays


def run_seed(cfg, entropy, seed):
    import time
    started = time.time()
    A_ANGLE[0], A_MIN[0] = cfg['angle_deg'], cfg['min_stratum']
    train_pool = T.collect(stream(entropy, 1, seed), cfg['train_episodes'], T.SEEN_MIXES)
    test_pool = T.collect(stream(entropy, 2, seed), cfg['test_episodes'], T.SEEN_MIXES)
    A_tr, A_te = Z.Arrays(train_pool, T.labels(train_pool)), Z.Arrays(test_pool, T.labels(test_pool))
    out = {'seed': seed, 'train_states': int(A_tr.n), 'test_states': int(A_te.n), 'test_digest': seed_digest(test_pool)}
    order = stream(entropy, 4, seed).permutation(A_tr.n)          # one permutation: the source states of every N are nested
    ns = [cfg['n_primary']]+list(cfg['n_extra'])
    primary = {}
    for n in ns:
        idx = order[:min(n, A_tr.n)]
        for name in MODELS:
            t0 = time.time()
            model = Z.FITS[name](A_tr, idx, hp_for(cfg, name), stream(entropy, 3, seed, CODE[name], n))
            fit_seconds = time.time()-t0
            r = score_model(model, A_te)
            if cfg['require_strata'] and not r['strata_adequate']:
                raise ValueError('stratum below %d states for %s at N=%d on seed %d' % (cfg['min_stratum'], name, n, seed))
            prefix = '%s_%d' % (name, n)
            out.update(flatten(prefix, r))
            out.update({'fit_seconds_'+prefix: fit_seconds, 'n_params_'+prefix: int(model.n_params), 'supervision_'+prefix: model.supervision,
                        'oracle_queries_'+prefix: int(getattr(model, 'oracle_queries', 0))})
            if n == cfg['n_primary']:
                primary[name] = model
                if cfg.get('run_dir'):
                    d = Path(cfg['run_dir'])/'models'
                    d.mkdir(parents=True, exist_ok=True)
                    path = d/('seed_%02d_%s.npz' % (seed, name))
                    tmp = path.with_name(path.name+'.tmp')
                    with open(tmp, 'wb') as f:
                        np.savez_compressed(f, **weights_of(model))
                    tmp.replace(path)
    policies = {'teacher': T.teacher_policy, 'rush': T.rush_policy, 'F0': Z.policy_of(primary['F0']), 'F*': Z.policy_of(primary[cfg['f_star']]),
                'C': Z.policy_of(primary['C']), 'S1': Z.policy_of(primary['S1'])}
    for pname in POLICIES:
        for opp in OPPONENTS:
            t0 = time.time()
            out['score_%s_%s' % (pname, opp)] = T.win_score(policies[pname], T.SEEN_MIXES, T.OPPONENTS[opp], stream(entropy, 7, seed, OPP_CODE[opp]), cfg['win_episodes'])
            out['score_seconds_%s_%s' % (pname, opp)] = time.time()-t0
    out['seconds'] = time.time()-started
    return out


def seed_job(args):
    cfg, entropy, seed = args
    try:
        return run_seed(cfg, entropy, seed)
    except Exception as error:  # noqa: BLE001 - recorded, never silently dropped
        return {'status': 'ERROR', 'seed': seed, 'error': repr(error)}


# ---------------------------------------------------------------- the registered verdict rules (PROPOSAL_0D.md section 4)

def ci(values, cfg, key):
    rng = stream(cfg['boot_entropy'], key)
    med, lo, hi = stats.paired_median_ci(values, np.zeros_like(values), rng, cfg['resamples'])
    return {'median': med, 'lo': lo, 'hi': hi, 'n': int(len(values))}


def contrast(rows, a, b, cfg, key):
    return ci(stats.paired_by_seed(rows, a, b), cfg, key)


def v1(e, d):
    return 'SUPPORTED' if e['lo'] > d['sup'] else 'REFUTED' if e['hi'] < d['sup'] else 'INDETERMINATE'


def v2_label(e, d):
    return ('SEPARATE_BETTER' if e['lo'] > d['sup'] else 'JOINT_BETTER' if e['hi'] < -d['sup'] else
            'EQUIVALENT' if (-d['eq'] < e['lo'] and e['hi'] < d['eq']) else 'INDETERMINATE')


def v_tune(e, d):
    return 'SUPPORTED' if e['lo'] > d['eq'] else 'REFUTED' if (-d['eq'] < e['lo'] and e['hi'] < d['eq']) else 'INDETERMINATE'


def evaluate(rows, cfg):
    d = {'eq': cfg['delta_eq'], 'sup': cfg['delta_sup']}
    n0 = cfg['n_primary']
    fs = cfg['f_star']
    key = lambda m, n=n0: 'a_joint_%s_%d' % (m, n)
    out = {'margins': d, 'seeds': len(rows)}
    E = {'E0': contrast(rows, key('C'), key('F0'), cfg, 10), 'E1': contrast(rows, key('C'), key(fs), cfg, 11), 'E2': contrast(rows, key('C'), key('S1'), cfg, 12),
          'E3': contrast(rows, key('S1'), key(fs), cfg, 13), 'T1': contrast(rows, key(fs), key('F0'), cfg, 14), 'T2': contrast(rows, key('F2'), key('F1'), cfg, 15)}
    win = lambda m: {r['seed']: float(np.mean([r['score_%s_%s' % (m, o)] for o in OPPONENTS])) for r in rows}

    def win_contrast(a, b, k):
        wa, wb = win(a), win(b)
        return ci(np.array([wa[s]-wb[s] for s in sorted(wa)]), cfg, k)
    W = {'C_minus_Fstar': win_contrast('C', 'F*', 20), 'C_minus_S1': win_contrast('C', 'S1', 21), 'C_minus_teacher': win_contrast('C', 'teacher', 22),
         'F0_minus_teacher': win_contrast('F0', 'teacher', 23), 'Fstar_minus_teacher': win_contrast('F*', 'teacher', 24), 'S1_minus_teacher': win_contrast('S1', 'teacher', 25),
         'teacher_minus_rush': win_contrast('teacher', 'rush', 26)}
    verdict1 = v1(E['E1'], d)
    w1 = W['C_minus_Fstar']
    if (verdict1 == 'SUPPORTED' and w1['hi'] < 0) or (verdict1 == 'REFUTED' and w1['lo'] >= d['sup']):
        verdict1 = 'INDETERMINATE (discordant with closed-loop win score)'
    label2 = v2_label(E['E2'], d)
    w2 = W['C_minus_S1']
    discordant = ((label2 == 'SEPARATE_BETTER' and w2['hi'] < 0) or (label2 == 'JOINT_BETTER' and w2['lo'] > 0)
                  or (label2 == 'EQUIVALENT' and (w2['lo'] >= d['eq'] or w2['hi'] <= -d['eq'])))
    s1_ok = bool(cfg['s1_adequate'])
    verdict2 = 'INDETERMINATE (S1 baseline inadequate)' if not s1_ok else 'INDETERMINATE (discordant with closed-loop win score)' if discordant else label2
    if not s1_ok or discordant:
        verdict3 = 'INDETERMINATE'
    elif verdict1 == 'SUPPORTED' and E['E3']['lo'] > d['sup'] and label2 == 'EQUIVALENT':
        verdict3 = 'SUPPORTED'
    elif verdict1 == 'SUPPORTED' and (label2 == 'SEPARATE_BETTER' or E['E3']['hi'] < d['sup']):
        verdict3 = 'REFUTED'
    else:
        verdict3 = 'INDETERMINATE'
    out['V1_the_wired_unit_beats_the_tuned_flat_model'] = {'contrast': 'E1 = A(C) - A(F*)', 'F_star': fs, 'E1': E['E1'], 'win_score_C_minus_Fstar': W['C_minus_Fstar'], 'verdict': verdict1}
    out['V2_training_mode_C_versus_S1'] = {'contrast': 'E2 = A(C) - A(S1)', 'E2': E['E2'], 'label_before_gates': label2, 'win_score_C_minus_S1': W['C_minus_S1'],
                                           's1_adequate_from_development': s1_ok, 'verdict': verdict2}
    out['V3_structure_explains_the_gain'] = {'E1': E['E1'], 'E2': E['E2'], 'E3': E['E3'], 'verdict': verdict3}
    out['V4_the_recorded_baseline_was_under_tuned'] = {'contrast': 'T1 = A(F*) - A(F0)', 'T1': E['T1'], 'E0': E['E0'], 'verdict': v_tune(E['T1'], d)}
    out['V5_a_discrete_move_head_matters'] = {'contrast': 'T2 = A(F2) - A(F1)', 'T2': E['T2'], 'verdict': v_tune(E['T2'], d)}
    # descriptive (no verdict depends on these)
    col = lambda k: stats.stats(stats.col(rows, k))
    out['descriptive'] = {
        'a_joint_by_model_and_N': {m: {str(n): col('a_joint_%s_%d' % (m, n)) for n in [n0]+list(cfg['n_extra'])} for m in MODELS},
        'contrasts_by_N': {str(n): {name: contrast(rows, 'a_joint_%s_%d' % a, 'a_joint_%s_%d' % b, cfg, 40+i)
                                   for i, (name, a, b) in enumerate((('E1', ('C', n), (fs, n)), ('E2', ('C', n), ('S1', n)), ('E3', ('S1', n), (fs, n))))} for n in cfg['n_extra']},
        'pieces_alone_and_connected': {m: {k: col('%s_%s_%d' % (k, m, n0)) for k in ('a_target_admissible', 'move_alone_joint_on_teacher_target', 'independent_prediction',
                                                                                    'connection_gap', 'aim_alone_agree_corrected')} for m in MODELS},
        'step_angle_median_moving_deg': {m: col('step_angle_median_moving_deg_%s_%d' % (m, n0)) for m in MODELS},
        'strata_a_joint': {m: {s: col('a_joint_stratum_%s_%s_%d' % (s, m, n0)) for s in STRATA} for m in MODELS},
        'win_score_contrasts': W, 'win_score_by_policy': {p: {o: col('score_%s_%s' % (p, o)) for o in OPPONENTS} for p in POLICIES},
        'parameters': {m: int(rows[0]['n_params_%s_%d' % (m, n0)]) for m in MODELS},
        'supervision_labels': {m: rows[0]['supervision_%s_%d' % (m, n0)] for m in MODELS}, 'oracle_queries': {m: rows[0]['oracle_queries_%s_%d' % (m, n0)] for m in MODELS},
        'fit_seconds': {m: col('fit_seconds_%s_%d' % (m, n0)) for m in MODELS}, 'seconds_per_seed': col('seconds'),
        'unadjusted_note': 'five separately pre-registered rows; every interval is unadjusted; seeds replicate one environment, not independent tasks'}
    out['endpoint_coverage'] = {k: 'evaluated' for k in ('E0', 'E1', 'E2', 'E3', 'T1', 'T2')}
    out['endpoint_coverage'].update({'win_'+k: 'evaluated' for k in W})
    return out


# ---------------------------------------------------------------- specification and the run

def build_config(dev_dir=HERE/'dev_0d'):
    """The registered configuration: tuned settings, comparator, seed count and adequacy flags come from the committed development records."""
    tuned = json.loads((dev_dir/'tuned2.json').read_text())
    gates = json.loads((dev_dir/'gates_results.json').read_text())
    cfg = dict(BASE_CONFIG)
    cfg['hps'] = {n: tuned['chosen'][n]['hp'] for n in ('F1', 'F2', 'C', 'S1')}
    cfg['f_star'] = tuned['comparator_F_star']
    cfg['seeds'] = gates['seeds_needed_S']
    cfg['c_adequate'], cfg['s1_adequate'] = gates['gates']['C_adequate_ge_0.90'], gates['gates']['S1_adequate']
    return cfg


def write_spec():
    path = HERE/'SPEC_0D.json'
    if path.exists():
        raise SystemExit('SPEC_0D.json already exists; the entropy is generated once')
    cfg = build_config()
    cfg['boot_entropy'] = secrets.randbits(96)
    write_json(path, {'note': 'Generated once by --write-spec from dev_0d/tuned2.json and dev_0d/gates_results.json; caps measured in dev_0d/cost_*.json.',
                      'entropy': secrets.randbits(96), 'smoke_entropy': secrets.randbits(96), 'config': cfg, 'smoke_overrides': SMOKE})
    print('wrote', path)


def main_run(smoke):
    return harness.run_experiment(spec_path=HERE/'SPEC_0D.json', here=HERE, root=ROOT, files=FILES, run_dirs=RUN_DIRS, run_name=RUN_DIRS[1] if smoke else RUN_DIRS[0],
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
