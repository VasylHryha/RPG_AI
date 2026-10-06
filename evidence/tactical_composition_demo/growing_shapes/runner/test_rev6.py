"""Tiny synthetic contracts only. No fixture execution, world episode or panel."""
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import pytest
from evidence.tactical_composition_demo.growing_shapes.medium.medium import Medium, Params, Drive
from evidence.tactical_composition_demo.growing_shapes.medium.rev6_native import Rev6Native
from evidence.tactical_composition_demo.growing_shapes.medium.rev6_design import Rev6Medium, ROLE_BY_MEASUREMENT, TRIAL_NAMES
from evidence.tactical_composition_demo.growing_shapes.medium.design_0h import Frame
from evidence.tactical_composition_demo.growing_shapes.runner import rev6_native as bridge
from evidence.tactical_composition_demo.growing_shapes.runner.rev6_protocol import seed,generator,recovery_generator,donor_entries,training_episode,template,template_hash,copy_template,decode,relay,replay_on_clock,paired_bounds,student_cdf,t_quantile,late_count,aggregate,stops,STOP_ROWS
from evidence.tactical_composition_demo.growing_shapes.runner.protocol import template as old_template,template_hash as old_hash
from evidence.tactical_composition_demo.growing_shapes.runner.rev6_control import Matched,Queue
from evidence.tactical_composition_demo.growing_shapes.runner.rev6_execution import Execution
from evidence.tactical_composition_demo.growing_shapes.runner.rev6_fixtures import construct_only,memory_summary
from evidence.tactical_composition_demo.growing_shapes.runner.rev6_evaluator import reused_calibration,Evaluator
from evidence.tactical_composition_demo.growing_shapes.runner.rev6_run import Run

HERE=Path(__file__).parent

@contextmanager
def medium():
    m=Rev6Medium(growth_rng=np.random.Generator(np.random.PCG64(17001)))
    try:yield m
    finally:m.close()


def drive(site=0,x=4,y=0,phase=1.,strength=2):return Drive(site,x,y,phase,math.pi,strength,1,3)


def test_seed_inventory_and_F8_keys():
    inventory=json.loads((HERE/'REV6_SEED_INVENTORY.json').read_text())
    assert len(inventory['seed_inventory'])==2842
    for key,value in inventory['seed_inventory'].items():assert value==seed(key)
    assert set(inventory['F8_consumer_keys'])=={'growth/F8/reward','recovery/F8/reward'}
    assert inventory['evaluation_result_exists'] is False
    assert inventory['fixture_execution']==inventory['development_execution']=='NOT_RUN'
    assert inventory['F6_donor_pairs']==[dict(recipient=788+j,donor=798+j) for j in range(10)]
    assert donor_entries()==inventory['donor_permutation']
    entries=donor_entries();assert {r['donor'] for r in entries}==set(range(640,768))
    assert training_episode('task_blind',7,1999)==1071999
    assert training_episode('reward',7,1999)==1151999


def test_persistent_PCG64_and_recovery_byte_order():
    a=generator('synthetic/test');b=generator('synthetic/test')
    assert np.array_equal(a.uniform(size=3),b.uniform(size=3))
    first=a.uniform(size=3);assert not np.array_equal(first,generator('synthetic/test').uniform(size=3))
    master=seed('recovery/synthetic/test');index=1234
    expected=int.from_bytes(hashlib.sha256(f'{master}:kick:{index}'.encode()).digest()[:8],'little')
    assert np.array_equal(recovery_generator(master,index).uniform(size=4),np.random.default_rng(expected).uniform(size=4))


def test_C4_parity_inside_wall_without_roles():
    with medium() as m,Medium(params=Params(window=101,min_samples=100)) as old:
        for x,y,theta,rate in [(0,0,.3,math.pi),(.7,.2,1.,2.8),(-.4,.1,-.2,3.3)]:
            a=m.add((x,y),theta,rate,.8);b=old.add(x,y,theta,rate);old.set_gain(b,.8)
        ds=[drive(x=1,y=0)];m.native.set_drives(ds);old.set_drives(ds)
        np.testing.assert_array_equal(m.native.rhs(),old.rhs())
        m.native.step(.02);old.step(.02)
        np.testing.assert_array_equal([[e.x,e.y,e.phase] for e in m.native.elements],[[e.x,e.y,e.phase] for e in old.elements])


def test_mask_and_lesion_at_all_four_RK_stages():
    with medium() as m:
        source=m.add((4,0),1.,gain=1.)
        output=m.add((4.1,0),0.,role='output')
        m.native.lesions([output]);m.native.set_drives([drive(phase=1.7)])
        for _ in range(5):
            m.native.step(.02);terms=m.native.stage_terms()
            assert len(terms)==4
            assert all(stage[1][0].hex()==0.0.hex() and stage[1][1].hex()==0.0.hex() for stage in terms)
            assert any(stage[0][0]!=0 for stage in terms)
        assert m.native.elements[1].phase==pytest.approx(math.pi*.1,abs=1e-15)
        assert m.role(source)=='element'


def test_soft_wall_units_origin_and_outside():
    with medium() as m:
        m.add((0,0),0);m.add((7,0),0)
        rhs=m.native.rhs()
        assert rhs[0][:2]==[0.,0.]
        assert rhs[1][:2]==[-1.,0.]
        m.native.step(.02)
        assert 6<m.native.elements[1].x<7  # A soft restoring velocity, not clipping.


def test_roles_clone_save_reindex_shift_and_hash():
    with medium() as m:
        ordinary=m.add((.2,.1),.7,3.,.6)
        output=m.add((1.1,.1),.9,3.1,.8,role='output')
        m.native.cut_off(ordinary,12.3);m.native.lesions([output])
        value=template(m.native,[output,ordinary],0)
        altered=deepcopy(value);altered['members'][1][5]='element'
        assert template_hash(value)!=template_hash(altered)
        branch=m.clone();loaded=Rev6Native.load(m.native.save())
        shifted=copy_template(value,math.pi)
        try:
            assert branch.native.save()==m.native.save()==loaded.save()
            assert loaded.role(output)=='output' and loaded.cut_off(ordinary)==12.3
            assert shifted.role(1)=='output'
            np.testing.assert_allclose([e.phase for e in shifted.native.elements],[.7+math.pi,.9+math.pi])
            roundtrip=template(shifted.native,[1,0],shifted.time)
            for expected,actual in zip(value['members'],roundtrip['members']):
                np.testing.assert_allclose(expected[:5],actual[:5],atol=1e-15);assert expected[5]==actual[5]
            assert value['template_version']=='rev6_template_v1'
        finally:branch.close();loaded.close();shifted.close()


def test_singleton_cap_and_legacy_load_identity():
    with medium() as m:
        m.add((0,0),0.,role='output')
        with pytest.raises(ValueError,match='singleton'):m.add((1,0),0.,role='output')
    with Medium() as native:
        id=native.add(0,0,.2,math.pi);native.set_gain(id,.5)
        value=old_template(native,[id],0);digest=old_hash(value)
        copy=copy_template(value)
        try:
            assert old_template(copy.native,[0],0)==value
            assert old_hash(value)==digest
            assert not isinstance(copy,Rev6Medium)
        finally:copy.close()


def test_role_measurement_histories_and_coverage():
    with medium() as m:
        ordinary=m.add((4,0),0.,gain=1.)
        output=m.add((4.2,0),0.,role='output')
        m.frames.clear()
        for k in range(101):
            m.frames.append(Frame(k,k*.1,{ordinary:(4,0,math.pi*k*.1),output:(4.2,0,math.pi*k*.1)}, {0:(4,0,math.pi*k*.1,2)}, {ordinary:(output,),output:(ordinary,)}))
        assert m.gain_signal(output) is None
        assert m.offsets(output,0,True) is None
        assert m.lock(output)==1.
        assert m.covered(0)
        assert m.gain_signal(ordinary)==1.
        m.remove(ordinary,'SYNTHETIC')
        assert not m.covered(0)
        assert ROLE_BY_MEASUREMENT['output']['e_i']==0
        # No C4 partner -> output lock 0 even if geometrically exposed to a site.
        for k in range(101):m.frames[k]=Frame(k,k*.1,{output:(4,0,0)},{0:(4,0,0,2)},{output:()})
        assert m.lock(output)==0.


def test_fresh_graph_roots_gain_and_D4_OR():
    with medium() as m:
        root=m.add((0,0),0.,gain=1.)
        frontier=m.add((2.9,0),0.,gain=0.)
        output=m.add((6,0),0.,role='output')
        isolated=m.add((10,0),0.)
        m.drives=[drive(x=0)];g=m.influence()
        assert g.roots[0]=={root}
        assert g.forward()=={root,frontier} and g.backward()=={output}
        m.frames.clear();m.record();m.timers()
        assert m.native.cut_off(root)==m.native.cut_off(frontier)==m.native.cut_off(output)==0.
        assert m.native.cut_off(isolated)==.1
        m.drives=[drive(x=0,strength=0)];m.frames.clear();m.record();m.timers()
        assert m.native.cut_off(root)==.1 and m.native.cut_off(output)==0
        m.native.set_element(output,5.8,0,0,math.pi)
        assert output in m.influence().outgoing[frontier]  # endpoint change, not old frame.
        m.native.set_gain(root,0);m.drives=[drive(x=0)]
        assert not m.influence().roots[0]


def test_strict_cutoffs():
    with medium() as m:
        a=m.add((0,0),0);b=m.add((3,0),0);o=m.add((0,1),0,role='output')
        m.drives=[drive(x=0)];g=m.influence()
        assert b not in g.roots[0] and b not in g.incoming[a]
        assert o not in g.roots[0]


def test_R3_2_saturated_receiver_candidate_REJECT_and_complete_restore():
    with medium() as m:
        u=m.add((-2.9,0),0,gain=1.)
        a=m.add((0,0),0,gain=0.)
        b=m.add((3.1,0),0,gain=0.,role='output')
        for j in range(7):m.add((1+.0001*j,2.72+.0001*j),0,gain=0.)
        for j in range(9):m.add((1+.001*j,2.85+.001*j),0,gain=0.)
        m.drives=[drive(x=-4)];before=m.native.save();rng=deepcopy(m.growth_rng.bit_generator.state)
        state=deepcopy((m.death,m.birth_steps,m.novelty,m.pointer,m.request_counter,list(m.frames),m.events))
        assert m.influence().forward(0)=={u,a}
        assert not m.influence().path(0)
        checks=m.trial(0,a,b,(.556,0))
        assert checks['edge_a_to_new'] and checks['paths_kept'] and checks['deficit_or_connect'] and checks['clearance']
        assert not checks['new_reached'] and not checks['a_reached']
        assert not all(checks.values())  # Mandatory REJECT c=(0.556,0).
        assert m.native.save()==before and m.growth_rng.bit_generator.state==rng
        assert (m.death,m.birth_steps,m.novelty,m.pointer,m.request_counter,list(m.frames),m.events)==state
        assert tuple(checks)==TRIAL_NAMES


def test_post_trial_birth_acceptance_and_full_order_quota():
    with medium() as m:
        for s in range(8):
            angle=s*math.pi/4;m.add((4*math.cos(angle),4*math.sin(angle)),0)
        m.drives=[drive(s,4*math.cos(s*math.pi/4),4*math.sin(s*math.pi/4)) for s in range(8)]
        m.frames.clear();m.record();m.novelty={s:20. for s in range(8)}
        event_start=len(m.events)
        added=m.growth()
        births=[e['rule'] for e in m.events[event_start:] if e['rule'] in ('B-out','B-path','B1')]
        assert births==['B-out','B-path','B-path','B1','B1']
        assert len(added)==2 and len(m.influence().outputs)==1
        terminals=[e['values'] for e in m.events if e['rule']=='birth_terminal']
        assert len({r['request'] for r in terminals})==len(terminals)
        assert any(r['outcome']=='quota' for r in terminals)
        assert all(r['attempts']<=104 for r in terminals if r['birth_rule']=='B-path')
        assert m.pointer==1
        assert all(m.native.gain(r['ids'][0])==1 for r in m.events if r['rule'] in ('B-out','B-path','B1'))


def fill_cap(m):
    for j in range(64):m.add((100+10*j,100),0)


def test_cap_cost_placement_schema_and_protection():
    with medium() as m:
        fill_cap(m);m.growth()
        out=[e['values'] for e in m.events if e['rule']=='birth_terminal' and e['values']['birth_rule']=='B-out']
        assert out[0]['outcome']=='cap'
    with medium() as m:
        for j in range(50):m.add((.06*(j%10),.06*(j//10)),0)
        assert m.cost()>64
        m.growth()
        assert any(e['rule']=='protected_over_budget' for e in m.events)
        out=[e['values'] for e in m.events if e['rule']=='birth_terminal' and e['values']['birth_rule']=='B-out']
        assert out[0]['outcome']=='cost' and len(m.native)==50


def test_D1_D4_D3_death_priority_and_protection():
    with medium() as m:
        a=m.add((0,0),0);b=m.add((8,0),0);protected=m.add((20,0),0)
        m.step_index=200;m.birth_steps[protected]=1
        m.death[a]=40;m.native.cut_off(a,120);m.native.cut_off(b,120);m.native.cut_off(protected,120)
        m.growth()
        deaths=[(e['rule'],e['ids']) for e in m.events if e['rule'] in ('D1','D4')]
        assert deaths==[('D1',[a]),('D4',[b])]
        assert protected in [e.id for e in m.native.elements]


def test_native_reference_live_endpoint_parity():
    with medium() as reference:
        reference.add((3.2,0),.2,3.,.5);reference.add((2.6,0),-.2,3.1,1.,role='output')
        native=reference.clone();lib=bridge.library()
        try:
            for _ in range(3):
                ds=[drive(phase=math.pi*reference.time+1.)]
                reference.integrate(ds);signals=reference.adapt();covered=reference.timers()
                row=bridge.contract(native,ds,lib=lib)['steps'][0]
                np.testing.assert_array_equal([[e.x,e.y,e.phase,e.rate] for e in reference.native.elements],[[e.x,e.y,e.phase,e.rate] for e in native.native.elements])
                assert row['event']['values']['defined_signals']==signals
                assert row['covered']==covered and row['paths']==reference.endpoint_diagnostics()['paths']
                assert reference.frames==native.frames
                assert reference.death==native.death and reference.novelty==native.novelty
                assert reference.native.save()==native.native.save()
        finally:native.close()


def test_native_recovery_frozen_future_uses_roles_wall_and_same_RHS():
    with medium() as reference:
        reference.add((6.3,0),.2);reference.add((6.8,0),-.4,role='output')
        native=reference.clone();reference.frozen=True
        schedule=[[drive(x=6.3,phase=1+j*.1*math.pi)] for j in range(3)]
        try:
            expected=[];frames=len(reference.frames)
            for ds in schedule:
                reference.integrate(ds);expected.append([[e.x,e.y,e.phase] for e in reference.native.elements])
            trajectory=bridge.future(native,schedule)
            np.testing.assert_array_equal(trajectory,expected)
            assert len(reference.frames)==frames
            assert native.native.role(1)=='output'
        finally:native.close()


def test_singleton_decode_relay_and_relative_donor_clock():
    with medium() as m:
        assert decode('perceive',None,*m.native.output(),0).angle==0
        m.add((100,100),1.,role='output')
        assert decode('perceive',None,*m.native.output(),0).magnitude==0
        assert decode('move',None,*m.native.output(),0).magnitude==1
        assert decode('remember_static',None,*m.native.output(),0).angle==1.
    ds=[drive(site=0,phase=.3),drive(site=2,phase=1.1,strength=3.)]
    assert relay('perceive',None,ds,0,'site0').angle==pytest.approx(.3)
    assert relay('perceive',None,ds,0,'oracle').angle==pytest.approx(1.1)
    ds[0].strength=0
    assert relay('perceive',None,ds,0,'site0').angle==0
    replay=replay_on_clock([[2,4,0,.8,math.pi,1,1,3]],10.)
    assert replay[0].phase==math.pi*10+.8 and replay[0].id==2


def test_M_exact_matching_and_unmatched_not_repaired():
    with medium() as m:
        q=Matched('matched/synthetic/test');m.step_index=200
        added=q.check(m,[99,100]);assert len(added)==2
        assert not q.unmatched and {r['check'] for r in q.slots}=={200}
        assert all(e['rule']!='B-path' for e in m.events)
        for j in range(62):m.add((100+10*j,100),0)
        m.step_index=400;q.check(m,[101]);assert len(q.unmatched)==1
        q.terminal(m);assert q.unmatched[0]['source_id']==101
        assert q.unmatched[0]['outcome']=='cap'


def test_U_FIFO_retry_later_terminal_drop():
    with medium() as m:
        fill_cap(m);q=Queue('control_u/synthetic/test');m.step_index=200
        q.check(m,[99]);assert q.queue[0]['attempts']==1 and q.drops==0
        q.check(m,[]);assert q.queue[0]['attempts']==1  # Same check never retries.
        m.step_index=400;q.check(m,[]);assert q.drops==1 and q.retries==1
        m.step_index=600;q.check(m,[100,101]);q.terminal(m);assert q.drops==3


def test_paired_t_numeric_constant_nonfinite_secondary():
    assert 1.656<t_quantile(.95)<1.658
    # Independent Simpson integration of t density checks the CDF/quantile.
    t=t_quantile(1-.05/3);n=2000;x=np.linspace(0,t,n+1)
    coefficient=math.exp(math.lgamma(64)-math.lgamma(63.5))/math.sqrt(127*math.pi)
    y=coefficient*(1+x*x/127)**(-64)
    integral=t/n/3*(y[0]+y[-1]+4*y[1:-1:2].sum()+2*y[2:-1:2].sum())
    assert .5+integral==pytest.approx(1-.05/3,abs=2e-12)
    assert student_cdf(-t)==pytest.approx(.05/3,abs=1e-13)
    zero=np.zeros(128)
    for delta in (1.,0.,-1.):
        row=paired_bounds(zero+delta,zero)
        assert row['constant'] and row['positive']==(delta>0) and row['negative']==(delta<0)
    values=np.linspace(-.2,.4,128);p=paired_bounds(values,zero);s=paired_bounds(values,zero,secondary=True)
    assert s['lower']<p['lower'] and s['upper']>p['upper']
    assert paired_bounds([math.nan]*128,zero)['verdict']=='INVALID'
    assert paired_bounds([0]*127,zero)['verdict']=='INVALID'


def test_inclusive_late_window_terminal_taxonomy():
    event=lambda t,rule,outcome=None:dict(time=t,rule=rule,values={} if outcome is None else dict(outcome=outcome,attempts=104))
    counts=[(25580,100),(25600,30),(32000,30)]
    events=[event(25599,'birth_terminal','exhausted'),event(25600,'birth_terminal','cost'),event(25601,'birth_attempt')]
    result=late_count(counts,events)
    assert result['settled'] and result['slope']==0 and result['terminal_requests']==1
    events.append(event(25600,'birth_terminal','exhausted'))
    assert not late_count(counts,events)['settled']
    assert late_count([(25600,30),(32000,32)],[])['slope']==.5


def passing_unit():
    bound=paired_bounds(np.ones(128),np.zeros(128))
    return dict(complete=True,invalid=None,perceive_usable=True,eligible=1,control_eligible=1,coverage=.8,control_coverage=.7,matched=True,g0=bound,bounds={'perceive':{c:bound for c in ('default','random','donor','output_channel')}},late=dict(invalid=None,settled=True),snapshots=1,g5=[0.])


def test_G0_G0prime_G2_cuts_INVALID_and_unmatched():
    units=[passing_unit() for _ in range(8)]
    assert aggregate(units)==dict(G0='PASS',**{"G0'":'PASS'},G2='PASS',G1='PASS',G1c='DESCRIPTIVE',G5='PASS')
    for s in units[:3]:s['matched']=False
    assert aggregate(units)['G0']=='INCONCLUSIVE'
    for s in units[:6]:s['bounds']['perceive']['donor']=paired_bounds(np.zeros(128),np.zeros(128))
    assert aggregate(units)['G2']=='FAIL'
    for s in units[:3]:s['late']['settled']=False
    assert aggregate(units)["G0'"]=='FAIL'
    units[0]['bounds']['perceive']['random']=dict(verdict='INVALID')
    assert aggregate(units)['G2']=='INVALID'
    units[0]['complete']=False
    assert set(aggregate(units).values())=={'INVALID'}


def test_F6_descriptive_degenerate_means_and_correlation():
    row=lambda angles:dict(decisions=[dict(angle=0,has_output=True)]*40+[dict(angle=a,has_output=True) for a in angles])
    degenerate=[row(np.linspace(0,2*math.pi,120,endpoint=False)) for _ in range(6)]
    result=memory_summary([.1]*6,degenerate)
    assert result['correlation'] is None and result['defined_pairs']==0
    assert all(r['reason']=='degenerate_resultant' for r in result['episodes'])
    angles=[-1,-.5,0,.5,1]
    assert memory_summary(angles,[row([a]*120) for a in angles])['correlation']==pytest.approx(1.)


def test_no_execution_grant_and_all_stop_rows():
    with pytest.raises(PermissionError):Execution().require('fixtures')
    with pytest.raises(PermissionError):Execution().require('development')
    for flag,action,role in STOP_ROWS:
        assert stops({flag:True})==[dict(question=flag,action=action,role=role)]
    rows,_=reused_calibration();evaluator=Evaluator(rows)
    with pytest.raises(PermissionError):evaluator.capture('perceive',640)
    run=Run(0,rows,episodes=1)
    try:
        with pytest.raises(PermissionError):run.episode(0)
        assert run.medium.step_index==0
    finally:run.close()


def test_construct_only_dry_check_never_integrates(monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError('construct-only may not integrate')
    monkeypatch.setattr(Rev6Medium,'integrate',forbidden)
    monkeypatch.setattr(Rev6Native,'step',forbidden)
    result=construct_only()
    assert result['integrated_world_steps']==0 and result['fixture_execution']=='NOT_RUN'
    assert len(result['recipes']['F1c']['members'])==10
    assert result['recipes']['F1c']['members'][-1][0]==pytest.approx(-1.804)
    assert result['recipes']['F5i']['members']==result['recipes']['F7']['members']
    assert len(result['recipes']['F5ii']['members'])==7
    assert result['recipes']['F8']['episodes']==tuple(range(2100000,2100040))
    (HERE/'REV6_CONSTRUCT_ONLY.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')


def test_all_preexisting_tracked_growing_shapes_bytes_preserved():
    hashes=json.loads((HERE/'REV6_BASELINE_IDENTITY.json').read_text())
    assert all(hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected for path,expected in hashes.items())


def test_reward_output_eligibility_and_running_baseline_contract():
    from collections import defaultdict
    rows,_=reused_calibration();run=Run(0,rows,reward=True,episodes=1)
    try:
        output=run.medium.add((0,0),0.,role='output');ordinary=run.medium.native.elements[0].id
        signals=defaultdict(list,{ordinary:[.8,.6]})
        before=run.medium.native.gain(output)
        run.reward_update('perceive',rows['perceive'].reference,signals)
        row=next(r for r in run._last_reward if r['id']==output)
        assert row['eligibility']==0 and row['delta']==0 and run.medium.native.gain(output)==before
        assert run.rbar==pytest.approx(.55)
    finally:run.close()


def test_chunked_small_evidence_order_and_exclusive_create(tmp_path):
    from evidence.tactical_composition_demo.growing_shapes.runner.rev6_trace import Chunks
    store=Chunks(tmp_path/'ledger');store.LIMIT=100
    for i in range(8):store.append(dict(index=i,payload='x'*40))
    receipt=store.receipt()
    assert len(receipt['files'])>1 and receipt['records']==8
    assert [r['index'] for r in store]==list(range(8))
    assert all(Path(r['path']).stat().st_size<50_000_000 for r in receipt['files'])
    with pytest.raises(FileExistsError):Chunks(tmp_path/'ledger')


def test_secondary_donor_capture_uses_valid_default_choose_synthetic_world(monkeypatch):
    from types import SimpleNamespace
    from evidence.tactical_composition_demo.growing_shapes.runner import rev6_evaluator as module
    class SyntheticWorld:
        def __init__(self,*args,**kwargs):self.step_index=0
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def observe(self):
            return SimpleNamespace(done=self.step_index==2,enemy_count=1,enemies=[SimpleNamespace(id=7,visible=True,hp=100,distance=1,angle=.2)])
        def step(self,chosen):
            assert chosen.choice==7 and chosen.magnitude==0
            self.step_index+=1
    monkeypatch.setattr(module,'World',SyntheticWorld)
    rows,_=reused_calibration();evaluator=Evaluator(rows)
    monkeypatch.setattr(evaluator,'require',lambda:None)
    schedule=evaluator.capture('choose',640)
    assert len(schedule)==2 and all(any(d[5]>0 for d in row) for row in schedule)
