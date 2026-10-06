"""Artifact-only verification and packaging; does not run scientific code."""
import gzip,hashlib,json,subprocess,tarfile
from pathlib import Path
OUT=Path(__file__).resolve().parent;HERE=OUT.parent;ROOT=OUT.parents[4]
MAX=50_000_000
REPORT=HERE/'REV7_FIXTURE_REPORT.md'
ARCHIVE=HERE/'REV7_FIXTURE_EVIDENCE.tar.gz'
MANIFEST=HERE/'REV7_FIXTURE_EVIDENCE_MANIFEST.json'
VERIFICATION=HERE/'REV7_FIXTURE_DELIVERY_VERIFICATION.json'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
def verify():
 r=json.loads((OUT/'RUN_RECEIPT.json').read_text())
 assert r['verdict']=='FIXTURES_FAIL'
 assert r['identity_snapshot']['pin_sha256']=='3b6cf5635a29da1b16969155016655c61c534622129d3fbae30605e19fbbb551'
 assert list(n for n in ('N1','F1','F2','F3','F4','F5','F6','F7','F8','F9') if n in r['results'])==['N1','F1','F2','F3','F4']
 assert r['not_run']==['F5','F6','F7','F8','F9']
 assert {n:v['verdict'] for n,v in r['results'].items()}==dict(N1='PASS',F1='FAIL',F2='PASS',F3='PASS',F4='PASS')
 assert r['stops']==[dict(action='Block F5 and development; report',question='F1_F4_failed',role='implementer')]
 checks=[]
 for n,info in r['traces'].items():
  p=ROOT/info['path'];data=gzip.decompress(p.read_bytes())
  assert p.stat().st_size==info['bytes'] and digest(p)==info['sha256']
  assert len(data)==info['decoded_bytes'] and hashlib.sha256(data).hexdigest()==info['decoded_sha256']
  expected=r['results']['F1']['configurations']['F1d'] if n=='F1d' else r['results'][n]
  assert json.loads(data)==expected
  checks.append(dict(fixture=n,status='PASS',sha256=info['sha256'],bytes=info['bytes']))
 for n,c in r['timings'].items():
  assert c==json.loads((OUT/(n+'_TIMING.json')).read_text())
  assert c['awake_seconds']>=0 and c['elapsed_utc_seconds']>=0
 baseline=json.loads((OUT/'OUTSIDE_SCOPE_BASELINE.json').read_text())
 changed=[p for p,h in baseline.items() if not (ROOT/p).is_file() or digest(ROOT/p)!=h]
 assert not changed,changed
 pin=json.loads((HERE/'REV7_SOURCE_IDENTITY.json').read_text())
 assert all(digest(ROOT/p)==h for p,h in pin['sha256'].items())
 assert digest(HERE/'REV7_SOURCE_IDENTITY.json')==r['identity_snapshot']['pin_sha256']
 assert digest(ROOT/'evidence/tactical_composition_demo/growing_shapes_review_claude/REV7_FIXTURE_READINESS.md')==r['identity_snapshot']['review_sha256']
 assert REPORT.read_text().splitlines()[0]==r['verdict']
 return dict(status='PASS',traces=checks,outside_scope_checked=len(baseline),outside_scope_changed=changed,pinned_files_checked=len(pin['sha256']),report_sha256=digest(REPORT),original_receipt_sha256=digest(OUT/'RUN_RECEIPT.json'),original_receipt_bytes=(OUT/'RUN_RECEIPT.json').stat().st_size,development_panels_training='NOT_RUN',verification='artifact hashes, gzip decoded equality to receipt, timings, sequence, stop and unchanged source bytes; no fixture rerun')
def package():
 check=verify()
 paths=[REPORT,HERE/'REV7_FIXTURE_DELIVERY_NOTE.md',HERE/'REV7_FIXTURE_COMMIT_MESSAGE.txt']+[p for p in OUT.iterdir() if p.is_file()]
 entries={};excluded={}
 for p in sorted(set(paths)):
  info=dict(bytes=p.stat().st_size,sha256=digest(p))
  if info['bytes']>=MAX or p.name=='EXECUTION_LOG.txt':excluded[str(p.relative_to(ROOT))]=dict(**info,reason='local-only raw stdout (decision 0031)' if p.name=='EXECUTION_LOG.txt' else 'over 50 MB; local original retained, never staged or packed')
  else:entries[str(p.relative_to(ROOT))]=info
 manifest=dict(kind='REV7_FIXTURE_REPORTS_AND_SMALL_EVIDENCE',provenance='Assisted-by: Codex:GPT-6',execution_pin_sha256='3b6cf5635a29da1b16969155016655c61c534622129d3fbae30605e19fbbb551',verdict='FIXTURES_FAIL',files=entries,excluded_large_files=excluded)
 write(MANIFEST,manifest)
 with tarfile.open(ARCHIVE,'w:gz') as arc:
  for n in entries:arc.add(ROOT/n,arcname=n,recursive=False)
  arc.add(MANIFEST,arcname=str(MANIFEST.relative_to(ROOT)),recursive=False)
 with tarfile.open(ARCHIVE,'r:gz') as arc:
  members=arc.getmembers();assert {m.name for m in members}==set(entries)|{str(MANIFEST.relative_to(ROOT))}
  for m in members:
   assert m.isfile() and m.size<MAX and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
   data=arc.extractfile(m).read()
   if m.name in entries:assert len(data)==entries[m.name]['bytes'] and hashlib.sha256(data).hexdigest()==entries[m.name]['sha256']
  assert json.loads(arc.extractfile(str(MANIFEST.relative_to(ROOT))).read())==manifest
 assert ARCHIVE.stat().st_size<MAX
 check.update(archive=str(ARCHIVE.relative_to(ROOT)),archive_sha256=digest(ARCHIVE),archive_bytes=ARCHIVE.stat().st_size,max_member_bytes=max(m.size for m in members),included_files=len(entries),excluded_large_files=excluded,provenance=manifest['provenance'])
 write(VERIFICATION,check)
 print(json.dumps({k:check[k] for k in ('status','archive_bytes','included_files','max_member_bytes','excluded_large_files')}))
if __name__=='__main__':package()
