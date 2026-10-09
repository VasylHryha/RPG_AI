"""Live operational authority for the recovery launcher, outside source identity.

Historical training/runtime files remain byte-identical. Their fixed ceilings
remain conservative compatibility guards; this adapter owns live admission,
deadlines, resource checks and evaluator decisions. No training math is replaced.
"""
import contextlib
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

import runtime as r


def _read():
    raw = (r.HERE / 'OWNER_APPROVALS.json').read_bytes()
    cfg = json.loads(raw)
    if cfg.get('schema') != 1 or cfg.get('approved_by') != 'owner' or not cfg.get('approval_reference') or not cfg.get('change_log'):
        raise ValueError('owner approvals identity/change log')
    def number(value, positive=True):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0 or (positive and value == 0):
            raise ValueError('owner approvals numeric bounds')
    for scope in ('training', 'dagger', 'lab'):
        number(cfg[scope]['cap_seconds'])
        if cfg[scope]['cap_seconds'] > cfg['training']['max_seconds']:
            raise ValueError('owner cap exceeds maximum')
    number(cfg['training']['max_seconds'])
    for value in cfg['resources'].values(): number(value)
    p = cfg['parity']
    for key in ('native_atol', 'float32_near_tie_ceiling', 'float32_recurrent_flip_rate_max', 'float32_recurrent_error_multiplier', 'calibrated_fire_error_multiplier', 'calibrated_fire_near_tie_ceiling'):
        number(p[key])
    if p['float32_recurrent_flip_rate_max'] > 1:
        raise ValueError('float32 flip rate must be <= 1')
    for key in ('native_categorical_mismatches', 'native_calibrated_fire_mismatches', 'uncertified_calibrated_fire_mismatches'):
        if type(p[key]) is not int or p[key] < 0: raise ValueError('parity mismatch count')
    for key in ('require_top2_gap', 'require_selected_class_deficit'):
        if type(p[key]) is not bool: raise ValueError('parity boolean')
    if p['float32_recurrent_head_error_ceiling'] is not None: number(p['float32_recurrent_head_error_ceiling'])
    number(cfg['smoke']['cap_seconds']); number(cfg['smoke']['fight_seconds'])
    if cfg['smoke']['cap_seconds'] > 300 or cfg['smoke']['fight_seconds'] > 3 or cfg['smoke']['threads'] != 2:
        raise ValueError('smoke fixture envelope')
    return cfg, raw


def load(): return _read()[0]


def snapshot(root=None):
    cfg, raw = _read(); digest = hashlib.sha256(raw).hexdigest()
    root = Path(root) if root is not None else r.LOCAL / 'owner_approvals'
    root.mkdir(parents=True, exist_ok=True)
    with (root / 'HISTORY.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        archive = root / (digest + '.json')
        if not archive.exists():
            with archive.open('xb') as file:
                file.write(raw); file.flush(); os.fsync(file.fileno())
        if archive.read_bytes() != raw: raise RuntimeError('owner approvals archive drift')
        history = root / 'CHANGES.jsonl'; previous = None
        if history.exists():
            lines = history.read_text().splitlines()
            if lines: previous = json.loads(lines[-1])['sha256']
        if previous != digest:
            with history.open('a') as file:
                file.write(json.dumps(dict(time_ns=time.time_ns(), previous_sha256=previous,
                    sha256=digest, approval_reference=cfg['approval_reference'])) + '\n')
                file.flush(); os.fsync(file.fileno())
    return dict(path=str(r.HERE / 'OWNER_APPROVALS.json'), sha256=digest,
                archive=str(archive), history=str(history), live_pin=False)


def verify_snapshot(note):
    if r.sha(note['archive']) != note['sha256'] or note.get('live_pin') is not False:
        raise RuntimeError('owner approvals snapshot drift')


def cap(scope='training'):
    cfg = load()
    return dict(cap_seconds=min(cfg['training']['max_seconds'], cfg[scope]['cap_seconds']),
                approved_by=cfg['approved_by'], approval_reference=cfg['approval_reference'],
                owner_approvals=snapshot())


def rss():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform == 'darwin' else value * 1024


def check_disk(path=None, required=0):
    free = shutil.disk_usage(path or r.LOCAL).free
    if free < required + load()['resources']['disk_reserve_bytes']:
        raise RuntimeError('owner disk reserve/projection refused')
    return free


class Deadline:
    """Config reductions apply live; a config increase never extends admission."""
    def __init__(self, seconds, scope='training'):
        self.started = time.monotonic(); self.limit = seconds; self.scope = scope
    def __sub__(self, other):
        self.limit = min(self.limit, cap(self.scope)['cap_seconds'])
        return self.started + self.limit - other
    def __rsub__(self, other): return -(self - other)
    def __le__(self, other): return self - other <= 0
    def __lt__(self, other): return self - other < 0
    def __ge__(self, other): return self - other >= 0
    def __gt__(self, other): return self - other > 0


class Monitor:
    fixture_only = False
    def __init__(self, test_mode=False):
        self.fixture_only = test_mode; self.peak = 0; self.python_peak = 0
    def live_memory(self, pid):
        cfg = load()['resources']; check_disk()
        value = rss() if pid == os.getpid() else 0
        if pid is not None and pid != os.getpid() and not self.fixture_only:
            query = subprocess.run(['ps', '-o', 'rss=', '-p', str(pid)], capture_output=True, text=True, timeout=5)
            if query.returncode or not query.stdout.strip(): raise RuntimeError('child RSS unavailable')
            value = int(query.stdout.strip()) * 1024
        limit = cfg['training_rss_cap_bytes'] if pid == os.getpid() else cfg['process_rss_cap_bytes']
        if value > limit: raise RuntimeError('owner RSS cap exceeded')
        if not self.fixture_only:
            query = subprocess.run(['vm_stat'], capture_output=True, text=True, timeout=5)
            if query.returncode or query.stderr.strip(): raise RuntimeError('live RAM unavailable')
            lines = query.stdout.splitlines(); page = int(lines[0].split('page size of ')[1].split()[0])
            values = {line.split(':')[0]: int(line.split(':')[1].strip().rstrip('.')) for line in lines[1:] if ':' in line and line.split(':')[1].strip().rstrip('.').isdigit()}
            if (values.get('Pages free', 0) + values.get('Pages inactive', 0)) * page < cfg['available_ram_reserve_bytes']:
                raise RuntimeError('owner available RAM reserve')
        if pid == os.getpid(): self.python_peak = max(self.python_peak, value)
        elif pid is not None: self.peak = max(self.peak, value)
        return value
    def memory_report(self, row):
        value = row['peak_rss_bytes']
        if not 0 < value <= load()['resources']['fixture_rss_cap_bytes']:
            raise RuntimeError('owner native fixture RSS cap')
        self.peak = max(self.peak, value)


def float32_passes(export):
    p = load()['parity']; errors = export.get('head_max_abs_error', {})
    if len(export['mismatches']) != export['categorical_mismatches']: return False
    if any(not math.isfinite(v) or v < 0 for v in errors.values()): return False
    ceiling = p['float32_recurrent_head_error_ceiling']
    if ceiling is not None and any(v > ceiling for v in errors.values()): return False
    for detail in export['mismatches']:
        bound = p['float32_recurrent_error_multiplier'] * errors.get(detail['head'], 0.)
        if p['require_top2_gap'] and not 0 <= detail['float64_top2_gap'] <= bound: return False
        if p['require_selected_class_deficit'] and not 0 <= detail['float64_selected_class_deficit'] <= bound: return False
    return 0 <= export['categorical_mismatches'] <= p['float32_recurrent_flip_rate_max'] * max(1, export['rows'])


def passes(proof):
    p = load()['parity']; native = proof['native_float64']; fire = proof['calibrated_fire']
    # Reuse measured values, never stale certification booleans after a live
    # config reduction. Receipts themselves remain untouched.
    details = fire.get('float32_mismatches', [])
    fire_ok = fire['uncertified_mismatches'] <= p['uncertified_calibrated_fire_mismatches']
    if details:
        error = fire.get('measured_logit_max_abs_error', float('nan'))
        if not math.isfinite(error) or error < 0: return False
        bound = min(p['calibrated_fire_error_multiplier'] * error, p['calibrated_fire_near_tie_ceiling'])
        invalid = sum(not math.isfinite(d['relevant_gap']) or not 0 <= d['relevant_gap'] <= bound for d in details)
        fire_ok = invalid <= p['uncertified_calibrated_fire_mismatches']
    return (0 <= native['categorical_mismatches'] <= p['native_categorical_mismatches']
            and 0 <= native['max_abs_error'] <= p['native_atol']
            and float32_passes(proof['float32_export'])
            and 0 <= fire['native_mismatches'] <= p['native_calibrated_fire_mismatches']
            and fire_ok)


def compare_calibrated(a, b, native, rows, thresholds):
    import numpy as np
    from calibration import fire_classes
    p = load()['parity']
    error = max((float(np.max(np.abs(x[:,3:6] - y[:,3:6]))) for x, y in zip(a,b)), default=0.)
    bound = min(p['calibrated_fire_error_multiplier'] * error, p['calibrated_fire_near_tie_ceiling'])
    details = []; native_errors = 0
    for at, (x, y, z, row) in enumerate(zip(a,b,native,rows)):
        own = sorted((u for u in row['units'] if u[1] == 0), key=lambda u:u[0]); roles = [u[2] for u in own]
        c32 = fire_classes(x[:,3:6], roles, thresholds); c64 = fire_classes(y[:,3:6], roles, thresholds)
        native_errors += int(np.sum(c64 != z))
        for i in np.flatnonzero(c32 != c64):
            gap = abs(float(max(y[i,3], y[i,5]) - y[i,4]) - thresholds[roles[i]])
            relevant = abs(float(y[i,3] - y[i,5])) if c32[i] != 1 and c64[i] != 1 else gap
            details.append(dict(frame_index=at, time=row['t'], unit_id=own[i][0], role=roles[i],
                float32_class=int(c32[i]), float64_class=int(c64[i]), threshold_gap=gap,
                relevant_gap=relevant, bound=bound, certified=relevant <= bound))
    return dict(native_mismatches=native_errors, float32_mismatches=details,
                uncertified_mismatches=sum(not d['certified'] for d in details), measured_logit_max_abs_error=error, bound=bound)


_installed = False
_scope = 'training'
def install(scope='training'):
    """Called only after provenance verification by launcher and its workers."""
    global _installed, _scope
    _scope = scope
    load()
    if _installed: return
    import train, training, training_control, parity_run, parity, calibrated_parity, jobs, execution, common
    def live_cap(here): return cap('training')
    for module in (train, training, training_control, parity_run): module.training_cap = live_cap
    calibrated_parity.stageb_float32_passes = float32_passes
    calibrated_parity.passes = passes
    calibrated_parity.compare_calibrated = compare_calibrated
    # Keep the historical manifest shape for archived parity cache validation.
    parity.PARITY_RULE.update(native_atol=load()['parity']['native_atol'],
        native_categorical_mismatches=load()['parity']['native_categorical_mismatches'],
        float32_near_tie_ceiling=load()['parity']['float32_near_tie_ceiling'])
    original_a0 = r.collect.a0
    def a0():
        base = original_a0(); base.owner_cap = lambda:cap(_scope)
        base.live_memory = Monitor().live_memory
        return base
    r.collect.a0 = a0
    # Training workers require a numeric absolute time; TrainingDeadline itself
    # polls config. Other invocations use the live scope-specific deadline.
    @contextlib.contextmanager
    def training_admitted(seconds):
        with jobs.locked():
            gate = common.load('stageb_config_process_gate', r.CPP/'s4_net_slice_v1/process_gate.py')
            gate.GATE_PATH = r.LOCAL/'PROCESS_GATE.json'
            absolute = time.monotonic()+seconds
            gate.process_gate(wait=False, deadline=absolute)
            monitor = Monitor(); monitor.live_memory(None)
            if _scope == 'training': yield absolute, monitor
            else: yield Deadline(min(seconds, cap(_scope)['cap_seconds']), _scope), monitor
    jobs.admitted = training_admitted
    r.collect.admitted = training_admitted
    original_step = training.step
    def step(*args, **kwargs):
        Monitor().live_memory(os.getpid()); result = original_step(*args, **kwargs)
        if result['rss_bytes'] > load()['resources']['training_rss_cap_bytes']: raise RuntimeError('owner training RSS cap')
        return result
    training.step = step
    def disk_projection(sample, todo):
        if not sample: raise RuntimeError('full-fight sample needed')
        per = max(c['compressed_bytes'] * 150.04 / max(c['stats']['t_end'], 1e-9) for c in sample)
        cfg = load()['resources']; required = cfg['disk_projection_multiplier'] * per * len(todo)
        check_disk(required=required)
        return dict(max_full150_bytes=per, remaining_fights=len(todo), required_free_bytes=required+cfg['disk_reserve_bytes'])
    import dagger, readout_run
    for module in (execution, dagger, readout_run): module.disk_projection = disk_projection
    # All subsequently written receipts/budgets/ledgers bind the config in use.
    # Export parameter dictionaries retain their established native schema.
    original_write = common.write
    def write(path, value, exclusive=False):
        if isinstance(value, dict) and 'parameters' not in value:
            value = dict(value, owner_approvals=snapshot())
        return original_write(path, value, exclusive)
    for module in list(sys.modules.values()):
        if getattr(module, 'write', None) is original_write: module.write = write
    _installed = True
