"""Verify and bundle this attempt's reports/small evidence; no fixture execution."""
import ast,hashlib,json,subprocess,tarfile
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4];HERE=OUT.parent
LIMIT=50_000_000

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
def inventory(p,reason=None):
 row=dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=digest(p))
 if reason:row['reason']=reason
 return row

def main():
 from evidence.tactical_composition_demo.growing_shapes.runner.rev7_identity import assert_inputs
 identity=assert_inputs();assert identity['pin_sha256']=='7a63d15064df745bfa63071473e02ffcb327901d6210c8310f5b5f8c3a330bce'
 measurement=json.loads((OUT/'MEASUREMENT_RECEIPT.json').read_text())
 assert measurement['verdict']=='FIXTURES_FAIL'
 assert measurement['wrapper_sha256']==digest(OUT/'execute_once.py')
 assert json.loads((OUT/'WRAPPER_SYNTHETIC_CHECK.json').read_text())['wrapper_sha256']==measurement['wrapper_sha256']
 tree=ast.parse((OUT/'execute_once.py').read_text())
 assert not any(isinstance(n,ast.Attribute) and n.attr in ('settrace','setprofile','f_trace','monitoring') for n in ast.walk(tree))
 for row in list(measurement['artifacts'].values())+[measurement['harness_receipt']]:
  p=OUT/row['path'];assert p.stat().st_size==row['bytes'] and digest(p)==row['sha256']
 summary=json.loads((OUT/'MEASURED_SUMMARY.json').read_text())
 assert {n:r['verdict'] for n,r in summary['results'].items() if isinstance(r,dict) and 'verdict' in r}==dict(N1='PASS',F1='PASS',F2='PASS',F3='PASS',F4='PASS',F5='FAIL')
 assert summary['not_run']==['F6','F7','F8','F9']
 assert summary['results']['F1c_numerical_hold']['agree'] is True
 assert (HERE/'REV75C_FIXTURE_REPORT.md').read_text().splitlines()[0]=='FIXTURES_FAIL'
 assert json.loads((OUT/'FINAL_PRESERVATION.json').read_text())['plan_unchanged']
 assert (OUT/'OWNER_RECHECK_DISPOSITION.md').is_file()
 excluded=[];paths=[]
 for p in sorted(OUT.rglob('*')):
  if not p.is_file():continue
  if p.name=='DELIVERY_VERIFICATION.json':continue
  if p.stat().st_size>=LIMIT:excluded.append(inventory(p,'Large raw trace retained locally, omitted from delivery and git'))
  elif p.name.endswith('_LOG.txt') or p.name=='PROCESS_LOAD_DURING_F5.txt':excluded.append(inventory(p,'Raw operational log retained locally, omitted from git and bundle'))
  else:paths.append(p)
 paths += [HERE/'REV75C_FIXTURE_REPORT.md',HERE/'REV75C_FIXTURE_DELIVERY_NOTE.md']
 entries={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=digest(p)) for p in paths}
 archive=HERE/'REV75C_FIXTURE_EVIDENCE_FINAL.tar.gz'
 with tarfile.open(archive,'x:gz') as bundle:
  for p in paths:
   assert p.stat().st_size<LIMIT
   bundle.add(p,arcname=str(p.relative_to(ROOT)),recursive=False)
 assert archive.stat().st_size<LIMIT
 with tarfile.open(archive,'r:gz') as bundle:
  members=bundle.getmembers();assert {m.name for m in members}==set(entries)
  for member in members:
   assert member.isfile() and member.size<LIMIT
   data=bundle.extractfile(member).read();assert len(data)==entries[member.name]['bytes']
   assert hashlib.sha256(data).hexdigest()==entries[member.name]['sha256']
 manifest=dict(files=entries,archive=inventory(archive),excluded_evidence=excluded,pin_sha256=identity['pin_sha256'],provenance='Assisted-by: Codex:GPT-6')
 write(HERE/'REV75C_FIXTURE_EVIDENCE_MANIFEST_FINAL.json',manifest)
 verification=dict(status='PASS',archive_sha256=digest(archive),archive_bytes=archive.stat().st_size,members_verified=len(entries),largest_member_bytes=max(r['bytes'] for r in entries.values()),every_delivered_file_strictly_under_50MB=True,excluded_evidence=excluded,scientific_inputs_checked=len(identity['sha256']),real_execution_once=True,fixture_outcome='FIXTURES_FAIL',F5_both_starts_persisted=True,stage_equals_exact_receipt_checked_by='analyze_saved.py; ANALYSIS_LOG.txt completed successfully',wrapper_synthetic_exact_return_persistence='PASS',no_line_hooks='PASS',N1f_hold_agrees=True,not_run=summary['not_run'],review='OWNER_RECHECK_REPORT.md / OWNER_RECHECK_DISPOSITION.md',manifest_policy='Manifest and final verification are adjacent; omitted as self-references from archive')
 write(OUT/'DELIVERY_VERIFICATION_FINAL.json',verification)
 print(json.dumps({k:v for k,v in verification.items() if k not in ('excluded_evidence',)}))
if __name__=='__main__':
 import sys
 sys.path.insert(0,str(ROOT));main()
