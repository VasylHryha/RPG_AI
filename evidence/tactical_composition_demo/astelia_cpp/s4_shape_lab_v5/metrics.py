"""Light streaming V1 measurements, exact launch/landing exposure seam."""
import collections
import gzip
import itertools
import json

FIELDS=('win','own_lost','landing_spread_s','enemy_dodge_success','hits_per_own_shell','shells_per_kill','idle_seconds_per_gun','fired_shells_per_gun_minute')

def average(values):
    values=[v for v in values if v is not None]
    return dict(n=len(values),mean=sum(values)/len(values) if values else None)

def measure(path):
    initial=latest=terminal=None;launches={};volleys=collections.defaultdict(list);shells=[];idle={};gun_seconds=0;previous_t=0;low=collections.defaultdict(lambda:dict(gun_seconds=0.0,shells=0,idle=0.0));eligible=escaped=censored=unassigned=0;previous_guns=0
    with gzip.open(path,'rt') as stream:
        for line in stream:
            row=json.loads(line)
            if row.get('observerV1'):
                if initial is None:
                    if row['step']!=0:raise RuntimeError('missing initial observer')
                    initial=row['units']
                latest=row['units'];dt=row['t']-previous_t;previous_t=row['t']
                guns=[u for u in latest if u[1]==0 and u[2]==2];gun_seconds+=previous_guns*dt
                previous_guns=len(guns)
                if len(guns) in (1,2):low[len(guns)]['gun_seconds']+=len(guns)*dt
                for g in row.get('battery',[]):
                    delta=g[4]-idle.get(g[0],0);idle[g[0]]=g[4]
                    if len(guns) in (1,2):low[len(guns)]['idle']+=delta
                for l in row['launches']:
                    if l[2]==0 and not l[9]:
                        shells.append(dict(source=l[0],born=l[5],at=l[6],hits=set(),kills=0))
                        if len(guns) in (1,2):low[len(guns)]['shells']+=1
                for event in row.get('launchAudit',[]):
                    key=(event['source'],event['born'],event['at'])
                    if event['type']=='launch':
                        if key in launches:raise RuntimeError('duplicate launch exposure')
                        launches[key]=event
                        volleys[event['volley']].append(event['at'])
                    elif event['type']=='landing':
                        if key not in launches:raise RuntimeError('landing without launch')
                        e=launches[key]
                        if 'settled' in e:raise RuntimeError('duplicate landing')
                        if event['eligible']+event['censored']!=len(e['exposed']) or event['escaped']>event['eligible']:raise RuntimeError('exposure denominator mismatch')
                        e['settled']=True;eligible+=event['eligible'];escaped+=event['escaped'];censored+=event['censored']
                    else:raise RuntimeError('unknown audit')
                for d in row['damage']:
                    if d['sourceTeam']!=0 or d['targetTeam']!=1 or d['sourceRole']!='artillery' or d['dealt']<=0:continue
                    candidates=[s for s in shells if s['source']==d['source'] and -1e-8<=d['t']-s['at']<=1/30+1e-7]
                    if len(candidates)>1:raise RuntimeError('ambiguous own shell attribution')
                    if candidates:candidates[0]['hits'].add(d['target']);candidates[0]['kills']+=int(d['died'])
                    else:unassigned+=d['dealt']
            elif 'survivors' in row:terminal=row
            else:raise RuntimeError('unexpected heavy stream')
    if initial is None or terminal is None:raise RuntimeError('incomplete fight')
    landed=[s for s in shells if s['at']<=terminal['t']+1e-8];hits=sum(len(s['hits']) for s in landed);kills=sum(s['kills'] for s in landed)
    if len(launches)!=len(shells):raise RuntimeError('launch audit coverage mismatch')
    unresolved=sum('settled' not in e for e in launches.values())
    spreads=[max(v)-min(v) for v in volleys.values() if len(v)>=2 and all(t<=terminal['t']+1e-8 for t in v)]
    own_initial=sum(u[1]==0 for u in initial);gun_count=sum(u[1]==0 and u[2]==2 for u in initial)
    stats=dict(win=terminal['enemySurvivors']==0 and terminal['survivors']>0 and terminal['t']<150,timeout=terminal['t']>=150,own_initial=own_initial,own_lost=own_initial-terminal['survivors'],t_end=terminal['t'],
        own_shells=len(shells),own_shells_landed=len(landed),own_shells_unresolved=unresolved,hits=hits,artillery_kills=kills,
        landing_spread_s=average(spreads)['mean'],landing_spreads_s=spreads,multi_shell_volleys=len(spreads),single_shell_volleys=sum(len(v)==1 for v in volleys.values()),
        enemy_dodge_eligible=eligible,enemy_dodge_escaped=escaped,enemy_dodge_censored=censored,enemy_dodge_launch_exposed=eligible+censored,enemy_dodge_success=escaped/(eligible+censored) if eligible+censored else None,
        hits_per_own_shell=hits/len(landed) if landed else None,shells_per_kill=len(landed)/kills if kills else None,
        gun_seconds=gun_seconds,idle_seconds=sum(idle.values()),idle_seconds_per_gun=sum(idle.values())/gun_count if gun_count else None,
        fired_shells_per_gun_minute=len(shells)*60/gun_seconds if gun_seconds else None,low_gun_behaviour={str(k):v for k,v in low.items()},unassigned_own_artillery_damage=unassigned)
    survivors=[dict(id=u[0],role=('melee','ranged','artillery')[u[2]]) for u in latest if u[1]==0]
    if len(survivors)!=terminal['survivors']:raise RuntimeError('survivor identity/count drift')
    return stats,survivors

def summarize(records):
    stats=[r['stats'] for r in records]
    return dict(n=len(stats),wins=sum(s['win'] for s in stats),own_losses_on_wins=average([s['own_lost'] for s in stats if s['win']]),own_losses_on_nonwins=average([s['own_lost'] for s in stats if not s['win']]),
        mechanism={f:average([s[f] for s in stats]) for f in FIELDS[2:]},
        denominators={f:sum(s[f] for s in stats) for f in ('own_shells','own_shells_landed','own_shells_unresolved','hits','artillery_kills','enemy_dodge_eligible','enemy_dodge_launch_exposed','enemy_dodge_censored','gun_seconds','idle_seconds','multi_shell_volleys','single_shell_volleys','unassigned_own_artillery_damage')},
        low_gun_behaviour=[dict(tag=r['tag'],behaviour=r['stats']['low_gun_behaviour']) for r in records])

def paired(records,key='pair'):
    arms=sorted({r['meta']['arm'] for r in records});output={}
    for a,b in itertools.combinations(arms,2):
        cells=collections.defaultdict(dict)
        for r in records:
            if r['meta']['arm'] not in (a,b):continue
            p=cells[r['meta'][key]]
            if r['meta']['arm'] in p:raise RuntimeError('duplicate paired arm')
            p[r['meta']['arm']]=r['stats']
        matched=[p for p in cells.values() if len(p)==2]
        output[f'{b} minus {a}']=dict(n=len(matched),unmatched_pairs=sum(len(p)!=2 for p in cells.values()),differences={f:average([float(p[b][f])-float(p[a][f]) for p in matched if p[a][f] is not None and p[b][f] is not None]) for f in FIELDS})
    return output
