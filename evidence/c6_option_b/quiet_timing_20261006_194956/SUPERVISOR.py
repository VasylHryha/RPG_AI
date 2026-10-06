"""Evidence supervision only: four unchanged queued normal timing commands."""
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OLD = ROOT / 'evidence/c6_option_b/quiet_session_20261006_161801'
QUEUE = ROOT / 'evidence/c6_option_b/recheck/QUEUED_CHECKS.json'
ENV = dict(os.environ, PYTHONPYCACHEPREFIX=str(HERE / 'pycache'))
LOG = HERE / 'EVENTS.jsonl'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def event(kind, **fields):
    row = dict(kind=kind, utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
               monotonic=time.monotonic(), load_average=list(os.getloadavg()), **fields)
    with LOG.open('a') as stream:
        stream.write(json.dumps(row) + '\n')
    print(json.dumps(row), flush=True)
    return row


def identities():
    old = json.loads((OLD / 'PREFLIGHT.json').read_text())
    expected = {row['path']: row['sha256'] for row in old['delivery_inventory']}
    expected.update({row['live']: row['sha256'] for row in old['build_pairs']})
    start = json.loads((OLD / 'worlds/quiet_smoke_0/START.json').read_text())
    expected.update(start['helper_hashes'])
    expected['evidence/c6_option_b/recheck/QUEUED_CHECKS.json'] = old['queue_sha256']
    rows = {name: dict(expected_sha256=digest, sha256=sha(ROOT / name))
            for name, digest in expected.items()}
    return dict(files=rows, passed=all(row['sha256'] == row['expected_sha256'] for row in rows.values()))


def snapshot():
    # Pin relevant tracked science, inputs, tools and historical evidence without
    # modifying them. Also capture unrelated dirty/staged state for preservation.
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    selected = [name for name in paths if name and (
        name.startswith(('geomind/', 'native/', 'tests/', 'tools/', 'research/rrg/',
                         'experiments/', 'milestones/', 'evidence/c6_option_b/'))
        or name in ('STATUS.json', 'pyproject.toml', 'uv.lock'))]
    return dict(base_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
        git_status=subprocess.check_output(['git', 'status', '--short'], cwd=ROOT).decode(),
        staged_paths=subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT).decode().splitlines(),
        files={name: sha(ROOT / name) for name in selected})


def run_pair(rows):
    assert identities()['passed'], 'Pinned identity drift before pair'
    active = []
    for row in rows:
        argv = [value.replace('evidence/c6_option_b/recheck_later',
                str(HERE.relative_to(ROOT) / 'worlds')) for value in row['command']]
        assert '--audit' not in argv and '--fixture' not in argv
        assert argv[:5] == ['.venv/bin/python', 'tools/c6_option_b_check.py', '--backend', 'native', '--parallel']
        stream = (HERE / (row['id'] + '.log')).open('xb')
        started = time.monotonic()
        child = subprocess.Popen(argv, cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT)
        active.append((row, child, stream, started, argv))
        event('start', id=row['id'], argv=argv, pid=child.pid)
    results = []
    failed = False
    while active:
        remaining = []
        for row, child, stream, started, argv in active:
            code = child.poll()
            if code is None:
                remaining.append((row, child, stream, started, argv))
                continue
            stream.close()
            event('end', id=row['id'], pid=child.pid, returncode=code,
                  process_wall_seconds=time.monotonic() - started)
            failed |= code != 0
            if code == 0:
                folder = ROOT / argv[-1]
                costs = json.loads((folder / 'COSTS.json').read_text())
                assert costs['audit'] is None and costs['parallel'] and costs['backend'] == 'native'
                assert costs['source_pin']['status'] == 'PASS'
                assert costs['world'] == int(argv[argv.index('--world') + 1])
                assert costs['helper_hashes'] == json.loads((OLD / 'worlds/quiet_smoke_0/START.json').read_text())['helper_hashes']
                for key in ('option_b_build', 'reference_build', 'source_pin'):
                    assert costs[key] == json.loads((OLD / 'VALIDATED_IDENTITIES.json').read_text())[key], key
                assert isinstance(costs['world_seconds'], (int, float)) and math.isfinite(costs['world_seconds'])
                assert costs['invalid'] is None
                assert sha(folder / 'world.json.gz') == costs['world_sha256']
                results.append(dict(id=row['id'], argv=argv, costs=costs,
                    costs_sha256=sha(folder / 'COSTS.json'), start_sha256=sha(folder / 'START.json')))
        active = remaining
        if active:
            event('timing_sample', active=[dict(id=row['id'], pid=child.pid,
                observed_wall_seconds=time.monotonic()-started) for row,child,stream,started,argv in active])
            time.sleep(30)
    assert not failed, 'Timing helper failed; no further worlds launched'
    return results


def main():
    assert not LOG.exists(), 'Fresh session required'
    event('initial')
    baseline = snapshot()
    write('BASELINE.json', baseline)
    preflight = identities()
    write('PREFLIGHT.json', preflight)
    assert preflight['passed'], 'Pinned identity mismatch; do not rebuild'
    queue = json.loads(QUEUE.read_text())
    rows = [row for row in queue['queued_full_world_computations'] if row['kind'] == 'quiet_timing']
    assert [row['id'] for row in rows] == ['quiet_smoke_0', 'quiet_smoke_1', 'quiet_development_0', 'quiet_development_1']
    write('TIMING_COMMANDS.json', dict(queue_sha256=sha(QUEUE), commands=rows,
        executing_comparison_commands=False, maximum_simultaneous_worlds=2))
    wait_started = time.monotonic()
    low_started = None
    while True:
        now = time.monotonic()
        load = os.getloadavg()
        if load[0] < 3:
            if low_started is None:
                low_started = now
        else:
            low_started = None
        elapsed = now - wait_started
        low_seconds = 0 if low_started is None else now - low_started
        event('load_wait_sample', wait_elapsed_seconds=elapsed,
              consecutive_low_seconds=low_seconds, strict_threshold=3, sample_interval_seconds=30)
        if low_seconds >= 300:
            gate = event('load_gate_passed', wait_elapsed_seconds=elapsed,
                         consecutive_low_seconds=low_seconds, sampled_quiet_condition_met=True)
            break
        if elapsed >= 5400:
            gate = event('load_wait_expired', wait_elapsed_seconds=elapsed,
                         sampled_quiet_condition_met=False,
                         condition='90-minute cap reached; proceed once and disclose measured load')
            break
        time.sleep(min(30, 5400-elapsed))
    # Validate again after the possibly long wait. No scientific code imported
    # by supervisor and no build operation is ever invoked.
    before = identities()
    write('IDENTITIES_BEFORE_TIMING.json', before)
    assert before['passed']
    event('batch_start', sampled_quiet_condition_met=gate['sampled_quiet_condition_met'])
    runs = run_pair(rows[:2])
    runs.extend(run_pair(rows[2:]))
    event('batch_complete')
    final = identities()
    write('IDENTITIES_AFTER_TIMING.json', final)
    changes = {name: dict(before=digest, after=sha(ROOT/name))
        for name,digest in baseline['files'].items() if sha(ROOT/name) != digest}
    write('PRESERVATION_CHECKS.json', dict(protected_file_count=len(baseline['files']),
        protected_changed_files=changes, identities_passed=final['passed'],
        status_unchanged=sha(ROOT/'STATUS.json') == baseline['files']['STATUS.json'],
        current_git_status=subprocess.check_output(['git','status','--short'],cwd=ROOT).decode()))
    assert final['passed'] and not changes, 'Relevant source/evidence changed during measurement'
    worst = max(runs, key=lambda row: row['costs']['world_seconds'])
    maximum = worst['costs']['world_seconds']
    rule = dict(formula='max(world seconds) * 40 / 2 * 1.5 <= 10800',
        maximum_world_seconds=maximum, worst_world=worst['id'], projection_seconds=maximum*40/2*1.5,
        limit_seconds=10800, per_world_limit_seconds=360,
        passed=maximum*40/2*1.5 <= 10800, uses_unrounded_values=True)
    write('RUN_RECEIPT.json', dict(kind='TIMING_ONLY_NON_FINAL_ENTROPY',
        supervisor_sha256=sha(Path(__file__)), preflight_sha256=sha(HERE/'PREFLIGHT.json'),
        queue_sha256=sha(QUEUE), gate=gate, runs=runs, runtime_rule=rule,
        prior_equivalence_preserved_not_rerun=True))
    write('RAW_FILES_OUTSIDE_GIT.json', {str(path.relative_to(ROOT)):dict(sha256=sha(path),bytes=path.stat().st_size)
        for path in HERE.glob('worlds/*/world.json.gz')})
    event('receipt_complete', runtime_rule=rule)


if __name__ == '__main__':
    keep_awake = subprocess.Popen(['caffeinate', '-i', '-s'])
    try:
        main()
    except BaseException as error:
        event('supervisor_failure', exception_type=type(error).__name__, message=str(error))
        raise
    finally:
        keep_awake.terminate()
        keep_awake.wait()
