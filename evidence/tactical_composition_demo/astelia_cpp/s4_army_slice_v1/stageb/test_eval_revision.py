"""Recovery gate fixtures only; no native processes, fitting or panel runs."""
import copy
import hashlib
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eval_revision as e


@pytest.fixture
def recovery(tmp_path, monkeypatch):
    import parity_run, dagger
    # Dispatch intentionally installs process-local gates; restore after fixtures.
    for module, name in ((e.train, 'checked'), (parity_run, 'checked'), (dagger, 'check')):
        monkeypatch.setattr(module, name, getattr(module, name))
    r = e.r
    here = tmp_path / 's4_army_slice_v1/stageb'
    local = here / '_local/round0'
    names = [e.PARITY, *sorted(e.TOOLING), e.PREFIX + 'train.py',
             e.PREFIX + 'runtime.py', e.PREFIX + 'loss.py',
             e.PREFIX + 'calibration.py', e.PREFIX + 'claude_train_cap.py',
             's4_army_slice_v1/stagea/models.py',
             's4_army_slice_v1/stagea/data.py',
             's4_army_slice_v1/stagea/training.py',
             's4_army_slice_v1/stagea/worker.py',
             's4_army_slice_v1/stagea/training_control.py',
             e.PREFIX + 'shadow.cpp']
    for name in names:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('original ' + name)
    old_parity = (tmp_path / e.PARITY).read_bytes()
    old = {name: r.sha(tmp_path / name) for name in names if name not in e.TOOLING}
    (tmp_path / e.PARITY).write_text('approved evaluation rule')
    new_parity = (tmp_path / e.PARITY).read_bytes()
    raw = local / 'raw'
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_bytes(b'original data')
    r.write(local / 'INDEX.json', dict(fights=[dict(tag='validation_0125', split='validation',
        frames=2, raw_file=str(raw), raw_sha256=r.sha(raw))]))
    budget = dict(round=0, status='ADMITTED', sources=old,
                  index_sha256=r.sha(local / 'INDEX.json'))
    r.write(local / 'TRAIN_BUDGET.json', budget)
    for arm in r.ARMS:
        out = local / 'training'
        for suffix in ('.pt', '.weights.json', '.calibration.json'):
            (out).mkdir(exist_ok=True)
            (out / (arm + suffix)).write_bytes(b'original trained artifact')
        r.write(out / (arm + '.outcome.json'), dict(
            status='FIT_CALIBRATED_PARITY_PENDING',
            budget_sha256=r.sha(local / 'TRAIN_BUDGET.json'),
            export_sha256=r.sha(out / (arm + '.weights.json')),
            calibration_sha256=r.sha(out / (arm + '.calibration.json')),
            checkpoint_sha256=r.sha(out / (arm + '.pt'))))
    native = tmp_path / 'native.cpp'
    native.write_text('native training-side code')
    old_build = dict(sources={**old, 'native.cpp': r.sha(native)},
                     binary_sha256='unchanged', engine='army_stageb',
                     scope='native_complete_engine', sanitized=False, portable=False)
    new_build = copy.deepcopy(old_build)
    new_build['sources'][e.PARITY] = r.sha(tmp_path / e.PARITY)
    monkeypatch.setattr(r, 'CPP', tmp_path)
    monkeypatch.setattr(r, 'HERE', here)
    monkeypatch.setattr(e.train, 'ROOT', here / '_local')
    monkeypatch.setattr(parity_run, 'ROOT', here / '_local')
    monkeypatch.setattr(e.train, 'validate_index', lambda index: None)
    monkeypatch.setattr(r, 'sources', lambda: {name: r.sha(tmp_path / name)
                                            for name in names if (tmp_path / name).exists()})
    monkeypatch.setattr(r.collect, 'identity', lambda: copy.deepcopy(new_build))
    monkeypatch.setattr(e, 'historical_json', lambda commit, name: dict(identity=copy.deepcopy(old_build)))
    def historical(commit, name):
        if name == e.PARITY:
            return old_parity if commit == e.BASELINE else new_parity
        return b'original protocol\n' if commit == e.BASELINE else b'original protocol\naddendum\n'
    monkeypatch.setattr(e, 'historical', historical)
    return local, names


def advance_tooling():
    for name in e.TOOLING:
        with (e.r.CPP / name).open('a') as file:
            file.write('\nlauncher/fixture revision')


def test_chained_launcher_recovery_keeps_original_and_only_pins_head(recovery):
    local, _ = recovery
    e.recover(0)
    original_sha = e.r.sha(e.receipt_path(local))
    advance_tooling()
    with pytest.raises(RuntimeError, match='chain head'):
        e.checked(local)
    note = e.recover_chain(0)
    assert note['revision'] == 2
    assert note['parent']['sha256'] == original_sha
    assert set(note['tooling_changes']) == e.TOOLING
    assert e.checked(local)['round'] == 0
    assert e.recover_chain(0) == note
    v2_sha = e.r.sha(e.chain_path(local, 2))
    advance_tooling()
    with pytest.raises(RuntimeError, match='chain head'):
        e.checked(local)
    e.recover_chain(0, 3)
    assert e.checked(local)['round'] == 0
    assert e.r.sha(e.receipt_path(local)) == original_sha
    assert e.r.sha(e.chain_path(local, 2)) == v2_sha


@pytest.mark.parametrize('part', ['train.py', 'loss.py', 'runtime.py', 'calibration.py', 'shadow.cpp'])
def test_chain_cannot_authorize_training_drift(recovery, part):
    local, _ = recovery
    e.recover(0)
    advance_tooling()
    e.recover_chain(0)
    (e.r.CPP / (e.PREFIX + part)).write_text('training change')
    with pytest.raises(RuntimeError, match='training-relevant source drift'):
        e.checked(local)
    with pytest.raises(RuntimeError, match='training-relevant source drift'):
        e.recover_chain(0, 3)
    assert not e.chain_path(local, 3).exists()


@pytest.mark.parametrize('part', ['ancestor', 'parent_link', 'training_proof', 'tooling_hash', 'gap'])
def test_chain_tampering_refused_even_when_resealed(recovery, part):
    local, _ = recovery
    e.recover(0)
    advance_tooling()
    e.recover_chain(0)
    path = e.receipt_path(local) if part == 'ancestor' else e.chain_path(local, 2)
    if part == 'gap':
        path.rename(e.chain_path(local, 3))
    else:
        note = e.r.read(path)
        if part == 'ancestor':
            note['reason'] = 'different authority'
        elif part == 'parent_link':
            note['parent']['sha256'] = 'unrelated parent'
        elif part == 'training_proof':
            note['training_sources'][e.PREFIX + 'train.py'] = 'changed training proof'
        else:
            note['recovery_tooling'][e.LAUNCHER] = 'unbound launcher'
        note['seal_sha256'] = e.digest({k: v for k, v in note.items() if k != 'seal_sha256'})
        e.r.write(path, note)
    with pytest.raises(RuntimeError):
        e.checked(local)


def test_historical_dagger_ledger_gate_preserves_non_source_checks(recovery, monkeypatch):
    import dagger
    local, _ = recovery
    e.recover(0)
    sources = e.r.sources()
    e.r.write(local / 'PARITY_STAGEB.json', {'status': 'PASS'})
    job = dict(tag='dagger_fixture', request_sha256='')
    request = e.train.ROOT / 'requests/dagger_fixture.json'
    e.r.write(request, dict(fixture=True))
    job['request_sha256'] = e.r.sha(request)
    path = e.train.ROOT / 'DAGGER_LEDGER_ROUND1.json'
    ledger = dict(round=1, sources=sources, binary=e.r.collect.identity(), jobs=[job],
                  parent_parity_sha256=e.r.sha(local / 'PARITY_STAGEB.json'))
    e.r.write(path, ledger)
    before = e.r.sha(path)
    advance_tooling()
    e.recover_chain(0)
    calls = []
    monkeypatch.setattr(dagger, 'gate', lambda round: calls.append(round))
    assert e.dagger_checked(1) == ledger
    assert calls == [0] and e.r.sha(path) == before
    bad = copy.deepcopy(ledger)
    bad['sources'][e.LAUNCHER] = 'never sealed tooling'
    e.r.write(path, bad)
    with pytest.raises(RuntimeError, match='unsealed historical'):
        e.dagger_checked(1)
    e.r.write(path, ledger)
    request.write_text('changed request')
    with pytest.raises(RuntimeError, match='request drift'):
        e.dagger_checked(1)


def test_round1_measure_run_parity_end_to_end_fixture(recovery, monkeypatch):
    """Real orchestration/receipts; numerical work, admission and children are fixtures."""
    from contextlib import contextmanager
    from types import SimpleNamespace
    import jobs, loss, parity, parity_run, calibrated_parity, training_control
    local, _ = recovery
    e.recover(0)
    advance_tooling()
    e.recover_chain(0)
    round1 = e.train.ROOT / 'round1'
    fight = e.r.read(local / 'INDEX.json')['fights'][0]
    index = dict(round=1, fights=[dict(fight, split=s, tag=s) for s in ('train', 'validation', 'test')])
    index['arm_fights'] = {arm: index['fights'] for arm in e.r.ARMS}
    e.r.write(round1 / 'INDEX.json', index)
    monkeypatch.setattr(e.train, 'prepare', lambda round: index)
    monkeypatch.setattr(e.train, 'configure', lambda round: round1)
    monkeypatch.setattr(parity_run, 'configure', lambda round: round1)
    monkeypatch.setattr(e.train.training, 'environment', lambda: None)
    monkeypatch.setattr(e.train.training, 'MONITOR', None, raising=False)
    monkeypatch.setattr(e.train.training, 'make', lambda arm: (object(), object()))
    monkeypatch.setattr(e.train.training, 'stored', lambda *a: ([{}, {}], {0: None, 1: None}, .01))
    monkeypatch.setattr(e.train.training, 'step', lambda *a: dict(wall_seconds=.01))
    monkeypatch.setattr(e.train.training, 'evaluate', lambda *a: dict(wall_seconds=.01))
    monkeypatch.setattr(e.train.training, 'selected_starts', lambda *a: [0, 1])
    monkeypatch.setattr(e.r.data, 'frames', lambda *a: iter([{}, {}]))
    monkeypatch.setattr(loss, 'target_weights', lambda *a: {'fixture': True})
    monkeypatch.setattr(loss, 'install', lambda *a: None)
    cap = dict(cap_seconds=16200)
    for module in (e.train, parity_run, training_control):
        monkeypatch.setattr(module, 'training_cap', lambda *a: cap)
        monkeypatch.setattr(module, 'TrainingDeadline', lambda *a: 10**20)
    monkeypatch.setattr(e.train, 'measured_cores', lambda: dict(slots=4))
    @contextmanager
    def admitted(seconds):
        assert seconds == 16200
        yield 10**20, SimpleNamespace(live_memory=lambda pid: None)
    monkeypatch.setattr(jobs, 'admitted', admitted)
    budget = e.dispatch('measure', 1)
    assert budget['status'] == 'ADMITTED' and budget['epochs'] == 10
    assert budget['sources'] == e.r.sources()
    budget_sha = e.r.sha(round1 / 'TRAIN_BUDGET.json')
    arms = []
    def child(argv, **kwargs):
        assert argv[1:3] == [str(e.r.HERE / 'eval_revision.py'), 'worker']
        assert argv[argv.index('--round') + 1] == '1'
        assert kwargs['pass_fds'] == jobs.ACTIVE_FDS
        arm = argv[argv.index('--arm') + 1]
        # The worker gate runs against the actual freshly measured budget.
        assert e.checked(round1) == budget
        arms.append(arm)
        out = round1 / 'training'
        for suffix in ('.pt', '.weights.json', '.calibration.json'):
            (out / (arm + suffix)).write_text('fixture fitted artifact')
        e.r.write(out / (arm + '.outcome.json'), dict(status='FIT_CALIBRATED_PARITY_PENDING',
            budget_sha256=budget_sha, export_sha256=e.r.sha(out / (arm + '.weights.json')),
            calibration_sha256=e.r.sha(out / (arm + '.calibration.json')),
            checkpoint_sha256=e.r.sha(out / (arm + '.pt'))))
        return SimpleNamespace(poll=lambda: 0, returncode=0, pid=0)
    monkeypatch.setattr(e.train, 'subprocess', SimpleNamespace(Popen=child, TimeoutExpired=TimeoutError,
                                                             STDOUT=-2))
    e.dispatch('run', 1)
    assert set(arms) == set(e.r.ARMS)
    assert all(e.train.complete(round1, arm, budget_sha) for arm in e.r.ARMS)
    monkeypatch.setattr(parity, 'environment', lambda: None)
    for attr in ('LOCAL', 'RECEIPT_DIRECTORY', 'DEADLINE', 'MONITOR'):
        monkeypatch.setattr(parity, attr, getattr(parity, attr, None), raising=False)
    def evaluate(arm, fight):
        return dict(arm=arm, fight=fight['tag'], frames=2, seconds=.01,
            native_float64=dict(categorical_mismatches=0, max_abs_error=0),
            float32_export=dict(head_max_abs_error={}, rows=2, categorical_mismatches=0, mismatches=[]),
            calibrated_fire=dict(native_mismatches=0, uncertified_mismatches=0))
    monkeypatch.setattr(calibrated_parity, 'evaluate', evaluate)
    e.dispatch('parity', 1)
    proof = parity_run.gate(1)
    assert proof['status'] == 'PASS' and len(proof['records']) == len(e.r.ARMS)
    assert e.r.sha(round1 / 'TRAIN_BUDGET.json') == budget_sha
    assert all(e.r.read(p)['status'] == 'DONE' for pattern in ('TRAIN_STAGEB_RUN_*.json', 'PARITY_STAGEB_RUN_*.json')
               for p in e.r.HERE.glob(pattern))


def test_eval_change_requires_receipt_and_preserves_budget_and_fits(recovery):
    local, _ = recovery
    before = e.r.sha(local / 'TRAIN_BUDGET.json'), e.preserved_artifacts(local)
    with pytest.raises(RuntimeError, match='sealed recovery receipt'):
        e.checked(local)
    note = e.recover(0)
    assert note['old_sources'] != note['new_sources']
    assert note['training_sources'] == {k: v for k, v in note['old_sources'].items() if k != e.PARITY}
    assert note['documentation_change']['live_pin'] is False
    assert e.checked(local) == e.r.read(local / 'TRAIN_BUDGET.json')
    receipt_hash = e.r.sha(e.receipt_path(local))
    assert e.recover(0) == note
    assert e.r.sha(e.receipt_path(local)) == receipt_hash
    assert before == (e.r.sha(local / 'TRAIN_BUDGET.json'), e.preserved_artifacts(local))


@pytest.mark.parametrize('source', [e.PREFIX + 'train.py', e.PREFIX + 'runtime.py',
    e.PREFIX + 'loss.py', e.PREFIX + 'calibration.py', e.PREFIX + 'claude_train_cap.py',
    's4_army_slice_v1/stagea/models.py', 's4_army_slice_v1/stagea/data.py',
    's4_army_slice_v1/stagea/training.py', 's4_army_slice_v1/stagea/worker.py',
    's4_army_slice_v1/stagea/training_control.py', e.PREFIX + 'shadow.cpp'])
@pytest.mark.parametrize('sealed', [False, True, 'chain'])
def test_training_drift_is_refused_before_and_after_recovery(recovery, source, sealed):
    local, _ = recovery
    if sealed:
        e.recover(0)
    if sealed == 'chain':
        advance_tooling()
        e.recover_chain(0)
    (e.r.CPP / source).write_text('training change')
    with pytest.raises(RuntimeError, match='training-relevant source drift'):
        e.checked(local) if sealed else e.recover(0)


def test_unknown_added_source_and_deleted_training_source_refused(recovery):
    local, names = recovery
    added = e.PREFIX + 'unregistered.py'
    (e.r.CPP / added).write_text('new dependency')
    names.append(added)
    with pytest.raises(RuntimeError, match='training-relevant source drift'):
        e.recover(0)
    names.remove(added)
    (e.r.CPP / (e.PREFIX + 'train.py')).unlink()
    with pytest.raises(RuntimeError, match='training-relevant source drift'):
        e.recover(0)


def test_only_approved_parity_revision_can_be_registered(recovery):
    (e.r.CPP / e.PARITY).write_text('arbitrary parity relaxation')
    with pytest.raises(RuntimeError, match='declared approved parity'):
        e.recover(0)


@pytest.mark.parametrize('part', ['receipt', 'resealed_receipt', 'budget', 'index', 'raw', 'export', 'tooling', 'native'])
@pytest.mark.parametrize('chained', [False, True])
def test_binding_or_artifact_drift_refused(recovery, part, chained):
    local, _ = recovery
    e.recover(0)
    if chained:
        advance_tooling()
        e.recover_chain(0)
    if part in ('receipt', 'resealed_receipt'):
        path = e.receipt_path(local)
        note = e.r.read(path)
        note['reason'] = 'changed reason'
        if part == 'resealed_receipt':
            note['seal_sha256'] = e.digest({k: v for k, v in note.items() if k != 'seal_sha256'})
        e.r.write(path, note)
    elif part == 'budget':
        path = local / 'TRAIN_BUDGET.json'
        e.r.write(path, dict(e.r.read(path), extra='changed budget'))
    elif part == 'index':
        (local / 'INDEX.json').write_text('{"fights": []}')
    elif part == 'raw':
        (local / 'raw').write_bytes(b'changed data')
    elif part == 'export':
        (local / 'training/N1.weights.json').write_text('changed export')
    elif part == 'tooling':
        (e.r.CPP / (e.PREFIX + 'eval_revision.py')).write_text('changed tooling')
    else:
        (e.r.CPP / 'native.cpp').write_text('native change outside budget map')
    with pytest.raises(RuntimeError):
        e.checked(local)


def test_protocol_is_provenance_not_living_pin(recovery):
    local, _ = recovery
    e.recover(0)
    (e.r.HERE / 'STAGEB_PROTOCOL.md').write_text('later living documentation edit')
    assert e.checked(local)['round'] == 0


def test_launcher_installs_gate_before_later_measurement(recovery, monkeypatch):
    local, _ = recovery
    e.recover(0)
    def measure(round):
        assert round == 1
        assert e.train.checked is e.checked
        assert e.train.checked(local)['round'] == 0
        # New budgets and ledgers keep the real current source map.
        assert set(e.TOOLING) <= e.r.sources().keys()
        return 'measured'
    monkeypatch.setattr(e.train, 'checked', e.ORIGINAL_CHECKED)
    monkeypatch.setattr(e.train, 'measure', measure)
    assert e.dispatch('measure', 1) == 'measured'


def test_unchanged_new_budget_retains_original_gate(recovery, monkeypatch):
    local, _ = recovery
    path = local / 'TRAIN_BUDGET.json'
    e.r.write(path, dict(e.r.read(path), sources=e.r.sources()))
    monkeypatch.setattr(e, 'ORIGINAL_CHECKED', lambda p: ('original', p))
    assert e.checked(local) == ('original', local)


def test_recovery_only_for_round_zero(recovery):
    with pytest.raises(RuntimeError, match='only completed round 0'):
        e.recover(1)


def test_cached_old_build_manifest_is_recovered_without_replay(recovery, monkeypatch):
    from contextlib import contextmanager
    import parity, calibrated_parity, training_control, jobs
    local, _ = recovery
    proof = e.baseline_proof(local)
    manifest = dict(binary=proof['old_build'], budget_sha256=proof['budget_sha256'],
                    index_sha256=proof['index_sha256'],
                    exports={a: e.r.sha(local / 'training' / (a + '.weights.json')) for a in e.r.ARMS},
                    parity_rule=parity.PARITY_RULE)
    originals = {}
    for arm in e.r.ARMS:
        flip = arm == 'N2'
        record = dict(arm=arm, fight='validation_0125', status='FAIL' if flip else 'PASS',
            raw_sha256=e.r.sha(local / 'raw'), frames=2, seconds=.01,
            manifest=manifest, native_float64=dict(categorical_mismatches=0, max_abs_error=0),
            float32_export=dict(head_max_abs_error=dict(target=.021), rows=45622,
                categorical_mismatches=int(flip), mismatches=[dict(head='target',
                float64_top2_gap=.0029, float64_selected_class_deficit=.0029)] if flip else []),
            calibrated_fire=dict(native_mismatches=0, uncertified_mismatches=0))
        path = local / 'parity/certified_near_tie_v1' / (arm + '_validation_0125.json')
        e.r.write(path, record, exclusive=True)
        originals[path] = e.r.sha(path)
    e.recover(0)
    @contextmanager
    def admitted(seconds):
        yield 10**20, object()
    monkeypatch.setattr(jobs, 'admitted', admitted)
    monkeypatch.setattr(training_control, 'training_cap', lambda here: dict(cap_seconds=60))
    monkeypatch.setattr(training_control, 'TrainingDeadline', lambda *args: 10**20)
    monkeypatch.setattr(parity, 'environment', lambda: None)
    monkeypatch.setattr(parity, 'check_live', lambda *args: None)
    def no_replay(*args):
        pytest.fail('cached numeric proofs must not launch native replay')
    monkeypatch.setattr(calibrated_parity, 'evaluate', no_replay)
    monkeypatch.setattr(e.train, 'checked', e.ORIGINAL_CHECKED)
    # train.configure mutates shared training state: use fixture-only configuration.
    monkeypatch.setattr(e.train, 'configure', lambda round: local)
    for attr in ('LOCAL', 'RECEIPT_DIRECTORY', 'DEADLINE', 'MONITOR'):
        monkeypatch.setattr(parity, attr, getattr(parity, attr, None), raising=False)
    e.dispatch('parity', 0)
    result = e.r.read(local / 'PARITY_STAGEB.json')
    import parity_run as original_parity
    monkeypatch.setattr(original_parity, 'checked', e.checked)
    assert original_parity.gate(0) == result  # The exact DAgger prerequisite.
    assert result['status'] == 'PASS' and len(result['records']) == 4
    assert result['binary'] != manifest['binary']
    revised = next(v for v in result['records'] if v['arm'] == 'N2')
    assert revised['status'] == 'PASS' and revised['original_receipt']['status'] == 'FAIL'
    assert all(e.r.sha(path) == sha for path, sha in originals.items())
    # Resume checks translated proofs and preserves original receipts.
    e.dispatch('parity', 0)
    altered = local / 'parity/eval_revision_v1/N2_validation_0125.json'
    record = e.r.read(altered)
    record['float32_export']['head_max_abs_error']['target'] = .04
    e.r.write(altered, record)
    with pytest.raises(RuntimeError, match='numeric proof drift'):
        e.dispatch('parity', 0)
