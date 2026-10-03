"""R4 pipeline runner; final entropy is inaccessible before panel/readiness guards."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import copy
import json
from pathlib import Path
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET
import numpy as np
from geomind import c6_r4_field as F,c6_r4_field_assay as A,c6_r4_field_protocol as P,c6_r4_field_analysis as E
from geomind.c6_r4_integrity import sha256,validate_pin,load_worlds
from tools import milestones
from tools.c6_r3_design_gate import write_world,jsonable
from tools.c6_r4_design_gate import dependencies,readiness
ROOT=P.ROOT;MANIFEST=ROOT/'experiments/c6_manifest.json'

def development_pass(manifest):
    folder=ROOT/manifest['development_gate'];receipt=json.loads((folder/'results.json').read_text())
    if receipt['kind']!='DEVELOPMENT_ONLY' or receipt['status']!='PASS' or receipt['file_hashes']!=dependencies():raise ValueError('missing/stale development PASS')
    rows=load_worlds(folder,receipt,range(10))
    s=P.load_settings();ready=readiness(rows,s,s['budget']['workers'],receipt['seconds'])
    if not ready['passed'] or ready!=receipt['readiness']:raise ValueError('readiness receipt differs from raw worlds')
    if manifest.get('development_results_sha256')!=sha256(folder/'results.json'):raise ValueError('final registration lacks bound development receipt')
    if not all(v['passed'] for v in receipt['engineering'].values()):raise ValueError('unqualified reference/covariance')
    return receipt

def smoke(output):
    s=P.load_settings();o=F.population(np.random.default_rng(s['smoke_entropy']),F.medium(np.random.default_rng(s['smoke_entropy']+1),s['model']),0,0)
    checks=[];grid=A.GridSet([o]*3,s,checks);grid.run(.2,'smoke',.1)
    value={'status':'PASS','kind':'SMOKE_ONLY','full_settings_qualified':False,'source_pin':validate_pin(ROOT),'checks':checks,
           'end_identities':grid.identities(),'native_build':F.native()[1]}
    if output.exists():raise FileExistsError('smoke artifact exists')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(value,indent=2)+'\n');return 0

def one(args):return P.run_world(*args)

def panel(output,contract_report):
    problems=milestones.check('c6','panel')
    if problems:raise RuntimeError('Gate blocked R4 panel: '+' '.join(problems))
    manifest=json.loads(MANIFEST.read_text())
    if set(manifest['endpoints'])!=set(E.ENDPOINTS) or manifest['status']!='REGISTERED_FINAL':raise ValueError('final registration incomplete')
    development=development_pass(manifest);s=P.load_settings()
    if manifest['protocol_sha256']!=sha256(P.PROTOCOL) or type(manifest['final_entropy']) is not int:raise ValueError('protocol/final entropy registration mismatch')
    if manifest['final_entropy'] in (s['development_entropy'],s['smoke_entropy'],s['bootstrap_entropy']):raise ValueError('final entropy reused')
    cases=list(ET.parse(contract_report).getroot().iter('testcase'))
    if not cases or any(list(c.iter('failure')) or list(c.iter('error')) or list(c.iter('skipped')) for c in cases):raise ValueError('complete passing contracts required')
    if output.exists():raise FileExistsError('recorded evidence exists')
    pin=validate_pin(ROOT);F.native();output.mkdir(parents=True);started=time.perf_counter();artifacts=[];records=[]
    bound={str(p.relative_to(ROOT)):sha256(p) for p in milestones.dependency_files('c6')}
    with ProcessPoolExecutor(max_workers=s['budget']['workers']) as pool:
        for row in pool.map(one,[(s,manifest['final_entropy'],w) for w in range(s['final_worlds'])]):
            records.append(row);artifacts.append(write_world(output,row))
    engineering=copy.deepcopy(development['engineering']);engineering['source_pin']={**pin,'passed':True}
    analysis=E.evaluate(records,s,s['bootstrap_entropy'],engineering)
    analysis['gates']['source_unchanged']=bound=={str(p.relative_to(ROOT)):sha256(p) for p in milestones.dependency_files('c6')} and validate_pin(ROOT)==pin
    analysis['gates']['endpoint_coverage']=not milestones.endpoint_coverage_problems(manifest,analysis)
    receipt={'kind':'RECORDED_PANEL','complete':True,'check_status':'PASS' if all(analysis['gates'].values()) else 'FAIL',
             'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'manifest':manifest,
             'file_hashes':bound,'world_artifacts':artifacts,'seconds':time.perf_counter()-started,**analysis,
             'limitations':['Conditional retained-environment apparatus','Arm A NOT_RUN','No population, indefinite recursion, AI or efficiency claim','Finite-grid and bootstrap approximations']}
    (output/'results.json').write_text(json.dumps(jsonable(receipt),indent=2,allow_nan=False)+'\n')
    shutil.copyfile(contract_report,output/'contracts.xml')
    for name in bound:
        target=output/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
    return 0 if receipt['check_status']=='PASS' else 1

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--smoke',action='store_true');parser.add_argument('--contract-report',type=Path)
    args=parser.parse_args(argv)
    if args.smoke:return smoke(args.output)
    if args.contract_report is None:parser.error('panel requires contract report')
    return panel(args.output,args.contract_report)
if __name__=='__main__':raise SystemExit(main())
