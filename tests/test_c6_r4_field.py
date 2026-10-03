"""Engineering contracts on separate fixtures; never final/dev world rehearsals."""
import copy
import hashlib
import gzip
import inspect
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
from geomind import c6_r4_field as F,c6_r4_field_reference as R,c6_r4_field_assay as A,c6_r4_field_protocol as P,c6_r4_field_analysis as E
from geomind import run_c6_r4 as runner
from tools import c6_r4_design_gate as gate

def owner(n=6):
    random=np.random.default_rng(882901)
    o=F.population(random,F.medium(random,P.load_settings()['model']),0,0,n)
    o.z=.55*np.exp(1j*random.uniform(-np.pi,np.pi,25));o.cohorts[0].carrier=o.z.copy()
    o.cohorts[0].selected=(0,1,2);o.cohorts[0].output=1.
    return o

@pytest.mark.parametrize('mode',list(F.MODES))
@pytest.mark.parametrize('on',[0.,1.])
def test_native_independent_actual_law(mode,on):
    o=owner(24);c=o.cohorts[0];c.mode=mode;c.output=on
    if mode=='no_geometry_to_mode':c.origin=c.x.copy();c.x[0]+=[.1,.2]
    assert np.max(np.abs(F.rhs(o)-R.rhs(o)))<1e-12
    native,flow=F.advance(o,.1,.005,.005);reference,ref=R.advance(o,.1,.005,.005)
    assert np.max(np.abs(flow-ref))<1e-11
    assert native.time==reference.time

def test_carrier_and_sham_are_decoupled_full_state():
    intact=owner();sham=intact.clone();sham.cohorts[0].output=0.
    a,aa=F.advance(intact,1.,.005,.005);b,bb=F.advance(sham,1.,.005,.005)
    assert np.max(np.abs(aa[:,50:]-bb[:,50:]))<1e-12
    assert np.max(np.abs(aa[:,:50]-bb[:,:50]))>1e-5
    assert np.max(np.abs(F.emissions(sham,bb)))==0.
    assert np.max(np.abs(F.emissions(intact,aa)))>0.
    changed=intact.clone();changed.z+=.5j
    assert np.array_equal(F.rhs(intact)[50:],F.rhs(changed)[50:])

def test_outgoing_channel_uses_selected_mean_then_mask():
    o=owner();base=o.clone();base.cohorts[0].output=0.
    difference=(F.rhs(o)-F.rhs(base))[:50].copy().view('c16')
    assert np.max(np.abs(difference-F.output(o)))<1e-13
    assert np.array_equal(F.rhs(o)[50:],F.rhs(base)[50:])

def test_complex_identity_roundtrip_and_schema():
    o=owner();i=o.identity();assert o.unpack(o.pack(),o.time).identity()==i
    changed=o.clone();changed.z.imag[0]+=.01;assert changed.identity()!=i
    changed=o.clone();changed.cohorts[0].carrier,changed.z=changed.z.copy(),changed.cohorts[0].carrier.copy()
    # Force nonidentical actual/carrier before swapping.
    o.cohorts[0].carrier[0]+=.04j;changed=o.clone();changed.cohorts[0].carrier,changed.z=changed.z.copy(),changed.cohorts[0].carrier.copy()
    assert changed.identity()!=o.identity()
    o.z=o.z.real
    with pytest.raises(ValueError,match='complex'):o.identity()

def test_invalid_normalization_and_duplicate_inventory():
    o=owner();o.cohorts[0].x[:]=1e4
    with pytest.raises(ValueError,match='invalid'):F.advance(o,.1,.005)
    o=owner();o.cohorts[0].tokens=('0'*32,)*6
    with pytest.raises(ValueError,match='identity'):o.pack()
    o=owner();o.cohorts[0].selected=(0,0)
    with pytest.raises(ValueError):o.pack()
    o=owner();o.cohorts[0].ids=(o.cohorts[0].ids[0],)*6
    with pytest.raises(ValueError,match='identity'):o.pack()
    o=owner();o=F.population(np.random.default_rng(552),o,1,0,6)
    o.cohorts[-1].ids=o.cohorts[0].ids
    with pytest.raises(ValueError,match='duplicate physical IDs'):o.pack()

def test_passive_factorization_matches_full_owner():
    o=owner();o.cohorts[0].output=0.
    o=F.population(np.random.default_rng(552),o,1,0,6);o.cohorts[-1].selected=(1,2,3);o.cohorts[-1].output=1.
    a,aa=F.advance(o,.2,.005,.005);b,bb=F.advance(o,.2,.005,.005,_factor=False)
    assert np.max(np.abs(aa-bb))<1e-12
    assert a.identity()==b.identity()

def test_all_off_probe_reuses_exact_source_flow_and_matches_coupled_owner(monkeypatch):
    o=owner();o.cohorts[0].output=0.;F._PASSIVE_CACHE.clear()
    a,aa=F.advance(o,.2,.005,.005);b,bb=F.advance(o,.2,.005,.005,_factor=False)
    assert np.max(np.abs(aa-bb))<1e-12
    keys=list(F._PASSIVE_CACHE);assert len(keys)==1
    original=F.advance;independent_calls=[]
    def observed(state,*args,**kwargs):
        if kwargs.get('_factor') is False:independent_calls.append(len(state.cohorts))
        return original(state,*args,**kwargs)
    monkeypatch.setattr(F,'advance',observed)
    perturbed=o.clone();perturbed.z[0]+=.05j
    end,_=F.advance(perturbed,.2,.005,.005)
    assert independent_calls==[0]  # only the changed actual medium evolves again
    assert list(F._PASSIVE_CACHE)==keys
    assert np.array_equal(end.cohorts[0].theta,a.cohorts[0].theta)

def test_exact_bistable_periodic_and_zero_solutions():
    for r in (0.,R.isolated_radius(-.18,-1),R.isolated_radius(-.18,1)):
        o=F.Owner(np.array([r+0j]),np.zeros((1,2)),np.array([.2]),np.zeros((1,8)),np.zeros((1,1),'i4'),dict(P.load_settings()['model']),(0,))
        o.model.update(diffusion=0.,drive=0.)
        end,flow=F.advance(o,1.,.005,.005);expected=r*np.exp(.2j*np.arange(len(flow))*.005)
        assert np.max(np.abs(flow.copy().view('c16').ravel()-expected))<1e-10

def test_complete_geometry_ablation_freezes_both_paths():
    o=owner();o.cohorts[0].output=0.;o.cohorts[0].origin=o.cohorts[0].x.copy();o.cohorts[0].mode='no_geometry_to_mode'
    b=o.clone();b.cohorts[0].x*=1.5
    aa,_=F.advance(o,1.,.005,.1);bb,_=F.advance(b,1.,.005,.1)
    assert np.max(np.abs(aa.cohorts[0].theta-bb.cohorts[0].theta))<1e-12
    o.cohorts[0].mode=b.cohorts[0].mode='intact'
    aa,_=F.advance(o,1.,.005,.1);bb,_=F.advance(b,1.,.005,.1)
    assert np.max(np.abs(aa.cohorts[0].theta-bb.cohorts[0].theta))>1e-5

def test_complete_mode_ablation_removes_all_phase_force():
    o=owner();o.cohorts[0].mode='no_mode_to_geometry';o.cohorts[0].output=0.;b=o.clone();b.cohorts[0].theta+=np.linspace(0,2,6)
    aa,_=F.advance(o,1.,.005,.1);bb,_=F.advance(b,1.,.005,.1)
    assert np.max(np.abs(aa.cohorts[0].x-bb.cohorts[0].x))<1e-12
    o.cohorts[0].mode=b.cohorts[0].mode='intact'
    aa,_=F.advance(o,1.,.005,.1);bb,_=F.advance(b,1.,.005,.1)
    assert np.max(np.abs(aa.cohorts[0].x-bb.cohorts[0].x))>1e-5

def test_equivariance_and_realized_intervention_covariance():
    o=owner();random=np.random.default_rng(43);ep=random.permutation(6);sp=random.permutation(25)
    angle=.4;phase=.5;shift=np.array([.3,-.2]);changed=gate.transform(o,ep,sp,angle,shift,phase)
    a,_=F.advance(o,.2,.005,.005);b,_=F.advance(changed,.2,.005,.005)
    assert np.max(np.abs(gate.transform(a,ep,sp,angle,shift,phase).pack()-b.pack()))<1e-9
    pert=A.perturbations(random,6);rotation=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
    o.cohorts[0].x+=pert['position']*.1;changed.cohorts[0].x+=(pert['position']@rotation.T)[ep]*.1
    o.cohorts[0].theta=pert['replacement'];changed.cohorts[0].theta=pert['replacement'][ep]+phase
    assert np.max(np.abs(gate.transform(o,ep,sp,angle,shift,phase).pack()-changed.pack()))<1e-12

def test_covariance_carries_future_introduction_axis_and_realized_kicks():
    o=owner();angle=.71;phase=.39;shift=np.array([1.3,-.2]);changed=gate.transform(o,angle=angle,shift=shift,phase=phase)
    first=F.population(np.random.default_rng(8211),o,1,0,6)
    second=F.population(np.random.default_rng(8211),changed,1,0,6)
    expected=gate.transform(first,angle=angle,shift=shift,phase=phase)
    assert np.max(np.abs(expected.pack()-second.pack()))<1e-12
    assert expected.identity()==second.identity()
    a=P.physical_perturbations(np.random.default_rng(421),first)
    b=P.physical_perturbations(np.random.default_rng(421),second)
    rotation=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
    assert np.array_equal(a['phase'],b['phase']) and np.array_equal(a['probe'],b['probe'])
    assert np.max(np.abs(a['position']@rotation.T-b['position']))<1e-12
    assert np.max(np.abs(a['replacement']+phase-b['replacement']))<1e-12

def test_selection_is_physical_token_based_not_labels():
    rows=[{'members':[0,1,2]},{'members':[3,4,5]}];tokens=tuple(f'{i:032x}' for i in (5,6,7,1,2,3))
    winner=A.select_accepted(rows,tokens);assert winner['members']==[3,4,5]
    order=[5,4,3,2,1,0];permuted=[{'members':[order.index(i) for i in row['members']]} for row in rows]
    result=A.select_accepted(permuted,tuple(tokens[i] for i in order))
    assert sorted(order[i] for i in result['members'])==[3,4,5]
    with pytest.raises(ValueError):A.select_accepted(rows,('0'*32,)*6)

def test_streamed_full_scope_numerics_and_failure():
    s=P.load_settings();o=owner();grid=A.GridSet([o]*3,s);flow=grid.run(.2,'fixture',.1)
    assert len(grid.checks)==1 and grid.checks[0]['duration']==.2 and grid.checks[0]['passed']
    assert grid.checks[0]['source_trace_hash_by_dt'] and all(g.shape==(3,len(o.pack())) for g in flow)
    other=o.clone();other.z[0]+=.1
    with pytest.raises(A.NumericalFailure):A.GridSet([o,o,other],s).run(.1,'invalid',.1)

def test_finite_probe_descriptor_ports_and_numerical_margin():
    s=P.load_settings();s['descriptor']=.1;o=owner();o.cohorts[0].output=0.
    grid=A.GridSet([o]*3,s);value=A.descriptor(grid,.3,'fixture')
    assert len(value['raw'])==50 and len(value['per_probe_by_dt'][0])==50
    assert {r['port'] for r in value['raw']}==set(o.site_ids)
    assert grid.owners[0].identity()==o.identity()  # probes are forks.
    assert max(value['gain_by_dt'])>0.

def test_descriptor_common_phase_covariance_including_realized_raw_probes():
    s=P.load_settings();s['descriptor']=.1;o=owner();o.cohorts[0].output=0.;phase=.71
    changed=gate.transform(o,phase=phase)
    first=A.descriptor(A.GridSet([o]*3,s),.3,'original-fixture')
    second=A.descriptor(A.GridSet([changed]*3,s),.3,'rotated-fixture')
    assert np.max(np.abs(np.asarray(first['per_probe_by_dt'])-second['per_probe_by_dt']))<1e-10
    for a,b in zip(first['raw'],second['raw']):
        assert np.max(np.abs(np.asarray(b['probe_phase_by_dt'])-np.asarray(a['probe_phase_by_dt'])-phase))<1e-12
        za=np.asarray(a['response_real_imag']);zb=np.asarray(b['response_real_imag'])
        assert np.max(np.abs((za[...,0]+1j*za[...,1])*np.exp(1j*phase)-(zb[...,0]+1j*zb[...,1])))<1e-10

def episodes(values):return [{'episode':i,'qualification':{'qualified':v}} for i,v in enumerate(values)]
def test_continuation_is_held_out_and_denominator_fixed():
    assert E.formation(episodes([True,False,False,False,False]))==0.
    assert E.formation(episodes([False,True,True,True,True]))==1.
    assert E.formation(episodes([True,True,False,False,False]))==.25
    with pytest.raises(ValueError):E.formation(episodes([True]*4))
    with pytest.raises(ValueError):E.formation(episodes([True]*5)[::-1])

@pytest.mark.parametrize('ci,n,margin,expected',[
    ([.11,.2],10,.1,'PASS'),([-.2,-.11],10,.1,'PASS'),([-.09,.09],10,.1,'FAIL'),
    ([.1,.2],10,.1,'INCONCLUSIVE'),([-.2,-.1],10,.1,'INCONCLUSIVE'),([-.1,.1],10,.1,'INCONCLUSIVE'),
    ([.11,.2],9,.1,'INCONCLUSIVE'),(None,10,.1,'INCONCLUSIVE')])
def test_two_sided_change_truth_table(ci,n,margin,expected):assert E.change_verdict(ci,n,margin)==expected

def test_causal_numerical_spread_and_all_ablations_required():
    s=P.load_settings();effects={k:{'intact':[.01,.01,.01],'ablated':[0.,0.,0.]} for k in ('g_to_m','m_to_g')}
    assert A.closure_valid(effects,s)
    bad=copy.deepcopy(effects);bad['g_to_m']['ablated'][2]=.003
    with pytest.raises(ValueError,match='ablation'):A.closure_valid(bad,s)
    bad=copy.deepcopy(effects);bad['m_to_g']['intact'][0]=.02
    with pytest.raises(A.NumericalFailure,match='refinement'):A.closure_valid(bad,s)
    bad=copy.deepcopy(effects);bad['m_to_g']['intact']=[0.,0.,0.];assert not A.closure_valid(bad,s)
    bad=copy.deepcopy(effects);bad['g_to_m']['intact']=[0.,.01,.01]
    with pytest.raises(A.NumericalFailure,match='grid-dependent'):A.closure_valid(bad,s)

def test_rolling_windows_preserve_exact_clock_and_first_qualification_window():
    s=P.load_settings();model=dict(s['model']);model['drive']=0.
    random=np.random.default_rng(569);o=F.population(random,F.medium(random,model),0,0,3)
    length=np.sqrt((1/(1+model['J']))**2-model['soft_core']**2)
    o.z[:]=0.;c=o.cohorts[0];c.carrier[:]=0.;c.x=np.array([[0.,0.],[length,0.],[length/2,np.sqrt(3)*length/2]])
    c.theta[:]=0.;c.rates[:]=.2
    at100,prefix=F.advance(o,100.,s['dt'],1.);at200,operation=F.advance(at100,100.,s['dt'],1.)
    rows=P.rolling_persistence(prefix,operation,at200,np.array([0,1,2]),s)
    assert len(rows)==101 and [r['time'] for r in rows]==list(range(100,201))
    assert all(r['stats']['freq_change']<1e-12 and r['passed'] for r in rows)
    from geomind import c4_detect as D
    xs,ths=A.frames(prefix[-31:],at100);locks=D.locked_pairs(ths,.1)
    expected=D.window_statistics(xs,ths,np.array([0,1,2]),1.,1.5,locks)
    assert rows[0]['stats']==expected

def test_recursive_rule_engineering_quorum_fail_and_witness_precedence():
    good=['SUPPORTED_WITHIN_SCOPE']*6
    assert E.recursive(good,10,10,True)=='SUPPORTED_WITHIN_SCOPE'
    assert E.recursive(good,10,9,True)=='INCONCLUSIVE'
    assert E.recursive(good,9,10,True)=='INCONCLUSIVE'
    assert E.recursive(good,10,10,False)=='INCONCLUSIVE'
    bad=good.copy();bad[0]='NOT_SUPPORTED'
    assert E.recursive(bad,10,0,True)=='NOT_SUPPORTED'
    assert E.recursive(bad,10,10,False)=='INCONCLUSIVE'
    assert E.combine(['PASS','PASS'],True,'NOT_SUPPORTED')=='INCONCLUSIVE'
    assert E.combine(['FAIL','PASS'],False)=='INCONCLUSIVE'

def row(world=0):
    return {'world':world,'turns':[],'checks':[],'invalid':None,'chain_complete':False,'enabled_witness':False,'links':[],
            'initial_source':{'qualification':{'qualified':False,'candidates':[]}},'seconds':1.,'peak_rss_bytes':100,
            'memory_measurement':{'scope':'Synthetic fixture, no measured RSS'},'native_build':{'fixture':True}}

def test_no_formation_panel_has_complete_endpoint_coverage_and_no_fake_support():
    s=P.load_settings();s['bootstrap_resamples']=1000
    result=E.evaluate([row(i) for i in range(40)],s,65,{k:{'passed':True} for k in ('source_pin','b_reference_equivalence','b_transform_equivariance')})
    coverage=result['endpoint_coverage'];assert len(E.ENDPOINTS)==len(set(E.ENDPOINTS))==79
    assert set(coverage['evaluated'])|set(coverage['not_run'])==set(E.ENDPOINTS)
    assert all(h=='INCONCLUSIVE' for k,h in result['hypotheses'].items() if k not in ('H-COMP','H-PRED','H-AI','H-EFF'))
    assert len(coverage['evaluated']['b_source_qualification_turn1']['value'])==40
    assert all(k in coverage['not_run'] for k in E.ARM_A)
    with pytest.raises(ValueError):E.evaluate([row(0)]*40,s,65,{})

def test_engineering_invalid_world_is_not_dropped_for_a_verdict():
    s=P.load_settings();s['bootstrap_resamples']=1000;rows=[row(i) for i in range(40)]
    rows[0]['invalid']={'turn':1,'message':'failed probe'}
    result=E.evaluate(rows,s,65,{k:{'passed':True} for k in ('source_pin','b_reference_equivalence','b_transform_equivariance')})
    assert not result['gates']['controls_numerics']
    assert result['endpoint_coverage']['evaluated']['b_response_vs_no_r_turn1']['verdict']=='INCONCLUSIVE'

def test_false_enabled_flag_and_unresolved_chain_rejected():
    r=row();r['enabled_witness']=True
    with pytest.raises(ValueError,match='witness'):E.validate_world(r)
    r=row();r['chain_complete']=True
    with pytest.raises(ValueError,match='chain'):E.validate_world(r)

def synthetic_chain(world):
    """Fabricated contract receipt, not a simulated world or formation result."""
    s=P.load_settings();base=owner();base.cohorts[0].output=0.;base.time=100.
    result=row(world);result['chain_complete']=True;result['enabled_witness']=True
    def q(o,qualified=True):
        c=o.cohorts[-1];members=[0,1,2];stats={'size':3}
        candidate=A.member_identity(o,np.array(members))
        return {'qualified':qualified,'selected_members':members,'selected_identity':candidate,
            'candidates':[{'members':members,'accepted':True,'stats':stats}],
            'publication':{'candidate':candidate,'snapshot':o.identity(),'size':1.,'centroid':[0.,0.],'phase':0.,'rate':.2,
                           'units':{'size':'L0','centroid':'L0','phase':'rad','rate':'rad/C0'},
                           'S':copy.deepcopy(stats),'ids':[c.ids[i] for i in members]} if qualified else None}
    for turn in (1,2):
        before=base.clone();after=base.clone();after.time+=100.
        introduced=F.population(np.random.default_rng(561+turn),after,turn,0,6)
        qualified=introduced.clone();qualified.time+=100.
        episodes_by_condition={}
        for condition in P.CONDITIONS:
            episodes_by_condition[condition]=[]
            for episode in range(5):
                episodes_by_condition[condition].append({'episode':episode,'inputs':{'fixture':episode},'perturbations':{'fixture':episode},
                    'initial_ids':[introduced.identity()]*3,'qualified_ids':[qualified.identity()]*3,
                    'introduced_states':[P.snapshot(introduced)]*3,'qualified_states':[P.snapshot(qualified)]*3,
                    'qualification':q(qualified,condition=='intact')})
        check={'source_trace_hash_by_dt':['same']*3,'output_max_by_dt':[0.]*3}
        conditions={c:{'after_ids':[after.identity()]*3,'after_states':[P.snapshot(after)]*3,'output_check':copy.deepcopy(check),
            'endpoint_qualification':q(after,c!='no_r'),'persistence_by_dt':[[{'passed':True}]]*3} for c in P.CONDITIONS}
        cell={'turn':turn,'source':q(before),'before_ids':[before.identity()]*3,'operation_eligible':True,'controls_passed':True,
            'episodes':episodes_by_condition,'conditions':conditions,'response':{c:{'gain_by_dt':[.1 if c=='intact' else 0.]*3} for c in P.CONDITIONS},
            'witness_tuple':[True,False,False],'physical_outcome':'PERSISTENT_UNIT',
            'before_formation':copy.deepcopy(episodes_by_condition['intact'][1:])}
        result['turns'].append(cell);result['links'].append({'episode':0,'clock':qualified.time,'after_ids':[after.identity()]*3,
            'introduced_ids':[introduced.identity()]*3,'qualified_ids':[qualified.identity()]*3,'next_operation_ids':[qualified.identity()]*3})
        base=qualified
    return result

def test_exact_chain_provenance_and_invalid_controls_are_rejected():
    r=synthetic_chain(0);E.validate_world(r)
    for change in ('source','restage','field','carrier','clock','sham','no_r','inputs','perturbations','witness','publication','before_publication'):
        bad=copy.deepcopy(r)
        if change=='source':bad['links'][0]['next_operation_ids']=['wrong']*3
        if change=='restage':bad['turns'][1]['before_ids']=['wrong']*3
        if change=='field':bad['turns'][0]['episodes']['intact'][0]['introduced_states'][0]['fields_real_imag'][0][0]+=.1
        if change=='carrier':bad['turns'][0]['episodes']['intact'][0]['introduced_states'][0]['cohorts'][-1]['carrier_real_imag'][0][0]+=.1
        if change=='clock':bad['links'][0]['clock']-=100.
        if change=='sham':bad['turns'][0]['conditions']['no_backreaction']['output_check']['output_max_by_dt'][0]=.001
        if change=='no_r':bad['turns'][0]['conditions']['no_r']['endpoint_qualification']['qualified']=True
        if change=='inputs':bad['turns'][0]['episodes']['no_r'][1]['inputs']={'unmatched':True}
        if change=='perturbations':bad['turns'][0]['episodes']['no_r'][1]['perturbations']={'unmatched':True}
        if change=='witness':bad['turns'][0]['witness_tuple']=[True,True,True]
        if change=='publication':bad['turns'][0]['source']['publication']['snapshot']='0'*64
        if change=='before_publication':bad['turns'][0]['before_formation'][0]['qualification']['publication']['snapshot']='0'*64
        with pytest.raises(ValueError):E.validate_world(bad)
    bad=copy.deepcopy(r);bad['enabled_witness']=False;bad['turns'][0]['witness_tuple']=[True,True,True]
    with pytest.raises(ValueError,match='witness tuple'):E.validate_world(bad)

def test_supported_synthetic_chain_and_mechanical_mask_not_enabled_subset():
    s=P.load_settings();s['bootstrap_resamples']=1000
    rows=[synthetic_chain(i) for i in range(40)]
    engineering={k:{'passed':True} for k in ('source_pin','b_reference_equivalence','b_transform_equivariance')}
    result=E.evaluate(rows,s,42,engineering)
    assert result['hypotheses']['H-RBG']=='SUPPORTED_WITHIN_SCOPE'
    assert all(c['value']['n']==40 and c['verdict']=='PASS' for k,c in result['endpoint_coverage']['evaluated'].items() if k in E.PRIMARY)
    for r in rows[10:]:
        r['enabled_witness']=False
        for cell in r['turns']:
            cell['episodes']['no_r'][0]['qualification']['qualified']=True
            cell['episodes']['no_r'][0]['qualification']['publication']=copy.deepcopy(cell['episodes']['intact'][0]['qualification']['publication'])
            cell['witness_tuple']=[True,True,False]
    result=E.evaluate(rows,s,42,engineering)
    assert result['hypotheses']['H-RBG']=='SUPPORTED_WITHIN_SCOPE'
    assert result['endpoint_coverage']['evaluated']['b_chain_later_formation_vs_no_r_turn1']['value']['n']==40
    rows[9]['enabled_witness']=False
    for cell in rows[9]['turns']:
        cell['episodes']['no_r'][0]['qualification']['qualified']=True
        cell['episodes']['no_r'][0]['qualification']['publication']=copy.deepcopy(cell['episodes']['intact'][0]['qualification']['publication'])
        cell['witness_tuple']=[True,True,False]
    result=E.evaluate(rows,s,42,engineering)
    assert result['hypotheses']['H-RBG']=='INCONCLUSIVE'

def test_physical_loss_is_valid_eligibility_and_late_error_preserves_first_turn():
    s=P.load_settings();s['bootstrap_resamples']=1000
    rows=[synthetic_chain(i) for i in range(40)]
    engineering={k:{'passed':True} for k in ('source_pin','b_reference_equivalence','b_transform_equivariance')}
    rows[0]['invalid']={'turn':2,'message':'later numerical failure'};rows[0]['chain_complete']=False;rows[0]['enabled_witness']=False
    result=E.evaluate(rows,s,41,engineering)
    assert result['hypotheses']['H-BG_turn1']=='SUPPORTED_WITHIN_SCOPE'
    assert result['hypotheses']['H-BG_turn2']=='INCONCLUSIVE'
    for key in E.PRIMARY:
        if key.startswith('b_chain_'):
            assert result['endpoint_coverage']['evaluated'][key]['verdict']=='INCONCLUSIVE'
            assert not result['endpoint_coverage']['evaluated'][key]['engineering_valid']
    assert result['hypotheses']['H-BG_chain_turn1']=='INCONCLUSIVE'
    assert result['hypotheses']['H-PS_chain_turn1']=='INCONCLUSIVE'
    rows[0]['invalid']=None;rows[0]['turns'][0]['operation_eligible']=False;rows[0]['turns'][0]['physical_outcome']='SOURCE_LOST_DURING_OPERATION'
    result=E.evaluate(rows,s,41,engineering)
    assert result['gates']['controls_numerics']
    assert result['endpoint_coverage']['evaluated']['b_response_vs_no_r_turn1']['value']['n']==39

def test_publication_not_validated_by_global_count():
    member_hash=hashlib.sha256(json.dumps(['a','b','c']).encode()).hexdigest()
    q={'qualified':True,'candidates':[{'members':[0,1,2],'accepted':True,'stats':{'size':3}}],
       'selected_members':[0,1,2],'selected_identity':member_hash,'publication':{'candidate':member_hash,'snapshot':'a'*64,'size':1.,
           'centroid':[0.,0.],'phase':0.,'rate':.2,'units':{'size':'L0','centroid':'L0','phase':'rad','rate':'rad/C0'},'S':{'size':3},'ids':['a','b','c']}}
    assert E.publication_valid(q)
    q['publication']['S']['size']=4;assert not E.publication_valid(q)
    q['publication']['S']['size']=3;q['publication']['candidate']='other';assert not E.publication_valid(q)
    q['publication']['candidate']=member_hash;q['publication']['size']=float('nan');assert not E.publication_valid(q)

def test_readiness_is_not_effect_selected():
    s=P.load_settings();rows=[row(i) for i in range(10)]
    for r in rows[:5]:r['initial_source']['qualification']['qualified']=True;r['chain_complete']=True
    assert gate.readiness(rows,s,2,10.)['passed']
    assert gate.readiness(rows[:9],s,2,10.)['reason']=='incomplete development worlds'
    rows[0]['invalid']={'message':'engineering error'};assert not gate.readiness(rows,s,2,10.)['passed']
    rows[0]['invalid']=None;rows[0]['seconds']=1000.;assert not gate.readiness(rows,s,2,10.)['passed']

def test_panel_checks_gate_before_reading_manifest(tmp_path,monkeypatch):
    monkeypatch.setattr(runner.milestones,'check',lambda *args:['unverified'])
    with pytest.raises(RuntimeError,match='blocked'):runner.panel(tmp_path/'panel',tmp_path/'missing.xml')
    assert not (tmp_path/'panel').exists()

def test_pending_development_registration_stops_before_output(tmp_path,monkeypatch):
    manifest=json.loads((P.ROOT/'experiments/c6_manifest.json').read_text());root=tmp_path/'fixture-root'
    (root/'experiments').mkdir(parents=True);monkeypatch.setattr(gate,'ROOT',root)
    for status in ('PENDING_DEVELOPMENT_APPROVAL','REGISTERED_DEVELOPMENT_ONLY'):
        manifest.update(status=status,development_gate='registered-output')
        (root/'experiments/c6_manifest.json').write_text(json.dumps(manifest))
        # Pending refuses even the exact path; registered refuses a wrong path.
        output=root/('registered-output' if status.startswith('PENDING') else 'wrong-output')
        with pytest.raises(SystemExit,match='owner-approved'):gate.main(['--output',str(output)])
        assert not output.exists()

def test_loaded_kernel_identity_is_pinned(monkeypatch):
    F.native();lib,record=F._NATIVE;fake=dict(record);fake['source_sha256']='0'*64
    monkeypatch.setattr(F,'_NATIVE',(lib,fake))
    with pytest.raises(RuntimeError,match='identity'):F.native()

def test_detector_api_has_no_condition_or_expected_subset():
    from geomind import c4_detect as D
    assert set(inspect.signature(D.components).parameters)=={'X','link_factor','locked'}
    assert 'condition' not in inspect.signature(A.select_accepted).parameters


def test_introductions_pair_inputs_but_keep_each_grids_actual_carrier():
    s=P.load_settings();s['elements']=6;base=owner();base.cohorts[0].output=0.
    states=[base.clone() for _ in range(3)]
    for k,o in enumerate(states):o.z[0]+=.01j*k
    grid=P.introduce(A.GridSet(states,s),882902,0,1,0)
    first=grid.owners[0].cohorts[-1]
    for original,o in zip(states,grid.owners):
        c=o.cohorts[-1]
        assert np.array_equal(c.carrier,original.z)
        assert np.array_equal(c.x,first.x) and np.array_equal(c.theta,first.theta)
        assert np.array_equal(c.rates,first.rates) and c.ids==first.ids and c.tokens==first.tokens


def test_qualification_prefix_emits_nothing_before_acceptance(monkeypatch):
    s=P.load_settings();s['elements']=6;base=owner();base.cohorts[0].output=0.;seen=[]
    def fake_run(grid,*args):
        seen.extend(c.output for o in grid.owners for c in o.cohorts)
        return [np.tile(o.pack(),(31,1)) for o in grid.owners]
    monkeypatch.setattr(A.GridSet,'run',fake_run)
    monkeypatch.setattr(A,'qualification',lambda *a,**kw:{'qualified':False})
    _,q,_=P.qualify_episode(A.GridSet([base]*3,s),882902,0,1,0,'synthetic-prefix')
    assert not q['qualified'] and seen and not any(seen)


def synthetic_operation(monkeypatch,source_lost=False,reserved_qualified=False):
    """Exercise the real operation caller with fabricated assays; no dynamics."""
    s=P.load_settings();s['elements']=6;base=owner();base.time=100.;base.cohorts[0].output=0.
    grid=A.GridSet([base]*3,s);descriptor_calls=[];reserved_ids=[]
    def fake_run(branch,duration,scope,*args):
        flows=[]
        for o in branch.owners:
            initial=o.pack();o.time+=duration;flows.append(np.array([initial,o.pack()]))
        branch.checks.append({'scope':scope,'source_trace_hash_by_dt':['paired-source']*3,
                             'output_max_by_dt':[0.]*3})
        return flows
    def fake_qualification(branch,*args,**kw):
        return {'qualified':not source_lost and branch.owners[0].cohorts[-1].mode!='no_r'}
    def fake_episode(background,entropy,world,generation,episode,scope):
        next_grid=background.clone()
        for o in next_grid.owners:o.time+=100.;o.z[0]+=.01*episode
        accepted=reserved_qualified if episode==0 else True
        if '/no_r/' in scope or '/no_backreaction/' in scope:accepted=False
        q={'qualified':accepted}
        record={'episode':episode,'qualification':q,'qualified_ids':next_grid.identities()}
        if '/intact/e0' in scope:reserved_ids.extend(record['qualified_ids'])
        return next_grid,q,record
    def fake_descriptor(branch,alpha,scope):
        descriptor_calls.append(scope)
        return {'gain_by_dt':[.1]*3,'snapshot_ids':branch.identities()}
    monkeypatch.setattr(A.GridSet,'run',fake_run);monkeypatch.setattr(A,'qualification',fake_qualification)
    monkeypatch.setattr(P,'rolling_persistence',lambda *a:[{'passed':not source_lost,'time':100.}])
    monkeypatch.setattr(P,'qualify_episode',fake_episode);monkeypatch.setattr(A,'descriptor',fake_descriptor)
    cell,continuation=P.operation(grid,{'selected_members':[0,1,2]},[None]*3,882902,0,1,.3,'fixture-turn')
    return cell,continuation,descriptor_calls,reserved_ids


def test_real_operation_never_replaces_reserved_continuation(monkeypatch):
    cell,continuation,calls,_=synthetic_operation(monkeypatch,reserved_qualified=False)
    assert cell['episodes']['intact'][1]['qualification']['qualified']
    assert continuation is None and cell['witness_tuple']==[False,False,False]
    cell,continuation,calls,ids=synthetic_operation(monkeypatch,reserved_qualified=True)
    assert continuation[0].identities()==ids
    assert len(calls)==4


def test_physical_source_loss_keeps_all_response_diagnostics(monkeypatch):
    cell,continuation,calls,_=synthetic_operation(monkeypatch,source_lost=True)
    assert not cell['operation_eligible'] and cell['physical_outcome']=='SOURCE_LOST_DURING_OPERATION'
    assert cell['first_loss_time']==100. and continuation is None and not cell['episodes']
    assert set(cell['response'])==set(P.CONDITIONS) and cell['before_response']
    assert len(calls)==4


def test_unqualified_initial_source_has_no_treatment_response(monkeypatch):
    s=P.load_settings();s['elements']=6;seen=[]
    def unqualified(grid,*args):
        return grid,{'qualified':False},{'qualification':{'qualified':False},'_prefixes':[]}
    monkeypatch.setattr(P,'qualify_episode',unqualified)
    def diagnostic(grid,alpha,scope):
        seen.append((scope,[c.output for o in grid.owners for c in o.cohorts]));return {'fixture':True}
    monkeypatch.setattr(A,'descriptor',diagnostic);monkeypatch.setattr(F,'native',lambda:(None,{'fixture':True}))
    result=P.run_world(s,882902,0)
    assert result['invalid'] is None and not result['turns'] and not result['chain_complete']
    assert result['initial_source']['no_treatment_response']=={'fixture':True}
    assert seen==[('turn1/source/no-treatment-response',[])]


def test_primary_ci_correction_and_empty_resample_policy():
    s=P.load_settings();s['ci_level']=.95;s['bootstrap_resamples']=1
    with pytest.raises(ValueError,match='uncorrected'):E.evaluate([row(i) for i in range(40)],s,65,{})
    values=[.2,np.nan];draws=np.array([[0,0],[1,1]])
    assert E.bootstrap(values,draws,.996875) is None
    assert E.bootstrap(values,np.array([[0,0],[0,1]]),.996875)==[.2,.2]
    assert P.load_settings()['bootstrap_empty_policy']=='INCONCLUSIVE_IF_ANY_EMPTY'


def test_final_entropy_excludes_old_development_reference_and_fixture_namespaces():
    s=P.load_settings()
    required={33333,46033001,46033002,46033009,*range(46034001,46034006),*range(46035001,46035005)}
    assert required<=set(s['reserved_entropy'].values())
    for entropy in s['reserved_entropy'].values():
        with pytest.raises(ValueError,match='reused'):runner.validate_final_entropy(entropy,s)
    for entropy in (True,-1,None,1.):
        with pytest.raises(ValueError):runner.validate_final_entropy(entropy,s)
    runner.validate_final_entropy(2**127+813,s)  # validation only; no RNG or final registration.


def test_development_binding_keeps_world_producers_and_excludes_check_sources():
    bound=gate.dependencies()
    assert 'tests/test_c6_r4_field.py' not in bound and 'tools/c6_r4_mutants.py' not in bound
    assert {'geomind/c6_r4_field_analysis.py','tools/c6_r3_design_gate.py','milestones/c6.json'}<=set(bound)
    final={str(p.relative_to(P.ROOT)) for p in runner.milestones.dependency_files('c6')}
    assert {'tests/test_c6_r4_field.py','tools/c6_r4_mutants.py'}<=final


@pytest.mark.parametrize('platform,unit,factor',[('darwin','bytes',1),('linux','KiB',1024)])
def test_peak_memory_reports_platform_units_and_worker_lifetime(monkeypatch,platform,unit,factor):
    monkeypatch.setattr(P.sys,'platform',platform)
    monkeypatch.setattr(P.resource,'getrusage',lambda *a:SimpleNamespace(ru_maxrss=123))
    value=P.process_memory()
    assert value['peak_rss_bytes']==123*factor
    assert value['memory_measurement']['raw_unit']==unit
    assert 'Lifetime peak' in value['memory_measurement']['scope']


def test_chain_contrasts_use_one_complete_world_mask_for_every_turn_and_control():
    s=P.load_settings();s['bootstrap_resamples']=1000;rows=[synthetic_chain(i) for i in range(40)]
    incomplete=rows[0];incomplete['chain_complete']=False;incomplete['enabled_witness']=False
    incomplete['turns']=incomplete['turns'][:1];incomplete['links']=[]
    reserved=incomplete['turns'][0]['episodes']['intact'][0]['qualification']
    reserved['qualified']=False;reserved['publication']=None
    incomplete['turns'][0]['witness_tuple']=[False,False,False]
    engineering={k:{'passed':True} for k in ('source_pin','b_reference_equivalence','b_transform_equivariance')}
    result=E.evaluate(rows,s,42,engineering)
    for key in E.PRIMARY:
        cell=result['endpoint_coverage']['evaluated'][key]
        if key.startswith('b_chain_'):
            assert cell['value']['world_ids']==list(range(1,40))
        elif key.endswith('turn1'):
            assert cell['value']['world_ids']==list(range(40))

def test_unsuccessful_source_raw_response_stays_in_world_artifact(tmp_path):
    s=P.load_settings();s['bootstrap_resamples']=1000;rows=[row(i) for i in range(40)]
    raw=[{'port':i,'quadrature':q,'response_real_imag':[[[0.,0.]]*25 for _ in range(100)]}
         for i in range(25) for q in (0,1)]
    response={'raw':raw,'gain_by_dt':[0.]*3,'per_probe_by_dt':[[0.]*50]*3,'alpha':.3,
              'phase_origin_by_dt':[0.]*3,'snapshot_ids':['a'*64]*3,'site_ids':list(range(25))}
    rows[0]['initial_source']['no_treatment_response']=response
    original=json.dumps(rows[0],sort_keys=True)
    engineering={k:{'passed':True} for k in ('source_pin','b_reference_equivalence','b_transform_equivariance')}
    result=E.evaluate(rows,s,42,engineering)
    value=result['endpoint_coverage']['evaluated']['b_source_population_inputs']['value'][0]['source']['no_treatment_response']
    assert value['raw']=={'artifact':'world_000.json.gz','json_pointer':'/initial_source/no_treatment_response/raw'}
    assert {k:v for k,v in value.items() if k!='raw'}=={k:v for k,v in response.items() if k!='raw'}
    assert json.dumps(rows[0],sort_keys=True)==original
    gate.write_world(tmp_path,rows[0])
    saved=json.loads(gzip.decompress((tmp_path/value['raw']['artifact']).read_bytes()))
    assert saved['initial_source']['no_treatment_response']['raw']==raw
