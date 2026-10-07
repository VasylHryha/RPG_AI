"""Scoped normal-hook attempt-2 commit/bundle, independently fetch/blob verified."""
import hashlib, json, os, pathlib, subprocess
from s4_v6_attempt2 import V
REPO = V.ROOT.parents[2]
PREFIX = str(V.ROOT.relative_to(REPO)) + '/'
def main():
    checks = V.CHECKS
    if not (checks/'OWNER_RECHECK.md').read_text().startswith(('APPROVE\n','APPROVE_WITH_NOTES\n')):
        raise RuntimeError('final owner recheck disposition required')
    if json.loads((checks/'REPORT_AUDIT.json').read_text())['status'] != 'PASS':
        raise RuntimeError('stored-only audit must pass before delivery')
    if json.loads((checks/'PRESERVATION_AFTER.json').read_text())['status'] != 'PASS':
        raise RuntimeError('preservation must pass')
    base = subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
    names = ['S4_V6_ATTEMPT2_SEEDS.json','s4_v6_attempt2.py','s4_v6_attempt2_supervisor.py',
             's4_v6_attempt2_report.py','s4_v6_attempt2_delivery.py','S4_V6_DEVELOPMENT_REPORT_ATTEMPT2.md']
    names += ['s4_v6_attempt2_checks/'+n for n in (
        'CACHE_SMOKE.json','CACHE_SMOKE_RECIPE.md','PART1_DELIVERY.json','PRESERVATION_BEFORE.json',
        'PRESERVATION_AFTER.json','GIT_WRITABILITY.json','LAUNCH.json','LEDGER_USED.json',
        'SUPERVISOR_TIMING.json','LOAD_SUMMARY.json','REPORT_AUDIT.json','REPORT_IDENTITY.json',
        'RAW_FILES_LOCAL.json','CLAUDE_REVIEW_AVAILABILITY.json','OWNER_RECHECK.md','DELIVERY_NOTE.md',
        'SYNTAX_CHECK.json','SYNTAX_ATTEMPT_FAILURE.json')]
    for p in checks.glob('REVIEW_STORED_*'):
        if p.is_file() and p.suffix in ('.py','.json'):
            names.append(str(p.relative_to(V.ROOT)))
    out = pathlib.Path(json.loads((checks/'LAUNCH.json').read_text())['output'])
    names += [str(out.relative_to(V.ROOT))+'/'+n for n in (
        'summary.json','RUN_TIMING.json','run_identity.json','A_best.json','B_best.json','selected_omega.json')]
    names = [PREFIX+n for n in names]
    expected = {n:(REPO/n).read_bytes() for n in names}
    if any(len(v)>=45_000_000 for v in expected.values()): raise RuntimeError('oversize committed payload')
    preserved = json.loads((checks/'PRESERVATION_BEFORE.json').read_text())
    if any(hashlib.sha256((REPO/n).read_bytes()).hexdigest()!=h for n,h in preserved.items()):
        raise RuntimeError('preserved evidence/control changed before commit')
    gitdir = V.ROOT/'build/s4_v6_attempt2_delivery.git'
    bundle = V.ROOT/'S4_V6_ATTEMPT2.bundle'
    fresh = V.ROOT/'build/s4_v6_attempt2_fresh_fetch'
    if any(p.exists() for p in (gitdir,bundle,fresh)): raise RuntimeError('preserve existing delivery')
    writable = json.loads((checks/'GIT_WRITABILITY.json').read_text())['writable']
    if writable:
        env = dict(os.environ)
        if subprocess.check_output(['git','diff','--cached','--name-only'],cwd=REPO,text=True).strip():
            raise RuntimeError('unowned staged work exists; preserve it')
    else:
        subprocess.run(['git','clone','--bare','--shared',str(REPO),str(gitdir)],check=True,capture_output=True)
        env = dict(os.environ,GIT_DIR=str(gitdir),GIT_WORK_TREE=str(REPO),GIT_INDEX_FILE=str(gitdir/'task.index'))
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=REPO,env=env,text=True).strip()
    if not writable:
        branch = 'refs/heads/v6-attempt2'
        git('config','core.hooksPath',str(REPO/'.githooks'))
        git('symbolic-ref','HEAD',branch);git('update-ref',branch,base);git('read-tree',base)
    else:
        branch = git('symbolic-ref','HEAD')
        # Ensure the repository's actual guardrail hooks run on a writable main clone.
        git('config','core.hooksPath',str(REPO/'.githooks'))
    git('add','--',*names)
    if set(git('diff','--cached','--name-only').splitlines())!=set(names): raise RuntimeError('scope mismatch')
    git('diff','--cached','--check')
    commit = subprocess.run(['git','commit','-m',
        'Run and review fresh 0g v6 A/B development attempt 2\n\nAssisted-by: Codex:GPT-6'],
        cwd=REPO,env=env,text=True,capture_output=True)
    (checks/'COMMIT.log').write_text(commit.stdout+commit.stderr)
    if commit.returncode: raise RuntimeError('normal hooks failed: '+commit.stdout+commit.stderr)
    head = git('rev-parse','HEAD')
    if set(git('diff-tree','--no-commit-id','--name-only','-r',head).splitlines())!=set(names):
        raise RuntimeError('committed scope mismatch')
    git('bundle','create',str(bundle),base+'..'+branch)
    verified = subprocess.run(['git','bundle','verify',str(bundle)],cwd=REPO,env=env,text=True,capture_output=True)
    (checks/'BUNDLE_VERIFY.log').write_text(verified.stdout+verified.stderr)
    if verified.returncode: raise RuntimeError('bundle verify failed')
    subprocess.run(['git','clone','--shared','--no-checkout',str(REPO),str(fresh)],check=True,capture_output=True)
    subprocess.run(['git','fetch',str(bundle),branch],cwd=fresh,check=True,capture_output=True)
    actual = subprocess.check_output(['git','rev-parse','FETCH_HEAD'],cwd=fresh,text=True).strip()
    if actual!=head: raise RuntimeError('independent fetch identity mismatch')
    for n,data in expected.items():
        if subprocess.check_output(['git','show',head+':'+n],cwd=fresh)!=data:
            raise RuntimeError('independent fetched blob mismatch: '+n)
    V.write(checks/'DELIVERY_TRANSPORT.json',dict(base=base,commit=head,bundle=str(bundle),
        bundle_sha256=V.sha(bundle),bundle_bytes=bundle.stat().st_size,normal_hooks_returncode=0,
        independent_fetch_verified=True,all_committed_blobs_verified=True,main_git_modified=writable,
        provenance='Assisted-by: Codex:GPT-6',committed_file_hashes={n:hashlib.sha256(v).hexdigest() for n,v in expected.items()},
        commit_hook_log_sha256=V.sha(checks/'COMMIT.log'),bundle_verify_log_sha256=V.sha(checks/'BUNDLE_VERIFY.log'),
        transport_receipt_sidecar=True))
    print(json.dumps(dict(commit=head,bundle=str(bundle),files=len(names),verified=True)))
if __name__=='__main__': main()
