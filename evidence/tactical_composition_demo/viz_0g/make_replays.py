"""Development replays for the owner (usage: make_replays.py <out.json> [knob file under astelia_cpp/] [skeleton v1|v2]) (not S5/S6 evidence). Seeds 2026100700-2026100702 are development seeds already excluded by SPEC_0G preflight.
Runs three fights with the amended-S4 stage-B knobs and writes compact replays (10 frames per game second) plus an end-of-fight analysis.
  python3 make_replays.py <out.json>"""
import json, math, subprocess, sys, collections
from pathlib import Path
CPP = Path(__file__).resolve().parent.parent / 'astelia_cpp'
sys.path.insert(0, str(CPP))
import s3_runner as R
KNOBS = sys.argv[2] if len(sys.argv) > 2 else 's4_amended_development/B_best.json'   # knob file under astelia_cpp/
SKELETON = sys.argv[3] if len(sys.argv) > 3 else None                                  # None = v0 (as originally), or 'v1' / 'v2'
B = json.load(open(CPP / KNOBS))
ROLE = {'melee': 0, 'ranged': 1, 'artillery': 2}
FIGHTS = [('resonator_vs_novice', 'resonator', 'novice', 2026100700), ('resonator_vs_regular', 'resonator', 'regular', 2026100701), ('morale_vs_regular', 'morale', 'regular', 2026100702)]

def one(name, arm, opp, seed):
    spec = {'arm': arm, 'params': B[arm], 'seed': seed, 'swapSides': False, 'controlledSide': 0, 'opponent': opp, 'setting': 's4_full_head'}
    if SKELETON: spec['skeleton'] = SKELETON
    req = R.request(spec)
    req['trace'] = True
    run = subprocess.run([str(CPP / 'build/astelia_native'), '--capture-s3'], input=json.dumps(req) + '\n', text=True, capture_output=True, timeout=300, check=True)
    rows = [json.loads(x) for x in run.stdout.splitlines()]
    terminal = rows[-1]
    maxhp, frames, pending, cap = {}, [], None, {}
    for row in rows:
        if 'state' in row:
            if pending is not None and pending['step'] % 3 == 0: frames.append((pending, dict(cap)))
            pending = row
            for u in row['state']['units']: maxhp.setdefault(u['id'], max(u['hp'], 1e-9))
        elif row.get('capture'):
            cap = {u['id']: u for u in row['units']}
    if pending is not None: frames.append((pending, dict(cap)))
    out = []
    for st, c in frames:
        us = []
        for u in st['state']['units']:
            if not u['alive']: continue
            k = c.get(u['id'], {})
            phase = k.get('state'); com = k.get('commitment')
            us.append([u['id'], u['team'], ROLE.get(u['role'], 1), round(u['x']), round(u['y']), round(u['hp'] / maxhp[u['id']], 2),
                       u['target'] if u['target'] is not None else -1,
                       None if phase is None else round(phase % (2 * math.pi) if arm == 'resonator' else phase, 3), None if com is None else round(com, 3)])
        out.append([round(st['state']['t'], 2), us])
    last = frames[-1][0]['state']['units']
    left = collections.Counter((u['team'], u['role']) for u in last if u['alive'])
    return {'name': name, 'arm': arm, 'opponent': opp, 'seed': seed, 'summary': {k: terminal[k] for k in ('survivors', 'enemySurvivors', 't', 'crossTeamDealt', 'crossTeamTaken')},
            'left_at_end': {f'team{t}_{r}': n for (t, r), n in sorted(left.items())}, 'frames': out}

data = {'note': 'development replays, amended-S4 stage-B knobs; not evidence for any registered endpoint', 'width': 1400, 'height': 800, 'role_codes': ROLE,
        'unit_fields': ['id', 'team', 'role', 'x', 'y', 'hp_fraction', 'target', 'phase_or_morale', 'commitment'], 'fights': [one(*f) for f in FIGHTS]}
json.dump(data, open(sys.argv[1], 'w'), separators=(',', ':'))
for f in data['fights']: print(f['name'], f['summary'], f['left_at_end'], len(f['frames']), 'frames')
