"""Streaming section-4 measures. HP damage, seconds and unit counts have explicit denominators.
The unchanged scorecard's historical 50-unit and 10-gun denominators are auxiliary only.
"""
import collections
import gzip
import json
import math

def measure(path):
    previous = None
    terminal = None
    initial = {}
    latest = {}
    role = {0:'melee',1:'ranged',2:'artillery'}
    deaths = collections.Counter()
    damage_guns = collections.Counter()
    own_gun_damage = 0.0
    own_gun_to_guns = 0.0
    enemy_gun_count = None
    enemy_gun_wipe = None
    shells = []
    slow_fields = 0
    reach_seconds = alive_seconds = 0.0
    out_ids = set()
    all_gun_damage = all_gun_to_guns = 0.0
    with gzip.open(path,'rt') as f:
        for line in f:
            r=json.loads(line)
            if r.get('observerV1'):
                us=r['units']
                if r['step']==0:
                    initial={u[0]:u for u in us}
                    enemy_gun_count=sum(u[1]==1 and u[2]==2 for u in us)
                if previous is not None:
                    dt=r['t']-previous['t']
                    enemies=[u for u in previous['units'] if u[1]==1]
                    for u in previous['units']:
                        if u[1]!=0: continue
                        alive_seconds+=dt
                        legal=any((u[8]<=math.hypot(u[3]-e[3],u[4]-e[4])<=u[7]) if u[2]==2 else
                                  math.hypot(u[3]-e[3],u[4]-e[4])-u[6]-e[6]<=u[7] for e in enemies)
                        if legal: reach_seconds+=dt
                        elif enemies: out_ids.add(u[0])
                for l in r['launches']:
                    if l[9]:
                        slow_fields += 1
                        continue  # Slow field creation is not a damaging shell.
                    shells.append(dict(source=l[0],team=l[2],at=l[6],targets=set(),any_hit=False,damage=0.0))
                for d in r['damage']:
                    st,tt,sr,tr=d['sourceTeam'],d['targetTeam'],d['sourceRole'],d['targetRole']
                    if st==0 and tt==1 and sr=='artillery':
                        all_gun_damage+=d['dealt']
                        if tr=='artillery': all_gun_to_guns+=d['dealt']
                        if enemy_gun_count:
                            own_gun_damage+=d['dealt']
                            if tr=='artillery':own_gun_to_guns+=d['dealt']
                    if st==1 and tt==0 and tr=='artillery':damage_guns[sr]+=d['dealt']
                    if sr=='artillery':
                        # One native non-ability shell per source per impact tick; match launch due by this tick.
                        candidates=[s for s in shells if s['source']==d['source'] and s['at']<=d['t']+1e-8 and d['t']-s['at']<=1/30+1e-7]
                        if len(candidates)>1:raise RuntimeError('ambiguous shell impact identity')
                        if candidates:
                            s=candidates[0]
                            if d['dealt']>0:s['any_hit']=True
                            if st!=tt and d['dealt']>0:s['targets'].add(d['target']);s['damage']+=d['dealt']
                    if d['died']:
                        deaths[(tt,tr)]+=1
                        if tt==1 and tr=='artillery':
                            enemy_gun_count-=1
                            if not enemy_gun_count:enemy_gun_wipe=d['t']
                latest={u[0]:u for u in us}
                previous=r
            elif 'survivors' in r:
                terminal=r
    if terminal is None or previous is None:raise RuntimeError('incomplete observer fight')
    counts=collections.Counter((u[1],role[u[2]]) for u in initial.values())
    own_initial=sum(u[1]==0 for u in initial.values())
    enemy_initial=sum(u[1]==1 for u in initial.values())
    landed=[s for s in shells if s['at']<=terminal['t']+1e-8]
    enemy_shells=[s for s in landed if s['team']==1]
    own_shells=[s for s in landed if s['team']==0]
    losses=own_initial-terminal['survivors']
    killed=enemy_initial-terminal['enemySurvivors']
    gun_loss=counts[(0,'artillery')]-sum(u[1]==0 and u[2]==2 for u in latest.values())
    melee_left=sum(u[1]==0 and u[2]==0 for u in latest.values())
    stats=dict(win=terminal['enemySurvivors']==0 and terminal['survivors']>0 and terminal['t']<150,
               timeout=terminal['t']>=150, t_end=terminal['t'], t_elimination=terminal['t'] if terminal['enemySurvivors']==0 and terminal['survivors']>0 and terminal['t']<150 else None,
               own_initial=own_initial, enemy_initial=enemy_initial, own_lost=losses,enemy_killed=killed,
               enemy_guns_killed=deaths[(1,'artillery')], own_guns_lost=gun_loss,t_enemy_guns_wiped=enemy_gun_wipe,
               gun_damage_on_enemy_guns_share_while_guns_alive=own_gun_to_guns/own_gun_damage if own_gun_damage else None,
               gun_damage_on_enemy_guns_share_all=all_gun_to_guns/all_gun_damage if all_gun_damage else None,
               own_shells_landed=len(own_shells),own_shells_no_hit=sum(not s['any_hit'] for s in own_shells),
               shells_unresolved=len(shells)-len(landed),slow_field_launches=slow_fields, enemy_shells_landed=len(enemy_shells),
               own_units_hit_per_enemy_shell=sum(len(s['targets']) for s in enemy_shells)/len(enemy_shells) if enemy_shells else None,
               damage_taken_per_enemy_shell=sum(s['damage'] for s in enemy_shells)/len(enemy_shells) if enemy_shells else None,
               damage_to_own_guns_by_source=dict(damage_guns),
               escorts_lost=deaths[(0,'ranged')],enemy_ranged_killed=deaths[(1,'ranged')],
               exchange_ratio=killed/losses if losses else None,exchange_zero_loss=losses==0,
               melee_survivors=melee_left,alive_unit_seconds=alive_seconds,in_reach_unit_seconds=reach_seconds,
               firepower_retained=reach_seconds/alive_seconds if alive_seconds else None,
               units_out_of_fight=len(out_ids),out_of_fight_ids=sorted(out_ids))
    survivors=[dict(id=u[0],role=role[u[2]],kind=('brute','spitter','shaman')[u[2]],hp=u[5]) for u in latest.values() if u[1]==0]
    # Kind is taken from trace state when nondefault; default catalog bodies in approved drills.
    return stats,survivors
