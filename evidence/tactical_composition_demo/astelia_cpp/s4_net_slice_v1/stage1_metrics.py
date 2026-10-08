"""Mechanism measurements from decision intents and exact native shell impacts.

Impact events precede native damage at the same post-walk positions. The reported
damage is the engine's raw HP-capped attack statistic; it is not an attribution
inferred from snapshot HP differences. No gun/tick is a statistical replicate.
"""
from collections import Counter,defaultdict
import math
from stage1_data import frame_rows
from stage1_arithmetic import slots,opportunities


def metrics(path,row):
    counts=Counter(); volley=defaultdict(list); casts={}; target_for_shell={}; terminal=None
    for frame in frame_rows(path):
        if frame.get('terminal'):
            terminal=frame; break
        joint=frame['joint']; post=frame.get('post_joint')
        counts['gun_ticks']+=len(frame['gun_ids'])
        for e in frame['events']:
            v=e['value']; stage=e['stage']
            if stage=='intent':
                if joint is None:
                    raise ValueError('intent lacks public context')
                counts['gun_decisions']+=1; counts['targeted_decisions']+=int(v['target']!=0)
                counts['categorical_moving_decisions']+=int(v['move_index']!=0)
                counts['start_opportunities']+=int(v['start_opportunity']); counts['release_opportunities']+=int(v['release_opportunity'])
                s={**joint,'self':e['unit']}; _,enemies,_,_=slots(s)
                target=next((u for u in enemies if u['id']==v['target']),None)
                start,release=opportunities(s,target,v['aim'])
                illegal=bool(v['target'] and target is None) or bool(v['start'] and not start) or bool(v['release'] and not release)
                counts['illegal_or_unsupported_decision_attempts']+=int(illegal)
            elif stage=='cast_start':
                casts[e['unit'],e['cast_tick']]=v['target']; counts['cast_starts']+=1
            elif stage=='launch':
                counts['launches']+=1; volley[e['volley']].append(v)
                key=(e['unit'],v['born'],v['landing_at'],tuple(v['aim']))
                target_for_shell[key]=casts.get((e['unit'],e['cast_tick']),0)
            elif stage=='shell_impact':
                if v['source_team']==0:
                    counts['own_shell_arrivals']+=1
                    counts['native_enemy_damage']+=sum(h['damage'] for h in v['hits'] if h['team']==1)
                    counts['native_friendly_damage']+=sum(h['damage'] for h in v['hits'] if h['team']==0)
                    key=(e['unit'],v['born'],v['landing_at'],tuple(v['aim']))
                    target=target_for_shell.get(key,0)
                    living=next((u for u in v['living_targets'] if u['id']==target),None)
                    if living is None:
                        counts['own_shell_target_censored']+=1
                    else:
                        counts['own_shell_target_arrivals']+=1
                        counts['enemy_target_dodged_shell']+=int(not any(h['id']==target for h in v['hits']))
                else:
                    counts['enemy_shell_arrivals']+=1
                    counts['own_gun_hits_by_enemy_shell']+=sum(h['team']==0 and h['gun'] for h in v['hits'])
                    counts['own_body_hits_by_enemy_shell']+=sum(h['team']==0 for h in v['hits'])
            elif stage in ('cancel','consumed_without_launch','act_veto'):
                counts[stage]+=1
            elif stage=='threat_overflow':
                counts['own_shell_overflow']+=v['own_shell']; counts['enemy_threat_overflow']+=v['enemy_threats']
            elif stage=='projection':
                raw,effective=v['raw'],v['effective']
                counts['ordinary_finite_projection_gun_ticks']+=int(math.dist(raw['goal'],effective['goal'])>1e-9 or raw['multiplier']!=effective['multiplier'])
                counts['cast_range_or_absence_veto_gun_ticks']+=int(v['reason'] in ('aim_range','target_range','absent_target'))
                counts['body_blocked_gun_ticks']+=int(v['reason']=='body')
        phases=frame.get('phase_state',[])
        if phases:
            counts['phase_order_sum']+=abs(sum(complex(math.cos(p),math.sin(p)) for _,p in phases))/len(phases)
            counts['phase_order_ticks']+=1
        if joint is not None and post is not None:
            before={u['id']:u for u in joint['units']}; after={u['id']:u for u in post['units']}
            for id,drift in zip(frame['gun_ids'],frame.get('phase_motion',[])):
                if id in after and id in before:
                    delta=(after[id]['x']-before[id]['x'],after[id]['y']-before[id]['y'])
                    counts['command_realized_dot_sum']+=sum(a*b for a,b in zip(drift,delta))
                    counts['command_realized_pairs']+=1
    if terminal is None or 'native_shell_totals' not in terminal:
        raise ValueError('supplemental native impact/terminal diagnostics required')
    totals=terminal['native_shell_totals']
    if abs(totals['enemy_damage']-counts['native_enemy_damage'])>1e-8 or totals['resolved_shells']!=counts['own_shell_arrivals']:
        raise ValueError('native impact/terminal reconciliation failed')
    initial_enemy=row['guns']+(2 if row['cell']=='D1-static' else 0)
    deaths=row['guns']-terminal['own_guns_alive']; kills=initial_enemy-terminal['enemy_alive']; seconds=terminal['time']
    ratio=lambda n,d:n/d if d else None
    illegal=ratio(counts['illegal_or_unsupported_decision_attempts'],counts['gun_decisions'])
    activated=counts['launches']>0 and counts['targeted_decisions']>0 and illegal is not None and illegal<.01
    spreads=[dict(launch_seconds=max(e['born'] for e in es)-min(e['born'] for e in es),
                  landing_seconds=max(e['landing_at'] for e in es)-min(e['landing_at'] for e in es)) for es in volley.values() if len(es)>=2]
    return dict(draw=row['draw'],arm=row['arm'],cell=row['cell'],guns=row['guns'],orientation=row['orientation'],counts=dict(counts),
                own_gun_deaths=deaths,enemy_kills=kills,seconds=seconds,survival_loss_fraction=deaths/row['guns'],offense_kill_fraction=kills/initial_enemy,
                kills_per_minute=60*kills/seconds,exchange=ratio(kills,deaths),enemy_damage=totals['enemy_damage'],friendly_damage=totals['friendly_damage'],
                damage_per_shell=ratio(totals['enemy_damage'],counts['launches']),shells_per_kill=ratio(counts['launches'],kills),
                fire_rate_per_gun_minute=ratio(60*counts['launches'],seconds*row['guns']),launch_opportunity_fraction=ratio(counts['launches'],counts['start_opportunities']),
                enemy_dodge_success=ratio(counts['enemy_target_dodged_shell'],counts['own_shell_target_arrivals']),
                own_gun_hits_per_enemy_shell=ratio(counts['own_gun_hits_by_enemy_shell'],counts['enemy_shell_arrivals']),
                own_bodies_hit_per_enemy_shell=ratio(counts['own_body_hits_by_enemy_shell'],counts['enemy_shell_arrivals']),
                unresolved_own_shells=counts['launches']-counts['own_shell_arrivals'],illegal_support_fraction=illegal,volley_spreads=spreads,
                reading='ACTIVATES' if activated else 'MECHANISM_REVIEW_REQUIRED',
                measurement_limits='damage is native raw HP-capped shell attack damage; dodge is original living target outside blast at exact post-walk native impact, deaths censored; unresolved shells at terminal retained separately; command-realized geometry includes native collision separation')
