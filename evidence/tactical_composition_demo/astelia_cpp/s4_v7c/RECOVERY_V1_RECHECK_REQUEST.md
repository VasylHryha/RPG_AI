Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

You are independent Claude reviewer. Report findings, never numeric scores. Read-only review; no tools or commands needed. Owner task: immutable interrupted analysis receipt recovery, stored data only/no fights; preserve original seal, no PLAN_CURRENT/DESIGN edits, conservative charge, tests, auditable new manifest. Full source/docs follow. No tests have run yet; findings will be fixed before one final test batch. Check actual budget accounting, fail-closed combat refusal, narrow versioned runtime override, safety of imports, additive sealing, preservation. Original common/run/analyze/render unchanged. Return APPROVE or CHANGES_REQUIRED and concrete findings.

FILE analysis_recovery_v1.py
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
        bound = (timestamp(record['wall_time_upper_bound_utc']) - timestamp(attempt['utc_start'])).total_seconds()
        charged = seconds(record['charged_seconds'])
        if bound < 0 or charged < bound:
            raise RuntimeError('interruption undercharges wall time: ' + name)
        total += charged
    return total


def verify_manifest():
    manifest = read(HERE / MANIFEST)
    if manifest['schema'] != 1 or manifest['scope'] != 'stored-only analysis/render recovery; no combat authorization':
        raise RuntimeError('recovery manifest scope mismatch')
    for name, known in manifest['hashes'].items():
        if Path(name).name != name or sha(HERE / name) != known:
            raise RuntimeError('recovery manifest drift: ' + name)
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


FILE test_analysis_recovery_v1.py
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
                  wall_time_upper_bound_utc='2026-10-07T18:08:31Z', charged_seconds=charged)
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
]):
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


FILE verify_analysis_recovery_v1.py
"""Read-only supplemental seal and byte/mtime preservation audit; no raw parsing."""
from analysis_recovery_v1 import HERE, read, sha, verify_manifest, spent
import hashlib
import json
import subprocess


def verify():
    manifest = verify_manifest()
    import common
    common.pins()
    baseline = read(HERE / 'RECOVERY_V1_PRESERVATION.json')
    for name, expected in baseline['original_files'].items():
        path = HERE / name
        if not path.is_file() or sha(path) != expected['sha256'] or path.stat().st_size != expected['bytes'] or path.stat().st_mtime_ns != expected['mtime_ns']:
            raise RuntimeError('original artifact changed: ' + name)
    for name, expected in baseline['protected'].items():
        path = common.REPO / name
        if sha(path) != expected['sha256'] or path.stat().st_mtime_ns != expected['mtime_ns']:
            raise RuntimeError('protected document changed: ' + name)
    staged = subprocess.check_output(['git', 'diff', '--cached', '--binary', '--', 'docs/PLAN_CURRENT.md'], cwd=common.REPO)
    if hashlib.sha256(staged).hexdigest() != baseline['plan_staged_diff_sha256']:
        raise RuntimeError('plan staging changed')
    total = spent()
    result = dict(status='PASS',original_artifacts_verified=len(baseline['original_files']),
                  sealed_original_hashes_verified=True,protected_bytes_mtimes_and_plan_staging_unchanged=True,
                  cumulative_seconds=total,cap_seconds=3600,remaining_seconds=max(0,3600-total),
                  executed_fights=0,analysis_started=False,render_started=False,
                  recovery_manifest_sha256=sha(HERE/'ANALYSIS_RECOVERY_V1_MANIFEST.json'))
    print(json.dumps(result,indent=2))
    return result


if __name__ == '__main__':
    verify()


FILE ANALYSIS_RECOVERY_V1.md
# Stored-only interruption recovery v1

Owner-authorized recovery of `ATTEMPT_eb681c6dfe8240248636f44adbcd5a4d.json`, stage `analyze_validate`, started `2026-10-07T18:06:31Z`. The owner reports reboot at approximately 21:51 local / 18:51Z because another session froze the laptop. The RUNNING receipt is preserved, never closed or rewritten.

`INTERRUPTION_95d7e6ccbe1043eda90e3b0ea8fe7055.json` binds its exact bytes, stage, start time, declaration, cause and stored-only provenance. `sysctl kern.boottime` was attempted and denied; its command, return code and error are retained. The charge is the entire elapsed wall time until the recovery observation: **3377.771384 s**, including downtime. The approximate owner reboot time is not treated as an exact timestamp or used to discount compute. Added to the closed validation attempt's **227.16235725 s**, cumulative compute is **3604.93374125 s**. No allowance is reset or clipped. The 3600 s cap is exhausted, so neither analysis nor rendering is started. No fight executed during this recovery.

The versioned launcher `analysis_recovery_v1.py` is the only runtime change. It runs the unchanged `analyze.py`/`render.py` entry points with a temporary replacement for `common.spent`, only within a stored-only launch. Every unclosed attempt needs one identity-matching interruption record for exactly `analyze_validate` or `render_validate`. Unclosed combat/unknown stages, missing records, duplicate/orphan records, changed receipts, nonfinite/negative charges and undercharges fail closed. `run.execute` is disabled during the launch; changes are restored on exit. Direct original commands keep refusing the unclosed attempt, including `run.py validate`. There is no combat recovery entry point.

Analysis imports `common`, `protocol`, read-only helpers from `run`, and the observation-only `s4_escort_probe_v3/metrics.py`. `run` defines combat code but its main invocation is guarded by `if __name__ == '__main__'`; importing it executes no fight. Analysis calls stored receipt/hash/telemetry readers and unchanged scientific functions. Rendering reads stored analysis and emits HTML. Neither stored entry point calls `execute`, `Executor`, or the native host. The existing `attempt` context and absolute deadline/cumulative cap remain authoritative.

`ANALYSIS_RECOVERY_V1_MANIFEST.json` is an additive post-validation analysis-recovery seal. It binds the new implementation, tests, interruption and preservation snapshot, plus the ORIGINAL declaration/seal and entry points. This uses the owner's explicit versioned-analysis-recovery exception; it does not reseal validation, replace historical hashes, allocate entropy, change requests or authorize fresh validation. No existing s4_v7c file is edited. All validation fights, raw traces/claims/completions, theta*, entropy, native sources/binary, protocol/readings and original evidence are untouched. `RECOVERY_V1_PRESERVATION.json` records hashes, sizes and mtimes of 2186 original artifacts and both protected documents; the read-only verifier checks them alongside all original seal pins and PLAN staging.

Audit commands from repository root:

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/analysis_recovery_v1.py ledger validate
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/verify_analysis_recovery_v1.py
```

Versioned stored entry points (currently refuse because the cumulative cap is exhausted; do not reset it):

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/analysis_recovery_v1.py analyze validate
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/analysis_recovery_v1.py render validate
```

| Stop condition (yes/no) | Action | Responsible role |
|---|---|---|
| Does any unclosed attempt lack a valid stored-only interruption? | Refuse further attempts | implementer |
| Is any unclosed combat attempt present? | Preserve and refuse recovery | implementer |
| Does any original/supplemental seal or preservation check fail? | Stop and investigate without editing historical evidence | implementer |
| Is cumulative compute at least 3600 s? | Stop without starting analysis/render or creating an attempt | executor |
| Is an exact reboot bound unavailable? | Charge through recovery observation, including downtime | implementer |

The owner recheck and disposition live in new `RECOVERY_V1_OWNER_RECHECK.md`, because this task explicitly forbids editing `docs/PLAN_CURRENT.md`. No scientific acceptance or S5 authorization is claimed.


FILE ANALYSIS_RECOVERY_V1_MANIFEST.json
{
  "schema": 1,
  "scope": "stored-only analysis/render recovery; no combat authorization",
  "created_utc": "2026-10-07T19:05:48.542666+00:00",
  "base_head": "6bf50d0d3059a2edb588b5e75729b8cdecefbf96",
  "original_delivery_commit": "f31583b2e9aa3a89aad901a1123b299810495fc2",
  "authorization": "Owner recovery request permits a versioned analysis-recovery file; original pre-validation seal stays authoritative for all original files.",
  "original_hashes_preserved": true,
  "validation_resealed": false,
  "compute_cap_s": 3600,
  "hashes": {
    "analysis_recovery_v1.py": "acd07d4bc1ed7debf200d830b5775ece5127dd6996f99bffbcea85c07941f3be",
    "test_analysis_recovery_v1.py": "25a0c34dce8769a9c6caf1ca30ec244f2a1015de808cdebeaee97a04048fcbd4",
    "verify_analysis_recovery_v1.py": "5d44f2f0f93d6b5503a6645d6ad21ec7f1fa270bf544b15dfdf849c064788143",
    "ANALYSIS_RECOVERY_V1.md": "e8a4d75bc8a04916c02d9bba3596ee26db609363548766684adc5db0df2960cc",
    "RECOVERY_V1_PRESERVATION.json": "900c9485ef123c73b636060e04920032e0160d26017726962b5c998f71e1c1c6",
    "INTERRUPTION_95d7e6ccbe1043eda90e3b0ea8fe7055.json": "3c458df2627237ff0bc7c524e85fa7aba80177753aadd517695168ebbac3675d",
    "SEAL.json": "62b1baa32b5af8616020f9127008f7d4ff0e503ce319aefa7b311079820677ff",
    "DECLARATION.json": "5d8ac75687155a47ade9476835c2d06138c83f4e1b5d684da2c500f74c2a5fa0",
    "common.py": "7574bde27ca17da3a2260ff8e511891aba6544661a5fcc23554ec0c55b36cb58",
    "run.py": "9e4db041089b0a2145be5ccc25be618a89ee30a02e687901186b46e60d92f710",
    "analyze.py": "5dc0bc0b42348b3d899c4f843ed82fcd51751d7ee3d7b9e197dcd2a2e59e06d3",
    "render.py": "bedad12e37d0b5ff4c0959af43b1e134b2d6f555b25d1d9d4b923672283dd2bf",
    "protocol.py": "c161310a75929718054df0710660e39d4b80ee81efa0d2f3ff22d6c838aa124e"
  }
}


FILE INTERRUPTION_95d7e6ccbe1043eda90e3b0ea8fe7055.json
{
  "schema": 1,
  "status": "INTERRUPTED_STORED_ONLY",
  "interruption_id": "95d7e6ccbe1043eda90e3b0ea8fe7055",
  "attempt_id": "eb681c6dfe8240248636f44adbcd5a4d",
  "attempt_file": "ATTEMPT_eb681c6dfe8240248636f44adbcd5a4d.json",
  "attempt_sha256": "0f8ba0348120c933243dd9b8bc39f1061d9155b9bda16d5246eeabfde7ac2f86",
  "stage": "analyze_validate",
  "utc_start": "2026-10-07T18:06:31Z",
  "declaration_sha256": "5d8ac75687155a47ade9476835c2d06138c83f4e1b5d684da2c500f74c2a5fa0",
  "recorded_utc": "2026-10-07T19:02:48.771384Z",
  "cause": {
    "kind": "host_reboot",
    "authority": "owner report in recovery request and current HEAD commit 36ca007",
    "reported_approximate_utc": "2026-10-07T18:51:00Z",
    "reported_approximate_local": "2026-10-07T21:51:00+03:00",
    "context": "Owner rebooted laptop because another session froze the machine; process exit was never recorded."
  },
  "boot_time_evidence": {
    "argv": [
      "/usr/sbin/sysctl",
      "kern.boottime"
    ],
    "returncode": 1,
    "stdout": "",
    "stderr": "sysctl: sysctl fmt -1 1024 1: Operation not permitted\n",
    "available": false
  },
  "wall_time_upper_bound_utc": "2026-10-07T19:02:48.771384Z",
  "charged_seconds": 3377.771384,
  "charge_basis": "Full elapsed wall time from receipt start to recovery observation; conservatively includes reboot and all subsequent downtime. No exact boot time accessible; approximate owner time is not used to discount compute. Never clamp to allowance or reset the cap.",
  "stored_only": true,
  "executed_fights": 0,
  "stored_only_evidence": {
    "entrypoint": "analyze.py validate",
    "entrypoint_sha256": "5dc0bc0b42348b3d899c4f843ed82fcd51751d7ee3d7b9e197dcd2a2e59e06d3",
    "gate": {
      "status": "not_run",
      "reason": "stored analysis; no fights"
    },
    "import_audit": "analyze imports common/protocol and read-only helpers from run; run defines combat functions but its guarded __main__ is not invoked by import; metrics.py is a pure observation oracle. Analysis entrypoint invokes only attempt/analyze/deadline.remaining. No native host, executor, or fight call."
  },
  "original_attempt_preserved": true
}


FILE common.py
"""Identity fences, immutable receipts, owned deadlines and repository process gate."""
import contextlib, hashlib, json, math, os, pathlib, re, signal, subprocess, sys, threading, time, uuid
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent;REPO=CPP.parents[2]
BINARY=HERE/'build/astelia_native_v7';sys.path.append(str(CPP))
from build_admission import admit
from s4_deadline import Deadline,BoundedPool
FORBIDDEN={'PLAN_CURRENT.md','DESIGN_0G.md','DESIGN_0H_REV7.md'}

def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def utc():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def read(p):return json.loads(pathlib.Path(p).read_text())
def write(p,v):
 p=pathlib.Path(p);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
 with tmp.open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def exclusive(p,v):
 with pathlib.Path(p).open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def pins():
 d=read(HERE/'DECLARATION.json');s=read(HERE/'SEAL.json')
 if sha(HERE/'DECLARATION.json')!=s['declaration_sha256']:raise RuntimeError('declaration drift')
 for n,h in d['hashes'].items():
  if pathlib.Path(n).name in FORBIDDEN:raise RuntimeError('forbidden mutable document pin')
  if sha(REPO/n)!=h:raise RuntimeError('input drift: '+n)
 if admit(BINARY)!=d['binary']:raise RuntimeError('binary drift')
 return d

def caffeinate():
 if os.environ.get('S4_V7_CAFFEINATED')!='1':
  os.environ['S4_V7_CAFFEINATED']='1';os.execv('/usr/bin/caffeinate',['caffeinate','-i','-s',sys.executable,*sys.argv])

def process_pattern():
 # Anchor the EXECUTABLE, so a concurrent pgrep containing this pattern cannot match.
 root=re.escape(str(REPO))
 py=r'([^[:space:]]*/)?[Pp]ython[0-9.]*[[:space:]]+'
 location=r'('+root+r'/|\./?evidence/tactical_composition_demo/|evidence/tactical_composition_demo/)'
 rootedpy=root+r'/\.venv/bin/[Pp]ython[0-9.]*([[:space:]]|$)'
 relativepy=r'(\./)?\.venv/bin/[Pp]ython[0-9.]*([[:space:]]|$)'
 native=location+r'[^[:space:]]*astelia_native[^[:space:]]*([[:space:]]|$)'
 return r'^('+rootedpy+r'|'+relativepy+r'|'+py+r'([^[:space:]]+[[:space:]]+)*'+location+r'[^[:space:]]*|'+native+r')'

def process_gate(wait=True):
 path=HERE/('GATE_'+uuid.uuid4().hex+'.json');attempts=[];start=time.monotonic()
 while True:
  argv=['pgrep','-fl',process_pattern()]
  try:
   p=subprocess.run(argv,text=True,capture_output=True,timeout=10)
   active=[]
   if p.returncode==0 and not p.stdout.strip():raise ValueError('pgrep zero with empty output')
   if p.returncode==0 and not p.stderr.strip():
    for line in p.stdout.splitlines():
     pieces=line.split(None,1)
     if len(pieces)!=2 or not pieces[0].isdigit():raise ValueError('unparseable pgrep output')
     if int(pieces[0])!=os.getpid():active.append(line)
   status='CLEAR' if p.returncode==1 and not p.stderr.strip() or p.returncode==0 and not p.stderr.strip() and not active else 'ACTIVE' if p.returncode==0 and not p.stderr.strip() else 'UNAVAILABLE'
   row=dict(utc=utc(),argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,active=active)
  except (OSError,subprocess.TimeoutExpired,ValueError) as e:status='UNAVAILABLE';row=dict(utc=utc(),argv=argv,error=str(e))
  attempts.append(row);write(path,dict(status=status,attempts=attempts,wait_wall_seconds=time.monotonic()-start,declaration_sha256=sha(HERE/'DECLARATION.json'),binary=admit(BINARY)))
  if status=='CLEAR':return dict(path=path.name,sha256=sha(path))
  if status=='UNAVAILABLE':raise RuntimeError('mandatory process gate unavailable; STOP before fights')
  if not wait:raise RuntimeError('repository python/native work active; STOP before fights')
  print('Waiting for repository work, including 0h rev711_diag/medium_variants batches; next check in 30 s',flush=True);time.sleep(30)

def spent():
 total=0 # Validation alone owns this version budget; no inherited tuning/engineering charge.
 for p in HERE.glob('ATTEMPT_*.json'):
  r=read(p)
  if r['status']=='RUNNING':raise RuntimeError('unclosed attempt; compute/resume ambiguous: '+p.name)
  total+=r['seconds']
 return total

@contextlib.contextmanager
def attempt(stage,gate):
 prior=spent();remaining=3600-prior
 if remaining<=0:raise TimeoutError('cumulative 3600 s cap exhausted')
 start=time.monotonic();path=HERE/('ATTEMPT_'+uuid.uuid4().hex+'.json')
 initial=dict(stage=stage,status='RUNNING',utc_start=utc(),prior_seconds=prior,allowance_seconds=remaining,gate=gate,declaration_sha256=sha(HERE/'DECLARATION.json'),binary=admit(BINARY))
 exclusive(path,initial);dl=Deadline(start+remaining);timer=threading.Timer(remaining,dl.stop);timer.daemon=True;timer.start();error=None
 def expired(*_):raise TimeoutError('cumulative 3600 s cap')
 previous=signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,remaining)
 try:yield dl,prior,start
 except BaseException as e:error=type(e).__name__+': '+str(e);raise
 finally:
  signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous);timer.cancel();dl.stop();write(path,dict(initial,status='STOP' if error else 'PASS',error=error,seconds=time.monotonic()-start,utc_end=utc()))

def projection_warmup(stage_batches):
 if type(stage_batches) is not int or stage_batches<1:raise ValueError('positive stage batch allocation required')
 return min(10,math.ceil(stage_batches*.05))

def project(prior,start,done,total,batches,stage_batches):
 elapsed=time.monotonic()-start
 if not all(math.isfinite(x) for x in (prior,elapsed)) or prior<0 or elapsed<=0:raise ValueError('invalid projection time')
 if any(type(x) is not int for x in (done,total,batches)) or not 0<batches<=stage_batches or not batches<=done<=total:raise ValueError('invalid projection completion count')
 threshold=projection_warmup(stage_batches)
 # Counts include every worker completion in this attempt, never cached fights.
 # The rate is already aggregate wall throughput; do not multiply by workers.
 ready=batches>=threshold
 rate=done/elapsed if ready else None
 projected=prior+elapsed+(total-done)/rate+120 if ready else None
 write(HERE/'PROJECTION.json',dict(status='PROJECTED' if ready else 'WARMUP',projected_seconds=projected,cap_seconds=3600,prior_seconds=prior,elapsed_wall_seconds=elapsed,completed_this_attempt=done,completed_batches_this_attempt=batches,stage_batches_remaining_at_start=stage_batches,warmup_batches=threshold,completed_fights_per_wall_second=rate,total_remaining_at_start=total,analysis_reserve_s=120))
 if prior+elapsed>=3600:raise TimeoutError('cumulative 3600 s cap exhausted')
 if ready and projected>3600:raise TimeoutError('projected compute exceeds 3600 s; preserve completions')

ORIGIN_COMMIT='796d0a8c43e5f81533b0b363d856d6a44e33413e'
ORIGIN=CPP/'s4_v7b'
VALIDATION_FIGHTS=400

def tuning_hash():return sha(ORIGIN/'TUNING.json')

def inherited_tuning():
 origin=read(HERE/'THETA_ORIGIN.json')
 if origin['commit']!=ORIGIN_COMMIT:raise RuntimeError('theta origin commit drift')
 if set(origin['hashes'])!={'TUNING.json','TUNING_ANALYSIS.json','DECLARATION.json'}:raise RuntimeError('theta origin hash allocation drift')
 for name,known in origin['hashes'].items():
  path=ORIGIN/name
  if sha(path)!=known:raise RuntimeError('committed tuning input drift: '+name)
  blob=subprocess.check_output(['git','show',ORIGIN_COMMIT+':'+str(path.relative_to(REPO))],cwd=REPO)
  if hashlib.sha256(blob).hexdigest()!=known:raise RuntimeError('theta input not committed at origin: '+name)
 t=read(ORIGIN/'TUNING.json');a=read(ORIGIN/'TUNING_ANALYSIS.json')
 if t['status']!='SELECTED' or a['status']!='SELECTED' or t['evaluations']!=257 or t['accounted_fights']!=8224 or a['validation_used'] is not False or a['tuning_sha256']!=tuning_hash():raise RuntimeError('incomplete/inconsistent committed tuning')
 if t['selected']!=a['selected'] or t['selected_params']!=a['selected_params'] or t['selected_params']!=t['selected']['params'] or t['selected']['ordinal']!=161 or not t['selected']['selection']['eligible']:raise RuntimeError('theta selection drift')
 if origin['selected_params']!=t['selected_params'] or origin['ordinal']!=161:raise RuntimeError('theta origin drift')
 if origin['historical_theta']!=read(ORIGIN/'DECLARATION.json')['historical_theta']:raise RuntimeError('historical theta origin drift')
 return t

def engineering_inputs():
 paths=list(HERE.glob('*.py'))+list(HERE.glob('*.cpp'))+list(HERE.glob('*REQUEST_TEMPLATE.json'))+[HERE/'THETA_ORIGIN.json',HERE/'VALIDATION_SEED_LEDGER.json']
 paths += [CPP/'s4_deadline.py',CPP/'build_admission.py',CPP/'s4_v6.py',CPP/'s4_v4.py',CPP/'s4_escort_probe_v3/metrics.py']
 return {str(p.relative_to(REPO)):sha(p) for p in paths}


FILE run.py
"""Claude executor: validation only with sealed identities and no ambiguous replay."""
import argparse, gzip, threading
from common import *
from protocol import *
RAW=HERE/'raw'

def request(arm,head,seed,orientation,params,telemetry=False):
 req=read(HERE/(head.upper()+'_REQUEST_TEMPLATE.json'))
 req['options'].update(seed=seed,swapSides=bool(orientation),duration=150)
 req['options']['ai'][0].update(controller=arm,skeleton='v7',params=params)
 req.update(trace=telemetry,diagnostics=False,killerTelemetry=telemetry,decisionTrace=telemetry,decisionDiagnostics=telemetry,attributionDiagnostics=telemetry)
 return req

def verified(tag,requests=None):
 done=RAW/(tag+'_COMPLETE.json');claim=RAW/(tag+'_CLAIM.json')
 if not done.exists():
  if any(RAW.glob(tag+'_*')) or (RAW/(tag+'.jsonl.gz')).exists():raise RuntimeError('ambiguous possibly executed fight; never replay: '+tag)
  return None
 r=read(done);c=read(claim);d=pins()
 if r['meta']!=c['meta']:raise RuntimeError('completion/claim metadata drift '+tag)
 if c['declaration_sha256']!=sha(HERE/'DECLARATION.json') or c['binary']!=d['binary'] or r['claim_sha256']!=sha(claim) or r['binary']!=c['binary']:raise RuntimeError('claim/identity drift '+tag)
 req=RAW/(tag+'_request.json')
 if sha(req)!=c['request_sha256'] or sha(req)!=r['request_sha256'] or requests is not None and read(req)!=requests:raise RuntimeError('request drift '+tag)
 gate=HERE/c['gate']['path'];g=read(gate)
 if sha(gate)!=c['gate']['sha256'] or g['status']!='CLEAR' or g['declaration_sha256']!=c['declaration_sha256'] or g['binary']!=c['binary']:raise RuntimeError('process gate drift '+tag)
 for key,suffix in (('raw_sha256','.jsonl.gz'),('stderr_sha256','_stderr.log')):
  if sha(RAW/(tag+suffix))!=r[key]:raise RuntimeError('raw receipt drift '+tag)
 with gzip.open(RAW/(tag+'.jsonl.gz'),'rt') as f:
  last=None
  for line in f:last=json.loads(line)
 summaries=last if isinstance(last,list) else [last]
 if summaries!=r['summaries'] or len(summaries)!=len(read(req)):raise RuntimeError('raw/summary mismatch '+tag)
 for s in summaries:measure(s)
 metrics=read(RAW/(tag+'_stderr.log'))
 if metrics!=r['metrics'] or metrics['executed_fights']!=len(summaries) or any(metrics[k] for k in ('forks','search_calls','branch_steps','artillery_rollouts')):raise RuntimeError('unexpected engine work '+tag)
 return r

def audit_raw():
 if not RAW.exists():return
 tags=set()
 for p in RAW.iterdir():
  matched=re.fullmatch(r'(.+)(_COMPLETE\.json|_CLAIM\.json|_request\.json|_stderr\.log|_FAILURE\.json|\.jsonl\.gz)',p.name)
  if not matched:raise RuntimeError('unknown raw artifact: '+p.name)
  tags.add(matched[1])
 expected={tag:(reqs,meta) for tag,reqs,meta in validation_plan(pins())}
 for tag in sorted(tags):
  if tag not in expected:raise RuntimeError('unexpected validation cell: '+tag)
  reqs,meta=expected[tag];r=verified(tag,reqs)
  if r is not None and r['meta']!=meta:raise RuntimeError('validation cell metadata drift: '+tag)

def execute(task,deadline):
 tag,reqs,meta,gate=task
 prior=verified(tag,reqs)
 if prior:return prior
 pins();identity=admit(BINARY);deadline.remaining()
 exclusive(RAW/(tag+'_request.json'),reqs)
 claim=RAW/(tag+'_CLAIM.json');exclusive(claim,dict(meta=meta,utc_start=utc(),declaration_sha256=sha(HERE/'DECLARATION.json'),binary=identity,gate=gate,request_sha256=sha(RAW/(tag+'_request.json'))))
 child=None
 try:
  with deadline.lock:
   deadline.remaining();child=subprocess.Popen([str(BINARY),'--metrics'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True);deadline.children.add(child)
  # Validation is a singleton native request.
  payload=reqs if len(reqs)>1 else reqs[0]
  child.stdin.write((json.dumps(payload)+'\n').encode());child.stdin.close()
  errors=[]
  def drain():
   try:
    with (RAW/(tag+'_stderr.log')).open('xb') as f:
     while True:
      b=child.stderr.read(65536)
      if not b:break
      f.write(b)
   except BaseException as e:errors.append(str(e));deadline.stop()
  thread=threading.Thread(target=drain);thread.start();last=None
  path=RAW/(tag+'.jsonl.gz')
  with path.open('xb') as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',compresslevel=1,mtime=0) as raw:
   for line in child.stdout:deadline.remaining();raw.write(line);last=line
  child.wait(timeout=deadline.remaining());thread.join(timeout=deadline.remaining())
  if child.returncode or thread.is_alive() or errors:raise RuntimeError('native execution failure')
  result=json.loads(last);summaries=result if isinstance(result,list) else [result]
  if len(summaries)!=len(reqs):raise RuntimeError('native count mismatch')
  for summary in summaries:measure(summary)
  metrics=read(RAW/(tag+'_stderr.log'))
  if metrics['executed_fights']!=len(reqs) or any(metrics[k] for k in ('forks','search_calls','branch_steps','artillery_rollouts')):raise RuntimeError('unexpected native work')
  deadline.remaining();pins()
  record=dict(tag=tag,meta=meta,binary=identity,summaries=summaries,metrics=metrics,claim_sha256=sha(claim),raw_sha256=sha(path),raw_bytes=path.stat().st_size,request_sha256=sha(RAW/(tag+'_request.json')),stderr_sha256=sha(RAW/(tag+'_stderr.log')),utc_end=utc())
  exclusive(RAW/(tag+'_COMPLETE.json'),record);return record
 except BaseException as e:
  deadline.stop()
  exclusive(RAW/(tag+'_FAILURE.json'),dict(error=type(e).__name__+': '+str(e),utc=utc(),never_replay=True))
  if child is not None:child.wait(timeout=2)
  raise
 finally:
  if child is not None:
   with deadline.lock:deadline.children.discard(child)
   for stream in (child.stdin,child.stdout,child.stderr):
    if stream:stream.close()

class Executor:
 def __init__(self,dl,gate,prior,start,total,stage_batches):
  self.dl=dl;self.gate=gate;self.prior=prior;self.start=start;self.total=total;self.done=0;self.batches=0;self.stage_batches=stage_batches;self.completion_lock=threading.Lock();self.pool=BoundedPool(10,dl)
 def completed(self,task,deadline):
  row=execute(task,deadline)
  with self.completion_lock:self.done+=len(row['summaries']);self.batches+=1
  return row
 def tasks(self,tasks):
  for row in self.pool.map(self.completed,tasks):
   with self.completion_lock:done,batches=self.done,self.batches
   project(self.prior,self.start,done,self.total,batches,self.stage_batches);yield row
 def close(self):self.pool.close()

def tuning_receipt():
 pins();return inherited_tuning()

def validation_plan(d):
 t=inherited_tuning();ledger=read(HERE/'VALIDATION_SEED_LEDGER.json')
 if len(ledger['validation'])!=20 or len(set(ledger['validation']))!=20:raise RuntimeError('validation seed allocation')
 for arm in ARMS:
  params=d['historical_theta'] if arm=='historicalP16' else t['selected_params']
  for h in HEADS:
   for c,s in enumerate(ledger['validation']):
    for o in (0,1):
     tag=f'validation_{arm}_{h}_c{c:02d}_o{o}';reqs=[request(arm,h,s,o,params,True)]
     yield tag,reqs,dict(stage='validation',arm=arm,head=h,cluster=c,orientation=o)

def validation(executor):
 d=pins();t=tuning_receipt();records=[];tasks=[]
 for tag,reqs,meta in validation_plan(d):
  prior=verified(tag,reqs)
  if prior:records.append(prior)
  else:tasks.append((tag,reqs,meta,executor.gate))
 records+=list(executor.tasks(tasks))
 if len(records)!=400:raise RuntimeError('validation allocation mismatch')
 result=validation_result(records)
 if (HERE/'VALIDATION.json').exists():
  if read(HERE/'VALIDATION.json')!=result:raise RuntimeError('validation receipt drift')
 else:exclusive(HERE/'VALIDATION.json',result)
 return result

def validation_result(records):
 t=tuning_receipt()
 return dict(status='COMPLETE',fights=400,tuning_sha256=tuning_hash(),selected_params=t['selected_params'],omega0_duplicate=t['selected_params']['omega_ranged']==0,records={r['tag']:sha(RAW/(r['tag']+'_COMPLETE.json')) for r in records},declaration_sha256=sha(HERE/'DECLARATION.json'))

def validation_receipt():
 # Caller owns an attempt or has called spent() before entering this read-only check.
 d=pins();audit_raw();records=[]
 for tag,requests,meta in validation_plan(d):
  r=verified(tag,requests)
  if r is None or r['meta']!=meta:raise RuntimeError('validation completion missing/cell drift: '+tag)
  records.append(r)
 if len(records)!=400:raise RuntimeError('validation allocation mismatch')
 expected=validation_result(records)
 if read(HERE/'VALIDATION.json')!=expected:raise RuntimeError('validation receipt drift')
 return expected

def main():
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=('validate',));args=parser.parse_args()
 d=pins();spent();engineering=read(HERE/'ENGINEERING.json')
 if sha(HERE/'ENGINEERING.json')!=d['engineering_sha256'] or engineering['binary']!=admit(BINARY):raise RuntimeError('engineering receipt drift')
 RAW.mkdir(exist_ok=True);audit_raw()
 # Already completed stages verify through reconstruction; they need no process gate or fights.
 if args.stage=='validate':tuning_receipt()
 complete=sum(len(read(p)['summaries']) for p in RAW.glob('*_COMPLETE.json'))
 if args.stage=='validate' and (HERE/'VALIDATION.json').exists():
  validation_receipt()
  print('Validation completion verified; no fights');return
 estimate=spent()+(VALIDATION_FIGHTS-complete)*.062+120
 write(HERE/'PROJECTION_BEFORE_FIGHTS.json',dict(projected_seconds=estimate,cap_seconds=3600,remaining_fights=VALIDATION_FIGHTS-complete,inherited_conservative_seconds_per_fight=.062,analysis_reserve_s=120))
 if estimate>3600:raise TimeoutError('pre-fight projection exceeds 3600 s')
 gate=process_gate(wait=True)
 with attempt(args.stage,gate) as (dl,prior,start):
  stage_name='validation'
  stage_done=sum(len(read(p)['summaries']) for p in RAW.glob('*_COMPLETE.json') if read(p)['meta']['stage']==stage_name)
  stage_batches=400-stage_done
  executor=Executor(dl,gate,prior,start,VALIDATION_FIGHTS-complete,stage_batches)
  try:validation(executor)
  finally:executor.close()
if __name__=='__main__':caffeinate();main()


FILE analyze.py
"""Hash-verified stored analysis; descriptive clustered readings, never executes fights."""
import collections,gzip,importlib.util,math,statistics
from common import *
from protocol import *
from run import RAW,verified,audit_raw,tuning_receipt,validation_receipt
spec=importlib.util.spec_from_file_location('delivered_p16_metrics',CPP/'s4_escort_probe_v3/metrics.py')
legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)

def ratio(a,b):return a/b if b else None

def telemetry(record):
 counters=collections.Counter();combos=collections.Counter();pair_modes=collections.Counter();nearest=[];deaths=[];initial=None;post=None;last_step=0;shells=legacy.ShellAudit();firing=collections.Counter()
 with gzip.open(RAW/(record['tag']+'.jsonl.gz'),'rt') as f:
  for line in f:
   r=json.loads(line)
   if r.get('observerV1'):
    post=r;shells.observe(r)
    if r['step']==0:initial={u[0]:u for u in r['units']}
    for d in r['damage']:
     if d['died']:deaths.append(d)
     if d['died'] and d['sourceTeam']==0 and d['sourceRole']=='artillery' and d['targetTeam']==1 and d['targetRole']=='ranged':counters['artillery_enemy_ranged_kills_lt20']+=int(d['t']<20);counters['artillery_enemy_ranged_kills_lt30']+=int(d['t']<30)
    for launch in r['launches']:
     if launch[2]==0:firing[str(launch[1])]+=1
    guns=[u for u in r['units'] if u[1]==0 and u[2]==2]
    for g in guns:
     other=[u for u in guns if u[0]!=g[0]]
     if other:nearest.append(min(legacy.distance(g,u) for u in other))
    continue
   if r.get('decisionDiagnostics'):
    if r['side']==0:
     for u in r['units']:
      for p in u['pairs']:pair_modes[p['mode']]+=1
    continue
   if not r.get('v7Telemetry'):continue
   if not post or r['step']!=post['step'] or r['step']!=last_step+1 or not r['accepted']:raise RuntimeError('telemetry sequence/integration failure')
   last_step=r['step'];before={u[0]:u for u in r['prepare'] if u[5]>0};actual={u[0]:u for u in post['units']}
   choices={q['id']:q for q in r['choices']};arm=record['meta']['arm']
   expected_own={u[0] for u in before.values() if u[1]==0}
   if arm!='historicalP16' and set(choices)!=expected_own:raise RuntimeError('missing per-unit source telemetry')
   for q in choices.values():
    if arm in ('v7','omega0') and (q['source']=='P16')!=(q['mode']=='commit'):raise RuntimeError('gate/source mismatch')
    if q['source'] not in ('P16','v6') or q['command']!=(q['p16'] if q['source']=='P16' else q['baseline']):raise RuntimeError('selected source mismatch')
    if arm=='forcedP16' and q['source']!='P16' or arm=='forcedv6' and q['source']!='v6':raise RuntimeError('forced selector mismatch')
    counters['selected_'+q['source']+'_unit_ticks']+=1;counters['gate_transitions']+=q['transition'];counters['target_differs_between_sources_ticks']+=q['p16'][4]!=q['baseline'][4]
    if before[q['id']][2]==0 and q['p16']!=q['baseline']:raise RuntimeError('melee changed')
   own=[u for u in before.values() if u[1]==0 and u[2]==2];enemy=[u for u in before.values() if u[1]==1 and u[2]==2];ranged=[u for u in before.values() if u[1]==1 and u[2]==1]
   width,height=r['width'],r['height'];oracle=legacy.gun_focus_oracle(list(before.values()),width,height,True)
   if {g['id'] for g in r['guns']}!=set(oracle):raise RuntimeError('missing gun geometry telemetry')
   for g in r['guns']:
    q=oracle[g['id']];command=g['command'];expected=q['command']
    if any(abs(command[i]-expected[i])>1e-7 for i in range(4)):raise RuntimeError('P16 geometry oracle mismatch')
    if g['focus']!=q['focus'] or g['anchor']!=q['anchor'] or q['target'] is not None and command[4]!=q['target']:raise RuntimeError('P16 focus oracle mismatch')
    chosen=command[4] if arm=='historicalP16' else choices[g['id']]['command'][4]
    counters['gun_focus_ticks']+=1
    if chosen in q['values_by_gun']:counters['gun_target_V_sum']+=q['values_by_gun'][chosen];counters['gun_target_V_ticks']+=1
    selected=arm=='historicalP16' or choices[g['id']]['source']=='P16'
    if not selected:continue
    if chosen in q['values_by_gun']:counters['P16_selected_target_V_sum']+=q['values_by_gun'][chosen];counters['P16_selected_target_V_ticks']+=1
    focus=before[g['focus']];radial=lambda xy:math.hypot(xy[0]-focus[3],xy[1]-focus[4])
    counters['selected_gun_post_ticks']+=1
    counters['raw_goal_outside_band_ticks']+=not g['minimum']<=radial(g['raw'])<=g['range']
    counters['clipped_goal_outside_band_ticks']+=not g['minimum']<=radial(g['clipped'])<=g['range']
    counters['post_arrival_prepare_ticks']+=math.hypot(before[g['id']][3]-g['clipped'][0],before[g['id']][4]-g['clipped'][1])<=20
    u=actual.get(g['id']);counters['post_surviving_gun_ticks']+=u is not None
    post_focus=actual.get(g['focus'])
    if u is not None and post_focus is not None:
     counters['post_alive_gun_and_focus_ticks']+=1
     counters['actual_in_focus_band_ticks']+=u[8]<=legacy.distance(u,post_focus)<=u[7]
   for p in r['escorts']:
    u=before[p['id']];q=legacy.point_for(u,own,enemy,ranged,60,width,height)
    if p['gun']!=q['gun'] or p['direction']!=q['direction']:raise RuntimeError('escort assignment oracle mismatch')
    if not p['direction']:counters['escort_degenerate_ticks']+=1;continue
    if any(abs(a-b)>1e-7 for a,b in zip(p['clipped'],q['clipped'])):raise RuntimeError('escort point oracle mismatch')
    source='P16' if arm=='historicalP16' else choices[p['id']]['source'];gun_source='P16' if arm=='historicalP16' else choices[p['gun']]['source']
    combos[source+'_escort__'+gun_source+'_gun']+=1
    if source=='P16':
     counters['selected_escort_ticks']+=1
     after=actual.get(p['id']);counters['escort_surviving_ticks']+=after is not None
     if after is not None:counters['escort_arrival_post_ticks']+=math.hypot(after[3]-p['clipped'][0],after[4]-p['clipped'][1])<=20
 if initial is None or last_step==0:raise RuntimeError('missing validation telemetry')
 own_deaths=[d for d in deaths if d['targetTeam']==0 and d['targetRole']=='artillery']
 curve=legacy.gun_curve(initial,own_deaths)
 shellcounts=collections.Counter()
 for s in shells.shells:
  if s['target_team']==s['side'] or s['target_role']!=2:continue
  prefix='own' if s['side']==0 else 'enemy';success=bool(s['opposing'][2])
  shellcounts[prefix+'_gun_damage_successful_shells']+=success
  shellcounts[prefix+'_gun_victims']+=len(s['opposing'][2])
 return dict(in_band_denominator='P16-selected gun ticks with gun and focus both alive after the step; both centres from post snapshot',counts=dict(counters),escort_gun_source_combinations=dict(combos),pair_mode_ticks=dict(pair_modes),gun_survival=curve,chosen_target_V=ratio(counters['gun_target_V_sum'],counters['gun_target_V_ticks']),P16_selected_chosen_target_V=ratio(counters['P16_selected_target_V_sum'],counters['P16_selected_target_V_ticks']),escort_arrival_fraction=ratio(counters['escort_arrival_post_ticks'],counters['selected_escort_ticks']),post_arrival_fraction=ratio(counters['post_arrival_prepare_ticks'],counters['selected_gun_post_ticks']),actual_in_focus_band_fraction=ratio(counters['actual_in_focus_band_ticks'],counters['post_alive_gun_and_focus_ticks']),nearest_own_gun_distance=dict(samples=len(nearest),median=statistics.median(nearest) if nearest else None,p10=sorted(nearest)[int(.1*(len(nearest)-1))] if nearest else None),shell_counts=dict(shellcounts),gun_victims_per_gun_damaging_shell={s:ratio(shellcounts[s+'_gun_victims'],shellcounts[s+'_gun_damage_successful_shells']) for s in ('own','enemy')},inherited_shell_summary=legacy.shell_summary(shells.counts()),firing_targets=dict(firing),complex_diagnostics=record['summaries'][0]['complexDiagnostics'])

def analyze():
 d=pins();t=tuning_receipt();audit_raw();v=validation_receipt()
 if v['fights']!=400 or len(v['records'])!=400 or v['tuning_sha256']!=tuning_hash() or v['declaration_sha256']!=sha(HERE/'DECLARATION.json'):raise RuntimeError('validation seal mismatch')
 per=[]
 for tag,h in v['records'].items():
  if sha(RAW/(tag+'_COMPLETE.json'))!=h:raise RuntimeError('validation record drift')
  r=verified(tag);per.append(dict(tag=tag,**r['meta'],**measure(r['summaries'][0]),telemetry=telemetry(r)))
 expected={(a,h,c,o) for a in ARMS for h in HEADS for c in range(20) for o in (0,1)}
 if {(r['arm'],r['head'],r['cluster'],r['orientation']) for r in per}!=expected or len(per)!=400:raise RuntimeError('validation cells')
 cells=[]
 for a in ARMS:
  for h in HEADS:
   rows=[r for r in per if (r['arm'],r['head'])==(a,h)]
   cells.append(dict(arm=a,head=h,wins=sum(r['win'] for r in rows),mean_S=statistics.mean(r['S'] for r in rows),own_losses=statistics.mean(r['losses'] for r in rows),failures=0,fights=40,timeouts=sum(r['timeout'] for r in rows),mean_termination_time=statistics.mean(r['termination_time'] for r in rows),gun_survival=[dict(t=tm,mean_alive=statistics.mean(next(x['alive'] for x in r['telemetry']['gun_survival'] if x['t']==tm) for r in rows)) for tm in (10,20,30,45,60)]))
 paired=[]
 for h in HEADS:
  for c in range(20):
   groups={a:sorted((r for r in per if (r['arm'],r['head'],r['cluster'])==(a,h,c)),key=lambda r:r['orientation']) for a in ARMS}
   paired.append(dict(head=h,cluster=c,wins={a:sum(r['win'] for r in rs) for a,rs in groups.items()},orientation_wins={a:[r['win'] for r in rs] for a,rs in groups.items()},mean_S={a:statistics.mean(r['S'] for r in rs) for a,rs in groups.items()}))
 by={(r['arm'],r['head']):r for r in cells};differences=[(r['wins']['v7']-r['wins']['forcedP16'])/2 for r in paired if r['head']=='regular']
 discord=collections.Counter()
 for r in paired:
  if r['head']=='regular':
   for a,b in zip(r['orientation_wins']['v7'],r['orientation_wins']['forcedP16']):discord[f'v7_{a}__forcedP16_{b}']+=1
 result=dict(status='ANALYZED_DEVELOPMENT_ONLY',validation_sha256=sha(HERE/'VALIDATION.json'),tuning_sha256=tuning_hash(),cells=cells,paired_clusters=paired,per_fight=per,readings=readings(by['v7','regular'],by['v7','novice'],by['forcedP16','regular']),positive_clusters=sum(d>0 for d in differences),negative_clusters=sum(d<0 for d in differences),tied_clusters=sum(d==0 for d in differences),orientation_discordance=dict(discord),paired_cluster_bootstrap=bootstrap(differences),omega0_duplicate=v['omega0_duplicate'],omega0_interpretation='Observed total effect of inherited ranged/artillery natural rate zero; gate transitions and firing target/geometry diagnostics accompany counts. No isolated gate timing inference.',not_run={'S5':'not authorized','judging':'not authorized','population_inference':'descriptive development only'})
 write(HERE/'ANALYSIS.json',result);print(json.dumps(result['readings']))
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('stage',nargs='?',default='validate',choices=('validate',));args=parser.parse_args()
 with attempt('analyze_'+args.stage,dict(status='not_run',reason='stored analysis; no fights')) as (deadline,_,__):
  analyze();deadline.remaining()


FILE render.py
"""Self-contained stored report; no engine invocation."""
import html
from common import *
from run import validation_receipt

def render():
 pins();r=read(HERE/'ANALYSIS.json')
 if r['validation_sha256']!=sha(HERE/'VALIDATION.json') or r['tuning_sha256']!=tuning_hash():raise RuntimeError('analysis identity drift')
 rows=['<tr><th>Arm</th><th>Head</th><th>Wins /40</th><th>Mean S</th><th>Own losses</th></tr>']
 for c in r['cells']:rows.append(f"<tr><td>{html.escape(c['arm'])}</td><td>{c['head']}</td><td>{c['wins']}</td><td>{c['mean_S']:.3f}</td><td>{c['own_losses']:.3f}</td></tr>")
 text='<!doctype html><meta charset="utf-8"><title>v7 development</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto}td,th{padding:8px;border-bottom:1px solid #bbb}pre{white-space:pre-wrap}</style><h1>v7 development observations</h1><p>Descriptive development; no scientific acceptance, population inference or S5 authorization.</p><table>'+''.join(rows)+'</table><p>'+html.escape(r['readings']['relative'])+'</p><p>Observed owner criterion: '+str(r['readings']['observed_owner_criterion'])+'</p><pre>'+html.escape(json.dumps({k:r[k] for k in ('positive_clusters','negative_clusters','tied_clusters','orientation_discordance','paired_cluster_bootstrap','omega0_duplicate','omega0_interpretation')},indent=2))+'</pre><details><summary>Paired cluster table and per-fight mechanism diagnostics</summary><pre>'+html.escape(json.dumps({k:r[k] for k in ('paired_clusters','per_fight')},indent=2))+'</pre></details>'
 (HERE/'REPORT.html').write_text(text)
 write(HERE/'RENDER.json',dict(analysis_sha256=sha(HERE/'ANALYSIS.json'),report_sha256=sha(HERE/'REPORT.html'),stored_only=True))
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('stage',nargs='?',default='validate',choices=('validate',));args=parser.parse_args()
 with attempt('render_'+args.stage,dict(status='not_run',reason='stored rendering; no fights')) as (deadline,_,__):
  validation_receipt();render();deadline.remaining()
