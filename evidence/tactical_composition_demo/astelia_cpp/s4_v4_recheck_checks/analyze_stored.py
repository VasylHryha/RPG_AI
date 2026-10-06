"""Read stored v4 raw exports only; no project imports or native execution.

Single process, paced at ~10% CPU duty (sleep follows every 100 lines).
Geometry is the preceding state dump (prepare geometry); current dump is
post-movement. Replay counts are descriptive and not validation estimates.
"""
import collections
import gzip
import hashlib
import json
import math
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def dist(a, b):
    return math.hypot(a['x'] - b['x'], a['y'] - b['y'])


def reach(a, b):
    if a['role'] == 'artillery':
        return 320.0
    return {'melee': 36., 'ranged': 259.}[a['role']] + a['debug']['r'] + b['debug']['r']


def analyze(arm):
    path = ROOT / 's4_v4_development/replays' / ('B_' + arm + '.jsonl.gz')
    c = collections.Counter()
    examples = collections.defaultdict(list)
    previous = current = {}
    modes = {}
    latent = {}
    snapshots = []
    next_snapshot = 0
    first_guns_only = None
    duty_start = time.monotonic()
    with gzip.open(path, 'rt') as stream:
        for line_number, line in enumerate(stream):
            row = json.loads(line)
            if 'state' in row:
                previous, current = current, {u['id']: u for u in row['state']['units']}
                t = row['state']['t']
                own = [u for u in current.values() if u['team'] == 0 and u['alive']]
                enemies = [u for u in current.values() if u['team'] == 1 and u['alive']]
                if t >= next_snapshot or not own:
                    snapshots.append(dict(t=t, own=len(own), enemy=len(enemies),
                                          enemy_guns=sum(u['role'] == 'artillery' for u in enemies)))
                    next_snapshot += 10
                if enemies and all(u['role'] == 'artillery' for u in enemies) and first_guns_only is None:
                    first_guns_only = dict(t=t, own=len(own), guns=len(enemies))
            if row.get('decisionDiagnostics'):
                guns = [u for u in previous.values() if u['team'] == 1 and u['alive'] and u['role'] == 'artillery']
                byid = {u['id']: u for u in row['units']}
                for event in row['holdEvents']:
                    reason = event['reason']
                    c['holds_' + reason] += 1
                    a, b = previous.get(event['id']), previous.get(event['enemy'])
                    oldmode = modes.get((event['id'], event['enemy']))
                    if reason == 'disappeared':
                        own_dead = not a or not a['alive']
                        enemy_dead = not b or not b['alive']
                        c['disappeared_own_only' if own_dead and not enemy_dead else
                          'disappeared_enemy_only' if enemy_dead and not own_dead else
                          'disappeared_both' if own_dead and enemy_dead else 'disappeared_neither'] += 1
                    elif reason == 'expired' and a and b:
                        pair = next((p for p in byid[event['id']]['pairs'] if p['enemy'] == b['id']), None)
                        danger = any(dist(a, g) <= 320 for g in guns)
                        c['expired_danger_any_gun'] += danger
                        c['expired_' + str(oldmode)] += 1
                        if pair and oldmode != pair['mode']:
                            c['expired_immediate_switch'] += 1
                        if b['role'] == 'artillery' and reach(a, b) < dist(a, b) <= 320:
                            c['expired_unanswered_gun_annulus'] += 1
                            if len(examples['expired_unanswered_gun_annulus']) < 5:
                                examples['expired_unanswered_gun_annulus'].append(dict(
                                    step=row['step'], prepareTime=row['prepareTime'],
                                    old_mode=oldmode, new_mode=pair['mode'] if pair else None,
                                    distance=dist(a, b), own_reach=reach(a, b), **event))
                switched_units = set()
                for d in row['units']:
                    a, post = previous[d['id']], current[d['id']]
                    c['unit_ticks'] += 1
                    old = latent.get(d['id'], d['c'] >= 0)
                    new = True if d['c'] > .2 else False if d['c'] < -.2 else old
                    c['latent_threshold_flips'] += d['id'] in latent and new != old
                    latent[d['id']] = new
                    focus = previous.get(d['focus'])
                    danger = any(dist(a, g) <= 320 for g in guns)
                    if focus:
                        c['focus_ticks'] += 1
                        c['focus_under_guns'] += danger
                        c['focus_non_gun_under_guns'] += danger and focus['role'] != 'artillery'
                        c['focus_c_below_escape_threshold'] += d['c'] < -.2
                        moving_toward = dist(post, focus) < dist(a, focus) - 1e-6
                        c['focus_toward_gun_while_out_of_own_reach'] += (focus['role'] == 'artillery' and
                            moving_toward and dist(a, focus) > reach(a, focus))
                        entering = any(dist(a, g) > 320 and dist(post, g) <= 320 for g in guns)
                        c['focus_gun_range_entry_ticks'] += entering
                        if entering and len(examples['focus_gun_range_entry']) < 5:
                            examples['focus_gun_range_entry'].append(dict(step=row['step'], id=a['id'],
                                focus=d['focus'], focus_role=focus['role'], c=d['c'],
                                before=[dict(id=g['id'],distance=dist(a,g)) for g in guns if dist(a,g)>320 and dist(post,g)<=320],
                                after_hp=post['hp'], before_hp=a['hp']))
                    if d['undefinedReason'] == 'zero_displacement':
                        c['zero_displacement'] += 1
                        wall = a['x'] <= a['debug']['r'] + 1e-6 or a['x'] >= 1200-a['debug']['r']-1e-6 or a['y'] <= a['debug']['r']+1e-6 or a['y'] >= 700-a['debug']['r']-1e-6
                        c['zero_wall'] += wall
                        c['zero_focus'] += focus is not None
                        c['zero_under_guns'] += danger
                        c['zero_active_hold'] += any(p['remainingHold'] > 0 for p in d['pairs'])
                        if len(examples['zero_displacement']) < 3:
                            examples['zero_displacement'].append(dict(step=row['step'],id=a['id'],x=a['x'],y=a['y'],
                                focus=d['focus'], c=d['c'], wall=wall, danger=danger,
                                active_hold=any(p['remainingHold']>0 for p in d['pairs'])))
                    for p in d['pairs']:
                        key = (a['id'], p['enemy'])
                        if key in modes and modes[key] != p['mode']:
                            c['pair_reversals'] += 1
                            switched_units.add(a['id'])
                        modes[key] = p['mode']
                c['unit_reversal_ticks'] += len(switched_units)
                started_pairs = {(e['id'], e['enemy']) for e in row['holdEvents'] if e['reason'] == 'started'}
                for event in row['holdEvents']:
                    if event['reason'] in ('expired', 'target_band'):
                        c[event['reason'] + '_same_tick_rearm'] += (event['id'], event['enemy']) in started_pairs
            if 'survivors' in row:
                terminal = row
            if line_number % 100 == 99:
                elapsed = time.monotonic() - duty_start
                time.sleep(min(1., elapsed * 9))
                duty_start = time.monotonic()
    # Exact stored diagnostic totals; errors abort instead of producing a receipt.
    reference = json.loads((ROOT/'s4_v4_development/DECISION_TRACE_SUMMARY.json').read_text())['v4']['B_'+arm+'.html']['counts']
    for key in ('unit_ticks', 'focus_ticks', 'pair_reversals', 'unit_reversal_ticks',
                'holds_started', 'holds_expired', 'holds_target_band', 'holds_disappeared'):
        assert c[key] == reference[key], (arm, key, c[key], reference[key])
    return dict(source=str(path.relative_to(ROOT)),sha256=sha(path),bytes=path.stat().st_size,
                counts=dict(c), examples=dict(examples), snapshots=snapshots,
                first_enemy_guns_only=first_guns_only,terminal=terminal)


if __name__ == '__main__':
    started = time.monotonic()
    result = dict(status='STORED_TRACE_ANALYSIS_ONLY', combat_executions=0,
                  geometry='previous raw state = prepare; current raw state = realized end of tick',
                  scope='one B regular seed/orientation per arm; descriptive, not population or causal attribution',
                  arms={arm:analyze(arm) for arm in ('resonator','morale')})
    result['wall_seconds'] = time.monotonic() - started
    (OUT/'STORED_TRACE_ANALYSIS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],wall_seconds=result['wall_seconds'],
                         counts={a:r['counts'] for a,r in result['arms'].items()})))
