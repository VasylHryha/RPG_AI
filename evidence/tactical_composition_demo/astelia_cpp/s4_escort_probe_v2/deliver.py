"""Scoped normal-hook commit, or independently fetched/verified bundle.

Never changes the main repository git config, index or refs when unwritable.
The bundle transport receipt is a local sidecar to avoid circular self-hashing.
"""
import hashlib
import json
import os
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
CPP = HERE.parent
REPO = CPP.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    validation = json.loads((HERE / 'VALIDATION.json').read_text())
    assert validation['status'] == 'PASS'
    for name, expected_hash in validation['checked_hashes'].items():
        assert sha(REPO/name)==expected_hash, ('changed after validation',name)
    assert (HERE / 'OWNER_RECHECK.md').read_text().startswith('APPROVE')
    base = subprocess.check_output(['git','rev-parse','HEAD'], cwd=REPO, text=True).strip()
    # The user's if-writable branch is checked by an actual exclusive write.
    marker = REPO / '.git/escort_probe_v2_write_probe'
    writable = False
    error = None
    try:
        with marker.open('x') as f:
            f.write('task scoped writability probe')
        marker.unlink()
        writable = True
    except OSError as e:
        error = str(e)
    (HERE / 'GIT_WRITABILITY.json').write_text(json.dumps(dict(writable=writable, error=error),indent=2)+'\n')
    names = sorted([*validation['checked_hashes'],str((HERE/'VALIDATION.json').relative_to(REPO)),str((HERE/'GIT_WRITABILITY.json').relative_to(REPO))])
    expected = {n:(REPO/n).read_bytes() for n in names}
    assert all(len(v) <= 45_000_000 for v in expected.values())
    env = dict(os.environ)
    branch = None
    bundle = CPP / 's4_escort_probe_v2/S4_ESCORT_PROBE.bundle'
    fresh = HERE / 'delivery/fresh_fetch'
    gitdir = HERE / 'delivery/delivery.git'
    assert not bundle.exists() and not fresh.exists() and not gitdir.exists(), 'refuse delivery overwrite'
    (HERE/'delivery').mkdir(exist_ok=True)
    if not writable:
        subprocess.run(['git','clone','--bare','--shared',str(REPO),str(gitdir)], check=True, capture_output=True)
        env.update(GIT_DIR=str(gitdir), GIT_WORK_TREE=str(REPO), GIT_INDEX_FILE=str(gitdir/'task.index'))
    def git(*args):
        return subprocess.check_output(['git',*args], cwd=REPO, env=env, text=True).strip()
    if not writable:
        branch = 'refs/heads/s4-escort-probe-v2'
        git('symbolic-ref','HEAD',branch)
        git('update-ref',branch,base)
        git('read-tree',base)
        git('config','core.hooksPath',str(REPO / '.githooks'))
    else:
        branch = git('symbolic-ref','HEAD')
        assert git('config','core.hooksPath') == '.githooks', 'expected installed repository hooks'
    staged_before = {n:subprocess.check_output(['git','diff','--cached','--binary','--',n],cwd=REPO,env=env)
                     for n in git('diff','--cached','--name-only').splitlines() if n not in names}
    git('add','--',*names)
    assert set(git('diff','--cached','--name-only','--',*names).splitlines()) == set(names)
    git('diff','--cached','--check','--',*names)
    message = 'Review 19.10 and prepare sealed P12/P14/P15 escort probe v2; combat reserved for Claude\n\nAssisted-by: Codex:GPT-6'
    result = subprocess.run(['git','commit','--only','-m',message,'--',*names],cwd=REPO,env=env,text=True,capture_output=True)
    (HERE / 'COMMIT.log').write_text(result.stdout+result.stderr)
    assert result.returncode == 0, result.stdout+result.stderr
    head = git('rev-parse','HEAD')
    assert set(git('diff-tree','--no-commit-id','--name-only','-r',head).splitlines()) == set(names)
    for n,v in staged_before.items():
        assert subprocess.check_output(['git','diff','--cached','--binary','--',n],cwd=REPO,env=env) == v
    git('bundle','create',str(bundle),base+'..'+branch)
    result = subprocess.run(['git','bundle','verify',str(bundle)],cwd=REPO,env=env,text=True,capture_output=True)
    (HERE / 'BUNDLE_VERIFY.log').write_text(result.stdout+result.stderr)
    assert result.returncode == 0
    # Fetch into a different git object store and verify every committed blob.
    subprocess.run(['git','clone','--shared','--no-checkout',str(REPO),str(fresh)],check=True,capture_output=True)
    subprocess.run(['git','fetch',str(bundle),branch],cwd=fresh,check=True,capture_output=True)
    assert subprocess.check_output(['git','rev-parse','FETCH_HEAD'],cwd=fresh,text=True).strip() == head
    for n,v in expected.items():
        assert subprocess.check_output(['git','show',head+':'+n],cwd=fresh) == v
    assert git('show','-s','--format=%B',head).endswith('Assisted-by: Codex:GPT-6')
    transport = dict(base=base, commit=head, main_git_modified=writable, bundle_sha256=sha(bundle),
                     bundle_bytes=bundle.stat().st_size, normal_hooks_returncode=0,
                     independent_fetch_and_all_blob_hashes_verified=True, explicit_paths=names,
                     committed_file_hashes={n:sha(REPO/n) for n in names})
    (HERE / 'DELIVERY_TRANSPORT.json').write_text(json.dumps(transport,indent=2)+'\n')
    print(json.dumps(dict(commit=head, main_git_modified=writable, bundle=str(bundle), verified=True)))


if __name__ == '__main__':
    main()
