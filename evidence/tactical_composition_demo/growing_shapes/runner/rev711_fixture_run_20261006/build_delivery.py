"""Verify saved data and package compact evidence. No fixture execution."""
import ast,gzip,hashlib,json,os,tarfile,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4];HERE=OUT.parent
PIN='e66c8969d434f475c4289b6d09b048940d148055567c7c1acfc8bd2652fde357';LIMIT=50_000_000
sys.path.insert(0,str(ROOT))
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
def item(p,reason=None):
 row=dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=digest(p))
 if reason:row['reason']=reason
 return row
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_identity import assert_inputs
identity=assert_inputs();assert identity['pin_sha256']==PIN
m=json.loads((OUT/'MEASUREMENT_RECEIPT.json').read_text());assert m['wrapper_sha256']==digest(OUT/'execute_once.py')
test=json.loads((OUT/'WRAPPER_SYNTHETIC_CHECK.json').read_text());assert test['status']=='PASS' and test['wrapper_sha256']==m['wrapper_sha256']
tree=ast.parse((OUT/'execute_once.py').read_text());assert not any(isinstance(n,ast.Attribute) and n.attr in ('settrace','setprofile','f_trace','monitoring') for n in ast.walk(tree))
for r in list(m['artifacts'].values())+[m['harness_receipt']]:
 p=OUT/r['path'];assert digest(p)==r['sha256'] and p.stat().st_size==r['bytes']
with gzip.open(OUT/'HARNESS_RECEIPT.json.gz','rt') as f:receipt=json.load(f)
assert receipt['revision']=='7.11' and receipt['identity_snapshot']['pin_sha256']==PIN
for n,r in receipt['results'].items():
 if n in m['artifacts']:
  with gzip.open(OUT/(n+'.json.gz'),'rt') as f:assert json.load(f)==r
assert (HERE/'REV711_FIXTURE_REPORT.md').read_text().splitlines()[0]==m['verdict']
assert (OUT/'OWNER_RECHECK_DISPOSITION.md').is_file()
baseline=json.loads((OUT/'PRESERVATION_BASELINE.json').read_text());changes=[]
for name,h in baseline.items():
 p=ROOT/name
 if not p.is_file() or digest(p)!=h:changes.append(dict(path=name,before_sha256=h,after_sha256=digest(p) if p.is_file() else None))
scoped=[r for r in changes if r['path'].startswith('evidence/tactical_composition_demo/growing_shapes/')]
assert not scoped,'Prior growing_shapes evidence changed; stop delivery'
write(OUT/'FINAL_PRESERVATION.json',dict(protected_count=len(baseline),prior_growing_shapes_unchanged=True,scientific_inputs_unchanged=True,agent_edited_plan=False,external_changes=changes))
commit_message='Record revision 7.11 fixture measurements and stop outcome\n\nPreserve exact harness returns, machine load, wrapper proof and reviewed report.\n\nAssisted-by: Codex:GPT-6\n'
with (OUT/'COMMIT_MESSAGE.txt').open('x') as f:f.write(commit_message)
write(OUT/'COMMIT_RESULT.json',dict(status='NOT_ATTEMPTED_READ_ONLY_GIT',git_writable=os.access(ROOT/'.git',os.W_OK),reason='Managed filesystem gives read-only .git; owner authorized verified-bundle fallback',provenance='Assisted-by: Codex:GPT-6'))
note=[m['verdict'],'','Revision 7.11 fixtures ran once through unchanged pinned Harness.run_all. See REV711_FIXTURE_REPORT.md for measured gates, stop rows, load and A7 partial cost projection. Pin: '+PIN+'.','', 'Git metadata is read-only in this managed workspace. No commit was attempted; COMMIT_MESSAGE.txt provides the requested Assisted-by trailer. This verified archive is the authorized fallback delivery.','', 'Every archive member and the archive itself is below 50 MB. Raw operational logs and traces too large for the compact bundle stay local and are listed by exact size and SHA256 in REV711_FIXTURE_EVIDENCE_MANIFEST.json. The exact full receipt and per-stage returns remain in rev711_fixture_run_20261006; included where size permits. Hash listings are identity evidence, not substitutes for inspecting omitted traces. No earlier evidence was overwritten.','', 'Rechecks and dispositions are tracked beside this attempt because the owner prohibits edits to docs/PLAN_CURRENT.md. Fixture outcome is separate from scientific acceptance, registration and development authorization. No training, development, panels or judging entropy executed.','', 'Assisted-by: Codex:GPT-6']
with (HERE/'REV711_FIXTURE_DELIVERY_NOTE.md').open('x') as f:f.write('\n'.join(note)+'\n')
paths=[];excluded=[]
for p in sorted(OUT.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts:continue
 if p.stat().st_size>=LIMIT:excluded.append(item(p,'Large evidence stays local; excluded from commit and archive'))
 elif p.name.endswith('_LOG.txt'):excluded.append(item(p,'Raw operational log stays local; excluded from commit and archive'))
 else:paths.append(p)
paths += [HERE/'REV711_FIXTURE_REPORT.md',HERE/'REV711_FIXTURE_DELIVERY_NOTE.md']
selected=[];used=0
for p in sorted(paths,key=lambda p:(p.stat().st_size,str(p))):
 charge=((p.stat().st_size+511)//512)*512+2048
 if used+charge>40_000_000:excluded.append(item(p,'Evidence stays local; compact archive size budget'))
 else:selected.append(p);used+=charge
entries={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=digest(p)) for p in selected}
archive=HERE/'REV711_FIXTURE_EVIDENCE.tar.gz'
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
write(HERE/'REV711_FIXTURE_EVIDENCE_MANIFEST.json',dict(files=entries,archive=item(archive),excluded_evidence=excluded,pin_sha256=PIN,provenance='Assisted-by: Codex:GPT-6'))
verification=dict(status='PASS',archive=item(archive),members_verified=len(entries),largest_member_bytes=max(r['bytes'] for r in entries.values()),every_delivered_file_under_50MB=True,scientific_inputs_checked=len(identity['sha256']),fixture_outcome=m['verdict'],not_run=receipt['not_run'],preservation='Prior growing_shapes and pinned scientific inputs unchanged',excluded_files=len(excluded))
write(OUT/'DELIVERY_VERIFICATION.json',verification)
print(json.dumps(verification))
