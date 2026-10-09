"""Config provenance, live controls, and fail-closed scratch boundary contracts."""
import copy
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import owner_approvals as a
import runtime as r


@pytest.fixture
def config(tmp_path, monkeypatch):
    raw = (r.HERE/'OWNER_APPROVALS.json').read_bytes()
    monkeypatch.setattr(r, 'HERE', tmp_path)
    monkeypatch.setattr(r, 'LOCAL', tmp_path/'_local')
    (tmp_path/'OWNER_APPROVALS.json').write_bytes(raw)
    return tmp_path/'OWNER_APPROVALS.json'


def test_config_is_not_source_pinned():
    assert not any('OWNER_APPROVALS' in key for key in r.sources())
    assert 's4_army_slice_v1/stageb/owner_approvals.py' in r.sources()


def test_hash_snapshots_and_return_to_old_config_are_logged(config):
    original = config.read_bytes(); first = a.snapshot()
    cfg = a.load(); cfg['training']['cap_seconds'] = 12345
    config.write_text(json.dumps(cfg)); second = a.snapshot()
    config.write_bytes(original); third = a.snapshot()
    assert first['sha256'] != second['sha256'] and third['sha256'] == first['sha256']
    for note in (first, second, third): a.verify_snapshot(note)
    history = [json.loads(line) for line in Path(first['history']).read_text().splitlines()]
    assert [v['sha256'] for v in history] == [first['sha256'], second['sha256'], first['sha256']]
    Path(first['archive']).write_text('drift')
    with pytest.raises(RuntimeError, match='snapshot drift'): a.verify_snapshot(first)


@pytest.mark.parametrize('field,value', [('cap_seconds', True), ('cap_seconds', float('nan')), ('cap_seconds', 0), ('cap_seconds', 16201)])
def test_invalid_training_cap_refuses(config, field, value):
    cfg = a.load(); cfg['training'][field] = value; config.write_text(json.dumps(cfg))
    with pytest.raises(ValueError): a.load()


def test_config_caps_are_live_and_scope_specific(config):
    cfg = a.load(); cfg['dagger']['cap_seconds'] = 456; cfg['lab']['cap_seconds'] = 789
    config.write_text(json.dumps(cfg))
    assert a.cap('dagger')['cap_seconds'] == 456 and a.cap('lab')['cap_seconds'] == 789
    assert a.cap()['cap_seconds'] == 16200


def test_live_reduction_never_extends_current_deadline(config, monkeypatch):
    now = [100.]; monkeypatch.setattr(a.time, 'monotonic', lambda:now[0])
    deadline = a.Deadline(100)
    cfg = a.load(); cfg['training']['cap_seconds'] = 40; config.write_text(json.dumps(cfg))
    assert deadline-100 == 40
    cfg['training']['cap_seconds'] = 200; config.write_text(json.dumps(cfg))
    assert deadline-100 == 40


def test_recurrent_rule_constants_change_without_source_edits(config):
    proof = dict(head_max_abs_error={'target':.02}, categorical_mismatches=1, rows=10000,
        mismatches=[dict(head='target',float64_top2_gap=.03,float64_selected_class_deficit=.03)])
    assert a.float32_passes(proof)
    cfg = a.load(); cfg['parity']['float32_recurrent_error_multiplier'] = 1
    config.write_text(json.dumps(cfg)); assert not a.float32_passes(proof)
    cfg['parity']['float32_recurrent_error_multiplier'] = 2
    cfg['parity']['float32_recurrent_flip_rate_max'] = .00001
    config.write_text(json.dumps(cfg)); assert not a.float32_passes(proof)


def test_config_native_atol_fire_rule_and_disk_reserve(config, monkeypatch):
    proof = dict(native_float64=dict(categorical_mismatches=0,max_abs_error=2e-8),
        float32_export=dict(head_max_abs_error={},categorical_mismatches=0,rows=1,mismatches=[]),
        calibrated_fire=dict(native_mismatches=0,uncertified_mismatches=0))
    assert not a.passes(proof)
    cfg = a.load(); cfg['parity']['native_atol'] = 3e-8; config.write_text(json.dumps(cfg))
    assert a.passes(proof)
    from types import SimpleNamespace
    monkeypatch.setattr(a.shutil, 'disk_usage', lambda path:SimpleNamespace(free=100))
    with pytest.raises(RuntimeError, match='disk reserve'): a.check_disk()
    cfg['resources']['disk_reserve_bytes'] = 50; config.write_text(json.dumps(cfg)); assert a.check_disk() == 100
    with pytest.raises(RuntimeError): a.check_disk(required=51)


def test_cached_fire_certification_is_recomputed_after_tightening(config):
    proof = dict(native_float64=dict(categorical_mismatches=0,max_abs_error=0),
        float32_export=dict(head_max_abs_error={},categorical_mismatches=0,rows=1,mismatches=[]),
        calibrated_fire=dict(native_mismatches=0,uncertified_mismatches=0,measured_logit_max_abs_error=.00004,
            float32_mismatches=[dict(relevant_gap=.00007, certified=True, bound=.00008)]))
    assert a.passes(proof)
    cfg = a.load(); cfg['parity']['calibrated_fire_near_tie_ceiling'] = .00006
    config.write_text(json.dumps(cfg)); assert not a.passes(proof)


def test_smoke_rejects_escape_existing_root_and_wrong_round(tmp_path):
    import smoke_chain
    with pytest.raises(ValueError, match='round 1'): smoke_chain.run(0, test_mode=True)
    with pytest.raises(ValueError, match='under stageb'): smoke_chain.run(1, test_mode=True, scratch_root=tmp_path)


def test_refused_remeasurement_preserves_raw_receipt_and_restores_on_early_failure(tmp_path, monkeypatch):
    import eval_revision as e
    root = tmp_path/'round1'; root.mkdir()
    path = root/'TRAIN_BUDGET.json'; original = b'{"status":"REFUSED","projection":421}\n'
    path.write_bytes(original)
    monkeypatch.setattr(e.train, 'ROOT', tmp_path)
    monkeypatch.setattr(e, 'checked', lambda local:r.read(path))
    def fail(round):
        assert not path.exists()
        raise RuntimeError('process gate refused')
    monkeypatch.setattr(e.train, 'measure', fail)
    with pytest.raises(RuntimeError, match='process gate'): e.measure(1)
    assert path.read_bytes() == original
    assert list((root/'refused_measurements').glob('*.json'))[0].read_bytes() == original
    def success(round):
        r.write(path, dict(status='ADMITTED')); return r.read(path)
    monkeypatch.setattr(e.train, 'measure', success)
    assert e.measure(1)['status'] == 'ADMITTED'
    assert list((root/'refused_measurements').glob('*.json'))[0].read_bytes() == original
    # Admitted budget is reused, never archived/replaced.
    before = path.read_bytes(); monkeypatch.setattr(e.train, 'measure', lambda round:r.read(path))
    assert e.measure(1)['status'] == 'ADMITTED' and path.read_bytes() == before


def test_refused_budget_with_training_artifacts_cannot_be_remeasured(tmp_path, monkeypatch):
    import eval_revision as e
    root = tmp_path/'round1'; (root/'training').mkdir(parents=True)
    path = root/'TRAIN_BUDGET.json'; r.write(path, dict(status='REFUSED'))
    (root/'training/checkpoint.pt').write_bytes(b'existing')
    monkeypatch.setattr(e.train, 'ROOT', tmp_path); monkeypatch.setattr(e, 'checked', lambda local:r.read(path))
    with pytest.raises(RuntimeError, match='training artifacts'): e.measure(1)
    assert path.exists() and not (root/'refused_measurements').exists()
