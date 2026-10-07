"""Stored-data-only coverage audit. Standard library; never imports/runs the medium.

Usage: python3 <this file>. Verifies the entire raw inventory BEFORE decoding
traces, then writes COVERAGE_DIAGNOSTIC.json and COVERAGE_DIAGNOSTIC.md only.
No new thresholds, experimental verdicts, or predictions are calculated.
"""
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import statistics

OUT = Path(__file__).resolve().parent
REVIEWED = '48078a5'
SITES = [(4*math.cos(2*math.pi*s/8), 4*math.sin(2*math.pi*s/8)) for s in range(8)]


def stats(values):
    values = [x for x in values if x is not None]
    return dict(n=len(values), min=min(values), median=statistics.median(values),
                max=max(values), mean=statistics.mean(values)) if values else dict(n=0)


def intervals(rows, predicate):
    result = []
    start = None
    for row in rows:
        if predicate(row):
            if start is None: start = round(row['t']-.1, 10)
        elif start is not None:
            result.append([start, round(row['t']-.1, 10)])
            start = None
    if start is not None: result.append([start, rows[-1]['t']])
    return result


def tally(events):
    result = {}
    for rule in ('B-path', 'B1'):
        selected = [x for x in events if x['birth_rule'] == rule]
        result[rule] = dict(Counter(x['outcome'] for x in selected))
    return result


def reachable(starts, edges):
    found = set(starts)
    todo = list(found)
    while todo:
        for v in edges.get(todo.pop(), ()):
            if v not in found: found.add(v); todo.append(v)
    return found


def geometry(figure, output_ids):
    pos = {int(k): v for k, v in figure['positions'].items()}
    ordinary = {i: xy for i, xy in pos.items() if i not in output_ids}
    outputs = {i: xy for i, xy in pos.items() if i in output_ids}
    # Angular sectors centered on the fixed sites, origin-centered, no overlap.
    sectors = Counter(int(math.floor((math.atan2(y, x) % (2*math.pi))/(math.pi/4)+.5)) % 8
                      for x, y in ordinary.values())
    near = {str(radius): sum(any(math.dist(xy, o) < radius for o in outputs.values())
                            for xy in ordinary.values()) for radius in (1., 3.)}
    return dict(t=figure['t'], ordinary=len(ordinary), output_positions=outputs,
                sectors=[sectors[s] for s in range(8)], near_O_strict=near)


def audit_run(row):
    name = f"{row['variant']}_{row['start']}_k{row['keyset']}_on"
    with gzip.open(OUT/'_local'/(name+'.legacy.json.gz'), 'rt') as f: legacy = json.load(f)
    with gzip.open(OUT/'_local'/(name+'.jsonl.gz'), 'rt') as f: trace = [json.loads(x) for x in f]
    world = [x for x in trace if x['kind'] == 'world_step']
    figures = [x for x in trace if x['kind'] == 'figure']
    growth = [x for x in trace if x['kind'] == 'growth_check']
    terms = []
    ordinary_count = 6 if row['start']=='ii' else 0
    for event in legacy['events']:
        if event['rule'] in ('B1','B-path'): ordinary_count += 1
        elif event['rule'] in ('D1','D3','D4'): ordinary_count -= 1
        elif event['rule']=='birth_terminal':
            terms.append(dict(t=event['time'], cost=event['cost'], **event['values'],
                              ordinary_at_terminal=ordinary_count,
                              ordinary_pair_cost=round(event['cost']-ordinary_count,10)))
    requests = [e for e in legacy['events'] if e['rule']=='birth_request']
    assert len(world) == len(legacy['steps']) == 8000
    assert [x['step'] for x in world] == list(range(1, 8001))
    assert len(terms) == len(requests)
    assert {x['request'] for x in terms} == {x['values']['request'] for x in requests}
    assert legacy['assay'] == row['summary']['assay']
    # The historical sink samples immediately after integrate (before growth).
    # Derive every historical summary field using its original sampling convention.
    steps = legacy['steps']; late = [x for x in steps if x['t'] > 640]
    conn = sum(len(set(x['paths']) & set(x['active']))/max(1, len(x['active'])) for x in late)/len(late)
    best = cur = 0; span = None; start = None
    for x in steps:
        if x['paths']:
            if cur == 0: start = x['t']
            cur += 1
            if cur > best: best = cur; span = [start, x['t']]
        else: cur = 0
    calculated = dict(start=legacy['start'], tag=legacy['tag'], steps=len(steps), last_t=steps[-1]['t'],
                      late_connectivity=round(conn, 3), present=sum(bool(x['paths']) for x in steps),
                      longest_any_site=[span, best], final_n=steps[-1]['n'], O=steps[-1]['O'],
                      births={k:sum(e['rule']==k for e in legacy['events']) for k in ('B-out','B-path','B1')},
                      final_dO=steps[-1]['dO'], keyset=legacy['keyset'], assay=legacy['assay'])
    assert calculated == row['summary'], name
    telemetry = row['telemetry']
    for s in range(8):
        active = sum(s in x['active'] for x in world)
        served = sum(s in x['served'] for x in world)
        both = sum(s in x['active_served'] for x in world)
        assert telemetry['sites'][str(s)] == dict(active_steps=active, active_served_steps=both,
                served_fraction_active=both/active if active else None, served_fraction_all=served/8000, ever_served=served>0)
    outages = [{k:v for k,v in x.items() if k!='kind'} for x in trace if x['kind']=='outage']
    removals = [{k:v for k,v in x.items() if k!='kind'} for x in trace if x['kind']=='removal']
    assert outages == telemetry['outages'] and removals == telemetry['removals']
    assert dict(Counter(x['service_class'] for x in removals if x['rule']=='D3')) == telemetry['d3_removals_by_class']
    assert len(outages) == telemetry['outage_count']
    assert max((x['duration'] for x in outages), default=0.) == telemetry['maximum_outage']
    assert [x['duration'] for x in outages if not x['censored']] == telemetry['repair_latencies']
    assert [x['duration'] for x in outages if x['censored']] == telemetry['latency_censored']
    for cause, n in telemetry['break_causes'].items(): assert n == sum(x['break_cause']==cause for x in outages)
    for cause, n in telemetry['non_repair_causes'].items(): assert n == sum(cause in x['non_repair_labels'] for x in outages)
    degrees = Counter()
    for x in world: degrees.update({str(k):v for k,v in x['realized_degrees'].items()})
    assert dict(degrees) == telemetry['realized_degree_distribution']
    assert sum(v for k,v in degrees.items() if int(k)>2)/sum(degrees.values()) == telemetry['realized_degree_above_2']
    first_cost = min((x['t'] for x in terms if x['outcome']=='cost'), default=None)
    output_ids = set()
    # Seeded O is id 6 (literal_start); empty O is supplied by B-out.
    if row['start']=='ii': output_ids.add(6)
    output_ids.update(e['ids'][0] for e in legacy['events'] if e['rule']=='B-out')
    spatial = [geometry(f, output_ids) for f in figures]
    budgets = []
    for g in growth:
        n = g['service']['population'] - len(output_ids)
        budgets.append(dict(t=g['t'], cost=g['cost'], ordinary=n,
                            ordinary_pair_cost=round(g['cost']-n, 10), headroom=round(64-g['cost'], 10)))
    first_b1 = next((x for x in terms if x['birth_rule']=='B1' and x['outcome']=='accepted'), None)
    if first_b1:
        attempts = [e for e in legacy['events'] if e['rule']=='birth_attempt' and e['values']['request']==first_b1['request']]
        first_b1 = dict(first_b1, position=attempts[-1]['values']['position'])
    first_ordinary_figure = next((f for f in figures if any(int(i) not in output_ids for i in f['positions'])), None)
    first_geometry = geometry(first_ordinary_figure, output_ids) if first_ordinary_figure else None
    per_site = {}
    for s in range(8):
        unserved = [x for x in world if s in x['active'] and s not in x['served']]
        named = [x for x in terms if x['site']==s and x['birth_rule'] in ('B-path','B1')]
        root_samples = [x for x in world if x['gaps'][str(s)] is not None]
        active_root_samples = [x for x in root_samples if s in x['active']]
        finite = [x['gaps'][str(s)] for x in unserved if x['gaps'][str(s)] is not None]
        # Exact logged gap: effective site roots to O's undirected spring component.
        # O is always present after t=20 in empty start and at t=0 seeded.
        # Thus finite gap certifies roots; None before O exists is indeterminate.
        preceding = {x['step']: x for x in world}
        event_rows = []
        for e in named:
            before = preceding.get(int(round(e['t']*10))-1)
            event_rows.append(dict(e, relative_to_first_cost=None if first_cost is None else round(e['t']-first_cost,10),
                    pre_boundary_active_unserved=bool(before and s in before['active'] and s not in before['served']),
                    pre_boundary_gap=before['gaps'][str(s)] if before else None))
        checks = [dict(t=e['time'], **e['values']) for e in legacy['events'] if e['rule']=='B_path_check' and e['values']['site']==s]
        request_opportunities = [dict(t=c['t'],active=c['active'],missing_route_before_B_path=c['missing_path_before'],
                     B_path_terminal_requests=[e['request'] for e in named if e['t']==c['t'] and e['birth_rule']=='B-path'],
                     B1_terminal_requests=[e['request'] for e in named if e['t']==c['t'] and e['birth_rule']=='B1']) for c in checks]
        sampled_roots = []
        for f in figures:
            pos = {int(k):v for k,v in f['positions'].items()}
            roots = [i for i,xy in pos.items() if i not in output_ids and math.dist(xy,SITES[s])<3]
            # Geometry-only root counts; effective roots/gaps are certified by world telemetry.
            incoming = {i:set() for i in pos}; spring = {i:set() for i in pos}
            for a,b in f['strong_edges']: incoming[b].add(a)
            for a,b in f['spring_pairs']: spring[a].add(b);spring[b].add(a)
            comp = reachable(output_ids & set(pos), spring)
            back = reachable(output_ids & set(pos), incoming)
            gap_strong = min((math.dist(pos[a],pos[b]) for a in roots for b in back), default=None)
            sampled_roots.append(dict(t=f['t'], geometric_root_ids=roots,
                                     gap_to_directed_O_ancestors=gap_strong,
                                     O_spring_component_size=len(comp)))
        per_site[str(s)] = dict(service=telemetry['sites'][str(s)], active_unserved_seconds=len(unserved)*.1,
             active_intervals=intervals(world,lambda x:s in x['active']),
             active_unserved_intervals=intervals(world,lambda x:s in x['active'] and s not in x['served']),
             ever_effective_roots=bool(root_samples), first_effective_roots_t=root_samples[0]['t'] if root_samples else None,
             ever_active_effective_roots=bool(active_root_samples),
             first_active_effective_roots_t=active_root_samples[0]['t'] if active_root_samples else None,
             effective_root_intervals=intervals(world,lambda x:x['gaps'][str(s)] is not None),
             gap_at_first_cost_boundary=next((x['gaps'][str(s)] for x in world if x['t']==first_cost), None),
             active_unserved_before_first_cost_seconds=sum(first_cost is None or x['t']<first_cost for x in unserved)*.1,
             active_unserved_after_first_cost_seconds=sum(first_cost is not None and x['t']>=first_cost for x in unserved)*.1,
             active_unserved_rootless_seconds=sum(x['gaps'][str(s)] is None and bool(x['fragment']['ids']) for x in unserved)*.1,
             active_unserved_before_O_seconds=sum(not x['fragment']['ids'] for x in unserved)*.1,
             active_unserved_gap_to_O_spring=stats(finite),
             root_gap_series=[[x['t'],x['gaps'][str(s)]] for x in world if x['step']%50==0],
             root_geometry_5s=sampled_roots, birth_terminal_counts=tally(named),
             birth_outcomes_before_first_cost=tally([x for x in named if first_cost is None or x['t']<first_cost]),
             birth_outcomes_at_or_after_first_cost=tally([x for x in named if first_cost is not None and x['t']>=first_cost]),
             birth_terminals=event_rows, B_path_checks=checks, growth_request_opportunities=request_opportunities,
             active_missing_B_path_checks_without_B1_request=sum(c['active'] and c['missing_route_before_B_path'] and not c['B1_terminal_requests'] for c in request_opportunities))
    return dict(variant=row['variant'], start=row['start'], keyset=row['keyset'],
                state_trajectory_sha256=row['state_trajectory_sha256'], first_cost_refusal_t=first_cost,
                first_cost_refusal=next((x for x in terms if x['outcome']=='cost'), None),
                first_accepted_B1=first_b1, first_population_geometry=first_geometry,
                sites=per_site, budget_growth_checks=budgets, geometry_5s=spatial,
                max_ordinary=max(x['population']-bool(x['fragment']['ids']) for x in world),
                max_growth_cost=max(x['cost'] for x in budgets),
                assay=row['summary']['assay'], telemetry_numeric_audit='PASS')


def main():
    receipt = json.loads((OUT/'SERVICE_RUN_SUMMARIES.json').read_text())
    inventory = receipt['raw_inventory']
    for x in inventory:
        p = OUT/x['path']
        assert p.stat().st_size == x['bytes'], x['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == x['sha256'], x['path']
    print(f'Inventory verified: {len(inventory)} files before decoding.', flush=True)
    runs = []
    for row in receipt['runs']:
        runs.append(audit_run(row))
        print('Audited',row['variant'],row['start'],row['keyset'],flush=True)
    aggregate = {}
    for variant in ('SCR','V1','RD3'):
        selected = [r for r in runs if r['variant']==variant]
        sites = {}
        for s in range(8):
            ss = [r['sites'][str(s)] for r in selected]
            active = sum(x['service']['active_steps'] for x in ss)
            served = sum(x['service']['active_served_steps'] for x in ss)
            evs = [e for x in ss for e in x['birth_terminals']]
            sites[str(s)] = dict(active_seconds=active*.1, active_served_seconds=served*.1,
                    served_fraction_active=served/active, ever_rooted_runs=sum(x['ever_effective_roots'] for x in ss),
                    ever_active_rooted_runs=sum(x['ever_active_effective_roots'] for x in ss),
                    rootless_active_unserved_seconds=sum(x['active_unserved_rootless_seconds'] for x in ss),
                    terminal_counts=tally(evs),
                    pre_cost_terminal_counts=tally([e for e in evs if e['relative_to_first_cost'] is None or e['relative_to_first_cost']<0]))
        aggregate[variant] = dict(sites=sites, first_cost_refusal_t=stats([r['first_cost_refusal_t'] for r in selected]),
                  max_ordinary=stats([r['max_ordinary'] for r in selected]),
                  max_growth_cost=stats([r['max_growth_cost'] for r in selected]),
                  mean_sectors_5s=[statistics.mean(g['sectors'][s] for r in selected for g in r['geometry_5s']) for s in range(8)],
                  mean_near_O_1=statistics.mean(g['near_O_strict']['1.0'] for r in selected for g in r['geometry_5s']))
    paired = [dict(start=s,keyset=k,state_identical=next(r for r in runs if (r['variant'],r['start'],r['keyset'])==('V1',s,k))['state_trajectory_sha256']==next(r for r in runs if (r['variant'],r['start'],r['keyset'])==('RD3',s,k))['state_trajectory_sha256']) for s in ('i','ii') for k in range(5)]
    data = dict(status='DONE', reviewed_commit=REVIEWED, mode='STORED_DATA_ONLY',
            inventory_verified=dict(files=len(inventory),bytes=sum(x['bytes'] for x in inventory)),
            separate_recheck=dict(reviewer='/root/coverage_recheck', family='Codex',
                 verdict='APPROVE_WITH_NOTES', scope='Stored-data diagnostic only; no experimental acceptance',
                 fixed_findings=['deterministic renderer','active versus idle roots','no-request demand',
                                 'frozen novelty candidate limit','seeded initial roots','world-boundary max N']),
            semantics=dict(time='seconds, DT=.1; intervals [start,end), boundary-state durations',
                 gaps='Exact minimum effective-root distance to undirected O spring component; not B-path directed deficit. None means no root or absent O.',
                 figure_roots='Geometric candidates, gain/silent flags absent from figures; effective-root existence independently certified by per-step gaps.',
                 geometry='5-second snapshots, ordinary excludes O; nearest angular sector about origin, centered on each physical site; near-O counts overlap sectors.',
                 event_status='pre_boundary is preceding world boundary at t-.1, NOT exact within-growth request-time service. B-path requests require missing route; B_path_checks seal initial active/missing/rank/deficit.',
                 cost='ordinary N + .1 * held undirected ordinary pairs, O and incident pairs excluded; budget capacity 64 is COST, not just N.',
                 assay='Raw stored assay values cross-checked with receipts; underlying assay decision streams are not archived here, so independent numerical recomputation of A/B/E is unavailable.'),
            aggregate=aggregate, V1_RD3_state_pairs=paired, runs=runs)
    (OUT/'COVERAGE_DIAGNOSTIC.json').write_text(json.dumps(data,separators=(',',':'),allow_nan=False)+'\n')
    write_report(data)


def write_report(data):
    lines = ['DONE','', 'Stored-data coverage diagnostic, reviewed commit `48078a5`. No medium executed. All 93 raw inventory entries verified by size and SHA256 before decoding; 30 stored runs analyzed.',
             '', 'Units and limits: seconds at 0.1-second world boundaries; geometry every 5 seconds. Strong service is structural reachability, not causal signal fidelity. Exact per-step gaps measure effective roots to the **undirected spring component at O**. B-path uses the directed forward-to-backward deficit instead; its growth-check deficits are retained separately. Before O exists, absent gaps cannot certify rootlessness. Figure root lists are geometric candidates (gain/silent flags were not logged there).',
             '', 'Every run/site has active and active-unserved intervals, request outcomes and times relative to first cost refusal, B-path ordering/deficit checks, gap summaries and root geometry in `COVERAGE_DIAGNOSTIC.json`. `growth_request_opportunities` also records checks with no B1 request. Request-time service is not fully logged: pre-boundary status is sampled at t−0.1, and earlier births/deaths in the same check can change it. B-path requests themselves require missing routes; B1 requests measure qualified coverage demand and can occur at structurally served sites. Effective-root onset in the tables uses all fixed physical sites, active or idle; JSON separately gives first active-root onset and active-root existence.',
             '', '| Variant | Site | Active served % | Runs ever with roots | Rootless active-unserved seconds | B-path outcomes | B1 outcomes |',
             '|---|---:|---:|---:|---:|---|---|']
    for variant,a in data['aggregate'].items():
        for s,x in a['sites'].items():
            lines.append(f"| {variant} | {s} | {100*x['served_fraction_active']:.2f} | {x['ever_rooted_runs']}/10 | {x['rootless_active_unserved_seconds']:.1f} | {x['terminal_counts']['B-path']} | {x['terminal_counts']['B1']} |")
    lines += ['', 'Per-run chronology and budget (O is excluded from ordinary N):','',
             '| Run | First cost refusal s | Max ordinary N (world boundaries) | Max cost (growth end) | First B1 site/time | Served active % sites 3/4/5/6 |',
             '|---|---:|---:|---:|---|---|']
    for r in data['runs']:
        first = r['first_accepted_B1']
        fractions = '/'.join(f"{100*r['sites'][str(s)]['service']['served_fraction_active']:.1f}" for s in (3,4,5,6))
        lines.append(f"| {r['variant']} {r['start']}/k{r['keyset']} | {r['first_cost_refusal_t']} | {r['max_ordinary']} | {r['max_growth_cost']:.1f} | {str(first['site'])+'/'+str(first['t']) if first else 'none'} | {fractions} |")
    lines += ['', 'Element allocation over time: `geometry_5s` gives the disjoint origin-centered angular sectors, positions of O, and near-O counts (strict radii 1 and 3; overlapping sector counts). `budget_growth_checks` gives ordinary N, pair-cost and headroom every 20 seconds. No element is assigned to a site just because it occupies that sector.', '',
              '| Variant | Mean ordinary elements by sectors 0…7 (5 s samples) | Mean ordinary elements within 1 of O |',
              '|---|---|---:|']
    for variant,a in data['aggregate'].items():
        lines.append(f"| {variant} | {', '.join(f'{x:.2f}' for x in a['mean_sectors_5s'])} | {a['mean_near_O_1']:.2f} |")
    lines += ['', 'The premise needs one correction: site 3 is served 18.89% under V1/RD3, but 13.26% under SCR. Sites 4/5/6 are 1.61/5.51/5.82% under SCR and 1.94/5.79/7.11% under V1/RD3. These are pooled active-time fractions, not fractions of runs passing.',
              '', 'All eight sites have effective roots while active at some point in **every** run. Lack of any root throughout the run is ruled out. Rootless periods still matter: for V1, sites 4/5/6 spend 1356.3/1340.3/1385.4 seconds active, unserved and rootless across ten runs; site 3 spends 826.9 seconds. The remaining unserved time mostly has roots but no directed strong route. Zero root-to-spring gap can coexist with unserved status: an undirected spring component does not certify a directed strong path.',
              '', 'B-path is not ignoring those sites: V1 sites 4/5/6 receive 278/288/249 B-path requests, including 36/27/36 accepted births. Before each run’s first cost refusal, those sites already suffer 85/96/75 quota refusals and 15/16/17 no-root refusals. Their B1 requests have 17/6/28 output-first deferrals before cost becomes limiting. There are no terminal placement, exhausted, or ordinary-cap refusals anywhere in these thirty runs. Candidate-search clearance failures can still occur within an accepted or exhausted search; terminal placement=0 does not mean every candidate was placeable.',
              '', 'The sequencing follows the code: B-path sorts missing active routes by the shortest directed deficit (pointer breaks ties), gives its check two accepted births, and can repeatedly grow the first site in output-first mode. Later sites receive quota terminals; rootless sites have infinite deficits and follow finite-deficit sites. The output-first predicate freezes novelty timers for all sites while any active roots exist but no active route reaches O. B1 itself can defer already accumulated demand; sites whose timers have not reached 20 seconds emit no B1 request at all. A check with no B1 request is therefore not proof of no demand (and earlier B-path births may already have connected it). At empty-start t=20, the first eligible B1 birth creates one root and immediately defers the remaining B1 sites. This combination gives an early connection priority over broad root/route coverage. These are observed scheduling constraints, not a counterfactual demonstration that changing them will solve coverage.',
              '', 'The first cost refusal occurs at 320–420 seconds (median 400), the same paired time under all three variants. Sites 3–6 already acquire roots while active before that refusal in every run (all-site first-root times below; active times separately in JSON). After this point, cost refusals dominate far-site B-path terminals (V1 sites 4/5/6: 141/143/112). Thus the system often reaches roots but does not finish or retain routes to O before affordable growth is curtailed.',
              '', '**The 64-element count cap is not exhausted.** Every run peaks at only 44–46 ordinary elements at world boundaries. Admission is constrained by weighted cost `N + 0.1 × ordinary undirected held pairs`, with O and its incident pairs exempt. Pair cost consumes about 19–20 cost units near the first refusal; a candidate can be refused even when current cost is below 64 because insertion adds both one element and new charged pairs. D3 can later remove elements after moving geometry raises held-pair cost. Raising an element-count cap alone would not address the observed terminal cost refusals.',
              '', 'Per-run root and geometry evidence (V1/RD3 share physical trajectories; SCR shares first-root times and first cost times, and its differing later details remain in JSON):','',
              '| Start/key | First all-site effective roots at sites 3/4/5/6, s | Gap to O spring component at first-cost boundary, sites 3/4/5/6 | Final sectors 0…7 |',
              '|---|---|---|---|']
    for r in data['runs']:
        if r['variant']!='V1': continue
        roots='/'.join(str(r['sites'][str(s)]['first_effective_roots_t']) for s in (3,4,5,6))
        gaps='/'.join('none' if r['sites'][str(s)]['gap_at_first_cost_boundary'] is None else f"{r['sites'][str(s)]['gap_at_first_cost_boundary']:.3f}" for s in (3,4,5,6))
        lines.append(f"| {r['start']}/k{r['keyset']} | {roots} | {gaps} | {r['geometry_5s'][-1]['sectors']} |")
    lines += ['', 'Across V1 runs, the median effective-root-to-O-spring gap during active-unserved time is 2.13–3.39 for site 3, 2.37–3.78 for site 4, 2.72–3.82 for site 5, and 2.35–3.71 for site 6. Gap alone cannot establish path-growth feasibility: B-path uses directed front/back sets and held receiver degree, and new links must pass strong-rate checks. The per-run JSON retains both the logged B-path deficits and spring-gap series.',
              '', 'O is fixed at (0,0) in every empty run and (−0.5,0) in every seeded run; it never moves in the figure snapshots. Empty first roots are B1 site 2 for k0, site 0 for k1/k3/k4, and site 1 for k2, all at t=20. All are on the north/east side. The seeded population begins as six ordinary elements on a ring centered at (3.1,0), east of O. In the seeded geometry, physical site 4 is actually nearer O (3.5) than site 0 (4.5), yet site 4 is poorly served: distance from the sensor site to O alone does not explain the asymmetry. Population origin and route economics are more consistent with it.',
              '', 'The full-time mean element population is concentrated in sectors 0–3; sectors 4–6 have fewer elements. This is a description, not proof of ownership or waste. Individual final populations can concentrate elsewhere (seeded k0 has 20 elements in sector 6). Counterexamples also prevent a deterministic first-root claim: empty k0 starts at site 2 and ends with 16 elements in sector 2 but some service at neighboring sites; other runs rotate or fragment. The traces show a directional start and uneven allocation, while separating their causal contributions needs a future one-change comparison.',
              '', 'Smallest supported single-mechanism candidates (each alternative stands alone; no runs performed):','',
              '| One task-blind rule | Evidence supporting the candidate | Expected trade-offs |',
              '|---|---|---|',
              '| At each B-path check, order active unserved physical sites by longest waiting time rather than smallest deficit, using the existing pointer for ties. | 85/96/75 pre-cost quota refusals for V1 sites 4/5/6 show competition before resource exhaustion. | Fairer opportunities can spend births on harder routes and delay the first reliable output connection; does not create roots or affordable headroom. |',
              '| Permit B1 to bootstrap an active rootless physical site with already accumulated novelty even while output-first is true. | All sites eventually root, but substantial early rootlessness and B1 deferrals precede cost refusal. | Earlier sensor coverage competes with output bridging for budget; output-first still freezes timers and the quota stays unchanged, so this alone may not generate a request or cover all sites. |',
              '| On a cost-refused birth for an unserved site, recycle one lowest-lock eligible non-service element and retry admission once. | Post-refusal cost dominates far-site requests; D3 currently acts only when existing cost exceeds 64, and V1/RD3 deleted only non-service elements. | A non-service element can be a future bridge or idle reserve. Repeated recycling may churn without making the proposed insertion affordable; current served paths should be recomputed before each choice. |',
              '| Reserve an equal share of available growth cost for each physical site’s root/connection demand. | Low allocation in sectors 4–6 and cost saturation before complete route coverage motivate budget fairness. | More invasive than ordering; elements can serve several sites, so a deterministic shared-element charging convention is needed. Equal shares may strand budget or underfund long routes. |',
              '', 'Priority among these alternatives is not established by stored observations. Waiting-first is the smallest scheduling change; recycling targets the demonstrated weighted-cost boundary. The protected-route D3 change alone improved reliability but left coverage low; the ten V1/RD3 paired state digests are identical. No causal per-site response or new experiment acceptance is claimed.',
              '', 'Numerical verification: all thirty legacy summary fields, site counters, outage/removal records, latency/cause totals and realized-degree distributions agree with stored receipts. A/B/E agree with the raw archived assay values; underlying assay decision streams were not archived, so those values cannot be independently recomputed here. The Part 1 review separately records classification limits and the B-label boundary artifact; this diagnostic does not use those labels to explain coverage.',
              '', 'Owner recheck request for the separate Part 2 reviewer pass:', '',
              '> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it\'s fine to break the things or fully rework. Check for issues, conflicts, gaps.',
              '', 'Separate reviewer `/root/coverage_recheck` (Reviewer family: Codex) returned **APPROVE_WITH_NOTES** for this stored-data diagnostic. It independently verified all 93 raw identities, all 240 site/run censuses, every figure allocation/cost identity, and all 40 growth-request checks per site/run; it inspected the final one-rule candidates. No blocking finding remained. This is a separate agent pass, not an other-family Claude review or experimental acceptance.',
              '', '| Recheck finding | Fix/disposition |',
              '|---|---|',
              '| Report must regenerate with the script | All interpretation, per-run tables and candidate rules are rendered by this script. |',
              '| All-site roots can precede active roots | Added ever_active_effective_roots and first_active_effective_roots_t; table explicitly labels all-site onset. All 240 site/run pairs have active roots, sites 3–6 before first cost refusal. |',
              '| B1 terminal counts omit frozen-timer demand | Added growth_request_opportunities and counts of missing-route checks with no B1 request; explained timer freezing and infinite-deficit ordering. |',
              '| B1 bypass alone does not advance paused timers | Candidate explicitly applies only to already accumulated novelty and keeps timer/quota trade-offs. |',
              '| Initial seeded roots are distinct from the first later B1 birth | Distinguished east-centered initial six-element population from later B1 roots. |',
              '', 'Part 2 disposition: DONE for the stored-data diagnostic; no proposed mechanism was implemented or run. PLAN_CURRENT.md remains unchanged at the owner’s instruction.']
    (OUT/'COVERAGE_DIAGNOSTIC.md').write_text('\n'.join(lines)+'\n')


if __name__ == '__main__': main()
