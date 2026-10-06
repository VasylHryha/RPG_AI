"""One owner-approved fixture execution; immutable integration, no reruns."""
import ctypes
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
BASE = '855d9310fbae5c71fa9d507d288372b17858a88c'
APPROVAL = 'docs/decisions/0030-0h-rev6-fixture-run.md'
AREA = 'evidence/tactical_composition_demo/growing_shapes'
PROVENANCE = 'Assisted-by: Codex:GPT-6'


def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


class Timebase(ctypes.Structure):
    _fields_ = [('numer', ctypes.c_uint32), ('denom', ctypes.c_uint32)]


lib = ctypes.CDLL('/usr/lib/libSystem.B.dylib')
lib.mach_absolute_time.restype = ctypes.c_uint64
lib.mach_continuous_time.restype = ctypes.c_uint64
tb = Timebase()
assert lib.mach_timebase_info(ctypes.byref(tb)) == 0
factor = tb.numer/tb.denom/1e9


def stamp():
    return dict(utc=utc(), awake_ns=int(lib.mach_absolute_time()*tb.numer/tb.denom),
                continuous_ns=int(lib.mach_continuous_time()*tb.numer/tb.denom))


def timing(start, end):
    elapsed = (datetime.fromisoformat(end['utc'])-datetime.fromisoformat(start['utc'])).total_seconds()
    return dict(start_utc=start['utc'], end_utc=end['utc'], elapsed_utc_seconds=elapsed,
                awake_seconds=(end['awake_ns']-start['awake_ns'])/1e9,
                continuous_seconds=(end['continuous_ns']-start['continuous_ns'])/1e9)


def small_raw(name, row):
    data = (json.dumps(row, separators=(',', ':'), allow_nan=False)+'\n').encode()
    path = OUT/(name+'.json.gz')
    with gzip.open(path, 'xb') as stream:
        stream.write(data)
    return dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                sha256=digest(path.read_bytes()), decoded_bytes=len(data),
                decoded_sha256=digest(data))


def main():
    # Exclusive claim prevents a second execution of the granted entropy.
    with (OUT/'EXECUTION_CLAIM.json').open('x') as stream:
        json.dump(dict(created_utc=utc(), integration_commit=BASE, approval=APPROVAL,
                       provenance=PROVENANCE), stream, indent=2)
        stream.write('\n')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    pin_path = f'{AREA}/runner/REV65_SOURCE_IDENTITY.json'
    pin = json.loads((ROOT/pin_path).read_text())
    checks = []
    # Native images are ignored build products, verified against the committed pin.
    for name, expected in {**pin['sha256'], pin_path:digest((ROOT/pin_path).read_bytes())}.items():
        path = ROOT/name
        actual = digest(path.read_bytes()) if path.is_file() else None
        committed = subprocess.run(['git', 'show', f'{BASE}:{name}'], cwd=ROOT, capture_output=True)
        recorded = digest(committed.stdout) if committed.returncode == 0 else None
        checks.append(dict(path=name, expected_sha256=expected, actual_sha256=actual,
                           integration_commit_sha256=recorded,
                           match=actual == expected and (recorded is None or recorded == expected)))
    # Explicitly require the identity record itself to match the integration commit.
    good = all(row['match'] for row in checks) and checks[-1]['integration_commit_sha256'] == checks[-1]['actual_sha256']
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, head], cwd=ROOT, check=True)
    write('COMMIT_IDENTITY.json', dict(status='MATCH' if good else 'INVALID', integration_commit=BASE,
          approval_head=head, head_changes_since_integration=subprocess.check_output(
              ['git', 'diff', '--name-only', BASE, head], cwd=ROOT, text=True).splitlines(), checks=checks))
    if not good:
        write('RUN_RECEIPT.json', dict(verdict='INVALID', reason='start identity mismatch', results={},
              not_run=[f'F{i}' for i in range(1,10)], provenance=PROVENANCE))
        return
    from evidence.tactical_composition_demo.growing_shapes.runner.rev6_execution import Execution
    from evidence.tactical_composition_demo.growing_shapes.runner.rev6_fixtures import Harness, finite_record
    from evidence.tactical_composition_demo.growing_shapes.runner.rev6_protocol import stops
    grant = Execution(owner_revision=True, owner_fixtures=True, engines_ready_reviewed=True,
                      integration_tested_reviewed=True, source_units_endpoints_ready=True,
                      approval_reference=APPROVAL)
    identity = grant.start('fixtures')
    write('START_IDENTITY.json', identity)
    inventory_path = ROOT/AREA/'runner/REV6_SEED_INVENTORY.json'
    write('PRE_EXECUTION_SEED_INVENTORY.json', json.loads(inventory_path.read_text()))
    harness = Harness(grant, backend='native')
    harness.identity_snapshot = identity
    results = {}
    costs = {}
    traces = {}
    order = [f'F{i}' for i in range(1,10)]
    begin = stamp()
    try:
        for name in order:
            if name == 'F5' and any(results[n]['verdict']=='FAIL' for n in order[:4]):
                print('STOP: F1-F4 failure blocks F5 and dependent fixture sequence', flush=True)
                break
            print(f'{utc()} START {name}', flush=True)
            started = stamp()
            try:
                row = finite_record(getattr(harness, name)())
            except Exception as error:
                row = dict(verdict='INVALID', reason=f'{type(error).__name__}: {error}',
                           traceback=traceback.format_exc())
            ended = stamp()
            costs[name] = timing(started, ended)
            traces[name] = small_raw(name, row)
            results[name] = dict(verdict=row['verdict'], raw=traces[name])
            write(name+'_TIMING.json', costs[name])
            print(f"{ended['utc']} END {name} {row['verdict']} {costs[name]['awake_seconds']:.3f}s awake", flush=True)
            if name == 'F5' and harness.intact:
                write('F5_I_RUN_STAGE_COSTS.json', dict(timing=harness.intact.timing,
                      exposure=harness.intact.exposure, note='inside the authorized fixture only'))
                traces['F5_I_GROWTH_DIAGNOSTICS'] = small_raw('F5_I_GROWTH_DIAGNOSTICS',
                       dict(diagnostics=list(harness.intact.medium.diagnostics),
                            counts=harness.intact.growth_counts))
            if row['verdict']=='INVALID':
                break
        flags = dict(fixture_invalid=any(r['verdict']=='INVALID' for r in results.values()),
                     F1_F4_failed=any(results.get(n,{}).get('verdict')=='FAIL' for n in order[:4]),
                     F5_failed=results.get('F5',{}).get('verdict')=='FAIL',
                     F7_unmatched=results.get('F7',{}).get('verdict')=='FAIL')
        verdict = 'INVALID' if flags['fixture_invalid'] else 'FIXTURES_FAIL' if any(r['verdict']=='FAIL' for r in results.values()) else 'FIXTURES_PASS' if len(results)==9 else 'INVALID'
        write('RUN_RECEIPT.json', dict(verdict=verdict, integration_commit=BASE, execution_head=head,
              approval=identity['approval_record'], results=results, timings=costs, traces=traces,
              flags=flags, stops=stops(flags), not_run=[n for n in order if n not in results],
              total=timing(begin, stamp()), clock_methods=dict(awake='mach_absolute_time, excludes sleep',
              elapsed='UTC timestamps', continuous='mach_continuous_time, includes sleep'),
              calibration=harness.calibration, provenance=PROVENANCE))
    finally:
        harness.close()


if __name__ == '__main__':
    main()
