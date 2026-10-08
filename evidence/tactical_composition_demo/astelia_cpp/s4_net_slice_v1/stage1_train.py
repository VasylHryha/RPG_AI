"""Stage-1 BC resource sample, stored-state matched-budget fits and diagnostics.

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
from stage1_data_v2 import HERE, DATA, HEADS, admit, load as data_load, read, sha, atomic,validate_arithmetic
from stage1_stored import StoredStates,PreparedFight,BURN_IN
from functools import lru_cache
from stage1_runtime import Replay

OUT=HERE/'_local/stage1_v2'
PREFIX='STAGE1_V2'
ROW_WEIGHTS={}
HEAD_MASS={}
STEPS_PER_EPOCH=1
STORED=None
N1_SEEDS=(41001,41101,41201)
GEOMETRY_ROOT=HERE/'_local/stage1_v2/prepared'
KINDS=('N1','N1r','N2')
SEEDS={'N1':41001,'N1r':41002,'N2':41003}
CONFIG=dict(epochs=10,window_ticks=90,batch_windows=4,learning_rate=.001,
            optimizer='Adam',weight_decay=0,gradient_clip=1,torch_threads=2,
            interop_threads=1,workers=0,seeds=SEEDS,device='cpu',dtype='float64',
            checkpoint='minimum validation weighted masked loss; earliest exact tie',
            history='R2D2 stored-state epoch refresh, 30-tick current-weight burn-in, 90-tick TBPTT',
            burn_in_ticks=BURN_IN,refresh='one chronological training-fight pass each epoch; state stale at most one epoch',
            epoch_shuffle_seed=41999,n1_seeds=N1_SEEDS,concurrent_fits=False,
            calibration_steps_per_arm=3,training_cap_seconds=3600,peak_rss_cap_bytes=512*1024**2)


def check_rss():
    rss=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024))
    if rss>CONFIG['peak_rss_cap_bytes']:
        raise MemoryError('measured process RSS exceeds 512 MiB cap')
    return rss


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
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    if torch.get_num_interop_threads()!=1:
        raise RuntimeError('interop pin mismatch')


def sources():
    names=sorted({*(p.name for p in HERE.glob('stage1_*') if p.suffix in ('.py','.cpp','.h')),
                  'models.py','losses.py','schema.py','dynamics.py','labels.py','CONTRACT.md','requirements.lock',
                  'requests_v2.py','collection_v2.py','CONTRACT_AMENDMENT_STAGE1_V2.md'})
    return {n:sha(HERE/n) for n in names}


def make(kind,seed=None):
    seed=SEEDS[kind] if seed is None else seed
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    model=Policy(kind)
    optimizer=torch.optim.Adam(model.parameters(),lr=CONFIG['learning_rate'],weight_decay=0)
    assert_imitation_optimizer(model,optimizer)
    return model,optimizer


def index(aggregate=None):
    admit()
    value=read(aggregate or DATA/'INDEX.json')
    if value['collection_receipt_sha256'] != sha(HERE/'COLLECTION_RECEIPT_V2.json') or value['source_sha256'] != sha(HERE/'stage1_data_v2.py'):
        raise RuntimeError('converted index provenance mismatch')
    if not aggregate and (value.get('version')!='NS1-conversion-2' or value.get('dedupe_sha256')!=sha(DATA/'DEDUPE.json') or read(DATA/'DEDUPE.json')['status']!='PASS'):
        raise RuntimeError('v2 deduplicated index required')
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


def schedule(fights,epoch=0):
    plan=windows(fights); random.Random(41999+epoch).shuffle(plan)
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
    weights=tuple((min(10.,max(1.,counts[k][1]/max(1,counts[k][0]))),
                   min(10.,max(1.,counts[k][0]/max(1,counts[k][1])))) for k in ('start','release'))
    modes={k:min(c,key=lambda v:(-c[v],v)) if c else 0 for k,c in majority.items()}
    return weights,modes,{k:dict(c) for k,c in counts.items()}


def load(group):
    return data_load(group,root=DATA)


@lru_cache(maxsize=4)
def prepare(group):
    return PreparedFight(*load(group),geometry_root=GEOMETRY_ROOT)


def window(model, group, start, end):
    meta,a=load(group)
    outputs=[]; labels=[]; masks=[]; legal=[]
    if model.kind=='N1':
        for d in range((start+5)//6,(end+5)//6):
            alive=np.flatnonzero(a['alive'][d*6]); x=torch.tensor(a['x'][d,alive],dtype=torch.float64)
            y,_=model(x); outputs.append(y)
            labels.append(a['labels'][d,alive]); masks.append(a['masks'][d,alive]); legal.append(a['legal'][d,alive])
    else:
        if STORED is None:
            raise RuntimeError('recurrent training requires epoch-refreshed stored states')
        f=prepare(group); replay=STORED.start(model,f,start)
        for t in range(start,end):
            y=f.tick(replay,t,emit=t%6==0)
            if y is not None and t%6==0:
                active=f.active[t]
                outputs.append(y); labels.append(a['labels'][t//6,active]); masks.append(a['masks'][t//6,active]); legal.append(a['legal'][t//6,active])
    if not outputs:
        return None
    return torch.cat(outputs),np.concatenate(labels),np.concatenate(masks),np.concatenate(legal)


def fire_loss(logit,truth,weights,reduction='none'):
    from torch.nn import functional as F
    # Legacy scalar accepted for isolated fixture callers; new fits declare both.
    negative,positive=weights if isinstance(weights,(tuple,list)) else (1.,weights)
    term=F.binary_cross_entropy_with_logits(logit,truth.to(logit.dtype),reduction='none')
    term=term*torch.where(truth.bool(),logit.new_tensor(positive),logit.new_tensor(negative))
    return term.mean() if reduction=='mean' else term


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
            term=fire_loss(logits[active,46+j],label[k][active],weights[j])
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
            rhs+=sum(4*max(1,math.ceil(float(a['dt'][t])*4/.25)) for t in range(max(0,s-BURN_IN),e) if a['alive'][t].any())
    return dict(wall_seconds=time.monotonic()-begin,cpu_seconds=time.process_time()-cpu,
                rss_bytes=rss,loss=float(loss.detach()),gradient_norm=float(norm),decision_rows=count,
                phase_rhs_evaluations=rhs)


def work(rows,kind,lookup):
    if kind=='N1':
        return sum((e-s+5)//6*lookup[g]['guns'] for g,s,e in rows)
    # Short no-grad burn-in plus retained forward/backward; refresh measured separately.
    return sum((min(s,BURN_IN)+3*(e-s))*lookup[g]['guns']**2 for g,s,e in rows)


def evaluate(model,fights,split,weights,modes,deadline=None):
    sums={k:Counter() for k in HEADS}; loss_sums=Counter(); active=Counter()
    with torch.no_grad():
        for meta in fights:
            if meta['split']!=split:
                continue
            _,a=load(meta['group']); ids0=meta['ids']
            f=prepare(meta['group']) if model.kind!='N1' else None
            from stage1_stored import TensorReplay
            replay=TensorReplay(model,meta['guns']) if f is not None else None
            for t in range(meta['ticks']):
                if deadline is not None and time.monotonic()>=deadline:
                    raise TimeoutError('training/sample cap during diagnostics')
                if t%90==0:
                    check_rss()
                gs=np.flatnonzero(a['alive'][t]); ids=[ids0[g] for g in gs]
                if not ids:
                    continue
                if model.kind=='N1':
                    if t%6:
                        continue
                    y,_=model(torch.tensor(a['x'][t//6,gs],dtype=torch.float64))
                else:
                    y=f.tick(replay,t,emit=t%6==0)
                if t%6:
                    continue
                lab=torch.as_tensor(a['labels'][t//6,gs]); mask=torch.as_tensor(a['masks'][t//6,gs]); sup=torch.as_tensor(a['legal'][t//6,gs])
                legal=dict(move=sup[:,:33],target=sup[:,33:46],aim=sup[:,46:])
                _,parts=losses(y,{k:lab[:,i] for i,k in enumerate(HEADS)}, {k:mask[:,i] for i,k in enumerate(HEADS)},legal,(1.,1.))
                for j,k in enumerate(('start','release')):
                    valid=mask[:,2+j]
                    parts[k]=fire_loss(y[valid,46+j],lab[valid,2+j],weights[j],reduction='mean') if bool(valid.any()) else y.sum()*0
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
                        c['nonzero_active']+=int((truth!=0).sum()); c['nonzero_correct']+=int(((truth!=0)&(pred==truth)).sum())
                        for cls in truth.unique().tolist():
                            c['class_'+str(cls)+'_active']+=int((truth==cls).sum())
                            c['class_'+str(cls)+'_correct']+=int(((truth==cls)&(pred==truth)).sum())
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
                           hold_when_ready_recall=c['tn']/negative if negative else None,
                           balanced_accuracy=(c['tp']/positive+c['tn']/negative)/2 if positive and negative else None,
                           baselines=dict(hold=dict(precision=None,recall=0 if positive else None,missed_readiness=1 if positive else None),
                                          permit=dict(precision=positive/n if n else None,recall=1 if positive else None,missed_readiness=0 if positive else None)))
        else:
            result[k]=dict(counts=dict(c),loss=loss,top1=c['correct']/n if n else None,
                           majority_top1=c['majority_correct']/n if n else None,
                           metric_condition='teacher-target-conditioned aim top-1' if k=='aim' else 'public supported categorical top-1',
                           nonzero_top1=c['nonzero_correct']/c['nonzero_active'] if c['nonzero_active'] else None,
                           balanced_accuracy=sum(c['class_'+str(i)+'_correct']/c['class_'+str(i)+'_active'] for i in range(46) if c['class_'+str(i)+'_active'])/sum(c['class_'+str(i)+'_active']>0 for i in range(46)) if n else None,
                           baseline=('nearest-target' if k=='target' else 'zero-offset'),baseline_top1=c['baseline_correct']/n if n else None)
            if k in ('move','aim'):
                result[k].update(mean_error_px=c['error_px_sum']/n if n else None,zero_offset_error_px=c['zero_error_px_sum']/n if n else None)
    objective=sum(WEIGHTS[k]*loss_sums[k]/active[k] for k in HEADS if active[k])
    return dict(split=split,weighted_masked_loss=objective,heads=result,
                target_repeat_consistency=None,target_repeat_baseline_scope='legacy duplicate-data baseline not applicable to v2')


def law_statistics(model,fights,deadline=None):
    if model.kind!='N2':
        return None
    from stage1_stored import TensorReplay
    force=[]; velocity=[]; order=[]
    with torch.no_grad():
        for m in fights:
            if m['split']!='validation':
                continue
            f=prepare(m['group']); replay=TensorReplay(model,m['guns'])
            for t in range(m['ticks']):
                if deadline is not None and time.monotonic()>=deadline:
                    raise TimeoutError('training/sample cap during law diagnostics')
                if t%90==0:
                    check_rss()
                gs=f.active[t]
                if not gs:
                    continue
                before=(replay.phase[gs].clone() if replay.phase is not None else
                        f.pos.new_tensor([(i%16)*math.pi/8 for i in f.ids[t]]))
                f.tick(replay,t,False)
                # Launch reset is an event, not phase velocity. Recover the RK4
                # pre-reset result for launched slots with the same law/context.
                after=replay.phase[gs]
                launched=[g in f.launches[t] for g in gs]
                if any(launched):
                    from stage1_runtime import n2_tick
                    _,after=n2_tick(model,replay.held[gs],f.pos[t,gs],f.ids[t],before,f.targets[t,gs],replay.assign[gs],float(f.arrays['dt'][t]),held_force=replay.force[gs],geometry=f.geometry(t,gs),emit_logits=False)
                force.extend(replay.force[gs].abs().tolist())
                velocity.extend(((after-before)/float(f.arrays['dt'][t])).tolist())
                order.append(float(torch.abs(torch.exp(1j*after).mean())))
    def distribution(values):
        return dict(count=len(values),quantiles=np.quantile(values,[0,.1,.5,.9,1]).tolist(),mean=float(np.mean(values))) if values else dict(count=0,quantiles=None,mean=None)
    return dict(K=float(model.law[3].sigmoid()*2),omega=float(model.law[4].tanh()*2),
                omega_scope='single shared scalar; individual variation from observation forcing',
                absolute_forcing=distribution(force),phase_velocity_rad_per_second=distribution(velocity),
                phase_order_parameter=distribution(order),phase_dispersion=distribution([1-v for v in order]),
                motion_prior='fixed J=0.5; A/B/J/share untrained by BC',replicate_unit='fight; ticks are diagnostic samples')



def run(run_if_admitted=False,aggregate=None):
    global OUT,PREFIX,ROW_WEIGHTS,HEAD_MASS,STEPS_PER_EPOCH,STORED
    if aggregate:
        r=read(aggregate)['round']; OUT=HERE/f'_local/stage1_v2/dagger_r{r}'; PREFIX=f'DAGGER_V2_R{r}'
    projection_path=HERE/('TRAINING_PROJECTION_02.json' if not aggregate else PREFIX+'_PROJECTION_02.json')
    budget_path=HERE/('STAGE1_BUDGET_02.json' if not aggregate else PREFIX+'_BUDGET_02.json')
    # Refuse before any write, expensive read/preparation or sample.
    if projection_path.exists() or budget_path.exists():
        raise RuntimeError('attempt 02 already recorded or interrupted; preserve receipts, no automatic repeated sample')
    environment(); fights=index(aggregate); plan=schedule(fights); lookup={m['group']:m for m in fights}
    OUT.mkdir(parents=True,exist_ok=True)
    ROW_WEIGHTS={m['group']:m.get('row_weight',1.) for m in fights}
    HEAD_MASS={k:sum(m['counts'].get(k+'_active',0)*ROW_WEIGHTS[m['group']] for m in fights if m['split']=='train') for k in HEADS}
    STEPS_PER_EPOCH=len(plan)
    weights,modes,counts=fire_stats(fights); pins=sources()
    declared_rows=sum(m['counts']['decision_rows'] for m in fights if m['split']=='train')
    budget=dict(**CONFIG,attempt=2,steps_per_epoch=len(plan),gradient_steps_per_arm=10*len(plan),decision_rows_per_arm=10*declared_rows,
                training_only_fire_class_weights=weights,fire_counts=counts,majority_modes=modes,
                dataset_index_sha256=sha(aggregate or DATA/'INDEX.json'),sources=pins)
    atomic(budget_path,budget)
    begin=time.monotonic(); sample_deadline=begin+3600; sampled={}; refresh={}; diagnostics={}; parity_timing={}
    # Preserve original early/middle/late-prefix nine-step sample selection.
    ordered=sorted(plan,key=lambda rows:sum((s+3*(e-s))*lookup[g]['guns']**2 for g,s,e in rows))
    selected=[ordered[min(len(ordered)-1,int((len(ordered)-1)*q))] for q in (.1,.5,.9)]
    try:
        prep_begin=time.monotonic()
        for m in fights:
            if m['split'] in ('train','validation','test'):
                if time.monotonic()>=sample_deadline:
                    raise TimeoutError('sample time cap during preprocessing')
                prepare(m['group']); check_rss()
        preparation_seconds=time.monotonic()-prep_begin
        for kind in KINDS:
            model,optimizer=make(kind); stats=[]; sampled[kind]=stats
            STORED=StoredStates() if kind!='N1' else None
            cpu=time.process_time()
            refresh[kind]=dict(wall_seconds=STORED.refresh(model,windows(fights),prepare,sample_deadline) if STORED else 0.)
            refresh[kind]['cpu_seconds']=time.process_time()-cpu
            for rows in selected:
                if time.monotonic()>=sample_deadline:
                    raise TimeoutError('sample wall cap')
                value=step(model,optimizer,rows,weights); value['windows']=rows; value['work_units']=work(rows,kind,lookup)
                stats.append(value)
                print(kind,'sample',len(stats),round(value['wall_seconds'],3),'s',flush=True)
            # Offline chronological diagnostics and parity timing have zero
            # optimizer steps and launch no physical fights.
            timings={}
            for split in ('validation','test'):
                start=time.monotonic(); evaluate(model,fights,split,weights,modes,deadline=sample_deadline)
                timings[split]=time.monotonic()-start
            if kind=='N2':
                start=time.monotonic(); law_statistics(model,fights,deadline=sample_deadline)
                timings['law']=time.monotonic()-start
            diagnostics[kind]=timings
            from stage1_export import sample_parity_timing
            parity_timing[kind]=sample_parity_timing(model,sample_deadline)
            check_rss()
            del optimizer,model; STORED=None
    except Exception as error:
        atomic(projection_path,dict(status='REFUSED_SAMPLE',attempt=2,reason=str(error),samples=sampled,refresh_pass=refresh,
                        budget_sha256=sha(budget_path),wall_seconds=time.monotonic()-begin,training_run=False))
        raise
    projections={}
    for kind,stats in sampled.items():
        rate=max(s['wall_seconds']/s['work_units'] for s in stats)
        train_work=10*sum(work(rows,kind,lookup) for rows in plan)
        diag=11*diagnostics[kind]['validation']+diagnostics[kind]['test']+diagnostics[kind].get('law',0)
        refresh_cost=10*refresh[kind]['wall_seconds']
        parity_cost=parity_timing[kind]['projected_seconds']
        cost=rate*train_work+diag+refresh_cost+parity_cost
        projections[kind]=dict(training_seconds=rate*train_work,diagnostics_seconds=diag,refresh_seconds=refresh_cost,
                               export_parity_seconds=parity_cost,total_seconds=cost,seconds_per_work_unit=rate,
                               seeds=3 if kind=='N1' else 1)
    for p in projections.values():
        p['all_seed_total_seconds']=p['seeds']*p['total_seconds']
    # All extra N1 seeds have the same rows/steps/epochs and validation selection.
    total=preparation_seconds+3*projections['N1']['total_seconds']+sum(projections[k]['total_seconds'] for k in ('N1r','N2'))
    def minimum_change():
        candidates=[]
        for epochs in range(9,0,-1):
            seconds=preparation_seconds
            for kind,p in projections.items():
                fixed=diagnostics[kind]['validation']+diagnostics[kind]['test']+diagnostics[kind].get('law',0)+p['export_parity_seconds']
                scalable=p['training_seconds']+p['refresh_seconds']+10*diagnostics[kind]['validation']
                seconds+=p['seeds']*(fixed+epochs*scalable/10)
            if seconds<3600:
                return dict(epochs_for_all_arms_and_seeds=epochs,projected_seconds=seconds,applied=False,responsible_role='owner')
        return dict(epochs_for_all_arms_and_seeds=None,reason='even one epoch exceeds cap; needs owner window/data budget decision',applied=False,responsible_role='owner')
    projection=dict(status='ADMITTED' if total<3600 else 'OVER_60_MINUTES',attempt=2,
                    prior_refused_attempt_sha256=sha(HERE/'TRAINING_PROJECTION.json'),
                    total_projected_seconds=total,total_projected_minutes=total/60,
                    method='sequential float64 fits; max nine-step measured rate; measured per-epoch refresh and chronological diagnostics; measured worst-sequence parity rate',
                    samples=sampled,refresh_pass=refresh,diagnostic_timing=diagnostics,parity_timing=parity_timing,
                    preprocessing_seconds=preparation_seconds,per_arm=projections,budget_sha256=sha(budget_path),training_run=False,
                    smallest_declared_change=minimum_change() if total>=3600 else None,
                    sample_wall_seconds=time.monotonic()-begin,cap_seconds=3600)
    atomic(projection_path,projection); print('Projected fits, refresh, diagnostics, three N1 seeds and export parity:',round(total/60,2),'minutes',flush=True)
    if total>=3600 or not run_if_admitted:
        return projection
    deadline=time.monotonic()+3600; outcomes={}
    fits=[('N1',seed,'N1' if i==0 else f'N1_seed{seed}') for i,seed in enumerate(N1_SEEDS)]+[(k,SEEDS[k],k) for k in ('N1r','N2')]
    for kind,seed,name in fits:
        model,optimizer=make(kind,seed); best=math.inf; best_epoch=None; history=[]; rows_seen=0; fit_start=time.monotonic(); fit_cpu=time.process_time()
        resources=Counter(); peak=0
        for epoch in range(10):
            if sources()!=pins or sha(aggregate or DATA/'INDEX.json')!=budget['dataset_index_sha256']:
                raise RuntimeError('training source/index drift')
            epoch_plan=schedule(fights,epoch)
            STORED=StoredStates() if kind!='N1' else None
            if STORED:
                cpu=time.process_time(); seconds=STORED.refresh(model,windows(fights),prepare,deadline)
                resources['refresh_wall_seconds']+=seconds; resources['refresh_cpu_seconds']+=time.process_time()-cpu
            with (OUT/(name+'.steps.jsonl')).open('a') as log:
                for step_id,rows in enumerate(epoch_plan):
                    if time.monotonic()>=deadline:
                        raise TimeoutError('training wall cap; partial checkpoints preserved')
                    measured=step(model,optimizer,rows,weights); rows_seen+=measured['decision_rows']
                    import json
                    log.write(json.dumps(dict(epoch=epoch+1,step=step_id,windows=rows,**measured),allow_nan=False)+'\n'); log.flush()
                    peak=max(peak,measured['rss_bytes'])
                    for k in ('wall_seconds','cpu_seconds','phase_rhs_evaluations'):
                        resources[k]+=measured[k]
            STORED=None
            diagnostic=evaluate(model,fights,'validation',weights,modes,deadline)
            value=diagnostic['weighted_masked_loss']; history.append(dict(epoch=epoch+1,validation=value))
            if value<best:
                best=value; best_epoch=epoch+1
                torch.save(dict(kind=kind,model=model.state_dict(),epoch=best_epoch,seed=seed,budget=budget),OUT/(name+'.pt'))
            print(name,'epoch',epoch+1,'validation',value,flush=True)
        if rows_seen!=budget['decision_rows_per_arm']:
            raise RuntimeError('unequal decision-row budget')
        model.load_state_dict(torch.load(OUT/(name+'.pt'),weights_only=False)['model'])
        export(model,OUT/(name+'.weights.json'))
        test_diagnostic=evaluate(model,fights,'test',weights,modes,deadline)
        validation_diagnostic=evaluate(model,fights,'validation',weights,modes,deadline)
        law=law_statistics(model,fights,deadline)
        outcomes[name]=dict(kind=kind,seed=seed,checkpoint_epoch=best_epoch,history=history,gradient_steps=10*len(plan),decision_rows=rows_seen,
                             resources={**resources,'peak_rss_bytes':peak,'checkpoint_bytes':(OUT/(name+'.pt')).stat().st_size,
                                        'export_bytes':(OUT/(name+'.weights.json')).stat().st_size},learned_law=law,
                             wall_seconds=time.monotonic()-fit_start,cpu_seconds=time.process_time()-fit_cpu,checkpoint_sha256=sha(OUT/(name+'.pt')),
                             export_sha256=sha(OUT/(name+'.weights.json')),test=test_diagnostic,validation=validation_diagnostic)
        del optimizer,model
    from stage1_export import parity
    export_parity=parity(model_root=OUT,prefix=PREFIX,deadline=deadline)
    seed_noise={}
    for head in HEADS:
        metric='balanced_accuracy' if head in ('start','release') else 'top1'
        values=[outcomes[name]['test']['heads'][head][metric] for name in ('N1','N1_seed41101','N1_seed41201')]
        finite=[v for v in values if v is not None]
        seed_noise[head]=dict(metric=metric,values=values,min=min(finite) if finite else None,max=max(finite) if finite else None,
                             sample_sd=float(np.std(finite,ddof=1)) if len(finite)>1 else None)
    if sources()!=pins:
        raise RuntimeError('source drift before training results')
    result=dict(status='TRAINED_BC',models=outcomes,export_parity=export_parity,
                budget_sha256=sha(budget_path),projection_sha256=sha(projection_path),sources=pins,physical_fights=0,
                n1_seed_noise=dict(primary_seed=41001,seeds=list(N1_SEEDS),heads=seed_noise,scope='descriptive three-seed noise yardstick; no hypothesis test'),
                interpretation='BC differences on a stateless teacher do not establish RRG mechanism; compare against three N1 seeds; fixed J prior is a motion confound',
                dagger_run=bool(aggregate),mechanism_run=False)
    atomic(HERE/(PREFIX+'_RESULTS.json'),result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--run-if-admitted',action='store_true'); p.add_argument('--aggregate',type=Path); a=p.parse_args()
    from stage1_jobs import job_lock
    with job_lock('training'):
        run(a.run_if_admitted,a.aggregate)
