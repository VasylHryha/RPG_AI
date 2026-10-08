"""Read-only paired rev-1 telemetry decomposition. Never launches a native host."""
import collections
import concurrent.futures
import gzip
import hashlib
import json
import math
from pathlib import Path
import statistics
import time

HERE = Path(__file__).resolve().parent
RAW = HERE / '_local/raw'
ROLES = ('melee', 'ranged', 'artillery')
ARMS = ('O', 'O+G', 'T')

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def fight(job):
    tag = job['tag']
    receipt_path = RAW / (tag + '_COMPLETE.json')
    receipt = json.loads(receipt_path.read_text())
    assert receipt['job'] == job
    raw = RAW / receipt['raw_file']
    assert digest(raw) == receipt['raw_sha256']
    counts = collections.Counter()
    sums = collections.Counter()
    prev_targets = {}
    prev_react = {}
    launched = collections.defaultdict(list)
    shell_hits = collections.Counter()
    shell_deaths = collections.Counter()
    previous_units = {}
    initial = None
    terminal = None
    shot_examples = []
    with gzip.open(raw, 'rt') as f:
        for line in f:
            row = json.loads(line)
            if not row.get('observerV1'):
                assert 'survivors' in row and terminal is None
                terminal = row
                continue
            units = {u[0]: u for u in row['units']}
            if initial is None:
                assert row['step'] == 0
                initial = units
            t = row['t']
            phase = 'early_0_30s' if t < 30 else 'late_30s_plus'
            event = next((e for e in row['shapeV6'] if e.get('a0Event')),None)
            planner = {e['id']:e for e in row['shapeV6'] if e.get('planner')}
            for launch in row['launches']:
                if launch[9]:
                    continue
                # Each physical shell has a source, born time and landing time.
                key = (launch[0], launch[5], launch[6])
                assert key not in launched[launch[0]]
                launched[launch[0]].append(key)
                counts[f'shells_launched/team{launch[2]}'] += 1
                shell_hits[key] += 0
                if launch[2] == 0:
                    gun = units.get(launch[0])
                    target = units.get(launch[1])
                    counts['own_shots'] += 1
                    if event and event['eligible']==1:
                        counts['single_event_shots'] += 1
                        old_target=previous_units.get(launch[1])
                        if old_target:
                            counts['single_event_target/'+ROLES[old_target[2]]] += 1
                            offset=math.hypot(launch[3]-old_target[3],launch[4]-old_target[4])
                            sums['single_event_aim_offset_pre_step_px'] += offset
                            counts['single_event_aim_rows'] += 1
                            counts['single_event_exact_named_target_point'] += offset<1e-8
                        if launch[0] in planner:
                            counts['single_event_teacher_family/'+planner[launch[0]]['family']] += 1
                    if launch[0] in planner and planner[launch[0]]['family']=='singles':
                        old_target=previous_units.get(launch[1])
                        if old_target:
                            counts['teacher_singles_pre_step_rows'] += 1
                            counts['teacher_singles_exact_named_target_point'] += math.hypot(launch[3]-old_target[3],launch[4]-old_target[4])<1e-8

                    if target:
                        counts['own_shot_target/' + ROLES[target[2]]] += 1
                        offset = math.hypot(launch[3]-target[3], launch[4]-target[4])
                        sums['aim_offset_current_target_px'] += offset
                        counts['aim_offset_rows'] += 1
                        if gun:
                            sums['shot_target_range_px'] += math.hypot(gun[3]-target[3], gun[4]-target[4])
                            counts['shot_range_rows'] += 1
                    if len(shot_examples) < 5:
                        shot_examples.append(launch)
            for d in row['damage']:
                friendly = d['sourceTeam'] == d['targetTeam']
                if d['targetTeam'] == 0:
                    origin = ('friendly_' if friendly else 'enemy_') + d['sourceRole']
                    victim = d['targetRole']
                    counts[f'hits_taken/{victim}/{origin}'] += 1
                    sums[f'damage_taken/{victim}/{origin}'] += d['dealt']
                    if d['died']:
                        counts['own_deaths'] += 1
                        counts['death_role/' + victim] += 1
                        counts[f'death_cause/{victim}/{origin}'] += 1
                        counts['death_time/' + phase] += 1
                        counts[f'death_role_time/{victim}/{phase}'] += 1
                if d['targetTeam'] == 1 and d['died']:
                    counts['enemy_deaths'] += 1
                    counts['enemy_death_role/' + d['targetRole']] += 1
                if d['sourceRole'] == 'artillery':
                    candidates = [k for k in launched[d['source']] if abs(k[2]-d['t']) < 1/30+1e-6 and k[2] <= d['t']+1e-6]
                    if len(candidates) == 1:
                        key = candidates[0]
                        if d['sourceTeam'] == 1 and d['targetTeam'] == 0:
                            shell_hits[key] += 1
                            shell_deaths[key] += d['died']
                    elif d['sourceTeam'] == 1 and d['targetTeam'] == 0:
                        counts['unmatched_enemy_shell_hits'] += 1
            for label in row['shapeV6']:
                if label.get('a0Label'):
                    role = label['role']; uid = label['id']
                    counts['labels/' + role] += 1
                    counts['react_ticks/' + role] += label['react']
                    counts['ready_ticks/' + role] += label['readyLabel']
                    counts['active_fire_ticks/' + role] += label['activeFire']
                    counts['react_activations/' + role] += label['react'] and not prev_react.get(uid, False)
                    prev_react[uid] = label['react']
                elif label.get('a0Event'):
                    counts['eligible_events'] += 1
                    counts['multi_events'] += label['eligible'] >= 2
                    counts['applied'] += label['applied']
                    counts['rejected'] += label['rejected']
                elif label.get('planner'):
                    counts['teacher_planner_family/' + label['family']] += 1
            for dodge in row['dodges']:
                if dodge[1] == 0:
                    counts['dodge_tick_records/' + ROLES[initial[dodge[0]][2]]] += 1
            # Position/target proxies sampled at 1 Hz on the same absolute window.
            # They are not latent v6 commitment or actual preparation commands.
            if row['step'] % 30 == 0 and 5 <= t <= 30+1e-6:
                enemy = [u for u in units.values() if u[1] == 1]
                for r, role in enumerate(ROLES):
                    own = [u for u in units.values() if u[1] == 0 and u[2] == r]
                    if not own:
                        continue
                    cx = statistics.mean(u[3] for u in own); cy = statistics.mean(u[4] for u in own)
                    sums['spread_rms_px/' + role] += math.sqrt(statistics.mean((u[3]-cx)**2+(u[4]-cy)**2 for u in own))
                    counts['spread_frames/' + role] += 1
                    targets = collections.Counter()
                    for u in own:
                        target = units.get(u[13])
                        if target and target[1] == 1:
                            targets[u[13]] += 1
                            distance = math.hypot(u[3]-target[3],u[4]-target[4])
                            sums['target_range_px/' + role] += distance
                            counts['target_rows/' + role] += 1
                            legal = u[8] <= distance <= u[7] if r == 2 else distance <= u[7]+u[6]+target[6]
                            counts['in_own_range/' + role] += legal
                            counts['out_of_range_target_rows/' + role] += not legal
                        if not target or target[1]!=1:counts['no_target_rows/' + role] += 1
                        if enemy:
                            distance = min(math.hypot(u[3]-e[3],u[4]-e[4]) for e in enemy)
                            sums['nearest_enemy_px/' + role] += distance
                            counts['nearest_rows/' + role] += 1
                            counts['close_contact_rows/' + role] += distance <= 80
                        if u[0] in prev_targets:
                            counts['switch_opportunities/' + role] += 1
                            counts['target_switches/' + role] += prev_targets[u[0]] != u[13]
                        prev_targets[u[0]] = u[13]
                        counts['prep_rows/' + role] += u[12] > 0
                        counts['unit_sample_rows/' + role] += 1
                    if targets:
                        n = sum(targets.values())
                        sums['focus_hhi/' + role] += sum((v/n)**2 for v in targets.values())
                        sums['max_target_share/' + role] += max(targets.values())/n
                        counts['focus_frames/' + role] += 1
            previous_units=units
    assert terminal and counts['own_deaths'] == receipt['stats']['own_deaths']
    assert len(initial) == 100
    assert sum(u[1] == 0 for u in units.values()) == terminal['survivors']
    # launched dict includes both sides; filter source using stable initial IDs.
    enemy_shells = {k: hits for k, hits in shell_hits.items() if initial[k[0]][1] == 1}
    hist = collections.Counter(enemy_shells.values())
    counts['enemy_shells_with_hits'] = sum(v > 0 for v in enemy_shells.values())
    counts['enemy_shell_hits_matched'] = sum(enemy_shells.values())
    counts['enemy_shells_2plus_hits'] = sum(v >= 2 for v in enemy_shells.values())
    counts['enemy_shells_3plus_hits'] = sum(v >= 3 for v in enemy_shells.values())
    counts['enemy_shell_deaths_matched'] = sum(shell_deaths.values())
    values = {'own_deaths': counts['own_deaths']}
    for role in ROLES:
        for family in ('death_role','react_activations','target_switches'):
            values[f'{family}/{role}'] = counts[f'{family}/{role}']
        for out, numerator, denominator in (
            ('spread_rms_px', 'spread_rms_px', 'spread_frames'),
            ('target_range_px','target_range_px','target_rows'),
            ('nearest_enemy_px','nearest_enemy_px','nearest_rows'),
            ('focus_hhi','focus_hhi','focus_frames'),
            ('max_target_share','max_target_share','focus_frames')):
            den=counts[f'{denominator}/{role}']
            values[f'{out}/{role}']=sums[f'{numerator}/{role}']/den if den else None
        for out,num,den in (
            ('react_fraction','react_ticks','labels'),('ready_fraction','ready_ticks','labels'),
            ('in_range_fraction','in_own_range','target_rows'),('legal_target_per_live_sample','in_own_range','unit_sample_rows'),('no_target_fraction','no_target_rows','unit_sample_rows'),('close_contact_fraction','close_contact_rows','nearest_rows'),
            ('prep_fraction','prep_rows','unit_sample_rows'),('switch_fraction','target_switches','switch_opportunities')):
            den=counts[f'{den}/{role}'];values[f'{out}/{role}']=counts[f'{num}/{role}']/den if den else None
    for num,den,out in (
        ('enemy_shell_hits_matched','shells_launched/team1','hits_per_enemy_shell_launched'),
        ('enemy_shell_hits_matched','enemy_shells_with_hits','hits_per_enemy_shell_hitting'),
        ('single_event_aim_offset_pre_step_px','single_event_aim_rows','single_event_aim_offset_pre_step_px'),
        ('aim_offset_current_target_px','aim_offset_rows','aim_offset_current_target_px'),
        ('shot_target_range_px','shot_range_rows','shot_target_range_px')):
        values[out]=(sums[num] if num in sums else counts[num])/counts[den] if counts[den] else None
    return {k:job[k] for k in ('tag','pair_key','panel','arm','tactic','seed','orientation')} | dict(
        counts=dict(counts),sums=dict(sums),values=values,enemy_shell_hit_histogram=dict(hist),
        raw_sha256=receipt['raw_sha256'],receipt_sha256=digest(receipt_path),seconds=receipt['seconds'],shot_examples=shot_examples)

def paired(rows, left, right):
    l={r['pair_key']:r for r in rows if r['arm']==left};r={r['pair_key']:r for r in rows if r['arm']==right}
    assert l.keys()==r.keys() and len(l)==50
    out={}
    fields = set().union(*(x['counts'] for x in rows))
    for kind, keys in (('counts',fields),('values',rows[0]['values'])):
        for key in sorted(keys):
            differences=[]
            for p in l:
                a=l[p][kind].get(key,0);b=r[p][kind].get(key,0)
                if a is not None and b is not None:differences.append(a-b)
            if not differences:continue
            n=len(differences);avg=statistics.mean(differences);sd=statistics.stdev(differences) if n>1 else 0
            out[kind+'/'+key]=dict(n=n,mean_left_minus_right=avg,total_left_minus_right=sum(differences),
                sd=sd,descriptive_ci95=[avg-1.96*sd/math.sqrt(n),avg+1.96*sd/math.sqrt(n)])
    return out

def main():
    start=time.monotonic();ledger_path=HERE/'_local/A0_LEDGER.json';ledger=json.loads(ledger_path.read_text())
    look=json.loads((HERE/'A0_LOOK_50.json').read_text())
    assert look['ledger_sha256']==digest(ledger_path)
    jobs=[j for j in ledger['jobs'] if j['stage']=='outcome' and j['index']<50]
    assert len(jobs)==300
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:
        rows=list(pool.map(fight,jobs))
    assert {r['tag']:r['receipt_sha256'] for r in rows}==look['completion_receipts']
    panels={}
    for panel in ('regular','C3'):
        group=[r for r in rows if r['panel']==panel];arms={}
        for arm in ARMS:
            subset=[r for r in group if r['arm']==arm];counts=collections.Counter();sums=collections.Counter();hist=collections.Counter()
            for r in subset:
                counts.update(r['counts']);sums.update(r['sums']);hist.update(r['enemy_shell_hit_histogram'])
            means={k:statistics.mean(vals) if (vals:=[r['values'][k] for r in subset if r['values'][k] is not None]) else None for k in subset[0]['values']}
            arms[arm]=dict(n=50,counts=dict(counts),sums=dict(sums),mean_per_fight_values=means,enemy_shell_hit_histogram=dict(hist))
        panels[panel]=dict(arms=arms,paired={f'{a} minus {b}':paired(group,a,b) for a,b in (('O','T'),('O+G','T'),('O','O+G'))})
    payload=dict(schema=1,status='POST_HOC_DIAGNOSIS_REV1_NOT_NEW_VERDICT',ledger_sha256=digest(ledger_path),
        look_sha256=digest(HERE/'A0_LOOK_50.json'),analysis_seconds=time.monotonic()-start,
        definitions={'early':'t < 30 seconds; fixed absolute boundary', 'state_sample':'1 Hz, absolute t in [5,30], post-step',
        'focus':'HHI of current live enemy target IDs per role, excluding absent targets',
        'spread':'RMS distance from live role centroid', 'shell_matching':'source ID and landing time within one 30 Hz tick; ambiguous hits counted separately',
        'aim_offset':'launch point minus current named target position in the post-step frame; not exact pre-release lead',
        'paired':'O minus T etc on all same-seed pairs; descriptive 1.96 SD/sqrt(n); no causal mediation or multiple-comparison inference'},
        unavailable=['latent commitment/phase','executed move goal and multiplier (decisionTrace=false)',
          'O planner family/score and rejected candidate points','exact pre-release target position/velocity and readiness','typed react primitive'],
        panels=panels,fights=rows)
    (HERE/'A0_DECOMPOSITION_COUNTS.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'seconds':payload['analysis_seconds'],'fights':len(rows),'panels':{p:{a:panels[p]['arms'][a]['mean_per_fight_values']['own_deaths'] for a in ARMS} for p in panels}}))

if __name__=='__main__':main()
