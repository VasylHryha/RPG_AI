"""Native frame batch and exact float64 ragged banks; padding only on consumption."""
import ctypes,os,subprocess,sys
from pathlib import Path
import numpy as np
import common as c
LIB=None

def library():
    global LIB
    if LIB is not None:return LIB
    identity=''.join(c.sha(c.HERE/p) for p in ('native_candidates.cpp','candidates.h','tools.h','movement.h'))
    import hashlib
    folder=c.HERE/'_local/native_candidates';folder.mkdir(parents=True,exist_ok=True)
    path=folder/(hashlib.sha256(identity.encode()).hexdigest()+('.dylib' if sys.platform=='darwin' else '.so'))
    if not path.exists():
        tmp=path.with_name(path.name+f'.{os.getpid()}.tmp')
        subprocess.run(['nice','-n','15','c++','-std=c++17','-O3','-ffp-contract=off','-fPIC','-shared',str(c.HERE/'native_candidates.cpp'),'-o',str(tmp)],check=True,timeout=60,capture_output=True)
        os.replace(tmp,path)
    LIB=ctypes.CDLL(str(path));D=ctypes.POINTER(ctypes.c_double)
    LIB.candidate_batch.argtypes=[D,ctypes.POINTER(ctypes.c_int),ctypes.c_double,ctypes.c_double,ctypes.c_int,ctypes.POINTER(D)]
    LIB.candidate_batch.restype=ctypes.c_long;LIB.candidate_error.restype=ctypes.c_char_p
    return LIB

def batch(row,allow_missing_aim=False):
    ids=sorted(u[0] for u in row['units'] if u[1]==0)
    # Native validates every actor; Python validates empty frames as well.
    if not ids:
        if row['own']:raise ValueError('candidate own-state coverage')
    matrices=[np.asarray(row[k],dtype=np.float64).reshape(-1,w) for k,w in zip(('units','own','shells','shots','fields','casts'),(23,10,9,7,5,7))]
    velocities=np.asarray([[int(k),*v] for k,v in row.get('longVelocity',{}).items()],dtype=np.float64).reshape(-1,3)
    matrices.append(velocities);counts=np.asarray([len(v) for v in matrices],dtype=np.int32)
    data=np.concatenate([v.ravel() for v in matrices]);result=ctypes.POINTER(ctypes.c_double)();lib=library()
    size=lib.candidate_batch(data.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),counts.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),row['width'],row['height'],int(allow_missing_aim),ctypes.byref(result))
    if size<0:raise ValueError(lib.candidate_error().decode())
    return np.ctypeslib.as_array(result,shape=(size,)).copy()

def unpack(flat):
    at=0;out={}
    while at<len(flat):
        id,na,nm=map(int,flat[at:at+3]);at+=3
        end=at+11*(na+nm);values=flat[at:end].reshape(na+nm,11)
        out[id]=(values[:na],values[na:]);at=end
    return out

def packed(banks,ids):
    from candidates import MAX_AIM,MAX_MOVE,FEATURES
    out={}
    for head,cap,column in (('aim',MAX_AIM,0),('move',MAX_MOVE,1)):
        pts=np.zeros((len(ids),cap,2));features=np.zeros((len(ids),cap,FEATURES));valid=np.zeros((len(ids),cap));sources=np.full((len(ids),cap),-1,dtype=np.int64)
        for i,id in enumerate(ids):
            v=banks[id][column];n=len(v);pts[i,:n]=v[:,:2];features[i,:n,11:18]=v[:,2:9];features[i,np.arange(n),v[:,9].astype(np.int64)]=1;valid[i,:n]=1;sources[i,:n]=v[:,10]
        out.update({head+'_points':pts,head+'_features':features,head+'_valid':valid,head+'_sources':sources})
    return out
