"""Typed full owner for the approved R4 field/material law. No coarse replay."""
import copy
import ctypes
from dataclasses import dataclass, field
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from geomind.c6_r4_integrity import array_digest
from tools import build_c6_r4 as build

PARAMETER_NAMES = ('mu','diffusion','drive','output','incoming','soft_core','sigma','J','K')
MODES = {'intact':0,'no_r':1,'no_geometry_to_mode':2,'no_mode_to_geometry':3}
_NATIVE = None
_PASSIVE_CACHE = {}

def exact_steps(time, dt):
    value = round(time/dt)
    if dt <= 0 or time < 0 or abs(value*dt-time)>1e-9: raise ValueError('nonintegral time grid')
    return value

def complex_arrays(value):
    v=np.asarray(value)
    if v.dtype.kind != 'c' or not np.isfinite(v).all(): raise ValueError('finite complex state required')
    return np.asarray(v.real,dtype='f8'),np.asarray(v.imag,dtype='f8')

@dataclass
class Cohort:
    x: np.ndarray
    theta: np.ndarray
    rates: np.ndarray
    carrier: np.ndarray
    ids: tuple
    tokens: tuple
    selected: tuple = ()
    output: float = 0.
    mode: str = 'intact'
    origin: np.ndarray = None

@dataclass
class Owner:
    z: np.ndarray
    q: np.ndarray
    omega: np.ndarray
    psi: np.ndarray
    adjacency: np.ndarray
    model: dict
    site_ids: tuple
    time: float = 0.
    cohorts: list = field(default_factory=list)

    def clone(self): return copy.deepcopy(self)
    def validate(self):
        ns=len(self.z)
        complex_arrays(self.z)
        if (self.q.shape!=(ns,2) or self.omega.shape!=(ns,) or self.psi.shape!=(ns,8)
                or self.adjacency.shape!=(ns,ns) or len(set(self.site_ids))!=ns
                or not np.isfinite(self.time) or set(self.model)!=set(PARAMETER_NAMES)):
            raise ValueError('invalid medium inventory/schema')
        if not np.isfinite(np.r_[self.q.ravel(),self.omega,self.psi.ravel(),list(self.model.values())]).all():
            raise ValueError('nonfinite medium metadata')
        if not np.array_equal(self.adjacency,self.adjacency.T) or np.any(np.diag(self.adjacency)):
            raise ValueError('invalid medium adjacency')
        sizes={len(c.theta) for c in self.cohorts}
        if len(sizes)>1: raise ValueError('cohort shape mismatch')
        all_ids=[]
        for c in self.cohorts:
            n=len(c.theta);complex_arrays(c.carrier)
            if (n<3 or c.x.shape!=(n,2) or c.rates.shape!=(n,) or c.carrier.shape!=(ns,)
                or len(c.ids)!=n or len(set(c.ids))!=n or len(c.tokens)!=n or len(set(c.tokens))!=n
                or any(not isinstance(t,str) or len(t)!=32 or any(ch not in '0123456789abcdef' for ch in t) for t in c.tokens)
                or c.mode not in MODES or c.output not in (0.,1.)
                or len(set(c.selected))!=len(c.selected) or any(type(i) is not int or i<0 or i>=n for i in c.selected)):
                raise ValueError('invalid cohort identity/mask')
            if not np.isfinite(np.r_[c.x.ravel(),c.theta,c.rates]).all():raise ValueError('nonfinite cohort state')
            if c.origin is not None and (c.origin.shape!=(n,2) or not np.isfinite(c.origin).all()):raise ValueError('invalid ablation origin')
            if c.mode=='no_geometry_to_mode' and c.origin is None:raise ValueError('missing common geometry origin')
            all_ids.extend(c.ids)
        if len(set(all_ids))!=len(all_ids):raise ValueError('duplicate physical IDs')
        return self

    def pack(self):
        self.validate()
        return np.concatenate([np.asarray(self.z,dtype='c16').view('f8'),*[
            np.r_[c.x.ravel(),c.theta,np.asarray(c.carrier,dtype='c16').view('f8')] for c in self.cohorts]])

    def unpack(self, value, time):
        other=self.clone();ns=len(self.z);offset=2*ns
        other.z=np.array(value[:offset],dtype='f8').view('c16').copy();other.time=float(time)
        for c in other.cohorts:
            n=len(c.theta);c.x=np.array(value[offset:offset+2*n]).reshape(n,2);offset+=2*n
            c.theta=np.array(value[offset:offset+n]);offset+=n
            c.carrier=np.array(value[offset:offset+2*ns],dtype='f8').view('c16').copy();offset+=2*ns
        if offset!=len(value):raise ValueError('owner vector shape mismatch')
        return other.validate()

    def identity(self):
        arrays=[];names=[]
        for name,a in [('actual',self.z),*[(f'carrier/{i}',c.carrier) for i,c in enumerate(self.cohorts)]]:
            r,im=complex_arrays(a);arrays.extend((r,im));names.extend((name+'/real',name+'/imag'))
        arrays.extend((self.q,self.omega,self.psi,self.adjacency));names.extend(('q','omega','psi','adjacency'))
        meta=[]
        for i,c in enumerate(self.cohorts):
            arrays.extend((c.x,c.theta,c.rates,c.x if c.origin is None else c.origin));names.extend(f'{i}/{k}' for k in ('x','theta','rates','origin'))
            meta.append({'ids':list(c.ids),'tokens':list(c.tokens),'selected':list(c.selected),'output':c.output,'mode':c.mode,'has_origin':c.origin is not None})
        return array_digest('c6-field-owner',*arrays,metadata={'fields':names,'time':self.time,'model':self.model,'site_ids':list(self.site_ids),'cohorts':meta})

def medium(rng,model):
    q=np.array([(x,y) for x in (-4,-2,0,2,4) for y in (-4,-2,0,2,4)],float)
    adj=(np.linalg.norm(q[:,None]-q[None,:],axis=-1)==2).astype('i4')
    order=rng.permutation(25)
    return Owner((rng.normal(0,.05,25)+1j*rng.normal(0,.05,25))[order],q[order],
                 rng.uniform(-.3,.7,25)[order],rng.uniform(-np.pi,np.pi,(25,8))[order],
                 adj[order][:,order],dict(model),tuple(int(i) for i in order)).validate()

def population(rng,owner,generation,episode,n=24):
    r=3*np.sqrt(rng.random(n));angle=rng.uniform(-np.pi,np.pi,n)
    x=np.c_[r*np.cos(angle)+2*generation,r*np.sin(angle)]
    tokens=tuple(rng.bytes(16).hex() for _ in range(n));order=rng.permutation(n)
    c=Cohort(x[order],rng.uniform(-np.pi,np.pi,n)[order],rng.uniform(-.05,.45,n)[order],owner.z.copy(),
             tuple(f'g{generation}/e{episode}/p{int(i)}' for i in order),tuple(tokens[i] for i in order))
    result=owner.clone();result.cohorts.append(c);return result.validate()

def native():
    global _NATIVE
    source=hashlib.sha256(build.SOURCE.read_bytes()).hexdigest()
    if _NATIVE is not None:
        lib,record=_NATIVE
        if record['source_sha256']!=source or hashlib.sha256(build.LIBRARY.read_bytes()).hexdigest()!=record['binary_sha256']:
            raise RuntimeError('loaded native identity changed; restart process')
        return lib,record
    try: record=json.loads((build.LIBRARY.parent/'BUILD.json').read_text())
    except (FileNotFoundError,json.JSONDecodeError):record={}
    if record.get('source_sha256')!=source or not build.LIBRARY.exists() or record.get('binary_sha256')!=hashlib.sha256(build.LIBRARY.read_bytes()).hexdigest():record=build.build()
    lib=ctypes.CDLL(str(build.LIBRARY));ptr=ctypes.POINTER(ctypes.c_double);iptr=ctypes.POINTER(ctypes.c_int)
    tail=[ptr,ptr,ptr,ptr,iptr,ptr,ptr,iptr,ptr,ptr,ptr]
    lib.field_rhs.argtypes=[ctypes.c_int]*3+[ctypes.c_double]+tail
    lib.field_run.argtypes=[ctypes.c_int]*3+[ctypes.c_double]*2+[ctypes.c_int]*2+tail
    lib.field_rhs.restype=lib.field_run.restype=ctypes.c_int;_NATIVE=(lib,record);return lib,record

def arguments(owner):
    owner.validate();ns=len(owner.z);nc=len(owner.cohorts);n=len(owner.cohorts[0].theta) if nc else 24
    rates=np.concatenate([c.rates for c in owner.cohorts]) if nc else np.zeros(0)
    masks=np.zeros((nc,n))
    # Mask inventory stays selected even when emission is switched off: kernel
    # normalizes by the number of nonzero selected markers, not emitted power.
    for j,c in enumerate(owner.cohorts): masks[j,list(c.selected)]=c.output if c.output else -0.0
    # Separate selection from output in native masks: negative marker means OFF.
    for j,c in enumerate(owner.cohorts):
        if not c.output: masks[j,list(c.selected)]=-1.
    origins=np.concatenate([(c.x if c.origin is None else c.origin).ravel() for c in owner.cohorts]) if nc else np.zeros(0)
    arrays=[owner.pack(),owner.q.ravel(),owner.omega,owner.psi.ravel(),owner.adjacency.ravel(),rates,masks.ravel(),
            np.array([MODES[c.mode] for c in owner.cohorts]),origins,np.array([owner.model[k] for k in PARAMETER_NAMES])]
    typed=[np.ascontiguousarray(a,dtype='i4' if i in (4,7) else 'f8') for i,a in enumerate(arrays)]
    return ns,n,nc,typed

def rhs(owner):
    ns,n,nc,a=arguments(owner);out=np.empty_like(a[0]);lib,_=native()
    pointers=[v.ctypes.data_as(ctypes.POINTER(ctypes.c_int if i in (4,7) else ctypes.c_double)) for i,v in enumerate(a)]
    err=lib.field_rhs(ns,n,nc,owner.time,*pointers,out.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
    if err:raise ValueError('native law invalid: '+str(err))
    return out

def advance(owner,duration,dt,sample_dt=None,_factor=True):
    sample_dt=dt if sample_dt is None else sample_dt;steps=exact_steps(duration,dt);sample=exact_steps(sample_dt,dt)
    if sample<1 or steps%sample:raise ValueError('incomplete sample interval')
    if _factor and len(owner.cohorts)>1 and all(c.output==0. for c in owner.cohorts[:-1]):
        # Previous sources are causally independent of actual field/current
        # source. Reuse their exact same-grid evolution, never a coarse replay.
        active=owner.clone();active.cohorts=active.cohorts[-1:]
        end,active_frames=advance(active,duration,dt,sample_dt,_factor=False)
        parts=[active_frames[:,:2*len(owner.z)]]
        for cohort in owner.cohorts[:-1]:
            passive=owner.clone();passive.z=np.zeros_like(owner.z);passive.cohorts=[copy.deepcopy(cohort)]
            key=(passive.identity(),duration,dt,sample_dt)
            if key not in _PASSIVE_CACHE:
                _,path=advance(passive,duration,dt,sample_dt,_factor=False)
                if len(_PASSIVE_CACHE)>=512:_PASSIVE_CACHE.clear()
                _PASSIVE_CACHE[key]=path[:,2*len(owner.z):].copy()
            parts.append(_PASSIVE_CACHE[key])
        parts.append(active_frames[:,2*len(owner.z):]);joined=np.concatenate(parts,axis=1)
        return owner.unpack(joined[-1],owner.time+duration),joined
    ns,n,nc,a=arguments(owner);frames=np.empty((steps//sample+1,len(a[0])),dtype='f8');lib,_=native()
    pointers=[v.ctypes.data_as(ctypes.POINTER(ctypes.c_int if i in (4,7) else ctypes.c_double)) for i,v in enumerate(a)]
    err=lib.field_run(ns,n,nc,owner.time,dt,steps,sample,*pointers,frames.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
    if err:raise ValueError('native flow invalid: '+str(err))
    return owner.unpack(frames[-1],owner.time+duration),frames

def output(owner):
    value=np.zeros(len(owner.z),complex)
    for c in owner.cohorts:
        if c.selected:
            m=np.array(c.selected);w=np.exp(-np.sum((owner.q[:,None]-c.x[m][None])**2,axis=-1)/(2*owner.model['sigma']**2))
            full=owner.model['output']*np.mean(w*np.exp(1j*c.theta[m]),axis=1)
            value+=full*c.output
    return value

def emissions(owner,flow):
    """Every production-step outgoing value, computed before each zero mask."""
    ns=len(owner.z);offset=2*ns;values=np.zeros((len(flow),ns),complex)
    for c in owner.cohorts:
        n=len(c.theta);x=flow[:,offset:offset+2*n].reshape(-1,n,2);theta=flow[:,offset+2*n:offset+3*n];offset+=3*n+2*ns
        if c.selected:
            m=list(c.selected);w=np.exp(-np.sum((owner.q[None,:,None,:]-x[:,None,m,:])**2,axis=-1)/(2*owner.model['sigma']**2))
            full=owner.model['output']*np.mean(w*np.exp(1j*theta[:,None,m]),axis=-1)
            values+=full*c.output
    return values
