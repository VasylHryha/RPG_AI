"""Owner replays of stored v7c validation fights (usage: make_v7_replays.py <out.json>).
Reads the committed-hash raw ledgers in astelia_cpp/s4_v7c/raw/ read-only; runs no fights and changes no recorded result.
Frames are sampled 5 times per game second; each of our units carries its v7 gate mode (1 commit / 0 escape)."""
import gzip, json, sys, collections
from pathlib import Path
CPP = Path(__file__).resolve().parent.parent / 'astelia_cpp'
RAW = CPP / 's4_v7c' / 'raw'
FPS = 5
# (tag suffix, why chosen)
PICKS = [('c12_o1', 'best win'), ('c06_o0', 'typical win'), ('c04_o1', 'narrowest win'),
         ('c05_o0', 'worst loss'), ('c19_o1', 'fastest loss'), ('c18_o0', 'timeout (no elimination)')]

def one(suffix, why, per_fight):
    tag = f'validation_v7_regular_{suffix}'
    rec = per_fight[tag]
    frames, modes, maxhp, last_obs = [], {}, {}, None
    next_t, width, height = 0.0, 1400, 800
    deaths = []
    def emit(obs):
        us = []
        for u in obs['units']:
            uid, team, role, x, y, hp = u[0], u[1], u[2], u[3], u[4], u[5]
            maxhp.setdefault(uid, max(hp, 1e-9))
            us.append([uid, team, role, round(x), round(y), round(hp / maxhp[uid], 2), -1 if u[13] is None else u[13],
                       modes.get(uid) if team == 0 else None])
        frames.append([round(obs['t'], 2), us])
    with gzip.open(RAW / f'{tag}.jsonl.gz', 'rt') as f:
        for line in f:
            r = json.loads(line)
            if r.get('observerV1'):
                if r['step'] == 0:
                    for u in r['units']: maxhp[u[0]] = max(u[5], 1e-9)
                for d in r['damage']:
                    if d['died']: deaths.append([round(d['t'], 2), d['targetTeam'], d['targetRole']])
                last_obs = r
                if r['t'] + 1e-9 >= next_t:
                    emit(r); next_t += 1 / FPS
            elif r.get('v7Telemetry'):
                width, height = r.get('width', width), r.get('height', height)
                for q in r['choices']: modes[q['id']] = 1 if q['mode'] == 'commit' else 0
            elif 'survivors' in r and 'enemySurvivors' in r:
                terminal = r
    if frames[-1][0] != round(last_obs['t'], 2): emit(last_obs)
    start = collections.Counter((u[1], u[2]) for u in frames[0][1])
    end = collections.Counter((u[1], u[2]) for u in frames[-1][1])
    role = {0: 'melee', 1: 'ranged', 2: 'guns'}
    return {'name': suffix, 'why': why, 'tag': tag, 'win': rec['win'], 'timeout': rec['timeout'], 'S': rec['S'],
            'width': width, 'height': height,
            'summary': {k: terminal[k] for k in ('survivors', 'enemySurvivors', 't', 'crossTeamDealt', 'crossTeamTaken', 'artilleryAlive')},
            'start': {f'team{t}_{role[r]}': n for (t, r), n in sorted(start.items())},
            'end': {f'team{t}_{role[r]}': n for (t, r), n in sorted(end.items())},
            'deaths': deaths, 'gun_survival': rec['telemetry'].get('gun_survival'), 'frames': frames}

if __name__ == '__main__':
    analysis = json.load(open(CPP / 's4_v7c' / 'ANALYSIS.json'))
    per_fight = {r['tag']: r for r in analysis['per_fight']}
    fights = [one(s, w, per_fight) for s, w in PICKS]
    data = {'note': 'stored v7c validation fights (v7 vs regular, theta* ordinal 161); read from raw ledgers, no fights run',
            'unit_fields': ['id', 'team', 'role(0 melee,1 ranged,2 gun)', 'x', 'y', 'hp_fraction', 'target', 'gate(1 commit,0 escape)'],
            'fps': FPS, 'fights': fights}
    json.dump(data, open(sys.argv[1], 'w'), separators=(',', ':'))
    for f in fights:
        print(f['name'], f['why'], 'win' if f['win'] else 'timeout' if f['timeout'] else 'loss', f['summary'], f['start'], f['end'], len(f['frames']), 'frames')
