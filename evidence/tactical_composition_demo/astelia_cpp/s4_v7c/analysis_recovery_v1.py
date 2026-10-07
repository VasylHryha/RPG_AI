"""Versioned stored-only launcher. Original seal and executable files stay intact."""
import argparse
import contextlib
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
STORED_STAGES = frozenset({'analyze_validate', 'render_validate'})
MANIFEST = 'ANALYSIS_RECOVERY_V1_MANIFEST.json'
ORIGINAL_DELIVERY = 'f31583b2e9aa3a89aad901a1123b299810495fc2'
REQUIRED_BINDINGS = frozenset({
    'analysis_recovery_v1.py', 'test_analysis_recovery_v1.py',
    'verify_analysis_recovery_v1.py', 'deliver_analysis_recovery_v1.py',
    'ANALYSIS_RECOVERY_V1.md', 'RECOVERY_V1_PRESERVATION.json',
    'SEAL.json', 'DECLARATION.json', 'common.py', 'run.py',
    'analyze.py', 'render.py', 'protocol.py',
})


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def timestamp(value):
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('UTC offset required')
    return parsed


def seconds(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError('finite nonnegative wall seconds required')
    return value


def spent(root=HERE, requested_stage='analyze_validate'):
    """Add interruption upper bounds once, while leaving RUNNING receipts intact."""
    attempts = {p.name: (p, read(p)) for p in root.glob('ATTEMPT_*.json')}
    interruptions = {}
    for path in root.glob('INTERRUPTION_*.json'):
        record = read(path)
        name = record['attempt_file']
        if name in interruptions or name not in attempts:
            raise RuntimeError('duplicate or orphan interruption: ' + path.name)
        interruptions[name] = record
    total = 0.0
    for name, (path, attempt) in attempts.items():
        if attempt['status'] != 'RUNNING':
            if name in interruptions:
                raise RuntimeError('interruption target must remain RUNNING: ' + name)
            total += seconds(attempt['seconds'])
            continue
        record = interruptions.get(name)
        if requested_stage not in STORED_STAGES or attempt['stage'] not in STORED_STAGES or record is None:
            raise RuntimeError('unclosed attempt; compute/resume ambiguous: ' + name)
        if (record['schema'] != 1 or record['status'] != 'INTERRUPTED_STORED_ONLY'
                or record['attempt_id'] != name[len('ATTEMPT_'):-len('.json')]
                or record['attempt_sha256'] != sha(path)
                or record['stage'] != attempt['stage']
                or record['utc_start'] != attempt['utc_start']
                or record['declaration_sha256'] != attempt['declaration_sha256']
                or record['declaration_sha256'] != sha(root / 'DECLARATION.json')
                or record['cause']['kind'] != 'host_reboot'
                or record['stored_only'] is not True
                or record['executed_fights'] != 0
                or attempt['gate']['status'] != 'not_run'):
            raise RuntimeError('interruption identity/stored-only mismatch: ' + name)
        observed = timestamp(record['recorded_utc'])
        upper = timestamp(record['wall_time_upper_bound_utc'])
        started = timestamp(attempt['utc_start'])
        boot = record['boot_time_evidence']
        if (observed < started or upper < observed
                or boot['argv'] != ['/usr/sbin/sysctl', 'kern.boottime']
                or type(boot['returncode']) is not int
                or boot['available'] is not (boot['returncode'] == 0)
                or not isinstance(boot['stdout'], str) or not isinstance(boot['stderr'], str)):
            raise RuntimeError('interruption observation/boot evidence mismatch: ' + name)
        bound = (upper - started).total_seconds()
        charged = seconds(record['charged_seconds'])
        if bound < 0 or charged < bound:
            raise RuntimeError('interruption undercharges wall time: ' + name)
        total += charged
    return total


def verify_manifest():
    manifest = read(HERE / MANIFEST)
    required = REQUIRED_BINDINGS | {p.name for p in HERE.glob('INTERRUPTION_*.json')}
    if (manifest['schema'] != 1
            or manifest['scope'] != 'stored-only analysis/render recovery; no combat authorization'
            or manifest['compute_cap_s'] != 3600
            or manifest['original_delivery_commit'] != ORIGINAL_DELIVERY
            or not required <= set(manifest['hashes'])
            or not list(HERE.glob('INTERRUPTION_*.json'))):
        raise RuntimeError('recovery manifest scope mismatch')
    for name, known in manifest['hashes'].items():
        if Path(name).name != name or sha(HERE / name) != known:
            raise RuntimeError('recovery manifest drift: ' + name)
    if manifest['base_head'] != read(HERE / 'RECOVERY_V1_PRESERVATION.json')['base_head']:
        raise RuntimeError('recovery manifest base identity mismatch')
    return manifest


@contextlib.contextmanager
def stored_runtime(stage):
    """Patch ledger only inside this launcher; combat paths stay unavailable."""
    if stage not in STORED_STAGES:
        raise RuntimeError('stored-only stage required')
    import common
    import run
    original_spent, original_execute = common.spent, run.execute
    def no_combat(*args, **kwargs):
        raise RuntimeError('combat forbidden in analysis recovery')
    common.spent = lambda: spent(HERE, stage)
    run.execute = no_combat
    try:
        yield
    finally:
        common.spent, run.execute = original_spent, original_execute


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('analyze', 'render', 'ledger'))
    parser.add_argument('stage', choices=('validate',))
    args = parser.parse_args()
    verify_manifest()
    import common
    common.pins()  # Verify every ORIGINAL sealed hash; no replacement exemptions.
    prior = spent()
    print(json.dumps({'prior_seconds': prior, 'cap_seconds': 3600,
                      'remaining_seconds': max(0, 3600 - prior), 'stored_only': True}), flush=True)
    if args.command == 'ledger':
        return
    if prior >= 3600:
        raise TimeoutError('cumulative 3600 s cap exhausted; no analysis/render started')
    stage = args.command + '_validate'
    original_argv = sys.argv[:]
    try:
        with stored_runtime(stage):
            sys.argv = [str(HERE / (args.command + '.py')), 'validate']
            runpy.run_path(sys.argv[0], run_name='__main__')
    finally:
        sys.argv = original_argv


if __name__ == '__main__':
    main()
