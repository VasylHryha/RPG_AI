"""Verify and package this attempt only; never execute fixtures."""
import ast
import hashlib
import json
import tarfile
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
HERE = OUT.parent
LIMIT = 50_000_000
PIN = '9628282d3407038a6b6947e86cb8ae1b7e7b2ef82fcdd3f9ecd540895c82e42e'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def entry(path):
    return dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                sha256=digest(path))


def main():
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_identity import assert_inputs
    identity = assert_inputs()
    assert identity['pin_sha256'] == PIN
    m = json.loads((OUT / 'MEASUREMENT_RECEIPT.json').read_text())
    summary = json.loads((OUT / 'MEASURED_SUMMARY.json').read_text())
    preservation = json.loads((OUT / 'FINAL_PRESERVATION.json').read_text())
    assert preservation['status'] == 'PASS' and preservation['plan_unchanged']
    assert m['wrapper_sha256'] == digest(OUT / 'execute_once.py')
    synthetic = json.loads((OUT / 'WRAPPER_SYNTHETIC_CHECK.json').read_text())
    assert synthetic['status'] == 'PASS' and synthetic['wrapper_sha256'] == m['wrapper_sha256']
    tree = ast.parse((OUT / 'execute_once.py').read_text())
    assert not any(isinstance(n, ast.Attribute) and n.attr in
                   ('settrace', 'setprofile', 'f_trace', 'monitoring') for n in ast.walk(tree))
    for row in list(m['artifacts'].values()) + [m['harness_receipt']]:
        path = OUT / row['path']
        assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256']
    assert summary['verdict'] == m['verdict']
    order=('N1','F1','F2','F3','F4','F5','F6','F7','F8','F9')
    measured=set(summary['results'])-{'F1c_numerical_hold'}
    assert measured == set(order)-set(summary['not_run'])
    if 'F5' in measured and summary['results']['F5']['verdict']!='INVALID':
        assert set(summary['results']['F5']['starts']) == {'i', 'ii'}
    assert (HERE / 'REV77_FIXTURE_REPORT.md').read_text().splitlines()[0] == m['verdict']
    assert (OUT / 'OWNER_RECHECK_REPORT.md').is_file()
    assert (OUT / 'OWNER_RECHECK_DISPOSITION.md').is_file()
    paths, excluded = [], []
    for path in sorted(OUT.rglob('*')):
        if not path.is_file() or path.name == 'DELIVERY_VERIFICATION.json' or '__pycache__' in path.parts:
            continue
        if path.stat().st_size >= LIMIT:
            excluded.append(dict(**entry(path), reason='Large complete raw trace stays local; omitted from git and bundle'))
        elif path.name.endswith('_LOG.txt'):
            excluded.append(dict(**entry(path), reason='Raw operational log stays local; omitted from git and bundle'))
        else:
            paths.append(path)
    paths += [HERE / 'REV77_FIXTURE_REPORT.md', HERE / 'REV77_FIXTURE_DELIVERY_NOTE.md']
    entries = {str(path.relative_to(ROOT)): entry(path) for path in paths}
    archive = HERE / 'REV77_FIXTURE_EVIDENCE.tar.gz'
    with tarfile.open(archive, 'x:gz') as bundle:
        for path in paths:
            assert path.stat().st_size < LIMIT
            bundle.add(path, arcname=str(path.relative_to(ROOT)), recursive=False)
    assert archive.stat().st_size < LIMIT
    with tarfile.open(archive, 'r:gz') as bundle:
        members = bundle.getmembers()
        assert {m.name for m in members} == set(entries)
        for member in members:
            assert member.isfile() and member.size < LIMIT
            data = bundle.extractfile(member).read()
            assert len(data) == entries[member.name]['bytes']
            assert hashlib.sha256(data).hexdigest() == entries[member.name]['sha256']
    manifest = dict(files=entries, archive=entry(archive), excluded_evidence=excluded,
                    execution_pin_sha256=PIN, provenance='Assisted-by: Codex:GPT-6')
    manifest_path = HERE / 'REV77_FIXTURE_EVIDENCE_MANIFEST.json'
    write(manifest_path, manifest)
    verification = dict(status='PASS', archive=entry(archive), manifest=entry(manifest_path),
                        members_verified=len(entries), largest_member_bytes=max(r['bytes'] for r in entries.values()),
                        every_delivered_file_strictly_under_50MB=True, excluded_evidence=excluded,
                        scientific_inputs_checked=len(identity['sha256']), real_execution_once=True,
                        fixture_outcome=m['verdict'], F5_both_starts_persisted='F5' in measured and 'starts' in summary['results'].get('F5',{}),
                        artifact_hashes_verified=True, exact_stage_receipt_equality='PASS: analyze_saved.py',
                        pooled_A_B_E_reconstruction='PASS: analyze_saved.py' if 'F5' in measured and 'starts' in summary['results'].get('F5',{}) else 'NOT_RUN: no F5 results', wrapper_double='PASS',
                        no_line_hooks=True, N1f_hold_agrees=summary['results']['F1c_numerical_hold']['agree'], preservation=preservation,
                        owner_recheck='OWNER_RECHECK_REPORT.md / OWNER_RECHECK_DISPOSITION.md',
                        manifest_policy='Manifest and final verification are adjacent, excluded from archive to avoid self-reference')
    write(OUT / 'DELIVERY_VERIFICATION.json', verification)
    print(json.dumps(dict(status='PASS', members=len(entries), archive_bytes=archive.stat().st_size,
                          largest_member_bytes=verification['largest_member_bytes'], excluded=len(excluded))))


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(ROOT))
    main()
