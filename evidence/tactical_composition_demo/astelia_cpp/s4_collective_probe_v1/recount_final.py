"""Stored-only telemetry recount; inherited shell identity logic plus realization audits."""
import pathlib,sys,json,gzip,math,statistics,collections,time,signal,importlib.util,re
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent;REPO=CPP.parents[2];sys.path.insert(0,str(CPP));from build_admission import sha
spec=importlib.util.spec_from_file_location('old_focus_analysis',CPP/'s4_focus_probe_v1/analyze.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base);base.HERE=HERE
write=lambda p,v:p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
_CONFIG=CPP/'src/native/observer_v1_world.cpp'
_DIM=re.search(r'Config sandboxConfig\(\) \{\s*Config c; c.width=([0-9.]+); c.height=([0-9.]+);',_CONFIG.read_text());assert _DIM
_WIDTH,_HEIGHT=map(float,_DIM.groups())
assert 'Config c=sandboxConfig();c.rules=Rules::Game' in _CONFIG.read_text()
_CODEC=CPP/'src/native/observer_v1_config_codec.cpp'
assert 'rules=="game"?gameConfig():sandboxConfig()' in _CODEC.read_text()
for _head in ('regular','novice'):
 _opts=json.loads((HERE/(_head.upper()+'_REQUEST_TEMPLATE.json')).read_text())['options']
 assert _opts['rules']=='game' and _opts.get('width',_WIDTH)==_WIDTH and _opts.get('height',_HEIGHT)==_HEIGHT
def axis(enemies):
 if len(enemies)<2:return None
 x=sum(e[1] for e in enemies)/len(enemies);y=sum(e[2] for e in enemies)/len(enemies);a=sum((e[1]-x)**2 for e in enemies);b=sum((e[1]-x)*(e[2]-y) for e in enemies);c=sum((e[2]-y)**2 for e in enemies)
 if a+c<=1e-12 or math.hypot(a-c,2*b)<=1e-10*max(1,a+c):return None
 return .5*math.atan2(2*b,a-c)
def angle_change(a,b):return abs((b-a+math.pi/2)%math.pi-math.pi/2)*180/math.pi if a is not None and b is not None else None
def geometry(r):
 wave=None;wave_axis=None;kill_axis=None;firstkill=None;wave_ids=[];kill_ids=[];initial_ids=[];reach_time=None;reach_counts=None;row=None;exposure=0;gun_ticks=0;wave_trigger=None;enemy_count_at_wave=None;post_ids=set();escort_ids=set();escort_ticks=0;escort_eligible=0;post_ticks=0;staging_outside=0;post_outside=0;staged_ticks=0;assignment_changes=0;last_assign=None;target_changes=0;last_target=None;ticks=0;previous_has_enemy=False
 def sample(obs,committed):
  nonlocal exposure,gun_ticks
  if not committed:return
  enemies=[u for u in obs['units'] if u[1]==1 and u[2]==2]
  for u in obs['units']:
   if u[1]==0 and u[2]==2:
    gun_ticks+=1;exposure+=sum(e[8]<=math.hypot(u[3]-e[3],u[4]-e[4])<=e[7] for e in enemies)
 with gzip.open(HERE/'raw'/(r['id']+'.jsonl.gz'),'rt') as f:
  for line in f:
   obj=json.loads(line)
   if obj.get('observerV1'):
    row=obj;ticks+=1
    if firstkill is None:firstkill=min((d['t'] for d in row['damage'] if d['died'] and d['targetTeam']==1 and d['targetRole']=='artillery'),default=None)
    if r['arm']=='P5' and row['step']>0:sample(row,previous_has_enemy)
    previous_has_enemy=any(u[1]==1 and u[2]==2 for u in row['units'])
   elif 'collectiveProbe' in obj:
    p=obj['collectiveProbe'];assert row and p['t']==row['t'];guns=p['guns'];enemies=p['enemyGuns']
    if not initial_ids and guns:initial_ids=[g[0] for g in guns]
    if p['wave'] and wave is None:
     wave=p['waveTime'];wave_axis=axis(enemies);wave_ids=[e[0] for e in enemies];wave_trigger=dict(reason=p['reason'],t=wave,ready=p['ready'],living=p['living'],initial_guns=len(initial_ids),own_deaths_before_wave=len(initial_ids)-p['living']);enemy_count_at_wave=len(enemies)
    if p['wave'] and guns and reach_time is None and sum(g[9] for g in guns)>=math.ceil(.8*len(guns)):
     reach_time=p['t'];reach_counts=dict(living=len(guns),engaged=sum(g[9] for g in guns),initial_cohort=len(initial_ids),initial_cohort_engaged=sum(g[9] for g in guns if g[0] in initial_ids))
    if firstkill is not None and kill_axis is None and p['t']==firstkill:kill_axis=axis(enemies);kill_ids=[e[0] for e in enemies]
    if row['step']>0:sample(row,p['wave'] and bool(guns))
    staging_outside+=sum(g[10] for g in guns if not p['wave']);staged_ticks+=sum(g[8] for g in guns if not p['wave'])
    if p['wave']:
     # Arrival references actual positions after step at the mathematical posts computed during prepare.
     actual={u[0]:u for u in row['units']}
     for g in guns:
      if g[0] in actual:
       u=actual[g[0]];arrived=math.hypot(u[3]-g[5],u[4]-g[6])<=20;post_ticks+=arrived
       if arrived:post_ids.add(g[0])
      post_outside+=g[5]<0 or g[5]>_WIDTH or g[6]<0 or g[6]>_HEIGHT
     for e in p['escorts']:
      escort_eligible+=bool(e[6]);u=actual.get(e[0]);arrived=bool(u and math.hypot(u[3]-e[3],u[4]-e[4])<=20);escort_ticks+=arrived
      if arrived:escort_ids.add(e[0])
    # Rank ordering captures reassignment without confusing translated target positions.
    assign=tuple(g[0] for g in guns)
    if last_assign is not None and assign!=last_assign:assignment_changes+=1
    last_assign=assign
    if p['target'] and last_target is not None and p['target']!=last_target:target_changes+=1
    if p['target']:last_target=p['target']
 latency=reach_time-wave if wave is not None and reach_time is not None else None
 angle=angle_change(wave_axis,kill_axis) if wave is not None and firstkill is not None and firstkill>=wave else None
 elimination=r['summary']['enemySurvivors']==0 and r['summary']['survivors']>=1 and r['summary']['t']<150
 before=elimination and r['arm']!='P5' and (wave is None or r['summary']['t']<wave)
 return dict(elimination_before_wave=before,elimination_after_wave=elimination and r['arm']!='P5' and not before,exposure_sum=exposure,committed_gun_ticks=gun_ticks,mean_realized_exposure=exposure/gun_ticks if gun_ticks else None,wave=wave_trigger,wave_started=wave is not None,simultaneity_s=latency,simultaneity_counts=reach_counts,simultaneity_status='not_applicable_P5' if r['arm']=='P5' else 'observed' if latency is not None else 'censored',enemy_line_angle_change_degrees=angle,line_angle_status='observed' if angle is not None else 'unavailable',enemy_ids_at_wave=wave_ids,enemy_ids_at_first_kill=kill_ids,post_arrival_guns=len(post_ids),post_arrival_gun_ticks=post_ticks,escort_arrival_units=len(escort_ids),escort_arrival_unit_ticks=escort_ticks,escort_focus_eligible_unit_ticks=escort_eligible,staging_outside_gun_ticks=staging_outside,post_outside_gun_ticks=post_outside,staged_gun_ticks=staged_ticks,assignment_changes=assignment_changes,target_changes=target_changes)
def aggregate(rows):
 out=[]
 for arm in ('P5','P7','P8','P9'):
  for head in ('regular','novice'):
   a=[r for r in rows if r['arm']==arm and r['head']==head];assert len(a)==20
   sums={k:sum(r[k] for r in a) for k in ('enemy_guns_destroyed','own_gun_losses','own_losses','enemy_units_killed','shell_hits_on_enemy_guns','shells_fired_at_enemy_guns','exposure_sum','committed_gun_ticks','post_arrival_gun_ticks','escort_arrival_unit_ticks','escort_focus_eligible_unit_ticks','staging_outside_gun_ticks','post_outside_gun_ticks')}
   first=[r['time_to_first_enemy_gun_kill_s'] for r in a if r['time_to_first_enemy_gun_kill_s'] is not None];lat=[r['simultaneity_s'] for r in a if r['simultaneity_s'] is not None];angles=[r['enemy_line_angle_change_degrees'] for r in a if r['enemy_line_angle_change_degrees'] is not None];killers=collections.Counter((d['team'],d['role']) for r in a for d in r['own_gun_killers'])
   out.append(dict(arm=arm,head=head,n=20,elimination_wins=sum(r['elimination_win'] for r in a),elimination_before_wave=sum(r['elimination_before_wave'] for r in a),elimination_after_wave=sum(r['elimination_after_wave'] for r in a),timeouts=sum(r['timeout'] for r in a),mean_S=statistics.mean(r['S'] for r in a),mean_enemy_guns_destroyed=sums['enemy_guns_destroyed']/20,mean_own_gun_losses=sums['own_gun_losses']/20,mean_own_losses=sums['own_losses']/20,mean_gun_exchange=(sums['enemy_guns_destroyed']-sums['own_gun_losses'])/20,own_losses_per_enemy_kill=sums['own_losses']/sums['enemy_units_killed'] if sums['enemy_units_killed'] else None,first_gun_kill_fights=len(first),mean_first_enemy_gun_kill_s=statistics.mean(first) if first else None,waves_started=sum(r['wave_started'] for r in a),wave_reasons=dict(collections.Counter(r['wave']['reason'] for r in a if r['wave'])),simultaneity_observed_fights=len(lat),mean_simultaneity_s=statistics.mean(lat) if lat else None,line_angle_observed_fights=len(angles),mean_enemy_line_angle_change_degrees=statistics.mean(angles) if angles else None,mean_realized_exposure=sums['exposure_sum']/sums['committed_gun_ticks'] if sums['committed_gun_ticks'] else None,fights_reaching_posts=sum(r['post_arrival_guns']>0 for r in a),fights_escorts_reaching_points=sum(r['escort_arrival_units']>0 for r in a),own_gun_killers=[dict(team=t,role=k,kills=v) for (t,k),v in sorted(killers.items())],**sums))
 return out
def reading(rows):
 a={r['arm']:r for r in rows if r['head']=='regular'};p=a['P5'];q=a['P9'];wins=q['elimination_wins']>0 or q['mean_enemy_guns_destroyed']>=7 and q['mean_own_gun_losses']<q['mean_enemy_guns_destroyed']
 better=[a[k] for k in ('P7','P8') if a[k]['mean_enemy_guns_destroyed']>p['mean_enemy_guns_destroyed'] and a[k]['mean_gun_exchange']>p['mean_gun_exchange']]
 if wins:
  if not q['waves_started'] or not q['fights_reaching_posts'] or (q['elimination_wins'] and not q['elimination_after_wave'] and not(q['mean_enemy_guns_destroyed']>=7 and q['mean_own_gun_losses']<q['mean_enemy_guns_destroyed'])):return 'P9 matches favorable outcome pattern, but wave/posts were unrealized: inconclusive for collective end-on mechanism'
  return 'P9 candidate end-on collective bundle worth encoding; mechanism not causally identified'
 if better:
  best=max(better,key=lambda r:(r['mean_gun_exchange'],r['mean_enemy_guns_destroyed']))
  if not(q['mean_enemy_guns_destroyed']>best['mean_enemy_guns_destroyed'] and q['mean_gun_exchange']>best['mean_gun_exchange']):
   if not best['waves_started'] or best['arm']=='P8' and not best['fights_escorts_reaching_points']:return 'P7/P8 improve on P5, but wave/screen unrealized: inconclusive for intended mechanism'
   return 'P7/P8 improve on P5; P9 adds no improvement on both metrics; synchrony/screen candidate, geometry not excluded'
 if all(a[k]['mean_gun_exchange']<=p['mean_gun_exchange'] for k in ('P7','P8','P9')):return 'No arm improves P5 gun exchange at this setting; return to telemetry, without general rejection'
 return 'Mixed/inconclusive; no declared outcome pattern fully applies'
def main():
 start=time.time();awake=time.monotonic();write(HERE/'ANALYSIS_SOURCE_PINS.json',dict(script_sha256=sha(HERE/'recount_final.py'),original_pre_fight_analyzer_sha256=sha(HERE/'analyze.py'),arena_width=_WIDTH,arena_height=_HEIGHT,native_config_sha256=sha(_CONFIG)));used=60+sum(json.loads(p.read_text())['awake_seconds'] for p in HERE.glob('STAGE_*.json'));assert used<3600
 def stop(*args):raise TimeoutError('analysis compute cap')
 signal.signal(signal.SIGALRM,stop);signal.alarm(max(1,int(min(1200,3600-used))));fights=json.loads((HERE/'FIGHTS.json').read_text());d=json.loads((HERE/'DECLARATION.json').read_text());assert len(fights)==160;rows=[]
 assert {(r['arm'],r['head'],r['cluster'],r['orientation']) for r in fights}=={(a,h,c,o) for a in d['arms'] for h in d['heads'] for c in range(10) for o in (0,1)}
 for r in fights:
  path=HERE/'raw'/(r['id']+'_request.json');assert sha(path)==r['request_sha256'];req=json.loads(path.read_text());template=json.loads((HERE/(r['head'].upper()+'_REQUEST_TEMPLATE.json')).read_text());template['options']['seed']=d['development_seeds'][r['cluster']];template['options']['swapSides']=bool(r['orientation']);template['options']['ai'][0]['controller']=r['arm'];assert req==template
  rows.append(dict(**base.analyze(r),**geometry(r)))
  if len(rows)%10==0:
   elapsed=time.monotonic()-awake;print(json.dumps(dict(recounted=len(rows),seconds=elapsed)),flush=True)
   if elapsed*160/len(rows)>3600-used:raise TimeoutError('analysis projection exceeds remaining1h')
 aggregates=aggregate(rows);paired=[]
 for head in ('regular','novice'):
  control={(r['cluster'],r['orientation']):r for r in rows if r['arm']=='P5' and r['head']==head}
  for arm in ('P7','P8','P9'):
   a=[r for r in rows if r['arm']==arm and r['head']==head];paired.append(dict(head=head,arm=arm,paired_cells=20,mean_kills_delta=sum(r['enemy_guns_destroyed']-control[(r['cluster'],r['orientation'])]['enemy_guns_destroyed'] for r in a)/20,mean_exchange_delta=sum((r['enemy_guns_destroyed']-r['own_gun_losses'])-(control[(r['cluster'],r['orientation'])]['enemy_guns_destroyed']-control[(r['cluster'],r['orientation'])]['own_gun_losses']) for r in a)/20))
 result=dict(paired_deltas_vs_P5=paired,status='DONE',scope='descriptive development scripted probe; no scientific/registration/readiness verdict',outcome_reading=reading(aggregates),rows=aggregates,fights=rows);write(HERE/'SUMMARY.json',result);write(HERE/'COMPACT.json',{k:v for k,v in result.items() if k!='fights'});write(HERE/'RAW_FILES_LOCAL.json',dict(files=[dict(path=str(p.relative_to(HERE)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted((HERE/'raw').iterdir())]));write(HERE/'ANALYSIS_VERIFICATION.json',dict(status='PASS',fights=160,all_raw_hashes_requests_and_casualties_reconciled=True,elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake));print(json.dumps(aggregates))
if __name__=='__main__':main()
