"""Short synthetic contracts/benchmarks only: no world or panel entrypoint."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
for variable in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS',
                 'VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[variable]='1'
import numpy as np
from geomind import c6_option_b as O, c6_r4_field as F, c6_r4_field_protocol as P
from geomind.c6_r4_integrity import validate_pin


def raw(lib,owner,steps=100):
    ns,n,nc,arrays=F.arguments(owner)
    frames=np.empty((steps+1,len(arrays[0])),dtype='f8')
    pointers=[a.ctypes.data_as(ct.POINTER(ct.c_int if i in (4,7) else ct.c_double)) for i,a in enumerate(arrays)]
    code=lib.field_run(ns,n,nc,owner.time,.005,steps,1,*pointers,frames.ctypes.data_as(O.PTR))
    if code:raise RuntimeError('synthetic native error: '+str(code))
    return frames


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    source_pin=validate_pin(ROOT);lib,build=O.load();ref,reference_build=O.reference()
    random=np.random.default_rng(882901)
    owner=F.population(random,F.medium(random,P.load_settings()['model']),0,0,6)
    owner.cohorts[0].selected=(0,1,2)
    compared=0;calls=0;rows=[]
    expected=raw(ref,owner)
    def check(value,reference):
        nonlocal compared,calls
        if not np.array_equal(value.view('u8'),reference.view('u8')):
            raise RuntimeError('synthetic full-flow bit mismatch')
        compared+=value.size;calls+=1
    for label,limits in [('uncached',(0,0,0)),('pressure',(128*1024,32*1024,64*1024)),
                         ('default',O.CACHE_LIMITS)]:
        lib.option_b_cache_limits(*limits)
        start=time.perf_counter();cpu=time.process_time()
        for i in range(30):
            changed=owner.clone();changed.z+=.001j*i
            check(raw(lib,changed),raw(ref,changed))
        rows.append({'case':label,'calls':30,'wall_seconds':time.perf_counter()-start,
                     'process_cpu_seconds':time.process_time()-cpu,'stats':O.cache_stats(lib)})
    # Native caches are process-wide and shared by workers. Churn clock/drive
    # keys concurrently under small limits and compare each complete result
    # with the original ABI on that thread.
    pressure=(12000,12000,5000)
    lib.option_b_cache_limits(*pressure)
    def worker(index):
        values=0
        for i in range(60):
            changed=owner.clone();changed.time=(i%17)*.01
            changed.psi[0,0]+=.001*index
            candidate=raw(lib,changed,4);reference=raw(ref,changed,4)
            if not np.array_equal(candidate.view('u8'),reference.view('u8')):
                raise RuntimeError('worker cache-pressure bit mismatch')
            values+=candidate.size
        return {'worker':index,'calls':60,'float64_values':values}
    with ThreadPoolExecutor(max_workers=4) as pool:workers=list(pool.map(worker,range(4)))
    stats=O.cache_stats(lib)
    if (stats['retired_bytes']+stats['control_bytes']>pressure[0] or stats['medium_bytes']>pressure[1]
            or stats['drive_bytes']>pressure[2]):
        raise RuntimeError('shared payload bound exceeded')
    workers.append({'shared_stats_after_concurrent_churn':stats})
    lib.option_b_cache_clear()
    if any(O.cache_stats(lib).values()):raise RuntimeError('shared cache clear incomplete')
    lib.option_b_cache_limits(*O.CACHE_LIMITS)
    # Unit timing has no reference audit in the measured interval. No hardware
    # or full-world speed claim: short durations and shared-machine noise apply.
    timings=[]
    for label,kernel,limits in [('reference',ref,None),('disabled',lib,(0,0,0)),('warm',lib,O.CACHE_LIMITS)]:
        if limits is not None:lib.option_b_cache_limits(*limits)
        for _ in range(3):check(raw(kernel,owner),expected)
        start=time.perf_counter();cpu=time.process_time()
        for _ in range(40):value=raw(kernel,owner)
        timings.append({'case':label,'calls':40,'wall_seconds':time.perf_counter()-start,
                        'process_cpu_seconds':time.process_time()-cpu})
        check(value,expected)
    lib.option_b_cache_limits(*O.CACHE_LIMITS)
    peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result={'passed':True,'kind':'SYNTHETIC_ENGINEERING_ONLY','entropy':882901,
        'source_pin':source_pin,'option_b_build':build,'reference_build':reference_build,
        'python':sys.version,'numpy':np.__version__,'platform':platform.platform(),
        'load_average':list(os.getloadavg()),'calls_bit_compared':calls+sum(w.get('calls',0) for w in workers),
        'float64_values_bit_compared':compared+sum(w.get('float64_values',0) for w in workers),
        'maximum_error':0.,'cache_churn':rows,'workers':workers,'unit_timings':timings,
        'peak_rss_bytes':int(peak if sys.platform=='darwin' else peak*1024),
        'helper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'limits':'Payload bounds exclude container overhead, in-flight arrays and protocol evidence; not an RSS bound.'}
    O.verify_build();O.reference_record()
    (args.output/'CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('passed','calls_bit_compared','float64_values_bit_compared','unit_timings','peak_rss_bytes')}))


if __name__=='__main__':main()
