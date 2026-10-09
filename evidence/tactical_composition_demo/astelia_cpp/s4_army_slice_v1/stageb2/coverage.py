"""Whole-fight expressiveness audit; no training or fights. Cap and lock required."""
import argparse,time,secrets
import runtime as r
from candidates import mapped_labels,TOLERANCE,AIM_OFFSET,MOVE_OFFSET

def accumulate(counts,row,drift=None):
    ids=sorted(v[0] for v in row['units'] if v[1]==0)
    for lab in mapped_labels(row,ids,drift):
        for name in ('move','aim'):
            v=lab[name]
            if v is None:continue
            for category in ('all', 'dodge' if lab['dodge'] else 'ordinary'):
                c=counts.setdefault((lab['role'],name,category),dict(rows=0,covered=0,representable=0,no_candidates=0,distance_sum=0.,max_distance=0.))
                c['rows']+=1;c['covered']+=v['covered'];c['representable']+=v['representable']
                if v['distance'] is None:c['no_candidates']+=1
                else:c['distance_sum']+=v['distance'];c['max_distance']=max(c['max_distance'],v['distance'])

def report(counts):
    return {':'.join(key):dict(c,coverage=c['covered']/c['rows'],bounded_residual_coverage=c['representable']/c['rows'],mean_distance=c['distance_sum']/max(1,c['rows']-c['no_candidates'])) for key,c in counts.items()}

def model_identity(model):
    import hashlib
    return hashlib.sha256(b''.join(k.encode()+v.detach().cpu().numpy().tobytes() for k,v in model.state_dict().items())).hexdigest()

def run(round):
    import torch,training
    from models import Policy,initial
    from train import configure,prepare
    from jobs import admitted
    from training_control import training_cap,TrainingDeadline
    from coverage_gate import THRESHOLDS,CAUSE,admission
    local=configure(round);index=prepare(round);training.environment();token=secrets.token_hex(8);start=time.monotonic()
    receipt=dict(status='RUNNING',index_sha256=r.sha(local/'INDEX.json'),sources=r.sources(),records=[],thresholds=THRESHOLDS,threshold_cause=CAUSE)
    cap=training_cap(r.HERE)
    try:
        with admitted(cap['cap_seconds']) as (absolute,monitor):
            deadline=TrainingDeadline(r.HERE,absolute,cap['cap_seconds']);counts={};fit_counts={};checkpoint_counts={};mass=0;initial_models={};checkpoints={}
            for arm in r.ARMS:
                model,_=training.make(arm);model.eval();initial_models[arm]=model
            receipt['fit_models']={arm:dict(state_sha256=model_identity(m),target='executed goal minus current model drift; same deterministic initialization/warm start as trainer') for arm,m in initial_models.items()}
            if round:
                path=r.LOCAL/f'round{round-1}/training/N2.pt'
                m=Policy('N2').float();m.load_state_dict(torch.load(path,weights_only=False)['model']);m.eval();checkpoints['N2']=m
                receipt['drift_checkpoint']=dict(path=str(path),sha256=r.sha(path),target='executed goal minus current DAgger policy checkpoint drift')
            for at,f in enumerate(index['fights']):
                if r.sha(f['raw_file'])!=f['raw_sha256']:raise RuntimeError('coverage shard drift')
                arms=[a for a in r.ARMS if f in index['arm_fights'][a]]
                contexts={a:(initial(a,[]),[],None,(0,[])) for a in arms}
                cp_context=(initial('N2',[]),[],None,(0,[]))
                with torch.no_grad():
                    for row in r.data.frames(f['raw_file']):
                        if time.monotonic()>=deadline:raise TimeoutError('coverage live cap')
                        accumulate(counts.setdefault(f['split']+':'+f.get('arm','shared'),{}),row);mass+=1
                        for arm in arms:
                            drift=None
                            if arm=='N2':
                                y,state,ids,_,cache,clock,_=training.forward(initial_models[arm],row,*contexts[arm]);contexts[arm]=(state,ids,cache,clock);drift=y['drift'].detach().numpy()
                            accumulate(fit_counts.setdefault(f['split']+':'+arm,{}),row,drift)
                        if 'N2' in arms and checkpoints:
                            y,state,ids,_,cache,clock,_=training.forward(checkpoints['N2'],row,*cp_context);cp_context=(state,ids,cache,clock)
                            accumulate(checkpoint_counts.setdefault(f['split']+':N2',{}),row,y['drift'].detach().numpy())
                        if mass%30==0:monitor.live_memory(__import__('os').getpid())
                receipt['records'].append(dict(tag=f['tag'],split=f['split'],raw_sha256=f['raw_sha256']))
                if at==0:
                    projection=1.2*(time.monotonic()-start)/max(1,mass)*sum(q['frames'] for q in index['fights'][1:]);receipt['projected_remaining_seconds']=projection
                    if projection>deadline-time.monotonic():raise RuntimeError('coverage projection exceeds cap')
            receipt.update(status='DONE',coverage={split:report(c) for split,c in counts.items()},fit_target_coverage={split:report(c) for split,c in fit_counts.items()},checkpoint_target_coverage={split:report(c) for split,c in checkpoint_counts.items()},tolerance_px=TOLERANCE,offset_px=dict(aim=AIM_OFFSET,move=MOVE_OFFSET),interpretation='Raw goal and drift-adjusted target use identical frames/units and nearest mapping as loss.py. Admission uses deterministic fit-initialization drift; DAgger additionally reports current checkpoint drift. Drift evolves during fitting, so availability must not be read as proof for every later update. Full-prefix denominators differ from four optimization windows. No closed-loop sufficiency claim.')
            receipt['admission']=admission(receipt,r.ARMS)
            r.write(local/'COVERAGE.json',receipt,exclusive=True)
    except BaseException as e:receipt.update(status='STOP',error=str(e));raise
    finally:receipt['seconds']=time.monotonic()-start;r.write(r.HERE/('COVERAGE_RUN_'+token+'.json'),receipt,exclusive=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--round',type=int,choices=(0,1,2),default=0);run(p.parse_args().round)
