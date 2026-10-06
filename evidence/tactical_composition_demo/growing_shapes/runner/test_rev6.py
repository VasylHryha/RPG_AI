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
    assert len(inventory['seed_inventory'])==2846
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


def test_construct_only_dry_check_never_integrates(monkeypatch,tmp_path):
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
    (tmp_path/'construct.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    committed=json.loads((HERE/'REV6_CONSTRUCT_ONLY.json').read_text())
    assert all(json.loads(json.dumps(result['recipes'][name]))==recipe for name,recipe in committed['recipes'].items() if name not in ('F3','F6'))
    assert result['recipes']['F3']['members'][0][0]!=result['recipes']['F3']['members'][1][0]
    assert 'F9' in result['recipes']
    current=json.loads((HERE/'REV65_19_9_CONSTRUCT_ONLY.json').read_text())
    assert current['label']=='19.9 and D1-D3 integration; construction only'
    assert json.loads(json.dumps(result))=={k:current[k] for k in result}
    assert result['recipes']['F6']['copies']==140
    assert result['recipes']['F6']['baseline_unique_recipient_episodes']==10


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


def test_geometric_trial_matches_native_clone_random_states(monkeypatch):
    from evidence.tactical_composition_demo.growing_shapes.medium.rev6_design import geometry,geometric_graph,deficit
    rng=np.random.default_rng(57302)
    for n in (3,12,24):
        with medium() as m:
            for j in range(n):
                x,y=rng.uniform(-4,4,2)
                m.add((x,y),rng.uniform(-1,1),gain=float(rng.choice([0.,1.])),role='output' if j==n-1 else 'element')
            m.native.remove(1);m.death.pop(1);m.birth_steps.pop(1) # array/id tie order after a deletion
            m.native.silence(0,True)
            m.drives=[drive(s,4*math.cos(s*math.pi/4),4*math.sin(s*math.pi/4)) for s in range(8)]
            es,ds=geometry(m.native,m.drives);g=geometric_graph(es,ds)
            assert g==m.influence()
            for _ in range(4):
                a=es[0][0];b=es[-1][0];point=tuple(rng.uniform(-3,3,2));site=int(rng.integers(8))
                before=m.influence();old_gap=deficit(m.native,before.forward(site),before.backward())
                branch=m.native.clone()
                try:
                    new=branch.add(*point,0.,math.pi);branch.set_gain(new,1.)
                    from evidence.tactical_composition_demo.growing_shapes.medium.rev6_design import graph
                    after=graph(branch,m.drives);reached=after.forward(site)
                    expected=dict(edge_a_to_new=a in after.incoming[new],new_reached=new in reached,a_reached=a in reached,
                        paths_kept=all(not before.path(s) or after.path(s) for s in before.roots),
                        deficit_or_connect=after.path(site) or deficit(branch,reached,after.backward())<old_gap,
                        clearance=all(math.hypot(e.x-point[0],e.y-point[1])>=.05 for e in m.native.elements))
                finally:branch.close()
                monkeypatch.setattr(m,'clone',lambda **kwargs:pytest.fail('trial cloned medium'))
                assert m.trial(site,a,b,point)==expected
    # Exact equal-distance ties and strict boundary, with array order preserved.
    with medium() as m:
        for j in range(10):m.add((1 if j%2 else -1,0),0,gain=0.)
        m.add((0,0),0,role='output');m.add((3,0),0)
        es,ds=geometry(m.native,[]);assert geometric_graph(es,ds)==m.influence()


@pytest.mark.parametrize('mode',['intact','donor','output_channel','receiver','site0','oracle','empty','input_phasor','k_zero','fixed_structure'])
def test_gp_assay_native_reference_tiny_synthetic(mode):
    from evidence.tactical_composition_demo.growing_shapes.world.world import Observation,Enemy
    with medium() as reference:
        reference.frozen=True
        reference.native.start_clock(1.);reference.step_index=10
        if mode not in ('empty','input_phasor'):
            reference.add((3.2,0),.1,gain=1.);reference.add((2.65,0),-.2,role='output')
        # Nonzero carrier catches start/end clock and donor off-by-one errors.
        reference.frames.clear();reference.record()
        if mode=='output_channel':reference.native.lesions([1])
        if mode=='receiver':reference.native.lesions([0])
        if mode in ('k_zero','fixed_structure'):reference.native.comparator(mode)
        native=reference.clone();observations=[];assignment=list(range(8));schedule=None
        for j in range(3):
            obs=Observation(task=0,step=j,horizon=3,enemy_count=2)
            obs.enemies[0]=Enemy(id=8,visible=int(j!=2),angle=.4,distance=1,hp=100)
            obs.enemies[1]=Enemy(id=3,visible=int(j!=2),angle=-.7,distance=1,hp=100)
            observations.append(obs)
        if mode=='donor':schedule=[replay_on_clock([[2,0,4,1.1,math.pi,2,1,3]],1+j*.1) for j in range(3)]
        try:
            got=bridge.assay_synthetic(native,observations,assignment,schedule=schedule,relay={'site0':1,'oracle':2,'input_phasor':3}.get(mode,0))
            for j,(obs,row) in enumerate(zip(observations,got['decisions'])):
                from evidence.tactical_composition_demo.growing_shapes.runner.rev6_protocol import bindings,action
                ds=bindings('perceive',obs,assignment,reference.time) if schedule is None else schedule[j]
                diag=reference.integrate(ds)
                from evidence.tactical_composition_demo.growing_shapes.runner.rev6_protocol import input_phasor
                chosen=input_phasor(obs,reference.drives,reference.time) if mode=='input_phasor' else relay('perceive',obs,reference.drives,reference.time,mode) if mode in ('site0','oracle') else action('perceive',obs,reference.native,reference.time)
                assert row['angle']==pytest.approx(chosen.angle,abs=1e-12)
                assert row['magnitude']==chosen.magnitude and row['choice']==chosen.choice
                assert row['paths']==diag['paths']
                assert row['has_output']==(mode in ('site0','oracle') or mode!='empty')
                np.testing.assert_allclose(row['drives'],[[getattr(d,f) for f,_ in d._fields_] for d in ds],atol=1e-14,rtol=0)
            np.testing.assert_array_equal([[e.x,e.y,e.phase] for e in native.native.elements],[[e.x,e.y,e.phase] for e in reference.native.elements])
            assert native.step_index==reference.step_index
        finally:native.close()


def test_F1_rejects_transient_crossing_and_requires_deadline():
    from evidence.tactical_composition_demo.growing_shapes.runner.rev6_fixtures import step_response
    records=[dict(time=8+(j+1)*.1,beta=math.pi/2 if j>=20 else 0.) for j in range(80)]
    result=step_response(records);assert result['response_pass'] and result['delay']==pytest.approx(2.1)
    records[21]['beta']=0.;assert not step_response(records)['response_pass']
    records[21]['beta']=math.pi/2;records[-1]['beta']=0.;assert not step_response(records)['response_pass']
    assert not step_response(records[:-1])['response_pass']


def test_memory_singleton_contract_and_window_split():
    from evidence.tactical_composition_demo.growing_shapes.runner.rev6_evaluator import single_oscillator,evaluation_modes
    from evidence.tactical_composition_demo.growing_shapes.runner.rev6_reporting import memory_windows
    from evidence.tactical_composition_demo.growing_shapes.medium.design_0h import SITES
    m=single_oscillator(719,math.pi)
    try:
        e=m.native.elements[0];q=SITES[__import__('evidence.tactical_composition_demo.growing_shapes.runner.rev6_protocol',fromlist=['permutation']).permutation(719)[0]]
        assert (e.x,e.y)==tuple(q) and m.role(e.id)=='element' and m.native.gain(e.id)==1 and e.rate==math.pi and e.phase==math.pi
        site=Drive(0,e.x,e.y,e.phase+.8,math.pi,2,1,3)
        m.integrate([site]);encoded=m.native.elements[0].phase-math.pi*m.time
        assert encoded>0
        m.integrate([Drive(0,e.x,e.y,math.pi*m.time,math.pi,0,1,3)])
        assert m.native.elements[0].phase-math.pi*m.time==pytest.approx(encoded,abs=1e-14)
        assert (m.native.elements[0].x,m.native.elements[0].y)==(e.x,e.y)
    finally:m.close()
    assert {'single_oscillator','sample_and_hold'}<=set(evaluation_modes('remember_static'))
    assert 'single_oscillator' not in evaluation_modes('perceive')
    decisions=[dict(angle=.2 if j<40 else .3,has_output=True,drives=[[0,4,0,math.pi*j*.1+.8,math.pi,2 if j<40 else 0,1,3]]) for j in range(160)]
    summary=memory_windows(decisions)
    assert summary['encoding']['mean_abs_error']==pytest.approx(.6)
    assert summary['retention']['mean_abs_error']==pytest.approx(.5)
    assert summary['retention']['mean_abs_drift_from_encoded_output']==pytest.approx(.1)


def test_silenced_root_native_reference():
    with medium() as m:
        id=m.add((4,0),0.);m.native.silence(id,True);m.add((3.4,0),0.,role='output')
        branch=m.clone()
        try:
            ds=[drive()];m.integrate(ds);m.timers();got=bridge.contract(branch,ds)['steps'][0]
            assert not m.influence().roots[0] and not any(got['paths'])
            assert got['cut_off'][str(id)]==m.native.cut_off(id)==.1
        finally:branch.close()


def test_descriptive_synthetic_ledgers():
    from evidence.tactical_composition_demo.growing_shapes.runner.rev6_reporting import descriptive
    def event(rule,**v):return dict(time=25600,rule=rule,values=v)
    events=[event('birth_request',birth_rule='B-path'),event('birth_request',birth_rule='B-path'),
        event('birth_terminal',birth_rule='B-path',outcome='cap',attempts=3,failures={'new_reached':2}),
        event('birth_terminal',birth_rule='B-path',outcome='accepted',attempts=2),event('D4'),event('growth_check')]
    diag=[dict(index=256001,paths=[True]+[False]*7,active_sites=[0,1],covered_sites={0:False,1:None},
        exposure={5:dict(radius=7.1,wall=True,sensor_access=False)})]
    summary=descriptive(events,diag,[(25600,8),(32000,9)],start=25600)
    role=summary['birth_roles']['B-path'];assert (role['opportunities'],role['attempts'],role['accepted'])==(2,5,1)
    assert role['resource_rejections']['cap']['per_opportunity']==.5 and summary['cap_limited']
    assert summary['turnover']['deaths']==1 and summary['count_range']==[8,9]
    assert summary['wall']['penetration_element_seconds']==.1 and summary['wall']['maximum_radius']==7.1
    assert summary['uncovered_sensor_exposure']['fraction']==1. and summary['uncovered_sensor_exposure']['undefined_warmup_site_steps']==1
    assert summary['unmet_output_or_path_demand'] and summary['path_exposure']['fractions'][0]==1


def test_committed_approval_record_and_start_snapshot(monkeypatch,tmp_path):
    from evidence.tactical_composition_demo.growing_shapes.runner import rev6_identity
    with pytest.raises(PermissionError):Execution(approval_reference='made up')
    with pytest.raises(PermissionError):Execution(approval_reference=str(tmp_path/'record.md'))
    grant=Execution(approval_reference='docs/decisions/0028-owner-directed-exploratory-composable-shapes.md')
    assert len(grant._approval['sha256'])==64
    with pytest.raises(PermissionError):grant.require('fixtures') # identity is no authorization
    # All authority booleans are synthetic here; no fixture method or world is called.
    grant=Execution(owner_revision=True,owner_fixtures=True,engines_ready_reviewed=True,integration_tested_reviewed=True,
        source_units_endpoints_ready=True,approval_reference=grant.approval_reference)
    calls=[]
    monkeypatch.setattr(rev6_identity,'assert_inputs',lambda:calls.append(1) or dict(sha256={'design':'snapshot'}))
    receipt=grant.start('fixtures');assert len(calls)==1
    for _ in range(3):assert grant.snapshot('fixtures')['sha256']==receipt['sha256']
    assert len(calls)==1
    monkeypatch.setattr(rev6_identity,'assert_inputs',lambda:pytest.fail('unexpected recheck'))
    assert grant.snapshot('fixtures')['sha256']=={'design':'snapshot'}


def test_F9_denied_and_move_decoder_limit():
    from evidence.tactical_composition_demo.growing_shapes.runner.rev6_fixtures import Harness,F9_CASES
    from evidence.tactical_composition_demo.growing_shapes.world.world import Observation
    from evidence.tactical_composition_demo.growing_shapes.runner.rev6_protocol import bindings
    with pytest.raises(PermissionError):Harness().F9()
    for bearing,distance,desired in F9_CASES.values():
        obs=Observation(task=1,target_angle=bearing,target_distance=distance,desired_range=desired)
        ds=bindings('move',obs,list(range(8)),0.)
        active=[d for d in ds if d.strength>0];phase=active[0].phase if active else 0.
        assert decode('move',obs,1.,phase,0.).magnitude==1.


def test_exhausted_site_104_trials_never_clones_medium_or_native(monkeypatch):
    from evidence.tactical_composition_demo.growing_shapes.runner.rev65_timing import exhausted_state
    m=exhausted_state(26)
    try:
        before=m.native.save()
        monkeypatch.setattr(m,'clone',lambda **kwargs:pytest.fail('medium cloned in B-path'))
        monkeypatch.setattr(m.native,'clone',lambda **kwargs:pytest.fail('native cloned in rejected B-path'))
        assert m.b_path()==[]
        result=[e['values'] for e in m.events if e['rule']=='birth_terminal'][-1]
        assert result['outcome']=='exhausted' and result['attempts']==104
        assert m.native.save()==before
    finally:m.close()


def test_memory_comparator_episode_uses_cue_and_hold_with_fake_world(monkeypatch):
    from types import SimpleNamespace
    from evidence.tactical_composition_demo.growing_shapes.runner import rev6_evaluator as module
    from evidence.tactical_composition_demo.growing_shapes.world.world import Observation,Enemy
    class SyntheticWorld:
        def __init__(self,*a,**kw):self.index=0
        def __enter__(self):return self
        def __exit__(self,*a):pass
        def observe(self):
            o=Observation(task=7,done=self.index==2,enemy_count=1)
            o.enemies[0]=Enemy(id=0,visible=self.index==0,angle=.8,distance=0,hp=100)
            return o
        def step(self,a):assert a.magnitude==0;self.index+=1
        def score(self):return SimpleNamespace(angular_error=0.,distance_error=0.)
    monkeypatch.setattr(module,'World',SyntheticWorld)
    rows,_=reused_calibration();e=Evaluator(rows,backend='reference');monkeypatch.setattr(e,'require',lambda:None)
    with medium() as m:
        value=template(m.native,[],0.)
        hold=e.episode(value,'remember_static',713,mode='sample_and_hold')
        oscillator=e.episode(value,'remember_static',713,mode='single_oscillator')
    assert [r['angle'] for r in hold['decisions']]==pytest.approx([.8,.8])
    assert 0<oscillator['decisions'][0]['angle']<.8
    assert oscillator['decisions'][1]['angle']==pytest.approx(oscillator['decisions'][0]['angle'],abs=1e-14)
    assert hold['memory_windows']['encoding']['mean_abs_error']==pytest.approx(0.)


def test_scientific_identity_scope_and_drift_detection(monkeypatch,tmp_path):
    from evidence.tactical_composition_demo.growing_shapes.runner import rev6_identity as identity
    snapshot=identity.assert_inputs()
    assert snapshot['checked']=='execution_start_once'
    assert 'AGENTS.md' not in snapshot['sha256']
    assert not any('/reviews/' in name for name in snapshot['sha256'])
    assert 'evidence/tactical_composition_demo/growing_shapes/runner/REV6_SEED_INVENTORY.json' in snapshot['sha256']
    design='evidence/tactical_composition_demo/DESIGN_0H_REV6.md'
    (tmp_path/design).parent.mkdir(parents=True);(tmp_path/design).write_text('design')
    digest=hashlib.sha256(b'design').hexdigest()
    pin=tmp_path/'pin';pin.mkdir();(pin/'REV65_SOURCE_IDENTITY.json').write_text(json.dumps({'sha256':{design:digest}}))
    monkeypatch.setattr(identity,'HERE',pin);monkeypatch.setattr(identity,'ROOT',tmp_path);monkeypatch.setattr(identity,'DESIGN_SHA256',digest)
    identity.assert_inputs()
    (tmp_path/'AGENTS.md').write_text('unrelated process change');identity.assert_inputs()
    (tmp_path/design).write_text('changed')
    with pytest.raises(ValueError,match='scientific input identity'):identity.assert_inputs()


def test_geometric_admission_cost_matches_native_clone():
    rng=np.random.default_rng(1860)
    for n in (4,24,50,64):
        with medium() as m:
            for _ in range(n):m.add(tuple(rng.uniform(-1,1,2)),0.)
            for _ in range(3):
                point=tuple(rng.uniform(-2,2,2))
                if n==64:expected='cap'
                else:
                    branch=m.native.clone()
                    try:
                        branch.add(*point,0.,math.pi)
                        expected='cost' if branch.cost(1.,.1)['total']>64 else None
                    finally:branch.close()
                assert m.feasible(point,0.)==expected


def test_19_9_K_zero_all_RK_stages_drive_motion_and_output_retained():
    with medium() as original:
        original.frozen=True
        original.add((3.2,0),.1,gain=.8)
        original.add((2.65,.1),1.2,gain=.4,role='output')
        ablated=original.clone()
        try:
            ablated.native.comparator('k_zero')
            before=[e.as_dict() for e in ablated.native.elements]
            ds=[drive(phase=1.7)]
            for _ in range(5):
                for m in (original,ablated):m.native.set_drives(ds);m.native.step(.02)
                assert all(row[1]==0. for stage in ablated.native.stage_terms() for row in stage)
                assert any(row[0]!=0. for stage in ablated.native.stage_terms() for row in stage)
                assert any(row[1]!=0. for stage in original.native.stage_terms() for row in stage)
            after=ablated.native.elements
            assert len(after)==len(before)==2 and not any(e.silent for e in after)
            assert after[0].x!=before[0]['x'] # motion remains on
            assert after[1].phase==pytest.approx(before[1]['phase']+math.pi*.1,abs=1e-14)
            assert original.native.elements[1].phase!=pytest.approx(after[1].phase,abs=1e-6)
            assert ablated.native.output()[0]==1. and ablated.role(after[1].id)=='output'
            assert ablated.native.gain(after[0].id)==.8
        finally:ablated.close()


def test_19_9_fixed_structure_freezes_wall_and_pair_motion_but_keeps_transfer():
    with medium() as original:
        original.frozen=True
        original.add((6.2,0),.1,gain=.8)
        original.add((5.65,.1),1.2,gain=.4,role='output')
        fixed=original.clone()
        try:
            fixed.native.comparator('fixed_structure')
            before=[(e.x,e.y,e.phase) for e in fixed.native.elements]
            for _ in range(3):
                for m in (original,fixed):m.integrate([drive(x=6.2,phase=1.7)])
                assert [(e.x,e.y) for e in fixed.native.elements]==[row[:2] for row in before]
                assert any(row[1]!=0. for stage in fixed.native.stage_terms() for row in stage)
            assert len(fixed.native)==2 and fixed.frozen
            assert fixed.native.elements[1].phase!=pytest.approx(before[1][2]+math.pi*.3,abs=1e-6)
            assert original.native.elements[0].x!=before[0][0]
            assert fixed.native.output()[0]==1.
        finally:fixed.close()


def test_19_9_phasor_weighted_inputs_no_medium_and_inactive_sites():
    from evidence.tactical_composition_demo.growing_shapes.runner.rev6_protocol import input_phasor
    from evidence.tactical_composition_demo.growing_shapes.world.world import Observation
    obs=Observation(task=0);time=1.1
    ds=[Drive(0,4,0,math.pi*time,math.pi,1,1,3),
        Drive(2,0,4,math.pi*time+math.pi/2,math.pi,2,1,3),
        Drive(3,0,-4,math.pi*time-1,math.pi,0,1,3)]
    assert input_phasor(obs,ds,time).angle==pytest.approx(math.atan2(2.,1.),abs=1e-14)
    assert input_phasor(obs,[],time).angle==pytest.approx(0.)
    # Relative input angles are invariant under the pi carrier-offset branch.
    for d in ds:d.phase+=math.pi
    assert input_phasor(obs,ds,time+1).angle==pytest.approx(math.atan2(2.,1.),abs=1e-14)


@pytest.mark.parametrize('mode,task',[('input_phasor','perceive')]+[(m,t) for m in ('k_zero','fixed_structure') for t in ('perceive','move','choose','remember_static')])
def test_19_9_evaluator_native_reference_with_fake_world(monkeypatch,mode,task):
    from types import SimpleNamespace
    from evidence.tactical_composition_demo.growing_shapes.runner import rev6_evaluator as module
    from evidence.tactical_composition_demo.growing_shapes.world.world import Observation,Enemy
    task_id={'perceive':0,'move':1,'choose':3,'remember_static':7}[task]
    observations=[]
    for j in range(3):
        o=Observation(task=task_id,step=j,horizon=3,enemy_count=2,target_angle=.4,target_distance=4.,desired_range=2.)
        o.enemies[0]=Enemy(id=0,visible=task=='choose' or j!=2,angle=.3,distance=1,hp=100)
        o.enemies[1]=Enemy(id=1,visible=task=='choose' or j!=2,angle=-.8,distance=2,hp=100)
        observations.append(o)
    class FakeWorld:
        def __init__(self,*a,**kw):self.index=0
        def __enter__(self):return self
        def __exit__(self,*a):pass
        def observe(self):return observations[self.index] if self.index<3 else Observation(task=task_id,done=1)
        def step(self,a):self.index+=1
        def score(self):return SimpleNamespace(angular_error=0.,distance_error=0.,goal_error=0.,correct_choice_rate=1.)
    def synthetic(m,w,assignment,**kw):
        if mode=='input_phasor':assert len(m.native)==0
        return bridge.assay_synthetic(m,observations,assignment,**kw)
    monkeypatch.setattr(module,'World',FakeWorld);monkeypatch.setattr(bridge,'assay',synthetic)
    rows,_=reused_calibration()
    with medium() as m:
        m.add((3.2,0),.1,gain=.8);m.add((2.65,0),1.2,role='output')
        value=template(m.native,[e.id for e in m.native.elements],0.)
    result=[]
    for backend in ('native','reference'):
        evaluator=Evaluator(rows,backend=backend);monkeypatch.setattr(evaluator,'require',lambda:None)
        result.append(evaluator.episode(value,task,713,mode=mode,carrier_offset=math.pi))
    from evidence.tactical_composition_demo.growing_shapes.runner.rev6_fixtures import assay_parity
    assert assay_parity(*result)['status']=='MATCH'
    assert result[0]['score']==result[1]['score']
    assert value['members'][0][0]==3.2 # disposable copies did not change the input


def test_19_9_reporting_same_estimator_and_verdict_isolation():
    from evidence.tactical_composition_demo.growing_shapes.runner.rev6_evaluator import descriptive_comparisons,descriptive_modes,evaluation_modes
    for task in ('perceive','move','choose','remember_static'):
        scores={'intact':np.linspace(.5,1.,128)}
        scores.update({mode:np.linspace(0.,.6,128) for mode in descriptive_modes(task)})
        rows=descriptive_comparisons(task,scores)
        assert set(rows)==set(descriptive_modes(task))<=set(evaluation_modes(task))
        for mode,row in rows.items():
            expected=paired_bounds(scores['intact'],scores[mode],secondary=task!='perceive')
            assert row['estimate']['lower']==expected['lower'] and row['estimate']['upper']==expected['upper']
            assert row['status']=='DESCRIPTIVE' and not row['used_in_verdict']
            assert not {'verdict','positive','negative'}&set(row['estimate'])
        assert ('input_phasor' in rows)==(task=='perceive')
    units=[passing_unit() for _ in range(8)];before=aggregate(units)
    for unit in units:unit['descriptive_comparators']={'input_phasor':{'estimate_status':'INVALID'}}
    assert aggregate(units)==before


def test_D2_F6_baselines_once_per_unique_episode_and_minimum_five():
    from evidence.tactical_composition_demo.growing_shapes.runner.rev6_fixtures import f6_baselines,F6_PAIRS
    class FakeEvaluator:
        def __init__(self):self.calls=[]
        def episode(self,value,task,episode,*,mode):
            self.calls.append((episode,mode))
            return dict(status='evaluated',instance=dict(world_episode=episode),decisions=[dict(angle=.1,has_output=True)]*160)
    fake=FakeEvaluator();rows=f6_baselines(fake,{})
    assert len(fake.calls)==20 and len(set(fake.calls))==20
    assert {e for e,_ in fake.calls}=={e for e,_ in F6_PAIRS}
    repeated=[rows['single_oscillator'][0]]*6
    result=memory_summary([.1]*6,repeated,unique_episodes=True)
    assert result['defined_pairs']==result['unique_episode_count']==1
    assert result['correlation'] is None and result['reason']=='fewer_than_five_defined_pairs'
    angles=[.1,.2,.3,.4,.5]
    unique=[dict(instance=dict(world_episode=i),decisions=[dict(angle=a,has_output=True)]*160) for i,a in enumerate(angles)]
    result=memory_summary(angles,unique,unique_episodes=True)
    assert result['defined_pairs']==result['unique_episode_count']==5 and result['correlation']==pytest.approx(1.)
    unique[-1]['decisions']=[dict(angle=.5,has_output=False)]*160
    assert memory_summary(angles,unique,unique_episodes=True)['defined_pairs']==4
    assert memory_summary(angles,unique,unique_episodes=True)['correlation'] is None


D1_INPUTS=(
 'evidence/tactical_composition_demo/DESIGN_0H.md',
 'evidence/tactical_composition_demo/growing_shapes/runner/development_20261006/CALIBRATION.json',
 'evidence/tactical_composition_demo/growing_shapes/medium/design_0h.py',
 'evidence/tactical_composition_demo/growing_shapes/medium/medium.py',
 'evidence/tactical_composition_demo/growing_shapes/runner/protocol.py',
 'evidence/tactical_composition_demo/growing_shapes/runner/control.py',
 'evidence/tactical_composition_demo/growing_shapes/world/world.py',
)


@pytest.mark.parametrize('changed',D1_INPUTS)
def test_D1_execution_identity_inherited_input_or_calibration_drift(monkeypatch,tmp_path,changed):
    from evidence.tactical_composition_demo.growing_shapes.runner import rev6_identity as identity
    snapshot=identity.assert_inputs();assert set(D1_INPUTS)<=set(snapshot['sha256'])
    design='evidence/tactical_composition_demo/DESIGN_0H_REV6.md';names=(*D1_INPUTS,design)
    hashes={}
    for name in names:
        source=identity.ROOT/name;dest=tmp_path/name;dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(source.read_bytes());hashes[name]=hashlib.sha256(dest.read_bytes()).hexdigest()
    pin=tmp_path/'pin';pin.mkdir();(pin/'REV65_SOURCE_IDENTITY.json').write_text(json.dumps({'sha256':hashes}))
    monkeypatch.setattr(identity,'HERE',pin);monkeypatch.setattr(identity,'ROOT',tmp_path)
    identity.assert_inputs();(tmp_path/changed).write_text('drift')
    with pytest.raises(ValueError,match='scientific input identity'):identity.assert_inputs()
