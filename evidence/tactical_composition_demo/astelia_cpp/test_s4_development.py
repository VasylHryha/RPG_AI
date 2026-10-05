"""S4 sampling, pairing, accounting and configuration negative controls."""
import json
import random
import pytest
import s4_development as S
from s3_runner import request, POOL, ELITE_NO_ROLLOUT


def test_p23_preserves_every_doctrine_and_disables_planning():
    for side in (0,1):
        for opp in POOL:
            r=request(dict(arm='resonator',setting='s4_p23',opponent=opp,controlledSide=side))
            enemy=r['options']['ai'][1-side]
            assert 'level' not in enemy
            assert enemy['skills']==ELITE_NO_ROLLOUT and enemy['lookahead'] is None
            assert enemy['skills']['artyRollout'] is None
            if side==0:assert r['opponent']==opp
            else:assert enemy['brain']==(opp if opp in ('alone','storm','wolfpack') else 'formation')
            assert r['options']['ai'][side]=={'controller':'resonator','params':{}}


def test_settings_are_fixed_and_compatible():
    r=request(dict(arm='morale',opponent='novice',setting='s4_melee10'))
    assert r['options']['army']==dict(melee=10,ranged=0,artillery=0)
    for setting,opp in [('s4_p23','regular'),('s4_melee10','regular'),('s4_full_head','line'),('bogus','novice'),('s4_anomaly_regular_alone','novice')]:
        with pytest.raises(ValueError):request(dict(arm='morale',opponent=opp,setting=setting))


def test_pairs_join_ids_and_fail_on_omitted_or_wrong_seed():
    assert S.paired({'a':1,'b':4},{'b':3,'a':2})=={'a':-1,'b':1}
    with pytest.raises(ValueError):S.paired({'seed1':1},{'seed2':1})
    assert not S.accept({'a':1,'b':1})
    assert S.accept({'a':1.1,'b':1.1})
    assert not S.accept({'a':-10,'b':20})


def test_sampler_is_bounded_reproducible_and_exercises_rates():
    for arm in S.BOUNDS:
        p=S.defaults(arm)
        a=S.sample(arm,p,random.Random(510050),0)
        assert a==S.sample(arm,p,random.Random(510050),0)
        assert all(lo<=c[k]<=hi for c in a for k,(lo,hi) in S.BOUNDS[arm].items())
        if arm=='resonator':assert any(c['omega_melee']!=0 for c in a)


def test_splits_have_no_overlap_and_doctrines_balanced():
    led=json.loads((S.ROOT/'S4_SEED_LEDGER.json').read_text())
    allseeds=set()
    for stage in 'ABC':
        tune={seed for r in range(8) for _,seed,_ in S.battles(stage,r)}
        valid={seed for _,seed,_ in S.battles(stage,validation=True)}
        assert not tune&valid and not allseeds&(tune|valid)
        allseeds|=tune|valid
        lo,hi=led['ranges'][stage]['tuning'];assert min(tune)==lo and max(tune)==hi
    counts={opp:sum(b[0]==opp for r in range(8) for b in S.battles('C',r)) for opp in POOL}
    assert max(counts.values())-min(counts.values())<=1


def test_equal_budget_with_cache_hits_and_rank_pruning(tmp_path):
    class Fake:
        output=tmp_path
        budget=dict.fromkeys(S.BOUNDS,0)
        def evaluate(self,arm,params,bs,tuning=False):
            if tuning:self.budget[arm]+=2*len(bs)
            # All ties: acceptance must fail, but full equal budget must still be used.
            return {json.dumps(b):0 for b in bs}
    b=Fake()
    for stage in 'ABC':
        for arm in S.BOUNDS:assert S.tune(b,stage,arm,S.defaults(arm))==S.defaults(arm)
    assert b.budget==dict.fromkeys(S.BOUNDS,7680)
    logs=json.loads((tmp_path/'C_resonator_tuning.json').read_text())
    assert len(logs)==8 and all(len(r['candidates'])==8 for r in logs)
    assert sum(c['fights'] for c in logs[0]['candidates'])==256


def test_source_identity_and_native_admission():
    assert S.verify_sources()['verification_status']=='VERIFIED'
    assert S.admit(S.BINARY)['engine']=='native'


def test_replay_packaging_keeps_fields_and_is_self_contained(tmp_path):
    import base64
    import gzip
    payload=dict(spec={'arm':'morale'},summary={},frames=[dict(step=3,state=dict(t=.1,debug={},units=[dict(id=1,team=0,role='melee',x=2,y=3,hp=4,alive=True,target=9,controllerState=.2,commitment=.2,cd=1,debug=dict(r=5,maxhp=10,ep=2))]))])
    S.package_replay(tmp_path,'fight',payload)
    decoded=json.loads(gzip.decompress((tmp_path/'fight.replay.json.gz').read_bytes()))
    unit=decoded['frames'][0]['state']['units'][0]
    assert unit['debug']==dict(r=5,maxhp=10) and unit['target']==9 and unit['controllerState']==.2
    assert 'cd' not in unit
    html=(tmp_path/'fight.html').read_text()
    assert '/*REPLAY_DATA*/null' not in html and '<script src=' not in html
    assert base64.b64encode((tmp_path/'fight.replay.json.gz').read_bytes()).decode() in html
