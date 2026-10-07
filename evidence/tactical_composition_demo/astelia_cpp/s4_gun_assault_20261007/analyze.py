"""Stored-only all-tick analysis. Descriptive associations, never causal ablation."""
import collections,gzip,json,math,statistics,time
from common import *

def dist(a,b):return math.hypot(a[3]-b[3],a[4]-b[4])
def band(g,u):return g[8]<=dist(g,u)<=g[7]
def reachable(u,g):
 d=dist(u,g)
 return u[8]<=d<=u[7] if u[2]==2 else d<=u[7]+u[6]+g[6]
def phase(t):return 'early_0_20' if t<20 else 'middle_20_60' if t<60 else 'late_60_end'
def stats(v):
 v=sorted(v)
 return dict(n=len(v),mean=statistics.mean(v) if v else None,median=statistics.median(v) if v else None,min=min(v) if v else None,max=max(v) if v else None)
def angle(u,g,others):
 if not others:return None
 dx=u[3]-g[3];dy=u[4]-g[4];ax=statistics.mean(x[3] for x in others)-g[3];ay=statistics.mean(x[4] for x in others)-g[4]
 d=math.hypot(dx,dy)*math.hypot(ax,ay)
 return math.degrees(math.acos(max(-1,min(1,(dx*ax+dy*ay)/d)))) if d else None

def analyze_fight(record):
 deaths=[];gun_deaths=[];approaches=[];episodes={};frames=collections.deque();launches=collections.deque()
 totals=collections.Counter();role_amount=collections.Counter();previous=None;last_t=0;gun_peak={};gun_integral=collections.Counter();gun_duration=collections.Counter()
 geometry=collections.defaultdict(list);dodge_n=collections.Counter();dodge_displacements=[];pending_dodge={};damage_all=[];gun_damage=collections.Counter();inside_peak=collections.Counter()
 with gzip.open(HERE/record['raw_file'],'rt') as f:
  for line in f:
   row=json.loads(line)
   if not row.get('observerV1'):continue
   t=row['t'];dt=t-last_t;units={u[0]:u for u in row['units']};own=[u for u in units.values() if u[1]==0];guns=[u for u in units.values() if u[1]==1 and u[2]==2]
   if previous is None:
    initial=units;previous=units;last_t=t;frames.append((t,units));continue
   prev=previous;pre_guns=[g for g in prev.values() if g[1]==1 and g[2]==2];pre_non_guns=any(u[1]==1 and u[2]!=2 for u in prev.values())
   for l in row['launches']:launches.append((t,l))
   for d in row['damage']:
    assert d['t']==t and d['amount']>=d['dealt']>=0
    assert math.isclose(d['distance'],math.hypot(d['sourceX']-d['targetX'],d['sourceY']-d['targetY']),abs_tol=1e-9)
    totals['events']+=1;totals['dealt_'+str(d['sourceTeam'])+'_'+str(d['targetTeam'])]+=d['dealt']
    damage_all.append(d)
    if d['targetTeam']==1 and d['targetRole']=='artillery' and d['sourceTeam']==0:gun_damage[d['source']]+=d['dealt']
    ep=episodes.get((d['source'],d['target']))
    if ep:ep['damage_to_gun']+=d['dealt']
    if d['died']:
     assert d['killer']==d['source'];d=dict(d,phase=phase(t),gun_only_before_tick=not pre_non_guns)
     if d['targetTeam']==0:deaths.append(d)
     if d['targetTeam']==1 and d['targetRole']=='artillery':
      g=list(prev[d['target']]);g[3:5]=[d['targetX'],d['targetY']];other=[[x[0],1,2,x[1],x[2],0,0,x[3],x[4]] for x in d['lethalGunSupport']]
      window=[(ft,us) for ft,us in frames if ft>=t-3]
      reach_samples=[];inside_samples=[];angles=[];sets=[]
      for ft,us in window:
       if g[0] not in us:continue
       gg=us[g[0]];attackers=[u for u in us.values() if u[1]==0 and reachable(u,gg)]
       reach_samples.append(len(attackers));inside_samples.append(sum(u[1]==0 and band(gg,u) for u in us.values()))
       sets.append([ft,[u[0] for u in attackers]])
       og=[x for x in us.values() if x[1]==1 and x[2]==2 and x[0]!=g[0]]
       angles.extend(a for u in attackers if (a:=angle(u,gg,og)) is not None)
      relevant=[l for lt,l in launches if lt>=t-3 and l[0]==g[0] and not l[9]]
      own_killer=dict(id=d['source'],role=d['sourceRole'],team=d['sourceTeam'],distance=d['distance'])
      source_position=[d['source'],d['sourceTeam'],0,d['sourceX'],d['sourceY']]
      gun_deaths.append(dict(event=d,killer=own_killer,prekill_seconds=3,reach_count=stats(reach_samples),
       max_simultaneous_within_reach=max([*reach_samples,len(d['lethalGunInReach'])],default=0),
       exact_lethal_in_reach_ids=d['lethalGunInReach'],exact_lethal_inside_band_ids=d['lethalGunInsideBand'],exact_lethal_support=d['lethalGunSupport'],within_reach_before_lethal_tick=reach_samples[-1] if reach_samples else None,
       inside_gun_band_count=stats(inside_samples),reach_attackers_by_tick=sets,
       attacker_angles_degrees=stats(angles),killer_angle_degrees=angle(source_position,g,other),
       other_guns_alive=len(other),other_guns_covering_killer=sum(band(x,source_position) for x in other),
       gun_launches_previous_3s=relevant,gun_was_shelling_other_target=any(l[1] not in (0,d['source']) for l in relevant),
       target_identity_semantics='current unit target at launch, not guaranteed recipient of splash or barrage',
       damage_sources_previous_3s=[dict(source=x['source'],sourceRole=x['sourceRole'],sourceTeam=x['sourceTeam'],dealt=x['dealt'],distance=x['distance'],t=x['t']) for x in damage_all if x['t']>=t-3 and x['target']==g[0]]))
   while launches and launches[0][0]<t-3:launches.popleft()
   # Record all entries for regular, including episodes which never target/fire at this gun.
   if record['head']=='regular':
    for entry in row['entries']:
     key=(entry['unit'],entry['gun'])
     if key in episodes:
      episodes[key].update(exit_t=t,duration=t-episodes[key]['enter_t'],outcome='recrossed_same_tick_or_band_reentry');del episodes[key]
     pos=[entry['unit'],0,0,*entry['pos']];gp=[entry['gun'],1,2,*entry['gunPos']];others=[[0,1,2,*x] for x in entry['otherGuns']]
     ep=dict(unit=entry['unit'],role=entry['role'],gun=entry['gun'],enter_t=t,entry_distance=entry['distance'],entry_angle_degrees=angle(pos,gp,others),
        entry_other_gun_cover=entry['cover'],max_other_gun_cover=entry['cover'],
        max_simultaneous_approachers=1,max_simultaneous_within_reach=len(entry['inReach']),damage_to_gun=0,
        entered_own_reach=entry['unit'] in entry['inReach'],entry_position=entry['pos'],gun_position=entry['gunPos'],
        exact_entry_in_reach_ids=entry['inReach'],exact_entry_inside_band_ids=entry['insideBand'])
     ep['damage_to_gun']=sum(d['dealt'] for d in row['damage'] if d['source']==key[0] and d['target']==key[1])
     episodes[key]=ep;approaches.append(ep)
    for key,ep in list(episodes.items()):
     u=units.get(key[0]);g=units.get(key[1]);other=[x for x in guns if x[0]!=key[1]]
     outcome=None
     if u is None and g is None:outcome='attacker_and_gun_died_same_tick'
     elif u is None:outcome='attacker_died'
     elif g is None:outcome='gun_died'
     elif not band(g,u):outcome='left_gun_band'
     if outcome:ep.update(exit_t=t,duration=t-ep['enter_t'],outcome=outcome);del episodes[key];continue
     ep['entered_own_reach']|=reachable(u,g)
     ep['max_other_gun_cover']=max(ep['max_other_gun_cover'],sum(band(x,u) for x in other))
     ep['max_simultaneous_approachers']=max(ep['max_simultaneous_approachers'],sum(k[1]==key[1] and k[0] in units and band(g,units[k[0]]) for k in episodes))
     ep['max_simultaneous_within_reach']=max(ep['max_simultaneous_within_reach'],sum(reachable(a,g) for a in own))
   for g in guns:
    n=sum(reachable(a,g) for a in own);gun_peak[g[0]]=max(gun_peak.get(g[0],0),n);gun_integral[g[0]]+=n*dt;gun_duration[g[0]]+=dt
    inside_peak[g[0]]=max(inside_peak[g[0]],sum(band(g,a) for a in own))
    others=[x for x in guns if x[0]!=g[0]]
    if others:geometry['gun_nearest_spacing'].append(min(dist(g,x) for x in others))
    geometry['gun_band_overlap_count'].append(sum(dist(g,x)<=g[7]+x[7] for x in others))
   for u in units.values():
    if u[1]!=1:continue
    geometry['enemy_has_slot'].append(int(u[9]))
    if u[9]:geometry['enemy_slot_offset'].append(math.hypot(u[3]-u[10],u[4]-u[11]))
   for d in row['dodges']:
    dodge_n['calls']+=1;dodge_n['team_'+str(d[1])]+=1
    if d[0] in units:
     actual=units[d[0]];delta=[actual[3]-d[2],actual[4]-d[3]];goal=[d[4]-d[2],d[5]-d[3]]
     if math.hypot(*delta)>.1 and delta[0]*goal[0]+delta[1]*goal[1]>0:dodge_n['same_tick_motion_toward_goal']+=1;dodge_n['same_tick_motion_team_'+str(d[1])]+=1
   frames.append((t,units))
   while frames and frames[0][0]<t-3:frames.popleft()
   damage_all=[d for d in damage_all if d['t']>=t-3]
   previous=units;last_t=t
 for ep in episodes.values():ep.update(exit_t=last_t,duration=last_t-ep['enter_t'],outcome='termination_censored')
 starts=collections.defaultdict(lambda:collections.defaultdict(list))
 for ep in approaches:starts[ep['gun']][ep['enter_t']].append(ep);ep['entry_inside_band_count']=len(ep['exact_entry_inside_band_ids'])
 for times in starts.values():
  window=collections.deque();active=collections.Counter()
  for t,entries in sorted(times.items()):
   while window and window[0][0]<t-3:
    _,ids=window.popleft()
    for unit in ids:
     active[unit]-=1
     if not active[unit]:del active[unit]
   ids={ep['unit'] for ep in entries};active.update(ids);window.append((t,ids))
   for ep in entries:ep['approach_starts_previous_3s']=len(active)
 result=record['summary'];own_end=sum(u[1]==0 for u in previous.values());enemy_end=sum(u[1]==1 for u in previous.values())
 assert own_end==result['survivors'] and enemy_end==result['enemySurvivors']
 assert len(deaths)==50-own_end and len(gun_deaths)==10-result['artilleryAlive'][1]
 for a,b,field in [(0,1,'crossTeamDealt'),(1,0,'crossTeamDealt'),(0,0,'friendlyDealt'),(1,1,'friendlyDealt')]:
  assert math.isclose(totals['dealt_'+str(a)+'_'+str(b)],result[field][a],abs_tol=1e-6)
 return dict(id=record['id'],arm=record['arm'],head=record['head'],cluster=record['cluster'],orientation=record['orientation'],
  outcomes=dict(elimination_win=enemy_end==0 and own_end>0 and result['t']<150,timeout=result['t']>=150,
   own_elimination=own_end==0,enemy_elimination=enemy_end==0,S=own_end-enemy_end,t=result['t'],own_losses=50-own_end,enemy_killed=50-enemy_end,guns_destroyed=10-result['artilleryAlive'][1]),
  own_deaths=deaths,gun_deaths=gun_deaths,approaches=approaches,damage_totals=dict(totals),dodge=dict(dodge_n),
  geometry={k:stats(v) for k,v in geometry.items()},gun_peak_within_reach=gun_peak,gun_peak_inside_band=dict(inside_peak))

def aggregate(fights):
 out={}
 for arm in ARMS:
  for head in ('novice','regular'):
   group=[r for r in fights if r['arm']==arm and r['head']==head];o=[r['outcomes'] for r in group]
   deaths=[d for r in group for d in r['own_deaths']];guns=[d for r in group for d in r['gun_deaths']];apps=[d for r in group for d in r['approaches']]
   bins={}
   for p in ('early_0_20','middle_20_60','late_60_end','gun_only'):
    dd=[d for d in deaths if d['gun_only_before_tick']] if p=='gun_only' else [d for d in deaths if d['phase']==p]
    bins[p]={f'{team}:{role}':dict(kills=len(x),distance=stats([d['distance'] for d in x]),victims=dict(collections.Counter(d['targetRole'] for d in x))) for team in (0,1) for role in ROLES if (x:=[d for d in dd if d['sourceTeam']==team and d['sourceRole']==role])}
   out[arm+'|'+head]=dict(fights=len(o),seed_clusters=10,elimination_wins=sum(x['elimination_win'] for x in o),elimination_win_rate=statistics.mean(x['elimination_win'] for x in o),timeouts=sum(x['timeout'] for x in o),
    mean_S=statistics.mean(x['S'] for x in o),mean_guns_destroyed=statistics.mean(x['guns_destroyed'] for x in o),mean_own_losses=statistics.mean(x['own_losses'] for x in o),
    elimination_time=stats([x['t'] for x in o if x['elimination_win']]),own_losses_per_enemy_killed=stats([x['own_losses']/x['enemy_killed'] for x in o if x['enemy_killed']]),
    cluster_rows=[dict(cluster=c,win_rate=statistics.mean(r['outcomes']['elimination_win'] for r in group if r['cluster']==c),S=statistics.mean(r['outcomes']['S'] for r in group if r['cluster']==c)) for c in range(10)],
    own_deaths_by_phase_killer=bins,
    gun_killers={f'{team}:{role}':dict(kills=len(x),distance=stats([g['event']['distance'] for g in x]),max_simultaneous=stats([g['max_simultaneous_within_reach'] for g in x]),
                  shelling_other=sum(g['gun_was_shelling_other_target'] for g in x),killer_angle=stats([g['killer_angle_degrees'] for g in x if g['killer_angle_degrees'] is not None]),other_gun_cover=stats([g['other_guns_covering_killer'] for g in x])) for team in (0,1) for role in ROLES if (x:=[g for g in guns if g['event']['sourceTeam']==team and g['event']['sourceRole']==role])},
    approaches=dict(count=len(apps),outcomes=dict(collections.Counter(a['outcome'] for a in apps)),roles=dict(collections.Counter(a['role'] for a in apps)),
     ever_reached_own_range=sum(a['entered_own_reach'] for a in apps),ever_dealt_damage=sum(a['damage_to_gun']>0 for a in apps),
     entry_cover=stats([a['entry_other_gun_cover'] for a in apps]),simultaneous_approachers=stats([a['max_simultaneous_approachers'] for a in apps]),
     simultaneous_in_reach=stats([a['max_simultaneous_within_reach'] for a in apps]),
     simultaneous_entry_inside_band=stats([a['entry_inside_band_count'] for a in apps]),approach_starts_previous_3s=stats([a['approach_starts_previous_3s'] for a in apps]),entry_angle=stats([a['entry_angle_degrees'] for a in apps if a['entry_angle_degrees'] is not None]),duration=stats([a['duration'] for a in apps])),
    dodge_calls=sum(r['dodge'].get('team_1',0) for r in group),dodge_same_tick_motion_toward_goal=sum(r['dodge'].get('same_tick_motion_team_1',0) for r in group),
    geometry={k:stats([r['geometry'][k]['mean'] for r in group if k in r['geometry'] and r['geometry'][k]['mean'] is not None]) for k in ('gun_nearest_spacing','gun_band_overlap_count','enemy_has_slot','enemy_slot_offset')})
 return out

def main():
 assert_pins();start=time.time();awake=time.monotonic();records=json.loads((HERE/'FIGHTS.json').read_text());fights=[]
 for i,r in enumerate(records):
  assert sha(HERE/r['raw_file'])==r['raw_sha256'];v=analyze_fight(r);write(HERE/(r['id']+'_summary.json'),v);fights.append(v)
  if (i+1)%10==0:print(json.dumps(dict(analyzed=i+1,elapsed=time.time()-start)),flush=True)
  if i>=3 and (time.monotonic()-awake)*120/(i+1)>3600:raise TimeoutError('analysis daytime projection exceeds 1h')
 write(HERE/'SUMMARY.json',aggregate(fights));assert_pins()
 write(HERE/'ANALYSIS_VERIFICATION.json',dict(status='PASS',fights=len(fights),all_raw_hashes=True,all_ticks_processed=True,death_gun_conservation=True,damage_ledger_vs_native_cross_and_friendly=True,terminal_reconciliation=True,elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake))
 write(HERE/'RAW_FILES_LOCAL.json',{str(p.relative_to(HERE)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in RAW.rglob('*') if p.is_file()})
if __name__=='__main__':main()
