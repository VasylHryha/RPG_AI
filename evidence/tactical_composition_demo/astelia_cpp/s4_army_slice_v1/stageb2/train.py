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
    import prepared_cache as candidate_cache
    if (local/'PREPARED_CACHE.json').exists():
        candidate_cache.activate(local,r.read(local/'INDEX.json'),r.frames)
        r.data.frames=candidate_cache.frames;training.frames=candidate_cache.frames
    training.environment.__globals__['HERE']=r.HERE
    training.checked_budget=lambda:checked(local)
    return local

_CHECK_DEPTH=0
_DAGGER_CHECKS={}

def checked(local):
    # Prior receipts form a DAG, not a tree. Verify each once within one nested
    # gate call; discard the cache before the next epoch/invocation check.
    global _CHECK_DEPTH
    if _CHECK_DEPTH==0:_DAGGER_CHECKS.clear()
    _CHECK_DEPTH+=1
    try:return _checked(local)
    finally:_CHECK_DEPTH-=1

def _checked(local):
    b=r.read(local/'TRAIN_BUDGET.json');validate_index(r.read(local/'INDEX.json'))
    coverage=coverage_admission(local)
    if r.read(local/'PREPARED_CACHE.json')!=b['candidate_cache']:raise RuntimeError('prepared cache manifest drift')
    if b.get('coverage_sha256')!=r.sha(local/'COVERAGE.json'):raise RuntimeError('coverage admission drift')
    if b['arms']!=list(r.ARMS) or b.get('variant')!=r.VARIANT:raise RuntimeError('arm/variant drift')
    if b['sources']!=r.sources() or b['index_sha256']!=r.sha(local/'INDEX.json'):raise RuntimeError('Stage B training code/index drift; preserve revision')
    for f in r.read(local/'INDEX.json')['fights']:
        if r.sha(f['raw_file'])!=f['raw_sha256']:raise RuntimeError('training shard drift')
    return b

def prepare(round):
    local=configure(round);path=local/'INDEX.json'
    if r.VARIANT=='learned_dodge':
        from enable_dodge import check
        check()
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

def coverage_admission(local,verify_models=False):
    from coverage_gate import require
    from coverage import model_identity
    coverage=r.read(local/'COVERAGE.json')
    if coverage['status']!='DONE' or coverage['index_sha256']!=r.sha(local/'INDEX.json') or coverage['sources']!=r.sources():raise RuntimeError('current label coverage required')
    require(coverage,r.ARMS)
    if verify_models:
        for arm in r.ARMS:
            model,_=training.make(arm)
            if coverage['fit_models'][arm]['state_sha256']!=model_identity(model):raise RuntimeError('coverage fit model drift')
    if coverage.get('drift_checkpoint'):
        cp=coverage['drift_checkpoint']
        if r.sha(cp['path'])!=cp['sha256']:raise RuntimeError('coverage DAgger checkpoint drift')
    return coverage

def project(samples,epochs,slots):
    costs={a:epochs*s['epoch_seconds']+s['tail_seconds'] for a,s in samples.items()}
    groups=lanes(costs,slots);return dict(groups=groups,projected_seconds=1.2*max(g['wall_seconds'] for g in groups),costs=costs)

def timing_fights(fights):
    # Largest prefix per panel, selected from metadata before any timing/labels.
    return [max([f for f in fights if f['panel']==panel],key=lambda f:(f['frames'],f['tag'])) for panel in sorted({f['panel'] for f in fights})]

def measure(round,test_mode=False):
    local=configure(round);index=prepare(round);training.environment();cap=training_cap(r.HERE)
    coverage=None if test_mode else coverage_admission(local,verify_models=True)
    if cap['cap_seconds']>cap['max_seconds']:raise RuntimeError('owner Stage B2 cap cannot exceed 4.5 h')
    if not test_mode and (local/'TRAIN_BUDGET.json').exists():return checked(local)
    from jobs import admitted
    with admitted(cap['cap_seconds']) as (absolute,monitor):
        deadline=TrainingDeadline(r.HERE,absolute,cap['cap_seconds']);training.MONITOR=monitor;samples={}
        audit_start=time.monotonic();validate_index(index)
        for fight in index['fights']:
            if r.sha(fight['raw_file'])!=fight['raw_sha256']:raise RuntimeError('measurement raw drift')
        admission_seconds=time.monotonic()-audit_start
        from prepared_cache import prepare as cache_prepare,activate as cache_activate,frames as cache_frames
        train_all=[f for f in index['fights'] if f['split']=='train']
        val=[f for f in index['fights'] if f['split']=='validation'];test=[f for f in index['fights'] if f['split']=='test']
        cache_index=index
        if test_mode:
            selected=timing_fights(train_all)+timing_fights(val)
            cache_index=dict(index,fights=selected)
        cache_root=local/'hier_speed_test' if test_mode else local
        cache_receipt=cache_prepare(cache_root,cache_index,r.frames,deadline,monitor)
        # Test mode never seals the full-cache marker or activates a partial cache
        # for a later production process.
        cache_activate(cache_root,cache_index,r.frames);r.data.frames=cache_frames;training.frames=cache_frames
        sample_start=time.monotonic()
        from loss import target_weights,install
        for arm in r.ARMS:
            train=[f for f in index['arm_fights'][arm] if f['split']=='train']
            setup=time.monotonic();balance=target_weights(train,deadline);setup_seconds=time.monotonic()-setup;install(balance)
            model,opt=training.make(arm);steps=[];panel_samples={}
            chosen=timing_fights(train)
            if len(chosen)*2*len(r.ARMS)>20:raise RuntimeError('timing design exceeds 20 optimizer steps')
            for f in chosen:
                rows,states,refresh=training.stored(model,f,4,deadline)
                contexts=list(states.items())
                if len(contexts)<2:raise RuntimeError('measurement needs warmup plus measured windows')
                measured=[]
                for at,ctx in (contexts[0],contexts[-1]):
                    value=training.step(model,opt,rows[at:at+training.WINDOW],ctx,None,deadline)
                    measured.append(value);steps.append(dict(tag=f['tag'],panel=f['panel'],tick=at,**value))
                diag=training.evaluate(model,[q for q in timing_fights(val) if q['panel']==f['panel']],4,None,deadline)
                vf=next(q for q in timing_fights(val) if q['panel']==f['panel'])
                read_start=time.monotonic();training.window_rows(f,4);read_seconds=time.monotonic()-read_start
                panel_samples[f['panel']]=dict(tag=f['tag'],frames=f['frames'],refresh_seconds_per_frame=refresh/f['frames'],read_seconds_per_frame=read_seconds/f['frames'],step_seconds=max(v['wall_seconds'] for v in measured),validation_prefix_seconds_per_frame=diag['prefix_seconds']/vf['frames'],validation_window_seconds_per_tick=(diag['wall_seconds']-diag['prefix_seconds'])/diag['window_ticks'])
            refresh_total=sum(panel_samples[f['panel']]['refresh_seconds_per_frame']*f['frames'] for f in train)
            read_total=sum(panel_samples[f['panel']]['read_seconds_per_frame']*f['frames'] for f in train)
            step_total=sum(panel_samples[f['panel']]['step_seconds']*len(training.selected_starts(f['frames'],4)) for f in train)
            def diagnostic_seconds(fights):
                return sum(panel_samples[f['panel']]['validation_prefix_seconds_per_frame']*f['frames']+panel_samples[f['panel']]['validation_window_seconds_per_tick']*sum(min(training.WINDOW,f['frames']-at) for at in training.selected_starts(f['frames'],4)) for f in fights)
            validation=diagnostic_seconds(val);test_seconds=diagnostic_seconds(test)
            step_mass=sum(len(training.selected_starts(f['frames'],4)) for f in train)
            # Worker final test, then calibration validation and test.
            # Calibration skips unused heads but replays physical-prefix state
            # once; using evaluate's prefix+windows cost is conservative.
            tail=3*admission_seconds+setup_seconds+validation+2*test_seconds
            epoch=admission_seconds+refresh_total+read_total+step_total+validation
            samples[arm]=dict(parameter_count=sum(p.numel() for p in model.parameters()),tool_head_parameters=sum(p.numel() for k,p in model.named_parameters() if k.startswith(('aim_','move_'))),threads=1,provenance_check_seconds=admission_seconds,target_balance=balance,setup_seconds=setup_seconds,steps=steps,per_step_seconds=max(s['wall_seconds'] for s in steps),panel_samples=panel_samples,steps_per_epoch=step_mass,refresh_seconds_per_epoch=refresh_total,read_seconds_per_epoch=read_total,epoch_seconds=epoch,tail_seconds=tail,validation_seconds=validation,fit_seconds=10*epoch+tail)
        topology=measured_cores();topology['slots']=min(4,topology['slots']);p=project(samples,10,topology['slots'])
        cache_frames_count=cache_receipt['frames']
        from candidate_cache import selected_ticks
        cache_projection=cache_receipt['compressed_bytes']/max(1,cache_receipt['cached_frames'])*sum(len(selected_ticks(f['frames'])) for f in index['fights'])
        b=dict(schema=1,sample_steps=sum(len(s['steps']) for s in samples.values()),measurement_seconds=time.monotonic()-sample_start,candidate_cache=cache_receipt,cache_projected_bytes=cache_projection,cache_projected_seconds=cache_receipt['projected_build_seconds']/cache_frames_count*sum(f['frames'] for f in index['fights']),coverage_sha256=None if test_mode else r.sha(local/'COVERAGE.json'),coverage_admission=None if test_mode else coverage['admission'],variant=r.VARIANT,sources=r.sources(),index_sha256=r.sha(local/'INDEX.json'),epochs=10,windows_per_fight=4,window_ticks=90,class_weights=None,loss='fire CE; train-only balanced pointer CE; family CE + conditional member CE (64) plus bounded residual SmoothL1 /100 px; validation-only fire calibration',arms=list(r.ARMS),dropped='N1h, N2J0',samples=samples,topology=topology,round=round,margin=1.2,training_cap=cap,status='TEST_ONLY' if test_mode else ('ADMITTED' if p['projected_seconds']<=cap['cap_seconds'] else 'REFUSED'),timing_selection='largest-frame training/validation fight per panel; first and last selected optimizer windows; all arms, at most 20 steps',**p)
        r.write((cache_root/'SPEED_MEASURE_TEST.json') if test_mode else (local/'TRAIN_BUDGET.json'),b,exclusive=True)
        print(__import__('json').dumps(dict(status=b['status'],sample_steps=b['sample_steps'],measurement_seconds=b['measurement_seconds'],projected_seconds=b['projected_seconds'],cache_projected_bytes=cache_projection,per_step_seconds={a:s['per_step_seconds'] for a,s in samples.items()})))
        if b['status']=='REFUSED':raise RuntimeError('measured projection exceeds live owner cap')
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
    if cap['cap_seconds']>cap['max_seconds']:raise RuntimeError('4.5 h maximum')
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
                    child=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,pass_fds=jobs.ACTIVE_FDS,start_new_session=True,env={**os.environ,'OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'});live[lane]=(child,arm)
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
        receipt['seconds']=time.monotonic()-started;r.write(r.HERE/('TRAIN_STAGEB2_RUN_'+r.VARIANT+'_'+run_id+'.json'),receipt,exclusive=True)


def verified_dagger(round):
    key=(round,r.sha(ROOT/f'DAGGER_ROUND{round}.json'),r.sha(ROOT/f'DAGGER_LEDGER_ROUND{round}.json'))
    if _CHECK_DEPTH and key in _DAGGER_CHECKS:return _DAGGER_CHECKS[key]
    from dagger import check
    ledger=check(round);p=ROOT/f'DAGGER_ROUND{round}.json';result=r.read(p);digest=r.sha(ROOT/f'DAGGER_LEDGER_ROUND{round}.json')
    if result['status']!='DONE' or result['ledger_sha256']!=digest or result['round']!=round:raise RuntimeError('DAgger aggregate receipt identity')
    registered={j['tag']:j for j in ledger['jobs']}
    if len(result['fights'])!=len(registered) or {f['tag'] for f in result['fights']}!=set(registered):raise RuntimeError('DAgger aggregate coverage')
    for f in result['fights']:
        c=r.read(ROOT/'raw'/(f['tag']+'_COMPLETE.json'))
        if c['status']!='DONE' or c['job']!=registered[f['tag']] or any(f.get(k)!=v for k,v in registered[f['tag']].items()) or c['ledger_sha256']!=digest or any(c[k]!=f[k] for k in ('raw_file','raw_sha256','frames')) or r.sha(ROOT/c['raw_file'])!=c['raw_sha256']:raise RuntimeError('DAgger aggregate completion drift')
    if _CHECK_DEPTH:_DAGGER_CHECKS[key]=result
    return result

def validate_index(index):
    global _CHECK_DEPTH
    if _CHECK_DEPTH==0:_DAGGER_CHECKS.clear()
    _CHECK_DEPTH+=1
    try:return _validate_index(index)
    finally:_CHECK_DEPTH-=1

def _validate_index(index):
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
    counts=[len([f for f in index['arm_fights'][a] if f['split']=='train']) for a in r.ARMS]
    if len(set(counts))!=1:raise RuntimeError('matched train fight budget violated')
    union=list({f['tag']:f for arm in r.ARMS for f in index['arm_fights'][arm]}.values())
    if index['fights']!=union:raise RuntimeError('global dataset union drift')
    if round and index['dagger_sha256']!=r.sha(ROOT/f'DAGGER_ROUND{round}.json'):raise RuntimeError('DAgger receipt drift')

def run(round):
    run_id=secrets.token_hex(8);start=time.monotonic();path=r.HERE/('TRAIN_STAGEB2_RUN_'+r.VARIANT+'_'+run_id+'.json')
    try:return _run(round,run_id)
    except BaseException as e:
        if not path.exists():r.write(path,dict(status='REFUSED',round=round,error=str(e),seconds=time.monotonic()-start),exclusive=True)
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('prepare','measure','run','worker'));p.add_argument('--round',type=int,choices=range(11),default=0);p.add_argument('--arm',choices=r.ARMS);p.add_argument('--absolute',type=float);p.add_argument('--cap',type=float);p.add_argument('--fds',type=int,nargs=2);p.add_argument('--test-mode',action='store_true');a=p.parse_args()
    if a.command=='worker':
        import jobs
        jobs.inherited(a.fds);os.nice(10);training.MONITOR=r.collect.a0();fit(a.arm,a.round,a.absolute,a.cap)
    elif a.command=='measure':measure(a.round,a.test_mode)
    else:
        if a.test_mode:raise ValueError('test mode is only available for measure')
        globals()[a.command](a.round)
