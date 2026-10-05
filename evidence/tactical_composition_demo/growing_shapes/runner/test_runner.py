"""Synthetic rule contracts only. Integration smoke is a separate bounded call."""
from collections import defaultdict, deque
from copy import deepcopy
import math
from types import SimpleNamespace
import numpy as np
import pytest
from geomind import c4_detect as c4
from evidence.tactical_composition_demo.growing_shapes.medium.medium import Drive, Params
from evidence.tactical_composition_demo.growing_shapes.medium.design_0h import DesignMedium, Frame
from evidence.tactical_composition_demo.growing_shapes.runner import protocol as p, qualification as q
from evidence.tactical_composition_demo.growing_shapes.runner.evaluator import copy_template, Evaluator
from evidence.tactical_composition_demo.growing_shapes.runner.control import ControlQueue
from evidence.tactical_composition_demo.growing_shapes.runner.run import Run, smoke


def observation(task='perceive'):
    enemies = [SimpleNamespace(id=i, visible=True, angle=.1*i, distance=1.+i, hp=50.) for i in reversed(range(3))]
    return SimpleNamespace(enemies=enemies, enemy_count=3, target_distance=1., desired_range=2., target_angle=.4)


@pytest.fixture
def medium():
    m = DesignMedium()
    yield m
    m.close()


@pytest.mark.parametrize('task', p.TASKS)
def test_slot_binding_permutation_every_task(task):
    obs = observation(task)
    if task == 'remember_static':
        obs.enemies = obs.enemies[-1:]
        obs.enemy_count = 1
    assignment = p.permutation(15)
    assert sorted(assignment) == list(range(8)) and assignment == p.permutation(15)
    assert assignment != p.permutation(16)
    ds = p.bindings(task, obs, assignment, 16)
    for j in range(1 if task in ('move', 'remember_static') else 3):
        assert ds[assignment[j]].strength > 0
    assert all(d.strength == 0 for d in ds if d.id not in assignment[:1 if task in ('move', 'remember_static') else 3])
    if task == 'move':
        assert ds[assignment[0]].phase == pytest.approx(16*math.pi+.4+math.pi)
        assert ds[assignment[0]].strength == 1
    else:
        assert ds[assignment[0]].phase == pytest.approx(16*math.pi)  # lowest world id
        expected = 2*math.exp(-.1)*(1.5 if task == 'choose' else 1)
        assert ds[assignment[0]].strength == pytest.approx(expected)


@pytest.mark.parametrize('distance,range_,sign,strength', [(2, 2, 0, 0), (3, 2, 0, 1), (0, 2, math.pi, 2)])
def test_move_binding_strength_precedence(distance, range_, sign, strength):
    obs = observation('move')
    obs.target_distance, obs.desired_range = distance, range_
    d = p.bindings('move', obs, tuple(range(8)), 0)[0]
    assert d.phase == pytest.approx(.4+sign) and d.strength == strength


def test_hidden_memory_unused_sites_zero():
    obs = observation()
    obs.enemies = [obs.enemies[0]]
    obs.enemy_count = 1
    obs.enemies[0].visible = False
    assert all(d.strength == 0 for d in p.bindings('remember_static', obs, p.permutation(7), 16))


@pytest.mark.parametrize('task', p.TASKS)
def test_action_table_abstention_and_nonchoice_id(task):
    class Native:
        def readout(self, *_):
            return .04, 1.
    obs = observation()
    a = p.action(task, obs, Native(), 16)
    assert a.angle == a.magnitude == 0
    assert a.choice == (0 if task == 'choose' else -1)


@pytest.mark.parametrize('task,magnitude', [('perceive', 10*math.log(2)), ('move', .625), ('remember_static', 0)])
def test_action_decode_uses_continuous_carrier(task, magnitude):
    class Native:
        def readout(self, *_):
            return .5, math.pi+.4
    a = p.action(task, observation(), Native(), 1.)
    assert a.angle == pytest.approx(.4)
    assert a.magnitude == pytest.approx(magnitude) and a.choice == -1


def test_choose_nearest_angle_ties_lowest_id():
    class Native:
        def readout(self, *_):
            return 1., .15
    obs = observation()
    obs.enemies[0].angle = .25
    obs.enemies[1].angle = .05
    obs.enemies[2].angle = 2
    assert p.action('choose', obs, Native(), 0).choice == 1


@pytest.mark.parametrize('episode,expected', [(0,'perceive'), (19,'perceive'), (20,'move'), (40,'remember_static'), (60,'choose'), (80,'perceive')])
def test_rotation_exact_blocks(episode, expected):
    assert p.rotation(episode, p.TASKS) == expected


def test_rotation_filtered_and_empty_invalid():
    assert p.rotation(20, ['perceive', 'choose']) == 'choose'
    with pytest.raises(ValueError, match='INVALID'):
        p.rotation(0, [])


def test_calibration_paired_se_and_unclipped_normalized_score():
    random = np.linspace(0, 1, 256)
    ref = random+1
    c = p.calibration('choose', ref, random)
    assert c.usable and c.se == pytest.approx(0, abs=1e-15)
    assert c.normalize(c.reference+1) == pytest.approx(2)
    assert c.normalize(c.random-1) == pytest.approx(-1)
    difference = np.r_[np.full(128,-1.),np.full(128,1.1)]
    c = p.calibration('choose', random+difference, random)
    assert c.difference > 0 and not c.usable
    assert c.se == pytest.approx(difference.std(ddof=1)/16)
    with pytest.raises(ValueError):
        p.calibration('choose', [1], [0])
    with pytest.raises(ValueError):
        p.calibration('choose', np.full(256,np.nan), random)


def test_template_canonical_hash_order_binding_identity_and_isolation(medium):
    a = medium.add((0, 0), .4, math.pi, .3)
    b = medium.add((1, 0), math.pi, math.pi, .7)
    value = p.template(medium.native, [b,a], 0.)
    assert value['members'][0][0] == 0
    reordered = {k: value[k] for k in reversed(list(value))}
    assert p.template_hash(value) == p.template_hash(reordered)
    assert value['binding'] == p.BINDING
    altered = deepcopy(value)
    altered['binding']['physical_sites'] = 9
    assert p.template_hash(value) != p.template_hash(altered)
    altered = deepcopy(value)
    altered['members'][0][4] += .1
    assert p.template_hash(value) != p.template_hash(altered)
    state = medium.native.save()
    first, second = copy_template(value), copy_template(value, math.pi)
    try:
        assert first.time == 0 and second.time == 1
        assert second.native.time == 1
        for ea, eb in zip(first.native.elements, second.native.elements):
            assert (ea.x,ea.y,ea.rate) == (eb.x,eb.y,eb.rate)
            assert eb.phase-ea.phase == pytest.approx(math.pi)
        first.native.remove(0)
        assert len(second.native) == 2 and medium.native.save() == state
    finally:
        first.close(); second.close()


def test_copy_covariance_zero_resultant_and_driven_dynamics():
    value = {'members': [[0.,0.,0.,math.pi,1.], [0.,0.,math.pi,math.pi,.5]],
             'binding': p.BINDING, 'constants_version': p.VERSION}
    a, b = copy_template(value), copy_template(value, math.pi)
    try:
        assert a.native.readout(0,0,1,2)[0] < .05
        for _ in range(10):
            obs = observation()
            a.integrate(p.bindings('perceive', obs, p.permutation(5), a.time))
            b.integrate(p.bindings('perceive', obs, p.permutation(5), b.time))
        for ea, eb in zip(a.native.elements,b.native.elements):
            assert (ea.x,ea.y) == pytest.approx((eb.x,eb.y), abs=1e-10)
            assert float(p.wrap(eb.phase-ea.phase-math.pi)) == pytest.approx(0,abs=1e-10)
    finally:
        a.close();b.close()


def synthetic_frames(m, entrant=False):
    x = [(0.,0.), (1/1.8,0.), (1/3.6,math.sqrt(3)/3.6)]
    ids = [m.add(point, 60*math.pi) for point in x]
    extra = m.add((1.5,0), 60*math.pi) if entrant else None
    if entrant:
        m.birth_steps[extra] = 590
    m.frames.clear()
    for k in range(601):
        elements = {id: (*point,k*.1*math.pi) for id, point in zip(ids,x)}
        if entrant and k >= 590:
            elements[extra] = (1.5,0.,k*.1*math.pi)
        m.frames.append(Frame(k,k*.1,elements,{}, {id: () for id in elements}))
    m.step_index = 600
    return ids, extra


def test_601_cohort_scaled_frozen_functions_and_full_recovery_state(medium):
    ids, entrant = synthetic_frames(medium, entrant=True)
    check = q.start(medium)
    assert check['cohort'] == ids and entrant not in check['cohort']
    assert len(check['candidates']) == 1
    assert q.THRESHOLDS['freq_tol'] == .005
    assert check['candidates'][0]['stats']['freq_change'] == pytest.approx(0,abs=1e-12)
    original = medium.native.save()
    recorded = [[Drive(0,4,0,math.pi*(60+k*.1),math.pi,1,1,3)] for k in range(600)]
    admitted, exposure = q.finish(medium, check, recorded, np.random.default_rng(5))
    assert exposure == 120
    assert medium.native.save() == original and len(medium.native) == 4
    stats = check['candidates'][0]['stats']
    assert all(k in stats for k in ('recovery_original_to_control','recovery_original_to_kicked','recovery_control_to_kicked'))
    assert 'tau_phase_censored' in stats and stats['tau_phase'] <= 60
    assert set(check['candidates'][0]['criteria']) == set(c4.criteria_checks(stats,q.THRESHOLDS))
    assert all(len(c['ids']) == 3 for c in admitted)


def test_first_endpoint_small_cohort_missing_frame_invalid(medium):
    assert medium.frames[0].index == 0
    with pytest.raises(ValueError, match='601'):
        q.start(medium)
    medium.frames.clear()
    medium.frames.extend(Frame(k,k*.1,{}, {}, {}) for k in range(601))
    medium.step_index = 600
    assert q.start(medium)['reason'] == 'small_cohort'
    medium.frames[1] = Frame(3,.3,{}, {}, {})
    with pytest.raises(ValueError, match='consecutive'):
        q.start(medium)


def test_revision2_aliasing_counterexample_is_negative_contract():
    omega = np.array([.5*math.pi,1.5*math.pi])
    coarse = np.arange(31)[:,None]*2*omega
    fine = np.arange(601)[:,None]*.1*omega
    assert c4.locked_pairs(coarse,.1)[0,1]
    assert not c4.locked_pairs(fine,.1)[0,1]
    # Warning screen cannot see full turns, and is explicitly not a certificate.
    assert q.alias_increment(coarse,[0,1]) < 1e-12
    fast = np.arange(601)[:,None]*np.array([0.,2.,4.])
    assert q.alias_increment(fast,[0,1,2]) > math.pi/2


def test_alias_flag_prevents_recovery_and_admission(medium):
    check = {'possibly_aliased': True, 'candidates': [{'ids':[0,1,2]}]}
    assert q.finish(medium,check,[[]]*600,np.random.default_rng(0)) == ([],0.)
    with pytest.raises(ValueError, match='full next'):
        q.finish(medium,check,[[]],np.random.default_rng(0))


def test_degenerate_hull_and_zero_spacing_rejected():
    assert q.degenerate(np.array([[[0.,0.],[1.,0.],[2.,0.]]]))
    assert q.degenerate(np.array([[[0.,0.],[0.,0.],[1.,1.]]]))
    assert not q.degenerate(np.array([[[0.,0.],[1.,0.],[0.,1.]]]))


def test_reward_arm_single_term_baseline_carried_and_empty_eligibility(medium):
    ids = [medium.add((i,0),0,gain=1.9) for i in range(2)]
    run = object.__new__(Run)
    run.medium, run.reward, run.rbar = medium, True, .5
    run.rows = {'choose': p.calibration('choose',np.ones(256),np.zeros(256))}
    run.exposure = {'reward_episodes':0}
    signals = defaultdict(list,{ids[0]: [1.,1.]})
    run.reward_update('choose',2.,signals)
    assert medium.native.gain(ids[0]) == 2. and medium.native.gain(ids[1]) == 1.9
    assert run.rbar == .55
    run.reward_update('choose',-1.,signals)
    assert medium.native.gain(ids[0]) == pytest.approx(2-.5*.55)
    assert run.rbar == pytest.approx(.495)
    assert run.exposure['reward_episodes'] == 2
    state = medium.native.save()
    run.reward = False
    run.reward_update('choose',100.,signals)
    assert medium.native.save() == state and run.rbar == pytest.approx(.495)


def test_control_queue_fifo_two_attempts_retry_later_redraw_and_terminal(medium, monkeypatch):
    queue = ControlQueue(17)
    monkeypatch.setattr(medium, 'feasible', lambda *_: 'cost')
    queue.check(medium,[10,11,12])
    assert len(queue.queue) == 3 and queue.queue[0]['attempts'] == 1
    queue.check(medium,[])
    assert queue.queue[0]['attempts'] == 1  # retry cannot occur at same check
    medium.step_index = 200
    queue.check(medium,[])
    assert queue.drops == 1 and queue.retries == 1 and queue.queue[0]['source_id'] == 11
    attempts = [e for e in medium.events if e['rule'] == 'control_attempt']
    assert attempts[0]['values']['position'] != attempts[1]['values']['position']
    assert len([e for e in attempts if e['time'] == 20]) == 2
    queue.terminal(medium)
    assert not queue.queue and queue.drops == 3
    assert medium.events[-1]['values']['reason'] == 'terminal'


def test_control_success_two_per_check_own_entropy_and_protection(medium):
    queue = ControlQueue(17)
    queue.check(medium,[1,2,3])
    assert queue.additions == 2 and len(queue.queue) == 1
    positions = [(e.x,e.y) for e in medium.native.elements]
    assert all(math.hypot(*x) <= 5 for x in positions)
    assert all(e.rate == math.pi and medium.native.gain(e.id) == 1 for e in medium.native.elements)
    assert p.entropy(17,'g0_control') != p.entropy(17,'initial')
    medium.death = {e.id:40 for e in medium.native.elements}
    medium.step_index = 199
    medium.growth(False)
    assert len(medium.native) == 2  # protected


def seed(**changes):
    s = dict(complete=True, usable=p.TASKS, eligible=1, invalid=None,
             coverage=1.,control_coverage=0.,competence=1.,control_competence=0.,
             slope=0.,rejected=False,protected_over_budget=False,snapshots=1,g5=[0.],dropped=0)
    s.update(changes)
    return s


def test_invalid_first_every_readout_and_dropped_nonpass():
    assert set(p.readouts([seed() for _ in range(8)]).values()) == {'PASS','DESCRIPTIVE'}
    for change in ({'invalid':'execution'}, {'eligible':0}, {'complete':False}, {'usable':[]}, {'coverage':float('nan')}, {'g5':[float('inf')]}):
        rows = [seed() for _ in range(8)]
        rows[0].update(change)
        assert set(p.readouts(rows).values()) == {'INVALID'}
    assert set(p.readouts([seed()]*7).values()) == {'INVALID'}
    rows = [seed(dropped=1) for _ in range(3)]+[seed() for _ in range(5)]
    assert p.readouts(rows)['G0'] == 'INCONCLUSIVE'


@pytest.mark.parametrize('bearing,g5,expected', [(5,[0.],'INCONCLUSIVE'),(6,[0.],'PASS'),(8,[.2],'FAIL'),(6,[0.,0.,.2],'INCONCLUSIVE')])
def test_g5_ordered_cuts_and_no_formation(bearing,g5,expected):
    rows = [seed(g5=g5,snapshots=len(g5)) for _ in range(bearing)]+[seed(snapshots=0,g5=[]) for _ in range(8-bearing)]
    assert p.readouts(rows)['G5'] == expected


@pytest.mark.parametrize('bearing,expected', [(2,'FAIL'),(3,'INCONCLUSIVE'),(5,'INCONCLUSIVE'),(6,'PASS')])
def test_g1_cuts(bearing,expected):
    rows = [seed() for _ in range(bearing)]+[seed(snapshots=0,g5=[]) for _ in range(8-bearing)]
    assert p.readouts(rows)['G1'] == expected


@pytest.mark.parametrize('slope,rejected,protected,expected', [(.5,False,False,'PASS'),(-.5,False,False,'PASS'),(.5001,False,False,'FAIL'),(0,True,False,'FAIL'),(0,False,True,'FAIL')])
def test_g0prime_cuts(slope,rejected,protected,expected):
    assert p.readouts([seed(slope=slope,rejected=rejected,protected_over_budget=protected)]*8)["G0'"] == expected


def test_g0_both_conditions_and_covariance_measurement():
    assert p.readouts([seed(coverage=0.,competence=0.)]*8)['G0'] == 'FAIL'
    assert p.readouts([seed(coverage=0.)]*8)['G0'] == 'INCONCLUSIVE'
    assert p.covariance({'a':1,'b':2},{'a':1.05,'b':1.8}) == pytest.approx(.2)
    with pytest.raises(ValueError):
        p.covariance({}, {})


def test_smoke_hard_cap_before_loading_native_world():
    with pytest.raises(ValueError,match='ten'):
        smoke(1,{},11)


def test_evaluator_fresh_128_copies_each_episode_both_offsets(monkeypatch):
    import evidence.tactical_composition_demo.growing_shapes.runner.evaluator as module
    copies = []
    class Native:
        def readout(self,*_):
            return 0.,0.
    class Copy:
        native = Native()
        time = 0.
        def integrate(self,*_):
            self.time += .1
        def close(self):
            pass
    class World:
        def __init__(self,task,episode,namespace,**_):
            assert namespace == 'validation' and episode < 128
            self.steps = 0
        def __enter__(self): return self
        def __exit__(self,*_): pass
        def observe(self):
            obs = observation()
            obs.done = self.steps == 2
            return obs
        def step(self,a):
            assert a.choice == -1 and a.magnitude == 0  # empty readout scored
            self.steps += 1
        def score(self): return SimpleNamespace(angular_error=1.)
    def copier(value,offset):
        copy = Copy()
        copies.append(copy)
        return copy
    monkeypatch.setattr(module,'World',World)
    monkeypatch.setattr(module,'copy_template',copier)
    rows = {t:p.calibration(t,np.ones(256),np.zeros(256)) for t in p.TASKS}
    for t in p.TASKS[1:]:
        rows[t] = p.calibration(t,np.zeros(256),np.zeros(256))
    evaluator = Evaluator(rows, library=object())
    value = {'members':[],'binding':p.BINDING,'constants_version':p.VERSION}
    assert evaluator.evaluate(value) == {'perceive':-1.}
    evaluator.evaluate(value,math.pi)
    assert len(copies) == len({id(c) for c in copies}) == 256
    assert evaluator.episodes == evaluator.copies == 256
    assert [i['instance_id'] for i in evaluator.instances] == list(range(256))


def test_qualification_schedule_last_check():
    # Contract arithmetic: no check may outlive the fixed 32000 s run.
    checks = [k*.1 for k in range(600,2000*160+1,600) if k+600 <= 2000*160]
    assert len(checks) == 532 and checks[-1] == 31920
    assert checks[-1]+60 == 31980


def test_snapshot_ranking_largest_then_minimum_persistent_id(monkeypatch,medium):
    # Exercise admission orchestration without executing recovery futures.
    def candidate(ids):
        return {'ids':ids,'template':{'members':[[float(i),0.,0.,math.pi,1.] for i in ids],
            'binding':p.BINDING,'constants_version':p.VERSION},'stats':{}}
    candidates = q.snapshot_order([candidate([8,9,10]),candidate([4,5,6,7]),candidate([0,1,2]),candidate([20,21,22])])
    assert [c['ids'] for c in candidates] == [[4,5,6,7],[0,1,2],[8,9,10]]
    monkeypatch.setattr(q,'finish',lambda *_:(candidates,360.))
    run = object.__new__(Run)
    run.medium,run.seed,run.snapshots,run.group_hashes = medium, 0, [],defaultdict(set)
    run.pending = [{'saved':medium.clone(),'check':{'candidates':candidates},'state':'immutable','index':600,'schedule':[[]]*600}]
    run.timing = {'recovery':0.}
    run.exposure = {'recovery_simulated_seconds':0.}
    medium.step_index = 1200
    Run.admissions(run)
    assert len(run.snapshots) == 3
    assert all(s['check_time'] == 60 and s['admission_time'] == 120 for s in run.snapshots)
    assert run.exposure['recovery_simulated_seconds'] == 360
    # Same live-member/hash combination is suppressed; changed content admitted.
    run.pending = [{'saved':medium.clone(),'check':{'candidates':candidates},'state':'immutable','index':1200,'schedule':[[]]*600}]
    Run.admissions(run)
    assert len(run.snapshots) == 3
    candidates[0]['template']['members'][0][4] = .9
    run.pending = [{'saved':medium.clone(),'check':{'candidates':candidates},'state':'immutable','index':1800,'schedule':[[]]*600}]
    Run.admissions(run)
    assert len(run.snapshots) == 4


def test_evaluation_cap_first_twenty_all_snapshots_retained(monkeypatch,medium):
    import evidence.tactical_composition_demo.growing_shapes.runner.run as module
    seen = []
    class Evaluator:
        episodes = 0
        instances = []
        def __init__(self,*_): pass
        def evaluate(self,value,offset=0.):
            seen.append((value['marker'] if 'marker' in value else 'whole',offset))
            return {'perceive':0.}
    monkeypatch.setattr(module,'Evaluator',Evaluator)
    run = object.__new__(Run)
    run.medium,run.rows,run.library,run.evaluations = medium,{},object(),[]
    run.timing,run.exposure = {'evaluation':0.},{}
    run.snapshots = [{'type_id':str(i),'template':{'marker':i}} for i in range(25)]
    run.evaluate()
    assert len(run.snapshots) == 25 and len(run.evaluations) == 20
    assert seen == [(i,offset) for i in range(20) for offset in (0.,math.pi)]+[('whole',0.)]


def test_copy_rejects_changed_binding_rule():
    with pytest.raises(ValueError,match='binding'):
        copy_template({'members':[], 'binding':{},'constants_version':p.VERSION})


def test_complete_clock_and_no_reset_between_episodes_without_world_run(monkeypatch):
    import evidence.tactical_composition_demo.growing_shapes.runner.run as module
    class World:
        def __init__(self,*args,**kwargs): self.steps = 0
        def __enter__(self): return self
        def __exit__(self,*_): pass
        def observe(self):
            obs = observation()
            obs.done = self.steps == 160
            return obs
        def step(self,a): self.steps += 1
        def score(self): return SimpleNamespace(angular_error=1.)
    monkeypatch.setattr(module,'World',World)
    rows = {t:p.calibration(t,np.ones(256),np.zeros(256)) for t in p.TASKS}
    run = Run(7,rows,episodes=2,library=object())
    try:
        run.episode(0)
        assert run.medium.time == 16
        first_id_set = {e.id for e in run.medium.native.elements}
        first = run.medium.frames[-1]
        run.rbar = .61
        run.episode(1)
        assert run.medium.time == 32 and run.medium.step_index == 320
        assert run.rbar == .61 and first in run.medium.frames
        assert first_id_set.intersection(e.id for e in run.medium.native.elements)
        assert run.exposure['training_steps'] == 320 and run.exposure['reward_episodes'] == 0
        report = run.report()
        assert report['final_type_id'] == p.template_hash(report['final_template'])
        assert len(report['final_template']['members']) == len(run.medium.native)
        assert [e['values']['assignment'] for e in run.medium.events if e['rule'] == 'episode_start'] == [p.permutation(0),p.permutation(1)]
    finally:
        run.close()


def test_reward_lower_clip_and_invalid_before_g5_no_formation(medium):
    id = medium.add((0,0),0,gain=.01)
    run = object.__new__(Run)
    run.medium,run.reward,run.rbar = medium,True,.9
    run.rows = {'choose':p.calibration('choose',np.ones(256),np.zeros(256))}
    run.exposure = {'reward_episodes':0}
    run.reward_update('choose',0.,defaultdict(list,{id:[1.]}))
    assert medium.native.gain(id) == 0
    rows = [seed(g5=[]) for _ in range(5)]+[seed(snapshots=0,g5=[]) for _ in range(3)]
    assert p.readouts(rows)['G5'] == 'INVALID'  # missing measurements precede no-formation cut


def test_cohort_missing_frame_and_nonfinite_history_invalid(medium):
    ids,_ = synthetic_frames(medium)
    f = medium.frames[1]
    elements = dict(f.elements)
    elements.pop(ids[0])
    medium.frames[1] = Frame(f.index,f.time,elements,f.sites,f.neighbors)
    with pytest.raises(ValueError,match='missing frame'):
        q.start(medium)
    medium.frames[1] = f
    elements = dict(f.elements)
    elements[ids[0]] = (float('nan'),0.,f.elements[ids[0]][2])
    medium.frames[1] = Frame(f.index,f.time,elements,f.sites,f.neighbors)
    with pytest.raises(ValueError,match='non-finite'):
        q.start(medium)


def test_interrupted_development_keeps_partial_raw_evidence_and_invalid(monkeypatch,tmp_path):
    import evidence.tactical_composition_demo.growing_shapes.runner.development as module
    calls = []
    class Run:
        def __init__(self,seed,rows,reward,control=False,library=None,**_):
            self.invalid = None
            self.library = object()
            self.control = control
        def episode(self,episode,*_):
            calls.append((self.control,episode))
            if self.control: raise KeyboardInterrupt('synthetic stop')
        def evaluate(self): raise AssertionError('interrupted run cannot evaluate')
        def report(self): return {'invalid':self.invalid,'raw':['kept']}
        def close(self): pass
    monkeypatch.setattr(module,'Run',Run)
    monkeypatch.setattr(module,'seed_unit',lambda a,b:seed(invalid=a.invalid,complete=False))
    result = module.execute_arm(list(range(8)),{'perceive':SimpleNamespace(usable=True)},audit_root=tmp_path)
    assert len(result['runs']) == 1 and result['runs'][0]['intact']['raw'] == ['kept']
    assert set(result['readouts'].values()) == {'INVALID'}
    assert calls == [(False,0),(True,0)]


def test_report_keeps_pending_check_state_without_recovery_execution():
    rows = {t:p.calibration(t,np.ones(256),np.zeros(256)) for t in p.TASKS}
    run = Run(7,rows,episodes=8,library=object())
    try:
        check = {'candidates':[]}
        run.pending = [{'saved':run.medium.clone(),'check':check,'state':{'native':'immutable'},
                        'index':600,'schedule':[[]]*10}]
        run.invalid = 'interrupted'
        report = run.report()
        assert report['pending_qualification'] == [{'check_time':60.,'state':{'native':'immutable'},
                                                   'recorded_future_steps':10,'candidates':[]}]
        assert report['final_type_id'] == p.template_hash(report['final_template'])
    finally:
        run.close()
