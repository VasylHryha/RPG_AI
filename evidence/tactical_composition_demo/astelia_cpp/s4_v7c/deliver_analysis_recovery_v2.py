"""Explicit new-file delivery with normal hooks, or verified current-HEAD bundle."""
from analysis_recovery_v2 import HERE, read, sha
from verify_analysis_recovery_v2 import verify
import json
import os
from pathlib import Path
import subprocess


def deliver():
    verify()
    if not (HERE/'RECOVERY_V2_OWNER_RECHECK.md').read_text().startswith('APPROVE'):
        raise RuntimeError('recheck not approved')
    repo = HERE.parents[3]
    baseline = read(HERE/'RECOVERY_V2_PRESERVATION.json')
    base = subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    if base != baseline['base_head']:
        raise RuntimeError('HEAD moved since recovery snapshot; inspect before delivery')
    names = [
        'analysis_recovery_v2.py', 'test_analysis_recovery_v2.py',
        'verify_analysis_recovery_v2.py', 'deliver_analysis_recovery_v2.py',
        'ANALYSIS_RECOVERY_V2.md', 'ANALYSIS_RECOVERY_V2_MANIFEST.json',
        'RECOVERY_V2_PRESERVATION.json',
        'RECOVERY_V2_RECHECK_REQUEST.md', 'RECOVERY_V2_OWNER_RECHECK.md',
        'RECOVERY_V2_CLAUDE_RECHECK.stdout.log', 'RECOVERY_V2_CLAUDE_RECHECK.stderr.log',
        'RECOVERY_V2_TESTS.json', 'RECOVERY_V2_TESTS.stdout.log', 'RECOVERY_V2_TESTS.stderr.log',
        'RECOVERY_V2_VERIFICATION.json',
        'RECOVERY_V2_TESTS_BEFORE_CONTINUATION_FIX.json',
        'RECOVERY_V2_TESTS_BEFORE_CONTINUATION_FIX.stdout.log',
        'RECOVERY_V2_TESTS_BEFORE_CONTINUATION_FIX.stderr.log',
        'RECOVERY_V2_TESTS_FAILED_SETUP.json',
        'RECOVERY_V2_TESTS_FAILED_SETUP.stdout.log', 'RECOVERY_V2_TESTS_FAILED_SETUP.stderr.log',
    ]
    if any(n in baseline['original_files'] for n in names):
        raise RuntimeError('delivery would stage an original artifact')
    paths = sorted(str((HERE/n).relative_to(repo)) for n in names)
    expected = {n:(repo/n).read_bytes() for n in paths}
    env = dict(os.environ)
    marker = repo/'.git/recovery_v2_write_probe'
    writable = False
    error = None
    try:
        with marker.open('x') as f:
            f.write('recovery writability probe')
        marker.unlink()
        writable = True
    except OSError as exc:
        error = str(exc)
    workspace = HERE/'delivery/recovery_v2'
    workspace.mkdir(parents=True,exist_ok=False)
    if not writable:
        gitdir = workspace/'delivery.git'
        subprocess.run(['git','clone','--bare','--shared',str(repo),str(gitdir)],check=True,capture_output=True)
        env.update(GIT_DIR=str(gitdir),GIT_WORK_TREE=str(repo),GIT_INDEX_FILE=str(gitdir/'task.index'))
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=repo,env=env,text=True).strip()
    branch = 'refs/heads/s4-v7c-analysis-recovery-v2'
    if not writable:
        git('symbolic-ref','HEAD',branch)
        git('update-ref',branch,base)
        git('read-tree',base)
        git('config','core.hooksPath',str(repo/'.githooks'))
    elif git('config','core.hooksPath') != '.githooks':
        raise RuntimeError('normal repository hooks not configured')
    before = subprocess.check_output(['git','diff','--cached','--binary'],cwd=repo)
    git('add','--',*paths)
    git('diff','--cached','--check','--',*paths)
    message = 'Add v7c boot-bound stored-only night recovery v2\n\nAssisted-by: Codex:GPT-6'
    committed = subprocess.run(['git','commit','--only','-m',message,'--',*paths],cwd=repo,env=env,text=True,capture_output=True)
    (workspace/'COMMIT.log').write_text(committed.stdout+committed.stderr)
    if committed.returncode:
        raise RuntimeError(committed.stdout+committed.stderr)
    head = git('rev-parse','HEAD')
    if set(git('diff-tree','--no-commit-id','--name-only','-r',head).splitlines()) != set(paths):
        raise RuntimeError('commit scope mismatch')
    for name, blob in expected.items():
        if subprocess.check_output(['git','show',head+':'+name],cwd=repo,env=env) != blob:
            raise RuntimeError('committed blob mismatch: '+name)
    # This task begins with no staged changes. Preserve any unrelated staging.
    if subprocess.check_output(['git','diff','--cached','--binary'],cwd=repo) != before:
        raise RuntimeError('main repository staging changed')
    transport = dict(base=base,commit=head,main_git_modified=writable,writability_error=error,
                     explicit_paths=paths,normal_hooks_returncode=0,committed_hashes={n:sha(repo/n) for n in paths})
    if not writable:
        bundle = workspace/'S4_V7C_ANALYSIS_RECOVERY_V2.bundle'
        git('bundle','create',str(bundle),base+'..'+branch)
        checked = subprocess.run(['git','bundle','verify',str(bundle)],cwd=repo,env=env,text=True,capture_output=True)
        (workspace/'BUNDLE_VERIFY.log').write_text(checked.stdout+checked.stderr)
        if checked.returncode:
            raise RuntimeError('bundle verification failed')
        fresh = workspace/'fresh_fetch'
        subprocess.run(['git','clone','--shared','--no-checkout',str(repo),str(fresh)],check=True,capture_output=True)
        subprocess.run(['git','fetch',str(bundle),branch],cwd=fresh,check=True,capture_output=True)
        if subprocess.check_output(['git','rev-parse','FETCH_HEAD'],cwd=fresh,text=True).strip() != head:
            raise RuntimeError('fetch commit mismatch')
        for name, blob in expected.items():
            if subprocess.check_output(['git','show',head+':'+name],cwd=fresh) != blob:
                raise RuntimeError('fetched blob mismatch: '+name)
        transport.update(bundle=str(bundle.relative_to(repo)),bundle_sha256=sha(bundle),
                         independent_fetch_and_all_blobs_verified=True)
    with (HERE/'RECOVERY_V2_DELIVERY_TRANSPORT.json').open('x') as f:
        json.dump(transport,f,indent=2);f.write('\n')
    print(json.dumps(transport,indent=2))


if __name__ == '__main__':
    deliver()
