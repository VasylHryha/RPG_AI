"""Versioned native rev7 RHS. Never loads or rebuilds a 5.1 image implicitly."""
import ctypes as C
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import platform
from .medium import Medium, Params, Drive, _library

HERE = Path(__file__).parent
BUILD = HERE / '_rev7_build'
IMAGE = BUILD / ('rev7_medium.dylib' if platform.system() == 'Darwin' else 'rev7_medium.so')


def budget_counts(roles, incoming):
    """7.6 external O: keep actual topology, charge ordinary bodies/pairs only."""
    ordinary={id for id,role in roles.items() if role!='output'}
    pairs={tuple(sorted((target,source))) for target,sources in incoming.items()
           for source in sources if target in ordinary and source in ordinary}
    return len(ordinary),len(pairs)


@lru_cache(maxsize=1)
def library():
    manifest = json.loads((BUILD / 'build.json').read_text())
    if manifest['version'] != 'rev7_rhs_v1':
        raise RuntimeError('rev7 native version mismatch')
    for name, digest in manifest['source_sha256'].items():
        if hashlib.sha256((HERE/name).read_bytes()).hexdigest() != digest:
            raise RuntimeError(f'stale rev7 native source: {name}')
    if hashlib.sha256(IMAGE.read_bytes()).hexdigest() != manifest['binary_sha256']:
        raise RuntimeError('rev7 binary identity mismatch')
    lib = _library(IMAGE)
    h,d,u,i,P = C.c_void_p,C.c_double,C.c_uint64,C.c_int,C.POINTER
    for name, args in {
        'add_role':[h,d,d,d,d,i,P(u)], 'role':[h,u,P(i)],
        'cut':[h,u,P(d),i], 'lesions':[h,P(u),i], 'output':[h,P(d)],
        'stage_terms':[h,P(d),i], 'comparator':[h,i],
        'phase_scale':[h,d], 'excursion':[h,P(d),i], 'motion_neighbors':[h,P(C.c_int32),P(C.c_int32),i], 'strong_neighbors':[h,P(C.c_int32),P(C.c_int32),i], 'pin':[h,u,P(d)],
        'policy':[h,P(d)], 'reference_drives':[h,P(Drive),i], 'reference_drive_count':[h],
        'reference_lesions':[h,P(u),i], 'reference_lesion_count':[h],
        'reference_commit':[h,P(d),P(d),P(d),i,d],
    }.items():
        fn=getattr(lib,'gm_'+name);fn.restype=i;fn.argtypes=args
    return lib


class Rev7Native(Medium):
    def __init__(self, seed=0, params=None):
        self._lib=library();self.params=params or Params(window=101,min_samples=100)
        self._handle=self._lib.gm_create(seed,C.byref(self.params))
        if not self._handle: raise ValueError('invalid rev7 native state')

    def add(self,x,y,phase=0.,rate=0.,role='element'):
        if role not in ('element','output'): raise ValueError('unknown role')
        value=C.c_uint64()
        self._call('add_role',x,y,phase,rate,int(role=='output'),C.byref(value))
        return value.value

    def split(self,*args,**kwargs):
        raise ValueError('B2/splitting is disabled in revision 7')

    def role(self,id):
        value=C.c_int();self._call('role',id,C.byref(value))
        return 'output' if value.value else 'element'

    def cost(self,c_e,c_c):
        import math
        if not all(math.isfinite(v) and v>=0 for v in (c_e,c_c)):
            raise ValueError('invalid cost coefficients')
        es=self.elements;indices,masks,_=self.neighbors()
        incoming={e.id:{es[j].id for j,on in zip(row,mask) if on}
                  for e,row,mask in zip(es,indices,masks)}
        n,pairs=budget_counts({e.id:self.role(e.id) for e in es},incoming)
        return dict(elements=n,active_couplings=pairs,total=c_e*n+c_c*pairs)

    def cut_off(self,id,value=None):
        result=C.c_double(0 if value is None else value)
        self._call('cut',id,C.byref(result),int(value is not None));return result.value

    def lesions(self,ids):
        ids=list(ids);self._call('lesions',(C.c_uint64*len(ids))(*ids),len(ids))

    def output(self):
        result=(C.c_double*2)();self._call('output',result);return tuple(result)

    def comparator(self,mode):
        if mode not in ('k_zero','fixed_structure','site_body_off'):raise ValueError('unknown evaluator comparator')
        self._call('comparator',{'k_zero':1,'fixed_structure':2,'site_body_off':3}[mode])
        if mode=='k_zero':self.params.K=0.

    def stage_terms(self):
        # Four RHS stages, one [drive,coupling,wall_x,wall_y] per element.
        result=(C.c_double*(16*len(self)))()
        self._call('stage_terms',result,len(result))
        return [[list(result[(k*len(self)+j)*4:(k*len(self)+j+1)*4])
                 for j in range(len(self))] for k in range(4)]

    def plv(self,*args,**kwargs):raise ValueError('rev7 estimators require timestamped Frame.excursion; use Rev7Medium.offsets')
    def measure(self,*args,**kwargs):raise ValueError('use Rev7Medium.lock with validity masks')
    def groups(self,*args,**kwargs):raise ValueError('use rev7_qual_v1 with cohort excursion masks')
    def configure_growth(self,*args,**kwargs):raise ValueError('use Rev7Medium growth rules')
    def apply_growth_rules(self):raise ValueError('use Rev7Medium growth rules')

    def phase_scale(self,value):self._call('phase_scale',value)

    def excursion(self):
        result=(C.c_double*len(self))();self._call('excursion',result,len(result));return list(result)

    def pin(self,id):
        result=(C.c_double*3)();self._call('pin',id,result)
        return bool(result[0]),(result[1],result[2]) if result[0] else None

    def motion_neighbors(self):
        n,k=len(self),self.params.k
        indices=(C.c_int32*(n*k))();counts=(C.c_int32*n)()
        self._call('motion_neighbors',indices,counts,n*k)
        return [list(indices[i*k:i*k+counts[i]]) for i in range(n)]

    def policy(self):
        values=(C.c_double*3)();self._call('policy',values);return values[0],bool(values[1]),bool(values[2])

    def strong_neighbors(self):
        """Selected phase edges filtered by strength; never the RHS neighbor list."""
        n,k=len(self),self.params.k
        indices=(C.c_int32*(n*k))();counts=(C.c_int32*n)()
        self._call('strong_neighbors',indices,counts,n*k)
        return [list(indices[i*k:i*k+counts[i]]) for i in range(n)]

    def reference_drives(self):
        n=self._lib.gm_reference_drive_count(self._handle);values=(Drive*n)()
        self._call('reference_drives',values,n);return list(values)

    def reference_lesions(self):
        n=self._lib.gm_reference_lesion_count(self._handle);values=(C.c_uint64*n)()
        self._call('reference_lesions',values,n);return list(values)

    def reference_commit(self,state,excursion,terms,h):
        import numpy as np
        arrays=[np.ascontiguousarray(v,dtype=float) for v in (state,excursion,terms)]
        self._call('reference_commit',*[v.ctypes.data_as(C.POINTER(C.c_double)) for v in arrays],len(self),h)

    def reference_step(self,h):
        from .rev7_rhs import step
        step(self,h)

    @classmethod
    def load(cls,data):
        data=Path(data).read_bytes() if isinstance(data,(Path,str)) else bytes(data)
        lib=library();buf=C.create_string_buffer(data);handle=lib.gm_load(buf,len(data))
        if not handle: raise ValueError('invalid rev7 snapshot')
        try:
            offset=8+len(b'rev7-medium-v1')
            return cls._adopt(lib,handle,Params.from_buffer_copy(data[offset:offset+C.sizeof(Params)]))
        except Exception:
            lib.gm_destroy(handle);raise
