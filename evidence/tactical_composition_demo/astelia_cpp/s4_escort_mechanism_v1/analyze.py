#!/usr/bin/env python3
"""Stored-data only. No engine imports, subprocesses, fights, or simulation.
Run: python3 evidence/tactical_composition_demo/astelia_cpp/s4_escort_mechanism_v1/analyze.py
All source raw files verified before any gzip parsing. Outputs only beside this script.
"""
import collections as C
import gzip, hashlib, json, math, pathlib, statistics, time
HERE=pathlib.Path(__file__).resolve().parent
SOURCE=HERE.parent/'s4_escort_probe_v1'
BINS=(0,10,20,30,60,150.1)
CURVE=(0,10,15,20,25,30,45,60,90,150)
ROLES=('melee','ranged','artillery')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def binof(t):return next(i for i in range(5) if BINS[i]<=t<BINS[i+1])
def cohort(u):return ('own_' if u[1]==0 else 'enemy_')+ROLES[u[2]]
def dist(a,b):return math.hypot(a[3]-b[3],a[4]-b[4])
def verify():
 idx=json.loads((SOURCE/'RAW_FILES_LOCAL.json').read_text());total=0
 for r in idx['files']:
  p=SOURCE/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path'];total+=r['bytes']
 return dict(status='PASS',files=len(idx['files']),bytes=total,index_sha256=sha(SOURCE/'RAW_FILES_LOCAL.json'))
def analyze(f):
 fid=f['id'];registry={};initial={};last={};damage=C.Counter();deaths=[];perunit=C.Counter();targets=C.Counter();releases=C.Counter();launches=C.Counter();selection=C.Counter();proxy=C.Counter();curves=[];cursor=0;previous=None;observer=None;ended=None;enemy_gun_end=None;phase_deaths=C.Counter();early_kills=C.Counter();dead=set();step=0;gun_release_times=[];gun_damage_events=[]
 with gzip.open(SOURCE/'raw'/(fid+'.jsonl.gz'),'rt') as stream:
  for line in stream:
   if '"observerV1":true' in line[:70] or '"observerV1": true' in line[:70]:
    r=json.loads(line);t=r['t'];now={u[0]:u for u in r['units']};observer=r
    if r['step']==0:
     registry=now;initial=now;last=now;previous=r
    else:
     assert r['step']==step+1
     step=r['step']
    actions={a[0]:a for a in r['actions']}
    for a in r['actions']:
     src=registry[a[0]]
     if src[1]==1 and src[2] in (1,2):
      dst=registry.get(a[2]);targets[(binof(t),ROLES[src[2]],cohort(dst) if dst else 'none')]+=1
     # Direct releases are inferred, not observer events. Only living post-step
     # ranged: prep resetting to zero with Direct/DodgeFire and target selected.
     u=now.get(a[0]);v=last.get(a[0])
     if src[2]==1 and u and v and v[12]>0 and u[12]==0 and a[7] in (2,3) and a[2]:
      releases[(binof(t),'own' if src[1]==0 else 'enemy',cohort(registry[a[2]]))]+=1
    for l in r['launches']:
     dst=registry.get(l[1]);launches[(binof(l[5]),'own' if l[2]==0 else 'enemy',cohort(dst) if dst else 'none')]+=1
     if l[2]==0:gun_release_times.append(l[5])
    for d in r['damage']:
     b=binof(d['t']);sc=('friendly_' if d['sourceTeam']==d['targetTeam'] else 'opposing_')+d['sourceRole'];dst=registry[d['target']];damage[(b,cohort(dst),sc)]+=d['dealt'];perunit[d['target']]+=d['dealt']
     if d['targetTeam']==0 and d['targetRole']=='artillery':gun_damage_events.append((d['t'],d['dealt']))
     if d['died']:
      assert d['target'] not in dead;dead.add(d['target']);deaths.append(d)
      if d['sourceTeam']==0 and d['targetTeam']==1 and d['targetRole']=='ranged':
       for cutoff in (20,30):
        if d['t']<cutoff:early_kills[(cutoff,d['sourceRole'])]+=1
     # Snapshot alignment proxy only. No direct-shot identity in these traces.
     if d['sourceTeam']==1 and d['sourceRole']=='ranged' and d['targetTeam']==0 and d['targetRole']=='ranged':
      a=actions.get(d['source']);g=now.get(a[2]) if a else None
      if g and g[1]==0 and g[2]==2:
       proxy['damage_events_with_current_gun_target']+=1;proxy['hp_with_current_gun_target']+=d['dealt']
       dx=g[3]-d['sourceX'];dy=g[4]-d['sourceY'];den=dx*dx+dy*dy
       q=((d['targetX']-d['sourceX'])*dx+(d['targetY']-d['sourceY'])*dy)/den if den else -1
       gap=abs((d['targetX']-d['sourceX'])*dy-(d['targetY']-d['sourceY'])*dx)/math.sqrt(den) if den else math.inf
       if 0<q<1 and gap<=dst[6]:proxy['between_source_and_current_gun_target_events']+=1;proxy['between_source_and_current_gun_target_hp']+=d['dealt']
    # Curves reconstructed from exact damage/death times; performed after parse.
    last=now;previous=r
    if enemy_gun_end is None and not any(u[1]==1 and u[2]==2 for u in now.values()):enemy_gun_end=t
   elif '"escortProbe":true' in line[:70] or '"escortProbe": true' in line[:70]:
    r=json.loads(line);t=r['t'];assert observer['step']==r['step'];before={u[0]:u for u in r['prepare'] if u[5]>0};guns=[u for u in before.values() if u[1]==0 and u[2]==2];eguns=[u for u in before.values() if u[1]==1 and u[2]==2]
    if not guns or not eguns:continue
    ers=[u for u in before.values() if u[1]==1 and u[2]==1];actions={a[0]:a for a in observer['actions']}
    threatening=[e for e in ers if any(dist(e,g)<=e[7]+e[6]+g[6] for g in guns)]
    for u in before.values():
     if u[1]!=0 or u[2]!=1:continue
     reachable={e[0] for e in threatening if dist(u,e)<=u[7]+u[6]+e[6]};a=actions.get(u[0]);target=a[2] if a else 0;dst=registry.get(target);key=(binof(t),)
     selection[key+('eligible',)]+=1
     if reachable:
      selection[key+('opportunity',)]+=1;selection[key+('selected_threat',)]+=target in reachable
      selection[key+('selected_'+(ROLES[dst[2]] if dst else 'none'),)]+=1
      if dst and dst[2]==1 and target not in reachable:selection[key+('selected_other_ranged',)]+=1
      if a and a[8] and a[5]>0:selection[key+('moving_opportunity',)]+=1;selection[key+('moving_selected_threat',)]+=target in reachable
    for d in observer['damage']:
     if d['died'] and d['targetTeam']==0 and d['targetRole']=='ranged':phase_deaths['both_guns_alive_at_prepare']+=1
   elif '"controllerStatus"' in line:
    ended=json.loads(line)
 assert ended==f['summary'] and step==observer['step'];assert set(last).isdisjoint(dead)
 for uid,u in initial.items():assert abs(u[5]-last.get(uid,[0]*6)[5]-perunit[uid])<1e-6,('HP conservation',fid,uid)
 assert sum(u[1]==0 for u in last.values())==ended['survivors'];assert sum(u[1]==1 for u in last.values())==ended['enemySurvivors']
 win=ended['enemySurvivors']==0 and ended['survivors']>0 and ended['t']<150
 # Right-continuous at exact t, terminal absorbing states after a fight ends.
 for t in CURVE:
  dd=[d for d in deaths if d['t']<=t];killed={d['target'] for d in dd}
  curves.append(dict(t=t,own_gun_hp_remaining=sum(u[5] for u in initial.values() if u[1]==0 and u[2]==2)-sum(hp for at,hp in gun_damage_events if at<=t),own_guns_alive=sum(u[1]==0 and u[2]==2 and uid not in killed for uid,u in initial.items()),enemy_guns_dead=sum(u[1]==1 and u[2]==2 and uid in killed for uid,u in initial.items()),enemy_ranged_alive=sum(u[1]==1 and u[2]==1 and uid not in killed for uid,u in initial.items()),own_ranged_alive=sum(u[1]==0 and u[2]==1 and uid not in killed for uid,u in initial.items())))
 ranged_killers=C.Counter(('friendly_' if d['sourceTeam']==0 else 'enemy_')+d['sourceRole'] for d in deaths if d['targetTeam']==0 and d['targetRole']=='ranged')
 return dict(id=fid,arm=f['arm'],head=f['head'],cluster=f['cluster'],orientation=f['orientation'],win=win,duration=ended['t'],own_losses=50-ended['survivors'],S=ended['survivors']-ended['enemySurvivors'],damage=[dict(bin=b,target=dst,source=src,hp=v) for (b,dst,src),v in sorted(damage.items())],targets=[dict(bin=b,source=src,target=dst,ticks=v) for (b,src,dst),v in sorted(targets.items())],direct_releases_inferred=[dict(bin=b,source=src,target=dst,releases=v) for (b,src,dst),v in sorted(releases.items())],shell_launches=[dict(bin=b,source=src,target=dst,launches=v) for (b,src,dst),v in sorted(launches.items())],selection=[dict(bin=b,metric=k,ticks=v) for (b,k),v in sorted(selection.items())],curves=curves,own_ranged_killers=dict(ranged_killers),own_ranged_gun_phase_deaths=dict(phase_deaths),enemy_guns_all_dead_at=enemy_gun_end,early_enemy_ranged_kills=[dict(before=cutoff,source=src,kills=v) for (cutoff,src),v in sorted(early_kills.items())],interception_snapshot_proxy=dict(proxy),hp_conservation_units=len(initial),own_gun_launches_before30=sum(t<30 for t in gun_release_times),own_gun_last_hits=[dict(t=d['t'],source=('friendly_' if d['sourceTeam']==0 else 'enemy_')+d['sourceRole']) for d in deaths if d['targetTeam']==0 and d['targetRole']=='artillery'])
def aggregate(fs):
 out=dict(n=len(fs),wins=sum(f['win'] for f in fs),mean_own_losses=statistics.mean(f['own_losses'] for f in fs),mean_S=statistics.mean(f['S'] for f in fs));n=len(fs)
 for field,value in [('damage','hp'),('targets','ticks'),('direct_releases_inferred','releases'),('shell_launches','launches'),('selection','ticks'),('early_enemy_ranged_kills','kills')]:
  c=C.Counter()
  for f in fs:
   for r in f[field]:c[tuple((k,v) for k,v in r.items() if k!=value)]+=r[value]
  out[field]=[dict(key,**{value:v}) for key,v in sorted(c.items())]
 for field in ('own_ranged_killers','own_ranged_gun_phase_deaths','interception_snapshot_proxy'):
  c=C.Counter()
  for f in fs:c.update(f[field])
  out[field]=dict(c)
 out['curves']=[dict(t=t,**{k:statistics.mean(f['curves'][i][k] for f in fs) for k in ('own_guns_alive','own_gun_hp_remaining','enemy_guns_dead','enemy_ranged_alive','own_ranged_alive')}) for i,t in enumerate(CURVE)]
 out['mean_own_gun_launches_before30']=statistics.mean(f['own_gun_launches_before30'] for f in fs)
 # HP curve using bin sums is separate from survivor curve; exact cutoff damage
 # not retained here, so no interpolated HP claim.
 return out
def main():
 start=time.monotonic();verification=verify();print(json.dumps(verification),flush=True)
 fights=json.loads((SOURCE/'FIGHTS.json').read_text());assert len(fights)==120;rows=[]
 for i,f in enumerate(fights):
  rows.append(analyze(f))
  if (i+1)%10==0:print('parsed',i+1,'elapsed',round(time.monotonic()-start),flush=True)
 cells=[];subgroups=[]
 for arm in ('P11','P12','P13'):
  for head in ('regular','novice'):
   fs=[f for f in rows if f['arm']==arm and f['head']==head];assert len(fs)==20
   cells.append(dict(arm=arm,head=head,**aggregate(fs)))
   if head=='regular':
    for win in (True,False):
     group=[f for f in fs if f['win']==win]
     if group:subgroups.append(dict(arm=arm,head=head,outcome='win' if win else 'nonwin',**aggregate(group)))
 wins=[f['id'] for f in rows if f['head']=='regular' and f['arm'] in ('P12','P13') and f['win']];assert len(wins)==11
 paired=[]
 for arm in ('P12','P13'):
  diffs=[]
  for c in range(10):
   pairs=[(next(f for f in rows if (f['arm'],f['head'],f['cluster'],f['orientation'])==(arm,'regular',c,o)),next(f for f in rows if (f['arm'],f['head'],f['cluster'],f['orientation'])==('P11','regular',c,o))) for o in (0,1)]
   diffs.append(dict(cluster=c,win_delta=sum(int(a['win'])-int(b['win']) for a,b in pairs),own_loss_delta_mean=statistics.mean(a['own_losses']-b['own_losses'] for a,b in pairs)))
  paired.append(dict(arm=arm,clusters=diffs))
 meta=dict(status='PARTIAL',scope='stored development traces only; no fights; exact damage/targets/shells, direct-release lower bound and interception proxy',reviewed_commit='0f8e823077d83bca76a66532a1988d2ec7c9052a',raw_verification=verification,source_hashes={n:sha(SOURCE/n) for n in ('DECLARATION.json','FIGHTS.json','COMPACT.json','SUMMARY.json')},script_sha256=sha(HERE/'analyze.py'),bins=[list(x) for x in zip(BINS,BINS[1:])],curve_convention='death at t<=sample; terminal survivors held after fight ends, not continuing simulated survival',units='HP and counts pooled over 20 fights per arm/head; divide by n for per-fight means; snapshots are 30 Hz, not independent samples',limits=['No direct shot ordinals, origins, directions or hit-to-shot identities. Snapshot proxy is not a prevented-shot count.','Direct releases inferred from prep reset only for post-step living ranged units. Missing same-step deceased shooters makes a lower bound.','P11 own ranged are a comparison cohort, not escorts. Active escort phase requires both sides guns alive at prepare.','Win/nonwin contrasts are outcome-conditioned associations, with 10 paired clusters per arm. No population-rate or causal counterfactual claims.'],elapsed_s=round(time.monotonic()-start,3))
 dump(HERE/'COMPACT.json',dict(**meta,cells=cells,regular_outcomes=subgroups,paired=paired,verified_regular_escort_wins=wins))
 dump(HERE/'PER_FIGHT.json',dict(**meta,fights=rows))
 print('DONE',meta['elapsed_s'],flush=True)
if __name__=='__main__':main()
