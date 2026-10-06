"""Verify tested revision 7.11 bytes and a source-only overlay; no engine runs."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

HERE=Path(__file__).resolve().parent
RUNNER=HERE.parent
BASE=RUNNER.parent
ROOT=RUNNER.parents[3]
REVIEW='docs/reviews/tactical_0h_rev711_design_review_codex_r2.md'
SCOPE='evidence/tactical_composition_demo/growing_shapes/'
LIMIT=50_000_000
ARCHIVE=RUNNER/'REV711_SOURCE_ONLY.tar.gz'
MANIFEST=RUNNER/'REV711_SOURCE_ONLY_MANIFEST.json'
FORBIDDEN={'.dylib','.so','.dll','.o','.obj','.a','.lib','.pyc'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')

def preserve():
    baseline=json.loads((HERE/'PRESERVATION_BASELINE.json').read_text())
    mutable={SCOPE+n for n in (
        'medium/rev7_design.py','runner/rev7_config.py','runner/rev7_identity.py',
        'runner/rev7_verify.py','runner/rev7_reporting.py','runner/test_rev7.py',
        'runner/REV7_SOURCE_IDENTITY.json','runner/REV7_SYNTHETIC_CHECKS.json',
        'runner/REV7_SYNTHETIC_TEST_LOG.txt','runner/REV7_INTEGRATION_REPORT.md')}
    for name,digest in baseline['preserved_sha256'].items():
        if name not in mutable:assert sha(ROOT/name)==digest,name
    staged=hashlib.sha256(subprocess.check_output(['git','diff','--cached','--binary'],cwd=ROOT)).hexdigest()
    assert staged==baseline['staged_sha256'],'staging changed'
    prior=set(line[3:] for line in baseline['status'].splitlines())
    current=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
    added=[line[3:] for line in current.splitlines() if line[3:] not in prior]
    assert all(n.startswith(SCOPE) or n==REVIEW for n in added),added
    return dict(status='PASS',preserved_files=len(baseline['preserved_sha256'])-len(mutable),
                staging_unchanged=True,design_PLAN_AGENTS_and_historical_evidence_unchanged=True,
                observed_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())

def inputs():
    pin=json.loads((RUNNER/'REV7_SOURCE_IDENTITY.json').read_text())
    assert pin['configuration']['revision']=='7.11'
    raw=json.dumps(pin['configuration'],sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    assert hashlib.sha256(raw).hexdigest()==pin['configuration_sha256']
    assert REVIEW in pin['sha256']
    for n,d in pin['sha256'].items():assert sha(ROOT/n)==d,n
    checks=json.loads((RUNNER/'REV7_SYNTHETIC_CHECKS.json').read_text())
    assert checks['status']=='PASS' and checks['exit_code']==0
    assert checks['execution_pin_sha256']==sha(RUNNER/'REV7_SOURCE_IDENTITY.json')
    assert checks['scientific_input_sha256']==pin['sha256']
    assert checks['test_log_sha256']==sha(RUNNER/'REV7_SYNTHETIC_TEST_LOG.txt')
    assert checks['fixture_execution']==checks['training_development_panels']=='NOT_RUN'
    assert (RUNNER/'REV7_INTEGRATION_REPORT.md').read_text().splitlines()[0]=='READY_FOR_REVIEW'
    return pin

def build():
    pin=inputs();preservation=preserve()
    save(HERE/'PRESERVATION_CHECK.json',preservation)
    paths=set(BASE.glob('medium/rev7_*.*'))|{BASE/'medium/build_rev7.py'}|set(RUNNER.glob('rev7_*.py'))
    paths|={ROOT/REVIEW}
    paths|={RUNNER/n for n in ('test_rev7.py','REV7_SOURCE_IDENTITY.json','REV7_SEED_INVENTORY.json',
                              'REV7_SYNTHETIC_CHECKS.json','REV7_SYNTHETIC_TEST_LOG.txt','REV7_INTEGRATION_REPORT.md')}
    paths|={p for p in HERE.iterdir() if p.is_file() and p.name!='DELIVERY_VERIFICATION.json'}
    for p in paths:
        assert p.suffix not in FORBIDDEN and not p.name.endswith('.tar.gz')
        assert p.stat().st_size<LIMIT
    manifest=dict(kind='SOURCE_ONLY_OVERLAY',revision='7.11',base_head=preservation['observed_head'],
        execution_pin_sha256=sha(RUNNER/'REV7_SOURCE_IDENTITY.json'),
        files={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(paths)},
        native_products='EXCLUDED',dependencies='base checkout inherited rev6/world sources, calibration, native images; rebuild if needed and regenerate configuration/source identity LAST before separate review',
        provenance='Assisted-by: Codex:GPT-6')
    save(MANIFEST,manifest)
    with tarfile.open(ARCHIVE,'w:gz') as a:
        for p in sorted(paths|{MANIFEST}):a.add(p,arcname=str(p.relative_to(ROOT)),recursive=False)
    return verify()

def verify():
    pin=inputs();preservation=preserve();manifest=json.loads(MANIFEST.read_text())
    expected=manifest['files'];packed_manifest=str(MANIFEST.relative_to(ROOT))
    assert ARCHIVE.stat().st_size<LIMIT
    with tarfile.open(ARCHIVE,'r:gz') as a:
        members=a.getmembers()
        assert len(members)==len(expected)+1 and {m.name for m in members}==set(expected)|{packed_manifest}
        for m in members:
            p=Path(m.name)
            assert m.isfile() and m.size<LIMIT and not p.is_absolute() and '..' not in p.parts
            assert p.suffix not in FORBIDDEN
            data=a.extractfile(m).read()
            assert data==(ROOT/m.name).read_bytes(),m.name
            if m.name!=packed_manifest:
                assert len(data)==expected[m.name]['bytes'] and hashlib.sha256(data).hexdigest()==expected[m.name]['sha256']
    result=dict(status='PASS',revision='7.11',archive=str(ARCHIVE.relative_to(ROOT)),
        archive_bytes=ARCHIVE.stat().st_size,archive_sha256=sha(ARCHIVE),source_files=len(expected),
        max_member_bytes=max(m.size for m in members),native_products=0,scientific_inputs_checked=len(pin['sha256']),
        configuration_sha256=pin['configuration_sha256'],execution_pin_sha256=sha(RUNNER/'REV7_SOURCE_IDENTITY.json'),
        preservation=preservation,fixture_training_panel_execution='NOT_RUN',implementation_acceptance='PENDING_CLAUDE_REVIEW')
    save(HERE/'DELIVERY_VERIFICATION.json',result);return result

if __name__=='__main__':
    import sys
    print(json.dumps(build() if '--build' in sys.argv else verify(),indent=2,sort_keys=True))
