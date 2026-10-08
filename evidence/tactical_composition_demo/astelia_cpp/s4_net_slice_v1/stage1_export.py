"""Export/check trained (or explicitly calibration-only) native weights.

Held-out public sequences include physical tick geometry, death pruning and
recorded actual-launch acknowledgements. No fights or teacher-data changes.
"""
import argparse
import json
import math
import time
import subprocess
import torch
from collection_v2 import HERE, ROOT, read, sha, atomic
from stage1_data_v2 import frame_rows, admit
from stage1_native import BINARY, admit_driver
from stage1_runtime import Replay
from models import Policy, export


def rpc(value,deadline=None):
    remaining=180 if deadline is None else min(180,deadline-time.monotonic())
    if remaining<=0:
        raise TimeoutError('parity wall cap')
    p=subprocess.run([str(BINARY)],input=json.dumps(value,allow_nan=False)+'\n',capture_output=True,text=True,timeout=remaining)
    if p.returncode:
        raise RuntimeError('native parity RPC failed: '+p.stderr)
    return json.loads(p.stdout)


def compare(native,python,path='root'):
    maximum=0.
    if isinstance(python,dict):
        if native.keys()!=python.keys():
            raise AssertionError(path+' keys')
        for k in python:
            maximum=max(maximum,compare(native[k],python[k],path+'.'+k))
    elif isinstance(python,list):
        if len(native)!=len(python):
            raise AssertionError(path+' length')
        for i,(a,b) in enumerate(zip(native,python)):
            maximum=max(maximum,compare(a,b,path+f'[{i}]'))
    elif isinstance(python,(int,float)) and not isinstance(python,bool):
        if isinstance(native,bool) or not isinstance(native,(int,float)) or not math.isfinite(native) or not math.isfinite(python):
            raise AssertionError(path+' nonfinite or nonnumeric parity value')
        error=abs(native-python)
        if error>1e-9+1e-9*abs(python):
            raise AssertionError(path+f': {native} vs {python}')
        maximum=error
    elif native!=python:
        raise AssertionError(path+f': {native} vs {python}')
    return maximum


def teacher_baseline():
    """Measured repeat/collected-label agreement on six held-out joint decisions."""
    from stage1_data import decision,HEADS
    rows=admit()['rows']; selected=[]
    for cell,guns in (('D1-static',1),('D2-shellfire',2),('D2-shellfire',10)):
        selected.append(next(r for r in rows if r['split']=='test' and r['cell']==cell and r['guns']==guns))
    counts={k:dict(active=0,repeat_correct=0,collected_correct=0) for k in HEADS}; keys=[]
    for row in selected:
        for frame in frame_rows(ROOT/(row['group']+'.jsonl')):
            if frame.get('terminal') or frame['tick']>7:
                break
            if frame['tick'] not in (1,7):
                continue
            snapshots=[{**frame['joint'],'self':i} for i in frame['gun_ids']]
            first=rpc(dict(operation='teacher',snapshots=snapshots)); second=rpc(dict(operation='teacher',snapshots=snapshots))
            repeated={v['id']:v['action'] for v in second['actions']}
            original={e['unit']:e['value'] for e in frame['events'] if e['stage']=='intent'}
            for result in first['actions']:
                id=result['id']; s=next(s for s in snapshots if s['self']==id)
                truth,mask,_,_=decision(s,original[id]); actual=decision(s,result['action'])[0]; other=decision(s,repeated[id])[0]
                for i,k in enumerate(HEADS):
                    if mask[i]:
                        counts[k]['active']+=1; counts[k]['repeat_correct']+=int(actual[i]==other[i]); counts[k]['collected_correct']+=int(actual[i]==truth[i])
                compare(result['action'],original[id]); compare(result['action'],repeated[id])
            keys.append(dict(group=row['group'],tick=frame['tick'],guns=len(snapshots)))
    value=dict(status='PASS',scope='six same-state held-out TEST joint decisions; no fights, no fitting',keys=keys,
               heads={k:{**v,'repeat_agreement':v['repeat_correct']/v['active'] if v['active'] else None,
                         'collected_agreement':v['collected_correct']/v['active'] if v['active'] else None} for k,v in counts.items()},
               binary_sha256=sha(BINARY),collection_receipt_sha256=sha(HERE/'COLLECTION_RECEIPT_V2.json'))
    atomic(HERE/'TEACHER_REPEAT_BASELINE_V2.json',value)
    return value


def sequence(row):
    frames=[]; launches=[]
    for f in frame_rows(ROOT/(row['group']+'.jsonl')):
        if f.get('terminal'):
            break
        frames.append([{**f['joint'],'self':i} for i in f['gun_ids']])
        launches.append([e['unit'] for e in f['events'] if e['stage']=='launch'])
    return frames,launches


def held_sequences():
    # Stream one complete sealed test fight at a time; no prefix cutoff.
    for row in admit()['rows']:
        if row['split']=='test':
            frames,launches=sequence(row)
            yield row,frames,launches


def stream_compare(row,model,weights,ablation,deadline=None):
    from stage1_stream import Session,CHUNK
    from stage1_train import check_rss
    replay=Replay(model,ablation); chunks=[]; ticks=launches=deaths=0; previous=set(); maximum=0.
    start=time.monotonic(); session=Session(weights,ablation,deadline)
    def consume(chunk):
        nonlocal ticks,launches,deaths,maximum,previous
        wires=[dict(joint=f['joint'],ids=f['gun_ids'],launches=[e['unit'] for e in f['events'] if e['stage']=='launch']) for f in chunk]
        native=session.call(dict(operation='stage1_stream_frames',frames=wires))
        snapshots=[[{**w['joint'],'self':i} for i in w['ids']] for w in wires]
        with torch.no_grad():
            expected=replay.deployment(snapshots,[w['launches'] for w in wires],start_tick=ticks,deadline=deadline)
        maximum=max(maximum,compare(native,expected))
        for w in wires:
            current=set(w['ids']); deaths+=len(previous-current); previous=current
            launches+=len(w['launches'])
        ticks+=len(chunk); check_rss()
    try:
        for frame in frame_rows(ROOT/(row['group']+'.jsonl')):
            if frame.get('terminal'):
                break
            chunks.append(frame)
            if len(chunks)==CHUNK:
                consume(chunks); chunks=[]
        if chunks:
            consume(chunks)
        resources=session.close()
    except Exception:
        session.close(kill=True)
        raise
    return dict(group=row['group'],ablation=ablation,ticks=ticks,launches=launches,deaths=deaths,
                maximum_absolute_error=maximum,wall_seconds=time.monotonic()-start,native_resources=resources,
                chunk_ticks=CHUNK,scope='complete sequence; persistent Host and Python Replay state across bounded chunks')


def sample_parity_timing(model,deadline,model_root=None,attempt=3):
    from stage1_native_v2 import admit_driver
    admit_driver()
    output=(model_root or HERE/'_local/stage1_v2')/(f'TIMING_{attempt:02}_'+model.kind+'.weights.json')
    weights=export(model,output)
    admission_start=time.monotonic()
    rows=[r for r in admit()['rows'] if r['split']=='test']
    admission_seconds=time.monotonic()-admission_start
    rates={}; checks=[]
    for guns in (1,2,10):
        subset=[r for r in rows if r['guns']==guns]
        row=max(subset,key=lambda r:read(ROOT/(r['group']+'.receipt.json'))['record_count'])
        arm_rates=[]
        for ab in (('intact','K0','frozen_phase','topology_only','no_geometry_to_mode','no_mode_to_geometry','no_reset') if model.kind=='N2' else ('intact',)):
            if time.monotonic()>=deadline:
                raise TimeoutError('sample time cap during parity timing')
            check=stream_compare(row,model,weights,ab,deadline)
            arm_rates.append(check['wall_seconds']/max(1,check['ticks'])); checks.append(check)
        rates[guns]=max(arm_rates)
    count=7 if model.kind=='N2' else 1
    projected=admission_seconds+count*sum(read(ROOT/(r['group']+'.receipt.json'))['record_count']*rates[r['guns']] for r in rows)
    return dict(projected_seconds=projected,admission_seconds=admission_seconds,seconds_per_tick_by_guns=rates,checks=checks,
                scope='discarded nine-step sample model; longest held-out fight per gun count; not trained parity')


def parity(calibration=False,model_root=None,prefix='STAGE1_V2',deadline=None):
    from stage1_train import environment,make
    from stage1_native_v2 import BINARY as stream_binary,admit_driver as admit_stream
    environment(); admit_stream(); results={}
    model_root=model_root or HERE/'_local/stage1_v2'
    for name,kind in [('N1','N1'),('N1_seed41101','N1'),('N1_seed41201','N1'),('N1r','N1r'),('N2','N2')]:
        if calibration:
            seed=int(name.split('seed')[1]) if 'seed' in name else None
            model,_=make(kind,seed)
            output=HERE/'_local/stage1_v2'/('CALIBRATION_'+name+'.weights.json')
        else:
            model=Policy(kind); model.load_state_dict(torch.load(model_root/(name+'.pt'),weights_only=False)['model'])
            output=model_root/(name+'.weights.json')
        weights=export(model,output); errors=[]
        for row in admit()['rows']:
            if row['split']!='test':
                continue
            for ab in (('intact','K0','frozen_phase','topology_only','no_geometry_to_mode','no_mode_to_geometry','no_reset') if kind=='N2' else ('intact',)):
                errors.append(stream_compare(row,model,weights,ab,deadline))
        results[name]=dict(export_sha256=sha(output),checks=errors,status='PASS')
    value=dict(status='PASS',scope='initialization exports only; NOT TRAINED' if calibration else 'selected exports: complete test sequences with supplied launch acknowledgements; actual Host-path parity additionally required on student logs',
               dtype='float64',atol=1e-9,rtol=1e-9,models=results,driver_sha256=sha(stream_binary),physical_fights=0)
    result_path=HERE/('STAGE1_V2_INITIALIZATION_PARITY.json' if calibration else prefix+'_EXPORT_PARITY.json')
    if result_path.exists():
        raise RuntimeError('preserve existing parity evidence; no overwrite')
    atomic(result_path,value)
    return value


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--initialization-only',action='store_true'); args=p.parse_args()
    print(parity(args.initialization_only)['status'])
