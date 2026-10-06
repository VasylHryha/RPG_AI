"""Kernel bench: baseline vs variant option-B dylib, bitwise frame equality + thread CPU."""
import sys, time, ctypes as ct, copy
sys.path.insert(0,'/Users/new/RiderProjects/ai_RPG_test')
import numpy as np
from geomind import c6_r4_field as F, c6_r4_field_protocol as P

PTR=ct.POINTER(ct.c_double); IP=ct.POINTER(ct.c_int)
def load(path):
    lib=ct.CDLL(path)
    tail=[PTR,PTR,PTR,PTR,IP,PTR,PTR,IP,PTR,PTR,PTR]
    lib.field_run.argtypes=[ct.c_int]*3+[ct.c_double]*2+[ct.c_int]*2+tail
    lib.field_run.restype=ct.c_int
    lib.field_rhs.argtypes=[ct.c_int]*3+[ct.c_double]+tail
    lib.field_rhs.restype=ct.c_int
    if 'base' in path:
        lib.option_b_cache_limits.argtypes=[ct.c_uint64]*4;lib.option_b_cache_limits(0,0,0,32*1024*1024)
    else:
        lib.option_b_cache_limits.argtypes=[ct.c_uint64]*3;lib.option_b_cache_limits(0,0,128*1024*1024)
    return lib

def owners():
    s=P.load_settings();r=np.random.default_rng(882901)
    o=F.population(r,F.medium(r,s['model']),0,0,24)
    o.z=.55*np.exp(1j*r.uniform(-np.pi,np.pi,25));o.cohorts[0].carrier=o.z.copy()
    out=[]
    a=o.clone();a.cohorts[0].selected=(0,1,2,5,7);a.cohorts[0].output=1.;out.append(('1c-on',a))
    b=o.clone();b.cohorts[0].selected=(0,1,2);b.cohorts[0].output=0.;out.append(('1c-off-retired',b))
    c=F.population(np.random.default_rng(552),a.clone(),1,0,24);c.cohorts[0].output=0.;c.cohorts[-1].selected=(1,2,3,4);c.cohorts[-1].output=1.;out.append(('2c-on',c))
    d=a.clone();d.cohorts[0].mode='no_geometry_to_mode';d.cohorts[0].origin=d.cohorts[0].x.copy();d.cohorts[0].x[0]+=[.1,.2];out.append(('1c-mode2',d))
    e=a.clone();e.cohorts[0].mode='no_r';out.append(('1c-no_r',e))
    f=a.clone();f.cohorts[0].mode='no_mode_to_geometry';out.append(('1c-mode3',f))
    g=F.population(np.random.default_rng(553),c.clone(),2,0,24);g.cohorts[1].output=0.;g.cohorts[-1].selected=(1,2,3,4,9,11);g.cohorts[-1].output=1.;out.append(('3c-on',g))
    return out

def run(lib,owner,duration,dt,sample_dt):
    steps=F.exact_steps(duration,dt);sample=F.exact_steps(sample_dt,dt)
    ns,n,nc,a=F.arguments(owner)
    frames=np.empty((steps//sample+1,len(a[0])),dtype='f8')
    ptrs=[v.ctypes.data_as(IP if i in (4,7) else PTR) for i,v in enumerate(a)]
    c0=time.thread_time()
    err=lib.field_run(ns,n,nc,owner.time,dt,steps,sample,*ptrs,frames.ctypes.data_as(PTR))
    c1=time.thread_time()
    assert err==0,err
    return frames,c1-c0

def rhs(lib,owner):
    ns,n,nc,a=F.arguments(owner);out=np.empty_like(a[0])
    ptrs=[v.ctypes.data_as(IP if i in (4,7) else PTR) for i,v in enumerate(a)]
    assert lib.field_rhs(ns,n,nc,owner.time,*ptrs,out.ctypes.data_as(PTR))==0
    return out

if __name__=='__main__':
    base=load(sys.argv[1]);var=load(sys.argv[2]);reps=int(sys.argv[3]) if len(sys.argv)>3 else 3
    tb=tv=0.
    for name,o in owners():
        for dt in (.005,.00125):
            bt=[];vt=[]
            for r in range(reps):
                fb,t1=run(base,o,2.,dt,.005);fv,t2=run(var,o,2.,dt,.005)
                bt.append(t1);vt.append(t2)
                if not np.array_equal(fb.view('u8'),fv.view('u8')):
                    print('MISMATCH',name,dt,np.abs(fb-fv).max());sys.exit(1)
            assert np.array_equal(rhs(base,o).view('u8'),rhs(var,o).view('u8')),name
            tb+=min(bt);tv+=min(vt)
            print(f'{name:16s} dt={dt:<8} base {min(bt)*1e3:8.1f} ms  var {min(vt)*1e3:8.1f} ms  ratio {min(vt)/min(bt):.3f}')
    print(f'TOTAL base {tb:.3f}s var {tv:.3f}s ratio {tv/tb:.3f}  (all bit-identical)')
