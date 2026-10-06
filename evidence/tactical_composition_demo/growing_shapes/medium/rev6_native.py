"""Versioned native rev6 RHS. Never loads or rebuilds a 5.1 image implicitly."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import platform
from .medium import Medium, Params, _library

HERE = Path(__file__).parent
BUILD = HERE / '_rev6_build'
IMAGE = BUILD / ('rev6_medium.dylib' if platform.system() == 'Darwin' else 'rev6_medium.so')


def library():
    manifest = json.loads((BUILD / 'build.json').read_text())
    if manifest['version'] != 'rev6_rhs_v1':
        raise RuntimeError('rev6 native version mismatch')
    for name, digest in manifest['source_sha256'].items():
        if hashlib.sha256((HERE/name).read_bytes()).hexdigest() != digest:
            raise RuntimeError(f'stale rev6 native source: {name}')
    if hashlib.sha256(IMAGE.read_bytes()).hexdigest() != manifest['binary_sha256']:
        raise RuntimeError('rev6 binary identity mismatch')
    lib = _library(IMAGE)
    h,d,u,i,P = C.c_void_p,C.c_double,C.c_uint64,C.c_int,C.POINTER
    for name, args in {
        'add_role':[h,d,d,d,d,i,P(u)], 'role':[h,u,P(i)],
        'cut':[h,u,P(d),i], 'lesions':[h,P(u),i], 'output':[h,P(d)],
        'stage_terms':[h,P(d),i],
    }.items():
        fn=getattr(lib,'gm_'+name);fn.restype=i;fn.argtypes=args
    return lib


class Rev6Native(Medium):
    def __init__(self, seed=0, params=None):
        self._lib=library();self.params=params or Params(window=101,min_samples=100)
        self._handle=self._lib.gm_create(seed,C.byref(self.params))
        if not self._handle: raise ValueError('invalid rev6 native state')

    def add(self,x,y,phase=0.,rate=0.,role='element'):
        if role not in ('element','output'): raise ValueError('unknown role')
        value=C.c_uint64()
        self._call('add_role',x,y,phase,rate,int(role=='output'),C.byref(value))
        return value.value

    def split(self,*args,**kwargs):
        raise ValueError('B2/splitting is disabled in revision 6')

    def role(self,id):
        value=C.c_int();self._call('role',id,C.byref(value))
        return 'output' if value.value else 'element'

    def cut_off(self,id,value=None):
        result=C.c_double(0 if value is None else value)
        self._call('cut',id,C.byref(result),int(value is not None));return result.value

    def lesions(self,ids):
        ids=list(ids);self._call('lesions',(C.c_uint64*len(ids))(*ids),len(ids))

    def output(self):
        result=(C.c_double*2)();self._call('output',result);return tuple(result)

    def stage_terms(self):
        # Four RHS stages, one [drive,coupling,wall_x,wall_y] per element.
        result=(C.c_double*(16*len(self)))()
        self._call('stage_terms',result,len(result))
        return [[list(result[(k*len(self)+j)*4:(k*len(self)+j+1)*4])
                 for j in range(len(self))] for k in range(4)]

    @classmethod
    def load(cls,data):
        data=Path(data).read_bytes() if isinstance(data,(Path,str)) else bytes(data)
        lib=library();buf=C.create_string_buffer(data);handle=lib.gm_load(buf,len(data))
        if not handle: raise ValueError('invalid rev6 snapshot')
        try:
            offset=8+len(b'rev6-medium-v1')
            return cls._adopt(lib,handle,Params.from_buffer_copy(data[offset:offset+C.sizeof(Params)]))
        except Exception:
            lib.gm_destroy(handle);raise
