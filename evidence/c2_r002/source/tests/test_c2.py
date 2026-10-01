"""Focused numerical contracts and evaluator negative controls; no recorded panel."""
from dataclasses import replace
import json
import numpy as np
import pytest

from geomind.c2_network import ConductanceNetwork, GRID_EDGES, Settings, digest
from geomind.c2_reference import equilibrium, gradient, finite_difference, direct_local_update

HASH=digest({'fixture':'C2 development only; never final panel'})


@pytest.fixture(scope='module',autouse=True)
def bind_contracts(record_testsuite_property):
    from tools import gate
    before=gate.fingerprint()
    record_testsuite_property('c2_fingerprint',before)
    yield
    assert gate.fingerprint()==before


def test_analytic_and_grid_equilibria_synchronous_bound_and_failures():
    g=np.array([.7,1.3]); x=(.2,.8)
    state=ConductanceNetwork(g,HASH,edges=((0,1),(1,2)),nodes=3,inputs=(0,2),output=1)
    answer=state.query(x)
    assert answer['status']=='OK'
    assert answer['output']==pytest.approx((g[0]*x[0]+g[1]*x[1])/(sum(g)+.01),abs=1e-9)
    assert answer['cost']['bound_edges']==2
    old=state.conductances; result=state.learn(x,.4)
    assert result['status']=='PASS'
    assert result['nudged'][1]==pytest.approx((old[0]*x[0]+old[1]*x[1]+.05*.4)/(sum(old)+.01+.05),abs=1e-9)
    for seed in (81001,81002,81003):
        g=np.random.default_rng(seed).uniform(.5,1.5,24)
        state=ConductanceNetwork(g,HASH)
        expected=equilibrium(g,GRID_EDGES,16,(0,3),x,10)
        answer=state.query(x)
        assert answer['status']=='OK' and answer['cost']['max_force']<1e-9
        assert answer['activity']==pytest.approx(expected,abs=1e-7)
        assert answer['cost']['force_edges']==24*(answer['cost']['sweeps']+1)
        one=ConductanceNetwork(g,HASH,replace(Settings(),max_sweeps=1))
        before=one.export(); result=one.learn(x,.6)
        assert result['status']=='NOT_CONVERGED' and one.export()==before
        degree=np.zeros(16)
        for value,(a,b) in zip(g,GRID_EDGES): degree[a]+=value; degree[b]+=value
        old=np.zeros(16); old[[0,3]]=x; force=.01*old
        for value,(a,b) in zip(g,GRID_EDGES):
            current=value*(old[a]-old[b]); force[a]+=current; force[b]-=current
        force[[0,3]]=0
        expected=old-.25/(2*degree.max()+.01)*force
        assert result['free']==pytest.approx(expected,abs=1e-15)
    assert state.query((float('nan'),.2))['status']=='INVALID_STATE'
    # Finite extreme inputs may overflow or exhaust the sweep cap; either is an
    # explicit refusal. Finiteness alone does not require arithmetic overflow.
    before=state.export(); extreme=state.query((1e308,-1e308))
    assert extreme['status'] in ('INVALID_STATE','NOT_CONVERGED') and extreme['output'] is None and state.export()==before


def test_same_old_geometry_update_sign_factor_gradient_and_feedback():
    g=np.random.default_rng(81004).uniform(.5,1.5,24); x=(.3,.9); y=.25
    state=ConductanceNetwork(g,HASH)
    result=state.learn(x,y)
    assert result['status']=='PASS' and result['cost']['phases']==2
    assert result['free']==pytest.approx(equilibrium(g,GRID_EDGES,16,(0,3),x,10),abs=1e-7)
    assert result['nudged']==pytest.approx(equilibrium(g,GRID_EDGES,16,(0,3),x,10,beta=.05,y=y),abs=1e-7)
    assert state.conductances==pytest.approx(direct_local_update(g,GRID_EDGES,16,(0,3),x,10,y),abs=1e-8)
    analytic=gradient(g,GRID_EDGES,16,(0,3),x,10,y)
    assert analytic==pytest.approx(finite_difference(g,GRID_EDGES,16,(0,3),x,10,y),abs=2e-10)
    errors=[]
    for beta in (.05,.005,.0001):
        small=ConductanceNetwork(g,HASH,replace(Settings(),beta=beta,tolerance=1e-12))
        assert small.learn(x,y)['status']=='PASS'
        direction=(g-small.conductances)/.01
        errors.append(np.linalg.norm(direction-analytic))
        if beta==.0001:
            assert np.dot(direction,analytic)/(np.linalg.norm(direction)*np.linalg.norm(analytic))>.999
    assert errors[2]<errors[1]<errors[0]
    disabled=ConductanceNetwork(g,HASH); before=disabled.export()
    assert disabled.learn(x,y,feedback=False)['status']=='PASS' and disabled.export()==before
    large=ConductanceNetwork(g,HASH,replace(Settings(),eta=1e6))
    assert large.learn(x,y)['status']=='PASS'
    assert large.conductances.min()>=.05 and large.conductances.max()<=5
    assert np.any((large.conductances==.05)|(large.conductances==5))


def test_freeze_clone_restore_no_target_permutation_and_causal_edge():
    g=np.random.default_rng(81005).uniform(.5,1.5,24); state=ConductanceNetwork(g,HASH)
    x=(.2,.8); before=state.export(); answer=state.query(x)
    assert state.export()==before
    with pytest.raises(TypeError): state.query(x,y=.3)
    clone=state.clone(); clone.learn(x,.3)
    assert clone.export()!=before and state.export()==before
    restored=ConductanceNetwork.load(before)
    assert restored.export()==before and restored.query(x)['output']==answer['output']
    with pytest.raises(RuntimeError): restored.learn(x,.3)
    r=json.loads(before); r['conductances'][0]=9
    with pytest.raises(ValueError): ConductanceNetwork.load(json.dumps(r))
    perm=np.random.default_rng(81006).permutation(16).tolist()
    mapped=ConductanceNetwork(g,HASH,edges=tuple((perm[a],perm[b]) for a,b in GRID_EDGES),
                              inputs=(perm[0],perm[3]),output=perm[10])
    assert mapped.query(x)['output']==pytest.approx(answer['output'],abs=1e-12)
    derivative=gradient(g,GRID_EDGES,16,(0,3),x,10,answer['output']-1)
    e=int(np.argmax(np.abs(derivative))); perturbed=g.copy(); perturbed[e]+=.01
    shifted=ConductanceNetwork(perturbed,HASH).query(x)['output']-answer['output']
    assert abs(shifted)>1e-6 and shifted*derivative[e]>0


def test_manifest_evaluator_failures_and_controls(tmp_path):
    from geomind.run_c2 import validate_manifest, score_answers, check_c1_acceptance, summarize, safe_evaluate_trial
    from pathlib import Path
    manifest=json.loads((Path(__file__).resolve().parents[1]/'experiments/c2_manifest.json').read_text())
    validate_manifest(manifest); check_c1_acceptance()
    for key,value in (('epochs',99),('initialization_seeds',manifest['initialization_seeds'][:-1]),('splits',{'train':100,'validation':50,'test':100})):
        bad=dict(manifest); bad[key]=value
        with pytest.raises(ValueError): validate_manifest(bad)
    assert score_answers([{'status':'NOT_CONVERGED','output':None}],[.2])['mse'] is None
    assert score_answers([{'status':'OK','output':float('nan')}],[.2])['status']=='ASSERTION_FAILURE'
    assert score_answers([{'status':'OK','output':1e308}],[.2])['status']=='ASSERTION_FAILURE'
    assert score_answers([], [.2])['status']=='ASSERTION_FAILURE'
    good=score_answers([{'status':'OK','output':.3}],[.2]); assert good['mse']==pytest.approx(.01)
    assert summarize([],manifest)['implementation_status']=='BLOCKED'
    # One epoch through the real caller on disjoint development seeds verifies
    # complete receipt serialization/retention without rehearsing final worlds.
    dev=dict(manifest,epochs=1,initialization_seeds=list(range(89000300,89000320)),
             dataset_seed_start=89000400,teacher_seed_start=89000500,order_seed_start=89000600)
    (tmp_path/'trials').mkdir(); (tmp_path/'trial_receipts').mkdir()
    row=safe_evaluate_trial((dev,0,'affine',str(tmp_path)))
    assert row['check_status']=='PASS',row
    assert json.loads(json.dumps(row,allow_nan=False))==row
    assert json.loads((tmp_path/'trial_receipts/affine_s89000300.json').read_text())==row
