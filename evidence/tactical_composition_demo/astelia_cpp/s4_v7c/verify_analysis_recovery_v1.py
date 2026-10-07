"""Read-only supplemental seal and byte/mtime preservation audit; no raw parsing."""
from analysis_recovery_v1 import HERE, read, sha, verify_manifest, spent
import hashlib
import json
import subprocess


def verify():
    manifest = verify_manifest()
    import common
    common.pins()
    baseline = read(HERE / 'RECOVERY_V1_PRESERVATION.json')
    for name, expected in baseline['original_files'].items():
        path = HERE / name
        if not path.is_file() or sha(path) != expected['sha256'] or path.stat().st_size != expected['bytes'] or path.stat().st_mtime_ns != expected['mtime_ns']:
            raise RuntimeError('original artifact changed: ' + name)
    for name, expected in baseline['protected'].items():
        path = common.REPO / name
        if sha(path) != expected['sha256'] or path.stat().st_mtime_ns != expected['mtime_ns']:
            raise RuntimeError('protected document changed: ' + name)
    staged = subprocess.check_output(['git', 'diff', '--cached', '--binary', '--', 'docs/PLAN_CURRENT.md'], cwd=common.REPO)
    if hashlib.sha256(staged).hexdigest() != baseline['plan_staged_diff_sha256']:
        raise RuntimeError('plan staging changed')
    total = spent()
    result = dict(status='PASS',original_artifacts_verified=len(baseline['original_files']),
                  sealed_original_hashes_verified=True,protected_bytes_mtimes_and_plan_staging_unchanged=True,
                  cumulative_seconds=total,cap_seconds=3600,remaining_seconds=max(0,3600-total),
                  executed_fights=0,analysis_started=False,render_started=False,
                  recovery_manifest_sha256=sha(HERE/'ANALYSIS_RECOVERY_V1_MANIFEST.json'))
    print(json.dumps(result,indent=2))
    return result


if __name__ == '__main__':
    verify()
