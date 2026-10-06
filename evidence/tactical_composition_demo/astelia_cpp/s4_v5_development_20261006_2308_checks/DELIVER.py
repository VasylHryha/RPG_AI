"""Commit this task with normal hooks and independently verify its bundle."""
import hashlib
import json
import os
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
HERE = pathlib.Path(__file__).resolve().parent
OUT = ROOT / 's4_v5_development_20261006_2308'
PREFIX = str(ROOT.relative_to(REPO)) + '/'
CHECKS = str(HERE.relative_to(ROOT)) + '/'
LIMIT = 50_000_000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
    git_dir = ROOT / 'build/s4_v5_development_20261006_2308.git'
    fresh = ROOT / 'build/s4_v5_development_20261006_2308_fetch'
    bundle = ROOT / 'S4_V5_DEVELOPMENT_20261006_2308.bundle'
    if any(p.exists() for p in (git_dir, fresh, bundle)):
        raise RuntimeError('Delivery already exists; preserve it')
    review = (HERE / 'OWNER_RECHECK.md').read_text()
    if not review.startswith('APPROVE_WITH_NOTES\n') and not review.startswith('APPROVE\n'):
        raise RuntimeError('Report review must be disposed before delivery')
    names = [PREFIX + '.gitignore', PREFIX + 'S4_V5_DEVELOPMENT_REPORT.md']
    names += [PREFIX + str(OUT.relative_to(ROOT)) + '/' + n for n in
              ('summary.json', 'RUN_TIMING.json', 'run_identity.json', 'A_best.json',
               'B_best.json', 'selected_omega.json')]
    names += [PREFIX + CHECKS + n for n in
              ('RUN_ONCE.py', 'AUDIT_STORED.py', 'MAKE_REPORT.py', 'DELIVER.py', 'AUDIT.json',
               'RAW_FILES_OUTSIDE_GIT.json', 'LAUNCH.json', 'SUPERVISOR_TIMING.json',
               'LOAD_SUMMARY.json', 'PRESERVED_ATTEMPT.json', 'CLAUDE_REVIEW_ATTEMPT.json',
               'OWNER_RECHECK.md', 'PLAN_AND_REVIEW.md', 'DELIVERY_NOTE.md')]
    expected = {n: (REPO / n).read_bytes() for n in names}
    # Other sessions' dirty plan changes remain live, outside this task's commit.
    live_plan = (REPO / 'docs/PLAN_CURRENT.md').read_text()
    plan = subprocess.check_output(['git', 'show', base + ':docs/PLAN_CURRENT.md'], cwd=REPO, text=True)
    old_row = next(x for x in plan.splitlines() if x.startswith('| B4 |'))
    row = next(x for x in live_plan.splitlines() if x.startswith('| B4 |'))
    disposition = next(x for x in live_plan.splitlines() if x.startswith('**B4 v5 development owner recheck:**'))
    plan = plan.replace(old_row, row)
    if disposition not in plan:
        plan = plan.replace('## Track C:', disposition + '\n\n## Track C:')
    (HERE / 'TASK_PLAN_CURRENT.md').write_text(plan)
    expected['docs/PLAN_CURRENT.md'] = plan.encode()
    for name, data in expected.items():
        if len(data) >= LIMIT:
            raise RuntimeError('Oversize payload: ' + name)
        if name.endswith(('.log', '.jsonl', '.gz')) or 'SEEDS' in name or name.endswith('_validation.json'):
            raise RuntimeError('Raw file in payload: ' + name)
    # Recheck pins without executing a fight or optimizer.
    identity = json.loads((OUT / 'run_identity.json').read_text())
    for name, known in identity['code_hashes'].items():
        if sha((ROOT / name).read_bytes()) != known:
            raise RuntimeError('Runtime identity drift: ' + name)
    raw = json.loads((HERE / 'RAW_FILES_OUTSIDE_GIT.json').read_text())
    for entry in raw['raw_artifacts']:
        path = REPO / entry['path']
        h = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(chunk)
        if path.stat().st_size != entry['bytes'] or h.hexdigest() != entry['sha256']:
            raise RuntimeError('Raw artifact drift: ' + entry['path'])
    subprocess.run(['git', 'clone', '--bare', '--shared', str(REPO), str(git_dir)], check=True, capture_output=True)
    env = dict(os.environ, GIT_DIR=str(git_dir), GIT_WORK_TREE=str(REPO), GIT_INDEX_FILE=str(git_dir / 'task.index'))

    def git(*args, data=None):
        return subprocess.check_output(['git', *args], cwd=REPO, env=env, input=data).decode().strip()

    git('config', 'core.hooksPath', str(REPO / '.githooks'))
    git('symbolic-ref', 'HEAD', 'refs/heads/v5-development')
    git('update-ref', 'refs/heads/v5-development', base)
    git('read-tree', base)
    git('add', '--', *names)
    blob = git('hash-object', '-w', '--stdin', data=expected['docs/PLAN_CURRENT.md'])
    git('update-index', '--add', '--cacheinfo', '100644', blob, 'docs/PLAN_CURRENT.md')
    if set(git('diff', '--cached', '--name-only').splitlines()) != set(expected):
        raise RuntimeError('Staging scope mismatch')
    git('diff', '--cached', '--check')
    committed = subprocess.run(['git', 'commit', '-m',
        'Run 0g v5 A/B development once and report reviewed progress\n\nAssisted-by: Codex:GPT-6'],
        cwd=REPO, env=env, text=True, capture_output=True)
    (HERE / 'COMMIT_HOOKS.log').write_text(committed.stdout + committed.stderr)
    if committed.returncode:
        raise RuntimeError('Normal commit hooks failed: ' + committed.stdout + committed.stderr)
    commit = git('rev-parse', 'HEAD')
    git('bundle', 'create', str(bundle), base + '..refs/heads/v5-development')
    git('bundle', 'verify', str(bundle))
    subprocess.run(['git', 'clone', '--shared', '--no-checkout', str(REPO), str(fresh)], check=True, capture_output=True)
    subprocess.run(['git', 'fetch', str(bundle), 'refs/heads/v5-development'], cwd=fresh, check=True, capture_output=True)
    fetched = subprocess.check_output(['git', 'rev-parse', 'FETCH_HEAD'], cwd=fresh, text=True).strip()
    if fetched != commit:
        raise RuntimeError('Fresh-fetch identity mismatch')
    changed = git('diff', '--name-only', base, commit).splitlines()
    if set(changed) != set(expected):
        raise RuntimeError('Committed scope mismatch')
    for name, data in expected.items():
        actual = subprocess.check_output(['git', 'show', commit + ':' + name], cwd=fresh)
        if actual != data or len(actual) >= LIMIT:
            raise RuntimeError('Independent blob mismatch: ' + name)
    if bundle.stat().st_size >= LIMIT:
        raise RuntimeError('Oversize bundle')
    transport = dict(commit=commit, parent=base, bundle=str(bundle), bundle_sha256=sha(bundle.read_bytes()),
        bundle_bytes=bundle.stat().st_size, independent_fetch_verified=True, hook_returncode=0,
        provenance='Assisted-by: Codex:GPT-6', main_git_modified=False, all_files_under_50_MB=True,
        committed_files={n: dict(sha256=sha(d), bytes=len(d)) for n, d in expected.items()},
        scoped_plan_payload='TASK_PLAN_CURRENT.md', scoped_plan_matches_full_live_plan=plan == live_plan,
        raw_fights_seeds_replays_logs_added=False, runtime_hashes_verified=len(identity['code_hashes']))
    transport['commit_hooks_log_sha256'] = sha((HERE / 'COMMIT_HOOKS.log').read_bytes())
    (HERE / 'DELIVERY_TRANSPORT.json').write_text(json.dumps(transport, indent=2) + '\n')
    print(json.dumps(dict(commit=commit, parent=base, bundle=str(bundle), bundle_bytes=bundle.stat().st_size,
                          verified=True, committed_files=len(expected))))


if __name__ == '__main__':
    main()
