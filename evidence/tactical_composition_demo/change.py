"""Change-cost test (Stage 0c). NOT a milestone, NOT C6 evidence. See MOTIVATION.md and SPECIFICATION_CHANGE.md.

The targeting doctrine changes (threat first). The wired unit retrains ONLY its AIM piece and reuses MOVE untouched; the one big controller must
relearn everything. How many labeled rows does each need to follow the new doctrine?

    python evidence/tactical_composition_demo/change.py --write-spec   # once, before the specification commit
    python evidence/tactical_composition_demo/change.py --smoke        # reduced run, own entropy, own directory
    python evidence/tactical_composition_demo/change.py --run          # the single recorded run
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
import demo  # noqa: E402  (shared helpers: streams, json, supervision)

STAGE0 = demo.CONFIG
CONFIG = {
    'seeds': 20, 'workers': 8, 'soft_cap': 2700.0, 'hard_cap': 3000.0,
    'train_episodes': 600, 'test_episodes': 60, 'eval_episodes': 40,
    'grid': [100, 300, 1000, 3000], 'ft_epochs': 60, 'ft_steps_floor': 200, 'ft_steps_cap': 2000, 'ft_batch': 64, 'ft_lr': 0.002,
    'recover_agreement_margin': 0.02, 'recover_angle_margin_deg': 3.0, 'absolute_agreement_bar': 0.95, 'absolute_angle_bar_deg': 10.0,
    'stage0': {k: STAGE0[k] for k in ('n_aim', 'n_move', 'piece_hidden', 'piece_steps', 'batch', 'lr')},
    'mono_equal': STAGE0['monolith'][0], 'mono_large': STAGE0['monolith'][2]}
SMOKE = {'seeds': 2, 'workers': 2, 'soft_cap': 600.0, 'hard_cap': 800.0, 'train_episodes': 40, 'test_episodes': 8, 'eval_episodes': 3,
         'grid': [50, 100], 'ft_steps_floor': 20, 'ft_steps_cap': 100,
         'stage0': {'n_aim': 300, 'n_move': 300, 'piece_hidden': 16, 'piece_steps': 200, 'batch': 128, 'lr': 0.003},
         'mono_equal': {'rows': 600, 'hidden': 15, 'steps': 300}, 'mono_large': {'rows': 2400, 'hidden': 60, 'steps': 400}}
OPPONENTS = ('rush', 'kiter')
FILES = ('MOTIVATION.md', 'SPECIFICATION_CHANGE.md', 'SPEC_CHANGE.json', 'change.py', 'tactics.py', 'demo.py', 'test_change.py', 'test_tactics.py')


def stream(entropy, *key):
    return demo.stream(entropy, *key)


def ft_steps(n, cfg):
    """The same schedule for every design: a fixed number of epochs over the new rows, floored and capped."""
    batch = min(cfg['ft_batch'], n)
    return int(min(cfg['ft_steps_cap'], max(cfg['ft_steps_floor'], np.ceil(cfg['ft_epochs']*n/batch))))


def recovered(agree, step_angle, pre_agree, pre_angle, cfg):
    """A design has followed the new doctrine when it is back within a small margin of ITS OWN quality before the change."""
    return (agree is not None and step_angle is not None and pre_agree is not None and pre_angle is not None
            and agree >= pre_agree-cfg['recover_agreement_margin'] and step_angle <= pre_angle+cfg['recover_angle_margin_deg'])


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
    out['same_target_teacher1_teacher2_multi'] = float(np.mean((tl2['scores'][np.arange(len(best2)), tl1['target']] >= best2-1e-9)[multi]))   # tie-aware
    # the controllers as they were taught under the original doctrine (as in Stage 0)
    data = T.piece_datasets(pool, lab1, s0['n_aim'], s0['n_move'], stream(entropy, 3, seed))
    aim1 = T.MLP(T.AIM_DIM, s0['piece_hidden'], 1, stream(entropy, 4, seed, 0)).fit(*data['AIM'], stream(entropy, 5, seed, 0), s0['piece_steps'], s0['batch'], s0['lr'])
    move = T.MLP(T.MOVE_DIM, s0['piece_hidden'], 2, stream(entropy, 4, seed, 1)).fit(*data['MOVE'], stream(entropy, 5, seed, 1), s0['piece_steps'], s0['batch'], s0['lr'])
    bigs = {}
    for j, (name, spec) in enumerate((('mono_eq', cfg['mono_equal']), ('mono_large', cfg['mono_large']))):
        X, Y = T.mono_dataset(pool, lab1, spec['rows'], stream(entropy, 6, seed, j))
        bigs[name] = T.MLP(T.MONO_IN, spec['hidden'], T.MONO_OUT, stream(entropy, 7, seed, j)).fit(X, Y, stream(entropy, 8, seed, j), spec['steps'], s0['batch'], s0['lr'])
    # each design's own quality before the change (against the OLD doctrine) and its distance from the NEW doctrine
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
    # the change: AIM retrains alone (MOVE is reused untouched); each big controller relearns everything
    for n in cfg['grid']:
        steps = ft_steps(n, cfg)
        out['ft_steps_%d' % n] = steps
        t0 = time.perf_counter()
        X, Y = T.aim_dataset(pool, lab2, n, stream(entropy, 9, seed, n))
        if len(X) != n:
            raise RuntimeError('AIM fine-tuning set is smaller than requested')
        aim2 = copy.deepcopy(aim1).fit(X, Y, stream(entropy, 10, seed, n), steps, cfg['ft_batch'], cfg['ft_lr'], keep_scaling=True)
        out['build_composed_%d' % n] = time.perf_counter()-t0
        out['train_rmse_composed_%d' % n] = float(np.sqrt(np.mean((aim2.predict(X)-Y)**2)))
        for key, value in T.change_fidelity_composed(aim2, move, test, tl2).items():
            out['composed_%d_%s' % (n, key)] = value
        controllers['composed_%d' % n] = T.composed_policy(aim2, move)
        for name, model in bigs.items():
            t0 = time.perf_counter()
            X, Y = T.mono_dataset(pool, lab2, n, stream(entropy, 11, seed, n))
            if len(X) != n:
                raise RuntimeError('big-controller fine-tuning set is smaller than requested')
            tuned = copy.deepcopy(model).fit(X, Y, stream(entropy, 12, seed, n), steps, cfg['ft_batch'], cfg['ft_lr'], keep_scaling=True)
            out['build_%s_%d' % (name, n)] = time.perf_counter()-t0
            out['train_rmse_%s_%d' % (name, n)] = float(np.sqrt(np.mean((tuned.predict(X)-Y)**2)))
            for key, value in T.change_fidelity_mono(tuned, test, tl2).items():
                out['%s_%d_%s' % (name, n, key)] = value
            if name == 'mono_eq':
                controllers['mono_eq_%d' % n] = T.mono_policy(tuned)
    opponents = {'rush': T.rush_policy, 'kiter': T.kiter_policy}
    for cell, policy in controllers.items():      # every controller plays the same episodes (paired)
        for m, (oppname, opp) in enumerate(opponents.items()):
            out['score_%s_%s' % (cell, oppname)] = T.win_score(policy, T.SEEN_MIXES, opp, stream(entropy, 13, seed, m), cfg['eval_episodes'])
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

def col(rows, key):
    return np.array([r[key] for r in rows if r.get(key) is not None], float)


def stats(values):
    return demo.stats(np.asarray(values, float))


AGREE, STEP = 'agree_tie_aware_multi', 'step_move_median_angle_deg'


def rows_needed(rows, prefix, cfg):
    """Per seed, the smallest number of fine-tuning rows at which the design is back within a margin of its OWN pre-change quality (inf if never)."""
    out = []
    for r in rows:
        need = float('inf')
        for n in cfg['grid']:
            if recovered(r.get('%s_%d_%s' % (prefix, n, AGREE)), r.get('%s_%d_%s' % (prefix, n, STEP)),
                         r.get('pre_%s_%s' % (prefix, AGREE)), r.get('pre_%s_%s' % (prefix, STEP)), cfg):
                need = float(n)
                break
        out.append(need)
    return np.array(out)


def evaluate(rows, cfg):
    """SPECIFICATION_CHANGE.md rules. SUPPORTED: the median and at least 75% of seeds meet the bar; REFUTED: the median misses by the stated margin."""
    out = {}
    grid = cfg['grid']
    same = col(rows, 'same_target_teacher1_teacher2_multi')
    old = col(rows, 'old_composed_%s_vs_new' % AGREE)
    real = (same <= 0.70) & (old <= 0.75)
    c1 = bool(np.median(same) <= 0.70 and np.median(old) <= 0.75 and real.mean() >= 0.75)
    out['C1_the_change_is_real'] = {'same_target_old_vs_new_doctrine_tie_aware': stats(same), 'old_composed_agreement_with_new_doctrine': stats(old),
                                    'old_big_equal_agreement_with_new_doctrine': stats(col(rows, 'old_mono_eq_%s_vs_new' % AGREE)),
                                    'tie_share_of_multi_enemy_states_under_new_doctrine': stats(col(rows, 'composed_%d_tie_share_multi' % grid[-1])),
                                    'share_of_seeds_meeting_bar': float(real.mean()),
                                    'verdict': 'SUPPORTED' if c1 else 'REFUTED' if np.median(same) > 0.85 else 'INDETERMINATE'}
    n_cheap = 300 if 300 in grid else grid[1]
    pre_c = col(rows, 'pre_composed_%s' % AGREE)
    ok_c = np.array([recovered(r.get('composed_%d_%s' % (n_cheap, AGREE)), r.get('composed_%d_%s' % (n_cheap, STEP)),
                               r.get('pre_composed_%s' % AGREE), r.get('pre_composed_%s' % STEP), cfg) for r in rows])
    top_cheap, top_max = col(rows, 'composed_%d_%s' % (n_cheap, AGREE)), col(rows, 'composed_%d_%s' % (grid[-1], AGREE))
    c2 = bool(c1 and np.median(top_cheap) >= np.median(pre_c)-cfg['recover_agreement_margin'] and ok_c.mean() >= 0.75)
    out['C2_cheap_change_for_the_wired_unit'] = {
        'rows': n_cheap, 'agreement_with_new_doctrine': stats(top_cheap), 'own_agreement_before_the_change': stats(pre_c),
        'share_of_seeds_recovered': float(ok_c.mean()), 'agreement_at_largest_grid': stats(top_max),
        'verdict': 'INDETERMINATE' if not c1 else 'SUPPORTED' if c2 else 'REFUTED' if np.median(top_max) < np.median(pre_c)-0.10 else 'INDETERMINATE'}
    need_c, need_m, need_l = (rows_needed(rows, p, cfg) for p in ('composed', 'mono_eq', 'mono_large'))
    mc, mm = float(np.median(need_c)), float(np.median(need_m))
    out['C3_cheaper_than_retraining_the_big_controller'] = {
        'rows_needed_wired_median': mc, 'rows_needed_big_equal_median': mm, 'rows_needed_big_large_median': float(np.median(need_l)),
        'own_agreement_before_the_change': {'wired': stats(pre_c), 'big_equal': stats(col(rows, 'pre_mono_eq_%s' % AGREE)), 'big_large': stats(col(rows, 'pre_mono_large_%s' % AGREE))},
        'share_of_seeds_never_recovering_within_the_grid': {'wired': float(np.mean(np.isinf(need_c))), 'big_equal': float(np.mean(np.isinf(need_m))),
                                                            'big_large': float(np.mean(np.isinf(need_l)))},
        'verdict': 'INDETERMINATE' if not c2 else 'SUPPORTED' if mm >= 3*mc else 'REFUTED' if mm <= mc else 'INDETERMINATE'}
    def by_n(prefix, key):
        return {str(n): stats(col(rows, '%s_%d_%s' % (prefix, n, key))) for n in grid if len(col(rows, '%s_%d_%s' % (prefix, n, key)))}
    score = lambda cell: np.mean([col(rows, 'score_%s_%s' % (cell, o)) for o in OPPONENTS], axis=0)
    teacher2 = score('teacher2')
    absolute = lambda prefix: {str(n): float(np.mean([(r.get('%s_%d_%s' % (prefix, n, AGREE)) or 0) >= cfg['absolute_agreement_bar'] and
                                                      (r.get('%s_%d_%s' % (prefix, n, STEP)) or 1e9) <= cfg['absolute_angle_bar_deg'] for r in rows])) for n in grid}
    out['descriptive'] = {
        'agreement_with_new_doctrine_by_rows': {p: by_n(p, AGREE) for p in ('composed', 'mono_eq', 'mono_large')},
        'step_angle_by_rows': {p: by_n(p, STEP) for p in ('composed', 'mono_eq', 'mono_large')},
        'share_of_seeds_meeting_the_absolute_bars_0.95_and_10deg': {p: absolute(p) for p in ('composed', 'mono_eq', 'mono_large')},
        'own_step_angle_before_the_change': {p: stats(col(rows, 'pre_%s_%s' % (p, STEP))) for p in ('composed', 'mono_eq', 'mono_large')},
        'win_score_minus_teacher2_by_rows': {p: {str(n): stats(score('%s_%d' % (p, n))-teacher2) for n in grid} for p in ('composed', 'mono_eq')},
        'win_score_minus_teacher2_before_change': {'composed_old': stats(score('composed_old')-teacher2), 'mono_eq_old': stats(score('mono_eq_old')-teacher2),
                                                   'rush': stats(score('rush')-teacher2)},
        'final_training_rmse_by_rows': {p: {str(n): stats(col(rows, 'train_rmse_%s_%d' % (p, n))) for n in grid} for p in ('composed', 'mono_eq', 'mono_large')},
        'build_seconds_by_rows': {p: {str(n): stats(col(rows, 'build_%s_%d' % (p, n))) for n in grid} for p in ('composed', 'mono_eq', 'mono_large')},
        'fine_tuning_steps_by_rows': {str(n): int(rows[0]['ft_steps_%d' % n]) for n in grid}, 'seconds_per_seed': stats(col(rows, 'seconds'))}
    return out


# ---------------------------------------------------------------- specification, preflight and the run

def write_spec():
    path = HERE/'SPEC_CHANGE.json'
    if path.exists():
        raise SystemExit('SPEC_CHANGE.json already exists; the entropy is generated once')
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
    dirty = [line for line in status if not any(m in line for m in ('/run/', '/smoke_run/', '/run_change', '/smoke_run_change')) and not line.endswith(('/run', '/smoke_run'))]
    if dirty:
        raise SystemExit('uncommitted changes: '+'; '.join(dirty))
    return {'git_head': subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()}


def main_run(smoke):
    spec = json.loads((HERE/'SPEC_CHANGE.json').read_text())
    cfg = dict(spec['config'])
    if smoke:
        cfg.update(spec['smoke_overrides'])
    entropy = spec['smoke_entropy'] if smoke else spec['entropy']
    guard = preflight(smoke)
    run_dir = HERE/('smoke_run_change' if smoke else 'run_change')
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
