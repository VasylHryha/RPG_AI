import datetime,json,os,pathlib,subprocess,time
root=pathlib.Path(__file__).resolve().parents[1]
repo=root.parents[2]
checks=pathlib.Path(__file__).resolve().parent
out=root/'s4_v5_development_20261006_2308'
if out.exists():raise RuntimeError('refuse existing output')
delivery=json.loads((root/'s4_v5_part1_checks/PART1_DELIVERY.json').read_text())
cmd=[str(repo/'.venv/bin/python'),str(root/'s4_v5.py'),'--implementation-commit',delivery['implementation_commit'],'--output',str(out)]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(name,data):(checks/name).write_text(json.dumps(data,indent=2)+'\n')
start=time.time();awake=time.monotonic()
save('LAUNCH.json',dict(start_utc=now(),command=cmd,output=str(out),load_average=os.getloadavg(),policy='launch immediately regardless of load; owner override',allowance_minutes=360,caffeinate=True,prior_attempt_preserved='s4_v5_development_checks',implementation_commit=delivery['implementation_commit']))
with (checks/'RUN.stdout.log').open('x') as stdout,(checks/'RUN.stderr.log').open('x') as stderr:
 p=subprocess.Popen(cmd,cwd=repo,stdout=stdout,stderr=stderr)
 print('LAUNCHED',p.pid,str(out),flush=True)
 with (checks/'LOAD_SAMPLES.jsonl').open('x') as load:
  while p.poll() is None:
   load.write(json.dumps(dict(utc=now(),elapsed_seconds=time.time()-start,awake_monotonic_seconds=time.monotonic()-awake,load_average=os.getloadavg()))+'\n');load.flush()
   try:p.wait(timeout=30)
   except subprocess.TimeoutExpired:pass
 rc=p.returncode
save('SUPERVISOR_TIMING.json',dict(start_epoch=start,end_utc=now(),elapsed_seconds=time.time()-start,awake_monotonic_seconds=time.monotonic()-awake,returncode=rc,load_average_end=os.getloadavg(),caffeinate=True))
print('FINISHED',rc,flush=True)
raise SystemExit(rc)
