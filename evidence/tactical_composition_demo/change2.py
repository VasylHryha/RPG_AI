"""Change-cost test, revision 2 (Stage 0c-r2). NOT a milestone, NOT C6 evidence. See MOTIVATION.md and SPECIFICATION_CHANGE2.md.

The targeting doctrine changes (threat first). The wired unit retrains ONLY its AIM piece from scratch on the new rows and reuses MOVE untouched;
the one big controller retrains whole from scratch on the same number of new rows. How many labeled rows does each need to recover its own
pre-change quality? Fine-tuning from the old weights (the first revision's protocol) is a secondary, reported comparison.

    python evidence/tactical_composition_demo/change2.py --write-spec   # once, before the specification commit
    python evidence/tactical_composition_demo/change2.py --smoke        # reduced run, own entropy, own directory
    python evidence/tactical_composition_demo/change2.py --run          # the single recorded run
"""
import argparse
import concurrent.futures as cf
import copy
import hashlib
import json
import multiprocessing as mp
import os
import resource
import secrets
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import tactics as T  # noqa: E402
import demo  # noqa: E402
import change as r1  # noqa: E402  (helpers of the first revision: recovered, col, stats, AGREE, STEP)

STAGE0 = demo.CONFIG
CONFIG = {
    'seeds': 20, 'workers': 8, 'soft_cap': 2700.0, 'hard_cap': 3000.0,
    'train_episodes': 600, 'test_episodes': 60, 'eval_episodes': 40,
    'grid': [100, 300, 1000, 3000, 6000, 12000],
    'scratch_epochs': 170, 'scratch_steps_floor': 500, 'scratch_steps_cap': 16000, 'scratch_batch': 128, 'scratch_lr': 0.003,
    'ft_epochs': 60, 'ft_steps_floor': 200, 'ft_steps_cap': 2000, 'ft_batch': 64, 'ft_lr': 0.002,
    'recover_agreement_margin': 0.03, 'recover_angle_margin_deg': 3.0, 'c2_refute_margin': 0.15, 'rows_share': 0.5,
    'absolute_agreement_levels': [0.80, 0.90, 0.95], 'common_level': 0.80, 'absolute_angle_bar_deg': 10.0,
    'c2_rows': 1000,
    'stage0': {k: STAGE0[k] for k in ('n_aim', 'n_move', 'piece_hidden', 'piece_steps', 'batch', 'lr')},
    'mono_equal': STAGE0['monolith'][0], 'mono_large': STAGE0['monolith'][2]}
SMOKE = {'seeds': 2, 'workers': 2, 'soft_cap': 600.0, 'hard_cap': 800.0, 'train_episodes': 40, 'test_episodes': 8, 'eval_episodes': 3,
         'grid': [50, 100], 'scratch_steps_floor': 30, 'scratch_steps_cap': 60, 'ft_steps_floor': 20, 'ft_steps_cap': 40, 'c2_rows': 100,
         'stage0': {'n_aim': 300, 'n_move': 300, 'piece_hidden': 16, 'piece_steps': 200, 'batch': 128, 'lr': 0.003},
         'mono_equal': {'rows': 600, 'hidden': 15, 'steps': 300}, 'mono_large': {'rows': 2400, 'hidden': 60, 'steps': 400}}
OPPONENTS = ('rush', 'kiter')
RAW = 'agree_tie_aware_multi'                     # raw tie-aware agreement (reported; the common-level view)
AGREE, STEP = 'agree_corrected_multi', 'step_tiebest_median_angle_deg'   # chance-corrected agreement and the best-matching-tie step (the relative view)
FILES = ('MOTIVATION.md', 'SPECIFICATION_CHANGE2.md', 'SPEC_CHANGE2.json', 'SPEC.json', 'change2.py', 'change.py', 'tactics.py', 'demo.py', 'test_change2.py', 'test_tactics.py',
         'dev_learnability.py', 'dev_learnability.json', 'dev_doctrine.py', 'dev_doctrine.json')


def stream(entropy, *key):
    return demo.stream(entropy, *key)


def scratch_steps(n, cfg):
    """Stage 0's recipe, scaled to the rows: 170 epochs over the n rows at the batch actually used (min(128, n)), at least 500 and at most 16,000 steps.
    The same for every design. Effective epochs: 500 at n=100, 213 at n=300, 170 from n=1,000 up (the cap never binds on the grid)."""
    batch = min(cfg['scratch_batch'], n)
    return int(min(cfg['scratch_steps_cap'], max(cfg['scratch_steps_floor'], np.ceil(cfg['scratch_epochs']*n/batch))))


def ft_steps(n, cfg):
    return r1.ft_steps(n, cfg)


# ---------------------------------------------------------------- one seed

def run_seed(cfg, entropy, seed):
    started = time.perf_counter()
    out = {'seed': seed}
    s0 = cfg['stage0']
    pool = T.collect(stream(entropy, 1, seed), cfg['train_episodes'], T.SEEN_MIXES)
    lab1, lab2 = T.labels(pool), T.labels(pool, T.teacher2_scores)
    test = T.collect(stream(entropy, 2, seed), cfg['test_episodes'], T.SEEN_MIXES)
    tl1, tl2 = T.labels(test), T.labels(test, T.teacher2_scores)
    need = max(cfg['mono_large']['rows'], max(cfg['grid']))
    if len(pool['own']) < need:
        raise RuntimeError('training pool has %d states, fewer than the %d rows requested' % (len(pool['own']), need))
    multi = T.multi_enemy(test)
    best2 = np.where(test['enemies'][:, :, 0] > 0, tl2['scores'], -np.inf).max(1)
    out['same_target_teacher1_teacher2_multi'] = float(np.mean((tl2['scores'][np.arange(len(best2)), tl1['target']] >= best2-1e-9)[multi]))
    # the controllers as they were taught under the original doctrine (as in Stage 0)
    data = T.piece_datasets(pool, lab1, s0['n_aim'], s0['n_move'], stream(entropy, 3, seed))
    aim1 = T.MLP(T.AIM_DIM, s0['piece_hidden'], 1, stream(entropy, 4, seed, 0)).fit(*data['AIM'], stream(entropy, 5, seed, 0), s0['piece_steps'], s0['batch'], s0['lr'])
    move = T.MLP(T.MOVE_DIM, s0['piece_hidden'], 2, stream(entropy, 4, seed, 1)).fit(*data['MOVE'], stream(entropy, 5, seed, 1), s0['piece_steps'], s0['batch'], s0['lr'])
    bigs, specs = {}, (('mono_eq', cfg['mono_equal']), ('mono_large', cfg['mono_large']))
    for j, (name, spec) in enumerate(specs):
        X, Y = T.mono_dataset(pool, lab1, spec['rows'], stream(entropy, 6, seed, j))
        bigs[name] = T.MLP(T.MONO_IN, spec['hidden'], T.MONO_OUT, stream(entropy, 7, seed, j)).fit(X, Y, stream(entropy, 8, seed, j), spec['steps'], s0['batch'], s0['lr'])
    for key, value in T.change_fidelity_composed(aim1, move, test, tl1).items():
        out['pre_composed_%s' % key] = value
    for key, value in T.change_fidelity_composed(aim1, move, test, tl2).items():
        out['old_composed_%s_vs_new' % key] = value
    for name, model in bigs.items():
        for key, value in T.change_fidelity_mono(model, test, tl1).items():
            out['pre_%s_%s' % (name, key)] = value
        for key, value in T.change_fidelity_mono(model, test, tl2).items():
            out['old_%s_%s_vs_new' % (name, key)] = value
    controllers = {'teacher2': T.teacher2_policy, 'rush': T.rush_policy, 'composed_old': T.composed_policy(aim1, move),
                   'mono_eq_old': T.mono_policy(bigs['mono_eq'])}
    for n in cfg['grid']:
        # PRIMARY protocol: retrain from scratch on n new rows. The wired unit retrains only AIM; MOVE is the same object as before.
        steps, batch = scratch_steps(n, cfg), min(cfg['scratch_batch'], n)
        out['scratch_steps_%d' % n] = steps
        t0 = time.perf_counter()
        X, Y = T.aim_dataset(pool, lab2, n, stream(entropy, 9, seed, n))
        if len(X) != n:
            raise RuntimeError('AIM retraining set is smaller than requested')
        aim2 = T.MLP(T.AIM_DIM, s0['piece_hidden'], 1, stream(entropy, 10, seed, n)).fit(X, Y, stream(entropy, 11, seed, n), steps, batch, cfg['scratch_lr'])
        out['build_composed_%d' % n] = time.perf_counter()-t0
        for key, value in T.change_fidelity_composed(aim2, move, test, tl2).items():
            out['composed_%d_%s' % (n, key)] = value
        controllers['composed_%d' % n] = T.composed_policy(aim2, move)
        for j, (name, spec) in enumerate(specs):
            t0 = time.perf_counter()
            X, Y = T.mono_dataset(pool, lab2, n, stream(entropy, 12, seed, n))
            if len(X) != n:
                raise RuntimeError('big-controller retraining set is smaller than requested')
            tuned = T.MLP(T.MONO_IN, spec['hidden'], T.MONO_OUT, stream(entropy, 13, seed, n, j)).fit(X, Y, stream(entropy, 14, seed, n, j), steps, batch, cfg['scratch_lr'])
            out['build_%s_%d' % (name, n)] = time.perf_counter()-t0
            for key, value in T.change_fidelity_mono(tuned, test, tl2).items():
                out['%s_%d_%s' % (name, n, key)] = value
            if name == 'mono_eq':
                controllers['mono_eq_%d' % n] = T.mono_policy(tuned)
        # SECONDARY protocol (the first revision's): fine-tune copies of the old models; fidelity only
        fsteps = ft_steps(n, cfg)
        Xa, Ya = T.aim_dataset(pool, lab2, n, stream(entropy, 15, seed, n))
        aim_f = copy.deepcopy(aim1).fit(Xa, Ya, stream(entropy, 16, seed, n), fsteps, cfg['ft_batch'], cfg['ft_lr'], keep_scaling=True)
        for key, value in T.change_fidelity_composed(aim_f, move, test, tl2).items():
            out['ft_composed_%d_%s' % (n, key)] = value
        Xf, Yf = T.mono_dataset(pool, lab2, n, stream(entropy, 17, seed, n))
        for name, model in bigs.items():
            tuned = copy.deepcopy(model).fit(Xf, Yf, stream(entropy, 18, seed, n), fsteps, cfg['ft_batch'], cfg['ft_lr'], keep_scaling=True)
            for key, value in T.change_fidelity_mono(tuned, test, tl2).items():
                out['ft_%s_%d_%s' % (name, n, key)] = value
    opponents = {'rush': T.rush_policy, 'kiter': T.kiter_policy}
    for cell, policy in controllers.items():      # every controller plays the same episodes (paired)
        for m, (oppname, opp) in enumerate(opponents.items()):
            out['score_%s_%s' % (cell, oppname)] = T.win_score(policy, T.SEEN_MIXES, opp, stream(entropy, 19, seed, m), cfg['eval_episodes'])
    for key, value in out.items():
        if isinstance(value, float) and not np.isfinite(value):
            raise FloatingPointError('non-finite result for '+key)
    out['seconds'] = time.perf_counter()-started
    return out


def seed_job(args):
    cfg, entropy, seed = args
    try:
        return run_seed(cfg, entropy, seed)
    except Exception as error:  # noqa: BLE001 - recorded, never silently dropped
        return {'status': 'ERROR', 'seed': seed, 'error': repr(error)}


# ---------------------------------------------------------------- predeclared verdicts

col, stats = r1.col, r1.stats


def needs_relative(rows, prefix, pre_prefix, cfg):
    """Per seed, the smallest number of new rows at which the design is back within a margin of its OWN pre-change quality (chance-corrected agreement,
    and the step against the best-matching tied-best enemy); inf if never."""
    out = []
    for r in rows:
        need = float('inf')
        for n in cfg['grid']:
            if r1.recovered(r.get('%s_%d_%s' % (prefix, n, AGREE)), r.get('%s_%d_%s' % (prefix, n, STEP)),
                            r.get('pre_%s_%s' % (pre_prefix, AGREE)), r.get('pre_%s_%s' % (pre_prefix, STEP)), cfg):
                need = float(n)
                break
        out.append(need)
    return np.array(out)


def needs_level(rows, prefix, level, cfg):
    """Per seed, the smallest number of new rows at which raw tie-aware agreement reaches a common absolute level (inf if never)."""
    return np.array([next((float(n) for n in cfg['grid'] if (r.get('%s_%d_%s' % (prefix, n, RAW)) or 0) >= level), float('inf')) for r in rows])


def rows_by_share(needs, cfg):
    """The smallest grid value by which at least half of the seeds have recovered (a grid value, never interpolated; inf if never)."""
    return next((float(n) for n in cfg['grid'] if np.mean(needs <= n) >= cfg['rows_share']), float('inf'))


def ratio_verdict(wired, big):
    return 'SUPPORTED' if big >= 3*wired else 'REFUTED' if big <= wired else 'INDETERMINATE'


def evaluate(rows, cfg):
    """SPECIFICATION_CHANGE2.md rules. SUPPORTED: the median and at least 75% of seeds meet the bar (where the bar is stated for seeds); REFUTED: the
    median misses by the stated margin; INDETERMINATE otherwise."""
    out = {}
    grid = cfg['grid']
    same = col(rows, 'same_target_teacher1_teacher2_multi')
    old = col(rows, 'old_composed_%s_vs_new' % RAW)
    c1 = bool(np.median(same) <= 0.70 and np.median(old) <= 0.75)
    out['C1_the_change_is_real'] = {
        'same_target_old_vs_new_doctrine_tie_aware': stats(same), 'old_composed_agreement_with_new_doctrine': stats(old),
        'old_big_equal_agreement_with_new_doctrine': stats(col(rows, 'old_mono_eq_%s_vs_new' % RAW)),
        'tie_share_of_multi_enemy_states_under_new_doctrine': stats(col(rows, 'composed_%d_tie_share_multi' % grid[-1])),
        'chance_agreement_old_doctrine': stats(col(rows, 'pre_composed_chance_tie_aware_multi')),
        'chance_agreement_new_doctrine': stats(col(rows, 'composed_%d_chance_tie_aware_multi' % grid[-1])),
        'share_of_seeds_with_same_target_at_most_0.70': float(np.mean(same <= 0.70)),
        'verdict': 'SUPPORTED' if c1 else 'REFUTED' if np.median(same) > 0.85 else 'INDETERMINATE'}
    n2 = cfg['c2_rows']
    pre_c = col(rows, 'pre_composed_%s' % AGREE)
    ok_c = np.array([r1.recovered(r.get('composed_%d_%s' % (n2, AGREE)), r.get('composed_%d_%s' % (n2, STEP)),
                                  r.get('pre_composed_%s' % AGREE), r.get('pre_composed_%s' % STEP), cfg) for r in rows])
    top_c, top_max = col(rows, 'composed_%d_%s' % (n2, AGREE)), col(rows, 'composed_%d_%s' % (grid[-1], AGREE))
    c2 = bool(c1 and np.median(top_c) >= np.median(pre_c)-cfg['recover_agreement_margin'] and ok_c.mean() >= 0.75)
    out['C2_cheap_change_for_the_wired_unit'] = {
        'rows': n2, 'chance_corrected_agreement_with_new_doctrine': stats(top_c), 'own_chance_corrected_agreement_before_the_change': stats(pre_c),
        'raw_tie_aware_agreement_with_new_doctrine': stats(col(rows, 'composed_%d_%s' % (n2, RAW))),
        'share_of_seeds_recovered': float(ok_c.mean()), 'chance_corrected_agreement_at_largest_grid': stats(top_max),
        'verdict': 'INDETERMINATE' if not c1 else 'SUPPORTED' if c2 else 'REFUTED' if np.median(top_max) < np.median(pre_c)-cfg['c2_refute_margin'] else 'INDETERMINATE'}
    rel = {p: needs_relative(rows, p, p, cfg) for p in ('composed', 'mono_eq', 'mono_large')}
    ab = {p: needs_level(rows, p, cfg['common_level'], cfg) for p in ('composed', 'mono_eq', 'mono_large')}
    rc, rm, rl = (rows_by_share(rel[p], cfg) for p in ('composed', 'mono_eq', 'mono_large'))
    ac, am, al = (rows_by_share(ab[p], cfg) for p in ('composed', 'mono_eq', 'mono_large'))
    v_rel, v_abs = ratio_verdict(rc, rm), ratio_verdict(ac, am)
    out['C3_cheaper_than_retraining_the_big_controller'] = {
        'relative_view_rows_needed_by_half_of_seeds': {'wired': rc, 'big_equal': rm, 'big_large': rl}, 'relative_view_verdict': v_rel,
        'common_level_view_level': cfg['common_level'], 'common_level_view_rows_needed_by_half_of_seeds': {'wired': ac, 'big_equal': am, 'big_large': al},
        'common_level_view_verdict': v_abs,
        'own_chance_corrected_agreement_before_the_change': {'wired': stats(pre_c), 'big_equal': stats(col(rows, 'pre_mono_eq_%s' % AGREE)), 'big_large': stats(col(rows, 'pre_mono_large_%s' % AGREE))},
        'share_of_seeds_never_recovering_within_the_grid_relative_view': {p: float(np.mean(np.isinf(rel[p]))) for p in rel},
        'verdict': 'INDETERMINATE' if not c2 else v_rel if v_rel == v_abs else 'INDETERMINATE'}
    def by_n(prefix, key):
        return {str(n): stats(col(rows, '%s_%d_%s' % (prefix, n, key))) for n in grid if len(col(rows, '%s_%d_%s' % (prefix, n, key)))}
    score = lambda cell: np.mean([col(rows, 'score_%s_%s' % (cell, o)) for o in OPPONENTS], axis=0)
    teacher2 = score('teacher2')
    absolute = lambda prefix: {str(n): float(np.mean([(r.get('%s_%d_%s' % (prefix, n, RAW)) or 0) >= cfg['absolute_agreement_levels'][-1] and
                                                      (r.get('%s_%d_%s' % (prefix, n, STEP)) or 1e9) <= cfg['absolute_angle_bar_deg'] for r in rows])) for n in grid}
    ft = {}
    for prefix, pre in (('ft_composed', 'composed'), ('ft_mono_eq', 'mono_eq'), ('ft_mono_large', 'mono_large')):
        ft[prefix] = {'rows_needed_by_half_of_seeds_relative_view': rows_by_share(needs_relative(rows, prefix, pre, cfg), cfg),
                      'raw_agreement_by_rows': by_n(prefix, RAW)}
    out['descriptive'] = {
        'raw_tie_aware_agreement_by_rows_retrain_from_scratch': {p: by_n(p, RAW) for p in ('composed', 'mono_eq', 'mono_large')},
        'chance_corrected_agreement_by_rows_retrain_from_scratch': {p: by_n(p, AGREE) for p in ('composed', 'mono_eq', 'mono_large')},
        'step_angle_best_matching_tie_by_rows_retrain_from_scratch': {p: by_n(p, STEP) for p in ('composed', 'mono_eq', 'mono_large')},
        'own_step_angle_before_the_change': {p: stats(col(rows, 'pre_%s_%s' % (p, STEP))) for p in ('composed', 'mono_eq', 'mono_large')},
        'rows_to_reach_an_absolute_agreement_level_by_half_of_seeds': {p: {str(level): rows_by_share(needs_level(rows, p, level, cfg), cfg) for level in cfg['absolute_agreement_levels']}
                                                                       for p in ('composed', 'mono_eq', 'mono_large')},
        'share_of_seeds_meeting_the_absolute_bars_0.95_and_10deg': {p: absolute(p) for p in ('composed', 'mono_eq', 'mono_large')},
        'fine_tuning_protocol_of_the_first_revision': ft,
        'win_score_minus_teacher2_by_rows_retrain_from_scratch': {p: {str(n): stats(score('%s_%d' % (p, n))-teacher2) for n in grid} for p in ('composed', 'mono_eq')},
        'win_score_minus_teacher2_before_change': {'composed_old': stats(score('composed_old')-teacher2), 'mono_eq_old': stats(score('mono_eq_old')-teacher2),
                                                   'rush': stats(score('rush')-teacher2)},
        'build_seconds_by_rows': {p: {str(n): stats(col(rows, 'build_%s_%d' % (p, n))) for n in grid} for p in ('composed', 'mono_eq', 'mono_large')},
        'retraining_steps_by_rows': {str(n): int(rows[0]['scratch_steps_%d' % n]) for n in grid}, 'seconds_per_seed': stats(col(rows, 'seconds'))}
    return out


# ---------------------------------------------------------------- specification, preflight and the run

def write_spec():
    path = HERE/'SPEC_CHANGE2.json'
    if path.exists():
        raise SystemExit('SPEC_CHANGE2.json already exists; the entropy is generated once')
    demo.write_json(path, {'note': 'Generated once by --write-spec; config refreshed from the code before the specification commit.',
                           'entropy': secrets.randbits(96), 'smoke_entropy': secrets.randbits(96), 'config': CONFIG, 'smoke_overrides': SMOKE})
    print('wrote', path)


def preflight(smoke):
    if smoke:
        return {'git': 'not enforced for smoke'}
    rel = str(HERE.relative_to(ROOT))
    for name in FILES:
        if subprocess.run(['git', 'ls-files', '--error-unmatch', rel+'/'+name], cwd=ROOT, capture_output=True).returncode:
            raise SystemExit(name+' is not committed; commit the specification and code first')
    status = subprocess.run(['git', 'status', '--porcelain', '--', rel], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    dirty = [line for line in status if not any(m in line for m in ('/run/', '/smoke_run/', '/run_change', '/smoke_run_change', '/run_change2', '/smoke_run_change2'))
             and not line.endswith(('/run', '/smoke_run'))]
    if dirty:
        raise SystemExit('uncommitted changes: '+'; '.join(dirty))
    return {'git_head': subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()}


def main_run(smoke):
    spec = json.loads((HERE/'SPEC_CHANGE2.json').read_text())
    cfg = dict(spec['config'])
    if smoke:
        cfg.update(spec['smoke_overrides'])
    entropy = spec['smoke_entropy'] if smoke else spec['entropy']
    guard = preflight(smoke)
    run_dir = HERE/('smoke_run_change2' if smoke else 'run_change2')
    try:
        os.mkdir(run_dir)
    except FileExistsError:
        raise SystemExit('%s exists: the one-shot latch is consumed; no resume, no retry' % run_dir.name)
    started, deadline = time.monotonic(), time.monotonic()+cfg['soft_cap']
    summary = {'status': 'INCOMPLETE', 'smoke': smoke, 'reason': 'not finished'}
    rows, errors, pool, watchdog = {}, {}, None, None
    try:
        (run_dir/'seeds').mkdir()
        for var in ('OMP_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
            os.environ[var] = '1'
        demo.write_json(run_dir/'RUN_STARTED.json', {
            'smoke': smoke, 'guard': guard, 'numpy': np.__version__, 'python': sys.version.split()[0], 'workers': cfg['workers'],
            'hashes': {n: hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in FILES if (HERE/n).exists()},
            'wall_clock': time.strftime('%Y-%m-%dT%H:%M:%S%z')})
        watchdog = demo.start_watchdog(run_dir, cfg['hard_cap'])
        pool = cf.ProcessPoolExecutor(max_workers=cfg['workers'], mp_context=mp.get_context('spawn'))

        def on_result(job, result):
            seed = job[2]
            if result.get('status') == 'ERROR':
                errors[seed] = result
                demo.write_json(run_dir/'seeds'/('error_%02d.json' % seed), result)
            else:
                rows[seed] = result
                demo.write_json(run_dir/'seeds'/('seed_%02d.json' % seed), result)

        status, sub, fin = demo.run_jobs(pool, seed_job, [(cfg, entropy, s) for s in range(cfg['seeds'])], on_result, deadline, cfg['workers'])
        summary['reason'] = 'complete' if status == 'done' else 'stopped: '+status
    except BaseException as error:  # noqa: BLE001
        summary['reason'] = 'exception: '+repr(error)
    finally:
        try:
            if pool is not None:
                demo.terminate(pool)
        except Exception as error:  # noqa: BLE001
            summary['cleanup_error'] = repr(error)
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        ordered = [rows[s] for s in sorted(rows)]
        summary.update({'wall_seconds': time.monotonic()-started, 'children_cpu_seconds': usage.ru_utime+usage.ru_stime,
                        'max_child_rss_bytes': int(usage.ru_maxrss), 'seeds_expected': cfg['seeds'], 'seeds_complete': len(rows),
                        'seed_errors': list(errors.values()), 'config': cfg})
        try:
            if summary['reason'] == 'complete' and not errors and len(rows) == cfg['seeds']:
                summary['evaluation'] = evaluate(ordered, cfg)
                summary['status'] = 'COMPLETE'
        except Exception as error:  # noqa: BLE001
            summary['evaluation_error'] = repr(error)
        try:
            demo.write_json(run_dir/'SUMMARY.json', summary)
        except Exception as error:  # noqa: BLE001
            demo.atomic_write(run_dir/'SUMMARY.json', json.dumps({'status': 'INCOMPLETE', 'reason': 'summary write failed: '+repr(error)}).encode())
        if watchdog is not None:
            watchdog.cancel()
    print(json.dumps({k: summary[k] for k in ('status', 'reason', 'wall_seconds', 'seeds_complete')}, indent=1))
    if summary['status'] == 'COMPLETE':
        print(json.dumps({k: v['verdict'] for k, v in summary['evaluation'].items() if 'verdict' in v}, indent=1))
    return 0 if summary['status'] == 'COMPLETE' else 1


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
