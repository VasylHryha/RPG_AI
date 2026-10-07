"""Launch declared continuation and record honest shared-machine load; no load wait."""
from pathlib import Path
import json,os,subprocess,time
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
start=json.loads((OUT/'CONTINUATION_START.json').read_text())['task_start_epoch']
cmd=['caffeinate','-i','-s',str(ROOT/'.venv/bin/python'),str(ROOT/'tools/c6_option_b_adopt.py'),'--output',str(OUT/'runs'),'--task-start',str(start),'--reuse-diagnostics',str(ROOT/'evidence/c6_option_b/adoption_0032/runs')]
began=time.time();awake=time.monotonic()
with (OUT/'RUN.raw.log').open('x') as log, (OUT/'LOAD_SAMPLES.jsonl').open('x') as samples:
    proc=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    while True:
        samples.write(json.dumps(dict(epoch=time.time(),load_average=list(os.getloadavg()),cpu_count=os.cpu_count(),running=proc.poll() is None))+'\n');samples.flush()
        if proc.poll() is not None:break
        time.sleep(10)
receipt=dict(command=cmd,exit_code=proc.returncode,awake_seconds=time.monotonic()-awake,elapsed_seconds=time.time()-began,task_elapsed_seconds=time.time()-start)
(OUT/'EXECUTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt),flush=True)
raise SystemExit(proc.returncode)
