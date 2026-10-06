"""Outer caffeinate launcher/supervisor; no repeat or low-load wait."""
import datetime,json,os,pathlib,subprocess,time
from s4_v6 import ROOT,CHECKS,write
REPO=ROOT.parents[2]
def main():
    d=json.loads((CHECKS/'PART1_DELIVERY.json').read_text());now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
    out=ROOT/('s4_v6_development_'+datetime.datetime.now().strftime('%Y%m%d_%H%M'))
    if out.exists() or (CHECKS/'LAUNCH.json').exists():raise RuntimeError('single run already claimed')
    argv=[str(REPO/'.venv/bin/python'),str(ROOT/'s4_v6.py'),'--implementation-commit',d['implementation_commit'],'--output',str(out)]
    command=['/usr/bin/caffeinate','-i','-s',*argv]
    started=time.time();awake=time.monotonic()
    write(CHECKS/'LAUNCH.json',dict(start_utc=now(),command=command,output=str(out),load_average=os.getloadavg(),
                                  expected_minutes=65,allowance_minutes=360,policy='owner/0031: night launch immediately, no low-load waiting'))
    with (CHECKS/'RUN.stdout.log').open('x') as stdout,(CHECKS/'RUN.stderr.log').open('x') as stderr:
        p=subprocess.Popen(command,cwd=REPO,stdout=stdout,stderr=stderr)
        print('LAUNCHED',p.pid,str(out),flush=True)
        with (CHECKS/'LOAD_SAMPLES.jsonl').open('x') as load:
            while p.poll() is None:
                load.write(json.dumps(dict(utc=now(),elapsed_seconds=time.time()-started,awake_seconds=time.monotonic()-awake,load_average=os.getloadavg()))+'\n');load.flush()
                try:p.wait(timeout=30)
                except subprocess.TimeoutExpired:pass
    write(CHECKS/'SUPERVISOR_TIMING.json',dict(elapsed_seconds=time.time()-started,awake_seconds=time.monotonic()-awake,
              end_utc=now(),returncode=p.returncode,load_average_end=os.getloadavg(),caffeinate=True))
    print('FINISHED',p.returncode,flush=True);raise SystemExit(p.returncode)
if __name__=='__main__':main()
