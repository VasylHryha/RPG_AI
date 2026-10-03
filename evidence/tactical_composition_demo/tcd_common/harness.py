"""One-shot experiment harness for new exploratory runs: commit guard, run-directory latch, spawn pool, watchdog, atomic summary.

Generic over the job function and the evaluation. Every stage is bounded: the jobs by soft_cap and hard_cap, evaluation and the summary write by eval_cap. The registered rules live in the experiment's own evaluate(); nothing here judges a result.
"""
import concurrent.futures as cf
import hashlib
import json
import multiprocessing as mp
import os
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from .fileio import atomic_write, write_json
from .supervise import Watchdog, run_jobs, terminate

THREAD_VARS = ('OMP_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS')


def _git(root, *args):
    return subprocess.run(['git', *args], cwd=root, capture_output=True, text=True)


def dirty_paths(root, rel):
    """Paths under `rel` that differ from HEAD (modified, staged or untracked, files listed individually), repo-relative."""
    out = _git(root, 'status', '--porcelain', '-z', '--untracked-files=all', '--', rel).stdout.split('\0')
    paths, i = [], 0
    while i < len(out):
        entry = out[i]
        i += 1
        if len(entry) < 4:
            continue
        paths.append(entry[3:])
        if entry[0] in 'RC':   # a rename or copy is followed by its source path
            i += 1
    return paths


def preflight(root, here, files, run_dirs, smoke):
    """Every file the run depends on is committed and unmodified. Only the experiment's own run directories (exact folder names) may be untracked."""
    if smoke:
        return {'git': 'not enforced for smoke'}
    rel = str(Path(here).relative_to(root))
    for name in files:
        if _git(root, 'ls-files', '--error-unmatch', rel+'/'+name).returncode:
            raise SystemExit(name+' is not committed; commit the specification and code first')
    ignored = tuple(rel+'/'+d for d in run_dirs)
    dirty = [p for p in dirty_paths(root, rel) if not any(p == d or p.startswith(d+'/') for d in ignored)]
    if dirty:
        raise SystemExit('uncommitted changes: '+'; '.join(dirty))
    return {'git_head': _git(root, 'rev-parse', 'HEAD').stdout.strip()}


def max_rss_bytes(usage):
    """ru_maxrss is bytes on macOS and kibibytes elsewhere."""
    return int(usage.ru_maxrss) * (1 if sys.platform == 'darwin' else 1024)


def run_experiment(*, spec_path, here, root, files, run_dirs, run_name, seed_job, evaluate, smoke, exit_fn=os._exit, kill_children=True):
    """The single recorded run (or the smoke run). `run_dirs` are all of this experiment's run and smoke directory names; `run_name` is this one.
    Returns (exit_code, summary)."""
    spec = json.loads(Path(spec_path).read_text())
    cfg = dict(spec['config'])
    if smoke:
        cfg.update(spec['smoke_overrides'])
    entropy = spec['smoke_entropy'] if smoke else spec['entropy']
    guard = preflight(root, here, files, run_dirs, smoke)
    run_dir = Path(here)/run_name
    try:
        os.mkdir(run_dir)
    except FileExistsError:
        raise SystemExit('%s exists: the one-shot latch is consumed; no resume, no retry' % run_dir.name)
    started, deadline = time.monotonic(), time.monotonic()+cfg['soft_cap']
    summary = {'status': 'INCOMPLETE', 'smoke': smoke, 'reason': 'not finished'}
    rows, errors, pool, watchdog = {}, {}, None, None
    try:
        (run_dir/'seeds').mkdir()
        cfg['run_dir'] = str(run_dir)   # workers may write per-seed artifacts (for example model weights) under it
        for var in THREAD_VARS:
            os.environ[var] = '1'
        write_json(run_dir/'RUN_STARTED.json', {
            'smoke': smoke, 'guard': guard, 'numpy': np.__version__, 'python': sys.version.split()[0], 'platform': platform.platform(), 'workers': cfg['workers'],
            'hashes': {n: hashlib.sha256((Path(here)/n).read_bytes()).hexdigest() for n in files if (Path(here)/n).exists()},
            'wall_clock': time.strftime('%Y-%m-%dT%H:%M:%S%z')})
        pool = cf.ProcessPoolExecutor(max_workers=cfg['workers'], mp_context=mp.get_context('spawn'))
        watchdog = Watchdog(run_dir, cfg['hard_cap'], cleanup=lambda: terminate(pool), exit_fn=exit_fn, kill_children=kill_children).start()

        def on_result(job, result):
            seed = job[2]
            if result.get('status') == 'ERROR':
                errors[seed] = result
                write_json(run_dir/'seeds'/('error_%02d.json' % seed), result)
            else:
                rows[seed] = result
                write_json(run_dir/'seeds'/('seed_%02d.json' % seed), result)

        status, _, _ = run_jobs(pool, seed_job, [(cfg, entropy, s) for s in range(cfg['seeds'])], on_result, deadline, cfg['workers'])
        summary['reason'] = 'complete' if status == 'done' else 'stopped: '+status
    except BaseException as error:  # noqa: BLE001
        summary['reason'] = 'exception: '+repr(error)
    finally:
        try:
            if pool is not None:
                terminate(pool)
        except Exception as error:  # noqa: BLE001
            summary['cleanup_error'] = repr(error)
        # all jobs are over: stop the watchdog BEFORE evaluation, so a finished run is never relabelled INCOMPLETE by a late hard stop
        if watchdog is not None and not watchdog.cancel():
            return 3, summary   # the hard stop already fired and owns the exit
        jobs_seconds = time.monotonic()-started
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        ordered = [rows[s] for s in sorted(rows)]
        summary.update({'jobs_wall_seconds': jobs_seconds, 'children_cpu_seconds': usage.ru_utime+usage.ru_stime,
                        'max_child_rss_bytes': max_rss_bytes(usage), 'seeds_expected': cfg['seeds'], 'seeds_complete': len(rows),
                        'seed_errors': list(errors.values()), 'config': cfg})
        # evaluation and the summary write run under their OWN bound (cfg['eval_cap'], default 300 s), so no stage is unbounded and the time is accounted for
        eval_watchdog = Watchdog(run_dir, cfg.get('eval_cap', 300.0), exit_fn=exit_fn, kill_children=kill_children).start()
        eval_started = time.monotonic()
        try:
            if summary['reason'] == 'complete' and not errors and len(rows) == cfg['seeds']:
                summary['evaluation'] = evaluate(ordered, cfg)
                summary['status'] = 'COMPLETE'
        except Exception as error:  # noqa: BLE001
            summary['evaluation_error'] = repr(error)
        summary['evaluation_seconds'] = time.monotonic()-eval_started
        summary['total_wall_seconds'] = time.monotonic()-started
        if eval_watchdog.fired:
            return 3, summary   # the evaluation bound fired: its HARD_STOP and INCOMPLETE summary stand
        try:
            write_json(run_dir/'SUMMARY.json', summary)
        except Exception as error:  # noqa: BLE001
            atomic_write(run_dir/'SUMMARY.json', json.dumps({'status': 'INCOMPLETE', 'reason': 'summary write failed: '+repr(error)}).encode())
        if not eval_watchdog.cancel():
            return 3, summary   # the evaluation bound fired and owns the exit
    print(json.dumps({k: summary[k] for k in ('status', 'reason', 'total_wall_seconds', 'seeds_complete') if k in summary}, indent=1))
    if summary['status'] == 'COMPLETE':
        print(json.dumps({k: v['verdict'] for k, v in summary['evaluation'].items() if isinstance(v, dict) and 'verdict' in v}, indent=1))
    return (0 if summary['status'] == 'COMPLETE' else 1), summary
