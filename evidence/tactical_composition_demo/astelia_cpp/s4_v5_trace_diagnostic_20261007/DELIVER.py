"""Normal-hook scoped commit plus independently verified bundle; never writes main .git."""
import hashlib,json,os,pathlib,subprocess
from COMMON import HERE,CPP,REPO,pins,sha,write

def main():
    verdict=(HERE/'OWNER_RECHECK.md').read_text().splitlines()[0].split()[0]
    if verdict not in ('APPROVE','APPROVE_WITH_NOTES'):raise RuntimeError('Dispose review findings first')
    pins()
    report=CPP/'S4_V5_TRACE_DIAGNOSTIC.md';viz=CPP.parent/'viz_0g/v5_trace_diagnostic_20261007'
    # The scope is all compact files created in this task, and only this task.
    files=[report]+[p for p in HERE.iterdir() if p.is_file() and p.name not in ('DELIVERY_TRANSPORT.json',)
                   and p.suffix not in ('.log','.bundle')]+[p for p in viz.iterdir() if p.is_file()]
    names=sorted(str(p.relative_to(REPO)) for p in files)
    expected={n:(REPO/n).read_bytes() for n in names}
    assert all(len(d)<45_000_000 for d in expected.values())
    assert not any('/raw/' in n or '/transport/' in n or n.endswith('.jsonl') or 'PLAN_CURRENT' in n for n in names)
    inventory=json.loads((HERE/'RAW_FILES_OUTSIDE_GIT.json').read_text())
    for f in inventory['files']:
        p=REPO/f['path'];assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],p
    base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
    if any(subprocess.run(['git','cat-file','-e',base+':'+n],cwd=REPO,capture_output=True).returncode==0 for n in names):
        raise RuntimeError('Delivery must contain new files only')
    # Record status externally; the index in the original repo is never touched.
    before=subprocess.check_output(['git','status','--porcelain=v1'],cwd=REPO)
    transport=HERE/'transport'/'final';transport.mkdir()
    gitdir=transport/'task.git';fresh=transport/'fresh_fetch';bundle=transport/'S4_V5_TRACE_DIAGNOSTIC.bundle'
    subprocess.run(['git','clone','--bare','--shared',str(REPO),str(gitdir)],check=True,capture_output=True)
    env=dict(os.environ,GIT_DIR=str(gitdir),GIT_WORK_TREE=str(REPO),GIT_INDEX_FILE=str(gitdir/'task.index'))
    def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,env=env,text=True).strip()
    git('config','core.hooksPath',str(REPO/'.githooks'))
    git('symbolic-ref','HEAD','refs/heads/v5-trace-diagnostic');git('update-ref','refs/heads/v5-trace-diagnostic',base)
    git('read-tree',base);git('add','--',*names)
    assert set(git('diff','--cached','--name-only').splitlines())==set(names)
    git('diff','--cached','--check')
    r=subprocess.run(['git','commit','-m','Diagnose unchanged 0g v5 trajectories on 60 fresh development fights\n\nAssisted-by: Codex:GPT-6'],cwd=REPO,env=env,text=True,capture_output=True)
    log=HERE/'COMMIT_HOOKS.log';log.write_text(r.stdout+r.stderr)
    if r.returncode:raise RuntimeError('Normal hooks rejected commit: '+r.stdout+r.stderr)
    commit=git('rev-parse','HEAD')
    git('bundle','create',str(bundle),base+'..refs/heads/v5-trace-diagnostic')
    git('bundle','verify',str(bundle))
    subprocess.run(['git','clone','--shared','--no-checkout',str(REPO),str(fresh)],check=True,capture_output=True)
    subprocess.run(['git','fetch',str(bundle),'refs/heads/v5-trace-diagnostic'],cwd=fresh,check=True,capture_output=True)
    fetched=subprocess.check_output(['git','rev-parse','FETCH_HEAD'],cwd=fresh,text=True).strip();assert fetched==commit
    changed=subprocess.check_output(['git','diff','--name-only',base,commit],cwd=fresh,text=True).splitlines()
    assert set(changed)==set(names)
    for n,d in expected.items():assert subprocess.check_output(['git','show',commit+':'+n],cwd=fresh)==d,n
    assert bundle.stat().st_size<45_000_000
    # Concurrent owners may have changed their files/HEAD. We make no claim that the whole tree was static.
    pins()
    write(HERE/'DELIVERY_TRANSPORT.json',dict(status='VERIFIED',commit=commit,parent=base,bundle=str(bundle.relative_to(REPO)),
       bundle_sha256=sha(bundle),bundle_bytes=bundle.stat().st_size,normal_hook_returncode=0,commit_hooks_sha256=sha(log),
       provenance='Assisted-by: Codex:GPT-6',independent_fresh_fetch_identity=fetched,independent_all_blobs_verified=True,
       main_git_modified_by_this_delivery=False,plan_in_payload=False,raw_files_in_payload=False,all_payload_files_new=True,
       files={n:dict(bytes=len(d),sha256=hashlib.sha256(d).hexdigest()) for n,d in expected.items()}))
    print(json.dumps(dict(commit=commit,parent=base,bundle=str(bundle),bytes=bundle.stat().st_size,files=len(expected),verified=True)))

if __name__=='__main__':main()
