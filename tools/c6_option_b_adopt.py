"""Bounded decision-0032 engineering adoption; stored smoke/development only.
Run under caffeinate. Refuses to overwrite any output. No panel or mutation.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
from tools import c6_option_b_adoption_analyze as A, c6_option_b_compare as C
from tools import build_c6_option_b as B
from geomind import c6_option_b as O, c6_r4_field_protocol as P
from geomind.c6_r4_integrity import validate_pin

# Original references are immutable inputs. Fix identities BEFORE measuring.
REFERENCES={
 'smoke_0':('evidence/c6_option_b/reference_smoke_0/world.json.gz','aeea74a98f3ffc1dec799633269382fa9b111d8a947e50bf3b4f2a79f290e0aa',25836899),
 'smoke_1':('evidence/c6_option_b/reference_smoke_1/world.json.gz','ae0e47fcb98711f8606f2ce8576dd04df24d989374e679398a8cdb1a0bb4b87f',12312845),
 'development_0':('evidence/c6_option_b/audited_v3_development_0/world.json.gz','1cd816944d20012f6369ea855f8d9468f0c4c1572ef5507e5bc0bc8aa095e57e',23343948),
 'development_1':('evidence/c6_option_b/quiet_session_20261006_161801/worlds/reference_development_1/world.json.gz','ac716e25112c562bd2f92a44bb9922ec4e36e8548292542bfb1f9c76e18db6ce',23336253),
}

def write(path,data):
    with path.open('x') as stream:json.dump(data,stream,indent=2,allow_nan=False);stream.write('\n')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--task-start',type=float,required=True,help='wall-clock start of builds/tests/compute batch')
    args=ap.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    deadline=args.task_start+3600;started=time.time();awake=time.monotonic()
    identity={'kind':'ENGINEERING_ADOPTION_0032','macos_build':B.require_platform(),
              'builds':{k:O.verify_build(B.library_for(k),k) for k in ('exact','inexact')},
              'reference_build':O.reference_record(),'source_pin':validate_pin(ROOT),
              'dependencies':{str(p.relative_to(ROOT)):sha(p) for p in
                  [Path(__file__),ROOT/'tools/c6_option_b_check.py',ROOT/'tools/c6_option_b_adoption_analyze.py',
                   ROOT/'tools/c6_option_b_compare.py',ROOT/'tools/build_c6_option_b.py',
                   ROOT/'geomind/c6_option_b.py',ROOT/'geomind/c6_option_b_parallel.py']},
              'protected':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'STATUS.json',ROOT/'docs/PLAN_CURRENT.md']},
              'exact_references':{},'task_start_epoch':args.task_start,
              'launch':['caffeinate','-dims',sys.executable,str(Path(__file__)),*sys.argv[1:]],
              'initial_projection_seconds':3300,'compute_deadline_epoch':deadline}
    for name,(rel,expected,size) in REFERENCES.items():
        path=ROOT/rel;receipt=json.loads((path.parent/'COSTS.json').read_text())
        if sha(path)!=expected or path.stat().st_size!=size or receipt['world_sha256']!=expected:
            raise RuntimeError('stored reference identity mismatch: '+name)
        identity['exact_references'][name]={'path':rel,'sha256':expected,'bytes':size,
            'costs_sha256':sha(path.parent/'COSTS.json')}
    write(out/'IDENTITY.json',identity)
    def preserve():
        if B.require_platform()!=identity['macos_build']:raise RuntimeError('OS changed during adoption')
        for name,build in identity['builds'].items():
            if O.verify_build(B.library_for(name),name)!=build:raise RuntimeError('build changed during adoption')
        for rel,expected in {**identity['dependencies'],**identity['protected']}.items():
            if sha(ROOT/rel)!=expected:raise RuntimeError('input changed during adoption: '+rel)
        for row in identity['exact_references'].values():
            p=ROOT/row['path']
            if sha(p)!=row['sha256'] or sha(p.parent/'COSTS.json')!=row['costs_sha256']:
                raise RuntimeError('old reference changed during adoption')
    observed=[]
    def budget(remaining_worlds):
        # Conservative sequential projection includes both worlds in the CPU
        # pair and 5 min of analysis/IO; never silently continue over 1 hour.
        per=max([300.,*observed])
        projected=time.time()-args.task_start+remaining_worlds*per+300.
        write(out/f'BUDGET_{len(list(out.glob("BUDGET_*.json"))):02d}.json',
              dict(elapsed_seconds=time.time()-args.task_start,remaining_worlds=remaining_worlds,
                   per_world_projection_seconds=per,projected_total_seconds=projected,limit_seconds=3600))
        if projected>3600:raise TimeoutError('STOP: projected task compute over one hour: %.1fs'%projected)
    def run_world(name,kernel,directory):
        entropy,world=name.rsplit('_',1)
        cmd=[sys.executable,str(ROOT/'tools/c6_option_b_check.py'),'--backend','native','--kernel',kernel,
             '--parallel','--entropy',entropy,'--world',world,'--output',str(directory)]
        log=out/(directory.name+'_'+directory.parent.name+'.raw.log')
        with log.open('x') as stream:
            proc=subprocess.Popen(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        return proc,log
    def finish(proc,directory):
        try:code=proc.wait(timeout=max(.1,deadline-time.time()))
        except BaseException:
            proc.terminate();proc.wait();raise
        if code:raise RuntimeError('world command failed: '+str(directory))
        rec=json.loads((directory/'COSTS.json').read_text())
        if rec['option_b_build']!=identity['builds'][rec['kernel']] or rec['macos_build']!=identity['macos_build']:
            raise RuntimeError('run identity changed')
        if sha(directory/'world.json.gz')!=rec['world_sha256']:raise RuntimeError('world hash changed')
        observed.append(rec['total_seconds']);return rec
    try:
        budget(10)
        os.environ['C6_OPTION_B_KERNEL']='inexact'
        # These are the unchanged registered diagnostic functions, called here
        # only as engineering fixtures, without the blocked development gate.
        from tools.c6_r4_design_gate import reference_battery,equivariance
        st=time.perf_counter()
        with O.backend('native'):
            rb=reference_battery(P.load_settings(),time.perf_counter()+max(.1,deadline-time.time()))
            eq=equivariance(P.load_settings())
        diagnostic=dict(b_reference_equivalence=rb,b_transform_equivariance=eq,
                        macos_build=identity['macos_build'],option_b_build=identity['builds']['inexact'],
                        seconds=time.perf_counter()-st)
        write(out/'DIAGNOSTICS.json',diagnostic)
        if not rb['passed'] or not eq['passed']:raise RuntimeError('registered numeric diagnostics failed')
        results={}
        for index,name in enumerate(REFERENCES):
            budget(10-index);directory=out/'verification'/name;directory.parent.mkdir(exist_ok=True)
            proc,_=run_world(name,'inexact',directory);finish(proc,directory);preserve()
            print('world computed: '+name,flush=True)
            rel,_,_=REFERENCES[name]
            result=A.analyze_paths(name,ROOT/rel,directory/'world.json.gz')
            result.update(macos_build=identity['macos_build'],option_b_build=identity['builds']['inexact'])
            write(directory/'COMPARISON.json',result);results[name]=result
            if not result['contract']['passed']:raise RuntimeError('0032 contract failed: '+name+' '+str(result['contract']['reasons']))
            print('contract passed: '+name,flush=True)
        summary=A.summarize(results);summary['all_contracts_passed']=True
        summary.update(macos_build=identity['macos_build'],option_b_build=identity['builds']['inexact'])
        write(out/'SUMMARY.json',summary)
        # Fresh generation is authorized only after ALL four old-reference
        # contracts and both diagnostics pass. Verify bits against first runs.
        for index,name in enumerate(REFERENCES):
            budget(6-index);directory=out/'references_inexact'/name;directory.parent.mkdir(exist_ok=True)
            proc,_=run_world(name,'inexact',directory);rec=finish(proc,directory);preserve()
            verification=out/'verification'/name/'world.json.gz'
            check=C.compare(C.read(verification),C.read(directory/'world.json.gz'),0.,False)
            check.update(macos_build=identity['macos_build'],option_b_build=identity['builds']['inexact'],
                         reference=str(verification),reference_sha256=sha(verification),
                         generated=str(directory/'world.json.gz'),generated_sha256=rec['world_sha256'])
            write(directory/'BIT_EXACT.json',check)
            if not check['passed']:raise RuntimeError('new inexact reference not reproducible: '+name)
            print('new reference bit-exact: '+name,flush=True)
        budget(2);pair_started=time.time();pa=time.monotonic()
        samples=[];procs={};directories={}
        for kernel in ('exact','inexact'):
            directory=out/'timing'/kernel;directory.parent.mkdir(exist_ok=True)
            proc,_=run_world('smoke_1',kernel,directory);procs[kernel]=proc;directories[kernel]=directory
        try:
            while any(p.poll() is None for p in procs.values()):
                samples.append(dict(epoch=time.time(),load_average=list(os.getloadavg()),
                    running={k:p.poll() is None for k,p in procs.items()}))
                if time.time()>=deadline:raise TimeoutError('one-hour task deadline')
                time.sleep(10)
            costs={k:finish(p,directories[k]) for k,p in procs.items()}
        finally:
            for p in procs.values():
                if p.poll() is None:p.terminate();p.wait()
        preserve()
        comparison=C.compare(C.read(directories['exact']/'world.json.gz'),C.read(directories['inexact']/'world.json.gz'),1e-8,True)
        timing={'kind':'ONE_WORLD_PAIRED_SHARED_LOAD','world':'smoke_1','launch_gap_seconds':
            abs(time.mktime(time.strptime(costs['exact']['start_machine']['utc'],'%Y-%m-%dT%H:%M:%SZ'))-
                time.mktime(time.strptime(costs['inexact']['start_machine']['utc'],'%Y-%m-%dT%H:%M:%SZ'))),
            'cpu_ratio_inexact_over_exact':costs['inexact']['compute_cpu_seconds']/costs['exact']['compute_cpu_seconds'],
            'compute_cpu_seconds':{k:v['compute_cpu_seconds'] for k,v in costs.items()},
            'compute_wall_seconds':{k:v['compute_seconds'] for k,v in costs.items()},
            'load_samples':samples,'awake_seconds':time.monotonic()-pa,'elapsed_seconds':time.time()-pair_started,
            'macos_build':identity['macos_build'],'builds':identity['builds'],'comparison':comparison}
        write(out/'TIMING.json',timing)
        if not comparison['passed']:raise RuntimeError('timing world contract failed')
        write(out/'COMPLETE.json',dict(status='PASS',macos_build=identity['macos_build'],builds=identity['builds'],
            awake_seconds=time.monotonic()-awake,elapsed_seconds=time.time()-started,
            task_elapsed_seconds=time.time()-args.task_start,remaining_budget_seconds=deadline-time.time()))
    except BaseException as error:
        write(out/'STOP.json',dict(status='STOP',reason=str(error),macos_build=identity['macos_build'],
            builds=identity['builds'],awake_seconds=time.monotonic()-awake,elapsed_seconds=time.time()-started))
        raise
    finally:
        raws={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=sha(p))
              for p in out.rglob('world.json.gz')}
        write(out/'RAW_FILES_LOCAL.json',raws)

if __name__=='__main__':main()
