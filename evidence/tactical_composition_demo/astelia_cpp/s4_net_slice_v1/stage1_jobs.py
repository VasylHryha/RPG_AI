"""New-job lock, repository ownership gate and immutable admitted child outputs.

Never writes to _local/collection. Failed launches are retained and charged;
physical hard limits include them. This module allocates nothing on import.
"""
from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import json
import os
from pathlib import Path
import time
import collection
import process_gate as gate
from collection import HERE, read, sha, atomic, cap

JOBS=HERE/'_local/stage1/jobs'


@dataclass(frozen=True)
class PhysicalBudget:
    started: float
    charged_before: float

    def deadline(self):
        # One origin across every child: waits and child wall consume elapsed
        # time, while old attempts are charged exactly once. Live reductions
        # shorten the deadline relative to that same origin.
        return self.started+cap()['cap_seconds']-self.charged_before


def physical_budget(directory):
    charged=sum(read(p).get('resources',{}).get('wall_seconds',0)
                for p in (Path(directory)/'attempts').glob('*.json'))
    return PhysicalBudget(time.monotonic(),charged)


def clear(deadline, path):
    original=gate.GATE_PATH; pattern=gate.HEAVY_PATTERN
    try:
        gate.GATE_PATH=Path(path)
        gate.HEAVY_PATTERN=pattern+r'|(^|/)(stage1_host)( |$)'
        return gate.process_gate(deadline=deadline)
    finally:
        gate.GATE_PATH=original
        gate.HEAVY_PATTERN=pattern


@contextmanager
def job_lock(name):
    JOBS.mkdir(parents=True,exist_ok=True)
    with (JOBS/'SLICE_JOB.lock').open('a') as f:
        try:
            fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('another stage-1 training/physical job is active')
        # Also refuse a live original collector; do not create/write its lock.
        lock=HERE/'_local/collection/RUN.lock'
        with lock.open('r') as cf:
            try:
                fcntl.flock(cf,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:
                raise RuntimeError('teacher collector owns the collection lock')
            clear(time.monotonic()+cap()['cap_seconds'],JOBS/(name+'_PROCESS_GATE.json'))
            yield


def pins(weights):
    from stage1_data import admit
    from stage1_native import admit_driver
    admit(); build=admit_driver()
    return dict(collection_seal_sha256=sha(HERE/'_local/collection/SEAL.json'),
                collection_receipt_sha256=sha(HERE/'COLLECTION_RECEIPT.json'),
                driver_binary_sha256=build['binary_sha256'],driver_build_sha256=sha(HERE/'STAGE1_NATIVE_BUILD.json'),
                weights={k:sha(v) for k,v in weights.items()},
                tooling_sources={p.name:sha(p) for p in HERE.glob('stage1_*.py')},
                driver_source_sha256=sha(HERE/'stage1_driver.cpp'))


def completed(directory, row, inventory_hash):
    path=directory/(row['fight']+'.receipt.json')
    if not path.exists():
        return None
    result=read(path); output=directory/(row['fight']+'.jsonl')
    if result['inventory_sha256']!=inventory_hash or result['request']!=row['request'] or sha(output)!=result['raw_sha256']:
        raise RuntimeError('completed physical result drift')
    return result


def execute(directory, row, inventory_hash, binary, attempt_cap, deadline):
    done=completed(directory,row,inventory_hash)
    if done:
        return done
    attempts=directory/'attempts'; attempts.mkdir(exist_ok=True)
    prior=[read(p) for p in attempts.glob('*.json')]
    if len(prior)>=attempt_cap:
        raise RuntimeError('physical hard cap including failures')
    for a in prior:
        if a['status'] in ('RUNNING','NATIVE_DONE'):
            rp=directory/(a['request']['fight']+'.receipt.json')
            target=directory/(a['request']['fight']+'.jsonl')
            if not rp.exists() or not target.exists():
                raise RuntimeError('unresolved native success/launch boundary; inspect, never silently repeat')
            sealed=read(rp)
            if sealed['request']!=a['request'] or sealed['inventory_sha256']!=inventory_hash or sealed['raw_sha256']!=sha(target):
                raise RuntimeError('unresolved native receipt drift')
    charged=sum(a['resources']['wall_seconds'] for a in prior if 'resources' in a)
    admission_start=time.monotonic()
    invocation_deadline=deadline.deadline() if isinstance(deadline,PhysicalBudget) else deadline
    remaining=min(invocation_deadline-admission_start,cap()['cap_seconds']-charged)
    if remaining<=0:
        raise TimeoutError('owner local LAB_CAP exhausted')
    effective_deadline=admission_start+remaining
    clear(effective_deadline,directory/'PROCESS_GATE.json')
    # Preserve the historical-charge bound while ownership waits consume it.
    # A reduced live owner cap can tighten, never extend, that fixed deadline.
    now=time.monotonic()
    invocation_deadline=deadline.deadline() if isinstance(deadline,PhysicalBudget) else deadline
    remaining=min(effective_deadline-now,invocation_deadline-now,
                  admission_start+cap()['cap_seconds']-charged-now)
    if remaining<=0:
        raise TimeoutError('owner local LAB_CAP exhausted after process wait')
    attempt=attempts/(f'{len(prior)+1:03}.json')
    partial=attempts/(f'{len(prior)+1:03}.partial.jsonl'); stderr=partial.with_suffix('.stderr')
    atomic(attempt,dict(status='RUNNING',request=row['request'],started_unix=time.time(),inventory_sha256=inventory_hash))
    # Use the proven wait4 resource collector, with its binary reference restored.
    original=collection.BINARY
    try:
        collection.BINARY=Path(binary)
        resources=collection.native(row['request'],partial,stderr,remaining)
    finally:
        collection.BINARY=original
    atomic(attempt,dict(status='FAILED' if resources['exit_code'] or resources['timed_out'] else 'NATIVE_DONE',
                        resources=resources,request=row['request'],inventory_sha256=inventory_hash))
    if resources['exit_code'] or resources['timed_out']:
        raise RuntimeError('native failed; preserve attempt; do not repeat automatically')
    # This validator is read-only, accepting group=fight for the existing wire.
    values=collection.measurements(partial,{**row,'group':row['fight']})
    target=directory/(row['fight']+'.jsonl')
    if target.exists():
        raise RuntimeError('orphan native output; inspect')
    os.replace(partial,target)
    result=dict(status='COMPLETE',request=row['request'],inventory_sha256=inventory_hash,
                raw_sha256=sha(target),resources=resources,**values)
    atomic(directory/(row['fight']+'.receipt.json'),result)
    atomic(attempt,dict(status='COMPLETE',resources=resources,request=row['request'],inventory_sha256=inventory_hash))
    return result
