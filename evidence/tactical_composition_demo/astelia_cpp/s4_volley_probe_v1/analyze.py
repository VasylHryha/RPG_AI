"""Stored-only all-tick recount. Shell numerator counts distinct targeted launches."""
import pathlib,json,gzip,hashlib,time,collections
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def analyze(r):
 p=HERE/'raw'/(r['id']+'.jsonl.gz');assert sha(p)==r['raw_sha256'];launches=[];hits=set();deaths=[];dodge=[0,0];initial=None;steps=0;last=-1;unmatched=0;holdInside=holdTicks=0;releaseGroups=[];arms=r['arm']
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
    if d['died']:deaths.append(d)
    if d['sourceTeam']==0 and d['sourceRole']=='artillery' and d['targetTeam']==1 and d['targetRole']=='artillery' and d['dealt']>0:
     due=[(i,s) for i,s in enumerate(launches) if s['source']==d['source'] and s['at']<=d['t']+1e-9 and d['t']-s['at']<=1/30+1e-7]
     assert len(due)==1,('ambiguous/unmatched shell',r['id'],d,len(due))
     i,s=due[0]
     if s['aimed_at_enemy_gun']:hits.add(i)
   for d in row['dodges']:dodge[int(d[1])]+=1
   enemy=[u for u in units.values() if u[1]==1 and u[2]==2]
   if arms=='P3' and len(enemy)>=4:
    for u in units.values():
     if u[1]==0 and u[2]==1:
      holdTicks+=1;holdInside+=any(g[8]<=((u[3]-g[3])**2+(u[4]-g[4])**2)**.5<=g[7] for g in enemy)
 assert terminal==r['summary'];s=terminal
 assert len({d['target'] for d in deaths})==len(deaths)
 assert sum(d['targetTeam']==0 for d in deaths)==50-s['survivors']
 assert sum(d['targetTeam']==1 and d['targetRole']=='artillery' for d in deaths)==10-s['artilleryAlive'][1]
 assert sum(d['targetTeam']==0 and d['targetRole']=='artillery' for d in deaths)==10-s['artilleryAlive'][0]
 fired=sum(s['aimed_at_enemy_gun'] for s in launches);assert len(hits)<=fired
 return dict(id=r['id'],arm=r['arm'],head=r['head'],cluster=r['cluster'],orientation=r['orientation'],elimination_win=s['enemySurvivors']==0 and s['survivors']>=1 and s['t']<150,timeout=s['t']>=150,S=s['survivors']-s['enemySurvivors'],enemy_guns_destroyed=10-s['artilleryAlive'][1],own_gun_losses=10-s['artilleryAlive'][0],own_losses=50-s['survivors'],enemy_units_killed=50-s['enemySurvivors'],win_time_s=s['t'] if s['enemySurvivors']==0 and s['survivors']>=1 and s['t']<150 else None,shell_hits_on_enemy_guns=len(hits),shells_fired_at_enemy_guns=fired,own_damage_shells=len(launches),dodge_events_enemy=dodge[1],dodge_events_own=dodge[0],p3_held_unit_ticks_inside_enemy_band=holdInside,p3_held_unit_ticks=holdTicks,targeted_gun_release_ticks=len(releaseGroups),release_ticks_ge3_guns=sum(len(g['guns'])>=3 for g in releaseGroups),release_ticks_ge3_distinct_targets=sum(len(g['guns'])>=3 and len(g['targets'])>=3 for g in releaseGroups),ticks=steps,raw_sha256=r['raw_sha256'])
def main():
 start=time.time();awake=time.monotonic();fights=json.loads((HERE/'FIGHTS.json').read_text());rows=[analyze(r) for r in fights];aggregates=[]
 for arm in ('P0','P1','P2','P3'):
  for head in ('regular','novice'):
   a=[r for r in rows if r['arm']==arm and r['head']==head];assert len(a)==20 and len({(r['cluster'],r['orientation']) for r in a})==20
   sums={k:sum(r[k] for r in a) for k in ('elimination_win','timeout','enemy_guns_destroyed','own_gun_losses','own_losses','enemy_units_killed','shell_hits_on_enemy_guns','shells_fired_at_enemy_guns','dodge_events_enemy','dodge_events_own','p3_held_unit_ticks_inside_enemy_band','p3_held_unit_ticks','targeted_gun_release_ticks','release_ticks_ge3_guns','release_ticks_ge3_distinct_targets')}
   wins=[r['win_time_s'] for r in a if r['elimination_win']];aggregates.append(dict(arm=arm,head=head,n=20,elimination_wins=sums.pop('elimination_win'),timeouts=sums.pop('timeout'),mean_S=sum(r['S'] for r in a)/20,mean_enemy_guns_destroyed=sums['enemy_guns_destroyed']/20,mean_own_gun_losses=sums['own_gun_losses']/20,mean_own_losses=sums['own_losses']/20,shell_hit_rate=sums['shell_hits_on_enemy_guns']/sums['shells_fired_at_enemy_guns'] if sums['shells_fired_at_enemy_guns'] else None,mean_win_time_s=sum(wins)/len(wins) if wins else None,own_losses_per_enemy_kill=sums['own_losses']/sums['enemy_units_killed'] if sums['enemy_units_killed'] else None,**sums))
 write(HERE/'SUMMARY.json',dict(status='DONE',scope='descriptive feasibility; no scientific/registration/readiness verdict',definitions=dict(hits='distinct damaging own shell launches aimed at enemy guns that hit one or more enemy guns; splash multiple targets counts once',denominator='all non-slow own launches whose current target at release is enemy artillery; all arrivals traced; global ability gate off',dodge='successful native dodgeGoal returns, not unique shells or dash reflexes',outcome='elimination iff enemy=0, own>=1, t<150; timeout iff t>=150'),rows=aggregates,fights=rows))
 write(HERE/'RAW_FILES_LOCAL.json',dict(raw_policy='local only, never deliver >45MB',files=[dict(path=str(p.relative_to(HERE)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted((HERE/'raw').iterdir())]))
 write(HERE/'ANALYSIS_VERIFICATION.json',dict(status='PASS',fights=len(rows),all_ticks_recounted=True,all_raw_hashes_verified=True,own_losses_and_gun_deaths_reconciled=True,targeted_shell_identity_unique=True,elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake));print(json.dumps(aggregates,indent=2))
if __name__=='__main__':main()
