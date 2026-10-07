"""Hash-first stored-trace arithmetic only; stdlib, no native/project imports or simulation.
Run python3 this_file.py. Writes new diagnostic outputs only; detailed raw stays local.
Parallel paths means internally vertex-disjoint directed effective-root-to-O paths,
with distinct roots and shared O. This is a capacity/resilience metric, not all walks.
"""
from collections import Counter, defaultdict, deque
from pathlib import Path
import gzip, hashlib, json, math, statistics

OUT=Path(__file__).resolve().parent
HEAD='cbe2da2b326ab9f495598ccffc1d6a1630352da2'
REQUEST="Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps."
SITES=[(4*math.cos(i*math.pi/4),4*math.sin(i*math.pi/4)) for i in range(8)]
# Declared before the count: degree-eight strong radius at scale32, K1, rate .5.
RADIUS=math.sqrt(math.log(32/(8*.5)))
THRESHOLD=.1*RADIUS

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def read(p): return json.loads(p.read_text())
def decode(p):
 with gzip.open(p,'rt') as f:return json.load(f)
def trace(p):
 with gzip.open(p,'rt') as f:return [json.loads(l) for l in f]
def reach(starts,edges,skip=None):
 seen=set(starts)-{skip};todo=list(seen)
 while todo:
  for v in edges.get(todo.pop(),()):
   if v!=skip and v not in seen:seen.add(v);todo.append(v)
 return seen

def graph(f,outputs):
 pos={int(k):v for k,v in f['positions'].items()};o=set(pos)&outputs
 roots={s:{i for i in pos if i not in o and math.dist(pos[i],xy)<3} for s,xy in enumerate(SITES)}
 edges={i:set() for i in pos};inc={i:set() for i in pos}
 for a,b in f['strong_edges']:edges[a].add(b);inc[b].add(a)
 forward={s:reach(r,edges) for s,r in roots.items()};back=reach(o,inc)
 served={s for s,r in forward.items() if r&o};on=set().union(*forward.values())&back
 deficits={s:min((math.dist(pos[a],pos[b]) for a in v for b in back),default=None) for s,v in forward.items()}
 critical={i for i in pos if i not in o and any(not(reach(roots[s],edges,i)&o) for s in served)}
 return dict(pos=pos,outputs=o,roots=roots,edges=edges,served=served,forward=forward,on=on,deficits=deficits,critical=critical)

def rebuild(pos):
 ids=sorted(pos);edges=[]
 for b in ids:
  near=sorted((math.dist(pos[a],pos[b]),a) for a in ids if a!=b)[:8]
  held=[(d,a) for d,a in near if d<3]
  for d,a in held:
   if 32*math.exp(-d*d)/max(1,len(held))>=.5:edges.append([a,b])
 return dict(positions=pos,strong_edges=edges)

def eligible_front(g,site,t,births):
 front=g['forward'][site]-g['on'];allroots=set().union(*g['roots'].values())
 tip=min(front,key=lambda i:(min(math.dist(g['pos'][i],g['pos'][o]) for o in g['outputs']),i)) if front and g['outputs'] else None
 candidates={i for i in front if i not in allroots and i!=tip and i not in g['outputs'] and t-births[i]>=20-1e-9}
 return dict(front_count=len(front),root_excluded=len(front&allroots),nonroot_count=len(front-allroots),eligible=sorted(candidates),tip=tip)

def self_check():
 # Independent synthetic counterexamples: shared bottleneck, cycles, two channels.
 for edge,expected in [([(1,3),(2,3),(3,0)],1), ([(1,0),(2,0)],2), ([(1,2),(2,1),(2,0)],1)]:
  g=dict(pos={i:[] for i in {0,1,2,3}},outputs={0},roots={0:{1,2}},edges=defaultdict(set))
  for a,b in edge:g['edges'][a].add(b)
  assert paths(g,0)==expected
 assert clock_reason(1.,1.+1e-10,False)=='finite_stall_add20'
 assert clock_reason(1.,1.+1e-8,False)=='progress_reset'
 assert clock_reason(None,1.,False)=='no_roots_or_no_output_hold'
 assert clock_reason(1.,None,False)=='roots_newly_gained_reset'
 assert clock_reason(0.,1.,True)=='served_reset'

def paths(g,site):
 """Integral unit vertex-capacity max flow, distinct roots, shared output sink."""
 cap=defaultdict(dict);adj=defaultdict(set);source=('S',);sink=('T',)
 def add(a,b,c):
  cap[a][b]=cap[a].get(b,0)+c;cap[b].setdefault(a,0);adj[a].add(b);adj[b].add(a)
 for i in g['pos']:add((i,0),(i,1),10000 if i in g['outputs'] else 1)
 for a,bs in g['edges'].items():
  for b in bs:add((a,1),(b,0),10000)
 for r in g['roots'][site]:add(source,(r,0),1)
 for o in g['outputs']:add((o,1),sink,10000)
 total=0
 while True:
  prev={source:None};todo=deque([source])
  while todo and sink not in prev:
   u=todo.popleft()
   for v in adj[u]:
    if v not in prev and cap[u].get(v,0)>0:prev[v]=u;todo.append(v)
  if sink not in prev:return total
  v=sink
  while prev[v] is not None:
   u=prev[v];cap[u][v]-=1;cap[v][u]+=1;v=u
  total+=1

def basic_summary(d):
 st=d['steps'];late=[s for s in st if s['t']>640];cur=best=0;span=None;first=None
 for s in st:
  if s['paths']:
   if not cur:first=s['t']
   cur+=1
   if cur>best:best=cur;span=[first,s['t']]
  else:cur=0
 return dict(start=d['start'],tag=d['tag'],steps=len(st),last_t=st[-1]['t'],late_connectivity=round(sum(len(set(s['paths'])&set(s['active']))/max(1,len(s['active'])) for s in late)/len(late),3),present=sum(bool(s['paths']) for s in st),longest_any_site=[span,best],final_n=st[-1]['n'],O=st[-1]['O'],births={k:sum(e['rule']==k for e in d['events']) for k in ('B-out','B-path','B1')},final_dO=st[-1]['dO'],keyset=d['keyset'],assay=d['assay'])

def stats(v):
 return dict(n=len(v),min=min(v),median=statistics.median(v),max=max(v),mean=statistics.mean(v)) if v else dict(n=0)

def clock_reason(now,prev,served,threshold=1e-9):
 if served:return 'served_reset'
 if now is None:return 'no_roots_or_no_output_hold'
 if prev is None:return 'roots_newly_gained_reset'
 if (now<prev-1e-9 if threshold==1e-9 else prev-now>=threshold):return 'progress_reset'
 return 'finite_stall_add20'

def summarize_paths(series):
 out={}
 for s in range(8):
  vals=[x['paths'][str(s)] for x in series if x['paths'][str(s)]>0]
  out[str(s)]=dict(served_samples=len(vals),parallel_paths_conditional=stats(vals),one_path_samples=sum(v==1 for v in vals),at_least_two_path_samples=sum(v>=2 for v in vals))
 return out

def main():
 self_check()
 receipts={n:read(OUT/n) for n in ('ECONOMY_RUN_SUMMARIES.json','SERVICE_RUN_SUMMARIES.json')}
 inv={}
 for d in receipts.values():
  for r in d['raw_inventory']:
   p=OUT/r['path'];assert not p.is_symlink() and p.resolve().is_relative_to((OUT/'_local').resolve())
   assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],str(p)
   if r['path'] in inv:assert inv[r['path']]['sha256']==r['sha256']
   inv[r['path']]=r
 print('Raw identity PASS:',len(inv),'files',flush=True)
 rows={};details={};legacy_steps={};figs={};clock=[];comparisons=[]
 for receipt in receipts.values():
  for row in receipt['runs']:
   if row['observer']!='on' or row['variant'] not in ('RD3','ECOF','ECOR'):continue
   name=f"{row['variant']}_{row['start']}_k{row['keyset']}_on";folder=OUT/'_local'/('economy' if row['variant']!='RD3' else '')
   d=decode(folder/(name+'.legacy.json.gz'));tr=trace(folder/(name+'.jsonl.gz'))
   assert basic_summary(d)==row['summary'],name
   world=[x for x in tr if x['kind']=='world_step'];fs=[x for x in tr if x['kind']=='figure'];growth=[x for x in tr if x['kind']=='growth_check']
   assert [x['step'] for x in world]==list(range(1,8001));assert [x['t'] for x in fs]==list(range(5,801,5));assert [x['t'] for x in growth]==list(range(20,801,20))
   for s in range(8):
    a=sum(s in x['active'] for x in world);v=sum(s in x['active_served'] for x in world)
    assert a==row['telemetry']['sites'][str(s)]['active_steps'] and v==row['telemetry']['sites'][str(s)]['active_served_steps']
   outputs={6} if row['start']=='ii' else set();outputs.update(e['ids'][0] for e in d['events'] if e['rule']=='B-out')
   births={i:0. for i in range(7)} if row['start']=='ii' else {}
   births.update({e['ids'][0]:e['time'] for e in d['events'] if e['rule'] in ('B1','B-path','B-out')})
   series=[];graphs={}
   wm={x['t']:x for x in world}
   for f in fs:
    g=graph(f,outputs);assert sorted(g['served'])==wm[f['t']]['served'],(name,f['t'])
    counts={str(s):paths(g,s) for s in range(8)};assert {int(s) for s,v in counts.items() if v}==g['served']
    redundant=len(g['on']-g['outputs']-g['critical'])
    series.append(dict(t=f['t'],paths=counts,critical=len(g['critical']),redundant=redundant,served=sorted(g['served'])))
    if f['t']%20==0:graphs[f['t']]=g
   if row['variant']=='ECOF':
    samples=[x for x in tr if x['kind']=='economy_event' and x['rule']=='economy_stall'];assert len(samples)==320
    assert samples==[dict(kind='economy_event',**s) for s in row['telemetry']['stall_samples']]
    no_front=[x for x in tr if x['kind']=='economy_event' and x['rule']=='D5f_none'];assert len(no_front)==len(row['telemetry']['no_front'])
    state={s:0. for s in range(8)};prev={s:None for s in range(8)};cf={s:0. for s in range(8)};records=[];opportunities=[];availability=[]
    for t in range(20,801,20):
     # Original D5 stage precedes this check's update; actual no-donor reset.
     for site in range(8):
      if state[site]>=60:
       event=next(x for x in no_front if x['site']==site and x['t']==t)
       assert event['reason']=='no_eligible_front';state[site]=0.
     for s in range(8):
      g=graphs[t];now=g['deficits'][s];sample=next(x for x in samples if x['site']==s and x['t']==t)
      assert (now is None)==(sample['deficit'] is None)
      if now is not None:assert math.isclose(now,sample['deficit'],rel_tol=1e-12,abs_tol=1e-12)
      assert sample['previous_deficit']==prev[s];assert sample['served']==(s in g['served'])
      reason=clock_reason(now,prev[s],s in g['served']);before=state[s]
      if reason.endswith('_reset'):state[s]=0.
      elif reason=='finite_stall_add20':state[s]+=20
      assert state[s]==sample['stall_seconds']
      delta=None if now is None or prev[s] is None else prev[s]-now
      # Exactly count rule invocations on fixed deficits, no deletions/dynamics.
      if cf[s]>=60:
       # These are original-stage invocation counts, not dynamic replays.
       # Birth insertion leaves survivor positions unchanged. D3 removes positions
       # absent from post figures, so only no-D3 checks can be inverted exactly.
       snapshot=eligible_front(g,s,t,births)
       removed=[e for e in d['events'] if e['time']==t and e['rule']=='D3']
       born={e['ids'][0] for e in d['events'] if e['time']==t and e['rule'] in ('B1','B-path','B-out')}
       prepos={i:v for i,v in g['pos'].items() if i not in born}
       pre=graph(rebuild(prepos),outputs) if not removed else None
       pre_available=eligible_front(pre,s,t,births) if pre is not None else None
       opportunities.append(dict(t=t,site=s,clock_before=cf[s],postcheck_donors=snapshot,original_stage_donors=pre_available,original_stage_status='RECONSTRUCTED_NO_D3' if pre is not None else 'UNRECORDED_D3_POSITIONS',D3_removed_ids=[i for e in removed for i in e['ids']]));cf[s]=0.
      cr=clock_reason(now,prev[s],s in g['served'],THRESHOLD)
      if cr.endswith('_reset'):cf[s]=0.
      elif cr=='finite_stall_add20':cf[s]+=20
      records.append(dict(t=t,site=s,d=now,previous_d=prev[s],decrease=delta,rule=reason,clock_before=before,clock_after=state[s],corrected_rule=cr,corrected_clock_after=cf[s]))
      prev[s]=now
    assert not row['telemetry']['economy_removals']
    for t,g in graphs.items():
     for site in range(8):availability.append(dict(t=t,site=site,**eligible_front(g,site,t,births)))
    compact_sites=[]
    for s in range(8):
     ss=[r for r in records if r['site']==s];small=[r['decrease'] for r in ss if r['rule']=='progress_reset']
     compact_sites.append(dict(site=s,d=[r['d'] for r in ss],decreases=[r['decrease'] for r in ss],rules=[r['rule'] for r in ss],clocks=[r['clock_after'] for r in ss],rule_counts=dict(Counter(r['rule'] for r in ss)),progress_decreases=stats(small),progress_below_declared_threshold=sum(x<THRESHOLD for x in small),maximum_clock=max(r['clock_after'] for r in ss),no_donor_resets=[x['t'] for x in no_front if x['site']==s]))
    clock.append(dict(start=row['start'],keyset=row['keyset'],checks=list(range(20,801,20)),sites=compact_sites,no_donor_resets=len(no_front),all_growth_end_donor_availability=availability,counterfactual_clock_invocations=len(opportunities),counterfactual_by_site=dict(Counter(x['site'] for x in opportunities)),counterfactual_times=opportunities))
    details[name]=dict(clock=records,no_front=no_front)
   events=[e for e in d['events'] if e['rule']=='episode_end']
   assert len(events)==50
   details.setdefault(name,{})['episode_scores']=[dict(t=e['time'],score=e['values']['score']) for e in events]
   rows[name]=dict(start=row['start'],keyset=row['keyset'],variant=row['variant'],assay=d['assay'],series_5s=series,paths=summarize_paths(series),removals=row['telemetry'].get('economy_removals',[]),prospective_trials=row['telemetry'].get('prospective_trials',[]))
   legacy_steps[name]=d['steps'];figs[name]=fs
   print('Analyzed',name,flush=True)
 assert len(rows)==28
 assert sum(c['no_donor_resets'] for c in clock)==71
 assert sum(s['clocks'].count(60.) for c in clock for s in c['sites'])==76
 assert sum(s['clocks'][-1]>=60 for c in clock for s in c['sites'])==5
 assert sum(len(s['d']) for c in clock for s in c['sites'])==3200
 assert all(a['nonroot_count']==0 and not a['eligible'] for c in clock for a in c['all_growth_end_donor_availability'])
 for c in clock:
  name=f"ECOF_{c['start']}_k{c['keyset']}_on";rd=name.replace('ECOF','RD3')
  assert legacy_steps[name]==legacy_steps[rd] and figs[name]==figs[rd]
  assert rows[name]['assay']==rows[rd]['assay']
 for name,r in rows.items():
  if r['variant']!='ECOR':continue
  rd=name.replace('ECOR','RD3');control=rows[rd]
  windows=[]
  ss={x['t']:x for x in r['series_5s']};rs={x['t']:x for x in control['series_5s']}
  for removal in r['removals']:
   assert removal['rule']=='D5r'
   trial=next(x for x in r['prospective_trials'] if x['t']==removal['t'] and x['ids']==[removal['id']])
   assert trial['passed'] and not trial['lost_sites'] and set(trial['served_before'])<=set(trial['served_after'])
   windows.append(dict(removal=removal,instant_service=trial,sampled_before=ss[removal['t']-5],sampled_after=ss[removal['t']],sampled_next=ss.get(removal['t']+5),RD3_same_times=[rs[t] for t in (removal['t']-5,removal['t'],removal['t']+5) if t in rs]))
  first=min((w['removal']['t'] for w in windows),default=801)
  assert [f for f in figs[name] if f['t']<first]==[f for f in figs[rd] if f['t']<first]
  assert [x for x in legacy_steps[name] if x['t']<first]==[x for x in legacy_steps[rd] if x['t']<first]
  periods={}
  for label,predicate in [('before_first',lambda x:x['t']<first),('after_first',lambda x:x['t']>=first),('late',lambda x:x['t']>640)]:
   eco=[x for x in r['series_5s'] if predicate(x)];rdseries=[x for x in control['series_5s'] if predicate(x)]
   periods[label]=dict(samples=len(eco),ECOR=summarize_paths(eco),RD3=summarize_paths(rdseries),mean_redundant_ECOR=statistics.mean(x['redundant'] for x in eco) if eco else None,mean_redundant_RD3=statistics.mean(x['redundant'] for x in rdseries) if rdseries else None)
  comparisons.append(dict(periods=periods,start=r['start'],keyset=r['keyset'],removals=len(windows),first_removal=min((w['removal']['t'] for w in windows),default=None),assay_ECOR=r['assay'],assay_RD3=control['assay'],gate_ECOR=r['assay']['A']>=.3 and r['assay']['B']>=.3 and max(r['assay']['E'])>=.5,gate_RD3=control['assay']['A']>=.3 and control['assay']['B']>=.3 and max(control['assay']['E'])>=.5,ABE_delta=dict(A=r['assay']['A']-control['assay']['A'],B=r['assay']['B']-control['assay']['B'],maxE=max(r['assay']['E'])-max(control['assay']['E'])),paths_ECOR=r['paths'],paths_RD3=control['paths'],removal_windows=windows))
 assert sum(r['removals'] for r in comparisons)==53
 # Save detailed derived arithmetic locally; small complete paths/clock series in compact JSON.
 local=OUT/'_local/economy/diagnostic_codex';local.mkdir(exist_ok=True)
 raw=local/'DETAILS.json';raw.write_text(json.dumps(details,separators=(',',':'),allow_nan=False)+'\n')
 known=[x for c in clock for x in c['counterfactual_times'] if x['original_stage_donors'] is not None]
 unknown=[x for c in clock for x in c['counterfactual_times'] if x['original_stage_donors'] is None]
 assert len(known)==287 and len(unknown)==35 and all(not x['original_stage_donors']['eligible'] for x in known)
 data=dict(geometry_assumptions='Ordinary gains start positive and remain positive under convex .005 updates toward nonnegative PLV; reward mode is off; live bodies unsilenced. Native append/increasing IDs and order-preserving erase make sorted ID ties match array order. Post-growth geometry, rootedness and served sets crosschecked. Inverse birth reconstruction uses unchanged survivor coordinates; D3 erased coordinates never inferred.',status='PARTIAL' ,reviewed_commit=HEAD,mode='STORED_DATA_ONLY',owner_recheck_request=REQUEST,source_hashes={n:sha(OUT/n) for n in ('analyze_economy_codex.py','ECONOMY_PILOT_SPEC.md','ECONOMY_PILOT_REPORT.md','ECONOMY_COMPACT_SUMMARIES.json','ECONOMY_RUN_SUMMARIES.json','SERVICE_RUN_SUMMARIES.json','economy_kernel.py','economy_telemetry.py','service_graph.py','pilot_common_scratch.py','kernel_builder/RD3_BUILD.json','kernel_builder/ECOF_BUILD.json','kernel_builder/ECOR_BUILD.json','kernel_builder/_worktrees/RD3/evidence/tactical_composition_demo/growing_shapes/medium/rev7_design.py','kernel_builder/_worktrees/RD3/evidence/tactical_composition_demo/growing_shapes/medium/rev7_medium.cpp','kernel_builder/_worktrees/RD3/evidence/tactical_composition_demo/growing_shapes/runner/rev7_run.py','kernel_builder/_worktrees/RD3/evidence/tactical_composition_demo/growing_shapes/medium/design_0h.py')},raw_inventory_verified=list(inv.values()),derived_local=dict(path=str(raw.relative_to(OUT)),bytes=raw.stat().st_size,sha256=sha(raw)),identity='All 10 ECOF/RD3 pairs: 8000 legacy world records, 160 unrounded position/strong/spring figures, and final aggregate assay identical. Full native phase/RNG state not stored for cross-arm comparison; different digest schemas.',front_clock=clock,corrected_rule=dict(progress_fraction=.1,degree8_strong_radius=RADIUS,threshold_coordinate_units=THRESHOLD,change='Only replace decrease>1e-9 progress with decrease>=0.1*sqrt(log(32/(8*.5))) per growth check; keep served/new-finite reset, infinite hold, +20 stalled, 60s trigger, original donor/exclusions/order.',counterfactual_clock_invocations=sum(c['counterfactual_clock_invocations'] for c in clock),counterfactual_actual_removals='NOT_IDENTIFIABLE: pre-D5 after-D1/D4 graph, measured locks and sequential donor changes absent. Clock invocations are not removals; no roots/output/donor can veto. Fixed original trajectories do not change after counterfactual triggers.',not_a_forecast=True,terminal_clock_censored='Clock due after t800 cannot trigger within recorded horizon; omitted.'),counterfactual_donor_accounting=dict(original_stage_fixed_trace_removal_lower_bound=0,original_stage_fixed_trace_removal_upper_bound=len(unknown),end_snapshot_removals=0,original_stage_reconstructible=sum(x['original_stage_donors'] is not None for c in clock for x in c['counterfactual_times']),original_stage_reconstructible_nonempty=sum(bool(x['original_stage_donors']['eligible']) for c in clock for x in c['counterfactual_times'] if x['original_stage_donors'] is not None),original_stage_unknown=sum(x['original_stage_donors'] is None for c in clock for x in c['counterfactual_times'])),ECOR=comparisons,paths_semantics='Maximum number of internally vertex-disjoint directed strong paths, distinct ordinary roots, common O. Integer unit vertex capacities; O unconstrained. Includes idle sites, strict roots radius3. Not all simple paths (cycles), not independent phase channels.',sampling='Figures post-growth every5s. t-5 to t includes motion,D1/D4/D3,births and D5r; cannot isolate deletion effect. Prospective trials establish instant served-set preservation only. A/B/E are retained aggregate assays across checkpoints, not live/time-resolved responses.',limitations=['No output phase or phase coherence recorded.','No F5 own/donor/lesion decision streams: aggregate A/B/E crosschecked, cannot independently recompute means.','No pre/post-removal exact geometry or locks: cannot identify exact immediate parallel-path change or original-stage counterfactual deletion count.','ECOR ii/key3 and ii/key4 not launched; no full-arm regression reading.'],recheck='Separate pass tracked in docs/reviews/tactical_0h_economy_diagnostic_recheck.md; no PLAN_CURRENT pin/edit.')
 (OUT/'ECONOMY_DIAGNOSTIC.json').write_text(json.dumps(data,separators=(',',':'),allow_nan=False)+'\n')
 attach_audit(data)
 (OUT/'ECONOMY_DIAGNOSTIC.json').write_text(json.dumps(data,separators=(',',':'),allow_nan=False)+'\n')
 render(data)
 print('Diagnostic written; counterfactual clock invocations',data['corrected_rule']['counterfactual_clock_invocations'],flush=True)

def attach_audit(d):
 d['counterfactual_count_convention']='Each invocation is assessed independently on unchanged stored geometry, with no hypothetical deletion carried across sites or checks. The0–35 interval is an independent-snapshot eligibility bound, not a sequential ECOF-policy deletion count or a dynamic forecast.'
 d['source_hashes']['analyze_economy_codex.py']=sha(OUT/'analyze_economy_codex.py')
 d['source_hashes']['recheck_economy_stored_codex.py']=sha(OUT/'recheck_economy_stored_codex.py')
 audit=OUT/'_local/economy/diagnostic_codex/PILOT_AUDIT.json'
 if audit.exists():
  a=read(audit);assert a['status']=='PASS';assert a['script_sha256']==sha(OUT/'recheck_economy_stored_codex.py')
  for n,h in a['source_sha256'].items():assert sha(OUT/n)==h,n
  d['pilot_audit']=dict(status=a['status'],local_path=str(audit.relative_to(OUT)),bytes=audit.stat().st_size,sha256=sha(audit),hash_first=a['hash_first'],completed_slots=len(a['completed_slots']),report_data_rows_verified=a['report_data_rows_verified'],front_clock_totals=a['front_clock_totals'],elapsed_seconds=a['elapsed_seconds'])
 else:d['pilot_audit']=dict(status='NOT_RUN',command='python3 '+str(OUT/'recheck_economy_stored_codex.py'))

def render(d):
 lines=['PARTIAL','','Stored-only economy diagnostic against `'+HEAD+'`; no pilot, medium, native or assay replay. All '+str(len(d['raw_inventory_verified']))+' retained raw inventory sizes/SHA256 verified before decoding. No plan/design/receipt changed or pinned.','',
 'ECO-F has zero D5f removals but71 D5f_none invocations, all no_eligible_front. The clock reaches60s76 times, including5 terminal checks with no following donor stage. At all3200 site/growth-end snapshots, every front body is protected as a root of some site; the tip/age exclusions cannot create an eligible donor. All ten pairs match RD3 in all8000 legacy world records, all160 unrounded position/strong-edge/spring figures, and aggregate assays. The different state digests include different fields (ECOF includes clock histories), so this is recorded trajectory equality, not a cross-arm phase/RNG proof.','',
 'Clock reasons below exhaust all3200 end-of-check site updates. Served resets dominate served sites; first finite deficit resets newly gained roots; any decrease>1e-9 resets progress; otherwise finite deficit adds20s, infinity holds. Infinity combines no roots/no O in the kernel; all checks have O, and reconstructed roots disambiguate it as no roots here. JSON gives each run/site full40-point d_s(k), decreases, rule and clock series, and no_donor_resets between end updates; local DETAILS.json also gives before/after values. Deficits are coordinate distances, clocks seconds.','',
 '| Run/site | served | progress | gained roots | stalled +20 | no roots hold | Max clock s | progress decrease min / median / max | below corrected threshold |','|---|---:|---:|---:|---:|---:|---:|---|---:|']
 for r in d['front_clock']:
  for s in r['sites']:
   c=s['rule_counts'];v=s['progress_decreases'];vtxt='none' if not v['n'] else f"{v['min']:.9g} / {v['median']:.9g} / {v['max']:.9g}"
   lines.append(f"| {r['start']}/k{r['keyset']}/{s['site']} | {c.get('served_reset',0)} | {c.get('progress_reset',0)} | {c.get('roots_newly_gained_reset',0)} | {c.get('finite_stall_add20',0)} | {c.get('no_roots_or_no_output_hold',0)} | {s['maximum_clock']:g} | {vtxt} | {s['progress_below_declared_threshold']} |")
 progress=[x for r in d['front_clock'] for s in r['sites'] for x,reason in zip(s['decreases'],s['rules']) if reason=='progress_reset']
 lines+=['',f"Unserved progress resets: {len(progress)}; smallest decrease {min(progress):.12g}, median {statistics.median(progress):.12g}. {sum(x<THRESHOLD for x in progress)} are smaller than the prospectively declared diagnostic threshold {THRESHOLD:.12g}. Original clock DOES reach60s76 times, and71 following stages reset because no eligible donor exists. Thus progress sensitivity is only one issue; protecting every site's effective roots plus each tip and the age condition can exclude all donors. A clock-only change has no demonstrated benefit unless it finds donors. JSON includes all71 intervening no-donor resets; do not confuse the ECO-R prospective-check zero with front-clock activity.",'',
 f"One proposed single change: progress requires d_s(k−1)−d_s(k) >=0.1*r8 = {THRESHOLD:.12g} coordinate units per20s, where r8=sqrt(log(32/(8*.5)))={RADIUS:.12g} is the guaranteed degree-eight strong-link radius for scale32,K1. Same constant for all sites/starts, declared before counting, no threshold sweep or site tuning. Keep every other Amendment1 condition. This is a hypothesis for owner/drafter consideration; no implementation or execution authorization.",'',
 f"On the immutable RD3/ECOF deficit sequences this would invoke the original-stage60s D5f clock {d['corrected_rule']['counterfactual_clock_invocations']} times within t<=800. These are counterfactual checks, not a certified number of removals. Every donor assessment uses each invocation independently on unchanged stored geometry; no hypothetical deletion is carried between sites or checks. All3200 site/growth-end donor assessments have zero non-root front candidates: a post-check fixed-trajectory count is exactly0 removals under this clock-only change. Original-stage graph is reconstructed by undoing births when no D3 removed positions; D3 checks are marked unrecorded. Exact original-stage donors require missing positions at those checks and lock ranks; multiple sites share donors, exclusions and no-donor resets apply. Do not substitute this count for removal count or predicted coverage. Terminal due clocks after800 are censored. Original-stage donor reconstruction proves zero eligible donors at287 of322 invocations. The remaining35 coincide with D3 erasures, whose prior coordinates were not saved. Thus independent-snapshot original-stage eligible-deletion opportunities are bounded0–35, with exact sampled post-check count0. A single exact original-stage removal count is NOT_IDENTIFIABLE without extra assumptions; that part of the owner request remains PARTIAL. This interval is not a sequential ECOF-policy count: within-check deletion could rewire a later site's candidates, and later trajectory evolution would differ. No simulated deletion is performed.",'',
 '| Run | counterfactual clock invocations | per-site counts |','|---|---:|---|']
 for c in d['front_clock']:lines.append(f"| {c['start']}/k{c['keyset']} | {c['counterfactual_clock_invocations']} | {c['counterfactual_by_site']} |")
 lines+=['','ECO-R:53 D5r removals in8 completed runs; all53 prospective trials pass, with zero lost currently served sites (idle included). Every completed gate shape fails:0/8. Matched RD3 passes7/8; its missing comparison runs are excluded. Reserve56 never promised restored headroom. No complete-arm REGRESSION reading is allowed because two seeded runs are absent.','',
 'A measures average wrapped decision-angle difference between own and donor; B between own and output-channel lesion. E is own-assay per-site strong-path exposure. Each is averaged over retained checkpoint assays, not a response measured immediately after a removal. Individual assay decisions/checkpoint means and output phase are not stored, so neither numerical re-derivation of A/B/E nor time-resolved coherence can be supplied. Aggregate values match the raw legacy aggregates; episode scores retained locally are task rewards and are not coherence proxies.','',
 '| Run | removals / first t | A RD3 → ECO-R | B RD3 → ECO-R | maxE RD3 → ECO-R | full ECO-R E |','|---|---|---|---|---|---|']
 for r in d['ECOR']:
  a=r['assay_RD3'];b=r['assay_ECOR'];lines.append(f"| {r['start']}/k{r['keyset']} | {r['removals']} / {r['first_removal']} | {a['A']:.6g} → {b['A']:.6g} | {a['B']:.6g} → {b['B']:.6g} | {max(a['E']):.6g} → {max(b['E']):.6g} | {b['E']} |")
 lines+=['','Parallel strong paths are defined as maximum internally vertex-disjoint directed paths from distinct effective roots to shared O, not arbitrary shortest routes or all walks through cycles. Unit ordinary vertex capacities, unbounded O; idle sites included. Full160-point per-site count/class series, paired before-first/after-first/late summaries and all53 deletion windows (t−5,t,t+5 and matched RD3) are in compact JSON. These quantify sampled resilience after deletion context; motion and other growth events share each window, so the window does not identify D5r causality.','',
 '| Run/site | RD3 served samples / mean parallel / single-path | ECO-R served samples / mean parallel / single-path |','|---|---|---|']
 for r in d['ECOR']:
  for s in range(8):
   cells=[]
   for field in ('paths_RD3','paths_ECOR'):
    p=r[field][str(s)];mean=p['parallel_paths_conditional'].get('mean');cells.append(f"{p['served_samples']} / {mean:.3f} / {p['one_path_samples']}" if mean is not None else '0 / undefined / 0')
   lines.append(f"| {r['start']}/k{r['keyset']}/{s} | "+' | '.join(cells)+' |')
 lines+=['','Recorded figures and legacy fields match RD3 exactly before the first D5r event in all8 pairs. The following paired table measures later structural change, with equal5s snapshot weights. Redundant-body count measures the forward/backward service intersection minus single-deletion critical bodies and O; it is not signal strength. A zero count may result from service absence or a purely critical surviving route.','', '| Run | after-first redundant bodies RD3 / ECO-R | late (>640s) RD3 / ECO-R |','|---|---|---|']
 for r in d['ECOR']:
  a=r['periods']['after_first'];b=r['periods']['late'];lines.append(f"| {r['start']}/k{r['keyset']} | {a['mean_redundant_RD3']:.4f} / {a['mean_redundant_ECOR']:.4f} | {b['mean_redundant_RD3']:.4f} / {b['mean_redundant_ECOR']:.4f} |")
 lines+=['', 'Across the8 matched runs, mean A is '+f"{statistics.mean(r['assay_RD3']['A'] for r in d['ECOR']):.9g} → {statistics.mean(r['assay_ECOR']['A'] for r in d['ECOR']):.9g}"+', mean B '+f"{statistics.mean(r['assay_RD3']['B'] for r in d['ECOR']):.9g} → {statistics.mean(r['assay_ECOR']['B'] for r in d['ECOR']):.9g}"+', and mean per-run maxE '+f"{statistics.mean(max(r['assay_RD3']['E']) for r in d['ECOR']):.9g} → {statistics.mean(max(r['assay_ECOR']['E']) for r in d['ECOR']):.9g}"+'. All8 paired differences are negative for A,B,maxE. Means use matched8, not the full10-run control.', '', 'Geometry reconstruction assumptions: '+d['geometry_assumptions']+' Source hashes pin the retained RD3 native/design/run definitions; figures independently reproduce all-site service and actual ECOF deficit values.']
 lines+=['','ECO-R implies that instant Boolean reachability is insufficient to protect retained response or later service. A geometrically redundant body need not be dynamically redundant: paths can supply resilience and change receiver degree, normalization, coupling and geometry. The data support an association between thinning and degraded response/exposure, not proof that loss of parallel paths or phase cancellation caused it. Inspect the conditional counts alongside service occupancy: a high conditional mean can coexist with near-total service loss; unserved samples are excluded from that mean. There is no recorded phase-coherence mechanism to assert. A future redundancy rule needs a declared dynamic/resilience obligation beyond its immediate served-set veto, but no such combined rule or run is proposed here.','',
 'Part1 disposition is in docs/reviews/tactical_0h_economy_pilot_recheck_codex.md. Separate Part2 owner request:', '', '> '+REQUEST,'',
 'Separate reviewer findings and disposition: docs/reviews/tactical_0h_economy_diagnostic_recheck.md. Claude CLI was unavailable (not logged in); a separate Codex reviewer performed this same-family pass. Tracking lives in these new artifacts under the owner prohibition on PLAN_CURRENT.md edits.','',
 'Reproduce only this arithmetic: `python3 evidence/tactical_composition_demo/growing_shapes_review_claude/rev711_diag/medium_variants/analyze_economy_codex.py`. Standard library only; never imports medium/evaluator/pilot code. Detailed derived records remain _local/economy/diagnostic_codex/DETAILS.json with size/hash in JSON.']
 (OUT/'ECONOMY_DIAGNOSTIC.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
