"""C2-only prerequisite pipeline: build/preflight -> focused checks -> smoke ->
four focused numerical mutations -> registered panel, once per source identity.
No C0/C1 panel or long C1 mutation suite is run.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools import gate

PYTHON=str(ROOT/'.venv/bin/python')
STAGES=('preflight','tests','smoke','mutation','panel')


def command(args):
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    result=subprocess.run([PYTHON,*args],cwd=ROOT,env=env)
    if result.returncode: raise RuntimeError('Stage command failed; later stages not run')


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--through',choices=STAGES,default='panel'); parser.add_argument('--jobs',type=int,default=4)
    args=parser.parse_args(); args.output=args.output.resolve(); code=gate.fingerprint()
    staging=ROOT/'.gate/c2'/code; staging.mkdir(parents=True,exist_ok=True)
    for stage in STAGES[:STAGES.index(args.through)+1]:
        if stage in gate.verified('c2'): print(stage+' already verified; skipped',flush=True); continue
        reasons=gate.check(stage,milestone='c2')
        if reasons: raise SystemExit('C2 '+stage+' blocked: '+' '.join(reasons))
        t=time.perf_counter(); print('C2 '+stage+' starting',flush=True); artifacts=[]
        if stage=='preflight':
            from geomind.run_c2 import check_c1_acceptance,validate_manifest
            validate_manifest(json.loads((ROOT/'experiments/c2_manifest.json').read_text())); check_c1_acceptance()
            if args.output.exists(): raise FileExistsError('Choose a fresh output directory')
            command(['tools/build_c2.py']); artifacts=[ROOT/'.gate/c2_backend/BUILD.json',ROOT/'.gate/c2_backend/relaxation.dylib']
        elif stage=='tests':
            command(['-m','pytest','-q','-x','-p','no:cacheprovider','tests/test_c2.py','tests/test_gate.py','tests/test_c2_gate.py',f'--junitxml={staging / "contracts.xml"}'])
            artifacts=[staging/'contracts.xml']
        elif stage=='smoke':
            command(['tools/c2_smoke.py',str(staging/'smoke.json')]); artifacts=[staging/'smoke.json']
        elif stage=='mutation':
            command(['tools/c2_mutation_probe.py',str(staging/'mutation.json')]); artifacts=[staging/'mutation.json']
        elif stage=='panel':
            command(['-m','geomind.run_c2','--output',str(args.output),'--contract-report',str(staging/'contracts.xml'),'--jobs',str(args.jobs)])
            shutil.copyfile(staging/'mutation.json',args.output/'MUTATION.json'); artifacts=[args.output/'results.json']
        if gate.fingerprint()!=code: raise RuntimeError('Source changed; refusing stamps')
        gate.record(stage,artifacts,{'seconds':time.perf_counter()-t},code,milestone='c2')
        print('C2 '+stage+' PASS',flush=True)
    if args.through=='panel':
        stamps=json.loads(gate.stamp_path(code,'c2').read_text())
        (args.output/'PIPELINE.json').write_text(json.dumps({'milestone':'c2','fingerprint':code,'stages':[{'stage':s,**stamps[s]} for s in STAGES]},indent=2)+'\n')
    return 0


if __name__=='__main__': raise SystemExit(main())
