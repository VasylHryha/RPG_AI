"""Package only this task's reports and small evidence; verify without execution."""
import ast
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
from execute_once import OUT, ROOT, PIN_DIGEST, digest, write


def main():
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_identity import assert_inputs
    identity = assert_inputs()
    assert identity['pin_sha256'] == PIN_DIGEST
    assert json.loads((OUT / 'WRAPPER_SYNTHETIC_CHECK.json').read_text())['status'] == 'PASS'
    for label in ('complete', 'failed_gate'):
        p = OUT / ('synthetic_' + label)
        stage = json.load(gzip.open(p / 'F5.json.gz', 'rt'))
        receipt = json.load(gzip.open(p / 'HARNESS_RECEIPT.json.gz', 'rt'))
        assert stage == receipt['results']['F5'] and set(stage['starts']) == {'i', 'ii'}
        measured = json.loads((p / 'MEASUREMENT_RECEIPT.json').read_text())
        assert measured['wrapper_sha256'] == digest(OUT / 'execute_once.py')
        assert measured['harness_receipt']['sha256'] == digest(p / 'HARNESS_RECEIPT.json.gz')
    tree = ast.parse((OUT / 'execute_once.py').read_text())
    assert not any(isinstance(n, ast.Attribute) and n.attr in ('settrace', 'setprofile', 'f_trace', 'monitoring') for n in ast.walk(tree))
    assert not (OUT / 'PRE_EXECUTION_SEED_INVENTORY.json').exists()
    assert not (OUT / 'START_IDENTITY.json').exists()
    assert not (OUT / 'HARNESS_RECEIPT.json.gz').exists()
    baseline = json.loads((OUT / 'PRESERVATION_BASELINE.json').read_text())
    changes = [dict(path=p, before_sha256=h, after_sha256=digest(ROOT / p) if (ROOT / p).is_file() else None)
               for p, h in baseline['tracked'].items()
               if not (ROOT / p).is_file() or digest(ROOT / p) != h]
    historical_changes = [p for p, h in baseline['previous_attempt'].items()
                          if not (ROOT / p).is_file() or digest(ROOT / p) != h]
    assert not historical_changes
    assert digest(ROOT / 'docs/PLAN_CURRENT.md') == baseline['tracked']['docs/PLAN_CURRENT.md']
    assert all(c['path'].startswith('evidence/tactical_composition_demo/astelia_cpp/') for c in changes)
    preservation = dict(scientific_pin='PASS', previous_attempt='PASS',
                        plan_unchanged=True, historical_attempt_files_checked=len(baseline['previous_attempt']),
                        tracked_files_checked=len(baseline['tracked']),
                        repository_wide_unchanged='FAIL_CONCURRENT_CHANGES' if changes else 'PASS',
                        concurrent_changes=changes,
                        disposition='These outside-scope current changes were observed read-only and left in place; no task command wrote to them.',
                        head_before=baseline['head'],
                        head_at_delivery=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip())
    write(OUT / 'FINAL_PRESERVATION.json', preservation)
    paths = sorted(p for p in OUT.rglob('*') if p.is_file())
    paths += [OUT.parent / 'REV75B_FIXTURE_REPORT.md', OUT.parent / 'REV75B_FIXTURE_DELIVERY_NOTE.md']
    assert all(p.stat().st_size < 50_000_000 for p in paths)
    inventory = {str(p.relative_to(ROOT)): dict(bytes=p.stat().st_size, sha256=digest(p)) for p in paths}
    archive = OUT.parent / 'REV75B_FIXTURE_EVIDENCE.tar.gz'
    with tarfile.open(archive, 'x:gz') as bundle:
        for p in paths:
            bundle.add(p, arcname=str(p.relative_to(ROOT)), recursive=False)
    assert archive.stat().st_size < 50_000_000
    with tarfile.open(archive, 'r:gz') as bundle:
        members = bundle.getmembers()
        assert {m.name for m in members} == set(inventory)
        for member in members:
            assert member.isfile() and member.size < 50_000_000
            data = bundle.extractfile(member).read()
            assert len(data) == inventory[member.name]['bytes']
            assert hashlib.sha256(data).hexdigest() == inventory[member.name]['sha256']
    write(OUT.parent / 'REV75B_FIXTURE_EVIDENCE_MANIFEST.json', dict(files=inventory,
          archive=dict(path=str(archive.relative_to(ROOT)), bytes=archive.stat().st_size,
                       sha256=digest(archive)), excluded_large_traces=[]))
    write(OUT / 'DELIVERY_VERIFICATION.json', dict(status='PASS',
          archive_sha256=digest(archive), archive_bytes=archive.stat().st_size,
          members_verified=len(inventory), largest_member_bytes=max(v['bytes'] for v in inventory.values()),
          every_file_strictly_under_50MB=True, large_traces_generated=False,
          scientific_inputs_checked=len(identity['sha256']),
          synthetic_exact_return_persistence='PASS', no_line_hooks='PASS',
          real_fixture_execution='NOT_RUN', real_execution_inventory_absent=True,
          preservation=preservation,
          self_reference_policy='Manifest and final delivery verification are adjacent to the archive; they are not archive members.'))
    print(json.dumps(dict(status='PASS', members=len(inventory), archive_bytes=archive.stat().st_size,
                         preservation=preservation['repository_wide_unchanged'])))


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(ROOT))
    main()
