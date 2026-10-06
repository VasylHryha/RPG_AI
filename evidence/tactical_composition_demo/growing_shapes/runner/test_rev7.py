"""Affected synthetic contracts only. Never execute N1, F1-F9, a world, or a panel."""
from contextlib import contextmanager
from copy import deepcopy
from collections import deque
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import pytest
from evidence.tactical_composition_demo.growing_shapes.medium.medium import Params,Drive,Medium
from evidence.tactical_composition_demo.growing_shapes.medium.rev7_native import Rev7Native
from evidence.tactical_composition_demo.growing_shapes.medium.rev7_design import Rev7Medium,Frame,clear_position,pair_valid,individual_valid
from evidence.tactical_composition_demo.growing_shapes.medium.rev7_rhs import lists,rhs
from evidence.tactical_composition_demo.growing_shapes.runner import rev7_protocol as p
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_config import CONFIG,CONFIG_SHA256,N1_RECIPES,PIN_TABLE
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_inventory import construct,check_disjoint
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_execution import Execution
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_fixtures import scaffold,literal_start,compare_n1,f1c_response,Harness
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_run import Run
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_control import Matched,Queue
from evidence.tactical_composition_demo.growing_shapes.runner import rev7_qualification as q
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_evaluator import reused_calibration,descriptive_modes,descriptive_comparisons
from evidence.tactical_composition_demo.growing_shapes.runner.protocol import template as old_template
from evidence.tactical_composition_demo.growing_shapes.runner.rev6_protocol import template as six_template
from evidence.tactical_composition_demo.growing_shapes.medium.rev6_design import Rev6Medium
HERE=Path(__file__).parent

@contextmanager
def medium(**kw):
    m=Rev7Medium(growth_rng=p.generator('synthetic/contracts'),**kw)
    try:yield m
    finally:m.close()

def drive(phase=.4,strength=2.,id=0,x=4.,y=0.):return Drive(id,x,y,phase,math.pi,strength,1.,3.)

def history(m,*,bounds=None):
    es=m.native.elements;m.frames.clear()
    for k in range(101):
        time=k*.1
        m.frames.append(Frame(k,time,{e.id:(e.x,e.y,math.pi*time) for e in es},
            {0:(4.,0.,math.pi*time,2.)},{e.id:tuple(f.id for f in es if f.id!=e.id) for e in es},
            {e.id:bounds(k,e.id) if bounds else 0. for e in es},{}))
    m.step_index=100


def test_lambda_coupling_drive_only_and_carrier():
    with medium() as m:
        m.add((3.,.2),.3,2.8,gain=.7);m.add((2.4,.4),1.,3.3,role='output')
        m.native.set_drives([drive()]);m.native.phase_scale(1);one=np.array(m.native.rhs())
        for scale in (8.,32.):
            m.native.phase_scale(scale);scaled=np.array(m.native.rhs())
            np.testing.assert_array_equal(one[:,:2],scaled[:,:2])
            np.testing.assert_allclose(scaled[:,2]-[2.8,3.3],scale*(one[:,2]-[2.8,3.3]),atol=1e-14)
        assert CONFIG['carrier']==math.pi and CONFIG['clocks']==dict(estimator=10.,qualification=60.,adaptation=.05,freq_cut=.005,pattern_cut=.1)


def test_separate_counts_tie_order_cutoffs_and_silence():
    with medium(params=Params(k=2)) as m:
        a=m.add((0.,0.),0.);b=m.add((1.,0.),0.);c=m.add((-1.,0.),0.)
        m.native.silence(b);m.native.set_drives([drive(id=9,x=0,y=1),drive(id=3,x=0,y=-1)])
        phase,motion=lists(m.native.elements,m.native.reference_drives(),2)
        assert motion[0]==[1,2] # elements before sites, then persistent id
        assert phase[0]==[2] and phase[1]==[]
        assert m.native.motion_neighbors()==motion
        assert m.native.neighbors()[2][0]==1.
        m.native.set_drives([drive(x=3,y=0)])
        assert all(j>=0 for j in m.native.motion_neighbors()[0]) # strict radius
        m.native.set_drives([drive(strength=0,x=0,y=.1)])
        assert all(j>=0 for row in m.native.motion_neighbors() for j in row)
        assert m.native.rhs()[1][:2]!=[0.,0.] # silenced body's motion role retained


def test_nearest_sites_sorted_by_id_with_own_mean():
    with medium(params=Params(k=2)) as m:
        m.add((0,0),.3);m.native.set_drives([drive(id=7,x=1,y=0),drive(id=1,x=-1,y=0)])
        assert m.native.motion_neighbors()==[[-2,-1]]
        assert m.native.neighbors()[0]==[[]]
        es=m.native.elements;ds=m.native.reference_drives();phase,motion=lists(es,ds,2)
        expected,_=rhs(np.array([[0.,0.,.3]]),es,ds,phase,motion,m.native.params,[1.],set(),set())
        np.testing.assert_allclose(m.native.rhs(),expected,rtol=0,atol=1e-14)


def test_site_vector_regularization_coincidence_and_inside_cutoff():
    for x in (4.,3.9,3.7):
        with medium() as m:
            m.add((x,0),math.pi,gain=0.);m.native.set_drives([drive(phase=0)])
            dx=4-x;rr=max(abs(dx),.3)
            expected=(1+.8*math.cos(-math.pi)-1/rr)*dx/rr
            assert m.native.rhs()[0][0]==pytest.approx(expected,abs=1e-14)
            assert m.native.rhs()[0][2]==math.pi


def test_stage_mask_pins_lesion_save_load_and_policy():
    with medium() as m:
        m.add((3.3,.2),1.,gain=1.);out=m.add((2.7,.1),0.,role='output')
        m.native.lesions([out]);m.native.set_drives([drive(phase=1.4)])
        m.native.step(.005)
        assert all(stage[1][:2]==[0.,0.] for stage in m.native.stage_terms())
        assert m.native.pin(out)==(True,(2.7,.1))
        with pytest.raises(ValueError,match='pinned'):m.native.set_element(out,0,0,0,math.pi)
        m.native.comparator('site_body_off');m.native.comparator('fixed_structure')
        loaded=Rev7Native.load(m.native.save());clone=m.native.clone()
        try:
            assert loaded.save()==m.native.save()==clone.save()
            assert loaded.policy()==(32.,True,False)
            assert loaded.excursion()==m.native.excursion()
        finally:loaded.close();clone.close()


@pytest.mark.parametrize('scale',[1.,8.,32.])
@pytest.mark.parametrize('h',[.005,.00125])
@pytest.mark.parametrize('mode',[None,'site_body_off','k_zero','fixed_structure'])
def test_native_independent_python_step_parity(scale,mode,h):
    with medium(h=h) as native:
        native.add((3.25,.27),.7,3.4,.8);native.add((2.5,-.2),-.2,2.9,role='output');native.add((3.6,.5),1.5,3.1,0.)
        native.native.phase_scale(scale)
        if mode:native.native.comparator(mode)
        reference=native.clone();reference.backend='reference'
        try:
            for j in range(3):
                a=native.integrate([drive(phase=.4+math.pi*native.time),drive(id=2,x=2.828,y=2.828,phase=1.+math.pi*native.time)])
                b=reference.integrate([drive(phase=.4+math.pi*reference.time),drive(id=2,x=2.828,y=2.828,phase=1.+math.pi*reference.time)])
                np.testing.assert_allclose([[e.x,e.y,e.phase] for e in native.native.elements],[[e.x,e.y,e.phase] for e in reference.native.elements],rtol=0,atol=2e-14)
                np.testing.assert_allclose(list(a['excursion'].values()),list(b['excursion'].values()),rtol=0,atol=3e-15)
                assert a['motion_neighbors']==b['motion_neighbors'] and native.influence()==reference.influence()
        finally:reference.close()


@pytest.mark.parametrize('h',[.005,.00125])
def test_frame_bound_sums_stages_and_recorded_endpoints(h):
    with medium(h=h) as m:
        m.add((3.4,.1),1.,gain=2.)
        m.integrate([drive(phase=-1.,strength=4)])
        with medium(frozen=True,h=h) as manual:
            manual.add((3.4,.1),1.,gain=2.);manual.native.set_drives([drive(phase=-1.,strength=4)])
            expected=0.
            for j in range(round(.1/h)):
                manual.native.step(h);expected+=h*max(abs(math.pi+stage[0][0]+stage[0][1]-math.pi) for stage in manual.native.stage_terms())
            assert m.frame_excursion[0]==pytest.approx(expected,abs=1e-14)
            assert m.frames[-1].excursion[0]==m.frame_excursion[0]
            assert [f.index for f in m.frames]==[0,1]


def test_pair_only_validity_records_and_80_active_rule():
    with medium() as m:
        a=m.add((3.4,.1),0.);b=m.add((3.1,.1),0.)
        history(m,bounds=lambda k,id:.8 if k>=80 else 0.)
        f=m.frames[-1];assert individual_valid(f,a) and individual_valid(f,b) and not pair_valid(f,a,b)
        assert m.offsets(a,b) is None # 21 invalid pair records leave only 79 active
        assert m.offsets(a,0,True) is not None and m.gain_signal(a)==1.
        assert len(m.frames)==101 and m.samples(a,101) is not None
        history(m,bounds=lambda k,id:.8 if k>=81 else 0.)
        assert len(m.offsets(a,b))==80


def test_individual_invalid_suspends_P_and_rate_only_at_endpoint():
    with medium() as m:
        a=m.add((3.4,.1),0.,rate=2.);history(m,bounds=lambda k,id:2. if k==100 else 0.)
        before=m.native.gain(a);assert m.gain_signal(a) is None
        m.adapt();assert m.native.elements[0].rate==2. and m.native.gain(a)==before
        assert len(m.frames)==101


def test_rate_start_endpoint_invalid_suspends_but_interior_invalid_does_not():
    for invalid_index in (0,50):
        with medium() as m:
            a=m.add((3.4,.1),0.,rate=2.)
            history(m,bounds=lambda k,id:2. if k==invalid_index else 0.)
            assert individual_valid(m.frames[-1],a) and m.gain_signal(a)==1.
            m.adapt()
            assert m.native.elements[0].rate==pytest.approx(2. if invalid_index==0 else 2.+.005*(math.pi-2.))
            assert len(m.frames)==101


def test_clearance_every_rule_origin_reservation_and_Bpath_trial():
    assert not clear_position((4.,0.),[]) and clear_position((3.7,0.),[])
    assert not clear_position((3.700001,0.),[]) and clear_position((3.699999,0.),[])
    assert clear_position((.05,0.),[(0.,0.)]) and not clear_position((.049999,0.),[(0.,0.)])
    with medium() as m:
        m.add((.01,0),0.)
        assert m.b_out()==[] and not m.influence().outputs
        assert m.events[-1]['values']['outcome']=='placement'
        m.remove(0,'SYNTHETIC');assert len(m.b_out())==1
        assert m.native.elements[0].x==m.native.elements[0].y==0.
        assert m.feasible((4.,0.),0.)=='placement'
        point,_=m.spiral_candidate((4.,0.),m.request('B1',0),'B1')
        assert math.hypot(point[0]-4,point[1])>=.3
        assert m.trial(0,1,1,(4,0))['clearance'] is False


def test_B1_freezes_hidden_defers_check_resumes_and_retains_refusal():
    with medium() as m:
        m.novelty[0]=20.;m.drives=[drive(strength=0)];m.frames.clear();m.record()
        m.timers();assert m.novelty[0]==20. and m.b1()==[]
        assert m.events[-1]['rule']=='queued_demand'
        m.drives=[drive()];m.frames.clear();m.record();m.timers()
        assert m.novelty[0]==20.1
        m.b1(blocked=True);assert m.novelty[0]==20.1
        assert m.events[-1]['values']['outcome']=='cost'
        assert len(m.b1())==1 and m.novelty[0]==0.


def test_coverage_resets_only_active_timer_and_quota_retains():
    with medium() as m:
        m.add((3.4,.1),0.);history(m);m.drives=[drive()]
        m.novelty[0]=22.;m.timers();assert m.novelty[0]==0.
        m.novelty={s:20. for s in range(8)}
        m.drives=[drive(id=s,x=4*math.cos(s*math.pi/4),y=4*math.sin(s*math.pi/4)) for s in range(8)]
        m.b1();assert m.novelty[2]==20.
        assert any(e['rule']=='birth_terminal' and e['values']['outcome']=='quota' for e in m.events)


def test_empty_start_all_policies_no_world_or_rng_initial_draw(monkeypatch):
    from evidence.tactical_composition_demo.growing_shapes.runner import rev7_run
    monkeypatch.setattr(rev7_run,'Library',lambda:object())
    rows=reused_calibration()[0]
    for policy in ('intact','M','U'):
        run=Run(0,rows,episodes=1,policy=policy)
        try:
            assert run.medium.h==.005 and run.medium.native.policy()[0]==32.
            assert not len(run.medium.native) and run.medium.step_index==0 and len(run.medium.frames)==1
            assert run.medium.novelty=={s:0. for s in range(8)} and not run.medium.birth_steps
            assert run.medium.native.add(0,0,0,math.pi)==0
        finally:run.close()


def test_templates_pins_versions_shift_and_legacy_loaders():
    with medium() as m:
        m.add((3.1,.2),.4);m.add((-.5,0),.2,role='output')
        value=p.template(m.native,[1,0],0.);copy=p.copy_template(value,math.pi)
        try:
            assert copy.native.pin(1)==(True,(-.5,0.))
            assert p.template(copy.native,[0,1],copy.time)['members'][1][6:]==[True,[-.5,0.]]
            altered=deepcopy(value);altered['members'][1][7]=[0.,0.]
            with pytest.raises(ValueError,match='pin'):p.validate_template(altered)
            assert p.template_hash(value)!=p.template_hash(altered)
        finally:copy.close()
    for ctor,make in [(Medium,old_template),(Rev6Medium,six_template)]:
        legacy=ctor()
        try:
            id=legacy.native.add(0,0,.4,math.pi) if isinstance(legacy,Rev6Medium) else legacy.add(0,0,.4,math.pi)
            native=legacy.native if isinstance(legacy,Rev6Medium) else legacy
            value=make(native,[id],0.);copy=p.copy_template(value)
            try:assert make(copy.native,[0],0.)==value
            finally:copy.close()
        finally:legacy.close()


def test_inventory_instantiated_disjoint_and_exact_seed_byte_orders():
    inventory=construct();assert check_disjoint(inventory)['status']=='DISJOINT'
    saved=json.loads((HERE/'REV7_SEED_INVENTORY.json').read_text());assert saved==inventory
    assert not saved['evaluation_result_exists']
    assert p.training_episode('reward',7,1999)==11151999
    assert {r['donor'] for r in p.donor_entries()}==set(range(10000640,10000768))
    master=p.seed('recovery/synthetic')
    expected=int.from_bytes(hashlib.sha256(f'{master}:kick:1234'.encode()).digest()[:8],'little')
    np.testing.assert_array_equal(p.recovery_generator(master,1234).normal(size=3),np.random.default_rng(expected).normal(size=3))
    overlap=deepcopy(saved);overlap['world_pools']['bad']=deepcopy(overlap['world_pools']['F6'])
    with pytest.raises(ValueError,match='overlap'):check_disjoint(overlap)


def test_literals_construct_only_new_F1c_F4_F5ii_and_N1_recipe():
    for kind in ('F1a','F1b','F1c','F2a','F2b','F3','F4'):
        m=scaffold(kind)
        try:
            assert m.step_index==0
            outputs=[e for e in m.native.elements if m.role(e.id)=='output']
            if outputs:assert [outputs[0].x,outputs[0].y]==PIN_TABLE[kind]
            if kind=='F1c':
                m.drives=[drive()];assert 0 not in m.influence().incoming[6]
                assert len(m.native)==7
            if kind=='F4':assert m.native.elements[0].x==3.7
        finally:m.close()
    m=literal_start()
    try:
        assert np.mean([e.x for e in m.native.elements[:6]])==pytest.approx(3.1)
        assert all(clear_position((e.x,e.y),[(f.x,f.y) for f in m.native.elements if e.id!=f.id]) for e in m.native.elements)
        m.drives=[drive()];assert not m.influence().path(0)
    finally:m.close()
    assert N1_RECIPES['N1d']['members'][1][0]==3.956
    assert N1_RECIPES['N1b']['members'][0][3]==1.5*math.pi


def test_N1_estimator_synthetic_unwrapped_turn_position_and_entry_failures():
    rows=[dict(time=(j+1)*.1,phases=[0.],positions=[[0.,0.]],free=[True],phase_topology={0:[]},motion_topology={0:[]},pin_invariant=True,minimum_distances=dict(element_element=None,element_site=None),excursion={0:0.}) for j in range(160)]
    assert compare_n1(rows,deepcopy(rows),True)['verdict']=='PASS' # neither enters
    ordered=deepcopy(rows)
    for row in ordered:
        row['phase_topology']={0:[1,2]}
        row['excursion']={0:0.,1:0.,2:0.}
        row['phases']=[0.,0.,0.];row['positions']=[[0.,0.],[.5,0.],[1.,0.]];row['free']=[True,True,True]
    shuffled=deepcopy(ordered)
    for row in shuffled[:2]:row['phase_topology']={0:[2,1]}
    assert compare_n1(ordered,shuffled,False)['Ntheta_agreement']==158/160
    assert compare_n1(ordered,shuffled,False)['verdict']=='FAIL'
    other=deepcopy(rows);other[0]['phases'][0]=2*math.pi
    r=compare_n1(rows,other,False);assert r['maximum_wrapped_phase']==0 and r['verdict']=='FAIL'
    other=deepcopy(rows);other[0]['positions'][0][0]=.02
    assert compare_n1(rows,other,False)['verdict']=='FAIL'
    other=deepcopy(rows);other[100]['phases'][0]=math.pi/2
    assert compare_n1(rows,other,True)['entry_pass'] is False
    other=deepcopy(rows);other[0]['phases'][0]=float('nan')
    with pytest.raises(ValueError,match='INVALID'):compare_n1(rows,other,False)


def test_F1c_gate_synthetic_inclusive_entry_hold_access_persistence():
    rows=[dict(time=(j+1)*.1,beta=0. if j<100 else math.pi/2,drive_access=True,pin_invariant=True) for j in range(1600)]
    assert f1c_response(rows)['response_pass']
    other=deepcopy(rows);other[200]['beta']=0.
    assert not f1c_response(other)['response_pass']
    other=deepcopy(rows)
    for row in other[1000:]:row['drive_access']=False
    assert not f1c_response(other)['response_pass']


def test_admissible_kick_free_RMS_phase_output_included_no_clipping():
    with medium() as m:
        a=m.add((0.,.6),0.);b=m.add((.7,.6),.2);o=m.add((0.,0.),.4,role='output')
        values,report=q.admissible_kick(m,dict(ids=[a,b,o]),p.generator('synthetic/kick'))
        assert values is not None and report['free_count']==2 and report['clipped'] is False
        assert report['achieved_position_rms']==pytest.approx(report['requested_position_rms'],rel=1e-14)
        assert report['achieved_phase_rms']==pytest.approx(.3,abs=1e-14)
        assert list(values[0][2])==[0.,0.] and values[1][2]!=.4
        for i in (0,1):assert clear_position(values[0][i],[values[0][j] for j in range(3) if j!=i])
        _,report=q.admissible_kick(m,dict(ids=[o]),p.generator('synthetic/kick'))
        assert report['reason']=='no_free_member'


def test_inadmissible_eight_draws_fixed_order(monkeypatch):
    with medium() as m:
        a=m.add((0,.6),0.);b=m.add((.7,.6),0.);o=m.add((0,0),0.,role='output')
        class Rng:
            calls=0
            def normal(self,size):self.calls+=1;return np.ones(size)
        rng=Rng();monkeypatch.setattr(q,'clear_position',lambda *args:False)
        values,report=q.admissible_kick(m,dict(ids=[a,b,o]),rng)
        assert values is None and report['reason']=='inadmissible_kick' and report['draws']==8 and rng.calls==8


def test_qualification_screens_cohort_before_circular_criteria(monkeypatch):
    with medium() as m:
        for point in ((0,0),(.6,0),(.3,.5)):m.add(point,0.)
        m.step_index=600;m.frames.clear()
        for k in range(601):m.frames.append(Frame(k,k*.1,{e.id:(e.x,e.y,math.pi*k*.1) for e in m.native.elements},{},{e.id:() for e in m.native.elements},{e.id:.8 for e in m.native.elements},{}))
        monkeypatch.setattr(q.c4,'locked_pairs',lambda *args:pytest.fail('circular criterion before mask'))
        result=q.start(m);assert not result['candidates'] and result['reason']=='fast_transient_cohort'
        assert result['invalid_pair_frames']==601


@pytest.mark.parametrize('invalid_ids',[(3,),(0,1)])
def test_recovery_validity_uses_candidate_pairs_only(monkeypatch,invalid_ids):
    # Both replays are stubs: no integration, fixture, world or recovery run.
    with medium() as m:
        for point in ((0.,0.),(.6,0.),(.3,.5),(5.,5.)):m.add(point,0.)
        candidate=dict(ids=[0,1,2],indices=np.array([0,1,2]),stats=dict(size=3,membership_jaccard=1.,shape_cv=0.,lock_std=0.,freq_change=0.,pattern_change=0.),template={})
        check=dict(cohort=[0,1,2,3],candidates=[candidate],possibly_aliased=False,locked=np.ones((4,4),dtype=bool))
        calls=[]
        def replay(branch,drives):
            assert branch.h==.005 and branch.native.policy()[0]==32.
            calls.append(branch)
            return dict(excursion={id:2. if id==3 and id in invalid_ids else .8 if id in invalid_ids else 0. for id in range(4)})
        monkeypatch.setattr(Rev7Medium,'integrate',replay)
        monkeypatch.setattr(q,'admissible_kick',lambda *args:((np.array([[e.x,e.y] for e in m.native.elements]),np.array([e.phase for e in m.native.elements])),dict(reason=None)))
        admitted,seconds=q.finish(m,check,[[]]*600,p.generator('synthetic/replay'))
        assert len(calls)==1200 and seconds==120.
        if invalid_ids==(3,):
            assert admitted==[candidate] and check['recovery_accounting']['skips']['fast_transient_cohort']==0
        else:
            assert not admitted and candidate['skip']=='fast_transient_cohort'
            assert check['recovery_accounting']['skips']['fast_transient_cohort']==1


def test_f5_descriptive_qualification_fraction_boundaries_and_empty_denominator(monkeypatch):
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_reporting import f5_qualification_summary
    events=[dict(time=t,rule='qualification',values=dict(reason=reason)) for t,reason in ((60.,'small_cohort'),(640.,'fast_transient_cohort'),(660.,None),(720.,'fast_transient_cohort'))]
    # Recovery skips must not count as not-qualified qualification windows.
    events.append(dict(time=700.,rule='recovery_complete',values=dict(reason='fast_transient_cohort')))
    frames=[dict(index=k,excursion={0:e,1:e},invalid_pairs=[(0,1)] if pair else []) for k,e,pair in ((6400,.8,True),(6401,0.,False),(7200,2.,True),(7201,0.,False))]
    result=f5_qualification_summary(events,frames,(40,45,50))
    assert result['used_in_verdict'] is False and 'verdict' not in result
    assert result['whole']['qualification_windows']==4
    assert result['whole']['not_qualified_invalid_pair_fraction']==.5
    assert result['whole']['fast_transient_frames']==2 # pair-only + individual, no double count
    a,b,c=result['checkpoint_intervals']
    assert a['qualification_windows']==b['qualification_windows']==2
    assert a['fast_transient_frames']==b['fast_transient_frames']==1
    assert c['qualification_windows']==0 and c['not_qualified_invalid_pair_fraction'] is None
    # Ensure the event feeding the summary carries the screen's actual reason.
    run=Run.__new__(Run);run.medium=type('FakeMedium',(),{})()
    run.medium.step_index=600;run.medium.time=60.;run.medium.birth_steps={};run.medium.h=.005
    run.medium.native=type('FakeNative',(),{'save':lambda self:b'','policy':lambda self:(32.,False,True),'elements':[]})()
    run.medium.death={};run.medium.novelty={};run.medium.frames=[]
    run.medium.clone=lambda **kwargs:run.medium
    emitted=[];run.medium.emit=lambda rule,**values:emitted.append((rule,values))
    run.exposure={'qualification_frames':0};run.pending=[];run.timing={'qualification':0.}
    monkeypatch.setattr(q,'start',lambda m:dict(cohort=[0,1,2],candidates=[],alias_max=2.,possibly_aliased=True,reason='fast_transient_cohort'))
    run.qualify()
    assert emitted[0][1]['reason']=='fast_transient_cohort'


def test_site_off_total_effect_recomputes_counts_keeps_drive_phase_graph():
    with medium() as m:
        m.add((3.2,.1),.2);m.add((2.6,.1),.4,role='output');m.native.set_drives([drive()])
        before=m.native.rhs();phase=m.native.neighbors();counts=[len(row) for row in m.native.motion_neighbors()]
        m.native.comparator('site_body_off');after=m.native.rhs()
        assert m.native.neighbors()==phase
        assert [row[2] for row in before]==[row[2] for row in after]
        assert counts[0]==2 and len(m.native.motion_neighbors()[0])==1
    assert 'site_body_off' in descriptive_modes('perceive') and 'site_body_off' not in descriptive_modes('move')
    scores={mode:[.1]*128 for mode in ('intact','k_zero','fixed_structure','input_phasor','site_body_off')}
    result=descriptive_comparisons('perceive',scores)['site_body_off']
    assert result['used_in_verdict'] is False and 'positive' not in result['estimate']


def test_stop_table_complete_and_default_execution_blocks_all():
    assert len(p.STOP_ROWS)==17 and len({row[0] for row in p.STOP_ROWS})==17
    assert p.stops({'F7_unmatched':True})==[dict(question='F7_unmatched',action='Block development; write failure report',role='drafter')]
    for scope in ('fixtures','development'):
        with pytest.raises(PermissionError,match='reviewed'):Execution().require(scope)
    h=Harness.__new__(Harness);h.execution=Execution();h.results={};h.identity_snapshot=None
    with pytest.raises(PermissionError):h.require('F1')


def test_fixture_sequence_stub_stops_N1_F5_F7_without_executing(monkeypatch):
    class FakeExecution:
        def start(self,scope):return {'synthetic':True}
    for stop in ('N1','F5','F7'):
        h=Harness.__new__(Harness);h.execution=FakeExecution();h.results={};h.calibration={};h.close=lambda:None;calls=[]
        for name in ('N1','F1','F2','F3','F4','F5','F6','F7','F8','F9'):
            def stub(name=name):calls.append(name);return dict(verdict='FAIL' if name==stop else 'PASS')
            setattr(h,name,stub)
        result=h.run_all();assert calls[-1]==stop and result['not_run']


@pytest.mark.parametrize('failed',['F1','F2','F3','F4'])
def test_fixture_sequence_early_fail_runs_independent_checks_then_blocks_F5(failed):
    h=Harness.__new__(Harness);h.execution=type('FakeExecution',(),{'start':lambda self,scope:{'synthetic':True}})()
    h.results={};h.calibration={};h.close=lambda:None;calls=[]
    for name in ('N1','F1','F2','F3','F4','F5','F6','F7','F8','F9'):
        def stub(name=name):calls.append(name);return dict(verdict='FAIL' if name==failed else 'PASS')
        setattr(h,name,stub)
    result=h.run_all()
    assert calls==['N1','F1','F2','F3','F4']
    assert result['not_run']==['F5','F6','F7','F8','F9']


@pytest.mark.parametrize('invalid',['N1','F1','F2','F3','F4'])
def test_fixture_sequence_any_invalid_blocks_next_stage(invalid):
    h=Harness.__new__(Harness);h.execution=type('FakeExecution',(),{'start':lambda self,scope:{'synthetic':True}})()
    h.results={};h.calibration={};h.close=lambda:None;calls=[]
    for name in ('N1','F1','F2','F3','F4','F5','F6','F7','F8','F9'):
        def stub(name=name):calls.append(name);return dict(verdict='INVALID' if name==invalid else 'PASS')
        setattr(h,name,stub)
    result=h.run_all()
    assert calls[-1]==invalid and result['results'][invalid]['verdict']=='INVALID'


def test_preservation_baseline():
    root=HERE.parents[3];old=json.loads((HERE/'REV7_LEGACY_BASELINE.json').read_text())
    for name,expected in old['sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,name


def test_development_fixture_receipt_requires_all_gates_and_current_pin(tmp_path):
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_execution import validate_fixture_receipt
    with pytest.raises(PermissionError,match='required'):validate_fixture_receipt('', 'pin')
    path=tmp_path/'synthetic_fixture.json'
    value=dict(revision='7.4',identity_snapshot=dict(pin_sha256='pin'),results={name:dict(verdict='DESCRIPTIVE' if name in ('F6','F8','F9') else 'PASS') for name in ('N1','F1','F2','F3','F4','F5','F6','F7','F8','F9')},not_run=[],stops=[])
    path.write_text(json.dumps(value));assert validate_fixture_receipt(path,'pin')['sha256']
    with pytest.raises(PermissionError,match='mismatch'):validate_fixture_receipt(path,'stale-pin')
    for name in ('N1','F1','F2','F3','F4','F5','F7'):
        failed=deepcopy(value);failed['results'][name]['verdict']='FAIL';path.write_text(json.dumps(failed))
        with pytest.raises(PermissionError,match='FAIL'):validate_fixture_receipt(path,'pin')
    invalid=deepcopy(value);invalid['results']['F6']['verdict']='INVALID';path.write_text(json.dumps(invalid))
    with pytest.raises(PermissionError,match='INVALID'):validate_fixture_receipt(path,'pin')
    incomplete=deepcopy(value);del incomplete['results']['F9'];path.write_text(json.dumps(incomplete))
    with pytest.raises(PermissionError,match='incomplete'):validate_fixture_receipt(path,'pin')

    for name in ('F6','F8','F9'):
        for verdict in (None,'NOT_RUN','FAIL'):
            missing=deepcopy(value);missing['results'][name]={} if verdict is None else dict(verdict=verdict)
            path.write_text(json.dumps(missing))
            with pytest.raises(PermissionError,match='measurement'):validate_fixture_receipt(path,'pin')


def test_clock_ledger_declared_units_no_rescaled_admission_windows():
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_reporting import clock_ledger,INTERPRETATION
    with medium() as m:
        m.add((3.,0),0.);m.add((2.5,0),.2,role='output')
        m.native.set_drives([drive()])
        ledger=clock_ledger(m.native)
        assert ledger['lambda_value']==32. and ledger['ratio_units']=='dimensionless'
        assert ledger['estimator_seconds']==10. and ledger['qualification_seconds']==60.
        assert ledger['geometric_length_reference']==pytest.approx(1/1.8)
        element=next(r for r in ledger['rows'] if r['kind']=='element')
        assert element['scaled_coefficient']==pytest.approx(32*math.exp(-.25))
        assert element['against_carrier']==pytest.approx(element['scaled_coefficient']/math.pi)
        assert element['against_geometric_reference']==pytest.approx(element['scaled_coefficient']/1.8)
        assert INTERPRETATION['revision_7_motion']['status']=='DESCRIPTIVE'


def test_rev74_configuration_identity_and_N1f_literal_recipe():
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_config import F1D_SCALES
    assert CONFIG['revision']=='7.4' and CONFIG['phase_scale']==32.
    assert CONFIG['excursion']['h']==.005 and CONFIG['excursion']['substeps']==20
    assert CONFIG['N1']['h']==[.005,.00125] and CONFIG['N1']['substeps']==[20,80]
    assert F1D_SCALES==(1.,8.,32.) and CONFIG['F1']['F1d']['h']==.005
    assert set(N1_RECIPES)=={'N1a','N1b','N1c','N1d','N1e','N1f'}
    m=scaffold('F1c')
    try:
        assert N1_RECIPES['N1f']['members']==[[e.x,e.y,e.phase,e.rate,m.native.gain(e.id),m.role(e.id)] for e in m.native.elements]
    finally:m.close()
    assert N1_RECIPES['N1f']['seconds']==24. and N1_RECIPES['N1f']['entry_member']==6
    for key,value in [('phase_scale',8.),('excursion',dict(CONFIG['excursion'],h=.02))]:
        altered=deepcopy(CONFIG);altered[key]=value
        assert hashlib.sha256(p.canonical(altered)).hexdigest()!=CONFIG_SHA256
    with pytest.raises(ValueError,match='solver'):Rev7Medium(h=.02)


@pytest.mark.parametrize('h',[.005,.00125])
def test_substep_lists_held_stage_carrier_and_single_frame(monkeypatch,h):
    from evidence.tactical_composition_demo.growing_shapes.medium import rev7_rhs
    original_lists,original_rhs=rev7_rhs.lists,rev7_rhs.rhs
    selections=[];stages=[]
    def select(*args,**kwargs):
        value=original_lists(*args,**kwargs);selections.append(value);return value
    def stage(state,elements,drives,phase,motion,*args,**kwargs):
        stages.append((phase,motion,drives[0].phase));return original_rhs(state,elements,drives,phase,motion,*args,**kwargs)
    monkeypatch.setattr(rev7_rhs,'lists',select);monkeypatch.setattr(rev7_rhs,'rhs',stage)
    with medium(backend='reference',h=h) as m:
        m.add((3.4,.1),.2);m.add((2.9,.1),.3,role='output')
        # Once-per-world-step adaptation/timers/growth are owned by Run,
        # never by integration; catch any accidental call within the loop.
        for name in ('adapt','timers','growth'):
            monkeypatch.setattr(m,name,lambda:pytest.fail('substep clock update'))
        m.integrate([drive()])
        count=round(.1/h)
        assert len(selections)==count and len(stages)==4*count
        for j,(phase,motion) in enumerate(selections):
            for k,offset in enumerate((0.,h/2,h/2,h)):
                assert stages[4*j+k][0] is phase and stages[4*j+k][1] is motion
                assert stages[4*j+k][2]==pytest.approx(.4+math.pi*(j*h+offset),abs=1e-14)
        assert m.step_index==1 and len(m.frames)==2 and m.time==.1
        assert m.drives[0].phase==pytest.approx(.4+math.pi*.1)


@pytest.mark.parametrize('scale',[1.,8.,32.])
@pytest.mark.parametrize('h',[.005,.00125])
def test_solver_policy_clone_template_and_native_snapshot(scale,h):
    with medium(h=h) as m:
        m.add((3.1,.2),.4);m.add((0.,0.),.2,role='output')
        m.native.phase_scale(scale);m.native.comparator('site_body_off');m.native.comparator('fixed_structure')
        value=p.template(m.native,[0,1],m.time,h=m.h)
        clone=m.clone();copy=p.copy_template(value,backend='reference');loaded=Rev7Native.load(m.native.save())
        try:
            assert clone.h==copy.h==h and clone.native.policy()==copy.native.policy()==loaded.policy()==(scale,True,False)
            assert p.template(copy.native,[0,1],copy.time,h=copy.h)==value
            altered=deepcopy(value);altered['solver_policy']['h']=.02
            with pytest.raises(ValueError,match='solver'):p.copy_template(altered)
            altered=deepcopy(value);altered['configuration_sha256']='old revision 7.3'
            with pytest.raises(ValueError,match='schema'):p.copy_template(altered)
        finally:clone.close();copy.close();loaded.close()


def test_N1f_synthetic_24_seconds_masks_disagree_without_new_gate():
    rows=[dict(time=(j+1)*.1,phases=[0.,math.pi/2 if j>=110 else 0.],positions=[[0.,0.],[.6,0.]],free=[True,False],phase_topology={0:[1],1:[0]},motion_topology={0:[1],1:[0]},pin_invariant=True,excursion={0:0.,1:0.}) for j in range(240)]
    fine=deepcopy(rows);rows[200]['excursion']={0:.8,1:.8}
    fine[201]['excursion'][0]=2.
    result=compare_n1(rows,fine,True,1,seconds=24.)
    assert result['verdict']=='PASS' and result['entry_times']==pytest.approx([11.1,11.1],abs=1e-12,rel=0)
    assert result['entry_hold_through_24']==[True,True] and result['hold_used_in_verdict'] is False
    validity=result['validity']
    assert validity['individual_invalid_frames']==[0,1]
    assert validity['used_pair_invalid_frames']==[1,1]
    assert validity['individual_disagreement_frames']==1 and validity['used_pair_disagreement_frames']==2
    assert validity['used_in_verdict'] is False
    with pytest.raises(ValueError,match='unmatched'):compare_n1(rows[:-1],fine,True,1,seconds=24.)
    missing=deepcopy(rows);del missing[0]['excursion'][1]
    with pytest.raises(ValueError,match='INVALID'):compare_n1(missing,fine,True,1,seconds=24.)


def test_F1c_four_second_margin_descriptive_sustained_entry_not_first_touch():
    def records(entry):return [dict(time=(j+1)*.1,beta=math.pi/2 if (j+1)*.1>=entry else 0.,drive_access=True,pin_invariant=True) for j in range(1600)]
    early=f1c_response(records(11.))
    assert early['response_pass'] and early['four_second_margin_met'] and early['error_at_12']==0.
    late=f1c_response(records(15.))
    assert late['response_pass'] and not late['four_second_margin_met'] and late['sustained_entry_delay']==7.
    assert late['error_at_12']==pytest.approx(math.pi/2) and late['margin_used_in_verdict'] is False
    touches=records(15.);touches[99]['beta']=math.pi/2
    response=f1c_response(touches)
    assert response['first_entry_time']==10. and response['sustained_entry_delay']==7.
    assert not response['response_pass'] and not response['four_second_margin_met']


@pytest.mark.parametrize('invalid_count',[20,21])
def test_estimator_window_denominators_pair_only_and_site_exclusions(invalid_count):
    with medium() as m:
        a=m.add((3.4,.1),0.);b=m.add((3.1,.1),0.)
        assert m.estimator_validity()['site'] is None and m.estimator_validity()['element'] is None
        history(m,bounds=lambda k,id:.8 if k>100-invalid_count else 0.)
        values=m.offsets(a,b)
        assert (values is not None)==(invalid_count==20)
        m.offsets(a,b) # repeated consumption of the same directed window counts once
        assert m.offsets(a,0,True) is not None # individual valid despite pair-only failures
        summary=m.estimator_validity();counts=summary['element']
        assert summary['used_in_verdict'] is False
        assert counts['windows']==1 and counts['eligible_observations']==100
        assert counts['valid_observations']==100-invalid_count and counts['transient_exclusions']==invalid_count
        assert counts['rejected_below_80']==int(invalid_count==21)
        assert counts['active_histogram']=={100-invalid_count:1}
        assert summary['site']['valid_observations']==100 and summary['site']['transient_exclusions']==0
    with medium() as m:
        a=m.add((3.4,.1),0.)
        history(m,bounds=lambda k,id:2. if k>100-invalid_count else 0.)
        assert (m.offsets(a,0,True) is not None)==(invalid_count==20)
        counts=m.estimator_validity()['site']
        assert counts['eligible_observations']==100 and counts['transient_exclusions']==invalid_count
        assert counts['active_histogram']=={100-invalid_count:1}
