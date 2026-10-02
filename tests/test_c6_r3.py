"""R3 causal apparatus contracts on deterministic fixtures, never panel worlds."""
import copy
import inspect
import json
from pathlib import Path

import numpy as np
import pytest

from geomind import c6_r3_background as B, c6_r3_assay as A, c6_r3_protocol as P
from geomind import c6_r3_reference as R, run_c6_r3 as runner
from tools import build_c6_r3, c6_r3_design_gate as gate


@pytest.fixture(scope='module',autouse=True)
def native_build():
    build_c6_r3.build()
    B._KERNEL=None


@pytest.fixture
def fixture():
    r=np.random.default_rng(812)
    def pop(n,shift):
        return r.uniform(-1.2,1.2,(n,2))+shift,r.uniform(-2.,2.,n),r.uniform(-.1,.1,n)
    bath=pop(7,0.);source=pop(6,.4);source=(source[0],source[1],np.zeros(6))
    ref=B.Replay(*B.run(*bath,.4),.02)
    px,pt,_=pop(4,-.3)
    prior=B.Replay(np.stack([px+t*.1 for t in np.arange(21)*.02]),
                   np.stack([pt+t*.2 for t in np.arange(21)*.02]),.02)
    return bath,source,ref,prior


@pytest.mark.parametrize('mode',B.MODES)
@pytest.mark.parametrize('outbound',[0.,1.])
@pytest.mark.parametrize('has_prior',[False,True])
def test_native_matches_independent_matrix_reference(fixture,mode,outbound,has_prior):
    bath,source,ref,prior=fixture
    kwargs=dict(source=source,reference=ref,prior=prior if has_prior else None,mode=mode,outbound=outbound)
    native=B.run(*bath,.2,**kwargs);reference=R.simulate(*bath,.2,**kwargs)
    for a,b in zip(native,reference):np.testing.assert_allclose(a,b,atol=2e-12,rtol=0.)


def test_bath_only_reduces_to_frozen_c4(fixture):
    from geomind import c4_model as C
    bath,*_=fixture
    native=B.run(*bath,.2)
    _,_,samples=C.simulate(bath[0][None],bath[1][None],bath[2][None],C.INTACT,.02,10,sample_every=1)
    for a,b in zip(native,samples):np.testing.assert_allclose(a,b[:,0],atol=2e-12,rtol=0.)


def test_sham_preserves_source_and_blocks_live_bath_effect(fixture):
    bath,source,ref,prior=fixture
    on=B.run(*bath,.2,source=source,reference=ref,prior=prior)
    off=B.run(*bath,.2,source=source,reference=ref,prior=prior,outbound=0.)
    nb=len(bath[0])
    for a,b in zip(on,off):np.testing.assert_array_equal(a[:,nb:],b[:,nb:])
    assert np.max(np.abs(on[0][:,:nb]-off[0][:,:nb]))>1e-4
    no_prior=B.run(*bath,.2,source=source,reference=ref,outbound=0.)
    alone=B.run(*bath,.2)
    for a,b in zip(no_prior,alone):np.testing.assert_array_equal(a[:,:nb],b)


def test_sham_keeps_zeroed_neighbor_in_denominator():
    bath=(np.array([[0.,0.]]),np.array([0.]),np.array([0.]))
    source=(np.array([[0.,1.4]]),np.array([.3]),np.array([0.]))
    ref=B.Replay(np.zeros((2,1,2)),np.zeros((2,1)),.000001)
    prior=B.Replay(np.array([[[2.,0.]],[[2.,0.]]]),np.zeros((2,1)),.000001)
    on=B.run(*bath,.000001,source=source,reference=ref,prior=prior,outbound=0.,dt=.000001,sample_dt=.000001)
    alone=B.run(*bath,.000001,prior=prior,dt=.000001,sample_dt=.000001)
    np.testing.assert_allclose(on[0][-1,0,0]/alone[0][-1,0,0],.5,atol=1e-6)


def test_complete_no_r_removes_incoming_phase_and_phase_dependent_motion(fixture):
    bath,source,ref,prior=fixture
    kwargs=dict(source=source,reference=ref,prior=prior,mode='no_r')
    result=B.run(*bath,.2,**kwargs);nb=len(bath[0])
    np.testing.assert_array_equal(result[1][:,nb:],np.broadcast_to(source[1],result[1][:,nb:].shape))
    changed=(source[0],source[1]+np.linspace(.2,2.,len(source[1])),source[2])
    varied=B.run(*bath,.2,source=changed,reference=B.Replay(ref.x,ref.theta+.7,ref.dt),prior=prior,mode='no_r')
    np.testing.assert_array_equal(result[0][:,nb:],varied[0][:,nb:])


def test_complete_g_to_m_uses_one_common_topology(fixture):
    bath,source,ref,prior=fixture;nb=len(bath[0]);origin=np.vstack([bath[0],source[0]])
    moved=(source[0]*5+4,source[1],source[2])
    a=B.run(*bath,.2,source=source,reference=ref,mode='no_geometry_to_mode',phase_origin=origin)
    b=B.run(*bath,.2,source=moved,reference=ref,mode='no_geometry_to_mode',phase_origin=origin)
    np.testing.assert_array_equal(a[1][:,nb:],b[1][:,nb:])


def test_permutation_equivariance_with_replay(fixture):
    bath,source,ref,prior=fixture
    bp=np.array([6,3,1,0,2,4,5]);sp=np.array([3,2,5,1,4,0]);dp=np.array([2,0,3,1])
    original=B.run(*bath,.2,source=source,reference=ref,prior=prior)
    permuted=B.run(*(a[bp] for a in bath),.2,source=tuple(a[sp] for a in source),
        reference=B.Replay(ref.x[:,bp],ref.theta[:,bp],ref.dt),prior=B.Replay(prior.x[:,dp],prior.theta[:,dp],prior.dt))
    order=np.r_[bp,len(bp)+sp]
    for a,b in zip(permuted,original):np.testing.assert_allclose(a,b[:,order],atol=2e-12,rtol=0.)


def test_translation_rotation_and_phase_symmetry(fixture):
    bath,source,ref,prior=fixture
    angle=.41;rot=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
    offset=np.array([3.,-6.]);phase=1.7
    def transform(pop):return pop[0]@rot.T+offset,pop[1]+phase,pop[2]
    a=B.run(*bath,.2,source=source,reference=ref,prior=prior)
    b=B.run(*transform(bath),.2,source=transform(source),
        reference=B.Replay(ref.x@rot.T+offset,ref.theta+phase,ref.dt),
        prior=B.Replay(prior.x@rot.T+offset,prior.theta+phase,prior.dt))
    np.testing.assert_allclose(b[0],a[0]@rot.T+offset,atol=2e-12,rtol=0.)
    np.testing.assert_allclose(b[1],a[1]+phase,atol=2e-12,rtol=0.)


def test_replay_is_owned_interpolated_and_never_extends_future():
    x=np.array([[[0.,1.]],[[2.,3.]],[[4.,5.]]]);th=np.array([[0.],[1.],[2.]])
    replay=B.Replay(x,th,.1);x[:]=77;th[:]=66
    np.testing.assert_array_equal(replay.sample(.05)[0],[[1.,2.]])
    np.testing.assert_array_equal(replay.sample(.05)[1],[.5])
    assert not replay.x.flags.writeable
    assert replay.slice(.1,.1).duration==.1
    for t in (-.01,.201,float('nan')):
        with pytest.raises(ValueError,match='insufficient'):replay.sample(t)
    with pytest.raises(ValueError):B.combined(replay,replay.slice(.1,.1))
    assert B.combined(replay,replay).x.shape==(3,2,2)


@pytest.mark.parametrize('duration,dt',[(.1,.03),(-1.,.02),(1.,0.),(float('inf'),.02)])
def test_invalid_grid(duration,dt):
    with pytest.raises(ValueError):B.exact_steps(duration,dt)


def test_build_identity_required(fixture,monkeypatch,tmp_path):
    fake=tmp_path/'x.dylib';fake.write_bytes(build_c6_r3.LIBRARY.read_bytes())
    record=json.loads((build_c6_r3.LIBRARY.parent/'BUILD.json').read_text());record['source_sha256']='wrong'
    (tmp_path/'BUILD.json').write_text(json.dumps(record));monkeypatch.setattr(build_c6_r3,'LIBRARY',fake)
    with pytest.raises(RuntimeError,match='identity'):B.kernel()


def test_label_free_detector_signature_and_discovery():
    assert list(inspect.signature(A.find_candidates).parameters)==['xs','ths','thresholds']
    x=np.repeat(np.array([[[0.,0.],[.8,0.],[.4,.7]]]),31,axis=0);th=np.zeros((31,3))
    rows,_=A.find_candidates(x,th,P.load_settings()['detector'])
    assert len(rows)==1 and rows[0]['members']==[0,1,2]


def effects(intact=.1,ablated=0.):
    return {d:{'intact':intact,'ablated':ablated} for d in ('g_to_m','m_to_g')}


@pytest.mark.parametrize('intact,ablated,expected',[(.1,0.,True),(.1,.02,True),(.1,.03,False),
    (1e-9,0.,False),(-.1,0.,False),(float('nan'),0.,False),(.1,float('inf'),False)])
def test_source_requires_both_causal_paths(intact,ablated,expected):
    assert A.source_qualifies(effects(intact,ablated),P.load_settings()) is expected
    e=effects();e['m_to_g']['intact']=0.
    assert not A.source_qualifies(e,P.load_settings())
    assert not A.source_qualifies(None,P.load_settings())


def test_source_selection_does_not_use_future_causality_or_publication():
    rows=[{'members':[7,8,9],'accepted':True,'attribution':'source','causal':effects()},
          {'members':[3,4,5,6],'accepted':True,'attribution':'source','causal':None},
          {'members':list(range(20)),'accepted':True,'attribution':'mixed_or_prior'}]
    assert A.select_source(rows) is rows[1]
    assert P.publication({'qualified':False},None,None,P.load_settings()) is None


def episode(ok):return {'persistent_unit':ok,'formation':{'qualified':ok}}


def synthetic_records(n=10,turns=2):
    records=[]
    for w in range(n):
        cells=[]
        for _ in range(turns):
            cells.append({'qualified':True,'controls':{'sham_preserved':True,'no_r_qualifies':False},
                'numerics':{'passed':True},'background':{'before':{'b_phase':.1},'intact':{'b_phase':.4},
                    'no_r':{'b_phase':.1},'no_backreaction':{'b_phase':.1}},
                'episodes':{c:[episode(c=='intact') for _ in range(4)] for c in P.CONDITIONS},
                'before_episodes':[episode(False) for _ in range(4)]})
        link={'first_after':'a','second_before':'a','first_episode_source':'s',
              'second_source_input':'s','intact_episode_reused':True} if turns==2 else None
        records.append({'world':w,'turns':cells,'chain_link':link,'seconds':1.})
    return records


def evaluate(records):
    s=P.load_settings();s['statistics']['bootstrap_resamples']=300
    return P.evaluate(records,s)


def test_complete_coverage_and_separate_supported_claims():
    e=evaluate(synthetic_records());cov=e['endpoint_coverage']
    assert set(cov['evaluated'])|set(cov['not_run'])==set(P.ENDPOINTS)
    assert set(cov['evaluated']).isdisjoint(cov['not_run'])
    assert all(e['hypotheses'][h]=='SUPPORTED_WITHIN_SCOPE' for h in ('H-BG_turn1','H-PS_turn1','H-BG_turn2','H-PS_turn2','H-RBG'))
    assert e['hypotheses']['H-COMP']=='NOT_TESTED'
    assert all(cov['not_run'][n]['reason'] for n in P.ARM_A_ENDPOINTS)
    assert 'source_pin' in cov['not_run']


def test_no_r_contrast_cannot_be_omitted():
    rows=synthetic_records()
    for row in rows:
        for c in row['turns']:c['background']['no_r']['b_phase']=.7
    e=evaluate(rows)
    assert e['hypotheses']['H-BG_turn1']=='NOT_SUPPORTED'
    assert e['hypotheses']['H-PS_turn1']=='INCONCLUSIVE'


def test_publication_or_formation_cannot_fake_background_support():
    rows=synthetic_records()
    for row in rows:
        for c in row['turns']:c['background']['intact']['b_phase']=.1
    e=evaluate(rows)
    assert e['hypotheses']['H-BG_turn1']=='NOT_SUPPORTED'
    assert e['hypotheses']['H-PS_turn1']=='INCONCLUSIVE'


def test_missing_second_turn_and_quorum_are_inconclusive():
    e=evaluate(synthetic_records(turns=1))
    assert e['hypotheses']['H-RBG']=='INCONCLUSIVE'
    assert 'b_background_phase_vs_no_r_turn2' in e['endpoint_coverage']['not_run']
    assert evaluate(synthetic_records(n=9))['hypotheses']['H-BG_turn1']=='INCONCLUSIVE'


@pytest.mark.parametrize('fault',['sham','no_r','numerics','link','source','reuse'])
def test_engineering_failure_at_second_turn_blocks_all_support(fault):
    rows=synthetic_records();cell=rows[0]['turns'][1]
    if fault=='sham':cell['controls']['sham_preserved']=False
    elif fault=='no_r':cell['controls']['no_r_qualifies']=True
    elif fault=='numerics':cell['numerics']['passed']=False
    elif fault=='link':rows[0]['chain_link']['second_before']='wrong'
    elif fault=='source':rows[0]['chain_link']['second_source_input']='wrong'
    else:rows[0]['chain_link']['intact_episode_reused']=False
    e=evaluate(rows)
    assert all(v!='SUPPORTED_WITHIN_SCOPE' for v in e['hypotheses'].values())


@pytest.mark.parametrize('ci,n,expected',[([.051,.1],10,'PASS'),([-.1,.04],10,'FAIL'),
    ([.05,.1],10,'INCONCLUSIVE'),([0.,.05],10,'INCONCLUSIVE'),([.2,.3],9,'INCONCLUSIVE'),(None,10,'INCONCLUSIVE')])
def test_margin_equality_and_quorum(ci,n,expected):
    assert P.contrast_verdict(ci,.05,n,10)==expected


def test_bootstrap_keeps_original_world_missing_masks():
    draws=np.array([[0,1,2],[2,2,0],[1,1,1]])
    np.testing.assert_allclose(P.interval([1.,np.nan,3.],draws,.95),np.quantile([2.,7./3.],[.025,.975]),atol=1e-15)


def test_episode_zero_is_preserved_without_replacement():
    first=(object(),object(),{'qualified':True})
    assert P.next_turn_source(first) is first
    assert P.next_turn_source((object(),object(),{'qualified':False})) is None
    assert P.next_turn_source(None) is None


def test_fixed_ports_and_receivers_do_not_depend_on_outcomes(monkeypatch):
    s=P.load_settings();bath=(np.c_[np.arange(14),np.zeros(14)],np.zeros(14),np.zeros(14))
    app=A.Apparatus(bath,bath,None,None,s);captured=[]
    control=(np.repeat(bath[0][None],101,axis=0),np.zeros((101,14)))
    def run(duration,condition='intact',start=0.,state=None,sample_dt=None,**kw):
        captured.append(state);return np.repeat(state[0][None],101,axis=0),np.repeat(state[1][None],101,axis=0)
    monkeypatch.setattr(app,'run',run)
    state=(bath[0].copy(),np.linspace(-3.,3.,14))
    result=app.descriptor_with_control(state,0.,2.,control)
    assert result['ports']==[0,12]
    assert all(len(r['phase_response'][0])==13 for r in result['raw'])
    assert np.flatnonzero(captured[0][1]!=state[1]).tolist()==[0]
    assert np.flatnonzero(captured[2][1]!=state[1]).tolist()==[12]


def test_panel_guard_runs_before_manifest_or_output(monkeypatch,tmp_path):
    monkeypatch.setattr(runner.milestones,'check',lambda *args:['blocked'])
    monkeypatch.setattr(runner,'MANIFEST',tmp_path/'missing.json')
    output=tmp_path/'output'
    with pytest.raises(RuntimeError,match='Gate blocked'):runner.panel(output,tmp_path/'missing.xml')
    assert not output.exists()


def test_source_pin_validates_bytes(monkeypatch,tmp_path):
    folder=tmp_path/'research/rrg/v0.2.1';folder.mkdir(parents=True);(folder/'source.md').write_text('audited')
    record={'verification_status':'VERIFIED','release':'v0.2.1','file_sha256':{'source.md':gate.sha256(folder/'source.md')}}
    (folder.parent/'v0.2.1.import.json').write_text(json.dumps(record));monkeypatch.setattr(gate,'ROOT',tmp_path)
    assert gate.validate_pin()['source_files_verified']==1
    (folder/'source.md').write_text('changed')
    with pytest.raises(ValueError,match='pin mismatch'):gate.validate_pin()


def test_world_receipt_binds_compressed_and_raw_bytes(tmp_path):
    row={'world':0,'seconds':.5,'value':[1,2]};entry=gate.write_world(tmp_path,row)
    receipt={'world_artifacts':[entry]}
    assert gate.read_worlds(tmp_path,receipt)==[row]
    entry['uncompressed_sha256']='wrong'
    with pytest.raises(ValueError,match='raw world hash'):gate.read_worlds(tmp_path,receipt)
    entry['sha256']='wrong'
    with pytest.raises(ValueError,match='artifact hash'):gate.read_worlds(tmp_path,receipt)
    with pytest.raises(FileExistsError):gate.write_world(tmp_path,row)


@pytest.mark.parametrize('fault',[None,'quorum','control','numeric','runtime','unreached'])
def test_development_readiness_honors_all_stop_rows(fault):
    rows=synthetic_records();settings=P.load_settings()
    if fault=='quorum':
        for r in rows:r['turns'][0]['qualified']=False
    elif fault=='control':rows[0]['turns'][0]['controls']['sham_preserved']=False
    elif fault=='numeric':rows[0]['turns'][1]['numerics']['passed']=False
    elif fault=='runtime':rows[0]['seconds']=10000.
    elif fault=='unreached':
        for r in rows:r['turns'][1]['episodes']=None
    result=gate.readiness(rows,settings,8)
    assert result['passed'] is (fault is None)
    if fault is not None:assert result['reason']


def test_native_cost_ledger_records_full_state_and_replay_work(fixture):
    bath,source,ref,prior=fixture;B.reset_costs()
    B.run(*bath,.2,source=source,reference=ref,prior=prior)
    costs=B.costs()
    assert costs['integration_steps']==10 and costs['element_steps']==130
    assert costs['native_calls']==1 and costs['dense_boundary_bytes']>0 and costs['neighbor_distance_evaluations']>0


def test_apparatus_sham_uses_zero_outgoing_mask(fixture):
    bath,source,ref,prior=fixture
    app=A.Apparatus(bath,source,ref,prior,P.load_settings())
    a=app.run(.2,'no_backreaction')
    b=B.run(*bath,.2,source=source,reference=ref,prior=prior,outbound=0.)
    for x,y in zip(a,b):np.testing.assert_array_equal(x,y)


def test_formed_numerical_failure_is_not_hidden(monkeypatch,fixture):
    bath,source,ref,prior=fixture;s=P.load_settings();s['integration']['formation']=.02
    app=A.Apparatus(bath,source,ref,prior,s)
    flow=app.run(.04)
    answers=iter([{'passed':True},{'passed':False}])
    monkeypatch.setattr(P,'numerics',lambda app:next(answers))
    checks=P.numerical_windows(app,flow,bath)
    assert checks['initial']['passed'] and not checks['formation_snapshot']['passed']
    assert not checks['passed']


def test_unlinked_measurements_cannot_establish_recursion():
    rows=synthetic_records()
    for row in rows:row['chain_link']=None
    e=evaluate(rows)
    assert e['hypotheses']['H-BG_turn2']=='SUPPORTED_WITHIN_SCOPE'
    assert e['hypotheses']['H-RBG']=='INCONCLUSIVE'


def test_publication_links_measured_frequency_to_qualified_candidate():
    s=P.load_settings();x=np.repeat(np.array([[[0.,0.],[.8,0.],[.4,.7]]]),31,axis=0)
    th=np.repeat((np.arange(31)*.123)[:,None],3,axis=1)
    rows,_=A.find_candidates(x,th,s['detector']);row=rows[0]
    row['digest']=A.member_digest(row['members'])
    row['stats'].update(recovery_jaccard=1.,recovery_original_to_control=1.,
        recovery_original_to_kicked=1.,recovery_control_to_kicked=1.,recovery_pattern_error=0.)
    formation={'qualified':True,'selected_digest':row['digest'],'candidates':rows,'causal':effects()}
    pub=P.publication(formation,(x[-1],th[-1]),np.zeros(3),s)
    assert pub['member_digest']==row['digest']
    assert pub['mode_signature']['collective_frequency']==pytest.approx(.123)
    assert P.finite(pub)


def test_development_readiness_requires_complete_unique_worlds():
    rows=synthetic_records()
    assert not gate.readiness(rows[:9],P.load_settings(),8)['passed']
    rows[0]['world']=1
    assert not gate.readiness(rows,P.load_settings(),8)['passed']
