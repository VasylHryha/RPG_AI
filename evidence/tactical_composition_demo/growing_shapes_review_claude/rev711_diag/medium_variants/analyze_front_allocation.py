"""Pure stored-data arithmetic. Standard library only; no project imports/runs.
Writes only FRONT_ALLOCATION_DIAGNOSTIC.{json,md} and derived _local raw.
Verify all receipt inventories before any gzip decoding. PLAN_CURRENT excluded.
"""
from pathlib import Path
from collections import Counter, defaultdict
import gzip, hashlib, json, math, statistics, subprocess

OUT=Path(__file__).resolve().parent
RAW=OUT/'_local/front_allocation'
SITES=[(4*math.cos(s*math.pi/4),4*math.sin(s*math.pi/4)) for s in range(8)]
REQUEST="Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps."

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def stats(v):
 return dict(n=len(v),min=min(v),median=statistics.median(v),mean=statistics.mean(v),p90=sorted(v)[min(len(v)-1,math.ceil(.9*len(v))-1)],max=max(v)) if v else dict(n=0)
def reach(starts,adj,skip=None):
 seen=set(starts)-{skip};todo=list(seen)
 while todo:
  for v in adj.get(todo.pop(),()):
   if v!=skip and v not in seen:seen.add(v);todo.append(v)
 return seen
def components(ids,adj):
 remaining=set(ids);result=[]
 while remaining:
  found=reach({min(remaining)},{i:set(adj[i])&ids for i in ids})
  result.append(found);remaining-=found
 return result

def allocation(f,outputs,births):
 pos={int(k):v for k,v in f['positions'].items()};o=outputs&pos.keys();ordinary=set(pos)-o
 roots={s:{i for i in ordinary if math.dist(pos[i],xy)<3} for s,xy in enumerate(SITES)}
 out={i:set() for i in pos};inc={i:set() for i in pos};weak={i:set() for i in pos}
 for a,b in f['strong_edges']:out[a].add(b);inc[b].add(a);weak[a].add(b);weak[b].add(a)
 forward={s:reach(r,out) for s,r in roots.items()};back=reach(o,inc)
 union=set().union(*forward.values());served={s for s in range(8) if forward[s]&o}
 front=(union-back)-o;on=(union&back)-o
 critical={i for i in on if any(not(reach(roots[s],out,i)&o) for s in served)}
 redundant=on-critical
 pairs=set()
 for i in sorted(pos):
  near=sorted((math.dist(pos[i],pos[j]),j) for j in pos if j!=i)[:8]
  pairs.update(tuple(sorted((i,j))) for d,j in near if d<3 and i not in o and j not in o)
 cost={i:1. for i in ordinary}
 for a,b in pairs:cost[a]+=.05;cost[b]+=.05
 owned=[0.]*8;owners={};rootn={i:sum(i in roots[s] for s in range(8)) for i in ordinary}
 for i in front:
  owners[i]=[s for s in range(8) if i in forward[s]]
  assert owners[i]
  for s in owners[i]:owned[s]+=cost[i]/len(owners[i])
 fc=sum(cost[i] for i in front);assert math.isclose(sum(owned),fc,abs_tol=1e-8)
 per=[]
 for s in range(8):
  ids=front&forward[s];comps=components(ids,weak)
  cc=[sum(cost[i]/len(owners[i]) for i in c) for c in comps]
  tip=lambda c:min(c,key=lambda i:(min(math.dist(pos[i],pos[j]) for j in o),i)) if c and o else None
  ts=[tip(c) for c in comps]
  per.append(dict(site=s,served=s in served,front_ids=sorted(ids),components=[dict(ids=sorted(c),tip=t,tip_owned_cost=cost[t]/len(owners[t]) if t is not None else 0.,owned_cost=k) for c,t,k in zip(comps,ts,cc)],component_count=len(comps),component_tip_count=sum(t is not None for t in ts),B_path_site_tip=tip(ids),B_path_site_tip_owned_cost=cost[tip(ids)]/len(owners[tip(ids)]) if tip(ids) is not None else 0.,owned_cost=owned[s],outside_largest_component_cost=owned[s]-max(cc,default=0),tip_body_owned_cost=sum(cost[t]/len(owners[t]) for t in ts if t is not None)))
 classes={'front':front,'redundant':redundant,'critical':critical,'orphan':ordinary-union}
 rules={c:{rule:dict(body_samples=sum(births[i]['rule']==rule for i in ids),cost=sum(cost[i] for i in ids if births[i]['rule']==rule)) for rule in ('B1','B-path','B-out','seeded')} for c,ids in classes.items()}
 age=[f['t']-births[i]['t'] for i in front]
 canonical_cost=len(ordinary)+.1*len(pairs)
 assert math.isclose(sum(cost.values()),canonical_cost,abs_tol=1e-8)
 return dict(t=f['t'],cost=canonical_cost,front_cost=fc,redundant_cost=sum(cost[i] for i in redundant),served=sorted(served),sites=per,origin=rules,front_age_seconds=age,front_count=len(front),front_roots=sum(rootn[i]>0 for i in front),front_shared_roots=sum(rootn[i]>=2 for i in front),front_root_membership_histogram=dict(Counter(rootn[i] for i in front)),front_owner_histogram=dict(Counter(len(owners[i]) for i in front)),ordinary_count=len(ordinary),ordinary_inside_one=sum(rootn[i]>=1 for i in ordinary),ordinary_inside_two=sum(rootn[i]>=2 for i in ordinary),all_positions_count=len(pos),all_positions_inside_one=sum(any(math.dist(xy,sp)<3 for sp in SITES) for xy in pos.values()),all_positions_inside_two=sum(sum(math.dist(xy,sp)<3 for sp in SITES)>=2 for xy in pos.values()),outside_nominal_arena=sum(math.hypot(*pos[i])>6 for i in ordinary),front_distance_O=[min(math.dist(pos[i],pos[j]) for j in o) for i in front] if o else [],output_root_zone_distance=[min(math.dist(pos[j],sp) for sp in SITES)-3 for j in o])

def adaptive(f,a,b,tol=1e-10):
 def sim(a,b,fa,fm,fb):return (b-a)*(fa+4*fm+fb)/6
 def step(a,b,fa,fm,fb,old,eps,n):
  m=(a+b)/2;lm=(a+m)/2;rm=(m+b)/2;fl=f(lm);fr=f(rm)
  left=sim(a,m,fa,fl,fm);right=sim(m,b,fm,fr,fb);d=left+right-old
  if n==0 or abs(d)<=15*eps:return left+right+d/15
  return step(a,m,fa,fl,fm,left,eps/2,n-1)+step(m,b,fm,fr,fb,right,eps/2,n-1)
 fa=f(a);fm=f((a+b)/2);fb=f(b)
 return step(a,b,fa,fm,fb,sim(a,b,fa,fm,fb),tol,24)
def arena(tol):
 def angular(r,k):
  if r<=1 or r>=7:return 0.
  delta=math.acos(max(-1.,min(1.,(r*r+7)/(8*r))))
  return max(0.,min(1.,2*delta/(math.pi/4)-(k-1)))
 cuts=sorted({1.,6.,*[4*math.cos(a)+sign*math.sqrt(9-16*math.sin(a)**2) for a in (math.pi/8,math.pi/4) for sign in (-1,1)]})
 cuts=[x for x in cuts if 1<=x<=6]
 return {str(k):sum(adaptive(lambda r:2*r*angular(r,k)/36,a,b,tol) for a,b in zip(cuts,cuts[1:])) for k in (1,2)}

def run(row,inventory):
 arm=row['variant'];name=f"{arm}_{row['start']}_k{row['keyset']}_on"
 folder=OUT/'_local'/('coverage' if arm!='RD3' else '')
 paths=[folder/(name+s) for s in ('.jsonl.gz','.legacy.json.gz')]
 assert all(str(p.relative_to(OUT)) in inventory for p in paths)
 with gzip.open(paths[0],'rt') as f:tr=[json.loads(l) for l in f]
 with gzip.open(paths[1],'rt') as f:legacy=json.load(f)
 world=[x for x in tr if x['kind']=='world_step'];figs=[x for x in tr if x['kind']=='figure']
 assert len(world)==len(legacy['steps'])==8000 and [x['step'] for x in world]==list(range(1,8001))
 assert [x['t'] for x in figs]==list(range(5,801,5))
 births={i:dict(t=0.,rule='seeded',site=None) for i in range(7)} if row['start']=='ii' else {}
 outputs={6} if row['start']=='ii' else set()
 for e in legacy['events']:
  if e['rule'] in ('B1','B-path','B-out'):
   births[e['ids'][0]]=dict(t=e['time'],rule=e['rule'],site=e['values'].get('site'))
   if e['rule']=='B-out':outputs.update(e['ids'])
 series=[allocation(f,outputs,births) for f in figs]
 for s in series:
  assert s['served']==world[int(s['t']*10)-1]['served']
  if s['t']%20==0:
   g=next(x for x in tr if x['kind']=='growth_check' and x['t']==s['t'])
   assert math.isclose(s['cost'],g['cost'],abs_tol=1e-8)
 demand=[0]*8;service=[0]*8;intd=[0]*8;ints=[0]*8;wait=[0.]*8;debtseries=[];checkstate={}
 for w,l in zip(world,legacy['steps']):
  assert w['t']==l['t']
  # At decisions t, observer's t frame is not complete yet. Use exactly t-.1.
  before=[(a-b)/10 for a,b in zip(demand,service)]
  for s in range(8):
   intd[s]+=s in l['active'];ints[s]+=s in l['active'] and s in l['paths']
   if s in (set(w['served']) if w['step']%200 else set(l['paths']) | (set(w['served'])-set(l['active']))):wait[s]=0.
   elif s in l['active']:wait[s]+=.1
  if w['step']%200==0:checkstate[w['t']]=dict(debt_settled_predecision=before,debt_integrate_boundary=[(a-b)/10 for a,b in zip(intd,ints)],waiting_integrate_seconds=list(wait))
  for s in range(8):
   demand[s]+=s in w['active'];service[s]+=s in w['active_served']
  debtseries.append(dict(t=w['t'],active_seconds=[a/10 for a in demand],served_active_seconds=[a/10 for a in service],debt_seconds=[(a-b)/10 for a,b in zip(demand,service)],integrate_active_seconds=[a/10 for a in intd],integrate_served_active_seconds=[a/10 for a in ints],integrate_debt_seconds=[(a-b)/10 for a,b in zip(intd,ints)]))
 for s in range(8):
  assert demand[s]==row['telemetry']['sites'][str(s)]['active_steps']
  assert service[s]==row['telemetry']['sites'][str(s)]['active_served_steps']
 checks=[];quota=[]
 for t,state in checkstate.items():
  cc={e['values']['site']:e['values'] for e in legacy['events'] if e['rule']=='B_path_check' and e['time']==t}
  assert len(cc)==8
  eligible=[s for s,v in cc.items() if v['active'] and v['missing_path_before']]
  p=cc[0]['pointer_before'];finite=lambda s:not cc[s]['infinite_deficit']
  longest=sorted(eligible,key=lambda s:(not finite(s),-state['waiting_integrate_seconds'][s],(s-p)%8))
  debtorder=sorted(eligible,key=lambda s:(-state['debt_integrate_boundary'][s],(s-p)%8))
  settledorder=sorted(eligible,key=lambda s:(-state['debt_settled_predecision'][s],(s-p)%8))
  actual=sorted(eligible,key=lambda s:cc[s]['rank'])
  proxy_longest=list(longest)
  if arm=='COVA':longest=actual
  clock_proxy_matches_recorded=(proxy_longest==actual) if arm=='COVA' else None
  checked=dict(t=t,**state,eligible=eligible,pointer_before=p,actual_order=actual,COVA_key_order=longest,clock_proxy_order=proxy_longest,clock_proxy_matches_recorded=clock_proxy_matches_recorded,debt_order=debtorder,settled_debt_order=settledorder,first_choice_differs=bool(eligible) and longest[0]!=debtorder[0],finite_deficit={s:finite(s) for s in eligible},B_path_checks=cc)
  checks.append(checked)
  terms=[x for x in tr if x['kind']=='event' and x['rule']=='birth_terminal' and x['outcome']=='quota' and x['t']==t]
  for e in terms:
   quota.append(dict(t=t,request=e['request'],site=e['site'],birth_rule=e['birth_rule'],**state,eligible_at_B_path_start=eligible,COVA_key_order=longest,debt_order=debtorder,settled_debt_order=settledorder,refused_site_debt=state['debt_integrate_boundary'][e['site']],maximum_initial_eligible_debt=max((state['debt_integrate_boundary'][s] for s in eligible),default=None)))
 final=debtseries[-1]
 return dict(name=name,variant=arm,start=row['start'],keyset=row['keyset'],series_5s=series,debt_series_01s=debtseries,checks=checks,quota_decisions=quota,final_service=final,final_service_integrate=dict(active_seconds=[a/10 for a in intd],served_active_seconds=[a/10 for a in ints],debt_seconds=[(a-b)/10 for a,b in zip(intd,ints)]),births=births)

def summarize(rr):
 ss=[s for r in rr for s in r['series_5s']];checks=[c for r in rr for c in r['checks']];q=[q for r in rr for q in r['quota_decisions']]
 out=dict(runs=len(rr),snapshots=len(ss),growth_checks=len(checks),front_cost_sum=sum(s['front_cost'] for s in ss),all_cost_sum=sum(s['cost'] for s in ss),front_body_samples=sum(s['front_count'] for s in ss),front_roots=sum(s['front_roots'] for s in ss),front_shared_roots=sum(s['front_shared_roots'] for s in ss),front_ages=stats([a for s in ss for a in s['front_age_seconds']]),front_distance_O=stats([a for s in ss for a in s['front_distance_O']]),sites=[],origin={},quota_counts=dict(Counter(x['birth_rule'] for x in q)))
 for rule in ('B1','B-path','B-out','seeded'):
  out['origin'][rule]={c:dict(body_samples=sum(s['origin'][c][rule]['body_samples'] for s in ss),cost_sum=sum(s['origin'][c][rule]['cost'] for s in ss)) for c in ('front','redundant')}
 for site in range(8):
  row={}
  for label,select in [('all_5s',ss),('growth_end_20s',[s for s in ss if s['t']%20==0]),('late',[s for s in ss if s['t']>640]),('cost_ge63',[s for s in ss if s['cost']>=63])]:
   us=[s['sites'][site] for s in select if site not in s['served']];rooted=[u for u in us if u['component_count']]
   row[label]=dict(selected_snapshots=len(select),unserved_site_checks=len(us),rooted_unserved_site_checks=len(rooted),component_tip_count_sum=sum(u['component_tip_count'] for u in us),site_tip_defined_checks=sum(u['B_path_site_tip'] is not None for u in us),site_tip_owned_cost_sum=sum(u['B_path_site_tip_owned_cost'] for u in us),component_count_histogram=dict(Counter(u['component_count'] for u in us)),components=stats([u['component_count'] for u in us]),multiple_component_checks=sum(u['component_count']>=2 for u in us),owned_front_cost_sum=sum(s['sites'][site]['owned_cost'] for s in select),owned_unserved_front_cost_sum=sum(u['owned_cost'] for u in us),outside_largest_component_cost_sum=sum(u['outside_largest_component_cost'] for u in us),tip_body_owned_cost_sum=sum(u['tip_body_owned_cost'] for u in us))
  row['site']=site
  row['final_active_seconds']=sum(r['final_service']['active_seconds'][site] for r in rr)
  row['final_served_active_seconds']=sum(r['final_service']['served_active_seconds'][site] for r in rr)
  row['final_debt_seconds']=sum(r['final_service']['debt_seconds'][site] for r in rr)
  row['final_integrate_debt_seconds']=sum(r['final_service_integrate']['debt_seconds'][site] for r in rr)
  row['quota_decisions']=sum(x['site']==site for x in q)
  row['quota_refused_debt_seconds']=stats([x['refused_site_debt'] for x in q if x['site']==site])
  out['sites'].append(row)
 relevant=[c for c in checks if c['eligible']];contested=[c for c in relevant if len(c['eligible'])>=2]
 out['scheduler']=dict(debt_sampling_first_choice_changes=sum(bool(c['eligible']) and c['debt_order'][0]!=c['settled_debt_order'][0] for c in checks),clock_proxy_order_mismatches=sum(c['clock_proxy_matches_recorded'] is False for c in checks),eligible_checks=len(relevant),contested_checks=len(contested),first_choice_differs=sum(c['first_choice_differs'] for c in relevant),different_on_quota_checks=sum(c['first_choice_differs'] and any(x['t']==c['t'] for x in r['quota_decisions']) for r in rr for c in r['checks'] if c['eligible']),debt_of_COVA_first=stats([c['debt_integrate_boundary'][c['COVA_key_order'][0]] for c in relevant]),debt_of_debt_first=stats([c['debt_integrate_boundary'][c['debt_order'][0]] for c in relevant]))
 out['B_path_initial_eligible_last_outcomes']=dict(Counter(c['B_path_checks'][site]['last_terminal_outcome'] for c in checks for site in c['eligible']))
 out['geometry']={k:sum(s[k] for s in ss) for k in ('ordinary_count','ordinary_inside_one','ordinary_inside_two','all_positions_count','all_positions_inside_one','all_positions_inside_two','outside_nominal_arena')}
 out['front_old_body_samples_ge60']=sum(a>=60 for s in ss for a in s['front_age_seconds'])
 out['front_old_body_samples_ge120']=sum(a>=120 for s in ss for a in s['front_age_seconds'])
 out['output_root_zone_distance']=stats([v for s in ss for v in s['output_root_zone_distance']])
 return out

def main():
 receipts={n:read(OUT/n) for n in ('SERVICE_RUN_SUMMARIES.json','COVERAGE_RUN_SUMMARIES.json')};inventory={}
 for receipt in receipts.values():
  for r in receipt['raw_inventory']:
   p=OUT/r['path'];assert not p.is_symlink() and p.resolve().is_relative_to((OUT/'_local').resolve())
   assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],str(p)
   if r['path'] in inventory:assert inventory[r['path']]==r
   inventory[r['path']]=r
 for arm in ('RD3','COVA','COVB'):
  build=read(OUT/f'kernel_builder/{arm}_BUILD.json')
  base=OUT/f'kernel_builder/_worktrees/{arm}/evidence/tactical_composition_demo/growing_shapes/medium'
  assert sha(base/'rev7_design.py')==build['design_sha256']
  assert sha(base/'rev7_medium.cpp')==build['build']['source_sha256']['rev7_medium.cpp']
  assert sha(OUT/'service_graph.py')==build['service_graph_sha256']
  if arm!='RD3':assert sha(OUT/'coverage_kernel.py')==build['coverage_kernel_sha256']
 print('Verified raw inventory and interpretation sources BEFORE decoding:',len(inventory),flush=True)
 runs=[]
 for receipt in receipts.values():
  for row in receipt['runs']:
   if row['observer']=='on' and row['variant'] in ('RD3','COVA','COVB'):
    runs.append(run(row,inventory));print('Analyzed',runs[-1]['name'],flush=True)
 assert len(runs)==30 and len({r['name'] for r in runs})==30
 RAW.mkdir(parents=True,exist_ok=True)
 raw=RAW/'DETAILS.json.gz'
 with gzip.GzipFile(filename=str(raw),mode='wb',mtime=0) as f:f.write(json.dumps(runs,separators=(',',':'),allow_nan=False).encode())
 area=arena(1e-10);fine=arena(1e-12);assert max(abs(area[k]-fine[k]) for k in area)<1e-8
 sources=['analyze_front_allocation.py','SERVICE_RUN_SUMMARIES.json','COVERAGE_RUN_SUMMARIES.json','MASS_BUDGET_DIAGNOSTIC.md','ECONOMY_DIAGNOSTIC.md','COVERAGE_PILOT_REPORT.md','coverage_kernel.py','service_graph.py']
 for arm in ('RD3','COVA','COVB'):
  prefix=f'kernel_builder/_worktrees/{arm}/evidence/tactical_composition_demo/growing_shapes/'
  sources += [f'kernel_builder/{arm}_BUILD.json']
  sources += [prefix+'medium/'+n for n in ('rev7_design.py','rev7_medium.cpp','design_0h.py')]
 owner=Path.home()/'Downloads/RRG_0H_FULL_COVERAGE_RESEARCH_UPDATE_AFTER_PUSH_2026-10-07.md'
 d=dict(status='PARTIAL',mode='STORED_DATA_ONLY',base_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=OUT,text=True).strip(),source_hashes={n:sha(OUT/n) for n in sources},owner_update=dict(path=str(owner),sha256=sha(owner),sections='3-6'),inventory_verified=list(inventory.values()),raw=dict(path=str(raw.relative_to(OUT)),bytes=raw.stat().st_size,sha256=sha(raw)),arena=dict(nominal_radius=6,area=36*math.pi,inside_one_fraction=fine['1'],inside_two_fraction=fine['2'],convergence_absolute=max(abs(area[k]-fine[k]) for k in area),origin_minimum_root_zone_distance=1.,seeded_O_minimum_root_zone_distance=.5,soft_wall=True),arms={a:summarize([r for r in runs if r['variant']==a]) for a in ('RD3','COVA','COVB')},runs=[dict(name=r['name'],summary=summarize([r])) for r in runs],owner_recheck_request=REQUEST)
 d['recommendation']=dict(first_single_change='SERVICE_DEBT_SCHEDULING',key='Largest cumulative integrate-boundary active-unserved seconds among active unserved sites, then pointer-relative site-id; no finite-deficit priority',expected_effect='Preserve accumulated unmet active service through transient service; shift growth priority toward greatest service debt. Coverage improvement is a hypothesis, no prediction of cost removal.',falsifier='If quota/service opportunity becomes less debt-skewed but minimum per-site active service remains poor, reject scheduling as dominant bottleneck; any gate regression also rejects candidate.',scope='Owner/drafter proposal only. No implementation, new run, combined rule, budget increase, pruning, or acceptance.')
 (OUT/'FRONT_ALLOCATION_DIAGNOSTIC.json').write_text(json.dumps(d,separators=(',',':'),allow_nan=False)+'\n')
 render(d)

def render(d):
 lines=['PARTIAL','','Stored-data front allocation over all 30 observer-on runs: RD3, COV-A, COV-B × starts i/ii × keys 0–4. No simulator, pilot, medium, mutation, assay, or policy replay executed. Raw inventories verified before decoding; all 157 retained files checked. The owner update sections 3–6 and relevant code/report hashes are in compact JSON. Base HEAD: `'+d['base_HEAD']+'`.','',
 'Complete for stored snapshot allocation, origin, age and sampled service debt; PARTIAL for exact intra-check components, unrecorded idle pre-growth waiting-clock resets, and continuous-time ownership, which were never recorded. Post-growth figures cannot establish geometry at each birth decision after preceding deletions/insertions. No recorded verdict is changed.','',
 'Definitions and denominators: 160 post-growth figures per run (5..800 s in 5 s steps); 40 growth-end checks per run (20..800 s). Each arm has 1,600 figures and 400 growth-end checks. Snapshot cost is N ordinary + .1 per undirected ordinary held pair (union of strict-radius-3 k=8 selections); O participates in selection/degree but O and its incident pairs are free. Each pair contributes .05 to each endpoint. Accounting cost is not deletion savings: neighbors can rewire.','',
 'For every physical site, including idle: roots are positive-gain unsilenced ordinary bodies at strict distance <3; F_s is directed strong reachability from its roots; H is backward reachability from O. Global front = (union F_s) minus H and O. Redundant = (union F_s intersect H) minus O and single-deletion critical bodies. Strong edges are the stored directed coefficient>=.5 graph, not springs. Positive live gains are preserved by the registered convex adaptation; all-site served sets and growth costs independently crosschecked.','',
 'A no-route component is a weakly connected component of the strong graph induced on F_s intersect global-front. Its diagnostic tip is the body nearest any O, ties by increasing ID. The site tip is the nearest body across these components; undefined before O exists. Thus component-tip count equals component count with O, whereas the single site-tip count is at most one by definition. Neither counts all leaves of a cyclic graph. The present B-path law searches up to eight frontier/backward pairs by gap; it does not own a persistent active tip. Multiplicity here measures graph components, not hidden sponsor identities.','',
 'A front body belongs to every site whose directed F_s contains it; its allocated endpoint cost splits equally among these owners. This conserves total front cost across sites even for shared roots and served/idle owners. Components carry that allocated cost; extra-component cost = owned cost outside the largest-cost component. Component-tip cost is the sum of component-tip body allocations; site-tip cost is the allocation of the single nearest-O front body. JSON also counts defined site tips and component tips over unserved site/checks. They are diagnostic sponsor proxies, not recorded accepted sponsors. Reported shares pool cost sums, never average undefined ratios. Near group is labels 0–3,7; far group labels 4–6 as requested, not Euclidean distance (all sites have radius 4).','',
 '| Arm | Unserved site/checks (20s) | >=2 components / denominator | Mean components | Extra-component / owned unserved cost | Component tips / owned cost | Site tip / owned cost | Front/all cost (5s) |','|---|---:|---:|---:|---:|---:|---:|---:|']
 for a,g in d['arms'].items():
  us=sum(s['growth_end_20s']['unserved_site_checks'] for s in g['sites']);mu=sum(s['growth_end_20s']['multiple_component_checks'] for s in g['sites']);cn=sum(sum(int(k)*v for k,v in s['growth_end_20s']['component_count_histogram'].items()) for s in g['sites']);oc=sum(s['growth_end_20s']['owned_unserved_front_cost_sum'] for s in g['sites']);ex=sum(s['growth_end_20s']['outside_largest_component_cost_sum'] for s in g['sites']);tc=sum(s['growth_end_20s']['tip_body_owned_cost_sum'] for s in g['sites']);stc=sum(s['growth_end_20s']['site_tip_owned_cost_sum'] for s in g['sites'])
  lines.append(f"| {a} | {us} | {mu}/{us} ({100*mu/us:.2f}%) | {cn/us:.3f} | {100*ex/oc:.2f}% | {100*tc/oc:.2f}% | {100*stc/oc:.2f}% | {100*g['front_cost_sum']/g['all_cost_sum']:.2f}% |")
 lines+=['','Exact per-site/check component IDs, tips and cost are in raw DETAILS; compact JSON contains per-site component histograms (zeros included), conditional rooted denominators, full-time, late (>640 s), and cost>=63 summaries. The >=63 selector is descriptive headroom within one unit of 64.','', '| Arm/site | Unserved 20s checks | >=2 | Owned front mean (5s) | Share of arm front | Active / served / debt seconds (sum10 runs) | Quota refusals |','|---|---:|---:|---:|---:|---|---:|']
 for a,g in d['arms'].items():
  for s in g['sites']:
   v=s['all_5s']['owned_front_cost_sum'];c=s['growth_end_20s']
   lines.append(f"| {a}/{s['site']} | {c['unserved_site_checks']} | {c['multiple_component_checks']} | {v/1600:.3f} | {100*v/g['front_cost_sum']:.2f}% | {s['final_active_seconds']:.1f} / {s['final_served_active_seconds']:.1f} / {s['final_debt_seconds']:.1f} | {s['quota_decisions']} |")
 lines+=['','| Arm | Near labels front share | Far labels front share | Front cost owned by currently served labels | Longest-wait/debt first choice differs | Quota B-path / B1 |','|---|---:|---:|---:|---:|---|']
 for a,g in d['arms'].items():
  near=sum(s['all_5s']['owned_front_cost_sum'] for s in g['sites'] if s['site'] in (0,1,2,3,7));uns=sum(s['all_5s']['owned_unserved_front_cost_sum'] for s in g['sites']);sc=g['scheduler']
  lines.append(f"| {a} | {100*near/g['front_cost_sum']:.2f}% | {100*(1-near/g['front_cost_sum']):.2f}% | {100*(1-uns/g['front_cost_sum']):.2f}% | {sc['first_choice_differs']}/{sc['eligible_checks']} | {g['quota_counts'].get('B-path',0)} / {g['quota_counts'].get('B1',0)} |")
 lines+=['', 'Primary integrated vs lagged settled debt changes the first debt choice on '+ ', '.join(f"{a}: {g['scheduler']['debt_sampling_first_choice_changes']}/{g['scheduler']['eligible_checks']} eligible checks" for a,g in d['arms'].items())+'. Clock proxies match all 400 recorded COV-A orders in this batch; that agreement does not recover missing idle pre-growth reset values.', '',
 'Observer service debt uses exact 0.1 s stored observer counts: D_s(k)=.1 sum through k of active_s and not served_s, equivalently active time minus served active time. Raw retains all 8,000 points/run and all quota terminals with all eight debts. At a quota decision t, settled debt includes world steps through t−.1, because the t observer step occurs after growth. This is a lagged settled-observer convention, not all elapsed exposure through t. The primary quota/scheduler comparison instead uses contemporaneous integrate-boundary debt: .1 times active-unserved historical steps through t, before growth at each boundary. Its current interval is already complete when the decision occurs. These historical paths list active sites only, which suffices for active service debt. Earlier growth boundaries also differ in pre-/post-growth service sampling; both full histories are preserved. JSON counts first-choice changes between the two debt conventions. No elapsed inactive time is charged.','',
 'COV-A key is (infinite-deficit last, descending active-unserved waiting, pointer-relative site ID). Waiting resets on any served integrate step (idle included), accumulates only while active and unserved, and is retained through inactive unserved periods. COV-A order is taken exactly from recorded B_path_check ranks. Clock arithmetic uses accumulated float +.1 (count/10 loses implementation precision), all-site served world records on nongrowth steps, and pre-growth active paths plus post-growth idle served as an explicit proxy at growth boundaries. Historical paths omit idle sites; exact pre-growth idle resets are not identifiable at checks with missing erased positions. Clock-proxy disagreements with COV-A ranks are counted in JSON. RD3/COV-B offline COV-A-key orders are therefore proxies, while COV-A actual-order/debt comparisons are exact. Debt key is descending integrate-boundary debt then the same pointer-relative ID among the recorded initial active-unserved candidates. It intentionally lacks finite-deficit priority; disagreement alone is not a causal scheduler benefit. Intra-check births may connect a later candidate, so initial ordering comparisons are not hypothetical quota acceptances. Refused-site debt distributions and run/check details remain in JSON/raw.','',
 'D. Existing economy result only: ECO-F retained trajectories and assays match RD3, zero removals; clock state/digests and telemetry bytes differ. Its clock reaches60 s 76 times; 71 following stages reset for no eligible donor (five terminal clocks censored). Of 891 unserved progress resets, 512 improvements are below .14420268866; minimum 1.26575e-7, median .114604. Every front body is a root of at least one site at all 3,200 site/growth-end donor assessments, excluding all non-root donors under the current rule. A meaningful-progress clock alone therefore does not solve donor availability. The prior original-stage reconstruction has 35 D3-erasure cases with missing coordinates; its 0–35 opportunity bound is not a sequential policy-removal prediction. No ECO-F recalibration/replay is performed here.','',
 '| Arm | Front body observations | Root / shared-root observations | Front age median / p90 (s) | Age>=120 | Front B1 / B-path / seeded cost share | Redundant B1 / B-path / seeded cost share |','|---|---:|---|---|---:|---|---|']
 for a,g in d['arms'].items():
  fc=g['front_cost_sum'];rc=sum(v['redundant']['cost_sum'] for v in g['origin'].values());ages=g['front_ages']
  fs=' / '.join(f"{100*g['origin'][r]['front']['cost_sum']/fc:.2f}%" for r in ('B1','B-path','seeded'));rs=' / '.join(f"{100*g['origin'][r]['redundant']['cost_sum']/rc:.2f}%" for r in ('B1','B-path','seeded'))
  lines.append(f"| {a} | {g['front_body_samples']} | {g['front_roots']} / {g['front_shared_roots']} | {ages['median']:.1f} / {ages['p90']:.1f} | {100*g['front_old_body_samples_ge120']/g['front_body_samples']:.2f}% | {fs} | {rs} |")
 lines+=['', 'Shared-root fractions over front-body observations: '+ '; '.join(f"{a} {g['front_shared_roots']}/{g['front_body_samples']} = {100*g['front_shared_roots']/g['front_body_samples']:.2f}%" for a,g in d['arms'].items())+'.', '',
 'Birth rule is exact event provenance; age = figure time minus exact birth time (seeded bodies born 0). Costs above describe body observations/current endpoint allocations, not counts of births or original admission costs. Bodies can change class and survive right-censored at 800. B-out creates O and owns zero front/redundant charged body cost; seeded O is likewise excluded. This is attribution of geometry to origin, not proof that the originating rule caused failure or that front/redundant cost is expendable.','',
 f"F. Nominal arena is the radius 6 disk, area36π={d['arena']['area']:.8f}; native wall is soft outside6, so this is a declared area denominator, not a hard containment claim. Eight strict-radius 3 reach disks centered on the radius 4 ring cover {100*d['arena']['inside_one_fraction']:.6f}% of that arena at least once and {100*d['arena']['inside_two_fraction']:.6f}% at least twice. Deterministic adaptive integration of radial angular coverage agrees to {d['arena']['convergence_absolute']:.2g} absolute fraction under tighter tolerance. Boundaries have zero area. The entire unbounded plane has no finite arena-fraction denominator.", '',
 'Geometry derivation: on radius r, each site covers a half-angle δ=acos((r²+7)/(8r)), for1<r<7. With angular spacingπ/4, at-least-one angular fraction is clamp(2δ/(π/4),0,1); at-least-two is clamp(2δ/(π/4)−1,0,1). Integrate each against2r/36 from 1 to 6, split at δ=π/8 and π/4. The nearest root-zone point is distance 1 from origin O (infimum; strict reach excludes the boundary); seeded O=(-.5,0) has infimum .5. No direct root lies at either fixed O. Actual output-to-zone distances are retained per snapshot, with their distributions in JSON.','',
 '| Arm | Ordinary observations in >=1 / >=2 zone | All positions including O in >=1 / >=2 | Ordinary observations outside radius 6 | Front distance to O median / p90 |','|---|---|---|---:|---|']
 for a,g in d['arms'].items():
  v=g['geometry'];ds=g['front_distance_O'];n=v['ordinary_count'];m=v['all_positions_count']
  lines.append(f"| {a} | {v['ordinary_inside_one']}/{n} ({100*v['ordinary_inside_one']/n:.2f}%) / {v['ordinary_inside_two']}/{n} ({100*v['ordinary_inside_two']/n:.2f}%) | {v['all_positions_inside_one']}/{m} / {v['all_positions_inside_two']}/{m} | {v['outside_nominal_arena']} | {ds['median']:.3f} / {ds['p90']:.3f} |")
 lines+=['',
 'Element fractions pool ordinary-body/snapshot observations (not unique bodies or area); the all-position denominator additionally includes O. All front bodies are direct roots in these retained samples: the current front classification is empirically root mass inside sensor reach without a directed strong route to O. It need not be a growing chain, and lacking a route is broader than lacking a single direct edge. Shared root zones and dense receiver-normalized bodies can create a single component with substantial unfinished cost.','',
 'Applying section 6: multiple components exist, but they do not own most unfinished cost. Extra components own only 18.15%/13.52%/13.44% of unserved-owned front cost at 20 s checks (RD3/COV-A/COV-B); the dominant component owns 81.85%/86.48%/86.56%. This is not a duplicated-front-dominance result. The current B-path can still branch inside one component, so one-active-tip is not disproved, but these observations do not make it the first supported change. The measured cost partition is not a causal upper bound on its benefit.', '',
 'The first single change supported for a bounded next proposal is SERVICE-DEBT SCHEDULING: largest cumulative integrate-boundary active-unserved seconds among current active-unserved sites, with the existing pointer-relative deterministic ID tie break. Keep the existing growth search, budget, roots, donor rules and service metric. In COV-A the key disagrees with recorded longest-wait first choice at 98/399 eligible checks, including 43 checks that contain quota refusals; these are fixed-history ordering differences, not predicted new acceptances. COV-A site 7 has 5143.9/5312 active seconds owed in the observer convention, while sites 5/6 owe 5715.7/5792 and 5117.1/5216. Transient service resets waiting without erasing cumulative debt. COV-A already validates the general fairness direction descriptively, but redistributes service strongly. This gives scheduling an observable, conservative lever before changing what a physical site/root means.', '',
 'Expected effect: preserve unmet active exposure through brief service and allocate the two accepted-birth opportunities toward larger outstanding debt; improved minimum per-site active coverage is a hypothesis. It does not recover front cost or guarantee route completion. Falsifier: if opportunity/quota allocation becomes less skewed by debt but minimum per-site active service stays poor, scheduling is not the dominant bottleneck; any gate regression also rejects the candidate. Formal success thresholds belong in an owner-approved proposal, not this retrospective diagnostic.', '',
 'Resource refusals remain material: last B-path-check outcomes for initial active-unserved candidates are RD3 cost 755/quota 505, COV-A cost 796/quota 592, COV-B cost 392/quota 539 plus 28 recycle_failed. Counts are site/check last outcomes, not all requests. Thus the recommendation is a bounded fairness test, not a claim that debt dominates every late budget limitation. Do not raise the budget.', '',
 'Old front bodies dominate residence, but age alone does not prove lack of meaningful progress. Meaningful-progress recycling requires both a prospective progress definition and a donor redesign because current all-root exclusions leave zero donors; stored evidence does not identify safe deletions. Geometry/shared-front representation deserves follow-up: roughly 90% of front observations are roots of multiple sites and all are roots of some site. However narrowing the physical root/service definition can merely change the measurement, and no stored evidence proves better service under that change. First separate a growth-authority definition from the physical reach/service metric in a reviewed design; no narrower-root rule is selected or run here. No redundancy thinning or combined intervention is supported.', '',
 'No change is implemented or authorized.','',
 'Separate owner recheck request:', '', '> '+REQUEST,'',
 'Reviewer pass and disposition: `FRONT_ALLOCATION_RECHECK.md`. Under the explicit owner prohibition, tracking is in this new artifact; docs/PLAN_CURRENT.md is neither edited, staged nor hashed.','',
 'Reproduce arithmetic only: `python3 evidence/tactical_composition_demo/growing_shapes_review_claude/rev711_diag/medium_variants/analyze_front_allocation.py`. Raw details: `'+d['raw']['path']+'`, '+str(d['raw']['bytes'])+' bytes, SHA256 `'+d['raw']['sha256']+'`. Compact JSON has all 30 run summaries, per-site denominators, source identity and raw inventory.']
 (OUT/'FRONT_ALLOCATION_DIAGNOSTIC.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
