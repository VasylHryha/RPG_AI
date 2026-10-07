"""Normal-hook scoped commit, bundle, and independent fetched-blob verification."""
import os,subprocess
from common import *
def main():
 assert_pins()
 assert (HERE/'OWNER_RECHECK.md').read_text().startswith(('APPROVE\n','APPROVE_WITH_NOTES\n'))
 assert json.loads((HERE/'ANALYSIS_VERIFICATION.json').read_text())['status']=='PASS'
 base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
 paths=[CPP/'S4_GUN_ASSAULT_DIAGNOSTIC.md',CPP/'build_observer_v1.py',CPP/'test_observer_v1.py',
        *[p for p in (CPP/'src/native').glob('*observer_v1*')],
        *[p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.md','.json') and p.name not in ('FIGHTS_PARTIAL.json','DELIVERY_TRANSPORT.json')]]
 names=[str(p.relative_to(REPO)) for p in paths];expected={n:(REPO/n).read_bytes() for n in names}
 assert all(len(v)<45_000_000 for v in expected.values())
 marker=REPO/'.git/observer_v1_write_probe';writable=False;error=None
 try:
  with marker.open('x') as f:f.write('task scoped writability check')
  marker.unlink();writable=True
 except OSError as e:error=repr(e)
 write(HERE/'GIT_WRITABILITY.json',dict(writable=writable,error=error))
 # Include the final factual probe, not speculative permission assumptions.
 n=str((HERE/'GIT_WRITABILITY.json').relative_to(REPO));names.append(n) if n not in names else None;expected[n]=(REPO/n).read_bytes()
 gitdir=CPP/'build/observer_v1_delivery.git';bundle=CPP/'S4_GUN_ASSAULT_DIAGNOSTIC.bundle';fresh=CPP/'build/observer_v1_fresh_fetch'
 if any(p.exists() for p in (gitdir,bundle,fresh)):raise RuntimeError('preserve existing delivery')
 if writable:
  env=dict(os.environ)
  if subprocess.check_output(['git','diff','--cached','--name-only'],cwd=REPO,text=True).strip():raise RuntimeError('unowned staged work')
 else:
  subprocess.run(['git','clone','--bare','--shared',str(REPO),str(gitdir)],check=True,capture_output=True)
  env=dict(os.environ,GIT_DIR=str(gitdir),GIT_WORK_TREE=str(REPO),GIT_INDEX_FILE=str(gitdir/'task.index'))
 def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,env=env,text=True).strip()
 if not writable:
  branch='refs/heads/observer-v1-gun-assault';git('symbolic-ref','HEAD',branch);git('update-ref',branch,base);git('read-tree',base)
 else:branch=git('symbolic-ref','HEAD')
 git('config','core.hooksPath',str(REPO/'.githooks'));git('add','--',*names)
 assert set(git('diff','--cached','--name-only').splitlines())==set(names)
 git('diff','--cached','--check')
 r=subprocess.run(['git','commit','-m','Add observer-only killer telemetry and descriptive gun-assault diagnostic\n\nAssisted-by: Codex:GPT-6'],cwd=REPO,env=env,capture_output=True,text=True)
 (HERE/'COMMIT.log').write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError('normal hooks rejected commit: '+r.stdout+r.stderr)
 head=git('rev-parse','HEAD');assert set(git('diff-tree','--no-commit-id','--name-only','-r',head).splitlines())==set(names)
 git('bundle','create',str(bundle),base+'..'+branch)
 v=subprocess.run(['git','bundle','verify',str(bundle)],cwd=REPO,env=env,capture_output=True,text=True);(HERE/'BUNDLE_VERIFY.log').write_text(v.stdout+v.stderr);assert v.returncode==0
 subprocess.run(['git','clone','--shared','--no-checkout',str(REPO),str(fresh)],check=True,capture_output=True)
 subprocess.run(['git','fetch',str(bundle),branch],cwd=fresh,check=True,capture_output=True)
 assert subprocess.check_output(['git','rev-parse','FETCH_HEAD'],cwd=fresh,text=True).strip()==head
 for n,data in expected.items():assert subprocess.check_output(['git','show',head+':'+n],cwd=fresh)==data,n
 assert_pins()
 write(HERE/'DELIVERY_TRANSPORT.json',dict(base=base,commit=head,bundle=str(bundle),bundle_sha256=sha(bundle),bundle_bytes=bundle.stat().st_size,
  normal_hooks_returncode=0,independent_fetch_verified=True,all_committed_blobs_verified=True,main_git_modified=writable,
  provenance='Assisted-by: Codex:GPT-6',committed_file_hashes={n:sha(REPO/n) for n in names},sidecar=True))
 print(json.dumps(dict(commit=head,bundle=str(bundle),files=len(names),verified=True)))
if __name__=='__main__':main()
