"""Focused no-fight regression on the real recorded v5 mechanism receipts."""
import copy
import gzip
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for name in ('build', 'integrity', 'requests', 'metrics', 'lab', 'report', 'replays'):
    existing = sys.modules.get(name)
    if existing and pathlib.Path(getattr(existing, '__file__', '/')).parent != HERE:
        sys.modules.pop(name)
import lab
import metrics
import report


@pytest.fixture
def scratch(monkeypatch, request):
    root = HERE / 'test_scratch' / request.node.name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    continuation = lab.read(HERE / 'CONTINUATION.json')
    names = set(continuation['tool_hashes']) | set(continuation['inherited_files']) | {'CONTINUATION.json'}
    for name in names:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / name, target)
    monkeypatch.setattr(lab, 'HERE', root)
    monkeypatch.setattr(lab, 'RAW', root / 'raw')
    monkeypatch.setattr(report, 'HERE', root)
    monkeypatch.setattr(report, 'RAW', root / 'raw')
    return root


def forbidden(*args, **kwargs):
    raise AssertionError('no native fights, raw decoding, or re-measurement allowed')


def test_recorded_calibrate_outcome_preflight_finishes_with_hard_deadline():
    start = time.monotonic()
    result = subprocess.run([sys.executable, '-B', str(HERE / 'lab.py'), 'calibrate',
                             '--stage', 'outcome', '--look', '50', '--preflight-only'],
                            env={**os.environ, 'SHAPE_LAB_V5_CAFFEINATED': '1'},
                            capture_output=True, text=True, timeout=20)
    elapsed = time.monotonic() - start
    assert result.returncode == 0, result.stderr
    receipt = json.loads(result.stdout)
    assert receipt['status'] == 'READY_FOR_CALIBRATION'
    assert receipt['calibration_samples'] == 60 and receipt['fights_started'] == 0
    assert not list((HERE / 'raw').glob('C3_*'))
    (HERE / 'CALIBRATE_PREFLIGHT_TIMING.json').write_text(json.dumps(
        dict(seconds=elapsed, limit_seconds=20, status='PASS', fights_started=0,
             mode='real CLI calibrate outcome --preflight-only on recorded mechanism receipts'), indent=2)+'\n')


def test_exact_inheritance_and_hash_only_mechanism_admission(monkeypatch):
    monkeypatch.setattr(gzip, 'open', forbidden)
    monkeypatch.setattr(metrics, 'measure', forbidden)
    monkeypatch.setattr(lab, 'measure', forbidden)
    monkeypatch.setattr(lab.subprocess, 'run', forbidden)
    declaration = lab.identity()
    manifest = lab.read(HERE / 'CONTINUATION.json')
    for name in manifest['inherited_files']:
        if name.startswith('inherited_audit/'):
            continue
        assert (HERE / name).read_bytes() == (lab.V5 / name).read_bytes()
    assert declaration == lab.read(lab.V5 / 'DECLARATION.json')
    assert lab.selected_knobs() == (2.0, -1)
    assert lab.require_review('mechanism')['decision'] == 'continue'
    rows = lab.records_for('mechanism')
    assert len(rows) == 220
    assert lab.stage_summary('mechanism')[1] == lab.read(HERE / 'MECHANISM_SUMMARY.json')
    assert list(rows) == manifest['mechanism_tags']


def test_full_calibrate_control_flow_mocked_fights_and_immutable_resume(scratch, monkeypatch):
    """Exercise the full calibration/projection path; all outcomes are synthetic."""
    real_records_for = lab.records_for
    template = next(iter(real_records_for('mechanism').values()))
    fake = {}
    monkeypatch.setattr(metrics, 'measure', forbidden)
    monkeypatch.setattr(gzip, 'open', forbidden)
    monkeypatch.setattr(lab.subprocess, 'run', forbidden)
    def records(stage):
        return fake if stage == 'outcome' else real_records_for(stage)
    monkeypatch.setattr(lab, 'records_for', records)
    def execute(tag, req, meta, *args):
        assert meta['stage'] == 'outcome' and tuple(meta['knobs']) == (2.0, -1)
        assert tag not in fake
        row = copy.deepcopy(template)
        row.update(tag=tag, meta=meta, seconds=1)
        row['stats']['t_end'] = 150
        lab.write(lab.RAW / (tag + '_COMPLETE.json'), row, exclusive=True)
        fake[tag] = row
        return row
    monkeypatch.setattr(lab, 'execute', execute)
    def attempt(kind, stage, cap, jobs):
        assert kind == 'CALIBRATE' and stage == 'outcome'
        jobs(time.monotonic() + 10)
        row = dict(status='PASS', seconds=10, declaration_sha256=lab.sha(scratch / 'DECLARATION.json'))
        lab.write(scratch / 'CALIBRATE_outcome_ATTEMPT_mock.json', row, exclusive=True)
        return row
    monkeypatch.setattr(lab, 'compute_attempt', attempt)
    start = time.monotonic()
    lab.calibrate('outcome', 50)
    elapsed = time.monotonic() - start
    assert elapsed < 20
    assert len(fake) == 60
    assert lab.read(scratch / 'CALIBRATION_outcome_PROJECTION.json')['remaining_fights_max'] == 90
    receipt = (scratch / 'CALIBRATION_outcome.json').read_bytes()
    monkeypatch.setattr(lab, 'execute', forbidden)
    monkeypatch.setattr(lab, 'compute_attempt', forbidden)
    lab.calibrate('outcome', 50)
    assert (scratch / 'CALIBRATION_outcome.json').read_bytes() == receipt
    (HERE / 'CALIBRATE_MOCK_TIMING.json').write_text(json.dumps(
        dict(seconds=elapsed, limit_seconds=20, status='PASS', fights_started=0,
             mode='full calibrate control flow, synthetic outcome samples only'), indent=2)+'\n')


@pytest.mark.parametrize('name', ('PICK.json', 'MECHANISM_READ.json', 'frozen/SHAPE_LAB_SPEC.md', 'metrics.py', 'raw/SEED_LEDGER.json'))
def test_sealed_input_drift_rejected(scratch, name):
    target = scratch / name
    target.write_bytes(target.read_bytes() + b' ')
    with pytest.raises(RuntimeError, match='drift'):
        lab.ensure_stage('outcome', 50)


@pytest.mark.parametrize('suffix', ('_COMPLETE.json', '_CLAIM.json', '_request.json', '_stderr.log', '.jsonl.gz'))
def test_completed_cell_drift_rejected_without_decoding(scratch, monkeypatch, suffix):
    tag = lab.read(scratch / 'CONTINUATION.json')['mechanism_tags'][0]
    if suffix == '.jsonl.gz':
        parent = scratch / 'parent'
        (parent / 'raw').mkdir(parents=True)
        source = lab.V5 / 'raw' / (tag + suffix)
        target = parent / 'raw' / (tag + suffix)
        shutil.copyfile(source, target)
        monkeypatch.setattr(lab, 'V5', parent)
    else:
        target = lab.RAW / (tag + suffix)
    # Warm the cache first, then replace bytes of the same length; ctime/mtime
    # invalidation must catch edits after a successful verification.
    if suffix != '.jsonl.gz':
        lab.verified_record(tag)
    payload = target.read_bytes()
    target.write_bytes(payload[:-1] + (b'X' if payload[-1:] != b'X' else b'Y'))
    monkeypatch.setattr(gzip, 'open', forbidden)
    with pytest.raises((RuntimeError, json.JSONDecodeError)):
        lab.verified_record(tag)


def test_fixed_pick_and_sequential_stop_gate(scratch, monkeypatch):
    with pytest.raises(RuntimeError, match='immutable'):
        lab.pick(1, 400, 'changed')
    lab.write(scratch / 'OUTCOME_LOOK_50_READ.json', dict(decision='stop'))
    real_review = lab.require_review
    monkeypatch.setattr(lab, 'require_review', lambda stage, look=None: dict(decision='continue')
                        if stage == 'outcome' else real_review(stage, look))
    with pytest.raises(RuntimeError, match='earlier look'):
        lab.ensure_stage('outcome', 100)
    with pytest.raises(RuntimeError, match='finish sequential'):
        lab.ensure_stage('series', 50)


def test_new_measurement_seal_and_resume_never_remeasure(scratch, monkeypatch):
    inherited = next(iter(lab.records_for('mechanism').values()))
    tag = 'C3_synthetic_seal_p000'
    row = copy.deepcopy(inherited)
    row['tag'] = tag
    row['meta']['stage'] = 'outcome'
    original_tag = inherited['tag']
    for suffix in ('_request.json', '_CLAIM.json', '_stderr.log'):
        shutil.copyfile(lab.RAW / (original_tag + suffix), lab.RAW / (tag + suffix))
    # Claim must carry the same metadata as the new synthetic completion.
    claim_path = lab.RAW / (tag + '_CLAIM.json')
    claim = lab.read(claim_path)
    claim['meta'] = row['meta']
    lab.write(claim_path, claim)
    row['claim_sha256'] = lab.sha(claim_path)
    shutil.copyfile(lab.V5 / 'raw' / (original_tag + '.jsonl.gz'), lab.RAW / (tag + '.jsonl.gz'))
    done = lab.RAW / (tag + '_COMPLETE.json')
    lab.write(done, row)
    with pytest.raises(FileNotFoundError):
        lab.verified_record(tag)
    seal = lab.RAW / (tag + '_VERIFIED.json')
    lab.write(seal, dict(receipt_sha256=lab.sha(done), metrics_sha256=lab.sha(lab.HERE / 'metrics.py')))
    monkeypatch.setattr(gzip, 'open', forbidden)
    monkeypatch.setattr(metrics, 'measure', forbidden)
    monkeypatch.setattr(lab.subprocess, 'run', forbidden)
    assert lab.execute_cell(tag, lab.read(lab.RAW / (tag + '_request.json')), row['meta']) == row
    row['stats']['own_lost'] += 1
    lab.write(done, row)
    with pytest.raises(RuntimeError, match='seal drift'):
        lab.verified_record(tag)


@pytest.mark.parametrize('command', ('calibrate', 'run', 'review'))
def test_inherited_mechanism_commands_block_without_receipt_changes(scratch, monkeypatch, command):
    names = lab.read(scratch / 'CONTINUATION.json')['inherited_files']
    before = {name: (scratch / name).read_bytes() for name in names}
    monkeypatch.setattr(lab, 'compute_attempt', forbidden)
    monkeypatch.setattr(lab, 'write', forbidden)
    with pytest.raises(RuntimeError, match='mechanism.*blocked'):
        if command == 'review':
            lab.review('mechanism', 50, 'continue', 'attempted repeat')
        else:
            getattr(lab, command)('mechanism', 50)
    assert before == {name: (scratch / name).read_bytes() for name in names}


def test_process_discovery_fail_closed(scratch, monkeypatch):
    class Result:
        returncode = 2
        stdout = ''
        stderr = 'unavailable'
    monkeypatch.setattr(lab.subprocess, 'run', lambda *args, **kwargs: Result())
    with pytest.raises(RuntimeError, match='UNAVAILABLE'):
        lab.process_gate(wait=False)
