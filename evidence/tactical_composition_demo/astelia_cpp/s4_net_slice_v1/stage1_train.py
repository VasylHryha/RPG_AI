"""Stage-1 BC resource sample, sequential matched-budget fits and diagnostics.

Run only from the pinned _local/mlenv. The sample uses fresh model/optimizer
instances and is discarded: final fits start from the declared seeds. No fights.
"""
import argparse
from collections import Counter
import importlib.metadata
import math
import os
from pathlib import Path
import random
import resource
import sys
import time
import numpy as np
import torch
from models import Policy, export, assert_imitation_optimizer
from losses import losses
from stage1_data import HERE, DATA, HEADS, admit, load, read, sha, atomic,validate_arithmetic
from stage1_runtime import Replay

OUT=HERE/'_local/stage1'
PREFIX='STAGE1'
ROW_WEIGHTS={}
HEAD_MASS={}
STEPS_PER_EPOCH=1
KINDS=('N1','N1r','N2')
SEEDS={'N1':41001,'N1r':41002,'N2':41003}
CONFIG=dict(epochs=10,window_ticks=90,batch_windows=4,learning_rate=.001,
            optimizer='Adam',weight_decay=0,gradient_clip=1,torch_threads=4,
            interop_threads=1,workers=0,seeds=SEEDS,device='cpu',dtype='float64',
            checkpoint='minimum validation weighted masked loss; earliest exact tie',
            history='recorded previous accepted assignments; full chronological prefix under current weights',
            calibration_steps_per_arm=3,training_cap_seconds=3600,peak_rss_cap_bytes=512*1024**2)


def environment():
    if Path(sys.prefix).resolve() != (HERE/'_local/mlenv').resolve():
        raise RuntimeError('use pinned _local/mlenv/bin/python')
    if sys.version.split()[0] != '3.11.15':
        raise RuntimeError('Python pin mismatch')
    for line in (HERE/'requirements.lock').read_text().splitlines():
        if line and not line.startswith('#'):
            name,version=line.split('==')
            if importlib.metadata.version(name)!=version:
                raise RuntimeError('ML distribution pin mismatch: '+name)
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)
    if torch.get_num_interop_threads()!=1:
        raise RuntimeError('interop pin mismatch')


def sources():
    names=sorted({*(p.name for p in HERE.glob('stage1_*') if p.suffix in ('.py','.cpp','.h')),
                  'models.py','losses.py','schema.py','dynamics.py','labels.py','CONTRACT.md','requirements.lock'})
    return {n:sha(HERE/n) for n in names}


def make(kind):
    random.seed(SEEDS[kind]); np.random.seed(SEEDS[kind]); torch.manual_seed(SEEDS[kind])
    model=Policy(kind)
    optimizer=torch.optim.Adam(model.parameters(),lr=CONFIG['learning_rate'],weight_decay=0)
    assert_imitation_optimizer(model,optimizer)
    return model,optimizer


def index(aggregate=None):
    admit()
    value=read(aggregate or DATA/'INDEX.json')
    if value['collection_receipt_sha256'] != sha(HERE/'COLLECTION_RECEIPT.json') or value['source_sha256'] != sha(HERE/'stage1_data.py'):
        raise RuntimeError('converted index provenance mismatch')
    inv={r['group']:r for r in admit()['rows']}
    if aggregate:
        from stage1_jobs import JOBS
        for r,digest in value['round_inventory_sha256'].items():
            p=JOBS/f'dagger_r{r}'/'INVENTORY.json'
            if sha(p)!=digest:
                raise RuntimeError('DAgger aggregate seal drift')
            inv.update({m['group']:m for m in read(p)['rows']})
    for m in value['fights']:
        validate_arithmetic(m)
        if m['split'] not in ('train','validation','test') or inv[m['group']]['split']!=m['split']:
            raise RuntimeError('sealed split mismatch/reporting leakage')
        p=DATA/m['group']
        own={k:v for k,v in m.items() if k not in ('round','visitor','row_weight')}
        if read(p/'META.json')!=own or any(sha(p/(k+'.npy'))!=v for k,v in m['arrays'].items()):
            raise RuntimeError('converted mmap drift')
    return value['fights']


def windows(fights, split='train'):
    result=[]
    for m in fights:
        if m['split']!=split:
            continue
        alive=np.load(DATA/m['group']/'alive.npy',mmap_mode='r')
        rows=0
        for start in range(0,m['ticks'],90):
            end=min(start+90,m['ticks']); count=int(alive[start:end:6].sum())
            if count:
                result.append((m['group'],start,end)); rows+=count
        if rows!=m['counts']['decision_rows']:
            raise RuntimeError('window schedule lost or duplicated decision rows')
    return result


def schedule(fights):
    plan=windows(fights); random.Random(41999).shuffle(plan)
    if not plan:
        raise ValueError('no supervised training windows')
    return [plan[i:i+4] for i in range(0,len(plan),4)]


def fire_stats(fights):
    counts={k:Counter() for k in ('start','release')}
    majority={k:Counter() for k in HEADS}
    for m in fights:
        if m['split']!='train':
            continue
        _,a=load(m['group'])
        for j,k in enumerate(HEADS):
            values=a['labels'][...,j][a['masks'][...,j]]
            majority[k].update(map(int,values))
            if k in counts:
                counts[k].update(map(int,values))
    weights=tuple(min(10.,max(1.,counts[k][0]/max(1,counts[k][1]))) for k in ('start','release'))
    modes={k:min(c,key=lambda v:(-c[v],v)) if c else 0 for k,c in majority.items()}
    return weights,modes,{k:dict(c) for k,c in counts.items()}


def window(model, group, start, end):
    meta,a=load(group); ids0=meta['ids']; replay=Replay(model)
    outputs=[]; labels=[]; masks=[]; legal=[]
    # N1 has no state: the same decision rows/budget, without unnecessary burn-in.
    if model.kind=='N1':
        ds=range((start+5)//6,(end+5)//6)
        for d in ds:
            alive=np.flatnonzero(a['alive'][d*6]); x=torch.tensor(a['x'][d,alive],dtype=torch.float64)
            y,_=model(x); outputs.append(y)
            labels.append(a['labels'][d,alive]); masks.append(a['masks'][d,alive]); legal.append(a['legal'][d,alive])
    else:
        for t in range(end):
            if t==start:
                replay.detach()
            active=np.flatnonzero(a['alive'][t])
            ids=[ids0[g] for g in active]
            if not ids:
                continue
            with torch.set_grad_enabled(torch.is_grad_enabled() and t>=start):
                x=torch.tensor(a['x'][t//6,active],dtype=torch.float64)
                pos=torch.tensor(a['pos'][t,active],dtype=torch.float64)
                y=replay.tick(ids,x,pos,a['targets'][t,active].tolist(),a['assignments'][t,active].tolist(),
                              float(a['dt'][t]),t%6==0,[ids0[g] for g in np.flatnonzero(a['launch'][t])])
                if t>=start and t%6==0:
                    outputs.append(y); labels.append(a['labels'][t//6,active]); masks.append(a['masks'][t//6,active]); legal.append(a['legal'][t//6,active])
    if not outputs:
        return None
    return torch.cat(outputs),np.concatenate(labels),np.concatenate(masks),np.concatenate(legal)


def batch(model, batch_rows, weights):
    pieces=[]; row_weights=[]
    for g,s,e in batch_rows:
        p=window(model,g,s,e)
        if p is not None:
            pieces.append(p); row_weights.extend([ROW_WEIGHTS.get(g,1.)]*len(p[0]))
    if not pieces:
        raise ValueError('empty joint-window batch')
    logits=torch.cat([p[0] for p in pieces])
    label=torch.as_tensor(np.concatenate([p[1] for p in pieces])); mask=torch.as_tensor(np.concatenate([p[2] for p in pieces]))
    support=torch.as_tensor(np.concatenate([p[3] for p in pieces]))
    label={k:label[:,i] for i,k in enumerate(HEADS)}; mask={k:mask[:,i] for i,k in enumerate(HEADS)}
    legal=dict(move=support[:,:33],target=support[:,33:46],aim=support[:,46:])
    # The same contract heads/losses, reduced by gun-row stratum weights.
    from torch.nn import functional as F
    from losses import WEIGHTS
    w=logits.new_tensor(row_weights); total=logits.sum()*0
    for k in HEADS:
        active=mask[k].bool()
        if not bool(active.any()):
            continue
        if k in ('move','target','aim'):
            b,e={'move':(0,33),'target':(33,46),'aim':(48,81)}[k]
            truth=label[k][active].long(); allowed=legal[k][active].bool()
            if not bool(allowed.gather(1,truth[:,None]).all()):
                raise ValueError('unsupported teacher categorical label')
            term=F.cross_entropy(logits[active,b:e].masked_fill(~allowed,-torch.inf),truth,reduction='none')
        else:
            j=0 if k=='start' else 1
            term=F.binary_cross_entropy_with_logits(logits[active,46+j],label[k][active].double(),
                                                    pos_weight=logits.new_tensor(weights[j]),reduction='none')
        # A fixed full-training head mass preserves exact round/visitor balance
        # over an epoch; normalizing each small batch would change that balance.
        total+=WEIGHTS[k]*(term*w[active]).sum()*STEPS_PER_EPOCH/HEAD_MASS[k]
    return total,len(logits)


def step(model,optimizer,rows,weights):
    begin=time.monotonic(); cpu=time.process_time(); optimizer.zero_grad(set_to_none=True)
    loss,count=batch(model,rows,weights)
    if not bool(torch.isfinite(loss)):
        raise FloatingPointError('nonfinite loss; no optimizer update')
    loss.backward()
    if any(p.grad is not None and not bool(torch.isfinite(p.grad).all()) for p in model.parameters()):
        raise FloatingPointError('nonfinite gradient; no optimizer update')
    norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1,error_if_nonfinite=True)
    rss=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024))
    if rss>CONFIG['peak_rss_cap_bytes']:
        raise MemoryError('measured training RSS exceeds declared 512 MiB cap; no optimizer update')
    assert_imitation_optimizer(model,optimizer); optimizer.step(); assert_imitation_optimizer(model,optimizer)
    rhs=0
    if model.kind=='N2':
        for g,s,e in rows:
            _,a=load(g)
            rhs+=sum(4*max(1,math.ceil(float(a['dt'][t])*4/.25)) for t in range(e) if a['alive'][t].any())
    return dict(wall_seconds=time.monotonic()-begin,cpu_seconds=time.process_time()-cpu,
                rss_bytes=rss,loss=float(loss.detach()),gradient_norm=float(norm),decision_rows=count,
                phase_rhs_evaluations=rhs)


def work(rows,kind,lookup):
    if kind=='N1':
        return sum((e-s+5)//6*lookup[g]['guns'] for g,s,e in rows)
    # Forward prefix plus retained forward/backward: conservative, explicit cost proxy.
    return sum((s+3*(e-s))*lookup[g]['guns']**2 for g,s,e in rows)


def evaluate(model,fights,split,weights,modes):
    sums={k:Counter() for k in HEADS}; loss_sums=Counter(); active=Counter()
    with torch.no_grad():
        for meta in fights:
            if meta['split']!=split:
                continue
            _,a=load(meta['group']); replay=Replay(model); ids0=meta['ids']
            for t in range(meta['ticks']):
                gs=np.flatnonzero(a['alive'][t]); ids=[ids0[g] for g in gs]
                if not ids:
                    continue
                x=torch.tensor(a['x'][t//6,gs],dtype=torch.float64)
                pos=torch.tensor(a['pos'][t,gs],dtype=torch.float64)
                if model.kind=='N1' and t%6:
                    continue
                y=replay.tick(ids,x,pos,a['targets'][t,gs].tolist(),a['assignments'][t,gs].tolist(),float(a['dt'][t]),t%6==0,
                              [ids0[g] for g in np.flatnonzero(a['launch'][t])])
                if t%6:
                    continue
                lab=torch.as_tensor(a['labels'][t//6,gs]); mask=torch.as_tensor(a['masks'][t//6,gs]); sup=torch.as_tensor(a['legal'][t//6,gs])
                legal=dict(move=sup[:,:33],target=sup[:,33:46],aim=sup[:,46:])
                _,parts=losses(y,{k:lab[:,i] for i,k in enumerate(HEADS)}, {k:mask[:,i] for i,k in enumerate(HEADS)},legal,weights)
                for j,k in enumerate(HEADS):
                    valid=mask[:,j]; n=int(valid.sum()); w=ROW_WEIGHTS.get(meta['group'],1.)
                    active[k]+=n*w; loss_sums[k]+=float(parts[k])*n*w
                    if not n:
                        continue
                    truth=lab[valid,j]; c=sums[k]; c['active']+=n
                    if k in ('start','release'):
                        pred=y[valid,46 if k=='start' else 47]>=0
                        c['tp']+=int((pred & (truth==1)).sum()); c['fp']+=int((pred & (truth==0)).sum())
                        c['fn']+=int((~pred & (truth==1)).sum()); c['tn']+=int((~pred & (truth==0)).sum())
                    else:
                        b,e={'move':(0,33),'target':(33,46),'aim':(48,81)}[k]
                        pred=y[valid,b:e].masked_fill(~legal[k][valid],-torch.inf).argmax(-1)
                        c['correct']+=int((pred==truth).sum())
                        c['majority_correct']+=int((truth==modes[k]).sum())
                        baseline=1 if k=='target' else 0
                        c['baseline_correct']+=int((truth==baseline).sum())
                        if k in ('move','aim'):
                            offsets=np.asarray(a['offsets'][t//6,gs,0 if k=='move' else 1])[valid.numpy()]
                            truth_points=offsets[np.arange(n),truth.numpy()]
                            c['error_px_sum']+=float(np.linalg.norm(offsets[np.arange(n),pred.numpy()]-truth_points,axis=1).sum())
                            c['zero_error_px_sum']+=float(np.linalg.norm(offsets[:,0]-truth_points,axis=1).sum())
    from losses import WEIGHTS
    result={}
    for k in HEADS:
        c=sums[k]; n=c['active']; loss=loss_sums[k]/active[k] if active[k] else None
        if k in ('start','release'):
            positive=c['tp']+c['fn']; negative=c['tn']+c['fp']
            result[k]=dict(counts=dict(c),loss=loss,
                           precision=c['tp']/(c['tp']+c['fp']) if c['tp']+c['fp'] else None,
                           recall=c['tp']/positive if positive else None,
                           missed_readiness=c['fn']/positive if positive else None,
                           baselines=dict(hold=dict(precision=None,recall=0 if positive else None,missed_readiness=1 if positive else None),
                                          permit=dict(precision=positive/n if n else None,recall=1 if positive else None,missed_readiness=0 if positive else None)))
        else:
            result[k]=dict(counts=dict(c),loss=loss,top1=c['correct']/n if n else None,
                           majority_top1=c['majority_correct']/n if n else None,
                           baseline=('nearest-target' if k=='target' else 'zero-offset'),baseline_top1=c['baseline_correct']/n if n else None)
            if k in ('move','aim'):
                result[k].update(mean_error_px=c['error_px_sum']/n if n else None,zero_offset_error_px=c['zero_error_px_sum']/n if n else None)
    objective=sum(WEIGHTS[k]*loss_sums[k]/active[k] for k in HEADS if active[k])
    baseline=read(HERE/'TEACHER_REPEAT_BASELINE.json')
    return dict(split=split,weighted_masked_loss=objective,heads=result,
                target_repeat_consistency=baseline['heads']['target'],target_repeat_baseline_scope=baseline['scope'],
                teacher_repeat_baseline_sha256=sha(HERE/'TEACHER_REPEAT_BASELINE.json'))


def run(run_if_admitted=False,aggregate=None):
    global OUT,PREFIX,ROW_WEIGHTS,HEAD_MASS,STEPS_PER_EPOCH
    environment(); fights=index(aggregate); plan=schedule(fights); lookup={m['group']:m for m in fights}
    if aggregate:
        r=read(aggregate)['round']; OUT=HERE/f'_local/stage1/dagger_r{r}'; PREFIX=f'DAGGER_R{r}'
    OUT.mkdir(parents=True,exist_ok=True)
    ROW_WEIGHTS={m['group']:m.get('row_weight',1.) for m in fights}
    HEAD_MASS={k:sum(m['counts'].get(k+'_active',0)*ROW_WEIGHTS[m['group']] for m in fights if m['split']=='train') for k in HEADS}
    STEPS_PER_EPOCH=len(plan)
    weights,modes,counts=fire_stats(fights); pins=sources()
    declared_rows=sum(m['counts']['decision_rows'] for m in fights if m['split']=='train')
    budget=dict(**CONFIG,steps_per_epoch=len(plan),gradient_steps_per_arm=10*len(plan),decision_rows_per_arm=10*declared_rows,
                training_only_fire_weights=weights,fire_counts=counts,majority_modes=modes,
                dataset_index_sha256=sha(aggregate or DATA/'INDEX.json'),sources=pins)
    budget_path=HERE/(PREFIX+'_BUDGET.json'); atomic(budget_path,budget)
    old=HERE/('TRAINING_PROJECTION.json' if not aggregate else PREFIX+'_PROJECTION.json')
    if old.exists():
        raise RuntimeError('calibration already recorded; no automatic repeated sample')
    sampled={}; begin=time.monotonic()
    # Same three full batches for every arm, spanning early/middle/late prefixes.
    ordered=sorted(plan,key=lambda rows:work(rows,'N2',lookup))
    selected=[ordered[min(len(ordered)-1,int((len(ordered)-1)*q))] for q in (.1,.5,.9)]
    try:
        for kind in KINDS:
            model,optimizer=make(kind); stats=[]
            sampled[kind]=stats
            for rows in selected:
                value=step(model,optimizer,rows,weights); value['windows']=rows; value['work_units']=work(rows,kind,lookup)
                stats.append(value)
                print(kind,'sample',len(stats),round(value['wall_seconds'],3),'s',flush=True)
            sampled[kind]=stats
            del optimizer,model
    except (MemoryError,FloatingPointError,ValueError) as error:
        atomic(old,dict(status='REFUSED_SAMPLE',reason=str(error),samples=sampled,budget_sha256=sha(budget_path),
                        wall_seconds=time.monotonic()-begin,training_run=False))
        raise
    projections={}
    for kind,stats in sampled.items():
        rate=max(s['wall_seconds']/s['work_units'] for s in stats)
        train_work=10*sum(work(rows,kind,lookup) for rows in plan)
        eval_work=sum(m['ticks']*(m['guns']**2 if kind!='N1' else m['guns']/6)*(10 if m['split']=='validation' else 1)
                      for m in fights if m['split'] in ('validation','test'))
        projections[kind]=dict(training_seconds=rate*train_work,diagnostics_seconds=rate*eval_work,
                               total_seconds=rate*(train_work+eval_work),seconds_per_work_unit=rate)
    total=sum(p['total_seconds'] for p in projections.values())
    projection=dict(status='ADMITTED' if total<3600 else 'OVER_60_MINUTES',
                    total_projected_seconds=total,total_projected_minutes=total/60,
                    method='maximum measured seconds/work unit across same early/middle/late batches; 10 epochs + 10 validation passes + test; no parallel fits',
                    samples=sampled,per_arm=projections,budget_sha256=sha(budget_path),training_run=False,
                    sample_wall_seconds=time.monotonic()-begin,cap_seconds=3600)
    atomic(old,projection); print('Projected three fits + diagnostics:',round(total/60,2),'minutes',flush=True)
    if total>=3600 or not run_if_admitted:
        return projection
    deadline=time.monotonic()+3600; outcomes={}
    for kind in KINDS:
        model,optimizer=make(kind); best=math.inf; best_epoch=None; history=[]; rows_seen=0; fit_start=time.monotonic(); fit_cpu=time.process_time()
        resources=Counter(); peak=0
        for epoch in range(10):
            with (OUT/(kind+'.steps.jsonl')).open('a') as log:
                for step_id,rows in enumerate(plan):
                    if time.monotonic()>=deadline:
                        raise TimeoutError('training wall cap; partial checkpoints preserved')
                    measured=step(model,optimizer,rows,weights); rows_seen+=measured['decision_rows']
                    import json
                    log.write(json.dumps(dict(epoch=epoch+1,step=step_id,windows=rows,**measured),allow_nan=False)+'\n'); log.flush()
                    peak=max(peak,measured['rss_bytes'])
                    for k in ('wall_seconds','cpu_seconds','phase_rhs_evaluations'):
                        resources[k]+=measured[k]
            diagnostic=evaluate(model,fights,'validation',weights,modes)
            value=diagnostic['weighted_masked_loss']; history.append(dict(epoch=epoch+1,validation=value))
            if value<best:
                best=value; best_epoch=epoch+1
                torch.save(dict(kind=kind,model=model.state_dict(),epoch=best_epoch,seed=SEEDS[kind],budget=budget),OUT/(kind+'.pt'))
            print(kind,'epoch',epoch+1,'validation',value,flush=True)
        if rows_seen!=budget['decision_rows_per_arm']:
            raise RuntimeError('unequal decision-row budget')
        model.load_state_dict(torch.load(OUT/(kind+'.pt'),weights_only=False)['model'])
        export(model,OUT/(kind+'.weights.json'))
        test_diagnostic=evaluate(model,fights,'test',weights,modes)
        validation_diagnostic=evaluate(model,fights,'validation',weights,modes)
        outcomes[kind]=dict(checkpoint_epoch=best_epoch,history=history,gradient_steps=10*len(plan),decision_rows=rows_seen,
                             resources={**resources,'peak_rss_bytes':peak,'checkpoint_bytes':(OUT/(kind+'.pt')).stat().st_size,
                                        'export_bytes':(OUT/(kind+'.weights.json')).stat().st_size},
                             wall_seconds=time.monotonic()-fit_start,cpu_seconds=time.process_time()-fit_cpu,checkpoint_sha256=sha(OUT/(kind+'.pt')),
                             export_sha256=sha(OUT/(kind+'.weights.json')),test=test_diagnostic,validation=validation_diagnostic)
        del optimizer,model
    from stage1_export import parity
    export_parity=parity(model_root=OUT,prefix=PREFIX)
    result=dict(status='TRAINED_BC',models=outcomes,export_parity=export_parity,
                budget_sha256=sha(budget_path),sources=pins,physical_fights=0,dagger_run=bool(aggregate),mechanism_run=False)
    atomic(HERE/(PREFIX+'_RESULTS.json'),result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--run-if-admitted',action='store_true'); p.add_argument('--aggregate',type=Path); a=p.parse_args()
    from stage1_jobs import job_lock
    with job_lock('training'):
        run(a.run_if_admitted,a.aggregate)
