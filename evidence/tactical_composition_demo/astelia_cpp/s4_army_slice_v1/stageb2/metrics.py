"""Stage A copy of A0 measure; only the native last-tick time boundary differs."""
import gzip
import json
import math
import statistics
import time

def ratio(a,b):
    return a/b if b else None

def last_tick_time(duration, dt):
    # World::done uses time >= duration; coreStep adds dt to time. Repeated
    # floating point addition can require one extra tick (150 s at 30 Hz).
    if not math.isfinite(duration) or not 0 < duration <= 150 or not math.isfinite(dt) or not 0 < dt <= .2 or duration/dt > 1e7:
        raise RuntimeError('invalid Stage A time envelope')
    t = 0.0
    while t < duration:t += dt
    return t

def measure(path,deadline=None,duration=150,dt=1/30):
    limit = last_tick_time(duration, dt)
    expected = 0.0
    last_step = -1
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
                if row['step'] != last_step+1 or not math.isfinite(row['t']) or abs(row['t']-expected)>1e-7:
                    raise RuntimeError('invalid observer tick time')
                last_step += 1
                expected += dt
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
    if not math.isfinite(t) or t<=0 or t>limit+1e-7 or abs(t-(expected-dt))>1e-7:
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
