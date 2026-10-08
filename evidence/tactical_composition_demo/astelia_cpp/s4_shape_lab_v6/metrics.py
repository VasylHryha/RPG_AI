"""Light event-seam measurements; both axes over ALL fights, ratio-of-totals."""
import collections
import gzip
import itertools
import json

FIELDS=('win','own_lost','enemy_kills','kills_per_own_death','damage_per_shell','damage_per_shot','kills_per_minute','shots_fired','firepower_utilization','in_range_seconds','rotation_activations')
def average(values):
    values=[v for v in values if v is not None]
    return dict(n=len(values),mean=sum(values)/len(values) if values else None)
def ratio(a,b):return a/b if b else None

def measure(path):
    initial=latest=terminal=None;previous_t=0;shells=[];shots={};shell_damage=shot_damage=enemy_damage=0;hits=collections.defaultdict(set);gun_kills=0;gun_seconds=ranged_seconds=inrange=ready=eligible=react_seconds=rotate_seconds=0
    floor_count=activations=predicted_deaths=rotation_trigger_contract_violations=0;triggered=set();base_predictions=[];planner_count=expected=0;role_start={};launch_index={};unassigned=0
    with gzip.open(path,'rt') as stream:
        for line in stream:
            row=json.loads(line)
            if row.get('observerV1'):
                if initial is None:
                    if row['step']!=0:raise RuntimeError('missing initial observer')
                    initial=row['units'];role_start={u[0]:u[2] for u in initial if u[1]==0}
                dt=row['t']-previous_t
                if dt<0:raise RuntimeError('nonmonotonic stream')
                previous=latest or initial;gun_seconds+=sum(u[1]==0 and u[2]==2 for u in previous)*dt;ranged_seconds+=sum(u[1]==0 and u[2]==1 for u in previous)*dt
                previous_t=row['t'];latest=row['units']
                for l in row.get('launches',[]):
                    if l[2]==0 and not l[9]:
                        key=(l[0],l[5],l[6])
                        if key in launch_index:raise RuntimeError('duplicate launch')
                        launch_index[key]=len(shells);shells.append(dict(source=l[0],born=l[5],at=l[6]))
                for sh in row.get('shotsV6',[]):
                    if sh[0] in shots:raise RuntimeError('duplicate shot')
                    shots[sh[0]]=sh
                for a in row.get('shapeV6',[]):
                    if a.get('plannerRejected'):continue
                    if a.get('planner'):planner_count+=1;expected+=a['expectedDamage'];continue
                    inrange+=int(a['inRange'])*dt;ready+=int(a['ready'])*dt;eligible+=int(a['eligible'])*dt;react_seconds+=int(a['react'])*dt;rotate_seconds+=int(a['rotating'])*dt;floor_count+=int(a['floor'])
                    if a['activation']:
                        activations+=1;triggered.add(a['id']);predicted_deaths+=int(a['D_base']>=a['hp']);rotation_trigger_contract_violations+=int(a['D_base']<a['hp'] or not a['D_p']<a['D_base']-1);base_predictions.append(dict(id=a['id'],t=a['t'],D_base=a['D_base'],D_p=a['D_p'],hp=a['hp'],participation=a['reason']))
                for d in row.get('damage',[]):
                    if d['sourceTeam']!=0 or d['targetTeam']!=1:continue
                    enemy_damage+=d['dealt']
                    if d['sourceRole']=='ranged':shot_damage+=d['dealt']
                    if d['sourceRole']=='artillery':
                        shell_damage+=d['dealt'];gun_kills+=int(d['died']);candidates=[i for i,s in enumerate(shells) if s['source']==d['source'] and -1e-8<=d['t']-s['at']<=1/30+1e-7]
                        if len(candidates)>1:raise RuntimeError('ambiguous shell attribution')
                        if candidates:hits[candidates[0]].add(d['target'])
                        else:unassigned+=d['dealt']
            elif 'survivors' in row:terminal=row
            else:raise RuntimeError('unexpected heavy stream')
    if initial is None or terminal is None:raise RuntimeError('incomplete fight')
    own_initial=sum(u[1]==0 for u in initial);enemy_initial=sum(u[1]==1 for u in initial);own_lost=own_initial-terminal['survivors'];enemy_kills=enemy_initial-terminal['enemySurvivors'];t=terminal['t'];landed=sum(s['at']<=t+1e-8 for s in shells)
    survivors=[dict(id=u[0],role=('melee','ranged','artillery')[u[2]]) for u in latest if u[1]==0]
    live={u['id'] for u in survivors}
    if len(survivors)!=terminal['survivors']:raise RuntimeError('survivor mismatch')
    stats=dict(win=terminal['enemySurvivors']==0 and terminal['survivors']>0 and t<150,timeout=t>=150,own_initial=own_initial,own_lost=own_lost,enemy_kills=enemy_kills,t_end=t,
        kills_per_own_death=ratio(enemy_kills,own_lost),enemy_damage=enemy_damage,kills_per_minute=ratio(enemy_kills*60,t),own_shells=len(shells),landed_shells=landed,shots_fired=len(shots),artillery_kills=gun_kills,
        shell_damage=shell_damage,shot_damage=shot_damage,damage_per_shell=ratio(shell_damage,len(shells)),damage_per_landed_shell=ratio(shell_damage,landed),damage_per_shot=ratio(shot_damage,len(shots)),targets_per_shell=ratio(sum(map(len,hits.values())),len(shells)),shells_per_kill=ratio(len(shells),gun_kills),fire_rate_shells_per_gun_minute=ratio(len(shells)*60,gun_seconds),
        gun_seconds=gun_seconds,ranged_seconds=ranged_seconds,in_range_seconds=inrange,ready_to_fire_seconds=ready,eligible_seconds=eligible,firepower_utilization=ratio(eligible,ready),reaction_override_seconds=react_seconds,ranged_deaths=sum(role==1 and id not in live for id,role in role_start.items()),engagement_floor_ticks=floor_count,
        rotation_activations=activations,counterfactual_predicted_deaths=predicted_deaths,triggered_units=len(triggered),triggered_unit_survivors=len(triggered&live),triggered_unit_survival=ratio(len(triggered&live),len(triggered)),rotation_trigger_contract_violations=rotation_trigger_contract_violations,rotation_seconds=rotate_seconds,
        false_extractions=dict(status='not_evaluated',reason='No untreated continuation; triggered survival cannot establish that extraction was unnecessary. Contract violations are reported separately.'),
        shots_lost='Paired shots_fired delta versus reference; no unobserved alternate-world count is invented.',rotation_counterfactuals=base_predictions,planner_assignments=planner_count,planner_expected_damage=expected,unassigned_shell_damage=unassigned,
        survivors_by_role={role:sum(u['role']==role for u in survivors) for role in ('melee','ranged','artillery')})
    return stats,survivors

def summarize(records):
    stats=[r['stats'] for r in records];totals={k:sum(s[k] for s in stats) for k in ('own_lost','enemy_kills','enemy_damage','own_shells','shots_fired','shell_damage','shot_damage','t_end','rotation_activations','triggered_units','triggered_unit_survivors','rotation_trigger_contract_violations','counterfactual_predicted_deaths','planner_assignments','ranged_seconds','eligible_seconds','ready_to_fire_seconds','in_range_seconds','reaction_override_seconds','ranged_deaths','engagement_floor_ticks','rotation_seconds')}
    return dict(n=len(stats),wins=sum(s['win'] for s in stats),losses=sum(not s['win'] and not s['timeout'] for s in stats),timeouts=sum(s['timeout'] for s in stats),
        own_deaths_per_fight=average([s['own_lost'] for s in stats]),own_losses_on_wins=average([s['own_lost'] for s in stats if s['win']]),own_losses_on_losses=average([s['own_lost'] for s in stats if not s['win'] and not s['timeout']]),own_losses_on_timeouts=average([s['own_lost'] for s in stats if s['timeout']]),own_losses_on_nonwins=average([s['own_lost'] for s in stats if not s['win']]),
        exchange_rate=ratio(totals['enemy_kills'],totals['own_lost']),zero_own_deaths=totals['own_lost']==0,kills_per_minute=ratio(totals['enemy_kills']*60,totals['t_end']),damage_per_shell=ratio(totals['shell_damage'],totals['own_shells']),damage_per_shot=ratio(totals['shot_damage'],totals['shots_fired']),
        false_extractions=dict(status='not_evaluated',reason='No untreated continuation; no causal false-extraction estimate.'),
        mechanism={k:average([s.get(k) for s in stats]) for k in ('targets_per_shell','shells_per_kill','fire_rate_shells_per_gun_minute','firepower_utilization','in_range_seconds','ready_to_fire_seconds','shots_fired','reaction_override_seconds','ranged_deaths','rotation_activations','counterfactual_predicted_deaths','triggered_unit_survival','rotation_trigger_contract_violations','rotation_seconds')},totals=totals,
        survivors_by_role={r:average([s['survivors_by_role'][r] for s in stats]) for r in ('melee','ranged','artillery')})

def paired(records,key='pair_key'):
    arms=sorted({r['meta']['arm'] for r in records});output={}
    for a,b in itertools.combinations(arms,2):
        cells=collections.defaultdict(dict)
        for r in records:
            if r['meta']['arm'] not in (a,b):continue
            p=cells[r['meta'][key]]
            if r['meta']['arm'] in p:raise RuntimeError('duplicate paired arm')
            p[r['meta']['arm']]=r['stats']
        matched=[p for p in cells.values() if len(p)==2]
        output[f'{b} minus {a}']=dict(n=len(matched),unmatched_pairs=sum(len(p)!=2 for p in cells.values()),differences={f:average([float(p[b][f])-float(p[a][f]) for p in matched if p[a][f] is not None and p[b][f] is not None]) for f in FIELDS},
            axis_plot=dict(own_deaths_saved=average([p[a]['own_lost']-p[b]['own_lost'] for p in matched]),enemy_kills_gained=average([p[b]['enemy_kills']-p[a]['enemy_kills'] for p in matched]),enemy_damage_gained=average([p[b]['enemy_damage']-p[a]['enemy_damage'] for p in matched])))
    return output
