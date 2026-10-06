"""Read-only verification of the 7.5 source overlay; executes no project code."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
RUNNER = HERE.parent
ROOT = RUNNER.parents[3]
MAX_BYTES = 50_000_000
FORBIDDEN = {'.dylib', '.so', '.dll', '.o', '.obj', '.a', '.lib', '.pyc'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    manifest_path = RUNNER / 'REV75_SOURCE_ONLY_MANIFEST.json'
    archive_path = RUNNER / 'REV75_SOURCE_ONLY.tar.gz'
    manifest = json.loads(manifest_path.read_text())
    assert manifest['kind'] == 'SOURCE_ONLY' and manifest['revision'] == '7.5'
    expected = manifest['files']
    packed_name = str(manifest_path.relative_to(ROOT))
    assert archive_path.stat().st_size < MAX_BYTES
    with tarfile.open(archive_path, 'r:gz') as archive:
        members = archive.getmembers()
        assert len(members) == len(expected) + 1
        assert {m.name for m in members} == set(expected) | {packed_name}
        for member in members:
            path = Path(member.name)
            assert member.isfile() and member.size < MAX_BYTES
            assert not path.is_absolute() and '..' not in path.parts
            assert path.suffix not in FORBIDDEN and '_rev7_build' not in path.parts
            assert not member.name.endswith('.tar.gz')
            data = archive.extractfile(member).read()
            if member.name == packed_name:
                assert data == manifest_path.read_bytes()
            else:
                row = expected[member.name]
                assert len(data) == row['bytes']
                assert hashlib.sha256(data).hexdigest() == row['sha256']
                assert sha(ROOT / member.name) == row['sha256']
    review = 'docs/reviews/tactical_0h_rev75_design_review_codex.md'
    assert review in expected
    changed = subprocess.check_output(['git', 'diff', '--name-only'], cwd=ROOT, text=True).splitlines()
    for name in changed:
        if name.startswith('evidence/tactical_composition_demo/growing_shapes/'):
            assert name in expected, f'missing changed file: {name}'
    pin_path = RUNNER / 'REV7_SOURCE_IDENTITY.json'
    pin_digest = sha(pin_path)
    pin = json.loads(pin_path.read_text())
    assert manifest['execution_pin_sha256'] == pin_digest
    assert pin['configuration']['revision'] == '7.5'
    configuration = json.loads((HERE / 'CONFIGURATION.json').read_text())
    assert configuration['configuration'] == pin['configuration']
    assert configuration['configuration_sha256'] == pin['configuration_sha256']
    assert configuration['execution_pin_sha256'] == pin_digest
    for name, digest in pin['sha256'].items():
        assert sha(ROOT / name) == digest, name
    checks = json.loads((RUNNER / 'REV7_SYNTHETIC_CHECKS.json').read_text())
    assert checks['status'] == 'PASS' and checks['exit_code'] == 0
    assert checks['scientific_input_sha256'] == pin['sha256']
    assert checks['execution_pin_sha256'] == pin_digest
    assert checks['test_log_sha256'] == sha(RUNNER / 'REV7_SYNTHETIC_TEST_LOG.txt')
    assert '84 passed' in (RUNNER / 'REV7_SYNTHETIC_TEST_LOG.txt').read_text()
    baseline = json.loads((HERE / 'PRESERVATION_BASELINE.json').read_text())
    for key in ('outside_sha256', 'historical_sha256'):
        for name, digest in baseline[key].items():
            assert sha(ROOT / name) == digest, name
    staged = subprocess.check_output(['git', 'diff', '--cached', '--binary'], cwd=ROOT)
    assert hashlib.sha256(staged).hexdigest() == baseline['staged_diff_sha256']
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == baseline['head']
    assert (RUNNER / 'REV7_INTEGRATION_REPORT.md').read_text().splitlines()[0] == 'READY_FOR_REVIEW'
    return dict(status='PASS', archive=str(archive_path.relative_to(ROOT)),
                archive_bytes=archive_path.stat().st_size, archive_sha256=sha(archive_path),
                source_files=len(expected), max_member_bytes=max(m.size for m in members),
                native_products=0, reviewed_design_sha256=pin['sha256']['evidence/tactical_composition_demo/DESIGN_0H_REV7.md'],
                configuration_sha256=pin['configuration_sha256'], execution_pin_sha256=pin_digest,
                scientific_inputs_checked=len(pin['sha256']), synthetic_tests=84,
                fixture_training_panel_execution='NOT_RUN', preservation='PASS')


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True, indent=2))
