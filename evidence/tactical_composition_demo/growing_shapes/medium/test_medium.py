"""Engine contracts only: no task growth, learning, judging entropy or panels."""
import ctypes as C
import json
import math
from pathlib import Path
import random
import subprocess
import pytest
from medium import Medium, Params, Drive, Growth, Need

ROOT = Path(__file__).resolve().parent
REFERENCE = ROOT.parents[1] / 'c4_reference' / 'c4_reference_states.json'

def config(**overrides):
    values = dict(L_on=.8, L_off=.2, S_split=.9, T_nov=100., T_split=100., T_death=100.,
                  growth_period=.25, T_protect=0., split_offset=.1, c_e=1., c_c=0., C_max=100.,
                  E_need=1., T_need=1., epsilon_U=.1, N_max=100, reward_arm=0, utility_checks=2)
    values.update(overrides)
    return Growth(**values)

def static(**kwargs):
    return Medium(params=Params(A=0., B=0., K=0., **kwargs))

def flat(value):
    if isinstance(value, (list, tuple)):
        return [n for row in value for n in flat(row)]
    return [value]

def close(actual, expected, tol=1e-9):
    a, b = flat(actual), flat(expected)
    assert len(a) == len(b)
    assert all(abs(x-y) <= tol for x, y in zip(a, b)), max(abs(x-y) for x, y in zip(a, b))

CASES = json.loads(REFERENCE.read_text())['cases']
@pytest.mark.parametrize('case', CASES, ids=lambda c: c['name'])
@pytest.mark.parametrize('variant', ['intact', 'J0', 'K0'])
def test_c4_reference(case, variant):
    v = case['variants'][variant]
    params = dict(v['params'])
    assert not params.pop('frozen_phase_topology')
    with Medium(params=Params(**params)) as m:
        for (x, y), phase, omega in zip(case['x'], case['th'], case['omega']):
            m.add(x, y, phase, omega)
        idx, mask, inv = m.neighbors()
        assert idx == v['neighbors']
        assert mask == v['mask']
        close(inv, v['inv_count'])
        out = m.rhs()
        close([row[:2] for row in out], v['x_dot'])
        close([row[2] for row in out], v['th_dot'])
        m.step(case['dt'])
        close([[e.x, e.y] for e in m.elements], v['x_after_step'])
        close([e.phase for e in m.elements], v['th_after_step'])

@pytest.mark.parametrize('n', [0, 1, 2, 9, 50, 200])
@pytest.mark.parametrize('spread', [.2, 3., 100.])
def test_grid_equals_bruteforce(n, spread):
    rng = random.Random(314159 + n)
    points = [(rng.uniform(-spread, spread), rng.uniform(-spread, spread)) for _ in range(n)]
    if n >= 9:
        points[:9] = [(0., 0.), (3., 0.), (-3., 0.), (0., 3.), (0., -3.), (1., 0.),
                      (-1., 0.), (0., 1.), (0., -1.)]
    with Medium() as m:
        for x, y in points:
            m.add(x, y)
        idx, mask, inv = m.neighbors()
        for i in range(n):
            neighbors = sorted((math.hypot(x-points[i][0], y-points[i][1]), j)
                               for j, (x, y) in enumerate(points) if j != i)[:min(8, n-1)]
            assert idx[i] == [j for _, j in neighbors]
            assert mask[i] == [float(r < 3) for r, _ in neighbors]
            assert inv[i] == 1 / max(1, sum(r < 3 for r, _ in neighbors))
        out = m.rhs()
        for i in range(n):
            # Independent brute-force oracle checks that RK/dynamics use grid active sets.
            indices = [j for j, on in zip(idx[i], mask[i]) if on]
            vx = vy = 0.
            for j in indices:
                dx, dy = points[j][0]-points[i][0], points[j][1]-points[i][1]
                r = max(math.hypot(dx, dy), 1e-6)
                vx += dx * (1.8 - 1/r) / r
                vy += dy * (1.8 - 1/r) / r
            close(out[i], [vx/max(1, len(indices)), vy/max(1, len(indices)), 0.])

def test_drive_and_readout():
    with static() as m:
        a, b, c = m.add(0, 0), m.add(1, 0), m.add(2, 0)
        m.set_drives([Drive(70, 0, 0, math.pi/2, 0., 2., 1., 2.)])
        rhs = m.rhs()
        close([row[2] for row in rhs], [2., 2*math.exp(-.5), 0.])
        m.set_element(a, 0, 0, math.pi/2, 0)
        m.set_element(b, 1, 0, math.pi/2, 0)
        close(m.readout(0, 0, 1., 2.), (1., math.pi/2))
        m.set_element(a, 0, 0, 0, 0)
        m.set_element(b, 1, 0, math.pi, 0)
        amp, phase = m.readout(0, 0, 1., 2.)
        close(amp, (1-math.exp(-.5))/(1+math.exp(-.5)))
        close(phase, 0.)
        close(m.readout(100, 0, 1., 2.), (0., 0.))
        # Input law is integrated at every RK4 stage; zero-distance analytic case.
        m.remove(b); m.remove(c)
        m.step(.01)
        close(m.elements[0].phase, 2*math.atan(math.tanh(.01)), 1e-9)
        m.set_drives([])
        assert m.rhs()[0][2] == 0

def test_time_varying_drive():
    with static() as m:
        m.add(0, 0, 0, 1.)
        m.set_drives([Drive(4, 0, 0, .5, 1., 1., 1., 2.)])
        # Equal oscillator/input rates => stable phase difference .5.
        # Independent fine scalar RK4 for delta_dot=-sin(delta).
        delta = .5
        for _ in range(10):
            dt = .002
            k1 = -math.sin(delta); k2 = -math.sin(delta+dt*k1/2)
            k3 = -math.sin(delta+dt*k2/2); k4 = -math.sin(delta+dt*k3)
            delta += dt*(k1+2*k2+2*k3+k4)/6
            m.step(dt)
        close(m.elements[0].phase, .52-delta, 1e-12)

def test_plv_lock_window_drive_and_groups():
    with static(window=4, min_samples=4) as m:
        a = m.add(0, 0); b = m.add(1, 0); c = m.add(10, 0)
        for k in range(4):
            m.set_element(a, 0, 0, k*math.pi/2, 0)
            m.set_element(b, 1, 0, k*math.pi/2+math.pi, 0)
            m.set_element(c, 10, 0, 0, 0)
            m.set_drives([Drive(5, 10, 0, k*math.pi/2, 0, 1, 1, 2)])
            m.observe()
        close(m.plv(a, b), 1.)  # Anti-phase counts as locked.
        close(m.plv(a, c), 0.)
        close(m.measure(a).lock, 1.)
        close(m.measure(c).lock, 0.)
        assert m.groups(.9, 2.) == [0, 0, 1]
        # Strict C4 spatial link boundary: nearest spacing 1, factor 1 excludes r=1.
        assert m.groups(.9, 1.) == [0, 1, 2]
        # Window eviction: four new constant samples replace old unrelated history.
        for _ in range(4):
            m.set_drives([Drive(5, 10, 0, 0, 0, 1, 1, 2)])
            m.observe()
        close(m.measure(c).lock, 1.)

@pytest.mark.parametrize('second,weight,expected', [(0., 1., 0.), (math.pi, 1., 1.),
                                                    (math.pi, 3., .75), (math.pi/2, 1., .5)])
def test_strain_two_cluster(second, weight, expected):
    with static(window=2) as m:
        a = m.add(0, 0)
        m.set_drives([Drive(1, 0, 0, 0, 0, 1, 1, 2), Drive(2, 0, 0, second, 0, weight, 1, 2)])
        m.observe(); m.observe()
        close(m.measure(a).strain, expected)
        assert 0 <= m.measure(a).strain <= 1

def test_strain_includes_c4_partner_weights():
    with Medium(params=Params(A=0, B=0, K=1, window=2)) as m:
        a=m.add(0, 0); m.add(-1, 0, 0); m.add(1, 0, math.pi)
        m.observe(); m.observe()
        close(m.measure(a).strain, 1.)

@pytest.mark.parametrize('novelty_time', [0., .5, 1.])
def test_b1_duration_at_threshold(novelty_time):
    with static() as m:
        m.set_drives([Drive(1, 0, 0, .3, .7, 1., 1., 2.)])
        m.configure_growth(config(T_nov=novelty_time))
        deadline = max(.25, novelty_time)
        while m.time < deadline:
            m.step(.25)
            m.apply_growth_rules()
            if m.time < deadline:
                assert len(m) == 0
        assert len(m) == 1
        assert m.events[-1]['rule'] == 'B1'
        assert m.events[-1]['measurements']['max_input_lock'] == 0
        assert m.events[-1]['measurements']['in_range'] == 0
        close(m.elements[0].rate, .7)
        close(m.elements[0].phase, .3+.7*deadline)

def test_b1_lock_hysteresis_and_range():
    with static(window=4) as m:
        a=m.add(0,0)
        # PLV exactly .5 over two samples (phase differences +/- pi/3).
        for phase in [-math.pi/3, math.pi/3]:
            m.set_drives([Drive(1,0,0,phase,0,1,1,2)])
            m.observe()
        close(m.measure(a).lock,.5)
        # Lock between off=.2 and on=.8: survives D1, allows B1.
        m.configure_growth(config(T_nov=0., T_death=0., L_off=.2, L_on=.8))
        m.step(.25);m.apply_growth_rules()
        assert a in [e.id for e in m.elements]
        assert any(e['rule']=='B1' for e in m.events)
    with static() as m:
        m.add(0,0);m.set_drives([Drive(1,0,0,0,0,1,1,2)])
        m.observe();m.observe()
        m.configure_growth(config(T_nov=0., L_on=1.))
        m.step(.25);m.apply_growth_rules()
        assert len(m)==1  # equality at L_on suppresses birth
    with static() as m:
        m.add(2,0);m.set_drives([Drive(1,0,0,0,0,1,1,2)])
        m.observe();m.observe();m.configure_growth(config(T_nov=0.))
        m.step(.25);m.apply_growth_rules()
        assert len(m)==2  # exactly reach is out of range

def strained(m):
    a=m.add(0,0)
    # Two opposing drives rotate together through the window: strain=1, lock=0.
    for phase in [0, math.pi/2, math.pi, 3*math.pi/2]:
        m.set_drives([Drive(10,0,0,phase,0,1,1,2),Drive(11,0,0,phase+math.pi,0,1,1,2)])
        m.observe()
    return a

def test_b2_strain_and_duration_threshold():
    with static(window=4, min_samples=4) as m:
        a=strained(m)
        close(m.measure(a).strain,1.);close(m.measure(a).lock,0.)
        m.configure_growth(config(S_split=1.,T_split=.5,L_on=1.))
        # Preserve complete phase cycles: 3 explicit samples + step's sample each period.
        for period in range(2):
            for phase in [0, math.pi/2, math.pi]:
                m.set_drives([Drive(10,0,0,phase,0,1,1,2),Drive(11,0,0,phase+math.pi,0,1,1,2)]);m.observe()
            m.set_drives([Drive(10,0,0,3*math.pi/2,0,1,1,2),Drive(11,0,0,5*math.pi/2,0,1,1,2)])
            m.step(.25);m.apply_growth_rules()
            if period==0:assert len(m)==1
        assert len(m)==2 and a not in [e.id for e in m.elements]
        assert m.events[-1]['rule']=='B2'
        close(math.hypot(m.elements[0].x-m.elements[1].x,m.elements[0].y-m.elements[1].y),.1)

def test_b2_below_strain_and_lock_boundary():
    with static(window=4) as m:
        a=m.add(0,0)
        m.set_drives([Drive(10,0,0,0,0,1,1,2),Drive(11,0,0,math.pi/2,0,1,1,2)])
        m.observe();m.observe()
        close(m.measure(a).strain,.5)
        m.configure_growth(config(S_split=.6,T_split=0.,L_on=1.))
        m.step(.25);m.apply_growth_rules();assert len(m)==1
    with static() as m:
        a=m.add(0,0);m.set_drives([Drive(10,0,0,0,0,1,1,2),Drive(11,0,0,math.pi,0,1,1,2)])
        m.observe();m.observe();m.configure_growth(config(S_split=1.,T_split=0.,L_on=1.))
        m.step(.25);m.apply_growth_rules();assert len(m)==1  # L==L_on blocks B2

@pytest.mark.parametrize('protection', [0., 1.5])
def test_d1_duration_and_protection(protection):
    with static() as m:
        m.add(0,0);m.observe();m.observe()
        m.configure_growth(config(T_death=1.,T_protect=protection))
        for _ in range(int(max(1.,protection)/.25)):
            m.step(.25);m.apply_growth_rules()
            if m.time<max(1.,protection):assert len(m)==1
        assert len(m)==0 and m.events[-1]['rule']=='D1'

def test_d1_at_lock_threshold_survives():
    with static(window=2) as m:
        a=m.add(0,0)
        # Two adjacent observed phase differences +/- pi/3 give lock .5 (within rounding).
        m.set_drives([Drive(1,0,0,-math.pi/3,0,1,1,2)]);m.observe()
        m.set_drives([Drive(1,0,0,math.pi/3,0,1,1,2)]);m.observe()
        lock=m.measure(a).lock
        m.configure_growth(config(L_off=lock,L_on=.9,T_death=0.))
        # A step replaces first sample: choose it again to preserve the threshold lock.
        m.set_drives([Drive(1,0,0,-math.pi/3,0,1,1,2)])
        m.set_element(a,0,0,0,-math.sin(-math.pi/3))
        m.step(.25);m.apply_growth_rules();assert len(m)==1
        close(m.measure(a).lock,lock,1e-15)

def test_d3_cost_boundary_rank_protection_and_death_order():
    with static() as m:
        a=m.add(0,0);b=m.add(1,0);c=m.add(10,0)
        m.observe();m.observe();m.configure_growth(config(C_max=3.))
        m.step(.25);m.apply_growth_rules();assert len(m)==3  # exactly budget
        m.configure_growth(config(C_max=2.))
        m.step(.25);m.apply_growth_rules()
        assert [e.id for e in m.elements]==[a,b] and m.events[-1]['ids']==[c]
        assert m.events[-1]['rule']=='D3'
    with static() as m:
        m.add(0,0);m.add(10,0);m.observe();m.observe()
        m.configure_growth(config(C_max=1.,T_protect=.5))
        m.step(.25);m.apply_growth_rules();assert len(m)==2
        m.step(.25);m.apply_growth_rules();assert len(m)==1
    with static() as m:
        m.add(10,0);m.observe();m.observe();m.set_drives([Drive(1,0,0,0,0,1,1,2)])
        m.configure_growth(config(T_death=.25,T_nov=.25,N_max=1))
        m.step(.25);m.apply_growth_rules()
        assert len(m)==1 and [e['rule'] for e in m.events[-2:]]==['D1','B1']

@pytest.mark.parametrize('error,expected', [(1.,False),(1.00001,True)])
def test_b3_strict_error_duration_cooldown(error,expected):
    with static() as m:
        m.set_needs([Need(1,0,0,.4,.7,error)])
        m.configure_growth(config(reward_arm=1,T_need=.5))
        m.step(.25);m.apply_growth_rules();assert len(m)==0
        m.step(.25);m.apply_growth_rules();assert bool(len(m))==expected
        m.step(.25);m.apply_growth_rules();assert len(m)==int(expected)
        m.step(.25);m.apply_growth_rules();assert len(m)==2*int(expected)

def test_d2_age_consecutive_fresh_evaluations_and_threshold():
    with static() as m:
        a=m.add(0,0);m.configure_growth(config(reward_arm=1))
        with pytest.raises(ValueError,match='age'):
            m.set_utility(a,0.)
        m.step(.25)
        with pytest.raises(ValueError,match='age'):
            m.set_utility(a,0.)
        m.step(.25);m.set_utility(a,.1);m.apply_growth_rules();assert len(m)==1 # equality survives
        m.step(.25);m.set_utility(a,0.);m.apply_growth_rules();assert len(m)==1
        m.step(.25);m.apply_growth_rules();assert len(m)==1 # stale result cannot count twice
        m.step(.25);m.set_utility(a,.1);m.apply_growth_rules();assert len(m)==1 # resets consecutive checks
        m.step(.25);m.set_utility(a,0.);m.apply_growth_rules();assert len(m)==1
        m.step(.25);m.set_utility(a,0.);m.apply_growth_rules();assert len(m)==0
        assert m.events[-1]['rule']=='D2'

def test_reward_d3_by_utility_and_stability_excludes_hooks():
    with static() as m:
        a=m.add(0,0);b=m.add(10,0)
        m.configure_growth(config(reward_arm=1,C_max=2.))
        m.step(.5);m.set_utility(a,.8);m.set_utility(b,-.2)
        m.configure_growth(config(reward_arm=1,C_max=1.))
        m.step(.25);m.apply_growth_rules()
        assert [e.id for e in m.elements]==[a]
    with static() as m:
        a=m.add(0,0);m.set_needs([Need(1,1,0,0,0,100)])
        m.configure_growth(config(T_need=0.,reward_arm=0))
        m.step(.5);m.set_utility(a,0.);m.apply_growth_rules()
        m.step(.25);m.set_utility(a,0.);m.apply_growth_rules()
        assert len(m)==1 and not any(e['rule'] in ('B3','D2') for e in m.events)

def test_growth_period_warmup_validation_and_cap():
    with static(min_samples=4) as m:
        m.add(0,0);m.configure_growth(config(T_death=0.))
        m.step(.125);m.apply_growth_rules();assert len(m)==1
        m.step(.125);m.apply_growth_rules();assert len(m)==1 # incomplete history protects inference
        m.step(.25);m.apply_growth_rules();assert len(m)==1
        m.step(.25);m.apply_growth_rules();assert len(m)==0
    with static() as m:
        m.set_drives([Drive(1,0,0,0,0,1,1,2),Drive(2,1,0,0,0,1,1,2)])
        m.configure_growth(config(T_nov=0.,N_max=1))
        m.step(.25);m.apply_growth_rules();assert len(m)==1
        with pytest.raises(ValueError,match='cap'):
            m.add(0,0)
        with pytest.raises(ValueError,match='cap'):
            m.split(m.elements[0].id,0,1,.1)
        assert len(m)==1
        with pytest.raises(ValueError):m.configure_growth(config(L_off=.8,L_on=.8))
    with pytest.raises(ValueError,match='Explicit'):
        Growth(L_on=.8)

@pytest.mark.parametrize('seed',[0,17,999])
def test_clone_save_load_determinism_and_identity(seed,tmp_path):
    with Medium(seed,Params(window=4)) as a:
        ids=[a.add(i*.3,0,i*.2,.02) for i in range(4)]
        a.set_drives([Drive(1,0,0,.3,.1,.7,1,3)])
        a.set_needs([Need(1,4,0,.8,.2,2)])
        a.configure_growth(config(reward_arm=1,T_protect=2.))
        a.step(.02,3)
        a.remove(ids[1])
        a.split(ids[2],0,math.pi,.1)
        snapshot=a.save(tmp_path/'state.bin')
        with a.clone() as b, Medium.load(snapshot) as c, Medium.load(tmp_path/'state.bin') as d:
            assert b.save()==c.save()==d.save()==snapshot
            for m in (a,b,c,d):
                m.step(.02,5);m.split(ids[0],.2,.8,.15)
            assert a.save()==b.save()==c.save()==d.save()
            old=a.save();b.remove(b.elements[0].id);assert a.save()==old
            assert sorted(e.id for e in a.elements)==[e.id for e in a.elements]
            assert all(e['time']<=a.time for e in a.events)
        for invalid in (snapshot[:-1],snapshot+b'x',b'',b'bad',b'\xff'*32):
            with pytest.raises(ValueError):Medium.load(invalid)

def test_silence_restore_evaluation_clone_and_cost():
    with Medium() as m:
        a=m.add(0,0,0);b=m.add(1,0,math.pi/2)
        m.set_drives([Drive(1,0,0,0,0,1,1,2)])
        assert m.cost(2,.5)=={'elements':2,'active_couplings':4,'total':6.}
        original=m.save()
        with m.evaluation_without(a) as branch:
            assert branch.rhs()[0]==[0.,0.,0.]
            assert branch.rhs()[1][0]==0.
            close(branch.readout(0,0,1,3),(1.,math.pi/2))
            branch.step(.02,4)
        assert m.save()==original
        with pytest.raises(RuntimeError):
            with m.silenced(a):
                assert m.elements[0].silent
                raise RuntimeError('evaluation failure')
        assert m.elements[0].silent==0 and m.save()==original
        m.configure_growth(config());m.silence(a)
        with pytest.raises(ValueError,match='restore'):m.apply_growth_rules()
        m.silence(a,False)

@pytest.mark.parametrize('kind',['params','drive','state','step','kernel'])
def test_nonfinite_and_invalid_inputs(kind):
    if kind=='params':
        with pytest.raises(ValueError):Medium(params=Params(eps=0))
        return
    with Medium() as m:
        a=m.add(0,0)
        if kind=='drive':
            with pytest.raises(ValueError):m.set_drives([Drive(1,0,0,0,0,1,0,2)])
            with pytest.raises(ValueError):m.set_drives([Drive(1,0,0,0,0,1,1,2)]*2)
        elif kind=='state':
            with pytest.raises(ValueError):m.set_element(a,float('nan'),0,0,0)
            with pytest.raises(ValueError):m.remove(999)
        elif kind=='step':
            with pytest.raises(ValueError):m.step(0)
        else:
            with pytest.raises(ValueError):m.readout(0,0,-1,2)

def test_long_synthetic_run_births_deaths_finite_capped():
    # Engine stress fixture, not a growth/task experiment. Deterministic adversarial
    # relocation repeatedly presents empty sites and leaves isolated old elements.
    def run():
        with Medium(2026,Params(window=4,min_samples=2)) as m:
            m.configure_growth(config(N_max=8,T_nov=.25,T_death=.5,T_protect=.5,C_max=5.,c_c=.01))
            for step in range(2000):
                site=(step//20)%11
                m.set_drives([Drive(1,site*10,0,.1*step,.2,.1,1,2)])
                m.step(.025);m.apply_growth_rules()
                assert len(m)<=8
                assert all(math.isfinite(v) for e in m.elements for v in (e.x,e.y,e.phase,e.rate))
            rules=[e['rule'] for e in m.events]
            assert rules.count('B1')>30 and rules.count('D1')>20
            return m.save()
    assert run()==run()

def test_cpp_contract():
    result=subprocess.run([str(ROOT/'_build'/'medium_contract')],capture_output=True,text=True,check=True)
    assert 'PASS' in result.stdout


def test_strain_extreme_weight_ratios_stay_finite():
    with static(window=2) as m:
        a=m.add(0,0)
        m.set_drives([Drive(1,0,0,0,0,1e200,1,2),Drive(2,0,0,math.pi,0,1e-200,1,2)])
        m.observe();m.observe()
        assert math.isfinite(m.measure(a).strain)
        assert 0 <= m.measure(a).strain <= 1


def test_b2_below_strain_with_unlocked_rotating_targets():
    with static(window=4,min_samples=4) as m:
        a=m.add(0,0)
        for phase in [0,math.pi/2,math.pi,3*math.pi/2]:
            m.set_drives([Drive(1,0,0,phase,0,1,1,2),Drive(2,0,0,phase+math.pi/2,0,1,1,2)])
            m.observe()
        close(m.measure(a).strain,.5)
        close(m.measure(a).lock,0.)
        m.configure_growth(config(S_split=.6,T_split=0.,L_on=1.))
        # Keep the four-phase history complete through the next integration sample.
        for phase in [0,math.pi/2,math.pi]:
            m.set_drives([Drive(1,0,0,phase,0,1,1,2),Drive(2,0,0,phase+math.pi/2,0,1,1,2)])
            m.observe()
        m.set_drives([Drive(1,0,0,3*math.pi/2,0,1,1,2),Drive(2,0,0,2*math.pi,0,1,1,2)])
        m.step(.25);m.apply_growth_rules()
        assert len(m)==1 and m.measure(a).lock<1
        close(m.measure(a).strain,.5)


def test_novelty_interruption_restarts_timer():
    with static() as m:
        drive=Drive(1,0,0,0,0,1,1,2)
        m.set_drives([drive]);m.configure_growth(config(T_nov=.5))
        m.step(.25);m.apply_growth_rules();assert len(m)==0
        m.set_drives([]);m.step(.25);m.apply_growth_rules();assert len(m)==0
        m.set_drives([drive]);m.step(.25);m.apply_growth_rules();assert len(m)==0
        m.step(.25);m.apply_growth_rules();assert len(m)==0
        m.step(.25);m.apply_growth_rules();assert len(m)==1
