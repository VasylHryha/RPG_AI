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


def request(spec):
    if not isinstance(spec, dict) or set(spec) - {'arm', 'params', 'seed', 'swapSides', 'controlledSide', 'opponent', 'diagnostics'}:
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
    for key in ('swapSides', 'diagnostics'):
        if key in spec and type(spec[key]) is not bool:
            raise ValueError('invalid boolean: ' + key)
    params = spec.get('params', {})
    if not isinstance(params, dict):
        raise ValueError('params must be an object')
    opponent = spec.get('opponent', 'alone')
    if opponent not in POOL + ['novice', 'regular', 'elite', 'elite-fast']:
        raise ValueError('invalid opponent')
    ai = [{}, {}]
    ai[side] = {'controller': arm, 'params': params}
    if opponent not in POOL:
        ai[1-side] = {'level': opponent}
    elif side == 1:
        ai[0] = {'brain': 'alone' if opponent == 'alone' else opponent if opponent in ('storm', 'wolfpack') else 'formation'}
        if opponent not in ('alone', 'storm', 'wolfpack'):
            ai[0]['formation'] = {'preset': opponent}
    return {'mode': 'alone', 'opponent': opponent if opponent in POOL and side == 0 else 'alone',
            's3': True, 'diagnostics': spec.get('diagnostics', False), 'options': {
                'seed': spec.get('seed', 2026100500), 'rules': 'game', 'scenario': 'mirror',
                'sandboxAbilities': False, 'perception': False, 'duration': 150, 'dt': 1/30,
                'army': {'melee': 10, 'ranged': 30, 'artillery': 10},
                'swapSides': spec.get('swapSides', False), 'ai': ai}}


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
