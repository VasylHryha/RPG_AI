"""Export/check trained (or explicitly calibration-only) native weights.

Held-out public sequences include physical tick geometry, death pruning and
recorded actual-launch acknowledgements. No fights or teacher-data changes.
"""
import argparse
import json
import math
import subprocess
import torch
from collection import HERE, ROOT, read, sha, atomic
from stage1_data import frame_rows, admit
from stage1_native import BINARY, admit_driver
from stage1_runtime import Replay
from models import Policy, export


def rpc(value):
    p=subprocess.run([str(BINARY)],input=json.dumps(value,allow_nan=False)+'\n',capture_output=True,text=True,timeout=180)
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
               binary_sha256=sha(BINARY),collection_receipt_sha256=sha(HERE/'COLLECTION_RECEIPT.json'))
    atomic(HERE/'TEACHER_REPEAT_BASELINE.json',value)
    return value


def held_sequences():
    # One whole-sequence prefix per cell/guns/orientation from sealed TEST only.
    rows=[r for r in admit()['rows'] if r['split']=='test']; result=[]
    for row in rows:
        frames=[]; launches=[]
        # Up to90 consecutive physical ticks; this is parity, not model selection.
        for f in frame_rows(ROOT/(row['group']+'.jsonl')):
            if f.get('terminal') or len(frames)>=90:
                break
            frames.append([{**f['joint'],'self':i} for i in f['gun_ids']])
            launches.append([e['unit'] for e in f['events'] if e['stage']=='launch'])
        result.append((row,frames,launches))
    return result


def parity(calibration=False,model_root=None,prefix='STAGE1'):
    from stage1_train import environment,make
    environment(); admit_driver(); results={}; sequence=held_sequences()
    model_root=model_root or HERE/'_local/stage1'
    for kind in ('N1','N1r','N2'):
        if calibration:
            model,_=make(kind)
            output=HERE/'_local/stage1'/('CALIBRATION_'+kind+'.weights.json')
        else:
            ckpt=model_root/(kind+'.pt')
            model=Policy(kind); model.load_state_dict(torch.load(ckpt,weights_only=False)['model'])
            output=model_root/(kind+'.weights.json')
        weights=export(model,output); errors=[]
        with torch.no_grad():
            for row,frames,launches in sequence:
                for ab in (('intact','K0','frozen_phase','topology_only','no_geometry_to_mode','no_mode_to_geometry','no_reset') if kind=='N2' else ('intact',)):
                    native=rpc(dict(operation='stage1_sequence',weights=weights,frames=frames,launches=launches,ablation=ab))
                    python=Replay(model,ab).deployment(frames,launches)
                    errors.append(dict(group=row['group'],ablation=ab,ticks=len(frames),maximum_absolute_error=compare(native,python)))
        results[kind]=dict(export_sha256=sha(output),checks=errors,status='PASS')
    value=dict(status='PASS',scope='initialization exports only; NOT TRAINED' if calibration else 'selected BC exports',
               dtype='float64',atol=1e-9,rtol=1e-9,models=results,driver_sha256=sha(BINARY),physical_fights=0)
    atomic(HERE/('STAGE1_INITIALIZATION_PARITY.json' if calibration else prefix+'_EXPORT_PARITY.json'),value)
    return value


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--initialization-only',action='store_true'); args=p.parse_args()
    print(parity(args.initialization_only)['status'])
