"""Native/reference synthetic contracts; no judging or development panel."""
from collections import deque
import ctypes as C
from dataclasses import asdict
import math
import numpy as np
import pytest
from evidence.tactical_composition_demo.growing_shapes.medium.design_0h import DesignMedium, Frame
from evidence.tactical_composition_demo.growing_shapes.medium.medium import Params, Drive
from evidence.tactical_composition_demo.growing_shapes.world.world import World
from evidence.tactical_composition_demo.growing_shapes.runner.native import contract, batch, library
from evidence.tactical_composition_demo.growing_shapes.runner.protocol import bindings, permutation, action, Calibration
from evidence.tactical_composition_demo.growing_shapes.runner.perf_compare import Compare, medium_state, snapshot
from evidence.tactical_composition_demo.growing_shapes.runner.run import Run
from evidence.tactical_composition_demo.growing_shapes.runner import qualification


@pytest.fixture(scope='module')
def native_library():
    return library()


def pair_step(reference,native,ds,lib,adapt=True):
    reference.integrate(ds)
    if adapt:
        reference.adapt()
        reference.timers()
    data = contract(native,ds,adapt=adapt,lib=lib)
    Compare().check(medium_state(reference),medium_state(native))
    if adapt:
        assert data['steps'][0]['covered'] == [reference.covered(s) for s in range(8)]
    else:
        assert reference.native.save() == native.native.save()
        assert [asdict(f) for f in reference.frames] == [asdict(f) for f in native.frames]
    return data


def test_rk4_byte_identical_complete_snapshot_continuation(native_library):
    m = DesignMedium(7)
    for i in range(5):
        m.add((i*.3,i*.1),i*.4,math.pi+i*.02,.3+i*.1)
    n = m.clone()
    try:
        for k in range(12):
            ds = [Drive(s,4*math.cos(s),4*math.sin(s),math.pi*m.time+s*.1,math.pi,
                        float(k%3!=0),1,3) for s in range(8)]
            pair_step(m,n,ds,native_library,False)
        assert snapshot(m.native.save()) == snapshot(n.native.save())
    finally:
        m.close();n.close()


@pytest.mark.parametrize('count',[98,99,100,101])
@pytest.mark.parametrize('active',[0,78,79,80,100])
@pytest.mark.parametrize('offset',[0.,.5,.50001,math.pi])
def test_warmup_eligibility_offset_and_timers(count,active,offset,native_library):
    m = DesignMedium(params=Params(A=0,B=0,K=0,geometry_rate=0,window=101,min_samples=100))
    id = m.add((0,0),math.pi*(count-1)*.1+offset,gain=0)
    m.frames = deque([Frame(k,k*.1,{id:(0.,0.,math.pi*k*.1+offset)},
        {0:(0.,0.,math.pi*k*.1,float(k>=count-active))},{id:()}) for k in range(count)],maxlen=601)
    m.step_index = count-1
    m.death[id] = 3.
    m.novelty[0] = 4.
    n = m.clone()
    try:
        pair_step(m,n,[Drive(0,0,0,math.pi*m.time,math.pi,float(active>0),1,3)],native_library)
    finally:
        m.close();n.close()


@pytest.mark.parametrize('distance',[3-1e-12,3.,3+1e-12])
def test_strict_reach_and_tied_salience(distance,native_library):
    m = DesignMedium(params=Params(A=0,B=0,K=0,geometry_rate=0,window=101,min_samples=100))
    id = m.add((0,0),10*math.pi,gain=.7)
    m.frames = deque([Frame(k,k*.1,{id:(0.,0.,math.pi*k*.1)},
        {s:(distance,0.,math.pi*k*.1+(math.pi*(k%2) if s else 0),1.) for s in range(2)},
        {id:()}) for k in range(101)],maxlen=601)
    m.step_index = 100
    n = m.clone()
    try:
        pair_step(m,n,[Drive(s,distance,0,math.pi*m.time,math.pi,1,1,3) for s in range(2)],native_library)
    finally:
        m.close();n.close()


@pytest.mark.parametrize('task',['perceive','move','remember_static','choose'])
@pytest.mark.parametrize('batch_size',[1,37,200])
def test_all_bindings_actions_batch_boundaries_and_hidden_memory(task,batch_size,native_library):
    m = DesignMedium(12)
    # Coherent readout, not just abstention; choose and movement decisions matter.
    for i in range(3):
        m.add((.2*i,0),.1*i,gain=.5)
    n = m.clone()
    assignment = permutation(4)
    try:
        with World(task,4,'dev') as a, World(task,4,'dev',library=a.library) as b:
            while not a.observe().done:
                count = min(batch_size,200-n.step_index%200)
                data = batch(n,b,assignment,count,0,native_library)
                for row in data['steps']:
                    obs = a.observe()
                    ds = bindings(task,obs,assignment,m.time)
                    Compare().check([[getattr(d,k) for k,_ in d._fields_] for d in ds],row['drives'],'drives')
                    m.integrate(ds);m.adapt();m.timers()
                    Compare().check(asdict(m.frames[-1]),row['frame'],'frame')
                    Compare().check(m.events[-1],row['event'],'event')
                    Compare().check(m.death,row['death'],'death',True)
                    Compare().check(list(m.novelty.values()),row['novelty'],'novelty',True)
                    assert [m.covered(s) for s in range(8)] == row['covered']
                    chosen = action(task,obs,m.native,m.time)
                    if row['action'] is not None:
                        Compare().check([chosen.angle,chosen.magnitude,chosen.choice],row['action'],'action')
                    a.step(chosen)
                if data['boundary']:
                    b.step(action(task,b.observe(),n.native,n.time))
                Compare().check(medium_state(m),medium_state(n),'state')
                Compare().check(a.observe().as_dict() if hasattr(a.observe(),'as_dict') else
                    bytes(a.observe()), b.observe().as_dict() if hasattr(b.observe(),'as_dict') else bytes(b.observe()),'world')
            Compare().check({k:getattr(a.score(),k) for k,_ in a.score()._fields_},
                            {k:getattr(b.score(),k) for k,_ in b.score()._fields_},'score')
    finally:
        m.close();n.close()


def test_growth_and_qualification_check_state_order(native_library):
    # No episode panel: drive a synthetic triangle into a qualification boundary.
    m = DesignMedium(params=Params(A=0,B=0,K=0,geometry_rate=0,window=101,min_samples=100))
    points = [(0.,0.),(1/1.8,0.),(1/3.6,math.sqrt(3)/3.6)]
    ids = [m.add(point,599*.1*math.pi,gain=0) for point in points]
    m.frames = deque([Frame(k,k*.1,{id:(*point,k*.1*math.pi) for id,point in zip(ids,points)},
        {0:(4.,0.,k*.1*math.pi,1.)},{id:tuple(j for j in ids if id!=j) for id in ids})
        for k in range(600)],maxlen=601)
    m.step_index = 599
    m.novelty[0] = 20.
    n = m.clone()
    try:
        pair_step(m,n,[Drive(0,4,0,math.pi*m.time,math.pi,1,1,3)],native_library)
        assert m.growth() == n.growth()
        Compare().check(medium_state(m),medium_state(n),'growth_state')
        Compare().check(qualification.start(m),qualification.start(n),'qualification')
        Compare().check(snapshot(m.native.save()),snapshot(n.native.save()),'saved_check_state')
    finally:
        m.close();n.close()


def test_batch_refuses_growth_crossing_without_mutation(native_library):
    m = DesignMedium()
    m.step_index = 199
    m.frames.clear();m.record()
    before = m.native.save()
    try:
        with World('perceive',0,'dev') as world:
            with pytest.raises(ValueError,match='crosses growth'):
                batch(m,world,permutation(0),2,0,native_library)
            assert m.native.save() == before and world.observe().step == 0
    finally:
        m.close()


def test_comparator_fails_on_event_and_decision_and_exact_timer():
    for a,b in [({'rule':'B1'},{'rule':'D1'}),({'covered':True},{'covered':False}),
                ({'death':{0:40.}},{'death':{0:40.+1e-12}})]:
        with pytest.raises(AssertionError):
            Compare().check(a,b)


@pytest.mark.parametrize('control',[False,True])
def test_episode_reward_and_control_boundaries(control,native_library):
    from types import SimpleNamespace
    rows = {'perceive':Calibration('perceive',0.,-2.,2.,0.,True)}
    reference = Run(17,rows,reward=True,episodes=2,control=control,backend='reference',audit=True)
    native = Run(17,rows,reward=True,episodes=2,control=control,backend='native',audit=True)
    source = SimpleNamespace(births_at=lambda index:[100,101,102]) if control else None
    try:
        for episode in range(2):
            reference.episode(episode,source)
            native.episode(episode,source)
            a,b = reference.report(),native.report()
            a.pop('timing');b.pop('timing')
            Compare().check(a,b,'report')
            Compare().check(reference.step_audit,native.step_audit,'endpoints')
            Compare().check(medium_state(reference.medium),medium_state(native.medium),'state')
            assert reference.rbar == pytest.approx(native.rbar,abs=1e-10)
        assert reference.exposure['reward_episodes'] == 2
        if control:
            assert reference.queue.additions == native.queue.additions == 2
            assert reference.queue.drops == native.queue.drops == 1
    finally:
        reference.close();native.close()


@pytest.mark.parametrize('case',['death','protection','cap','budget','novelty_reset'])
def test_native_timers_feed_unchanged_growth_decisions(case,native_library):
    m = DesignMedium(params=Params(A=0,B=0,K=0,geometry_rate=0,window=101,min_samples=100))
    count = 64 if case in ('cap','budget') else 1
    for i in range(count):
        m.add((10.*i,0),199*.1*math.pi,gain=0)
    if case == 'protection':
        m.birth_steps[0] = 100
    m.frames.clear()
    for k in range(99,200):
        m.frames.append(Frame(k,k*.1,{i:(10.*i,0.,k*.1*math.pi) for i in range(count)},
            {0:(4.,0.,k*.1*math.pi,1.)},{i:() for i in range(count)}))
    m.step_index = 199
    m.death = {i:39.9 if case in ('death','protection') else 0. for i in range(count)}
    m.novelty[0] = 19.9
    if case == 'novelty_reset':
        m.novelty[0] = 12.
    if case == 'budget':
        # Cost veto before N cap; 63 live entries with one internal pair.
        m.remove(63,'fixture_remove')
        m.native.set_element(1,.1,0,199*.1*math.pi,math.pi)
        m.native.set_element(2,.2,0,199*.1*math.pi,math.pi)
        m.native.set_element(3,.3,0,199*.1*math.pi,math.pi)
        m.native.set_element(4,.4,0,199*.1*math.pi,math.pi)
        # Ten union pairs -> cost 64 before the potential birth.
    n = m.clone()
    try:
        drives = [] if case == 'novelty_reset' else [Drive(0,4,0,math.pi*m.time,math.pi,1,1,3)]
        pair_step(m,n,drives,native_library)
        assert m.growth() == n.growth()
        Compare().check(medium_state(m),medium_state(n),'growth')
        rules = [e['rule'] for e in m.events]
        if case == 'death':
            assert 'D1' in rules
        elif case == 'protection':
            assert 'D1' not in rules
        elif case == 'cap':
            assert any(e['rule']=='B1_rejected' and e['values']['reason']=='cap' for e in m.events)
        elif case == 'budget':
            assert any(e['rule']=='B1_rejected' and e['values']['reason']=='cost' for e in m.events)
        else:
            assert m.novelty[0] == 0.
    finally:
        m.close();n.close()
