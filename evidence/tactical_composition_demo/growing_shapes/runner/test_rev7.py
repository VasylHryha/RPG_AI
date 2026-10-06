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
        m.native.phase_scale(8);eight=np.array(m.native.rhs())
        np.testing.assert_array_equal(one[:,:2],eight[:,:2])
        np.testing.assert_allclose(eight[:,2]-[2.8,3.3],8*(one[:,2]-[2.8,3.3]),atol=2e-15)
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
        m.native.step(.02)
        assert all(stage[1][:2]==[0.,0.] for stage in m.native.stage_terms())
        assert m.native.pin(out)==(True,(2.7,.1))
        with pytest.raises(ValueError,match='pinned'):m.native.set_element(out,0,0,0,math.pi)
        m.native.comparator('site_body_off');m.native.comparator('fixed_structure')
        loaded=Rev7Native.load(m.native.save());clone=m.native.clone()
        try:
            assert loaded.save()==m.native.save()==clone.save()
            assert loaded.policy()==(8.,True,False)
            assert loaded.excursion()==m.native.excursion()
        finally:loaded.close();clone.close()


@pytest.mark.parametrize('scale',[1.,8.])
@pytest.mark.parametrize('mode',[None,'site_body_off','k_zero','fixed_structure'])
def test_native_independent_python_step_parity(scale,mode):
    with medium() as native:
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


def test_frame_bound_sums_stages_and_recorded_endpoints():
    with medium() as m:
        m.add((3.4,.1),1.,gain=2.)
        m.integrate([drive(phase=-1.,strength=4)])
        with medium(frozen=True) as manual:
            manual.add((3.4,.1),1.,gain=2.);manual.native.set_drives([drive(phase=-1.,strength=4)])
            expected=0.
            for j in range(5):
                manual.native.step(.02);expected+=.02*max(abs(math.pi+stage[0][0]+stage[0][1]-math.pi) for stage in manual.native.stage_terms())
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
    for row in ordered:row['phase_topology']={0:[1,2]}
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


def test_preservation_baseline():
    root=HERE.parents[3];old=json.loads((HERE/'REV7_LEGACY_BASELINE.json').read_text())
    for name,expected in old['sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,name


def test_development_fixture_receipt_requires_all_gates_and_current_pin(tmp_path):
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_execution import validate_fixture_receipt
    with pytest.raises(PermissionError,match='required'):validate_fixture_receipt('', 'pin')
    path=tmp_path/'synthetic_fixture.json'
    value=dict(revision='7.3',identity_snapshot=dict(pin_sha256='pin'),results={name:dict(verdict='DESCRIPTIVE' if name in ('F6','F8','F9') else 'PASS') for name in ('N1','F1','F2','F3','F4','F5','F6','F7','F8','F9')},not_run=[],stops=[])
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
        assert ledger['lambda_value']==8. and ledger['ratio_units']=='dimensionless'
        assert ledger['estimator_seconds']==10. and ledger['qualification_seconds']==60.
        assert ledger['geometric_length_reference']==pytest.approx(1/1.8)
        element=next(r for r in ledger['rows'] if r['kind']=='element')
        assert element['scaled_coefficient']==pytest.approx(8*math.exp(-.25))
        assert element['against_carrier']==pytest.approx(element['scaled_coefficient']/math.pi)
        assert element['against_geometric_reference']==pytest.approx(element['scaled_coefficient']/1.8)
        assert INTERPRETATION['revision_7_motion']['status']=='DESCRIPTIVE'
