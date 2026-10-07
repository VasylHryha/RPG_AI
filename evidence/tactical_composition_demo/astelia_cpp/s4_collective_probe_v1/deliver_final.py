"""Scoped normal-hook delivery, independent fetched-blob verification."""
import pathlib,sys,json,os,subprocess
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent;REPO=CPP.parents[2];sys.path.insert(0,str(CPP))
from build_admission import sha,admit

def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def pins():
 for n,h in json.loads((HERE/'DECLARATION.json').read_text())['protected'].items():assert sha(REPO/n)==h,n
 for n,h in json.loads((HERE/'RUN_START.json').read_text())['code'].items():assert sha(REPO/n)==h,n
 admit(CPP/'build/astelia_native_collective_probe_v1')
def main():
 pins();assert (HERE/'OWNER_RECHECK.md').read_text().startswith('APPROVE_WITH_NOTES\n');assert json.loads((HERE/'ANALYSIS_VERIFICATION.json').read_text())['status']=='PASS'
 write(HERE/'BUILD_IDENTITY.json',json.loads((CPP/'build/astelia_native_collective_probe_v1.build.json').read_text()))
 base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip();writable=False;error=None;marker=REPO/'.git/collective_probe_v1_write_probe'
 try:
  with marker.open('x') as f:f.write('task scoped writability probe')
  marker.unlink();writable=True
 except OSError as e:error=repr(e)
 write(HERE/'GIT_WRITABILITY.json',dict(writable=writable,error=error))
 paths=[CPP/'S4_COLLECTIVE_PROBE.md',REPO/'docs/reviews/tactical_0g_s194_probe_review_codex.md',*[p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.cpp','.h','.md','.json') and p.name not in ('PARTIAL.json','DELIVERY_TRANSPORT.json','COMMIT.log','BUNDLE_VERIFY.log')]]
 names=[str(p.relative_to(REPO)) for p in paths];expected={n:(REPO/n).read_bytes() for n in names};assert all(len(v)<=45_000_000 for v in expected.values())
 gitdir=CPP/'build/collective_probe_v1_delivery.git';bundle=CPP/'S4_COLLECTIVE_PROBE.bundle';fresh=CPP/'build/collective_probe_v1_fresh_fetch'
 resume='--resume' in sys.argv
 if bundle.exists() or fresh.exists():raise RuntimeError('refuse delivery overwrite')
 if gitdir.exists() and not resume:raise RuntimeError('use explicit resume for owned precommit failure')
 if writable:
  env=dict(os.environ)
  staged_before={n:subprocess.check_output(['git','diff','--cached','--binary','--',n],cwd=REPO) for n in subprocess.check_output(['git','diff','--cached','--name-only'],cwd=REPO,text=True).splitlines() if n not in names}
 else:
  if not gitdir.exists():subprocess.run(['git','clone','--bare','--shared',str(REPO),str(gitdir)],capture_output=True,check=True)
  env=dict(os.environ,GIT_DIR=str(gitdir),GIT_WORK_TREE=str(REPO),GIT_INDEX_FILE=str(gitdir/'task.index'))
 def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,env=env,text=True).strip()
 if not writable:
  branch='refs/heads/s4-collective-probe-v1'
  if resume:
   assert not git('ls-tree','HEAD','--',str((CPP/'S4_COLLECTIVE_PROBE.md').relative_to(REPO))),'refuse to reset committed task delivery'
   subprocess.run(['git','merge-base','--is-ancestor',git('rev-parse','HEAD'),base],cwd=REPO,env=env,check=True)
  git('symbolic-ref','HEAD',branch);git('update-ref',branch,base);git('read-tree',base)
 else:branch=git('symbolic-ref','HEAD')
 git('config','core.hooksPath',str(REPO/'.githooks'));git('add','--',*names);assert set(git('diff','--cached','--name-only','--',*names).splitlines())==set(names);git('diff','--cached','--check','--',*names)
 r=subprocess.run(['git','commit','--only','-m','Record declared scripted collective-commitment probe with realization audits\n\nAssisted-by: Codex:GPT-6','--',*names],cwd=REPO,env=env,capture_output=True,text=True);(HERE/'COMMIT.log').write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError('normal hooks rejected delivery: '+r.stdout+r.stderr)
 head=git('rev-parse','HEAD')
 if writable:
  for n,v in staged_before.items():assert subprocess.check_output(['git','diff','--cached','--binary','--',n],cwd=REPO)==v,n
 assert set(git('diff-tree','--no-commit-id','--name-only','-r',head).splitlines())==set(names)
 git('bundle','create',str(bundle),base+'..'+branch);r=subprocess.run(['git','bundle','verify',str(bundle)],cwd=REPO,env=env,capture_output=True,text=True);(HERE/'BUNDLE_VERIFY.log').write_text(r.stdout+r.stderr);assert r.returncode==0
 subprocess.run(['git','clone','--shared','--no-checkout',str(REPO),str(fresh)],check=True,capture_output=True);subprocess.run(['git','fetch',str(bundle),branch],cwd=fresh,check=True,capture_output=True)
 assert subprocess.check_output(['git','rev-parse','FETCH_HEAD'],cwd=fresh,text=True).strip()==head
 for n,v in expected.items():assert subprocess.check_output(['git','show',head+':'+n],cwd=fresh)==v,n
 pins();write(HERE/'DELIVERY_TRANSPORT.json',dict(base=base,commit=head,bundle=str(bundle),bundle_sha256=sha(bundle),bundle_bytes=bundle.stat().st_size,normal_hooks_returncode=0,independent_fetch_verified=True,all_committed_blobs_verified=True,main_git_modified=writable,provenance='Assisted-by: Codex:GPT-6',committed_file_hashes={n:sha(REPO/n) for n in names},sidecar=True));print(json.dumps(dict(commit=head,bundle=str(bundle),verified=True,files=len(names))))
if __name__=='__main__':main()
