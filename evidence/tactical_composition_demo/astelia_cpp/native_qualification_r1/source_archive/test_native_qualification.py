"""Fail closed on omitted coverage, incomplete work and invalid trace authority."""
import copy
import pytest
from qualify_native import assess
from verify_native import trace_invariants
from result_cache import Engine
def evidence():
    groups={name:dict(speed_up=10,count=1,samples={label:[dict(wall_seconds=seconds,user_seconds=seconds,system_seconds=0,execution=dict(cache_hits=0,executed_fights=1)) for _ in range(2)] for label,seconds in [('js',10),('cpp',1)]}) for name in ('basic50','elite','elite-fast','artillery-rollout')}
    return dict(coverage=dict(status='NATIVE_COVERAGE_PASSED',counts={'completed':623},traces=[{}]*20,determinism=[{'equal':True}]*20),costs=dict(status='MATCHED_COSTS_PASSED',costs={k:dict(speed_up=4) for k in ('geometry','network','fork_playout')}),work=dict(status='WORK_AUDIT_PASSED',groups={k:{} for k in groups}),benchmark=dict(status='TIMING_PASSED_AWAITING_WORK_AND_CORRECTNESS_REVIEW',groups=groups),tests=dict(exit_code=0))
def test_bound_evidence_components_are_all_required():
    data=evidence();assert assess(**data)=='ENGINEERING_READY'
    for key in ('coverage','costs','work','benchmark'):
        changed=copy.deepcopy(data);changed[key]['status']='RUNNING';assert assess(**changed)!='ENGINEERING_READY'
    changed=copy.deepcopy(data);changed['tests']['exit_code']=1;assert assess(**changed)=='TESTS_FAILED'
def test_high_timing_ratio_cannot_cover_missing_requests_or_cache_use():
    data=evidence();data['coverage']['counts']={'completed':622};assert assess(**data)=='INCOMPLETE_COVERAGE'
    data=evidence();data['benchmark']['groups']['elite']['samples']['cpp'][0]['execution']['cache_hits']=1;assert assess(**data)=='CACHED_OR_MISSING_WORK'
    data=evidence();data['benchmark']['groups']['elite']['samples']['cpp'][0]['wall_seconds']=4;assert assess(**data)=='UNSTABLE_TIMING'
def trace():
    request=dict(mode='alone',trace=True,options=dict(scenario='mirror',duration=.2,dt=.1))
    unit=dict(id=1,team=0,role='melee',x=100,y=100,hp=10,cd=0,alive=True,target=None)
    frames=[dict(step=i,state=dict(t=i*.1,units=[dict(unit)])) for i in range(3)]
    final=dict(mode='alone',melee=0,ranged=0,artillery=0,total=0,wasted=0,monsterDeaths=0,hunterKills=0,aliveSeconds=.2,enemyDamage=0,survivors=1,enemySurvivors=1,t=.2)
    return request,frames+[final]
def test_trace_authority_negative_controls():
    req,rows=trace();assert trace_invariants(req,rows)==3
    changed=copy.deepcopy(rows);changed[1]['state']['units'][0]['target']=999
    with pytest.raises(ValueError,match='world-local'):trace_invariants(req,changed)
    changed=copy.deepcopy(rows);changed[1]['state']['units'][0]['hp']=11
    with pytest.raises(ValueError,match='health increased'):trace_invariants(req,changed)
    changed=copy.deepcopy(rows);changed[1]['state']['units'][0]['debug']=dict(prep=0,ep=11,epMax=10,r=1,maxhp=10)
    with pytest.raises(ValueError,match='energy'):trace_invariants(req,changed)
def test_invalid_encoding_does_not_start_or_leak_host():
    from result_cache import ROOT
    engine=Engine('js',['node',str(ROOT/'js_host.cjs')],cache_dir=None)
    with pytest.raises(ValueError):engine.fight({'value':float('nan')})
    assert engine.process is None;engine.close()
