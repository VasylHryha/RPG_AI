"""Script-only A0. Native fights require host process discovery and live RAM checks."""
import argparse
import contextlib
import fcntl
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import random
import secrets
import subprocess
import sys
import time
from a0_common import ARMS, BINARY, CELLS, CPP, HERE, LOCAL, MAX_RSS, POOL, code_hashes, load, owner_cap, read, sha, write
from a0_metrics import measure, report
LEDGER = LOCAL/'A0_LEDGER.json'
REQUESTS = LOCAL/'requests'
RAW = LOCAL/'raw'
_DEADLINE = None
_VERIFIED = {}
WIRE_FORM = 'json.loads sealed UTF-8 file; json.dumps separators=(",", ":"), allow_nan=False; UTF-8 plus one newline'


def wire_request(path, expected_sha256):
    payload=Path(path).read_bytes()
    if hashlib.sha256(payload).hexdigest()!=expected_sha256:
        raise RuntimeError('sealed request drift')
    return (json.dumps(json.loads(payload),separators=(',',':'),allow_nan=False)+'\n').encode()


def host_command():
    # Observer/summary telemetry is stdout. --metrics adds stderr counters, which
    # measure() does not consume; keep stderr empty so diagnostics fail closed.
    return ['nice','-n','15',str(BINARY)]


def check_deadline():
    if _DEADLINE is not None and time.monotonic()>=_DEADLINE:
        raise TimeoutError('owner wall cap during validation/reporting')

@contextlib.contextmanager
def lock():
    LOCAL.mkdir(exist_ok=True)
    with (LOCAL/'execution.lock').open('a') as f:
        try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise RuntimeError('another A0 invocation holds the lock')
        yield

def request(arm,tactic,seed,orientation):
    adapter=load('a0_request_parent',CPP/'s4_react_adapter_v1/requests.py')
    enemy=adapter.lab.controller('regular') if tactic=='regular' else adapter.lab.doctrine(tactic,POOL)
    req=adapter.request('forcedP16+react',enemy,seed,orientation,abilities_off=True)
    req.update(trace=False,debug=False,killerTelemetry=True,decisionTrace=True,
               diagnostics=False,decisionDiagnostics=False,attributionDiagnostics=False,s3=True)
    req['labBattery']={'mode':'base','k':1,'radius':400}
    req['labShapes']={'arm':arm}
    return req

def declaration(record):
    payload={k:v for k,v in record.items() if k!='jobs'} | {'ledger_sha256':sha(LEDGER)}
    path=HERE/'A0_DECLARATION.json'
    if path.exists():
        if read(path)!=payload:raise RuntimeError('declaration drift')
    else:write(path,payload,exclusive=True)

def prior_seeds():
    return {j['seed'] for j in read(HERE.parent/'_local/A0_LEDGER.json')['jobs']}


def check_equivalence():
    proof=read(HERE/'A0_EQUIVALENCE.json')
    if (proof.get('status')!='PASS' or proof.get('binary_sha256')!=sha(BINARY) or
        proof.get('code_hashes')!=code_hashes() or proof.get('total_mismatches')!=0):
        raise RuntimeError('current zero-mismatch same-state equivalence proof required')
    return proof


def prepare():
    if LEDGER.exists():
        record=read(LEDGER)
        declaration(record)
        return identity()
    plan_path=LOCAL/'PREPARATION.json'
    admission=load('a0_binary_admission',CPP/'build_admission.py')
    binary=admission.admit(BINARY);check_equivalence();fingerprints=code_hashes()
    if plan_path.exists():
        preparation=read(plan_path)
        if preparation['binary']!=binary or preparation['code_hashes']!=fingerprints:
            raise RuntimeError('preparation input drift; preserve transaction and revise prospectively')
        pairs=preparation['pairs']
    else:
        # Separate pilot and outcome entropy; fresh OS entropy, never historic seeds.
        rng=random.Random(secrets.randbits(256));used=prior_seeds();pairs=[]
        def pair(stage,panel,index,tactic,orientation):
            seed=rng.randrange(1,2**32)
            while seed in used:seed=rng.randrange(1,2**32)
            used.add(seed)
            pairs.append(dict(stage=stage,panel=panel,index=index,tactic=tactic,orientation=orientation,
                              seed=seed,pair_key=f'{stage}_{panel}_{index:03d}'))
        for i in range(3):
            pair('pilot','regular',i,'regular',i%2)
            pair('pilot','C3',i,('storm','loose','wolfpack')[i],i%2)
        # C3: 2/cell then ten extras at 50; 5/cell at 100. Orientations alternate per cell.
        order=[]
        shuffled=list(CELLS);rng.shuffle(shuffled)
        for cycle in range(5):
            for cell in shuffled:order.append((cell,cycle%2))
        for i in range(100):
            pair('outcome','regular',i,'regular',i%2)
            cell,orientation=order[i];pair('outcome','C3',i,cell,orientation)
        preparation=dict(binary=binary,code_hashes=fingerprints,pairs=pairs,
            decision_source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=CPP,text=True).strip())
        write(plan_path,preparation,exclusive=True)
    REQUESTS.mkdir(parents=True,exist_ok=True)
    jobs=[]
    for p in pairs:
        for arm in ARMS:
            tag=p['pair_key']+'_'+arm.replace('+','_')
            path=REQUESTS/(tag+'.json');payload=request(arm,p['tactic'],p['seed'],p['orientation'])
            if path.exists():
                if read(path)!=payload:raise RuntimeError('partial request drift')
            else:write(path,payload,exclusive=True)
            jobs.append(dict(**p,arm=arm,tag=tag,request_sha256=sha(path)))
    record=dict(schema=1,revision=2,prior_ledger_sha256=sha(HERE.parent/'_local/A0_LEDGER.json'),status='DEVELOPMENT_ONLY_A0_NO_NETWORKS',arms=list(ARMS),cells=list(CELLS),
                binary=binary,code_hashes=fingerprints,jobs=jobs,pilot_fights=18,looks=[50,100],workers=1,event_floor=.01,
                useful_thresholds={'deaths_saved':2,'exchange_gain':.10},
                decision_source_commit=preparation['decision_source_commit'])
    write(LEDGER,record,exclusive=True);declaration(record)
    return record

def identity():
    ledger=read(LEDGER)
    if ledger.get('revision')!=2:raise RuntimeError('not an A0 rev2 ledger')
    if ledger['prior_ledger_sha256']!=sha(HERE.parent/'_local/A0_LEDGER.json'):raise RuntimeError('rev1 evidence ledger drift')
    expected=ledger
    if expected['code_hashes']!=code_hashes():raise RuntimeError('A0 rev2 code drift; revise prospectively')
    check_equivalence()
    admission=load('a0_binary_admission',CPP/'build_admission.py')
    if expected['binary']!=admission.admit(BINARY):raise RuntimeError('A0 binary drift')
    if read(HERE/'A0_DECLARATION.json')['ledger_sha256']!=sha(LEDGER):raise RuntimeError('ledger drift')
    for job in ledger['jobs']:
        if sha(REQUESTS/(job['tag']+'.json'))!=job['request_sha256']:raise RuntimeError('request drift')
    return ledger

def completed(job):
    check_deadline()
    path=RAW/(job['tag']+'_COMPLETE.json')
    if not path.exists():return None
    row=read(path)
    raw=RAW/row.get('raw_file',job['tag']+'.jsonl.gz')
    key=(str(path),path.stat().st_mtime_ns,path.stat().st_size,raw.stat().st_mtime_ns,raw.stat().st_size,sha(LEDGER))
    if key in _VERIFIED:return _VERIFIED[key]
    if row['job']!=job or row['ledger_sha256']!=sha(LEDGER) or row['raw_sha256']!=sha(raw):
        raise RuntimeError('completion identity drift')
    if measure(raw,_DEADLINE)!=row['stats']:raise RuntimeError('completion statistics drift')
    result=dict(**job,stats=row['stats'],seconds=row['seconds'],receipt_sha256=sha(path))
    _VERIFIED[key]=result
    return result

def process_gate(deadline):
    gate=load('a0_repository_gate',CPP/'s4_net_slice_v1/process_gate.py')
    gate.GATE_PATH=LOCAL/'PROCESS_GATE.json'
    return gate.process_gate(wait=False,deadline=deadline)

def live_memory(pid):
    # macOS host. Fail closed if process/RAM discovery is unavailable.
    rss=0
    if pid is not None:
        query=subprocess.run(['ps','-o','rss=','-p',str(pid)],capture_output=True,text=True,timeout=5)
        if query.returncode or not query.stdout.strip():raise RuntimeError('child RSS unavailable')
        rss=int(query.stdout.strip())*1024
        if rss>MAX_RSS:raise RuntimeError('child exceeds 2 GiB RSS')
    query=subprocess.run(['vm_stat'],capture_output=True,text=True,timeout=5)
    if query.returncode or query.stderr.strip():raise RuntimeError('live RAM unavailable')
    lines=query.stdout.splitlines();page=int(lines[0].split('page size of ')[1].split()[0])
    fields={line.split(':')[0]:int(line.split(':')[1].strip().rstrip('.')) for line in lines[1:] if ':' in line and line.split(':')[1].strip().rstrip('.').isdigit()}
    available=(fields.get('Pages free',0)+fields.get('Pages inactive',0))*page
    if available<512*1024**2:raise RuntimeError('live available RAM below 512 MiB reserve')
    return rss

def execute(job,deadline):
    prior=completed(job)
    if prior:return prior
    if time.monotonic()>=deadline:raise TimeoutError('owner wall cap reached before fight')
    RAW.mkdir(parents=True,exist_ok=True)
    tag=job['tag'];attempt=secrets.token_hex(8)
    previous=list(RAW.glob(tag+'_*_ATTEMPT.json'))
    retry_causes={}
    for path in previous:
        if read(path).get('status')!='INTERRUPTED':
            raise RuntimeError('unresolved prior attempt; explicit tooling diagnosis required: '+path.name)
        retry_causes[path.name]=read(path)['error']
    retry_of={p.name:sha(p) for p in previous}
    if previous:print(json.dumps(dict(job=tag,retry_of=retry_of,retry_causes=retry_causes)),flush=True)
    start=time.monotonic();peak=live_memory(None);child=None
    wire=wire_request(REQUESTS/(tag+'.json'),job['request_sha256'])
    plain=RAW/(tag+'_'+attempt+'.stdout');err=RAW/(tag+'_'+attempt+'.stderr')
    packed=RAW/(tag+'_'+attempt+'.jsonl.gz')
    attempt_row=dict(attempt_id=attempt,job=job,retry_of=retry_of,retry_causes=retry_causes,
        wire_form=WIRE_FORM,wire_sha256=hashlib.sha256(wire).hexdigest(),
        host_command=host_command(),status='RUNNING')
    try:
        with plain.open('xb') as output,err.open('xb') as errors:
            child=subprocess.Popen(host_command(),stdin=subprocess.PIPE,stdout=output,stderr=errors)
            child.stdin.write(wire);child.stdin.close()
            while child.poll() is None:
                if time.monotonic()>=deadline:raise TimeoutError('owner wall cap reached')
                try:peak=max(peak,live_memory(child.pid))
                except RuntimeError:
                    if child.poll() is None:raise
                if plain.stat().st_size>512*1024**2:raise RuntimeError('per-fight raw stream exceeds 512 MiB local limit')
                time.sleep(.5)
            if child.returncode:raise RuntimeError('host exited '+str(child.returncode))
            if err.stat().st_size:raise RuntimeError('host stderr must be reviewed (no --metrics)')
        with plain.open('rb') as src,packed.open('xb') as out,gzip.GzipFile(fileobj=out,mode='wb') as dst:
            for chunk in iter(lambda:src.read(1024**2),b''):
                check_deadline();dst.write(chunk)
        stats=measure(packed,_DEADLINE)
        digest=sha(packed);check_deadline()
        receipt=dict(job=job,stats=stats,seconds=time.monotonic()-start,peak_rss_bytes=peak,
            ledger_sha256=sha(LEDGER),raw_sha256=digest,raw_file=packed.name,
            attempt_id=attempt,wire_form=WIRE_FORM,wire_sha256=attempt_row['wire_sha256'])
        write(RAW/(tag+'_COMPLETE.json'),receipt,exclusive=True)
        attempt_row['status']='DONE'
    except BaseException as error:
        if child is not None and child.poll() is None:child.kill();child.wait()
        attempt_row.update(status='INTERRUPTED' if isinstance(error,TimeoutError) else 'FAILED',
            error=f'{type(error).__name__}: {error}')
        raise
    finally:
        attempt_row.update(returncode=child.poll() if child else None,
            seconds=time.monotonic()-start,peak_rss_bytes=peak)
        write(RAW/(tag+'_'+attempt+'_ATTEMPT.json'),attempt_row,exclusive=True)
    return completed(job)

def records(jobs):
    return [r for job in jobs if (r:=completed(job)) is not None]

def projection(jobs,pilot):
    if len(pilot)!=18 or {r['arm'] for r in pilot}!=set(ARMS):raise RuntimeError('complete 18-fight calibration required')
    # Worst full-duration rate per arm (includes both regular and evasive/rushing C3).
    rates={a:max(r['seconds']*150/r['stats']['t_end'] for r in pilot if r['arm']==a) for a in ARMS}
    todo=[j for j in jobs if not (RAW/(j['tag']+'_COMPLETE.json')).exists()]
    return dict(remaining_fights=len(todo),projected_seconds=1.2*sum(rates[j['arm']] for j in todo),
                seconds_per_full_150s_fight=rates,safety_multiplier=1.2,workers=1,
                basis='18 measured pilot fights; worst per-arm full-150s equivalent, serial, plus 20%; not a guarantee',
                max_frame_bytes=max(r['stats']['max_frame_bytes'] for r in pilot))

def run(stage,look):
    global _DEADLINE
    _VERIFIED.clear()
    ledger=identity();cap=owner_cap();start=time.monotonic();deadline=start+cap['cap_seconds']
    run_id=secrets.token_hex(8);receipt=HERE/f'A0_RUN_{stage}_{look}_{run_id}.json'
    row=dict(status='RUNNING',stage=stage,look=look,ledger_sha256=sha(LEDGER),cap=cap,fights_started=0,fights_reused=0)
    write(receipt,row,exclusive=True)
    _DEADLINE=deadline
    try:
        process_gate(deadline)
        live_memory(None)
        pilot_jobs=[j for j in ledger['jobs'] if j['stage']=='pilot']
        jobs=pilot_jobs if stage=='pilot' else [j for j in ledger['jobs'] if j['stage']=='outcome' and j['index']<look]
        if stage=='outcome':
            pilot=records(pilot_jobs);projected=projection(jobs,pilot)
            write(HERE/f'A0_PROJECTION_{look}.json',{**projected,**cap})
            if projected['projected_seconds']>max(0,deadline-time.monotonic()):raise RuntimeError('measured projection exceeds owner cap; report to owner')
            if look==100:
                previous=read(HERE/'A0_LOOK_50.json')
                previous_jobs=[j for j in ledger['jobs'] if j['stage']=='outcome' and j['index']<50]
                verified=records(previous_jobs)
                if (previous['ledger_sha256']!=sha(LEDGER) or previous['report']!=report(verified,50) or
                    previous['completion_receipts']!={r['tag']:r['receipt_sha256'] for r in verified} or
                    previous['report']['leader_decision']!='CONTINUE_TO_100' or
                    previous['report']['unit_decision']=='REVISE_O_BEFORE_TRAINING'):
                    raise RuntimeError('verified 50-pair look must complete without stop before 100')
        for job in jobs:
            if completed(job):row['fights_reused']+=1;continue
            row['fights_started']+=1
            execute(job,deadline)
        data=records(jobs)
        result=report(data,None if stage=='pilot' else look)
        check_deadline()
        row.update(status='DONE',report=result,completed_fights=len(data),completion_receipts={r['tag']:r['receipt_sha256'] for r in data})
        if stage=='pilot':
            row['projection_50']=projection([j for j in ledger['jobs'] if j['stage']=='outcome' and j['index']<50],data)
            row['projection_100']=projection([j for j in ledger['jobs'] if j['stage']=='outcome'],data)
            row['mechanism_first']={p:result['panels'][p]['arms']['O'] for p in ('regular','C3')}
        else:
            target=HERE/f'A0_LOOK_{look}.json'
            payload=dict(ledger_sha256=sha(LEDGER),report=result,completion_receipts=row['completion_receipts'])
            if target.exists():
                if read(target)!=payload:raise RuntimeError('sequential look receipt drift')
            else:write(target,payload,exclusive=True)
    except BaseException as error:
        row.update(status='STOP_RESUMABLE',error=f'{type(error).__name__}: {error}')
        raise
    finally:
        row['seconds']=time.monotonic()-start;write(receipt,row);_DEADLINE=None
    print(json.dumps(row,indent=2))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=('prepare','pilot','run','report'))
    parser.add_argument('--look',type=int,choices=(50,100),default=50)
    args=parser.parse_args()
    with lock():
        if args.command=='prepare':prepare()
        elif args.command in ('pilot','run'):run('pilot' if args.command=='pilot' else 'outcome',args.look)
        else:
            ledger=identity();jobs=[j for j in ledger['jobs'] if j['stage']=='outcome' and j['index']<args.look]
            print(json.dumps(report(records(jobs),args.look),indent=2))

if __name__=='__main__':main()
