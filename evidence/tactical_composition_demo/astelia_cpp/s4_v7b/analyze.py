"""Hash-verified stored analysis; descriptive clustered readings, never executes fights."""
import collections,gzip,importlib.util,math,statistics
from common import *
from protocol import *
from run import RAW,verified,audit_raw,tuning_receipt
spec=importlib.util.spec_from_file_location('delivered_p16_metrics',CPP/'s4_escort_probe_v3/metrics.py')
legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)

def ratio(a,b):return a/b if b else None

def telemetry(record):
 counters=collections.Counter();combos=collections.Counter();pair_modes=collections.Counter();nearest=[];deaths=[];initial=None;post=None;last_step=0;shells=legacy.ShellAudit();firing=collections.Counter()
 with gzip.open(RAW/(record['tag']+'.jsonl.gz'),'rt') as f:
  for line in f:
   r=json.loads(line)
   if r.get('observerV1'):
    post=r;shells.observe(r)
    if r['step']==0:initial={u[0]:u for u in r['units']}
    for d in r['damage']:
     if d['died']:deaths.append(d)
     if d['died'] and d['sourceTeam']==0 and d['sourceRole']=='artillery' and d['targetTeam']==1 and d['targetRole']=='ranged':counters['artillery_enemy_ranged_kills_lt20']+=int(d['t']<20);counters['artillery_enemy_ranged_kills_lt30']+=int(d['t']<30)
    for launch in r['launches']:
     if launch[2]==0:firing[str(launch[1])]+=1
    guns=[u for u in r['units'] if u[1]==0 and u[2]==2]
    for g in guns:
     other=[u for u in guns if u[0]!=g[0]]
     if other:nearest.append(min(legacy.distance(g,u) for u in other))
    continue
   if r.get('decisionDiagnostics'):
    if r['side']==0:
     for u in r['units']:
      for p in u['pairs']:pair_modes[p['mode']]+=1
    continue
   if not r.get('v7Telemetry'):continue
   if not post or r['step']!=post['step'] or r['step']!=last_step+1 or not r['accepted']:raise RuntimeError('telemetry sequence/integration failure')
   last_step=r['step'];before={u[0]:u for u in r['prepare'] if u[5]>0};actual={u[0]:u for u in post['units']}
   choices={q['id']:q for q in r['choices']};arm=record['meta']['arm']
   expected_own={u[0] for u in before.values() if u[1]==0}
   if arm!='historicalP16' and set(choices)!=expected_own:raise RuntimeError('missing per-unit source telemetry')
   for q in choices.values():
    if arm in ('v7','omega0') and (q['source']=='P16')!=(q['mode']=='commit'):raise RuntimeError('gate/source mismatch')
    if q['source'] not in ('P16','v6') or q['command']!=(q['p16'] if q['source']=='P16' else q['baseline']):raise RuntimeError('selected source mismatch')
    if arm=='forcedP16' and q['source']!='P16' or arm=='forcedv6' and q['source']!='v6':raise RuntimeError('forced selector mismatch')
    counters['selected_'+q['source']+'_unit_ticks']+=1;counters['gate_transitions']+=q['transition'];counters['target_differs_between_sources_ticks']+=q['p16'][4]!=q['baseline'][4]
    if before[q['id']][2]==0 and q['p16']!=q['baseline']:raise RuntimeError('melee changed')
   own=[u for u in before.values() if u[1]==0 and u[2]==2];enemy=[u for u in before.values() if u[1]==1 and u[2]==2];ranged=[u for u in before.values() if u[1]==1 and u[2]==1]
   width,height=r['width'],r['height'];oracle=legacy.gun_focus_oracle(list(before.values()),width,height,True)
   if {g['id'] for g in r['guns']}!=set(oracle):raise RuntimeError('missing gun geometry telemetry')
   for g in r['guns']:
    q=oracle[g['id']];command=g['command'];expected=q['command']
    if any(abs(command[i]-expected[i])>1e-7 for i in range(4)):raise RuntimeError('P16 geometry oracle mismatch')
    if g['focus']!=q['focus'] or g['anchor']!=q['anchor'] or q['target'] is not None and command[4]!=q['target']:raise RuntimeError('P16 focus oracle mismatch')
    chosen=command[4] if arm=='historicalP16' else choices[g['id']]['command'][4]
    counters['gun_focus_ticks']+=1
    if chosen in q['values_by_gun']:counters['gun_target_V_sum']+=q['values_by_gun'][chosen];counters['gun_target_V_ticks']+=1
    selected=arm=='historicalP16' or choices[g['id']]['source']=='P16'
    if not selected:continue
    if chosen in q['values_by_gun']:counters['P16_selected_target_V_sum']+=q['values_by_gun'][chosen];counters['P16_selected_target_V_ticks']+=1
    focus=before[g['focus']];radial=lambda xy:math.hypot(xy[0]-focus[3],xy[1]-focus[4])
    counters['selected_gun_post_ticks']+=1
    counters['raw_goal_outside_band_ticks']+=not g['minimum']<=radial(g['raw'])<=g['range']
    counters['clipped_goal_outside_band_ticks']+=not g['minimum']<=radial(g['clipped'])<=g['range']
    counters['post_arrival_prepare_ticks']+=math.hypot(before[g['id']][3]-g['clipped'][0],before[g['id']][4]-g['clipped'][1])<=20
    u=actual.get(g['id']);counters['post_surviving_gun_ticks']+=u is not None
    post_focus=actual.get(g['focus'])
    if u is not None and post_focus is not None:
     counters['post_alive_gun_and_focus_ticks']+=1
     counters['actual_in_focus_band_ticks']+=u[8]<=legacy.distance(u,post_focus)<=u[7]
   for p in r['escorts']:
    u=before[p['id']];q=legacy.point_for(u,own,enemy,ranged,60,width,height)
    if p['gun']!=q['gun'] or p['direction']!=q['direction']:raise RuntimeError('escort assignment oracle mismatch')
    if not p['direction']:counters['escort_degenerate_ticks']+=1;continue
    if any(abs(a-b)>1e-7 for a,b in zip(p['clipped'],q['clipped'])):raise RuntimeError('escort point oracle mismatch')
    source='P16' if arm=='historicalP16' else choices[p['id']]['source'];gun_source='P16' if arm=='historicalP16' else choices[p['gun']]['source']
    combos[source+'_escort__'+gun_source+'_gun']+=1
    if source=='P16':
     counters['selected_escort_ticks']+=1
     after=actual.get(p['id']);counters['escort_surviving_ticks']+=after is not None
     if after is not None:counters['escort_arrival_post_ticks']+=math.hypot(after[3]-p['clipped'][0],after[4]-p['clipped'][1])<=20
 if initial is None or last_step==0:raise RuntimeError('missing validation telemetry')
 own_deaths=[d for d in deaths if d['targetTeam']==0 and d['targetRole']=='artillery']
 curve=legacy.gun_curve(initial,own_deaths)
 shellcounts=collections.Counter()
 for s in shells.shells:
  if s['target_team']==s['side'] or s['target_role']!=2:continue
  prefix='own' if s['side']==0 else 'enemy';success=bool(s['opposing'][2])
  shellcounts[prefix+'_gun_damage_successful_shells']+=success
  shellcounts[prefix+'_gun_victims']+=len(s['opposing'][2])
 return dict(in_band_denominator='P16-selected gun ticks with gun and focus both alive after the step; both centres from post snapshot',counts=dict(counters),escort_gun_source_combinations=dict(combos),pair_mode_ticks=dict(pair_modes),gun_survival=curve,chosen_target_V=ratio(counters['gun_target_V_sum'],counters['gun_target_V_ticks']),P16_selected_chosen_target_V=ratio(counters['P16_selected_target_V_sum'],counters['P16_selected_target_V_ticks']),escort_arrival_fraction=ratio(counters['escort_arrival_post_ticks'],counters['selected_escort_ticks']),post_arrival_fraction=ratio(counters['post_arrival_prepare_ticks'],counters['selected_gun_post_ticks']),actual_in_focus_band_fraction=ratio(counters['actual_in_focus_band_ticks'],counters['post_alive_gun_and_focus_ticks']),nearest_own_gun_distance=dict(samples=len(nearest),median=statistics.median(nearest) if nearest else None,p10=sorted(nearest)[int(.1*(len(nearest)-1))] if nearest else None),shell_counts=dict(shellcounts),gun_victims_per_gun_damaging_shell={s:ratio(shellcounts[s+'_gun_victims'],shellcounts[s+'_gun_damage_successful_shells']) for s in ('own','enemy')},inherited_shell_summary=legacy.shell_summary(shells.counts()),firing_targets=dict(firing),complex_diagnostics=record['summaries'][0]['complexDiagnostics'])

def analyze():
 d=pins();t=tuning_receipt();audit_raw();v=read(HERE/'VALIDATION.json')
 if v['fights']!=400 or len(v['records'])!=400 or v['tuning_sha256']!=sha(HERE/'TUNING.json') or v['declaration_sha256']!=sha(HERE/'DECLARATION.json'):raise RuntimeError('validation seal mismatch')
 per=[]
 for tag,h in v['records'].items():
  if sha(RAW/(tag+'_COMPLETE.json'))!=h:raise RuntimeError('validation record drift')
  r=verified(tag);per.append(dict(tag=tag,**r['meta'],**measure(r['summaries'][0]),telemetry=telemetry(r)))
 expected={(a,h,c,o) for a in ARMS for h in HEADS for c in range(20) for o in (0,1)}
 if {(r['arm'],r['head'],r['cluster'],r['orientation']) for r in per}!=expected or len(per)!=400:raise RuntimeError('validation cells')
 cells=[]
 for a in ARMS:
  for h in HEADS:
   rows=[r for r in per if (r['arm'],r['head'])==(a,h)]
   cells.append(dict(arm=a,head=h,wins=sum(r['win'] for r in rows),mean_S=statistics.mean(r['S'] for r in rows),own_losses=statistics.mean(r['losses'] for r in rows),failures=0,fights=40,timeouts=sum(r['timeout'] for r in rows),mean_termination_time=statistics.mean(r['termination_time'] for r in rows),gun_survival=[dict(t=tm,mean_alive=statistics.mean(next(x['alive'] for x in r['telemetry']['gun_survival'] if x['t']==tm) for r in rows)) for tm in (10,20,30,45,60)]))
 paired=[]
 for h in HEADS:
  for c in range(20):
   groups={a:sorted((r for r in per if (r['arm'],r['head'],r['cluster'])==(a,h,c)),key=lambda r:r['orientation']) for a in ARMS}
   paired.append(dict(head=h,cluster=c,wins={a:sum(r['win'] for r in rs) for a,rs in groups.items()},orientation_wins={a:[r['win'] for r in rs] for a,rs in groups.items()},mean_S={a:statistics.mean(r['S'] for r in rs) for a,rs in groups.items()}))
 by={(r['arm'],r['head']):r for r in cells};differences=[(r['wins']['v7']-r['wins']['forcedP16'])/2 for r in paired if r['head']=='regular']
 discord=collections.Counter()
 for r in paired:
  if r['head']=='regular':
   for a,b in zip(r['orientation_wins']['v7'],r['orientation_wins']['forcedP16']):discord[f'v7_{a}__forcedP16_{b}']+=1
 result=dict(status='ANALYZED_DEVELOPMENT_ONLY',validation_sha256=sha(HERE/'VALIDATION.json'),tuning_sha256=sha(HERE/'TUNING.json'),cells=cells,paired_clusters=paired,per_fight=per,readings=readings(by['v7','regular'],by['v7','novice'],by['forcedP16','regular']),positive_clusters=sum(d>0 for d in differences),negative_clusters=sum(d<0 for d in differences),tied_clusters=sum(d==0 for d in differences),orientation_discordance=dict(discord),paired_cluster_bootstrap=bootstrap(differences),omega0_duplicate=v['omega0_duplicate'],omega0_interpretation='Observed total effect of inherited ranged/artillery natural rate zero; gate transitions and firing target/geometry diagnostics accompany counts. No isolated gate timing inference.',not_run={'S5':'not authorized','judging':'not authorized','population_inference':'descriptive development only'})
 write(HERE/'ANALYSIS.json',result);print(json.dumps(result['readings']))
def analyze_tuning():
 t=tuning_receipt()
 candidates=[read(HERE/f'CANDIDATE_{i:03d}.json') for i in range(257)]
 report=dict(status=t['status'],tuning_sha256=sha(HERE/'TUNING.json'),evaluations=257,fights=8224,validation_used=False,selected=t['selected'],selected_params=t['selected_params'],candidate_metrics=[dict(ordinal=r['ordinal'],selection=r['selection']) for r in candidates],ranked_ordinals=[r['ordinal'] for r in sorted(candidates,key=lambda r:rank(r['selection']))],development_only=True)
 write(HERE/'TUNING_ANALYSIS.json',report)
 return report

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('stage',nargs='?',default='validate',choices=('tune','validate'));args=parser.parse_args()
 with attempt('analyze_'+args.stage,dict(status='not_run',reason='stored analysis; no fights')) as (deadline,_,__):
  analyze_tuning() if args.stage=='tune' else analyze();deadline.remaining()
