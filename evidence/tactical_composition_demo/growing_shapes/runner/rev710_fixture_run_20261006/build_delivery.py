"""Verify exact persisted results and pack reports/small evidence; no fixture calls."""
import ast,gzip,hashlib,json,tarfile,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4];HERE=OUT.parent
PIN='ebc58aa2fa30509356f97b079cec0f8c089df88047f10f0aad6a9c95cbac0071';LIMIT=50_000_000
sys.path.insert(0,str(ROOT))
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
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_identity import assert_inputs
identity=assert_inputs();assert identity['pin_sha256']==PIN
m=json.loads((OUT/'MEASUREMENT_RECEIPT.json').read_text());assert m['wrapper_sha256']==digest(OUT/'execute_once.py')
test=json.loads((OUT/'WRAPPER_SYNTHETIC_CHECK.json').read_text());assert test['status']=='PASS' and test['wrapper_sha256']==m['wrapper_sha256']
tree=ast.parse((OUT/'execute_once.py').read_text());assert not any(isinstance(n,ast.Attribute) and n.attr in ('settrace','setprofile','f_trace','monitoring') for n in ast.walk(tree))
for r in list(m['artifacts'].values())+[m['harness_receipt']]:
 p=OUT/r['path'];assert digest(p)==r['sha256'] and p.stat().st_size==r['bytes']
with gzip.open(OUT/'HARNESS_RECEIPT.json.gz','rt') as f:receipt=json.load(f)
assert receipt['revision']=='7.10' and receipt['identity_snapshot']['pin_sha256']==PIN
for n,r in receipt['results'].items():
 if n in m['artifacts']:
  with gzip.open(OUT/(n+'.json.gz'),'rt') as f:assert json.load(f)==r
assert (HERE/'REV710_FIXTURE_REPORT.md').read_text().splitlines()[0]==m['verdict']
assert (OUT/'OWNER_RECHECK_DISPOSITION.md').is_file()
baseline=json.loads((OUT/'PRESERVATION_BASELINE.json').read_text());changed=[p for p,h in baseline.items() if not (ROOT/p).is_file() or digest(ROOT/p)!=h]
write(OUT/'FINAL_PRESERVATION.json',dict(protected_count=len(baseline),changed=changed,plan_unchanged='docs/PLAN_CURRENT.md' not in changed))
assert not changed, 'Protected prior evidence/source changed; investigate without overwriting'
paths=[];excluded=[]
for p in sorted(OUT.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts:continue
 if p.stat().st_size>=LIMIT:excluded.append(item(p,'Large trace stays local, excluded from git and bundle'))
 elif p.name.endswith('_LOG.txt') or p.name=='EXECUTION_LOG.txt':excluded.append(item(p,'Raw operational log stays local, excluded from git and bundle'))
 else:paths.append(p)
paths += [HERE/'REV710_FIXTURE_REPORT.md',HERE/'REV710_FIXTURE_DELIVERY_NOTE.md']
selected=[];used=0
for p in sorted(paths,key=lambda p:(p.stat().st_size,str(p))):
 charge=((p.stat().st_size+511)//512)*512+2048
 if used+charge>40_000_000:excluded.append(item(p,'Raw evidence stays local; compact delivery size limit'))
 else:selected.append(p);used+=charge
entries={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=digest(p)) for p in selected}
archive=HERE/'REV710_FIXTURE_EVIDENCE.tar.gz'
with tarfile.open(archive,'x:gz') as bundle:
 for p in selected:assert p.stat().st_size<LIMIT;bundle.add(p,arcname=str(p.relative_to(ROOT)),recursive=False)
assert archive.stat().st_size<LIMIT
with tarfile.open(archive,'r:gz') as bundle:
 assert set(bundle.getnames())==set(entries)
 for member in bundle:
  assert member.isfile() and member.size<LIMIT
  h=hashlib.sha256();stream=bundle.extractfile(member)
  for b in iter(lambda:stream.read(1048576),b''):h.update(b)
  assert h.hexdigest()==entries[member.name]['sha256']
write(HERE/'REV710_FIXTURE_EVIDENCE_MANIFEST.json',dict(files=entries,archive=item(archive),excluded_evidence=excluded,pin_sha256=PIN,provenance='Assisted-by: Codex:GPT-6'))
verification=dict(status='PASS',archive=item(archive),members_verified=len(entries),largest_member_bytes=max(r['bytes'] for r in entries.values()),every_delivered_file_under_50MB=True,excluded_evidence=excluded,scientific_inputs_checked=len(identity['sha256']),fixture_outcome=m['verdict'],not_run=receipt['not_run'],preservation='PASS')
write(OUT/'DELIVERY_VERIFICATION.json',verification)
print(json.dumps({k:v for k,v in verification.items() if k!='excluded_evidence'}))
