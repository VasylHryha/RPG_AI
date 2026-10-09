"""One native batch per cached head; no candidate generation or model inputs."""
import ctypes,hashlib,os,subprocess,sys
import numpy as np
import common as c
LIB=None

def library():
    global LIB
    if LIB is not None:return LIB
    digest=hashlib.sha256(''.join(c.sha(c.HERE/p) for p in ('cache_codec.cpp','native_cache_codec.py')).encode()).hexdigest()
    root=c.HERE/'_local/cache_codec';root.mkdir(parents=True,exist_ok=True)
    path=root/(digest+('.dylib' if sys.platform=='darwin' else '.so'))
    if not path.exists():
        tmp=path.with_name(path.name+f'.{os.getpid()}.tmp')
        subprocess.run(['nice','-n','15','c++','-std=c++17','-O3','-ffp-contract=off','-fPIC','-shared',str(c.HERE/'cache_codec.cpp'),'-o',str(tmp)],check=True,timeout=60,capture_output=True)
        os.replace(tmp,path)
    LIB=ctypes.CDLL(str(path));ptr=ctypes.c_void_p
    LIB.codec_bank.argtypes=[ctypes.c_int]*5+[ctypes.c_double]*2+[ptr]*17
    LIB.codec_bank.restype=None
    LIB.codec_plane.argtypes=[ptr]*4+[ctypes.c_int64,ctypes.c_int,ctypes.c_int];LIB.codec_plane.restype=None
    LIB.codec_mapping.argtypes=[ptr,ptr]+[ctypes.c_int]*3;LIB.codec_mapping.restype=ctypes.c_int
    return LIB

def pointer(value):return None if value is None else value.ctypes.data

def bank(arrays,head,actual=None):
    expand=actual is None;n,cap=arrays[head+'_types'].shape
    if cap>1280:raise ValueError('codec candidate envelope')
    names=('codec_own','codec_units','codec_nearest','codec_shift','codec_gun','codec_artcentre','codec_centre','codec_velocity','codec_threat')
    values=[np.require(arrays[k],dtype=np.float64,requirements=['C','A']) for k in names]
    values += [np.require(arrays[head+'_'+k],dtype=d,requirements=['C','A']) for k,d in (('types',np.int8),('sources',np.int16),('valid',np.uint8))]
    actual=None if expand else np.require(actual,dtype=np.float64,requirements=['C','A'])
    point_bits=np.require(arrays[head+'_point_bits'],dtype=np.uint64,requirements=['C','A']) if expand else None
    numeric_bits=np.require(arrays[head+'_numeric_bits'],dtype=np.uint32,requirements=['C','A']) if expand else None
    points=np.empty((n,cap,2),dtype=np.float64);numeric=np.empty((n,cap,7),dtype=np.float32)
    library().codec_bank(int(expand),int(head=='move'),n,cap,len(values[1]),*map(float,arrays['codec_arena']),
                         *[pointer(v) for v in values],pointer(actual),pointer(point_bits),pointer(numeric_bits),pointer(points),pointer(numeric))
    return points,numeric

def plane(value,width,mode,previous=None,older=None):
    unsigned=np.dtype('u'+str(width));out=np.empty(len(value)//width,dtype=unsigned)
    library().codec_plane(pointer(value),pointer(out),pointer(previous),pointer(older),len(out),width,mode)
    return out


def mapping(members,cap):
    members=np.require(members,dtype=np.int16,requirements=['C','A'])
    if members.ndim!=3 or members.shape[2]!=64:raise ValueError('codec hierarchy shape')
    n,f,_=members.shape
    out=np.empty((n,cap,2),dtype=np.int16)
    if cap<=0 or f>32767:raise ValueError('codec mapping envelope')
    if library().codec_mapping(pointer(members),pointer(out),n,cap,f):raise ValueError('codec member out of bounds')
    return out
