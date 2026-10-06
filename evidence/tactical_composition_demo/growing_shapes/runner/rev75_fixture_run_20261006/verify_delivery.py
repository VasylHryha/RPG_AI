"""Create once or verify the report/small-evidence bundle; never execute fixtures."""
import argparse,gzip,hashlib,json,sys,tarfile
from pathlib import Path
OUT=Path(__file__).resolve().parent;HERE=OUT.parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
LIMIT=50_000_000
ARCHIVE=HERE/'REV75_FIXTURE_EVIDENCE.tar.gz';MANIFEST=HERE/'REV75_FIXTURE_EVIDENCE_MANIFEST.json';VERIFICATION=HERE/'REV75_FIXTURE_DELIVERY_VERIFICATION.json'
PIN='7a63d15064df745bfa63071473e02ffcb327901d6210c8310f5b5f8c3a330bce'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
def contracts():
 from evidence.tactical_composition_demo.growing_shapes.runner.rev7_identity import assert_inputs
 identity=assert_inputs();assert identity['pin_sha256']==PIN
 receipt=json.loads((OUT/'OPERATOR_INTERRUPTION_RECEIPT.json').read_text())
 assert receipt['kind']=='OPERATOR_INTERRUPTION_RECEIPT_NOT_HARNESS_RECEIPT' and receipt['verdict']=='INVALID'
 assert receipt['revision']=='7.5' and receipt['process_exit_code']==130 and receipt['execution_once'] is True
 assert receipt['identity_snapshot']['pin_sha256']==PIN
 assert receipt['not_run']==['F6','F7','F8','F9'] and receipt['interrupted_fixture']=='F5' and receipt['F5_result_persisted'] is False
 assert not (OUT/'RUN_RECEIPT.json').exists() and not (OUT/'F5.json.gz').exists()
 assert set(receipt['completed_results'])=={'N1','F1','F2','F3','F4'}
 for n,row in receipt['completed_results'].items():
  p=ROOT/row['path'];assert digest(p)==row['sha256'] and row['verdict']=='PASS'
  value=json.load(gzip.open(p,'rt'));assert value['verdict']=='PASS'
  if n=='N1':assert set(value['cases'])=={'N1a','N1b','N1c','N1d','N1e','N1f','N1g'} and value['cases']['N1g']['used_in_verdict'] is False and value['cases']['N1g']['verdict']=='DESCRIPTIVE'
 report=(HERE/'REV75_FIXTURE_REPORT.md').read_text();assert report.splitlines()[0]=='INVALID'
 summary=json.loads((OUT/'MEASURED_SUMMARY.json').read_text());assert summary['verdict']=='INVALID'
 assert summary['results']['F1c_numerical_hold']['coarse_fine']==[True,True]
 assert summary['results']['F5']['verdict']=='INVALID'
 for row in summary['results']['F5']['starts'].values():
  assert all(row[k] is None for k in ('A','B','E','B_out','B_path','events','qualification_validity','awake_seconds','elapsed_utc_seconds'))
 stops=json.loads((OUT/'STOP_ROW_OUTCOMES.json').read_text());assert [s['question'] for s in stops if s['outcome']=='YES']==['fixture_invalid']
 projection=json.loads((OUT/'A7_DEVELOPMENT_COST_PROJECTION.json').read_text());assert projection['qualified_total_hours'] is None
 baseline=json.loads((OUT/'OUTSIDE_SCOPE_BASELINE.json').read_text())
 historical={n:h for n,h in baseline.items() if n.startswith('evidence/tactical_composition_demo/growing_shapes/')}
 assert all((ROOT/n).is_file() and digest(ROOT/n)==h for n,h in historical.items())
 # Concurrent outside-scope changes are recorded, not restored or certified unchanged.
 observed=json.loads((OUT/'CONCURRENT_STATE_CHANGES.json').read_text());assert observed['task_writes_outside_growing_shapes'] is False
 return receipt,len(identity['sha256']),len(historical)
def create():
 receipt,inputs,historical=contracts()
 assert not ARCHIVE.exists() and not MANIFEST.exists() and not VERIFICATION.exists()
 paths=[p for p in OUT.rglob('*') if p.is_file()]+[HERE/'REV75_FIXTURE_REPORT.md',HERE/'REV75_FIXTURE_COMMIT_MESSAGE.txt',HERE/'REV75_FIXTURE_DELIVERY_NOTE.md']
 included={};excluded={}
 for p in sorted(paths):
  assert p.is_relative_to(HERE.parent)
  n=str(p.relative_to(ROOT));v={'bytes':p.stat().st_size,'sha256':digest(p)}
  if v['bytes']>=LIMIT:excluded[n]=dict(**v,reason='>=50 MB; local trace retained, omitted from delivery')
  elif p.name=='EXECUTION_LOG.txt':excluded[n]=dict(**v,reason='raw execution log retained locally, omitted under decision 0031')
  else:included[n]=v
 manifest={'kind':'REPORTS_AND_SMALL_EVIDENCE','revision':'7.5','verdict':'INVALID','execution_pin_sha256':PIN,'files':included,'excluded_files':excluded,'max_file_bytes_exclusive':LIMIT,'provenance':'Assisted-by: Codex:GPT-6','native_products_and_scientific_code':'NOT_INCLUDED','one_shot_execution':'INTERRUPTED_ON_WRAPPER_MEASUREMENT_DEFECT','harness_receipt':'NOT_RETURNED; operator interruption receipt only'}
 write(MANIFEST,manifest)
 with tarfile.open(ARCHIVE,'x:gz') as tar:
  for n in included:tar.add(ROOT/n,arcname=n,recursive=False)
  tar.add(MANIFEST,arcname=str(MANIFEST.relative_to(ROOT)),recursive=False)
 result=verify();result.update(scientific_inputs_checked=inputs,historical_tracked_growing_shapes_files_checked=historical,commit_created=False,creation_contract_checks='PASS: identity, saved results, INVALID interruption, stops, missing F5 measurements and historical evidence')
 write(VERIFICATION,result);print(json.dumps(result,indent=2))
def verify():
 manifest=json.loads(MANIFEST.read_text());entries=manifest['files'];assert ARCHIVE.stat().st_size<LIMIT
 with tarfile.open(ARCHIVE,'r:gz') as tar:
  members=tar.getmembers();assert {m.name for m in members}==set(entries)|{str(MANIFEST.relative_to(ROOT))}
  assert len(members)==len(entries)+1
  for m in members:
   assert m.isfile() and m.size<LIMIT and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
   assert m.name.startswith('evidence/tactical_composition_demo/growing_shapes/')
   data=tar.extractfile(m).read()
   if m.name in entries:assert len(data)==entries[m.name]['bytes'] and hashlib.sha256(data).hexdigest()==entries[m.name]['sha256']
   else:assert json.loads(data)==manifest
 return {'status':'PASS','scope':'archive member identities, paths and size limits only; not fixture acceptance or live source verification','archive':str(ARCHIVE.relative_to(ROOT)),'archive_bytes':ARCHIVE.stat().st_size,'archive_sha256':digest(ARCHIVE),'manifest_sha256':digest(MANIFEST),'members_verified':len(members),'max_member_bytes':max(m.size for m in members),'excluded_files':manifest['excluded_files'],'verdict':'INVALID','provenance':'Assisted-by: Codex:GPT-6'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--create',action='store_true');args=p.parse_args()
 if args.create:create()
 else:print(json.dumps(verify(),indent=2))
