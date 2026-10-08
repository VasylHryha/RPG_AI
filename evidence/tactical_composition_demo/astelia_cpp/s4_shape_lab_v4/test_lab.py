"""Focused synthetic fixtures and mocked controls; never run a combat world."""
import copy
import gzip
import importlib.util
import json
import pathlib
import subprocess
import sys
from types import SimpleNamespace
import pytest

HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
# Use these exact sibling modules even if pytest collected another lab earlier.
for name in ('build','requests','metrics','lab','report','replays'):
    existing=sys.modules.get(name)
    if existing and pathlib.Path(getattr(existing,'__file__','/')).parent!=HERE:
        sys.modules.pop(name)
import lab
import build
import metrics
import requests
import report


@pytest.fixture
def local(tmp_path,monkeypatch):
    raw=tmp_path/'raw'
    raw.mkdir()
    for module in (lab,report):
        monkeypatch.setattr(module,'HERE',tmp_path)
        monkeypatch.setattr(module,'RAW',raw)
    monkeypatch.setattr(lab,'identity',lambda:dict(pool=[f'tactic{i}' for i in range(19)]))
    lab.write(tmp_path/'DECLARATION.json',{'test':'synthetic'})
    return tmp_path


def test_requests_share_world_and_disable_diagnostics():
    pool=['line','box']
    for group,tactic in [('D2',None),('C3','regular'),('C3','box')]:
        a=requests.drill_request(group,requests.ARMS[0],tactic,314159,1,pool)
        b=requests.drill_request(group,requests.ARMS[1],tactic,314159,1,pool)
        assert a['labScenario']==b['labScenario']
        assert a['options']['seed']==b['options']['seed']
        assert a['options']['ai'][1]==b['options']['ai'][1]
        assert a['options']['ai'][0]['params']==b['options']['ai'][0]['params']
        assert b['labReact']=={'shadow':False}
        for req in (a,b):
            assert req['killerTelemetry']
            assert not any(req[k] for k in ('trace','debug','decisionTrace','diagnostics','decisionDiagnostics','attributionDiagnostics'))
            assert req['options']['duration']==150


def test_reduced_series_heals_keeps_common_enemy_and_excludes_dead():
    survivors=[u for u in requests.cohort() if u['cohort_id'] in (2,5,13,42)]
    draw=dict(seed=12345,orientation=1,tactic='line')
    a=requests.series_request(requests.ARMS[0],draw,['line'],survivors)
    b=requests.series_request(requests.ARMS[1],draw,['line'],survivors)
    assert a['labScenario']==b['labScenario']
    assert len(a['labScenario']['sides'][0])==4
    assert all(u['hp_fraction']==1 for u in a['labScenario']['sides'][0])
    assert a['labAbilities']==b['labAbilities']=='off'
    assert all(p['skills']['abilities']=='off' for p in a['options']['ai'])


def test_overlay_removes_heavy_output_and_collectors():
    sources=build.derived_sources()
    host=sources['lean_host.cpp']
    observer=sources['lean_observer.cpp']
    assert '"v7Telemetry"' not in host
    assert 'react_v1::telemetry(w)' not in host
    assert 'lethalGunSupport' not in host
    assert 'observer.entries)' not in host
    assert 'e.otherGuns' not in observer and 'event.support.push' not in observer
    assert 'observerV1' in host and 'observer.dodges' in host and 'observer.launches' in host
    assert 'void movement(const World&,uint32_t,Vec2){}' in observer
    assert 'observer_v1_observer_v1.o' in pathlib.Path(build.__file__).read_text()


def unit(i,team,role=1,hp=100):
    return [i,team,role,100,400,hp,10,300,0,False,0,0,0,None]


def stream_fixture(path,rows):
    with gzip.open(path,'wt') as stream:
        for row in rows: stream.write(json.dumps(row)+'\n')


def observer(step,t,units,launches=None,damage=None,dodges=None):
    return dict(observerV1=True,step=step,t=t,units=units,launches=launches or [],damage=damage or [],dodges=dodges or [])


def damage(source,target,dealt=12,t=1):
    return dict(source=source,sourceTeam=1,sourceRole='artillery',target=target,targetTeam=0,targetRole='ranged',dealt=dealt,t=t,died=False)


def test_zero_hit_shells_censored_shells_and_dodge_ticks(tmp_path):
    path=tmp_path/'stream.gz'
    launches=[[51,1,1,100,400,0,1,60,False,False],
              [52,1,1,100,400,0,1,60,False,False],
              [53,1,1,100,400,0,5,60,False,False]]
    rows=[observer(0,0,[unit(1,0),unit(2,0),unit(51,1,2)],launches),
          observer(30,1,[unit(1,0),unit(2,0)],damage=[damage(51,1),damage(51,1,3),damage(51,2,5)],dodges=[[1,0,0,0,1,1],[51,1,0,0,1,1]]),
          dict(survivors=2,enemySurvivors=0,t=1,controllerFailures=[0,0])]
    stream_fixture(path,rows)
    stats,survivors=metrics.measure(path)
    assert stats['win'] and stats['own_dodges']==1
    assert stats['enemy_shells_landed']==2 and stats['enemy_shells_unresolved']==1
    assert stats['own_units_hit_per_enemy_shell']==1
    assert stats['damage_taken_per_enemy_shell']==10
    assert len(survivors)==2


def test_no_shell_denominator_and_nonwin_timeout(tmp_path):
    path=tmp_path/'stream.gz'
    stream_fixture(path,[observer(0,0,[unit(1,0)]),dict(survivors=1,enemySurvivors=0,t=150)])
    stats,_=metrics.measure(path)
    assert not stats['win'] and stats['damage_taken_per_enemy_shell'] is None


def test_metrics_fail_on_heavy_rows_and_ambiguous_impacts(tmp_path):
    path=tmp_path/'stream.gz'
    stream_fixture(path,[dict(reactV1=True)])
    with pytest.raises(RuntimeError,match='heavy'): metrics.measure(path)
    launches=[[51,1,1,100,400,0,1,60,False,False]]*2
    stream_fixture(path,[observer(0,0,[unit(1,0)],launches),observer(30,1,[unit(1,0)],damage=[damage(51,1)])])
    with pytest.raises(RuntimeError,match='ambiguous'): metrics.measure(path)


def stats(win=True,lost=3,shells=2,dodges=5):
    return dict(win=win,own_lost=lost,own_dodges=dodges,enemy_shells_landed=shells,
                own_shell_hit_units=2 if shells else 0,enemy_shell_damage=10 if shells else 0,
                own_units_hit_per_enemy_shell=2/shells if shells else None,
                damage_taken_per_enemy_shell=10/shells if shells else None,
                unassigned_enemy_artillery_damage=0,enemy_shells_unresolved=0,t_end=50)


def record(arm,pair,**kwargs):
    return dict(meta=dict(arm=arm,pair=pair),stats=stats(**kwargs))


def test_pair_missing_arm_and_denominator_are_not_imputed():
    rows=[record('forcedP16',0,shells=0),record('forcedP16+react',0,lost=1),record('forcedP16',1,win=False)]
    data=metrics.paired(rows)
    assert data['n']==1 and data['unmatched_pairs']==1
    assert data['differences']['own_lost']==dict(n=1,mean=-2)
    assert data['differences']['damage_taken_per_enemy_shell']['n']==0
    summary=metrics.summarize(rows)
    assert summary['own_losses_on_wins']['n']==2
    assert summary['own_losses_on_nonwins']['n']==1


def test_plan_pairs_fixed_draws_and_c3_bound(local):
    ledger=dict(mechanism=[dict(seed=100+i,orientation=i%2) for i in range(10)],
                outcome=[dict(seed=200+i,orientation=i%2,tactic='regular') for i in range(200)])
    lab.write(lab.RAW/'SEED_LEDGER.json',ledger)
    assert len(list(lab.plan('mechanism')))==20
    for look in (50,100,200):
        cells=list(lab.plan('outcome',look))
        assert len(cells)==2*look
        for a,b in zip(cells[::2],cells[1::2]):
            assert a[1]['labScenario']==b[1]['labScenario']
            assert a[2]['seed']==b[2]['seed'] and a[2]['pair']==b[2]['pair']
    assert len(lab.samples_for('outcome'))==40
    assert len(lab.samples_for('mechanism'))==2
    assert len(lab.samples_for('series'))==2


def test_gate_blocks_outcome_and_series_without_read(local):
    with pytest.raises((RuntimeError,FileNotFoundError)): lab.ensure_stage('outcome',50)
    with pytest.raises((RuntimeError,FileNotFoundError)): lab.ensure_stage('series',50)


def test_sequential_gate_stop_and_series_order(local,monkeypatch):
    decisions={('mechanism',None):'continue',('outcome',50):'continue',('outcome',100):'stop'}
    monkeypatch.setattr(lab,'require_review',lambda stage,look=None:dict(decision=decisions[(stage,look)]))
    lab.ensure_stage('outcome',100)
    with pytest.raises(RuntimeError,match='stopped'): lab.ensure_stage('outcome',200)
    with pytest.raises(RuntimeError,match='read C3'): lab.ensure_stage('series',50)
    lab.write(local/'OUTCOME_LOOK_50_READ.json',dict(decision='continue'))
    with pytest.raises(RuntimeError,match='finish sequential'): lab.ensure_stage('series',50)
    lab.write(local/'OUTCOME_LOOK_100_READ.json',dict(decision='stop'))
    lab.ensure_stage('series',50)
    decisions[('mechanism',None)]='stop'
    with pytest.raises(RuntimeError,match='mechanism stopped'): lab.ensure_stage('outcome',50)


def test_review_binds_complete_summary_and_cannot_overwrite(local,monkeypatch):
    summary=dict(complete=True,n=10)
    path=local/'MECHANISM_SUMMARY.json'
    lab.write(path,summary)
    monkeypatch.setattr(lab,'stage_summary',lambda *a:(path,summary))
    lab.review('mechanism',50,'continue','observed mock dodges')
    assert lab.require_review('mechanism')['reader']=='Claude'
    with pytest.raises(RuntimeError,match='already fixed'):lab.review('mechanism',50,'stop','changed mind')
    lab.write(path,dict(complete=True,n=9))
    with pytest.raises(RuntimeError,match='summary'):lab.require_review('mechanism')


def test_outcome_calibration_is_blocked_before_execute(local,monkeypatch):
    calls=[]
    monkeypatch.setattr(lab,'compute_attempt',lambda *a:calls.append(a))
    with pytest.raises((RuntimeError,FileNotFoundError)):lab.calibrate('outcome',50)
    assert not calls


def test_process_gate_foreign_scoping_and_missing_discovery(local,monkeypatch):
    assert lab.scoped_path('/Users/new/RiderProjects/ai_RPG_test-lookalike/run.py') is None
    assert lab.scoped_path(str(lab.CPP/'s4_shape_lab_v4/build/tactics_react_host_v4')) is not None
    monkeypatch.setattr(lab.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=1,stdout='',stderr=''))
    assert lab.process_gate(wait=False)['status']=='CLEAR'
    monkeypatch.setattr(lab.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=2,stdout='',stderr='denied'))
    with pytest.raises(RuntimeError,match='UNAVAILABLE'):lab.process_gate(wait=False)
    assert 'tactics_react_host' in lab.HEAVY_PATTERN


def test_process_lock_refuses_second_runner(local):
    with lab.execution_lock():
        with pytest.raises(RuntimeError,match='another v4'):
            with lab.execution_lock():pass


def test_cap_uses_exact_mutable_bytes_outside_identity(local,monkeypatch):
    monkeypatch.setattr(lab,'CAP_PATH',local/'CAP.json')
    monkeypatch.setattr(lab,'CPP',local)
    assert lab.local_cap()['cap_seconds']==3600
    # relative_to(CPP) is a display label, mimic production root.
    monkeypatch.setattr(lab,'CPP',local)
    payload=b'{"cap_seconds":10800,"approved_by":"owner","date":"2026-10-08"}\n'
    lab.CAP_PATH.write_bytes(payload)
    assert lab.local_cap()['cap_file_sha256']==lab.hashlib.sha256(payload).hexdigest()
    lab.write(lab.CAP_PATH,dict(cap_seconds=True,approved_by='owner',date='today'))
    with pytest.raises(RuntimeError,match='invalid'):lab.local_cap()


def test_cap_interrupt_archives_only_incomplete_and_resume_reuses(local,monkeypatch):
    def failed(tag,*a):
        lab.write(lab.RAW/(tag+'_request.json'),dict(seed=1),exclusive=True)
        raise subprocess.TimeoutExpired('mock',1)
    monkeypatch.setattr(lab,'execute_cell',failed)
    with pytest.raises(TimeoutError,match='preserved'):lab.execute('new',{}, {},deadline=999999999)
    assert not (lab.RAW/'new_request.json').exists()
    archives=list((lab.RAW/'interrupted').glob('*/INTERRUPTION.json'))
    assert len(archives)==1 and lab.read(archives[0])['retry_allowed']
    lab.write(lab.RAW/'done_COMPLETE.json',{'immutable':True})
    monkeypatch.setattr(lab,'execute_cell',lambda *a:{'reused':True})
    assert lab.execute('done',{}, {},deadline=999999999)=={'reused':True}
    assert lab.read(lab.RAW/'done_COMPLETE.json')=={'immutable':True}


def test_projection_scales_horizon_and_excludes_completed(local,monkeypatch):
    cells=[('done',{},dict(arm=ARMS[0],opponent='regular')),('pending',{},dict(arm=ARMS[0],opponent='regular'))]
    monkeypatch.setattr(lab,'plan',lambda *a:iter(cells))
    sample=dict(seconds=10,stats=dict(t_end=50),meta=cells[0][2])
    p=lab.projection('outcome',50,{'done':sample},[sample],10)
    assert p['remaining_fights_max']==1 and p['remaining_projected_seconds']==pytest.approx(36)
    with pytest.raises(RuntimeError,match='timing'):lab.projection('outcome',50,{},[dict(sample,seconds=0)],10)

ARMS=requests.ARMS


def test_series_carryover_stops_first_nonwin_without_resurrecting(local,monkeypatch):
    lab.write(lab.RAW/'SEED_LEDGER.json',dict(draws=[[dict(seed=i+1,tactic='line',orientation=0) for i in range(10)]]))
    monkeypatch.setattr(lab,'identity',lambda:dict(pool=['line']))
    calls=[]
    def fake(tag,req,meta,*args):
        calls.append((req,meta))
        # Keep cohort #2 melee and #12 ranged after first fight, then lose.
        left=[dict(id=2,role='melee'),dict(id=12,role='ranged')] if len(calls)==1 else [dict(id=11,role='ranged')]
        return dict(tag=tag,stats=dict(win=len(calls)==1),survivors=left)
    monkeypatch.setattr(lab,'execute',fake)
    result=lab.run_series('forcedP16',0,99999999)
    assert result['streak']==1 and result['fight_reached']==2
    assert calls[1][1]['cohort_before']==[2,12]
    assert result['fights'][1]['cohort_after']==[12]
    assert len(calls[1][0]['labScenario']['sides'][0])==2
    assert all(u['hp_fraction']==1 for u in calls[1][0]['labScenario']['sides'][0])


def test_streak_is_paired_by_series_despite_unequal_reach():
    rows=[]
    for arm,count in zip(ARMS,(1,2)):
        for f in range(1,count+1):
            row=record(arm,0,win=f<count)
            row['meta'].update(series=0,fight=f,tactic='line',seed=f,orientation=0,units_before=50,roles_before=dict(melee=10,ranged=30,artillery=10))
            rows.append(row)
    data=report.series_data(rows)
    assert data['paired_streak_difference']==dict(direction='react minus base',n=1,mean=1)
    assert data['paired_reached_fights']['n']==1
    assert data['paired_reached_fights']['unmatched_pairs']==1
    assert not data['complete']


def test_no_series_calibration_until_c3_finished(local,monkeypatch):
    monkeypatch.setattr(lab,'require_review',lambda *a:dict(decision='continue'))
    calls=[]
    monkeypatch.setattr(lab,'compute_attempt',lambda *a:calls.append(a))
    with pytest.raises(RuntimeError,match='read C3'):lab.calibrate('series',50)
    assert not calls


def test_selected_replay_can_render_measured_stream(local,monkeypatch):
    import replays
    monkeypatch.setattr(replays,'HERE',local)
    monkeypatch.setattr(replays,'RAW',lab.RAW)
    tag='C3_forcedP16_p000'
    path=lab.RAW/(tag+'.jsonl.gz')
    stream_fixture(path,[observer(0,0,[unit(1,0),unit(51,1,2)]),
                         observer(30,1,[unit(1,0)]),dict(survivors=1,enemySurvivors=0,t=1)])
    measured,_=metrics.measure(path)
    rows=[dict(tag=tag,meta=dict(group='C3',arm='forcedP16',pair=0),stats=measured,
               summary=dict(survivors=1,enemySurvivors=0,t=1))]
    replays.render_selected(rows)
    data=lab.read(local/'C3_forcedP16_replays.json')
    assert len(data['fights'])==1 and data['fights'][0]['win']
    assert len(data['fights'][0]['frames'])==2
    # Declared selection excludes arbitrary later C3 fights, even if available.
    later=dict(rows[0],meta=dict(group='C3',arm='forcedP16',pair=2))
    replays.render_selected([later])
    assert lab.read(local/'REPLAY_INDEX.json')['groups']==[]


def test_immutable_completion_recomputes_measurements_and_rejects_drift(local):
    tag='D2_forcedP16_p000'
    req={'synthetic':True}
    meta=dict(stage='mechanism',arm='forcedP16',pair=0)
    request_path=lab.RAW/(tag+'_request.json')
    claim_path=lab.RAW/(tag+'_CLAIM.json')
    stderr_path=lab.RAW/(tag+'_stderr.log')
    raw_path=lab.RAW/(tag+'.jsonl.gz')
    terminal=dict(survivors=1,enemySurvivors=0,t=1,controllerFailures=[0,0])
    stream_fixture(raw_path,[observer(0,0,[unit(1,0)]),terminal])
    measured,survivors=metrics.measure(raw_path)
    lab.write(request_path,req)
    lab.write(claim_path,dict(meta=meta,request_sha256=lab.sha(request_path),declaration_sha256=lab.sha(local/'DECLARATION.json')))
    lab.write(stderr_path,dict(executed_fights=1))
    result=dict(tag=tag,meta=meta,summary=terminal,stats=measured,survivors=survivors,
                native_metrics=dict(executed_fights=1),seconds=1,
                declaration_sha256=lab.sha(local/'DECLARATION.json'),claim_sha256=lab.sha(claim_path),
                request_sha256=lab.sha(request_path),raw_sha256=lab.sha(raw_path),stderr_sha256=lab.sha(stderr_path))
    lab.write(lab.RAW/(tag+'_COMPLETE.json'),result)
    assert lab.verified_record(tag,req,meta)==result
    with pytest.raises(RuntimeError,match='metadata drift'):lab.verified_record(tag,{'other':True},meta)
    with raw_path.open('ab') as stream: stream.write(b'tamper')
    with pytest.raises(RuntimeError,match='raw/stderr drift'):lab.verified_record(tag)


def test_unclosed_attempt_and_over_cap_run_refuse_execution(local,monkeypatch):
    lab.write(local/'RUN_mechanism_ATTEMPT_synthetic.json',dict(status='RUNNING',seconds=0))
    calls=[]
    with pytest.raises(RuntimeError,match='unclosed'):
        lab.compute_attempt('RUN','mechanism',dict(cap_seconds=10),lambda d:calls.append(d))
    assert not calls
    monkeypatch.setattr(lab,'ensure_stage',lambda *a:None)
    monkeypatch.setattr(lab,'calibration_receipt',lambda *a:dict(sample_tags=[],wall_seconds=1))
    monkeypatch.setattr(lab,'records_for',lambda *a:{})
    monkeypatch.setattr(lab,'local_cap',lambda:dict(cap_seconds=10))
    monkeypatch.setattr(lab,'projection',lambda *a:dict(remaining_projected_seconds=11))
    lab.write(local/'CALIBRATION_mechanism.json',dict(synthetic=True))
    monkeypatch.setattr(lab,'compute_attempt',lambda *a:calls.append(a))
    with pytest.raises(RuntimeError,match='exceeds cap'):lab.run('mechanism',50)
    assert not calls and lab.read(local/'RUN_GATE_mechanism.json')['status']=='REFUSED'
