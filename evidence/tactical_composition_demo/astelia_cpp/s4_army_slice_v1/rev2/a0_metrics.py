"""All-fight decision-0034 numbers and explicitly censored elimination time."""
import gzip
import json
import math
import statistics
import time
from a0_common import ARMS, CELLS

def ratio(a,b):
    return a/b if b else None

def measure(path,deadline=None):
    initial = terminal = latest = None
    events = multi = joint = applied = rejected = labels = active = 0
    raw_distance = damage = 0.0
    roles={r:dict(rows=0,active=0,ready=0,raw_distance=0.0) for r in ("melee","ranged","artillery")}
    max_frame = 0
    with gzip.open(path,'rt') as stream:
        for line in stream:
            if deadline is not None and time.monotonic()>=deadline:raise TimeoutError("wall cap during raw validation")
            max_frame = max(max_frame,len(line.encode()))
            row = json.loads(line)
            if 'error' in row:
                raise RuntimeError('host error: '+str(row['error']))
            if row.get('observerV1'):
                if initial is None:
                    if row['step']!=0:
                        raise RuntimeError('missing initial frame')
                    initial = row['units']
                latest = row['units']
                for event in row.get('shapeV6',[]):
                    if event.get('a0Event'):
                        events += 1; multi += event['eligible']>=2; joint += event['joint']
                        applied += event['applied']; rejected += event['rejected']
                    if event.get('a0Label'):
                        labels += 1; active += event['activeFire']; raw_distance += event['rawToExecuted']
                        role=roles[event['role']];role['rows']+=1;role['active']+=event['activeFire'];role['ready']+=event['readyLabel'];role['raw_distance']+=event['rawToExecuted']
                damage += sum(d['dealt'] for d in row.get('damage',[]) if d['sourceTeam']==0 and d['targetTeam']==1)
            elif 'survivors' in row:
                if terminal is not None:
                    raise RuntimeError('duplicate terminal')
                terminal = row
            else:
                raise RuntimeError('unexpected host row')
    if initial is None or terminal is None or terminal.get('controllerStatus')!='completed':
        raise RuntimeError('incomplete or failed fight')
    if any(n!=50 for n in (sum(u[1]==0 for u in initial),sum(u[1]==1 for u in initial))):
        raise RuntimeError('A0 needs a full 50v50 army')
    for team,key in ((0,'survivors'),(1,'enemySurvivors')):
        if sum(u[1]==team for u in latest)!=terminal[key]:
            raise RuntimeError('terminal survivor mismatch')
    t = terminal['t']
    if not math.isfinite(t) or t<=0 or t>150+1e-6:
        raise RuntimeError('invalid end time')
    own = 50-terminal['survivors']; kills = 50-terminal['enemySurvivors']
    eliminated = terminal['enemySurvivors']==0
    return dict(own_deaths=own,enemy_kills=kills,enemy_damage=damage,t_end=t,
                kills_per_own_death=ratio(kills,own),kills_per_minute=kills*60/t,
                time_to_elimination=t if eliminated else None,
                elimination_time_censored=not eliminated,win=eliminated and terminal['survivors']>0,
                eligible_events=events,multi_gun_events=multi,joint_events=joint,
                multi_gun_event_share=ratio(multi,events),assignments=applied,rejected_assignments=rejected,
                active_fire_label_rate=ratio(active,labels),label_rows=labels,active_label_count=active,raw_distance_sum_px=raw_distance,per_role_labels=roles,
                raw_to_executed_mean_px=ratio(raw_distance,labels),max_frame_bytes=max_frame)

def mean(values):
    return statistics.mean(values) if values else None

def summary(records):
    rows = [r['stats'] for r in records]
    if not rows:
        return {'n':0}
    deaths=sum(r['own_deaths'] for r in rows);kills=sum(r['enemy_kills'] for r in rows)
    total_t=sum(r['t_end'] for r in rows);events=sum(r['eligible_events'] for r in rows)
    return dict(n=len(rows),own_deaths_per_fight=deaths/len(rows),enemy_kills_per_fight=kills/len(rows),
                kills_per_own_death=ratio(kills,deaths),zero_death_denominator=deaths==0,
                kills_per_minute=60*kills/total_t,enemy_damage_per_fight=mean([r['enemy_damage'] for r in rows]),
                eliminated_n=sum(not r['elimination_time_censored'] for r in rows),
                censored_n=sum(r['elimination_time_censored'] for r in rows),
                time_to_elimination_mean_eliminated_only=mean([r['time_to_elimination'] for r in rows if r['time_to_elimination'] is not None]),
                elimination_fraction=mean([not r['elimination_time_censored'] for r in rows]),
                restricted_elimination_time_150=mean([150 if r['elimination_time_censored'] else r['time_to_elimination'] for r in rows]),
                kills_saturation_fraction=mean([r['enemy_kills']==50 for r in rows]),
                wins=sum(r['win'] for r in rows),
                won_lost={name:dict(n=len(part),own_deaths_per_fight=mean([r['own_deaths'] for r in part]),
                                   enemy_kills_per_fight=mean([r['enemy_kills'] for r in part]))
                          for name,part in [('won',[r for r in rows if r['win']]),('nonwon',[r for r in rows if not r['win']])]},
                eligible_events=events,multi_gun_events=sum(r['multi_gun_events'] for r in rows),
                multi_gun_event_share=ratio(sum(r['multi_gun_events'] for r in rows),events),
                assignments=sum(r['assignments'] for r in rows),rejected_assignments=sum(r['rejected_assignments'] for r in rows),
                active_fire_label_rate=ratio(sum(r.get('active_label_count',0) for r in rows),sum(r.get('label_rows',0) for r in rows)),
                raw_to_executed_mean_px=ratio(sum(r.get('raw_distance_sum_px',0) for r in rows),sum(r.get('label_rows',0) for r in rows)),
                per_role_labels={role:dict(rows=sum(r.get('per_role_labels',{}).get(role,{}).get('rows',0) for r in rows),
                    active_fire_rate=ratio(sum(r.get('per_role_labels',{}).get(role,{}).get('active',0) for r in rows),sum(r.get('per_role_labels',{}).get(role,{}).get('rows',0) for r in rows)),
                    ready_opportunity_rate=ratio(sum(r.get('per_role_labels',{}).get(role,{}).get('ready',0) for r in rows),sum(r.get('per_role_labels',{}).get(role,{}).get('rows',0) for r in rows))) for role in ('melee','ranged','artillery')})

def contrast(records,reference,candidate):
    pairs={}
    for r in records:
        if r['arm'] not in (reference,candidate):continue
        cell=pairs.setdefault(r['pair_key'],{})
        if r['arm'] in cell:raise RuntimeError('duplicate arm in pair')
        cell[r['arm']]=r
    matched=[p for p in pairs.values() if len(p)==2]
    delta=[p[reference]['stats']['own_deaths']-p[candidate]['stats']['own_deaths'] for p in matched]
    n=len(delta);sd=statistics.stdev(delta) if n>1 else None
    ci=None if sd is None else [mean(delta)-1.96*sd/math.sqrt(n),mean(delta)+1.96*sd/math.sqrt(n)]
    left=summary([p[reference] for p in matched]);right=summary([p[candidate] for p in matched])
    exchange=None if not n or left['kills_per_own_death'] is None or right['kills_per_own_death'] is None else right['kills_per_own_death']-left['kills_per_own_death']
    return dict(n=n,unmatched_pairs=len(pairs)-n,deaths_saved=mean(delta),deaths_saved_sd=sd,
                deaths_saved_approx_95_ci=ci,exchange_gain=exchange,
                planned_death_mde_80pct={str(k):None if sd is None else 2.8*sd/math.sqrt(k) for k in (50,100)},
                enemy_kills_gained=None if not n else right['enemy_kills_per_fight']-left['enemy_kills_per_fight'],
                kills_per_minute_gain=None if not n else right['kills_per_minute']-left['kills_per_minute'],
                restricted_elimination_seconds_saved=None if not n else left['restricted_elimination_time_150']-right['restricted_elimination_time_150'])

def report(records,look=None):
    panels={}
    for panel in ('regular','C3'):
        selected=[r for r in records if r['panel']==panel]
        comparisons={f'{b} minus {a}':contrast(selected,a,b) for a,b in (('O','O+G'),('O','T'),('T','O+G'))}
        gain=comparisons['O+G minus O']
        complete=look is not None and all(sum(r['arm']==a for r in selected)==look for a in ARMS) and all(c['unmatched_pairs']==0 for c in comparisons.values())
        useful=complete and (gain['deaths_saved']>=2 or (gain['exchange_gain'] is not None and gain['exchange_gain']>=.10))
        harm=complete and (gain['deaths_saved']<=-2 or gain['enemy_kills_gained']<=-2)
        event_rate=summary([r for r in selected if r['arm']=='O']).get('multi_gun_event_share')
        gap=comparisons['T minus O']
        decomposition_harm=complete and (gap['deaths_saved']>=2 or gap['enemy_kills_gained']>=2)
        panels[panel]=dict(complete=complete,decomposition_harm=decomposition_harm,arms={a:summary([r for r in selected if r['arm']==a]) for a in ARMS},
                          comparisons=comparisons,useful_effect=useful,harm=harm,
                          multi_gun_floor_pass=event_rate is not None and event_rate>=.01,
                          per_tactic={cell:{'arms':{a:summary([r for r in selected if r['tactic']==cell and r['arm']==a]) for a in ARMS},
                                            'O+G minus O':contrast([r for r in selected if r['tactic']==cell],'O','O+G')}
                                      for cell in (('regular',) if panel=='regular' else CELLS)})
    complete=all(p['complete'] for p in panels.values())
    parked=complete and (any(p['harm'] or not p['multi_gun_floor_pass'] for p in panels.values()) or
                       (look==100 and not all(p['useful_effect'] for p in panels.values())))
    return dict(status='COMPLETE' if complete else 'PARTIAL',look=look,panels=panels,
                training_readiness='BLOCKED_UNIT_DECOMPOSITION' if complete and any(p['decomposition_harm'] for p in panels.values()) else 'UNITS_ONLY_LEADER_PARKED' if parked else 'FUTURE_DESIGN_GATE_ONLY_NO_TRAINING_AUTHORIZATION' if complete else 'UNRESOLVED',
                unit_decision='REVISE_O_BEFORE_TRAINING' if complete and any(p['decomposition_harm'] for p in panels.values()) else 'DECOMPOSITION_NOT_HARMFUL_AT_THIS_LOOK' if complete else 'UNRESOLVED',
                leader_decision='PARK_REPORT_TO_OWNER_UNITS_ALONE_PROCEEDS' if parked else
                                'REVISE_UNIT_ORACLE_BEFORE_LEADER_DECISION' if complete and any(p['decomposition_harm'] for p in panels.values()) else 'SCRIPT_CEILING_PASSED_FUTURE_LEADER_DESIGN_ONLY' if complete and look==100 else 'CONTINUE_TO_100' if complete else 'UNRESOLVED',
                series_streak={'status':'not_run','reason':'A0 contains independent fights, no series'},
                multi_single_gain_attribution={'status':'not_identified','reason':'Event share and assignment counts are measured; fight outcomes cannot be causally divided between events in these three arms.'})
