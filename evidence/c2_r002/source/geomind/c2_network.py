"""Persistent conductances, transient activity; inference accepts only inputs.

The native kernel performs synchronous Euler relaxation and the R4 local rule.
It has no target at inference, no reference imports and no backward program.
"""
import ctypes
from dataclasses import dataclass, asdict
import hashlib
import json
from pathlib import Path
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
GRID_EDGES = tuple((i,j) for i in range(16) for j in range(i+1,16)
                   if j-i==4 or (j-i==1 and i//4==j//4))


class Cost(ctypes.Structure):
    _fields_ = [(name,ctypes.c_uint64) for name in
               ('phases','sweeps','bound_edges','force_edges','force_nodes','node_updates',
                'learning_edges','committed','refused','saturated')] + [
                    ('max_force',ctypes.c_double),('update_norm',ctypes.c_double)]

    def report(self):
        return {name:getattr(self,name) for name,_ in self._fields_}


@dataclass(frozen=True)
class Settings:
    leak: float = 0.01
    beta: float = 0.05
    eta: float = 0.01
    tolerance: float = 1e-9
    max_sweeps: int = 20000

    def validate(self):
        if any(type(v) not in (int,float) or not np.isfinite(v) or v<=0
               for v in (self.leak,self.beta,self.eta,self.tolerance)):
            raise ValueError('Positive finite settings required')
        if type(self.max_sweeps) is not int or self.max_sweeps<1:
            raise ValueError('Positive integer sweep cap required')


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def library():
    build = ROOT/'.gate/c2_backend'
    record = json.loads((build/'BUILD.json').read_text())
    source = ROOT/'native/c2/relaxation.cpp'
    binary = build/'relaxation.dylib'
    if record['source_sha256']!=hashlib.sha256(source.read_bytes()).hexdigest() or record['binary_sha256']!=hashlib.sha256(binary.read_bytes()).hexdigest():
        raise RuntimeError('Native build identity changed; run tools/build_c2.py')
    lib=ctypes.CDLL(str(binary))
    ints=np.ctypeslib.ndpointer(dtype=np.int32,flags='C_CONTIGUOUS')
    doubles=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
    common=[ctypes.c_int,ctypes.c_int,ints,ints,doubles,ctypes.c_int,ctypes.c_int,ctypes.c_int,doubles]
    lib.c2_relax.argtypes=common+[ctypes.c_double]*4+[ctypes.c_int,doubles,ctypes.POINTER(Cost)]
    lib.c2_learn.argtypes=common+[ctypes.c_double]*4+[ctypes.c_int,ctypes.c_double,ctypes.c_int,doubles,doubles,ctypes.POINTER(Cost)]
    lib.c2_relax.restype=lib.c2_learn.restype=ctypes.c_int
    return lib


class ConductanceNetwork:
    schema='geomind.c2.conductances.v1'
    algorithm='synchronous-euler-local-ep.v1'

    def __init__(self, conductances, manifest_hash, settings=Settings(), edges=GRID_EDGES,
                 nodes=16, inputs=(0,3), output=10):
        settings.validate()
        if not isinstance(manifest_hash,str) or len(manifest_hash)!=64 or any(c not in '0123456789abcdef' for c in manifest_hash):
            raise ValueError('Manifest SHA256 required')
        if type(nodes) is not int or nodes<3 or not isinstance(edges,tuple) or not edges:
            raise ValueError('Nonempty immutable topology required')
        if (not isinstance(inputs,tuple) or len(inputs)!=2 or len(set(inputs+(output,)))!=3
                or any(type(i) is not int or not 0<=i<nodes for i in inputs+(output,))):
            raise ValueError('Distinct valid ports required')
        if any(not isinstance(e,tuple) or len(e)!=2 or any(type(i) is not int or not 0<=i<nodes for i in e) or e[0]==e[1] for e in edges) or len(set(frozenset(e) for e in edges))!=len(edges):
            raise ValueError('Invalid undirected edges')
        visited={inputs[0]}
        for _ in range(nodes):
            for a,b in edges:
                if a in visited or b in visited: visited.update((a,b))
        if len(visited)!=nodes: raise ValueError('Connected topology required')
        if not isinstance(conductances,(list,tuple,np.ndarray)) or len(conductances)!=len(edges):
            raise ValueError('Conductance vector length mismatch')
        raw=list(conductances)
        if any(isinstance(v,(bool,np.bool_)) or not isinstance(v,(int,float,np.integer,np.floating)) for v in raw):
            raise ValueError('Numeric conductances required')
        g=np.asarray(raw,dtype=np.float64)
        if g.shape!=(len(edges),) or not np.isfinite(g).all() or np.any((g<.05)|(g>5)):
            raise ValueError('Conductances outside finite bounds')
        self._g=g.copy(); self.edges=edges; self.nodes=nodes; self.inputs=inputs; self.output=output
        self.settings=settings; self.manifest_hash=manifest_hash; self._frozen=False
        self._a=np.array([e[0] for e in edges],dtype=np.int32)
        self._b=np.array([e[1] for e in edges],dtype=np.int32)
        self._lib=library()

    @property
    def conductances(self):
        return self._g.copy()

    def _input(self,x):
        if not isinstance(x,(tuple,list,np.ndarray)) or len(x)!=2 or any(isinstance(v,(bool,np.bool_)) or not isinstance(v,(int,float,np.integer,np.floating)) for v in x):
            raise ValueError('Two finite inputs required')
        values=np.asarray(x,dtype=np.float64)
        if values.shape!=(2,) or not np.isfinite(values).all(): raise ValueError('Two finite inputs required')
        return values

    def _arguments(self,x):
        return [self.nodes,len(self.edges),self._a,self._b,self._g,*self.inputs,self.output,x]

    def query(self,x):
        start=time.perf_counter(); cost=Cost()
        try:
            x=self._input(x); activity=np.zeros(self.nodes,dtype=np.float64); s=self.settings
            status=self._lib.c2_relax(*self._arguments(x),0.,0.,s.leak,s.tolerance,s.max_sweeps,activity,ctypes.byref(cost))
            result={'status':('OK','NOT_CONVERGED','INVALID_STATE')[status],
                    'output':float(activity[self.output]) if status==0 else None,
                    'activity':activity.tolist() if status==0 else None}
        except (ValueError,TypeError,OverflowError) as exc:
            result={'status':'INVALID_STATE','output':None,'activity':None,'reason':str(exc)}
        return dict(result,cost=cost.report(),seconds=time.perf_counter()-start)

    def learn(self,x,y,feedback=True):
        if self._frozen: raise RuntimeError('Frozen network cannot learn')
        cost=Cost(); start=time.perf_counter()
        try:
            x=self._input(x)
            if isinstance(y,(bool,np.bool_)) or not isinstance(y,(int,float,np.integer,np.floating)) or not np.isfinite(y) or type(feedback) is not bool:
                raise ValueError('Finite scalar training feedback required')
            free=np.zeros(self.nodes); nudged=np.zeros(self.nodes); s=self.settings
            status=self._lib.c2_learn(*self._arguments(x),float(y),s.beta,s.leak,s.tolerance,s.max_sweeps,s.eta,int(feedback),free,nudged,ctypes.byref(cost))
            result={'status':('PASS','NOT_CONVERGED','INVALID_STATE')[status],
                    'free':free.tolist(),'nudged':nudged.tolist()}
        except (ValueError,TypeError,OverflowError) as exc:
            result={'status':'INVALID_STATE','reason':str(exc)}
        return dict(result,cost=cost.report(),seconds=time.perf_counter()-start)

    def freeze(self):
        self._frozen=True

    def export(self):
        payload={'schema':self.schema,'algorithm':self.algorithm,'manifest_hash':self.manifest_hash,
                 'settings':asdict(self.settings),'edges':[list(e) for e in self.edges],
                 'nodes':self.nodes,'inputs':list(self.inputs),'output':self.output,'conductances':self._g.tolist()}
        return canonical(dict(payload,checksum=digest(payload)))

    @classmethod
    def load(cls,encoded,frozen=True):
        def unique(pairs):
            d={}
            for k,v in pairs:
                if k in d: raise ValueError('Duplicate snapshot key')
                d[k]=v
            return d
        r=json.loads(encoded,object_pairs_hook=unique)
        if not isinstance(r,dict) or set(r)!={'schema','algorithm','manifest_hash','settings','edges','nodes','inputs','output','conductances','checksum'}:
            raise ValueError('Invalid snapshot fields')
        checksum=r.pop('checksum')
        if r['schema']!=cls.schema or r['algorithm']!=cls.algorithm or digest(r)!=checksum:
            raise ValueError('Invalid snapshot identity')
        state=cls(r['conductances'],r['manifest_hash'],Settings(**r['settings']),
                  tuple(tuple(e) for e in r['edges']),r['nodes'],tuple(r['inputs']),r['output'])
        if frozen: state.freeze()
        return state

    def clone(self,frozen=False):
        return type(self).load(self.export(),frozen=frozen)
