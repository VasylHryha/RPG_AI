"""Exploratory two-body force-map pilot. NOT C6 evidence. See SPECIFICATION.md.

Scratch code outside geomind/. Reuses the project's level-generic modules read-only. There is no worker entry
point: the only way to run work is `--run` / `--smoke`, which create the exclusive run directory (the one-shot latch).

    python evidence/c6_dev_pilot/a_twobody/pilot.py --write-spec     # once, before the specification commit
    python evidence/c6_dev_pilot/a_twobody/pilot.py --smoke          # code-path smoke, its own entropy, own directory
    python evidence/c6_dev_pilot/a_twobody/pilot.py --run            # the single recorded run
    python evidence/c6_dev_pilot/a_twobody/pilot.py --interpret DIR  # read-only re-interpretation of a stored run
"""
import argparse
import concurrent.futures as cf
from concurrent.futures.process import BrokenProcessPool
import gzip
import hashlib
import json
import multiprocessing as mp
import os
import pickle
import resource
import secrets
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from geomind import c4_model, c6_native, c6_levels as levels, c6_compose as compose, c6_experiment as ex  # noqa: E402
from geomind.c5_experiment import assign_templates as assign_c5  # noqa: E402

DEPENDENCIES = [
    'geomind/c4_model.py', 'geomind/c4_detect.py', 'geomind/c4_experiment.py', 'geomind/c5_experiment.py',
    'geomind/c5_detect.py', 'geomind/c5_units.py', 'geomind/c5_compose.py', 'geomind/c5_coarse.py',
    'geomind/c6_native.py', 'geomind/c6_levels.py', 'geomind/c6_units.py', 'geomind/c6_experiment.py',
    'geomind/c6_compose.py', 'geomind/c6_effective.py', 'experiments/c4_manifest.json',
    'native/c6/element_law.cpp', 'build/c6/element_law.dylib', 'build/c6/BUILD.json',
    'pyproject.toml', 'uv.lock']
RUN_DIRS = ('run', 'smoke_run', 'smoke_level1_only')
CASES = ('natural', 'phase0', 'phase_halfpi', 'phase_pi')
FIXED_OFFSETS = {'phase0': 0.0, 'phase_halfpi': np.pi/2, 'phase_pi': np.pi}
DT = 0.02
RADIUS = 3.0
C1 = 1.0
EFFECTIVE_GAPS = (0.6, 1.2)   # phase-coupling weight exp(-gap^2) >= 0.1 (element law); wider gaps are tabulated, not scored
OFFSET_MIN = 1.0              # a lock is only informative from an initial offset outside the lock zone
SLOPE_FLOOR = 0.01            # L0/C0, ten times the decoupled drift noise


# ---------------------------------------------------------------- io helpers

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


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
        # Legitimate in diagnostics (for example an infinite overlap for a degenerate hull); float() reads it back.
        return 'Infinity' if value > 0 else '-Infinity' if value < 0 else 'NaN'
    return value


def atomic_write(path, data):
    path = Path(path)
    tmp = path.with_name(path.name + '.tmp%d' % os.getpid())
    with open(tmp, 'wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    fd = os.open(str(path.parent), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_json(path, obj, compress=False):
    data = json.dumps(jsonable(obj), sort_keys=True).encode()
    atomic_write(path, gzip.compress(data, 6) if compress else data)


def read_json(path):
    raw = Path(path).read_bytes()
    if str(path).endswith('.gz'):
        raw = gzip.decompress(raw)

    def unique(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ValueError('duplicate JSON key: ' + k)
            out[k] = v
        return out
    return json.loads(raw, object_pairs_hook=unique)


# ---------------------------------------------------------------- specification and identity

def identity():
    return {'files': {p: sha256_file(ROOT / p) for p in DEPENDENCIES},
            'python': sys.version.split()[0], 'numpy': np.__version__}


def write_spec():
    path = HERE / 'SPEC.json'
    if path.exists():
        raise SystemExit('SPEC.json already exists; the entropy is generated once')
    spec = {
        'note': 'Generated once by --write-spec before the specification commit. Pilot-only entropy.',
        'entropy': secrets.randbits(96), 'smoke_entropy': secrets.randbits(96),
        'C2': 3.4, 'C3': 16.4, 'gaps': [0.6, 1.2, 2.0, 2.8, 4.5], 'cases': list(CASES),
        'long_gaps': [0.6, 2.0, 2.8], 'T_short': 200.0, 'T_long': 1640.0,
        'full': {'n_prim1': 1600, 'n_l2': 200, 'n_prim2': 200, 'pairs': {'2': 16, '1': 24},
                  'workers': 8, 'soft_cap': 2700.0, 'hard_cap': 3000.0, 'batch': 100, 'long': True},
        'smoke': {'n_prim1': 120, 'n_l2': 15, 'n_prim2': 60, 'pairs': {'2': 2, '1': 3},
                   'workers': 4, 'soft_cap': 900.0, 'hard_cap': 1100.0, 'batch': 30, 'long': False,
                   'gaps': [0.6, 4.5], 'cases': ['natural', 'phase_pi'], 'T_short': {'2': 130.0, '1': 60.0}},
        'identity': identity()}
    write_json(path, spec)
    print('wrote', path)


def load_spec():
    return read_json(HERE / 'SPEC.json')


def verify_native(spec_identity):
    """Hash check of the loaded artifact and its sources; the loader in this import chain cannot build."""
    build = json.loads((ROOT / 'build/c6/BUILD.json').read_text())
    got = {'binary': sha256_file(ROOT / 'build/c6/element_law.dylib'),
           'source': sha256_file(ROOT / 'native/c6/element_law.cpp')}
    if got['binary'] != build['binary_sha256'] or got['source'] != build['source_sha256']:
        raise RuntimeError('native artifact differs from BUILD.json')
    files = spec_identity['files']
    if got['binary'] != files['build/c6/element_law.dylib'] or got['source'] != files['native/c6/element_law.cpp']:
        raise RuntimeError('native artifact differs from SPEC.json')
    return got


def preflight(spec, smoke):
    """Cheap deterministic refusals. They happen before the latch, so a refusal consumes no attempt."""
    now = identity()
    if now['files'] != spec['identity']['files']:
        diff = sorted(p for p in now['files'] if now['files'][p] != spec['identity']['files'].get(p))
        raise SystemExit('dependency identity differs from SPEC.json: ' + ', '.join(diff))
    verify_native(spec['identity'])
    if smoke:
        return {'git': 'not enforced for smoke'}
    rel = str(HERE.relative_to(ROOT))
    for name in ('SPEC.json', 'SPECIFICATION.md', 'pilot.py', 'test_harness.py'):
        tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', rel + '/' + name], cwd=ROOT,
                                 capture_output=True)
        if tracked.returncode:
            raise SystemExit(name + ' is not committed; commit the specification and harness first')
    status = subprocess.run(['git', 'status', '--porcelain', '--', rel, 'geomind', 'native', 'build', 'tools',
                             'experiments', 'pyproject.toml', 'uv.lock'],
                            cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    dirty = [line for line in status if not any(('/' + d + '/') in line or line.endswith('/' + d) for d in RUN_DIRS)]
    if dirty:
        raise SystemExit('uncommitted changes in the pilot or its dependencies: ' + '; '.join(dirty))
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {'git_head': head}


# ---------------------------------------------------------------- pair construction

def rotation(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s], [s, c]])


def contact_at_gap(points, cluster, target, direction, gap):
    """`c6_compose.contact_solve` with the gap as a parameter (same scan, bracket and bisection)."""
    direction = np.asarray(direction, float)
    direction = direction/np.linalg.norm(direction)
    points, cluster, target = (np.asarray(a, float) for a in (points, cluster, target))
    extent = np.max(np.linalg.norm(cluster-target, axis=1)) + np.max(np.linalg.norm(points, axis=1)) + gap + 0.02
    distance = lambda r: float(np.min(np.linalg.norm(points[:, None] + target + r*direction - cluster[None], axis=-1)))
    outer = extent
    while outer > 0:
        inner = max(0., outer-0.02)
        if distance(inner) <= gap:
            for _ in range(60):
                mid = (inner+outer)/2
                found = distance(mid)
                if gap <= found <= gap + 1e-6:
                    return target+mid*direction, found
                if found < gap:
                    inner = mid
                else:
                    outer = mid
            raise RuntimeError('contact bisection did not converge')
        outer = inner
    return None


def pair_randomness(entropy, level, pair, c_dest):
    rng = np.random.default_rng(np.random.SeedSequence([entropy, 77, level, pair]))
    half = 0.096/c_dest
    return {'angle_a': float(rng.uniform(0, 2*np.pi)), 'angle_b': float(rng.uniform(0, 2*np.pi)),
            'direction': float(rng.uniform(0, 2*np.pi)), 'phase': float(rng.uniform(-np.pi, np.pi)),
            'rate_a': float(rng.uniform(-half, half)), 'rate_b': float(rng.uniform(-half, half)), 'c_dest': c_dest}


def build_state(ta, tb, pr, gap, case):
    xa = ta['x'] @ rotation(pr['angle_a']).T
    xb = tb['x'] @ rotation(pr['angle_b']).T
    oa = compose.remap_owner(ta['owner'], 0)
    ob = compose.remap_owner(tb['owner'], len(xa))
    centre = levels.published_series(oa, xa[None], np.zeros((1, len(xa))))[0][0]
    direction = [np.cos(pr['direction']), np.sin(pr['direction'])]
    solution = contact_at_gap(xb, xa, centre, direction, gap)
    if solution is None:
        raise RuntimeError('no placement')
    xb = xb + solution[0]
    offset = pr['phase'] if case == 'natural' else FIXED_OFFSETS[case]
    th = np.concatenate([ta['th'], tb['th'] + offset])
    rate_a, rate_b = (pr['rate_a'], pr['rate_b']) if case == 'natural' else (0.0, 0.0)
    omega = np.concatenate([np.asarray(ta['omega']) + rate_a - ta['isolated_rate'],
                            np.asarray(tb['omega']) + rate_b - tb['isolated_rate']])
    return np.concatenate([xa, xb]), th, omega, oa, ob


# ---------------------------------------------------------------- integration and measurement

def frame_plan(T, W):
    return [(0.0, 20.0, 10), (20.0, T-W, 50), (T-W, T, 10)]


def integrate(x, th, omega, T, W):
    times, xs, ths = [], [], []
    cx, ct = x[None].copy(), th[None].copy()
    for k, (a, b, every) in enumerate(frame_plan(T, W)):
        steps = int(round((b-a)/DT))
        if abs(steps*DT-(b-a)) > 1e-9 or steps % every:
            raise ValueError('segment is not a whole number of steps and samples')
        cx, ct, samples = c6_native.simulate(cx, ct, omega[None], c4_model.INTACT, DT, steps, every)
        sx, st = samples
        start = 0 if k == 0 else 1
        times.extend(a + DT*every*np.arange(start, sx.shape[0]))
        xs.append(sx[start:, 0])
        ths.append(st[start:, 0])
    return np.array(times), np.concatenate(xs), np.concatenate(ths)


def minimum_distance(xs, na, chunk=100):
    out = []
    for i in range(0, len(xs), chunk):
        a, b = xs[i:i+chunk, :na], xs[i:i+chunk, na:]
        d = np.linalg.norm(a[:, :, None, :]-b[:, None, :, :], axis=-1)
        out.append(d.reshape(len(d), -1).min(axis=1))
    return np.concatenate(out)


def radius_of_gyration_series(xs, members):
    p = xs[:, list(members)]
    return np.sqrt(((p-p.mean(axis=1, keepdims=True))**2).sum(-1).mean(-1))


def own_validity(parts, xs, ths, times, c_part, base):
    window = round(30*c_part, 6)
    wanted = times[-1]-window + np.arange(31)*c_part
    idx = np.searchsorted(times, wanted-1e-8)
    if np.any(idx >= len(times)) or not np.allclose(times[idx], wanted, rtol=0, atol=1e-7):
        raise ValueError('own-level observation grid incomplete')
    geometry = levels.geometric_validity(parts, xs[idx])
    out = []
    for part, geo in zip(parts, geometry):
        dyn = levels.dynamic_validity(part, xs, ths, times, c_part, base, observation_W=window)
        out.append({'hull_overlap_max': float(geo['hull_overlap']), 'degenerate': bool(geo['degenerate']),
                    'dynamic_ok': bool(dyn['ok']), 'dynamic_reason': dyn['reason'], 'windows': dyn['windows']})
    return {'window': window, 'frames': len(idx), 'parts': out}


def snapshot_times(T, count):
    return np.linspace(0.0, T, count)


def run_one(job):
    """One two-body run. Returns a record; never raises (an error is a missing value, not a result)."""
    started, cpu = time.perf_counter(), time.process_time()
    try:
        ta, tb, pr = job['ta'], job['tb'], job['pr']
        level, T, long_run = job['level'], job['T'], job['long']
        c_part = job['c_part']
        x, th, omega, oa, ob = build_state(ta, tb, pr, job['gap'], job['case'])
        na = len(ta['x'])
        parent = levels.Owner((oa, ob), C=pr['c_dest'])
        base = ex.c4_manifest()['detector']
        window = levels.observation_window(parent) if long_run else round(30*c_part, 6)
        times, xs, ths = integrate(x, th, omega, T, window)
        if not (np.isfinite(xs).all() and np.isfinite(ths).all()):
            raise FloatingPointError('non-finite trajectory')
        Xa, Pa = levels.published_series(oa, xs, ths)
        Xb, Pb = levels.published_series(ob, xs, ths)
        dmin = minimum_distance(xs, na)
        keep = (times <= 20+1e-9) | (np.abs(times-np.round(times)) < 1e-6)
        series = {'t': times[keep], 'R': np.linalg.norm(Xb-Xa, axis=1)[keep],
                  'dtheta': c4_model.wrap(Pb-Pa)[keep], 'dmin': dmin[keep],
                  'rg_a': radius_of_gyration_series(xs, oa.members)[keep],
                  'rg_b': radius_of_gyration_series(xs, ob.members)[keep]}
        if abs(dmin[0]-job['gap']) > 1e-4:
            raise RuntimeError('placed gap %.8f differs from requested %.3f' % (dmin[0], job['gap']))
        if long_run:
            validity = {'parent': levels.recursive_validity(parent, xs, ths, times, base), 'window': window}
        else:
            validity = own_validity((oa, ob), xs, ths, times, c_part, base)
        snaps = np.searchsorted(times, snapshot_times(T, 21 if long_run else 13)-1e-8)
        record = {'status': 'OK', 'key': job['key'], 'level': level, 'pair': job['pair'], 'case': job['case'],
                  'gap': job['gap'], 'T': T, 'long': long_run, 'n_a': na, 'n_b': len(tb['x']),
                  'pair_randomness': pr, 'series': series, 'validity': validity,
                  'snapshots': {'t': times[snaps], 'x': xs[snaps], 'th': ths[snaps]},
                  'seconds': time.perf_counter()-started, 'cpu_seconds': time.process_time()-cpu}
        jsonable(record)
        return record
    except Exception as error:  # noqa: BLE001 - recorded, never silently dropped
        return {'status': 'ERROR', 'key': job.get('key'), 'error': repr(error),
                'seconds': time.perf_counter()-started}


# ---------------------------------------------------------------- workers

def _init(entropy, spec_identity):
    verify_native(spec_identity)
    ex.DEVELOPMENT_ENTROPY = entropy


def job_primitives(args):
    purpose, start, count = args
    templates, raw = ex.harvest_primitives(purpose, count, c6_native.simulate, start=start)
    return {'purpose': purpose, 'start': start, 'templates': templates,
            'worlds': count, 'seconds': sum(r['seconds'] for r in raw)}


def job_level2(args):
    index, templates, c2, factors, short = args
    row = ex.formation(templates, c2, 11, index, c6_native.simulate, factors, short)
    groups, records = ex.harvest_composites(row, c6_native.simulate, 21, index)
    return {'index': index, 'templates': groups, 'records': records, 'record': row['record']}


# ---------------------------------------------------------------- supervision

def terminate(pool):
    """Cancel queued work, then stop the workers (SIGTERM, SIGKILL after 5 s). Never waits on running work."""
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
    """Bounded submission. Returns ('done'|'deadline'|'broken', submitted, finished). Never blocks past a deadline."""
    pending, finished, submitted = {}, 0, 0
    iterator = iter(jobs)
    exhausted = False
    status = 'done'
    while True:
        while not exhausted and len(pending) < 2*workers and time.monotonic() < deadline:
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
                status = 'broken'
                result = {'status': 'ERROR', 'error': 'BrokenProcessPool'}
            except Exception as error:  # noqa: BLE001
                result = {'status': 'ERROR', 'error': repr(error)}
            on_result(job, result)
            finished += 1
        if status == 'broken':
            break
        if time.monotonic() >= deadline:
            status = 'deadline'
            break
    for future in pending:
        future.cancel()
    if status == 'done' and not exhausted:
        status = 'deadline'
    return status, submitted, finished


# ---------------------------------------------------------------- planning

def pick_one_per_source(templates):
    seen, out = set(), []
    for t in templates:
        if t['source_world'] not in seen:
            seen.add(t['source_world'])
            out.append(t)
    return out


def make_pairs(picks, count):
    return [(picks[2*k], picks[2*k+1]) for k in range(min(count, len(picks)//2))]


def conditions(cfg, spec):
    gaps = cfg.get('gaps', spec['gaps'])
    cases = cfg.get('cases', spec['cases'])
    return gaps, cases


def two_body_jobs(spec, cfg, entropy, pairs_by_level):
    gaps, cases = conditions(cfg, spec)
    t_short = cfg.get('T_short', {'2': spec['T_short'], '1': spec['T_short']})
    t_long = cfg.get('T_long', spec['T_long'])
    long_gaps = cfg.get('long_gaps', spec['long_gaps'])
    jobs = []
    for level in (2, 1):
        c_part = spec['C2'] if level == 2 else C1
        c_dest = spec['C3'] if level == 2 else spec['C2']
        for k, (ta, tb) in enumerate(pairs_by_level[level]):
            pr = pair_randomness(entropy, level, k, c_dest)
            T = t_short[str(level)] if isinstance(t_short, dict) else t_short
            for gap in gaps:
                for case in cases:
                    jobs.append({'key': 'L%d_p%02d_%s_g%.1f_T%d' % (level, k, case, gap, int(T)),
                                 'level': level, 'pair': k, 'case': case, 'gap': gap, 'T': float(T),
                                 'long': False, 'c_part': c_part, 'pr': pr, 'ta': ta, 'tb': tb})
            if level == 2 and cfg['long'] and 'natural' in cases:
                for gap in long_gaps:
                    jobs.append({'key': 'L2_p%02d_natural_g%.1f_T%d' % (k, gap, int(t_long)),
                                 'level': 2, 'pair': k, 'case': 'natural', 'gap': gap, 'T': float(t_long),
                                 'long': True, 'c_part': c_part, 'pr': pr, 'ta': ta, 'tb': tb})
    # The runs that decide the predictions (short, level 2) go first; long runs last.
    jobs.sort(key=lambda j: (j['long'], j['level'] != 2, j['pair'], j['gap'], j['case']))
    return jobs


# ---------------------------------------------------------------- interpretation

def circular_summary(angles):
    z = np.exp(1j*np.asarray(angles)).mean()
    rho = float(np.clip(abs(z), 1e-300, 1.0))
    return float(np.angle(z)), float(np.sqrt(max(-2*np.log(rho), 0.0)))


def category(coupled_end, overlap, distinct):
    """Mutually exclusive end state of a pair."""
    if not coupled_end:
        return 'SEPARATED'
    if overlap > 0.2:
        return 'FUSED'
    return 'DISTINCT_COUPLED' if distinct else 'PARTS_DAMAGED'


def derive(rec):
    s = rec['series']
    t, R, dth, dmin = (np.asarray(s[k]) for k in ('t', 'R', 'dtheta', 'dmin'))
    T = rec['T']
    early = t <= 3.0+1e-9
    slope = float(np.polyfit(t[early], R[early], 1)[0])
    window = (t >= 50-1e-9) & (t <= 100+1e-9)
    mean, std = circular_summary(dth[window])
    locked = bool(abs(mean) <= 0.5 and std <= 0.3)
    i50 = int(np.argmin(np.abs(t-50)))
    end = t >= T-50-1e-9
    coupled_end = bool(np.all(dmin[end] < RADIUS))
    bound = bool(coupled_end and abs(R[end][-1]-R[end][0])/float(np.mean(R[end])) <= 0.10)
    if rec['long']:
        rows = rec['validity']['parent']
        distinct = bool(all(r['ok'] for r in rows))
        overlap = float(max(float(r['hull_overlap']) for r in rows))
    else:
        parts = rec['validity']['parts']
        overlap = float(max(float(p['hull_overlap_max']) for p in parts))
        distinct = bool(all(p['dynamic_ok'] and not p['degenerate'] for p in parts) and overlap <= 0.2)
    return {'coupled': bool(rec['gap'] < RADIUS), 'early_slope': slope, 'locked': locked,
            'offset0': float(abs(dth[0])), 'dtheta_50': float(dth[i50]), 'coupled_50': bool(dmin[i50] < RADIUS),
            'lock_mean': mean, 'lock_std': std, 'coupled_end': coupled_end, 'bound': bound, 'distinct': distinct,
            'distinct_bound': bool(distinct and bound), 'overlap': overlap, 'final_R': float(R[-1]),
            'category': category(coupled_end, overlap, distinct),
            'dmin_ever_below_radius': bool(np.any(dmin < RADIUS))}


def fraction(values):
    return (float(np.mean(values)), len(values)) if len(values) else (None, 0)


def verdict(value, supported, refuted, direction, n=0, minimum=1):
    if value is None or n < minimum:
        return 'INDETERMINATE'
    if direction == 'high':
        return 'SUPPORTED' if value >= supported else 'REFUTED' if value < refuted else 'INDETERMINATE'
    return 'SUPPORTED' if value <= supported else 'REFUTED' if value >= refuted else 'INDETERMINATE'


def at_gap(d, gaps):
    return any(abs(d['gap']-g) < 1e-9 for g in gaps)


CATEGORIES = ('SEPARATED', 'FUSED', 'DISTINCT_COUPLED', 'PARTS_DAMAGED')


def decomposition(rows):
    cells = {}
    for d in rows:
        cells.setdefault((d['case'], d['gap']), []).append(d)
    out = {}
    for (case, gap), v in sorted(cells.items()):
        out['%s|%.1f' % (case, gap)] = {
            'n': len(v), 'locked': float(np.mean([x['locked'] for x in v])),
            'bound': float(np.mean([x['bound'] for x in v])),
            'distinct_bound': float(np.mean([x['distinct_bound'] for x in v])),
            'categories': {c: float(np.mean([x['category'] == c for x in v])) for c in CATEGORIES},
            'median_early_slope': float(np.median([x['early_slope'] for x in v])),
            'median_final_R': float(np.median([x['final_R'] for x in v])),
            'median_overlap': float(np.median([x['overlap'] for x in v]))}
    return out


def interpret(records, plan):
    """Predeclared rules from SPECIFICATION.md. INCOMPLETE takes precedence over every verdict; the short-run
    scope that decides P1-P3 is evaluated independently of the long runs, which are reported separately."""
    expected = set(plan['expected_keys'])
    long_keys = set(plan.get('long_keys', []))
    got, problems = {}, []
    for rec in records:
        key = rec.get('key')
        if key in got:
            problems.append('duplicate ' + str(key))
        got[key] = rec
    for level, rows in plan.get('pairs', {}).items():
        sources = [x for r in rows for x in (r['source_a'], r['source_b'])]
        if len(set(sources)) != len(sources):
            problems.append('level %s pairs share a source world' % level)
    missing = sorted(expected - set(got))
    extra = sorted(set(got) - expected)
    bad = sorted(k for k, r in got.items() if r.get('status') != 'OK')
    short_gap = [k for k in missing + bad if k not in long_keys]
    long_gap = [k for k in missing + bad if k in long_keys]
    out = {'expected': len(expected), 'found': len(got), 'missing': len(missing), 'errors': len(bad),
           'extra': extra, 'problems': problems, 'short_complete': not short_gap and not extra and not problems,
           'long_complete': not long_gap, 'missing_keys': missing[:50], 'error_keys': bad[:50]}
    out['status'] = 'COMPLETE' if out['short_complete'] and out['long_complete'] else 'INCOMPLETE'
    if not out['short_complete']:
        return out
    derived = {k: {**derive(r), 'level': r['level'], 'case': r['case'], 'gap': r['gap'], 'pair': r['pair'],
                   'long': r['long']} for k, r in got.items() if r.get('status') == 'OK'}
    shorts = [d for d in derived.values() if not d['long']]
    out['tables'] = {str(level): decomposition([d for d in shorts if d['level'] == level]) for level in (2, 1)}
    longs = [d for d in derived.values() if d['long']]
    out['long'] = {'%.1f' % g: {'n': len([d for d in longs if d['gap'] == g]),
                                 'criterion6_ok': float(np.mean([d['distinct'] for d in longs if d['gap'] == g])),
                                 'coupled_end': float(np.mean([d['coupled_end'] for d in longs if d['gap'] == g])),
                                 'bound': float(np.mean([d['bound'] for d in longs if d['gap'] == g])),
                                 'locked': float(np.mean([d['locked'] for d in longs if d['gap'] == g])),
                                 'categories': {c: float(np.mean([d['category'] == c for d in longs if d['gap'] == g]))
                                                for c in CATEGORIES}}
                   for g in sorted({d['gap'] for d in longs})}
    pairs2 = len(plan['pairs']['2'])
    out['level2_pairs'] = pairs2
    out['level1_pairs'] = len(plan['pairs']['1'])
    if pairs2 < 8:
        out['level2'] = 'INCOMPLETE: fewer than 8 level-2 pairs'
        out['status'] = 'INCOMPLETE'
        return out
    l2 = [d for d in shorts if d['level'] == 2]
    informative = lambda d: d['case'] in ('natural', 'phase_halfpi', 'phase_pi') and d['offset0'] >= OFFSET_MIN
    eff = [d for d in l2 if at_gap(d, EFFECTIVE_GAPS) and informative(d)]
    base = [d for d in l2 if abs(d['gap']-4.5) < 1e-9 and informative(d)]
    p1, n1 = fraction([d['locked'] for d in eff])
    b1, nb1 = fraction([d['locked'] for d in base])
    v1 = 'INDETERMINATE' if (b1 is None or b1 > 0.10) else verdict(p1, 0.80, 0.50, 'high', n1, 8)
    coupled_end = [d for d in l2 if d['coupled_end'] and d['gap'] < RADIUS]
    p2, n2 = fraction([d['distinct_bound'] for d in coupled_end])
    fused, _ = fraction([d['category'] == 'FUSED' for d in coupled_end])
    v2 = verdict(p2, 0.10, 0.25, 'low', n2, 10)
    if v2 == 'SUPPORTED' and v1 == 'SUPPORTED' and fused is not None and fused >= 0.5:
        reading = 'FUSION_REGIME'
    elif v2 == 'SUPPORTED':
        reading = 'NO_DISTINCT_BOUND_PAIR_NOT_DOMINATED_BY_FUSION_OR_PHASE_LOCK_UNCONFIRMED'
    elif v2 == 'REFUTED':
        reading = 'DISTINCT_BOUND_REGIME_EXISTS'
    else:
        reading = 'INDETERMINATE'
    key = lambda d: (d['pair'], round(d['gap'], 6))
    zero = {key(d): d['early_slope'] for d in l2 if d['case'] == 'phase0' and d['gap'] in (0.6, 1.2, 2.0, 4.5)}
    pi = {key(d): d['early_slope'] for d in l2 if d['case'] == 'phase_pi' and d['gap'] in (0.6, 1.2, 2.0, 4.5)}
    push = [k for k in sorted(set(zero) & set(pi)) if k[1] < RADIUS]
    control = [k for k in sorted(set(zero) & set(pi)) if k[1] > RADIUS]
    p3a, n3a = fraction([pi[k]-zero[k] > SLOPE_FLOOR for k in push])
    ctl, nctl = fraction([abs(pi[k]-zero[k]) < SLOPE_FLOOR for k in control])
    pi_eff = [d for d in l2 if d['case'] == 'phase_pi' and at_gap(d, EFFECTIVE_GAPS)]
    still = [d for d in pi_eff if d['coupled_50']]
    p3b, n3b = fraction([abs(d['dtheta_50']) <= 0.5 for d in still])
    sep, nsep = fraction([not d['coupled_50'] for d in pi_eff])
    if p3a is None or p3b is None or n3a < 8 or n3b < 8 or ctl is None or ctl < 0.90:
        v3 = 'INDETERMINATE'
    elif p3a >= 0.75 and p3b >= 0.75:
        v3 = 'SUPPORTED'
    elif p3a < 0.60 or p3b < 0.60:
        v3 = 'REFUTED'
    else:
        v3 = 'INDETERMINATE'
    out['predictions'] = {
        'P1_phase_locking': {'fraction': p1, 'n': n1, 'decoupled_baseline': b1, 'n_baseline': nb1, 'verdict': v1},
        'P2_no_distinct_bound_pair': {'fraction': p2, 'n': n2, 'fused_fraction': fused, 'verdict': v2,
                                      'reading': reading},
        'P3_phase_push_then_slip': {'push_fraction': p3a, 'n_push': n3a, 'push_control_quiet': ctl,
                                    'n_control': nctl, 'slip_fraction': p3b, 'n_slip': n3b,
                                    'separated_before_t50_fraction': sep, 'n_antiphase_effective': nsep, 'verdict': v3}}
    return out


# ---------------------------------------------------------------- the run

class Accounting:
    def __init__(self):
        self.stages = []
        self.t0 = time.monotonic()

    def stage(self, name, **info):
        self.stages.append({'stage': name, 'at': time.monotonic()-self.t0, **info})


def inventory(run_dir):
    out = {}
    for path in sorted(Path(run_dir).rglob('*')):
        if path.is_file() and not path.name.endswith('.tmp') and '.tmp' not in path.suffix:
            out[str(path.relative_to(run_dir))] = {'bytes': path.stat().st_size, 'sha256': sha256_file(path)}
    return out


def load_records(run_dir):
    return [read_json(p) for p in sorted((Path(run_dir)/'runs').glob('*.json.gz'))]


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
                        write_json(Path(run_dir)/'SUMMARY.json', {'status': 'INCOMPLETE',
                                                                  'reason': 'hard stop after %s s' % hard_cap})
                finally:
                    os._exit(3)
    timer = threading.Timer(hard_cap, stop)
    timer.daemon = True
    timer.start()
    return timer


def main_run(smoke):
    spec = load_spec()
    cfg = spec['smoke'] if smoke else spec['full']
    entropy = spec['smoke_entropy'] if smoke else spec['entropy']
    guard = preflight(spec, smoke)
    run_dir = HERE/('smoke_run' if smoke else 'run')
    try:
        os.mkdir(run_dir)
    except FileExistsError:
        raise SystemExit('%s exists: the one-shot latch is consumed; no resume, no retry' % run_dir.name)
    started = time.monotonic()
    deadline = started + cfg['soft_cap']
    account = Accounting()
    summary = {'status': 'INCOMPLETE', 'smoke': smoke, 'reason': 'not finished'}
    pool = None
    plan = None
    watchdog = None
    try:
        (run_dir/'runs').mkdir()
        for var in ('OMP_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
            os.environ[var] = '1'
        write_json(run_dir/'RUN_STARTED.json', {'smoke': smoke, 'guard': guard,
                                                'spec_sha256': sha256_file(HERE/'SPEC.json'),
                                                'pilot_sha256': sha256_file(HERE/'pilot.py'), 'workers': cfg['workers'],
                                                'wall_clock': time.strftime('%Y-%m-%dT%H:%M:%S%z')})
        watchdog = start_watchdog(run_dir, cfg['hard_cap'])
        pool = cf.ProcessPoolExecutor(max_workers=cfg['workers'], mp_context=mp.get_context('spawn'),
                                      initializer=_init, initargs=(entropy, spec['identity']))
        factors = {1: C1, 2: spec['C2'], 3: spec['C3']}
        batch = cfg['batch']

        # stage 1: level-1 units
        jobs = [(1, s, min(batch, cfg['n_prim1']-s)) for s in range(0, cfg['n_prim1'], batch)] + \
               [(2, s, min(batch, cfg['n_prim2']-s)) for s in range(0, cfg['n_prim2'], batch)]
        harvested = {}
        status, sub, fin = run_jobs(pool, job_primitives, jobs, lambda j, r: harvested.__setitem__(j, r), deadline,
                                    cfg['workers'])
        account.stage('primitive_harvest', status=status, submitted=sub, finished=fin)
        if status != 'done' or any('templates' not in r for r in harvested.values()):
            raise RuntimeError('primitive harvest incomplete: ' + status)
        pool1 = [t for j in sorted(j for j in harvested if j[0] == 1) for t in harvested[j]['templates']]
        pool2 = [t for j in sorted(j for j in harvested if j[0] == 2) for t in harvested[j]['templates']]
        account.stage('primitive_counts', level1_pool1=len(pool1), level1_pool2=len(pool2))
        # stage 2: level-2 worlds (full formation horizon, cheap) and groups
        assigned = assign_c5(pool1, 5, cfg['n_l2'])
        level2 = {}
        l2jobs = [(i, ts, spec['C2'], factors, False) for i, ts in enumerate(assigned)]
        status, sub, fin = run_jobs(pool, job_level2, l2jobs, lambda j, r: level2.__setitem__(j[0], r), deadline,
                                    cfg['workers'])
        account.stage('level2_formation', status=status, submitted=sub, finished=fin)
        if status != 'done' or any('templates' not in r for r in level2.values()):
            raise RuntimeError('level-2 harvest incomplete: ' + status)
        groups = [t for i in sorted(level2) for t in level2[i]['templates']]
        outcomes = {}
        for i in sorted(level2):
            outcomes[level2[i]['record']['outcome']] = outcomes.get(level2[i]['record']['outcome'], 0) + 1
        picks2, picks1 = pick_one_per_source(groups), pick_one_per_source(pool2)
        pairs_by_level = {2: make_pairs(picks2, cfg['pairs']['2']), 1: make_pairs(picks1, cfg['pairs']['1'])}
        account.stage('pairing', level2_groups=len(groups), level2_sources=len(picks2),
                      level2_pairs=len(pairs_by_level[2]), level1_sources=len(picks1),
                      level1_pairs=len(pairs_by_level[1]), level2_world_outcomes=outcomes)
        write_json(run_dir/'HARVEST.json', {'level2_world_records': [level2[i]['record'] for i in sorted(level2)],
                                            'level2_alone_records': [level2[i]['records'] for i in sorted(level2)]},
                   compress=True)
        with open(run_dir/'inputs.pkl.tmp', 'wb') as f:
            pickle.dump({2: pairs_by_level[2], 1: pairs_by_level[1]}, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(run_dir/'inputs.pkl.tmp', run_dir/'inputs.pkl')
        # stage 3: two-body runs (decisive short runs first)
        jobs = two_body_jobs(spec, cfg, entropy, pairs_by_level)
        plan = {'expected_keys': [j['key'] for j in jobs], 'long_keys': [j['key'] for j in jobs if j['long']],
                'pairs': {str(level): [{'pair': k, 'source_a': a['source_world'], 'source_b': b['source_world'],
                                        'n_a': len(a['x']), 'n_b': len(b['x'])}
                                       for k, (a, b) in enumerate(pairs_by_level[level])] for level in (2, 1)},
                'config': cfg}
        write_json(run_dir/'PLAN.json', plan)
        seen = set()

        def on_run(job, result):
            key = job['key']
            if key in seen:
                raise RuntimeError('duplicate run key ' + key)
            seen.add(key)
            if result.get('status') == 'OK':
                write_json(run_dir/'runs'/(key + '.json.gz'), result, compress=True)
            else:
                write_json(run_dir/('error_' + key + '.json'), result)

        status, sub, fin = run_jobs(pool, run_one, jobs, on_run, deadline, cfg['workers'])
        account.stage('two_body', status=status, submitted=sub, finished=fin, planned=len(jobs))
        summary['reason'] = 'complete' if status == 'done' else 'stopped: ' + status
        summary['two_body_status'] = status
    except BaseException as error:  # noqa: BLE001 - everything becomes a recorded INCOMPLETE
        summary['reason'] = 'exception: ' + repr(error)
    finally:
        try:
            if pool is not None:
                terminate(pool)
        except Exception as error:  # noqa: BLE001
            summary['cleanup_error'] = repr(error)
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        summary.update({'wall_seconds': time.monotonic()-started, 'children_cpu_seconds': usage.ru_utime+usage.ru_stime,
                        'max_child_rss_bytes': int(usage.ru_maxrss), 'stages': account.stages})
        try:
            if plan is not None:
                result = interpret(load_records(run_dir), plan)
                summary['interpretation'] = result
                if summary.get('reason') == 'complete':
                    summary['status'] = result['status']
        except Exception as error:  # noqa: BLE001
            summary['interpretation_error'] = repr(error)
            summary['status'] = 'INCOMPLETE'
        try:
            summary['inventory'] = inventory(run_dir)
        except Exception as error:  # noqa: BLE001
            summary['inventory_error'] = repr(error)
        try:
            write_json(run_dir/'SUMMARY.json', summary)
        except Exception as error:  # noqa: BLE001 - never leave a run without a summary
            try:
                write_json(run_dir/'SUMMARY.json', {'status': 'INCOMPLETE', 'reason': 'summary write failed: ' + repr(error),
                                                    'partial': {k: summary.get(k) for k in
                                                                ('reason', 'wall_seconds', 'two_body_status')}})
            except Exception:  # noqa: BLE001
                pass
        if watchdog is not None:
            watchdog.cancel()
    print(json.dumps({k: summary[k] for k in ('status', 'reason', 'wall_seconds')}, indent=1))
    return 0 if summary['status'] == 'COMPLETE' else 1


def main_interpret(directory):
    directory = Path(directory)
    plan = read_json(directory/'PLAN.json')
    result = interpret(load_records(directory), plan)
    write_json(directory/'INTERPRETATION.json', result)
    print(json.dumps(result.get('predictions', result), indent=1, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write-spec', action='store_true')
    group.add_argument('--run', action='store_true')
    group.add_argument('--smoke', action='store_true')
    group.add_argument('--interpret')
    args = parser.parse_args()
    if args.write_spec:
        write_spec()
    elif args.run:
        sys.exit(main_run(False))
    elif args.smoke:
        sys.exit(main_run(True))
    else:
        main_interpret(args.interpret)


if __name__ == '__main__':
    main()
