"""Read-only preservation/seal audit; never parses traces or runs fights."""
import hashlib
import json
import subprocess
from analysis_recovery_v2 import HERE, ledger, read, sha, verify_manifest


def verify():
    verify_manifest()
    import common
    common.pins()
    baseline = read(HERE / 'RECOVERY_V2_PRESERVATION.json')
    for name, expected in baseline['original_files'].items():
        path = HERE / name
        stat = path.stat()
        if sha(path) != expected['sha256'] or stat.st_size != expected['bytes'] or stat.st_mtime_ns != expected['mtime_ns']:
            raise RuntimeError('original artifact changed: ' + name)
    for name, expected in baseline['protected'].items():
        path = common.REPO / name
        if sha(path) != expected['sha256'] or path.stat().st_mtime_ns != expected['mtime_ns']:
            raise RuntimeError('protected document changed: ' + name)
    staged = subprocess.check_output(['git', 'diff', '--cached', '--binary'], cwd=common.REPO)
    if hashlib.sha256(staged).hexdigest() != baseline['staged_diff_sha256']:
        raise RuntimeError('unrelated staging changed')
    result = dict(status='PASS', original_artifacts_verified=len(baseline['original_files']),
                  protected_documents_and_staging_unchanged=True, original_seal_verified=True,
                  executed_fights=0, analysis_started=False, render_started=False, **ledger())
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    verify()
