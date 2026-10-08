"""Focused native fixtures + synthetic paired staging/report checks; no fights."""
import copy
import gzip
import json
import pathlib
import subprocess
import sys
import time
from types import SimpleNamespace
import pytest
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
for name in ('build','requests','metrics','lab','report','replays'):
    existing=sys.modules.get(name)
    if existing and pathlib.Path(getattr(existing,'__file__','/')).parent!=HERE:sys.modules.pop(name)
import build,requests,metrics,lab,report,replays

@pytest.fixture
def local(tmp_path,monkeypatch):
    raw=tmp_path/'raw';raw.mkdir()
    for module in (lab,report,replays):
        monkeypatch.setattr(module,'HERE',tmp_path);monkeypatch.setattr(module,'RAW',raw)
    declaration=dict(pool=['line'],timing=dict(mode='base',k=1,radius=400))
    monkeypatch.setattr(lab,'identity',lambda:declaration)
    monkeypatch.setattr(lab,'SELECTED_ARM','V2')
    lab.write(tmp_path/'DECLARATION.json',declaration)
    return tmp_path

def test_native_fixtures():
    payload=json.loads((HERE.parent/'s4_v7c/THETA_ORIGIN.json').read_text())
    payload['planner_states']=json.loads((HERE/'PLANNER_STATES.json').read_text())
    pool=json.loads((HERE.parent/'s4_shape_lab_v4/DECLARATION.json').read_text())['pool'];timing=dict(mode='base',k=1,radius=400)
    payload['requests']=[requests.drill_request(g,a,'regular',731,0,pool,timing) for g in ('D1','V2D2','D5','RD','C3') for a in requests.ARMS]
    payload['requests'] += [requests.series_request(a,dict(seed=732,orientation=1,tactic='line'),pool,requests.cohort()[:3],timing) for a in requests.ARMS]
    results=[]
    for name in ('shape_fixture','adapter_fixture'):
        binary=HERE/'build'/name;build.admit(binary);started=time.monotonic()
        result=subprocess.run([str(binary)],input=json.dumps(payload)+'\n',text=True,capture_output=True,timeout=60)
        (HERE/f'{name.upper()}.stdout.log').write_text(result.stdout);(HERE/f'{name.upper()}.stderr.log').write_text(result.stderr)
        assert result.returncode==0,result.stderr
        rows=[json.loads(s) for s in result.stdout.splitlines()]
        assert rows[-1]['status']=='PASS' and rows[-1]['fights']==0
        results.append(dict(name=name,seconds=time.monotonic()-started,**rows[-1]))
    lab.write(HERE/'NATIVE_FIXTURES.json',dict(status='PASS',fixtures=results,fights=0))

@pytest.mark.parametrize('group',('D1','V2D2','D5','RD','C3'))
def test_world_pairing(group):
    timing=dict(mode='base',k=1,radius=400)
    reqs=[requests.drill_request(group,a,'regular',314,1,['line'],timing) for a in requests.ARMS]
    assert all(r['labScenario']==reqs[0]['labScenario'] and r['options']==reqs[0]['options'] for r in reqs)
    assert all(r['labBattery']==timing and r['labAbilities']=='off' for r in reqs)
    assert all(not any(r[k] for k in ('trace','debug','diagnostics','decisionDiagnostics','attributionDiagnostics','decisionTrace')) for r in reqs)

def test_series_cohort_pairing():
    survivors=[u for u in requests.cohort() if u['cohort_id'] in (2,13,42)]
    reqs=[requests.series_request(a,dict(seed=789,orientation=1,tactic='line'),['line'],survivors,dict(mode='base',k=1,radius=400)) for a in requests.ARMS]
    assert all(r['labScenario']==reqs[0]['labScenario'] for r in reqs)
    assert all(u['hp_fraction']==1 for u in reqs[0]['labScenario']['sides'][0])

def ledger():return dict(mechanism={g:[dict(seed=100+i,orientation=i%2,group=g,tactic='regular' if g=='RD' else None) for i in range(10 if g in ('D1','V2D2') else 20)] for g in ('D1','V2D2','D5','RD')},outcome=[dict(seed=1000+i,orientation=i%2,tactic='regular') for i in range(200)])
def test_shared_base_and_e1_receipts_identical(local,monkeypatch):
    lab.write(lab.RAW/'SEED_LEDGER.json',ledger());plans={}
    for arm in requests.ARMS[1:]:
        monkeypatch.setattr(lab,'SELECTED_ARM',arm)
        plans[arm]=list(lab.plan('outcome',50))
        cells=list(lab.plan('mechanism'));assert len(cells)==(60 if arm=='E1+R1' else 40)
        assert len({t for t,_,_ in cells})==len(cells)
    bases=[[r for r in rows if r[2]['arm']=='base'] for rows in plans.values()]
    assert all(rows==bases[0] for rows in bases)
    assert [r for r in plans['E1'] if r[2]['arm']=='E1']==[r for r in plans['E1+R1'] if r[2]['arm']=='E1']
    monkeypatch.setattr(lab,'SELECTED_ARM','R1');a=[r for r in lab.plan('mechanism') if r[2]['arm']=='base']
    monkeypatch.setattr(lab,'SELECTED_ARM','E1+R1');b=[r for r in lab.plan('mechanism') if r[2]['arm']=='base'];assert a==b

def test_timing_slot_fixed_before_claims(local):
    lab.configure_timing('central_sync',1,400,'actual synthetic V1 reading')
    assert lab.timing()['mode']=='central_sync'
    with pytest.raises(RuntimeError,match='immutable'):lab.configure_timing('base',1,400,'changed')
    (local/'TIMING_SELECTION.json').unlink();(lab.RAW/'x_CLAIM.json').write_text('{}')
    with pytest.raises(RuntimeError,match='already opened'):lab.configure_timing('base',1,400,'default')

def test_precedence_overlay_public_projection_and_no_live_doc_pins():
    s=build.derived_sources();assert 'shapes_v6::augment(*this)' in s['react.cpp'];assert 'shapes_v6::threats(w,side,out)' in s['react.cpp']
    assert 'shapes_v6::shot(w,i,p)' in s['react_rules.cpp']
    assert s['react_combat.cpp'].index('gamePrep(w,i,dt*w.state[i].timeRate)')<s['react_combat.cpp'].index('shapes_v6::geometry(w)')
    assert 'react_v1::telemetry(w)' not in s['lean_host.cpp'] and 'event.support.push' not in s['lean_observer.cpp']
    text=(HERE/'lab.py').read_text();assert "CPP.parent/'SHAPE_LAB_SPEC.md'" not in text and "'docs/decisions/" not in text and 'Downloads' not in text

def unit(i,team,role=1):return [i,team,role,100,400,100,10,300,0,False,0,0,0,None]
def stream(path,rows):
    with gzip.open(path,'wt') as f:
        for row in rows:f.write(json.dumps(row)+'\n')
def obs(t,units,**extra):return dict(observerV1=True,t=t,step=round(t*30),units=units,launches=[],damage=[],shapeV6=[],shotsV6=[],**extra)
def test_all_fight_axes_and_ratios(tmp_path):
    p=tmp_path/'light.gz';r=obs(1,[unit(1,0,2),unit(51,1)]);r['launches']=[[1,51,0,100,400,0,1,45,False,False]];r['damage']=[dict(source=1,sourceRole='artillery',sourceTeam=0,target=52,targetRole='ranged',targetTeam=1,dealt=20,t=1,died=True)]
    stream(p,[obs(0,[unit(1,0,2),unit(2,0),unit(51,1),unit(52,1)]),r,dict(t=1,survivors=1,enemySurvivors=1)])
    s,_=metrics.measure(p);assert s['own_lost']==1 and s['enemy_kills']==1 and not s['win'];assert s['damage_per_shell']==20 and s['targets_per_shell']==1
    record=dict(meta=dict(arm='base',pair_key='C3:0'),stats=s)
    summary=metrics.summarize([record]);assert summary['own_deaths_per_fight']['mean']==1 and summary['exchange_rate']==1 and summary['own_losses_on_losses']['n']==1
    copied=copy.deepcopy(record);copied['meta']['arm']='E1';copied['stats']['own_lost']=0
    pairs=metrics.paired([record,copied]);axis=next(iter(pairs.values()))['axis_plot'];assert abs(axis['own_deaths_saved']['mean'])==1

def test_zero_death_denominator_timeout_and_missing_stream(tmp_path):
    p=tmp_path/'light.gz';stream(p,[obs(0,[unit(1,0)]),obs(150,[unit(1,0)]),dict(t=150,survivors=1,enemySurvivors=0)])
    s,_=metrics.measure(p);assert not s['win'] and s['timeout'] and s['kills_per_own_death'] is None
    stream(p,[{'reactV1':True}])
    with pytest.raises(RuntimeError,match='heavy'):metrics.measure(p)

def test_rotation_stage_requires_e1_and_series_survivor(local,monkeypatch):
    monkeypatch.setattr(lab,'SELECTED_ARM','R1');monkeypatch.setattr(lab,'require_review',lambda *args:dict(decision='stop'))
    with pytest.raises(RuntimeError,match='E1'):lab.ensure_stage('mechanism',50)
    monkeypatch.setattr(lab,'SELECTED_ARM','E1');lab.write(local/'OUTCOME_E1_LOOK_50_READ.json',{})
    monkeypatch.setattr(lab,'require_review',lambda *args:dict(decision='stop',survivor=False))
    with pytest.raises(RuntimeError,match='mechanism stopped'):lab.ensure_stage('series',50)
    monkeypatch.setattr(lab,'require_review',lambda stage,*args:dict(decision='continue' if stage=='mechanism' else 'stop',survivor=False))
    with pytest.raises(RuntimeError,match='survivor'):lab.ensure_stage('series',50)
    monkeypatch.setattr(lab,'require_review',lambda stage,*args:dict(decision='continue' if stage=='mechanism' else 'stop',survivor=True))
    lab.ensure_stage('series',50)

def test_cap_and_repository_process_gate(local,monkeypatch):
    cap=local/'CAP.json';monkeypatch.setattr(lab,'CAP_PATH',cap);monkeypatch.setattr(lab,'CPP',local)
    assert lab.local_cap()['cap_seconds']==3600
    cap.write_text('{"cap_seconds":10800,"approved_by":"owner","date":"2026-10-08"}')
    assert lab.local_cap()['cap_file_sha256']==lab.sha(cap)
    monkeypatch.setattr(lab.subprocess,'run',lambda *args,**kwargs:SimpleNamespace(returncode=0,stdout='121 /foreign/tactics_react_host_v6\n',stderr=''))
    assert lab.process_gate(wait=False)['status']=='CLEAR'
    monkeypatch.setattr(lab.subprocess,'run',lambda *args,**kwargs:SimpleNamespace(returncode=2,stdout='',stderr='unavailable'))
    with pytest.raises(RuntimeError,match='UNAVAILABLE'):lab.process_gate(wait=False)

def test_resume_and_all_twenty_cells(local,monkeypatch):
    (lab.RAW/'x_COMPLETE.json').write_text('{}');sentinel=object();monkeypatch.setattr(lab,'verified_record',lambda *args:sentinel)
    assert lab.execute_cell('x',{}, {}) is sentinel
    monkeypatch.setattr(lab,'records_for',lambda *args:{})
    monkeypatch.setattr(lab,'identity',lambda:dict(pool=[f't{i}' for i in range(19)]))
    outcome=report.stage_data('outcome',50);assert len(outcome['per_tactic'])==20 and not outcome['complete']
    series=report.series_data([],('base','V2'));assert series['primary']=='streak' and not series['complete']
