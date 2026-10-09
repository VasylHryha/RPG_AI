"""Explicit inference-only recovery; sealed training and collection stay frozen."""
import argparse
from common import ARMS, BINARY, CPP, HERE, LOCAL, read, sha, sources, write
from collect import identity, ledger_path

RECOVERY = HERE/'RECOVERY_STAGEA_PARMEM.json'
ALLOWED = ('bounded_json.h', 'build.py', 'stagea.cpp', 'stagea.h', 'parity.py',
           'readout.py', 'parmem_recovery.py', 'test_stagea_parmem.py',
           'test_stagea_parmem_host.py')


def verify_baseline(baseline, allowed_names=ALLOWED):
    for name, digest in baseline['preserved'].items():
        if sha(HERE/name) != digest:
            raise RuntimeError('parity recovery fixed evidence drift: '+name)
    old = baseline['sources']; now = sources()
    delta = {k for k in old.keys() | now.keys() if old.get(k) != now.get(k)}
    allowed = {str((HERE/n).relative_to(CPP)) for n in allowed_names}
    if not delta or not delta <= allowed:
        raise RuntimeError('parity recovery unauthorized source changes')
    budget = read(LOCAL/'TRAIN_BUDGET.json')
    audit = read(LOCAL/'DECIDABILITY.json')
    ledger = read(ledger_path())
    if (str(ledger_path().relative_to(LOCAL)) != baseline['ledger_file'] or
            ledger['sources'] != old or ledger['binary'] != baseline['binary'] or
            budget['sources'] != old or audit['sources'] != old or audit['status'] != 'PASS' or
            budget['status'] != 'ADMITTED' or
            budget['index_sha256'] != sha(LOCAL/'INDEX.json') or
            budget['audit_sha256'] != sha(LOCAL/'DECIDABILITY.json')):
        raise RuntimeError('parity recovery baseline identity mismatch')
    for job in ledger['jobs']:
        if sha(LOCAL/'requests'/(job['tag']+'.json')) != job['request_sha256']:
            raise RuntimeError('parity recovery sealed request drift')
    failure = read(HERE/'PARITY_RUN_c7136052e0485bba.json')
    if (failure['status'] != 'STOP_RESUMABLE' or
            failure['error'] != 'RuntimeError: child exceeds 2 GiB RSS' or
            failure['manifest']['binary'] != baseline['binary'] or
            failure['manifest']['budget_sha256'] != sha(LOCAL/'TRAIN_BUDGET.json') or
            failure['manifest']['index_sha256'] != sha(LOCAL/'INDEX.json')):
        raise RuntimeError('parity recovery failed receipt mismatch')
    for arm in ARMS:
        result = read(LOCAL/'training'/(arm+'.outcome.json'))
        if (result['budget_sha256'] != sha(LOCAL/'TRAIN_BUDGET.json') or
                result['export_sha256'] != sha(LOCAL/'training'/(arm+'.weights.json')) or
                result['checkpoint_sha256'] != sha(LOCAL/'training'/(arm+'.pt')) or
                result['export_sha256'] != failure['manifest']['exports'][arm]):
            raise RuntimeError('parity recovery trained artifact drift')
    current = identity()
    before = baseline['binary']['sources']; after = current['sources']
    build_delta = {k for k in before.keys() | after.keys() if before.get(k) != after.get(k)}
    if not build_delta <= allowed | {str((BINARY.parent/'lean_host.cpp').relative_to(CPP))}:
        raise RuntimeError('parity recovery unrelated native/build changes')
    if any(current[k] != baseline['binary'][k] for k in ('engine','scope','sanitized','portable')):
        raise RuntimeError('parity recovery engine admission changed')
    return budget, current, sorted(delta)


def register():
    from jobs import locked
    with locked():
        if RECOVERY.exists():return checked_inference_budget()
        baseline = read(LOCAL/'PARMEM_BASELINE.json')
        budget, current, delta = verify_baseline(baseline)
        write(RECOVERY, dict(status='REGISTERED_INFERENCE_ONLY_NO_RETRY',
              reason='Bounded input layouts and row streaming; decision 0036; no retraining',
              baseline=baseline, sources=sources(), binary=current, changed_sources=delta,
              scope='parity and outcome inference only; original collection/training gates unchanged',
              budget_sha256=sha(LOCAL/'TRAIN_BUDGET.json'),
              index_sha256=sha(LOCAL/'INDEX.json'),
              failure_sha256=sha(HERE/'PARITY_RUN_c7136052e0485bba.json')), exclusive=True)
        return budget


def checked_inference_budget():
    if (HERE/'RECOVERY_STAGEA_PARTIE.json').exists():
        from parity_recovery import checked as checked_ties
        return checked_ties()
    if not RECOVERY.exists():
        from training import checked_budget
        return checked_budget()
    note = read(RECOVERY)
    budget, current, delta = verify_baseline(note['baseline'])
    if (note['status'] != 'REGISTERED_INFERENCE_ONLY_NO_RETRY' or
            note['sources'] != sources() or note['binary'] != current or
            note['changed_sources'] != delta or
            note['budget_sha256'] != sha(LOCAL/'TRAIN_BUDGET.json') or
            note['index_sha256'] != sha(LOCAL/'INDEX.json') or
            note['failure_sha256'] != sha(HERE/'PARITY_RUN_c7136052e0485bba.json')):
        raise RuntimeError('parity recovery registration drift')
    return budget


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    register()
    print('Parity memory recovery registered; no replay or training executed.')
