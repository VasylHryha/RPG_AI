"""Float32 stored-state window training, prospective measured budget only."""
import copy
import gzip
import json
import math
import random
import time
from pathlib import Path
import numpy as np
import torch
from common import ARMS,HERE,LOCAL,read,sha,sources,write
from data import frames,labels,pack
from models import Policy,initial,remap
from training_control import atomic_checkpoint,last_checkpoint,training_cap,TrainingDeadline
WINDOW=90
FORWARD_FLOPS=0
ENCODER_CALLS=0
PHASE_RHS=0
MONITOR=None
LAST_MONITOR=0.
def live_check():
    global LAST_MONITOR
    now=time.monotonic()
    if MONITOR is not None and now-LAST_MONITOR>=1:
        MONITOR.live_memory(__import__("os").getpid());LAST_MONITOR=now
        worker_memory()

def worker_memory():
    import resource,sys
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform!='darwin':rss*=1024
    if rss>=1.5*1024**3:raise RuntimeError('training worker exceeds 1.5 GiB')
    return rss

def environment():
    import importlib.metadata
    import sys
    from common import CPP
    if sys.version.split()[0]!='3.11.15':raise RuntimeError('use existing pinned s4_net_slice_v1/_local/mlenv/bin/python (3.11.15)')
    for line in (HERE/'requirements.lock').read_text().splitlines():
        if line and not line.startswith('#'):
            name,version=line.split('==')
            if importlib.metadata.version(name)!=version:raise RuntimeError('ML distribution pin mismatch: '+name)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)
    try:torch.set_num_interop_threads(1)
    except RuntimeError:pass

def make(kind):
    random.seed(41001);np.random.seed(41001);torch.manual_seed(41001)
    m=Policy(kind).float()
    import runtime as r
    if r.VARIANT=='learned_dodge':
        from enable_dodge import check
        proof=check();path=Path(proof['checkpoints'][kind]['path'])
        value=torch.load(path,weights_only=False);m.load_state_dict(value['model'])
    return m,torch.optim.Adam(m.parameters(),lr=.001,weight_decay=0)

def tensor(x,dtype=torch.float32):return {k:torch.as_tensor(v,dtype=torch.long if k in ('own','enemy','assignments','aim_sources','move_sources','aim_members','move_members','aim_mapping','move_mapping') else dtype) for k,v in x.items()}

def forward(model,row,state,previous,cache,next_frame,state_only=False,supervised=False):
    global FORWARD_FLOPS,ENCODER_CALLS,PHASE_RHS
    x,ids,enemies=pack(row,model.kind,with_candidates=not state_only);x=tensor(x,next(model.parameters()).dtype)
    if supervised and not state_only:
        labs=labels(row,ids,enemies)
        scale=x['pos'].new_tensor([row['width'],row['height']])
        for name in ('aim','move'):x['teacher_'+name]=x['pos'].new_tensor([v[name] for v in labs]).reshape(-1,2)*scale
    state=remap(model.kind,state,previous,ids)
    # Force a shared refresh on entity removal; no stale-token index reuse.
    current=[u[0] for u in sorted(row['units'],key=lambda u:u[0])]
    refresh=True # B2 public hazards and source embeddings refresh every physical tick
    y,state,cache=model.tick(**x,ids=ids,state=state,dt=row['dt'],refresh=refresh,cache=cache,state_only=state_only)
    if refresh:next_frame=(row['t']+.2,current)
    n=len(ids);nt=len(x['tokens']);ne=len(enemies)
    # Conservative dense multiply/add bound: each scored family has <=64 members; nonlinear kernels are separate.
    FORWARD_FLOPS += (nt*2*2*64*64 if refresh else 0)+n*2*(128*64+2*nt*64+(0 if state_only else 136*64+64*9+64*64+ne*64))
    from candidates import FEATURES
    choices=0 if state_only else 2*n*64*(2 if supervised else 1)
    # Two choice/source/offset heads, factored MLP projections and source dots.
    if not state_only:FORWARD_FLOPS += n*2*2*64*32+2*(n*2*(64*FEATURES+64*64+64*2+64*16+nt*64)+nt*2*64*16+choices*(FEATURES+FEATURES*16+16))
    if model.kind in ('N1r','N1rb'):FORWARD_FLOPS+=n*2*144*8
    if model.kind in ('N2','N2J0'):FORWARD_FLOPS+=n*2*128;PHASE_RHS+=4
    ENCODER_CALLS+=int(refresh)
    return y,state,ids,enemies,cache,next_frame,refresh

def flat(y):return torch.cat((y['move'],y['mult'][:,None],y['fire'],y['aim'],y['drift'],y['target'],y['aim_logits'],y['move_logits'],y['aim_family_logits'],y['move_family_logits'],y['aim_residual'],y['move_residual']),-1)

def objective(y,row,ids,enemies,weights=None):
    labs=labels(row,ids,enemies);device=y['move'].device;dtype=y['move'].dtype
    if not labs:return sum(v.sum()*0 for v in y.values()),{}
    def values(key):return torch.tensor([l[key] for l in labs],device=device,dtype=dtype)
    target=values('target').long();fire=values('fire').long();aimmask=values('aim_mask').bool()
    # Actual movement includes the N2 bounded spacing channel, so J gets gradient.
    move=y['move']+y['drift']/y['move'].new_tensor([row['width'],row['height']])
    losses=dict(move=torch.mean((move-values('move'))**2),mult=torch.mean((y['mult']-values('mult'))**2),target=torch.nn.functional.cross_entropy(y['target'],target),fire=torch.nn.functional.cross_entropy(y['fire'],fire,weight=None if weights is None else y['fire'].new_tensor(weights)),aim=torch.mean((y['aim'][aimmask]-values('aim')[aimmask])**2) if aimmask.any() else y['aim'].sum()*0)
    return sum(losses.values()),{k:float(v.detach()) for k,v in losses.items()}

def selected_starts(length,windows):
    starts=list(range(0,length,WINDOW))
    if len(starts)<=windows:return starts
    return [starts[i] for i in np.linspace(0,len(starts)-1,windows,dtype=int)]

def stored(model,fight,windows,deadline,path=None):
    """One linear full-fight replay; detached state and encoder at window starts.
    No teacher-forced memory and no prefix replay per training window.
    """
    start=time.monotonic();rows=list(frames(LOCAL/fight['raw_file']));starts=selected_starts(len(rows),windows)
    state=initial(model.kind,[],next(model.parameters()).dtype);ids=[];cache=None;next_frame=(0,[]);saved={}
    model.eval()
    if model.kind in ('N1','N1b'):
        # Memoryless arms refresh their encoder each tick; no prefix forward is needed.
        saved={i:(state.clone(),[],None,(0,[])) for i in starts}
        if path:atomic_checkpoint(path,saved)
        return rows,saved,time.monotonic()-start
    with torch.no_grad():
        for i,row in enumerate(rows):
            live_check()
            if time.monotonic()>=deadline:raise TimeoutError('cap during stored-state refresh')
            if i in starts:saved[i]=(state.clone(),ids[:],None if cache is None else cache.clone(),next_frame)
            y,state,ids,enemies,cache,next_frame,refresh=forward(model,row,state,ids,cache,next_frame,state_only=True)
    if path:atomic_checkpoint(path,saved)
    return rows,saved,time.monotonic()-start

def step(model,optimizer,rows,context,weights,deadline):
    state,ids,cache,next_frame=copy.deepcopy(context);model.train();start=time.monotonic();cpu=time.process_time();loss=0;mass=0;decisions=0
    previous_active={}
    for tick,row in enumerate(rows):
        live_check()
        if time.monotonic()>=deadline:raise TimeoutError('cap during optimizer step')
        y,state,ids,enemies,cache,next_frame,refresh=forward(model,row,state,ids,cache,next_frame,supervised=True)
        # Every release/readiness/reaction transition; otherwise base frames /4.
        important=any(r['ready'] or r['engineRelease'] or previous_active.get(r['id'])!=r['active'] for r in row['labels'])
        previous_active={r['id']:r['active'] for r in row['labels']}
        if important or (refresh and tick%24==0):
            value,_=objective(y,row,ids,enemies,weights);loss=loss+value*len(ids);mass+=len(ids);decisions+=len(ids)
    if not mass:raise RuntimeError('empty training window')
    optimizer.zero_grad();(loss/mass).backward();torch.nn.utils.clip_grad_norm_(model.parameters(),5);optimizer.step()
    if not all(torch.isfinite(v).all() for v in model.parameters()):raise FloatingPointError('nonfinite weights')
    rss=worker_memory()
    return dict(wall_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu,rss_bytes=rss,decision_rows=decisions,loss=float((loss/mass).detach()))

def evaluate(model,fights,windows,weights,deadline):
    total=mass=0;heads={};roles={};start=time.monotonic();cpu=time.process_time();prefix_seconds=0.;window_ticks=0
    for fight in fights:
        rows,saved,refresh_seconds=stored(model,fight,windows,deadline);prefix_seconds+=refresh_seconds
        with torch.no_grad():
            for at,context in saved.items():
                state,ids,cache,next_frame=context
                for row in rows[at:at+WINDOW]:
                    window_ticks+=1
                    y,state,ids,enemies,cache,next_frame,_=forward(model,row,state,ids,cache,next_frame,supervised=True);v,ls=objective(y,row,ids,enemies,weights);total+=float(v)*len(ids);mass+=len(ids)
                    for k,x in ls.items():heads[k]=heads.get(k,0)+x*len(ids)
                    for i,l in enumerate(labels(row,ids,enemies)):
                        c=roles.setdefault(l['role'],dict(rows=0,target_correct=0,fire_correct=0,active_predicted=0,active_oracle=0,ready_rows=0))
                        c['rows']+=1;c['target_correct']+=int(int(y['target'][i].argmax())==l['target']);pred=int(y['fire'][i].argmax());c['fire_correct']+=int(pred==l['fire']);c['active_predicted']+=pred!=1;c['active_oracle']+=l['fire']!=1;c['ready_rows']+=l['ready']
    if not mass:raise RuntimeError('empty evaluation')
    return dict(prefix_seconds=prefix_seconds,window_ticks=window_ticks,loss=total/mass,rows=mass,heads={k:v/mass for k,v in heads.items()},roles=roles,wall_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu)

def checked_budget():
    b=read(LOCAL/'TRAIN_BUDGET.json')
    if b['sources']!=sources() or b['index_sha256']!=sha(LOCAL/'INDEX.json') or b['audit_sha256']!=sha(LOCAL/'DECIDABILITY.json'):raise RuntimeError('training identity drift; cannot resume')
    if read(LOCAL/'DECIDABILITY.json')['status']!='PASS':raise RuntimeError('decidability gate blocked')
    from collect import check
    check();return b

def measure(epochs=2,windows=4):
    global MONITOR
    environment()
    if not 1<=epochs<=10 or not 1<=windows<=32:raise ValueError('budget envelope')
    if (LOCAL/'TRAIN_BUDGET.json').exists():raise RuntimeError('budget already sealed; preserve prior measured sample')
    from collect import check
    check();index=read(LOCAL/'INDEX.json');audit=read(LOCAL/'DECIDABILITY.json')
    if audit['status']!='PASS' or audit.get('sources')!=sources() or audit['index_sha256']!=sha(LOCAL/'INDEX.json'):raise RuntimeError('current PASS audit required')
    train=[f for f in index['fights'] if f['split']=='train'];val=[f for f in index['fights'] if f['split']=='validation'];cap=training_cap(HERE)
    from jobs import admitted
    with admitted(cap['cap_seconds']) as (absolute,monitor):
        deadline=TrainingDeadline(HERE,absolute,cap['cap_seconds']);MONITOR=monitor
        samples={};setup_start=time.monotonic();firecounts=np.zeros(3)
        for f in train:
            for row in frames(LOCAL/f['raw_file']):
                live_check()
                if time.monotonic()>=deadline:raise TimeoutError('cap during class-weight preparation')
                for r in row['labels']:firecounts[('automatic','hold','release').index(r['executed']['fire'])]+=1
        weights=(firecounts.sum()/np.maximum(firecounts,1));weights/=weights.mean();weights=weights.tolist();setup_seconds=time.monotonic()-setup_start
        for arm in ARMS:
            model,optimizer=make(arm)
            # Full-size first training fight, four declared windows; 20 steps total.
            rows,states,refresh_time=stored(model,train[0],4,deadline)
            reload_start=time.monotonic();list(frames(LOCAL/train[0]['raw_file']));reload_seconds=time.monotonic()-reload_start
            reload_projection=reload_seconds/max(1,train[0]['frames'])*sum(f['frames'] for f in train)
            if len(states)<2:raise RuntimeError('timing fight too short; need warmup plus measured windows')
            sample=[]
            for at,context in list(states.items())[:4]:sample.append(step(model,optimizer,rows[at:at+WINDOW],context,weights,deadline))
            diag=evaluate(model,val[:1],windows,weights,deadline)
            steps=sum(len(selected_starts(f['frames'],windows)) for f in train)
            refresh=(refresh_time/max(1,train[0]['frames']))*sum(f['frames'] for f in train)
            diagnostic=diag['wall_seconds']/max(1,val[0]['frames'])*sum(f['frames'] for f in val)
            fit=setup_seconds+epochs*(steps*max(s['wall_seconds'] for s in sample[1:])+refresh+reload_projection+diagnostic)+diagnostic*2
            samples[arm]=dict(steps=sample,steps_per_epoch=steps,refresh_seconds_per_epoch=refresh,reload_seconds_per_epoch=reload_projection,validation_seconds=diagnostic,fit_seconds=fit,parameter_count=sum(v.numel() for v in model.parameters()),dtype='float32',J_trainable=arm=='N2')
        topology=__import__('training_control').measured_cores();topology['slots']=min(topology['slots'],len(ARMS))
        groups=__import__('training_control').lanes({a:s['fit_seconds'] for a,s in samples.items()},topology['slots'])
        projection=1.2*max(g['wall_seconds'] for g in groups)
        budget=dict(sources=sources(),index_sha256=sha(LOCAL/'INDEX.json'),audit_sha256=sha(LOCAL/'DECIDABILITY.json'),epochs=epochs,windows_per_fight=windows,window_ticks=WINDOW,class_weights=weights,samples=samples,groups=groups,topology=topology,projected_seconds=projection,margin=1.2,training_cap=cap,status='ADMITTED' if projection<=cap['cap_seconds'] and all(1.2*s['fit_seconds']<=3600 for s in samples.values()) else 'REFUSED',parity='separate mandatory host stage; measured from full validation replay before outcome',sample_steps=sum(len(s['steps']) for s in samples.values()))
        write(LOCAL/'TRAIN_BUDGET.json',budget,exclusive=True)
        if budget['status']!='ADMITTED':raise RuntimeError('measured fit exceeds 1h per arm or whole-job owner cap; revise prospectively')
