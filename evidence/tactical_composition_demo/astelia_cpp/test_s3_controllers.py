"""S3 equations against independent arithmetic and S2/S3 admission boundaries."""
import json
import math
import pathlib
import subprocess
import sys
import numpy as np
import pytest
from s3_runner import request
ROOT = pathlib.Path(__file__).resolve().parent


@pytest.fixture(scope='module')
def s3_build():
    for target in ('native', 's3-check'):
        run = subprocess.run([sys.executable, str(ROOT/'build.py'), '--engine', target], capture_output=True)
        assert run.returncode == 0, run.stderr.decode()
    return ROOT/'build/native_s3_contract'


def evaluate(binary, req):
    return json.loads(subprocess.check_output([str(binary), '--equations'], input=json.dumps(req)+'\n', text=True))


def test_native_s3_contracts(s3_build):
    out = subprocess.check_output([str(s3_build)], text=True)
    assert json.loads(out)['status'] == 'passed'


def test_c4_all_stored_rhs_and_coupled_steps(s3_build):
    cases = json.loads((ROOT.parent/'c4_reference/c4_reference_states.json').read_text())['cases']
    for case in cases:
        for name, variant in case['variants'].items():
            params = variant['params']
            units = [dict(id=i+1, target=0, x=x[0], y=x[1], state=th, rate=om, pressure=0)
                     for i, (x, th, om) in enumerate(zip(case['x'], case['th'], case['omega']))]
            req = dict(operation='reference', units=units, dt=case['dt'], K=params['K'], J=params['J'], eps=params['eps'])
            actual = evaluate(s3_build, req)
            expected = np.column_stack((variant['x_dot'], variant['th_dot']))
            assert np.max(np.abs(np.array(actual['rhs'])-expected)) < 1e-9, (case['name'], name, 'rhs')
            frozen_rhs = evaluate(s3_build, dict(operation='frozen', arm='resonator', units=units, dt=case['dt'], K=params['K'], K_t=0))
            assert np.max(np.abs(np.array(frozen_rhs['rhs'])-variant['th_dot'])) < 1e-9
            expected = np.column_stack((variant['x_after_step'], variant['th_after_step']))
            assert np.max(np.abs(np.array(actual['step'])-expected)) < 1e-9, (case['name'], name, 'step')


def independent_rhs(units, state, arm, K, Kt):
    answer = []
    for i, u in enumerate(units):
        near = sorted((j for j in range(len(units)) if j != i),
                      key=lambda j: (math.hypot(units[j]['x']-u['x'], units[j]['y']-u['y']), units[j]['id']))[:8]
        near = [j for j in near if math.hypot(units[j]['x']-u['x'], units[j]['y']-u['y']) < 3]
        group = [state[j] for j, v in enumerate(units) if j != i and u['target'] and v['target'] == u['target']]
        torque = 0
        if group:
            if arm == 'resonator':
                z = sum(complex(math.cos(x), math.sin(x)) for x in group)
                if abs(z) >= .1*len(group):
                    torque = Kt*math.sin(math.atan2(z.imag, z.real)-state[i])
            else:
                torque = Kt*(sum(group)/len(group)-state[i])
        value = (u['rate']+u['pressure']*math.sin(state[i]) if arm == 'resonator'
                 else -u['rate']*state[i]-u['pressure']) + torque
        for j in near:
            r = math.hypot(units[j]['x']-u['x'], units[j]['y']-u['y'])
            diff = state[j]-state[i]
            value += K*math.exp(-r*r)*(math.sin(diff) if arm == 'resonator' else diff)/len(near)
        answer.append(value)
    return np.array(answer)


@pytest.mark.parametrize('arm', ['resonator', 'morale'])
def test_frozen_production_step_nonzero_rates_pressure_and_group(s3_build, arm):
    units = [dict(id=i+1, target=8 if i < 3 else 0, x=i*.45, y=(i%2)*.3,
                  state=s, rate=.7 if i%2 else -.2 if arm == 'resonator' else .2,
                  pressure=(i-2)*.1) for i, s in enumerate([.4, -.7, .9, -.2])]
    dt = 1/30
    state = np.array([u['state'] for u in units])
    f = lambda s: independent_rhs(units, s, arm, 2.3, 1.7)
    k1 = f(state); k2 = f(state+dt*k1/2); k3 = f(state+dt*k2/2); k4 = f(state+dt*k3)
    step = state + dt*(k1+2*k2+2*k3+k4)/6
    if arm == 'morale':
        step = np.clip(step, -1, 1)
    actual = evaluate(s3_build, dict(operation='frozen', arm=arm, units=units, dt=dt, K=2.3, K_t=1.7))
    assert np.max(np.abs(actual['rhs']-k1)) < 1e-12
    assert np.max(np.abs(actual['step']-step)) < 1e-12


@pytest.mark.parametrize('arm,params', [('resonator', {'K': -1}), ('morale', {'omega_melee': 0}),
    ('pushpull', {'gamma': 1}), ('resonator', {'f': 1.3}), ('morale', {'lambda_melee': 3}),
    ('resonator', {'K': True}), ('pushpull', {'G': '1'}), ('resonator', {'other': 0})])
def test_native_param_rejection(s3_build, arm, params):
    req = request(dict(arm=arm, params=params))
    row = json.loads(subprocess.check_output([str(ROOT/'build/astelia_native')], input=json.dumps(req)+'\n', text=True))
    assert 'error' in row


@pytest.mark.parametrize('spec', [dict(arm='passthrough'), dict(arm='nearest', duration=1),
    dict(arm='nearest', controlledSide=True), dict(arm='nearest', swapSides=1), dict(arm='nearest', seed=True)])
def test_s3_runner_rejects_nonfixed_world(spec):
    with pytest.raises(ValueError):
        request(spec)


def test_passthrough_refused_by_production_host(s3_build):
    req = {'mode': 'alone', 'options': {'rules': 'game', 'scenario': 'mirror', 'duration': .1,
                                     'ai': [{'controller': 'passthrough'}, {}]}}
    row = json.loads(subprocess.check_output([str(ROOT/'build/astelia_native')], input=json.dumps(req)+'\n', text=True))
    assert row == {'error': 'passthrough is test-only'}


def test_fixed_world_either_controlled_side():
    for side in (0, 1):
        r = request(dict(arm='morale', controlledSide=side, opponent='wedge'))
        assert r['options']['ai'][side] == {'controller': 'morale', 'params': {}}
        assert r['options']['rules'] == 'game' and r['options']['duration'] == 150
        assert not r['options']['sandboxAbilities'] and not r['options']['perception']


def test_refinement_clips_only_at_game_tick_end(s3_build):
    units = [dict(id=i+1, target=9, x=i*.2, y=0, state=s, rate=1, pressure=p)
             for i, (s, p) in enumerate([(0.98, -40), (-0.9, 1), (0.1, -2)])]
    state = np.array([u['state'] for u in units])
    h = 1/60
    f = lambda s: independent_rhs(units, s, 'morale', 2.5, 2.5)
    for _ in range(2):
        k1 = f(state); k2 = f(state+h*k1/2); k3 = f(state+h*k2/2); k4 = f(state+h*k3)
        state = state+h*(k1+2*k2+2*k3+k4)/6
    expected = np.clip(state, -1, 1)
    actual = evaluate(s3_build, dict(operation='frozen', arm='morale', units=units,
                                   dt=1/30, K=2.5, K_t=2.5, substeps=2))
    assert np.max(np.abs(actual['step']-expected)) < 1e-12
