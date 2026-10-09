"""Exact window banks in bounded chunks; full public prefixes stay intact.

Rows retain lazy handles: training.stored(list(frames)) cannot eagerly retain
whole-fight arrays. Four registered90-tick head windows share banks across arms.
"""
import hashlib,time,shutil,os
from pathlib import Path
from collections.abc import Mapping
import numpy as np
import common as c
from native_candidates import batch,unpack
ACTIVE=None
BASE_FRAMES=None
VERIFIED=set()
MAX_FIGHT_BYTES=512*1024**2 # original worker storage ceiling
MAX_CHUNK_BYTES=32*1024**2 # working arrays remain below original512MiB
LOADED=None
LAST_BANK=None

def identity(fight):
    return dict(raw_sha256=fight['raw_sha256'],builder={p:c.sha(c.HERE/p) for p in ('native_candidates.cpp','native_candidates.py','candidates.h','tools.h','movement.h','movement.py','candidate_cache.py','public_velocity.py','runtime.py','data.py','recording.py','streaming.py','training.py')})

def location(root,fight):
    digest=hashlib.sha256(__import__('json').dumps(identity(fight),sort_keys=True).encode()).hexdigest()
    return root/'candidates'/(digest+'.npz')

def selected_ticks(length):
    from training import selected_starts,WINDOW
    return sorted({tick for at in selected_starts(length,4) for tick in range(at,min(length,at+WINDOW))})

def activate(root,index,base_frames):
    global ACTIVE,BASE_FRAMES,LOADED,LAST_BANK
    ACTIVE=(Path(root),{str(Path(f['raw_file']).resolve()):f for f in index['fights']});BASE_FRAMES=base_frames
    LOADED=LAST_BANK=None

def validate_chunk(root,record):
    path=root/record['file'];signature=(str(path),record['sha256'],path.stat().st_mtime_ns,path.stat().st_size)
    if record['uncompressed_bytes']>MAX_CHUNK_BYTES:raise RuntimeError('candidate chunk exceeds worker bound')
    if signature not in VERIFIED:
        if c.sha(path)!=record['sha256']:raise RuntimeError('candidate cache content drift')
        VERIFIED.add(signature)
    return path,signature

def load_chunk(root,record):
    global LOADED,LAST_BANK
    path,signature=validate_chunk(root,record)
    if LOADED is not None and LOADED[0]==signature:return LOADED[1:]
    LOADED=LAST_BANK=None
    with np.load(path,allow_pickle=False) as z:bits=z['flat'];offsets=z['offsets']
    if bits.dtype!=np.uint64 or offsets.dtype!=np.int64 or bits.ndim!=1 or offsets.ndim!=1 or bits.nbytes!=record['uncompressed_bytes'] or len(offsets)!=len(record['ticks'])+1 or offsets[0]!=0 or offsets[-1]!=len(bits) or np.any(np.diff(offsets)<0):raise RuntimeError('candidate chunk schema drift')
    previous=None
    for i in range(len(offsets)-1):
        v=bits[offsets[i]:offsets[i+1]]
        if previous is not None and len(v)==len(previous):np.bitwise_xor(v,previous,out=v)
        previous=v
    LOADED=(signature,bits.view(np.float64),offsets)
    return LOADED[1:]

class LazyBank(Mapping):
    """No arrays retained by rows: one shared chunk and one shared frame bank."""
    def __init__(self,root,record,index):self.root,self.record,self.index=root,record,index
    def values_for_frame(self):
        global LAST_BANK
        flat,offsets=load_chunk(self.root,self.record)
        key=(LOADED[0],self.index)
        if LAST_BANK is None or LAST_BANK[0]!=key:LAST_BANK=(key,unpack(flat[offsets[self.index]:offsets[self.index+1]]))
        return LAST_BANK[1]
    def __getitem__(self,key):return self.values_for_frame()[key]
    def __iter__(self):return iter(self.values_for_frame())
    def __len__(self):return len(self.values_for_frame())

def frames(path):
    key=str(Path(path).resolve());fight=ACTIVE[1].get(key) if ACTIVE else None
    if fight is None:yield from BASE_FRAMES(path);return
    root=ACTIVE[0];cache=location(root,fight);meta=c.read(cache.with_suffix('.json'))
    if meta['identity']!=identity(fight) or meta['schema']!=2 or meta['frames']!=fight['frames']:raise RuntimeError('candidate cache identity drift')
    expected=selected_ticks(fight['frames']);lookup={}
    for record in meta['chunks']:
        validate_chunk(root,record)
        for i,tick in enumerate(record['ticks']):
            if tick in lookup:raise RuntimeError('duplicate candidate frame')
            lookup[tick]=(record,i)
    if sorted(lookup)!=expected or meta['cached_frames']!=len(expected) or meta['uncompressed_bytes']!=sum(q['uncompressed_bytes'] for q in meta['chunks']):raise RuntimeError('candidate window coverage drift')
    n=0
    for n,row in enumerate(BASE_FRAMES(path),1):
        if n-1 in lookup:
            record,i=lookup[n-1];row['_candidate_banks']=LazyBank(root,record,i)
        yield row
    if n!=fight['frames']:raise RuntimeError('candidate frame count drift')

def prepare(root,index,base_frames,deadline,monitor=None):
    start=time.monotonic();records=[];root=Path(root);total_frames=sum(f['frames'] for f in index['fights']);mass=bytes_written=cached_frames=0
    for f in index['fights']:
        if time.monotonic()>=deadline:raise TimeoutError('candidate cache cap')
        if c.sha(f['raw_file'])!=f['raw_sha256']:raise RuntimeError('candidate raw drift')
        path=location(root,f);meta_path=path.with_suffix('.json');began=time.monotonic();ticks=selected_ticks(f['frames'])
        if meta_path.exists():
            meta=c.read(meta_path)
            if meta['schema']!=2 or meta['identity']!=identity(f) or [tick for q in meta['chunks'] for tick in q['ticks']]!=ticks:raise RuntimeError('candidate cache drift')
            for q in meta['chunks']:validate_chunk(root,q)
        else:
            path.parent.mkdir(parents=True,exist_ok=True);chunks=[];values=[];offsets=[0];chunk_ticks=[];previous=None;n=0
            def flush():
                nonlocal values,offsets,chunk_ticks,previous
                if not chunk_ticks:return
                destination=path if not chunks else path.with_name(path.stem+f'.part{len(chunks):04d}.npz')
                tmp=destination.with_name(destination.name+f'.{os.getpid()}.tmp')
                try:
                    with tmp.open('xb') as stream:np.savez_compressed(stream,flat=np.concatenate(values),offsets=np.asarray(offsets,dtype=np.int64))
                    os.replace(tmp,destination)
                finally:
                    if tmp.exists():tmp.unlink()
                chunks.append(dict(file=str(destination.relative_to(root)),sha256=c.sha(destination),ticks=chunk_ticks,uncompressed_bytes=offsets[-1]*8,compressed_bytes=destination.stat().st_size))
                values=[];offsets=[0];chunk_ticks=[];previous=None
            wanted=set(ticks)
            for n,row in enumerate(base_frames(f['raw_file']),1):
                if time.monotonic()>=deadline:raise TimeoutError('candidate cache cap')
                if monitor and n%30==0:monitor.live_memory(os.getpid())
                if n-1 not in wanted:continue
                v=batch(row);bits=v.view(np.uint64)
                if bits.nbytes>MAX_CHUNK_BYTES:raise RuntimeError('candidate frame exceeds chunk bound')
                if offsets[-1]*8+bits.nbytes>MAX_CHUNK_BYTES:flush()
                if offsets[-1]*8+bits.nbytes>shutil.disk_usage(root).free-2*1024**3:raise RuntimeError('candidate scratch needs 2 GiB free reserve')
                encoded=np.bitwise_xor(bits,previous) if previous is not None and len(bits)==len(previous) else bits.copy()
                values.append(encoded);offsets.append(offsets[-1]+len(bits));chunk_ticks.append(n-1);previous=bits
            if n!=f['frames']:raise RuntimeError('candidate raw frame count drift')
            flush()
            meta=dict(schema=2,identity=identity(f),frames=f['frames'],cached_frames=len(ticks),chunks=chunks,compressed_bytes=sum(q['compressed_bytes'] for q in chunks),uncompressed_bytes=sum(q['uncompressed_bytes'] for q in chunks),build_seconds=time.monotonic()-began,selection='four registered90-tick windows; full physical prefix retained',encoding='xor_u64_v1: previous original bits when flat lengths match; reset per chunk')
            c.write(meta_path,meta,exclusive=True)
        records.append(dict(tag=f['tag'],**meta));mass+=f['frames'];cached_frames+=meta['cached_frames'];bytes_written+=meta['compressed_bytes']
        projected=bytes_written/mass*total_frames;free=shutil.disk_usage(root).free
        if projected>20*1024**3 or 1.2*(projected-bytes_written)>free-2*1024**3:raise RuntimeError('candidate disk projection exceeds 20 GiB / free disk reserve')
        remaining=1.2*(time.monotonic()-start)/mass*(total_frames-mass)
        if remaining>deadline-time.monotonic():raise RuntimeError('candidate time projection exceeds cap')
    result=dict(records=records,seconds=time.monotonic()-start,compressed_bytes=bytes_written,free_bytes=shutil.disk_usage(root).free,frames=mass,cached_frames=cached_frames,format='schema2: exact float64 banks, XOR uint64 chunks; lazy handles; four registered head windows only',max_chunk_bytes=MAX_CHUNK_BYTES,worker_storage_ceiling_bytes=MAX_FIGHT_BYTES,disk_limit_bytes=20*1024**3,reserve_bytes=2*1024**3)
    c.write(root/'CANDIDATE_CACHE.json',result);return result
