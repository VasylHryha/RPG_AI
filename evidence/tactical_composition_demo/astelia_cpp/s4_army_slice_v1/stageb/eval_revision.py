"""Explicit evaluation recovery launcher; never change training sources or exports.

Use this launcher for recovered parity, DAgger and subsequent measurement. Direct
train.py retains its original strict gate. Later fits and their workers use this
launcher so historical DAgger ledgers retain their sealed source identities.
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
LAUNCHER = PREFIX + 'eval_revision.py'
CHAIN_REASON = ('Decision 0036; launcher-only recovery: eval_revision.py added run '
                'for rounds 1-2 at f0426d30; chained provenance, historical DAgger '
                'gate and worker/readout routing; no training-source changes.')


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


def chain_path(local, revision):
    return receipt_path(local).with_name(receipt_path(local).stem + '_V' + str(revision) + '.json')


def sealed(path):
    note = r.read(path)
    if note.get('seal_sha256') != digest({k: v for k, v in note.items() if k != 'seal_sha256'}):
        raise RuntimeError('evaluation recovery receipt seal drift')
    return note


def chain(local, bind_head=True):
    """Verify ancestors historically; only the head pins live recovery tooling."""
    path = receipt_path(local)
    if not path.exists():
        raise RuntimeError('Stage B evaluation drift requires a sealed recovery receipt')
    note = sealed(path)
    expected = baseline_proof(local)
    historical_sources = note['new_sources']
    if without_tooling(historical_sources) != without_tooling(expected['new_sources']):
        raise RuntimeError('evaluation recovery receipt identity drift')
    # The original sealed tooling hashes are provenance, not live ancestor pins.
    expected.update(new_sources=historical_sources,
                    recovery_tooling=source_proof(expected['old_sources'], historical_sources)['recovery_tooling'])
    if any(note.get(k) != v for k, v in expected.items()):
        raise RuntimeError('evaluation recovery receipt identity drift')
    if note.get('preserved_training_artifacts') != preserved_artifacts(local):
        raise RuntimeError('recovered training artifacts drift')
    if note.get('preserved_parity_receipts') != preserved_parity(local, expected):
        raise RuntimeError('original cached parity receipts drift')
    nodes = [(path, note)]
    paths = list(path.parent.glob(path.stem + '_V*.json'))
    ordered = [chain_path(local, n) for n in range(2, len(paths) + 2)]
    if set(paths) != set(ordered):
        raise RuntimeError('evaluation recovery chain gap or invalid revision')
    for revision, current in enumerate(ordered, 2):
        parent_path, parent = nodes[-1]
        head = sealed(current)
        sources = head['new_sources']
        proof = source_proof(expected['old_sources'], sources)
        fields = dict(schema=2, status='SEALED_LAUNCHER_RECOVERY', round=0,
                      revision=revision, reason=CHAIN_REASON,
                      parent=dict(path=parent_path.name, sha256=r.sha(parent_path)),
                      budget_sha256=expected['budget_sha256'], index_sha256=expected['index_sha256'],
                      training_sources=expected['training_sources'],
                      evaluation_changes=expected['evaluation_changes'],
                      recovery_tooling=proof['recovery_tooling'],
                      tooling_changes={k: dict(old_sha256=parent['new_sources'][k], new_sha256=sources[k])
                                       for k in sorted(TOOLING) if parent['new_sources'][k] != sources[k]})
        if (without_tooling(sources) != without_tooling(expected['new_sources']) or
                any(head.get(k) != v for k, v in fields.items())):
            raise RuntimeError('evaluation recovery chain identity drift')
        nodes.append((current, head))
    if bind_head and nodes[-1][1]['new_sources'] != r.sources():
        raise RuntimeError('evaluation recovery receipt identity drift at chain head')
    return nodes


def without_tooling(sources):
    return {k: v for k, v in sources.items() if k not in TOOLING}


def verify(local):
    chain(local)
    return r.read(local / 'TRAIN_BUDGET.json')


def recover_chain(round, revision=2):
    if round != 0 or revision < 2:
        raise RuntimeError('launcher recovery chains require round 0, revision >= 2')
    local = train.ROOT / 'round0'
    nodes = chain(local, bind_head=False)
    path = chain_path(local, revision)
    if path.exists():
        if nodes[-1][0] != path:
            raise RuntimeError('requested recovery revision is not the chain head')
        verify(local)
        return r.read(path)
    if revision != len(nodes) + 1:
        raise RuntimeError('recovery revision must extend the chain head once')
    parent_path, parent = nodes[-1]
    now = r.sources()
    payload = dict(schema=2, status='SEALED_LAUNCHER_RECOVERY', round=0, revision=revision,
        reason=CHAIN_REASON, parent=dict(path=parent_path.name, sha256=r.sha(parent_path)),
        budget_sha256=parent['budget_sha256'], index_sha256=parent['index_sha256'],
        training_sources=parent['training_sources'], evaluation_changes=parent['evaluation_changes'],
        new_sources=now, recovery_tooling={k: now[k] for k in sorted(TOOLING)},
        tooling_changes={k: dict(old_sha256=parent['new_sources'][k], new_sha256=now[k])
                         for k in sorted(TOOLING) if parent['new_sources'][k] != now[k]})
    payload['seal_sha256'] = digest(payload)
    r.write(path, payload, exclusive=True)
    verify(local)
    return payload


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
    if budget['round'] == 0:
        return verify(local)
    require_known_sources(budget['sources'])
    dataset_checked(local, budget)
    return budget


def require_known_sources(sources):
    nodes = chain(train.ROOT / 'round0')
    if sources not in [note['new_sources'] for _, note in nodes]:
        raise RuntimeError('unsealed historical source identity; preserve revision')


def dagger_checked(round):
    """Keep all original ledger gates; permit only exact sealed tooling history."""
    import dagger
    path = train.ROOT / ('DAGGER_LEDGER_ROUND' + str(round) + '.json')
    ledger = r.read(path)
    dagger.gate(round - 1)
    require_known_sources(ledger['sources'])
    if (ledger['round'] != round or ledger['binary'] != r.collect.identity() or
            ledger['parent_parity_sha256'] != r.sha(train.ROOT / ('round' + str(round - 1)) / 'PARITY_STAGEB.json')):
        raise RuntimeError('DAgger identity drift')
    for job in ledger['jobs']:
        if r.sha(train.ROOT / 'requests' / (job['tag'] + '.json')) != job['request_sha256']:
            raise RuntimeError('DAgger request drift')
    return ledger


def install_gates():
    train.checked = checked
    import parity_run, dagger
    parity_run.checked = checked  # Also covers modules imported before dispatch.
    dagger.check = dagger_checked


def training_run(round):
    # Only this launcher's children are rerouted; no source/global map changes.
    from types import SimpleNamespace
    original = train.subprocess
    def popen(argv, **kwargs):
        if argv[1:3] != [str(r.HERE / 'train.py'), 'worker']:
            raise RuntimeError('unexpected Stage B worker invocation')
        argv = [argv[0], str(r.HERE / 'eval_revision.py'), *argv[2:]]
        return original.Popen(argv, **kwargs)
    train.subprocess = SimpleNamespace(Popen=popen, TimeoutExpired=original.TimeoutExpired,
                                      STDOUT=original.STDOUT)
    try:
        return train.run(round)
    finally:
        train.subprocess = original


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


def dispatch(command, round, revision=2, look=20):
    if command == 'recover-eval-chain':
        note = recover_chain(round, revision)
        print('Sealed launcher recovery:', chain_path(train.ROOT / 'round0', revision))
        print('Changed tooling:', ', '.join(note['tooling_changes']))
        return note
    if command == 'recover-eval-revision':
        note = recover(round)
        print('Sealed evaluation recovery:', receipt_path(train.ROOT / 'round0'))
        print('Changed sources:', ', '.join(note['changed_sources']))
        return
    # Always recheck original provenance before a later-round gate/measurement.
    verify(train.ROOT / 'round0')
    install_gates()
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
        return training_run(round)
    if command in ('readout-prepare', 'readout-run'):
        import readout_run
        return readout_run.prepare(round) if command == 'readout-prepare' else readout_run.run(round, look)
    raise ValueError('unknown recovery command')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('recover-eval-revision', 'recover-eval-chain', 'parity',
        'dagger-prepare', 'dagger-run', 'measure', 'run', 'worker', 'readout-prepare', 'readout-run'))
    parser.add_argument('--round', type=int, choices=(0, 1, 2), required=True)
    parser.add_argument('--revision', type=int, default=2)
    parser.add_argument('--look', type=int, choices=(20, 50), default=20)
    parser.add_argument('--arm', choices=r.ARMS)
    parser.add_argument('--absolute', type=float)
    parser.add_argument('--cap', type=float)
    parser.add_argument('--fds', type=int, nargs=2)
    args = parser.parse_args()
    if args.command == 'worker':
        if args.round not in (1, 2) or any(v is None for v in (args.arm, args.absolute, args.cap, args.fds)):
            parser.error('later-round worker requires arm, absolute, cap and both lock fds')
        import jobs, os
        jobs.inherited(args.fds)
        verify(train.ROOT / 'round0')
        install_gates()
        os.nice(10)
        train.training.MONITOR = r.collect.a0()
        train.fit(args.arm, args.round, args.absolute, args.cap)
    else:
        dispatch(args.command, args.round, args.revision, args.look)
