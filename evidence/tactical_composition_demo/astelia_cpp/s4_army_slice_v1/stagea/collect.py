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

def fix3_ledger_path():
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

# Only these Python changes are authorized by the disk-only revision. Every
# native/build/recording/request source must still match its previous identity.
DISK_SOURCE_CHANGES = ('collect.py', 'disk_policy.py', 'test_stagea_disk.py')

def disk_note():
    path=LOCAL/'DATA_DISK_RECOVERY_ACTIVE.json'
    return read(path) if path.exists() else None

def ledger_path():
    previous=fix3_ledger_path();note=disk_note()
    if note is None:return previous
    previous=LOCAL/note['previous_ledger_file']
    if sha(previous)!=note['previous_ledger_sha256']:
        raise RuntimeError('disk recovery baseline drift')
    for name,digest in note['preserved_evidence'].items():
        if sha(LOCAL/name)!=digest:raise RuntimeError('disk recovery preserved evidence drift: '+name)
    path=LOCAL/note['ledger_file']
    if sha(path)!=note['ledger_sha256']:raise RuntimeError('disk recovery ledger drift')
    return path

def completion_path(job):
    note=disk_note()
    if note and job['tag'] in note['reused'] and note['reused'][job['tag']].get('completion_file'):
        return LOCAL/note['reused'][job['tag']]['completion_file']
    if note and job['tag'] in note['resample']:
        return LOCAL/note['resample'][job['tag']]['completion_file']
    return LOCAL/'raw'/(job['tag']+'_COMPLETE.json')

def completion_identity(path,record,ledger_hash):
    if record['ledger_sha256']==ledger_hash:return
    note=disk_note()
    reuse=note and note['reused'].get(record['job']['tag'])
    if (not reuse or note['ledger_sha256']!=ledger_hash or
            record['ledger_sha256']!=reuse.get('ledger_sha256',note['previous_ledger_sha256']) or
            sha(path)!=reuse['completion_sha256']):
        raise RuntimeError('completed fight ledger drift; explicit recovery required')

def publish_recovery_marker(path,value,previous_sha256=None):
    # Both repository locks are held. Common.write fsyncs the temporary file
    # before atomic replacement; no partial JSON becomes a recovery marker.
    if path.exists():
        if previous_sha256 is None or sha(path)!=previous_sha256:
            raise RuntimeError('recovery marker drift or unregistered replacement: '+str(path))
    elif previous_sha256 is not None:raise RuntimeError('previous recovery marker missing')
    write(path,value)

def recover_disk():
    from jobs import locked
    with locked():return _recover_disk()

def _recover_disk():
    """Logged source/manifest transaction; old receipts and raw bytes never change."""
    active=disk_note()
    if active and read(ledger_path())['sources']==sources():return check()
    pending=LOCAL/'DATA_DISK_RECOVERY_PENDING.json'
    manifest=BINARY.with_suffix('.build.json')
    if not pending.exists() or (active and read(pending)['ledger_sha256']==active['ledger_sha256']):
        previous=ledger_path();old=read(previous);before=read(manifest)
        original=dict(manifest_sha256=sha(manifest),binary_sha256=sha(BINARY),
                      sources=before['source_hashes'],**{k:before[k] for k in ('engine','scope','sanitized','portable')})
        if before['schema']!=2 or before['binary_sha256']!=sha(BINARY) or old['binary']!=original:
            raise RuntimeError('disk recovery requires unchanged admitted binary/build identity')
        now=sources();allowed={str((HERE/n).relative_to(CPP)) for n in DISK_SOURCE_CHANGES}
        delta={k for k in old['sources'].keys()|now.keys() if old['sources'].get(k)!=now.get(k)}
        if not delta or not delta<=allowed:raise RuntimeError('disk recovery has unauthorized source changes')
        for name,digest in before['source_hashes'].items():
            path=Path(name) if Path(name).is_absolute() else CPP/name
            if name not in allowed and sha(path)!=digest:raise RuntimeError('disk recovery build source drift: '+name)
        for j in old['jobs']:
            if sha(LOCAL/'requests'/(j['tag']+'.json'))!=j['request_sha256']:raise RuntimeError('sealed request drift')
        # Never use development fixture completions as collection calibration.
        from recording import CADENCE
        run_id=secrets.token_hex(8);folder=LOCAL/'disk_revision'/run_id
        kept={};resample={};preserved=dict(old.get('recovery',{}).get('preserved_evidence',{}));calibration=[]
        preserved[str(previous.relative_to(LOCAL))]=sha(previous)
        previous_active_sha256=sha(LOCAL/'DATA_DISK_RECOVERY_ACTIVE.json') if active else None
        previous_pending_sha256=sha(pending) if pending.exists() else None
        for marker in (LOCAL/'DATA_DISK_RECOVERY_ACTIVE.json',pending):
            if marker.exists():
                snapshot=folder/('PREVIOUS_'+marker.name);snapshot.parent.mkdir(parents=True,exist_ok=True)
                with snapshot.open('xb') as out:out.write(marker.read_bytes())
                preserved[str(snapshot.relative_to(LOCAL))]=sha(snapshot)
        for j in old['jobs']:
            path=completion_path(j)
            if not path.exists():continue
            r=read(path);raw=LOCAL/r['raw_file']
            completion_identity(path,r,sha(previous))
            if (r['status']!='DONE' or sha(raw)!=r['raw_sha256'] or raw.stat().st_size!=r['compressed_bytes']):
                raise RuntimeError('disk recovery completion drift: '+j['tag'])
            preserved[str(path.relative_to(LOCAL))]=sha(path)
            preserved[str(raw.relative_to(LOCAL))]=sha(raw)
            request=read(LOCAL/'requests'/(j['tag']+'.json'))
            reasons=[]
            if r['job']!=j:reasons.append('request/job identity changed')
            if r.get('recording')!='STAGEASLIM1' or r.get('recording_cadence')!=CADENCE or r.get('physical_dt')!=request['options'].get('dt',1/30):
                reasons.append('recording identity changed')
            if reasons:
                resample[j['tag']]=dict(reason='; '.join(reasons),old_completion_sha256=sha(path),
                    completion_file=str((folder/'resampled'/(j['tag']+'_COMPLETE.json')).relative_to(LOCAL)))
            else:
                kept[j['tag']]=dict(completion_file=str(path.relative_to(LOCAL)),completion_sha256=sha(path),raw_sha256=r['raw_sha256'],ledger_sha256=r['ledger_sha256'],
                                   binary_sha256=original['binary_sha256'],request_sha256=j['request_sha256'],
                                   recording=r['recording'],recording_cadence=r['recording_cadence'],physical_dt=r['physical_dt'])
                if j['tag'] in old['timing_sample']:calibration.append(r)
        if active:
            for tag,row in active['resample'].items():
                if tag not in kept and tag not in resample:resample[tag]=row
        for path in sorted(HERE.glob('TESTS_STAGEA_DISK_ATTEMPT*.json')):
            preserved['../'+path.name]=sha(path)
        for path in sorted(LOCAL.glob('TEST_DISK_ATTEMPT*.*')):
            if path.is_file():preserved[str(path.relative_to(LOCAL))]=sha(path)
        for path in sorted(HERE.glob('COLLECT_RUN_*.json')):
            if read(path).get('status')=='STOP_RESUMABLE':preserved['../'+path.name]=sha(path)
        for path in sorted((LOCAL/'attempts').glob('*.json')):
            r=read(path)
            if r.get('status')!='STOP_RESUMABLE':continue
            preserved[str(path.relative_to(LOCAL))]=sha(path)
            if r.get('raw_file'):
                raw=LOCAL/r['raw_file']
                for artifact in (raw,raw.with_suffix('.stderr'),raw.with_suffix('.metrics.gz')):
                    if artifact.exists():preserved[str(artifact.relative_to(LOCAL))]=sha(artifact)
        gate=LOCAL/'COLLECTION_DISK_GATE.json'
        if gate.exists():
            snapshot=folder/gate.name;snapshot.parent.mkdir(parents=True,exist_ok=True)
            with snapshot.open('xb') as out:out.write(gate.read_bytes())
            preserved[str(snapshot.relative_to(LOCAL))]=sha(snapshot)
        from disk_policy import length_policy
        policy=length_policy()
        measured=disk_projection(calibration,len(old['jobs']),sum(j['tag'] not in kept for j in old['jobs'])) if calibration else None
        target=old.get('recovery',{}).get('collection_limit_bytes',COLLECTION_LIMIT_BYTES);cause='Retain original 4 decimal GB target: measured bound projection fits, or no compatible sample yet.'
        if measured and measured['projected_collection_bytes']>target:
            target=REVISED_COLLECTION_LIMIT_BYTES
            cause=(f"A0 look-100 nearest-rank p99 is {policy['p99_seconds']} s, with "
                   f"{policy['censored_fights']}/{policy['fights']} censored at 150 s. "
                   f"Compatible sealed samples project {measured['projected_collection_bytes']/1e9:.6f} GB; "
                   'exceeds original 4 GB. Declare 5 decimal GB; free-space formula unchanged.')
            if measured['projected_collection_bytes']>target:
                raise RuntimeError('measured projection exceeds proposed 5 GB revision; declare a new target with owner')
        if target>COLLECTION_LIMIT_BYTES and active and target==active['collection_limit_bytes']:
            cause=active['collection_limit_cause']
        if measured:measured.update(collection_limit_bytes=target,collection_limit_cause=cause)
        # Sources change prospectively; executable, build commands, objects and
        # all non-whitelisted source pins retain their exact original identities.
        old_manifest=folder/'ORIGINAL.build.json';old_manifest.parent.mkdir(parents=True,exist_ok=True)
        with old_manifest.open('xb') as out:out.write(manifest.read_bytes())
        preserved[str(old_manifest.relative_to(LOCAL))]=sha(old_manifest)
        revised=dict(before,source_hashes=dict(before['source_hashes']))
        for name in delta:revised['source_hashes'][name]=now[name]
        new_manifest=folder/'REVISED.build.json';write(new_manifest,revised,exclusive=True)
        new_binary=dict(original,manifest_sha256=sha(new_manifest),sources=revised['source_hashes'])
        recovery=dict(reason='A0 look-100 p99/censor-aware byte projection; explicit Python source revision',
            previous_ledger_file=str(previous.relative_to(LOCAL)),previous_ledger_sha256=sha(previous),
            previous_binary=original,changed_sources=sorted(delta),preserved_evidence=preserved,
            previous_active_sha256=previous_active_sha256,previous_pending_sha256=previous_pending_sha256,
            reused=kept,resample=resample,disk_policy=policy,measured_projection=measured,
            collection_limit_bytes=target,collection_limit_cause=cause)
        path=folder/'DATA_LEDGER.json'
        write(path,dict(old,binary=new_binary,sources=now,disk_policy=policy,recovery=recovery),exclusive=True)
        note=dict(status='SOURCE_REVISION_REGISTERED',recovery_id=run_id,ledger_file=str(path.relative_to(LOCAL)),
            ledger_sha256=sha(path),new_manifest_file=str(new_manifest.relative_to(LOCAL)),
            new_manifest_sha256=sha(new_manifest),requests_unchanged=True,binary_unchanged=True,**recovery)
        publish_recovery_marker(pending,note,previous_sha256=previous_pending_sha256)
    note=read(pending)
    # If interrupted after registration, resume only this exact transaction.
    if (sha(BINARY)!=note['previous_binary']['binary_sha256'] or
            sha(manifest) not in (note['previous_binary']['manifest_sha256'],note['new_manifest_sha256']) or
            sources()!=read(LOCAL/note['ledger_file'])['sources'] or
            sha(LOCAL/note['ledger_file'])!=note['ledger_sha256'] or
            sha(LOCAL/note['new_manifest_file'])!=note['new_manifest_sha256']):
        raise RuntimeError('disk recovery pending transaction drift')
    fix3_ledger_path() # Keep the entire pre-disk recovery chain verified.
    if sha(LOCAL/note['previous_ledger_file'])!=note['previous_ledger_sha256']:raise RuntimeError('disk recovery baseline drift')
    for name,digest in note['preserved_evidence'].items():
        if sha(LOCAL/name)!=digest:raise RuntimeError('disk recovery preserved evidence drift: '+name)
    for j in read(LOCAL/note['ledger_file'])['jobs']:
        if sha(LOCAL/'requests'/(j['tag']+'.json'))!=j['request_sha256']:raise RuntimeError('sealed request drift')
    write(manifest,read(LOCAL/note['new_manifest_file']))
    if identity()!=read(LOCAL/note['ledger_file'])['binary']:raise RuntimeError('disk recovery revised admission drift')
    publish_recovery_marker(LOCAL/'DATA_DISK_RECOVERY_ACTIVE.json',note,previous_sha256=note['previous_active_sha256'])
    return check()

def recover_fix3():
    if (LOCAL/'DATA_FIX3_RECOVERY_ACTIVE.json').exists():return check()
    previous=slim_ledger_path();old=read(previous)
    if any(completion_path(j).exists() for j in old['jobs']):raise RuntimeError('fix3 recovery requires zero completed collection fights')
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
    if any(completion_path(j).exists() for j in old['jobs']):raise RuntimeError('slim recovery requires zero completed collection fights')
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
    if any(completion_path(j).exists() for j in old['jobs']):raise RuntimeError('memory recovery requires zero completed collection fights')
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
    if 'disk_policy' in ledger:
        from disk_policy import length_policy
        if ledger['disk_policy']!=length_policy():raise RuntimeError('collection length policy drift')
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
    path=completion_path(job)
    request_path=LOCAL/'requests'/(job['tag']+'.json')
    if sha(request_path)!=job['request_sha256']:raise RuntimeError('request drift')
    request=read(request_path);duration=request['options']['duration'];dt=request['options'].get('dt',1/30)
    if path.exists():
        r=read(path)
        completion_identity(path,r,ledger_hash)
        if r['status']!='DONE' or r['job']!=job or sha(LOCAL/r['raw_file'])!=r['raw_sha256']:raise RuntimeError('completed fight drift')
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

COLLECTION_LIMIT_BYTES=4_000_000_000
REVISED_COLLECTION_LIMIT_BYTES=5_000_000_000
DISK_RESERVE_BYTES=5_000_000_000

def disk_projection(records,total,remaining=None):
    from recording import DROPPED
    from metrics import last_tick_time
    from disk_policy import length_policy
    policy=length_policy()
    if not records:raise RuntimeError('disk projection requires measured fights')
    import math
    if any(not math.isfinite(r['stats']['t_end']) or r['stats']['t_end']<=0 or
           not math.isfinite(r['compressed_bytes']) or r['compressed_bytes']<=0 for r in records):
        raise RuntimeError('invalid disk calibration')
    rate=max(r['compressed_bytes']/r['stats']['t_end'] for r in records)
    bounded=max(max(r['compressed_bytes'] for r in records),
                max(r['compressed_bytes']/r['stats']['t_end']*last_tick_time(policy['fight_length_bound_seconds'],r.get('physical_dt',1/30)) for r in records))
    zipped=max(r['compressed_bytes']*max(1.,last_tick_time(150,r.get('physical_dt',1/30))/r['stats']['t_end']) for r in records)
    remaining=total if remaining is None else remaining
    free=shutil.disk_usage(LOCAL).free
    return dict(full_fight_compact_bytes=zipped,total_fights=total,remaining_fights=remaining,
                projected_collection_bytes=total*bounded,bounded_fight_compact_bytes=bounded,
                measured_bytes_per_simulated_second=rate,length_policy=policy,
                worst_case_150s_projected_collection_bytes=total*zipped,
                collection_limit_bytes=(disk_note() or {}).get('collection_limit_bytes',COLLECTION_LIMIT_BYTES),
                collection_limit_cause=(disk_note() or {}).get('collection_limit_cause','Original 4 decimal GB target'),
                required_free_bytes=2*remaining*zipped+DISK_RESERVE_BYTES,
                actual_free_bytes=free,margin=2,reserve_bytes=DISK_RESERVE_BYTES,
                fields_dropped=DROPPED,compression='lossless float64 arrays with bitwise XOR deltas; streaming LZMA preset 1',
                transient='one observer/terminal-only gzip validation file per active fight')

def disk_gate(records,total,remaining):
    p=disk_projection(records,total,remaining)
    write(LOCAL/'COLLECTION_DISK_GATE.json',p)
    if p['projected_collection_bytes']>p['collection_limit_bytes']:raise RuntimeError(f"compact collection projection exceeds declared {p['collection_limit_bytes']/1e9:g} GB")
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
            def remaining():return sum(not completion_path(j).exists() for j in ledger['jobs'])
            # Before the first measurement, reserve the complete target twice plus
            # 5 GB. Afterwards every new fight uses measured duration-normalized bytes.
            if not any(completion_path(j).exists() for j in ledger['jobs']):
                if shutil.disk_usage(LOCAL).free < 2*COLLECTION_LIMIT_BYTES+DISK_RESERVE_BYTES:raise RuntimeError('initial collection disk reserve below 13 GB')
            for j in ledger['jobs']:
                if j['tag'] not in ledger['timing_sample']:continue
                if calibration:disk_gate(calibration,total,remaining())
                calibration.append(execute(j,deadline,monitor,result['ledger_sha256']))
            disk=disk_gate(calibration,total,remaining())
            rates=max(r['seconds']*150/r['stats']['t_end'] for r in calibration)
            todo=[j for j in jobs if not completion_path(j).exists()]
            projection=1.2*len(todo)*rates
            write(LOCAL/'COLLECTION_PROJECTION.json',dict(sample_fights=len(calibration),remaining_fights=len(todo),projected_seconds=projection,slowest_full_fight_seconds=rates,disk=disk))
            if projection>deadline-time.monotonic():raise RuntimeError('collection projection exceeds invocation owner cap')
            results=[]
            for j in jobs:
                disk_gate(calibration+results,total,remaining())
                results.append(execute(j,deadline,monitor,result['ledger_sha256']))
            disk_gate(calibration+results,total,remaining())
            result.update(status='DONE',completed=len(results),completion_hashes={r['job']['tag']:sha(completion_path(r['job'])) for r in results})
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
    p=argparse.ArgumentParser();p.add_argument('command',choices=('prepare','recover-memory','recover-slim','recover-fix3','recover-disk','fixture-sample','sample','run','audit','diagnostic'));p.add_argument('--tag');a=p.parse_args()
    if a.command=='prepare':prepare()
    elif a.command=='recover-memory':recover_memory()
    elif a.command=='recover-slim':recover_slim()
    elif a.command=='recover-fix3':recover_fix3()
    elif a.command=='recover-disk':recover_disk()
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
