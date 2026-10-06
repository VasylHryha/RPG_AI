"""Fixed-world S3 engineering/controller entry point. Never enables passthrough."""
import argparse
import json
import math
import pathlib
import subprocess
from build_admission import admit
ROOT = pathlib.Path(__file__).resolve().parent
POOL = ['line', 'wide line', 'wedge', 'box', 'column', 'loose', 'screen',
        'crescent', 'ring', 'wedge hold', 'line anvil', 'wedge flank', 'loose free',
        'swarm', 'loose skirmish', 'loose berserk', 'storm', 'wolfpack', 'alone']
ARMS = ('resonator', 'morale', 'pushpull', 'nearest')
# Fixed development profiles, never controller tuning knobs.
ELITE_NO_ROLLOUT = {'artyFire': 'plan', 'lockedDodge': True,
    'dodgeShells': 'smart', 'castDodge': True, 'weaponsFree': True,
    'saveWounded': .3, 'artyBattery': True, 'artyRollout': None}
SETTINGS = ('s3_full_pool', 's4_melee10', 's4_full_head', 's4_p23',
            's4_anomaly_novice_line', 's4_anomaly_regular_alone')


def request(spec):
    if not isinstance(spec, dict) or set(spec) - {'arm', 'params', 'seed', 'swapSides', 'controlledSide', 'opponent', 'diagnostics', 'setting', 'trace', 'skeleton', 'endCounts', 'decisionDiagnostics', 'attributionDiagnostics'}:
        raise ValueError('unsupported S3 field')
    seed = spec.get('seed', 2026100500)
    if type(seed) not in (int, float) or not math.isfinite(seed):
        raise ValueError('invalid seed')
    arm = spec.get('arm')
    if arm not in ARMS:
        raise ValueError('unknown/test-only S3 arm')
    side = spec.get('controlledSide', 0)
    if type(side) is not int or side not in (0, 1):
        raise ValueError('invalid controlled side')
    for key in ('swapSides', 'diagnostics', 'trace', 'endCounts', 'decisionDiagnostics', 'attributionDiagnostics'):
        if key in spec and type(spec[key]) is not bool:
            raise ValueError('invalid boolean: ' + key)
    params = spec.get('params', {})
    if not isinstance(params, dict):
        raise ValueError('params must be an object')
    opponent = spec.get('opponent', 'alone')
    if 'skeleton' in spec and spec['skeleton'] not in ('v0', 'v1', 'v2', 'v3', 'v4', 'v5', 'H', 'F', 'HF'):
        raise ValueError('invalid skeleton')
    if opponent not in POOL + ['novice', 'regular', 'elite', 'elite-fast']:
        raise ValueError('invalid opponent')
    setting = spec.get('setting', 's3_full_pool')
    if setting not in SETTINGS:
        raise ValueError('unknown development setting')
    if setting == 's4_p23' and opponent not in POOL:
        raise ValueError('P2/P3 requires a doctrine')
    if setting in ('s4_full_head', 's4_melee10') and opponent not in ('novice', 'regular'):
        raise ValueError('head-to-head requires novice or regular')
    if setting == 's4_melee10' and opponent != 'novice':
        raise ValueError('stage A requires novice')
    if setting.startswith('s4_anomaly_') and opponent not in ('novice', 'regular'):
        raise ValueError('anomaly requires a level')
    ai = [{}, {}]
    ai[side] = {'controller': arm, 'params': params}
    if 'skeleton' in spec: ai[side]['skeleton'] = spec['skeleton']
    if opponent not in POOL:
        ai[1-side] = {'level': opponent}
    elif side == 1:
        ai[0] = {'brain': 'alone' if opponent == 'alone' else opponent if opponent in ('storm', 'wolfpack') else 'formation'}
        if opponent not in ('alone', 'storm', 'wolfpack'):
            ai[0]['formation'] = {'preset': opponent}
    if setting == 's4_p23':
        ai[1-side]['skills'] = dict(ELITE_NO_ROLLOUT)
        ai[1-side]['lookahead'] = None
    if setting == 's4_anomaly_novice_line':
        if opponent != 'novice':
            raise ValueError('anomaly novice mismatch')
        ai[1-side].update(brain='formation', formation={'preset': 'line'})
    if setting == 's4_anomaly_regular_alone':
        if opponent != 'regular':
            raise ValueError('anomaly regular mismatch')
        ai[1-side].update(brain='alone')
    result = {'trace': spec.get('trace', False), 'debug': spec.get('trace', False), 'mode': 'alone', 'opponent': opponent if opponent in POOL and side == 0 else 'alone',
            's3': True, 'diagnostics': spec.get('diagnostics', False), 'options': {
                'seed': spec.get('seed', 2026100500), 'rules': 'game', 'scenario': 'mirror',
                'sandboxAbilities': False, 'perception': False, 'duration': 150, 'dt': 1/30,
                'army': {'melee': 10, 'ranged': 0 if setting == 's4_melee10' else 30, 'artillery': 0 if setting == 's4_melee10' else 10},
                'swapSides': spec.get('swapSides', False), 'ai': ai}}
    if 'decisionDiagnostics' in spec: result['decisionDiagnostics'] = spec['decisionDiagnostics']
    if 'attributionDiagnostics' in spec: result['attributionDiagnostics'] = spec['attributionDiagnostics']
    if 'endCounts' in spec: result['endCounts'] = spec['endCounts']
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec', type=pathlib.Path, help='JSON fixed-world S3 specification')
    args = ap.parse_args()
    fight = request(json.loads(args.spec.read_text()))
    binary = ROOT/'build/astelia_native'
    admit(binary)
    run = subprocess.run([str(binary), '--metrics'], input=json.dumps(fight)+'\n', text=True)
    raise SystemExit(run.returncode)


if __name__ == '__main__':
    main()
