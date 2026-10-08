"""Concurrent arms with one whole-job gate, live caps and epoch resume."""
import argparse
import os
import secrets
import signal
import subprocess
import sys
import time
from common import ARMS,HERE,LOCAL,read,sha,write
from training_control import TrainingDeadline,training_cap

def completed(arm,digest):
    path=LOCAL/'training'/(arm+'.outcome.json')
    if not path.exists():return False
    r=read(path)
    if r['budget_sha256']!=digest or r['export_sha256']!=sha(LOCAL/'training'/(arm+'.weights.json')) or r['checkpoint_sha256']!=sha(LOCAL/'training'/(arm+'.pt')):raise RuntimeError('completed training drift')
    return True

def run():
    from training import checked_budget
    from jobs import admitted
    import jobs
    b=checked_budget();cap=training_cap(HERE);digest=sha(LOCAL/'TRAIN_BUDGET.json')
    if b['status']!='ADMITTED':raise RuntimeError('training projection refused')
    remaining={}
    from training_control import last_checkpoint,lanes
    for a in ARMS:
        if completed(a,digest):remaining[a]=0;continue
        ck=last_checkpoint(LOCAL/'training/epochs'/a,digest);fraction=1-(ck['epoch'] if ck else 0)/b['epochs'];remaining[a]=b['samples'][a]['fit_seconds']*fraction+b['samples'][a]['validation_seconds']*2
    groups=lanes(remaining,b['topology']['slots']);projection=1.2*max(g['wall_seconds'] for g in groups)
    if projection>cap['cap_seconds']:raise RuntimeError('remaining training projection exceeds current owner cap')
    receipt=dict(status='RUNNING',cap=cap,budget_sha256=digest,projected_remaining_seconds=projection);run_id=secrets.token_hex(8);live={};handles=[]
    try:
        with admitted(cap['cap_seconds']) as (absolute,monitor):
            deadline=TrainingDeadline(HERE,absolute,cap['cap_seconds']);queues=[list(g['arms']) for g in groups]
            while any(queues) or live:
                if time.monotonic()>=deadline:raise TimeoutError('training wall cap reached')
                for lane,queue in enumerate(queues):
                    if lane in live or not queue:continue
                    arm=queue.pop(0)
                    if completed(arm,digest):continue
                    out=LOCAL/'training';out.mkdir(parents=True,exist_ok=True);log=(out/(arm+'.worker.log')).open('a');handles.append(log)
                    child=subprocess.Popen([sys.executable,str(HERE/'worker.py'),'--arm',arm,'--deadline',str(absolute),'--cap',str(cap['cap_seconds']),'--fds',*[str(f) for f in jobs.ACTIVE_FDS]],stdout=log,stderr=subprocess.STDOUT,pass_fds=jobs.ACTIVE_FDS,start_new_session=True,env={**os.environ,'OMP_NUM_THREADS':'2','MKL_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2'});live[lane]=(child,arm)
                for lane,(child,arm) in list(live.items()):
                    if child.poll() is not None:
                        if child.returncode or not completed(arm,digest):raise RuntimeError(arm+' worker failed; inspect log then resume')
                        del live[lane]
                    else:monitor.live_memory(child.pid)
                time.sleep(.2)
            receipt['status']='DONE'
    except BaseException as e:receipt.update(status='STOP_RESUMABLE',error=f'{type(e).__name__}: {e}');raise
    finally:
        for child,arm in live.values():
            if child.poll() is None:os.killpg(child.pid,signal.SIGTERM)
        for child,arm in live.values():
            try:child.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
        for f in handles:f.close()
        write(HERE/('TRAIN_RUN_'+run_id+'.json'),receipt,exclusive=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('measure','run'));p.add_argument('--epochs',type=int,default=2);p.add_argument('--windows',type=int,default=4);a=p.parse_args()
    if a.command=='measure':
        from training import measure
        measure(a.epochs,a.windows)
    else:run()
