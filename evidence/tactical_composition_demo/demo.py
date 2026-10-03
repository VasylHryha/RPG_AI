"""Tactical composition demo, Stage 0 (AIM + MOVE). NOT a milestone, NOT C6 evidence. See PROPOSAL.md and SPECIFICATION.md.

    python evidence/tactical_composition_demo/demo.py --write-spec   # once, before the specification commit
    python evidence/tactical_composition_demo/demo.py --smoke        # reduced run, own entropy, own directory
    python evidence/tactical_composition_demo/demo.py --run          # the single recorded run

Seeds run in parallel worker processes. There is no worker entry point: the only way to run work is --run / --smoke, which create the
exclusive run directory (the one-shot latch).
"""
import argparse
import concurrent.futures as cf
from concurrent.futures.process import BrokenProcessPool
import hashlib
import json
import multiprocessing as mp
import os
import resource
import secrets
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import tactics as T  # noqa: E402

CONFIG = {
    'seeds': 20, 'workers': 8, 'soft_cap': 2700.0, 'hard_cap': 3000.0,
    'train_episodes': 600, 'test_episodes': 60, 'eval_episodes': 60,
    'n_aim': 3000, 'n_move': 3000, 'piece_hidden': 16, 'piece_steps': 4000, 'batch': 128, 'lr': 0.003,
    'monolith': [{'rows': 6000, 'hidden': 15, 'steps': 8000}, {'rows': 24000, 'hidden': 30, 'steps': 16000},
                 {'rows': 96000, 'hidden': 60, 'steps': 32000}]}
SMOKE = {'seeds': 2, 'workers': 2, 'soft_cap': 600.0, 'hard_cap': 800.0, 'train_episodes': 40, 'test_episodes': 8, 'eval_episodes': 4,
         'n_aim': 300, 'n_move': 300, 'piece_steps': 300,
         'monolith': [{'rows': 600, 'hidden': 15, 'steps': 600}, {'rows': 1200, 'hidden': 30, 'steps': 800},
                      {'rows': 2400, 'hidden': 60, 'steps': 1000}]}
OPPONENTS = ('rush', 'kiter')
FLOOR_MARGIN = 0.15


# ---------------------------------------------------------------- io helpers

def atomic_write(path, data):
    path = Path(path)
    tmp = path.with_name(path.name+'.tmp%d' % os.getpid())
    with open(tmp, 'wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return jsonable(value.tolist())
    if isinstance(value, np.generic):
        return jsonable(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return 'Infinity' if value > 0 else '-Infinity' if value < 0 else 'NaN'
    return value


def write_json(path, obj):
    atomic_write(path, json.dumps(jsonable(obj), sort_keys=True, indent=1).encode())


def stream(entropy, *key):
    return np.random.default_rng(np.random.SeedSequence([entropy, *key]))


# ---------------------------------------------------------------- one seed

def run_seed(cfg, entropy, seed):
    """Teach the pieces and the one big controller, then play. Returns scalars only."""
    started = time.perf_counter()
    out = {'seed': seed}
    pool = T.collect(stream(entropy, 1, seed), cfg['train_episodes'], T.SEEN_MIXES)
    lab = T.labels(pool)
    test = T.collect(stream(entropy, 2, seed), cfg['test_episodes'], T.SEEN_MIXES)
    tlab = T.labels(test)
    need = max(m['rows'] for m in cfg['monolith'])
    if len(pool['own']) < need:
        raise RuntimeError('training pool has %d states, fewer than the %d rows requested' % (len(pool['own']), need))
    out['pool_states'] = len(pool['own'])
    data = T.piece_datasets(pool, lab, cfg['n_aim'], cfg['n_move'], stream(entropy, 3, seed))
    if len(data['AIM'][0]) != cfg['n_aim'] or len(data['MOVE'][0]) != cfg['n_move']:
        raise RuntimeError('piece datasets are smaller than requested')
    t0 = time.perf_counter()
    aim = T.MLP(T.AIM_DIM, cfg['piece_hidden'], 1, stream(entropy, 4, seed, 0)).fit(*data['AIM'], stream(entropy, 5, seed, 0), cfg['piece_steps'], cfg['batch'], cfg['lr'])
    move = T.MLP(T.MOVE_DIM, cfg['piece_hidden'], 2, stream(entropy, 4, seed, 1)).fit(*data['MOVE'], stream(entropy, 5, seed, 1), cfg['piece_steps'], cfg['batch'], cfg['lr'])
    out['build_seconds_pieces'] = time.perf_counter()-t0
    out['pieces_rows'] = len(data['AIM'][0])+len(data['MOVE'][0])      # actual rows, asserted equal to the configured ones above
    out['pieces_parameters'] = T.MLP.parameter_count(T.AIM_DIM, cfg['piece_hidden'], 1)+T.MLP.parameter_count(T.MOVE_DIM, cfg['piece_hidden'], 2)
    for key, value in T.fidelity({'AIM': aim, 'MOVE': move}, test, tlab).items():
        out['fid_'+key] = value
    policies = {'teacher': T.teacher_policy, 'rush': T.rush_policy, 'composed': T.composed_policy(aim, move)}
    for j, spec in enumerate(cfg['monolith']):
        X, Y = T.mono_dataset(pool, lab, spec['rows'], stream(entropy, 6, seed, j))
        if len(X) != spec['rows']:
            raise RuntimeError('monolith dataset is smaller than requested')
        out['mono_%d_rows_actual' % j] = len(X)
        t0 = time.perf_counter()
        model = T.MLP(T.MONO_IN, spec['hidden'], T.MONO_OUT, stream(entropy, 7, seed, j)).fit(X, Y, stream(entropy, 8, seed, j), spec['steps'], cfg['batch'], cfg['lr'])
        out['build_seconds_mono_%d' % j] = time.perf_counter()-t0
        out['mono_%d_parameters' % j] = T.MLP.parameter_count(T.MONO_IN, spec['hidden'], T.MONO_OUT)
        for key, value in T.mono_fidelity(model, test, tlab).items():
            out['fid_mono_%d_%s' % (j, key)] = value
        policies['mono_%d' % j] = T.mono_policy(model)
    opponents = {'rush': T.rush_policy, 'kiter': T.kiter_policy}
    for cell, policy in policies.items():     # every controller plays the same episodes (same mixes and start positions): paired
        for mixname, mixes in (('seen', T.SEEN_MIXES), ('unseen', T.UNSEEN_MIXES)):
            for m, (oppname, opp) in enumerate(opponents.items()):
                out['score_%s_%s_%s' % (cell, mixname, oppname)] = T.win_score(policy, mixes, opp, stream(entropy, 9, seed, m, int(mixname == 'unseen')), cfg['eval_episodes'])
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

def column(rows, key):
    return np.array([r[key] for r in rows if key in r], float)


def avg_over_opponents(row, cell, mixname):
    return float(np.mean([row['score_%s_%s_%s' % (cell, mixname, o)] for o in OPPONENTS]))


def series(rows, cell, mixname):
    return np.array([avg_over_opponents(r, cell, mixname) for r in rows])


def stats(values):
    return {'median': float(np.median(values)), 'q1': float(np.quantile(values, .25)), 'q3': float(np.quantile(values, .75)), 'n': int(len(values))}


def share(mask):
    return float(np.mean(mask))


def paired(rows, cell_a, cell_b, mixname):
    return series(rows, cell_a, mixname)-series(rows, cell_b, mixname)


def evaluate(rows, cfg):
    """SPECIFICATION.md rules. Comparisons are paired per seed. SUPPORTED: the median and at least 75% of seeds meet the bar; REFUTED:
    the median misses by the stated margin; INDETERMINATE otherwise."""
    out = {}
    aim, ang, hold = column(rows, 'fid_aim_top1'), column(rows, 'fid_move_median_angle_deg'), column(rows, 'fid_move_hold_agreement')
    floor = column(rows, 'fid_aim_nearest_enemy_floor')
    backoff = [r.get('fid_move_backoff_median_angle_deg') for r in rows]
    backoff_ok = np.array([b is None or b <= 20.0 for b in backoff])
    met = (aim >= 0.95) & (ang <= 10.0) & (hold >= 0.90) & backoff_ok
    out['P1_pieces_learn'] = {
        'aim_top1': stats(aim), 'aim_nearest_enemy_floor': stats(floor), 'move_median_angle_deg': stats(ang), 'move_hold_agreement': stats(hold),
        'move_backoff_median_angle_deg': stats(np.array([b for b in backoff if b is not None])) if any(b is not None for b in backoff) else None,
        'share_of_seeds_meeting_all_bars': share(met),
        'verdict': 'SUPPORTED' if (np.median(aim) >= 0.95 and np.median(ang) <= 10 and np.median(hold) >= 0.90 and backoff_ok.mean() >= 0.75 and share(met) >= 0.75)
        else 'REFUTED' if (np.median(aim) < 0.90 or np.median(ang) > 20) else 'INDETERMINATE'}
    teacher, rush, composed = (series(rows, c, 'seen') for c in ('teacher', 'rush', 'composed'))
    d_teacher, d_rush = composed-teacher, composed-rush
    ok2 = (d_teacher >= -0.10) & (d_rush >= FLOOR_MARGIN)
    clears = bool(np.median(d_teacher) >= -0.10 and np.median(d_rush) >= FLOOR_MARGIN and share(ok2) >= 0.75)
    out['P2_composed_unit_plays'] = {
        'teacher': stats(teacher), 'rush': stats(rush), 'composed': stats(composed),
        'composed_minus_teacher': stats(d_teacher), 'composed_minus_rush': stats(d_rush), 'share_of_seeds_meeting_bar': share(ok2),
        'verdict': 'SUPPORTED' if clears else 'REFUTED' if (np.median(d_rush) < 0.05 or np.median(d_teacher) < -0.20) else 'INDETERMINATE'}
    n_mono = len(cfg['monolith'])
    d_mono = [composed-series(rows, 'mono_%d' % j, 'seen') for j in range(n_mono)]            # composed minus each big controller
    adequate_gap = series(rows, 'mono_%d' % (n_mono-1), 'seen')-rush                             # largest big controller minus rush
    adequate = bool(np.median(adequate_gap) >= FLOOR_MARGIN)
    d_unseen = series(rows, 'composed', 'unseen')-series(rows, 'mono_0', 'unseen')
    s3 = clears and adequate and np.median(d_mono[0]) >= 0.10 and share(d_mono[0] >= 0.10) >= 0.75 \
        and np.median(d_unseen) >= 0.10 and share(d_unseen >= 0.10) >= 0.75
    out['P3_composition_beats_one_big_controller'] = {
        'composed_minus_mono_equal_budget_seen': stats(d_mono[0]), 'composed_minus_mono_equal_budget_unseen_type': stats(d_unseen),
        'mono_equal_budget_seen': stats(series(rows, 'mono_0', 'seen')), 'composed_clears_P2': clears,
        'largest_mono_minus_rush': stats(adequate_gap), 'baseline_adequate_largest_mono_beats_rush_by_0.15': adequate,
        'verdict': 'SUPPORTED' if s3 else 'REFUTED' if np.median(d_mono[0]) < 0.03 else 'INDETERMINATE'}
    matches = [bool(np.median(-d) >= -0.03) for d in d_mono]                                      # big controller within 0.03 of, or above, the composed one
    scaled_match = any(matches[1:])
    v4 = 'REFUTED' if matches[0] else 'INDETERMINATE' if (not clears or not adequate or scaled_match) else 'SUPPORTED'
    out['P4_data_needed_to_match'] = {
        'mono_medians_seen': [float(np.median(series(rows, 'mono_%d' % j, 'seen'))) for j in range(n_mono)],
        'composed_median_seen': float(np.median(composed)), 'matches': matches, 'scales': cfg['monolith'],
        'smallest_matching_scale_index': next((j for j, m in enumerate(matches) if m), None), 'verdict': v4}
    un_teacher, un_rush, un_composed = (series(rows, c, 'unseen') for c in ('teacher', 'rush', 'composed'))
    d5_teacher, d5_rush = un_composed-un_teacher, un_composed-un_rush
    ok5 = (d5_teacher >= -0.15) & (d5_rush >= FLOOR_MARGIN)
    clears5 = bool(np.median(d5_teacher) >= -0.15 and np.median(d5_rush) >= FLOOR_MARGIN and share(ok5) >= 0.75)
    out['P5_new_unit_type_without_retraining'] = {
        'teacher_unseen': stats(un_teacher), 'rush_unseen': stats(un_rush), 'composed_unseen': stats(un_composed),
        'composed_minus_teacher': stats(d5_teacher), 'composed_minus_rush': stats(d5_rush),
        'mono_equal_budget_unseen': stats(series(rows, 'mono_0', 'unseen')), 'share_of_seeds_meeting_bar': share(ok5),
        'verdict': 'SUPPORTED' if clears5 else 'REFUTED' if np.median(d5_rush) < 0.05 else 'INDETERMINATE'}
    def per_opponent(cell, mixname):
        return {o: stats(column(rows, 'score_%s_%s_%s' % (cell, mixname, o))) for o in OPPONENTS}
    def mono_fid(j):
        keys = ('aim_top1', 'move_median_angle_deg', 'move_hold_agreement', 'move_backoff_median_angle_deg')
        return {k: stats(column(rows, 'fid_mono_%d_%s' % (j, k))) for k in keys if len(column(rows, 'fid_mono_%d_%s' % (j, k)))}
    out['descriptive'] = {
        'win_score_by_opponent_seen': {c: per_opponent(c, 'seen') for c in ('teacher', 'rush', 'composed', 'mono_0', 'mono_1', 'mono_2')},
        'win_score_by_opponent_unseen_type': {c: per_opponent(c, 'unseen') for c in ('teacher', 'rush', 'composed', 'mono_0', 'mono_1', 'mono_2')},
        'monolith_fidelity_to_teacher': {'mono_%d' % j: mono_fid(j) for j in range(n_mono)},
        'build_seconds_pieces': stats(column(rows, 'build_seconds_pieces')),
        'build_seconds_monolith': [stats(column(rows, 'build_seconds_mono_%d' % j)) for j in range(n_mono)],
        'rows_pieces': int(rows[0]['pieces_rows']), 'rows_monolith_actual': [int(rows[0]['mono_%d_rows_actual' % j]) for j in range(n_mono)],
        'pool_states': stats(column(rows, 'pool_states')),
        'parameters_pieces': int(rows[0]['pieces_parameters']), 'parameters_monolith': [int(rows[0]['mono_%d_parameters' % j]) for j in range(n_mono)],
        'seconds_per_seed': stats(column(rows, 'seconds'))}
    return out


# ---------------------------------------------------------------- supervision (as in the two-body pilot)

def terminate(pool):
    procs = list((getattr(pool, '_processes', None) or {}).values())
    try:
        pool.shutdown(wait=False, cancel_futures=True)
    except Exception:  # noqa: BLE001
        pass
    for p in procs:
        try:
            p.terminate()
        except Exception:  # noqa: BLE001
            pass
    deadline = time.monotonic()+5
    for p in procs:
        try:
            p.join(max(0.0, deadline-time.monotonic()))
            if p.is_alive():
                p.kill()
                p.join(2)
        except Exception:  # noqa: BLE001
            pass


def run_jobs(pool, fn, jobs, on_result, deadline, workers):
    """Bounded submission. Returns ('done'|'deadline'|'broken', submitted, finished). Never blocks past the deadline."""
    pending, finished, submitted, status = {}, 0, 0, 'done'
    iterator, exhausted = iter(jobs), False
    while True:
        while not exhausted and len(pending) < workers and time.monotonic() < deadline:
            try:
                job = next(iterator)
            except StopIteration:
                exhausted = True
                break
            pending[pool.submit(fn, job)] = job
            submitted += 1
        if not pending:
            break
        done, _ = cf.wait(list(pending), timeout=1.0, return_when=cf.FIRST_COMPLETED)
        for future in done:
            job = pending.pop(future)
            try:
                result = future.result()
            except BrokenProcessPool:
                status, result = 'broken', {'status': 'ERROR', 'seed': job[2], 'error': 'BrokenProcessPool'}
            except Exception as error:  # noqa: BLE001
                result = {'status': 'ERROR', 'seed': job[2], 'error': repr(error)}
            on_result(job, result)
            finished += 1
        if status == 'broken' or time.monotonic() >= deadline:
            status = status if status == 'broken' else 'deadline'
            break
    for future in pending:
        future.cancel()
    if status == 'done' and not exhausted:
        status = 'deadline'
    return status, submitted, finished


def start_watchdog(run_dir, hard_cap):
    def stop():
        try:
            subprocess.run(['pkill', '-9', '-P', str(os.getpid())], capture_output=True, timeout=10)
        finally:
            try:
                write_json(Path(run_dir)/'HARD_STOP.json', {'status': 'HARD_STOP', 'after_seconds': hard_cap})
            finally:
                try:
                    if not (Path(run_dir)/'SUMMARY.json').exists():
                        write_json(Path(run_dir)/'SUMMARY.json', {'status': 'INCOMPLETE', 'reason': 'hard stop after %s s' % hard_cap})
                finally:
                    os._exit(3)
    timer = threading.Timer(hard_cap, stop)
    timer.daemon = True
    timer.start()
    return timer


# ---------------------------------------------------------------- specification, preflight and the run

def write_spec():
    path = HERE/'SPEC.json'
    if path.exists():
        raise SystemExit('SPEC.json already exists; the entropy is generated once')
    write_json(path, {'note': 'Generated once by --write-spec; config refreshed from the code before the specification commit.',
                      'entropy': secrets.randbits(96), 'smoke_entropy': secrets.randbits(96), 'config': CONFIG, 'smoke_overrides': SMOKE})
    print('wrote', path)


FILES = ('PROPOSAL.md', 'SPECIFICATION.md', 'SPEC.json', 'demo.py', 'tactics.py', 'test_tactics.py', 'test_demo.py')


def preflight(smoke):
    if smoke:
        return {'git': 'not enforced for smoke'}
    rel = str(HERE.relative_to(ROOT))
    for name in FILES:
        if subprocess.run(['git', 'ls-files', '--error-unmatch', rel+'/'+name], cwd=ROOT, capture_output=True).returncode:
            raise SystemExit(name+' is not committed; commit the specification and code first')
    status = subprocess.run(['git', 'status', '--porcelain', '--', rel], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    dirty = [line for line in status if '/run/' not in line and '/smoke_run/' not in line and not line.endswith(('/run', '/smoke_run'))]
    if dirty:
        raise SystemExit('uncommitted changes: '+'; '.join(dirty))
    return {'git_head': subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()}


def main_run(smoke):
    spec = json.loads((HERE/'SPEC.json').read_text())
    cfg = dict(spec['config'])
    if smoke:
        cfg.update(spec['smoke_overrides'])
    entropy = spec['smoke_entropy'] if smoke else spec['entropy']
    guard = preflight(smoke)
    run_dir = HERE/('smoke_run' if smoke else 'run')
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
        write_json(run_dir/'RUN_STARTED.json', {
            'smoke': smoke, 'guard': guard, 'numpy': np.__version__, 'python': sys.version.split()[0], 'workers': cfg['workers'],
            'hashes': {n: hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in FILES if (HERE/n).exists()},
            'wall_clock': time.strftime('%Y-%m-%dT%H:%M:%S%z')})
        watchdog = start_watchdog(run_dir, cfg['hard_cap'])
        pool = cf.ProcessPoolExecutor(max_workers=cfg['workers'], mp_context=mp.get_context('spawn'))

        def on_result(job, result):
            seed = job[2]
            if result.get('status') == 'ERROR':
                errors[seed] = result
                write_json(run_dir/'seeds'/('error_%02d.json' % seed), result)
            else:
                rows[seed] = result
                write_json(run_dir/'seeds'/('seed_%02d.json' % seed), result)

        status, sub, fin = run_jobs(pool, seed_job, [(cfg, entropy, s) for s in range(cfg['seeds'])], on_result, deadline, cfg['workers'])
        summary['reason'] = 'complete' if status == 'done' else 'stopped: '+status
    except BaseException as error:  # noqa: BLE001
        summary['reason'] = 'exception: '+repr(error)
    finally:
        try:
            if pool is not None:
                terminate(pool)
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
            write_json(run_dir/'SUMMARY.json', summary)
        except Exception as error:  # noqa: BLE001
            atomic_write(run_dir/'SUMMARY.json', json.dumps({'status': 'INCOMPLETE', 'reason': 'summary write failed: '+repr(error)}).encode())
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
