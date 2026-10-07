"""Stored-only, hash-verified analysis; no combat imports or execution."""
import collections,gzip,importlib.util,math,statistics
from common import *
from metrics import distance,point_for,reading,shift_for,target_for,gun_curve,ShellAudit,shell_summary
spec=importlib.util.spec_from_file_location('escort_spacing_analysis',CPP/'s4_spacing_probe_v1/analyze.py');spacing=importlib.util.module_from_spec(spec);spec.loader.exec_module(spacing)
spacing.HERE=HERE;spacing.fire.SOURCE=HERE
quantile=spacing.quantile;dist=spacing.dist
BINS=(0,10,20,30,60,150.1)
def hp_bin(t):return next(i for i in range(len(BINS)-1) if BINS[i]<=t<BINS[i+1])
def nearpoint(p,u):return math.hypot(p[0]-u[3],p[1]-u[4])
def escort_geometry(fight):
 c=collections.Counter();values=collections.defaultdict(list);bins=[collections.Counter() for _ in range(5)];first={};seen=set();last={};assignments={};deaths=[];current=None;gunsrow=None;initial=None;terminal=None;damagehp=0;last_audit=0;shells=ShellAudit()
 with gzip.open(HERE/'raw'/(fight['id']+'.jsonl.gz'),'rt') as stream:
  for line in stream:
   row=json.loads(line)
   if row.get('observerV1'):
    current=row;gunsrow=None;shells.observe(row)
    if row['step']==0:initial={u[0]:u for u in row['units']}
    for d in row['damage']:
     if d['died']:deaths.append(d)
     if d['targetTeam']==0 and d['targetRole']=='artillery':
      label=('friendly_' if d['sourceTeam']==0 else 'enemy_')+d['sourceRole'];bins[hp_bin(d['t'])][label]+=d['dealt'];damagehp+=d['dealt']
     if d['died'] and d['sourceTeam']==0 and d['targetTeam']==1 and d['targetRole']=='ranged' and d['sourceRole']=='ranged':
      c['ranged_enemy_ranged_last_hits_full']+=1;c['ranged_enemy_ranged_last_hits_lt20']+=d['t']<20;c['ranged_enemy_ranged_last_hits_lt30']+=d['t']<30
     if d['died'] and d['sourceTeam']==0 and d['targetTeam']==1 and d['targetRole']=='ranged' and d['sourceRole']=='artillery':
      c['artillery_enemy_ranged_last_hits_full']+=1;c['artillery_enemy_ranged_last_hits_lt20']+=d['t']<20;c['artillery_enemy_ranged_last_hits_lt30']+=d['t']<30
    continue
   if row.get('spacingProbe'):gunsrow=row;continue
   if not row.get('escortProbe'):
    if 'controllerStatus' in row:terminal=row
    continue
   assert current and row['step']==current['step'] and row['t']==current['t'] and row['step']==last_audit+1
   last_audit=row['step'];before={u[0]:u for u in row['prepare'] if u[5]>0};post={u[0]:u for u in current['units']};actions={a[0]:a for a in current['actions']}
   own=[u for u in before.values() if u[1]==0 and u[2]==2];enemy=[u for u in before.values() if u[1]==1 and u[2]==2];ers=[u for u in before.values() if u[1]==1 and u[2]==1];ours=[u for u in before.values() if u[1]==0 and u[2]==1]
   points={p['id']:p for p in row['points']};assert len(points)==len(row['points']);assert set(points)==({u[0] for u in ours} if own and enemy else set())
   if not (own and enemy):last.clear();continue
   valid=[]
   for side in (0,1):
    gs=[g for g in post.values() if g[1]==side and g[2]==2]
    for gun in gs:
     others=[g for g in gs if g[0]!=gun[0]]
     if not others:c[f'gun{side}_singleton_ticks']+=1;continue
     n=min(distance(gun,g) for g in others);values[f'gun{side}_nearest'].append(n)
     for lo,hi in ((10,20),(20,30)):
      if lo<=row['t']<hi:values[f'gun{side}_nearest_{lo}_{hi}'].append(n)
   for u in sorted(ours,key=lambda x:x[0]):
    uid=u[0];c['prepare_living_ranged_ticks']+=1;seen.add(uid);p=points[uid];expected=point_for(u,own,enemy,ers,row['dose'],row['width'],row['height'])
    anchor=dict(expected);arm=row.get('arm',12)
    if arm==15 and expected['direction']:
     shift=shift_for(u,ours);expected=dict(expected,raw=[expected['raw'][i]+shift[i] for i in (0,1)]);expected['clipped']=[min(row['width'],max(0,expected['raw'][0])),min(row['height'],max(0,expected['raw'][1]))]
    if 'p12Raw' in p:
     for key,label in (('raw','p12Raw'),('clipped','p12Clipped')):
      assert (p[label] is None)==(anchor[key] is None)
      if p[label] is not None:assert all(abs(a-b)<1e-7 for a,b in zip(p[label],anchor[key]))
    for key in ('gun','threat','direction'):assert p[key]==expected[key]
    for key in ('raw','clipped'):
     assert (p[key] is None)==(expected[key] is None)
     if p[key] is not None:assert all(abs(a-b)<1e-7 for a,b in zip(p[key],expected[key]))
    assert p['baseTarget']==p['base'][4];a=actions[uid]
    baseline=p.get('p12',p['base']);expected_target=target_for(u,own,ers) if arm==14 and row['accepted'] else 0
    assert p['command'][4]==(expected_target or baseline[4])
    assert p['command'][5]==baseline[5]
    if arm==14:assert p['command'][:4]==baseline[:4]
    if arm==15 and (not p['direction'] or not row['accepted']):assert p['command']==baseline
    if not a[8]:c['native_guard_hold_ticks']+=1
    else:
     assert abs(a[3]-min(row['width'],max(0,p['command'][0])))<1e-7 and abs(a[4]-min(row['height'],max(0,p['command'][1])))<1e-7 and a[5]==p['command'][2] and a[6]==p['command'][3]
     assert a[2]==p['command'][4];c['action_reconciled_ticks']+=1
    if row['applied'] and p['direction'] and row['accepted']:
     assert p['command'][0:2]==p['clipped'] and p['command'][3]==0
     assert p['command'][2]==int(nearpoint(p['clipped'],u)>2)
    else:assert p['command']==baseline or (arm==14 and p['command'][:4]==baseline[:4])
    threats={e[0] for e in ers if any(distance(e,g)<=e[7]+e[6]+g[6] for g in own) and distance(e,u)<=u[7]+u[6]+e[6]}
    c['target_opportunity_ticks']+=bool(threats);c['threat_selected_ticks']+=bool(threats) and a[2] in threats
    for lo,hi in ((10,20),(20,30)):
     if lo<=row['t']<hi:c[f'target_opportunity_ticks_{lo}_{hi}']+=bool(threats);c[f'threat_selected_ticks_{lo}_{hi}']+=bool(threats) and a[2] in threats
    if uid in assignments and assignments[uid]!=p['gun']:c['reassignment_ticks']+=1
    assignments[uid]=p['gun'];v=post.get(uid)
    if not p['direction']:c['degenerate_direction_ticks']+=1
    if v is None:c['post_step_dead_ticks']+=1
    arrived=False
    if p['direction']:
     valid.append(p);g=before[p['gun']];c['clipped_goal_ticks']+=p['raw']!=p['clipped']
     values['raw_assigned_gun_distance'].append(nearpoint(p['raw'],g));values['clipped_assigned_gun_distance'].append(nearpoint(p['clipped'],g))
     c['clipped_assigned_gun_within_splash49_ticks']+=nearpoint(p['clipped'],g)<=49
     others=[g for g in own if g[0]!=p['gun']]
     if others:
      for key in ('raw','clipped'):
       gaps=[nearpoint(p[key],g)-u[6]-g[6] for g in others];values[key+'_other_gun_body_clearance'].append(min(gaps));c[key+'_other_gun_body_overlap_ticks']+=min(gaps)<=0
     if gunsrow:
      goals=[g[8:10] for g in gunsrow['guns'] if g[0]!=p['gun']]
      if goals:values['clipped_other_gun_shifted_goal_distance'].append(min(math.dist(p['clipped'],g) for g in goals));c['coincident_other_gun_shifted_goal_ticks']+=any(math.dist(p['clipped'],g)<1e-9 for g in goals)
    if v is not None:
     neighbours=[q for q in post.values() if q[1]==0 and q[2]==1 and q[0]!=uid]
     if neighbours:
      nr=min(distance(v,q) for q in neighbours);values['realized_ranged_to_ranged_nearest'].append(nr)
      for lo,hi in ((10,20),(20,30)):
       if lo<=row['t']<hi:values[f'realized_ranged_to_ranged_nearest_{lo}_{hi}'].append(nr)
     else:c['post_ranged_singleton_ticks']+=1
     values['actual_displacement'].append(distance(u,v));c['displacement_known_ticks']+=1;c['moving_ticks']+=distance(u,v)>1e-6
     for lo,hi in ((10,20),(20,30)):
      if lo<=row['t']<hi:values[f'actual_displacement_{lo}_{hi}'].append(distance(u,v))
     postguns=[g for g in post.values() if g[1]==0 and g[2]==2]
     if postguns:
      ng=min(distance(v,g) for g in postguns);values['realized_ranged_to_gun_nearest'].append(ng)
      for lo,hi in ((10,20),(20,30)):
       if lo<=row['t']<hi:values[f'realized_ranged_to_gun_nearest_{lo}_{hi}'].append(ng)
     else:c['post_nearest_gun_unavailable_ticks']+=1
     if p['direction']:
      c['arrival_available_ticks']+=1
      c['p12_raw_anchor_arrival_ticks']+=nearpoint(anchor['raw'],v)<=20;c['p12_clipped_anchor_arrival_ticks']+=nearpoint(anchor['clipped'],v)<=20
      values['goal_shift_from_p12_px'].append(math.dist(p['raw'],anchor['raw']))
      rawerr=nearpoint(p['raw'],v);cliperr=nearpoint(p['clipped'],v);values['raw_point_error'].append(rawerr);values['clipped_goal_error'].append(cliperr)
      c['raw_arrival_ticks']+=rawerr<=20;arrived=cliperr<=20;c['clipped_arrival_ticks']+=arrived
      if arrived and uid not in first:first[uid]=dict(unit=uid,t=row['t'],prepare_t=row['prepareTime'],gun=p['gun'])
      c['holding_ticks']+=arrived and last.get(uid)==(True,p['gun'])
     per=[e for e in post.values() if e[1]==1 and e[2]==1]
     if per:
      nearest=min(distance(v,e) for e in per);values['own_ranged_to_enemy_ranged'].append(nearest)
      for lo,hi in ((10,20),(20,30)):
       if lo<=row['t']<hi:values[f'own_ranged_to_enemy_ranged_{lo}_{hi}'].append(nearest)
     else:c['nearest_enemy_ranged_unavailable_ticks']+=1
    last[uid]=(arrived,p['gun'])
   for key in ('raw','clipped'):
    for i,p in enumerate(valid):
     for q in valid[i+1:]:c[key+'_shared_point_pairs']+=math.dist(p[key],q[key])<1e-9
 if terminal:
  end={u[0]:u for u in current['units']};expected=sum(u[5] for u in initial.values() if u[1]==0 and u[2]==2)-sum(u[5] for u in end.values() if u[1]==0 and u[2]==2)
  assert math.isclose(expected,damagehp,abs_tol=1e-6),('gun HP conservation',fight['id'],expected,damagehp)
 assert last_audit==current['step'] and terminal==fight['summary']
 c['arrival_unavailable_ticks']=c['prepare_living_ranged_ticks']-c['arrival_available_ticks']
 c['first_arrival_units']=len(first);c['first_arrival_censored_units']=len(seen)-len(first)
 return dict(counts=c,values=values,gun_hp_loss_bins=bins,first_arrivals=list(first.values()),killers=deaths,shell_counts=shells.counts(),gun_survival=gun_curve(initial,deaths))

def escort_summary(c,values,bins):
 den=c['prepare_living_ranged_ticks'];opp=c['target_opportunity_ticks']
 return dict(counts=dict(c),window_threat_selection=[dict(interval=[lo,hi],opportunities=c[f'target_opportunity_ticks_{lo}_{hi}'],selected=c[f'threat_selected_ticks_{lo}_{hi}'],fraction=c[f'threat_selected_ticks_{lo}_{hi}']/c[f'target_opportunity_ticks_{lo}_{hi}'] if c[f'target_opportunity_ticks_{lo}_{hi}'] else None) for lo,hi in ((10,20),(20,30))],p12_raw_anchor_arrival_fraction=c['p12_raw_anchor_arrival_ticks']/den if den else None,p12_clipped_anchor_arrival_fraction=c['p12_clipped_anchor_arrival_ticks']/den if den else None,raw_arrival_fraction=c['raw_arrival_ticks']/den if den else None,clipped_arrival_fraction=c['clipped_arrival_ticks']/den if den else None,holding_fraction=c['holding_ticks']/den if den else None,threat_selection_fraction=c['threat_selected_ticks']/opp if opp else None,distributions={k:dist(v) for k,v in values.items()},gun_hp_loss_bins=[dict(interval=[BINS[i],BINS[i+1]],hp=dict(b)) for i,b in enumerate(bins)])

@stage('analysis')
def main():
 d=pins();fights=json.loads((HERE/'FIGHTS.json').read_text());assert len(fights)==120
 from run import task,verified
 expected={task(d,a,h,c,o)[0] for a in d['arms'] for h in d['heads'] for c in range(10) for o in d['orientations']};assert {r['id'] for r in fights}==expected
 # All raw/request/claim/stderr identities checked BEFORE any gzip is parsed.
 for r in fights:
  tag,req,_=task(d,r['arm'],r['head'],r['cluster'],r['orientation']);assert verified(tag,req)==r
 rows=[];per=[]
 for arm in d['arms']:
  for head in d['heads']:
   subset=[r for r in fights if (r['arm'],r['head'])==(arm,head)];assert len(subset)==20
   counters=[collections.Counter(),collections.Counter()];ns=[[],[]];early=[[],[]];single=[0,0];ticks=[0,0];ranges=[0,0];aud=collections.Counter();ec=collections.Counter();ev=collections.defaultdict(list);eb=[collections.Counter() for _ in range(5)];cell=[];sc=collections.Counter()
   for r in subset:
    remaining_check=remaining();assert remaining_check>0
    f=spacing.fire.analyze(r);g=spacing.geometry(r);e=escort_geometry(r);s=r['summary']
    sc.update(e['shell_counts']);ec.update(e['counts']);aud.update(g['audit'])
    for k,v in e['values'].items():ev[k].extend(v)
    for i in range(5):eb[i].update(e['gun_hp_loss_bins'][i])
    for i in (0,1):
     counters[i].update(f['sides'][i]);ns[i].extend(g['nearest_values'][i]);early[i].extend(g['early_values'][i]);single[i]+=g['nearest_singleton_ticks'][i];ticks[i]+=g['gun_phase_ticks'][i];ranges[i]+=g['gun_range_ticks'][i]
    row=dict(id=r['id'],arm=arm,head=head,cluster=r['cluster'],orientation=r['orientation'],elimination_win=s['enemySurvivors']==0 and s['survivors']>=1 and s['t']<150,timeout=s['t']>=150,S=s['survivors']-s['enemySurvivors'],duration_s=s['t'],enemy_guns_destroyed=10-s['artilleryAlive'][1],own_guns_lost=10-s['artilleryAlive'][0],own_losses=50-s['survivors'],sides=[spacing.side(x) for x in f['sides']],nearest=[dist(x) for x in g['nearest_values']],early_10_20_nearest=[dist(x) for x in g['early_values']],nearest_singleton_ticks=g['nearest_singleton_ticks'],gun_phase_ticks=g['gun_phase_ticks'],gun_range_ticks=g['gun_range_ticks'],spacing_audit=g['audit'],escort=escort_summary(e['counts'],e['values'],e['gun_hp_loss_bins']),first_arrivals=e['first_arrivals'],killers=e['killers'],escort_shells=shell_summary(e['shell_counts']),gun_survival=e['gun_survival'])
    cell.append(row);per.append(row)
   sides=[spacing.side(x) for x in counters];hp=sides[0]['artillery_hp_to_opposing_guns']
   rows.append(dict(arm=arm,head=head,fights=20,elimination_wins=sum(r['elimination_win'] for r in cell),timeouts=sum(r['timeout'] for r in cell),mean_S=statistics.mean(r['S'] for r in cell),mean_enemy_guns_destroyed=statistics.mean(r['enemy_guns_destroyed'] for r in cell),mean_own_guns_lost=statistics.mean(r['own_guns_lost'] for r in cell),mean_own_losses=statistics.mean(r['own_losses'] for r in cell),sides=sides,nearest=[dist(x) for x in ns],early_10_20_nearest=[dist(x) for x in early],nearest_singleton_ticks=single,gun_phase_ticks=ticks,gun_range_ticks=ranges,spacing_audit=dict(aud),enemy_over_own_artillery_hp_ratio=sides[1]['artillery_hp_to_opposing_guns']/hp if hp else None,escort=escort_summary(ec,ev,eb),escort_shells=shell_summary(sc),gun_survival=[dict(t=t,mean_alive=statistics.mean(next(v['alive'] for v in r['gun_survival'] if v['t']==t) for r in cell)) for t in (10,20,30,45,60)],own_ranged_killers=dict(collections.Counter(str(k['sourceTeam'])+'_'+k['sourceRole'] for r in cell for k in r['killers'] if k['targetTeam']==0 and k['targetRole']=='ranged'))))
   print(json.dumps(dict(analyzed=[arm,head],utc=utc())),flush=True)
 compact=dict(status='DONE',scope='descriptive development only',P12_sanity=json.loads((HERE/'P12_SANITY.json').read_text()),rows=rows,reading=reading(rows),declaration_sha256=sha(HERE/'DECLARATION.json'),fights_sha256=sha(HERE/'FIGHTS.json'))
 write(HERE/'COMPACT.json',compact);write(HERE/'SUMMARY.json',dict(**compact,fights=per));write(HERE/'ANALYSIS_VERIFICATION.json',dict(status='PASS',fights=120,raw_requests_claims_actions_points_and_HP_verified=True))
if __name__=='__main__':caffeinate();main()
