"""Verify recorded identity/preservation and package reports and small evidence; no run."""
import hashlib,json,subprocess,tarfile
from pathlib import Path
OUT=Path(__file__).resolve().parent;HERE=OUT.parent;ROOT=OUT.parents[4]
MAX=50_000_000
ARCHIVE=HERE/'REV74_FIXTURE_EVIDENCE.tar.gz';MANIFEST=HERE/'REV74_FIXTURE_EVIDENCE_MANIFEST.json';VERIFICATION=HERE/'REV74_FIXTURE_DELIVERY_VERIFICATION.json'
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while data:=f.read(1024*1024):h.update(data)
    return h.hexdigest()
def write(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n')
def package():
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_identity import assert_inputs
    identity=assert_inputs();expected='f370c3b5ea17cf0b3c751de794de0c8ab1dffdb35cbffdc35d81f9b8280c3ce5'
    assert identity['pin_sha256']==expected
    baseline=json.loads((OUT/'OUTSIDE_SCOPE_BASELINE.json').read_text())
    changed=[n for n,h in baseline.items() if not (ROOT/n).is_file() or digest(ROOT/n)!=h]
    assert not changed,changed
    receipt=json.loads((OUT/'RUN_RECEIPT.json').read_text())
    assert receipt['revision']=='7.4' and receipt['identity_snapshot']['pin_sha256']==expected
    assert receipt['verdict']=='FIXTURES_FAIL' and set(receipt['results'])=={'N1'}
    assert receipt['results']['N1']['verdict']=='FAIL' and receipt['not_run']==['F1','F2','F3','F4','F5','F6','F7','F8','F9']
    assert [v['question'] for v in receipt['stops']]==['N1_failed_or_invalid']
    assert (HERE/'REV74_FIXTURE_REPORT.md').read_text().splitlines()[0]==receipt['verdict']
    staged=subprocess.check_output(['git','diff','--cached','--binary'],cwd=ROOT)
    preservation={'status':'PASS','tracked_files_checked':len(baseline),'tracked_changes':changed,'execution_pin_sha256':expected,'plan_unchanged':digest(ROOT/'docs/PLAN_CURRENT.md')==baseline['docs/PLAN_CURRENT.md'],'staged_diff_sha256':hashlib.sha256(staged).hexdigest(),'pre_delivery_staged_unchanged':json.loads((OUT/'PRESERVATION.json').read_text())['staged_diff_unchanged'],'historical_rev73_tracked_unchanged':True}
    write(OUT/'FINAL_PRESERVATION.json',preservation)
    paths=[p for p in OUT.rglob('*') if p.is_file()]
    paths+=[HERE/'REV74_FIXTURE_REPORT.md',HERE/'REV74_FIXTURE_COMMIT_MESSAGE.txt',HERE/'REV74_FIXTURE_DELIVERY_NOTE.md']
    entries={};excluded={}
    for p in sorted(paths):
        assert p.is_relative_to(HERE.parent)
        n=str(p.relative_to(ROOT));v={'bytes':p.stat().st_size,'sha256':digest(p)}
        if v['bytes']>=MAX:excluded[n]=dict(**v,reason='>=50 MB: retained locally; omitted from bundle')
        else:entries[n]=v
    manifest={'kind':'REPORTS_AND_SMALL_FIXTURE_EVIDENCE','revision':'7.4','verdict':receipt['verdict'],'execution_pin_sha256':expected,'files':entries,'excluded_large_files':excluded,'max_file_bytes_exclusive':MAX,'provenance':'Assisted-by: Codex:GPT-6','code_and_native_build_products':'NOT_INCLUDED'}
    write(MANIFEST,manifest)
    with tarfile.open(ARCHIVE,'w:gz') as tar:
        for n in entries:tar.add(ROOT/n,arcname=n,recursive=False)
        tar.add(MANIFEST,arcname=str(MANIFEST.relative_to(ROOT)),recursive=False)
    assert ARCHIVE.stat().st_size<MAX
    with tarfile.open(ARCHIVE,'r:gz') as tar:
        members=tar.getmembers();assert len(members)==len(entries)+1
        assert {m.name for m in members}==set(entries)|{str(MANIFEST.relative_to(ROOT))}
        for m in members:
            assert m.isfile() and m.size<MAX and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
            data=tar.extractfile(m).read()
            if m.name in entries:assert len(data)==entries[m.name]['bytes'] and hashlib.sha256(data).hexdigest()==entries[m.name]['sha256']
        assert json.loads(tar.extractfile(str(MANIFEST.relative_to(ROOT))).read())==manifest
    verification={'status':'PASS','archive':str(ARCHIVE.relative_to(ROOT)),'archive_sha256':digest(ARCHIVE),'archive_bytes':ARCHIVE.stat().st_size,'members_verified':len(members),'max_member_bytes':max(m.size for m in members),'excluded_large_files':excluded,'preservation':preservation,'fixture_execution':'ONCE_COMPLETED_STOPPED_N1','commit_created':False,'git_block':'index.lock Operation not permitted','provenance':'Assisted-by: Codex:GPT-6'}
    write(VERIFICATION,verification);print(json.dumps(verification,indent=2))
if __name__=='__main__':package()
