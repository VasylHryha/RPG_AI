"""Follow-up synthetic contracts; no development or judging seeds."""
from collections import deque
import math
import numpy as np
import pytest
from evidence.tactical_composition_demo.growing_shapes.medium.medium import Medium, Params, Drive
from evidence.tactical_composition_demo.growing_shapes.medium.design_0h import DesignMedium, Frame, spiral, kernel


@pytest.fixture
def medium():
    m = DesignMedium(params=Params(A=0, B=0, K=0, geometry_rate=0, window=101, min_samples=100))
    yield m
    m.close()


def history(m, ids, *, count=101, active=100, offset=0., distance=0., neighbor=False):
    m.frames.clear()
    for k in range(count):
        phase = math.pi*k*.1
        elems = {id: (0., 0., phase+offset) for id in ids}
        sites = {0: (distance, 0., phase, 1. if k >= count-active else 0.)}
        links = {id: tuple(j for j in ids if j != id) if neighbor else () for id in ids}
        m.frames.append(Frame(k, k*.1, elems, sites, links))
    m.step_index = count-1


@pytest.mark.parametrize('gain', [0., .5, 1., 2.])
def test_gain_inside_every_rk4_stage(gain):
    with Medium(params=Params(A=0, B=0, K=0)) as m:
        id = m.add(0, 0)
        m.set_gain(id, gain)
        m.set_drives([Drive(0, 0, 0, math.pi/2, 0, 2, 1, 3)])
        assert m.rhs()[0][2] == 2*gain
        m.step(.01)
        assert m.elements[0].phase == pytest.approx(2*math.atan(math.tanh(gain*.01)), abs=2e-9)


def test_gain_and_options_exact_snapshot_continuation():
    with Medium() as m:
        m.options(automatic_samples=False, carried_sites=True, undirected_cost=True)
        m.first_id(0)
        id = m.add(0, 0)
        m.set_gain(id, .3)
        state = m.save()
        with Medium.load(state) as b:
            assert b.save() == state and b.gain(0) == .3
            m.step(.02)
            b.step(.02)
            assert b.save() == m.save()
        for bad in (-.1, 2.1, float('nan')):
            with pytest.raises(ValueError):
                m.set_gain(id, bad)


def test_world_sampling_and_carried_strength_history():
    with Medium(params=Params(A=0, B=0, K=0, window=101, min_samples=2)) as m:
        id = m.add(0, 0)
        m.options(automatic_samples=False, carried_sites=True)
        for strength in (1., 2., 0., 1.):
            m.set_drives([Drive(0, 0, 0, .3, 0, strength, 1, 3)])
            m.step(.02, 5)
            assert m.measure(id).samples == (0 if strength == 1 and m.time < .2 else round(m.time/.1)-1)
            m.observe()
        assert m.measure(id).samples == 4
        assert m.plv(id, 0, drive=True) > .99
    # Legacy default still invalidates a changed strength, preserving its contract.
    with Medium(params=Params(A=0, B=0, K=0)) as m:
        id = m.add(0, 0)
        m.set_drives([Drive(0, 0, 0, .3, 0, 1, 1, 3)])
        m.observe(); m.observe()
        assert m.plv(id, 0, drive=True) == 1
        m.set_drives([Drive(0, 0, 0, .3, 0, 2, 1, 3)])
        assert m.plv(id, 0, drive=True) == 0


@pytest.mark.parametrize('distance,eligible', [(3.-1e-12, True), (3., False), (3.+1e-12, False)])
def test_strict_drive_partner_coverage_boundary(medium, distance, eligible):
    id = medium.add((0, 0), 0)
    history(medium, [id], distance=distance)
    assert (medium.gain_signal(id) is not None) == eligible
    assert medium.covered(0) == eligible
    assert medium.lock(id) == float(eligible)
    assert bool(kernel(distance)) == eligible
    medium.native.set_drives([Drive(0, distance, 0, math.pi/2, 0, 1, 1, 3)])
    assert (medium.native.rhs()[0][2]-math.pi > 0) == eligible


@pytest.mark.parametrize('distance,amplitude', [(2.-1e-12, 1.), (2., 0.), (2.+1e-12, 0.)])
def test_strict_readout_boundary(distance, amplitude):
    with Medium() as m:
        m.add(distance, 0)
        assert m.readout(0, 0, 1, 2)[0] == amplitude


@pytest.mark.parametrize('active,expected', [(79, False), (80, True), (100, True)])
@pytest.mark.parametrize('offset,covered', [(0., True), (.5, True), (.50001, False), (math.pi, False)])
def test_site_eligibility_offset_and_samples(medium, active, expected, offset, covered):
    id = medium.add((0, 0), 0)
    history(medium, [id], active=active, offset=offset)
    assert (medium.gain_signal(id) is not None) == expected
    assert medium.covered(0) == (expected and covered)
    assert medium.lock(id) == pytest.approx(float(expected), abs=1e-14)  # lock permits anti-phase


@pytest.mark.parametrize('count,lock_defined,gain_defined', [(99, False, False), (100, True, False), (101, True, True)])
def test_indexed_warmup(medium, count, lock_defined, gain_defined):
    id = medium.add((0, 0), 0)
    history(medium, [id], count=count, active=count)
    assert (medium.lock(id) is not None) == lock_defined
    assert (medium.gain_signal(id) is not None) == gain_defined
    assert medium.covered(0) == gain_defined


@pytest.mark.parametrize('active,expected', [(79, 0.), (80, 1.)])
def test_neighbor_eligibility_counts_historical_membership(medium, active, expected):
    ids = [medium.add((i, 0), 0) for i in range(2)]
    history(medium, ids, active=0, neighbor=True)
    medium.frames = deque([Frame(f.index, f.time, f.elements, f.sites,
        {id: tuple(j for j in ids if j != id) if k >= 101-active else () for id in ids})
        for k, f in enumerate(medium.frames)], maxlen=601)
    assert medium.lock(ids[0]) == pytest.approx(expected, abs=1e-14)


def test_union_cost_no_drive_links_and_asymmetric_lists():
    with Medium(params=Params(k=8)) as m:
        for i in range(11):
            m.add(i*.1, 0)
        idx, masks, _ = m.neighbors()
        pairs = {tuple(sorted((i, j))) for i, row in enumerate(idx) for j, on in zip(row, masks[i]) if on}
        directed = sum(sum(row) for row in masks)
        assert len(pairs) != directed/2  # deliberately asymmetric k<=8 lists
        m.set_drives([Drive(0, 0, 0, 0, 0, 1, 1, 3)])
        m.options(undirected_cost=True)
        assert m.cost(1, .1)['active_couplings'] == len(pairs)
        assert m.cost(1, .1)['total'] == pytest.approx(11+.1*len(pairs))
        m.options(undirected_cost=False)
        assert m.cost(1, .1)['active_couplings'] == directed+11


def test_spiral_exact_order_and_exhaustion():
    site = (4., 0.)
    positions = [np.array(site)+.1*j*np.array([math.cos(j*2.39996), math.sin(j*2.39996)]) for j in range(50)]
    assert spiral(site, []) == site
    assert spiral(site, positions[:1]) == tuple(positions[1])
    assert spiral(site, positions) is None


def test_no_drive_gain_rule_and_rate_endpoints(medium):
    id = medium.add((0, 0), 0, rate=math.pi, gain=.7)
    history(medium, [id], active=0)
    medium.adapt()
    assert medium.native.gain(id) == .7
    assert medium.native.elements[0].rate == pytest.approx(math.pi)
    # Endpoint estimator needs k-100 as well as the current sample.
    fs = list(medium.frames)
    fs[0] = Frame(0, 0, {id: (0., 0., -10.)}, fs[0].sites, fs[0].neighbors)
    medium.frames = deque(fs, maxlen=601)
    medium.adapt()
    assert medium.native.elements[0].rate == pytest.approx(math.pi+.005)


def test_gain_uses_current_salience_and_lowest_site_tie(medium):
    id = medium.add((0, 0), 0)
    history(medium, [id])
    medium.frames = deque([Frame(f.index, f.time, f.elements,
        {0: f.sites[0], 1: (0., 0., f.sites[0][2]+math.pi*(f.index%2), 1.)}, f.neighbors)
        for f in medium.frames], maxlen=601)
    assert medium.gain_signal(id) == pytest.approx(1., abs=1e-14)  # equal salience, lowest site 0


def test_timer_resets_and_birth_reset(medium):
    id = medium.add((0, 0), 0)
    history(medium, [id], count=99, active=0)
    medium.death[id] = 4
    medium.timers()
    assert medium.death[id] == 0  # undefined lock resets
    history(medium, [id], active=0)
    medium.timers()
    assert medium.death[id] == .1
    history(medium, [id], offset=math.pi)
    medium.timers()
    assert medium.death[id] == 0
    assert medium.novelty[0] == .1  # locked, but not covered
    history(medium, [id], active=0)
    medium.timers()
    assert medium.novelty[0] == 0
    history(medium, [id], offset=math.pi)
    medium.step_index = 200
    medium.novelty[0] = 20
    born = medium.growth()
    assert len(born) == 1 and medium.novelty[0] == 0
    assert medium.native.gain(born[0]) == 1
    assert medium.samples(born[0], 100) is None


def test_d1_protection_and_monotone_identity(medium):
    id = medium.add((0, 0), 0)
    medium.death[id] = 40
    medium.step_index = 199
    medium.growth(False)
    assert len(medium.native) == 1
    medium.step_index = 200
    medium.growth(False)
    assert len(medium.native) == 0
    new = medium.add((0, 0), 0)
    assert id == 0 and new == 1
    assert medium.events[-2]['rule'] == 'growth_check'


def test_d3_recomputes_cost_ties_and_protected_flag(medium):
    for i in range(65):
        medium.add((i*4, 0), 0)
    medium.growth(False)
    assert any(e['rule'] == 'protected_over_budget' for e in medium.events)
    medium.step_index = 200
    medium.growth(False)
    assert len(medium.native) == 64
    removed = [e for e in medium.events if e['rule'] == 'D3']
    assert removed[0]['ids'] == [0] and removed[0]['cost'] == 64


def test_b1_site_order_two_birth_cap_and_empty_histories(medium):
    medium.frames.clear()
    sites = {s: (10*s, 0., s*.2, 1.) for s in range(8)}
    medium.frames.append(Frame(200, 20, {}, sites, {}))
    medium.step_index = 200
    medium.novelty = {s: 20 for s in range(8)}
    born = medium.growth()
    assert born == [0, 1]
    assert [e.phase for e in medium.native.elements] == [0, .2]
    assert medium.native.gain(0) == 1
    assert all(medium.samples(id, 100) is None for id in born)
    assert [e['values']['site'] for e in medium.events if e['rule'] == 'B1'] == [0, 1]

@pytest.mark.parametrize('reason', ['cap','cost','placement'])
def test_birth_rejections_logged_without_timer_reset(medium,monkeypatch,reason):
    import evidence.tactical_composition_demo.growing_shapes.medium.design_0h as module
    medium.frames.clear()
    medium.frames.append(Frame(200,20,{}, {0:(4.,0.,.3,1.)},{}))
    medium.step_index = 200
    medium.novelty[0] = 20
    if reason == 'placement':
        monkeypatch.setattr(module,'spiral',lambda *_: None)
    else:
        monkeypatch.setattr(medium,'feasible',lambda *_: reason)
    assert medium.growth() == []
    rejected = [e for e in medium.events if e['rule'] == 'B1_rejected']
    assert rejected[0]['values']['reason'] == reason and medium.novelty[0] == 20


def test_feasible_cost_with_newborn_recomputes_union(medium):
    # 63 widely spaced elements, except one existing pair: cost 63.1.
    for i in range(61):
        medium.add((100+4*i,0),0)
    medium.add((0,0),0)
    medium.add((1,0),0)
    assert medium.cost() == pytest.approx(63.1)
    before = medium.native.save()
    assert medium.feasible((.5,0),0) == 'cost'  # N64 + three pairs >64
    assert medium.native.save() == before
    medium.add((1000,0),0)
    assert medium.feasible((2000,0),0) == 'cap'


def test_historical_reach_not_current_geometry(medium):
    id = medium.add((0,0),0)
    history(medium,[id])
    fs = list(medium.frames)
    for k in range(22):
        fs[k] = Frame(k,k*.1,{id:(3.,0.,fs[k].elements[id][2])},fs[k].sites,fs[k].neighbors)
    medium.frames = deque(fs,maxlen=601)
    assert medium.gain_signal(id) is None and not medium.covered(0)  # only 79 reachable samples


def test_one_sample_per_world_step_and_append_before_adapt(medium):
    id = medium.add((0,0),0,gain=0.)
    medium.frames.clear();medium.record()
    for k in range(100):
        medium.integrate([Drive(0,0,0,math.pi*k*.1,math.pi,1,1,3)])
    assert len(medium.frames) == 101
    assert [f.index for f in medium.frames] == list(range(101))
    assert medium.frames[-1].sites[0][2] == pytest.approx(medium.frames[-1].elements[id][2])
    assert medium.gain_signal(id) == pytest.approx(1., abs=1e-14)
    medium.adapt()
    assert medium.native.gain(id) == pytest.approx(.005, abs=1e-14)


def test_rate_and_gain_euler_clip_at_declared_bounds(medium):
    id = medium.add((0,0),0,rate=math.pi,gain=2.)
    history(medium,[id])
    fs = list(medium.frames)
    fs[0] = Frame(0,0,{id:(0.,0.,-100000.)},fs[0].sites,fs[0].neighbors)
    medium.frames = deque(fs,maxlen=601)
    medium.adapt()
    assert medium.native.elements[0].rate == 1.5*math.pi
    assert medium.native.gain(id) == pytest.approx(1.995)
    fs[-1] = Frame(100,10,{id:(0.,0.,-200000.)},fs[-1].sites,fs[-1].neighbors)
    medium.frames = deque(fs,maxlen=601)
    medium.adapt()
    assert medium.native.elements[0].rate == .5*math.pi


def test_v1_native_snapshot_readable_without_options_or_gains():
    # Independently remove the documented v2 extension fields from a one-element
    # explicit-field blob, producing the exact v1 layout (without C padding).
    import ctypes as C
    from evidence.tactical_composition_demo.growing_shapes.medium.medium import Growth, Element
    with Medium() as m:
        id = m.add(1,2,.3,.4)
        v2 = bytearray(m.save())
        header = 8+len(b'growing-medium-v2')
        params_bytes = sum(C.sizeof(t) for _,t in Params._fields_)
        growth_bytes = sum(C.sizeof(t) for _,t in Growth._fields_)
        options = header+params_bytes+growth_bytes
        element_start = options+12+4+4*8+8  # options/config, clock fields, element count
        gain = element_start+sum(C.sizeof(t) for _,t in Element._fields_)
        del v2[gain:gain+8]
        del v2[options:options+12]
        v2[header-1] = ord('1')
        with Medium.load(v2) as old:
            assert old.gain(id) == 1.
            assert old.elements[0].as_dict() == m.elements[0].as_dict()
            old.step(.02);m.step(.02)
            assert old.save() == m.save()
