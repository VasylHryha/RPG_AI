"""Fresh O full fights, sealed whole-fight splits and <=20-fight timing gate."""
import argparse
import gzip
import hashlib
import json
import os
import random
import shutil
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

def memory_ledger_path():
    active=LOCAL/'DATA_RECOVERY_ACTIVE.json'
    if not active.exists():return LOCAL/'DATA_LEDGER.json'
    r=read(active)
    if sha(LOCAL/'DATA_LEDGER.json')!=r['previous_ledger_sha256']:raise RuntimeError('recovery baseline drift')
    path=LOCAL/r['ledger_file']
    if sha(path)!=r['ledger_sha256']:raise RuntimeError('recovery ledger drift')
    for name,digest in r['failed_evidence'].items():
        if sha(LOCAL/name)!=digest:raise RuntimeError('failed attempt evidence drift')
    return path

def slim_ledger_path():
    previous=memory_ledger_path()
    active=LOCAL/'DATA_SLIM_RECOVERY_ACTIVE.json'
    if not active.exists():return previous
    r=read(active)
    if str(previous.relative_to(LOCAL))!=r['previous_ledger_file'] or sha(previous)!=r['previous_ledger_sha256']:raise RuntimeError('slim recovery baseline drift')
    for name,digest in r['failed_evidence'].items():
        if sha(LOCAL/name)!=digest:raise RuntimeError('failed attempt evidence drift')
    path=LOCAL/r['ledger_file']
    if sha(path)!=r['ledger_sha256']:raise RuntimeError('slim recovery ledger drift')
    return path

def ledger_path():
    previous=slim_ledger_path()
    active=LOCAL/'DATA_FIX3_RECOVERY_ACTIVE.json'
    if not active.exists():return previous
    r=read(active)
    if str(previous.relative_to(LOCAL))!=r['previous_ledger_file'] or sha(previous)!=r['previous_ledger_sha256']:raise RuntimeError('fix3 recovery baseline drift')
    for name,digest in r['failed_evidence'].items():
        if sha(LOCAL/name)!=digest:raise RuntimeError('failed attempt evidence drift')
    path=LOCAL/r['ledger_file']
    if sha(path)!=r['ledger_sha256']:raise RuntimeError('fix3 recovery ledger drift')
    return path

def recover_fix3():
    if (LOCAL/'DATA_FIX3_RECOVERY_ACTIVE.json').exists():return check()
    previous=slim_ledger_path();old=read(previous)
    if any((LOCAL/'raw'/(j['tag']+'_COMPLETE.json')).exists() for j in old['jobs']):raise RuntimeError('fix3 recovery requires zero completed collection fights')
    for j in old['jobs']:
        if sha(LOCAL/'requests'/(j['tag']+'.json'))!=j['request_sha256']:raise RuntimeError('sealed request drift')
    failed=dict(old.get('recovery',{}).get('failed_evidence',{}))
    for p in sorted((LOCAL/'attempts').glob('*.json')):
        attempt=read(p)
        if attempt.get('status')!='STOP_RESUMABLE':continue
        failed[str(p.relative_to(LOCAL))]=sha(p)
        if attempt.get('raw_file'):
            raw=LOCAL/attempt['raw_file']
            for artifact in (raw,raw.with_suffix('.stderr'),raw.with_suffix('.metrics.gz')):
                if artifact.exists():failed[str(artifact.relative_to(LOCAL))]=sha(artifact)
    for p in HERE.glob('COLLECT_RUN_*.json'):
        if read(p).get('status')=='STOP_RESUMABLE':failed['../'+p.name]=sha(p)
    run_id=secrets.token_hex(8);path=LOCAL/('DATA_LEDGER_FIX3_'+run_id+'.json')
    from recording import CADENCE
    recovery=dict(reason='physical tick starts at dt after native clock advance; validation and fixture launch correction',previous_ledger_file=str(previous.relative_to(LOCAL)),previous_ledger_sha256=sha(previous),failed_evidence=failed)
    write(path,dict(old,binary=identity(),sources=sources(),recording_cadence=CADENCE,recovery=recovery),exclusive=True)
    note=dict(status='RECOVERY_REGISTERED_NO_RETRY',recovery_id=run_id,ledger_file=path.name,ledger_sha256=sha(path),requests_unchanged=True,fresh_attempt_ids_required=True,**recovery)
    write(LOCAL/('FIX3_RECOVERY_'+run_id+'.json'),note,exclusive=True)
    write(LOCAL/'DATA_FIX3_RECOVERY_ACTIVE.json',note,exclusive=True)
    return check()

def recover_slim():
    if (LOCAL/'DATA_SLIM_RECOVERY_ACTIVE.json').exists():return check()
    previous=memory_ledger_path();old=read(previous)
    if any((LOCAL/'raw'/(j['tag']+'_COMPLETE.json')).exists() for j in old['jobs']):raise RuntimeError('slim recovery requires zero completed collection fights')
    for j in old['jobs']:
        if sha(LOCAL/'requests'/(j['tag']+'.json'))!=j['request_sha256']:raise RuntimeError('sealed request drift')
    failed=dict(old.get('recovery',{}).get('failed_evidence',{}))
    # Preserve failed collection and development-host attempts, including any
    # transient metric file left by the old failed validation.
    for p in sorted((LOCAL/'attempts').glob('*.json')):
        attempt=read(p)
        if attempt.get('status')!='STOP_RESUMABLE':continue
        failed[str(p.relative_to(LOCAL))]=sha(p)
        if attempt.get('raw_file'):
            raw=LOCAL/attempt['raw_file']
            for artifact in (raw,raw.with_suffix('.stderr'),raw.with_suffix('.metrics.gz')):
                if artifact.exists():failed[str(artifact.relative_to(LOCAL))]=sha(artifact)
    run_id=secrets.token_hex(8);path=LOCAL/('DATA_LEDGER_SLIM_'+run_id+'.json')
    recovery=dict(reason='native last-tick boundary and lossless compact binary; same sealed requests',previous_ledger_file=str(previous.relative_to(LOCAL)),previous_ledger_sha256=sha(previous),failed_evidence=failed)
    write(path,dict(old,binary=identity(),sources=sources(),recording='STAGEASLIM1 float64 lzma1',recovery=recovery),exclusive=True)
    note=dict(status='RECOVERY_REGISTERED_NO_RETRY',recovery_id=run_id,ledger_file=path.name,ledger_sha256=sha(path),requests_unchanged=True,fresh_attempt_ids_required=True,**recovery)
    write(LOCAL/('SLIM_RECOVERY_'+run_id+'.json'),note,exclusive=True)
    write(LOCAL/'DATA_SLIM_RECOVERY_ACTIVE.json',note,exclusive=True)
    return check()

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

def validate_raw(path,deadline,duration=150,dt=1/30):
    # One bounded reparse validates inference/labels, physical history and metrics.
    from data import pack,labels
    from recording import rows,PhysicalTicks
    import metrics
    ticks=PhysicalTicks(dt);parity_ticks=PhysicalTicks(dt);pending_parity=None;trajectory=hashlib.sha256();observer_steps=0
    filtered=Path(str(path)+'.validation.gz');memory=[]
    try:
        with gzip.open(filtered,'wt',compresslevel=1) as met:
            for row in rows(path):
                if time.monotonic()>=deadline:raise TimeoutError('cap during raw revalidation')
                if 'error' in row:raise RuntimeError('host error '+str(row['error']))
                if row.get('stageA'):
                    ticks.add(row)
                    x,ids,enemies=pack(row,'N1');labels(row,ids,enemies)
                    if len(row['labels'])!=len(ids) or len({r['id'] for r in row['labels']})!=len(ids):raise RuntimeError('label identity coverage')
                    if parity_ticks.count:
                        public={k:v for k,v in row.items() if k not in ('labels','networkState','networkKind')}
                        if pending_parity!=public:raise RuntimeError('parity/recorded input mismatch')
                        pending_parity=None
                    trajectory.update(json.dumps({k:v for k,v in row.items() if k not in ('history','pairModes','labels','networkState','networkKind')},sort_keys=True,separators=(',',':')).encode())
                elif row.get('stageAMemory'):memory.append(row)
                elif row.get('stageAParity'):
                    if pending_parity is not None:raise RuntimeError('missing collected parity tick')
                    parity_ticks.add(row['input']);pending_parity=row['input']
                else:
                    if row.get('observerV1'):observer_steps=row['step']
                    met.write(json.dumps(row,separators=(',',':'))+'\n')
        stats=metrics.measure(filtered,deadline,duration=duration,dt=dt)
        ticks.finish(stats['t_end'])
        parity_ticks.finish(stats['t_end'])
        if ticks.count and ticks.count!=observer_steps:raise RuntimeError('incomplete physical-tick history')
        if parity_ticks.count and (parity_ticks.count!=ticks.count or pending_parity is not None):raise RuntimeError('incomplete parity history')
    finally:
        if filtered.exists():filtered.unlink()
    return dict(stats=stats,frames=ticks.count,trajectory_sha256=trajectory.hexdigest(),memory_profile=memory)

def execute(job,deadline,monitor,ledger_hash,memory_profile=False,full_detail=False):
    path=LOCAL/'raw'/(job['tag']+'_COMPLETE.json')
    request_path=LOCAL/'requests'/(job['tag']+'.json')
    if sha(request_path)!=job['request_sha256']:raise RuntimeError('request drift')
    request=read(request_path);duration=request['options']['duration'];dt=request['options'].get('dt',1/30)
    if path.exists():
        r=read(path)
        if r['job']!=job or r['ledger_sha256']!=ledger_hash or sha(LOCAL/r['raw_file'])!=r['raw_sha256']:raise RuntimeError('completed fight drift')
        checked=validate_raw(LOCAL/r['raw_file'],deadline,duration,dt)
        if any(r[k]!=v for k,v in checked.items()):raise RuntimeError('completion statistics drift')
        return r
    # Outcome/network/parity fixtures retain complete diagnostics; the sealed O
    # dataset and maximum-size memory fixture use compact recording by default.
    compact=not full_detail and not request.get('stageA',{}).get('weights') and job.get('split')!='outcome'
    run_id=secrets.token_hex(8);suffix='.slim.xz' if compact else '.jsonl.gz'
    raw=LOCAL/'raw'/(job['tag']+'_'+run_id+suffix);raw.parent.mkdir(parents=True,exist_ok=True)
    err=raw.with_suffix('.stderr');start=time.monotonic();receipt=dict(job=job,status='RUNNING',ledger_sha256=ledger_hash,attempt_id=run_id,raw_file=str(raw.relative_to(LOCAL)),recording='STAGEASLIM1' if compact else 'full-detail JSON',physical_dt=dt,recording_cadence=__import__('recording').CADENCE)
    try:
        monitor.live_memory(None)
        from streaming import stream_host
        stream_host(BINARY,request,raw,err,deadline,monitor,receipt,profile=memory_profile,compact=compact)
        checked=validate_raw(raw,deadline,duration,dt)
        if request.get('stageA',{}).get('collect') and not checked['frames']:raise RuntimeError('missing physical-tick history')
        for row in checked['memory_profile']:receipt['peak_rss_bytes']=max(receipt['peak_rss_bytes'],row['peak_rss_bytes'])
        receipt.update(status='DONE',raw_sha256=sha(raw),seconds=time.monotonic()-start,**checked)
        write(path,receipt,exclusive=True)
    except BaseException as e:
        receipt.update(status='STOP_RESUMABLE',error=f'{type(e).__name__}: {e}')
        raise
    finally:write(LOCAL/'attempts'/(job['tag']+'_'+run_id+'.json'),receipt,exclusive=True)
    return receipt

# Claude 2026-10-09: declared target raised 4 -> 5 GB. The projection scales every sampled fight to a
# full 150 s (worst case; measured fights end ~45 s, ~4.5 MB each); it read 4.23 GB. The free-space gate
# (measured x remaining x 2 + 5 GB vs actual free) is unchanged and passes.
COLLECTION_LIMIT_BYTES=5_000_000_000
DISK_RESERVE_BYTES=5_000_000_000

def disk_projection(records,total,remaining=None):
    from recording import DROPPED
    from metrics import last_tick_time
    zipped=max(r['compressed_bytes']*max(1.,last_tick_time(150,r.get('physical_dt',1/30))/r['stats']['t_end']) for r in records)
    remaining=total if remaining is None else remaining
    free=shutil.disk_usage(LOCAL).free
    return dict(full_fight_compact_bytes=zipped,total_fights=total,remaining_fights=remaining,
                projected_collection_bytes=total*zipped,required_free_bytes=2*remaining*zipped+DISK_RESERVE_BYTES,
                actual_free_bytes=free,margin=2,reserve_bytes=DISK_RESERVE_BYTES,
                fields_dropped=DROPPED,compression='lossless float64 arrays with bitwise XOR deltas; streaming LZMA preset 1',
                transient='one observer/terminal-only gzip validation file per active fight')

def disk_gate(records,total,remaining):
    p=disk_projection(records,total,remaining)
    write(LOCAL/'COLLECTION_DISK_GATE.json',p)
    if p['projected_collection_bytes']>COLLECTION_LIMIT_BYTES:raise RuntimeError('compact collection projection exceeds 5 GB')
    if p['required_free_bytes']>p['actual_free_bytes']:raise RuntimeError('collection disk gate: measured bytes/fight x remaining x 2 + 5 GB exceeds free space')
    return p

def run(sample=False):
    ledger=check();base=a0();cap=base.owner_cap();run_id=secrets.token_hex(8);result=dict(status='RUNNING',sample=sample,ledger_sha256=sha(ledger_path()),cap=cap)
    path=HERE/('COLLECT_RUN_'+run_id+'.json')
    try:
        with admitted(cap['cap_seconds']) as (deadline,monitor):
            jobs=[j for j in ledger['jobs'] if not sample or j['tag'] in ledger['timing_sample']]
            calibration=[]
            total=len(ledger['jobs'])
            def remaining():return sum(not (LOCAL/'raw'/(j['tag']+'_COMPLETE.json')).exists() for j in ledger['jobs'])
            # Before the first measurement, reserve the complete target twice plus
            # 5 GB. Afterwards every new fight uses measured duration-normalized bytes.
            if not any((LOCAL/'raw'/(j['tag']+'_COMPLETE.json')).exists() for j in ledger['jobs']):
                if shutil.disk_usage(LOCAL).free < 2*COLLECTION_LIMIT_BYTES+DISK_RESERVE_BYTES:raise RuntimeError('initial collection disk reserve below 15 GB')
            for j in ledger['jobs']:
                if j['tag'] not in ledger['timing_sample']:continue
                if calibration:disk_gate(calibration,total,remaining())
                calibration.append(execute(j,deadline,monitor,result['ledger_sha256']))
            disk=disk_gate(calibration,total,remaining())
            rates=max(r['seconds']*150/r['stats']['t_end'] for r in calibration)
            todo=[j for j in jobs if not (LOCAL/'raw'/(j['tag']+'_COMPLETE.json')).exists()]
            projection=1.2*len(todo)*rates
            write(LOCAL/'COLLECTION_PROJECTION.json',dict(sample_fights=len(calibration),remaining_fights=len(todo),projected_seconds=projection,slowest_full_fight_seconds=rates,disk=disk))
            if projection>deadline-time.monotonic():raise RuntimeError('collection projection exceeds invocation owner cap')
            results=[]
            for j in jobs:
                disk_gate(calibration+results,total,remaining())
                results.append(execute(j,deadline,monitor,result['ledger_sha256']))
            disk_gate(calibration+results,total,remaining())
            result.update(status='DONE',completed=len(results),completion_hashes={r['job']['tag']:sha(LOCAL/'raw'/(r['job']['tag']+'_COMPLETE.json')) for r in results})
            if not sample:
                index=dict(ledger_sha256=result['ledger_sha256'],fights=[dict(**r['job'],raw_file=r['raw_file'],raw_sha256=r['raw_sha256'],frames=r['frames'],trajectory_sha256=r['trajectory_sha256']) for r in results])
                write(LOCAL/'INDEX.json',index)
    except BaseException as e:result.update(status='STOP_RESUMABLE',error=f'{type(e).__name__}: {e}');raise
    finally:write(path,result,exclusive=True)

def diagnostic(tag):
    # A handful of separately named full-detail copies; sealed requests and
    # collection completions never change or enter the training index.
    ledger=check()
    if sum(1 for p in (LOCAL/'attempts').glob('diagnostic_*.json'))>=3:raise RuntimeError('three diagnostic attempts already recorded')
    job=dict(next(j for j in ledger['jobs'] if j['tag']==tag))
    original=LOCAL/'requests'/(tag+'.json')
    job.update(tag='diagnostic_'+secrets.token_hex(8),split='diagnostic')
    destination=LOCAL/'requests'/(job['tag']+'.json')
    destination.write_bytes(original.read_bytes())
    if sha(destination)!=job['request_sha256']:raise RuntimeError('diagnostic request copy drift')
    with admitted(a0().owner_cap()['cap_seconds']) as (deadline,monitor):
        if shutil.disk_usage(LOCAL).free<DISK_RESERVE_BYTES+2*1024**3:raise RuntimeError('diagnostic disk reserve')
        return execute(job,deadline,monitor,sha(ledger_path()),full_detail=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('prepare','recover-memory','recover-slim','recover-fix3','fixture-sample','sample','run','audit','diagnostic'));p.add_argument('--tag');a=p.parse_args()
    if a.command=='prepare':prepare()
    elif a.command=='recover-memory':recover_memory()
    elif a.command=='recover-slim':recover_slim()
    elif a.command=='recover-fix3':recover_fix3()
    elif a.command=='fixture-sample':
        from fixture_host import sample
        sample()
    elif a.command=='diagnostic':
        if not a.tag:p.error('diagnostic requires --tag from the sealed ledger')
        diagnostic(a.tag)
    elif a.command=='audit':
        from data import audit
        if audit(read(LOCAL/'INDEX.json'))['status']!='PASS':raise SystemExit('label gate BLOCKED')
    else:run(a.command=='sample')
