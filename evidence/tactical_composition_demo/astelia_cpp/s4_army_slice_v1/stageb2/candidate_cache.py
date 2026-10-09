"""Round-local compressed ragged float64 candidate cache, shared by all arms.
Exact candidate ordering/features are retained; no labels enter the builder.
"""
import hashlib,time,shutil,os
from pathlib import Path
import numpy as np
import common as c
from native_candidates import batch,unpack
ACTIVE=None
BASE_FRAMES=None
VERIFIED=set()
MAX_FIGHT_BYTES=512*1024**2

def identity(fight):
    return dict(raw_sha256=fight['raw_sha256'],builder={p:c.sha(c.HERE/p) for p in ('native_candidates.cpp','native_candidates.py','candidates.h','tools.h','candidate_cache.py','public_velocity.py','runtime.py','data.py','recording.py','streaming.py')})

def location(root,fight):
    digest=hashlib.sha256(__import__('json').dumps(identity(fight),sort_keys=True).encode()).hexdigest()
    return root/'candidates'/(digest+'.npz')

def activate(root,index,base_frames):
    global ACTIVE,BASE_FRAMES
    ACTIVE=(Path(root),{str(Path(f['raw_file']).resolve()):f for f in index['fights']});BASE_FRAMES=base_frames

def frames(path):
    key=str(Path(path).resolve());fight=ACTIVE[1].get(key) if ACTIVE else None
    if fight is None:yield from BASE_FRAMES(path);return
    cache=location(ACTIVE[0],fight);meta=c.read(cache.with_suffix('.json'))
    if meta['identity']!=identity(fight):raise RuntimeError('candidate cache identity drift')
    signature=(str(cache),meta['sha256'],cache.stat().st_mtime_ns,cache.stat().st_size)
    if signature not in VERIFIED:
        if c.sha(cache)!=meta['sha256']:raise RuntimeError('candidate cache content drift')
        VERIFIED.add(signature)
    if meta['uncompressed_bytes']>MAX_FIGHT_BYTES:raise RuntimeError('candidate fight cache exceeds 512 MiB worker bound')
    with np.load(cache,allow_pickle=False) as z:flat=z['flat'];offsets=z['offsets']
    n=0
    for n,row in enumerate(BASE_FRAMES(path),1):
        if n>=len(offsets):raise RuntimeError('candidate frame count drift')
        row['_candidate_banks']=unpack(flat[offsets[n-1]:offsets[n]])
        yield row
    if n!=fight['frames'] or len(offsets)!=n+1:raise RuntimeError('candidate frame count drift')

def prepare(root,index,base_frames,deadline,monitor=None):
    start=time.monotonic();records=[];root=Path(root);total_frames=sum(f['frames'] for f in index['fights']);mass=bytes_written=0
    for f in index['fights']:
        if time.monotonic()>=deadline:raise TimeoutError('candidate cache cap')
        if c.sha(f['raw_file'])!=f['raw_sha256']:raise RuntimeError('candidate raw drift')
        path=location(root,f);meta_path=path.with_suffix('.json');began=time.monotonic()
        if path.exists() and meta_path.exists():
            meta=c.read(meta_path)
            if meta['identity']!=identity(f) or meta['sha256']!=c.sha(path):raise RuntimeError('candidate cache drift')
        else:
            path.parent.mkdir(parents=True,exist_ok=True);offsets=[0]
            scratch=path.with_name(path.name+f'.{os.getpid()}.raw.tmp')
            tmp=path.with_name(path.name+f'.{os.getpid()}.tmp')
            try:
                with scratch.open('xb') as stream:
                    for at,row in enumerate(base_frames(f['raw_file'])):
                        if time.monotonic()>=deadline:raise TimeoutError('candidate cache cap')
                        if monitor and at%30==0:monitor.live_memory(os.getpid())
                        v=batch(row);offsets.append(offsets[-1]+len(v))
                        if offsets[-1]*8>MAX_FIGHT_BYTES:raise RuntimeError('candidate fight cache exceeds 512 MiB worker bound')
                        if offsets[-1]*8>shutil.disk_usage(root).free-2*1024**3:raise RuntimeError('candidate scratch needs 2 GiB free reserve')
                        stream.write(v.tobytes())
                if len(offsets)-1!=f['frames']:raise RuntimeError('candidate raw frame count drift')
                uncompressed=offsets[-1]*8
                flat=np.memmap(scratch,dtype=np.float64,mode='r',shape=(offsets[-1],)) if offsets[-1] else np.empty(0)
                with tmp.open('xb') as stream:np.savez_compressed(stream,flat=flat,offsets=np.asarray(offsets,dtype=np.int64))
                del flat
                os.replace(tmp,path)
            finally:
                scratch.unlink(missing_ok=True);tmp.unlink(missing_ok=True)
            meta=dict(identity=identity(f),sha256=c.sha(path),frames=f['frames'],compressed_bytes=path.stat().st_size,uncompressed_bytes=uncompressed,build_seconds=time.monotonic()-began)
            c.write(meta_path,meta,exclusive=True)
        records.append(dict(tag=f['tag'],**meta));mass+=f['frames'];bytes_written+=meta['compressed_bytes']
        # Charge already materialized bytes plus projected remainder; never fill the disk.
        projected=bytes_written/mass*total_frames
        free=shutil.disk_usage(root).free
        if projected>20*1024**3 or 1.2*(projected-bytes_written)>free-2*1024**3:raise RuntimeError('candidate disk projection exceeds 20 GiB / free disk reserve')
        remaining=1.2*(time.monotonic()-start)/mass*(total_frames-mass)
        if remaining>deadline-time.monotonic():raise RuntimeError('candidate time projection exceeds cap')
    result=dict(records=records,seconds=time.monotonic()-start,compressed_bytes=bytes_written,free_bytes=shutil.disk_usage(root).free,frames=mass,format='npz: exact float64 ragged point(2), nonzero feature tail(7), type/source(2); int64 frame offsets; one-hot feature prefix reconstructed',max_fight_bytes=MAX_FIGHT_BYTES,disk_limit_bytes=20*1024**3,reserve_bytes=2*1024**3)
    c.write(root/'CANDIDATE_CACHE.json',result);return result
