"""Engineering contracts on separate fixtures; never final/dev world rehearsals."""
import copy
import hashlib
import inspect
import json
from pathlib import Path
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
            'initial_source':{'qualification':{'qualified':False,'candidates':[]}},'seconds':1.,'peak_rss_bytes':100,'native_build':{'fixture':True}}

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
            'witness_tuple':[True,False,False],'physical_outcome':'PERSISTENT_UNIT','before_formation':None}
        result['turns'].append(cell);result['links'].append({'episode':0,'clock':qualified.time,'after_ids':[after.identity()]*3,
            'introduced_ids':[introduced.identity()]*3,'qualified_ids':[qualified.identity()]*3,'next_operation_ids':[qualified.identity()]*3})
        base=qualified
    return result

def test_exact_chain_provenance_and_invalid_controls_are_rejected():
    r=synthetic_chain(0);E.validate_world(r)
    for change in ('source','restage','field','carrier','sham','no_r','inputs','witness','publication'):
        bad=copy.deepcopy(r)
        if change=='source':bad['links'][0]['next_operation_ids']=['wrong']*3
        if change=='restage':bad['turns'][1]['before_ids']=['wrong']*3
        if change=='field':bad['turns'][0]['episodes']['intact'][0]['introduced_states'][0]['fields_real_imag'][0][0]+=.1
        if change=='carrier':bad['turns'][0]['episodes']['intact'][0]['introduced_states'][0]['cohorts'][-1]['carrier_real_imag'][0][0]+=.1
        if change=='sham':bad['turns'][0]['conditions']['no_backreaction']['output_check']['output_max_by_dt'][0]=.001
        if change=='no_r':bad['turns'][0]['conditions']['no_r']['endpoint_qualification']['qualified']=True
        if change=='inputs':bad['turns'][0]['episodes']['no_r'][1]['inputs']={'unmatched':True}
        if change=='witness':bad['turns'][0]['witness_tuple']=[True,True,True]
        if change=='publication':bad['turns'][0]['source']['publication']['snapshot']='0'*64
        with pytest.raises(ValueError):E.validate_world(bad)

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

def test_pending_development_registration_stops_before_output(tmp_path):
    manifest=json.loads((P.ROOT/'experiments/c6_manifest.json').read_text())
    if manifest['status']=='PENDING_DEVELOPMENT_APPROVAL':
        with pytest.raises(SystemExit,match='owner-approved'):gate.main(['--output',str(tmp_path/'unapproved')])
        assert not (tmp_path/'unapproved').exists()

def test_loaded_kernel_identity_is_pinned(monkeypatch):
    F.native();lib,record=F._NATIVE;fake=dict(record);fake['source_sha256']='0'*64
    monkeypatch.setattr(F,'_NATIVE',(lib,fake))
    with pytest.raises(RuntimeError,match='identity'):F.native()

def test_detector_api_has_no_condition_or_expected_subset():
    from geomind import c4_detect as D
    assert set(inspect.signature(D.components).parameters)=={'X','link_factor','locked'}
    assert 'condition' not in inspect.signature(A.select_accepted).parameters
