"""One-shot measured wrapper: delegates sequence and verdicts to the pinned harness."""
import gzip, hashlib, inspect, json, subprocess, sys, traceback
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_identity import assert_inputs, PIN
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_execution import Execution
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_fixtures import Harness
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_verify import clocks
PIN_DIGEST='3b6cf5635a29da1b16969155016655c61c534622129d3fbae30605e19fbbb551'
REVIEW='evidence/tactical_composition_demo/growing_shapes_review_claude/REV7_FIXTURE_READINESS.md'
APPROVAL='docs/decisions/0031-owner-run-approval-policy.md'
PROVENANCE='Assisted-by: Codex:GPT-6'
AREA='evidence/tactical_composition_demo/growing_shapes/'
ORDER=('N1','F1','F2','F3','F4','F5','F6','F7','F8','F9')
def write(name,value):
    with (OUT/name).open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def timing(a,b):return dict(start_utc=a['utc'],end_utc=b['utc'],awake_seconds=b['awake']-a['awake'],continuous_seconds=b['continuous']-a['continuous'],elapsed_utc_seconds=(datetime.fromisoformat(b['utc'])-datetime.fromisoformat(a['utc'])).total_seconds())
def preserve():
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    return {p:digest(ROOT/p) for p in paths if p and not p.startswith(AREA) and (ROOT/p).is_file()}
def raw(name,row):
    data=(json.dumps(row,separators=(',',':'),allow_nan=False)+'\n').encode()
    path=OUT/(name+'.json.gz')
    with gzip.open(path,'xb') as stream:stream.write(data)
    return dict(path=str(path.relative_to(ROOT)),bytes=path.stat().st_size,sha256=digest(path),decoded_bytes=len(data),decoded_sha256=hashlib.sha256(data).hexdigest(),delivery_eligible=path.stat().st_size<50_000_000)
class MeasuredHarness(Harness):
    def __getattribute__(self,name):
        method=super().__getattribute__(name)
        if name not in ORDER+('F1d',):return method
        def measured():
            a=clocks();print(a['utc'],'START',name,flush=True)
            try:
                row=method()
                return row
            finally:
                b=clocks();cost=timing(a,b);costs[name]=cost;write(name+'_TIMING.json',cost)
                print(b['utc'],'END',name,'awake',cost['awake_seconds'],flush=True)
                if 'row' in locals():traces[name]=raw(name,row)
        return measured
costs={};traces={};sub_starts={}
# Passive line observer captures F1a-c times without replacing any harness method.
f1_lines,start_line=inspect.getsourcelines(Harness.F1)
f1_begin=start_line+next(i for i,s in enumerate(f1_lines) if "m=scaffold(name" in s)
f1_end=start_line+next(i for i,s in enumerate(f1_lines) if 'finally:m.close()' in s)
def local_trace(frame,event,arg):
    if event=='line':
        name=frame.f_locals.get('name')
        if frame.f_lineno==f1_begin:sub_starts[name]=clocks()
        elif frame.f_lineno==f1_end and name in sub_starts:
            cost=timing(sub_starts.pop(name),clocks());cost['scope']='integration and measurement, excludes final close'
            costs[name]=cost;write(name+'_TIMING.json',cost)
    return local_trace
def global_trace(frame,event,arg):
    return local_trace if event=='call' and frame.f_code is Harness.F1.__code__ else None
if __name__=='__main__':
    assert digest(PIN)==PIN_DIGEST,'execution pin mismatch'
    identity=assert_inputs()
    write('PREFLIGHT_IDENTITY.json',identity)
    write('DURATION_ESTIMATE.json',dict(estimate_seconds=[300,1800],exceeds_one_hour=False,qualified=False,source='REV7_INTEGRATION_REPORT.md lines 47-49, verified against Harness workload',workload=dict(N1_RK4_substeps=20000,F1_world_steps=8000,F2_world_steps=320,F4_assay_episodes=10,F5_growth_steps=16000,F5_assay_episodes=180,F5_qualification_starts=24,F6_assay_episodes=140,F7_growth_steps=8000,F8_growth_steps=6400,F8_qualification_starts=10,F9_decoder_observations=4),recovery='candidate-dependent, no benchmark or rehearsal'))
    before=preserve();write('OUTSIDE_SCOPE_BASELINE.json',before)
    staged=subprocess.check_output(['git','diff','--cached','--binary'],cwd=ROOT)
    write('EXECUTION_CLAIM.json',dict(created_utc=clocks()['utc'],pin_sha256=PIN_DIGEST,approval_reference=APPROVAL,integration_review=REVIEW,provenance=PROVENANCE,execution_once=True))
    grant=Execution(engines_ready_reviewed=True,integration_tested_reviewed=True,approval_reference=APPROVAL,integration_review=str(ROOT/REVIEW),receipt_dir=str(OUT))
    harness=MeasuredHarness(grant,backend='native')
    a=clocks();sys.settrace(global_trace)
    try:receipt=harness.run_all()
    except Exception as error:
        receipt=dict(revision='7.3',identity_snapshot=identity,results=harness.results,not_run=[n for n in ORDER if n not in harness.results],stops=[],error=f'{type(error).__name__}: {error}',traceback=traceback.format_exc())
    finally:sys.settrace(None)
    b=clocks()
    verdict='INVALID' if receipt.get('error') or any(r['verdict']=='INVALID' for r in receipt['results'].values()) else 'FIXTURES_FAIL' if any(r['verdict']=='FAIL' for r in receipt['results'].values()) else 'FIXTURES_PASS' if not receipt['not_run'] else 'INVALID'
    receipt.update(verdict=verdict,timings=costs,traces=traces,total=timing(a,b),provenance=PROVENANCE,clock_methods=dict(awake='mach_absolute_time excludes sleep',continuous='mach_continuous_time includes sleep',elapsed='UTC timestamp difference'),run_wrapper_sha256=digest(Path(__file__)))
    write('RUN_RECEIPT.json',receipt)
    after=preserve();changed=[p for p in set(before)|set(after) if before.get(p)!=after.get(p)]
    end_identity=assert_inputs()
    write('PRESERVATION.json',dict(status='PASS' if not changed and staged==subprocess.check_output(['git','diff','--cached','--binary'],cwd=ROOT) else 'FAIL',outside_scope_changed=changed,tracked_files_checked=len(before),pin_unchanged=end_identity['pin_sha256']==PIN_DIGEST,staged_diff_unchanged=staged==subprocess.check_output(['git','diff','--cached','--binary'],cwd=ROOT),plan_unchanged=before['docs/PLAN_CURRENT.md']==after['docs/PLAN_CURRENT.md']))
    print(json.dumps(dict(verdict=verdict,results={n:r['verdict'] for n,r in receipt['results'].items()},not_run=receipt['not_run'],total=receipt['total'])),flush=True)
