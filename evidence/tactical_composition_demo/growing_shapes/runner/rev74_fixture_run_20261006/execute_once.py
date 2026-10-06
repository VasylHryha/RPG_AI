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
PIN_DIGEST='f370c3b5ea17cf0b3c751de794de0c8ab1dffdb35cbffdc35d81f9b8280c3ce5'
REVIEW='evidence/tactical_composition_demo/growing_shapes_review_claude/REV74_FIXTURE_READINESS.md'
APPROVAL='docs/decisions/0031-owner-run-approval-policy.md'
PROVENANCE='Assisted-by: Codex:GPT-6'
AREA='evidence/tactical_composition_demo/growing_shapes/'
ORDER=('N1','F1','F2','F3','F4','F5','F6','F7','F8','F9')
def write(name,value):
    with (OUT/name).open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def timing(a,b):return dict(start_clock=a,end_clock=b,start_utc=a['utc'],end_utc=b['utc'],awake_seconds=b['awake']-a['awake'],continuous_seconds=b['continuous']-a['continuous'],elapsed_utc_seconds=(datetime.fromisoformat(b['utc'])-datetime.fromisoformat(a['utc'])).total_seconds())
def preserve():
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    return {p:digest(ROOT/p) for p in paths if p and (ROOT/p).is_file()}
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
costs={};traces={};sub_starts={};growth_starts={};run_components={}
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
# Passive F5 line timestamps and final live Run costs. No scientific method replaced.
f5_lines,f5_start=inspect.getsourcelines(Harness.F5)
f5_begin=f5_start+next(i for i,s in enumerate(f5_lines) if "initial=literal_start()" in s)
f5_end=f5_start+next(i for i,s in enumerate(f5_lines) if s.strip()=='finally:')
def run_snapshot(run):
    return dict(timing=dict(run.timing),exposure=dict(run.exposure),population=len(run.medium.native),peak_population=run.medium.peak,snapshots=len(run.snapshots),growth_checks=len(run.growth_counts),estimator_validity=run.medium.estimator_validity())
def growth_trace(frame,event,arg):
    if event=='line':
        label=frame.f_locals.get('start')
        if frame.f_lineno==f5_begin:growth_starts[label]=clocks();print(clocks()['utc'],'START F5('+label+')',flush=True)
        elif frame.f_lineno==f5_end and label in growth_starts:
            name='F5'+label;cost=timing(growth_starts.pop(label),clocks());costs[name]=cost;write(name+'_TIMING.json',cost)
            run_components[name]=run_snapshot(frame.f_locals['run']);write(name+'_COMPONENT_COSTS.json',run_components[name]);print(cost['end_utc'],'END',name,flush=True)
    return growth_trace
terminal_lines={}
for method in (Harness.F7,Harness.F8):
    lines,start=inspect.getsourcelines(method)
    terminal_lines[method.__code__]=start+next(i for i,s in enumerate(lines) if 'finally:run.close()' in s)
def terminal_trace(frame,event,arg):
    if event=='line' and frame.f_lineno==terminal_lines[frame.f_code]:
        name=frame.f_code.co_name;run_components[name]=run_snapshot(frame.f_locals['run']);write(name+'_COMPONENT_COSTS.json',run_components[name])
    return terminal_trace
def global_trace(frame,event,arg):
    if event!='call':return None
    if frame.f_code is Harness.F1.__code__:return local_trace
    if frame.f_code is Harness.F5.__code__:return growth_trace
    if frame.f_code in (Harness.F7.__code__,Harness.F8.__code__):return terminal_trace
    return None
if __name__=='__main__':
    assert digest(PIN)==PIN_DIGEST,'execution pin mismatch'
    estimate=json.loads((OUT/'DURATION_ESTIMATE.json').read_text())
    if estimate['exceeds_one_hour']:raise SystemExit('estimate exceeds one hour; STOP')
    identity=assert_inputs()
    write('PREFLIGHT_IDENTITY.json',identity)
    before=preserve();write('OUTSIDE_SCOPE_BASELINE.json',before)
    staged=subprocess.check_output(['git','diff','--cached','--binary'],cwd=ROOT)
    write('EXECUTION_CLAIM.json',dict(created_utc=clocks()['utc'],pin_sha256=PIN_DIGEST,approval_reference=APPROVAL,integration_review=REVIEW,provenance=PROVENANCE,execution_once=True))
    grant=Execution(engines_ready_reviewed=True,integration_tested_reviewed=True,approval_reference=APPROVAL,integration_review=str(ROOT/REVIEW),receipt_dir=str(OUT))
    harness=MeasuredHarness(grant,backend='native')
    a=clocks();sys.settrace(global_trace)
    try:receipt=harness.run_all()
    except Exception as error:
        receipt=dict(revision='7.4',identity_snapshot=identity,results=harness.results,not_run=[n for n in ORDER if n not in harness.results],stops=[],error=f'{type(error).__name__}: {error}',traceback=traceback.format_exc())
    finally:sys.settrace(None)
    b=clocks()
    verdict='INVALID' if receipt.get('error') or any(r['verdict']=='INVALID' for r in receipt['results'].values()) else 'FIXTURES_FAIL' if any(r['verdict']=='FAIL' for r in receipt['results'].values()) else 'FIXTURES_PASS' if not receipt['not_run'] else 'INVALID'
    receipt.update(verdict=verdict,timings=costs,traces=traces,total=timing(a,b),provenance=PROVENANCE,clock_methods=dict(awake='mach_absolute_time excludes sleep',continuous='mach_continuous_time includes sleep',elapsed='UTC timestamp difference'),run_wrapper_sha256=digest(Path(__file__)),run_components=run_components)
    write('RUN_RECEIPT.json',receipt)
    after=preserve();changed=[p for p in set(before)|set(after) if before.get(p)!=after.get(p)]
    end_identity=assert_inputs()
    write('PRESERVATION.json',dict(status='PASS' if not changed and staged==subprocess.check_output(['git','diff','--cached','--binary'],cwd=ROOT) else 'FAIL',outside_scope_changed=changed,tracked_files_checked=len(before),pin_unchanged=end_identity['pin_sha256']==PIN_DIGEST,staged_diff_unchanged=staged==subprocess.check_output(['git','diff','--cached','--binary'],cwd=ROOT),plan_unchanged=before['docs/PLAN_CURRENT.md']==after['docs/PLAN_CURRENT.md']))
    print(json.dumps(dict(verdict=verdict,results={n:r['verdict'] for n,r in receipt['results'].items()},not_run=receipt['not_run'],total=receipt['total'])),flush=True)
