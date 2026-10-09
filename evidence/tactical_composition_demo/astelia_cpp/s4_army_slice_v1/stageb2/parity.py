"""Full validation-sequence float32 / exported float64 / C++ parity gate."""
import argparse
import copy
import json
import os
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

def sequence(model,rows,audit=None):
    state=initial(model.kind,[],next(model.parameters()).dtype);ids=[];cache=None;next_frame=(0,[]);outputs=[]
    with torch.no_grad():
        for row in rows:
            check_live()
            y,state,ids,enemies,cache,next_frame,_=forward(model,row,state,ids,cache,next_frame);outputs.append(flat(y).detach().numpy())
            if audit is not None:
                from candidate_audit import observe_prediction
                observe_prediction(audit,row,ids,y)
    return outputs

def categories(x):return np.stack([x[:,s].argmax(1) for _,s in HEADS],1)

def replay(weights,rows,timeout=600,profile=None,fixture_monitor=None):
    # Stream one frame per RPC; persistent native state, bounded JS heap per tick.
    import secrets
    directory=LOCAL/'parity';directory.mkdir(parents=True,exist_ok=True)
    token=secrets.token_hex(8);request_path=directory/(token+'.requests.jsonl');output_path=directory/(token+'.outputs.jsonl')
    if fixture_monitor is not None and (os.environ.get('STAGEA_HOST_TEST')!='1' or not getattr(fixture_monitor,'fixture_only',False)):
        raise RuntimeError('explicit fixture-only replay monitor required')
    count=0
    with request_path.open('w') as f:
        for i,row in enumerate(rows):
            check_live()
            request=dict(operation='stageaReplay',frames=[row])
            if i==0:request['weights']=weights
            f.write(json.dumps(request,allow_nan=False,separators=(',',':'))+'\n')
            count+=1
    if not count:raise RuntimeError('empty native replay sequence')
    with request_path.open('r') as src,output_path.open('w') as dst:
        errpath=directory/(token+'.stderr')
        with errpath.open('w') as err:
            child=subprocess.Popen([str(BINARY)],stdin=src,stdout=dst,stderr=err,start_new_session=True,env={**os.environ,'STAGEA_MEMORY_PROFILE':'1'})
            started=time.monotonic()
            try:
                while child.poll() is None:
                    if fixture_monitor is None:check_live(child.pid)
                    else:fixture_monitor.live_memory(child.pid)
                    if time.monotonic()-started>timeout:raise TimeoutError('native sequence replay timeout')
                    time.sleep(.1)
                if child.returncode or errpath.stat().st_size:raise RuntimeError('native parity host failed; inspect local stream/stderr')
            finally:
                if child.poll() is None:__import__('os').killpg(child.pid,9);child.wait()
    out=[];memory=[]
    with output_path.open() as f:
        for line in f:
            check_live()
            result=json.loads(line)
            if result.get('stageAMemory'):
                memory.append(result)
                if fixture_monitor is not None:fixture_monitor.memory_report(result)
                continue
            if 'error' in result or result.get('combat_steps')!=0:raise RuntimeError('bad native replay '+str(result))
            if len(result['outputs'])!=1:raise RuntimeError('stream replay tick count')
            out.append(np.asarray(result['outputs'][0],dtype=np.float64))
    if len(out)!=count or not memory or not memory[-1]['final'] or memory[-1]['tick']!=count:
        raise RuntimeError('incomplete native replay/profile')
    if profile is not None:profile.update(frames=count,peak_rss_bytes=max(r['peak_rss_bytes'] for r in memory),memory_profile=memory)
    request_path.unlink();output_path.unlink();errpath.unlink()
    return out

from owner_approvals import load as approvals
PARITY_RULE = dict(version='certified_near_tie_v1', native_atol=approvals()['parity']['native_atol'],
                   native_categorical_mismatches=approvals()['parity']['native_categorical_mismatches'],
                   float32_bound='min(2 * measured max_abs_error per categorical head, 1e-4)',
                   float32_near_tie_ceiling=approvals()['parity']['float32_near_tie_ceiling'],
                   reference='float64', require_selected_class_deficit=True)
from candidates import MAX_AIM,MAX_MOVE
TAIL=MAX_AIM+MAX_MOVE+64+4
HEADS = (('fire', slice(3,6)), ('target', slice(10,-TAIL)), ('aim_choice',slice(-TAIL,-MAX_MOVE-68)), ('move_choice',slice(-MAX_MOVE-68,-68)), ('aim_family',slice(-68,-36)), ('move_family',slice(-36,-4)))
RECEIPT_DIRECTORY = LOCAL/'parity'/'certified_near_tie_v1'

def compare(a,b,near_ties=False):
    # b is the float64 reference for float32 comparison. Head-wise errors are
    # measured over the entire sequence, before certifying any mismatch.
    if len(a)!=len(b) or any(x.shape!=y.shape or x.ndim!=2 or x.shape[1]<11 for x,y in zip(a,b)):
        raise RuntimeError('parity sequence dimensions')
    if any(not np.isfinite(x).all() or not np.isfinite(y).all() for x,y in zip(a,b)):
        raise RuntimeError('nonfinite parity output')
    result = dict(max_abs_error=max((float(np.max(np.abs(x-y))) if x.size else 0 for x,y in zip(a,b)),default=0),
                  categorical_mismatches=sum(int(np.sum(categories(x)!=categories(y))) for x,y in zip(a,b)),
                  rows=sum(len(x) for x in a))
    if not near_ties:return result
    errors={name:max((float(np.max(np.abs(x[:,part]-y[:,part]))) if x[:,part].size else 0
                     for x,y in zip(a,b)),default=0) for name,part in HEADS}
    details=[]
    for frame,(x,y) in enumerate(zip(a,b)):
        for name,part in HEADS:
            observed=x[:,part];reference=y[:,part]
            choices=observed.argmax(1);expected=reference.argmax(1)
            bound=min(2*errors[name],PARITY_RULE['float32_near_tie_ceiling'])
            for row in np.flatnonzero(choices!=expected):
                logits=reference[row];top=np.sort(logits)[-2:]
                gap=float(top[-1]-top[-2]) if len(top)>1 else 0.
                deficit=float(logits[expected[row]]-logits[choices[row]])
                details.append(dict(frame_index=frame,row_index=int(row),head=name,
                    float32_class=int(choices[row]),float64_class=int(expected[row]),
                    float64_top2_gap=gap,float64_selected_class_deficit=deficit,
                    max_abs_error=errors[name],bound=bound,
                    certified=gap<=bound and deficit<=bound))
    result.update(head_max_abs_error=errors,near_tie_bounds={k:min(2*v,PARITY_RULE['float32_near_tie_ceiling']) for k,v in errors.items()},
                  mismatches=details,uncertified_mismatches=sum(not d['certified'] for d in details))
    return result

def parity_passes(result):
    native=result['native_float64'];export=result['float32_export'];rule=approvals()['parity']
    return (native['categorical_mismatches']==0 and native['max_abs_error']<=rule['native_atol']
            and export['uncertified_mismatches']==0
            and len(export['mismatches'])==export['categorical_mismatches']
            and all(d['certified'] and d['float64_top2_gap']<=min(d['bound'],rule['float32_near_tie_ceiling'])
                    and d['float64_selected_class_deficit']<=min(d['bound'],rule['float32_near_tie_ceiling']) for d in export['mismatches']))

def evaluate(arm,fight,models=None,fixture_monitor=None):
    raw=LOCAL/fight['raw_file']
    if sha(raw)!=fight['raw_sha256']:raise RuntimeError('parity shard drift')
    began=time.monotonic()
    m32,weights,m64=models if models is not None else (*load_model(arm,torch.float32),load_model(arm,torch.float64)[0])
    profile={}
    a=sequence(m32,frames(raw));b=sequence(m64,frames(raw))
    c=replay(weights,frames(raw),timeout=300 if DEADLINE is None else max(1,float(DEADLINE-time.monotonic())),
             profile=profile,fixture_monitor=fixture_monitor)
    result=dict(arm=arm,fight=fight['tag'],raw_sha256=sha(raw),
                float32_export=compare(a,b,near_ties=True),native_float64=compare(b,c),
                seconds=time.monotonic()-began,frames=len(a),native_memory=profile,parity_rule=PARITY_RULE)
    # Report stable unit/time identity without retaining the decoded input bank.
    by_frame={}
    for detail in result['float32_export']['mismatches']:by_frame.setdefault(detail['frame_index'],[]).append(detail)
    if by_frame:
        from data import pack
        for i,row in enumerate(frames(raw)):
            if i in by_frame:
                _,ids,enemies=pack(row,arm)
                for detail in by_frame[i]:
                    detail.update(time=row['t'],unit_id=ids[detail['row_index']])
                    if detail['head']=='target':
                        detail.update(float32_target_id=0 if detail['float32_class']==0 else enemies[detail['float32_class']-1],
                                      float64_target_id=0 if detail['float64_class']==0 else enemies[detail['float64_class']-1])
    result['status']='PASS' if parity_passes(result) else 'FAIL'
    return result

def run():
    global DEADLINE,MONITOR
    environment();from collect import identity
    from parmem_recovery import checked_inference_budget
    checked_inference_budget();index=read(LOCAL/'INDEX.json');records=[];start=time.monotonic()
    from jobs import admitted
    from training_control import training_cap,TrainingDeadline
    cap=training_cap(HERE);run_id=__import__('secrets').token_hex(8)
    manifest=dict(parity_rule=PARITY_RULE,binary=identity(),budget_sha256=sha(LOCAL/'TRAIN_BUDGET.json'),index_sha256=sha(LOCAL/'INDEX.json'),exports={a:sha(LOCAL/'training'/(a+'.weights.json')) for a in ARMS})
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
                proof_path=RECEIPT_DIRECTORY/f"{arm}_{fight['tag']}.receipt.json"
                if proof_path.exists():
                    r=read(proof_path)
                    if r['manifest']!=manifest or r['raw_sha256']!=sha(raw) or r['status']!='PASS' or not parity_passes(r):raise RuntimeError('stored parity receipt drift')
                else:
                    r=evaluate(arm,fight,models[arm]);r['manifest']=manifest
                    write(proof_path,r,exclusive=True)
                    if r['status']!='PASS':raise RuntimeError('categorical/numeric export parity defect')
                records.append(r);rates[arm]=max(rates.get(arm,0),r['seconds']/max(1,r['frames']))
                if i==len(ARMS)-1:
                    remaining=[(a,f) for a,f in jobs[i+1:] if not (RECEIPT_DIRECTORY/f"{a}_{f['tag']}.receipt.json").exists()]
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
