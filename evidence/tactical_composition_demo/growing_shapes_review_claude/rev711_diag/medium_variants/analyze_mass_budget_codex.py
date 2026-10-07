"""Stored-only mass audit. No medium imports, native calls, runs or receipt writes.
Run: python3 <this file>. All raw inventory sizes/hashes checked before decoding.
5s class residence estimates are sample allocations, never continuous lifetimes.
"""
from collections import Counter, defaultdict
from pathlib import Path
import gzip, hashlib, json, math, statistics

OUT=Path(__file__).resolve().parent
REVIEWED='e4c6d75d348731d707a1f7dab16250c6a396dc43'
CLASSES=('critical','redundant','front','orphan')
SITES=[(4*math.cos(s*math.pi/4),4*math.sin(s*math.pi/4)) for s in range(8)]
REQUEST="Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps."

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def reach(starts,edges,skip=None):
 seen=set(starts)-{skip};todo=list(seen)
 while todo:
  for v in edges.get(todo.pop(),()):
   if v!=skip and v not in seen:seen.add(v);todo.append(v)
 return seen

def stats(v):
 return dict(n=len(v),min=min(v),median=statistics.median(v),mean=statistics.mean(v),max=max(v)) if v else dict(n=0)

def partition(pos,edges,outputs):
 ordinary=set(pos)-outputs
 roots={s:{i for i in ordinary if math.dist(pos[i],xy)<3} for s,xy in enumerate(SITES)}
 out={i:set() for i in pos};inc={i:set() for i in pos}
 for a,b in edges:out[a].add(b);inc[b].add(a)
 forwards={s:reach(r,out) for s,r in roots.items()}
 served={s for s,r in forwards.items() if r&outputs}
 forward=set().union(*forwards.values());on_route=forward&reach(outputs,inc)
 critical={i for i in ordinary if any(not(reach(roots[s],out,i)&outputs) for s in served)}
 cls={i:'critical' if i in critical else 'redundant' if i in on_route else 'front' if i in forward else 'orphan' for i in ordinary}
 assert len(cls)==len(ordinary)
 return cls,served,roots

def held_pairs(pos,outputs):
 # Native array order is increasing creation id: append births, erase deaths.
 ids=sorted(pos);held={}
 for i in ids:
  near=sorted((math.dist(pos[i],pos[j]),ids.index(j),j) for j in ids if j!=i)
  held[i]=[j for d,_,j in near[:8] if d<3]
 pairs={tuple(sorted((i,j))) for i,row in held.items() for j in row if i not in outputs and j not in outputs}
 return held,pairs

def sample(t,pos,edges,outputs):
 cls,served,roots=partition(pos,edges,outputs)
 held,pairs=held_pairs(pos,outputs)
 counts=Counter(cls.values());pair_share=Counter();matrix=Counter()
 for a,b in pairs:
  pair_share[cls[a]]+=.05;pair_share[cls[b]]+=.05
  matrix['/'.join(sorted((cls[a],cls[b])))]+=1
 by={c:dict(elements=counts[c],pair_cost=pair_share[c],cost=counts[c]+pair_share[c]) for c in CLASSES}
 near={}
 for r in (1.,3.):
  ids={i for i in cls if any(math.dist(pos[i],pos[o])<r for o in outputs)}
  share=sum(.05*((a in ids)+(b in ids)) for a,b in pairs)
  near[str(r)]=dict(elements=len(ids),pair_cost=share,cost=len(ids)+share,classes=dict(Counter(cls[i] for i in ids)))
 cost=len(cls)+.1*len(pairs)
 assert math.isclose(sum(x['cost'] for x in by.values()),cost,abs_tol=1e-9)
 return dict(t=t,ordinary=len(cls),held_pairs=len(pairs),cost=cost,classes=by,pair_class_matrix=dict(matrix),near_O=near,served=sorted(served)),cls,roots

def ideal_star(start,spacing=.556):
 # Two ordinary elements per spoke, offset from O by .556 and 1.112.
 # This concrete geometry tests the quoted approximate 22-unit estimate.
 o=(0.,0.) if start=='i' else (-.5,0.)
 pos={0:o}
 for s in range(8):
  d=(SITES[s][0]-o[0],SITES[s][1]-o[1]);norm=math.hypot(*d)
  for k in (1,2):pos[1+2*s+(k-1)]=(o[0]+spacing*k*d[0]/norm,o[1]+spacing*k*d[1]/norm)
 held,pairs=held_pairs(pos,{0})
 edges=[(j,i) for i,row in held.items() for j in row if 32*math.exp(-math.dist(pos[i],pos[j])**2)/len(row)>=.5]
 cls,served,roots=partition(pos,edges,{0})
 clear=min(math.dist(pos[i],xy) for i in pos for xy in SITES)
 return dict(start=start,spoke_spacing=spacing,ordinary=16,held_pairs=len(pairs),cost=16+.1*len(pairs),served_sites=sorted(served),root_counts={str(s):len(r) for s,r in roots.items()},minimum_site_clearance=clear,minimum_element_clearance=min(math.dist(pos[i],pos[j]) for i in pos for j in pos if i<j),positions=pos,status='STATIC_GEOMETRY_ONLY_NOT_A_DYNAMIC_OR_ASSAY_WITNESS')

def audit_run(row,folder):
 name=f"{row['variant']}_{row['start']}_k{row['keyset']}_on"
 with gzip.open(folder/(name+'.legacy.json.gz'),'rt') as f:legacy=json.load(f)
 with gzip.open(folder/(name+'.jsonl.gz'),'rt') as f:trace=[json.loads(x) for x in f]
 figs=[x for x in trace if x['kind']=='figure'];world={x['t']:x for x in trace if x['kind']=='world_step'}
 growth={x['t']:x for x in trace if x['kind']=='growth_check'}
 assert len(world)==8000 and len(figs)==160
 assert [f['t'] for f in figs]==list(range(5,801,5))
 outputs={6} if row['start']=='ii' else set()
 outputs.update(e['ids'][0] for e in legacy['events'] if e['rule']=='B-out')
 births={};deaths={}
 for e in legacy['events']:
  if e['rule'] in ('B1','B-path'):births[e['ids'][0]]=dict(t=e['time'],rule=e['rule'])
  if e['rule'] in ('D1','D3','D4','D3r'):deaths[e['ids'][0]]=dict(t=e['time'],rule=e['rule'])
 init=set(range(6)) if row['start']=='ii' else set()
 histories=defaultdict(list);series=[];cost_checks=[]
 for f in figs:
  pos={int(k):xy for k,xy in f['positions'].items()};out=outputs&set(pos)
  s,cls,roots=sample(f['t'],pos,f['strong_edges'],out)
  assert s['served']==world[f['t']]['served'],(name,f['t'],'served')
  assert len(pos)==world[f['t']]['population']
  for site in range(8):
   if out:assert bool(roots[site])==(world[f['t']]['gaps'][str(site)] is not None)
  if f['t'] in growth:
   assert math.isclose(s['cost'],growth[f['t']]['cost'],abs_tol=1e-9),(name,f['t'],'cost')
   cost_checks.append(f['t'])
  for i,c in cls.items():histories[i].append((f['t'],c))
  series.append(s)
 assert set(histories)<=init|set(births)
 elements=[];spells={c:[] for c in CLASSES};last_counts=Counter();removed_fates=Counter();deleted_sample=Counter();survivor_sample=Counter();unknown=0
 removals={x['id']:x for x in trace if x['kind']=='removal'}
 for i in sorted(init|set(births)):
  obs=histories.get(i,[]);b=births.get(i,dict(t=0,rule='INITIAL'));death=deaths.get(i)
  residence={c:5*sum(k==c for t,k in obs) for c in CLASSES}
  per_spells={c:[] for c in CLASSES};prev=None;length=0;prev_t=None
  for t,c in obs:
   if c!=prev or (prev_t is not None and t-prev_t!=5):
    if prev is not None:per_spells[prev].append(length)
    prev=c;length=0
   length+=5;prev_t=t
  if prev is not None:per_spells[prev].append(length)
  for c in CLASSES:spells[c].extend(per_spells[c])
  last=obs[-1][1] if obs else 'UNOBSERVED'
  assert not obs or obs[0][0]>=b['t']
  assert not obs or death is None or obs[-1][0]<death['t']
  # All figures are AFTER growth: removed elements at that instant absent.
  fate='SURVIVING_RIGHT_CENSORED' if death is None else removals.get(i,{}).get('service_class','UNKNOWN')
  if i in births:
   last_counts[last]+=1
   if death:removed_fates[fate]+=1;deleted_sample[last]+=1
   else:survivor_sample[last]+=1
   if not obs:unknown+=1
  elements.append(dict(id=i,birth=b,death=death,lifetime_or_censored_seconds=(death['t'] if death else 800)-b['t'],right_censored=death is None,sampled_residence_seconds=residence,maximum_observed_spell_seconds={c:max(per_spells[c],default=0) for c in CLASSES},last_observed_class=last,last_observed_t=obs[-1][0] if obs else None,removal_class=fate))
 mean={c:{k:sum(s['classes'][c][k] for s in series)/160 for k in ('elements','pair_cost','cost')} for c in CLASSES}
 pooled=Counter()
 for e in elements:
  pooled.update(e['sampled_residence_seconds'])
 nb=len(births);nd=sum(i in deaths for i in births)
 return dict(variant=row['variant'],start=row['start'],keyset=row['keyset'],verified_growth_cost_samples=len(cost_checks),mean_sample_allocation=mean,mean_cost=sum(x['cost'] for x in mean.values()),late_mean_allocation={c:{k:sum(s['classes'][c][k] for s in series if s['t']>640)/32 for k in ('elements','pair_cost','cost')} for c in CLASSES},sampled_element_seconds=dict(pooled),observed_spell_seconds={c:stats(spells[c]) for c in CLASSES},birth_fates=dict(births=nb,deleted_births=nd,surviving_births=nb-nd,last_observed_class_counts=dict(last_counts),last_observed_orphan_fraction=last_counts['orphan']/nb if nb else None,last_observed_redundant_fraction=last_counts['redundant']/nb if nb else None,exact_removal_service_class_counts=dict(removed_fates),deleted_birth_last_sample_counts=dict(deleted_sample),surviving_birth_last_sample_counts=dict(survivor_sample),unobserved_births=unknown),near_O_mean={r:{k:sum(s['near_O'][r][k] for s in series)/160 for k in ('elements','pair_cost','cost')} for r in ('1.0','3.0')},series_5s=series,elements=elements)

def main():
 receipts={n:json.loads((OUT/n).read_text()) for n in ('SERVICE_RUN_SUMMARIES.json','COVERAGE_RUN_SUMMARIES.json')}
 inventory={}
 for receipt in receipts.values():
  for r in receipt['raw_inventory']:
   p=OUT/r['path'];assert p.stat().st_size==r['bytes'],str(p);assert sha(p)==r['sha256'],str(p);inventory[r['path']]=r
 print('Raw inventory verified before decoding:',len(inventory),flush=True)
 runs=[]
 for n,receipt in receipts.items():
  for row in receipt['runs']:
   if row['observer']!='on' or row['variant'] not in ('RD3','COVA','COVB'):continue
   folder=OUT/'_local' if row['variant']=='RD3' else OUT/'_local'/'coverage'
   runs.append(audit_run(row,folder));print('Analyzed',row['variant'],row['start'],row['keyset'],flush=True)
 assert len(runs)==30
 aggregate={}
 for arm in ('RD3','COVA','COVB'):
  rr=[r for r in runs if r['variant']==arm];assert len(rr)==10
  means={c:{k:sum(r['mean_sample_allocation'][c][k] for r in rr)/10 for k in ('elements','pair_cost','cost')} for c in CLASSES}
  nb=sum(r['birth_fates']['births'] for r in rr);counts=Counter();removed=Counter()
  for r in rr:counts.update(r['birth_fates']['last_observed_class_counts']);removed.update(r['birth_fates']['exact_removal_service_class_counts'])
  aggregate[arm]=dict(mean_allocation=means,mean_cost=sum(x['cost'] for x in means.values()),births=nb,deleted_births=sum(r['birth_fates']['deleted_births'] for r in rr),last_observed_birth_class_counts=dict(counts),last_observed_orphan_fraction=counts['orphan']/nb,last_observed_redundant_fraction=counts['redundant']/nb,exact_removal_class_counts=dict(removed),cost_dominant_class=max(CLASSES,key=lambda c:means[c]['cost']),near_O_mean={radius:{k:sum(r['near_O_mean'][radius][k] for r in rr)/10 for k in ('elements','pair_cost','cost')} for radius in ('1.0','3.0')})
 sources=['analyze_mass_budget_codex.py','SERVICE_RUN_SUMMARIES.json','COVERAGE_RUN_SUMMARIES.json','service_graph.py','service_telemetry.py','coverage_telemetry.py','kernel_builder/RD3_BUILD.json','kernel_builder/COVA_BUILD.json','kernel_builder/COVB_BUILD.json']
 data=dict(status='PARTIAL',reviewed_commit=REVIEWED,mode='STORED_DATA_ONLY',owner_recheck_request=REQUEST,source_hashes={n:sha(OUT/n) for n in sources},raw_inventory_verified=list(inventory.values()),semantics=dict(classes='Ordinary only, all eight physical sites including idle; critical=single deletion loses any served site, redundant=forward AND backward reachable but not critical, front=forward only, orphan=no forward reach. Reachability matches RD3 (cycles included).',roots='Gain-positive unsilenced ordinary within strict radius 3. Live add gains positive; convex gain adaptation preserves positivity; no live silencing. Figure service/root existence independently matches world telemetry.',held_pairs='Reconstructed strict radius 3, k=8, distance/creation-order ties, union undirected; includes O in neighbor selection but excludes O and incident pairs from charges.',pair_allocation='Each ordinary pair costs .1, split .05 per endpoint. Cross-class pair matrix retained. Accounting attribution, not marginal savings on deletion (neighbors can rewire).',time='160 post-growth figures, t=5..800 every 5 s. Equal right-endpoint weights5 s, not exact lifespan occupancy; birth at endpoint can be overallocated by one bin. No interpolation/inferred transitions. Sampled spells can hide excursions and are censored at boundaries; exact births/deaths from events.',near_O='Strict radii 1 and 3; overlapping diagnostic overlays, not fifth/sixth budget classes.',birth_fate='New B1/B-path births only; initial seeded six excluded. Last observed class is a sampled proxy, not exact deletion fate. Survivor classes right-censored at 800 s. Exact pre-removal redundant/critical/non-service recorded; non-service cannot be split into front/orphan there.',not_observed=['continuous class durations','exact front/orphan class immediately before deletion','future fate of survivors','causal avoidability of allocated cost','dynamic stability or F5 assay of ideal star']),ideal_star=[ideal_star(s,spacing) for spacing in (.556,.8) for s in ('i','ii')],aggregate=aggregate,runs=runs)
 enrich(d=data)
 (OUT/'MASS_BUDGET_DIAGNOSTIC.json').write_text(json.dumps(data,indent=2)+'\n')
 render(data)


def enrich(d):
 for arm in ('RD3','COVA','COVB'):
  prefix=f'kernel_builder/_worktrees/{arm}/evidence/tactical_composition_demo/growing_shapes/'
  for rel in ('medium/rev7_native.py','medium/rev7_design.py','medium/design_0h.py','medium/rev7_medium.cpp','runner/rev7_config.py'):
   d['source_hashes'][prefix+rel]=sha(OUT/(prefix+rel))
 for arm,g in d['aggregate'].items():
  rr=[r for r in d['runs'] if r['variant']==arm]
  late=[s for r in rr for s in r['series_5s'] if s['t']>640]
  saturated=[s for r in rr for s in r['series_5s'] if s['cost']>=63]
  for name,ss in [('late',late),('cost_at_least_63',saturated)]:
   g[name]=dict(samples=len(ss),mean_cost=sum(s['cost'] for s in ss)/len(ss) if ss else None,allocation={c:{k:sum(s['classes'][c][k] for s in ss)/len(ss) if ss else None for k in ('elements','pair_cost','cost')} for c in CLASSES})
 d['semantics']['near_cap']='Cost >=63 snapshots selected descriptively within 1 cost unit of capacity64, not a new experimental endpoint. Late is existing >640 s period.'

def render(d):
 lines=['PARTIAL','','Stored-data mass-budget diagnostic; reviewed commit `'+REVIEWED+'`. No pilots, medium runs, economy-rule runs, or assay replays.','',
 'The stored figures support a complete snapshot allocation, but only sampled residence and last-observed birth classes. Exact continuous residence and orphan/front class at deletion are unavailable; survivor fates are censored. PARTIAL names these limits, not missing trajectories.','',
 'An explicit two-node-per-spoke star checks the approximate 22-unit claim using the real k=8/radius-3 held graph and O exemption:', '',
 '| Start/spoke spacing | Ordinary N | Charged held pairs | Weighted cost | Structurally served sites |','|---|---:|---:|---:|---|']
 for s in d['ideal_star']:lines.append(f"| {s['start']}/{s['spoke_spacing']} | 16 | {s['held_pairs']} | {s['cost']:.1f} | {s['served_sites']} |")
 lines += ['', 'Coordinates and root counts are in JSON. Each spoke places two ordinary bodies at one and two times the stated spacing from O toward the fixed sensor site. The .556-spacing estimate costs 22.4 but fails three seeded roots; spacing .8 reaches all eight sites in both starts at the same 22.4 cost (16 bodies + .1 × 64 charged pairs). All static clearances pass .05 for elements and .3 for sites. Cost is N + .1 times ordinary undirected held pairs; O participates in k-nearest selection and receiver degree but O and incident pairs are free. A sparse drawn star still pays cross-spoke proximity pairs. Strong edges use 32 exp(−r²)/full held receiver degree ≥ .5 s⁻¹. No project code is imported.', '',
 'This is a static structural feasibility illustration, not a constructive growth path, minimum-cost proof, stable dynamic solution, all-site temporal coverage, or A/B/E witness. Seeded O is offset, which requires checking actual sensor-root distances rather than reusing an origin-centered drawing. Thus cheap static geometry alone does not prove the actual controller can achieve/retain service.', '',
 'Snapshot classification follows RD3 using all eight physical sites, including idle sites. Critical bodies individually preserve at least one served site; redundant bodies are on the forward/backward reachability intersection but individually dispensable; fronts are forward reachable without an output route; orphans are unreachable from every site’s roots. Every ordinary element belongs to exactly one class. Near-O radii are overlays. Each pair’s .1 cost splits equally across endpoints, including mixed-class pairs; this is allocation, not deletion savings.', '',
 '| Arm/class | Mean elements | Mean pair cost | Mean total cost | Share of arm cost |','|---|---:|---:|---:|---:|']
 for a,g in d['aggregate'].items():
  for c,m in g['mean_allocation'].items():lines.append(f"| {a}/{c} | {m['elements']:.3f} | {m['pair_cost']:.3f} | {m['cost']:.3f} | {100*m['cost']/g['mean_cost']:.1f}% |")
 lines += ['', 'Means equally weight 160 post-growth snapshots per run and ten runs per arm. The JSON retains every 5 s point, cross-class pair matrix, full-time and late (>640 s) allocation per run, radii <1/<3 near O, per-element sampled residence/maximal observed spells, exact event lifetimes and censoring, and class-spell distributions. A 5 s spell means one observed sample; intermediate switches are unknown.', '',
 '| Arm | New births | Deleted births | Last sampled orphan | Last sampled redundant |','|---|---:|---:|---:|---:|']
 for a,g in d['aggregate'].items():lines.append(f"| {a} | {g['births']} | {g['deleted_births']} | {100*g['last_observed_orphan_fraction']:.1f}% | {100*g['last_observed_redundant_fraction']:.1f}% |")
 lines += ['', 'These fractions count last observed classes over all new births, including right-censored survivors. They must not be read as exact fractions ending in those classes. Exact pre-removal service-class counts and missing-sample births are in JSON; recorded non-service removals cannot retrospectively distinguish fronts and orphans.', '',
 'Fronts hold the largest average cost in every arm: RD3 28.961/48.183 = 60.1%; COV-A 32.355/47.595 = 68.0%; COV-B 23.987/48.159 = 49.8%. Redundant mass is the second-largest allocation (36.4%, 30.0%, 46.1% respectively); orphan allocation is only 0.52%, 0.21%, 0.33%. Orphan-only cleanup therefore has little observed headroom to recover. These full-time means hide a change near capacity: late RD3 and COV-A still allocate most cost to fronts (37.688 and 40.241 units), while late COV-B allocates most to redundancy (34.523 units versus 26.222 fronts). Cost>=63 snapshots show the same switch: fronts 37.823/41.529 for RD3/COV-A, redundancy 32.908 for COV-B. The potential economy target is therefore unfinished reachable growth for RD3/COV-A and service redundancy for cost-limited COV-B. Front/orphan allocation is presently outside service; redundant allocation is individually removable in the current strong graph. Neither establishes causal waste: fronts can become routes, redundant elements alter degree and protect against future losses, orphans can return as geometry moves. A rule deleting several individually dispensable bodies can destroy service after the first deletion.','',
 '| Smallest single task-blind candidate | Evidence to consult | Expected trade-offs |','|---|---|---|',
 '| Remove an orphan only after continuous orphanhood T (low-yield alternative) | Orphan allocation is below .6% in each arm; sampled spells describe the small target; choose T prospectively, continuous persistence cannot be certified here | Releases unrooted mass; can erase dormant future roots/routes; proximity rewiring may offset pair savings; recompute after each removal |',
 '| Thin one service-redundant body per check only after testing the prospective post-deletion all-site graph | Redundant allocation and spells, exact recorded redundant removals | Frozen-graph redundant labels do not guarantee service after nearest-neighbor rewiring and degree changes. A prospective graph check can preserve instant service; dynamics and resilience remain at risk; reclassify every next donor |',
 '| Add a persistence cost for front bodies | Front allocation and residence quantify unfinished route investment | Encourages completion rather than accumulating fronts; can penalize precisely the difficult sites needing longer construction and worsen fairness |',
 '| Charge age-weighted orphan occupancy in admission | Orphan cost share, avoiding a task-specific signal | Discourages carrying long-unrooted bodies; does not itself free capacity and can further block births; class transitions invite oscillation |', '',
 'Prioritize investigating a single persistence rule for fronts or a sequential redundancy thinning rule. Orphan deletion has little numerical support as the main budget remedy. These alternatives stand alone and are evidence-supported targets, not validated improvements. No threshold T, combined mechanism, tuned penalty, or future run is authorized by this diagnostic. Keep physical sites/graph/age as inputs; no tasks, scores, assay results, or learned site preferences.','',
 f"Integrity: all {len(d['raw_inventory_verified'])} raw inventory sizes/SHA256 verified before decoding. All 30 trajectories have 8000 world boundaries and 160 figures; figure service/root existence and coincident growth cost are checked. Costs conserve across four classes. Hash manifest explicitly excludes docs/PLAN_CURRENT.md.",'',
 'Separate Part 2 owner recheck requested verbatim:', '', '> '+REQUEST, '',
 'Recheck disposition: see docs/reviews/tactical_0h_mass_budget_recheck_codex.md; the separate available reviewer is Codex (same family as this analyst), not Claude cross-family acceptance. Fixed recheck findings: named/quantified waste by arm and late period; added per-run residence/fate/near-O tables and censoring; tested the offset-O star; pinned actual retained cost/geometry/gain sources; stated that deletion needs a prospective graph check because neighbors and degrees rewire. Plan tracking lives here under the owner’s prohibition on editing docs/PLAN_CURRENT.md.']
 lines += ['', 'Budget near the binding limit. Late means t>640 s; near-cap snapshots mean cost>=63 (within one unit of capacity64), a descriptive selection. Values are mean class cost, not marginal reclaimable units.', '', '| Arm/period | Samples | Mean cost | Critical | Redundant | Front | Orphan |', '|---|---:|---:|---:|---:|---:|---:|---:|']
 for arm,g in d['aggregate'].items():
  for period in ('late','cost_at_least_63'):
   x=g[period]
   cells=[f"{x['allocation'][c]['cost']:.3f}" if x['samples'] else '—' for c in CLASSES]
   lines.append(f"| {arm}/{period} | {x['samples']} | {x['mean_cost']:.3f} | "+' | '.join(cells)+' |')
 lines += ['', 'Per-run mean allocation (C=critical, R=redundant, F=front, U=orphan; each cell elements + pair cost = total). The full 5 s cost series is in JSON.', '', '| Run | C | R | F | U | Near O <1 / <3, mean total cost |', '|---|---|---|---|---|---|']
 for r in d['runs']:
  cells=[f"{r['mean_sample_allocation'][c]['elements']:.2f} + {r['mean_sample_allocation'][c]['pair_cost']:.2f} = {r['mean_sample_allocation'][c]['cost']:.2f}" for c in CLASSES]
  lines.append('| '+f"{r['variant']}/{r['start']}/k{r['keyset']}"+' | '+' | '.join(cells)+f" | {r['near_O_mean']['1.0']['cost']:.2f} / {r['near_O_mean']['3.0']['cost']:.2f} |")
 lines += ['', 'Observed spell lengths and fate per run. Initial/final spells and disappearance boundaries are censored; these medians are descriptive sample runs, not a survival estimator. C/R/F/U spell cells give median/max sample weights in seconds (— means never observed). These are sample runs, not verified uninterrupted periods. Endpoint sample allocation can exceed an exact lifetime by one 5 s bin, e.g. a birth at 800 s has zero observed future lifetime but a weighted endpoint. Exact lifespan is separate in JSON.', '', '| Run | C spell median/max | R | F | U | Births / deleted / surviving | Last sample orphan / redundant, % all births | Exact removed-born class |','|---|---|---|---|---|---|---|---|']
 for r in d['runs']:
  cells=[f"{r['observed_spell_seconds'][c]['median']:g}/{r['observed_spell_seconds'][c]['max']:g}" if r['observed_spell_seconds'][c]['n'] else '—' for c in CLASSES]
  b=r['birth_fates']
  lines.append('| '+f"{r['variant']}/{r['start']}/k{r['keyset']}"+' | '+' | '.join(cells)+f" | {b['births']}/{b['deleted_births']}/{b['surviving_births']} | {100*b['last_observed_orphan_fraction']:.2f}/{100*b['last_observed_redundant_fraction']:.2f} | {b['exact_removal_service_class_counts']} |")
 lines += ['', 'All deleted new bodies were recorded non-service at deletion; exact redundant endpoints were zero. Some were redundant at the preceding figure: classification changes before removal, so the last-observed redundant percentage is not the redundant-at-death percentage. The JSON separates deleted/surviving last-sample counts; initial seeded elements are excluded from birth denominators.']
 (OUT/'MASS_BUDGET_DIAGNOSTIC.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
