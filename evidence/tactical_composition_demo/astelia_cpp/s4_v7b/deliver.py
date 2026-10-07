"""Explicit-path normal-hook commit, or verified current-HEAD bundle."""
from common import *

def deliver():
 d=pins();review=HERE/'OWNER_RECHECK.md'
 if not review.read_text().startswith('APPROVE'):raise RuntimeError('implementation recheck missing')
 base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
 names=[str(p.relative_to(REPO)) for p in sorted(HERE.iterdir()) if p.is_file() and (p.suffix in ('.py','.md','.json') or p.name=='.gitignore' or p.name=='FIXTURE.log' or p.name.startswith('TESTS') and p.suffix=='.log') and p.name not in ('DELIVERY_TRANSPORT.json',)]
 if any(pathlib.Path(n).name in FORBIDDEN for n in names):raise RuntimeError('forbidden path in delivery')
 names=sorted(set(names));expected={n:(REPO/n).read_bytes() for n in names}
 marker=REPO/'.git/v7b_write_probe';writable=False;error=None
 try:
  with marker.open('x') as f:f.write('scoped v7b writability check')
  marker.unlink();writable=True
 except OSError as e:error=str(e)
 env=dict(os.environ);delivery=HERE/'delivery';delivery.mkdir(exist_ok=True)
 if not writable:
  gitdir=delivery/'delivery.git'
  if gitdir.exists():raise RuntimeError('existing delivery transport; do not overwrite')
  subprocess.run(['git','clone','--bare','--shared',str(REPO),str(gitdir)],check=True,capture_output=True)
  env.update(GIT_DIR=str(gitdir),GIT_WORK_TREE=str(REPO),GIT_INDEX_FILE=str(gitdir/'task.index'))
 def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,env=env,text=True).strip()
 if not writable:
  branch='refs/heads/s4-v7b-codex';git('symbolic-ref','HEAD',branch);git('update-ref',branch,base);git('read-tree',base);git('config','core.hooksPath',str(REPO/'.githooks'))
 else:
  branch=git('symbolic-ref','HEAD')
  if git('config','core.hooksPath')!='.githooks':raise RuntimeError('repository hooks not installed')
 staged_before={n:subprocess.check_output(['git','diff','--cached','--binary','--',n],cwd=REPO,env=env) for n in git('diff','--cached','--name-only').splitlines() if n not in names}
 git('add','--',*names);git('diff','--cached','--check','--',*names)
 message='Deliver v7b with parallel throughput projection warm-up and fresh development entropy; no fights\n\nAssisted-by: Codex:GPT-6'
 p=subprocess.run(['git','commit','--only','-m',message,'--',*names],cwd=REPO,env=env,text=True,capture_output=True)
 (HERE/'COMMIT.log').write_text(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 head=git('rev-parse','HEAD')
 if set(git('diff-tree','--no-commit-id','--name-only','-r',head).splitlines())!=set(names):raise RuntimeError('commit scope mismatch')
 for n,b in staged_before.items():
  if subprocess.check_output(['git','diff','--cached','--binary','--',n],cwd=REPO,env=env)!=b:raise RuntimeError('unrelated staging changed')
 if not git('show','-s','--format=%B',head).endswith('Assisted-by: Codex:GPT-6'):raise RuntimeError('provenance mismatch')
 for n,b in expected.items():
  if subprocess.check_output(['git','show',head+':'+n],cwd=REPO,env=env)!=b:raise RuntimeError('committed blob mismatch')
 transport=dict(base=base,commit=head,main_git_modified=writable,writability_error=error,normal_hooks_returncode=0,explicit_paths=names,committed_file_hashes={n:sha(REPO/n) for n in names})
 if not writable:
  bundle=HERE/'S4_V7B.bundle';git('bundle','create',str(bundle),base+'..'+branch)
  result=subprocess.run(['git','bundle','verify',str(bundle)],cwd=REPO,env=env,text=True,capture_output=True)
  (HERE/'BUNDLE_VERIFY.log').write_text(result.stdout+result.stderr)
  if result.returncode:raise RuntimeError('bundle verification failed')
  fresh=delivery/'fresh_fetch';subprocess.run(['git','clone','--shared','--no-checkout',str(REPO),str(fresh)],check=True,capture_output=True)
  subprocess.run(['git','fetch',str(bundle),branch],cwd=fresh,check=True,capture_output=True)
  if subprocess.check_output(['git','rev-parse','FETCH_HEAD'],cwd=fresh,text=True).strip()!=head:raise RuntimeError('fetch commit mismatch')
  for n,b in expected.items():
   if subprocess.check_output(['git','show',head+':'+n],cwd=fresh)!=b:raise RuntimeError('fetched blob mismatch')
  transport.update(bundle_sha256=sha(bundle),bundle_bytes=bundle.stat().st_size,independent_fetch_and_all_blobs_verified=True,bundle=str(bundle.relative_to(REPO)))
 write(HERE/'DELIVERY_TRANSPORT.json',transport);print(json.dumps(transport))
if __name__=='__main__':deliver()
