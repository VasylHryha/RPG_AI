"""Once-only Amendment-1 schedule: 20 on runs and two off controls, no pilots on import."""
import concurrent.futures
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
LOCAL = OUT / '_local' / 'economy'
CAP = 5400  # owner approval 2026-10-07 ~19:20 (decision 0031, daytime run just over 1 h; projection about 66 min); raised explicitly, as Amendment 1 requires
MAX_WORKERS = 10
# Anchor at executable, not any substring of the command. Both script/native
# alternatives contain this exact repository path. In particular pgrep cannot match.
REPO = re.escape(str(ROOT))
PATTERN = (r'^[^ ]*/?[Pp]ython[^ /]* ([-][^ ]+ )*' + REPO +
           r'/evidence/tactical_composition_demo/astelia_cpp/s4_[^ /]*_v1/[^ ]+([ ]|$)|^' +
           REPO + r'/[^ ]*/astelia_native[^ / ]*([ ]|$)')
ARMS = ('ECOF', 'ECOR')
JOBS = [(v,s,k,'on') for v in ARMS for s in ('i','ii') for k in range(5)] + [(v,'i',0,'off') for v in ARMS]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def job_name(job):
    v,s,k,o = job
    return f'{v}_{s}_k{k}_{o}'


def process_check():
    try:
        p = subprocess.run(['pgrep','-fl',PATTERN], text=True, capture_output=True)
        status = 'PROCESS_ACCESS_BLOCKED' if p.returncode not in (0,1) or p.stderr else 'BUSY' if p.returncode == 0 else 'CLEAR'
        return dict(status=status,command=['pgrep','-fl',PATTERN],returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,time_epoch=time.time())
    except OSError as error:
        return dict(status='PROCESS_ACCESS_BLOCKED',error=str(error),time_epoch=time.time())


def build_files(variant):
    kernel = OUT/'kernel_builder/_worktrees'/variant
    receipt = json.loads((OUT/f'kernel_builder/{variant}_BUILD.json').read_text())
    native = kernel/'evidence/tactical_composition_demo/growing_shapes/medium'
    world = kernel/'evidence/tactical_composition_demo/growing_shapes/world'
    paths = {native/'rev7_design.py':receipt['design_sha256'],
             kernel/'service_graph.py':receipt['service_graph_sha256'],
             kernel/'economy_kernel.py':receipt['economy_kernel_sha256'],
             kernel/'evidence/tactical_composition_demo/growing_shapes_review_claude/rev711_diag/pilot_common.py':receipt['harness_sha256']}
    paths.update({native/name:h for name,h in receipt['build']['source_sha256'].items()})
    images = list((native/'_rev7_build').glob('rev7_medium.*'))
    if len(images)!=1: raise RuntimeError('ambiguous/missing native image')
    paths[images[0]]=receipt['build']['binary_sha256']
    paths.update({world/name:h for name,h in receipt['world_build']['source_sha256'].items()})
    paths.update({world/'_build'/name:h for name,h in receipt['world_build']['binary_sha256'].items()})
    return paths


def validate_build(variant):
    receipt=json.loads((OUT/f'kernel_builder/{variant}_BUILD.json').read_text())
    current={OUT/'economy_kernel.py':receipt['economy_kernel_sha256'],OUT/'service_graph.py':receipt['service_graph_sha256'],OUT/'ECONOMY_PILOT_SPEC.md':receipt['spec_sha256'],OUT/'pilot_common_scratch.py':receipt['harness_sha256']}
    for p,h in {**build_files(variant),**current}.items():
        if sha(p)!=h: raise RuntimeError('build identity mismatch: '+str(p))


def code_hashes():
    names = ['execute_economy_plan.py','run_economy_pilot.py','write_economy_report.py',
             'economy_kernel.py','economy_telemetry.py','service_graph.py','pilot_common_scratch.py',
             'ECONOMY_PILOT_SPEC.md','MASS_BUDGET_DIAGNOSTIC.json','COVERAGE_COMPACT_SUMMARIES.json','COVERAGE_RUN_SUMMARIES.json','SERVICE_RUN_SUMMARIES.json','SERVICE_COMPACT_SUMMARIES.json',
             'bond_v2_screening.patch','kernel_builder/build_economy_kernels.py',
             'kernel_builder/ranked_d3_body.txt','kernel_builder/RD3_BUILD.json',
             'kernel_builder/HISTORICAL_SCREENING_IDENTITY.json']
    paths = {OUT/n for n in names}
    paths.update({OUT/'execute_coverage_plan.py',OUT/'write_coverage_report.py'})
    for v in ARMS:
        validate_build(v)
        paths.add(OUT/f'kernel_builder/{v}_BUILD.json')
        paths.update(build_files(v))
        # Bind runner, evaluator, entropy/calibration and all scratch Python/C++
        # dependencies, not merely the modified design and helper.
        kernel = OUT/'kernel_builder/_worktrees'/v
        subtree = kernel/'evidence/tactical_composition_demo/growing_shapes'
        paths.update(p for p in subtree.rglob('*') if p.is_file() and p.suffix in ('.py','.json','.cpp','.hpp','.h') and '__pycache__' not in p.parts)
    paths={p for p in paths if p.name not in ('PLAN_CURRENT.md','DESIGN_0G.md','DESIGN_0H_REV7.md')}
    return {str(p):sha(p) for p in sorted(paths)}


def check_frozen(expected):
    for p,h in expected.items():
        if sha(p)!=h: raise RuntimeError('code changed: '+p)


def load_completed(job, baseline, local=LOCAL):
    name = job_name(job)
    path = local/(name+'.summary.json')
    if not path.exists():
        if any((local/(name+s)).exists() for s in ('.started','.raw.log','.harness')):
            raise RuntimeError('started/incomplete slot cannot rerun: '+name)
        return None
    if path.is_symlink(): raise RuntimeError('unsafe summary path')
    row = json.loads(path.read_text())
    if (row['variant'],row['start'],row['keyset'],row['observer'])!=job or row['code_hashes']!=baseline:
        raise RuntimeError('completion identity mismatch: '+name)
    if row.get('binary_sha256')!=json.loads((OUT/f'kernel_builder/{job[0]}_BUILD.json').read_text())['build']['binary_sha256']:
        raise RuntimeError('completion binary mismatch')
    if row['summary'].get('steps')!=8000 or row['summary'].get('last_t')!=800.:
        raise RuntimeError('incomplete trajectory summary')
    if row['clone_isolation']!='PASS': raise RuntimeError('clone isolation failed: '+name)
    for field in ('cpu_seconds','elapsed_seconds'):
        if not math.isfinite(row[field]) or row[field]<=0: raise RuntimeError('invalid completion timing')
    if not re.fullmatch('[0-9a-f]{64}',row['state_trajectory_sha256']): raise RuntimeError('invalid trajectory digest')
    if not row['raw_traces']: raise RuntimeError('completion has no raw trace identity')
    for raw in row['raw_traces']:
        p = OUT/raw['path']
        if p.is_symlink() or not p.resolve().is_relative_to(local.resolve()): raise RuntimeError('unsafe raw path')
        if p.stat().st_size!=raw['bytes'] or sha(p)!=raw['sha256']: raise RuntimeError('raw trace identity mismatch: '+str(p))
    if job[3]=='on' and row['telemetry'].get('steps')!=8000: raise RuntimeError('incomplete observer trajectory')
    if job[3]=='on' and row['telemetry'].get('label_revision')!='AMENDMENT_1_ECONOMY': raise RuntimeError('observer revision mismatch')
    return row


def estimate_seconds(completed):
    # Historical workers measured both CPU and elapsed. Use their maximum, never
    # a smaller hand-tuned estimate, and update after every completed job.
    historical=[r for r in json.loads((OUT/'SERVICE_RUN_SUMMARIES.json').read_text())['runs'] if r['variant']=='RD3']
    return max([660.] + [max(r['cpu_seconds'],r['elapsed_seconds']) for r in historical+completed])


def projection(remaining, workers, per_job, elapsed=0.):
    return elapsed+math.ceil(remaining/workers)*per_job


def integrity(rows):
    checks={}
    for v in ARMS:
        pair={r['observer']:r for r in rows if (r['variant'],r['start'],r['keyset'])==(v,'i',0)}
        if set(pair)!= {'on','off'}: checks[v]='NOT_RUN'; continue
        on,off=pair['on'],pair['off']
        checks[v]='PASS' if on['summary']==off['summary'] and on['state_trajectory_sha256']==off['state_trajectory_sha256'] and on['clone_isolation']==off['clone_isolation']=='PASS' else 'FAIL'
    return checks


def worker(job,ticket):
    check=process_check()
    if check['status']!='CLEAR': raise RuntimeError('process gate: '+json.dumps(check))
    grant=json.loads(ticket.read_text());check_frozen(grant['code_hashes'])
    if grant['status']!='RUNNING' or time.time()>=grant['deadline_epoch']: raise RuntimeError('expired grant')
    name=job_name(job)
    with (LOCAL/(name+'.raw.log')).open('x') as log:
        subprocess.run([sys.executable,str(OUT/'run_economy_pilot.py'),'--variant',job[0],
                        '--start',job[1],'--keyset',str(job[2]),'--observer',job[3],'--ticket',str(ticket)],
                       cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,
                       timeout=max(1,grant['deadline_epoch']-time.time()))
    return load_completed(job,grant['code_hashes'])


def main():
    LOCAL.mkdir(parents=True,exist_ok=True)
    # Exclusive scheduler lock prevents competing grants; retained after abnormal
    # scheduler death, requiring inspection rather than silently restarting.
    lock=LOCAL/'SCHEDULER.lock'
    try:
        with lock.open('x') as f: f.write(str(os.getpid()))
    except FileExistsError:
        print('STOP: economy scheduler lock exists; inspect original process');return 2
    checks=[];rows=[];ticket=None;awake=None;status='PARTIAL';data={};baseline=None
    started=time.monotonic()
    try:
        while True:
            check=process_check();checks.append(check)
            (OUT/'ECONOMY_PREFLIGHT.json').write_text(json.dumps(dict(status=check['status'],checks=checks),indent=2)+'\n')
            if check['status']=='PROCESS_ACCESS_BLOCKED': raise RuntimeError('process access blocked; no jobs launched')
            if check['status']=='CLEAR': break
            if time.monotonic()-started>=CAP: raise RuntimeError('combat wait exceeded cap')
            print('Waiting for this repository combat processes...',flush=True);time.sleep(15)
        started=time.monotonic();baseline=code_hashes()
        rows=[r for j in JOBS if (r:=load_completed(j,baseline)) is not None]
        remaining=[j for j in JOBS if not any(job_name(j)==job_name((r['variant'],r['start'],r['keyset'],r['observer'])) for r in rows)]
        workers=min(MAX_WORKERS,os.cpu_count() or 1)
        projected=projection(len(remaining),workers,estimate_seconds(rows))
        if projected>=CAP: raise RuntimeError(f'projection {projected:.1f}s exceeds {CAP}s cap; report to owner')
        ticket=LOCAL/f'RUN_TICKET_{time.time_ns()}.json'
        data=dict(status='RUNNING',started_epoch=time.time(),deadline_epoch=time.time()+CAP,
                  code_hashes=baseline,jobs=JOBS,projection_seconds=projected,workers=workers,reused=[job_name((r['variant'],r['start'],r['keyset'],r['observer'])) for r in rows])
        with ticket.open('x') as f: json.dump(data,f,indent=2)
        awake=subprocess.Popen(['caffeinate','-i','-s'])
        # Controls are inside this one main phase; dispatch both pairs first.
        priority=[(v,'i',0,o) for v in ARMS for o in ('on','off')]
        remaining.sort(key=lambda j:priority.index(j) if j in priority else len(priority)+JOBS.index(j))
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            pending={};error=None
            while remaining or pending:
                check_frozen(baseline)
                while remaining and len(pending)<workers and error is None:
                    # Include in-flight waves, all remaining jobs and both off
                    # controls; elapsed time reduces this attempt's shared cap.
                    elapsed=time.monotonic()-started
                    proj=projection(len(remaining)+len(pending),workers,estimate_seconds(rows),elapsed)
                    if proj>=CAP:
                        error=RuntimeError(f'projection {proj:.1f}s exceeds {CAP}s; stop launching');break
                    j=remaining.pop(0);pending[pool.submit(worker,j,ticket)]=j
                if not pending:
                    if error: raise error
                    break
                done,_=concurrent.futures.wait(pending,timeout=min(15,max(0,data['deadline_epoch']-time.time())),return_when=concurrent.futures.FIRST_COMPLETED)
                if time.time()>=data['deadline_epoch']: error=RuntimeError('shared deadline exceeded')
                for f in done:
                    pending.pop(f)
                    try: rows.append(f.result())
                    except Exception as e: error=e
                if 'FAIL' in integrity(rows).values(): error=RuntimeError('observer on/off identity failed')
                if error and not pending: raise error
            check_frozen(baseline)
        if integrity(rows)!=dict.fromkeys(ARMS,'PASS'): raise RuntimeError('integrity pairs incomplete')
        status='DONE'
    except Exception as error:
        data['stop_reason']=str(error);print('STOP:',error,flush=True)
    finally:
        if awake is not None: awake.terminate();awake.wait()
        if baseline is not None:
            # Recover only verified completions; failed slots remain untouched.
            rows=[]
            for j in JOBS:
                try:
                    r=load_completed(j,baseline)
                    if r is not None:rows.append(r)
                except Exception as error:
                    data.setdefault('completion_errors',[]).append(str(error));status='PARTIAL'
        if not rows and not any(LOCAL.glob('*_*.started')) and not any(LOCAL.glob('*.raw.log')) and not any(LOCAL.glob('*.harness')): status='NOT_RUN'
        data.update(status=status,elapsed_seconds=time.monotonic()-started,
                    awake_seconds=time.monotonic()-started if awake else 0.,integrity=integrity(rows),checks=checks)
        if ticket is not None:ticket.write_text(json.dumps(data,indent=2)+'\n')
        inventory=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(LOCAL.rglob('*')) if p.is_file() and (p.suffix=='.gz' or p.name.endswith('.raw.log'))]
        (OUT/'ECONOMY_RUN_SUMMARIES.json').write_text(json.dumps(dict(status=status,runs=rows,integrity=integrity(rows),timing=data,raw_inventory=inventory),separators=(',',':'),allow_nan=False)+'\n')
        lock.unlink()
    return 0 if status=='DONE' else 2


if __name__=='__main__':sys.exit(main())
