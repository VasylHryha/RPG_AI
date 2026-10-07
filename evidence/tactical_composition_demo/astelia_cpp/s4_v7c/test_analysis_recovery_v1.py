"""Fake receipts only; no native fixture, fight, panel, or raw-data execution."""
import importlib.util
import json
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('analysis_recovery_v1', Path(__file__).with_name('analysis_recovery_v1.py'))
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)


def put(path, value):
    path.write_text(json.dumps(value))


def receipts(root, stage='analyze_validate', charged=120):
    put(root / 'DECLARATION.json', {'sealed': True})
    put(root / 'ATTEMPT_closed.json', {'stage': 'validate', 'status': 'PASS', 'seconds': 227})
    attempt = dict(stage=stage, status='RUNNING', utc_start='2026-10-07T18:06:31Z',
                   declaration_sha256=recovery.sha(root / 'DECLARATION.json'),
                   gate={'status': 'not_run' if stage in recovery.STORED_STAGES else 'CLEAR'})
    path = root / 'ATTEMPT_open.json'
    put(path, attempt)
    record = dict(schema=1, status='INTERRUPTED_STORED_ONLY', attempt_id='open',
                  attempt_file=path.name, attempt_sha256=recovery.sha(path), stage=stage,
                  utc_start=attempt['utc_start'], declaration_sha256=attempt['declaration_sha256'],
                  cause={'kind': 'host_reboot'}, stored_only=True, executed_fights=0,
                  wall_time_upper_bound_utc='2026-10-07T18:08:31Z', charged_seconds=charged,
                  recorded_utc='2026-10-07T18:08:31Z',
                  boot_time_evidence=dict(argv=['/usr/sbin/sysctl', 'kern.boottime'], returncode=1,
                                          available=False, stdout='', stderr='denied'))
    interruption = root / 'INTERRUPTION_test.json'
    put(interruption, record)
    return path, interruption, record


@pytest.mark.parametrize('stage', sorted(recovery.STORED_STAGES))
@pytest.mark.parametrize('requested', sorted(recovery.STORED_STAGES))
def test_stored_interruption_charged_once_receipts_unchanged(tmp_path, stage, requested):
    receipts(tmp_path, stage)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert recovery.spent(tmp_path, requested) == 347
    assert recovery.spent(tmp_path, requested) == 347
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir()}


@pytest.mark.parametrize('stage', ['validate', 'tune', 'unknown', 'analyze_tune'])
def test_unclosed_combat_or_unknown_never_recovered(tmp_path, stage):
    receipts(tmp_path, stage)
    with pytest.raises(RuntimeError, match='unclosed attempt'):
        recovery.spent(tmp_path)


def test_recovery_cannot_enable_combat_caller(tmp_path):
    receipts(tmp_path)
    with pytest.raises(RuntimeError, match='unclosed attempt'):
        recovery.spent(tmp_path, 'validate')


def test_every_unclosed_attempt_requires_record(tmp_path):
    receipts(tmp_path)
    put(tmp_path / 'ATTEMPT_other.json', {'status': 'RUNNING', 'stage': 'render_validate'})
    with pytest.raises(RuntimeError, match='unclosed attempt'):
        recovery.spent(tmp_path)


@pytest.mark.parametrize('field,value', [
    ('attempt_id', 'wrong'), ('stage', 'render_validate'), ('utc_start', '2026-10-07T18:06:32Z'),
    ('declaration_sha256', 'wrong'), ('attempt_sha256', 'wrong'), ('stored_only', False),
    ('executed_fights', 1), ('status', 'PASS'), ('charged_seconds', 119),
    ('charged_seconds', -1), ('charged_seconds', float('nan')), ('charged_seconds', True),
    ('wall_time_upper_bound_utc', '2026-10-07T18:08:31'),
])
def test_invalid_or_undercharged_record_refused(tmp_path, field, value):
    _, path, record = receipts(tmp_path)
    record[field] = value
    put(path, record)
    with pytest.raises((RuntimeError, ValueError)):
        recovery.spent(tmp_path)


def test_changed_attempt_bytes_refused(tmp_path):
    path, _, _ = receipts(tmp_path)
    path.write_text(path.read_text() + '\n')
    with pytest.raises(RuntimeError, match='mismatch'):
        recovery.spent(tmp_path)


def test_duplicate_or_orphan_refused(tmp_path):
    _, path, record = receipts(tmp_path)
    put(tmp_path / 'INTERRUPTION_duplicate.json', record)
    with pytest.raises(RuntimeError, match='duplicate or orphan'):
        recovery.spent(tmp_path)
    path.unlink()
    record['attempt_file'] = 'ATTEMPT_missing.json'
    put(tmp_path / 'INTERRUPTION_duplicate.json', record)
    with pytest.raises(RuntimeError, match='duplicate or orphan'):
        recovery.spent(tmp_path)


def test_no_budget_reset_or_clamp(tmp_path):
    receipts(tmp_path, charged=4000)
    assert recovery.spent(tmp_path) == 4227


def test_normal_closed_attempt_accounting(tmp_path):
    put(tmp_path / 'ATTEMPT_a.json', {'status': 'STOP', 'seconds': 3})
    put(tmp_path / 'ATTEMPT_b.json', {'status': 'PASS', 'seconds': 4})
    assert recovery.spent(tmp_path) == 7


def test_runtime_only_patches_stored_ledger_and_restores(monkeypatch):
    import types, sys
    original_spent = lambda: 99
    original_execute = lambda: 'combat'
    common = types.SimpleNamespace(spent=original_spent)
    run = types.SimpleNamespace(execute=original_execute)
    monkeypatch.setitem(sys.modules, 'common', common)
    monkeypatch.setitem(sys.modules, 'run', run)
    monkeypatch.setattr(recovery, 'spent', lambda root, stage: 347)
    with recovery.stored_runtime('analyze_validate'):
        assert common.spent() == 347
        with pytest.raises(RuntimeError, match='combat forbidden'):
            run.execute()
    assert common.spent is original_spent
    assert run.execute is original_execute
    with pytest.raises(RuntimeError, match='stored-only stage'):
        with recovery.stored_runtime('validate'):
            pytest.fail('combat stage entered')


def test_cap_exhaustion_stops_before_entrypoint_and_receipt(monkeypatch):
    import sys, types
    monkeypatch.setitem(sys.modules, 'common', types.SimpleNamespace(pins=lambda: None))
    monkeypatch.setattr(recovery, 'verify_manifest', lambda: {})
    monkeypatch.setattr(recovery, 'spent', lambda: 3604.9)
    monkeypatch.setattr(recovery.runpy, 'run_path', lambda *a, **k: pytest.fail('entrypoint invoked'))
    monkeypatch.setattr(sys, 'argv', ['analysis_recovery_v1.py', 'analyze', 'validate'])
    with pytest.raises(TimeoutError, match='cap exhausted'):
        recovery.main()


def test_original_common_still_refuses_unclosed_attempt():
    # Immutable source establishes that direct commands retain their old fence.
    text = Path(__file__).with_name('common.py').read_text()
    assert "if r['status']=='RUNNING':raise RuntimeError('unclosed attempt; compute/resume ambiguous:" in text


@pytest.mark.parametrize('field,value', [
    ('recorded_utc', '2026-10-07T18:05:00Z'),
    ('recorded_utc', '2026-10-07T19:02:00Z'),
    ('wall_time_upper_bound_utc', '2026-10-07T18:07:00Z'),
    ('boot_time_evidence', dict(argv=['sysctl'], returncode=1, available=False, stdout='', stderr='denied')),
])
def test_observation_bound_and_boot_audit_required(tmp_path, field, value):
    _, path, record = receipts(tmp_path)
    record[field] = value
    put(path, record)
    with pytest.raises(RuntimeError, match='observation/boot'):
        recovery.spent(tmp_path)


def manifest_fixture(tmp_path, monkeypatch):
    receipts(tmp_path)
    for name in recovery.REQUIRED_BINDINGS:
        if not (tmp_path / name).exists():
            (tmp_path / name).write_text('fixture')
    put(tmp_path / 'RECOVERY_V1_PRESERVATION.json', {'base_head': 'a' * 40})
    manifest = dict(schema=1, scope='stored-only analysis/render recovery; no combat authorization',
                    compute_cap_s=3600, original_delivery_commit=recovery.ORIGINAL_DELIVERY,
                    base_head='a' * 40,
                    hashes={p.name: recovery.sha(p) for p in tmp_path.iterdir() if p.name in recovery.REQUIRED_BINDINGS or p.name.startswith('INTERRUPTION_')})
    put(tmp_path / recovery.MANIFEST, manifest)
    monkeypatch.setattr(recovery, 'HERE', tmp_path)
    return manifest


def test_supplemental_manifest_complete(tmp_path, monkeypatch):
    manifest = manifest_fixture(tmp_path, monkeypatch)
    assert recovery.verify_manifest() == manifest


@pytest.mark.parametrize('missing', sorted(recovery.REQUIRED_BINDINGS) + ['INTERRUPTION_test.json', 'ALL'])
def test_supplemental_manifest_missing_binding_refused(tmp_path, monkeypatch, missing):
    manifest = manifest_fixture(tmp_path, monkeypatch)
    if missing == 'ALL':
        manifest['hashes'] = {}
    else:
        del manifest['hashes'][missing]
    put(tmp_path / recovery.MANIFEST, manifest)
    with pytest.raises(RuntimeError, match='scope mismatch'):
        recovery.verify_manifest()


@pytest.mark.parametrize('field,value', [('compute_cap_s', 3601), ('original_delivery_commit', 'b'*40), ('base_head', 'b'*40)])
def test_supplemental_manifest_identity_refused(tmp_path, monkeypatch, field, value):
    manifest = manifest_fixture(tmp_path, monkeypatch)
    manifest[field] = value
    put(tmp_path / recovery.MANIFEST, manifest)
    with pytest.raises(RuntimeError):
        recovery.verify_manifest()
