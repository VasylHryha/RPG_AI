"""Sealed, sequential teacher collection. sample/collect execute; project is read-only arithmetic.
No physical evaluation occurs on import. Native fights are never launched by tests.
"""
import argparse
from collections import Counter
import fcntl
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import secrets
import signal
import shutil
import subprocess
import sys
import time
from requests import drill
from protocol import split
from project import projection
from process_gate import process_gate

HERE=Path(__file__).resolve().parent
ROOT=HERE/'_local/collection'
BINARY=HERE/'_local/build/net_host'
CAP_PATH=HERE.parent/'s4_shape_lab_v1/raw/LAB_CAP.json'
STRATA=list(itertools.product(('D1-static','D2-shellfire'),(1,2,10),(0,1)))
DISK_SAFETY_FACTOR=2
DISK_FREE_FLOOR_BYTES=5_000_000_000  # 5 GB, decimal bytes; retained after collection.

def sha(path):
    with Path(path).open('rb') as f:
        h=hashlib.sha256()
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def read(path):return json.loads(Path(path).read_bytes())
def atomic(path,payload):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp')
    with tmp.open('w') as f:
        json.dump(payload,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def cap():
    raw=CAP_PATH.read_bytes();value=json.loads(raw)
    if type(value.get('cap_seconds')) is not int or value['cap_seconds']<=0 or value.get('approved_by')!='owner' or not value.get('date'):
        raise RuntimeError('invalid owner LAB_CAP.json')
    return {**value,'path':str(CAP_PATH),'sha256':hashlib.sha256(raw).hexdigest()}

def admission():
    build=read(HERE/'BUILD.json')
    if build['status']!='PASS' or sha(BINARY)!=build['binaries']['net_host']:raise RuntimeError('binary build admission drift')
    sources=dict(build['sources']);amendment=HERE/'BUILD_TOOLING_AMENDMENT.json'
    if amendment.exists():
        update=read(amendment)
        if update['build_sha256']!=sha(HERE/'BUILD.json') or set(update['source_hashes'])!={'collection.py','test_collection.py'}:
            raise RuntimeError('invalid collection tooling build amendment')
        for name,hashes in update['source_hashes'].items():
            path=str(HERE/name)
            if sources.get(path)!=hashes['before']:raise RuntimeError('tooling build amendment baseline drift')
            sources[path]=hashes['after']
    for path,digest in {**sources,**build['reused_object_sha256']}.items():
        if sha(path)!=digest:raise RuntimeError('build source/object drift: '+path)
    files=[BINARY,HERE/'frozen/collection_CONTRACT.md',HERE/'requests.py',HERE/'collection.py',HERE/'project.py',HERE/'protocol.py',HERE/'process_gate.py']
    if amendment.exists():files.append(amendment)
    return {str(p.relative_to(HERE)):sha(p) for p in files}

def inventory(collection_entropy,reporting_entropy,count=200,sample_count=20):
    if collection_entropy==reporting_entropy:raise ValueError('collection and reporting entropy must differ')
    if not 12<=count<=200 or not 12<=sample_count<=min(20,count):raise ValueError('balanced inventory/sample limits: 12..200 / 12..20')
    used=set(range(10000));rows=[];seen=Counter()
    # Round-robin strata: every prefix at 12 or more covers all cells; imbalance <=1.
    for i in range(count):
        cell,guns,orientation=STRATA[i%12];stratum=(cell,guns,orientation);k=seen[stratum];seen[stratum]+=1
        # Last 20 of the 200 are reporting-only, independent of timing/fitting entropy.
        report=(k>=15)
        desired='report' if report else ('test' if k==0 else 'validation' if k in (1,2) else 'train')
        entropy=reporting_entropy if report else collection_entropy
        counter=0
        while True:
            digest=hashlib.sha256(f'NS1-recorded-{desired}:{entropy}:{i}:{counter}'.encode()).hexdigest()
            seed=int(digest[:8],16);group='NS1-'+digest[8:40];counter+=1
            if seed not in used and (report or split(group)==desired):break
        used.add(seed)
        request=drill(cell,guns,seed,orientation,fight=group)
        rows.append(dict(index=i,group=group,split=desired,cell=cell,guns=guns,orientation=orientation,seed=seed,sample=i<sample_count,request=request))
    return dict(version='NS1-collection-1',total=count,sample_count=sample_count,collection_entropy=collection_entropy,reporting_entropy=reporting_entropy,
                fixture_exclusion='all seeds 0..9999; fresh domain-separated 256-bit entropy; no fixture/reporting reuse',rows=rows)

def seal(sample_count):
    path=ROOT/'INVENTORY.json'
    if path.exists():
        inv=admit_inventory()
        if inv['sample_count']!=sample_count:raise RuntimeError('sealed sample count cannot change')
        return inv
    if any(ROOT.glob('*.json')):raise RuntimeError('incomplete seal; inspect existing files before recovery')
    pins=admission()
    inv=inventory(secrets.token_hex(32),secrets.token_hex(32),sample_count=sample_count)
    # All identities/splits and requests persist before a process gate or launch.
    atomic(path,inv)
    atomic(ROOT/'SEAL.json',dict(inventory_sha256=sha(path),pins=pins))
    return inv

def admit_inventory():
    seal=read(ROOT/'SEAL.json')
    if sha(ROOT/'INVENTORY.json')!=seal['inventory_sha256'] or admission()!=seal['pins']:raise RuntimeError('sealed collection admission drift')
    inv=read(ROOT/'INVENTORY.json')
    if inv!=inventory(inv['collection_entropy'],inv['reporting_entropy'],inv['total'],inv['sample_count']):raise RuntimeError('inventory derivation mismatch')
    return inv

def completed(row):
    path=ROOT/(row['group']+'.receipt.json')
    if not path.exists():return None
    receipt=read(path)
    target=ROOT/(row['group']+'.jsonl')
    partial=Path(receipt['output'])
    if receipt['inventory_sha256']!=sha(ROOT/'INVENTORY.json') or receipt['request']!=row['request']:raise RuntimeError('completed fight drift')
    if not target.exists() and partial.exists() and sha(partial)==receipt['raw_sha256']:os.replace(partial,target)
    if receipt['inventory_sha256']!=sha(ROOT/'INVENTORY.json') or receipt['request']!=row['request'] or receipt['raw_sha256']!=sha(target):
        raise RuntimeError('completed fight drift')
    return receipt

def measurements(path,row):
    """Streaming validation; memory bounded by the native 1 MiB record cap."""
    records=0;total=0;maximum=0;terminal=None;decisions=0;overflow=Counter();last_tick=0
    with path.open('rb') as f:
        while True:
            line=f.readline(1048578)
            if not line:break
            if len(line)>1048577 or not line.endswith(b'\n'):raise RuntimeError('record size/truncated line')
            v=json.loads(line)
            if terminal is not None:raise RuntimeError('data after terminal')
            if v.get('cell')!=row['cell']:raise RuntimeError('record cell mismatch')
            if v.get('terminal'):
                terminal=v;continue
            if v.get('fight')!=row['group'] or v.get('tick')!=last_tick+1:raise RuntimeError('fight/tick identity mismatch')
            last_tick=v['tick'];records+=1;total+=len(line)-1;maximum=max(maximum,len(line)-1)
            for event in v['events']:
                if event['stage']=='threat_overflow':
                    decisions+=1;overflow.update(event['value'])
    if not records or not terminal or terminal['maximum_record_bytes']!=maximum or records>4501:raise RuntimeError('missing/invalid terminal or record maximum')
    if decisions<=0:raise RuntimeError('missing per-decision threat overflow')
    return dict(record_count=records,record_bytes=total,mean_record_bytes=total/records,maximum_record_bytes=maximum,
                disk_bytes=path.stat().st_size,decision_count=decisions,threat_overflow_by_kind=dict(overflow),terminal=terminal)

def native(request,output,stderr,seconds):
    """Exact per-child CPU/max RSS from wait4; no cumulative sibling RSS subtraction."""
    start=time.monotonic()
    with output.open('wb') as out,stderr.open('wb') as err:
        p=subprocess.Popen([str(BINARY),'--collect'],stdin=subprocess.PIPE,stdout=out,stderr=err)
        timed_out=False
        try:
            p.stdin.write((json.dumps(request,allow_nan=False)+'\n').encode());p.stdin.close()
            while True:
                pid,status,usage=os.wait4(p.pid,os.WNOHANG)
                if pid:break
                if time.monotonic()-start>=seconds:
                    timed_out=True
                    try:os.kill(p.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    pid,status,usage=os.wait4(p.pid,0);break
                time.sleep(.05)
            p.returncode=os.waitstatus_to_exitcode(status)
        finally:
            if p.returncode is None:
                try:os.kill(p.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                _,status,usage=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
            out.flush();os.fsync(out.fileno())
    return dict(wall_seconds=time.monotonic()-start,cpu_seconds=usage.ru_utime+usage.ru_stime,
                rss_bytes=int(usage.ru_maxrss*(1 if sys.platform=='darwin' else 1024)),exit_code=p.returncode,timed_out=timed_out)

def execute(row,deadline):
    done=completed(row)
    if done:return done
    admit_inventory()
    remaining=min(deadline-time.monotonic(),cap()['cap_seconds']-ledger(admit_inventory())['charged_wall_seconds'])
    if remaining<=0:raise TimeoutError('local time cap exhausted')
    group=row['group'];attempts=ROOT/'attempts';attempts.mkdir(exist_ok=True)
    index=len(list(attempts.glob(group+'-*.json')))+1;prefix=attempts/f'{group}-{index:03}'
    output=prefix.with_suffix('.partial.jsonl');stderr=prefix.with_suffix('.stderr')
    atomic(prefix.with_suffix('.request.json'),row['request'])
    attempt_records=[read(p) for p in attempts.glob('*.json') if not p.name.endswith('.request.json')]
    inv=read(ROOT/'INVENTORY.json');sample_groups={r['group'] for r in inv['rows'] if r['sample']}
    if len(attempt_records)>=200 or (row['sample'] and sum(a['request']['fight'] in sample_groups for a in attempt_records)>=20):raise RuntimeError('physical launch hard cap reached, including failed attempts')
    identity=sha(ROOT/'INVENTORY.json')
    atomic(prefix.with_suffix('.json'),dict(status='RUNNING',request=row['request'],inventory_sha256=identity,started_unix=time.time()))
    stats=native(row['request'],output,stderr,remaining)
    attempt=dict(**stats,inventory_sha256=identity,request=row['request'],output=str(output),stderr=str(stderr),disk_bytes=output.stat().st_size+stderr.stat().st_size)
    atomic(prefix.with_suffix('.json'),dict(status='FAILED' if stats['exit_code'] else 'NATIVE_DONE',**attempt))
    if stats['exit_code'] or stats['timed_out']:raise RuntimeError('fight interrupted; partial/attempt preserved; resume never repeats completed fights')
    values=measurements(output,row);admit_inventory()
    target=ROOT/(group+'.jsonl')
    if target.exists():raise RuntimeError('orphan atomic output; inspect before recovery')
    receipt={**attempt,**values,'raw_sha256':sha(output),'status':'COMPLETE'}
    atomic(ROOT/(group+'.receipt.json'),receipt)
    os.replace(output,target)
    atomic(prefix.with_suffix('.json'),dict(status='COMPLETE',**attempt))
    return receipt

def ledger(inv):
    records={r['group']:completed(r) for r in inv['rows']}
    attempts=[read(p) for p in (ROOT/'attempts').glob('*.json') if not p.name.endswith('.request.json')]
    for path in (ROOT/'attempts').glob('*.json'):
        if path.name.endswith('.request.json'):continue
        a=read(path)
        if a['status'] in ('RUNNING','NATIVE_DONE'):
            group=a['request']['fight']
            if records.get(group):
                a.update(status='COMPLETE',wall_seconds=records[group]['wall_seconds'])
            elif a['status']=='NATIVE_DONE':
                row=next(r for r in inv['rows'] if r['group']==group)
                output=Path(a['output']);values=measurements(output,row)
                receipt={**a,**values,'raw_sha256':sha(output),'status':'COMPLETE'}
                atomic(ROOT/(group+'.receipt.json'),receipt)
                completed(row);records[group]=receipt;a['status']='COMPLETE'
            else:
                # An interrupted launcher has no exact child usage. Wait for heavy
                # repository processes to clear before retry; conservatively charge elapsed time.
                recovery_charge=min(cap()['cap_seconds'],max(0,time.time()-a['started_unix']))
                known_charge=sum(item.get('wall_seconds',0) for item in attempts)
                process_gate(deadline=time.monotonic()+max(0,cap()['cap_seconds']-known_charge-recovery_charge))
                a.update(status='INTERRUPTED',wall_seconds=min(cap()['cap_seconds'],max(0,time.time()-a['started_unix'])),usage_unavailable=True)
            atomic(path,a)
    attempts=[read(p) for p in (ROOT/'attempts').glob('*.json') if not p.name.endswith('.request.json')]
    value=dict(inventory_sha256=sha(ROOT/'INVENTORY.json'),complete=[g for g,r in records.items() if r],pending=[g for g,r in records.items() if not r],
               charged_wall_seconds=sum(a.get('wall_seconds',0) for a in attempts),attempts=len(attempts))
    atomic(ROOT/'LEDGER.json',value)
    return value

def sample_measurements(inv):
    records=[completed(r) for r in inv['rows'] if r['sample']]
    if not records or any(r is None for r in records):raise RuntimeError('complete sealed timing sample required')
    overflow=Counter()
    for r in records:overflow.update(r['threat_overflow_by_kind'])
    # Stratified means: sample count imbalance does not bias the 200-fight projection.
    cells={}
    for stratum in STRATA:
        rows=[v for r,v in zip([r for r in inv['rows'] if r['sample']],records) if (r['cell'],r['guns'],r['orientation'])==stratum]
        cells['|'.join(map(str,stratum))]={k:sum(v[k] for v in rows)/len(rows) for k in ('wall_seconds','cpu_seconds','disk_bytes','record_count','mean_record_bytes')}
    return dict(fights=len(records),decision_count=sum(r['decision_count'] for r in records),threat_overflow_by_kind=dict(overflow),mean_record_bytes=sum(r['record_bytes'] for r in records)/sum(r['record_count'] for r in records),maximum_record_bytes=max(r['maximum_record_bytes'] for r in records),
                maximum_rss_bytes=max(r['rss_bytes'] for r in records),strata=cells,receipt_hashes={r['group']:sha(ROOT/(r['group']+'.receipt.json')) for r in inv['rows'] if r['sample']})

def projected(inv,persist=True):
    m=sample_measurements(inv);wall=cpu=disk=0
    for row in inv['rows']:
        cell=m['strata']['|'.join(map(str,(row['cell'],row['guns'],row['orientation'])))];wall+=cell['wall_seconds'];cpu+=cell['cpu_seconds'];disk+=cell['disk_bytes']
    value=dict(status='MEASURED_SAMPLE_PROJECTION',inventory_sha256=sha(ROOT/'INVENTORY.json'),measurements=m,
               collection_wall_seconds=wall,collection_cpu_seconds=cpu,collection_disk_bytes=math.ceil(disk),local_cap=cap(),
               expected_40s=projection(40,m['mean_record_bytes'],m['maximum_record_bytes']),hard_150s=projection(150,m['mean_record_bytes'],m['maximum_record_bytes']))
    if persist:atomic(ROOT/'PROJECTION.json',value)
    return value

def resource_gate(inv):
    stored=read(ROOT/'PROJECTION.json');fresh=projected(inv,persist=False)
    if stored!=fresh:raise RuntimeError('sample or cap changed; run project again before collection')
    state=ledger(inv)
    remaining_wall=0;remaining_fights=0
    for r in inv['rows']:
        if completed(r):continue
        m=fresh['measurements']['strata']['|'.join(map(str,(r['cell'],r['guns'],r['orientation'])))];remaining_wall+=m['wall_seconds'];remaining_fights+=1
    if state['charged_wall_seconds']+remaining_wall>cap()['cap_seconds']:raise RuntimeError('projected collection exceeds owner local LAB_CAP.json; owner cap decision required')
    # Collection stores raw fights only. Converted datasets/training have their
    # own gate; reserve from the largest measured sample cell, not record caps.
    maximum_cell_disk=max(m['disk_bytes'] for m in fresh['measurements']['strata'].values())
    reserve=math.ceil(maximum_cell_disk*remaining_fights*DISK_SAFETY_FACTOR)+DISK_FREE_FLOOR_BYTES
    free=shutil.disk_usage(ROOT).free
    gate=dict(status='PASS' if free>=reserve else 'REFUSED',inventory_sha256=fresh['inventory_sha256'],
              projection_sha256=sha(ROOT/'PROJECTION.json'),maximum_cell_disk_bytes=maximum_cell_disk,
              remaining_fights=remaining_fights,disk_safety_factor=DISK_SAFETY_FACTOR,
              disk_free_floor_bytes=DISK_FREE_FLOOR_BYTES,disk_reserve_bytes=reserve,free_disk_bytes=free)
    if fresh['measurements']['maximum_rss_bytes']>512*1024**2:
        gate.update(status='REFUSED',reason='sample exceeds 512 MiB RSS allowance')
    elif free<reserve:gate['reason']='measured-size disk reserve unavailable'
    atomic(ROOT/'RESOURCE_GATE.json',gate)
    if gate['status']=='REFUSED':raise RuntimeError(gate['reason'])
    return fresh

def run(stage,fights):
    if type(fights) is not int or fights<1 or fights>(20 if stage=='sample' else 200):raise ValueError('hard fight cap')
    ROOT.mkdir(parents=True,exist_ok=True)
    with (ROOT/'RUN.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise RuntimeError('another collection invocation owns the ledger')
        inv=seal(fights) if stage=='sample' else admit_inventory()
        state=ledger(inv)
        if stage=='collect':resource_gate(inv)
        if fights>inv['total']:raise ValueError('sealed inventory cap')
        rows=[r for r in inv['rows'] if r['sample']] if stage=='sample' else inv['rows'][:fights]
        invocation_start=time.monotonic()
        deadline=invocation_start+cap()['cap_seconds']-state['charged_wall_seconds']
        for row in rows:
            if completed(row):continue
            deadline=min(deadline,invocation_start+cap()['cap_seconds']-state['charged_wall_seconds'])
            process_gate(deadline=deadline)
            deadline=min(deadline,invocation_start+cap()['cap_seconds']-state['charged_wall_seconds'])
            execute(row,deadline);ledger(inv)
        if stage=='sample':atomic(ROOT/'SAMPLE.json',sample_measurements(inv))
        print(json.dumps(ledger(inv),indent=2))

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='stage',required=True)
    for stage,n in [('sample',20),('collect',200)]:
        q=sub.add_parser(stage);q.add_argument('--fights',type=int,default=n)
    sub.add_parser('project');a=p.parse_args()
    if a.stage=='project':
        ROOT.mkdir(parents=True,exist_ok=True)
        with (ROOT/'RUN.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            print(json.dumps(projected(admit_inventory()),indent=2))
    else:run(a.stage,a.fights)
if __name__=='__main__':main()
