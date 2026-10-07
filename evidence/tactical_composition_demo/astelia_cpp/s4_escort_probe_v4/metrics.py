"""Independent observation-only escort oracle and exact reporting conventions."""
import math

def distance(a,b):return math.hypot(a[3]-b[3],a[4]-b[4])
def point_for(u,own,enemy,ranged,dose,width,height):
 gun=min(own,key=lambda g:(distance(u,g),g[0]));threats=[r for r in ranged if distance(r,gun)<=400]
 threat=min(threats,key=lambda r:(distance(r,gun),r[0]),default=None)
 def vector(p):return p[0]-gun[3],p[1]-gun[4]
 direction=1;dx,dy=vector(threat[3:5]) if threat else (0,0)
 if threat is None or math.hypot(dx,dy)<1e-9:
  direction=2;ordered=sorted(enemy,key=lambda e:e[0]);dx,dy=vector((sum(e[3] for e in ordered)/len(enemy),sum(e[4] for e in ordered)/len(enemy)))
 if math.hypot(dx,dy)<1e-9:
  direction=3;e=min(enemy,key=lambda e:(distance(e,gun),e[0]));dx,dy=vector(e[3:5])
 n=math.hypot(dx,dy)
 if n<1e-9:return dict(gun=gun[0],threat=threat[0] if threat else 0,direction=0,raw=None,clipped=None)
 raw=[gun[3]+dose*dx/n,gun[4]+dose*dy/n]
 return dict(gun=gun[0],threat=threat[0] if threat else 0,direction=direction,raw=raw,clipped=[min(width,max(0,raw[0])),min(height,max(0,raw[1]))])
def splash_value(g,enemies):return sum(distance(g,u)<=40+u[6] for u in enemies if u[5]>0)
def gun_focus_oracle(prepare,width,height,rank_splash):
 own=sorted((u for u in prepare if u[5]>0 and u[1]==0 and u[2]==2),key=lambda u:u[0])
 enemies=[u for u in prepare if u[5]>0 and u[1]==1];guns=[u for u in enemies if u[2]==2]
 values={g[0]:splash_value(g,enemies) for g in guns}
 guns.sort(key=lambda g:((-values[g[0]],g[5],g[0]) if rank_splash else (g[5],g[0])))
 if not own or not guns:return {}
 def reach(g,e):return g[8]<=distance(g,e)<=g[7]
 anchor=next((e for e in guns if any(reach(g,e) for g in own)),guns[0]);out={}
 for g in own:
  target=next((e for e in guns if reach(g,e)),None);focus=target or anchor
  dx,dy=g[3]-focus[3],g[4]-focus[4];d=math.hypot(dx,dy);preferred=max(g[8],g[7]-12)
  bx=focus[3]+preferred*(dx/d if d else 1);by=focus[4]+preferred*(dy/d if d else 0);sx=sy=0
  for n in own:
   if n[0]==g[0]:continue
   dx,dy=g[3]-n[3],g[4]-n[4];nd=math.hypot(dx,dy)
   if nd<60:sx+=(60-nd)*(dx/nd if nd else (-1 if g[0]<n[0] else 1));sy+=(60-nd)*(dy/nd if nd else 0)
  out[g[0]]=dict(target=target[0] if target else None,focus=focus[0],anchor=anchor[0],focus_V=values[focus[0]],anchor_V=values[anchor[0]],values_by_gun=values,command=[bx+sx,by+sy,int(abs(d-preferred)>1e-9),0],reachable=target is not None)
 return out
CURVE_TIMES=(10,20,30,45,60)
def gun_curve(initial,deaths):
 ids={u[0] for u in initial.values() if u[1]==0 and u[2]==2}
 assert len({d['target'] for d in deaths})==len(deaths),'duplicate deaths'
 times={d['target']:d['t'] for d in deaths}
 return [dict(t=t,alive=sum(times.get(uid,math.inf)>t for uid in ids)) for t in CURVE_TIMES]
def paired_clusters(per):
 out=[]
 for head in ('regular','novice'):
  for cluster in range(20):
   cells={a:sorted([r for r in per if (r['arm'],r['head'],r['cluster'])==(a,head,cluster)],key=lambda r:r['orientation']) for a in ('P12','P16')}
   assert all([r['orientation'] for r in rs]==[0,1] for rs in cells.values())
   wins={a:sum(r['elimination_win'] for r in rs) for a,rs in cells.items()};scores={a:sum(r['S'] for r in rs)/2 for a,rs in cells.items()}
   out.append(dict(head=head,cluster=cluster,orientations={a:[dict(orientation=r['orientation'],win=r['elimination_win'],S=r['S']) for r in rs] for a,rs in cells.items()},wins=wins,mean_S=scores,win_difference=dict(P16=wins['P16']-wins['P12']),mean_S_difference=dict(P16=scores['P16']-scores['P12'])))
 return out

def cluster_uncertainty(pairs):
 import statistics
 out=[]
 for head in ('regular','novice'):
  rs=[r for r in pairs if r['head']==head];assert len(rs)==20
  values={a:[r['wins'][a]/2 for r in rs] for a in ('P12','P16')}
  values['P16_minus_P12']=[r['win_difference']['P16']/2 for r in rs]
  for name,xs in values.items():
   mean=statistics.mean(xs);se=statistics.stdev(xs)/math.sqrt(20)
   out.append(dict(head=head,quantity=name,clusters=20,mean=mean,cluster_standard_error=se,approximate_t95_interval=[mean-2.093024054*se,mean+2.093024054*se],assumptions='Independent development clusters; paired orientations averaged first. Approximate t interval (19 df), unbounded; descriptive, not a registered population-rate guarantee. Zero sample variance is not proof of certainty.'))
 return out

def reading(rows,pairs):
 cells={(r['arm'],r['head']):r for r in rows};q=cells['P16','regular'];n=cells['P16','novice']
 regular=[r for r in pairs if r['head']=='regular'];assert len(regular)==20
 better=sum(r['win_difference']['P16']>0 for r in regular)
 failures=sum(r['failure_count'] for r in rows)
 checks=dict(regular_at_least_26=q['elimination_wins']>=26,regular_mean_S_positive=q['mean_S']>0,novice_mean_S_positive=n['mean_S']>0,novice_at_least_21=n['elimination_wins']>=21,no_failures=failures==0,better_in_at_least_12_clusters=better>=12)
 replicated=all(checks.values())
 label='Replicated' if replicated else 'Not replicated' if q['elimination_wins']<=20 else 'Descriptive; replication conjunction not met'
 return dict(reading=label,replicated=replicated,checks=checks,regular_clusters_better=better,regular_clusters_tied=sum(r['win_difference']['P16']==0 for r in regular),regular_clusters_worse=sum(r['win_difference']['P16']<0 for r in regular),cluster_uncertainty=cluster_uncertainty(pairs),limits='20 fresh paired development clusters; no population-rate, resonator, judging, registration or scientific acceptance claim. A replicated result supplies the scripted feasibility witness for the owner-directed v7 revision; it does not approve the draft v7.')

class ShellAudit:
 """Unique source/scheduled-impact attribution, distinct ranged victims."""
 def __init__(self):
  self.registry=None;self.previous=None;self.pending={};self.shells=[]
 def observe(self,row):
  if self.registry is None:
   self.registry={u[0]:u for u in row['units']};self.previous=row['t'];return
  dt=row['t']-self.previous;assert abs(dt-1/30)<1e-10
  for l in row.get('launches',[]):
   assert not l[8] and not l[9]
   target=self.registry[l[1]]
   s=dict(source=l[0],side=l[2],at=l[6],target_team=target[1],target_role=target[2],victims=set(),hp=0,friendly_hp=0,opposing={0:set(),1:set(),2:set()},opposing_hp={0:0,1:0,2:0},all_friendly_hp=0)
   self.shells.append(s);self.pending.setdefault(l[0],[]).append(s)
  for d in row['damage']:
   if d['sourceRole']!='artillery' or d['dealt']<=0:continue
   due=[s for s in self.pending.get(d['source'],[]) if -1e-9<=d['t']-s['at']<=dt+1e-7]
   assert len(due)==1,('ambiguous shell attribution',d)
   s=due[0];assert s['side']==d['sourceTeam']
   role={'melee':0,'ranged':1,'artillery':2}[d['targetRole']]
   if d['targetTeam']!=s['side']:s['opposing'][role].add(d['target']);s['opposing_hp'][role]+=d['dealt']
   else:s['all_friendly_hp']+=d['dealt']
   if d['targetTeam']==0 and d['targetRole']=='ranged':
    if s['side']==1:s['victims'].add(d['target']);s['hp']+=d['dealt']
    else:s['friendly_hp']+=d['dealt']
  self.pending={src:[s for s in ss if row['t']-s['at']<=dt+1e-7] for src,ss in self.pending.items()};self.previous=row['t']
 def counts(self):
  from collections import Counter
  c=Counter()
  for s in self.shells:
   c['friendly_artillery_hp_to_own_ranged']+=s['friendly_hp']
   if s['side']==0:
    prefix='own_gun_targeted' if s['target_team']==1 and s['target_role']==2 else 'own_other_targeted'
    success=any(s['opposing'].values());c[prefix+'_launches']+=1;c[prefix+'_successful_shells']+=success
    c[prefix+'_distinct_opposing_victims']+=sum(map(len,s['opposing'].values()));c[prefix+'_friendly_hp']+=s['all_friendly_hp']
    for role,name in ((0,'melee'),(1,'ranged'),(2,'artillery')):c[prefix+'_'+name+'_victims']+=len(s['opposing'][role]);c[prefix+'_'+name+'_hp']+=s['opposing_hp'][role]
   if s['side']!=1:continue
   aimed=s['target_team']==0 and s['target_role']==1
   prefix='escort_targeted' if aimed else 'incidental_other_aim'
   c[prefix+'_launches']+=1;c[prefix+'_own_ranged_hp']+=s['hp'];c[prefix+'_distinct_victims']+=len(s['victims']);c[prefix+'_successful_shells']+=bool(s['victims'])
  return c

def shell_summary(counts):
 c=dict(counts);den=c.get('escort_targeted_successful_shells',0)
 success=c.get('own_gun_targeted_successful_shells',0)
 return dict(counts=c,all_opposing_victims_per_successful_own_gun_targeted_shell=c.get('own_gun_targeted_distinct_opposing_victims',0)/success if success else None,role_victims_per_successful_own_gun_targeted_shell={role:c.get('own_gun_targeted_'+role+'_victims',0)/success if success else None for role in ('melee','ranged','artillery')},own_ranged_victims_per_successful_enemy_escort_targeted_shell=c.get('escort_targeted_distinct_victims',0)/den if den else None)
