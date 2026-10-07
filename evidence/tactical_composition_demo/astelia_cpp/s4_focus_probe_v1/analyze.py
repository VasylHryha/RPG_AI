"""Stored-only all-tick recount. Shell numerator counts distinct targeted launches."""
import pathlib,json,gzip,hashlib,time,collections,statistics,signal
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def analyze(r):
 p=HERE/'raw'/(r['id']+'.jsonl.gz');assert sha(p)==r['raw_sha256'];launches=[];hits=set();deaths=[];dodge=[0,0];initial=None;steps=0;last=-1;unmatched=0;releaseGroups=[];terminal=None;gunKills=[];ownGunDeaths=[]
 with gzip.open(p,'rt') as f:
  for l in f:
   row=json.loads(l)
   if not row.get('observerV1'):terminal=row;continue
   assert row['step']==steps;steps+=1;assert row['t']>=last;last=row['t'];units={u[0]:u for u in row['units']}
   if initial is None:initial=units;assert sum(u[1]==0 for u in units.values())==50 and sum(u[1]==1 for u in units.values())==50
   ownRelease=[l for l in row['launches'] if l[2]==0 and not l[9] and initial.get(l[1], [0,0,0])[2]==2]
   if ownRelease:releaseGroups.append(dict(t=row['t'],guns=sorted({l[0] for l in ownRelease}),targets=sorted({l[1] for l in ownRelease})))
   for launch in row['launches']:
    if launch[2]==0 and not launch[9]:
     target=initial.get(launch[1]);launches.append(dict(source=launch[0],target=launch[1],born=launch[5],at=launch[6],barrage=launch[8],aimed_at_enemy_gun=bool(target and target[1]==1 and target[2]==2)))
   for d in row['damage']:
    if d['died']:
     deaths.append(d)
     if d['targetTeam']==1 and d['targetRole']=='artillery':gunKills.append(d)
     if d['targetTeam']==0 and d['targetRole']=='artillery':ownGunDeaths.append(d)
    if d['sourceTeam']==0 and d['sourceRole']=='artillery' and d['targetTeam']==1 and d['targetRole']=='artillery' and d['dealt']>0:
     due=[(i,s) for i,s in enumerate(launches) if s['source']==d['source'] and s['at']<=d['t']+1e-9 and d['t']-s['at']<=1/30+1e-7]
     assert len(due)==1,('ambiguous/unmatched shell',r['id'],d,len(due))
     i,s=due[0]
     if s['aimed_at_enemy_gun']:hits.add(i)
   for d in row['dodges']:dodge[int(d[1])]+=1
 assert terminal==r['summary'];s=terminal
 assert len({d['target'] for d in deaths})==len(deaths)
 assert sum(d['targetTeam']==1 for d in deaths)==50-s['enemySurvivors']
 assert sum(d['targetTeam']==0 for d in deaths)==50-s['survivors']
 assert sum(d['targetTeam']==1 and d['targetRole']=='artillery' for d in deaths)==10-s['artilleryAlive'][1]
 assert sum(d['targetTeam']==0 and d['targetRole']=='artillery' for d in deaths)==10-s['artilleryAlive'][0]
 fired=sum(s['aimed_at_enemy_gun'] for s in launches);assert len(hits)<=fired
 return dict(id=r['id'],arm=r['arm'],head=r['head'],cluster=r['cluster'],orientation=r['orientation'],elimination_win=s['enemySurvivors']==0 and s['survivors']>=1 and s['t']<150,timeout=s['t']>=150,S=s['survivors']-s['enemySurvivors'],enemy_guns_destroyed=10-s['artilleryAlive'][1],own_gun_losses=10-s['artilleryAlive'][0],own_losses=50-s['survivors'],enemy_units_killed=50-s['enemySurvivors'],win_time_s=s['t'] if s['enemySurvivors']==0 and s['survivors']>=1 and s['t']<150 else None,shell_hits_on_enemy_guns=len(hits),shells_fired_at_enemy_guns=fired,own_damage_shells=len(launches),dodge_events_enemy=dodge[1],dodge_events_own=dodge[0],time_to_first_enemy_gun_kill_s=min((d['t'] for d in gunKills),default=None),own_gun_killers=[dict(source=d['source'],team=d['sourceTeam'],role=d['sourceRole'],target=d['target'],t=d['t']) for d in ownGunDeaths],enemy_gun_killers=[dict(source=d['source'],team=d['sourceTeam'],role=d['sourceRole'],target=d['target'],t=d['t']) for d in gunKills],targeted_gun_release_ticks=len(releaseGroups),release_ticks_ge3_guns=sum(len(g['guns'])>=3 for g in releaseGroups),release_ticks_ge3_distinct_targets=sum(len(g['guns'])>=3 and len(g['targets'])>=3 for g in releaseGroups),ticks=steps,raw_sha256=r['raw_sha256'])
def main():
 start=time.time();awake=time.monotonic()
 used=sum(json.loads((HERE/n).read_text())['awake_seconds'] for n in ('BUILD_TIMING.json','FAILED_FIRST_CHECK_TIMING.json','CHECK_TIMING.json','RUN_TIMING.json'))
 assert used<3600,'1h compute budget exhausted'
 def stop(signum,frame):raise TimeoutError('stored-only recount compute cap')
 signal.signal(signal.SIGALRM,stop);signal.alarm(max(1,int(min(1200,3600-used))))
 fights=json.loads((HERE/'FIGHTS.json').read_text());rows=[];aggregates=[]
 d=json.loads((HERE/'DECLARATION.json').read_text());expected={(a,h,c,o) for a in d['arms'] for h in d['heads'] for c in range(10) for o in d['orientations']}
 assert len(fights)==160 and {(r['arm'],r['head'],r['cluster'],r['orientation']) for r in fights}==expected
 for r in fights:
  reqpath=HERE/'raw'/(r['id']+'_request.json');assert sha(reqpath)==r['request_sha256']
  req=json.loads(reqpath.read_text());template=json.loads((HERE/(r['head'].upper()+'_REQUEST_TEMPLATE.json')).read_text())
  template['options']['seed']=d['development_seeds'][r['cluster']]
  template['options']['swapSides']=bool(r['orientation'])
  template['options']['ai'][0]['controller']=r['arm']
  assert req==template,('request declaration mismatch',r['id'])
  rows.append(analyze(r))
  if len(rows)%10==0:print(json.dumps(dict(recounted=len(rows),elapsed_seconds=time.time()-start)),flush=True)
  if len(rows)>=8 and (time.monotonic()-awake)*len(fights)/len(rows)>3600-used:raise TimeoutError('recount projection exceeds remaining1h budget')
 for arm in ('P0','P4','P5','P6'):
  for head in ('regular','novice'):
   a=[r for r in rows if r['arm']==arm and r['head']==head];assert len(a)==20 and len({(r['cluster'],r['orientation']) for r in a})==20
   sums={k:sum(r[k] for r in a) for k in ('elimination_win','timeout','enemy_guns_destroyed','own_gun_losses','own_losses','enemy_units_killed','shell_hits_on_enemy_guns','shells_fired_at_enemy_guns','dodge_events_enemy','dodge_events_own','targeted_gun_release_ticks','release_ticks_ge3_guns','release_ticks_ge3_distinct_targets')}
   wins=[r['win_time_s'] for r in a if r['elimination_win']]
   first=[r['time_to_first_enemy_gun_kill_s'] for r in a if r['time_to_first_enemy_gun_kill_s'] is not None]
   killers=collections.Counter((d['team'],d['role']) for r in a for d in r['own_gun_killers']);assert sum(killers.values())==sums['own_gun_losses']
   enemyKillers=collections.Counter((d['team'],d['role']) for r in a for d in r['enemy_gun_killers']);assert sum(enemyKillers.values())==sums['enemy_guns_destroyed']
   aggregates.append(dict(arm=arm,head=head,n=20,elimination_wins=sums.pop('elimination_win'),timeouts=sums.pop('timeout'),mean_S=sum(r['S'] for r in a)/20,first_gun_kill_fights=len(first),no_enemy_gun_kill_fights=20-len(first),mean_first_enemy_gun_kill_s=sum(first)/len(first) if first else None,median_first_enemy_gun_kill_s=statistics.median(first) if first else None,own_gun_killers=[dict(team=t,role=k,kills=v) for (t,k),v in sorted(killers.items())],enemy_gun_killers=[dict(team=t,role=k,kills=v) for (t,k),v in sorted(enemyKillers.items())],mean_enemy_guns_destroyed=sums['enemy_guns_destroyed']/20,mean_own_gun_losses=sums['own_gun_losses']/20,mean_own_losses=sums['own_losses']/20,shell_hit_rate=sums['shell_hits_on_enemy_guns']/sums['shells_fired_at_enemy_guns'] if sums['shells_fired_at_enemy_guns'] else None,mean_win_time_s=sum(wins)/len(wins) if wins else None,own_losses_per_enemy_kill=sums['own_losses']/sums['enemy_units_killed'] if sums['enemy_units_killed'] else None,**sums))
 write(HERE/'SUMMARY.json',dict(status='DONE',scope='descriptive feasibility; no scientific/registration/readiness verdict',definitions=dict(hits='distinct damaging own shell launches aimed at enemy guns that hit one or more enemy guns; splash multiple targets counts once',denominator='all non-slow own launches whose current target at release is enemy artillery; includes misses and shells still airborne at termination; global ability gate off',dodge='successful native dodgeGoal returns, not unique shells or dash reflexes',outcome='elimination iff enemy=0, own>=1, t<150; timeout iff t>=150'),rows=aggregates,fights=rows))
 write(HERE/'RAW_FILES_LOCAL.json',dict(raw_policy='local only, never deliver >45MB',files=[dict(path=str(p.relative_to(HERE)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted((HERE/'raw').iterdir())]))
 write(HERE/'ANALYSIS_VERIFICATION.json',dict(status='PASS',fights=len(rows),all_ticks_recounted=True,all_raw_hashes_verified=True,own_losses_and_gun_deaths_reconciled=True,first_gun_kill_and_killers_reconciled=True,targeted_shell_identity_unique=True,elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake));print(json.dumps(aggregates,indent=2))
if __name__=='__main__':main()
