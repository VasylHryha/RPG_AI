"""Focused S0/S1 tests: fixtures and fake launches only, never native fights."""
import copy
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pytest
from fixtures import snapshot, threat
from schema import encode, check
from s1_public import intercept, support, reaction, retained_threats, oracle, encoded_view
from s1_metrics import chi2_quantile, spread, exchange, interpolate, measure, summarize
from s0_analysis import Conflicts
import s1_build
import s1_pilot


def test_actual_distance_intercept_support_and_motion():
    s=snapshot();s['threats']=[];gun=check(s);target=s['units'][-2];target.update(vx=0,vy=70)
    q,residual=intercept(gun,target)
    assert q[1]>target['y'] and residual<gun['splash']/4
    sup=support(s,target);assert len(sup['points'])==33 and sup['index'] is not None
    assert sup['radius']>gun['splash'] and math.dist(sup['lead'],q)<1e-10
    target['vx']=1000
    assert intercept(gun,target)[1]>gun['splash']/4
    gun['lob']=0
    with pytest.raises(ValueError):intercept(gun,target)


def test_encoded_oracle_omits_ninth_threat_and_preserves_masks():
    s=snapshot();s['threats']=[threat('own_shell',i+1) for i in range(8)]
    distant=threat('shell',9);distant.update(x=400,y=400,at=20);s['threats'].append(distant)
    x,_=encode(s);x=[__import__('struct').unpack('<f',__import__('struct').pack('<f',v))[0] for v in x]
    represented=encoded_view(s,x)
    assert len(represented['threats'])==8
    assert check(represented)['time_rate']==pytest.approx(1)
    assert all(q['kind']=='own_shell' for q in represented['threats'])
    labs,_=oracle(represented);assert len(labs)==5
    x2=copy.deepcopy(s);x2['fight']='metadata';x2['tick']=999
    assert oracle(encoded_view(x2,x))[0]==labs


def test_reaction_overflow_detects_goal_difference():
    s=snapshot();s['threats']=[];s['units'][0]['guard_until']=0
    assert not reaction(s)[0]
    q=threat('shell');q.update(x=400,y=400,at=s['t']+.8);s['threats']=[q]
    assert reaction(s)[0] and not reaction(s,[])[0]


def test_conflicts_and_empty_collision_coverage():
    c=Conflicts();x=[0.]*1008;c.add('test',x,[0,1,1,1,0],[True]*5);c.add('test',x,[0,1,1,1,2],[True]*5)
    r=c.report();assert r['test|exact|aim']['conflicting_inputs']==1
    assert r['test|exact|move']['conflicting_inputs']==0
    c=Conflicts();c.add('single',x,[0]*5,[True]*5)
    assert c.report()['single|exact|aim']['coverage']=='UNRESOLVED_NO_COLLISIONS'


def test_sd_inflation_quantiles_and_constant_mde():
    assert chi2_quantile(.05,9)==pytest.approx(3.325112843,rel=1e-8)
    r=spread(list(range(10)));assert r['sd_upper']>r['paired_sd']
    assert r['MDE_100']>r['ordinary_MDE_100']
    assert r['MDE_200']==pytest.approx(r['MDE_100']/math.sqrt(2))
    assert spread([0]*10)['MDE_100'] is None


def test_exchange_uses_ratio_totals_and_pseudovalues():
    pairs=[(dict(kills=i+1,deaths=i%3+1),dict(kills=i+2,deaths=(i+1)%3+1)) for i in range(10)]
    r=exchange(pairs);assert r['mean']==pytest.approx(sum(b['kills'] for a,b in pairs)/sum(b['deaths'] for a,b in pairs)-sum(a['kills'] for a,b in pairs)/sum(a['deaths'] for a,b in pairs))
    assert r['paired_sd']>0
    assert exchange([(dict(kills=10,deaths=0),dict(kills=10,deaths=1))]*10)['status']=='UNRESOLVED'


def test_interpolation_never_imputes_terminal_or_dead_focus():
    trace=[(0,{1:[0,0]}),(1,{1:[2,0]}),(2,{})]
    assert interpolate(trace,1,.5)==[1,0]
    assert interpolate(trace,1,1.5) is None
    assert interpolate(trace,1,3) is None


def test_generation_preserves_focus_and_existing_files():
    before={p:s1_build.sha(p) for p in (s1_build.HERE/'teacher.cpp',s1_build.HERE/'host.cpp',s1_build.HERE/'rpc.cpp')}
    v=s1_build.generate()
    assert 'scoredOrigins.at(best)' in v['s1_planner']
    assert 'w.units[q.gun.slot].id' in v['s1_planner']
    assert '\nPUBLIC_VIEW_HELPER\n' not in v['s1_host']
    assert before=={p:s1_build.sha(p) for p in before}


def test_definitions_and_seal_seed_pairs(tmp_path,monkeypatch):
    monkeypatch.setattr(s1_pilot,'ROOT',tmp_path/'pilot');monkeypatch.setattr(s1_pilot,'HERE',tmp_path)
    monkeypatch.setattr(s1_pilot,'pins',lambda:dict(design_commit='fixed'))
    monkeypatch.setattr(s1_pilot,'forbidden_seeds',lambda:(set(range(10000)),{}))
    inv=s1_pilot.seal();assert len(inv['rows'])==160 and len(set(inv['seeds']))==80
    assert sum(r['sample'] for r in inv['rows'])==20
    for cell in s1_pilot.CELLS:
        for pair in range(20):
            rows=[r for r in inv['rows'] if r['pilot_cell']==cell and r['pair']==pair]
            assert rows[0]['seed']==rows[1]['seed']
            a=rows[0]['request'];b=rows[1]['request'];assert a['roster']==b['roster']
            assert all(u['initial_prep']==0 for u in a['roster'])


def test_process_gate_is_fail_closed_and_local(monkeypatch,tmp_path):
    monkeypatch.setattr(s1_pilot,'ROOT',tmp_path)
    def unavailable(*a,**k):raise PermissionError('process discovery unavailable')
    monkeypatch.setattr(s1_pilot.gate.subprocess,'run',unavailable)
    old=s1_pilot.gate.GATE_PATH
    with pytest.raises(RuntimeError,match='UNAVAILABLE'):s1_pilot.clear(100)
    assert s1_pilot.gate.GATE_PATH==old and (tmp_path/'PROCESS_GATE.json').exists()


def test_completed_refuses_neighbor_or_raw_drift(tmp_path,monkeypatch):
    monkeypatch.setattr(s1_pilot,'ROOT',tmp_path);(tmp_path/'INVENTORY.json').write_text('{}')
    row=dict(fight='one',request={'fight':'one'});(tmp_path/'one.jsonl').write_text('raw')
    record=dict(inventory_sha256=s1_pilot.sha(tmp_path/'INVENTORY.json'),request=row['request'],raw_sha256=s1_pilot.sha(tmp_path/'one.jsonl'))
    (tmp_path/'one.receipt.json').write_text(json.dumps(record));assert s1_pilot.completed(row)==record
    (tmp_path/'one.jsonl').write_text('changed')
    with pytest.raises(RuntimeError,match='drift'):s1_pilot.completed(row)


def test_historical_seed_exclusion_outside_slice(tmp_path,monkeypatch):
    here=tmp_path/'tactical'/'cpp'/'slice';here.mkdir(parents=True)
    past=tmp_path/'tactical'/'cpp'/'s4_shape_lab_v4'/'raw';past.mkdir(parents=True)
    p=past/'SEED_LEDGER.json';p.write_text(json.dumps(dict(mechanism=[dict(seed=4060879288)],pilot_seeds=[4000000001])))
    monkeypatch.setattr(s1_pilot,'HERE',here);monkeypatch.setattr(s1_pilot,'ROOT',here/'pilot')
    seeds,files=s1_pilot.forbidden_seeds()
    assert {4060879288,4000000001}.issubset(seeds) and str(p) in files


def test_miss_shadow_flight_times_and_root_physical_join():
    s=snapshot();s['threats']=[];s['t']=0;s['fight']='pilot';s['tick']=1
    # Static focus at x=650. A 20px shape intentionally shifts the shell.
    focus=101;selfpos=[400,400];requested=[650,420];auto=[650,400];lob=300
    native_at=math.dist(selfpos,requested)/lob
    def event(stage,value,tick=1,unit=1,cast=1,decision=1):return dict(stage=stage,value=value,unit=unit,tick=tick,cast_tick=cast,decision_tick=decision,volley=1)
    refresh=dict(focus=focus,requested=requested,autonomous=auto,autonomous_snapped=auto,self=selfpos,t=0,lob=lob,splash=40,shape=[0,20],residual=0,plan=1)
    events=[event('s1_joint',dict(eligible=2,feasible=2,changed_assignment=True)),event('s1_refresh',refresh),event('launch',dict(aim=requested,born=0,landing_at=native_at))]
    frames=[dict(fight='pilot',tick=1,joint=s,post_joint=s,events=events)]
    for tick in range(2,32):
        v={**s,'tick':tick,'t':(tick-1)/30};frames.append(dict(fight='pilot',tick=tick,joint=v,post_joint=v,events=[]))
    frames.append(dict(terminal=True,native_shell_totals=dict(enemy_damage=0,friendly_damage=0,resolved_shells=1),own_alive=2,own_guns_alive=2,enemy_alive=2,time=1,strict_win=False))
    r=measure(frames,dict(fight='pilot'))
    assert r['miss'][0]['raw_difference']==pytest.approx(20)
    assert r['miss'][0]['shape_subtracted_raw_miss']==pytest.approx(0)
    assert r['miss'][0]['times']['raw']>r['miss'][0]['times']['autonomous']
    assert r['on_state_changed_physical_decisions']==1
    assert r['enemy_dash_events']==0
    assert r['fire_rates']['starts_per_start_opportunity'] is None
    assert r['outcome']=='timeout'
    broken=copy.deepcopy(frames);broken[0]['events'][2]['tick']=2
    assert measure(broken,dict(fight='pilot'))['missing_miss']['launch_after_first_release_opportunity']==1


def test_no_projection_without_measured_twenty_fights(tmp_path,monkeypatch):
    monkeypatch.setattr(s1_pilot,'inventory',lambda:dict(rows=[dict(sample=True)]*20))
    monkeypatch.setattr(s1_pilot,'completed',lambda r:None)
    with pytest.raises(RuntimeError,match='sample required'):s1_pilot.projection()


def test_native_boundary_adapter_preserves_imported_modules():
    import schema
    import labels
    from s0_arithmetic import math as native, opportunities
    original=schema.opportunities
    assert native.hypot(900-580.8211916071846,360-382.9104402607728)==320
    s=snapshot();s['threats']=[];me=check(s);me.update(x=580.8211916071846,y=382.9104402607728)
    target=s['units'][-2];target.update(x=900,y=360)
    assert opportunities(s,target,[900,360])[0]
    assert schema.opportunities is original and labels.join.__globals__['math'] is __import__('math')


def test_contestedness_uses_same_state_physical_response_not_chaos():
    def row(i,wrapper=False):
        return dict(deaths=1+i%2,gun_deaths=1,kills=2+i%3,damage=100+i*10+(i%4-2 if wrapper else 0),clear_time=150,cleared=False,own_roster=4,enemy_roster=2,enemy_hp=400,counts=dict(eligible_multi=10,command_multi=10 if wrapper else 0,changed_assignment_multi=10 if wrapper else 0),support=dict(unforced=20,bad_residual=0,bad_snap=0,forced=0,center_illegal=0),miss=[],missing_miss={},plans=[1] if wrapper else [],physical_patterns={1:[[1,[650+i,400]]]},impact_patterns={},enemy_dash_events=0,on_state_changed_physical_decisions=0,on_state_changed_impact_count=0)
    pairs=[(row(i),row(i,True)) for i in range(10)]
    result=summarize(pairs,False)
    assert result['assignment_change_rate']==1 and result['physical_response_rate']==0
    assert not result['admitted'] and result['stops'][0]['yes']
    for _,b in pairs:b['on_state_changed_physical_decisions']=1
    result=summarize(pairs,False)
    assert result['physical_response_rate']==.1 and result['admitted']
    assert result['axes']['clear_time']['status']=='UNRESOLVED'
    assert result['final_N'] in (100,200)
    assert sum(v['fights'] for v in result['outcome_splits']['T-unit-alone'].values())==10
    assert result['outcome_splits']['T-unit+wrapper']['timeout']['launches_per_start_opportunity'] is None
    assert result['axes']['damage']['planning_harm_halfwidth']['100']>0
