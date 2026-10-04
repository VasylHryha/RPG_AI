"""Freeze a balanced equivalence set, not an AI experiment or performance verdict."""
import copy
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent


def main():
    cat = json.loads(subprocess.check_output(['node', str(ROOT / 'js_host.cjs'), '--catalog'], text=True))
    levels = list(cat['LEVELS']) + ['alone']
    fights = []
    descriptions = []

    def add(req, label):
        fights.append(req)
        descriptions.append(label)

    def request(opponent, seed, swap, profile, rules, abilities, compact=False):
        o = dict(seed=seed, scenario='mirror', duration=20, swapSides=swap,
                 abilities=abilities, sandboxAbilities=abilities,
                 ai=[profile, {}])
        if rules == 'game':
            o['rules'] = 'game'
        if compact:
            o['army'] = dict(melee=2, ranged=4, artillery=2)
            o['width'] = 650
        return dict(mode='alone', opponent=opponent, options=o)

    # Every opponent x both placements x seeds 1..10. The other factors rotate
    # to cover levels/rules/abilities without claiming a full Cartesian product.
    for i, opponent in enumerate(cat['POOL']):
        for seed in range(1, 11):
            for swap in (False, True):
                index = len(fights)
                level = levels[(i + seed + int(swap)) % len(levels)]
                profile = dict(brain='alone') if level == 'alone' else dict(level=level)
                rules = 'game' if (seed + int(swap)) % 2 else 'default'
                abilities = (seed // 2 + i + int(swap)) % 2 == 0
                add(request(opponent, seed, swap, profile, rules, abilities,
                            level in ('elite', 'elite-fast')), f'pool:{opponent}:{seed}:{swap}:{level}:{rules}:{abilities}')

    # Each skill's def, alt, explicit values and values used by any level.
    for key, skill in cat['SKILLS'].items():
        values = [skill['def'], skill['alt'], *skill.get('values', [])]
        values.extend(lv['skills'][key] for lv in cat['LEVELS'].values() if key in lv.get('skills', {}))
        seen = set()
        for value in values:
            identity = json.dumps(value, sort_keys=True)
            if identity in seen:
                continue
            seen.add(identity)
            for rules in ('game', 'default'):
                req = request(cat['POOL'][len(fights) % len(cat['POOL'])], len(fights) % 10 + 1,
                              bool(len(fights) % 2), dict(level='novice', skills={key: value}), rules, True, True)
                add(req, f'skill:{key}:{identity}:{rules}')

    # Skill-only opponents: preserve their pool brain; explicitly empty versus
    # elite skills, with and without the artillery outcome check.
    for i, opponent in enumerate(cat['POOL']):
        for style in ('none', 'elite', 'elite_without_rollout'):
            off = {k: False if isinstance(v['def'], bool) else 0 if isinstance(v['def'], (int, float)) else None
                   for k, v in cat['SKILLS'].items()}
            off.update(abilities='off', lead='none', pursuit='chase', artyFire='single', artyModel='simple')
            skills = off if style == 'none' else copy.deepcopy(cat['LEVELS']['elite']['skills'])
            if style == 'elite_without_rollout':
                skills['artyRollout'] = None
            req = request(opponent, i % 10 + 1, bool(i % 2), dict(level='regular'), 'game', True, True)
            req['options']['ai'][1] = dict(skills=skills)
            add(req, f'opponent-skills:{opponent}:{style}')

    # Larger elite callers, other scenarios, custom kinds, homing, combos, mind,
    # and rule switches in the same process supplement the balanced pool set.
    for level in ('elite', 'elite-fast'):
        req = request('wolfpack', 5, False, dict(level=level), 'game', False)
        req['options']['duration'] = 12
        add(req, f'full-army:{level}')
    for scenario in ('hunters', 'skirmish'):
        for brain in ('alone', 'formation', 'reactive', 'storm', 'wolfpack', 'gamepack'):
            req = request('alone', 4, False, dict(brain='rules' if brain == 'reactive' else brain), 'game', True, True)
            req['mode'] = brain
            req['options']['scenario'] = scenario
            add(req, f'scenario:{scenario}:{brain}')
    for shots in ('aimed', 'homing'):
        req = request('storm', 3, True, dict(level='regular'), 'default', True, True)
        req['options']['shots'] = shots
        req['options']['windUp'] = True
        add(req, f'shots:{shots}')
    for shape in ('line', 'wedge', 'box', 'column', 'screen', 'crescent', 'ring'):
        req = request('alone', 9, False, dict(brain='formation', formation=dict(shape=shape)), 'game', True, True)
        add(req, f'shape:{shape}')
    for extras in ({'combos': []}, {'combos': ['tchain', 'fixlob']}, {'artyFire': 'plan', 'artyModel': 'exact', 'artyOwn': True,
                    'artyFollow': True, 'artyHerd': 10, 'holdFire': {'sync': .5, 'wave': .45}},
                   {'leaderFire': True, 'fireControl': True, 'fireDepth': .25, 'waves': 3}):
        req = request('wolfpack', 8, False, dict(level='veteran', skills=extras), 'game', True, True)
        add(req, 'coordinated:' + json.dumps(extras, sort_keys=True))
    req = request('gamepack', 7, True, dict(brain='rules', lookahead=dict(extends='mind', budget=4)), 'game', True, True)
    add(req, 'lookahead:mind')
    req = request('alone', 6, False, dict(brain='alone'), 'game', False, True)
    req['options']['perception'] = True
    req['options']['unitSet'] = {'kinds': {'dart🐾': {'role': 'ranged', 'hp': 80, 'speed': 60, 'r': 6,
        'dmg': 12, 'cd': 1, 'windup': .5, 'reach': 220, 'ep': 100, 'epRegen': 8, 'cost': 5, 'shot': 350}}, 'army': [['dart🐾', 4]]}
    add(req, 'custom-kind:perception')
    req = request('alone', 2, False, dict(brain='alone'), 'default', False, True)
    req['options']['enemyArmy'] = dict(melee=3, ranged=2, artillery=1)
    req['options']['ours'] = [dict(role='melee', hp=123), dict(role='ranged', hp=42)]
    add(req, 'carried-army:different-enemy')

    (ROOT / 'check_fights.jsonl').write_text(''.join(json.dumps(r, separators=(',', ':')) + '\n' for r in fights))
    # Fixed trace selection includes all brains, skill paths, and fork users.
    # These twenty traces use game rules; default rules are covered by summaries.
    trace_ids = []
    for label in ('alone', 'novice', 'regular', 'veteran', 'elite', 'elite-fast'):
        matches = [i for i, d in enumerate(descriptions) if d.startswith('pool:') and f':{label}:game:' in d]
        trace_ids.extend(matches[:2])
    for prefix in ('scenario:skirmish:alone', 'scenario:skirmish:storm', 'scenario:skirmish:gamepack',
                   'shape:ring', 'coordinated:', 'lookahead:mind', 'full-army:elite-fast', 'custom-kind:'):
        trace_ids.extend([i for i, d in enumerate(descriptions) if d.startswith(prefix)][:1])
    trace_ids = list(dict.fromkeys(trace_ids))[:20]
    reference_ids = list(dict.fromkeys(trace_ids + [round(i * (len(fights) - 1) / 59) for i in range(60)]))
    for i in range(len(fights)):
        if len(reference_ids) >= 80:
            break
        if i not in reference_ids:
            reference_ids.append(i)
    speed_ids = [i for i, d in enumerate(descriptions[:380]) if ':elite:' not in d and ':elite-fast:' not in d and ':veteran:default:' not in d][:50]
    (ROOT / 'check_selection.json').write_text(json.dumps(dict(descriptions=descriptions, trace_ids=trace_ids,
        reference_ids=reference_ids[:80], speed_ids=speed_ids, policy='balanced coverage, not Cartesian; 20-second fights; elite/skill probes use compact armies; two additional full-army elite fights'), indent=2) + '\n')
    print(f'{len(fights)} fights; {len(trace_ids)} traces; 80 references; 50 timing fights')


if __name__ == '__main__':
    main()
