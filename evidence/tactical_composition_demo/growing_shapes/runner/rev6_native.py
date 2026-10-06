"""Revision-5.1 batch bridge. Python reference remains selectable in Run.

Native owns the whole step loop; Python imports complete records only at the
next protocol boundary. No native handle or history is retained across calls,
so growth, reward, clones and synthetic history edits remain authoritative.
"""
import ctypes as C
from functools import lru_cache
import hashlib
import json
import platform
import threading
from contextlib import contextmanager
import numpy as np
from pathlib import Path
from ..medium.medium import Drive
from ..medium.design_0h import Frame, SITES
from ..native_guard import pin_image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


class Row(C.Structure):
    _fields_ = [('id',C.c_uint64),('x',C.c_double),('y',C.c_double),('phase',C.c_double),
                ('count',C.c_int32),('neighbors',C.c_uint64*64)]


class History(C.Structure):
    _fields_ = [('index',C.c_int32),('count',C.c_int32),('sites',C.c_int32),
                ('rows',Row*64),('drives',Drive*8)]

class Schedule(C.Structure):
    _fields_ = [('count',C.c_int32),('drives',Drive*8)]


@lru_cache(maxsize=1)
def library():
    path = HERE/'_rev6_build'/('rev6_perf.dylib' if platform.system() == 'Darwin' else 'rev6_perf.so')
    manifest = json.loads((path.parent/'build.json').read_text())
    if manifest.get('abi') != 3 or manifest.get('numpy') != np.__version__ or np.__version__ != '2.0.2':
        raise RuntimeError('unsupported native ABI/NumPy reduction identity; rebuild or qualify a new reduction')
    for name, expected in manifest['source_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != expected:
            raise RuntimeError(f'stale native orchestration build: {name}; run build_perf')
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest['binary_sha256']:
        raise RuntimeError('native orchestration binary identity mismatch')
    for name, expected in manifest['dependencies'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != expected:
            raise RuntimeError(f'rev6 native dependency identity mismatch: {name}; run build_perf')
        pin_image(ROOT/name,expected)
    pin_image(path,manifest['binary_sha256'])
    lib = C.CDLL(str(path))
    common = [C.c_void_p,C.POINTER(History),C.c_int,C.c_int,C.POINTER(C.c_uint64),
              C.POINTER(C.c_double),C.c_int,C.POINTER(C.c_double)]
    for name in ('gp_batch','gp_contract','gp_replay','gp_evaluate_episode','gp_future'):
        getattr(lib,name).restype = C.c_char_p
    lib.gp_batch.argtypes = [C.c_void_p,C.c_void_p,*common[1:],C.POINTER(C.c_int32),
                            C.POINTER(C.c_double),C.c_int,C.c_double]
    lib.gp_contract.argtypes = [*common,C.POINTER(Drive),C.c_int,C.c_int]
    lib.gp_replay.argtypes = [*common,C.POINTER(Schedule),C.c_int,C.c_int]
    lib.gp_evaluate_episode.argtypes = lib.gp_batch.argtypes[:-2]
    lib.gp_future.argtypes = [C.c_void_p,C.POINTER(Schedule),C.c_int,C.POINTER(C.c_double),C.c_int]
    lib.gp_abi_version.restype,lib.gp_abi_version.argtypes = C.c_int,[]
    lib.gp_struct_size.restype,lib.gp_struct_size.argtypes = C.c_int,[C.c_int]
    if lib.gp_abi_version()!=3 or any(lib.gp_struct_size(i)!=C.sizeof(t) for i,t in enumerate((Row,History,Schedule))):
        raise RuntimeError('native orchestration ABI layout mismatch')
    lib.gp_assay.restype=C.c_char_p
    lib.gp_assay.argtypes=lib.gp_batch.argtypes[:-2]+[C.POINTER(Schedule),C.c_int,C.c_int]
    from ..world.world import Observation
    lib.gp_assay_synthetic.restype=C.c_char_p
    lib.gp_assay_synthetic.argtypes=common+[C.POINTER(C.c_int32),C.POINTER(C.c_double),C.POINTER(Schedule),C.c_int,C.c_int,C.POINTER(Observation),C.c_int]
    lib._dependency_paths = {str((ROOT/n).resolve()) for n in manifest['dependencies']}
    return lib


@contextmanager
def locked(medium, lib, world=None):
    """Distinct handles may run concurrently; a shared handle fails on overlap.

    ctypes releases the GIL. Never retry a runtime native failure on the mutated
    state: only prevalidated argument failures are guaranteed mutation-free.
    """
    if getattr(medium, '_perf_failed', False):
        raise RuntimeError('native state invalid after failure; discard this run')
    owners = [medium.native] + ([world] if world is not None else [])
    acquired = []
    try:
        for owner in owners:
            if not owner._handle:
                raise RuntimeError('closed native handle')
            api = owner._lib if owner is medium.native else owner.library.api
            if str(Path(api._name).resolve()) not in lib._dependency_paths:
                raise RuntimeError('unqualified native handle library')
            # Attribute creation is under the GIL, before any native call.
            if not hasattr(owner, '_perf_lock'):
                owner._perf_lock = threading.RLock()
            if getattr(owner,'_perf_owner',None) is not None:
                raise RuntimeError('concurrent native handle use')
            if not owner._perf_lock.acquire(blocking=False):
                raise RuntimeError('concurrent native handle use')
            acquired.append(owner._perf_lock)
            owner._perf_owner = threading.get_ident()
        yield
    finally:
        for owner in reversed(owners[:len(acquired)]):
            owner._perf_owner = None
            owner._perf_lock.release()


def decode(medium, raw):
    data = json.loads(raw)
    if 'error' in data:
        medium._perf_failed = True
        raise ValueError(data['error'])
    return data


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
        if 'paths' in row:
            medium.observe_diagnostics(row)
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
    if type(steps) is not int or not 1 <= steps <= 200:
        raise ValueError('batch steps must be 1..200')
    with locked(medium,lib,world):
        raw = lib.gp_batch(medium.native._handle,world._handle,*pack(medium),
            (C.c_int32*8)(*assignment),(C.c_double*16)(*(v for s in SITES for v in s)),steps,coverage_start)
        return unpack(medium,decode(medium,raw))


def contract(medium, drives, *, adapt=True, lib=None):
    lib = lib or library()
    with locked(medium,lib):
        raw = lib.gp_contract(medium.native._handle,*pack(medium),
                             (Drive*len(drives))(*drives),len(drives),int(adapt))
        return unpack(medium,decode(medium,raw))


def replay(medium, schedule, *, adapt=False, lib=None):
    """Engineering/recovery supplied drives only; no world or protocol boundary."""
    lib = lib or library()
    if not 1 <= len(schedule) <= 600 or any(len(ds)>8 for ds in schedule):
        raise ValueError('replay requires 1..600 steps with at most eight drives')
    values = (Schedule*len(schedule))()
    for dst, ds in zip(values,schedule):
        dst.count = len(ds)
        for j,d in enumerate(ds):
            dst.drives[j] = d
    with locked(medium,lib):
        raw = lib.gp_replay(medium.native._handle,*pack(medium),values,len(values),int(adapt))
        return unpack(medium,decode(medium,raw))


def evaluate_episode(medium, world, assignment, lib=None):
    """Consume one isolated, disposable frozen copy. External history is unused.

    Internal native endpoint history is still observed exactly once per step.
    The caller owns scores and identity accounting; this never creates a panel.
    """
    lib = lib or library()
    with locked(medium,lib,world):
        raw = lib.gp_evaluate_episode(medium.native._handle,world._handle,*pack(medium),
            (C.c_int32*8)(*assignment),(C.c_double*16)(*(v for s in SITES for v in s)))
        data = decode(medium,raw)
        medium.step_index = data['index']
        return data


def future(medium, schedule, lib=None):
    """Disposable frozen recovery branch; native history retained, Python history unused."""
    lib=lib or library()
    if not 1<=len(schedule)<=600 or any(len(ds)>8 for ds in schedule):
        raise ValueError('future requires 1..600 steps with at most eight drives')
    values=(Schedule*len(schedule))()
    for dst,ds in zip(values,schedule):
        dst.count=len(ds)
        for j,d in enumerate(ds):dst.drives[j]=d
    with locked(medium,lib):
        output=(C.c_double*(len(schedule)*len(medium.native)*3))()
        decode(medium,lib.gp_future(medium.native._handle,values,len(values),output,len(output)))
        medium.step_index+=len(schedule)
        return np.ctypeslib.as_array(output).reshape(len(schedule),len(medium.native),3)


def assay(medium,world,assignment,*,schedule=None,relay=0,lib=None):
    lib=lib or library()
    values=None
    if schedule is not None:
        values=(Schedule*len(schedule))()
        for dst,ds in zip(values,schedule):
            dst.count=len(ds)
            for j,d in enumerate(ds):dst.drives[j]=d
    with locked(medium,lib,world):
        data=decode(medium,lib.gp_assay(medium.native._handle,world._handle,*pack(medium),
            (C.c_int32*8)(*assignment),(C.c_double*16)(*(v for s in SITES for v in s)),values,0 if schedule is None else len(schedule),relay))
        medium.step_index=data['index']
        return data


def assay_synthetic(medium,observations,assignment,*,schedule=None,relay=0,lib=None):
    """At most four supplied observations; identical gp_assay loop, no World."""
    from ..world.world import Observation
    if not 1<=len(observations)<=4:raise ValueError('synthetic assay requires 1..4 observations')
    if schedule is not None and (len(schedule)!=len(observations) or any(len(ds)>8 for ds in schedule)):
        raise ValueError('synthetic donor schedule must match observations')
    lib=lib or library();values=None
    if schedule is not None:
        values=(Schedule*len(schedule))()
        for dst,ds in zip(values,schedule):
            dst.count=len(ds)
            for j,d in enumerate(ds):dst.drives[j]=d
    with locked(medium,lib):
        data=decode(medium,lib.gp_assay_synthetic(medium.native._handle,*pack(medium),
            (C.c_int32*8)(*assignment),(C.c_double*16)(*(v for s in SITES for v in s)),
            values,0 if schedule is None else len(schedule),relay,(Observation*len(observations))(*observations),len(observations)))
        medium.step_index=data['index']
        return data
