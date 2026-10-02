"""One fresh-development R3 qualification, never a final panel or rehearsal.

Runs the ten predeclared worlds once. Streams immutable raw world records and
retains a STOP when controls/numerics/quorum/budget fail. No parameter search.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from geomind import c6_r3_protocol as P  # noqa: E402


def sha256(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dependencies():
    patterns=('geomind/c6_r3_*.py','geomind/run_c6_r3.py','native/c6_r3/*.cpp',
              'tools/c6_r3*.py','tools/build_c6_r3.py','tests/test_c6_r3.py',
              'geomind/c4_model.py','geomind/c4_detect.py','geomind/c4_experiment.py',
              'experiments/c4_manifest.json','experiments/c6_r3_protocol.json',
              'experiments/c6_proposal_r3.md','pyproject.toml','uv.lock')
    return {str(p.relative_to(ROOT)):sha256(p) for pattern in patterns for p in ROOT.glob(pattern) if p.is_file()}


def validate_pin():
    record=json.loads((ROOT/'research/rrg/v0.2.1.import.json').read_text())
    problems=[name for name,h in record['file_sha256'].items() if not (ROOT/'research/rrg/v0.2.1'/name).is_file()
              or sha256(ROOT/'research/rrg/v0.2.1'/name)!=h]
    if record.get('verification_status')!='VERIFIED' or problems:raise ValueError('audited source pin mismatch: '+', '.join(problems))
    return {'release':record['release'],'import_record_sha256':sha256(ROOT/'research/rrg/v0.2.1.import.json'),
            'source_files_verified':len(record['file_sha256']),'verdict':'PASS'}


def jsonable(value):
    import numpy as np
    if isinstance(value,dict):return {str(k):jsonable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [jsonable(v) for v in value]
    if isinstance(value,np.ndarray):return jsonable(value.tolist())
    if isinstance(value,np.generic):return jsonable(value.item())
    if isinstance(value,float) and not __import__('math').isfinite(value):raise ValueError('nonfinite development record')
    return value


def write_world(folder,row):
    raw=(json.dumps(jsonable(row),sort_keys=True,allow_nan=False)+'\n').encode()
    path=folder/f"world_{row['world']:03d}.json.gz"
    with path.open('xb') as target:target.write(gzip.compress(raw,mtime=0))
    return {'world':row['world'],'path':path.name,'sha256':sha256(path),
            'uncompressed_sha256':hashlib.sha256(raw).hexdigest(),'seconds':row['seconds']}


def read_worlds(folder,receipt):
    rows=[]
    for entry in receipt['world_artifacts']:
        path=folder/entry['path']
        if sha256(path)!=entry['sha256']:raise ValueError('world artifact hash mismatch')
        raw=gzip.decompress(path.read_bytes())
        if hashlib.sha256(raw).hexdigest()!=entry['uncompressed_sha256']:raise ValueError('raw world hash mismatch')
        rows.append(json.loads(raw))
    return rows


def readiness(records,settings,workers):
    if not records:return {'passed':False,'reason':'no development worlds','panel_seconds':None}
    if len(records)!=settings['development_worlds'] or sorted(row['world'] for row in records)!=list(range(settings['development_worlds'])):
        return {'passed':False,'reason':'incomplete or duplicate development worlds','panel_seconds':None}
    controls=all(c['controls']['sham_preserved'] and not c['controls']['no_r_qualifies'] for row in records for c in row['turns'])
    numerics=all(c['numerics']['passed'] for row in records for c in row['turns'])
    quorum=sum(row['turns'][0]['qualified'] for row in records)
    # Conservative measured worst reached world, including second-turn costs if reached.
    max_seconds=max(row['seconds'] for row in records)
    projected=max_seconds*settings['final_worlds']/workers*1.5
    full_workload_reached=any(len(row['turns'])==2 and row['turns'][1]['episodes'] is not None for row in records)
    reason=('numerical check failed' if not numerics else 'matched causal control failed' if not controls
            else 'source quorum below fixed development target' if quorum<settings['qualification']['development_source_quorum']
            else 'full second-turn workload not reached; panel runtime remains unknown' if not full_workload_reached
            else 'projected panel exceeds approved budget' if projected>settings['qualification']['maximum_panel_seconds'] else None)
    return {'passed':reason is None,'reason':reason,'qualified_sources':quorum,'worlds':len(records),
            'controls_passed':controls,'numerics_passed':numerics,
            'full_workload_reached':full_workload_reached,'panel_seconds':projected if full_workload_reached else None}


def _one(args):return P.run_world(*args)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--workers',type=int,default=8)
    args=parser.parse_args(argv)
    if args.workers<1 or args.workers>8:parser.error('workers must be between one and eight')
    if args.output.exists():raise SystemExit('development evidence exists; never overwrite or repeat a gate')
    if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True).strip():
        raise SystemExit('commit the complete implementation before the long development gate')
    settings=P.load_settings();pin=validate_pin();before=dependencies()
    if len(settings['conditions'])!=3 or tuple(settings['conditions'])!=P.CONDITIONS:raise ValueError('control set mismatch')
    args.output.mkdir(parents=True)
    started=time.perf_counter();rows=[]
    receipt={'kind':'DEVELOPMENT_ONLY','status':'RUNNING','hypothesis_verdicts':'NOT_ASSIGNED',
             'protocol':settings,'file_hashes':before,'source_pin':pin,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             'workers':args.workers,'world_artifacts':[],'stop_rows':[],'errors':[]}
    def save():
        (args.output/'results.json').write_text(json.dumps(jsonable(receipt),indent=2,allow_nan=False)+'\n')
    save()
    try:
        tasks=[(settings,settings['development_entropy'],w) for w in range(settings['development_worlds'])]
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures={pool.submit(_one,task):task[-1] for task in tasks}
            for f in as_completed(futures):
                row=f.result();rows.append(row);receipt['world_artifacts'].append(write_world(args.output,row));save()
                print(f"world {row['world']}: source={row['turns'][0]['qualified']}, turns={len(row['turns'])}, {row['seconds']:.1f}s",flush=True)
        rows.sort(key=lambda row:row['world'])
        ready=readiness(rows,settings,args.workers)
        if dependencies()!=before:raise ValueError('implementation changed during development; receipt invalid')
        if validate_pin()!=pin:raise ValueError('source pin changed during development; receipt invalid')
        receipt.update(status='PASS' if ready['passed'] else 'STOP',readiness=ready,
                       seconds=time.perf_counter()-started,
                       stop_rows=[{'condition':'development controls/numerics/quorum/runtime fail?',
                                   'answer':not ready['passed'],'action':'Return STOP to owner' if not ready['passed'] else 'Proceed to registration',
                                   'responsible':'implementer'}])
    except Exception as exc:
        receipt.update(status='INFRASTRUCTURE_FAILURE',seconds=time.perf_counter()-started)
        receipt['errors'].append({'type':type(exc).__name__,'message':str(exc)})
    save()
    from tools import build_c6_r3
    (args.output/'NATIVE_BUILD.json').write_bytes((build_c6_r3.LIBRARY.parent/'BUILD.json').read_bytes())
    (args.output/'README.md').write_text('# C6 R3 development qualification\n\nDevelopment-only, fresh fixed entropy. No final seeds, panel or hypothesis verdict.\n\nStatus: '+receipt['status']+'\n')
    print(json.dumps({'status':receipt['status'],'seconds':receipt['seconds'],'readiness':receipt.get('readiness'),'errors':receipt['errors']}),flush=True)
    return 0 if receipt['status']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
