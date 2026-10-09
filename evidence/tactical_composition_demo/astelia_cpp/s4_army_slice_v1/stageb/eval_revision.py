"""Explicit evaluation recovery launcher; never change training sources or exports.

Use this launcher for recovered parity, DAgger and subsequent measurement. Direct
train.py retains its original strict gate, including for training/resume.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import secrets
import time

import runtime as r
import train

BASELINE = '9975c28990baf059a47e349ac6df8077cea3e642'
APPROVED = '0b710410064ca2cf45103be79ba6388e432ca346'
PREFIX = 's4_army_slice_v1/stageb/'
PARITY = PREFIX + 'calibrated_parity.py'
TOOLING = {PREFIX + 'eval_revision.py', PREFIX + 'test_eval_revision.py'}
REASON = ('Decision 0036; owner-requested evaluation-source recovery for the '
          'declared Stage B recurrent float32 parity rule at 0b71041; '
          'no training, calibration, export or native changes.')
ORIGINAL_CHECKED = train.checked


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


def historical(commit, name):
    # Fixed commits, no checkout or execution of historical code.
    root = r.CPP.parents[2]
    path = str((r.CPP / name).relative_to(root))
    return subprocess.check_output(['git', 'show', commit + ':' + path], cwd=root)


def historical_json(commit, name):
    return json.loads(historical(commit, name))


def receipt_path(local):
    return r.HERE / ('RECOVERY_STAGEB_EVAL_ROUND' + str(r.read(local / 'TRAIN_BUDGET.json')['round']) + '.json')


def source_proof(old, new):
    changed = sorted(k for k in old.keys() | new.keys() if old.get(k) != new.get(k))
    # Everything except this one approved evaluator is conservatively protected,
    # including train, runtime, calibration, workers, control and native code.
    allowed = {PARITY} | TOOLING
    if not set(changed) <= allowed or PARITY not in changed:
        raise RuntimeError('training-relevant source drift; preserve revision: ' + ', '.join(changed))
    if any(k in old or k not in new for k in TOOLING):
        raise RuntimeError('recovery tooling must be new, not a training dependency')
    before = hashlib.sha256(historical(BASELINE, PARITY)).hexdigest()
    after = hashlib.sha256(historical(APPROVED, PARITY)).hexdigest()
    if old.get(PARITY) != before or new.get(PARITY) != after:
        raise RuntimeError('only the declared approved parity revision may be recovered')
    return dict(changed_sources=changed,
                training_sources={k: v for k, v in old.items() if k != PARITY},
                evaluation_changes={PARITY: dict(old_sha256=before, new_sha256=after)},
                recovery_tooling={k: new[k] for k in sorted(TOOLING)})


def dataset_checked(local, budget):
    index = r.read(local / 'INDEX.json')
    train.validate_index(index)
    if budget['index_sha256'] != r.sha(local / 'INDEX.json'):
        raise RuntimeError('Stage B training index drift; preserve revision')
    for fight in index['fights']:
        if r.sha(fight['raw_file']) != fight['raw_sha256']:
            raise RuntimeError('training shard drift')


def baseline_proof(local):
    budget = r.read(local / 'TRAIN_BUDGET.json')
    if budget['round'] != 0 or local.resolve() != (train.ROOT / 'round0').resolve():
        raise RuntimeError('this recovery is only for the completed round-0 fit')
    if budget['status'] != 'ADMITTED':
        raise RuntimeError('admitted original budget required')
    dataset_checked(local, budget)
    now = r.sources()
    proof = source_proof(budget['sources'], now)
    budget_sha = r.sha(local / 'TRAIN_BUDGET.json')
    if not all(train.complete(local, arm, budget_sha) for arm in r.ARMS):
        raise RuntimeError('all original calibrated fits must be complete')
    # TRAIN_BUDGET has the Python/train/runtime/native seams. The contemporaneous
    # build additionally covers generated native files and engine dependencies.
    old_build = historical_json(BASELINE, PREFIX + 'BUILD_STAGEB.json')['identity']
    current_build = r.collect.identity()  # Original build admission, unchanged.
    for name, expected in old_build['sources'].items():
        if name == PARITY:
            continue
        if current_build['sources'].get(name) != expected or r.sha(r.CPP / name) != expected:
            raise RuntimeError('training/native build source drift: ' + name)
    if any(current_build[k] != old_build[k] for k in
           ('binary_sha256', 'engine', 'scope', 'sanitized', 'portable')):
        raise RuntimeError('original native binary identity drift')
    if any(old_build['sources'].get(k) != v for k, v in budget['sources'].items()):
        raise RuntimeError('original budget and contemporaneous build disagree')
    return dict(schema=1, status='SEALED_EVALUATION_ONLY', round=0, reason=REASON,
                baseline_commit=BASELINE, approved_eval_commit=APPROVED,
                budget_sha256=budget_sha, index_sha256=budget['index_sha256'],
                old_sources=budget['sources'], new_sources=now,
                old_build=old_build, new_build=current_build, **proof)


def preserved_artifacts(local):
    # All epochs/checkpoints, calibrated exports and outcomes remain immutable.
    return {str(p.relative_to(local)): r.sha(p)
            for p in sorted((local / 'training').rglob('*')) if p.is_file()}


def preserved_parity(local, proof):
    import parity
    manifest = dict(binary=proof['old_build'], budget_sha256=proof['budget_sha256'],
                    index_sha256=proof['index_sha256'],
                    exports={a: r.sha(local / 'training' / (a + '.weights.json')) for a in r.ARMS},
                    parity_rule=parity.PARITY_RULE)
    fights = {f['tag']: f for f in r.read(local / 'INDEX.json')['fights'] if f['split'] == 'validation'}
    preserved = {}
    for path in sorted((local / 'parity/certified_near_tie_v1').glob('*.json')):
        record = r.read(path)
        if (record['manifest'] != manifest or record['arm'] not in r.ARMS or
                record['fight'] not in fights or
                path.name != record['arm'] + '_' + record['fight'] + '.json' or
                record['raw_sha256'] != fights[record['fight']]['raw_sha256']):
            raise RuntimeError('original cached parity identity drift: ' + path.name)
        preserved[str(path.relative_to(local))] = r.sha(path)
    return preserved


def verify(local):
    path = receipt_path(local)
    if not path.exists():
        raise RuntimeError('Stage B evaluation drift requires a sealed recovery receipt')
    note = r.read(path)
    payload = {k: v for k, v in note.items() if k != 'seal_sha256'}
    if note.get('seal_sha256') != digest(payload):
        raise RuntimeError('evaluation recovery receipt seal drift')
    expected = baseline_proof(local)
    if any(note.get(k) != v for k, v in expected.items()):
        raise RuntimeError('evaluation recovery receipt identity drift')
    if note.get('preserved_training_artifacts') != preserved_artifacts(local):
        raise RuntimeError('recovered training artifacts drift')
    if note.get('preserved_parity_receipts') != preserved_parity(local, expected):
        raise RuntimeError('original cached parity receipts drift')
    return r.read(local / 'TRAIN_BUDGET.json')


def recover(round):
    if round != 0:
        raise RuntimeError('only completed round 0 may be recovered')
    local = train.ROOT / 'round0'
    path = receipt_path(local)
    if path.exists():
        verify(local)
        return r.read(path)
    payload = baseline_proof(local)
    # Documentation is recorded as provenance only, never a live source pin.
    protocol = PREFIX + 'STAGEB_PROTOCOL.md'
    old_doc = historical(BASELINE, protocol)
    new_doc = historical(APPROVED, protocol)
    if not new_doc.startswith(old_doc):
        raise RuntimeError('approved protocol revision must be an addendum')
    payload['documentation_change'] = dict(path=protocol,
        old_sha256=hashlib.sha256(old_doc).hexdigest(),
        new_sha256=hashlib.sha256(new_doc).hexdigest(), live_pin=False)
    payload['preserved_training_artifacts'] = preserved_artifacts(local)
    payload['preserved_parity_receipts'] = preserved_parity(local, payload)
    payload['seal_sha256'] = digest(payload)
    r.write(path, payload, exclusive=True)
    verify(local)
    return payload


def checked(local):
    # No global source-map substitution: later ledgers/budgets pin current code.
    budget = r.read(local / 'TRAIN_BUDGET.json')
    if budget['sources'] == r.sources():
        return ORIGINAL_CHECKED(local)
    budget = verify(local)
    return budget


def adjudicate(original, original_name, note, manifest, recovery_sha):
    import calibrated_parity as calibrated
    record = dict(original)
    record['original_receipt'] = dict(path=original_name,
        sha256=note['preserved_parity_receipts'][original_name], status=record['status'])
    record['adjudication'] = 'approved Stage B recurrent float32 rule; preserved numeric comparisons'
    record['status'] = 'PASS' if calibrated.passes(record) else 'FAIL'
    record.update(manifest=manifest, recovery_sha256=recovery_sha)
    return record


def parity_run(round):
    """Adjudicate preserved numeric proofs into a separate evaluation revision."""
    # Other rounds use their normally registered current sources and caches.
    if round != 0:
        import parity_run as runner
        return runner.run(round)
    import calibrated_parity as calibrated
    import parity
    from jobs import admitted
    from training_control import training_cap, TrainingDeadline
    local = train.configure(round)
    checked(local)
    note = r.read(receipt_path(local))
    recovery_sha = r.sha(receipt_path(local))
    parity.LOCAL = local
    parity.RECEIPT_DIRECTORY = local / 'parity/eval_revision_v1'
    parity.environment()
    manifest = dict(binary=r.collect.identity(), budget_sha256=r.sha(local / 'TRAIN_BUDGET.json'),
                    index_sha256=r.sha(local / 'INDEX.json'),
                    exports={a: r.sha(local / 'training' / (a + '.weights.json')) for a in r.ARMS},
                    parity_rule=parity.PARITY_RULE)
    started = time.monotonic()
    receipt = dict(status='RUNNING', round=round, manifest=manifest,
                   recovery_sha256=recovery_sha, records=[])
    cap = training_cap(r.HERE)
    try:
        with admitted(cap['cap_seconds']) as (absolute, monitor):
            parity.DEADLINE = TrainingDeadline(r.HERE, absolute, cap['cap_seconds'])
            parity.MONITOR = monitor
            val = [f for f in r.read(local / 'INDEX.json')['fights'] if f['split'] == 'validation']
            rates = {}
            for index, fight in enumerate(val):
                for arm in r.ARMS:
                    parity.check_live()
                    path = parity.RECEIPT_DIRECTORY / (arm + '_' + fight['tag'] + '.json')
                    original = local / 'parity/certified_near_tie_v1' / path.name
                    original_name = str(original.relative_to(local))
                    if path.exists():
                        record = r.read(path)
                        if (record['manifest'] != manifest or record['recovery_sha256'] != recovery_sha or
                                not calibrated.passes(record)):
                            raise RuntimeError('revised parity cache drift')
                        if original_name in note['preserved_parity_receipts'] and record != adjudicate(
                                r.read(original), original_name, note, manifest, recovery_sha):
                            raise RuntimeError('revised parity numeric proof drift')
                    else:
                        if original_name in note['preserved_parity_receipts']:
                            record = adjudicate(r.read(original), original_name, note, manifest, recovery_sha)
                        else:
                            record = calibrated.evaluate(arm, fight)
                        record.update(manifest=manifest, recovery_sha256=recovery_sha)
                        r.write(path, record, exclusive=True)
                        if not calibrated.passes(record):
                            raise RuntimeError('native/export numeric parity failed under approved rule')
                    receipt['records'].append(record)
                    rates[arm] = max(rates.get(arm, 0), record['seconds'] / max(1, record['frames']))
                if index == 0:
                    projection = 1.2 * sum(rates[a] * f['frames'] for f in val[1:] for a in r.ARMS
                        if not (parity.RECEIPT_DIRECTORY / (a + '_' + f['tag'] + '.json')).exists()
                        and 'parity/certified_near_tie_v1/' + a + '_' + f['tag'] + '.json'
                        not in note['preserved_parity_receipts'])
                    if projection > parity.DEADLINE - time.monotonic():
                        raise RuntimeError('measured parity tail exceeds cap')
            r.write(local / 'PARITY_STAGEB.json', dict(status='PASS', round=round,
                seconds=time.monotonic() - started, **manifest, records=receipt['records'],
                recovery_sha256=recovery_sha))
            receipt['status'] = 'DONE'
    except BaseException as error:
        receipt.update(status='STOP_RESUMABLE', error=str(error))
        raise
    finally:
        parity.DEADLINE = None
        parity.MONITOR = None
        receipt['seconds'] = time.monotonic() - started
        r.write(r.HERE / ('PARITY_STAGEB_EVAL_RUN_' + secrets.token_hex(8) + '.json'), receipt, exclusive=True)


def dispatch(command, round):
    if command == 'recover-eval-revision':
        note = recover(round)
        print('Sealed evaluation recovery:', receipt_path(train.ROOT / 'round0'))
        print('Changed sources:', ', '.join(note['changed_sources']))
        return
    # Always recheck original provenance before a later-round gate/measurement.
    verify(train.ROOT / 'round0')
    train.checked = checked
    if command == 'parity':
        return parity_run(round)
    if command in ('dagger-prepare', 'dagger-run'):
        import dagger
        return (dagger.prepare if command == 'dagger-prepare' else dagger.run)(round)
    if command == 'measure':
        if round not in (1, 2):
            raise RuntimeError('recovered measurement is for later rounds only')
        return train.measure(round)
    if command == 'run':
        # Claude 2026-10-09: later-round fits under the same recovery binding as their measurement.
        if round not in (1, 2):
            raise RuntimeError('recovered training run is for later rounds only')
        return train.run(round)
    raise ValueError('unknown recovery command')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('recover-eval-revision', 'parity',
        'dagger-prepare', 'dagger-run', 'measure', 'run'))
    parser.add_argument('--round', type=int, choices=(0, 1, 2), required=True)
    args = parser.parse_args()
    dispatch(args.command, args.round)
