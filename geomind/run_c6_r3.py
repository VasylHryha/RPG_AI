"""C6 R3 runner. Recorded worlds require the generic pipeline and a qualified gate."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET

from geomind import c6_r3_protocol as P
from tools import milestones
from tools.c6_r3_design_gate import validate_pin,dependencies,write_world,jsonable,sha256

ROOT=P.ROOT
MANIFEST=ROOT/'experiments/c6_manifest.json'


def check_panel():
    problems=milestones.check('c6','panel')
    if problems:raise RuntimeError('Gate blocked R3 panel: '+' '.join(problems))


def development_pass(manifest):
    folder=ROOT/manifest['development_gate']
    receipt=json.loads((folder/'results.json').read_text())
    if receipt['status']!='PASS' or receipt['file_hashes']!=dependencies():
        raise ValueError('R3 development qualification missing or stale')
    from tools.c6_r3_design_gate import read_worlds
    read_worlds(folder,receipt)
    return receipt


def smoke(output):
    s=copy.deepcopy(P.load_settings())
    s['episodes']=1
    s['integration'].update(formation=2.,window=1.,recovery=1.,descriptor=.2,frame_dt=.1)
    s['detector'].update(window=1.,frame_dt=.1,recovery_time=1.)
    s['interventions'].update(gm_window=.2,mg_window=.2)
    row=P.run_world(s,46033009,0)
    gates=all(c['numerics']['passed'] and c['controls']['sham_preserved'] and not c['controls']['no_r_qualifies'] for c in row['turns'])
    pin=validate_pin()
    if output.exists():raise FileExistsError('smoke artifact already exists')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({'status':'PASS' if gates else 'FAIL','kind':'SMOKE_ONLY',
                                 'qualified_settings':False,'source_pin':pin,'record':jsonable(row)},indent=2)+'\n')
    return 0 if gates else 1


def _one(args):return P.run_world(*args)


def panel(output,contract_report):
    check_panel()  # Before reading final entropy, creating output, or constructing any final world.
    manifest=json.loads(MANIFEST.read_text())
    if set(manifest['endpoints'])!=set(P.ENDPOINTS):raise ValueError('registered endpoint set mismatch')
    development_pass(manifest);pin=validate_pin()
    tests=list(ET.parse(contract_report).getroot().iter('testcase'))
    if not tests or any(list(t.iter('failure')) or list(t.iter('error')) or list(t.iter('skipped')) for t in tests):
        raise ValueError('complete passing contract report required')
    if output.exists():raise FileExistsError('recorded evidence exists; never overwrite')
    settings=P.load_settings()
    if manifest['protocol_sha256']!=sha256(P.PROTOCOL):raise ValueError('protocol differs from registration')
    output.mkdir(parents=True);before=dependencies();bound={str(p.relative_to(ROOT)):sha256(p) for p in milestones.dependency_files('c6')};started=time.perf_counter()
    artifacts=[];records=[]
    tasks=[(settings,manifest['final_entropy'],w) for w in range(settings['final_worlds'])]
    with ProcessPoolExecutor(max_workers=manifest['workers']) as pool:
        for row in pool.map(_one,tasks):records.append(row);artifacts.append(write_world(output,row))
    evaluation=P.evaluate(records,settings,manifest['bootstrap_entropy'])
    evaluation['endpoint_coverage']['not_run'].pop('source_pin')
    evaluation['endpoint_coverage']['evaluated']['source_pin']={'value':pin,'verdict':'PASS'}
    gates=evaluation['gates'];gates['source_pin']=pin['verdict']=='PASS';gates['source_unchanged']=dependencies()==before
    coverage=milestones.endpoint_coverage_problems(manifest,evaluation)
    gates['endpoint_coverage']=not coverage
    receipt={'complete':True,'check_status':'PASS' if all(gates.values()) else 'FAIL','manifest':manifest,
        'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'file_hashes':bound,'world_artifacts':artifacts,'gates':gates,
        'endpoint_coverage':evaluation['endpoint_coverage'],'hypotheses':evaluation['hypotheses'],
        'seconds':time.perf_counter()-started,'limitations':['Arm A NOT_RUN: retained R2 STOP','Conditional directed/replay model; no AI or efficiency claim']}
    (output/'results.json').write_text(json.dumps(jsonable(receipt),indent=2,allow_nan=False)+'\n')
    shutil.copyfile(contract_report,output/'contracts.xml')
    source=output/'source'
    for name in bound:
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,path)
    from tools import build_c6_r3
    shutil.copyfile(build_c6_r3.LIBRARY.parent/'BUILD.json',output/'NATIVE_BUILD.json')
    return 0 if receipt['check_status']=='PASS' else 1


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke',action='store_true');parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--contract-report',type=Path)
    args=parser.parse_args(argv)
    if args.smoke:return smoke(args.output)
    if args.contract_report is None:parser.error('panel requires --contract-report')
    return panel(args.output,args.contract_report)


if __name__=='__main__':raise SystemExit(main())
