"""Fresh O full fights, sealed whole-fight splits and <=20-fight timing gate."""
import argparse
import gzip
import hashlib
import json
import os
import random
import secrets
import subprocess
import time
from pathlib import Path
from common import ARMY,BINARY,CPP,HERE,LOCAL,load,read,sha,sources,write
from jobs import admitted

def a0():return load('stagea_a0run',ARMY/'rev2/a0_run.py')

def identity():
    admission=load('stagea_build_admit',CPP/'build_admission.py');return admission.admit(BINARY)

def excluded():
    seeds=set()
    for path in CPP.rglob('*LEDGER*.json'):
        if '/build/' in str(path):continue
        row=read(path)
        for j in row.get('jobs',row.get('pairs',[])):
            if 'seed' in j:seeds.add(j['seed'])
    return seeds

def prepare():
    path=LOCAL/'DATA_LEDGER.json'
    if path.exists():return check()
    rng=random.Random(secrets.randbits(256));used=excluded();base=a0();jobs=[]
    # 180 independent training fights. Balanced C3 cells, alternating orientations.
    for split,regular,cycles in (('train',20,3),('validation',10,2),('test',10,2)):
        cells=list(base.CELLS);rng.shuffle(cells)
        sequence=[('regular','regular',i%2) for i in range(regular)]+[('C3',cell,i%2) for i in range(cycles) for cell in cells]
        rng.shuffle(sequence)
        for panel,cell,orientation in sequence:
            seed=rng.randrange(1,2**32)
            while seed in used:seed=rng.randrange(1,2**32)
            used.add(seed);tag=f'{split}_{len(jobs):04d}'
            request=base.request('O',cell,seed,orientation);request['stageA']={'collect':True};request['decisionTrace']=False
            req=LOCAL/'requests'/(tag+'.json');write(req,request,exclusive=True)
            jobs.append(dict(tag=tag,split=split,panel=panel,tactic=cell,orientation=orientation,seed=seed,request_sha256=sha(req)))
    # Twenty training-only draws cover all cells; never validation/test data.
    sample=[]
    for cell in base.CELLS:sample.append(next(j['tag'] for j in jobs if j['split']=='train' and j['panel']=='C3' and j['tactic']==cell))
    ledger=dict(schema=1,binary=identity(),sources=sources(),jobs=jobs,timing_sample=sample,fresh_entropy=True,split_unit='whole fight',leader='PARKED')
    write(path,ledger,exclusive=True);return ledger

def ledger_path():
    active=LOCAL/'DATA_RECOVERY_ACTIVE.json'
    if not active.exists():return LOCAL/'DATA_LEDGER.json'
    r=read(active)
    if sha(LOCAL/'DATA_LEDGER.json')!=r['previous_ledger_sha256']:raise RuntimeError('recovery baseline drift')
    path=LOCAL/r['ledger_file']
    if sha(path)!=r['ledger_sha256']:raise RuntimeError('recovery ledger drift')
    for name,digest in r['failed_evidence'].items():
        if sha(LOCAL/name)!=digest:raise RuntimeError('failed attempt evidence drift')
    return path

def recover_memory():
    # Explicit prospective rebind of the same sealed jobs, before any completion.
    active=LOCAL/'DATA_RECOVERY_ACTIVE.json'
    if active.exists():return check()
    old=read(LOCAL/'DATA_LEDGER.json');old_hash=sha(LOCAL/'DATA_LEDGER.json')
    if any((LOCAL/'raw'/(j['tag']+'_COMPLETE.json')).exists() for j in old['jobs']):raise RuntimeError('memory recovery requires zero completed collection fights')
    failure=LOCAL/'attempts/train_0000_9d48acc6753c473a.json'
    r=read(failure)
    first=next(j for j in old['jobs'] if j['tag']=='train_0000')
    if r['status']!='STOP_RESUMABLE' or r['error']!='RuntimeError: child exceeds 2 GiB RSS' or r['ledger_sha256']!=old_hash or r['job']!=first:
        raise RuntimeError('unexpected memory recovery baseline')
    for j in old['jobs']:
        if sha(LOCAL/'requests'/(j['tag']+'.json'))!=j['request_sha256']:raise RuntimeError('sealed request drift')
    failed=[failure,LOCAL/'raw/train_0000_9d48acc6753c473a.jsonl.stdout',LOCAL/'raw/train_0000_9d48acc6753c473a.jsonl.stderr']
    failed_hashes={str(p.relative_to(LOCAL)):sha(p) for p in failed}
    run_id=secrets.token_hex(8);path=LOCAL/('DATA_LEDGER_MEM_'+run_id+'.json')
    updated=dict(old,binary=identity(),sources=sources(),recovery=dict(reason='bounded JSON arena and streaming gzip; same sealed requests',previous_ledger_sha256=old_hash,failed_evidence=failed_hashes))
    write(path,updated,exclusive=True)
    note=dict(status='RECOVERY_REGISTERED_NO_RETRY',recovery_id=run_id,previous_ledger_sha256=old_hash,ledger_file=path.name,ledger_sha256=sha(path),failed_evidence=failed_hashes,requests_unchanged=True,fresh_attempt_ids_required=True)
    write(LOCAL/('MEMORY_RECOVERY_'+run_id+'.json'),note,exclusive=True)
    write(active,note,exclusive=True)
    return check()

def check():
    ledger=read(ledger_path())
    if ledger['sources']!=sources() or ledger['binary']!=identity():raise RuntimeError('collection source/binary drift')
    for j in ledger['jobs']:
        if sha(LOCAL/'requests'/(j['tag']+'.json'))!=j['request_sha256']:raise RuntimeError('request drift')
    return ledger

def validate_raw(path,deadline):
    # One bounded streaming reparse validates both inference/label history and A0 metrics.
    import tempfile
    from data import pack,labels
    metrics=load('stagea_a0metrics',ARMY/'rev2/a0_metrics.py');n=0;previous=None;trajectory=hashlib.sha256()
    filtered=Path(str(path)+'.validation.gz')
    try:
        with gzip.open(path,'rt') as src,gzip.open(filtered,'wt') as met:
            for line in src:
                if time.monotonic()>=deadline:raise TimeoutError('cap during raw revalidation')
                row=json.loads(line)
                if 'error' in row:raise RuntimeError('host error '+str(row['error']))
                if row.get('stageA'):
                    x,ids,enemies=pack(row,'N1');ys=labels(row,ids,enemies)
                    if len(row['labels'])!=len(ids):raise RuntimeError('label identity coverage')
                    if previous is not None and abs(row['t']-previous-row['dt'])>1e-7:raise RuntimeError('incomplete physical-tick history')
                    previous=row['t'];n+=1
                    trajectory.update(json.dumps({k:v for k,v in row.items() if k not in ('history','pairModes','labels','networkState','networkKind')},sort_keys=True,separators=(',',':')).encode())
                elif not row.get('stageAParity') and not row.get('stageAMemory'):met.write(line)
        stats=metrics.measure(filtered,deadline)
    finally:
        if filtered.exists():filtered.unlink()
    return dict(stats=stats,frames=n,trajectory_sha256=trajectory.hexdigest())

def execute(job,deadline,monitor,ledger_hash,memory_profile=False):
    path=LOCAL/'raw'/(job['tag']+'_COMPLETE.json')
    if path.exists():
        r=read(path)
        if r['job']!=job or r['ledger_sha256']!=ledger_hash or sha(LOCAL/r['raw_file'])!=r['raw_sha256']:raise RuntimeError('completed fight drift')
        checked=validate_raw(LOCAL/r['raw_file'],deadline)
        if any(r[k]!=v for k,v in checked.items()):raise RuntimeError('completion statistics drift')
        return r
    run_id=secrets.token_hex(8);raw=LOCAL/'raw'/(job['tag']+'_'+run_id+'.jsonl.gz');raw.parent.mkdir(parents=True,exist_ok=True)
    err=raw.with_suffix('.stderr');start=time.monotonic();receipt=dict(job=job,status='RUNNING',ledger_sha256=ledger_hash,attempt_id=run_id,raw_file=str(raw.relative_to(LOCAL)))
    try:
        monitor.live_memory(None)
        request_path=LOCAL/'requests'/(job['tag']+'.json')
        if sha(request_path)!=job['request_sha256']:raise RuntimeError('request drift')
        request=read(request_path)
        from streaming import stream_host
        stream_host(BINARY,request,raw,err,deadline,monitor,receipt,profile=memory_profile)
        # A0 metrics consume observer and terminal only; no duplicate plain file.
        filtered=raw.with_suffix('.metrics.gz')
        n=0;previous=None;trajectory=hashlib.sha256();memory=[]
        with gzip.open(raw,'rt') as src,gzip.open(filtered,'wt',compresslevel=1) as met:
            for line in src:
                if time.monotonic()>=deadline:raise TimeoutError('cap during validation')
                row=json.loads(line)
                if 'error' in row:raise RuntimeError('host error '+str(row['error']))
                if row.get('stageA'):
                    from data import pack,labels
                    x,ids,enemies=pack(row,'N1');labels(row,ids,enemies)
                    if previous is not None and abs(row['t']-previous-row['dt'])>1e-7:raise RuntimeError('incomplete physical-tick history')
                    previous=row['t'];n+=1;trajectory.update(json.dumps({k:v for k,v in row.items() if k not in ('history','pairModes','labels','networkState','networkKind')},sort_keys=True,separators=(',',':')).encode())
                elif row.get('stageAMemory'):
                    memory.append(row)
                    receipt['peak_rss_bytes']=max(receipt['peak_rss_bytes'],row['peak_rss_bytes'])
                elif not row.get('stageAParity'):met.write(line)
        if request.get('stageA',{}).get('collect') and not n:raise RuntimeError('missing physical-tick history')
        metrics=load('stagea_a0metrics',ARMY/'rev2/a0_metrics.py');stats=metrics.measure(filtered,deadline)
        checked=validate_raw(raw,deadline)
        if checked!=dict(stats=stats,frames=n,trajectory_sha256=trajectory.hexdigest()):raise RuntimeError('fresh completion validation mismatch')
        receipt.update(status='DONE',raw_file=str(raw.relative_to(LOCAL)),raw_sha256=sha(raw),stats=stats,seconds=time.monotonic()-start,frames=n,memory_profile=memory,trajectory_sha256=trajectory.hexdigest())
        write(path,receipt,exclusive=True);filtered.unlink()
    except BaseException as e:
        receipt.update(status='STOP_RESUMABLE',error=f'{type(e).__name__}: {e}')
        raise
    finally:write(LOCAL/'attempts'/(job['tag']+'_'+run_id+'.json'),receipt,exclusive=True)
    return receipt

def disk_projection(records,total):
    raw=max(r['uncompressed_bytes']*150/r['stats']['t_end'] for r in records)
    zipped=max(r['compressed_bytes']*150/r['stats']['t_end'] for r in records)
    return dict(full_fight_raw_bytes=raw,full_fight_gzip_bytes=zipped,total_fights=total,
                projected_raw_bytes=1.2*total*raw,projected_gzip_bytes=1.2*total*zipped,
                margin=1.2,fields_dropped=[],compression='streaming gzip level 1; 64 KiB read buffer',
                transient='one compressed observer/terminal-only validation file per active fight')

def run(sample=False):
    ledger=check();base=a0();cap=base.owner_cap();run_id=secrets.token_hex(8);result=dict(status='RUNNING',sample=sample,ledger_sha256=sha(ledger_path()),cap=cap)
    path=HERE/('COLLECT_RUN_'+run_id+'.json')
    try:
        with admitted(cap['cap_seconds']) as (deadline,monitor):
            jobs=[j for j in ledger['jobs'] if not sample or j['tag'] in ledger['timing_sample']]
            calibration=[execute(j,deadline,monitor,result['ledger_sha256']) for j in ledger['jobs'] if j['tag'] in ledger['timing_sample']]
            rates=max(r['seconds']*150/r['stats']['t_end'] for r in calibration)
            todo=[j for j in jobs if not (LOCAL/'raw'/(j['tag']+'_COMPLETE.json')).exists()]
            projection=1.2*len(todo)*rates
            write(LOCAL/'COLLECTION_PROJECTION.json',dict(sample_fights=len(calibration),remaining_fights=len(todo),projected_seconds=projection,slowest_full_fight_seconds=rates,disk=disk_projection(calibration,len(ledger['jobs']))))
            if projection>deadline-time.monotonic():raise RuntimeError('collection projection exceeds invocation owner cap')
            results=[execute(j,deadline,monitor,result['ledger_sha256']) for j in jobs]
            result.update(status='DONE',completed=len(results),completion_hashes={r['job']['tag']:sha(LOCAL/'raw'/(r['job']['tag']+'_COMPLETE.json')) for r in results})
            if not sample:
                index=dict(ledger_sha256=result['ledger_sha256'],fights=[dict(**r['job'],raw_file=r['raw_file'],raw_sha256=r['raw_sha256'],frames=r['frames'],trajectory_sha256=r['trajectory_sha256']) for r in results])
                write(LOCAL/'INDEX.json',index)
    except BaseException as e:result.update(status='STOP_RESUMABLE',error=f'{type(e).__name__}: {e}');raise
    finally:write(path,result,exclusive=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('prepare','recover-memory','sample','run','audit'));a=p.parse_args()
    if a.command=='prepare':prepare()
    elif a.command=='recover-memory':recover_memory()
    elif a.command=='audit':
        from data import audit
        if audit(read(LOCAL/'INDEX.json'))['status']!='PASS':raise SystemExit('label gate BLOCKED')
    else:run(a.command=='sample')
