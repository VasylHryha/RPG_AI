"""Read-only verify and deliver new reports/small evidence; never run fixtures."""
import ast,gzip,hashlib,json,tarfile
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4];HERE=OUT.parent
LIMIT=50_000_000
PIN='27a3c46254cbbba16c1eafa48b34379bc40044bcbec08dcebad0cda1ca9d4768'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
def item(p,reason=None):
 v=dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=digest(p))
 if reason:v['reason']=reason
 return v
def main():
 from evidence.tactical_composition_demo.growing_shapes.runner.rev7_identity import assert_inputs
 identity=assert_inputs();assert identity['pin_sha256']==PIN
 m=json.loads((OUT/'MEASUREMENT_RECEIPT.json').read_text())
 assert m['wrapper_sha256']==digest(OUT/'execute_once_now.py')
 synthetic=json.loads((OUT/'WRAPPER_SYNTHETIC_CHECK_NOW.json').read_text())
 assert synthetic['status']=='PASS' and synthetic['wrapper_sha256']==m['wrapper_sha256']
 tree=ast.parse((OUT/'execute_once_now.py').read_text())
 assert not any(isinstance(n,ast.Attribute) and n.attr in ('settrace','setprofile','f_trace','monitoring') for n in ast.walk(tree))
 for row in list(m['artifacts'].values())+[m['harness_receipt']]:
  p=OUT/row['path'];assert p.stat().st_size==row['bytes'] and digest(p)==row['sha256']
 baseline=json.loads((OUT/'PRESERVATION_BASELINE.json').read_text())
 changed=[p for p,h in baseline.items() if not (ROOT/p).is_file() or digest(ROOT/p)!=h]
 write(OUT/'FINAL_PRESERVATION.json',dict(protected_file_count=len(baseline),changed=changed,plan_unchanged='docs/PLAN_CURRENT.md' not in changed,agent_edited_plan=False,external_changes=changed))
 external=json.loads((OUT/'EXTERNAL_PRESERVATION_CHANGES_NOW.json').read_text()) if (OUT/'EXTERNAL_PRESERVATION_CHANGES_NOW.json').exists() else {}
 assert set(changed)<=set(external)
 for path in changed:assert digest(ROOT/path)==external[path]['current_sha256']
 summary=json.loads((OUT/'MEASURED_SUMMARY.json').read_text())
 with gzip.open(OUT/'HARNESS_RECEIPT.json.gz','rt') as stream:receipt=json.load(stream)
 assert receipt['identity_snapshot']['pin_sha256']==PIN and receipt['revision']=='7.9'
 rows=receipt['results']
 expected=('INVALID' if any(r['verdict']=='INVALID' for r in rows.values()) else 'FIXTURES_FAIL' if any(r['verdict']=='FAIL' for r in rows.values()) else 'INVALID' if receipt['not_run'] else 'FIXTURES_PASS')
 assert expected==m['verdict']==summary['verdict']
 assert summary['not_run']==receipt['not_run'] and summary['harness_stops']==receipt['stops']
 for name,row in rows.items():
  assert summary['results'][name]['verdict']==row['verdict']
  if name in m['artifacts']:
   with gzip.open(OUT/(name+'.json.gz'),'rt') as stream:assert json.load(stream)==row
 assert (HERE/'REV79_FIXTURE_REPORT.md').read_text().splitlines()[0]==m['verdict']
 assert (OUT/'OWNER_RECHECK_DISPOSITION.md').is_file()
 excluded=[];paths=[]
 for p in sorted(OUT.rglob('*')):
  if not p.is_file():continue
  if '__pycache__' in p.parts:continue
  if p.stat().st_size>=LIMIT:excluded.append(item(p,'Large trace remains local, omitted from delivery and git'))
  elif p.name.endswith('_LOG.txt'):excluded.append(item(p,'Raw operational log remains local, omitted from delivery and git'))
  else:paths.append(p)
 paths+=[HERE/'REV79_FIXTURE_REPORT.md',HERE/'REV79_FIXTURE_DELIVERY_NOTE.md']
 # Reserve a 40 MB uncompressed compact evidence budget, including tar headers.
 # All omitted returns remain local and hash-listed, including smaller raw traces.
 selected=[];used=0
 for p in sorted(paths,key=lambda p:(p.stat().st_size,str(p))):
  charge=((p.stat().st_size+511)//512)*512+2048
  if used+charge>40_000_000:
   excluded.append(item(p,'Raw trace omitted to keep compact delivery below 50 MB; retained locally'))
  else:selected.append(p);used+=charge
 paths=selected
 entries={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=digest(p)) for p in paths}
 archive=HERE/'REV79_FIXTURE_EVIDENCE.tar.gz'
 with tarfile.open(archive,'x:gz') as bundle:
  for p in paths:
   assert p.stat().st_size<LIMIT
   bundle.add(p,arcname=str(p.relative_to(ROOT)),recursive=False)
 assert archive.stat().st_size<LIMIT
 with tarfile.open(archive,'r:gz') as bundle:
  assert {member.name for member in bundle.getmembers()}==set(entries)
  for member in bundle:
   assert member.isfile() and member.size<LIMIT
   data=bundle.extractfile(member).read();assert len(data)==entries[member.name]['bytes'] and hashlib.sha256(data).hexdigest()==entries[member.name]['sha256']
 write(HERE/'REV79_FIXTURE_EVIDENCE_MANIFEST.json',dict(files=entries,archive=item(archive),excluded_evidence=excluded,pin_sha256=PIN,provenance='Assisted-by: Codex:GPT-6'))
 verification=dict(status='PASS',archive=item(archive),members_verified=len(entries),largest_member_bytes=max(row['bytes'] for row in entries.values()),every_delivered_file_strictly_under_50MB=True,excluded_evidence=excluded,scientific_inputs_checked=len(identity['sha256']),fixture_outcome=m['verdict'],not_run=summary['not_run'],N1f_hold=summary['results']['F1c_numerical_hold'],preservation='PASS',stage_equals_exact_receipt='checked by analyze_saved.py',review='OWNER_RECHECK_REPORT.md and OWNER_RECHECK_DISPOSITION.md')
 write(OUT/'DELIVERY_VERIFICATION.json',verification)
 print(json.dumps(verification))
if __name__=='__main__':
 import sys
 sys.path.insert(0,str(ROOT));main()
