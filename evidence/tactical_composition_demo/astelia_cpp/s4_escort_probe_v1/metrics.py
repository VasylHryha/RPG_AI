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
def reading(rows):
 cells={r['arm']:r for r in rows if r['head']=='regular'};control=cells['P11'];out=[]
 for arm in ('P12','P13'):
  q=cells[arm];v=q['sides'][1]['gun_victims_per_successful_shell'];arrival=q['escort']['clipped_arrival_fraction'];kills=q['escort']['counts'].get('ranged_enemy_ranged_last_hits_lt20',0);base=control['escort']['counts'].get('ranged_enemy_ranged_last_hits_lt20',0)
  clearly=q['elimination_wins']>=5 and q['elimination_wins']>=control['elimination_wins']+3
  engage=None if arrival is None else arrival>=.5 and kills>=2*base and kills>=5
  lost=None if v is None else v>1.5
  text='Mixed/descriptive or unavailable; no complete declared reading'
  if lost:text='Own spacing lost by opponent-shell multiplicity; realization inconclusive'
  elif clearly and lost is False:text='Clearly-above-P11 descriptive candidate; no v7 permission or population-rate claim'
  elif engage and q['mean_own_guns_lost']==10 and lost is False:text='Arrive-and-engage with heavy gun losses; escort alone insufficient on this panel'
  elif arrival==0:text='No clipped-point arrival; escort realization inconclusive'
  out.append(dict(arm=arm,clearly_above_P11=clearly,arrive_and_engage=engage,spacing_lost=lost,enemy_shell_own_gun_victims_per_success=v,reading=text))
 return out
