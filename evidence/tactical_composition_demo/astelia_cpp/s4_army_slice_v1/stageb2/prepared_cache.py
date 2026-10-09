"""Versioned, bounded float32 training inputs; raw-only float64 parity.

Every public physical row is packed once. Only the four declared head windows
store native banks, hierarchy, masks and static nearest labels. N2's drift-based
movement nearest label remains weight-dependent and is never frozen here.
"""
import gzip, hashlib, json, os, shutil, time
from pathlib import Path
import numpy as np
import torch
import common as c
SCHEMA=11
MAX_CHUNK_BYTES=64*1024**2
DISK_LIMIT_BYTES=5_000_000_000
ACTIVE=None
META_HASHES={}
BASE_FRAMES=None
LOADED=None
VERIFIED=set()
LAST=None

def identity(fight):
    names=('prepared_cache.py','candidate_cache.py','native_candidates.py','native_candidates.cpp',
           'candidates.h','tools.h','movement.h','movement.py','hierarchy.py','data.py',
           'public_velocity.py','runtime.py','recording.py','training.py','models.py',
           'candidates.py','requirements.lock','cache_codec.py','cache_codec.cpp','native_cache_codec.py')
    return dict(schema=SCHEMA,raw_sha256=fight['raw_sha256'],frames=fight['frames'],
                builder={p:c.sha(c.HERE/p) for p in names})

def location(root,fight):
    key=hashlib.sha256(json.dumps(identity(fight),sort_keys=True).encode()).hexdigest()
    return Path(root)/'prepared'/(key+'.json')

def selected_ticks(length):
    from candidate_cache import selected_ticks as selected
    return selected(length)

def build(row,heads):
    from data import pack,labels
    from native_candidates import packet,batch_packet,unpack,packed
    from hierarchy import partition_batch
    inputs,ids,enemies=pack(row,'N1',with_candidates=False)
    arrays={k:np.asarray(v,dtype=np.int64 if k in ('own','enemy','assignments') else np.float32) for k,v in inputs.items()}
    arrays['ids']=np.asarray(ids,dtype=np.int64);arrays['enemies']=np.asarray(enemies,dtype=np.int64)
    labs=labels(row,ids,enemies)
    for key in ('move','aim','mult','fire','target','aim_mask','ready','release'):
        v=np.asarray([l[key] for l in labs],dtype=np.float32)
        if key in ('move','aim'):v=v.reshape(-1,2)
        arrays['label_'+key]=v
    arrays['label_role']=np.asarray([('melee','ranged','artillery').index(l['role']) for l in labs],dtype=np.int8)
    # Graph arithmetic uses exactly the training dtype and PyTorch kernels.
    pos=torch.from_numpy(arrays['pos']);d=pos[None,:,:]-pos[:,None,:]
    radius=torch.linalg.vector_norm(d,dim=-1)/100
    order=torch.argsort(radius+torch.eye(len(ids))*1e6,dim=-1,stable=True)[:,:8]
    mask=(radius.gather(1,order)<3)&(order!=torch.arange(len(ids))[:,None])
    arrays.update(graph_order=order.numpy(),graph_mask=mask.numpy(),graph_edge_radius=radius.gather(1,order).numpy(),graph_edge_delta=d[torch.arange(len(ids))[:,None],order].numpy())
    if heads:
        p=packet(row);arrays['native_packet']=p
        banks=packed(unpack(batch_packet(p)),ids)
        scale=np.asarray([row['width'],row['height']],dtype=np.float32)
        for head in ('aim','move'):
            table,mapping=partition_batch(banks[head+'_features'],banks[head+'_valid'],head)
            # Round only at the same float64->float32 boundary as training.tensor.
            arrays[head+'_points']=banks[head+'_points'].astype(np.float32)
            arrays[head+'_codec_points']=banks[head+'_points']
            arrays[head+'_numeric']=banks[head+'_features'][:,:,11:18].astype(np.float32)
            typelist=np.array(list(range(11))+list(range(18,26)))
            types=typelist[banks[head+'_features'][:,:,typelist].argmax(-1)]
            arrays[head+'_types']=types.astype(np.int8)
            arrays[head+'_valid']=banks[head+'_valid'].astype(np.bool_)
            arrays[head+'_sources']=banks[head+'_sources'].astype(np.int16)
            arrays[head+'_members']=table.astype(np.int16)
            arrays[head+'_mapping']=mapping.astype(np.int16)
            teacher=arrays['label_'+head]*scale
            arrays['teacher_'+head]=teacher
            delta=torch.from_numpy(teacher)[:,None,:]-torch.from_numpy(arrays[head+'_points'])
            nearest=delta.square().sum(-1).masked_fill(~torch.from_numpy(arrays[head+'_valid']),torch.inf).argmin(-1)
            arrays[head+'_nearest']=nearest.numpy()
    return arrays

def encode(arrays,history=None):
    from cache_codec import encode_arrays
    return encode_arrays(arrays,{} if history is None else history)

def verify(root,record):
    path=root/record['file'];st=path.stat()
    key=(str(path),record['sha256'],st.st_mtime_ns,st.st_size)
    if record['uncompressed_bytes']>MAX_CHUNK_BYTES:raise RuntimeError('prepared chunk exceeds bound')
    if key not in VERIFIED:
        if c.sha(path)!=record['sha256']:raise RuntimeError('prepared cache content drift')
        VERIFIED.add(key)
    return path,key

def load(root,record,index,heads=True):
    global LOADED,LAST
    path,key=verify(root,record)
    if LOADED is None or LOADED[0]!=key:
        with np.load(path,allow_pickle=False) as z:flat=z['flat'];offsets=z['offsets']
        if flat.dtype!=np.uint8 or offsets.dtype!=np.int64 or flat.nbytes!=record['uncompressed_bytes'] or len(offsets)!=len(record['ticks'])+1 or offsets[0]!=0 or offsets[-1]!=len(flat) or np.any(np.diff(offsets)<0):raise RuntimeError('prepared chunk schema')
        from cache_codec import decode_frame
        previous={}
        for i in range(len(offsets)-1):
            value=flat[offsets[i]:offsets[i+1]]
            layout=record['layouts'][record['layout_indices'][i]]
            decode_frame(value,layout,previous)
        LOADED=(key,flat,offsets);LAST=None
    framekey=(key,index)
    if LAST is None or LAST[0]!=framekey:
        flat,offsets=LOADED[1:];value=flat[offsets[index]:offsets[index+1]];arrays={}
        if len(record['layout_indices'])!=len(record['ticks']):raise RuntimeError('prepared layouts schema')
        for name,dtype,shape,at,size,mode in record['layouts'][record['layout_indices'][index]]:
            if at<0 or size<0 or at+size>len(value):raise RuntimeError('prepared array bounds')
            arrays[name]=np.frombuffer(value[at:at+size],dtype=dtype).reshape(shape)
        LAST=(framekey,arrays,{})
    from cache_codec import expand_banks
    if heads and 'codec_arena' in LAST[1] and 'aim_points' not in LAST[1]:expand_banks(LAST[1])
    return LAST[1],LAST[2]

class Frame:
    def __init__(self,root,record,index):self.root,self.record,self.index=root,record,index
    def arrays(self,heads=True):return load(self.root,self.record,self.index,heads=heads)[0]
    def tensors(self,dtype,heads=True):
        arrays,memo=load(self.root,self.record,self.index,heads=heads)
        key=(dtype,heads)
        if key in memo:return memo[key]
        names=('tokens','query','own','enemy','pos','speeds','assignments')
        # Autograd must retain small inputs, never an entire decompressed shard.
        out={k:torch.as_tensor(arrays[k],dtype=torch.long if k in ('own','enemy','assignments') else dtype).clone() for k in names}
        for k in ('graph_order','graph_mask','graph_edge_radius','graph_edge_delta'):
            out[k]=torch.as_tensor(arrays[k],dtype=torch.long if k=='graph_order' else torch.bool if k=='graph_mask' else dtype).clone()
        if heads:
            if 'codec_arena' not in arrays:raise RuntimeError('head outside declared prepared window')
            if dtype!=torch.float32:raise RuntimeError('prepared tensors are float32 only; use raw frames for float64 parity')
            from candidates import FEATURES
            for head in ('aim','move'):
                numeric=arrays[head+'_numeric'];types=arrays[head+'_types']
                features=np.zeros((*types.shape,FEATURES),dtype=np.float32)
                features[:,:,11:18]=numeric
                np.put_along_axis(features,types[:,:,None],arrays[head+'_valid'][:,:,None].astype(np.float32),axis=-1)
                out[head+'_features']=torch.from_numpy(features)
                for suffix in ('points','valid','sources','members','mapping','types','nearest'):
                    value=arrays[head+'_'+suffix]
                    out[head+'_'+suffix]=torch.as_tensor(value,dtype=torch.bool if suffix=='valid' else torch.float32 if suffix=='points' else torch.long).clone()
                out['teacher_'+head]=torch.from_numpy(arrays['teacher_'+head]).clone()
        memo[key]=out
        return out
    def label_tensors(self,dtype):
        arrays,memo=load(self.root,self.record,self.index,heads=False);key=('labels',dtype)
        if key not in memo:
            memo[key]={k[6:]:torch.as_tensor(v,dtype=dtype).clone() for k,v in arrays.items() if k.startswith('label_')}
        return memo[key]

def activate(root,index,base_frames):
    global ACTIVE,BASE_FRAMES,LOADED,LAST,META_HASHES
    marker=c.read(Path(root)/'PREPARED_CACHE.json')
    if marker['schema']!=SCHEMA:raise RuntimeError('prepared marker schema')
    META_HASHES={q['meta_file']:q['meta_sha256'] for q in marker['records']}
    expected={str(location(root,f).relative_to(root)) for f in index['fights']}
    if set(META_HASHES)!=expected:raise RuntimeError('prepared marker fight coverage drift')
    ACTIVE=(Path(root),{str(Path(f['raw_file']).resolve()):f for f in index['fights']})
    BASE_FRAMES=base_frames;LOADED=LAST=None

def frames(path):
    fight=ACTIVE[1].get(str(Path(path).resolve())) if ACTIVE else None
    if fight is None:
        if BASE_FRAMES is None:raise RuntimeError('prepared cache not activated')
        yield from BASE_FRAMES(path);return
    root=ACTIVE[0];meta_path=location(root,fight)
    if c.sha(meta_path)!=META_HASHES[str(meta_path.relative_to(root))]:raise RuntimeError('prepared metadata content drift')
    meta=c.read(meta_path)
    if meta['identity']!=identity(fight) or meta['schema']!=SCHEMA:raise RuntimeError('prepared identity drift')
    lookup={}
    for record in meta['chunks']:
        verify(root,record)
        for i,tick in enumerate(record['ticks']):
            if tick in lookup:raise RuntimeError('duplicate prepared tick')
            lookup[tick]=(record,i)
    if sorted(lookup)!=list(range(fight['frames'])):raise RuntimeError('prepared prefix coverage drift')
    rowpath=root/meta['rows_file']
    if c.sha(rowpath)!=meta['rows_sha256']:raise RuntimeError('prepared row metadata drift')
    with gzip.open(rowpath,'rt') as stream:rows=json.load(stream)
    if len(rows)!=fight['frames']:raise RuntimeError('prepared row count drift')
    for tick,row in enumerate(rows):
        record,i=lookup[tick];row['_prepared']=Frame(root,record,i);yield row

def prepare(root,index,base_frames,deadline,monitor=None):
    root=Path(root);root.mkdir(parents=True,exist_ok=True);started=time.monotonic();records=[]
    total_frames=sum(f['frames'] for f in index['fights']);total_selected=sum(len(selected_ticks(f['frames'])) for f in index['fights'])
    for fight in index['fights']:
        if time.monotonic()>=deadline:raise TimeoutError('prepared cache cap')
        if c.sha(fight['raw_file'])!=fight['raw_sha256']:raise RuntimeError('prepared raw drift')
        path=location(root,fight);began=time.monotonic()
        if path.exists():
            meta=c.read(path)
            if meta['identity']!=identity(fight) or meta['schema']!=SCHEMA:raise RuntimeError('prepared reuse drift')
            for rec in meta['chunks']:verify(root,rec)
            if c.sha(root/meta['rows_file'])!=meta['rows_sha256']:raise RuntimeError('prepared row metadata drift')
        else:
            path.parent.mkdir(parents=True,exist_ok=True);chunks=[];pieces=[];offsets=[0];ticks=[];layouts=[];previous={};previous_heads=None
            wanted=set(selected_ticks(fight['frames']));rowmeta=[]
            def flush():
                nonlocal pieces,offsets,ticks,layouts,previous
                if not ticks:return
                dest=path.with_name(path.stem+f'.part{len(chunks):04d}.npz');tmp=dest.with_name(dest.name+f'.{os.getpid()}.tmp')
                try:
                    with tmp.open('xb') as stream:np.savez_compressed(stream,flat=np.concatenate(pieces),offsets=np.asarray(offsets,dtype=np.int64))
                    os.replace(tmp,dest)
                finally:
                    if tmp.exists():tmp.unlink()
                unique=[];indices=[];by_layout={}
                for layout in layouts:
                    key=json.dumps(layout,separators=(',',':'))
                    if key not in by_layout:by_layout[key]=len(unique);unique.append(layout)
                    indices.append(by_layout[key])
                chunks.append(dict(file=str(dest.relative_to(root)),sha256=c.sha(dest),ticks=ticks,layouts=unique,layout_indices=indices,uncompressed_bytes=offsets[-1],compressed_bytes=dest.stat().st_size))
                pieces=[];offsets=[0];ticks=[];layouts=[];previous={}
            for n,row in enumerate(base_frames(fight['raw_file']),1):
                if time.monotonic()>=deadline:raise TimeoutError('prepared cache cap')
                if monitor and n%30==0:monitor.live_memory(os.getpid())
                heads=n-1 in wanted
                slim={k:row[k] for k in ('width','height','t','dt')}
                slim['units']=[[u[0]] for u in sorted(row['units'],key=lambda u:u[0])]
                slim['own']=row['own'] if heads else []
                slim['labels']=[{k:lab[k] for k in ('id','role','active','ready','engineRelease','executed')} for lab in row['labels']] if heads else []
                rowmeta.append(slim)
                if previous_heads is not None and heads!=previous_heads:flush()
                previous_heads=heads
                from cache_codec import compress_banks
                arrays=compress_banks(build(row,heads));size=sum(v.nbytes for v in arrays.values())
                if size>MAX_CHUNK_BYTES:raise RuntimeError('prepared row exceeds chunk bound')
                if offsets[-1]+size>MAX_CHUNK_BYTES:flush()
                data,layout=encode(arrays,previous);bits=np.frombuffer(data,dtype=np.uint8)
                if shutil.disk_usage(root).free<2*1024**3+MAX_CHUNK_BYTES:raise RuntimeError('prepared disk reserve')
                pieces.append(bits.copy());offsets.append(offsets[-1]+len(bits));ticks.append(n-1);layouts.append(layout)
            if n!=fight['frames']:raise RuntimeError('prepared raw frame count')
            flush()
            rowpath=path.with_name(path.stem+'.rows.json.gz')
            with gzip.open(rowpath,'wt',compresslevel=6) as stream:json.dump(rowmeta,stream,separators=(',',':'))
            meta=dict(rows_file=str(rowpath.relative_to(root)),rows_sha256=c.sha(rowpath),rows_bytes=rowpath.stat().st_size,schema=SCHEMA,identity=identity(fight),frames=fight['frames'],cached_frames=len(wanted),chunks=chunks,compressed_bytes=sum(q['compressed_bytes'] for q in chunks)+rowpath.stat().st_size,uncompressed_bytes=sum(q['uncompressed_bytes'] for q in chunks),build_seconds=time.monotonic()-began)
            c.write(path,meta,exclusive=True)
        records.append(dict(tag=fight['tag'],meta_file=str(path.relative_to(root)),meta_sha256=c.sha(path),
                            **{k:meta[k] for k in ('frames','cached_frames','compressed_bytes','uncompressed_bytes','build_seconds')}))
        written=sum(q['compressed_bytes']+location(root,f).stat().st_size for q,f in zip(records,index['fights']))
        # Include public-prefix storage and head-window storage in projection.
        frame_projection=written/sum(q['frames'] for q in records)*total_frames
        head_projection=written/sum(q['cached_frames'] for q in records)*total_selected
        projected=max(frame_projection,head_projection)
        if projected>DISK_LIMIT_BYTES or projected-written>shutil.disk_usage(root).free-2*1024**3:raise RuntimeError('prepared disk projection exceeds 5 GB / reserve')
        remaining=1.2*sum(q['build_seconds'] for q in records)/sum(q['frames'] for q in records)*(total_frames-sum(q['frames'] for q in records))
        if remaining>deadline-time.monotonic():raise RuntimeError('prepared build projection exceeds cap')
    result=dict(schema=SCHEMA,records=records,seconds=time.monotonic()-started,compressed_bytes=written if records else 0,
                frames=sum(q['frames'] for q in records),cached_frames=sum(q['cached_frames'] for q in records),
                projected_bytes=projected if records else 0,projected_build_seconds=sum(q['build_seconds'] for q in records),
                format='schema11: exact float32 banks; native batch bit codec; typed temporal differences and byte planes; reversible int16 hierarchy; edge graphs; cloned training inputs',
                max_chunk_bytes=MAX_CHUNK_BYTES,disk_limit_bytes=DISK_LIMIT_BYTES,regeneration='none during float32 training')
    c.write(root/'PREPARED_CACHE.json',result);return result

def prepare_window(root,fight,rows,deadline):
    sample=dict(fight,frames=len(rows),tag=fight['tag']+'_first_window')
    stream=lambda path:iter(rows)
    report=prepare(root,dict(fights=[sample]),stream,deadline)
    activate(root,dict(fights=[sample]),stream)
    return list(frames(sample['raw_file'])),report
