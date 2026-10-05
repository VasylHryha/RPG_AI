"""Non-final engineering checks; at most two cold world subprocesses at once."""
import json
import os
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
ENV=dict(os.environ,PYTHONPYCACHEPREFIX='/private/tmp/c6_option_b_parallel_pycache')

def run_pair(cases):
    live=[]
    for name,flags in cases:
        command=[str(ROOT/'.venv/bin/python'),str(ROOT/'tools/c6_option_b_check.py'),
                 '--backend','native','--parallel','--output',str(OUT/name),*flags]
        log=(OUT/(name+'.log')).open('x')
        process=subprocess.Popen(command,cwd=ROOT,env=ENV,stdout=log,stderr=subprocess.STDOUT)
        live.append((name,process,log,command))
    with (OUT/'MACHINE_LOAD.jsonl').open('a') as load:
        while any(p.poll() is None for _,p,_,_ in live):
            load.write(json.dumps({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                'load_average':list(os.getloadavg()),'logical_cpus':os.cpu_count(),
                'active':[name for name,p,_,_ in live if p.poll() is None]})+'\n');load.flush()
            time.sleep(10)
    for name,p,log,command in live:
        log.close()
        record={'command':command,'exit_code':p.returncode}
        (OUT/(name+'_COMMAND.json')).write_text(json.dumps(record,indent=2)+'\n')
        print(json.dumps({'name':name,**record}),flush=True)
        if p.returncode:raise RuntimeError(name+' failed')
        cost=json.loads((OUT/name/'COSTS.json').read_text())
        if cost['invalid'] is not None:raise RuntimeError(name+' invalid: '+str(cost['invalid']))

if __name__=='__main__':
    # Fixture pair audits every full array against the reference on identical inputs.
    run_pair([(f'fixture_{order}',['--fixture','--audit','--schedule',order]) for order in ('forward','reverse')])
    run_pair([(f'smoke_{i}_forward',['--entropy','smoke','--world',str(i)]) for i in (0,1)])
    run_pair([('development_0_forward',['--entropy','development','--world','0','--audit']),
              ('smoke_0_reverse',['--entropy','smoke','--world','0','--schedule','reverse'])])
    run_pair([('smoke_1_reverse',['--entropy','smoke','--world','1','--schedule','reverse']),
              ('development_0_reverse',['--entropy','development','--world','0','--schedule','reverse'])])
