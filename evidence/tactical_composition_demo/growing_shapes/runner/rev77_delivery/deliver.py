"""Verify and package the 7.7 source overlay; standard libraries only."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

HERE=Path(__file__).resolve().parent
RUNNER=HERE.parent
BASE=RUNNER.parent
ROOT=RUNNER.parents[3]
REVIEW='docs/reviews/tactical_0h_rev77_design_review_codex.md'
SCOPE='evidence/tactical_composition_demo/growing_shapes/'
LIMIT=50_000_000
ARCHIVE=RUNNER/'REV77_SOURCE_ONLY.tar.gz'
MANIFEST=RUNNER/'REV77_SOURCE_ONLY_MANIFEST.json'
FORBIDDEN={'.dylib','.so','.dll','.o','.obj','.a','.lib','.pyc'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')


def preserve():
    baseline=json.loads((HERE/'PRESERVATION_BASELINE.json').read_text())
    # These two runtime files were intentionally added to the scoped batch
    # after initial capture, not excluded retrospectively from the baseline.
    intended={SCOPE+'runner/rev7_verify.py',SCOPE+'runner/rev7_fixtures.py'}
    for name,digest in baseline['preserved_sha256'].items():
        if name not in intended:assert sha(ROOT/name)==digest,name
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==baseline['head']
    assert hashlib.sha256(subprocess.check_output(['git','diff','--cached','--binary'],cwd=ROOT)).hexdigest()==baseline['staged_diff_sha256']
    changes=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
    assert all(name.startswith(SCOPE) or name==REVIEW for name in changes),changes
    result=dict(status='PASS',preserved_tracked_files=len(baseline['preserved_sha256'])-len(intended),
        additional_intended_changes=sorted(intended),head_and_staged_unchanged=True,design_and_PLAN_CURRENT_unchanged=True,
        saved_rev76_and_other_historical_receipts_unchanged=True)
    save(HERE/'PRESERVATION_CHECK.json',result)
    return result


def verify_inputs():
    pin_path=RUNNER/'REV7_SOURCE_IDENTITY.json';pin=json.loads(pin_path.read_text())
    assert pin['configuration']['revision']=='7.7'
    assert hashlib.sha256(json.dumps(pin['configuration'],sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()==pin['configuration_sha256']
    for name,digest in pin['sha256'].items():assert sha(ROOT/name)==digest,name
    assert REVIEW in pin['sha256']
    checks=json.loads((RUNNER/'REV7_SYNTHETIC_CHECKS.json').read_text())
    assert checks['status']=='PASS' and checks['exit_code']==0
    assert checks['execution_pin_sha256']==sha(pin_path)
    assert checks['scientific_input_sha256']==pin['sha256']
    assert checks['test_log_sha256']==sha(RUNNER/'REV7_SYNTHETIC_TEST_LOG.txt')
    assert checks['fixture_execution']==checks['training_development_panels']=='NOT_RUN'
    assert (RUNNER/'REV7_INTEGRATION_REPORT.md').read_text().splitlines()[0]=='READY_FOR_REVIEW'
    return pin,checks


def build():
    preservation=preserve();pin,checks=verify_inputs()
    paths=set(BASE.glob('medium/rev7_*.*'))|{BASE/'medium/build_rev7.py'}|set(RUNNER.glob('rev7_*.py'))
    paths|={RUNNER/name for name in ('test_rev7.py','REV7_SEED_INVENTORY.json','REV7_SOURCE_IDENTITY.json',
             'REV7_SYNTHETIC_CHECKS.json','REV7_SYNTHETIC_TEST_LOG.txt','REV7_INTEGRATION_REPORT.md')}
    paths|={ROOT/REVIEW}
    paths|={p for p in HERE.iterdir() if p.is_file() and p.name!='DELIVERY_VERIFICATION.json'}
    for name in subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines():
        assert name.startswith(SCOPE) or name==REVIEW,name
        paths.add(ROOT/name)
    for path in paths:
        assert path.suffix not in FORBIDDEN and '_rev7_build' not in path.parts
        assert path.stat().st_size<LIMIT and not path.name.endswith('.tar.gz')
    manifest=dict(kind='SOURCE_ONLY_OVERLAY',revision='7.7',base_head=json.loads((HERE/'PRESERVATION_BASELINE.json').read_text())['head'],
        execution_pin_sha256=sha(RUNNER/'REV7_SOURCE_IDENTITY.json'),
        files={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(paths)},
        native_products='EXCLUDED; rebuild from final sources',provenance='Assisted-by: Codex:GPT-6')
    save(MANIFEST,manifest)
    with tarfile.open(ARCHIVE,'w:gz') as archive:
        for path in sorted(paths|{MANIFEST}):archive.add(path,arcname=str(path.relative_to(ROOT)),recursive=False)
    return verify(preservation)


def verify(preservation=None):
    pin,checks=verify_inputs();manifest=json.loads(MANIFEST.read_text());expected=manifest['files']
    packed_manifest=str(MANIFEST.relative_to(ROOT));assert ARCHIVE.stat().st_size<LIMIT
    with tarfile.open(ARCHIVE,'r:gz') as archive:
        members=archive.getmembers()
        assert len(members)==len(expected)+1
        assert {m.name for m in members}==set(expected)|{packed_manifest}
        for member in members:
            path=Path(member.name)
            assert member.isfile() and member.size<LIMIT and not path.is_absolute() and '..' not in path.parts
            assert path.suffix not in FORBIDDEN and '_rev7_build' not in path.parts
            data=archive.extractfile(member).read()
            if member.name==packed_manifest:assert data==MANIFEST.read_bytes()
            else:
                row=expected[member.name]
                assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
                assert sha(ROOT/member.name)==row['sha256'],member.name
    for name in subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines():assert name in expected,name
    assert REVIEW in expected
    assert manifest['execution_pin_sha256']==sha(RUNNER/'REV7_SOURCE_IDENTITY.json')
    result=dict(status='PASS',revision='7.7',archive=str(ARCHIVE.relative_to(ROOT)),archive_bytes=ARCHIVE.stat().st_size,
        archive_sha256=sha(ARCHIVE),source_files=len(expected),max_member_bytes=max(m.size for m in members),native_products=0,
        scientific_inputs_checked=len(pin['sha256']),configuration_sha256=pin['configuration_sha256'],
        execution_pin_sha256=manifest['execution_pin_sha256'],preservation=preservation or preserve(),
        fixture_training_panel_execution='NOT_RUN',implementation_acceptance='PENDING_CLAUDE_REVIEW')
    save(HERE/'DELIVERY_VERIFICATION.json',result)
    return result


if __name__=='__main__':
    import sys
    print(json.dumps(build() if '--build' in sys.argv else verify(),sort_keys=True,indent=2))
