"""Focused contract tests: scenario admission, survival/series logic and metric denominators.
No panel or judging execution. Native requests here have duration 0 only.
"""
import copy
import gzip
import json
import pathlib
import sys
import pytest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import lab
from metrics import measure
from replays import one


def test_placement_keeps_role_and_kind_and_heals():
    survivors=[dict(cohort_id=44,role='artillery',kind='shaman',hp=1),dict(cohort_id=11,role='ranged',kind='spitter',hp=3)]
    placed=lab.placement(9382,survivors,orientation=1)
    assert [u['role'] for u in placed]==['ranged','artillery']
    assert all(u['hp_fraction']==1 for u in placed)
    assert placed==lab.placement(9382,list(reversed(survivors)),orientation=1)


def test_drill_allocations():
    pool=lab.catalog()['POOL']
    expected={'D1':(10,30),'D2':(30,10),'D3':(30,15),'D4':(10,10),'D5':(30,30),'C1':(50,50),'C2':(50,50),'C3':(50,50)}
    for drill,counts in expected.items():
        req=lab.drill_request(drill,'v7','regular',18231,0,pool)
        assert tuple(map(len,req['labScenario']['sides']))==counts
        reversed_req=lab.drill_request(drill,'v7','regular',18231,1,pool)
        for side,other in zip(req['labScenario']['sides'],reversed_req['labScenario']['sides']):
            assert all(abs(a['position']['x']+b['position']['x']-1400)<1e-9 for a,b in zip(side,other))
    assert lab.drill_request('D1','v7',None,18231,0,pool)['options']['ai'][1]['params']=={'ranged':0}


def test_doctrines_keep_regular_skills_not_elite():
    for name in lab.catalog()['POOL']:
        p=lab.doctrine(name,lab.catalog()['POOL'])
        assert p['level']=='regular'
        assert 'lookahead' not in p and 'skills' not in p
        req=lab.request('elite',p,9832,abilities_off=True)
        assert req['labAbilities']=='off'
        assert all(ai['skills']['abilities']=='off' for ai in req['options']['ai'])
        assert req['options']['ai'][0]['level']=='elite'


def native(req):
    p=lab.subprocess.run([str(lab.BINARY),'--metrics'],input=json.dumps(req)+'\n',text=True,capture_output=True,check=True)
    rows=[json.loads(line) for line in p.stdout.splitlines()]
    return rows,json.loads(p.stderr)

@pytest.mark.parametrize('mutation',[lambda q:q['labScenario']['sides'][0][0].update(hp_fraction=0),lambda q:q['labScenario']['sides'][0][0].update(hp_fraction=1.01),lambda q:q['labScenario']['sides'][0][0].update(kind='spitter'),lambda q:q['labScenario']['sides'][0][0]['position'].update(x=-1),lambda q:q.update(labAbilities='on')])
def test_native_rejects_invalid_scenario(mutation):
    q=lab.request('v7',lab.controller('dummy_static'),88234)
    q['options']['duration']=0
    mutation(q)
    rows,m=native(q)
    assert 'error' in rows[-1]
    assert m['executed_steps']==0


def test_native_custom_kind_uses_catalog_stats():
    sides=lab.standard(82723)
    sides[0]=[sides[0][0]]
    sides[0][0]['kind']='hound'
    sides[0][0]['hp_fraction']=.5
    q=lab.request('v7',lab.controller('dummy_static'),82723,sides=sides)
    q['options']['duration']=0
    rows,m=native(q)
    u=next(u for u in rows[0]['units'] if u[1]==0)
    assert u[5]==53 and u[6]==6 and u[7]==38
    assert rows[-1]['survivors']==1 and m['executed_steps']==0


def unit(uid,team,role,x,hp=100,reach=300):
    return [uid,team,role,x,400,hp,10,reach,0,False,x,400,0,None]

def test_stream_metrics_use_all_landed_shells_and_real_initial_count(tmp_path):
    path=tmp_path/'fixture.jsonl.gz'
    initial=[unit(41,0,2,500),unit(91,1,2,700)]
    launch=lambda source,team,at:[source,41 if team else 91,team,500,400,0,at,40,False,False]
    damage=dict(source=91,sourceTeam=1,sourceRole='artillery',target=41,targetTeam=0,targetRole='artillery',dealt=20,t=.2,died=False)
    rows=[dict(observerV1=True,step=0,t=0,units=initial,launches=[],damage=[]),
          dict(observerV1=True,step=1,t=.1,units=initial,launches=[launch(91,1,.2),launch(91,1,.4)],damage=[]),
          dict(observerV1=True,step=2,t=.2,units=initial,launches=[],damage=[damage]),
          dict(observerV1=True,step=3,t=.4,units=initial,launches=[],damage=[]),
          dict(survivors=1,enemySurvivors=1,t=.4)]
    with gzip.open(path,'wt') as f:
        for r in rows:f.write(json.dumps(r)+'\n')
    s,alive=measure(path)
    assert s['own_lost']==0 and s['enemy_killed']==0
    assert s['own_units_hit_per_enemy_shell']==.5
    assert s['damage_taken_per_enemy_shell']==10
    assert s['firepower_retained']==1
    assert s['units_out_of_fight']==0
    assert alive[0]['id']==41


def test_series_stops_on_timeout_and_preserves_cohort(monkeypatch,tmp_path):
    pool=lab.catalog()['POOL'];draws=[[dict(seed=100+i,tactic=pool[i]) for i in range(10)]]
    ledger=dict(draws=draws)
    monkeypatch.setattr(lab,'identity',lambda:dict(pool=pool))
    monkeypatch.setattr(lab,'RAW',tmp_path)
    real_read=lab.read
    monkeypatch.setattr(lab,'read',lambda p:ledger if str(p).endswith('SEED_LEDGER.json') else real_read(p))
    seen=[]
    def fake(tag,req,meta,timeout,deadline):
        seen.append((req,meta))
        assert req['labAbilities']=='off'
        assert len(req['labScenario']['sides'][1])==50
        survivors=[dict(id=41,role='artillery',kind='shaman',hp=1)]
        return dict(tag=tag,stats=dict(win=len(seen)==1),survivors=survivors)
    monkeypatch.setattr(lab,'execute',fake)
    r=lab.run_series('v7',0,lab.time.monotonic()+100)
    assert r['streak']==1 and r['fight_reached']==2
    assert r['fights'][1]['units_before']==1 and r['fights'][1]['cohort_before']==[41]
    assert len(seen[1][0]['labScenario']['sides'][0])==1
    assert seen[1][0]['labScenario']['sides'][0][0]['hp_fraction']==1


def test_no_elimination_win_at_timeout(tmp_path):
    p=tmp_path/'late.jsonl.gz'
    rows=[dict(observerV1=True,step=0,t=0,units=[unit(1,0,0,500),unit(51,1,0,520)],launches=[],damage=[]),
          dict(observerV1=True,step=1,t=150,units=[unit(1,0,0,500)],launches=[],damage=[]),dict(survivors=1,enemySurvivors=0,t=150)]
    with gzip.open(p,'wt') as f:
        for r in rows:f.write(json.dumps(r)+'\n')
    stats,_=measure(p)
    assert not stats['win'] and stats['timeout'] and stats['t_elimination'] is None


def test_expired_deadline_never_claims_or_starts_child(monkeypatch,tmp_path):
    monkeypatch.setattr(lab,'RAW',tmp_path)
    monkeypatch.setattr(lab,'identity',lambda:pytest.fail('admission after expiry'))
    with pytest.raises(TimeoutError):lab.execute('expired',{}, {},deadline=lab.time.monotonic()-1)
    assert not list(tmp_path.iterdir())


def test_failed_check_report_survives_missing_timing(monkeypatch,tmp_path):
    import report
    monkeypatch.setattr(report,'HERE',tmp_path)
    monkeypatch.setattr(report,'RAW',tmp_path/'raw')
    monkeypatch.setattr(report,'catalog',lambda:dict(POOL=['line']))
    lab.write(tmp_path/'BUILD.json',dict(status='PASS'))
    lab.write(tmp_path/'CHECKS.json',dict(status='FAIL',checks=[dict(name='early check',pass_check=False)]))
    report.render()
    text=(tmp_path/'SHAPE_LAB_REPORT.md').read_text()
    assert text.startswith('PARTIAL\n') and 'FAIL' in text and 'not evaluated' in text


def test_cached_receipt_tampering_is_rejected(monkeypatch,tmp_path):
    monkeypatch.setattr(lab,'RAW',tmp_path)
    monkeypatch.setattr(lab,'HERE',tmp_path)
    monkeypatch.setattr(lab,'identity',lambda:{})
    declaration=tmp_path/'DECLARATION.json';lab.write(declaration,{})
    req={};meta={};tag='receipt'
    lab.write(tmp_path/(tag+'_request.json'),req)
    claim=dict(meta=meta,request_sha256=lab.sha(tmp_path/(tag+'_request.json')),declaration_sha256=lab.sha(declaration))
    lab.write(tmp_path/(tag+'_CLAIM.json'),claim)
    terminal=dict(survivors=1,enemySurvivors=1,t=0,controllerFailures=[0,0])
    raw=tmp_path/(tag+'.jsonl.gz')
    with gzip.open(raw,'wt') as f:
        f.write(json.dumps(dict(observerV1=True,step=0,t=0,units=[unit(1,0,0,500),unit(51,1,0,520)],launches=[],damage=[]))+'\n')
        f.write(json.dumps(terminal)+'\n')
    native=dict(executed_fights=1)
    lab.write(tmp_path/(tag+'_stderr.log'),native)
    stats,survivors=measure(raw)
    r=dict(meta=meta,summary=terminal,native_metrics=native,stats=stats,survivors=survivors,
           declaration_sha256=lab.sha(declaration),claim_sha256=lab.sha(tmp_path/(tag+'_CLAIM.json')),
           request_sha256=lab.sha(tmp_path/(tag+'_request.json')),raw_sha256=lab.sha(raw),stderr_sha256=lab.sha(tmp_path/(tag+'_stderr.log')))
    lab.write(tmp_path/(tag+'_COMPLETE.json'),r)
    assert lab.verified_record(tag,req,meta)==r
    claim['declaration_sha256']='wrong';lab.write(tmp_path/(tag+'_CLAIM.json'),claim)
    with pytest.raises(RuntimeError,match='declaration/claim'):lab.verified_record(tag,req,meta)


def test_replay_group_size_fallback_retains_all_fights(monkeypatch,tmp_path):
    import replays
    def fake(r,fps):return dict(name=r['tag'],frames=['x'*(1_000_000 if fps>1 else 100)])
    monkeypatch.setattr(replays,'one',fake)
    records=[dict(tag=str(i)) for i in range(10)]
    p=tmp_path/'compact.json';receipt=replays.extract(records,p,'C3')
    assert p.stat().st_size<=8_000_000 and receipt['fps']==1
    assert len(json.loads(p.read_text())['fights'])==10


def test_slow_fields_excluded_from_shell_denominator(tmp_path):
    p=tmp_path/'slow.jsonl.gz'
    rows=[dict(observerV1=True,step=0,t=0,units=[unit(1,0,0,500),unit(91,1,2,700)],launches=[],damage=[]),
          dict(observerV1=True,step=1,t=.2,units=[unit(1,0,0,500),unit(91,1,2,700)],launches=[[91,1,1,500,400,0,.1,45,False,True]],damage=[]),dict(survivors=1,enemySurvivors=1,t=.2)]
    with gzip.open(p,'wt') as f:
        for r in rows:f.write(json.dumps(r)+'\n')
    s,_=measure(p)
    assert s['slow_field_launches']==1 and s['enemy_shells_landed']==0
    assert s['own_units_hit_per_enemy_shell'] is None


def test_cap_default_owner_hash_and_invalid(monkeypatch,tmp_path):
    p=tmp_path/'LAB_CAP.json'
    monkeypatch.setattr(lab,'CPP',tmp_path)
    monkeypatch.setattr(lab,'CAP_PATH',p)
    assert lab.local_cap()['cap_seconds']==3600
    assert lab.local_cap()['cap_file_sha256'] is None
    lab.write(p,dict(cap_seconds=10800,approved_by='owner',date='2026-10-08'))
    cap=lab.local_cap()
    assert cap['cap_seconds']==10800 and cap['cap_file_sha256']==lab.sha(p)
    for value in (True,0,-1,1.5,'10800'):
        lab.write(p,dict(cap_seconds=value,approved_by='owner',date='2026-10-08'))
        with pytest.raises(RuntimeError):lab.local_cap()
    lab.write(p,dict(cap_seconds=10800,approved_by='implementer',date='2026-10-08'))
    with pytest.raises(RuntimeError):lab.local_cap()


def test_fixed_calibration_subset_uses_allocated_requests(monkeypatch):
    monkeypatch.setattr(lab,'identity',lambda:dict(pool=['regular-doctrine']*19))
    ledger=dict(drills={d:list(range(1,6)) for d in lab.DRILLS})
    monkeypatch.setattr(lab,'read',lambda _:ledger)
    monkeypatch.setattr(lab,'drill_request',lambda d,a,o,s,r,p:dict(drill=d,arm=a,opponent=o,seed=s,orientation=r))
    full=list(lab.plan());subset=lab.calibration_cells()
    assert len(full)==560 and len(subset)==56
    assert all(cell in full and cell[2]['cluster']==0 and cell[2]['orientation']==0 for cell in subset)
    assert len(lab.sample_tags())==59 and lab.sample_tags()[-1]=='S10X_elite_s00_f01'


def timing(tag,group,arm,seconds=10,t_end=150,win=True):
    return dict(tag=tag,meta=dict(group=group,arm=arm,opponent=None),seconds=seconds,stats=dict(t_end=t_end,win=win))


def test_projection_uses_measured_workers_full_horizon_and_stopped_series(monkeypatch):
    monkeypatch.setattr(lab,'plan',lambda:iter([('d1',{},dict(group='D1',arm='v7',opponent=None))]))
    monkeypatch.setattr(lab,'read',lambda _:dict(draws=[[{} for _ in range(10)]]))
    samples=[timing('sample','D1','v7',10,75)]+[timing(f'S10X_{a}_s00_f01','S10X',a) for a in lab.SERIES_ARMS]
    records={r['tag']:r for r in samples}
    records['S10X_v7_s00_f01']['stats']['win']=False
    p=lab.measured_projection(samples,records,20,6)
    # One pending drill, no v7 continuation, nine fights for each other series arm.
    assert p['remaining_fights_max']==19
    assert p['measured_utilization']==pytest.approx(1/3)
    assert next(c for c in p['categories'] if c['group']=='D1')['measured_full_horizon_seconds']==20
    assert p['remaining_projected_seconds']==pytest.approx(120)
    # Same wall measurement at fewer workers does not invent extra throughput.
    assert lab.measured_projection(samples,records,20,3)['remaining_projected_seconds']==pytest.approx(120)
    with pytest.raises(RuntimeError):lab.measured_projection(samples,records,0,6)
    with pytest.raises(RuntimeError):lab.measured_projection(samples,records,20,7)


def test_cap_native_interruption_preserved_and_complete_not_repeated(monkeypatch,tmp_path):
    monkeypatch.setattr(lab,'HERE',tmp_path);monkeypatch.setattr(lab,'RAW',tmp_path)
    lab.write(tmp_path/'DECLARATION.json',{})
    calls=[]
    def partial(tag,req,meta,timeout,deadline):
        calls.append(tag)
        lab.write(tmp_path/(tag+'_request.json'),req)
        (tmp_path/(tag+'.stdout')).write_text('partial stream')
        raise lab.subprocess.TimeoutExpired('fake worker',1)
    monkeypatch.setattr(lab,'execute_cell',partial)
    with pytest.raises(TimeoutError):lab.execute('cell',{'seed':1},{},deadline=100)
    archive=list((tmp_path/'interrupted').iterdir())[0]
    receipt=lab.read(archive/'INTERRUPTION.json')
    assert receipt['retry_allowed'] and not receipt['completed']
    assert (archive/'cell.stdout').read_text()=='partial stream'
    assert not list(tmp_path.glob('cell*'))
    assert calls==['cell']


def test_execute_cell_reuses_complete_receipt_without_native(monkeypatch,tmp_path):
    monkeypatch.setattr(lab,'RAW',tmp_path);monkeypatch.setattr(lab,'identity',lambda:{})
    lab.write(tmp_path/'cell_COMPLETE.json',{})
    monkeypatch.setattr(lab,'verified_record',lambda tag,req,meta:dict(tag=tag,reused=True))
    monkeypatch.setattr(lab.subprocess,'run',lambda *a,**k:pytest.fail('repeated complete fight'))
    assert lab.execute('cell',{}, {},deadline=lab.time.monotonic()+100)['reused']


def fake_run_environment(monkeypatch,tmp_path,projected=5):
    monkeypatch.setattr(lab,'HERE',tmp_path);monkeypatch.setattr(lab,'RAW',tmp_path/'raw')
    lab.write(tmp_path/'DECLARATION.json',{});lab.write(tmp_path/'CALIBRATION.json',{})
    monkeypatch.setattr(lab,'require_checks',lambda:{})
    monkeypatch.setattr(lab,'calibration_receipt',lambda:dict(sample_tags=[],projection=dict(calibration_wall_seconds=1)))
    monkeypatch.setattr(lab,'completed_records',lambda:{})
    monkeypatch.setattr(lab,'local_cap',lambda:dict(cap_seconds=10,cap_file='local',cap_file_sha256='setting-hash'))
    monkeypatch.setattr(lab,'measured_projection',lambda *a:dict(remaining_projected_seconds=projected))


def test_run_refuses_measured_over_cap_without_process_or_native(monkeypatch,tmp_path):
    fake_run_environment(monkeypatch,tmp_path,11)
    monkeypatch.setattr(lab,'compute_attempt',lambda *a:pytest.fail('over-cap launched'))
    with pytest.raises(RuntimeError,match='exceeds local cap'):lab.run()
    gate=lab.read(tmp_path/'RUN_GATE.json')
    assert gate['status']=='REFUSED' and gate['cap_file_sha256']=='setting-hash'


def test_run_cap_receipt_and_resume_uses_completed_fights(monkeypatch,tmp_path):
    fake_run_environment(monkeypatch,tmp_path)
    monkeypatch.setattr(lab,'completed_records',lambda:{'done':{}})
    monkeypatch.setattr(lab,'plan',lambda:iter([('done',{},{}),('pending',{}, {})]))
    jobs=[]
    monkeypatch.setattr(lab,'parallel_jobs',lambda batch:jobs.extend(batch))
    def attempt(kind,cap,fn):
        assert cap['cap_file_sha256']=='setting-hash'
        fn(123)
        return dict(seconds=2)
    monkeypatch.setattr(lab,'compute_attempt',attempt)
    lab.run()
    assert [args[0] for fn,args in jobs if fn==lab.execute]==['pending']
    receipt=lab.read(tmp_path/'RUN.json')
    assert receipt['status']=='DONE' and receipt['cap_seconds']==10 and receipt['cap_file_sha256']=='setting-hash'
    def cutoff(*a):raise TimeoutError('local cap')
    monkeypatch.setattr(lab,'compute_attempt',cutoff)
    lab.run()
    assert lab.read(tmp_path/'RUN.json')['status']=='PAUSED_CAP'


def test_attempt_reuses_cap_per_invocation_and_requires_clear_gate(monkeypatch,tmp_path):
    monkeypatch.setattr(lab,'HERE',tmp_path)
    lab.write(tmp_path/'DECLARATION.json',{})
    seen=[]
    monkeypatch.setattr(lab,'process_gate',lambda:seen.append('gate'))
    lab.write(tmp_path/'RUN_ATTEMPT_prior.json',dict(status='STOP',seconds=100))
    start=lab.time.monotonic()
    row=lab.compute_attempt('RUN',dict(cap_seconds=10,cap_file_sha256='hash'),lambda deadline:seen.append(deadline-start))
    assert seen[0]=='gate' and 9<=seen[1]<=11
    assert row['prior_seconds']==100 and row['cap_seconds']==10 and row['status']=='PASS'
    lab.write(tmp_path/'RUN_ATTEMPT_unclosed.json',dict(status='RUNNING'))
    with pytest.raises(RuntimeError,match='unclosed'):lab.compute_attempt('RUN',{},lambda _:pytest.fail('unclosed launched'))


def test_calibration_receipt_identity_and_sample_coverage(monkeypatch,tmp_path):
    monkeypatch.setattr(lab,'HERE',tmp_path);monkeypatch.setattr(lab,'RAW',tmp_path)
    lab.write(tmp_path/'DECLARATION.json',{})
    lab.write(tmp_path/'sample_COMPLETE.json',dict(seconds=1))
    monkeypatch.setattr(lab,'sample_tags',lambda:['sample'])
    receipt=dict(status='MEASURED',workers=6,declaration_sha256=lab.sha(tmp_path/'DECLARATION.json'),sample_tags=['sample'],sample_receipt_hashes={'sample':lab.sha(tmp_path/'sample_COMPLETE.json')})
    attempt=tmp_path/'CALIBRATE_ATTEMPT_fake.json'
    lab.write(attempt,dict(status='PASS',kind='CALIBRATE',workers=6,declaration_sha256=receipt['declaration_sha256'],seconds=20))
    receipt['attempt_hashes']={attempt.name:lab.sha(attempt)}
    receipt['projection']=dict(calibration_wall_seconds=20)
    lab.write(tmp_path/'CALIBRATION.json',receipt)
    assert lab.calibration_receipt()==receipt
    lab.write(tmp_path/'sample_COMPLETE.json',dict(seconds=2))
    with pytest.raises(RuntimeError,match='sample receipt drift'):lab.calibration_receipt()


@pytest.mark.parametrize('won',[True,False])
def test_series_calibration_stops_after_first_fight_without_finalizing(monkeypatch,tmp_path,won):
    pool=['line'];ledger=dict(draws=[[dict(seed=100+i,tactic='line') for i in range(10)]])
    monkeypatch.setattr(lab,'identity',lambda:dict(pool=pool));monkeypatch.setattr(lab,'RAW',tmp_path)
    actual_read=lab.read
    monkeypatch.setattr(lab,'read',lambda p:ledger if str(p).endswith('SEED_LEDGER.json') else actual_read(p))
    seen=[]
    def fake(tag,req,meta,timeout,deadline):
        seen.append(tag)
        return dict(tag=tag,stats=dict(win=won),survivors=[dict(id=41)])
    monkeypatch.setattr(lab,'execute',fake)
    result=lab.run_series('elite',0,100,first_only=True,cap_seconds=10800)
    assert seen==['S10X_elite_s00_f01'] and result['stats']['win']==won
    assert not list(tmp_path.glob('*_SERIES.json'))


def test_calibrate_orchestration_measured_receipt_and_idempotence(monkeypatch,tmp_path):
    monkeypatch.setattr(lab,'HERE',tmp_path);monkeypatch.setattr(lab,'RAW',tmp_path)
    lab.write(tmp_path/'DECLARATION.json',{})
    monkeypatch.setattr(lab,'require_checks',lambda:{})
    monkeypatch.setattr(lab,'local_cap',lambda:dict(cap_seconds=10800,cap_file_sha256='cap-hash'))
    cells=[('drill',{'seed':7},dict(group='D1',arm='v7',opponent=None))]
    monkeypatch.setattr(lab,'calibration_cells',lambda:cells)
    tags=['drill']+[f'S10X_{a}_s00_f01' for a in lab.SERIES_ARMS]
    monkeypatch.setattr(lab,'sample_tags',lambda:tags)
    jobs=[]
    monkeypatch.setattr(lab,'parallel_jobs',lambda batch:jobs.extend(batch))
    def attempt(kind,cap,fn):
        assert kind=='CALIBRATE' and cap['cap_seconds']==10800
        fn(111)
        lab.write(tmp_path/'CALIBRATE_ATTEMPT_fake.json',dict(status='PASS',kind='CALIBRATE',workers=6,declaration_sha256=lab.sha(tmp_path/'DECLARATION.json'),seconds=20))
    monkeypatch.setattr(lab,'compute_attempt',attempt)
    records={tag:timing(tag,'D1' if tag=='drill' else 'S10X','v7') for tag in tags}
    for tag in tags:lab.write(tmp_path/(tag+'_COMPLETE.json'),records[tag])
    monkeypatch.setattr(lab,'completed_records',lambda:records)
    monkeypatch.setattr(lab,'measured_projection',lambda samples,records,wall,workers:dict(remaining_projected_seconds=5,calibration_wall_seconds=wall,workers=workers))
    lab.calibrate()
    receipt=lab.calibration_receipt()
    assert receipt['cap_file_sha256']=='cap-hash' and receipt['projection']['calibration_wall_seconds']==20
    assert len(jobs)==4 and jobs[0][1][0]=='drill'
    assert all(args[3] is True for fn,args in jobs if fn==lab.run_series)
    monkeypatch.setattr(lab,'compute_attempt',lambda *a:pytest.fail('calibration repeated'))
    lab.calibrate()
    assert lab.calibration_receipt()==receipt
    monkeypatch.setattr(lab,'local_cap',lambda:dict(cap_seconds=1))
    with pytest.raises(RuntimeError,match='exceeds local cap'):lab.calibrate()


def test_expired_call_does_not_quarantine_prior_incomplete_cell(monkeypatch,tmp_path):
    monkeypatch.setattr(lab,'RAW',tmp_path)
    lab.write(tmp_path/'old_request.json',dict(seed=1))
    with pytest.raises(TimeoutError):lab.execute('old',{}, {},deadline=lab.time.monotonic()-1)
    assert (tmp_path/'old_request.json').exists() and not (tmp_path/'interrupted').exists()


def test_near_complete_resume_projects_only_remaining_series_suffix(monkeypatch):
    monkeypatch.setattr(lab,'plan',lambda:iter([]))
    monkeypatch.setattr(lab,'read',lambda _:dict(draws=[[{} for _ in range(10)]]))
    samples=[timing(f'S10X_{a}_s00_f01','S10X',a) for a in lab.SERIES_ARMS]
    records={}
    for arm in lab.SERIES_ARMS:
        for fight in range(1,10):
            tag=f'S10X_{arm}_s00_f{fight:02d}'
            records[tag]=timing(tag,'S10X',arm)
    p=lab.measured_projection(samples,records,5,6)
    assert p['remaining_fights_max']==3 and p['series_chain_bound_seconds']==10
    assert p['remaining_projected_seconds']==pytest.approx(12)
    for arm in lab.SERIES_ARMS:
        tag=f'S10X_{arm}_s00_f10';records[tag]=timing(tag,'S10X',arm)
    assert lab.measured_projection(samples,records,5,6)['remaining_projected_seconds']==0


def test_calibration_attempt_tampering_rejected(monkeypatch,tmp_path):
    monkeypatch.setattr(lab,'HERE',tmp_path);monkeypatch.setattr(lab,'RAW',tmp_path)
    lab.write(tmp_path/'DECLARATION.json',{})
    monkeypatch.setattr(lab,'sample_tags',lambda:[])
    declaration_hash=lab.sha(tmp_path/'DECLARATION.json')
    path=tmp_path/'CALIBRATE_ATTEMPT_fake.json'
    attempt=dict(status='PASS',kind='CALIBRATE',workers=6,declaration_sha256=declaration_hash,seconds=20)
    lab.write(path,attempt)
    receipt=dict(status='MEASURED',workers=6,declaration_sha256=declaration_hash,sample_tags=[],sample_receipt_hashes={},attempt_hashes={path.name:lab.sha(path)},projection=dict(calibration_wall_seconds=20))
    lab.write(tmp_path/'CALIBRATION.json',receipt)
    assert lab.calibration_receipt()==receipt
    attempt['seconds']=1;lab.write(path,attempt)
    with pytest.raises(RuntimeError,match='timing attempt drift'):lab.calibration_receipt()
    receipt['attempt_hashes'][path.name]=lab.sha(path);lab.write(tmp_path/'CALIBRATION.json',receipt)
    with pytest.raises(RuntimeError,match='measured wall drift'):lab.calibration_receipt()


@pytest.mark.parametrize('command,expected',[
    ('/Users/new/RiderProjects/ai_RPG_test/build/tactics_lab_host --metrics', True),
    ('/Users/new/RiderProjects/astelia-hunte/build/tactics_lab_host --metrics', False),
    ('/private/tmp/claude-501/-Users-new-RiderProjects-ai-RPG-test/job/tactics_lab_host', True),
    ('/private/tmp/claude-501/-Users-new-RiderProjects-astelia-hunte/job/tactics_lab_host', False),
    ('/private/tmp/claude-501/-Users-new-RiderProjects-ai-RPG-test-extra/tactics_lab_host', False),
    ('/Users/new/RiderProjects/ai_RPG_test_extra/tactics_lab_host', False),
    ('/usr/bin/python3 /Users/new/RiderProjects/ai_RPG_test/evidence/medium_runner.py', True),
    ('/usr/bin/python3 /Users/new/RiderProjects/astelia-hunte/medium_runner.py', False),
    ('/foreign/astelia_native --input=/Users/new/RiderProjects/ai_RPG_test/raw/request.json', True),
    ('/Users/new/RiderProjects/ai_RPG_test/../astelia-hunte/tactics_lab_host', False),
    ('/foreign/astelia_native "/Users/new/RiderProjects/ai_RPG_test/a b/request.json"', True),
])
def test_process_scope_absolute_and_scratch_boundaries(command,expected):
    item=lab.classify_process(123,command)
    assert ('path' in item)==expected
    assert item['pid']==123 and item['command']==command and item['reason']


@pytest.mark.parametrize('cwd,expected',[
    ('/Users/new/RiderProjects/ai_RPG_test',True),
    ('/Users/new/RiderProjects/astelia-hunte',False),
    ('/private/tmp/claude-501/-Users-new-RiderProjects-ai-RPG-test/job',True),
])
def test_relative_heavy_runner_resolves_in_process_cwd(monkeypatch,cwd,expected):
    calls=[]
    def query(argv,**kwargs):
        calls.append(argv)
        return lab.subprocess.CompletedProcess(argv,0,'p123\nn'+cwd+'\n','')
    monkeypatch.setattr(lab.subprocess,'run',query)
    item=lab.classify_process(123,'python3 evidence/medium_runner.py')
    assert ('path' in item)==expected
    assert calls==[['lsof','-a','-p','123','-d','cwd','-Fn']]


def test_scope_resolves_symlinks_without_prefix_false_positive(monkeypatch,tmp_path):
    repo=tmp_path/'repo';repo.mkdir()
    outside=tmp_path/'outside';outside.mkdir()
    (tmp_path/'alias').symlink_to(repo,target_is_directory=True)
    (repo/'foreign').symlink_to(outside,target_is_directory=True)
    monkeypatch.setattr(lab,'REPO_ROOT',repo.resolve())
    assert lab.scoped_path(str(tmp_path/'alias/tactics_lab_host'))
    assert lab.scoped_path(str(repo/'foreign/tactics_lab_host')) is None


def test_process_gate_records_ignored_foreign_and_waits_only_for_local(monkeypatch,tmp_path):
    monkeypatch.setattr(lab,'HERE',tmp_path)
    foreign='91 /private/tmp/claude-501/-Users-new-RiderProjects-astelia-hunte/job/tactics_lab_host\n'
    local='92 /Users/new/RiderProjects/ai_RPG_test/build/astelia_native_v7 --metrics\n'
    outputs=iter([foreign+local,foreign])
    sleeps=[]
    monkeypatch.setattr(lab.time,'sleep',lambda seconds:sleeps.append(seconds))
    snapshots=[]
    real_write=lab.write
    def capture(path,row,**kwargs):
        snapshots.append(copy.deepcopy(row));real_write(path,row,**kwargs)
    monkeypatch.setattr(lab,'write',capture)
    monkeypatch.setattr(lab.subprocess,'run',lambda argv,**kwargs:lab.subprocess.CompletedProcess(argv,0,next(outputs),''))
    row=lab.process_gate()
    assert sleeps==[30] and [s['status'] for s in snapshots]==['ACTIVE','CLEAR']
    assert snapshots[0]['matched'][0]['pid']==92
    assert row['matched']==[] and row['ignored_foreign'][0]['pid']==91
    assert row['ignored_foreign'][0]['reason'] and lab.read(tmp_path/'PROCESS_GATE.json')==row


@pytest.mark.parametrize('result',[(1,'',''),(2,'','error'),(0,'bad row',''),(0,'',''),(0,'123 /foreign/tactics_lab_host','error')])
def test_process_gate_empty_and_unavailable_fail_closed(monkeypatch,tmp_path,result):
    monkeypatch.setattr(lab,'HERE',tmp_path)
    monkeypatch.setattr(lab.subprocess,'run',lambda argv,**kwargs:lab.subprocess.CompletedProcess(argv,*result))
    if result==(1,'',''):
        assert lab.process_gate(wait=False)['status']=='CLEAR'
    else:
        with pytest.raises(RuntimeError,match='UNAVAILABLE'):lab.process_gate(wait=False)
        assert lab.read(tmp_path/'PROCESS_GATE.json')['status']=='UNAVAILABLE'


def test_process_gate_relative_cwd_failure_is_unavailable(monkeypatch,tmp_path):
    monkeypatch.setattr(lab,'HERE',tmp_path)
    def query(argv,**kwargs):
        return lab.subprocess.CompletedProcess(argv,0,'123 python3 evidence/medium_runner.py\n','') if argv[0]=='pgrep' else lab.subprocess.CompletedProcess(argv,1,'','')
    monkeypatch.setattr(lab.subprocess,'run',query)
    with pytest.raises(RuntimeError,match='UNAVAILABLE'):lab.process_gate(wait=False)
    row=lab.read(tmp_path/'PROCESS_GATE.json')
    assert row['ignored_foreign']==[] and row['unresolved'][0]['pid']==123


def test_process_gate_no_wait_still_blocks_own_heavy_runner(monkeypatch,tmp_path):
    monkeypatch.setattr(lab,'HERE',tmp_path)
    monkeypatch.setattr(lab.subprocess,'run',lambda argv,**kwargs:lab.subprocess.CompletedProcess(argv,0,'123 /Users/new/RiderProjects/ai_RPG_test/build/tactics_lab_host\n',''))
    with pytest.raises(RuntimeError,match='ACTIVE'):lab.process_gate(wait=False)
    assert lab.read(tmp_path/'PROCESS_GATE.json')['matched'][0]['pid']==123


def test_prepare_excludes_v1_and_v2_entropy_and_keeps_inherited_checks(monkeypatch,tmp_path):
    cpp=tmp_path;here=cpp/'v3';v1=cpp/'v1';v2=cpp/'v2'
    for path in (here,v1/'raw',v2/'raw'):path.mkdir(parents=True)
    monkeypatch.setattr(lab,'CPP',cpp);monkeypatch.setattr(lab,'HERE',here)
    monkeypatch.setattr(lab,'RAW',here/'raw');monkeypatch.setattr(lab,'V1',v1);monkeypatch.setattr(lab,'V2',v2)
    lab.write(v1/'raw/SEED_LEDGER.json',dict(seeds=[101,102,103]))
    lab.write(v2/'raw/SEED_LEDGER.json',dict(drills={'D1':[104,105]},draws=[[dict(seed=106)]]))
    lab.write(v2/'DECLARATION.json',dict(ledger_sha256=lab.sha(v2/'raw/SEED_LEDGER.json')))
    parent=dict(status='PASS',declaration_sha256='old')
    monkeypatch.setattr(lab,'verify_parent',lambda:parent)
    monkeypatch.setattr(lab,'catalog',lambda:dict(POOL=[str(i) for i in range(19)]))
    monkeypatch.setattr(lab,'controller',lambda _:dict(params={'fixed':True}))
    monkeypatch.setattr(lab,'admit',lambda _:dict(binary='unchanged'))
    actual_read=lab.read
    monkeypatch.setattr(lab,'read',lambda p:dict(resonator={'fixed':True}) if str(p).endswith('B_best.json') else actual_read(p))
    actual_sha=lab.sha
    monkeypatch.setattr(lab,'sha',lambda p:actual_sha(p) if pathlib.Path(p).exists() else 'inherited-hash')
    # Force candidate collisions with both generations before new allocations.
    class Candidates:
        def __init__(self):self.values=iter(range(101,1000))
        def randrange(self,*args):return next(self.values)
    actual_random=lab.random.Random
    monkeypatch.setattr(lab.random,'Random',lambda seed:Candidates() if seed>2**32 else actual_random(seed))
    monkeypatch.setattr(lab.secrets,'token_hex',lambda _: 'f'*64)
    lab.prepare()
    ledger=actual_read(here/'raw/SEED_LEDGER.json')
    seeds=[n for group in ledger['drills'].values() for n in group]+ledger['series']+ledger['checks']+[d['seed'] for draws in ledger['draws'] for d in draws]
    assert len(seeds)==158 and len(set(seeds))==158 and not set(seeds)&set(range(101,107))
    assert 'v1/raw/SEED_LEDGER.json' in ledger['inventories'] and 'v2/raw/SEED_LEDGER.json' in ledger['inventories']
    assert actual_read(here/'CHECKS.json')==dict(parent,declaration_sha256=actual_sha(here/'DECLARATION.json'),inherited_from='s4_shape_lab_v1/CHECKS.json')
    assert actual_read(here/'DECLARATION.json')['binary']==dict(binary='unchanged')


def test_bare_system_python_in_repo_cwd_does_not_own_foreign_script(monkeypatch):
    monkeypatch.setattr(lab.subprocess,'run',lambda argv,**kwargs:lab.subprocess.CompletedProcess(argv,0,'p123\nn/Users/new/RiderProjects/ai_RPG_test\n',''))
    assert 'path' not in lab.classify_process(123,'python3 /Users/new/RiderProjects/astelia-hunte/medium_runner.py')


def test_bare_argument_file_resolves_in_process_cwd(monkeypatch,tmp_path):
    repo=tmp_path/'repo';repo.mkdir();(repo/'request.json').write_text('{}')
    monkeypatch.setattr(lab,'REPO_ROOT',repo.resolve())
    monkeypatch.setattr(lab.subprocess,'run',lambda argv,**kwargs:lab.subprocess.CompletedProcess(argv,0,'p123\nn'+str(repo)+'\n',''))
    assert 'path' in lab.classify_process(123,'/foreign/astelia_native --input request.json')
    assert 'path' not in lab.classify_process(123,'/foreign/astelia_native --url=https://example.com/input')


@pytest.mark.parametrize('executable_path,expected',[
    ('/Users/new/RiderProjects/ai_RPG_test/build/tactics_lab_host',True),
    ('/Users/new/RiderProjects/astelia-hunte/build/tactics_lab_host',False),
    ('/private/tmp/claude-501/-Users-new-RiderProjects-ai-RPG-test/job/tactics_lab_host',True),
])
def test_path_native_executable_uses_txt_not_cwd(monkeypatch,executable_path,expected):
    calls=[]
    def query(argv,**kwargs):
        calls.append(argv)
        return lab.subprocess.CompletedProcess(argv,0,'p123\nn'+executable_path+'\nn/Users/new/RiderProjects/ai_RPG_test/lib/other.dylib\n','')
    monkeypatch.setattr(lab.subprocess,'run',query)
    assert ('path' in lab.classify_process(123,'tactics_lab_host --metrics'))==expected
    assert calls==[['lsof','-a','-p','123','-d','txt','-Fn']]


def test_path_native_executable_lookup_failure_stops_gate(monkeypatch,tmp_path):
    monkeypatch.setattr(lab,'HERE',tmp_path)
    def query(argv,**kwargs):
        return lab.subprocess.CompletedProcess(argv,0,'123 astelia_native_v7 --metrics\n','') if argv[0]=='pgrep' else lab.subprocess.CompletedProcess(argv,1,'','')
    monkeypatch.setattr(lab.subprocess,'run',query)
    with pytest.raises(RuntimeError,match='UNAVAILABLE'):lab.process_gate(wait=False)
    assert lab.read(tmp_path/'PROCESS_GATE.json')['unresolved'][0]['reason']=='heavy process executable path unavailable'


@pytest.mark.parametrize('command',[
    '/Users/new/RiderProjects/ai_RPG_test/a=b/tactics_lab_host --metrics',
    '/foreign/astelia_native --input=/Users/new/RiderProjects/ai_RPG_test/a=b/request.json',
])
def test_literal_equals_in_process_paths_remains_intact(command):
    item=lab.classify_process(123,command)
    assert item['path'].startswith('/Users/new/RiderProjects/ai_RPG_test/a=b/')
