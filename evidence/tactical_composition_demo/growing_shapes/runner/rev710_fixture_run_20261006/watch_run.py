"""Launch once under caffeinate; observe shared load without scientific hooks."""
import json,os,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent
if (OUT/'PROCESS_START.json').exists():raise SystemExit('STOP: already launched')
with (OUT/'PROCESS_START.json').open('x') as f:json.dump(dict(start_utc=datetime.now(timezone.utc).isoformat(),command=['/usr/bin/caffeinate','-i','-s',sys.executable,'-u',str(OUT/'execute_once.py')],load_average=list(os.getloadavg()),logical_cpus=os.cpu_count()),f,indent=2)
with (OUT/'EXECUTION_LOG.txt').open('x') as log, (OUT/'OBSERVED_LOAD_SAMPLES.jsonl').open('x') as load:
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 process=subprocess.Popen(['/usr/bin/caffeinate','-i','-s',sys.executable,'-u',str(OUT/'execute_once.py')],stdout=log,stderr=subprocess.STDOUT,env=env)
 while True:
  load.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),load_average_1_5_15=list(os.getloadavg()),logical_cpus=os.cpu_count(),owner_reported_concurrency=['0g v5 development','C6 performance analysis'],per_task_cpu_allocation=None))+'\n');load.flush()
  try:
   result=process.wait(timeout=30);break
  except subprocess.TimeoutExpired:pass
with (OUT/'PROCESS_END.json').open('x') as f:json.dump(dict(end_utc=datetime.now(timezone.utc).isoformat(),exit_code=result,load_average=list(os.getloadavg())),f,indent=2)
print('Fixture process completed:',result,flush=True)
raise SystemExit(result)
