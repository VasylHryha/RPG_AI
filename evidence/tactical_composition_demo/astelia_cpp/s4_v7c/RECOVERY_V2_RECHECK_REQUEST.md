Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Final sources independently reviewed after midnight-continuation fix. No reviewer code/tests/fights. Findings and disposition: RECOVERY_V2_OWNER_RECHECK.md.

FILE ANALYSIS_RECOVERY_V2.md

# Stored-only night recovery v2

V2 supersedes v1's accounting only. All original validation, receipts, raw data, the RUNNING attempt, the v1 interruption record and launcher remain unchanged. The supplemental manifest binds `HOST_BOOT_EVIDENCE_20261007.json` from commit `4147896`, v1 from `c8241f2`, the original seal and both historical attempts. It binds decision 0031 and records the owner's instruction to Claude to continue, followed by this explicit recovery-v2 authorization. Validation is not resealed; no fights, entropy, scientific rules or acceptance are changed.

The sysctl output contains epoch **1791399114.777526** (boot **2026-10-07T18:51:54.777526Z**). The interrupted attempt started **18:06:31Z**. V2 charges exactly **2723.777526 s**, or **2723.8 s** rounded, instead of v1's **3377.771384 s** through recovery observation. The closed validation charge is **227.16235725 s**, making historical cumulative time **2950.93988325 s**. This still leaves only **649.06011675 s** of the original 3600 s cap, insufficient for analysis that already ran over 45 minutes before reboot.

The two stored stages `analyze_validate` and `render_validate` receive one **shared cumulative 7200 s night allowance**, starting with new v2 attempts. Historical time remains charged and visible separately; it is not deducted from this new allowance or erased. Each new attempt records its budget ID, supplemental manifest hash, declaration/binary identity, historical time, prior night time, remaining allowance and local start. PASS and STOP both consume measured wall time without clipping. No combat stage can use it: launcher choices, ledger calls, attempt calls and runtime combat entry points refuse combat/unknown stages. Direct original commands retain their original 3600 s fence and refuse the preserved RUNNING attempt.

Authority is **decision 0031's rule for launches at or after 22:00 local**, plus **the owner's instruction that Claude continue the work and this explicit 7200 s stored-only allowance**. The supplemental authority binds the batch's earliest start to **2026-10-07T22:00:00+03:00**. The explicit owner grant covers analysis and rendering as one batch, including continuation after midnight; it does not renew on another date. Each attempt records its actual local start and reuses the remaining shared allowance. Earlier starts refuse; changing dates never replenishes the budget. Decision 0031 supplies the initial night authority, while continuation belongs to the owner's explicit two-stage grant.

The launcher verifies the full original seal and unchanged v1 supplemental manifest, then patches only the stored runtime's attempt/deadline handling. It disables `run.execute`, `run.Executor` and `run.validation`. The unchanged analysis reads the 400 stored validation fights and full diagnostics; rendering reads stored analysis. Both use owned monotonic deadlines, a watchdog timer and SIGALRM; no negative-ledger trick or global original-cap edit is used. An exclusive lock covers ledger allocation and execution, preventing overlapping budgets. A new interrupted attempt or stale lock fails closed and needs a new recovery record; v2 does not automatically discount subsequent interruptions. Existing analysis/render outputs are refused rather than overwritten.

Codex does not launch analysis/render in this sandbox. Claude should run from repository root, outside the restricted sandbox. The launcher invokes `caffeinate` before entering the stored runtime. Allow roughly 45–120 minutes for analysis and rendering together; the exact remaining duration is unknown, and the shared 7200 s deadline is authoritative. Do not run the second command if the first fails.

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/analysis_recovery_v2.py analyze validate
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/analysis_recovery_v2.py render validate
```

Read-only audits (no trace parsing or fights):

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/analysis_recovery_v2.py ledger validate
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/verify_analysis_recovery_v2.py
```

| Stop condition (yes/no) | Action | Responsible role |
|---|---|---|
| Is boot evidence missing, invalid or changed? | Refuse recovery | implementer |
| Does an original or supplemental pin differ? | Stop and investigate without editing history | implementer |
| Is any new unclosed attempt or stale lock present? | Preserve it and require a new recovery decision | implementer |
| Is combat or an unknown stage requested? | Refuse execution under the unchanged 3600 s combat cap | implementer |
| Is the shared night allowance exhausted? | Stop before a new attempt | implementer |
| Is a new attempt starting before the authorized 2026-10-07 22:00 local instant? | Refuse this night allowance | implementer |
| Does a target analysis/render output already exist? | Preserve it and refuse overwrite | implementer |

The recheck and disposition are in `RECOVERY_V2_OWNER_RECHECK.md`. This task explicitly prohibits editing `docs/PLAN_CURRENT.md` and `DESIGN_0G.md`. Verification results are separate new v2 sidecars. No analysis result, S5 authorization or scientific acceptance is claimed by this implementation.

Delivery is based on current HEAD, after the unrelated economy commit `cbe2da2`; the snapshot retains the initial `4147896` observation and intervening paths. It preserves every original/protected hash and mtime. If the primary `.git` is read-only, the new delivery helper creates a commit through normal hooks in an isolated git directory, then verifies a current-HEAD incremental bundle and every committed blob after a fresh fetch. No protected document is staged.


FILE analysis_recovery_v2.py

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


FILE test_analysis_recovery_v2.py

"""Synthetic receipts and fake runtimes only: no fights, traces or analysis."""
import datetime as dt
import importlib.util
import json
from pathlib import Path
import sys
import types
import pytest

# pytest may load this directory without placing it on sys.path.
sys.path.insert(0, str(Path(__file__).parent))
import analysis_recovery_v2 as recovery
from test_analysis_recovery_v1 import receipts, put


def fixture(root):
    attempt, interruption, record = receipts(root)
    data = recovery.read(attempt)
    data['binary'] = {'fixture': True}
    put(attempt, data)
    record['attempt_sha256'] = recovery.sha(attempt)
    attempt.rename(root / recovery.HISTORICAL_ATTEMPT)
    (root / 'ATTEMPT_closed.json').rename(root / recovery.CLOSED_ATTEMPT)
    record.update(attempt_id=recovery.HISTORICAL_ATTEMPT[8:-5],
                  attempt_file=recovery.HISTORICAL_ATTEMPT,
                  charged_seconds=3377.771384,
                  recorded_utc='2026-10-07T19:02:48.771384Z',
                  wall_time_upper_bound_utc='2026-10-07T19:02:48.771384Z')
    interruption.unlink()
    put(root / recovery.INTERRUPTION, record)
    boot = json.loads(Path(__file__).with_name(recovery.BOOT).read_text())
    put(root / recovery.BOOT, boot)
    put(root / recovery.MANIFEST, {'fixture': True})
    return boot


def closed_night(root, stage='analyze_validate', elapsed=10, name='night', prior=0):
    put(root / ('ATTEMPT_' + name + '.json'), dict(
        stage=stage, status='PASS', seconds=elapsed, recovery_budget=recovery.BUDGET,
        recovery_manifest_sha256=recovery.sha(root / recovery.MANIFEST),
        cap_seconds=7200, gate={'status': 'not_run'}, binary={'fixture': True},
        prior_seconds=prior, allowance_seconds=7200-prior, historical_seconds=2950.777526,
        local_start='2026-10-07T22:30:00+03:00', utc_start='2026-10-07T19:30:00Z',
        utc_end='2026-10-07T23:00:00Z',
        declaration_sha256=recovery.sha(root / 'DECLARATION.json')))


def test_boot_exact_charge_and_historical_no_downtime(tmp_path):
    fixture(tmp_path)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    for _ in range(2):
        result = recovery.ledger(tmp_path)
        assert result['interrupted_analysis_seconds'] == 2723.777526
        assert result['historical_seconds'] == pytest.approx(2950.777526)
        assert result['night_remaining_seconds'] == 7200
        assert result['combat_cap_seconds'] == 3600 and result['combat_refused']
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir()}


def test_shared_night_budget_excludes_legacy_charges_and_never_clamps(tmp_path):
    fixture(tmp_path)
    closed_night(tmp_path, elapsed=7000)
    closed_night(tmp_path, stage='render_validate', elapsed=250, name='render', prior=7000)
    result = recovery.ledger(tmp_path)
    assert result['historical_seconds'] == pytest.approx(2950.777526)
    assert result['night_seconds'] == 7250
    assert result['night_remaining_seconds'] == 0


@pytest.mark.parametrize('stage', ['validate', 'tune', 'validation', 'fight', 'analyze_tune', 'unknown'])
def test_every_combat_or_unknown_stage_refused(tmp_path, stage):
    fixture(tmp_path)
    with pytest.raises(RuntimeError, match='refused'):
        recovery.ledger(tmp_path, stage)
    with pytest.raises(RuntimeError, match='refused'):
        with recovery.stored_runtime(stage):
            pytest.fail('combat entered')
    with pytest.raises(RuntimeError, match='refused'):
        with recovery.night_attempt(stage, {'status': 'not_run'}):
            pytest.fail('combat attempt created')


@pytest.mark.parametrize('field,value', [
    ('kind', 'OTHER'), ('command', ['sysctl']), ('returncode', 1), ('returncode', False),
    ('stderr', 'denied'), ('captured_by', 'unknown'), ('boot_epoch_seconds', float('nan')),
    ('boot_epoch_seconds', -1), ('boot_epoch_seconds', True), ('boot_epoch_seconds', 1791399115),
    ('stdout', '{ sec = 1791399114, usec = 1000000 } bad'),
    ('boot_utc', '2026-10-07T18:51:55Z'), ('boot_utc', '2026-10-07T18:51:54'),
    ('captured_utc', '2026-10-07T18:00:00Z'),
])
def test_invalid_boot_refused(tmp_path, field, value):
    boot = fixture(tmp_path)
    boot[field] = value
    put(tmp_path / recovery.BOOT, boot)
    with pytest.raises((RuntimeError, ValueError)):
        recovery.ledger(tmp_path)


def test_missing_boot_refused(tmp_path):
    fixture(tmp_path)
    (tmp_path / recovery.BOOT).unlink()
    with pytest.raises(FileNotFoundError):
        recovery.ledger(tmp_path)


def test_boot_before_attempt_refused(tmp_path):
    boot = fixture(tmp_path)
    boot.update(boot_epoch_seconds=1791396300, boot_utc='2026-10-07T18:05:00Z',
                stdout='{ sec = 1791396300, usec = 0 } Wed Oct 7 21:05:00 2026')
    put(tmp_path / recovery.BOOT, boot)
    with pytest.raises(RuntimeError):
        recovery.ledger(tmp_path)


@pytest.mark.parametrize('stage', ['validate', 'tune', 'analyze_validate', 'render_validate'])
def test_new_running_attempts_are_never_auto_recovered(tmp_path, stage):
    fixture(tmp_path)
    put(tmp_path / 'ATTEMPT_new.json', {'status': 'RUNNING', 'stage': stage})
    with pytest.raises(RuntimeError, match='unclosed'):
        recovery.ledger(tmp_path)


@pytest.mark.parametrize('field,value', [('cap_seconds', 7201), ('stage', 'validate'),
    ('recovery_budget', 'wrong'), ('recovery_manifest_sha256', 'wrong'),
    ('gate', {'status': 'CLEAR'}), ('binary', {'drift': True}),
    ('prior_seconds', 10), ('allowance_seconds', 7199),
    ('local_start', '2026-10-07T21:30:00+03:00'), ('utc_end', '2026-10-07T18:00:00Z'),
    ('seconds', -1), ('seconds', float('inf'))])
def test_invalid_night_receipt_refused(tmp_path, field, value):
    fixture(tmp_path)
    closed_night(tmp_path)
    path = tmp_path / 'ATTEMPT_night.json'
    record = recovery.read(path)
    record[field] = value
    put(path, record)
    with pytest.raises((RuntimeError, ValueError)):
        recovery.ledger(tmp_path)


@pytest.mark.parametrize('value,allowed', [
    ('2026-10-07T18:59:59Z', False), ('2026-10-07T19:00:00Z', True),
    ('2026-10-07T21:30:00Z', True), ('2026-10-08T10:00:00Z', True),
    ('2026-10-06T20:00:00Z', False),
])
def test_owner_authorized_batch_start_and_continuation(value, allowed):
    now = recovery.timestamp(value)
    if allowed:
        assert recovery.night_start(now)
    else:
        with pytest.raises(RuntimeError, match='22:00'):
            recovery.night_start(now)


def runtime_modules(monkeypatch):
    common = types.SimpleNamespace(attempt=lambda *a: None, spent=lambda: 99)
    run = types.SimpleNamespace(execute=lambda: 'combat', Executor=lambda: 'combat', validation=lambda: 'combat')
    monkeypatch.setitem(sys.modules, 'common', common)
    monkeypatch.setitem(sys.modules, 'run', run)
    return common, run


def test_runtime_blocks_all_combat_and_restores_on_error(monkeypatch):
    common, run = runtime_modules(monkeypatch)
    originals = (common.attempt, common.spent, run.execute, run.Executor, run.validation)
    monkeypatch.setattr(recovery, 'ledger', lambda **k: {'night_seconds': 10})
    with pytest.raises(ValueError):
        with recovery.stored_runtime('analyze_validate'):
            assert common.spent() == 10
            for f in (run.execute, run.Executor, run.validation):
                with pytest.raises(RuntimeError, match='combat forbidden'):
                    f()
            with pytest.raises(RuntimeError, match='mismatch'):
                common.attempt('validate', {'status': 'CLEAR'})
            raise ValueError('exit')
    assert originals == (common.attempt, common.spent, run.execute, run.Executor, run.validation)


def fake_common(monkeypatch):
    class Deadline:
        def __init__(self, absolute): self.absolute = absolute
        def remaining(self): return self.absolute - recovery.time.monotonic()
        def stop(self): pass
    common = types.SimpleNamespace(Deadline=Deadline, utc=lambda: '2026-10-07T19:30:00Z',
        admit=lambda binary: {'fixture': True}, BINARY='fake', exclusive=put, write=put)
    monkeypatch.setitem(sys.modules, 'common', common)
    monkeypatch.setattr(recovery, 'night_start', lambda: '2026-10-07T22:30:00+03:00')
    return common


@pytest.mark.parametrize('stage', sorted(recovery.STORED_STAGES))
def test_attempt_deadline_uses_remaining_night_budget_and_charges_stop(tmp_path, monkeypatch, stage):
    fixture(tmp_path)
    closed_night(tmp_path, elapsed=6000)
    monkeypatch.setattr(recovery, 'HERE', tmp_path)
    fake_common(monkeypatch)
    before = recovery.ledger(tmp_path)
    with pytest.raises(ValueError):
        with recovery.night_attempt(stage, {'status': 'not_run'}) as (deadline, prior, start):
            assert prior == 6000
            assert deadline.absolute == pytest.approx(start + 1200)
            with pytest.raises(FileExistsError):
                with recovery.night_attempt(stage, {'status': 'not_run'}):
                    pytest.fail('concurrent allocation')
            raise ValueError('synthetic stop')
    assert not (tmp_path / 'RECOVERY_V2_ACTIVE.lock').exists()
    new = [recovery.read(p) for p in tmp_path.glob('ATTEMPT_*.json') if p.name not in {recovery.HISTORICAL_ATTEMPT, recovery.CLOSED_ATTEMPT, 'ATTEMPT_night.json'}]
    assert len(new) == 1 and new[0]['status'] == 'STOP'
    assert new[0]['cap_seconds'] == 7200 and new[0]['allowance_seconds'] == 1200
    assert recovery.ledger(tmp_path)['night_seconds'] >= before['night_seconds']


def test_exhausted_night_budget_creates_no_attempt(tmp_path, monkeypatch):
    fixture(tmp_path)
    closed_night(tmp_path, elapsed=7200)
    monkeypatch.setattr(recovery, 'HERE', tmp_path)
    fake_common(monkeypatch)
    before = set(tmp_path.iterdir())
    with pytest.raises(TimeoutError, match='7200'):
        with recovery.night_attempt('analyze_validate', {'status': 'not_run'}):
            pytest.fail('entered')
    assert set(tmp_path.iterdir()) == before


def manifest_fixture(tmp_path, monkeypatch):
    fixture(tmp_path)
    for name in recovery.REQUIRED_BINDINGS:
        if not (tmp_path / name).exists():
            (tmp_path / name).write_text('fixture')
    put(tmp_path / 'RECOVERY_V2_PRESERVATION.json', {'base_head': 'a' * 40})
    manifest = dict(schema=2, base_head='a' * 40,
        scope='stored-only analysis/render recovery; no combat authorization',
        combat_cap_seconds=3600, night_cap_seconds=7200,
        night_stages=sorted(recovery.STORED_STAGES), authority=recovery.AUTHORITY,
        budget_id=recovery.BUDGET, supersedes_accounting_only=recovery.INTERRUPTION,
        hashes={n: recovery.sha(tmp_path / n) for n in recovery.REQUIRED_BINDINGS},
        repo_hashes={recovery.DECISION: recovery.sha(recovery.REPO / recovery.DECISION)})
    put(tmp_path / recovery.MANIFEST, manifest)
    monkeypatch.setattr(recovery, 'HERE', tmp_path)
    monkeypatch.setattr(recovery.v1, 'verify_manifest', lambda: {})
    return manifest


@pytest.mark.parametrize('missing', sorted(recovery.REQUIRED_BINDINGS))
def test_required_manifest_bindings_cannot_be_omitted(tmp_path, monkeypatch, missing):
    manifest = manifest_fixture(tmp_path, monkeypatch)
    del manifest['hashes'][missing]
    put(tmp_path / recovery.MANIFEST, manifest)
    with pytest.raises(RuntimeError, match='scope/authority'):
        recovery.verify_manifest()


@pytest.mark.parametrize('field,value', [('night_cap_seconds', 7201), ('combat_cap_seconds', 7200),
    ('night_stages', ['validate']), ('authority', {}), ('repo_hashes', {}), ('budget_id', 'wrong')])
def test_manifest_cap_and_authority_changes_refused(tmp_path, monkeypatch, field, value):
    manifest = manifest_fixture(tmp_path, monkeypatch)
    manifest[field] = value
    put(tmp_path / recovery.MANIFEST, manifest)
    with pytest.raises(RuntimeError, match='scope/authority'):
        recovery.verify_manifest()


def test_missing_night_budget_marker_never_resets_allowance(tmp_path):
    fixture(tmp_path)
    closed_night(tmp_path, elapsed=7000)
    path = tmp_path / 'ATTEMPT_night.json'
    receipt = recovery.read(path)
    del receipt['recovery_budget']
    del receipt['recovery_manifest_sha256']
    put(path, receipt)
    with pytest.raises(RuntimeError, match='lacks night budget'):
        recovery.ledger(tmp_path)


def test_existing_output_and_stale_lock_refuse_before_new_receipt(tmp_path, monkeypatch):
    fixture(tmp_path)
    monkeypatch.setattr(recovery, 'HERE', tmp_path)
    fake_common(monkeypatch)
    (tmp_path / 'ANALYSIS.json').write_text('existing')
    with pytest.raises(RuntimeError, match='untouched'):
        with recovery.night_attempt('analyze_validate', {'status': 'not_run'}):
            pytest.fail('overwrite')
    assert (tmp_path / 'ANALYSIS.json').read_text() == 'existing'
    (tmp_path / 'RECOVERY_V2_ACTIVE.lock').write_text('interrupted')
    with pytest.raises(FileExistsError):
        with recovery.night_attempt('render_validate', {'status': 'not_run'}):
            pytest.fail('stale lock ignored')


def test_cli_combat_refusal_precedes_any_import_or_entrypoint(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['analysis_recovery_v2.py', 'validate', 'validate'])
    monkeypatch.setattr(recovery, 'verify_manifest', lambda: pytest.fail('manifest entered'))
    with pytest.raises(SystemExit) as exc:
        recovery.main()
    assert exc.value.code == 2


def test_manifest_complete_and_boot_pin_drift(tmp_path, monkeypatch):
    manifest = manifest_fixture(tmp_path, monkeypatch)
    assert recovery.verify_manifest() == manifest
    (tmp_path / recovery.BOOT).write_text('{}')
    with pytest.raises(RuntimeError, match='manifest drift'):
        recovery.verify_manifest()


def test_main_exhaustion_before_entrypoint(monkeypatch):
    monkeypatch.setitem(sys.modules, 'common', types.SimpleNamespace(pins=lambda: None))
    monkeypatch.setattr(recovery, 'verify_manifest', lambda: {})
    monkeypatch.setattr(recovery, 'ledger', lambda: {'night_remaining_seconds': 0})
    monkeypatch.setattr(recovery, 'night_start', lambda: 'night')
    monkeypatch.setattr(recovery.runpy, 'run_path', lambda *a, **k: pytest.fail('entrypoint'))
    monkeypatch.setattr(sys, 'argv', ['analysis_recovery_v2.py', 'analyze', 'validate'])
    with pytest.raises(TimeoutError, match='7200'):
        recovery.main()


@pytest.mark.parametrize('missing', ['binary', 'local_start', 'utc_start', 'utc_end',
    'prior_seconds', 'allowance_seconds', 'historical_seconds', 'gate', 'cap_seconds'])
def test_truncated_completed_night_receipt_refused(tmp_path, missing):
    fixture(tmp_path)
    closed_night(tmp_path)
    path = tmp_path / 'ATTEMPT_night.json'
    receipt = recovery.read(path)
    del receipt[missing]
    put(path, receipt)
    with pytest.raises((RuntimeError, KeyError)):
        recovery.ledger(tmp_path)


def test_watchdogs_exclude_setup_time_and_pass_is_charged(tmp_path, monkeypatch):
    fixture(tmp_path)
    monkeypatch.setattr(recovery, 'HERE', tmp_path)
    common = fake_common(monkeypatch)
    clock = [100.0]
    monkeypatch.setattr(recovery.time, 'monotonic', lambda: clock[0])
    def slow_exclusive(path, value):
        put(path, value)
        clock[0] += 7
    common.exclusive = slow_exclusive
    alarms, timers = [], []
    monkeypatch.setattr(recovery.signal, 'signal', lambda *a: 'previous')
    monkeypatch.setattr(recovery.signal, 'setitimer', lambda mode, delay: alarms.append(delay))
    class Timer:
        def __init__(self, delay, callback): timers.append(delay)
        def start(self): pass
        def cancel(self): pass
    monkeypatch.setattr(recovery.threading, 'Timer', Timer)
    with recovery.night_attempt('analyze_validate', {'status': 'not_run'}) as (deadline, prior, start):
        assert deadline.absolute == start + 7200
        assert alarms == [7193] and timers == [7193]
        clock[0] += 5
    receipt = next(recovery.read(p) for p in tmp_path.glob('ATTEMPT_*.json')
        if p.name not in {recovery.HISTORICAL_ATTEMPT, recovery.CLOSED_ATTEMPT})
    assert receipt['status'] == 'PASS' and receipt['seconds'] == 12
    assert recovery.ledger(tmp_path)['night_seconds'] == 12
    assert alarms == [7193, 0]


@pytest.mark.parametrize('local_start,utc_start,utc_end', [
    ('2026-10-08T00:30:00+03:00', '2026-10-07T21:30:00Z', '2026-10-07T21:30:01Z'),
    ('2026-10-09T12:00:00+03:00', '2026-10-09T09:00:00Z', '2026-10-09T09:00:01Z'),
])
def test_midnight_or_later_date_never_resets_batch_budget(tmp_path, local_start, utc_start, utc_end):
    fixture(tmp_path)
    closed_night(tmp_path, elapsed=7000)
    closed_night(tmp_path, stage='render_validate', elapsed=1, name='render', prior=7000)
    path = tmp_path / 'ATTEMPT_render.json'
    receipt = recovery.read(path)
    receipt.update(local_start=local_start, utc_start=utc_start, utc_end=utc_end)
    put(path, receipt)
    result = recovery.ledger(tmp_path, 'render_validate')
    assert result['night_remaining_seconds'] == 199
    assert result['night_seconds'] == 7001


FILE verify_analysis_recovery_v2.py

"""Read-only preservation/seal audit; never parses traces or runs fights."""
import hashlib
import json
import subprocess
from analysis_recovery_v2 import HERE, ledger, read, sha, verify_manifest


def verify():
    verify_manifest()
    import common
    common.pins()
    baseline = read(HERE / 'RECOVERY_V2_PRESERVATION.json')
    for name, expected in baseline['original_files'].items():
        path = HERE / name
        stat = path.stat()
        if sha(path) != expected['sha256'] or stat.st_size != expected['bytes'] or stat.st_mtime_ns != expected['mtime_ns']:
            raise RuntimeError('original artifact changed: ' + name)
    for name, expected in baseline['protected'].items():
        path = common.REPO / name
        if sha(path) != expected['sha256'] or path.stat().st_mtime_ns != expected['mtime_ns']:
            raise RuntimeError('protected document changed: ' + name)
    staged = subprocess.check_output(['git', 'diff', '--cached', '--binary'], cwd=common.REPO)
    if hashlib.sha256(staged).hexdigest() != baseline['staged_diff_sha256']:
        raise RuntimeError('unrelated staging changed')
    result = dict(status='PASS', original_artifacts_verified=len(baseline['original_files']),
                  protected_documents_and_staging_unchanged=True, original_seal_verified=True,
                  executed_fights=0, analysis_started=False, render_started=False, **ledger())
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    verify()


FILE deliver_analysis_recovery_v2.py

"""Explicit new-file delivery with normal hooks, or verified current-HEAD bundle."""
from analysis_recovery_v2 import HERE, read, sha
from verify_analysis_recovery_v2 import verify
import json
import os
from pathlib import Path
import subprocess


def deliver():
    verify()
    if not (HERE/'RECOVERY_V2_OWNER_RECHECK.md').read_text().startswith('APPROVE'):
        raise RuntimeError('recheck not approved')
    repo = HERE.parents[3]
    baseline = read(HERE/'RECOVERY_V2_PRESERVATION.json')
    base = subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    if base != baseline['base_head']:
        raise RuntimeError('HEAD moved since recovery snapshot; inspect before delivery')
    names = [
        'analysis_recovery_v2.py', 'test_analysis_recovery_v2.py',
        'verify_analysis_recovery_v2.py', 'deliver_analysis_recovery_v2.py',
        'ANALYSIS_RECOVERY_V2.md', 'ANALYSIS_RECOVERY_V2_MANIFEST.json',
        'RECOVERY_V2_PRESERVATION.json',
        'RECOVERY_V2_RECHECK_REQUEST.md', 'RECOVERY_V2_OWNER_RECHECK.md',
        'RECOVERY_V2_CLAUDE_RECHECK.stdout.log', 'RECOVERY_V2_CLAUDE_RECHECK.stderr.log',
        'RECOVERY_V2_TESTS.json', 'RECOVERY_V2_TESTS.stdout.log', 'RECOVERY_V2_TESTS.stderr.log',
        'RECOVERY_V2_VERIFICATION.json',
        'RECOVERY_V2_TESTS_BEFORE_CONTINUATION_FIX.json',
        'RECOVERY_V2_TESTS_BEFORE_CONTINUATION_FIX.stdout.log',
        'RECOVERY_V2_TESTS_BEFORE_CONTINUATION_FIX.stderr.log',
        'RECOVERY_V2_TESTS_FAILED_SETUP.json',
        'RECOVERY_V2_TESTS_FAILED_SETUP.stdout.log', 'RECOVERY_V2_TESTS_FAILED_SETUP.stderr.log',
    ]
    if any(n in baseline['original_files'] for n in names):
        raise RuntimeError('delivery would stage an original artifact')
    paths = sorted(str((HERE/n).relative_to(repo)) for n in names)
    expected = {n:(repo/n).read_bytes() for n in paths}
    env = dict(os.environ)
    marker = repo/'.git/recovery_v2_write_probe'
    writable = False
    error = None
    try:
        with marker.open('x') as f:
            f.write('recovery writability probe')
        marker.unlink()
        writable = True
    except OSError as exc:
        error = str(exc)
    workspace = HERE/'delivery/recovery_v2'
    workspace.mkdir(parents=True,exist_ok=False)
    if not writable:
        gitdir = workspace/'delivery.git'
        subprocess.run(['git','clone','--bare','--shared',str(repo),str(gitdir)],check=True,capture_output=True)
        env.update(GIT_DIR=str(gitdir),GIT_WORK_TREE=str(repo),GIT_INDEX_FILE=str(gitdir/'task.index'))
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=repo,env=env,text=True).strip()
    branch = 'refs/heads/s4-v7c-analysis-recovery-v2'
    if not writable:
        git('symbolic-ref','HEAD',branch)
        git('update-ref',branch,base)
        git('read-tree',base)
        git('config','core.hooksPath',str(repo/'.githooks'))
    elif git('config','core.hooksPath') != '.githooks':
        raise RuntimeError('normal repository hooks not configured')
    before = subprocess.check_output(['git','diff','--cached','--binary'],cwd=repo)
    git('add','--',*paths)
    git('diff','--cached','--check','--',*paths)
    message = 'Add v7c boot-bound stored-only night recovery v2\n\nAssisted-by: Codex:GPT-6'
    committed = subprocess.run(['git','commit','--only','-m',message,'--',*paths],cwd=repo,env=env,text=True,capture_output=True)
    (workspace/'COMMIT.log').write_text(committed.stdout+committed.stderr)
    if committed.returncode:
        raise RuntimeError(committed.stdout+committed.stderr)
    head = git('rev-parse','HEAD')
    if set(git('diff-tree','--no-commit-id','--name-only','-r',head).splitlines()) != set(paths):
        raise RuntimeError('commit scope mismatch')
    for name, blob in expected.items():
        if subprocess.check_output(['git','show',head+':'+name],cwd=repo,env=env) != blob:
            raise RuntimeError('committed blob mismatch: '+name)
    # This task begins with no staged changes. Preserve any unrelated staging.
    if subprocess.check_output(['git','diff','--cached','--binary'],cwd=repo) != before:
        raise RuntimeError('main repository staging changed')
    transport = dict(base=base,commit=head,main_git_modified=writable,writability_error=error,
                     explicit_paths=paths,normal_hooks_returncode=0,committed_hashes={n:sha(repo/n) for n in paths})
    if not writable:
        bundle = workspace/'S4_V7C_ANALYSIS_RECOVERY_V2.bundle'
        git('bundle','create',str(bundle),base+'..'+branch)
        checked = subprocess.run(['git','bundle','verify',str(bundle)],cwd=repo,env=env,text=True,capture_output=True)
        (workspace/'BUNDLE_VERIFY.log').write_text(checked.stdout+checked.stderr)
        if checked.returncode:
            raise RuntimeError('bundle verification failed')
        fresh = workspace/'fresh_fetch'
        subprocess.run(['git','clone','--shared','--no-checkout',str(repo),str(fresh)],check=True,capture_output=True)
        subprocess.run(['git','fetch',str(bundle),branch],cwd=fresh,check=True,capture_output=True)
        if subprocess.check_output(['git','rev-parse','FETCH_HEAD'],cwd=fresh,text=True).strip() != head:
            raise RuntimeError('fetch commit mismatch')
        for name, blob in expected.items():
            if subprocess.check_output(['git','show',head+':'+name],cwd=fresh) != blob:
                raise RuntimeError('fetched blob mismatch: '+name)
        transport.update(bundle=str(bundle.relative_to(repo)),bundle_sha256=sha(bundle),
                         independent_fetch_and_all_blobs_verified=True)
    with (HERE/'RECOVERY_V2_DELIVERY_TRANSPORT.json').open('x') as f:
        json.dump(transport,f,indent=2);f.write('\n')
    print(json.dumps(transport,indent=2))


if __name__ == '__main__':
    deliver()
