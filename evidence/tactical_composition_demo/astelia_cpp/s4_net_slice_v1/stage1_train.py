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
            epoch_shuffle_seed=41999,n1_seeds=N1_SEEDS,concurrent_fits=True,
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



def run(run_if_admitted=False,aggregate=None,epochs=None,resume=False):
    global OUT,PREFIX,ROW_WEIGHTS,HEAD_MASS,STEPS_PER_EPOCH,STORED
    from stage1_training_control import training_cap,measured_cores,project,FITS,last_checkpoint,validate_resume,TrainingDeadline
    from stage1_training_worker import execute,completed_outcome
    if epochs is not None and (type(epochs) is not int or epochs<=0):
        raise ValueError('epochs must be a positive integer')
    if aggregate:
        r=read(aggregate)['round']; OUT=HERE/f'_local/stage1_v2/dagger_r{r}'; PREFIX=f'DAGGER_V2_R{r}'
    projection_path=HERE/('TRAINING_PROJECTION_03.json' if not aggregate else PREFIX+'_PROJECTION_03.json')
    budget_path=HERE/('STAGE1_BUDGET_03.json' if not aggregate else PREFIX+'_BUDGET_03.json')
    result_path=HERE/(PREFIX+'_RESULTS.json')
    if result_path.exists():
        raise RuntimeError('training results already recorded; preserve evidence')
    if not resume and (projection_path.exists() or budget_path.exists()):
        raise RuntimeError('attempt 03 already recorded or interrupted; use --resume, never overwrite or re-sample')
    if resume and not (projection_path.exists() and budget_path.exists()):
        raise RuntimeError('resume requires completed attempt-03 sample and budget; inspect interrupted sample')
    if not resume and any((OUT/(name+suffix)).exists() for kind,seed,name in FITS for suffix in ('.pt','.weights.json','.outcome.json')):
        raise RuntimeError('pre-existing fit artifacts; preserve and inspect')
    authority=training_cap(HERE); topology=measured_cores()
    environment(); fights=index(aggregate); plan=schedule(fights); lookup={m['group']:m for m in fights}
    OUT.mkdir(parents=True,exist_ok=True)
    ROW_WEIGHTS={m['group']:m.get('row_weight',1.) for m in fights}
    HEAD_MASS={k:sum(m['counts'].get(k+'_active',0)*ROW_WEIGHTS[m['group']] for m in fights if m['split']=='train') for k in HEADS}
    STEPS_PER_EPOCH=len(plan)
    weights,modes,counts=fire_stats(fights); pins=sources()
    declared_rows=sum(m['counts']['decision_rows'] for m in fights if m['split']=='train')
    if resume:
        budget=read(budget_path)
        validate_resume(budget,pins,sha(aggregate or DATA/'INDEX.json'),epochs)
        recorded=read(projection_path)
        if recorded['budget_sha256']!=sha(budget_path) or recorded['status']=='REFUSED_SAMPLE':
            raise RuntimeError('resume sample/budget invalid')
        sampled=recorded['samples']; refresh=recorded['refresh_pass']; diagnostics=recorded['diagnostic_timing']
        parity_timing=recorded['parity_timing']; preparation_seconds=recorded['preprocessing_seconds']
    else:
        epoch_count=CONFIG['epochs'] if epochs is None else epochs
        budget={**CONFIG,'epochs':epoch_count,'attempt':3,'concurrent_fits':True,
                'training_cap_seconds':authority['cap_seconds'],'training_cap_authority':authority,'topology':topology,
                'steps_per_epoch':len(plan),'gradient_steps_per_arm':epoch_count*len(plan),
                'decision_rows_per_epoch':declared_rows,'decision_rows_per_arm':epoch_count*declared_rows,
                'work_units_per_epoch':{k:sum(work(rows,k,lookup) for rows in plan) for k in KINDS},
                'training_only_fire_class_weights':weights,'fire_counts':counts,'majority_modes':modes,
                'dataset_index_sha256':sha(aggregate or DATA/'INDEX.json'),'sources':pins,
                'timing_reuse':False,'timing_reuse_reason':'attempt-03 trainer identity changed; fresh bounded nine-step sample',
                'aggregate':str(aggregate.resolve()) if aggregate else None,'output':str(OUT.resolve()),
                'live_cap_check_interval_seconds':1}
        atomic(budget_path,budget)
        begin=time.monotonic(); sample_cap=min(3600,authority['cap_seconds']); sample_deadline=TrainingDeadline(HERE,begin+sample_cap,sample_cap); sampled={}; refresh={}; diagnostics={}; parity_timing={}
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
                parity_timing[kind]=sample_parity_timing(model,sample_deadline,model_root=OUT,attempt=3)
                check_rss()
                del optimizer,model; STORED=None
        except Exception as error:
            atomic(projection_path,dict(status='REFUSED_SAMPLE',attempt=3,reason=str(error),samples=sampled,refresh_pass=refresh,
                            budget_sha256=sha(budget_path),wall_seconds=time.monotonic()-begin,training_run=False))
            raise
    if sources()!=pins:
        raise RuntimeError('source drift during timing sample')
    sample=dict(samples=sampled,refresh_pass=refresh,diagnostic_timing=diagnostics,
                parity_timing=parity_timing,preprocessing_seconds=preparation_seconds)
    completed={}
    for kind,seed,name in FITS:
        state=last_checkpoint(OUT/'epochs'/name,sha(budget_path))
        completed[name]=state['epoch'] if state else 0
    sealed={name:completed_outcome(sys.modules[__name__],OUT,name,sha(budget_path)) for kind,seed,name in FITS}
    parity_path=HERE/(PREFIX+'_EXPORT_PARITY.json')
    if parity_path.exists():
        existing_parity=read(parity_path)
        if existing_parity['status']!='PASS' or any(sealed[n] is None or existing_parity['models'][n]['export_sha256']!=sealed[n]['export_sha256'] for k,s,n in FITS):
            raise RuntimeError('recorded export parity drift')
    calculated=project(sample,budget,topology,completed,sealed_arms=[n for n,v in sealed.items() if v],sealed_parity=parity_path.exists())
    total=calculated['total_projected_seconds']
    projection=dict(**sample,**calculated,status='ADMITTED' if total<=authority['cap_seconds'] else 'OVER_TRAIN_CAP',
                    attempt=3,budget_sha256=sha(budget_path),training_run=False,
                    cap_seconds=authority['cap_seconds'],training_cap_authority=authority,
                    completed_epochs=completed,timing_sources=pins,
                    prior_proxy_receipt_sha256=sha(HERE/'TRAINING_PROJECTION_02.json') if not aggregate else None)
    if not aggregate:
        prior=read(HERE/'TRAINING_PROJECTION_02.json')
        projection['historical_attempt_02_proxy']=dict(status=prior['status'],total_projected_seconds=prior['total_projected_seconds'],
                         total_projected_minutes=prior['total_projected_minutes'],receipt_sha256=sha(HERE/'TRAINING_PROJECTION_02.json'))
    if resume:
        directory=OUT/'resumptions'; directory.mkdir(exist_ok=True)
        invocation=directory/f'{len(list(directory.glob("*.json")))+1:03}.json'
        atomic(invocation,projection)
    else:
        projection['sample_wall_seconds']=time.monotonic()-begin
        atomic(projection_path,projection)
    print('Projected job:',round(total/60,2),'minutes; owner cap:',authority['cap_seconds']/60,'minutes',flush=True)
    if total>authority['cap_seconds'] or not run_if_admitted:
        return projection
    # Cap may only tighten after admission; a later increase requires a new invocation.
    active_cap=min(authority['cap_seconds'],training_cap(HERE)['cap_seconds'])
    if total>active_cap:
        raise RuntimeError('owner training cap tightened after admission')
    job_begin=time.monotonic(); job_cpu=time.process_time()
    deadline=TrainingDeadline(HERE,job_begin+active_cap,active_cap)
    # Workers import the canonical module, even when this coordinator is __main__.
    outcomes=execute(sys.modules[__name__],budget_path,aggregate,OUT,projection,deadline)
    from stage1_export import parity
    parity_path=HERE/(PREFIX+'_EXPORT_PARITY.json')
    if parity_path.exists():
        export_parity=read(parity_path)
        if export_parity['status']!='PASS' or any(export_parity['models'][n]['export_sha256']!=outcomes[n]['export_sha256'] for k,s,n in FITS):
            raise RuntimeError('recorded export parity drift')
    else:
        export_parity=parity(model_root=OUT,prefix=PREFIX,deadline=deadline)
    seed_noise={}
    for head in HEADS:
        metric='balanced_accuracy' if head in ('start','release') else 'top1'
        values=[outcomes[name]['test']['heads'][head][metric] for name in ('N1','N1_seed41101','N1_seed41201')]
        finite=[v for v in values if v is not None]
        seed_noise[head]=dict(metric=metric,values=values,min=min(finite) if finite else None,max=max(finite) if finite else None,
                             sample_sd=float(np.std(finite,ddof=1)) if len(finite)>1 else None)
    validate_resume(budget,sources(),sha(aggregate or DATA/'INDEX.json'),budget['epochs'])
    result=dict(status='TRAINED_BC',attempt=3,models=outcomes,export_parity=export_parity,
                budget_sha256=sha(budget_path),projection_sha256=sha(projection_path),sources=pins,physical_fights=0,
                admission=projection,invocation_wall_seconds=time.monotonic()-job_begin,
                coordinator_cpu_seconds=time.process_time()-job_cpu,
                arm_resource_scope='per-arm counters declare completed checkpoint/current invocation scope; interrupted uncheckpointed work excluded',
                n1_seed_noise=dict(primary_seed=41001,seeds=list(N1_SEEDS),heads=seed_noise,scope='descriptive three-seed noise yardstick; no hypothesis test'),
                interpretation='BC differences on a stateless teacher do not establish RRG mechanism; compare against three N1 seeds; fixed J prior is a motion confound',
                dagger_run=bool(aggregate),mechanism_run=False)
    atomic(result_path,result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--run-if-admitted',action='store_true'); p.add_argument('--aggregate',type=Path)
    p.add_argument('--epochs',type=int); p.add_argument('--resume',action='store_true'); a=p.parse_args()
    from stage1_jobs import job_lock
    from stage1_training_control import training_cap
    with job_lock('training',deadline=time.monotonic()+training_cap(HERE)['cap_seconds']):
        run(a.run_if_admitted,a.aggregate,a.epochs,a.resume)
