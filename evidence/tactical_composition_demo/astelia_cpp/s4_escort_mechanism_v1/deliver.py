#!/usr/bin/env python3
"""Scoped normal-hook delivery; readonly-main fallback uses a verified bundle."""
import os,subprocess,json
from analyze import HERE,sha,dump
REPO=HERE.parents[3]
def main():
 validation=json.loads((HERE/'VALIDATION.json').read_text());assert validation['status']=='PASS'
 names=sorted([*validation['checked_hashes'],str((HERE/'VALIDATION.json').relative_to(REPO)),str((HERE/'GIT_WRITABILITY.json').relative_to(REPO))])
 for n,h in validation['checked_hashes'].items():assert sha(REPO/n)==h,('changed after validation',n)
 base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip();writable=False;error=None
 marker=REPO/'.git/escort_mechanism_write_probe'
 try:
  with marker.open('x') as f:f.write('authorized scoped delivery writability check')
  marker.unlink();writable=True
 except OSError as e:error=str(e)
 dump(HERE/'GIT_WRITABILITY.json',dict(writable=writable,error=error))
 expected={n:(REPO/n).read_bytes() for n in names};assert all(len(b)<=45_000_000 for b in expected.values())
 primary_index=subprocess.check_output(['git','diff','--cached','--binary'],cwd=REPO);env=dict(os.environ)
 if not writable:
  gitdir=HERE/'delivery/attempt2.git';assert not gitdir.exists()
  gitdir.parent.mkdir(exist_ok=True)
  subprocess.run(['git','clone','--bare','--shared',str(REPO),str(gitdir)],check=True,capture_output=True)
  env.update(GIT_DIR=str(gitdir),GIT_WORK_TREE=str(REPO),GIT_INDEX_FILE=str(gitdir/'task.index'))
 def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,env=env,text=True).strip()
 if not writable:
  branch='refs/heads/s4-escort-mechanism-v1';git('symbolic-ref','HEAD',branch);git('update-ref',branch,base);git('read-tree',base);git('config','core.hooksPath',str(REPO/'.githooks'))
 else:
  branch=git('symbolic-ref','HEAD');assert git('config','core.hooksPath')=='.githooks'
 unrelated={n:subprocess.check_output(['git','diff','--cached','--binary','--',n],cwd=REPO,env=env) for n in git('diff','--cached','--name-only').splitlines() if n not in names}
 git('add','--',*names);git('diff','--cached','--check','--',*names)
 result=subprocess.run(['git','commit','--only','-m','Audit sealed escort probe and diagnose stored escort mechanism\n\nAssisted-by: Codex:GPT-6','--',*names],cwd=REPO,env=env,text=True,capture_output=True)
 (HERE/'COMMIT.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stdout+result.stderr
 head=git('rev-parse','HEAD');assert set(git('diff-tree','--no-commit-id','--name-only','-r',head).splitlines())==set(names)
 for n,b in unrelated.items():assert subprocess.check_output(['git','diff','--cached','--binary','--',n],cwd=REPO,env=env)==b
 bundle=HERE/'S4_ESCORT_MECHANISM.bundle';assert not bundle.exists();git('bundle','create',str(bundle),base+'..'+branch)
 result=subprocess.run(['git','bundle','verify',str(bundle)],cwd=REPO,env=env,text=True,capture_output=True);(HERE/'BUNDLE_VERIFY.log').write_text(result.stdout+result.stderr);assert result.returncode==0
 fresh=HERE/'delivery/fresh_fetch';assert not fresh.exists()
 subprocess.run(['git','clone','--shared','--no-checkout',str(REPO),str(fresh)],check=True,capture_output=True)
 subprocess.run(['git','fetch',str(bundle),branch],cwd=fresh,check=True,capture_output=True)
 assert subprocess.check_output(['git','rev-parse','FETCH_HEAD'],cwd=fresh,text=True).strip()==head
 for n,b in expected.items():assert subprocess.check_output(['git','show',head+':'+n],cwd=fresh)==b
 assert git('show','-s','--format=%B',head).endswith('Assisted-by: Codex:GPT-6')
 current=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
 if not writable:
  assert current==base,('primary HEAD moved during delivery',base,current)
  assert subprocess.check_output(['git','diff','--cached','--binary'],cwd=REPO)==primary_index
 dump(HERE/'DELIVERY_TRANSPORT.json',dict(base=base,commit=head,main_git_modified=writable,main_head_after=current,bundle_sha256=sha(bundle),bundle_bytes=bundle.stat().st_size,normal_hooks_returncode=0,independent_fetch_and_all_blob_bytes_verified=True,explicit_paths=names,committed_file_hashes={n:sha(REPO/n) for n in names}))
 print(json.dumps(dict(base=base,commit=head,main_git_modified=writable,bundle=str(bundle),verified=True)))
if __name__=='__main__':main()
