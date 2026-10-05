import gzip
import json
import pathlib
import pytest
import s4_amended as A
from result_schema import validate_summary
from result_cache import Cache
from test_result_cache import SUMMARY


def extended():
    return dict(SUMMARY,controllerFailures=[0,0],controllerStatus='completed',crossTeamDealt=[10,12],crossTeamTaken=[12,10],friendlyDealt=[0,0],friendlyTaken=[0,0])


def test_extended_schema_is_closed_and_failure_status_consistent():
    row=extended();assert validate_summary(row)=='completed'
    row['controllerFailures'][0]=1
    with pytest.raises(ValueError):validate_summary(row)
    row['controllerStatus']='controller_failure';assert validate_summary(row)=='controller_failure'
    for field,value in [('crossTeamDealt',[1]),('controllerFailures',[.1,0]),('crossTeamTaken',[float('nan'),1])]:
        r=extended();r[field]=value
        with pytest.raises(ValueError):validate_summary(r)
    r=extended();r['extra']=1
    with pytest.raises(ValueError):validate_summary(r)


def test_extended_cache_round_trip_and_identity_partition(tmp_path):
    req=dict(mode='alone',s3=True,options=dict(duration=SUMMARY['t'],dt=.1,scenario='mirror'))
    c=Cache(tmp_path,dict(binary='a',sources='pinned'));c.put(req,[extended()]);assert c.load(req)==[extended()]
    assert Cache(tmp_path,dict(binary='b',sources='pinned')).load(req) is None


def test_normalization_optimizer_bounds_and_population():
    for arm in A.BOUNDS:
        start=A.defaults(arm);assert A.knobs(arm,A.normalized(arm,start))==start
        A.optimizer.stage='A';es=A.optimizer(arm,start);xs=es.ask();assert len(xs)==16
        assert all(0<=v<=1 for x in xs for v in x)
        es.tell(xs,[sum((v-.2)**2 for v in x) for x in xs]);assert es.countiter==1
        assert len(es.ask())==16


def test_common_seed_panels_and_100_validation_clusters():
    all_tuning=set();all_valid=set()
    for stage in 'ABC':
        t=A.battles(stage,'tuning');v=A.battles(stage,'validation');assert len(t)==19
        seeds={b[1] for b in t};valid={b[1] for b in v};assert not seeds&valid
        assert not all_tuning&seeds and not all_valid&valid;all_tuning|=seeds;all_valid|=valid
        assert all(sum(b[0]==opp and b[2]==setting for b in v)==100 for opp,_,setting in v)
    assert 38+16*16*38==9766
    assert set(b[0] for b in A.battles('C','tuning'))==set(A.POOL)


def test_fresh_and_cached_native_extended_summary_are_identical(tmp_path):
    spec=dict(arm='nearest',params={},opponent='novice',seed=414000000,setting='s4_melee10',swapSides=False)
    engine=A.identity('cpp',[str(A.BINARY),'--metrics'])
    task=(engine,tmp_path,[spec])
    first=A.execute(task)[0];second=A.execute(task)[0]
    assert not first['cache_hit'] and second['cache_hit']
    assert first['summary']==second['summary'] and first['S']==second['S']
    assert first['metrics']==second['metrics']
    assert first['summary']['controllerStatus']=='completed'


def test_contract_drift_stops_before_further_fights(tmp_path):
    p=tmp_path/'request.md';p.write_text('approved protocol')
    expected={str(p):A.sha(p)};A.check_inputs(expected)
    p.write_text('changed protocol')
    with pytest.raises(RuntimeError,match='input changed'):A.check_inputs(expected)
