"""Build/verify the 7.6 source overlay using standard libraries only."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

HERE=Path(__file__).resolve().parent
RUNNER=HERE.parent
BASE=RUNNER.parent
ROOT=RUNNER.parents[3]
SCOPE='evidence/tactical_composition_demo/growing_shapes/'
REVIEW='docs/reviews/tactical_0h_rev76_design_review_codex.md'
MAX_BYTES=50_000_000
MANIFEST=RUNNER/'REV76_SOURCE_ONLY_MANIFEST.json'
ARCHIVE=RUNNER/'REV76_SOURCE_ONLY.tar.gz'
FORBIDDEN={'.dylib','.so','.dll','.o','.obj','.a','.lib','.pyc'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')


def preserve():
    baseline=json.loads((HERE/'PRESERVATION_BASELINE.json').read_text())
    for key in ('outside_sha256','historical_sha256'):
        for name,digest in baseline[key].items():assert sha(ROOT/name)==digest,name
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==baseline['head']
    assert hashlib.sha256(subprocess.check_output(['git','diff','--cached','--binary'],cwd=ROOT)).hexdigest()==baseline['staged_diff_sha256']
    old=RUNNER/'rev75_integration_history'
    # Current copied prior metadata matches the original baseline scientific pin,
    # test receipt and log; remaining historical metadata are carried as delivered.
    receipt=json.loads((old/'REV7_SYNTHETIC_CHECKS.json').read_text())
    assert sha(old/'REV7_SYNTHETIC_TEST_LOG.txt')==receipt['test_log_sha256']
    assert sha(old/'REV7_SOURCE_IDENTITY.json')==receipt['execution_pin_sha256']
    result=dict(status='PASS',outside_tracked_files=len(baseline['outside_sha256']),historical_files=len(baseline['historical_sha256']),head_and_staged_unchanged=True)
    save(HERE/'PRESERVATION_CHECK.json',result)
    return result


def build():
    preservation=preserve()
    pin=json.loads((RUNNER/'REV7_SOURCE_IDENTITY.json').read_text())
    assert pin['configuration']['revision']=='7.6'
    checks=json.loads((RUNNER/'REV7_SYNTHETIC_CHECKS.json').read_text())
    assert checks['status']=='PASS' and checks['exit_code']==0
    paths=set(BASE.glob('medium/rev7_*.*'))|set(BASE.glob('medium/build_rev7.py'))|set(RUNNER.glob('rev7_*.py'))
    paths|={RUNNER/'test_rev7.py',RUNNER/'REV7_SEED_INVENTORY.json',RUNNER/'REV7_SOURCE_IDENTITY.json',RUNNER/'REV7_INTEGRATION_REPORT.md',RUNNER/'REV7_SYNTHETIC_CHECKS.json',RUNNER/'REV7_SYNTHETIC_TEST_LOG.txt',ROOT/REVIEW}
    paths|={p for p in HERE.iterdir() if p.is_file() and p.name!='DELIVERY_VERIFICATION.json'}
    paths|={p for p in (RUNNER/'rev75_integration_history').iterdir() if p.is_file()}
    paths|={p for p in (RUNNER/'rev76_failed_synthetic_attempt').iterdir() if p.is_file()}
    changed=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
    paths|={ROOT/name for name in changed if name.startswith(SCOPE)}
    for path in paths:
        assert path.stat().st_size<MAX_BYTES and path.suffix not in FORBIDDEN
        assert not path.name.endswith('.tar.gz') and '_rev7_build' not in path.parts
    manifest=dict(kind='SOURCE_ONLY',revision='7.6',execution_pin_sha256=sha(RUNNER/'REV7_SOURCE_IDENTITY.json'),files={str(p.relative_to(ROOT)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(paths)})
    save(MANIFEST,manifest)
    with tarfile.open(ARCHIVE,'w:gz') as archive:
        for path in sorted(paths|{MANIFEST}):archive.add(path,arcname=str(path.relative_to(ROOT)),recursive=False)
    return verify(preservation)


def verify(preservation=None):
    manifest=json.loads(MANIFEST.read_text());expected=manifest['files']
    assert ARCHIVE.stat().st_size<MAX_BYTES
    packed_name=str(MANIFEST.relative_to(ROOT))
    with tarfile.open(ARCHIVE,'r:gz') as archive:
        members=archive.getmembers()
        assert len(members)==len(expected)+1
        assert {m.name for m in members}==set(expected)|{packed_name}
        for member in members:
            p=Path(member.name)
            assert member.isfile() and member.size<MAX_BYTES
            assert not p.is_absolute() and '..' not in p.parts and p.suffix not in FORBIDDEN
            assert '_rev7_build' not in p.parts and not member.name.endswith('.tar.gz')
            data=archive.extractfile(member).read()
            if member.name==packed_name:assert data==MANIFEST.read_bytes()
            else:
                row=expected[member.name]
                assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
                assert sha(ROOT/member.name)==row['sha256'],member.name
    assert REVIEW in expected
    for name in subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines():
        if name.startswith(SCOPE):assert name in expected,name
    pin=json.loads((RUNNER/'REV7_SOURCE_IDENTITY.json').read_text())
    for name,digest in pin['sha256'].items():assert sha(ROOT/name)==digest,name
    assert manifest['execution_pin_sha256']==sha(RUNNER/'REV7_SOURCE_IDENTITY.json')
    native_manifest=json.loads((BASE/'medium/_rev7_build/build.json').read_text())
    for name,digest in native_manifest['source_sha256'].items():assert sha(BASE/'medium'/name)==digest,name
    image=BASE/'medium/_rev7_build/rev7_medium.dylib'
    if not image.exists():image=BASE/'medium/_rev7_build/rev7_medium.so'
    assert sha(image)==native_manifest['binary_sha256']
    checks=json.loads((RUNNER/'REV7_SYNTHETIC_CHECKS.json').read_text())
    assert checks['scientific_input_sha256']==pin['sha256']
    assert checks['execution_pin_sha256']==manifest['execution_pin_sha256']
    assert checks['test_log_sha256']==sha(RUNNER/'REV7_SYNTHETIC_TEST_LOG.txt')
    config=json.loads((HERE/'CONFIGURATION.json').read_text())
    assert config['configuration']==pin['configuration'] and config['configuration_sha256']==pin['configuration_sha256']
    assert config['execution_pin_sha256']==manifest['execution_pin_sha256']
    assert (RUNNER/'REV7_INTEGRATION_REPORT.md').read_text().splitlines()[0]=='READY_FOR_REVIEW'
    result=dict(status='PASS',revision='7.6',archive=str(ARCHIVE.relative_to(ROOT)),archive_bytes=ARCHIVE.stat().st_size,archive_sha256=sha(ARCHIVE),source_files=len(expected),max_member_bytes=max(m.size for m in members),native_products=0,scientific_inputs_checked=len(pin['sha256']),configuration_sha256=pin['configuration_sha256'],execution_pin_sha256=manifest['execution_pin_sha256'],preservation=preservation or preserve(),fixture_training_panel_execution='NOT_RUN')
    save(HERE/'DELIVERY_VERIFICATION.json',result)
    return result


if __name__=='__main__':
    import sys
    print(json.dumps(build() if '--build' in sys.argv else verify(),sort_keys=True,indent=2))
