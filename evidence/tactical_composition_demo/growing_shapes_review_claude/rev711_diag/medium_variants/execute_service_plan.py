"""Exact A6w/A6x one-shot schedule. No fresh keys, tuning, or retries."""
import concurrent.futures
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

OUT=Path(__file__).resolve().parent
LOCAL=OUT/'_local'
PATTERN='s4_spacing_probe_v1|astelia_native|tactics.*host'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def process_check():
    p=subprocess.run(['pgrep','-fl',PATTERN],text=True,capture_output=True)
    result=dict(command=['pgrep','-fl',PATTERN],returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,time_epoch=time.time())
    if p.returncode not in (0,1) or p.stderr: result['status']='PROCESS_ACCESS_BLOCKED'
    else: result['status']='BUSY' if p.returncode==0 else 'CLEAR'
    return result


def code_hashes():
    paths=list(OUT.glob('*.py'))+list((OUT/'kernel_builder').glob('*.py'))+list((OUT/'kernel_builder').glob('*_BUILD.json'))
    paths += [OUT/'kernel_builder/ranked_d3_body.txt',OUT/'bond_v2_screening.patch',OUT/'bond_v2_screening_V1_path_protected_D3.pydiff']
    for variant in ('SCR','V1','RD3'):
        kernel=OUT/'kernel_builder/_worktrees'/variant
        paths += [kernel/'evidence/tactical_composition_demo/growing_shapes/medium/rev7_design.py',kernel/'evidence/tactical_composition_demo/growing_shapes_review_claude/rev711_diag/pilot_common.py']
        if variant=='RD3': paths += [kernel/'service_graph.py']
    return {str(p):sha(p) for p in paths}


def check_frozen(expected):
    for name,h in expected.items():
        if sha(Path(name))!=h: raise RuntimeError(f'code changed during run: {name}')


def worker(job,ticket):
    variant,start,key,observer=job
    process=process_check()
    if process['status']!='CLEAR': raise RuntimeError('process preflight changed: '+json.dumps(process))
    name=f'{variant}_{start}_k{key}_{observer}'
    with (LOCAL/(name+'.raw.log')).open('x') as log:
        subprocess.run([sys.executable,str(OUT/'run_service_pilot.py'),'--variant',variant,'--start',start,'--keyset',str(key),'--observer',observer,'--ticket',str(ticket)],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=max(1,json.loads(ticket.read_text())['deadline_epoch']-time.time()))
    return json.loads((LOCAL/(name+'.summary.json')).read_text())


def expected_log(result):
    name=f"{result['variant'].lower()}_{result['start']}_k{result['keyset']}.log"
    for line in (OUT/'logs'/name).read_text().splitlines():
        if line.startswith('{'): return json.loads(line)
    raise ValueError('missing committed summary '+name)


def schedule(pool,jobs,ticket,baseline,started,cpu_estimate=660.,future_groups=()):
    # Every phase must fit before starting; elapsed/awake is capped at 3600 s.
    # 10 concurrent slots is a cap, not a promise of 10 effective CPUs.
    elapsed=time.monotonic()-started
    projected=elapsed+sum(math.ceil(n/min(10,os.cpu_count() or 1)) for n in (len(jobs),*future_groups))*cpu_estimate
    if projected>=3600: raise RuntimeError(f'STOP projection {projected:.1f}s exceeds 1 hour')
    check_frozen(baseline)
    results=list(pool.map(lambda job:worker(job,ticket),jobs))
    check_frozen(baseline)
    return results


def main():
    LOCAL.mkdir(exist_ok=True)
    checks=[]
    # Wait for 0g to finish, using short waits. Inaccessible pgrep is never clear.
    wait_started=time.monotonic()
    while True:
        check=process_check();checks.append(check)
        (OUT/'SERVICE_PREFLIGHT.json').write_text(json.dumps(dict(status=check['status'],checks=checks),indent=2)+'\n')
        if check['status']=='PROCESS_ACCESS_BLOCKED':
            print('STOP: pgrep cannot verify shared-machine combat load');return 2
        if check['status']=='CLEAR': break
        if time.monotonic()-wait_started>3600: print('STOP: 0g still busy after one hour waiting');return 2
        print('Waiting for competing combat processes...',flush=True);time.sleep(15)
    started=time.monotonic();baseline=code_hashes()
    ticket=LOCAL/'RUN_TICKET.json'
    initial_projection=sum(math.ceil(n/min(10,os.cpu_count() or 1)) for n in (2,19,10))*660
    if initial_projection>=3600:
        (OUT/'SERVICE_PREFLIGHT.json').write_text(json.dumps(dict(status='PROJECTION_STOP',projection_seconds=initial_projection,checks=checks),indent=2)+'\n');return 2
    data=dict(status='RUNNING',started_epoch=time.time(),deadline_epoch=time.time()+3600,code_hashes=baseline,projection_seconds=initial_projection)
    with ticket.open('x') as f: json.dump(data,f,indent=2)
    caffeinate=subprocess.Popen(['caffeinate','-i','-s'])
    results=[]; integrity={}; status='PARTIAL'
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            # On key 0 is Part A's single SCR empty run; off is the extra required
            # complete integrity control. No reported key is rerun.
            pair=schedule(pool,[('SCR','i',0,'off'),('SCR','i',0,'on')],ticket,baseline,started,future_groups=(19,10))
            if pair[0]['state_trajectory_sha256']!=pair[1]['state_trajectory_sha256']: raise RuntimeError('observer changes state trajectory')
            integrity['observer_on_off']='PASS';integrity['clone_isolation']='PASS'
            if pair[1]['summary']!=expected_log(pair[1]): raise RuntimeError('SCR integrity summary mismatch')
            results.append(pair[1])
            measured=max(max(r['cpu_seconds'],r['elapsed_seconds']) for r in pair)
            remainder=[(v,s,k,'on') for v in ('SCR','V1') for s in ('i','ii') for k in range(5) if (v,s,k)!=('SCR','i',0)]
            a=schedule(pool,remainder,ticket,baseline,started,max(660,measured),future_groups=(10,));results+=a
            mismatches=[(r['variant'],r['start'],r['keyset']) for r in results if r['summary']!=expected_log(r)]
            if mismatches: raise RuntimeError('committed log reproduction mismatch '+repr(mismatches))
            integrity['scr_v1_reproduction']='PASS'
            measured=max(measured,max(max(r['cpu_seconds'],r['elapsed_seconds']) for r in a))
            # RD3 never starts before all Part A reproduction checks pass.
            results+=schedule(pool,[('RD3',s,k,'on') for s in ('i','ii') for k in range(5)],ticket,baseline,started,max(660,measured))
            status='DONE'
    except Exception as error:
        data['stop_reason']=str(error);print('STOP:',error,flush=True)
    finally:
        caffeinate.terminate();caffeinate.wait()
        # Recover all successful jobs even when a parallel phase raised.
        completed=[json.loads(p.read_text()) for p in sorted(LOCAL.glob('*_on.summary.json'))]
        results=list({(r['variant'],r['start'],r['keyset']):r for r in completed}.values())
        raw_inventory=[]
        for p in sorted(LOCAL.rglob('*')):
            if p.is_file() and (p.name.endswith('.gz') or p.name.endswith('.raw.log')):
                job=p.name.split('.jsonl')[0].split('.legacy')[0].split('.raw.log')[0]
                raw_inventory.append(dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p),
                                          completeness='COMPLETE' if (LOCAL/(job+'.summary.json')).exists() else 'INCOMPLETE'))
        data.update(status=status,elapsed_seconds=time.monotonic()-started,awake_seconds=time.monotonic()-started,integrity=integrity)
        ticket.write_text(json.dumps(data,indent=2)+'\n')
        (OUT/'SERVICE_RUN_SUMMARIES.json').write_text(json.dumps(dict(status=status,integrity=integrity,runs=results,raw_inventory=raw_inventory,timing=data),separators=(',',':'),allow_nan=False)+'\n')
    return 0 if status=='DONE' else 2


if __name__=='__main__': sys.exit(main())
