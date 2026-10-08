"""Per-shape scorecard of stored v7c validation fights (read-only; runs no fights; changes no recorded result).
usage: scorecard.py <out.json>   — reads s4_v7c/raw/*.jsonl.gz for arms v7 and forcedP16 against regular.
Each metric measures one shape's own job; definitions are in SHAPE_SCORECARD.md."""
import gzip, json, math, sys, collections
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
CPP = Path(__file__).resolve().parents[2]
RAW = CPP / 's4_v7c' / 'raw'
ARMS = ('v7', 'forcedP16')
SAMPLE = 0.2          # s between position samples for the in-fight measures
ENGAGE_MARGIN = 50.0  # px beyond a unit's own weapon range still counted as "in the fight"
EDGE = 30.0           # px from the map border counted as "at the edge"
ROLE = {0: 'melee', 1: 'ranged', 2: 'gun'}

def fight(tag):
    dmg = collections.defaultdict(float)            # (src_team, src_role, tgt_team, tgt_role) -> damage dealt
    died = collections.Counter()                    # (team, role) -> deaths
    gun_deaths = {0: [], 1: []}
    shells = collections.defaultdict(set)           # (src_team, src_id, t) -> set of distinct targets hit (enemy-team only)
    mode = {}
    infight = collections.Counter()                 # (mode, state) -> unit-seconds, state in fight/out/edge
    hp_rot = collections.Counter()                  # damaged (<50% hp) own units: in fight vs out
    next_t, width, height, terminal, hp0 = 0.0, 1400, 800, None, {}
    with gzip.open(RAW / f'{tag}.jsonl.gz', 'rt') as f:
        for line in f:
            r = json.loads(line)
            if r.get('observerV1'):
                if r['step'] == 0: hp0 = {u[0]: u[5] for u in r['units']}
                for d in r['damage']:
                    st, tt = d['sourceTeam'], d['targetTeam']
                    sr, tr = d['sourceRole'], d['targetRole']
                    dmg[(st, sr, tt, tr)] += d['dealt']
                    if st != tt and sr == 'artillery': shells[(st, d['source'], round(d['t'], 4))].add(d['target'])
                    if st == tt and sr == 'artillery': shells[(st, d['source'], round(d['t'], 4), 'ff')].add(d['target'])
                    if d['died']:
                        died[(tt, tr)] += 1
                        if tr == 'artillery': gun_deaths[tt].append(d['t'])
                if r['t'] + 1e-9 >= next_t:
                    next_t += SAMPLE
                    units = r['units']
                    enemies = [u for u in units if u[1] == 1]
                    for u in units:
                        if u[1] != 0: continue
                        reach = u[7] + ENGAGE_MARGIN
                        near = min((math.hypot(u[3] - e[3], u[4] - e[4]) for e in enemies), default=math.inf)
                        edge = min(u[3], u[4], width - u[3], height - u[4]) <= EDGE
                        state = 'in' if near <= reach else ('edge' if edge else 'out')
                        m = mode.get(u[0], 'commit')
                        infight[(m, state)] += SAMPLE
                        if u[0] in hp0 and u[5] < 0.5 * hp0[u[0]]:
                            hp_rot['in' if state == 'in' else 'out'] += SAMPLE
            elif r.get('v7Telemetry'):
                width, height = r.get('width', width), r.get('height', height)
                for q in r['choices']: mode[q['id']] = q['mode']
            elif 'survivors' in r and 'enemySurvivors' in r:
                terminal = r
    hits = [len(v) for k, v in shells.items() if k[0] == 1 and len(k) == 3]
    ours = [len(v) for k, v in shells.items() if k[0] == 0 and len(k) == 3]
    ff = sum(v for (st, sr, tt, tr), v in dmg.items() if st == tt == 0)
    to_own_guns = {sr: v for (st, sr, tt, tr), v in dmg.items() if st == 1 and tt == 0 and tr == 'artillery'}
    our_gun_out = {tr: v for (st, sr, tt, tr), v in dmg.items() if st == 0 and sr == 'artillery' and tt == 1}
    eg_wipe = max(gun_deaths[1]) if len(gun_deaths[1]) == 10 else None
    og_wipe = max(gun_deaths[0]) if len(gun_deaths[0]) == 10 else None
    win = terminal['enemySurvivors'] == 0 and terminal['survivors'] > 0
    timeout = terminal['enemySurvivors'] > 0 and terminal['survivors'] > 0
    total_unit_s = sum(infight.values())
    return {
        'tag': tag, 'arm': tag.split('_')[1], 'win': win, 'timeout': timeout, 't_end': terminal['t'],
        'own_lost': 50 - terminal['survivors'], 'enemy_killed': 50 - terminal['enemySurvivors'],
        'deaths': {f'{t}_{r}': n for (t, r), n in died.items()},
        # gun battery
        'enemy_guns_killed': len(gun_deaths[1]), 'own_guns_lost': len(gun_deaths[0]),
        't_first_enemy_gun': min(gun_deaths[1], default=None), 't_enemy_guns_wiped': eg_wipe, 't_own_guns_wiped': og_wipe,
        'gun_damage_on_enemy_guns_share': (our_gun_out.get('artillery', 0) / sum(our_gun_out.values())) if our_gun_out else None,
        'friendly_fire': ff, 'enemy_damage_dealt': sum(v for (st, sr, tt, tr), v in dmg.items() if st == 0 and tt == 1),
        # screen
        'damage_to_own_guns_by_source': to_own_guns,
        # spacing
        'targets_per_enemy_shell': (sum(hits) / len(hits)) if hits else None, 'enemy_shells_hitting': len(hits),
        'targets_per_own_shell': (sum(ours) / len(ours)) if ours else None,
        # gate / staying in the fight
        'unit_seconds': {f'{m}_{s}': round(v, 1) for (m, s), v in infight.items()},
        'out_of_fight_share': (sum(v for (m, s), v in infight.items() if s != 'in') / total_unit_s) if total_unit_s else None,
        'escape_share': (sum(v for (m, s), v in infight.items() if m == 'escape') / total_unit_s) if total_unit_s else None,
        'damaged_units_in_fight_share': (hp_rot['in'] / (hp_rot['in'] + hp_rot['out'])) if (hp_rot['in'] + hp_rot['out']) else None,
    }

if __name__ == '__main__':
    tags = sorted(p.name[:-9] for p in RAW.glob('validation_*_regular_c*_o*.jsonl.gz') if p.name.split('_')[1] in ARMS)
    with ProcessPoolExecutor(4) as ex: rows = list(ex.map(fight, tags))
    json.dump({'note': 'stored v7c validation fights vs regular; no fights run', 'sample_s': SAMPLE, 'engage_margin_px': ENGAGE_MARGIN, 'edge_px': EDGE, 'fights': rows}, open(sys.argv[1], 'w'), indent=1)
    print(len(rows), 'fights')
