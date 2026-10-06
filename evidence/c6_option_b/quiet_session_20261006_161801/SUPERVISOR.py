"""Evidence-only supervision of unchanged argv from QUEUED_CHECKS.json.

Does not import scientific code or rebuild artifacts. Global process telemetry
is unavailable under this sandbox; helper COSTS supplies final CPU/RSS/caches.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
QUEUE = ROOT / 'evidence/c6_option_b/recheck/QUEUED_CHECKS.json'
ENV = dict(os.environ, PYTHONPYCACHEPREFIX=str(HERE / 'pycache'))
OUTPUT_PREFIX = 'evidence/c6_option_b/recheck_later'
NEW_PREFIX = str(HERE.relative_to(ROOT) / 'worlds')
LOG = HERE / 'EVENTS.jsonl'


def event(kind, **fields):
    row = dict(kind=kind, utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
               load_average=list(os.getloadavg()), **fields)
    with LOG.open('a') as f:
        f.write(json.dumps(row) + '\n')
        f.flush()
    print(json.dumps(row), flush=True)


def run_group(rows, compare=False):
    active = []
    for row in rows:
        argv = [value.replace(OUTPUT_PREFIX, NEW_PREFIX) for value in row['comparison_command' if compare else 'command']]
        suffix = '_comparison' if compare else ''
        stream = (HERE / (row['id'] + suffix + '.log')).open('xb')
        started = time.monotonic()
        child = subprocess.Popen(argv, cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT)
        active.append((row, child, stream, started))
        event('start', id=row['id'] + suffix, argv=argv, pid=child.pid)
    failed = False
    while active:
        remaining = []
        for row, child, stream, started in active:
            code = child.poll()
            if code is None:
                remaining.append((row, child, stream, started))
            else:
                stream.close()
                failed |= code != 0
                event('end', id=row['id'] + ('_comparison' if compare else ''),
                      pid=child.pid, returncode=code, process_wall_seconds=time.monotonic()-started)
        active = remaining
        if active:
            event('sample', active=[dict(id=row['id'], pid=child.pid,
                  process_wall_seconds=time.monotonic()-started,
                  periodic_cpu_seconds=None, periodic_rss_bytes=None,
                  periodic_cache_counters=None) for row,child,stream,started in active],
                  telemetry_limit='Global process inspection is sandbox-refused; final helper COSTS records CPU/RSS/cache counters.')
            time.sleep(30)
    if failed:
        raise RuntimeError('Queued computation/comparison failed; no subsequent worlds launched.')


def main():
    assert not LOG.exists(), 'Fresh session required'
    queue = json.loads(QUEUE.read_text())
    preflight = json.loads((HERE / 'PREFLIGHT.json').read_text())
    assert hashlib.sha256(QUEUE.read_bytes()).hexdigest() == preflight['queue_sha256']
    assert preflight['all_identity_checks_passed']
    assert not (ROOT / NEW_PREFIX).exists(), 'Fresh output root required'
    for row in preflight['delivery_inventory']:
        assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    for row in preflight['build_pairs']:
        assert hashlib.sha256((ROOT/row['live']).read_bytes()).hexdigest() == row['sha256'], row['live']
    for name, record in preflight['references'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == record['sha256'], name
    event('pre_run')
    # A load above 3 must persist for ten minutes before the extended wait.
    # Stop waiting once it falls to <=3; never start two phases simultaneously.
    high_start = time.monotonic()
    while os.getloadavg()[0] > 3:
        elapsed = time.monotonic()-high_start
        event('waiting_for_load', elapsed_seconds=elapsed,
              ten_minutes_high=elapsed >= 600, wait_cap_seconds=4200)
        if elapsed >= 4200:
            event('load_wait_expired', conditions='Proceed under owner-authorized 10+60 minute cap; do not claim quietness.')
            break
        time.sleep(30)
    event('batch_start', process_inspection='unavailable; owner reports heavy jobs finished')
    rows = queue['queued_full_world_computations']
    run_group([rows[0]])
    for offset in range(1, 13, 3):
        group = rows[offset:offset+3]
        for row in group:
            run_group([row])
        for row in group:
            run_group([row], compare=True)
    event('equivalence_complete')
    run_group(rows[13:15])
    run_group(rows[15:17])
    for row in rows[13:17]:
        run_group([row], compare=True)
    event('batch_complete')


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        event('supervisor_failure', exception_type=type(error).__name__, message=str(error))
        raise
