"""Stage B round-specific 10-epoch fits, measured admission, concurrent resume."""
import runtime as r
import argparse,copy,math,os,random,secrets,signal,subprocess,sys,time
import numpy as np,torch
import training
from training_control import training_cap,TrainingDeadline,lanes,measured_cores,last_checkpoint
ROOT=r.LOCAL

def configure(round):
    local=ROOT/f'round{round}';local.mkdir(parents=True,exist_ok=True)
    for m in (training,r.data):m.LOCAL=local
    training.environment.__globals__['HERE']=r.STAGEA
    training.checked_budget=lambda:checked(local)
    return local

def checked(local):
    b=r.read(local/'TRAIN_BUDGET.json');validate_index(r.read(local/'INDEX.json'))
    if b['sources']!=r.sources() or b['index_sha256']!=r.sha(local/'INDEX.json'):raise RuntimeError('Stage B training code/index drift; preserve revision')
    for f in r.read(local/'INDEX.json')['fights']:
        if r.sha(f['raw_file'])!=f['raw_sha256']:raise RuntimeError('training shard drift')
    return b

def prepare(round):
    local=configure(round);path=local/'INDEX.json'
    if path.exists():
        index=r.read(path);validate_index(index);return index
    prior=r.read(r.A_LOCAL/'INDEX.json')
    if round==0:
        fights=[dict(f,raw_file=str((r.A_LOCAL/f['raw_file']).resolve())) for f in prior['fights']]
        index=dict(schema=1,arm_fights={a:fights for a in r.ARMS},fights=fights,stagea_index_sha256=r.sha(r.A_LOCAL/'INDEX.json'),round=0)
    else:
        previous=r.read(ROOT/f'round{round-1}/INDEX.json');dagger=verified_dagger(round)
        if dagger['status']!='DONE':raise RuntimeError('completed full-fight DAgger round required')
        arm_fights={a:previous['arm_fights'][a]+[dict(f,raw_file=str((ROOT/f['raw_file']).resolve())) for f in dagger['fights'] if f['arm']==a] for a in r.ARMS}
        # Validation and test remain immutable round 0 whole fights.
        index=dict(schema=1,arm_fights=arm_fights,fights=list({f['tag']:f for a in r.ARMS for f in arm_fights[a]}.values()),stagea_index_sha256=previous['stagea_index_sha256'],dagger_sha256=r.sha(ROOT/f'DAGGER_ROUND{round}.json'),round=round)
    validate_index(index);r.write(path,index,exclusive=True);return index

def project(samples,epochs,slots):
    costs={a:epochs*s['epoch_seconds']+s['tail_seconds'] for a,s in samples.items()}
    groups=lanes(costs,slots);return dict(groups=groups,projected_seconds=1.2*max(g['wall_seconds'] for g in groups),costs=costs)

def measure(round):
    local=configure(round);index=prepare(round);training.environment();cap=training_cap(r.HERE)
    if cap['cap_seconds']>10800:raise RuntimeError('owner Stage B cap cannot exceed 3 h')
    if (local/'TRAIN_BUDGET.json').exists():return checked(local)
    from jobs import admitted
    with admitted(cap['cap_seconds']) as (absolute,monitor):
        deadline=TrainingDeadline(r.HERE,absolute,cap['cap_seconds']);training.MONITOR=monitor;samples={}
        audit_start=time.monotonic();validate_index(index)
        for fight in index['fights']:
            if r.sha(fight['raw_file'])!=fight['raw_sha256']:raise RuntimeError('measurement raw drift')
        admission_seconds=time.monotonic()-audit_start
        for arm in r.ARMS:
            train=[f for f in index['arm_fights'][arm] if f['split']=='train'];val=[f for f in index['fights'] if f['split']=='validation'];test=[f for f in index['fights'] if f['split']=='test']
            from loss import target_weights,install
            setup=time.monotonic();balance=target_weights(train,deadline);setup_seconds=time.monotonic()-setup;install(balance)
            model,opt=training.make(arm);rows,states,refresh=training.stored(model,train[0],4,deadline);steps=[]
            for at,ctx in list(states.items())[:4]:steps.append(training.step(model,opt,rows[at:at+training.WINDOW],ctx,None,deadline))
            if len(steps)<2:raise RuntimeError('measurement needs warmup plus measured windows')
            diag=training.evaluate(model,val[:1],4,None,deadline);frame_mass=sum(f['frames'] for f in train);step_mass=sum(len(training.selected_starts(f['frames'],4)) for f in train)
            # Reparse both stored replay and optimization; charge validation every epoch.
            read_start=time.monotonic();list(r.data.frames(train[0]['raw_file']));read_seconds=time.monotonic()-read_start
            validation=diag['wall_seconds']/val[0]['frames']*sum(f['frames'] for f in val)
            tail=3*admission_seconds+setup_seconds+3*validation+diag['wall_seconds']/val[0]['frames']*sum(f['frames'] for f in test)
            epoch=admission_seconds+refresh/train[0]['frames']*frame_mass+read_seconds/train[0]['frames']*frame_mass+step_mass*max(s['wall_seconds'] for s in steps[1:])+validation
            samples[arm]=dict(provenance_check_seconds=admission_seconds,target_balance=balance,setup_seconds=setup_seconds,steps=steps,steps_per_epoch=step_mass,epoch_seconds=epoch,tail_seconds=tail,validation_seconds=validation,fit_seconds=10*epoch+tail)
        topology=measured_cores();topology['slots']=min(4,topology['slots']);p=project(samples,10,topology['slots'])
        b=dict(schema=1,sources=r.sources(),index_sha256=r.sha(local/'INDEX.json'),epochs=10,windows_per_fight=4,window_ticks=90,class_weights=None,loss='fire CE; train-only role-balanced target CE; goal/aim SmoothL1 in 100 px geometry units; validation-only role fire thresholds',arms=list(r.ARMS),dropped='N2J0: lane saving after 0 wins; distinct attack behavior, no proof J irrelevant',samples=samples,topology=topology,round=round,margin=1.2,training_cap=cap,status='ADMITTED' if p['projected_seconds']<=cap['cap_seconds'] else 'REFUSED',**p)
        r.write(local/'TRAIN_BUDGET.json',b,exclusive=True)
        if b['status']!='ADMITTED':raise RuntimeError('measured projection exceeds live owner cap')
        return b

def fit(arm,round,absolute,cap):
    local=configure(round);training.environment();b=checked(local);out=local/'training';digest=r.sha(local/'TRAIN_BUDGET.json')
    from loss import install
    install(b['samples'][arm]['target_balance'])
    # The reused epoch worker receives this arm's aggregated student states.
    master=r.read(local/'INDEX.json');arm_index=dict(master,fights=master['arm_fights'][arm]);path=local/(arm+'_INDEX.json');r.write(path,arm_index)
    import worker
    worker.LOCAL=local;worker.HERE=r.HERE
    original_read=worker.read
    worker.read=lambda p:arm_index if Path(p)==local/'INDEX.json' else original_read(p)
    worker.checked_budget=lambda:checked(local)
    worker.fit(arm,TrainingDeadline(r.HERE,absolute,cap))
    from parity import load_model
    import parity
    parity.LOCAL=local
    model,weights=load_model(arm,torch.float32)
    from calibration import fit as calibrate,collect_scores,choose
    deadline=TrainingDeadline(r.HERE,absolute,cap)
    val=[f for f in master['fights'] if f['split']=='validation'];test=[f for f in master['fights'] if f['split']=='test']
    cal=calibrate(model,val,deadline);weights['fireThresholds']=[cal[role]['threshold'] for role in ('melee','ranged','artillery')]
    r.write(out/(arm+'.weights.json'),weights)
    # Held-out test reports use the validation threshold, never choose anew.
    test_values=collect_scores(model,test,deadline);test_report={}
    for role,v in test_values.items():
        scores=np.asarray(v['scores']);truth=np.asarray(v['truth']);allowed=np.asarray(v['allowed']);pred=allowed & (scores>=cal[role]['threshold']);tp=int((pred&truth).sum());fp=int((pred&~truth).sum());fn=int((~pred&truth).sum())
        test_report[role]=dict(rows=len(scores),oracle_active=int(truth.sum()),predicted_active=int(pred.sum()),tp=tp,fp=fp,fn=fn,precision=tp/max(1,tp+fp),recall=tp/max(1,tp+fn))
    r.write(out/(arm+'.calibration.json'),dict(budget_sha256=digest,export_sha256=r.sha(out/(arm+'.weights.json')),validation=cal,test=test_report,selection='closest attainable active count per role on fixed validation windows; safety-blocked rows stay held'))
    result=r.read(out/(arm+'.outcome.json'));result.update(export_sha256=r.sha(out/(arm+'.weights.json')),calibration_sha256=r.sha(out/(arm+'.calibration.json')),status='FIT_CALIBRATED_PARITY_PENDING');r.write(out/(arm+'.outcome.json'),result)

from pathlib import Path

def complete(local,arm,digest):
    p=local/'training'/(arm+'.outcome.json')
    if not p.exists():return False
    v=r.read(p)
    if v['status']!='FIT_CALIBRATED_PARITY_PENDING':return False
    if v['budget_sha256']!=digest or v['export_sha256']!=r.sha(local/'training'/(arm+'.weights.json')) or v['calibration_sha256']!=r.sha(local/'training'/(arm+'.calibration.json')) or v['checkpoint_sha256']!=r.sha(local/'training'/(arm+'.pt')):raise RuntimeError('completed training drift')
    return True

def _run(round,run_id):
    local=configure(round);b=checked(local);cap=training_cap(r.HERE);digest=r.sha(local/'TRAIN_BUDGET.json')
    if b['status']!='ADMITTED':raise RuntimeError('budget refused')
    if cap['cap_seconds']>10800:raise RuntimeError('3 h maximum')
    costs={}
    for arm in r.ARMS:
        ck=last_checkpoint(local/'training/epochs'/arm,digest)
        costs[arm]=0 if complete(local,arm,digest) else (10-(ck['epoch'] if ck else 0))*b['samples'][arm]['epoch_seconds']+b['samples'][arm]['tail_seconds']
    groups=lanes(costs,b['topology']['slots']);projection=1.2*max(g['wall_seconds'] for g in groups)
    if projection>cap['cap_seconds']:raise RuntimeError('remaining projection exceeds live cap')
    import jobs
    started=time.monotonic();live={};handles=[];receipt=dict(round=round,status='RUNNING',projected_seconds=projection,budget_sha256=digest,cap=cap)
    try:
        with jobs.admitted(cap['cap_seconds']) as (absolute,monitor):
            deadline=TrainingDeadline(r.HERE,absolute,cap['cap_seconds']);queues=[g['arms'][:] for g in groups]
            while any(queues) or live:
                if time.monotonic()>=deadline:raise TimeoutError('Stage B training cap')
                for lane,queue in enumerate(queues):
                    if lane in live or not queue:continue
                    arm=queue.pop(0)
                    if complete(local,arm,digest):continue
                    folder=local/'training';folder.mkdir(parents=True,exist_ok=True);log=(folder/(arm+'.worker.log')).open('a');handles.append(log)
                    argv=[sys.executable,str(r.HERE/'train.py'),'worker','--round',str(round),'--arm',arm,'--absolute',str(absolute),'--cap',str(cap['cap_seconds']),'--fds',*[str(fd) for fd in jobs.ACTIVE_FDS]]
                    child=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,pass_fds=jobs.ACTIVE_FDS,start_new_session=True,env={**os.environ,'OMP_NUM_THREADS':'2','MKL_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2'});live[lane]=(child,arm)
                for lane,(child,arm) in list(live.items()):
                    if child.poll() is not None:
                        if child.returncode or not complete(local,arm,digest):raise RuntimeError(arm+' worker failed; resume only after inspecting its log')
                        del live[lane]
                    else:monitor.live_memory(child.pid)
                time.sleep(.2)
            receipt['status']='DONE'
    except BaseException as e:receipt.update(status='STOP_RESUMABLE',error=str(e));raise
    finally:
        for child,arm in live.values():
            if child.poll() is None:os.killpg(child.pid,signal.SIGTERM)
        for child,arm in live.values():
            try:child.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
        for log in handles:log.close()
        receipt['seconds']=time.monotonic()-started;r.write(r.HERE/('TRAIN_STAGEB_RUN_'+run_id+'.json'),receipt,exclusive=True)


def verified_dagger(round):
    from dagger import check
    ledger=check(round);p=ROOT/f'DAGGER_ROUND{round}.json';result=r.read(p);digest=r.sha(ROOT/f'DAGGER_LEDGER_ROUND{round}.json')
    if result['status']!='DONE' or result['ledger_sha256']!=digest or result['round']!=round:raise RuntimeError('DAgger aggregate receipt identity')
    registered={j['tag']:j for j in ledger['jobs']}
    if len(result['fights'])!=len(registered) or {f['tag'] for f in result['fights']}!=set(registered):raise RuntimeError('DAgger aggregate coverage')
    for f in result['fights']:
        c=r.read(ROOT/'raw'/(f['tag']+'_COMPLETE.json'))
        if c['status']!='DONE' or c['job']!=registered[f['tag']] or any(f.get(k)!=v for k,v in registered[f['tag']].items()) or c['ledger_sha256']!=digest or any(c[k]!=f[k] for k in ('raw_file','raw_sha256','frames')) or r.sha(ROOT/c['raw_file'])!=c['raw_sha256']:raise RuntimeError('DAgger aggregate completion drift')
    return result

def validate_index(index):
    if index['stagea_index_sha256']!=r.sha(r.A_LOCAL/'INDEX.json'):raise RuntimeError('round 0 dataset drift')
    audit=r.read(r.A_LOCAL/'DECIDABILITY.json')
    if audit['status']!='PASS' or audit['index_sha256']!=index['stagea_index_sha256']:raise RuntimeError('round 0 audit gate')
    baseline=[dict(f,raw_file=str((r.A_LOCAL/f['raw_file']).resolve())) for f in r.read(r.A_LOCAL/'INDEX.json')['fights']]
    round=index['round']
    for arm in r.ARMS:
        expected=baseline[:]
        for number in range(1,round+1):
            receipt=verified_dagger(number)
            expected.extend(dict(f,raw_file=str((ROOT/f['raw_file']).resolve())) for f in receipt['fights'] if f['arm']==arm)
        if index['arm_fights'][arm]!=expected:raise RuntimeError('cross-arm or held-out aggregation leak')
    union=list({f['tag']:f for arm in r.ARMS for f in index['arm_fights'][arm]}.values())
    if index['fights']!=union:raise RuntimeError('global dataset union drift')
    if round and index['dagger_sha256']!=r.sha(ROOT/f'DAGGER_ROUND{round}.json'):raise RuntimeError('DAgger receipt drift')

def run(round):
    run_id=secrets.token_hex(8);start=time.monotonic();path=r.HERE/('TRAIN_STAGEB_RUN_'+run_id+'.json')
    try:return _run(round,run_id)
    except BaseException as e:
        if not path.exists():r.write(path,dict(status='REFUSED',round=round,error=str(e),seconds=time.monotonic()-start),exclusive=True)
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('prepare','measure','run','worker'));p.add_argument('--round',type=int,choices=(0,1,2),default=0);p.add_argument('--arm',choices=r.ARMS);p.add_argument('--absolute',type=float);p.add_argument('--cap',type=float);p.add_argument('--fds',type=int,nargs=2);a=p.parse_args()
    if a.command=='worker':
        import jobs
        jobs.inherited(a.fds);os.nice(10);training.MONITOR=r.collect.a0();fit(a.arm,a.round,a.absolute,a.cap)
    else:globals()[a.command](a.round)
