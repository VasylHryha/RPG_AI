"""Timed caffeinated stages with remaining-total cap, including failed attempts."""
import pathlib,subprocess,sys,time,json,os,signal
HERE=pathlib.Path(__file__).resolve().parent;REPO=HERE.parents[3]
def main():
 name=sys.argv[1];assert name in ('build','check','run','analyze','report','boundary');prior=sum(json.loads(p.read_text())['awake_seconds'] for p in HERE.glob('STAGE_*.json'));remaining=3600-60-prior
 if remaining<=0:raise SystemExit('STOP total budget exhausted')
 start=time.time();awake=time.monotonic();child=None;ok=False;out='';err='';cap=min(1200,remaining)
 try:
  child=subprocess.Popen(['/usr/bin/caffeinate','-i','-s',str(REPO/'.venv/bin/python'),str(HERE/({'analyze':'recount_final.py','report':'render.py','boundary':'boundary_audit.py'}.get(name,name+'.py'))),*sys.argv[2:]],cwd=REPO,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
  out,err=child.communicate(timeout=cap);ok=child.returncode==0
 except subprocess.TimeoutExpired:
  os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5);err+='\nSTOP stage/total compute deadline\n'
 finally:
  count=len(list(HERE.glob('STAGE_'+name+'_*.json')));record=dict(stage=name,status='PASS' if ok else 'STOP',returncode=child.returncode if child else None,cap_seconds=cap,elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake)
  (HERE/f'STAGE_{name}_{count:02d}.json').write_text(json.dumps(record,indent=2)+'\n');(HERE/f'{name.upper()}_{count:02d}.stdout.log').write_text(out);(HERE/f'{name.upper()}_{count:02d}.stderr.log').write_text(err);(HERE/f'{name.upper()}.stdout.log').write_text(out);(HERE/f'{name.upper()}.stderr.log').write_text(err)
 print(out);print(err,file=sys.stderr);raise SystemExit(0 if ok else 1)
if __name__=='__main__':main()
