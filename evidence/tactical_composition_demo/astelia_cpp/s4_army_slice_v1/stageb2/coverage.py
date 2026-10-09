"""Deterministic 5 Hz availability check over all fights; exact N2 prefix states."""
import argparse,time,secrets
import runtime as r
from candidates import mapped_labels,TOLERANCE,AIM_OFFSET,MOVE_OFFSET

def accumulate(counts,row,drift=None,mapped=None):
    ids=sorted(v[0] for v in row['units'] if v[1]==0)
    for lab in mapped_labels(row,ids,drift) if mapped is None else mapped:
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

STRIDE=6 # recorded physical ticks are 30 Hz; one declared phase per fight
from owner_approvals import load as approvals
MAX_SECONDS=approvals()['coverage']['max_seconds']

def population(counts,row):
    for lab in row['labels']:
        for head in ('move','aim'):
            if head=='aim' and lab['executed']['aim'] is None:continue
            for cat in ('all','dodge' if lab.get('active') else 'ordinary'):
                key=(lab['role'],head,cat);counts[key]=counts.get(key,0)+1

def error_bounds(table,pop):
    out=report(table)
    for key,c in table.items():
        n=pop[key];v=out[':'.join(key)];v['population_rows']=n
        v['deterministic_error_bound']={}
        for metric,total in (('coverage','covered'),('bounded_residual_coverage','representable')):
            lo=c[total]/n;hi=(c[total]+n-c['rows'])/n
            v['deterministic_error_bound'][metric]=dict(lower=lo,upper=hi,max_absolute_error=max(v[metric]-lo,hi-v[metric]))
    return out

def preserve_previous(local,sources,index_sha256):
    """Explicit corrected-revision binding, under the ordinary admitted lock."""
    path=local/'COVERAGE.json'
    if not path.exists():return None
    old=r.read(path)
    if old.get('sources')==sources and old.get('index_sha256')==index_sha256:
        raise RuntimeError('same-code coverage already recorded; do not repeat')
    digest=r.sha(path);archive=local/('COVERAGE_PRE_B2MOVE_'+digest[:16]+'.json')
    if archive.exists():raise RuntimeError('previous coverage archive already exists; preserve and inspect')
    path.rename(archive)
    return dict(path=str(archive),sha256=digest)

def run(round,test_mode=False,preserve_stale=False):
    import torch,training
    from models import Policy,initial
    from train import configure,prepare
    from jobs import admitted
    from training_control import training_cap,TrainingDeadline
    from coverage_gate import THRESHOLDS,CAUSE,admission
    global MAX_SECONDS
    MAX_SECONDS=approvals()['coverage']['max_seconds']
    local=configure(round);index=prepare(round);training.environment();token=secrets.token_hex(8);start=time.monotonic()
    receipt=dict(status='RUNNING',index_sha256=r.sha(local/'INDEX.json'),sources=r.sources(),records=[],thresholds=approvals()['coverage']['thresholds'],threshold_cause=CAUSE)
    cap=training_cap(r.HERE);cap['cap_seconds']=min(cap['cap_seconds'],MAX_SECONDS)
    from native_candidates import batch,unpack
    if test_mode:
        from train import timing_fights
        index=dict(index,fights=timing_fights([f for f in index['fights'] if f['split']=='train']))
    try:
        with admitted(cap['cap_seconds']) as (absolute,monitor):
            if preserve_stale and not test_mode:receipt['preserved_coverage']=preserve_previous(local,receipt['sources'],receipt['index_sha256'])
            deadline=TrainingDeadline(r.HERE,absolute,cap['cap_seconds'],scope='coverage');coverage_end=time.monotonic()+MAX_SECONDS;counts={};fit_counts={};checkpoint_counts={};populations={};fit_populations={};mass=0;physical_mass=0;initial_models={};checkpoints={}
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
                group=f['split']+':'+f.get('arm','shared');pop={}
                import hashlib
                phase=int(hashlib.sha256(f['tag'].encode()).hexdigest()[:8],16)%STRIDE
                fight_sample=0;fight_start=time.monotonic()
                contexts={a:(initial(a,[]),[],None,(0,[])) for a in arms}
                cp_context=(initial('N2',[]),[],None,(0,[]))
                with torch.no_grad():
                    for tick,row in enumerate(r.frames(f['raw_file'])):
                        if time.monotonic()>=deadline or time.monotonic()>=coverage_end:raise TimeoutError('coverage live cap')
                        physical_mass+=1;population(pop,row)
                        sampled=tick%STRIDE==phase
                        drift=None;cp_drift=None
                        # State evolution is independent of candidate heads. Batched
                        # units at every physical tick preserve exact prefix phase.
                        if 'N2' in arms:
                            y,state,ids,_,cache,clock,_=training.forward(initial_models['N2'],row,*contexts['N2'],state_only=True)
                            contexts['N2']=(state,ids,cache,clock)
                            if sampled:drift=y['drift'].detach().numpy()
                            if checkpoints:
                                y,state,ids,_,cache,clock,_=training.forward(checkpoints['N2'],row,*cp_context,state_only=True)
                                cp_context=(state,ids,cache,clock)
                                if sampled:cp_drift=y['drift'].detach().numpy()
                        if tick%30==0:monitor.live_memory(__import__('os').getpid())
                        if not sampled:continue
                        row['_candidate_banks']=unpack(batch(row,allow_missing_aim=True))
                        raw_labels=mapped_labels(row,sorted(row['_candidate_banks']))
                        accumulate(counts.setdefault(group,{}),row,mapped=raw_labels);mass+=1;fight_sample+=1
                        for arm in arms:
                            accumulate(fit_counts.setdefault(f['split']+':'+arm,{}),row,drift if arm=='N2' else None,mapped=None if arm=='N2' else raw_labels)
                        if cp_drift is not None:accumulate(checkpoint_counts.setdefault(f['split']+':N2',{}),row,cp_drift)
                        if mass%30==0:monitor.live_memory(__import__('os').getpid())
                for key,n in pop.items():
                    raw_pop=populations.setdefault(group,{});raw_pop[key]=raw_pop.get(key,0)+n
                    for arm in arms:
                        fit_pop=fit_populations.setdefault(f['split']+':'+arm,{});fit_pop[key]=fit_pop.get(key,0)+n
                receipt['records'].append(dict(tag=f['tag'],panel=f['panel'],tactic=f['tactic'],split=f['split'],raw_sha256=f['raw_sha256'],phase=phase,physical_frames=tick+1,sampled_frames=fight_sample,seconds=time.monotonic()-fight_start))
                if at==0 and not test_mode:
                    projection=1.2*(time.monotonic()-start)/max(1,physical_mass)*sum(q['frames'] for q in index['fights'][1:]);receipt['projected_remaining_seconds']=projection
                    if projection>min(deadline-time.monotonic(),coverage_end-time.monotonic()):raise RuntimeError('coverage projection exceeds cap')
            receipt.update(status='TEST_ONLY' if test_mode else 'DONE',sampling=dict(stride=STRIDE,phase='sha256(fight tag) first 32 bits modulo 6',fights='TEST ONLY: largest-frame train fight per panel' if test_mode else 'all indexed fights; panel/tactic/split/arm strata retained',physical_frames=physical_mass,sampled_frames=mass,sampling_error='Exact worst-case finite-population bounds per role/head/category: unsampled binary outcomes can all fail or all pass. Deterministic systematic sampling has no distribution-free narrow statistical CI; thresholds apply to the declared sample only. Physical ticks are correlated. No full-population certification.',cadence='every sixth physical tick (5 Hz at 30 Hz)'),coverage={split:error_bounds(c,populations[split]) for split,c in counts.items()},fit_target_coverage={split:error_bounds(c,fit_populations[split]) for split,c in fit_counts.items()},checkpoint_target_coverage={split:error_bounds(c,fit_populations[split]) for split,c in checkpoint_counts.items()},tolerance_px=TOLERANCE,offset_px=dict(aim=AIM_OFFSET,move=MOVE_OFFSET),interpretation='Declared deterministic sample only. N2 drift uses exact full-prefix recurrent evolution with batched units and skips unused candidate/output heads; N1/N1b/N1r/N1rb drift is identically zero. Raw goal and drift-adjusted target use identical frames/units and nearest mapping as loss.py. Admission uses deterministic fit-initialization drift; DAgger additionally reports current checkpoint drift. Drift evolves during fitting, so availability must not be read as proof for every later update. Sample denominators differ from four optimization windows. No closed-loop sufficiency claim.')
            receipt['admission']=admission(receipt,r.ARMS)
            print(__import__('json').dumps(dict(status=receipt['status'],seconds=time.monotonic()-start,sampled_frames=mass,physical_frames=physical_mass,admission_passed=receipt['admission']['passed'])))
            receipt['seconds']=time.monotonic()-start
            if not test_mode:r.write(local/'COVERAGE.json',receipt,exclusive=True)
    except BaseException as e:receipt.update(status='STOP',error=str(e));raise
    finally:receipt['seconds']=time.monotonic()-start;r.write(r.HERE/('COVERAGE_RUN_'+token+'.json'),receipt,exclusive=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--round',type=int,choices=range(11),default=0);p.add_argument('--test-mode',action='store_true');p.add_argument('--preserve-stale',action='store_true');a=p.parse_args();run(a.round,a.test_mode,a.preserve_stale)
