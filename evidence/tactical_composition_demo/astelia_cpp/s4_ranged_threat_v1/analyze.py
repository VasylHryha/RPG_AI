"""Stored traces only. No project imports, native binaries, fights or simulations.

Run from any directory: python3 <this file>. Verify every manifest hash before
parsing any trace. Original receipts remain read-only. Geometry is descriptive;
it does not predict the result of any proposed policy intervention.
"""
import collections
import gzip
import hashlib
import json
import math
import pathlib
import statistics
import time
from array import array

HERE = pathlib.Path(__file__).resolve().parent
CPP = HERE.parent
SOURCE = CPP / 's4_spacing_probe_v1'
COMMIT = 'a13b51cfe7525fd5951e94e73bdae73f2692c597'
BINS = (0, 10, 20, 30, 60, 150.1)
ROLES = {0: 'melee', 1: 'ranged', 2: 'artillery'}


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


def load(p):
    return json.loads(p.read_text())


def write(name, obj):
    (HERE / name).write_text(json.dumps(obj, separators=(',', ':'), allow_nan=False) + '\n')


def quantile(xs, p):
    if not xs:
        return None
    x = (len(xs)-1)*p
    i = int(x)
    return xs[i] + (xs[min(i+1, len(xs)-1)]-xs[i])*(x-i)


def distribution(xs):
    xs = sorted(xs)
    return dict(n=len(xs), mean=statistics.mean(xs) if xs else None,
                p10=quantile(xs, .1), median=quantile(xs, .5), p90=quantile(xs, .9))


def ratio(n, d):
    return n/d if d else None


def distance(a, b):
    return math.hypot(a[3]-b[3], a[4]-b[4])


def direct_reach(a, b):
    return distance(a, b) <= a[7]+a[6]+b[6]


def nearest(u, candidates):
    return min(candidates, key=lambda v: (distance(u, v), v[0]), default=None)


def centroid(us):
    return (statistics.mean(u[3] for u in us), statistics.mean(u[4] for u in us)) if us else None


def bin_index(t):
    return next(i for i in range(len(BINS)-1) if BINS[i] <= t < BINS[i+1])


def analyze(fight):
    """Independent shell matching, casualty, realization and threat analysis."""
    diag = fight['head'] == 'regular'
    counts = [collections.Counter(), collections.Counter()]
    audits = collections.Counter()
    ns = [array('d'), array('d')]
    early = [array('d'), array('d')]
    singles = [0, 0]
    ticks = [0, 0]
    ranges = [0, 0]
    shifts, radials = array('d'), array('d')
    geom = collections.defaultdict(lambda: array('d'))
    geom_counts = collections.Counter()
    actions_count = collections.Counter()
    damage_bins = [collections.Counter() for _ in range(len(BINS)-1)]
    target_bins = [collections.Counter() for _ in range(len(BINS)-1)]
    first_reach, reach_details = {}, []
    damage_events, kills = [], []
    initial = previous = current = terminal = None
    death_times = {}
    shells = []
    pending = collections.defaultdict(list)
    laststep = -1
    first_damage = None
    all_own_gun_damage = 0
    with gzip.open(SOURCE / 'raw' / (fight['id']+'.jsonl.gz'), 'rt') as f:
        for line in f:
            row = json.loads(line)
            if row.get('spacingProbe'):
                assert current and row['step'] == current['step']
                assert row['S'] == (100 if fight['arm'] == 'P10' else 60)
                acts = {a[0]: a for a in current['actions']}
                for g in row['guns']:
                    audits['prepare_gun_ticks'] += 1
                    audits['clipped_goal_ticks'] += abs(g[6]-g[8]) > 1e-9 or abs(g[7]-g[9]) > 1e-9
                    shift = math.hypot(g[10], g[11])
                    shifts.append(shift)
                    radials.append(g[13])
                    audits['shift_ticks'] += shift > 1e-9
                    audits['zero_multiplier_shift_ticks'] += shift > 1e-9 and g[12] == 0
                    audits['raw_goal_out_of_focus_band_ticks'] += not g[14] <= g[13] <= g[15]
                    audits['coincident_pair_terms'] += g[17]
                    audits['neighbour_terms'] += g[16]
                    a = acts[g[0]]
                    if a[8]:
                        assert abs(a[3]-g[8]) < 1e-7 and abs(a[4]-g[9]) < 1e-7 and a[5] == g[12] and a[6] == 0
                        audits['clipped_action_reconciled_ticks'] += 1
                    else:
                        audits['native_guard_hold_ticks'] += 1
                continue
            if not row.get('observerV1'):
                terminal = row
                continue
            assert row['step'] == laststep+1
            laststep = row['step']
            current = row
            units = {u[0]: u for u in row['units']}
            if initial is None:
                initial = units
                assert len(initial) == 100
            before = {u[0]: u for u in previous['units']} if previous else units
            dt = row['t']-previous['t'] if previous else 0
            if previous:
                assert abs(dt-1/30) < 1e-10
            for launch in row['launches']:
                assert initial[launch[0]][2] == 2 and not launch[8] and not launch[9]
                item = dict(source=launch[0], target=launch[1], side=launch[2], born=launch[5],
                            at=launch[6], gun_target=initial[launch[1]][2] == 2, hits=set(), hp=0)
                shells.append(item)
                pending[launch[0]].append(item)
            for d in row['damage']:
                if d['targetRole'] == 'artillery' and d['dealt'] > 0 and d['sourceRole'] == 'artillery':
                    due = [s for s in pending[d['source']] if -1e-9 <= d['t']-s['at'] <= dt+1e-7]
                    assert len(due) == 1
                    s = due[0]
                    if d['targetTeam'] != s['side']:
                        s['hits'].add(d['target'])
                        s['hp'] += d['dealt']
                if d['died']:
                    assert d['target'] not in death_times
                    death_times[d['target']] = d['t']
                    kills.append(d)
                if diag:
                    k = bin_index(d['t'])
                    if d['targetTeam'] == 0 and d['targetRole'] == 'artillery':
                        all_own_gun_damage += d['dealt']
                        label = str(d['sourceTeam'])+'_'+d['sourceRole']
                        damage_bins[k][label] += d['dealt']
                        if d['sourceTeam'] == 1 and d['sourceRole'] == 'ranged' and d['dealt'] > 0:
                            first_damage = d['t'] if first_damage is None else first_damage
                            damage_events.append(dict(t=d['t'], source=d['source'], target=d['target'],
                                                      distance=d['distance'], hp=d['dealt'], died=d['died']))
                    if d['died'] and d['targetTeam'] == 1 and d['targetRole'] == 'ranged':
                        damage_bins[k]['enemy_ranged_kills_by_'+str(d['sourceTeam'])+'_'+d['sourceRole']] += 1
            own_guns = [u for u in units.values() if u[1] == 0 and u[2] == 2]
            enemy_guns = [u for u in units.values() if u[1] == 1 and u[2] == 2]
            enemy_ranged = [u for u in units.values() if u[1] == 1 and u[2] == 1]
            gun_phase = previous and any(u[1] == 1 and u[2] == 2 for u in before.values())
            if gun_phase:
                for side, guns, enemies in ((0, own_guns, enemy_guns), (1, enemy_guns, own_guns)):
                    for u in guns:
                        ticks[side] += 1
                        ranges[side] += any(u[8] <= distance(u, e) <= u[7] for e in enemies)
                        v = nearest(u, [g for g in guns if g[0] != u[0]])
                        if v is None:
                            singles[side] += 1
                        else:
                            nd = distance(u, v)
                            ns[side].append(nd)
                            if 10 <= row['t'] < 20:
                                early[side].append(nd)
            if diag:
                # First observed legal reach at every post-step snapshot. This is
                # geometric reach, not fire, visibility, or a cooldown assertion.
                for e in enemy_ranged:
                    if e[0] not in first_reach:
                        g = nearest(e, own_guns)
                        if g is not None and direct_reach(e, g):
                            first_reach[e[0]] = row['t']
                            eg = nearest(e, enemy_guns)
                            reach_details.append(dict(unit=e[0], t=row['t'], own_gun=g[0],
                                                      distance_to_own_gun=distance(e, g),
                                                      distance_to_enemy_gun=distance(e, eg) if eg else None))
                k = bin_index(previous['t'] if previous else row['t'])
                before_guns = [g for g in before.values() if g[1] == 0 and g[2] == 2]
                threatened = [e for e in before.values() if e[1] == 1 and e[2] == 1 and any(direct_reach(e, g) for g in before_guns)] if gun_phase and before_guns else []
                for a in row['actions']:
                    u = before[a[0]]
                    if u[1] != 0 or u[2] not in (0, 1):
                        continue
                    role = ROLES[u[2]]
                    target = initial.get(a[2])
                    label = role+'_target_'+(str(target[1])+'_'+ROLES[target[2]] if target else 'none')
                    target_bins[k][label] += 1
                    if gun_phase and before_guns:
                        actions_count[label] += 1
                        actions_count[role+'_ticks'] += 1
                        actions_count[role+'_move_ticks'] += bool(a[8] and a[5] > 0 and math.hypot(a[3]-u[3], a[4]-u[4]) > a[6]+1e-9)
                        reachable = [e for e in threatened if direct_reach(u, e)]
                        actions_count[role+'_threat_reachable_ticks'] += bool(reachable)
                        actions_count[role+'_selects_reachable_threat_ticks'] += a[2] in [e[0] for e in reachable]
                # One snapshot per simulated second, with equal unit-snapshot
                # weight. Whole scope and early window are kept separate.
                if row['step'] % 30 == 0 and own_guns and enemy_guns:
                    windows = ['whole'] + (['early_10_20'] if 10 <= row['t'] < 20 else [])
                    ec, oc = centroid(enemy_guns), centroid(own_guns)
                    dx, dy = oc[0]-ec[0], oc[1]-ec[1]
                    norm = math.hypot(dx, dy)
                    toward = (dx/norm, dy/norm) if norm else None
                    for window in windows:
                        for e in enemy_ranged:
                            eg, og = nearest(e, enemy_guns), nearest(e, own_guns)
                            geom[window+'_enemy_ranged_to_enemy_gun'].append(distance(e, eg))
                            geom[window+'_enemy_ranged_to_own_gun'].append(distance(e, og))
                            if toward:
                                offset = (e[3]-ec[0])*toward[0]+(e[4]-ec[1])*toward[1]
                                geom[window+'_enemy_ranged_forward_offset'].append(offset)
                                geom_counts[window+'_enemy_ranged_line_samples'] += 1
                                geom_counts[window+'_enemy_ranged_in_front'] += offset > 0
                            geom_counts[window+'_enemy_ranged_samples'] += 1
                            geom_counts[window+'_enemy_ranged_in_gun_reach'] += direct_reach(e, og)
                        for role, name in ((0, 'melee'), (1, 'ranged')):
                            for u in units.values():
                                if u[1] != 0 or u[2] != role:
                                    continue
                                og, er = nearest(u, own_guns), nearest(u, enemy_ranged)
                                geom[window+'_own_'+name+'_to_own_gun'].append(distance(u, og))
                                if er:
                                    geom[window+'_own_'+name+'_to_enemy_ranged'].append(distance(u, er))
                        for g in own_guns:
                            tg = units.get(next((a[2] for a in row['actions'] if a[0] == g[0]), 0))
                            geom_counts[window+'_own_gun_samples'] += 1
                            safe = not any(direct_reach(e, g) for e in enemy_ranged)
                            legal_target = tg is not None and tg[1] == 1 and tg[2] == 2 and g[8] <= distance(g, tg) <= g[7]
                            geom_counts[window+'_own_gun_safe_and_gun_target_in_range'] += safe and legal_target
                            geom_counts[window+'_own_gun_enemy_ranged_reach'] += not safe
            previous = row
    assert terminal == fight['summary']
    assert sum(d['targetTeam'] == 0 and d['targetRole'] == 'artillery' for d in kills) == 10-terminal['artilleryAlive'][0]
    assert len(kills) == 100-terminal['survivors']-terminal['enemySurvivors']
    for s in shells:
        c = counts[s['side']]
        if s['gun_target']:
            c['gun_launches'] += 1
            c['successful'] += bool(s['hits'])
            c['victims'] += len(s['hits'])
            c['targeted_hp'] += s['hp']
            c['dead_before_impact'] += death_times.get(s['target'], math.inf) < s['at']-1e-9
        else:
            c['incidental_hp'] += s['hp']
        c['all_artillery_hp'] += s['hp']
    if diag:
        assert sum(b['1_artillery'] for b in damage_bins) == counts[1]['all_artillery_hp']
        assert math.isclose(all_own_gun_damage, sum(u[5] for u in initial.values() if u[1] == 0 and u[2] == 2)-sum(u[5] for u in units.values() if u[1] == 0 and u[2] == 2), abs_tol=1e-7)
    s = terminal
    summary = dict(id=fight['id'], arm=fight['arm'], head=fight['head'], cluster=fight['cluster'],
                   orientation=fight['orientation'], duration_s=s['t'], survivors=s['survivors'],
                   enemy_survivors=s['enemySurvivors'], enemy_guns_destroyed=10-s['artilleryAlive'][1],
                   own_guns_lost=10-s['artilleryAlive'][0], own_losses=50-s['survivors'],
                   S=s['survivors']-s['enemySurvivors'], timeout=s['t'] >= 150,
                   elimination_win=s['enemySurvivors'] == 0 and s['survivors'] >= 1 and s['t'] < 150)
    diagnostic = dict(**summary, first_enemy_ranged_reach_s=min(first_reach.values(), default=None),
                      ranged_units_ever_in_reach=len(first_reach), first_reach_details=reach_details,
                      first_enemy_ranged_gun_damage_s=first_damage, damage_bins=[dict(b) for b in damage_bins],
                      target_bins=[dict(b) for b in target_bins], commit_action_counts=dict(actions_count),
                      geometry_counts=dict(geom_counts), geometry={k: distribution(v) for k, v in geom.items()},
                      enemy_ranged_gun_damage_events=damage_events,
                      enemy_gun_death_times_s=[d['t'] for d in kills if d['targetTeam'] == 1 and d['targetRole'] == 'artillery'],
                      own_gun_death_times_s=[d['t'] for d in kills if d['targetTeam'] == 0 and d['targetRole'] == 'artillery'],
                      enemy_ranged_deaths=[dict(t=d['t'], source=d['source'], source_team=d['sourceTeam'],
                                                source_role=d['sourceRole'], victim=d['target']) for d in kills
                                           if d['targetTeam'] == 1 and d['targetRole'] == 'ranged']) if diag else None
    audit = dict(**summary, counts=[dict(c) for c in counts], audit=dict(audits),
                 own_gun_killers=dict(collections.Counter(str(d['sourceTeam'])+'_'+d['sourceRole'] for d in kills
                                                        if d['targetTeam'] == 0 and d['targetRole'] == 'artillery')))
    return audit, diagnostic, (ns, early, singles, ticks, ranges, shifts, radials, geom)


def main():
    start = time.monotonic()
    manifest = load(SOURCE/'RAW_FILES_LOCAL.json')
    for e in manifest['files']:
        p = SOURCE/e['path']
        assert p.stat().st_size == e['bytes'] and sha(p) == e['sha256'], str(p)
    fights = load(SOURCE/'FIGHTS.json')
    declared = load(SOURCE/'DECLARATION.json')
    assert len(fights) == 120
    assert len({(r['arm'], r['head'], r['cluster'], r['orientation']) for r in fights}) == 120
    for r in fights:
        assert sha(SOURCE/'raw'/(r['id']+'.jsonl.gz')) == r['raw_sha256']
        req = SOURCE/'raw'/(r['id']+'_request.json')
        assert sha(req) == r['request_sha256']
        wanted = load(SOURCE/(r['head'].upper()+'_REQUEST_TEMPLATE.json'))
        wanted['options']['seed'] = declared['development_seeds'][r['cluster']]
        wanted['options']['swapSides'] = bool(r['orientation'])
        wanted['options']['ai'][0]['controller'] = r['arm']
        assert load(req) == wanted
    comparisons, diagnostics, cells = [], [], []
    compact = load(SOURCE/'COMPACT.json')
    original = load(SOURCE/'SUMMARY.json')
    for arm in ('P5', 'P10', 'P11'):
        for head in ('regular', 'novice'):
            subset = [r for r in fights if (r['arm'], r['head']) == (arm, head)]
            ars, ds = [], []
            ns, es = [array('d'), array('d')], [array('d'), array('d')]
            singles, ticks, ranges = [0, 0], [0, 0], [0, 0]
            shifts, radials = array('d'), array('d')
            geom = collections.defaultdict(lambda: array('d'))
            for r in subset:
                a, d, g = analyze(r)
                ars.append(a)
                if d:
                    ds.append(d)
                for i in (0, 1):
                    ns[i].extend(g[0][i]); es[i].extend(g[1][i])
                    singles[i] += g[2][i]; ticks[i] += g[3][i]; ranges[i] += g[4][i]
                shifts.extend(g[5]); radials.extend(g[6])
                for k, v in g[7].items():
                    geom[k].extend(v)
                stored = next(x for x in original['fights'] if x['id'] == r['id'])
                for k in ('duration_s', 'S', 'enemy_guns_destroyed', 'own_guns_lost', 'own_losses', 'timeout', 'elimination_win'):
                    assert a[k] == stored[k], (r['id'], k)
            c = [sum((collections.Counter(a['counts'][i]) for a in ars), collections.Counter()) for i in (0, 1)]
            nearest_rows = [dict(n=len(x), median=distribution(x)['median'], p10=distribution(x)['p10']) for x in ns]
            early_rows = [dict(n=len(x), median=distribution(x)['median'], p10=distribution(x)['p10']) for x in es]
            aud = sum((collections.Counter(a['audit']) for a in ars), collections.Counter())
            killers = sum((collections.Counter(a['own_gun_killers']) for a in ars), collections.Counter())
            observed = dict(elimination_wins=sum(a['elimination_win'] for a in ars), timeouts=sum(a['timeout'] for a in ars),
                            mean_S=statistics.mean(a['S'] for a in ars),
                            mean_enemy_guns_destroyed=statistics.mean(a['enemy_guns_destroyed'] for a in ars),
                            mean_own_guns_lost=statistics.mean(a['own_guns_lost'] for a in ars),
                            mean_own_losses=statistics.mean(a['own_losses'] for a in ars),
                            nearest=nearest_rows, early_10_20_nearest=early_rows, nearest_singleton_ticks=singles,
                            gun_phase_ticks=ticks, gun_range_ticks=ranges, gun_range_fraction=[ratio(ranges[i], ticks[i]) for i in (0, 1)],
                            audit=dict(aud), own_gun_killers_by_team_role=dict(killers),
                            enemy_over_own_artillery_hp_ratio=ratio(c[1]['all_artillery_hp'], c[0]['all_artillery_hp']))
            stored = next(x for x in compact['rows'] if (x['arm'], x['head']) == (arm, head))
            for k, v in observed.items():
                # Counter equality treats zero-count omitted fields consistently.
                assert ({n: x for n, x in v.items() if x} == {n: x for n, x in stored[k].items() if x} if k == 'audit' else v == stored[k]), (arm, head, k, v, stored[k])
            for i in (0, 1):
                for k, ck in [('gun_targeted_launches', 'gun_launches'), ('successful_gun_targeted_shells', 'successful'),
                              ('gun_victims', 'victims'), ('artillery_hp_to_opposing_guns', 'all_artillery_hp'),
                              ('incidental_hp', 'incidental_hp'), ('already_dead_before_impact', 'dead_before_impact')]:
                    assert c[i][ck] == stored['sides'][i][k], (arm, head, i, k)
                assert ratio(c[i]['victims'], c[i]['successful']) == stored['sides'][i]['gun_victims_per_successful_shell']
            comparisons.append(dict(arm=arm, head=head, **observed, independent_shell_counts=[dict(x) for x in c], status='PASS'))
            if ds:
                bins = [sum((collections.Counter(d['damage_bins'][i]) for d in ds), collections.Counter()) for i in range(len(BINS)-1)]
                cells.append(dict(arm=arm, fights=20, geometry={k: distribution(v) for k, v in geom.items()},
                                  geometry_counts=dict(sum((collections.Counter(d['geometry_counts']) for d in ds), collections.Counter())),
                                  commit_action_counts=dict(sum((collections.Counter(d['commit_action_counts']) for d in ds), collections.Counter())),
                                  damage_bins=[dict(b) for b in bins],
                                  target_bins=[dict(sum((collections.Counter(d['target_bins'][i]) for d in ds), collections.Counter())) for i in range(len(BINS)-1)],
                                  first_enemy_ranged_reach_s=distribution([d['first_enemy_ranged_reach_s'] for d in ds if d['first_enemy_ranged_reach_s'] is not None]),
                                  first_enemy_ranged_gun_damage_s=distribution([d['first_enemy_ranged_gun_damage_s'] for d in ds if d['first_enemy_ranged_gun_damage_s'] is not None])))
                diagnostics.extend(ds)
            print(arm, head, 'PASS', round(time.monotonic()-start, 1), 'seconds', flush=True)
    write('SPACING_RECOMPUTATION.json', dict(status='PASS', reviewed_commit=COMMIT, rows=comparisons,
                                          regular_wins=[d for d in diagnostics if d['elimination_win']],
                                          all_raw_hashes_and_requests_verified=True))
    write('COMPACT.json', dict(status='DONE', reviewed_commit=COMMIT, stored_data_only=True,
                              time_bins_s=list(BINS), geometry_clock='post-step every 30 ticks; living own and enemy guns; equal unit-snapshot weight',
                              direct_reach='centre distance <= native range + source radius + target radius',
                              front_definition='positive projection from enemy gun centroid toward own gun centroid; relative front, not fitted line normal',
                              cells=cells, fights=diagnostics, elapsed_seconds=time.monotonic()-start,
                              input_hashes={n: sha(SOURCE/n) for n in ('RAW_FILES_LOCAL.json', 'DECLARATION.json', 'FIGHTS.json', 'COMPACT.json', 'SUMMARY.json')},
                              script_sha256=sha(pathlib.Path(__file__))))


if __name__ == '__main__':
    main()
