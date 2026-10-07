"""Stored-only night recovery; immutable v1 and combat's original cap remain intact."""
import argparse
import contextlib
import datetime as dt
import json
import os
from pathlib import Path
import re
import runpy
import signal
import sys
import threading
import time
import uuid
from zoneinfo import ZoneInfo
import analysis_recovery_v1 as v1

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
STORED_STAGES = v1.STORED_STAGES
MANIFEST = 'ANALYSIS_RECOVERY_V2_MANIFEST.json'
BOOT = 'HOST_BOOT_EVIDENCE_20261007.json'
INTERRUPTION = 'INTERRUPTION_95d7e6ccbe1043eda90e3b0ea8fe7055.json'
CLOSED_ATTEMPT = 'ATTEMPT_dc296a269683490a8bcf6899a51f335a.json'
HISTORICAL_ATTEMPT = 'ATTEMPT_eb681c6dfe8240248636f44adbcd5a4d.json'
BUDGET = 's4_v7c_stored_night_v2'
NIGHT_CAP = 7200
COMBAT_CAP = 3600
DECISION = 'docs/decisions/0031-owner-run-approval-policy.md'
AUTHORITY = {
    'decision': DECISION,
    'night_rule': 'Any run started 22:00 or later: Claude runs what the plan needs.',
    'owner_instruction': 'Owner instructed Claude to continue; recovery v2 explicitly authorizes a separate 7200 s allowance for stored-only analyze_validate and render_validate.',
    'timezone': 'Europe/Kiev',
    'authorized_not_before_local': '2026-10-07T22:00:00+03:00',
    'continuation': 'The explicit owner grant covers this two-stage stored-only batch across midnight; one shared allowance, no date-based renewal.',
}
REQUIRED_BINDINGS = frozenset({
    'analysis_recovery_v2.py', 'test_analysis_recovery_v2.py',
    'verify_analysis_recovery_v2.py', 'deliver_analysis_recovery_v2.py',
    'ANALYSIS_RECOVERY_V2.md', 'RECOVERY_V2_PRESERVATION.json',
    'RECOVERY_V2_OWNER_RECHECK.md', 'RECOVERY_V2_RECHECK_REQUEST.md',
    'RECOVERY_V2_CLAUDE_RECHECK.stdout.log', 'RECOVERY_V2_CLAUDE_RECHECK.stderr.log',
    'RECOVERY_V2_TESTS.json', 'RECOVERY_V2_TESTS.stdout.log', 'RECOVERY_V2_TESTS.stderr.log',
    v1.MANIFEST, BOOT, INTERRUPTION, HISTORICAL_ATTEMPT, CLOSED_ATTEMPT,
    'DECLARATION.json', 'SEAL.json', 'common.py', 'run.py', 'analyze.py', 'render.py',
})
read, sha, timestamp, seconds = v1.read, v1.sha, v1.timestamp, v1.seconds


def require_stored(stage):
    if stage not in STORED_STAGES:
        raise RuntimeError('combat/unknown stage refused; original cumulative cap remains 3600 s')


def boot_charge(root):
    """Validate the exact sysctl epoch against its raw output and preserved attempt."""
    boot = read(root / BOOT)
    attempt = read(root / HISTORICAL_ATTEMPT)
    if (boot.get('kind') != 'HOST_BOOT_EVIDENCE'
            or boot.get('command') != ['sysctl', '-n', 'kern.boottime']
            or type(boot.get('returncode')) is not int or boot['returncode'] != 0
            or boot.get('stderr') != '' or not isinstance(boot.get('captured_by'), str)
            or not boot['captured_by'].startswith('Claude')):
        raise RuntimeError('invalid host boot evidence')
    match = re.fullmatch(r'\{ sec = (\d+), usec = (\d+) \} .+', boot['stdout'])
    if not match or not 0 <= int(match[2]) < 1000000:
        raise RuntimeError('invalid sysctl boot output')
    epoch = seconds(boot['boot_epoch_seconds'])
    if epoch != int(match[1]) + int(match[2]) / 1000000:
        raise RuntimeError('boot epoch/output mismatch')
    bound = dt.datetime.fromtimestamp(epoch, dt.timezone.utc)
    displayed = timestamp(boot['boot_utc'])
    captured = timestamp(boot['captured_utc'])
    started = timestamp(attempt['utc_start'])
    if (displayed != bound.replace(microsecond=0) or not started <= bound <= captured
            or attempt['status'] != 'RUNNING' or attempt['stage'] != 'analyze_validate'):
        raise RuntimeError('boot chronology/attempt mismatch')
    return (bound - started).total_seconds()


def ledger(root=None, requested_stage='analyze_validate'):
    require_stored(requested_stage)
    root = HERE if root is None else root
    # v1 checks all receipt/interruption identities and refuses any new RUNNING
    # attempt (including an interrupted v2 attempt). Its conservative charge is
    # superseded for accounting here only; the record itself is never rewritten.
    original_total = v1.spent(root, requested_stage)
    exact = boot_charge(root)
    old = read(root / INTERRUPTION)['charged_seconds']
    night = 0.0
    allocations = []
    binary = read(root / HISTORICAL_ATTEMPT)['binary']
    for path in root.glob('ATTEMPT_*.json'):
        receipt = read(path)
        if path.name in (HISTORICAL_ATTEMPT, CLOSED_ATTEMPT):
            if 'recovery_budget' in receipt:
                raise RuntimeError('historical budget identity changed')
            continue
        if 'recovery_budget' not in receipt:
            raise RuntimeError('new attempt lacks night budget identity')
        require_stored(receipt['stage'])
        if (receipt['recovery_budget'] != BUDGET
                or receipt['recovery_manifest_sha256'] != sha(root / MANIFEST)
                or type(receipt['cap_seconds']) is not int or receipt['cap_seconds'] != NIGHT_CAP
                or receipt['binary'] != binary
                or receipt['gate']['status'] != 'not_run'
                or receipt['declaration_sha256'] != sha(root / 'DECLARATION.json')
                or receipt['status'] not in ('PASS', 'STOP')):
            raise RuntimeError('night attempt identity mismatch')
        local = timestamp(receipt['local_start'])
        utc_start = timestamp(receipt['utc_start'])
        utc_end = timestamp(receipt['utc_end'])
        regional = local.astimezone(ZoneInfo(AUTHORITY['timezone']))
        prior = seconds(receipt['prior_seconds'])
        allowance = seconds(receipt['allowance_seconds'])
        elapsed = seconds(receipt['seconds'])
        seconds(receipt['historical_seconds'])
        if (local.utcoffset() != regional.utcoffset() or local < timestamp(AUTHORITY['authorized_not_before_local'])
                or utc_start < local - dt.timedelta(seconds=1) or utc_end < utc_start
                or prior >= NIGHT_CAP or allowance != NIGHT_CAP - prior):
            raise RuntimeError('night attempt allocation/time mismatch')
        allocations.append((prior, elapsed))
        night += elapsed
    allocated = 0.0
    for prior, elapsed in sorted(allocations):
        if abs(prior - allocated) > 1e-8:
            raise RuntimeError('night attempt allocation chain mismatch')
        allocated += elapsed
    historical = original_total - old + exact - night
    return dict(interrupted_analysis_seconds=exact, historical_seconds=historical,
                combat_cap_seconds=COMBAT_CAP, combat_refused=True,
                night_seconds=night, night_cap_seconds=NIGHT_CAP,
                night_remaining_seconds=max(0, NIGHT_CAP - night), stored_only=True)


def verify_manifest():
    manifest = read(HERE / MANIFEST)
    if (manifest['schema'] != 2 or manifest['base_head'] != read(HERE / 'RECOVERY_V2_PRESERVATION.json')['base_head']
            or manifest['scope'] != 'stored-only analysis/render recovery; no combat authorization'
            or manifest['combat_cap_seconds'] != COMBAT_CAP or manifest['night_cap_seconds'] != NIGHT_CAP
            or manifest['night_stages'] != sorted(STORED_STAGES) or manifest['authority'] != AUTHORITY
            or manifest['budget_id'] != BUDGET or manifest['supersedes_accounting_only'] != INTERRUPTION
            or not REQUIRED_BINDINGS <= set(manifest['hashes'])
            or set(manifest['repo_hashes']) != {DECISION}):
        raise RuntimeError('v2 supplemental manifest scope/authority mismatch')
    for name, known in manifest['hashes'].items():
        if Path(name).name != name or sha(HERE / name) != known:
            raise RuntimeError('v2 supplemental manifest drift: ' + name)
    for name, known in manifest['repo_hashes'].items():
        if sha(REPO / name) != known:
            raise RuntimeError('decision authority drift')
    v1.verify_manifest()
    boot_charge(HERE)
    return manifest


def night_start(now=None):
    local = (now or dt.datetime.now(dt.timezone.utc)).astimezone(ZoneInfo(AUTHORITY['timezone']))
    if local < timestamp(AUTHORITY['authorized_not_before_local']):
        raise RuntimeError('night allowance requires the owner-authorized 2026-10-07 22:00 local start under decision 0031')
    return local.isoformat()


@contextlib.contextmanager
def night_attempt(stage, gate):
    require_stored(stage)
    if gate.get('status') != 'not_run':
        raise RuntimeError('stored-only gate required')
    import common
    # Exclusive lock precedes ledger read: concurrent analyze/render cannot each
    # allocate the same remaining allowance. A stale lock is never auto-cleared.
    lock = HERE / 'RECOVERY_V2_ACTIVE.lock'
    with lock.open('x') as f:
        f.write(str(os.getpid()))
    try:
        local_start = night_start()
        outputs = ('ANALYSIS.json',) if stage == 'analyze_validate' else ('REPORT.html', 'RENDER.json')
        if any((HERE / name).exists() for name in outputs):
            raise RuntimeError('existing analysis/render output must remain untouched')
        accounting = ledger(requested_stage=stage)
        remaining = accounting['night_remaining_seconds']
        if remaining <= 0:
            raise TimeoutError('shared cumulative 7200 s night allowance exhausted')
        start = time.monotonic()
        path = HERE / ('ATTEMPT_' + uuid.uuid4().hex + '.json')
        initial = dict(stage=stage, status='RUNNING', utc_start=common.utc(),
                       local_start=local_start, prior_seconds=accounting['night_seconds'],
                       historical_seconds=accounting['historical_seconds'],
                       allowance_seconds=remaining, cap_seconds=NIGHT_CAP, gate=gate,
                       recovery_budget=BUDGET, recovery_manifest_sha256=sha(HERE / MANIFEST),
                       declaration_sha256=sha(HERE / 'DECLARATION.json'), binary=common.admit(common.BINARY))
        common.exclusive(path, initial)
        deadline = common.Deadline(start + remaining)
        timer = None
        previous = None
        error = None
        def expired(*_):
            raise TimeoutError('shared cumulative 7200 s night allowance')
        try:
            previous = signal.signal(signal.SIGALRM, expired)
            signal.setitimer(signal.ITIMER_REAL, deadline.remaining())
            timer = threading.Timer(deadline.remaining(), deadline.stop)
            timer.daemon = True
            timer.start()
            yield deadline, accounting['night_seconds'], start
            deadline.remaining()
        except BaseException as exc:
            error = type(exc).__name__ + ': ' + str(exc)
            raise
        finally:
            if previous is not None:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
            if timer is not None:
                timer.cancel()
            deadline.stop()
            common.write(path, dict(initial, status='STOP' if error else 'PASS', error=error,
                                    seconds=time.monotonic() - start, utc_end=common.utc()))
    finally:
        lock.unlink()


@contextlib.contextmanager
def stored_runtime(stage):
    require_stored(stage)
    import common
    import run
    def no_combat(*args, **kwargs):
        raise RuntimeError('combat forbidden in analysis recovery v2')
    def scoped_attempt(requested, gate):
        if requested != stage:
            raise RuntimeError('stored-only stage mismatch')
        return night_attempt(requested, gate)
    replacements = [(common, 'attempt', scoped_attempt),
                    (common, 'spent', lambda: ledger(requested_stage=stage)['night_seconds']),
                    (run, 'execute', no_combat), (run, 'Executor', no_combat),
                    (run, 'validation', no_combat)]
    originals = [(module, name, getattr(module, name)) for module, name, _ in replacements]
    try:
        for module, name, value in replacements:
            setattr(module, name, value)
        yield
    finally:
        for module, name, value in originals:
            setattr(module, name, value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('analyze', 'render', 'ledger'))
    parser.add_argument('stage', choices=('validate',))
    args = parser.parse_args()
    verify_manifest()
    import common
    common.pins()
    accounting = ledger()
    print(json.dumps(accounting), flush=True)
    if args.command == 'ledger':
        return
    night_start()
    if accounting['night_remaining_seconds'] <= 0:
        raise TimeoutError('shared cumulative 7200 s night allowance exhausted')
    outputs = ('ANALYSIS.json',) if args.command == 'analyze' else ('REPORT.html', 'RENDER.json')
    if any((HERE / name).exists() for name in outputs):
        raise RuntimeError('existing analysis/render output must remain untouched')
    common.caffeinate()  # Re-exec this launcher before applying runtime patches.
    original_argv = sys.argv[:]
    try:
        with stored_runtime(args.command + '_validate'):
            sys.argv = [str(HERE / (args.command + '.py')), 'validate']
            runpy.run_path(sys.argv[0], run_name='__main__')
    finally:
        sys.argv = original_argv


if __name__ == '__main__':
    main()
