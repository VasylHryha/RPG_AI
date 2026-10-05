"""Engineering worlds/fixtures only. No final-entropy argument or panel path."""
from contextlib import nullcontext
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import sys
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
# The declared budget includes native numerical helpers: prohibit extra BLAS
# teams before importing NumPy, in both sequential and parallel CLI processes.
for variable in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS',
                 'VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[variable]='1'
import numpy as np
from geomind import c6_option_b as O, c6_r4_field as F, c6_r4_field_assay as A, c6_r4_field_protocol as P
from geomind.c6_r4_integrity import validate_pin

def machine():
    return {'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
            'load_average':list(os.getloadavg()),'cpu_count':os.cpu_count(),'platform':platform.platform()}

def write(path,data):
    if path.exists(): raise FileExistsError(path)
    temp=path.with_suffix(path.suffix+'.tmp')
    with temp.open('xb') as out:
        out.write(data);out.flush();os.fsync(out.fileno())
    os.replace(temp,path)

def fixture():
    s=P.load_settings();random=np.random.default_rng(882901)
    o=F.population(random,F.medium(random,s['model']),0,0,24)
    o.z=.55*np.exp(1j*random.uniform(-np.pi,np.pi,25));o.cohorts[0].carrier=o.z.copy()
    o.cohorts[0].selected=(0,1,2)
    o=F.population(np.random.default_rng(552),o,1,0,24)
    o.cohorts[-1].selected=(1,2,3);o.time=17.3
    grid=A.GridSet([o]*3,s)
    descriptor=A.descriptor(grid,.3,'performance-fixture')
    return {'kind':'ENGINEERING_FIXTURE_ONLY','initial_identity':o.identity(),'descriptor':descriptor,'checks':grid.checks}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend',choices=('reference','native'),required=True)
    parser.add_argument('--entropy',choices=('smoke','development'),default='smoke')
    parser.add_argument('--world',type=int,choices=(0,1),default=0)
    parser.add_argument('--fixture',action='store_true')
    parser.add_argument('--audit',action='store_true')
    parser.add_argument('--parallel',action='store_true')
    parser.add_argument('--schedule',choices=('forward','reverse'),default='forward')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.parallel and args.backend != 'native':parser.error('--parallel requires --backend native')
    args.output.mkdir(parents=True,exist_ok=False)
    s=P.load_settings();pin=validate_pin(ROOT)
    meta={'kind':'OPTION_B_ENGINEERING_ONLY','backend':args.backend,'audit':args.audit,
          'parallel':args.parallel,'schedule':args.schedule,
          'thread_budget':{'world_workers':2,'threads_per_world':5 if args.parallel else 1,
                           'blas_threads':1},
          'entropy':s[args.entropy+'_entropy'],'world':args.world,'fixture':args.fixture,
          'start_machine':machine(),'source_pin':pin}
    write(args.output/'START.json',(json.dumps(meta,indent=2)+'\n').encode())
    started=time.perf_counter();cpu=time.process_time()
    with O.backend(args.backend,args.audit) as checker:
        from geomind.c6_option_b_parallel import parallel
        with parallel(args.schedule) if args.parallel else nullcontext() as scheduler:
            row=fixture() if args.fixture else P.run_world(s,meta['entropy'],args.world)
            audit=checker.summary() if checker else None
            cache=scheduler.summary() if scheduler else O.cache_stats(O.load()[0]) if args.backend=='native' else None
    compute=time.perf_counter()-started
    compute_cpu=time.process_time()-cpu
    io=time.perf_counter();io_cpu=time.process_time()
    raw=json.dumps(row,allow_nan=False,separators=(',',':')).encode()
    compressed=gzip.compress(raw,mtime=0)
    write(args.output/'world.json.gz',compressed)
    io_seconds=time.perf_counter()-io
    meta.update(compute_seconds=compute,compute_cpu_seconds=compute_cpu,
                world_seconds=row.get('seconds'),serialization_write_seconds=io_seconds,
                serialization_cpu_seconds=time.process_time()-io_cpu,
                total_seconds=compute+io_seconds,raw_bytes=len(raw),compressed_bytes=len(compressed),
                world_sha256=hashlib.sha256(compressed).hexdigest(),end_machine=machine(),
                audit=audit,native_cache=cache,invalid=row.get('invalid'),chain_complete=row.get('chain_complete'))
    peak=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    meta['post_serialization_peak_rss_bytes']=peak if sys.platform=='darwin' else peak*1024
    write(args.output/'COSTS.json',(json.dumps(meta,indent=2)+'\n').encode())
    print(json.dumps({k:meta[k] for k in ('backend','world','compute_seconds','world_seconds','invalid','chain_complete','audit')}),flush=True)

if __name__=='__main__':main()
