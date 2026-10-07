"""Stored-only analysis; all identities checked before any trace is parsed."""
import collections,gzip,importlib.util,math,statistics,sys,signal,time
from common import *
spec=importlib.util.spec_from_file_location('historical_fire_analysis',CPP/'s4_fire_efficiency_v1/analyze.py');fire=importlib.util.module_from_spec(spec);spec.loader.exec_module(fire);fire.SOURCE=HERE

def quantile(xs,p):
 if not xs:return None
 xs=sorted(xs);x=(len(xs)-1)*p;i=int(x);return xs[i]+(xs[min(i+1,len(xs)-1)]-xs[i])*(x-i)
def dist(xs):return dict(n=len(xs),median=quantile(xs,.5),p10=quantile(xs,.1))
def geometry(r):
 nearest=[[],[]];early=[[],[]];single=[0,0];ticks=[0,0];ranges=[0,0];deaths=[];audit=collections.Counter();radials=[];shift=[];before=None;current=None;laststep=-1
 with gzip.open(HERE/'raw'/(r['id']+'.jsonl.gz'),'rt') as f:
  for line in f:
   row=json.loads(line)
   if row.get('observerV1'):
    assert row['step']==laststep+1;laststep=row['step'];current=row
    deaths.extend(d for d in row['damage'] if d['died'])
    if before and any(u[1]==1 and u[2]==2 for u in before['units']):
     for side in (0,1):
      guns=[u for u in row['units'] if u[1]==side and u[2]==2 and u[5]>0];enemies=[u for u in row['units'] if u[1]!=side and u[2]==2 and u[5]>0]
      for u in guns:
       ticks[side]+=1;ranges[side]+=any(u[8]<=math.hypot(u[3]-e[3],u[4]-e[4])<=u[7] for e in enemies)
       others=[v for v in guns if v[0]!=u[0]]
       if not others:single[side]+=1;continue
       n=min(math.hypot(u[3]-v[3],u[4]-v[4]) for v in others);nearest[side].append(n)
       if 10<=row['t']<20:early[side].append(n)
    before=row
   elif row.get('spacingProbe'):
    assert current and row['step']==current['step'] and row['t']==current['t']
    actions={a[0]:a for a in current['actions']}
    for g in row['guns']:
     audit['prepare_gun_ticks']+=1;clipped=abs(g[6]-g[8])>1e-9 or abs(g[7]-g[9])>1e-9;audit['clipped_goal_ticks']+=clipped
     n=math.hypot(g[10],g[11]);shift.append(n);radials.append(g[13]);audit['shift_ticks']+=n>1e-9;audit['zero_multiplier_shift_ticks']+=n>1e-9 and g[12]==0;audit['raw_goal_out_of_focus_band_ticks']+=not(g[14]<=g[13]<=g[15]);audit['coincident_pair_terms']+=g[17];audit['neighbour_terms']+=g[16]
     a=actions.get(g[0]);assert a is not None
     # Native guard can erase movement; count it, do not claim goal equality then.
     if not a[8]:audit['native_guard_hold_ticks']+=1
     else:
      assert abs(a[3]-g[8])<1e-7 and abs(a[4]-g[9])<1e-7 and a[5]==g[12] and a[6]==0
      audit['clipped_action_reconciled_ticks']+=1
 return dict(nearest_values=nearest,early_values=early,nearest_singleton_ticks=single,gun_phase_ticks=ticks,gun_range_ticks=ranges,killers=deaths,audit=dict(audit),radial_values=radials,shift_values=shift)

def side(c):
 c=collections.Counter(c);success=c['gun_launches_hit_any_gun'];damage=c['gun_target_shell_gun_damage']+c['other_target_shell_gun_damage']
 return dict(counts=dict(c),gun_targeted_launches=c['gun_launches'],successful_gun_targeted_shells=success,gun_victims=c['gun_target_shell_gun_victims'],gun_victims_per_successful_shell=c['gun_target_shell_gun_victims']/success if success else None,artillery_hp_to_opposing_guns=damage,incidental_hp=c['other_target_shell_gun_damage'],already_dead_before_impact=c['gun_launches_target_dead_before_scheduled_impact'],airborne_at_end=c['gun_launches_airborne_at_end'])
def reading(rows):
 a={r['arm']:r for r in rows if r['head']=='regular'};p=a['P5'];out=[]
 for k in ('P10','P11'):
  q=a[k];v=q['sides'][1]['gun_victims_per_successful_shell'];pv=p['sides'][1]['gun_victims_per_successful_shell'];ratio=q['enemy_over_own_artillery_hp_ratio'];pr=p['enemy_over_own_artillery_hp_ratio']
  comparisons=[q['nearest'][0][f]>p['nearest'][0][f] if q['nearest'][0][f] is not None and p['nearest'][0][f] is not None else None for f in ('median','p10')]
  realization='both_increased' if comparisons==[True,True] else 'neither_increased' if comparisons==[False,False] else 'mixed' if None not in comparisons else 'unavailable'
  if q['elimination_wins']>p['elimination_wins'] and q['elimination_wins']>0 and q['mean_gun_exchange']>p['mean_gun_exchange'] and q['mean_enemy_guns_destroyed']>p['mean_enemy_guns_destroyed']:message='Regular elimination and better-than-P5 candidate pattern; no resonator/causal claim'
  elif v is not None and pv is not None and v<pv and abs(v-1)<abs(pv-1) and ratio is not None and pr is not None and ratio<1<=pr and q['elimination_wins']==0:message='§19.6 favorable splash/exchange but no eliminations; supports this setting, insufficient for elimination, necessity unproven'
  elif v is not None and pv is not None and v>=pv:message='§19.6 inconclusive/unrealized spacing pattern' if realization=='neither_increased' else 'Distances increased but no demonstrated splash benefit at this setting' if realization=='both_increased' else 'Mixed/unavailable distance realization and nonfalling multiplicity: inconclusive'
  else:message='Mixed/inconclusive: no declared pattern fully applies'
  out.append(dict(arm=k,distance_realization=realization,reading=message))
 return out

@stage('analysis')
def main():
 start=time.monotonic();d=pins();allowance=min(1200,remaining());assert allowance>0
 fights=json.loads((HERE/'FIGHTS.json').read_text());assert len(fights)==120
 assert {(r['arm'],r['head'],r['cluster'],r['orientation']) for r in fights}=={(a,h,c,o) for a in d['arms'] for h in d['heads'] for c in range(10) for o in d['orientations']}
 for e in json.loads((HERE/'RAW_FILES_LOCAL.json').read_text())['files']:
  p=HERE/e['path'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
 for r in fights:
  assert sha(HERE/'raw'/(r['id']+'.jsonl.gz'))==r['raw_sha256']
  reqpath=HERE/'raw'/(r['id']+'_request.json');assert sha(reqpath)==r['request_sha256'];req=json.loads(reqpath.read_text());wanted=json.loads((HERE/(r['head'].upper()+'_REQUEST_TEMPLATE.json')).read_text());wanted['options']['seed']=d['development_seeds'][r['cluster']];wanted['options']['swapSides']=bool(r['orientation']);wanted['options']['ai'][0]['controller']=r['arm'];assert req==wanted
 summaries=[];allrows=[]
 for arm in d['arms']:
  for head in d['heads']:
   subset=[r for r in fights if (r['arm'],r['head'])==(arm,head)];counters=[collections.Counter(),collections.Counter()];ns=[[],[]];es=[[],[]];rad=[];shift=[];aud=collections.Counter();single=[0,0];ticks=[0,0];ranges=[0,0];kills=[];rs=[]
   for r in subset:
    f=fire.analyze(r);g=geometry(r);s=r['summary'];deaths=g.pop('killers');kills.extend(deaths)
    for i in (0,1):
     counters[i].update(f['sides'][i]);ns[i].extend(g['nearest_values'][i]);es[i].extend(g['early_values'][i]);single[i]+=g['nearest_singleton_ticks'][i];ticks[i]+=g['gun_phase_ticks'][i];ranges[i]+=g['gun_range_ticks'][i]
    rad.extend(g['radial_values']);shift.extend(g['shift_values']);aud.update(g['audit'])
    row=dict(id=r['id'],arm=arm,head=head,cluster=r['cluster'],orientation=r['orientation'],elimination_win=s['enemySurvivors']==0 and s['survivors']>=1 and s['t']<150,timeout=s['t']>=150,S=s['survivors']-s['enemySurvivors'],duration_s=s['t'],enemy_guns_destroyed=10-s['artilleryAlive'][1],own_guns_lost=10-s['artilleryAlive'][0],own_losses=50-s['survivors'],enemy_units_killed=50-s['enemySurvivors'],sides=[side(c) for c in f['sides']],nearest=[dist(x) for x in g['nearest_values']],nearest_singleton_ticks=g['nearest_singleton_ticks'],audit=g['audit'],killers=deaths,first_enemy_gun_kill_s=min((x['t'] for x in deaths if x['targetTeam']==1 and x['targetRole']=='artillery'),default=None))
    rs.append(row);allrows.append(row)
   sides=[side(c) for c in counters];ownhp=sides[0]['artillery_hp_to_opposing_guns'];enemyhp=sides[1]['artillery_hp_to_opposing_guns'];first=[r['first_enemy_gun_kill_s'] for r in rs if r['first_enemy_gun_kill_s'] is not None];wins=[r['duration_s'] for r in rs if r['elimination_win']];totalenemy=sum(r['enemy_units_killed'] for r in rs)
   summaries.append(dict(arm=arm,head=head,fights=20,elimination_wins=sum(r['elimination_win'] for r in rs),timeouts=sum(r['timeout'] for r in rs),mean_S=statistics.mean(r['S'] for r in rs),mean_enemy_guns_destroyed=statistics.mean(r['enemy_guns_destroyed'] for r in rs),mean_own_guns_lost=statistics.mean(r['own_guns_lost'] for r in rs),mean_gun_exchange=statistics.mean(r['enemy_guns_destroyed']-r['own_guns_lost'] for r in rs),mean_own_losses=statistics.mean(r['own_losses'] for r in rs),own_losses_per_enemy_kill=sum(r['own_losses'] for r in rs)/totalenemy if totalenemy else None,elimination_times_s=wins,first_enemy_gun_kill_s=fire.distribution(first),first_enemy_gun_kill_censored=20-len(first),sides=sides,enemy_over_own_artillery_hp_ratio=enemyhp/ownhp if ownhp else None,nearest=[dist(x) for x in ns],early_10_20_nearest=[dist(x) for x in es],nearest_singleton_ticks=single,gun_phase_ticks=ticks,gun_range_ticks=ranges,gun_range_fraction=[ranges[i]/ticks[i] if ticks[i] else None for i in (0,1)],audit=dict(aud),raw_shift_px=dist(shift),raw_goal_focus_radius_px=dist(rad),killers_by_source_team_role=dict(collections.Counter(str(x['sourceTeam'])+'_'+x['sourceRole'] for x in kills)),own_gun_killers_by_team_role=dict(collections.Counter(str(x['sourceTeam'])+'_'+x['sourceRole'] for x in kills if x['targetTeam']==0 and x['targetRole']=='artillery'))))
   print(json.dumps(dict(analyzed_cell=[arm,head],seconds=time.monotonic()-start)),flush=True)
 compact=dict(status='DONE',scope='descriptive development only',P5_sanity=json.loads((HERE/'P5_SANITY.json').read_text()),rows=summaries,reading=reading(summaries));write(HERE/'COMPACT.json',compact);write(HERE/'SUMMARY.json',dict(**compact,fights=allrows));write(HERE/'ANALYSIS_VERIFICATION.json',dict(status='PASS',fights=120,all_raw_hashes_requests_and_casualties_reconciled=True))
if __name__=='__main__':
 from common import caffeinate
 caffeinate();main()
