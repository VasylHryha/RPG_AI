"""Profiling harness (scratch, engineering only): smoke world 0, native parallel path.

Records per-thread CPU (thread_time) attribution to native field_run calls,
Python diagnostics, scheduler barriers and duplicate full-input native calls.
"""
import os, sys, time, json, hashlib, threading, ctypes as ct, collections, gzip
for v in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[v]='1'
ROOT='/Users/new/RiderProjects/ai_RPG_test'
sys.path.insert(0,ROOT)
import numpy as np
from geomind import c6_option_b as O, c6_r4_field as F, c6_r4_field_assay as A, c6_r4_field_protocol as P, c4_detect as D
from geomind import c6_option_b_parallel as PP

OUT=sys.argv[1]; entropy_kind=sys.argv[2] if len(sys.argv)>2 else 'smoke'; world=int(sys.argv[3]) if len(sys.argv)>3 else 0
os.makedirs(OUT,exist_ok=False)
lock=threading.Lock()
acc=collections.defaultdict(lambda:[0,0.,0.])   # name -> calls, cpu, wall (inclusive, per-thread)
def timed(name,fn):
    def wrapper(*a,**k):
        c0=time.thread_time();w0=time.perf_counter()
        try:return fn(*a,**k)
        finally:
            c1=time.thread_time();w1=time.perf_counter()
            with lock:
                r=acc[(name,threading.current_thread().name.startswith('c6-grid'))];r[0]+=1;r[1]+=c1-c0;r[2]+=w1-w0
    return wrapper

calls=[]   # native field_run records
keys=collections.Counter()
def nbytes(ns,n,nc):
    return [8*(2*ns+nc*(3*n+2*ns)),16*ns,8*ns,64*ns,4*ns*ns,8*n*nc,8*n*nc,4*nc,16*n*nc,72]
class Proxy:
    def __init__(self,lib):self.lib=lib
    def __getattr__(self,k):return getattr(self.lib,k)
    def field_run(self,*args):
        ns,n,nc,start,dt,steps,sample=args[:7]
        h=hashlib.sha256(repr((ns,n,nc,float(start).hex(),float(dt).hex(),steps,sample)).encode())
        masks=None
        for i,(p,b) in enumerate(zip(args[7:17],nbytes(ns,n,nc))):
            raw=ct.string_at(p,b);h.update(raw)
            if i==6:masks=np.frombuffer(raw,dtype='f8')
        key=h.hexdigest()
        eligible=nc==1 and not (masks>0).any()
        c0=time.thread_time();w0=time.perf_counter()
        code=self.lib.field_run(*args)
        c1=time.thread_time();w1=time.perf_counter()
        with lock:
            keys[key]+=1
            calls.append((key,keys[key],ns,n,nc,steps,float(dt),bool(eligible),bool((masks<0).any()) if nc else False,
                          c1-c0,w1-w0,threading.current_thread().name))
        return code

barriers=[]
pylog=[]
def main():
    s=P.load_settings()
    entropy=s[entropy_kind+'_entropy']
    started=time.perf_counter();cpu=time.process_time()
    with O.backend('native',False) as checker:
        orig_native=F.native
        lib,record=orig_native()
        prox=Proxy(lib)
        F.native=lambda:(prox,record)
        with PP.parallel('forward') as sched:
            orig_completed=sched.completed
            def completed(fn,jobs,costs=None):
                w0=time.perf_counter();c0=time.thread_time()
                for item in orig_completed(fn,jobs,costs):
                    yield item
                barriers.append((len(jobs),w0,time.perf_counter(),time.thread_time()-c0))
            sched.completed=completed
            orig_cached=F.cached_array
            def cached(cache,limit,key,compute):
                name='passive_compute' if cache is F._PASSIVE_CACHE else 'emission_compute'
                box=[False,0.]
                def comp():
                    c0=time.thread_time();r=compute();box[0]=True;box[1]=time.thread_time()-c0;return r
                r=orig_cached(cache,limit,key,timed(name,comp))
                with lock:pylog.append((name,hashlib.sha256(repr(key).encode()).hexdigest()[:16],box[0],int(r.nbytes),box[1]))
                return r
            F.cached_array=cached
            # Instrument Python hot spots (inclusive, per thread role).
            PP.grid_block=timed('grid_block',PP.grid_block)
            F.emissions=timed('emissions',F.emissions)
            A.state_errors=timed('state_errors',A.state_errors)
            D.window_statistics=timed('window_statistics',D.window_statistics)
            D.locked_pairs=timed('locked_pairs',D.locked_pairs)
            D.components=timed('components',D.components)
            F.Owner.identity=timed('identity',F.Owner.identity)
            F.Owner.clone=timed('clone',F.Owner.clone)
            F.Owner.pack=timed('pack',F.Owner.pack)
            F.Owner.unpack=timed('unpack',F.Owner.unpack)
            F.Owner.validate=timed('validate',F.Owner.validate)
            P.snapshot=timed('snapshot',P.snapshot)
            P.rolling_persistence=timed('rolling_persistence',P.rolling_persistence)
            F.arguments=timed('arguments',F.arguments)
            A.descriptor=timed('descriptor',A.descriptor)
            A.qualification=timed('qualification',A.qualification)
            A.recovery=timed('recovery',A.recovery)
            A.causal=timed('causal',A.causal)
            P.qualify_episode=timed('qualify_episode',P.qualify_episode)
            P.operation=timed('operation',P.operation)
            row=P.run_world(s,entropy,world)
            summary=sched.summary()
    wall=time.perf_counter()-started;pcpu=time.process_time()-cpu
    raw=json.dumps(row,allow_nan=False,separators=(',',':')).encode()
    with open(OUT+'/world.json.gz','wb') as f:f.write(gzip.compress(raw,mtime=0))
    dup=[c for c in calls if c[1]>1]
    res={'wall':wall,'process_cpu':pcpu,'world_seconds':row['seconds'],'invalid':row['invalid'],'chain':row['chain_complete'],
         'native_calls':len(calls),'native_cpu':sum(c[9] for c in calls),'native_wall':sum(c[10] for c in calls),
         'dup_calls':len(dup),'dup_cpu':sum(c[9] for c in dup),
         'dup_noneligible_cpu':sum(c[9] for c in dup if not c[7]),
         'acc':{f'{k[0]}|{"worker" if k[1] else "coord"}':v for k,v in acc.items()},
         'barriers':barriers,'cache':summary,'native_stats':O.cache_stats(lib)}
    json.dump(res,open(OUT+'/PROFILE.json','w'),indent=1)
    with open(OUT+'/pycache.jsonl','w') as f:
        for c in pylog:f.write(json.dumps(c)+'\n')
    with open(OUT+'/calls.jsonl','w') as f:
        for c in calls:f.write(json.dumps(c)+'\n')
    print(json.dumps({k:res[k] for k in ('wall','process_cpu','native_calls','native_cpu','dup_calls','dup_cpu','dup_noneligible_cpu')}))
main()
