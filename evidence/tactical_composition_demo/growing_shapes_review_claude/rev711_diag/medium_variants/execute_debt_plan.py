"""Once-only DEBT schedule: 10 on runs and one off control, no pilots on import."""
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
LOCAL = OUT / '_local' / 'debt'
CAP_CONFIG = OUT / '_local' / 'DEBT_CAP.json'


def read_cap(path=None):
    path = CAP_CONFIG if path is None else Path(path)
    config = json.loads(path.read_text()) if path.exists() else {'cap_seconds': 5400}
    value = config['cap_seconds']
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError('cap_seconds must be finite and positive')
    return float(value)


MAX_WORKERS = 10
# Anchor at executable, not any substring of the command. Both script/native
# alternatives contain this exact repository path. In particular pgrep cannot match.
REPO = re.escape(str(ROOT))
PATTERN = (r'^[^ ]*/?[Pp]ython[^ /]* ([-][^ ]+ )*' + REPO +
           r'/evidence/tactical_composition_demo/astelia_cpp/s4_[^ /]*_v1/[^ ]+([ ]|$)|^' +
           REPO + r'/[^ ]*/astelia_native[^ / ]*([ ]|$)')
ARMS = ('DEBT',)
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
             kernel/'debt_kernel.py':receipt['debt_kernel_sha256'],
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
    current={OUT/'debt_kernel.py':receipt['debt_kernel_sha256'],OUT/'service_graph.py':receipt['service_graph_sha256'],OUT/'pilot_common_scratch.py':receipt['harness_sha256']}
    for p,h in {**build_files(variant),**current}.items():
        if sha(p)!=h: raise RuntimeError('build identity mismatch: '+str(p))


def code_hashes():
    names = ['execute_debt_plan.py', 'run_debt_pilot.py', 'write_debt_report.py',
             'debt_kernel.py', 'debt_telemetry.py', 'coverage_telemetry.py',
             'economy_telemetry.py', 'service_graph.py', 'pilot_common_scratch.py',
             'SERVICE_RUN_SUMMARIES.json', 'COVERAGE_RUN_SUMMARIES.json',
             'bond_v2_screening.patch', 'kernel_builder/build_debt_kernel.py',
             'kernel_builder/ranked_d3_body.txt',
             'kernel_builder/RD3_BUILD.json', 'kernel_builder/HISTORICAL_SCREENING_IDENTITY.json',
             'write_coverage_report.py', 'execute_coverage_plan.py']
    paths = {OUT/n for n in names}
    for v in ARMS:
        validate_build(v)
        paths.add(OUT/f'kernel_builder/{v}_BUILD.json')
        paths.update(build_files(v))
        # Bind runner, evaluator, entropy/calibration and all scratch Python/C++
        # dependencies, not merely the modified design and helper.
        kernel = OUT/'kernel_builder/_worktrees'/v
        subtree = kernel/'evidence/tactical_composition_demo/growing_shapes'
        paths.update(p for p in subtree.rglob('*') if p.is_file() and p.suffix in ('.py','.json','.cpp','.hpp','.h') and '__pycache__' not in p.parts)
    paths={p for p in paths if p.suffix != '.md'}
    return {str(p):sha(p) for p in sorted(paths)}


def check_frozen(expected):
    for p,h in expected.items():
        if sha(p)!=h: raise RuntimeError('code changed: '+p)


def load_completed(job, baseline, local=LOCAL):
    name = job_name(job)
    path = local/(name+'.summary.json')
    if not path.exists():
        if any((local/(name+s)).exists() for s in ('.started','.raw.log','.harness','.jsonl.gz','.legacy.json.gz')):
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
    required={str((local/(name+'.legacy.json.gz')).relative_to(OUT))}
    if job[3]=='on': required.add(str((local/(name+'.jsonl.gz')).relative_to(OUT)))
    if {r['path'] for r in row['raw_traces']} != required or len(row['raw_traces']) != len(required):
        raise RuntimeError('completion raw trace set mismatch')
    for raw in row['raw_traces']:
        p = OUT/raw['path']
        if p.is_symlink() or not p.resolve().is_relative_to(local.resolve()): raise RuntimeError('unsafe raw path')
        if p.stat().st_size!=raw['bytes'] or sha(p)!=raw['sha256']: raise RuntimeError('raw trace identity mismatch: '+str(p))
    if job[3]=='on' and row['telemetry'].get('steps')!=8000: raise RuntimeError('incomplete observer trajectory')
    if job[3]=='on' and row['telemetry'].get('debt_boundary_steps')!=8000: raise RuntimeError('incomplete debt telemetry')
    if job[3]=='on' and row['telemetry'].get('label_revision')!='AMENDMENT_1_DEBT': raise RuntimeError('observer revision mismatch')
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
        subprocess.run([sys.executable,str(OUT/'run_debt_pilot.py'),'--variant',job[0],
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
        print('STOP: debt scheduler lock exists; inspect original process');return 2
    checks=[];rows=[];ticket=None;awake=None;status='PARTIAL';data={};baseline=None
    started=time.monotonic()
    try:
        cap=read_cap()
        data.update(cap_seconds=cap, cap_config_path=str(CAP_CONFIG), cap_in_completion_identity=False)
        while True:
            check=process_check();checks.append(check)
            (OUT/'DEBT_PREFLIGHT.json').write_text(json.dumps(dict(status=check['status'],checks=checks),indent=2)+'\n')
            if check['status']=='PROCESS_ACCESS_BLOCKED': raise RuntimeError('process access blocked; no jobs launched')
            if check['status']=='CLEAR': break
            if time.monotonic()-started>=cap: raise RuntimeError('combat wait exceeded cap')
            print('Waiting for this repository combat processes...',flush=True);time.sleep(15)
        started=time.monotonic();baseline=code_hashes()
        rows=[r for j in JOBS if (r:=load_completed(j,baseline)) is not None]
        remaining=[j for j in JOBS if not any(job_name(j)==job_name((r['variant'],r['start'],r['keyset'],r['observer'])) for r in rows)]
        workers=min(MAX_WORKERS,os.cpu_count() or 1)
        projected=projection(len(remaining),workers,estimate_seconds(rows))
        if projected>=cap: raise RuntimeError(f'projection {projected:.1f}s exceeds {cap}s cap; report to owner')
        ticket=LOCAL/f'RUN_TICKET_{time.time_ns()}.json'
        data.update(status='RUNNING',started_epoch=time.time(),deadline_epoch=time.time()+cap,
                  code_hashes=baseline,jobs=JOBS,projection_seconds=projected,workers=workers,reused=[job_name((r['variant'],r['start'],r['keyset'],r['observer'])) for r in rows])
        with ticket.open('x') as f: json.dump(data,f,indent=2)
        awake=subprocess.Popen(['caffeinate','-i','-s']) if sys.platform == 'darwin' and remaining else None
        # Controls are inside this one main phase; dispatch the on/off pair first.
        priority=[(v,'i',0,o) for v in ARMS for o in ('on','off')]
        remaining.sort(key=lambda j:priority.index(j) if j in priority else len(priority)+JOBS.index(j))
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            pending={};error=None
            while remaining or pending:
                check_frozen(baseline)
                while remaining and len(pending)<workers and error is None:
                    # Include in-flight waves, all remaining jobs and the off
                    # controls; elapsed time reduces this attempt's shared cap.
                    elapsed=time.monotonic()-started
                    proj=projection(len(remaining)+len(pending),workers,estimate_seconds(rows),elapsed)
                    if proj>=cap:
                        error=RuntimeError(f'projection {proj:.1f}s exceeds {cap}s; stop launching');break
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
        (OUT/'DEBT_RUN_SUMMARIES.json').write_text(json.dumps(dict(status=status,runs=rows,integrity=integrity(rows),timing=data,raw_inventory=inventory),separators=(',',':'),allow_nan=False)+'\n')
        lock.unlink()
    return 0 if status=='DONE' else 2


if __name__=='__main__':sys.exit(main())
