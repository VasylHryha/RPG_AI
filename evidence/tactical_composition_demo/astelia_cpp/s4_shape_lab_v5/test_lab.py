"""Focused fixtures and mocked gates only. No fights or coreStep."""
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
for name in ('build','requests','metrics','lab','report','replays'):
    existing=sys.modules.get(name)
    if existing and pathlib.Path(getattr(existing,'__file__','/')).parent!=HERE:sys.modules.pop(name)
import lab,build,requests,metrics,report,replays

@pytest.fixture
def local(tmp_path,monkeypatch):
    raw=tmp_path/'raw';raw.mkdir()
    for module in (lab,report,replays):
        monkeypatch.setattr(module,'HERE',tmp_path);monkeypatch.setattr(module,'RAW',raw)
    monkeypatch.setattr(lab,'identity',lambda:dict(pool=['line']*19))
    lab.write(tmp_path/'DECLARATION.json',{'synthetic':True})
    return tmp_path


def test_native_unit_fixtures_and_request_construction():
    pool=json.loads((HERE.parent/'s4_shape_lab_v4/DECLARATION.json').read_text())['pool']
    payload=json.loads((HERE.parent/'s4_v7c/THETA_ORIGIN.json').read_text())
    payload['central_states']=json.loads((HERE/'CENTRAL_STATES.json').read_text())
    payload['requests']=[requests.drill_request(g,a,'regular',731,0,pool) for g in ('D1','V1D2','C3') for a in requests.ARMS]
    payload['requests'] += [requests.series_request(a,dict(seed=732,orientation=1,tactic='line'),pool,requests.cohort()[:3]) for a in requests.ARMS]
    results=[]
    for name in ('battery_fixture','adapter_fixture'):
        binary=HERE/'build'/name;build.admit(binary)
        result=subprocess.run([str(binary)],input=json.dumps(payload)+'\n',text=True,capture_output=True,timeout=30)
        (HERE/f'{name.upper()}.stdout.log').write_text(result.stdout);(HERE/f'{name.upper()}.stderr.log').write_text(result.stderr)
        assert result.returncode==0,result.stderr
        rows=[json.loads(s) for s in result.stdout.splitlines()]
        assert rows[-1]['status']=='PASS' and rows[-1]['fights']==0
        results.append(dict(name=name,**rows[-1]))
    lab.write(HERE/'NATIVE_FIXTURES.json',dict(status='PASS',fixtures=results,fights=0))


@pytest.mark.parametrize('group',('D1','V1D2','C3'))
def test_arms_paired_world_and_heavy_diagnostics_off(group):
    reqs=[requests.drill_request(group,a,'regular',314,1,['line']) for a in requests.ARMS]
    assert all(r['labScenario']==reqs[0]['labScenario'] for r in reqs)
    assert all(r['options']['ai']==reqs[0]['options']['ai'] for r in reqs)
    for r in reqs:
        assert r['options']['seed']==314 and r['killerTelemetry']
        assert not any(r[k] for k in ('trace','debug','diagnostics','decisionDiagnostics','attributionDiagnostics','decisionTrace'))
    if group=='V1D2':
        assert reqs[0]['options']['ai'][1]['controller']=='dummy_advance_fire'
        assert all(u['role']=='ranged' for u in reqs[0]['labScenario']['sides'][1])


def test_grid_declared_and_requests_reject_extra_knobs():
    assert len(requests.GRID)==9
    for k,r in requests.GRID:assert requests.drill_request('C3',requests.ARMS[2],'regular',11,0,['line'],(k,r))['labBattery']==dict(mode='battery_oscillator',k=k,radius=r)
    with pytest.raises(ValueError):requests.drill_request('D1','unknown',None,11,0,['line'])
    with pytest.raises(ValueError):requests.drill_request('D1',requests.ARMS[2],None,11,0,['line'],(3,400))


def test_series_heals_survivors_and_preserves_pair_draws():
    survivors=[u for u in requests.cohort() if u['cohort_id'] in (2,13,42)]
    reqs=[requests.series_request(a,dict(seed=789,orientation=1,tactic='line'),['line'],survivors) for a in requests.ARMS]
    assert all(r['labScenario']==reqs[0]['labScenario'] for r in reqs)
    assert reqs[0]['labAbilities']=='off' and len(reqs[0]['labScenario']['sides'][0])==3
    assert all(u['hp_fraction']==1 for u in reqs[0]['labScenario']['sides'][0])


def test_native_overlay_seams_and_light_streams():
    s=build.derived_sources()
    assert '"v7Telemetry"' not in s['lean_host.cpp'] and 'react_v1::telemetry(w)' not in s['lean_host.cpp']
    assert 'event.support.push' not in s['lean_observer.cpp']
    assert 'battery_v1::oscillator(w);' in s['react_combat.cpp']
    assert s['react_combat.cpp'].index('gamePrep(w,i,dt*w.state[i].timeRate)')<s['react_combat.cpp'].index('battery_v1::oscillator(w);')
    assert 'battery_v1::fired(w,i);' in s['react_combat.cpp']
    assert 'battery_v1::launch(w,i,sh);' in s['react_rules.cpp']
    assert 'battery_v1::launch(w,i,sh);' in s['v5_abilities.cpp']
    assert 'battery_v1::landing(w,shell);' in s['react_combat.cpp']
    assert 'constexpr double pi=tau/2;' in s['central_gate.cpp']


def unit(i,team,role=1):return [i,team,role,100,400,100,10,300,0,False,0,0,0,None]
def obs(t,units,launches=None,damage=None,audit=None,battery=None):return dict(observerV1=True,step=round(t*30),t=t,units=units,launches=launches or [],damage=damage or [],dodges=[],launchAudit=audit or [],battery=battery or [])
def stream(path,rows):
    with gzip.open(path,'wt') as f:
        for r in rows:f.write(json.dumps(r)+'\n')

def test_mechanism_denominators_spread_idle_and_low_gun_intervals(tmp_path):
    p=tmp_path/'stream.gz'
    launches=[[1,51,0,100,400,0,1,45,False,False],[2,51,0,100,400,0,1.1,45,False,False],[1,51,0,100,400,0,5,45,False,False]]
    audit=[dict(type='launch',source=l[0],born=l[5],at=l[6],volley=1 if l[6]<2 else 2,exposed=[51,52]) for l in launches]
    landing=[dict(type='landing',source=l[0],born=l[5],at=l[6],eligible=1,escaped=1,censored=1) for l in launches[:2]]
    damage=[dict(source=1,sourceTeam=0,sourceRole='artillery',target=52,targetTeam=1,targetRole='ranged',dealt=20,t=1,died=True)]
    stream(p,[obs(0,[unit(1,0,2),unit(2,0,2),unit(51,1),unit(52,1)],launches,audit=audit),obs(1.1,[unit(1,0,2),unit(2,0,2),unit(51,1)],damage=damage,audit=landing,battery=[[1,0,4,1,2,1,False,1,'bound'],[2,0,4,1,3,1,False,1,'bound']]),dict(t=1.1,survivors=2,enemySurvivors=1)])
    s,_=metrics.measure(p)
    assert s['own_shells_landed']==2 and s['own_shells_unresolved']==1
    assert s['enemy_dodge_launch_exposed']==4 and s['enemy_dodge_success']==.5 and s['enemy_dodge_censored']==2
    assert s['hits_per_own_shell']==.5 and s['shells_per_kill']==2
    assert s['landing_spread_s']==pytest.approx(.1) and s['multi_shell_volleys']==1 and s['single_shell_volleys']==1
    assert s['idle_seconds_per_gun']==2.5 and s['gun_seconds']==pytest.approx(2.2)
    assert s['fired_shells_per_gun_minute']==pytest.approx(180/2.2)
    assert json.loads(json.dumps(s))==s


def test_metrics_null_and_timeout_are_not_benefit(tmp_path):
    p=tmp_path/'stream.gz';stream(p,[obs(0,[unit(1,0,2)]),obs(150,[unit(1,0,2)]),dict(t=150,survivors=1,enemySurvivors=0)])
    s,_=metrics.measure(p)
    assert not s['win'] and s['enemy_dodge_success'] is None and s['landing_spread_s'] is None and s['shells_per_kill'] is None
    assert s['low_gun_behaviour']['1']['gun_seconds']==150


def test_metrics_missing_audit_or_heavy_stream_fails(tmp_path):
    p=tmp_path/'stream.gz';stream(p,[{'reactV1':True}])
    with pytest.raises(RuntimeError,match='heavy'):metrics.measure(p)
    stream(p,[obs(0,[unit(1,0,2)],launches=[[1,51,0,0,0,0,1,45,False,False]]),dict(t=1,survivors=1,enemySurvivors=0)])
    with pytest.raises(RuntimeError,match='coverage'):metrics.measure(p)


def test_plan_grid_reuses_baseline_and_fixed_draws(local):
    ledger=dict(mechanism=[dict(seed=100+i,orientation=i%2,group='D1' if i<10 else 'V1D2',guns=1 if i%10==8 else 2 if i%10==9 else 10) for i in range(20)],outcome=[dict(seed=1000+i,orientation=i%2,tactic='regular') for i in range(200)])
    lab.write(lab.RAW/'SEED_LEDGER.json',ledger)
    cells=list(lab.plan('mechanism'))
    assert len(cells)==220 and len({t for t,_,_ in cells})==220
    for pair in range(20):
        rows=[(req,m) for _,req,m in cells if m['pair']==pair]
        assert len(rows)==11 and len({m['seed'] for _,m in rows})==1
        assert all(req['labScenario']==rows[0][0]['labScenario'] for req,_ in rows)
    assert len(lab.samples_for('mechanism'))==22
    assert len({lab.category(m) for _,_,m in cells})==22


def test_pick_is_mechanism_only_once_and_identity_bound(local,monkeypatch):
    summary=dict(complete=True,test='mechanism')
    monkeypatch.setattr(lab,'stage_summary',lambda *args:(local/'MECHANISM_SUMMARY.json',summary))
    lab.write(local/'MECHANISM_SUMMARY.json',summary)
    lab.pick(1,400,'actual synthetic rationale')
    assert lab.selected_knobs()==(1,400)
    lab.pick(1,400,'actual synthetic rationale')
    with pytest.raises(RuntimeError,match='immutable'):lab.pick(.5,200,'changed pick')
    lab.write(local/'MECHANISM_SUMMARY.json',dict(complete=True,test='changed'))
    with pytest.raises(RuntimeError,match='drift'):lab.selected_knobs()


def test_incomplete_mechanism_and_open_outcomes_block_pick(local,monkeypatch):
    monkeypatch.setattr(lab,'stage_summary',lambda *args:(local/'MECHANISM_SUMMARY.json',dict(complete=False)))
    with pytest.raises(RuntimeError,match='complete mechanism'):lab.pick(1,400,'rationale')
    summary=dict(complete=True);lab.write(local/'MECHANISM_SUMMARY.json',summary)
    monkeypatch.setattr(lab,'stage_summary',lambda *args:(local/'MECHANISM_SUMMARY.json',summary))
    (lab.RAW/'C3_claim.json').write_text('{}')
    with pytest.raises(RuntimeError,match='outcome already'):lab.pick(1,400,'rationale')


def test_stage_gate_requires_mechanism_pick_and_previous_look(local,monkeypatch):
    monkeypatch.setattr(lab,'require_review',lambda *args:dict(decision='stop'))
    with pytest.raises(RuntimeError,match='mechanism stopped'):lab.ensure_stage('outcome',50)
    monkeypatch.setattr(lab,'require_review',lambda *args:dict(decision='continue'))
    with pytest.raises(FileNotFoundError):lab.ensure_stage('outcome',50)
    monkeypatch.setattr(lab,'selected_knobs',lambda:(1,400))
    lab.ensure_stage('outcome',50)
    lab.write(local/'OUTCOME_LOOK_50_READ.json',dict(decision='stop'))
    with pytest.raises(RuntimeError,match='earlier look'):lab.ensure_stage('outcome',100)


def test_cap_snapshots_exact_owner_file(local,monkeypatch):
    cap=local/'CAP.json';monkeypatch.setattr(lab,'CAP_PATH',cap);monkeypatch.setattr(lab,'CPP',local)
    assert lab.local_cap()['cap_seconds']==3600
    cap.write_text('{"cap_seconds": 10800, "approved_by":"owner", "date":"2026-10-08"}\n')
    monkeypatch.setattr(lab,'CPP',local)
    result=lab.local_cap();assert result['cap_seconds']==10800 and result['cap_file_sha256']==lab.sha(cap)


def test_repository_gate_ignores_foreign_and_stops_unavailable(local,monkeypatch):
    monkeypatch.setattr(lab.subprocess,'run',lambda *args,**kwargs:SimpleNamespace(returncode=0,stdout='121 /foreign/tactics_react_host_v5\n',stderr=''))
    assert lab.process_gate(wait=False)['status']=='CLEAR'
    monkeypatch.setattr(lab.subprocess,'run',lambda *args,**kwargs:SimpleNamespace(returncode=2,stdout='',stderr='unavailable'))
    with pytest.raises(RuntimeError,match='UNAVAILABLE'):lab.process_gate(wait=False)


def test_projection_accounts_all_grid_categories_and_cap(local,monkeypatch):
    metas=[dict(stage='mechanism',group=g,arm=a,variant=v,opponent=None) for g in ('D1','V1D2') for a,v in [(requests.ARMS[0],None),(requests.ARMS[1],None),*[(requests.ARMS[2],lab.grid_name(x)) for x in requests.GRID]]]
    jobs=[(str(i),{},m) for i,m in enumerate(metas)]
    monkeypatch.setattr(lab,'plan',lambda *args:iter(jobs))
    samples=[dict(meta=m,seconds=2,stats=dict(t_end=150)) for m in metas]
    result=lab.projection('mechanism',200,{},samples,8)
    assert result['remaining_fights_max']==22 and result['remaining_projected_seconds']>0


def test_resume_does_not_execute_successful_cell(local,monkeypatch):
    (lab.RAW/'x_COMPLETE.json').write_text('{}')
    sentinel=object();monkeypatch.setattr(lab,'verified_record',lambda *args:sentinel)
    assert lab.execute_cell('x',{}, {}) is sentinel


def test_series_primary_summary_pairs_all_three_arms(local):
    # Empty preparation is incomplete, with no fabricated outcomes/streaks.
    data=report.series_data([])
    assert not data['complete'] and all(a['n_series']==0 for a in data['arms'].values())
    assert len(data['paired_streak_difference'])==3


def test_series_streak_summary_roundtrip_uses_text_keys(local):
    sample={f:0 for f in metrics.FIELDS}
    sample.update(own_shells=0,own_shells_landed=0,own_shells_unresolved=0,hits=0,artillery_kills=0,enemy_dodge_eligible=0,enemy_dodge_launch_exposed=0,enemy_dodge_censored=0,gun_seconds=0,idle_seconds=0,multi_shell_volleys=0,single_shell_volleys=0,unassigned_own_artillery_damage=0,low_gun_behaviour={})
    records=[dict(tag=a,meta=dict(arm=a,series=0,fight=1,tactic='line',units_before=50,roles_before=dict(melee=10,ranged=30,artillery=10)),stats=copy.deepcopy(sample)) for a in requests.ARMS]
    data=report.series_data(records)
    assert all(d['streak_distribution']=={'0':1} for d in data['arms'].values())
    assert json.loads(json.dumps(data))==data
