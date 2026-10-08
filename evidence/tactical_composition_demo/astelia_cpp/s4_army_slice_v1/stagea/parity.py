"""Full validation-sequence float32 / exported float64 / C++ parity gate."""
import argparse
import copy
import json
import subprocess
import time
import numpy as np
import torch
from common import ARMS,BINARY,HERE,LOCAL,read,sha,write
from data import frames
from models import Policy,initial
from training import environment,flat,forward
DEADLINE=None
MONITOR=None
LAST_CHECK=0.
def check_live(pid=None):
    global LAST_CHECK
    if DEADLINE is not None and time.monotonic()>=DEADLINE:raise TimeoutError("parity invocation cap")
    if MONITOR is not None and time.monotonic()-LAST_CHECK>=1:
        MONITOR.live_memory(__import__("os").getpid() if pid is None else pid);LAST_CHECK=time.monotonic()

def load_model(arm,dtype):
    weights=read(LOCAL/'training'/(arm+'.weights.json'));m=Policy(arm).to(dtype=dtype)
    m.load_state_dict({k:torch.tensor(v['values'],dtype=dtype).reshape(v['shape']) for k,v in weights['parameters'].items()});m.eval();return m,weights

def sequence(model,rows):
    state=initial(model.kind,[],next(model.parameters()).dtype);ids=[];cache=None;next_frame=(0,[]);outputs=[]
    with torch.no_grad():
        for row in rows:
            check_live()
            y,state,ids,enemies,cache,next_frame,_=forward(model,row,state,ids,cache,next_frame);outputs.append(flat(y).detach().numpy())
    return outputs

def categories(x):return np.concatenate((x[:,3:6].argmax(1)[:,None],x[:,10:].argmax(1)[:,None]),1)

def replay(weights,rows,timeout=600):
    # Stream one frame per RPC; persistent native state, bounded JS heap per tick.
    import secrets
    directory=LOCAL/'parity';directory.mkdir(parents=True,exist_ok=True)
    token=secrets.token_hex(8);request_path=directory/(token+'.requests.jsonl');output_path=directory/(token+'.outputs.jsonl')
    with request_path.open('w') as f:
        for i,row in enumerate(rows):
            check_live()
            request=dict(operation='stageaReplay',frames=[row])
            if i==0:request['weights']=weights
            f.write(json.dumps(request,allow_nan=False,separators=(',',':'))+'\n')
    with request_path.open('r') as src,output_path.open('w') as dst:
        errpath=directory/(token+'.stderr')
        with errpath.open('w') as err:
            child=subprocess.Popen([str(BINARY)],stdin=src,stdout=dst,stderr=err,start_new_session=True)
            started=time.monotonic()
            try:
                while child.poll() is None:
                    check_live(child.pid)
                    if time.monotonic()-started>timeout:raise TimeoutError('native sequence replay timeout')
                    time.sleep(.1)
                if child.returncode or errpath.stat().st_size:raise RuntimeError('native parity host failed; inspect local stream/stderr')
            finally:
                if child.poll() is None:__import__('os').killpg(child.pid,9);child.wait()
    out=[]
    with output_path.open() as f:
        for line in f:
            check_live()
            result=json.loads(line)
            if 'error' in result or result.get('combat_steps')!=0:raise RuntimeError('bad native replay '+str(result))
            if len(result['outputs'])!=1:raise RuntimeError('stream replay tick count')
            out.append(np.asarray(result['outputs'][0],dtype=np.float64))
    request_path.unlink();output_path.unlink();errpath.unlink()
    return out

def compare(a,b):
    if len(a)!=len(b) or any(x.shape!=y.shape for x,y in zip(a,b)):raise RuntimeError('parity sequence dimensions')
    return dict(max_abs_error=max((float(np.max(np.abs(x-y))) if x.size else 0 for x,y in zip(a,b)),default=0),categorical_mismatches=sum(int(np.sum(categories(x)!=categories(y))) for x,y in zip(a,b)),rows=sum(len(x) for x in a))

def run():
    global DEADLINE,MONITOR
    environment();from collect import identity,check
    check();from training import checked_budget
    checked_budget();index=read(LOCAL/'INDEX.json');records=[];start=time.monotonic()
    from jobs import admitted
    from training_control import training_cap,TrainingDeadline
    cap=training_cap(HERE);run_id=__import__('secrets').token_hex(8)
    manifest=dict(binary=identity(),budget_sha256=sha(LOCAL/'TRAIN_BUDGET.json'),index_sha256=sha(LOCAL/'INDEX.json'),exports={a:sha(LOCAL/'training'/(a+'.weights.json')) for a in ARMS})
    receipt=dict(status='RUNNING',cap=cap,manifest=manifest)
    try:
        with admitted(cap['cap_seconds']) as (absolute,monitor):
            DEADLINE=TrainingDeadline(HERE,absolute,cap['cap_seconds']);MONITOR=monitor
            val=[f for f in index['fights'] if f['split']=='validation']
            if not val:raise RuntimeError('validation sequences required')
            # First full sequence for each arm measures the sequential parity tail.
            jobs=[(a,f) for f in val for a in ARMS]
            rates={};models={a:(*load_model(a,torch.float32),load_model(a,torch.float64)[0]) for a in ARMS}
            for i,(arm,fight) in enumerate(jobs):
                check_live();raw=LOCAL/fight['raw_file']
                if sha(raw)!=fight['raw_sha256']:raise RuntimeError('parity shard drift')
                proof_path=LOCAL/'parity'/f"{arm}_{fight['tag']}.receipt.json"
                if proof_path.exists():
                    r=read(proof_path)
                    if r['manifest']!=manifest or r['raw_sha256']!=sha(raw) or r['status']!='PASS':raise RuntimeError('stored parity receipt drift')
                else:
                    began=time.monotonic();m32,weights,m64=models[arm];rows=list(frames(raw));check_live()
                    a=sequence(m32,rows);b=sequence(m64,rows);c=replay(weights,rows,timeout=max(1,float(DEADLINE-time.monotonic())))
                    r=dict(status='PASS',manifest=manifest,arm=arm,fight=fight['tag'],raw_sha256=sha(raw),float32_export=compare(a,b),native_float64=compare(b,c),seconds=time.monotonic()-began,frames=len(rows))
                    if r['float32_export']['categorical_mismatches'] or r['native_float64']['categorical_mismatches'] or r['native_float64']['max_abs_error']>1e-8:
                        r['status']='FAIL';write(proof_path,r,exclusive=True);raise RuntimeError('categorical/numeric export parity defect')
                    write(proof_path,r,exclusive=True)
                records.append(r);rates[arm]=max(rates.get(arm,0),r['seconds']/max(1,r['frames']))
                if i==len(ARMS)-1:
                    remaining=[(a,f) for a,f in jobs[i+1:] if not (LOCAL/'parity'/f"{a}_{f['tag']}.receipt.json").exists()]
                    projected=1.2*sum(rates[a]*f['frames'] for a,f in remaining)
                    write(LOCAL/'PARITY_PROJECTION.json',dict(projected_remaining_seconds=projected,sample_sequences=len(ARMS),rates=rates))
                    if projected>DEADLINE-time.monotonic():raise RuntimeError('measured remaining parity projection exceeds owner cap')
            if identity()!=manifest['binary']:raise RuntimeError('parity binary drift')
            result=dict(status='PASS',scope='all physical ticks of all held-out validation fights; resets and identity pruning',seconds=time.monotonic()-start,**manifest,records=records)
            write(HERE/'PARITY_STAGEA.json',result);receipt['status']='DONE'
    except BaseException as error:receipt.update(status='STOP_RESUMABLE',error=f'{type(error).__name__}: {error}');raise
    finally:
        DEADLINE=None;MONITOR=None;write(HERE/('PARITY_RUN_'+run_id+'.json'),receipt,exclusive=True)

if __name__=='__main__':run()
