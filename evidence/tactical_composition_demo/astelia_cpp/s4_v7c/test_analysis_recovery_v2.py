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
