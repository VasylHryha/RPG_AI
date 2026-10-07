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
def shift_for(u,ours):
 sx=sy=0
 for v in sorted(ours,key=lambda x:x[0]):
  if v[0]==u[0]:continue
  dx,dy=u[3]-v[3],u[4]-v[4];d=math.hypot(dx,dy)
  if d<58:
   sx+=(58-d)*(dx/d if d else (-1 if u[0]<v[0] else 1))
   sy+=(58-d)*(dy/d if d else 0)
 return [sx,sy]
def target_for(u,own,ers):
 candidates=[e for e in ers if distance(u,e)<=u[7]+u[6]+e[6] and any(distance(e,g)<=e[7]+e[6]+g[6] for g in own)]
 return min(candidates,key=lambda e:(distance(u,e),e[0]))[0] if candidates else 0
CURVE_TIMES=(10,20,30,45,60)
def gun_curve(initial,deaths):
 ids={u[0] for u in initial.values() if u[1]==0 and u[2]==2}
 assert len({d['target'] for d in deaths})==len(deaths),'duplicate deaths'
 times={d['target']:d['t'] for d in deaths}
 return [dict(t=t,alive=sum(times.get(uid,math.inf)>t for uid in ids)) for t in CURVE_TIMES]
def reading(rows):
 cells={r['arm']:r for r in rows if r['head']=='regular'};control=cells['P12'];out=[]
 for arm in ('P14','P15'):
  q=cells[arm];v=q['sides'][1]['gun_victims_per_successful_shell']
  above=q['elimination_wins']>=8 and q['elimination_wins']>=control['elimination_wins']+3
  out.append(dict(arm=arm,clearly_above_P12=above,observed_owner_criterion=q['elimination_wins']>=11,spacing_lost=None if v is None else v>1.5,reading='Clearly-above-P12 descriptive candidate' if above else 'Descriptive; above-P12 rule not met',limits='Ten paired development clusters; no population claim or v7 permission'))
 return out

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
   s=dict(source=l[0],side=l[2],at=l[6],target_team=target[1],target_role=target[2],victims=set(),hp=0,friendly_hp=0)
   self.shells.append(s);self.pending.setdefault(l[0],[]).append(s)
  for d in row['damage']:
   if d['sourceRole']!='artillery' or d['dealt']<=0:continue
   due=[s for s in self.pending.get(d['source'],[]) if -1e-9<=d['t']-s['at']<=dt+1e-7]
   assert len(due)==1,('ambiguous shell attribution',d)
   s=due[0];assert s['side']==d['sourceTeam']
   if d['targetTeam']==0 and d['targetRole']=='ranged':
    if s['side']==1:s['victims'].add(d['target']);s['hp']+=d['dealt']
    else:s['friendly_hp']+=d['dealt']
  self.pending={src:[s for s in ss if row['t']-s['at']<=dt+1e-7] for src,ss in self.pending.items()};self.previous=row['t']
 def counts(self):
  from collections import Counter
  c=Counter()
  for s in self.shells:
   c['friendly_artillery_hp_to_own_ranged']+=s['friendly_hp']
   if s['side']!=1:continue
   aimed=s['target_team']==0 and s['target_role']==1
   prefix='escort_targeted' if aimed else 'incidental_other_aim'
   c[prefix+'_launches']+=1;c[prefix+'_own_ranged_hp']+=s['hp'];c[prefix+'_distinct_victims']+=len(s['victims']);c[prefix+'_successful_shells']+=bool(s['victims'])
  return c

def shell_summary(counts):
 c=dict(counts);den=c.get('escort_targeted_successful_shells',0)
 return dict(counts=c,own_ranged_victims_per_successful_enemy_escort_targeted_shell=c.get('escort_targeted_distinct_victims',0)/den if den else None)
