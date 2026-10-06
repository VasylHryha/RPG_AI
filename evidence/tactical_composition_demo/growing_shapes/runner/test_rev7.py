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
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_fixtures import scaffold,literal_start,compare_n1,n1_case_result,n1_verdict,f1c_response,Harness
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


@pytest.mark.parametrize('backend',['native','reference'])
def test_rev79_weak_connected_scaffold_grows_until_strong_path_reaches_O(backend):
    with medium(backend=backend) as m:
        out=m.b_out()[0]
        root=m.add((3.2,0.),.2)
        m.add((2.644,0.),.2,gain=0.)
        m.drives=[drive()]
        assert m.influence().path(0) and not m.strong_influence().path(0)
        births=[]
        for _ in range(2):
            assert not m.strong_influence().path(0)
            added=m.b_path();assert len(added)==1
            births+=added
            assert m.influence().path(0)
            assert m.native.pin(out)==(True,(0.,0.))
        assert m.strong_influence().path(0)
        assert len(births)==2 and m.b_path()==[]
        assert m.endpoint_diagnostics()['paths'][0]
        assert root in m.strong_influence().roots[0] and out not in m.strong_influence().roots[0]
        attempts={e['values']['request']:e for e in m.events
                  if e['rule']=='birth_attempt' and e['values']['birth_rule']=='B-path'}
        accepted=[e for e in m.events if e['rule']=='birth_terminal'
                  and e['values']['birth_rule']=='B-path' and e['values']['outcome']=='accepted']
        assert len(accepted)==2
        assert all(all(attempts[e['values']['request']]['values']['checks'].values()) for e in accepted)


@pytest.mark.parametrize('backend',['native','reference'])
def test_rev710_empty_start_multiple_sites_completes_bridge_before_budget(backend):
    from evidence.tactical_composition_demo.growing_shapes.medium.design_0h import SITES
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_reporting import b_path_waiting
    with medium(backend=backend) as m:
        assert not m.native.elements
        m.drives=[drive(id=s,x=SITES[s][0],y=SITES[s][1]) for s in (0,2,4)]
        for s in (0,2,4):m.novelty[s]=20.
        out=m.b_out()[0]
        assert m.b_path()==[] and len(m.b1())==2
        for check in range(1,16):
            m.step_index=check*200
            before=len(m.native);births=m.b_path();assert len(births)<=2
            assert len(m.native)==before+len(births)
            m.b1()
            if any(m.strong_influence().path(s) for s in (0,2,4)):break
        else:pytest.fail('no bridge completed in the bounded static synthetic construction')
        assert m.cost()<64 and len(m.native)<64
        assert m.native.pin(out)==(True,(0.,0.))
        rows=b_path_waiting(m.events)['sites']
        assert all(rows[s]['lifetime_counters']['eligible_checks']>0 for s in (0,2,4))
        assert any(rows[s]['lifetime_counters']['unserved_checks']>0 for s in (0,2,4))
        assert rows[7]['lifetime_counters']['accepted_births']==0
        assert rows[7]['last_outcome']=='inactive'


def test_rev710_native_reference_multisite_order_events_and_geometry_identical():
    with medium(backend='native') as native,medium(backend='reference') as reference:
        for m in (native,reference):
            m.b_out();m.add((3.3,0.),.2);m.add((-3.8,0.),.2)
            m.drives=[drive(id=0),drive(id=4,x=-4.)];m.pointer=4
        for _ in range(5):
            assert native.b_path()==reference.b_path()
            assert native.pointer==reference.pointer
            assert native.events==reference.events
            assert [(e.id,e.x,e.y,e.phase) for e in native.native.elements]==[(e.id,e.x,e.y,e.phase) for e in reference.native.elements]
            assert native.strong_influence()==reference.strong_influence()


@pytest.mark.parametrize('backend',['native','reference'])
def test_rev710_shortest_deficit_overrides_pointer_and_exact_ties_rotate(backend):
    with medium(backend=backend) as m:
        m.b_out();m.add((3.2,0.),0.);m.add((-3.8,0.),0.)
        m.drives=[drive(id=0),drive(id=4,x=-4.)];m.pointer=4
        m.b_path(blocked=True)
        requests=[e['values']['site'] for e in m.events if e['rule']=='birth_request' and e['values']['birth_rule']=='B-path']
        assert requests==[0,4] and m.pointer==5
    with medium(backend=backend) as m:
        m.b_out();m.add((3.2,0.),0.);m.add((-3.2,0.),0.)
        m.drives=[drive(id=0),drive(id=4,x=-4.)];m.pointer=4
        for expected in ([4,0],[0,4]):
            begin=len(m.events);m.b_path(blocked=True)
            requests=[e['values']['site'] for e in m.events[begin:] if e['rule']=='birth_request' and e['values']['birth_rule']=='B-path']
            assert requests==expected
        assert m.pointer==6


@pytest.mark.parametrize('backend',['native','reference'])
def test_rev710_no_root_infinite_ties_empty_checks_and_wait_pause_reset(backend):
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_reporting import b_path_waiting,descriptive
    with medium(backend=backend) as m:
        assert m.b_path()==[] and m.pointer==1
        m.drives=[drive(id=0),drive(id=2,x=0.,y=4.)]
        for _ in range(2):m.b_path()
        rows=b_path_waiting(m.events)['sites']
        assert rows[0]['lifetime_counters']['current_wait_checks']==2
        assert rows[0]['outcomes_in_window']['no_output']==2
        m.drives=[];m.b_path()
        assert m.path_waiting[0]['current_wait_checks']==2
        m.b_out();m.drives=[drive(id=0)]
        m.b_path();assert m.events[-8]['values']['outcome']=='no_root'
        assert m.path_waiting[0]['current_wait_checks']==3
        m.add((3.2,0.),0.);assert len(m.b_path())==1
        assert m.path_waiting[0]['current_wait_checks']==0
        assert m.path_waiting[0]['maximum_wait_checks']==3
        report=descriptive(m.events,[],[],end=1.)['B_path_waiting']
        assert report['finite_wait_bound'] is False and len(report['sites'])==8
        assert report['sites'][0]['lifetime_counters']['accepted_births']==1
        assert report['sites'][2]['lifetime_counters']['current_wait_checks']==2
        assert all(r['lifetime_counters'] is None for r in b_path_waiting([])['sites'].values())
        # Connection resets active wait even without an insertion for this site.
        m.path_waiting[0]['current_wait_checks']=7
        m.native.set_gain(0,0.) # O remains ineligible as a root.
        m.add((1.5,0.),0.)
        assert m.strong_influence().path(0)
        m.b_path();assert m.path_waiting[0]['current_wait_checks']==0


def test_rev710_reporting_works_with_append_only_chunk_events(tmp_path):
    from evidence.tactical_composition_demo.growing_shapes.runner.rev6_trace import Chunks
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_reporting import b_path_waiting
    with medium() as m:
        m.events=Chunks(tmp_path/'events')
        m.drives=[drive()];m.b_path();m.b_out();m.b_path()
        rows=b_path_waiting(m.events)['sites']
        assert rows[0]['lifetime_counters']['current_wait_checks']==2
        assert rows[0]['outcomes_in_window']=={'no_output':1,'no_root':1}
        m.events.close()


@pytest.mark.parametrize('backend',['native','reference'])
def test_rev710_far_site_quota_wait_is_reported_and_shared_connection_rechecked(backend):
    with medium(backend=backend) as m:
        m.b_out()
        for point in ((3.2,0.),(0.,3.3),(-3.8,0.)):m.add(point,0.)
        m.drives=[drive(id=0),drive(id=2,x=0.,y=4.),drive(id=4,x=-4.)]
        m.pointer=4
        assert len(m.b_path())==2
        checks={e['values']['site']:e['values'] for e in m.events if e['rule']=='B_path_check'}
        assert [checks[s]['rank'] for s in (0,2,4)]==[0,1,2]
        assert checks[4]['outcome']=='quota' and checks[4]['current_wait_checks']==1
        assert not checks[4]['path_after']
    with medium(backend=backend) as m:
        m.b_out();m.add((3.2,0.),0.);m.add((2.644,0.),0.,gain=0.)
        m.drives=[drive(id=s,x=4.,y=.01*s) for s in range(3)]
        assert len(m.b_path())==2
        checks={e['values']['site']:e['values'] for e in m.events if e['rule']=='B_path_check'}
        assert all(checks[s]['path_after'] for s in range(3))
        assert checks[2]['outcome']=='connected_by_earlier_birth'
        assert checks[2]['current_wait_checks']==0 and checks[2]['accepted_births']==0


@pytest.mark.parametrize('distance',[
    math.nextafter(math.sqrt(math.log(64)),0.),
    math.sqrt(math.log(64)),
    math.nextafter(math.sqrt(math.log(64)),math.inf),
    2.2,3.])
def test_rev79_native_python_strong_distance_boundary_subset_and_full_mean(distance):
    from evidence.tactical_composition_demo.growing_shapes.medium.rev7_design import geometric_graph,geometry
    with medium() as m:
        out=m.add((0.,0.),0.,role='output');root=m.add((distance,0.),.4)
        m.drives=[drive(x=distance+1.)]
        es,ds=geometry(m.native,m.drives)
        full=m.influence();strong=m.strong_influence()
        assert strong==geometric_graph(es,ds,strong=True)
        assert full==geometric_graph(es,ds)
        assert strong.path(0)==(distance<3. and 32*math.exp(-distance*distance)>=.5)
        assert full.path(0)==(distance<3.)
        assert strong.incoming[out]<=full.incoming[out]
        assert m.native.neighbors()[2][0]==1. # full count, never strong count
        assert m.endpoint_diagnostics()['paths'][0]==strong.path(0)
        assert root in strong.roots[0] and out not in strong.roots[0]


@pytest.mark.parametrize('K,expected',[
    (math.nextafter(1/64,0.),False),(1/64,True),
    (math.nextafter(1/64,math.inf),True),(0.,False),(-1.,False)])
@pytest.mark.parametrize('backend',['native','reference'])
def test_rev79_exact_coefficient_inclusive_boundary(K,expected,backend):
    from evidence.tactical_composition_demo.growing_shapes.medium.rev7_design import geometric_graph,geometry
    # Coincident synthetic points make exp(-r*r)=1 exactly; these do not
    # exercise birth clearance. Multiplication by 32 preserves adjacent ULPs.
    with medium(params=Params(K=K),backend=backend) as m:
        out=m.add((0.,0.),0.,role='output');root=m.add((0.,0.),0.)
        es,ds=geometry(m.native,[])
        assert m.strong_influence()==geometric_graph(es,ds,K=K,strong=True)
        assert (root in m.strong_influence().incoming[out]) is expected
        assert m.influence().incoming[out]=={root}


@pytest.mark.parametrize('backend',['native','reference'])
def test_rev79_full_receiver_degree_direction_and_weak_neighbor_dilution(backend):
    from evidence.tactical_composition_demo.growing_shapes.medium.rev7_design import geometric_graph,geometry
    with medium(backend=backend) as m:
        out=m.add((0.,0.),0.,role='output');root=m.add((2.,0.),0.)
        beyond=m.add((3.5,0.),0.,gain=0.)
        # root->O has n_O=1 (rate .586), reverse has n_root=2 (.293).
        assert m.strong_influence().incoming[out]=={root}
        assert out not in m.strong_influence().incoming[root]
        weak=m.add((0.,2.9),0.,gain=0.)
        # The weak incoming edge itself fails, but must still dilute root->O.
        assert m.influence().incoming[out]=={root,weak}
        assert m.strong_influence().incoming[out]==set()
        es,ds=geometry(m.native,[])
        assert m.strong_influence()==geometric_graph(es,ds,strong=True)
        m.native.silence(weak)
        assert m.strong_influence().incoming[out]=={root}
        m.remove(weak,'SYNTHETIC')
        assert m.strong_influence().incoming[out]=={root}
        assert beyond not in m.influence().incoming[out]


@pytest.mark.parametrize('backend',['native','reference'])
def test_rev79_live_scale_K_and_trial_post_insertion_degree(backend):
    from evidence.tactical_composition_demo.growing_shapes.medium.rev7_design import geometric_trial,geometry
    with medium(backend=backend) as m:
        out=m.add((0.,0.),0.,role='output');root=m.add((2.,0.),0.)
        m.drives=[Drive(0,2.,0.,.4,math.pi,2.,1.,.1)]
        assert m.strong_influence().path(0)
        # Insertion of an unreachable weak neighbour dilutes the existing
        # receiver row and must trigger paths_kept=False, despite fixed geometry.
        es,ds=geometry(m.native,m.drives)
        checks=geometric_trial(es,ds,0,root,out,(0.,2.9),2)
        assert not checks['paths_kept']
        assert m.trial(0,root,out,(0.,2.9))==checks
        m.native.phase_scale(8.)
        assert not m.strong_influence().path(0)
        assert m.trial(0,root,out,(0.,2.9))==geometric_trial(es,ds,0,root,out,(0.,2.9),2,phase_scale=8.)
        m.native.phase_scale(32.)
        m.native.comparator('k_zero')
        assert not m.strong_influence().path(0)
        assert m.trial(0,root,out,(1.,0.))['edge_a_to_new'] is False


def test_rev77_directed_selection_ties_silence_and_topology_refresh():
    from evidence.tactical_composition_demo.growing_shapes.medium.rev7_design import geometric_graph,geometry
    with medium(params=Params(k=1)) as m:
        out=m.add((0.,0.),0.,role='output')
        first=m.add((.5,0.),0.,gain=0.);second=m.add((-.5,0.),0.)
        m.drives=[drive(x=-1.5)]
        assert m.strong_influence().incoming[out]=={first}
        assert out in m.strong_influence().incoming[second]
        assert not m.strong_influence().path(0) # nearest selection is directed
        es,ds=geometry(m.native,m.drives)
        assert m.strong_influence()==geometric_graph(es,ds,k=1,strong=True)
        m.native.silence(first)
        assert m.strong_influence().incoming[out]=={second} and m.strong_influence().path(0)
        assert m.strong_influence().incoming[first]==set()
        es,ds=geometry(m.native,m.drives)
        assert m.strong_influence()==geometric_graph(es,ds,k=1,strong=True)
        m.remove(second,'SYNTHETIC')
        assert not m.strong_influence().path(0)
    with medium() as empty:
        assert empty.native.strong_neighbors()==[] and empty.strong_influence().incoming=={}


def test_rev77_strong_filter_does_not_change_RHS_normalization_or_cost():
    with medium() as m:
        out=m.add((0.,0.),0.,role='output')
        near=m.add((.5,0.),.4,gain=0.);far=m.add((2.2,0.),.4,gain=0.)
        assert m.strong_influence().incoming[out]=={near}
        assert m.influence().incoming[out]=={near,far}
        assert m.native.neighbors()[2][0]==.5
        expected=math.pi+32/2*(math.exp(-.25)+math.exp(-2.2**2))*math.sin(.4)
        assert m.native.rhs()[0][2]==pytest.approx(expected,abs=1e-14)
        assert m.native.cost(1.,.1)==dict(elements=2,active_couplings=1,total=2.1)


def test_rev77_trials_reject_weak_edges_preserve_strong_paths_and_clearance():
    from evidence.tactical_composition_demo.growing_shapes.medium.rev7_design import geometric_trial
    # A formerly admissible weak edge a->new must no longer pass its trial.
    es=[(0,0.,0.,'output',1.,False),(1,2.9,0.,'element',1.,False)]
    ds=[(0,2.9,0.,2.,.1)] # only a is a root; new must be reached through edges
    checks=geometric_trial(es,ds,0,1,0,(.7,0.),2)
    assert not checks['edge_a_to_new'] and not checks['new_reached']
    assert not geometric_trial(es,ds,0,1,0,(2.9,.556),2)['deficit_or_connect']
    # A trial can displace a's source and leave a/new in a disconnected strong cycle.
    crowded=[(0,0.,0.,'output',1.,False),(1,2.4,0.,'element',1.,False),
             (2,1.8,0.,'element',0.,False)]
    checks=geometric_trial(crowded,[(0,2.4,0.,2.,.1)],0,2,0,(1.3,0.),3,k=1)
    assert checks['edge_a_to_new'] and not checks['new_reached'] and not checks['a_reached']
    # Replacing a nearest source can destroy an existing strong route for another site.
    es=[(0,0.,0.,'output',1.,False),(1,.5,0.,'element',1.,False),
        (2,2.4,0.,'element',1.,False)]
    ds=[(0,4.,0.,2.,3.),(1,.5,0.,2.,.1)]
    checks=geometric_trial(es,ds,0,2,0,(.1,0.),3,k=1)
    assert not checks['paths_kept']
    assert not geometric_trial(es,ds,0,2,0,(0.,0.),3)['clearance']


def test_rev77_weak_connectivity_does_not_bypass_budget_refusal():
    with medium() as m:
        m.b_out();m.add((3.2,0.),0.);m.add((2.644,0.),0.,gain=0.)
        m.drives=[drive()];before=len(m.native)
        assert m.influence().path(0) and not m.strong_influence().path(0)
        assert m.b_path(blocked=True)==[] and len(m.native)==before
        terminal=next(e for e in reversed(m.events) if e['rule']=='birth_terminal')
        assert terminal['values']['outcome']=='cost'


@pytest.mark.parametrize('backend',['native','reference'])
def test_rev77_full_D4_budget_and_qualification_history_survive_weak_path(backend):
    with medium(backend=backend) as m:
        out=m.add((0.,0.),0.,role='output');root=m.add((2.2,0.),0.)
        # No active root: full backward liveness alone must protect this element.
        m.drives=[];m.native.cut_off(root,119.9)
        m.timers()
        assert m.native.cut_off(root)==0.
        assert root in m.influence().backward() and root not in m.strong_influence().backward()
        assert m.native.cost(1.,.1)['elements']==1
        m.record()
        assert m.frames[-1].neighbors[out]==(root,)
        assert m.frames[-1].neighbors[root]==(out,)


def test_rev79_configuration_pins_screen_and_preserves_clock_and_entropy():
    policy=CONFIG['strong_links']
    assert policy['rate_min_per_second']==.5
    assert 'full held receiver' in policy['formula']
    assert policy['clock']['tau_link_seconds']==2.
    assert 'no end-to-end' in policy['clock']['status']
    previous=json.loads((HERE/'rev79_delivery/PRIOR_REV7_SOURCE_IDENTITY.json').read_text())['configuration']
    assert {k:v for k,v in CONFIG.items() if k not in ('revision','strong_links','B_path')}=={
        k:v for k,v in previous.items() if k not in ('revision','strong_links')}
    current_previous=json.loads((HERE/'rev710_delivery/PRIOR_REV7_SOURCE_IDENTITY.json').read_text())['configuration']
    assert {k:v for k,v in CONFIG.items() if k not in ('revision','B_path')}=={
        k:v for k,v in current_previous.items() if k!='revision'}
    assert not CONFIG['B_path']['service_guarantee'] and CONFIG['B_path']['maximum_births_per_check']==2


def test_rev79_qualification_keeps_coherent_weak_link_cohort_synthetic():
    with medium() as m:
        ids=[m.add(point,0.) for point in ((0.,0.),(2.2,0.),(1.1,2.2*math.sqrt(3)/2))]
        assert all(not row for row in m.strong_influence().incoming.values())
        assert all(len(row)==2 for row in m.influence().incoming.values())
        m.step_index=600;m.frames.clear()
        for k in range(601):
            m.frames.append(Frame(k,k*.1,
                {e.id:(e.x,e.y,math.pi*k*.1) for e in m.native.elements},{},
                {id:tuple(other for other in ids if other!=id) for id in ids},
                {id:0. for id in ids},{}))
        result=q.start(m)
        assert result['cohort']==ids and len(result['candidates'])==1
        assert result['candidates'][0]['ids']==ids


@pytest.mark.parametrize('rule,timer',[('D1',40.),('D4',120.)])
def test_rev76_death_rules_preserve_output_and_remove_ordinary(rule,timer,monkeypatch):
    with medium() as m:
        out=m.add((0.,0.),0.,role='output');ordinary=m.add((1.,0.),0.)
        m.step_index=2000
        monkeypatch.setattr(m,'lock',lambda id:0.)
        if rule=='D1':m.death={out:timer,ordinary:timer}
        else:
            m.native.cut_off(out,timer);m.native.cut_off(ordinary,timer)
        m.growth(b1=False)
        assert {e.id for e in m.native.elements}=={out}
        assert [(e['rule'],e['ids']) for e in m.events if e['rule'] in ('D1','D3','D4')]==[(rule,[ordinary])]
        assert m.native.pin(out)==(True,(0.,0.))


def test_rev76_D3_preserves_lowest_lock_output_and_prunes_ordinary(monkeypatch):
    with medium() as m:
        out=m.add((0.,0.),0.,role='output')
        ordinary=[m.add((1.+.06*j,1.),0.) for j in range(64)]
        m.step_index=2000
        monkeypatch.setattr(m,'lock',lambda id:0. if id==out else 1.)
        assert m.cost()>64
        m.growth(b1=False)
        deaths=[e for e in m.events if e['rule']=='D3']
        assert deaths and all(e['ids'][0] in ordinary for e in deaths)
        assert out in {e.id for e in m.native.elements} and m.cost()<=64
        assert not any(e['rule']=='B-out' for e in m.events)


def test_rev76_cost_excludes_O_incident_pairs_but_retains_actual_topology():
    with medium(params=Params(k=1)) as m:
        out=m.add((0.,0.),0.,role='output')
        a=m.add((-.5,0.),0.);b=m.add((.5,0.),0.)
        assert m.phase_topology()[a]==[out] and m.phase_topology()[b]==[out]
        assert m.native.cost(1.,.1)==dict(elements=2,active_couplings=0,total=2.)
        m.remove(out,'SYNTHETIC')
        assert m.phase_topology()=={a:[b],b:[a]}
        assert m.native.cost(1.,.1)==dict(elements=2,active_couplings=1,total=2.1)


def test_rev76_admission_and_live_cost_share_ordinary_cap_and_pairs():
    with medium() as m:
        m.add((0.,0.),0.,role='output')
        for j in range(63):m.add((10.+4*j,10.),0.)
        assert m.cost()==63.
        assert m.feasible((.6,0.),0.) is None # incident O pair costs zero
        m.add((.6,0.),0.)
        assert len(m.native)==65 and m.cost()==64.
        assert m.feasible((400.,10.),0.)=='cap'
    with medium() as m:
        m.add((0.,0.),0.,role='output')
        for j in range(63):m.add((1.+.06*j,1.),0.)
        assert m.feasible((2.,2.),0.)=='cost' # ordinary pairs still charged


@pytest.mark.parametrize('over_budget',[False,True])
def test_rev76_Bout_succeeds_with_full_cap_and_protected_budget(over_budget):
    with medium() as m:
        for j in range(64):m.add((1.+.06*j,1.) if over_budget else (10.+4*j,10.),0.)
        assert m.cost()>64 if over_budget else m.cost()==64
        m.growth(b1=False) # ordinary elements too young for D3; blocked when over budget
        outputs=m.influence().outputs
        assert len(outputs)==1 and len(m.native)==65
        terminals=[e['values']['outcome'] for e in m.events if e['rule']=='birth_terminal' and e['values']['birth_rule']=='B-out']
        assert terminals==['accepted']
        assert bool([e for e in m.events if e['rule']=='protected_over_budget'])==over_budget
        before=len(m.events);assert m.b_out(blocked=True)==[] and len(m.events)==before


def test_rev76_Bout_placement_still_required_when_budget_blocked():
    with medium() as m:
        m.add((.01,0.),0.)
        assert m.b_out(blocked=True)==[] and not m.influence().outputs
        assert m.events[-1]['values']['outcome']=='placement'


def test_rev76_isolated_immortal_output_has_no_drive_root_coverage_or_path(monkeypatch):
    with medium() as m:
        out=m.add((0.,0.),.7,role='output')
        m.drives=[drive(x=.5,y=0.)];m.native.set_drives(m.drives)
        m.step_index=2000;m.death[out]=1000.;m.native.cut_off(out,1000.)
        monkeypatch.setattr(m,'lock',lambda id:0.)
        m.growth(b1=False)
        assert m.influence().outputs=={out} and not any(m.influence().roots.values())
        assert not any(m.influence().path(s) for s in range(8))
        assert not m.covered(0) and m.gain_signal(out) is None
        assert m.native.rhs()[0][2]==math.pi and m.cost()==0.
        # Existence alone cannot satisfy F5's unchanged E >= .5 gate.


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
    value=dict(revision=CONFIG['revision'],identity_snapshot=dict(pin_sha256='pin'),results={name:dict(verdict='DESCRIPTIVE' if name in ('F6','F8','F9') else 'PASS') for name in ('N1','F1','F2','F3','F4','F5','F6','F7','F8','F9')},not_run=[],stops=[])
    path.write_text(json.dumps(value));assert validate_fixture_receipt(path,'pin')['sha256']
    with pytest.raises(PermissionError,match='mismatch'):validate_fixture_receipt(path,'stale-pin')
    stale=deepcopy(value);stale['revision']='7.4';path.write_text(json.dumps(stale))
    with pytest.raises(PermissionError,match='mismatch'):validate_fixture_receipt(path,'pin')
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


def test_rev75_configuration_identity_and_N1f_literal_recipe():
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_config import F1D_SCALES
    assert CONFIG['revision']=='7.10' and CONFIG['phase_scale']==32.
    assert CONFIG['output_port']['death_exempt']==['D1','D3','D4']
    assert CONFIG['output_port']['B_out_budget_exempt']
    assert CONFIG['fixture_entropy']['development']=='unchanged'
    assert CONFIG['excursion']['h']==.005 and CONFIG['excursion']['substeps']==20
    assert CONFIG['N1']['h']==[.005,.00125] and CONFIG['N1']['substeps']==[20,80]
    assert F1D_SCALES==(1.,8.,32.) and CONFIG['F1']['F1d']['h']==.005
    assert set(N1_RECIPES)=={'N1a','N1b','N1c','N1d','N1e','N1f','N1g'}
    m=scaffold('F1c')
    try:
        assert N1_RECIPES['N1f']['members']==[[e.x,e.y,e.phase,e.rate,m.native.gain(e.id),m.role(e.id)] for e in m.native.elements]
    finally:m.close()
    assert N1_RECIPES['N1f']['seconds']==24. and N1_RECIPES['N1f']['entry_member']==6
    for key,value in [('phase_scale',8.),('excursion',dict(CONFIG['excursion'],h=.02))]:
        altered=deepcopy(CONFIG);altered[key]=value
        assert hashlib.sha256(p.canonical(altered)).hexdigest()!=CONFIG_SHA256
    with pytest.raises(ValueError,match='solver'):Rev7Medium(h=.02)


def test_rev75_offset_and_saddle_preserve_old_recipes_and_inside_cutoff():
    previous=json.loads((HERE/'rev74_integration_history/REV7_SOURCE_IDENTITY.json').read_text())['configuration']['N1']['recipes']
    for name,recipe in N1_RECIPES.items():
        prior=deepcopy(previous['N1d' if name=='N1g' else name])
        if name=='N1d':prior['members'][0][2]=math.pi-.5
        assert {k:v for k,v in recipe.items() if k!='used_in_verdict'}==prior
        assert recipe['used_in_verdict'] is (name!='N1g')
    d,g=N1_RECIPES['N1d'],N1_RECIPES['N1g']
    assert d['members'][0][2]==math.pi-.5 and g['members'][0][2]==math.pi
    assert abs(d['sites'][0][0]-d['members'][0][0])==pytest.approx(.3,rel=0,abs=1e-15)
    assert abs(d['sites'][0][0]-d['members'][1][0])<CONFIG['site_body_r0']
    changed=deepcopy(CONFIG);changed['N1']['saddle_diagnostic']['departure_radians']=.25
    assert hashlib.sha256(p.canonical(changed)).hexdigest()!=CONFIG_SHA256
    changed=deepcopy(CONFIG);changed['N1']['recipes']['N1g']['used_in_verdict']=True
    assert hashlib.sha256(p.canonical(changed)).hexdigest()!=CONFIG_SHA256


def synthetic_saddle_records():
    """Fabricated endpoints; neither a solver nor Harness.N1 is called."""
    return [dict(time=(j+1)*.1,phases=[math.pi,0.],positions=[[3.7,0.],[3.956,0.]],
        free=[True,True],phase_topology={0:[1],1:[0]},motion_topology={0:[1],1:[0]},
        pin_invariant=True,excursion={0:0.,1:0.}) for j in range(160)]


@pytest.mark.parametrize('direction',[-1,1])
@pytest.mark.parametrize('first',[0,4])
def test_N1g_slip_direction_time_and_unwrapped_winding_synthetic(direction,first):
    rows=synthetic_saddle_records()
    for r in rows[first:]:r['phases'][0]=math.pi+direction*.5
    rows[-1]['phases'][0]=math.pi+direction*2*math.pi
    result=n1_case_result('N1g',rows,deepcopy(rows))
    assert result['verdict']=='DESCRIPTIVE' and result['used_in_verdict'] is False
    assert result['interpretation']=='SENSITIVITY_NOT_ACCURACY'
    for h,slip in zip((.005,.00125),result['slip']):
        assert slip['h']==h and slip['status']=='OBSERVED' and slip['direction']==direction
        assert slip['time_seconds']==rows[first]['time']
        assert slip['time_bracket_seconds']==[0. if first==0 else rows[first-1]['time'],rows[first]['time']]
        assert slip['final_unwrapped_displacement']==pytest.approx(direction*2*math.pi,rel=0,abs=1e-14)
        assert slip['horizon_seconds']==16. and slip['used_in_verdict'] is False


def test_N1g_censored_branch_and_accuracy_gate_exclusion_synthetic():
    a,b=synthetic_saddle_records(),synthetic_saddle_records()
    for r in a:r['phases'][0]=math.pi-.4 # below the declared diagnostic cut
    quiet=n1_case_result('N1g',a,b)
    for slip in quiet['slip']:
        assert slip['status']=='NOT_OBSERVED' and slip['direction'] is None
        assert slip['time_seconds'] is None and slip['time_bracket_seconds'] is None
    for rows,phase in ((a,0.),(b,2*math.pi)):
        for r in rows:r['phases'][0]=phase
    b[0]['positions'][0][0]+=1.
    b[0]['phase_topology']={0:[],1:[]};b[0]['pin_invariant']=False
    diagnostic=n1_case_result('N1g',a,b)
    assert diagnostic['verdict']=='DESCRIPTIVE' and diagnostic['maximum_unwrapped_phase']==pytest.approx(2*math.pi)
    assert diagnostic['maximum_free_position']==1. and not diagnostic['pins_invariant']
    assert [s['direction'] for s in diagnostic['slip']]==[-1,1]
    cases={name:dict(verdict='PASS',used_in_verdict=True) for name in N1_RECIPES if name!='N1g'}
    cases['N1g']=diagnostic
    assert n1_verdict(cases)=='PASS'
    cases['N1d']=n1_case_result('N1d',a,b)
    assert cases['N1d']['verdict']=='FAIL' and n1_verdict(cases)=='FAIL'
    del cases['N1g']
    with pytest.raises(ValueError,match='incomplete'):n1_verdict(cases)


def test_N1g_descriptive_still_rejects_invalid_measurements_and_policy_synthetic():
    rows=synthetic_saddle_records();bad=deepcopy(rows);bad[0]['phases'][0]=float('nan')
    with pytest.raises(ValueError,match='nonfinite'):n1_case_result('N1g',rows,bad)
    with pytest.raises(ValueError,match='unmatched'):n1_case_result('N1g',rows,rows[:-1])
    for invalid in (float('nan'),float('inf')):
        bad=deepcopy(rows);bad[0]['time']=invalid
        with pytest.raises(ValueError,match='unmatched'):n1_case_result('N1g',rows,bad)
    bad=deepcopy(rows);del bad[0]['excursion'][1]
    with pytest.raises(ValueError,match='INVALID'):n1_case_result('N1g',rows,bad)
    cases={name:dict(verdict='PASS',used_in_verdict=True) for name in N1_RECIPES}
    with pytest.raises(ValueError,match='policy'):n1_verdict(cases)


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
