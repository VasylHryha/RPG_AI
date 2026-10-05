"""Revision-5.1 batch bridge. Python reference remains selectable in Run.

Native owns the whole step loop; Python imports complete records only at the
next protocol boundary. No native handle or history is retained across calls,
so growth, reward, clones and synthetic history edits remain authoritative.
"""
import ctypes as C
import hashlib
import json
import platform
from pathlib import Path
from ..medium.medium import Drive
from ..medium.design_0h import Frame, SITES

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


class Row(C.Structure):
    _fields_ = [('id',C.c_uint64),('x',C.c_double),('y',C.c_double),('phase',C.c_double),
                ('count',C.c_int32),('neighbors',C.c_uint64*64)]


class History(C.Structure):
    _fields_ = [('index',C.c_int32),('count',C.c_int32),('sites',C.c_int32),
                ('rows',Row*64),('drives',Drive*8)]


def library():
    path = HERE/'_build'/('perf.dylib' if platform.system() == 'Darwin' else 'perf.so')
    manifest = json.loads((path.parent/'build.json').read_text())
    for name, expected in manifest['source_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != expected:
            raise RuntimeError(f'stale native orchestration build: {name}; run build_perf')
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest['binary_sha256']:
        raise RuntimeError('native orchestration binary identity mismatch')
    lib = C.CDLL(str(path))
    common = [C.c_void_p,C.POINTER(History),C.c_int,C.c_int,C.POINTER(C.c_uint64),
              C.POINTER(C.c_double),C.c_int,C.POINTER(C.c_double)]
    lib.gp_batch.restype = lib.gp_contract.restype = C.c_char_p
    lib.gp_batch.argtypes = [C.c_void_p,C.c_void_p,*common[1:],C.POINTER(C.c_int32),
                            C.POINTER(C.c_double),C.c_int,C.c_double]
    lib.gp_contract.argtypes = [*common,C.POINTER(Drive),C.c_int,C.c_int]
    return lib


def pack(medium):
    frames = (History*len(medium.frames))()
    for dst, f in zip(frames,medium.frames):
        if len(f.elements)>64 or len(f.sites)>8:
            raise ValueError('history exceeds protocol cap')
        dst.index,dst.count,dst.sites = f.index,len(f.elements),len(f.sites)
        for row,(id,values) in zip(dst.rows,f.elements.items()):
            links = f.neighbors[id]
            if len(links)>64:
                raise ValueError('too many historical neighbors')
            row.id,row.x,row.y,row.phase,row.count = id,*values,len(links)
            row.neighbors[:len(links)] = links
        for j,(site,values) in enumerate(f.sites.items()):
            dst.drives[j] = Drive(site,*values[:3],0,values[3],1,3)
    elements = medium.native.elements
    ids = (C.c_uint64*len(elements))(*(e.id for e in elements))
    death = (C.c_double*len(elements))(*(medium.death.get(e.id,0.) for e in elements))
    novelty = (C.c_double*8)(*(medium.novelty[s] for s in range(8)))
    return frames,len(frames),medium.step_index,ids,death,len(elements),novelty


def unpack(medium, data):
    if 'error' in data:
        raise ValueError(data['error'])
    for row in data['steps']:
        f = row['frame']
        medium.frames.append(Frame(f['index'],f['time'],
            {int(k):tuple(v) for k,v in f['elements'].items()},
            {int(k):tuple(v) for k,v in f['sites'].items()},
            {int(k):tuple(v) for k,v in f['neighbors'].items()}))
        medium.step_index = f['index']
        medium.drives = [Drive(*d) for d in row['drives']]
        for d in medium.drives:
            d.phase += .1*d.rate
        if 'event' in row:
            event = row['event']
            for key in ('rates','gains','defined_signals'):
                event['values'][key] = {int(k):v for k,v in event['values'][key].items()}
            medium.events.append(event)
        medium.death = {int(k):v for k,v in row['death'].items()}
        medium.novelty = dict(enumerate(row['novelty']))
    return data


def batch(medium, world, assignment, steps, coverage_start, lib=None):
    lib = lib or library()
    raw = lib.gp_batch(medium.native._handle,world._handle,*pack(medium),
        (C.c_int32*8)(*assignment),(C.c_double*16)(*(v for s in SITES for v in s)),steps,coverage_start)
    return unpack(medium,json.loads(raw))


def contract(medium, drives, *, adapt=True, lib=None):
    lib = lib or library()
    raw = lib.gp_contract(medium.native._handle,*pack(medium),
                         (Drive*len(drives))(*drives),len(drives),int(adapt))
    return unpack(medium,json.loads(raw))
