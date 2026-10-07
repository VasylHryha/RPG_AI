"""Stored-data arithmetic only; one process, standard library, no native/project engine.
Reuse the reviewed front allocation decoder/helpers. Only three named outputs and
new _local/front_tips_rootzone intermediates are written. No existing evidence edits.
"""
from pathlib import Path
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
import math
import os
import statistics
import subprocess
import sys
import time

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
REPO = OUT.parents[4]
RAW = OUT / '_local/front_tips_rootzone'
ARMS = ('RD3', 'COVA', 'COVB', 'CAP96', 'CAP128')
QUANTUM = .556  # pinned rev7_design.R_STAR, placement length, never fitted to scores
ZONE = 1.44  # requested rounded sqrt(log(32/(8*.5))) = 1.4420268866
FAR = {3, 4, 5, 6}
REQUEST = "Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps."
spec = importlib.util.spec_from_file_location('stored_front_allocation', OUT / 'analyze_front_allocation.py')
fa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fa)  # guarded main; no simulation imports or side effects


def dump(path, obj):
    path.write_text(json.dumps(obj, separators=(',', ':'), allow_nan=False) + '\n')


def equal(a, b):
    assert math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-8), (a, b)


def graph(f, outputs):
    pos = {int(i): xy for i, xy in f['positions'].items()}
    assert all(all(math.isfinite(x) for x in xy) for xy in pos.values())
    o = outputs & pos.keys()
    ordinary = set(pos) - o
    out = {i: set() for i in pos}
    inc = {i: set() for i in pos}
    for a, b in f['strong_edges']:
        out[a].add(b)
        inc[b].add(a)
    roots = {s: {i for i in ordinary if math.dist(pos[i], xy) < 3} for s, xy in enumerate(fa.SITES)}
    narrow = {s: {i for i in roots[s] if math.dist(pos[i], xy) < ZONE} for s, xy in enumerate(fa.SITES)}
    forward = {s: fa.reach(r, out) for s, r in roots.items()}
    narrowed = {s: fa.reach(r, out) for s, r in narrow.items()}
    back = fa.reach(o, inc)
    union = set().union(*forward.values())
    small_union = set().union(*narrowed.values())
    front = union - back - o
    served = {s for s in roots if forward[s] & o}
    on = union & back - o
    critical = {i for i in on if any(not (fa.reach(roots[s], out, i) & o) for s in served)}
    redundant = on - critical
    # Full held receiver degree including O; strict radius, k=8. Check stored
    # directed coefficient graph too, including uniqueness at k boundary.
    pairs = set()
    predicted = set()
    for i in pos:
        near = sorted((math.dist(pos[i], pos[j]), j) for j in pos if i != j)
        if len(near) > 8:
            assert near[7][0] != near[8][0], 'ambiguous held-neighbor boundary'
        held = [(d, j) for d, j in near[:8] if d < 3]
        for d, j in held:
            if 32 * math.exp(-d*d) / len(held) >= .5:
                predicted.add((j, i))
            if i not in o and j not in o:
                pairs.add(tuple(sorted((i, j))))
    assert predicted == set(map(tuple, f['strong_edges'])), (f['t'], predicted ^ set(map(tuple, f['strong_edges'])))
    cost = {i: 1. for i in ordinary}
    for a, b in pairs:
        cost[a] += .05
        cost[b] += .05
    return pos, o, out, inc, forward, narrowed, back, front, redundant, served, cost, small_union


def snapshot(f, outputs, births, active):
    pos, o, out, inc, forward, narrow, back, front, redundant, served, cost, small_union = graph(f, outputs)
    # Reuse reviewed allocation and crosscheck class totals, roots, service/cost.
    base = fa.allocation(f, outputs, births)
    equal(base['front_cost'], sum(cost[i] for i in front))
    equal(base['redundant_cost'], sum(cost[i] for i in redundant))
    equal(base['cost'], sum(cost.values()))
    assert set(base['served']) == served
    owner = {i: [s for s in range(8) if i in forward[s]] for i in front}
    bins = [0., 0., 0.]
    for i in front:
        d = min(math.dist(pos[i], xy) for xy in fa.SITES)
        bins[0 if d < ZONE else 1 if d < 3 else 2] += cost[i]
    equal(sum(bins), base['front_cost'])
    lost_union = sum(cost[i] for i in front - small_union)
    per = []
    for s in range(8):
        ids = front & forward[s]
        owned = {i: cost[i] / len(owner[i]) for i in ids}
        equal(sum(owned.values()), base['sites'][s]['owned_cost'])
        row = dict(site=s, active=s in active, served=s in served, owned_cost=sum(owned.values()),
                   component_count=base['sites'][s]['component_count'],
                   lost_site_reach_cost=sum(owned[i] for i in ids - narrow[s]),
                   narrow_served=bool(narrow[s] & o), tips=None, best_tip=None,
                   best_subtree_cost=0., rest_subtree_cost=0., alternate_best_cost=0., same_component_multiple=False)
        if o:
            dO = {i: min(math.dist(pos[i], pos[j]) for j in o) for i in ids}
            decreasing = {i: {j for j in out[i] & ids if dO[j] < dO[i]} for i in ids}
            tips = {i for i in ids if not decreasing[i]}
            gap = {i: min(math.dist(pos[i], pos[j]) for j in back) for i in tips}
            best = min(tips, key=lambda i: (gap[i], dO[i], i)) if tips else None
            # Deterministic distance-decreasing forest; cycles cannot occur.
            sink = {}
            for i in sorted(ids, key=lambda i: (dO[i], i)):
                sink[i] = sink[min(decreasing[i], key=lambda j: (dO[j], j))] if decreasing[i] else i
            assert set(sink.values()) == tips
            subtree = {i: sum(owned[j] for j in ids if sink[j] == i) for i in tips}
            equal(sum(subtree.values()), row['owned_cost'])
            # Sensitivity: split each body among ALL minima reachable by strictly
            # decreasing edges, instead of choosing one steepest edge.
            destinations = {}
            for i in sorted(ids, key=lambda i: (dO[i], i)):
                destinations[i] = set().union(*(destinations[j] for j in decreasing[i])) if decreasing[i] else {i}
            alternate = sum(owned[i] / len(destinations[i]) for i in ids if best in destinations[i]) if best is not None else 0.
            comps = base['sites'][s]['components']
            row.update(tips={i: dict(gap=gap[i], distance_O=dO[i], subtree_cost=subtree[i]) for i in sorted(tips)},
                       best_tip=best, best_subtree_cost=subtree.get(best, 0.),
                       rest_subtree_cost=row['owned_cost'] - subtree.get(best, 0.), alternate_best_cost=alternate,
                       same_component_multiple=any(len(tips & set(c['ids'])) >= 2 for c in comps))
        per.append(row)
    # Redundancy allocation is to route-supporting physical sites, idle included;
    # NOT proximity, birth sponsor, or a selected shortest path.
    route = [0.] * 8
    active_route = [0.] * 8
    exclusive = dict(far_only=0., near_only=0., shared=0.)
    for i in redundant:
        support = {s for s in range(8) if i in forward[s] and i in back}
        assert support and support <= served
        for s in support:
            route[s] += cost[i] / len(support)
            if s in active:
                active_route[s] += cost[i] / len(support)
        key = 'shared' if support & FAR and support - FAR else 'far_only' if support & FAR else 'near_only'
        exclusive[key] += cost[i]
    equal(sum(route), base['redundant_cost'])
    equal(sum(exclusive.values()), base['redundant_cost'])
    return dict(t=f['t'], cost=base['cost'], front_cost=base['front_cost'], redundant_cost=base['redundant_cost'],
                front_distance_bins=bins, lost_union_reach_cost=lost_union, sites=per,
                redundant_site_support_cost=route, active_redundant_site_support_cost=active_route,
                redundant_support_groups=exclusive)


def persistence(series, interval):
    points = [x for x in series if x['t'] % interval == 0]
    previous = {}
    spells = {}
    closed = []
    rows = []
    transitions = Counter()
    for p in points:
        current = {}
        for r in p['sites']:
            if r['active'] and not r['served'] and r['tips'] is not None:
                for i, tip in r['tips'].items():
                    current[(r['site'], i)] = tip['gap']
        continuing = previous.keys() & current.keys()
        transitions['candidate_tip_transitions'] += len(previous)
        transitions['persistent_tip_transitions'] += len(continuing)
        transitions['persistent_no_quantum_progress'] += sum(previous[k] - current[k] < QUANTUM for k in continuing)
        transitions['persistent_quantum_progress'] += sum(previous[k] - current[k] >= QUANTUM for k in continuing)
        for k in list(spells):
            if k not in current:
                closed.append(dict(site=k[0], tip=k[1], **spells.pop(k), end_observation=p['t'], right_censored=False))
        for k, gap in current.items():
            if k not in spells:
                spells[k] = dict(start=p['t'], last=p['t'], anchor_gap=gap, observations=1, cumulative_quantum_events=0, last_quantum_t=p['t'], longest_no_quantum_span=0.)
            else:
                sp = spells[k]
                sp['last'] = p['t']
                sp['observations'] += 1
                if sp['anchor_gap'] - gap >= QUANTUM:
                    sp['longest_no_quantum_span'] = max(sp['longest_no_quantum_span'], p['t'] - interval - sp['last_quantum_t'])
                    sp['cumulative_quantum_events'] += 1
                    sp['anchor_gap'] = gap
                    sp['last_quantum_t'] = p['t']
                else:
                    sp['longest_no_quantum_span'] = max(sp['longest_no_quantum_span'], p['t'] - sp['last_quantum_t'])
        rows.append(dict(t=p['t'], previous_t=p['t']-interval,
                         previous_tip_count=len(previous), persistent=len(continuing),
                         no_quantum_progress=sum(previous[k]-current[k] < QUANTUM for k in continuing)))
        previous = current
    # Last samples have no next observed transition.
    for k, sp in spells.items():
        closed.append(dict(site=k[0], tip=k[1], **sp, end_observation=None, right_censored=True))
    return dict(interval=interval, counters=dict(transitions), spells=closed, transitions=rows)


def select(series, period):
    return [x for x in series if period == 'all_5s' or period == 'growth_end_20s' and x['t'] % 20 == 0 or period == 'late_5s' and x['t'] > 640]


def summarize(runs):
    result = dict(runs=len(runs), periods={}, sites=[])
    for period in ('all_5s', 'growth_end_20s', 'late_5s'):
        points = [x for r in runs for x in select(r['series'], period)]
        eligible = [s for p in points for s in p['sites'] if s['active'] and not s['served']]
        defined = [s for s in eligible if s['tips'] is not None]
        owned = sum(s['owned_cost'] for s in defined)
        best = sum(s['best_subtree_cost'] for s in defined)
        hist = Counter(len(s['tips']) for s in defined)
        result['periods'][period] = dict(snapshots=len(points), active_unserved=len(eligible), no_output_checks=len(eligible)-len(defined),
            defined_tip_checks=len(defined), tip_histogram=dict(sorted(hist.items())), tips=fa.stats([len(s['tips']) for s in defined]),
            multiple_tips=sum(len(s['tips']) >= 2 for s in defined), same_component_multiple=sum(s['same_component_multiple'] for s in defined),
            owned_active_unserved_cost=owned, best_subtree_cost=best, rest_subtree_cost=owned-best,
            alternate_best_cost=sum(s['alternate_best_cost'] for s in defined),
            mean_front_cost=statistics.mean(p['front_cost'] for p in points),
            front_cost_sum=sum(p['front_cost'] for p in points), mean_redundant_cost=statistics.mean(p['redundant_cost'] for p in points),
            mean_total_cost=statistics.mean(p['cost'] for p in points),
            front_distance_bins_cost_sum=[sum(p['front_distance_bins'][b] for p in points) for b in range(3)],
            lost_union_reach_cost_sum=sum(p['lost_union_reach_cost'] for p in points),
            lost_allocated_site_reach_cost_sum=sum(s['lost_site_reach_cost'] for p in points for s in p['sites']),
            mean_redundant_site_support_cost=[statistics.mean(p['redundant_site_support_cost'][s] for p in points) for s in range(8)],
            mean_active_redundant_site_support_cost=[statistics.mean(p['active_redundant_site_support_cost'][s] for p in points) for s in range(8)],
            mean_redundant_support_groups={k: statistics.mean(p['redundant_support_groups'][k] for p in points) for k in ('far_only','near_only','shared')})
    for s in range(8):
        site = dict(site=s, periods={})
        for period in ('all_5s', 'growth_end_20s', 'late_5s'):
            points = [p for r in runs for p in select(r['series'], period)]
            e = [p['sites'][s] for p in points if p['sites'][s]['active'] and not p['sites'][s]['served']]
            defined = [v for v in e if v['tips'] is not None]
            site['periods'][period] = dict(active_unserved=len(e), defined_tip_checks=len(defined), no_output_checks=len(e)-len(defined),
                tip_histogram=dict(sorted(Counter(len(v['tips']) for v in defined).items())),
                owned_cost=sum(v['owned_cost'] for v in defined), best_cost=sum(v['best_subtree_cost'] for v in defined),
                rest_cost=sum(v['rest_subtree_cost'] for v in defined),
                mean_front_cost=statistics.mean(p['sites'][s]['owned_cost'] for p in points),
                mean_lost_site_reach_cost=statistics.mean(p['sites'][s]['lost_site_reach_cost'] for p in points),
                old_served_checks=sum(p['sites'][s]['served'] for p in points),
                narrowed_served_checks=sum(p['sites'][s]['narrow_served'] for p in points))
        site['active_steps'] = sum(r['service'][s]['active_steps'] for r in runs)
        site['active_served_steps'] = sum(r['service'][s]['active_served_steps'] for r in runs)
        site['service_fraction'] = site['active_served_steps'] / site['active_steps']
        site['run_service_fraction'] = fa.stats([r['service'][s]['active_served_steps']/r['service'][s]['active_steps'] for r in runs])
        result['sites'].append(site)
    result['persistence'] = {}
    for interval in (5, 20):
        counter = Counter()
        spells = []
        for r in runs:
            a = r['persistence'][str(interval)]
            counter.update(a['counters'])
            spells.extend(a['spells'])
        result['persistence'][str(interval)] = dict(**counter, spells=len(spells),
            spans_seconds=fa.stats([s['last']-s['start'] for s in spells]),
            longest_no_quantum_span=fa.stats([s['longest_no_quantum_span'] for s in spells]),
            spells_span_ge60_no_quantum=sum(s['last']-s['start'] >= 60 and s['cumulative_quantum_events']==0 for s in spells),
            spells_span_ge60=sum(s['last']-s['start'] >= 60 for s in spells),
            right_censored_spells=sum(s['right_censored'] for s in spells))
    result['zero_site_runs'] = sum(any(r['service'][s]['active_served_steps']==0 for s in range(8)) for r in runs)
    return result


def analyze_run(row):
    paths = {('legacy' if '.legacy.' in p['path'] else 'trace'): OUT/p['path'] for p in row['raw_traces']}
    with gzip.open(paths['trace'], 'rt') as stream:
        tr = [json.loads(line) for line in stream]
    with gzip.open(paths['legacy'], 'rt') as stream:
        legacy = json.load(stream)
    world = [x for x in tr if x['kind']=='world_step']
    figs = [x for x in tr if x['kind']=='figure']
    growth = {x['t']: x for x in tr if x['kind']=='growth_check'}
    assert len(world)==len(legacy['steps'])==8000
    assert [x['step'] for x in world] == list(range(1, 8001))
    assert [x['t'] for x in figs] == list(range(5, 801, 5))
    assert sorted(growth) == list(range(20, 801, 20))
    # The legacy harness omits adaptation states. Role comes from birth events;
    # live gain stays positive by pinned convex adaptation from gain=1, reward
    # disabled, no live silencing; do not claim direct gain-state decoding.
    assert not any(e['rule']=='reward_gain' for e in legacy['events'])
    births = {i: dict(t=0., rule='seeded') for i in range(7)} if row['start']=='ii' else {}
    outputs = {6} if row['start']=='ii' else set()
    for e in legacy['events']:
        if e['rule'] in ('B1', 'B-path', 'B-out'):
            births[e['ids'][0]] = dict(t=e['time'], rule=e['rule'])
            assert e['values']['role'] == ('output' if e['rule']=='B-out' else 'element')
            if e['rule']=='B-out':
                outputs.update(e['ids'])
    service = [dict(active_steps=0, active_served_steps=0) for s in range(8)]
    for w, l in zip(world, legacy['steps']):
        assert w['t']==l['t'] and w['active']==l['active']
        assert set(w['active_served'])==set(w['active']) & set(w['served'])
        for s in w['active']:
            service[s]['active_steps'] += 1
            service[s]['active_served_steps'] += s in w['served']
    for s in range(8):
        assert service[s]=={k:row['telemetry']['sites'][str(s)][k] for k in service[s]}
    samples = {x['t']:x for x in row['telemetry'].get('capacity_samples', [])}
    series = []
    for f in figs:
        w = world[int(f['t']*10)-1]
        v = snapshot(f, outputs, births, set(w['active']))
        assert [s['site'] for s in v['sites'] if s['served']]==w['served']
        if f['t'] in growth:
            equal(v['cost'], growth[f['t']]['cost'])
        if samples:
            equal(v['front_cost'], samples[f['t']]['classes']['front']['cost'])
            equal(v['redundant_cost'], samples[f['t']]['classes']['redundant']['cost'])
        series.append(v)
    name = f"{row['variant']}_{row['start']}_k{row['keyset']}_on"
    return dict(name=name, variant=row['variant'], start=row['start'], keyset=row['keyset'], series=series, service=service,
                persistence={str(n):persistence(series, n) for n in (5, 20)})


def main():
    start = time.monotonic()
    priority = 'unavailable'
    try:
        priority = str(os.nice(10))
    except (AttributeError, OSError):
        pass  # sandbox may refuse nice; retain one-worker resource cap
    receipts = [fa.read(OUT/n) for n in ('SERVICE_RUN_SUMMARIES.json', 'COVERAGE_RUN_SUMMARIES.json', 'CAPACITY_RUN_SUMMARIES.json')]
    inventory = {}
    for receipt in receipts:
        for item in receipt['raw_inventory']:
            p = OUT/item['path']
            assert not p.is_symlink() and p.resolve().is_relative_to((OUT/'_local').resolve())
            assert p.stat().st_size==item['bytes'] and fa.sha(p)==item['sha256'], p
            if item['path'] in inventory:
                assert inventory[item['path']]==item
            inventory[item['path']]=item
    sources = {}
    for arm in ARMS:
        buildp = OUT/f'kernel_builder/{arm}_BUILD.json'
        build = fa.read(buildp)
        base = OUT/f'kernel_builder/_worktrees/{arm}/evidence/tactical_composition_demo/growing_shapes'
        for p, digest in [(base/'medium/rev7_design.py', build['design_sha256']),
                          (base/'medium/rev7_medium.cpp', build['build']['source_sha256']['rev7_medium.cpp']),
                          (base/'../growing_shapes_review_claude/rev711_diag/pilot_common.py', build['harness_sha256']),
                          (OUT/'service_graph.py', build['service_graph_sha256'])]:
            assert fa.sha(p)==digest, p
            sources[str(p.resolve().relative_to(REPO))] = digest
        for n in ('medium/design_0h.py', 'runner/rev7_run.py', 'runner/rev7_fixtures.py'):
            p = base/n
            sources[str(p.relative_to(REPO))] = fa.sha(p)
        sources[str(buildp.relative_to(REPO))] = fa.sha(buildp)
        design = (base/'medium/rev7_design.py').read_text()
        assert 'R_STAR=.556' in design
    for n in ('analyze_front_allocation.py', 'FRONT_ALLOCATION_DIAGNOSTIC.md', 'MASS_BUDGET_DIAGNOSTIC.md', 'CAPACITY_DIAGNOSTIC_REPORT.md',
              'SERVICE_RUN_SUMMARIES.json', 'COVERAGE_RUN_SUMMARIES.json', 'CAPACITY_RUN_SUMMARIES.json', 'service_graph.py'):
        p = OUT/n
        sources[str(p.relative_to(REPO))] = fa.sha(p)
    for n in ('docs/reviews/tactical_0h_capacity_result_recheck_codex.md', 'docs/reports/SESSION_SUMMARY_2026-10-07_08.md', 'AGENTS.md'):
        sources[n] = fa.sha(REPO/n)
    print('Verified inventories before decoding:', len(inventory), flush=True)
    rows = [r for d in receipts for r in d['runs'] if r['observer']=='on' and r['variant'] in ARMS]
    assert {(r['variant'], r['start'], r['keyset']) for r in rows}=={(a,s,k) for a in ARMS for s in ('i','ii') for k in range(5)}
    assert len(rows)==50
    for r in rows:
        for item in r['raw_traces']:
            assert inventory[item['path']]['sha256']==item['sha256'] and inventory[item['path']]['bytes']==item['bytes']
    RAW.mkdir(parents=True, exist_ok=True)
    runs = []
    raw_inventory = []
    for row in rows:
        r = analyze_run(row)
        p = RAW/(r['name']+'.json.gz')
        with gzip.GzipFile(filename=str(p), mode='wb', mtime=0) as stream:
            stream.write(json.dumps(r, separators=(',', ':'), allow_nan=False).encode())
        raw_inventory.append(dict(path=str(p.relative_to(OUT)), bytes=p.stat().st_size, sha256=fa.sha(p)))
        runs.append(r)
        print('Analyzed', r['name'], flush=True)
    d = dict(status='DONE', mode='STORED_DATA_ONLY', worker_processes=1, nice=priority,
             base_HEAD=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=OUT, text=True).strip(),
             source_hashes=sources, inventory_verified=list(inventory.values()), derived_raw_inventory=raw_inventory,
             elapsed_seconds=time.monotonic()-start, quantum=QUANTUM, narrow_radius=ZONE,
             arms={a:summarize([r for r in runs if r['variant']==a]) for a in ARMS},
             starts={a:{s:summarize([r for r in runs if r['variant']==a and r['start']==s]) for s in ('i','ii')} for a in ARMS},
             runs=[dict(name=r['name'], summary=summarize([r])) for r in runs], owner_recheck_request=REQUEST,
             review=dict(status='PENDING', family='Codex', tracking='This new report and summary; owner prohibits editing existing PLAN_CURRENT.'))
    # Old verified snapshots are comparison targets, never overwritten/reinterpreted.
    prior = fa.read(OUT/'FRONT_ALLOCATION_DIAGNOSTIC.json')
    for a in ('RD3','COVA','COVB'):
        equal(d['arms'][a]['periods']['all_5s']['front_cost_sum'], prior['arms'][a]['front_cost_sum'])
    d['source_hashes'][str((OUT/'FRONT_ALLOCATION_DIAGNOSTIC.json').relative_to(REPO))] = fa.sha(OUT/'FRONT_ALLOCATION_DIAGNOSTIC.json')
    save(d)


def pct(a, b):
    return f'{100*a/b:.2f}%' if b else 'undefined'


def save(d):
    d['definitions'] = dict(
        tip='No strong out-neighbour in the same F_s minus H minus O with strictly smaller distance-to-O; undefined if no O.',
        subtree='Acyclic forest: select the strictly closer strong neighbour minimizing (distance_O, ID); assign to terminal tip.',
        best_tip='Minimize (distance to H, distance to O, ID).',
        progress='Gap decrease >= .556; endpoint pairs and anchored cumulative spells, same body ID and site.',
        persistence='Active-unserved and a tip at consecutive 5s or 20s endpoints; intermediate eligibility is unknown.',
        ownership='Split charged front endpoint cost equally among all site forward-reach owners, idle/served included.',
        rootzone='Frozen geometry/strong graph reclassification at strict <1.44; union loss and fractional original-owner loss are distinct.',
        redundant_support='Split redundant body cost equally among sites whose F_s contains it; all-site structural support, idle included.',
        far_labels=[3,4,5,6], near_labels=[0,1,2,7], units='Model length for gaps; seconds for spans; endpoint allocated charged cost for cost.')
    d['W8'] = dict(stored_target_rank=['one_active_front_per_site', 'narrow_sensor_root_zone'],
        rationale='Conditional on the front-mass-release rationale: competing tips own a minority but material front share; nearly all front mass stays inside narrower direct root zones and union reach loss is tiny. The roughly 60% loss of original site support could still affect sponsorship or phase interference; those benefits are unresolved.',
        fallback='Ceiling 96 has observed combined admission/retention gains, including shared far-site support, but zero-service starvation persists.',
        limit='Neither efficiency change is tested; narrowing also changes phase drive, so the stored reclassification cannot rank causal improvements.')
    for arm in d['arms'].values():
        for period in arm['periods'].values():
            period['rooted_defined_tip_checks'] = period['defined_tip_checks'] - period['tip_histogram'].get('0', period['tip_histogram'].get(0, 0))
    validation = RAW/'VALIDATION.json'
    if validation.exists():
        d['validation'] = fa.read(validation)
    review = RAW/'RECHECK.json'
    if review.exists():
        d['review'] = fa.read(review)
    d['analysis_script_sha256'] = fa.sha(Path(__file__))
    path = OUT/'FRONT_TIPS_ROOTZONE_SUMMARY.json'
    dump(path, d)
    assert path.stat().st_size < 5_000_000
    render(d)


def render(d):
    lines = ['DONE', '', 'Stored-data-only diagnostic: 50 observer-on runs, RD3/COV-A/COV-B/CAP96/CAP128 × starts i/ii × keys 0–4; 8,000 stored 5 s figures (5..800 s), including 2,000 post-growth 20 s checks (20..800 s). One worker (nice request '+d['nice']+'), standard-library arithmetic; no simulation, native loading, pilot, policy replay, or changes to existing evidence. Complete for the requested sampled discriminants; continuous histories and changed-law outcomes are unavailable. Base HEAD: `'+d['base_HEAD']+'`.', '',
        'Definitions declared before computation. Reuses `analyze_front_allocation.py` for directed reachability, verified decoding conventions and conserved endpoint allocation. Physical sites are the eight radius-4 positions. Roots are unsilenced positive-gain ordinary bodies at strict distance <3, including idle physical sites. O role comes from seeded ID 6 or retained B-out birth events. Exact gains/silence are absent from legacy figures: eligibility follows the pinned live harness (gain=1 birth, positive convex adaptation, reward disabled, no live silencing); this is a source-supported inference, not decoded gain-state values. All stored strong edges, all-site figure service, growth-end cost, prior front totals and CAP class totals are crosschecked.', '',
        'Strong edges are source→receiver with coefficient 32 exp(−r²)/held_receiver_degree >= .5. H is backward reachability from O; F_s is forward reachability from site s roots. Its front is F_s minus H and O. Cost = one per ordinary body + .1 per undirected ordinary held pair (union of strict-radius-3 k=8 selections); O participates in neighbor selection/degree but O and incident pairs are free. Split pair cost .05 to each endpoint. Front endpoint cost is split equally among ALL sites whose F_s contains that body, including served/idle owners. This conserves cost; active-unserved selections use only their fractional shares.', '',
        'A tip is a front body with no strong out-neighbour in that same site front strictly closer to O (minimum Euclidean distance to any present O). No output means undefined, separately counted; an empty front with O has zero tips. Equal-distance edges do not disqualify tips. For a deterministic subtree, each body chooses its strictly closer strong neighbour minimizing (distance-to-O, ID), then follows to a sink. The strictly decreasing forest is acyclic and partitions the front; it is a diagnostic ownership convention, not a recorded sponsor tree. The best tip minimizes (distance to H, distance to O, ID), matching the B-path gap objective more closely than radial rank alone. Best subtree versus rest conserves each site’s allocated front cost. Sensitivity splits each body equally among all tips reachable through strictly decreasing strong edges; it is reported separately.', '',
        'Meaningful gap progress = decrease of at least .556 model length units, the pinned in-phase placement R_STAR. Gap of a tip is its minimum Euclidean distance to H; O belongs to H. Tip persistence means the SAME body ID remains a tip of the SAME active-unserved site at consecutive sampled endpoints. Report 5 s and 20 s separately; no continuous persistence or intervening eligibility is assumed. Per-pair progress compares endpoint gaps. Spells also track cumulative progress against the initial/last-quantum anchor (not reset for small numerical improvements); span = last minus first observed time. A moving H can change gap without tip motion; identity turnover can carry progress to a child. Initial spells are left-limited by sampling; final spells are right-censored. Persistence pools sole and competing tips: it is not a stalled competing-lineage frequency, because growth may transfer progress to a new child ID or another tip.', '',
        'Tip distributions below use only active-unserved site/figure or site/growth-end observations WITH O; zero fronts remain in the denominator. Histograms are tips:count. Cost shares pool sums; they are not averages of ratios.', '']
    for period, label in [('all_5s','5 s figures'),('growth_end_20s','20 s growth-end checks')]:
        lines += [label, '', '| Arm | Active unserved / no O | Defined denominator | Tip histogram | Mean tips | >=2 tips | >=2 in one component | Best / rest owned cost | Alternate best share |', '|---|---:|---:|---|---:|---:|---:|---|---:|']
        for a in ARMS:
            p = d['arms'][a]['periods'][period]
            lines.append(f"| {a} | {p['active_unserved']} / {p['no_output_checks']} | {p['defined_tip_checks']} | {p['tip_histogram']} | {p['tips'].get('mean',0):.3f} | {pct(p['multiple_tips'],p['defined_tip_checks'])} | {pct(p['same_component_multiple'],p['defined_tip_checks'])} | {pct(p['best_subtree_cost'],p['owned_active_unserved_cost'])} / {pct(p['rest_subtree_cost'],p['owned_active_unserved_cost'])} | {pct(p['alternate_best_cost'],p['owned_active_unserved_cost'])} |")
        lines.append('')
    lines += ['| Arm/spacing | Previous tip opportunities | Same-ID persistent | No .556 progress / persistent | >=60s spells with zero cumulative quantum / all >=60s spells | Max sampled no-quantum span |', '|---|---:|---:|---:|---:|---:|']
    for a in ARMS:
        for dt in ('5','20'):
            p = d['arms'][a]['persistence'][dt]
            lines.append(f"| {a}/{dt}s | {p.get('candidate_tip_transitions',0)} | {p.get('persistent_tip_transitions',0)} | {p.get('persistent_no_quantum_progress',0)} / {p.get('persistent_tip_transitions',0)} ({pct(p.get('persistent_no_quantum_progress',0),p.get('persistent_tip_transitions',0))}) | {p['spells_span_ge60_no_quantum']} / {p['spells_span_ge60']} | {p['longest_no_quantum_span'].get('max',0):.0f}s |")
    lines += ['', 'Root-zone geometry: bins use each BODY’s nearest physical-site distance, independent of ownership. Narrow roots use strict distance <1.44; the exact degree-8 strong range is sqrt(log(8)) = 1.4420268866, so 1.44 is the requested rounded geometric threshold, not a universal edge bound. Keep all stored positions, held edges, strong edges and H fixed. Union loss is front cost outside the UNION of narrowed F_s. Allocated-site loss instead counts each existing fractional owner whose narrowed F_s no longer reaches that body; other sites can still reach it. Outside-zone cost is not necessarily union loss because strong chains can remain reachable.', '',
              'This is a PURE RECLASSIFICATION ON STORED GEOMETRY. It is NOT a counterfactual of a changed sensing law: narrowing the sensor root zone also changes sensor phase drive, dynamics, growth, degree and service. No lost root-reachable cost is assumed safely recyclable or saved.', '']
    for period in ('all_5s','growth_end_20s','late_5s'):
        lines += [period+' (late means t>640 s)', '', '| Arm | Mean front cost | <1.44 | 1.44–3 | >=3 | Union reach lost: mean / % front | Allocated-site reach lost: mean / % front |', '|---|---:|---:|---:|---:|---|---|']
        for a in ARMS:
            p = d['arms'][a]['periods'][period]
            fc, n = p['front_cost_sum'], p['snapshots']
            bins = p['front_distance_bins_cost_sum']
            lines.append(f"| {a} | {p['mean_front_cost']:.3f} | {pct(bins[0],fc)} | {pct(bins[1],fc)} | {pct(bins[2],fc)} | {p['lost_union_reach_cost_sum']/n:.3f} / {pct(p['lost_union_reach_cost_sum'],fc)} | {p['lost_allocated_site_reach_cost_sum']/n:.3f} / {pct(p['lost_allocated_site_reach_cost_sum'],fc)} |")
        lines.append('')
    lines += ['Per physical site at 20 s growth-end checks (all starts/keys). Mean front/lost-site costs include idle/served checks; tip histogram and best/rest select active-unserved checks with O.', '', '| Arm/site | Defined / no O | Tip histogram | Best / rest cost sums | Mean front / lost-site reach | Old / narrowed structurally served checks |', '|---|---:|---|---|---|---:|']
    for a in ARMS:
        for s in d['arms'][a]['sites']:
            p = s['periods']['growth_end_20s']
            lines.append(f"| {a}/{s['site']} | {p['defined_tip_checks']} / {p['no_output_checks']} | {p['tip_histogram']} | {p['best_cost']:.2f} / {p['rest_cost']:.2f} | {p['mean_front_cost']:.3f} / {p['mean_lost_site_reach_cost']:.3f} | {p['old_served_checks']} / {p['narrowed_served_checks']} |")
    lines += ['', 'C. Service-supported redundancy. A redundant body supports site s if it lies in F_s ∩ H: it is on some directed root→O walk, not necessarily a simple/shortest route. Split cost equally among those supporting sites (all are structurally served; idle included). “Far” here is the owner-requested labels 3–6; “near” is 0–2,7. These labels are relative to the seeded side, NOT radial physical-site distance (all sites have radius 4). JSON gives each site, active-only portions with the same ownership denominator, starts, runs and shared-group buckets.', '', '| Arm/window | Mean redundant cost | Far 3–6 | Near 0–2,7 | Far-only / near-only / shared bodies cost |', '|---|---:|---:|---:|---|']
    for period in ('all_5s','late_5s'):
        for a in ('RD3','CAP96','CAP128'):
            p = d['arms'][a]['periods'][period]
            vals = p['mean_redundant_site_support_cost']
            g = p['mean_redundant_support_groups']
            lines.append(f"| {a}/{period} | {p['mean_redundant_cost']:.3f} | {sum(vals[s] for s in FAR):.3f} | {sum(vals[s] for s in set(range(8))-FAR):.3f} | {g['far_only']:.3f} / {g['near_only']:.3f} / {g['shared']:.3f} |")
    lines += ['', '| Capacity versus RD3/window | Extra redundant cost | Far-supported increment / share | Near-supported increment / share |', '|---|---:|---|---|']
    for period in ('all_5s','late_5s'):
        b = d['arms']['RD3']['periods'][period]
        for a in ('CAP96','CAP128'):
            p = d['arms'][a]['periods'][period]
            delta = p['mean_redundant_cost']-b['mean_redundant_cost']
            far = sum(p['mean_redundant_site_support_cost'][s]-b['mean_redundant_site_support_cost'][s] for s in FAR)
            near = delta-far
            lines.append(f'| {a}/{period} | {delta:.3f} | {far:.3f} / {pct(far,delta)} | {near:.3f} / {pct(near,delta)} |')
    lines += ['', 'The extra redundant cost is slightly more far-supported than near-supported: 55.62%/56.99% of the late CAP96/CAP128 increment is fractionally attributed to sites 3–6. Almost all late CAP redundancy supports BOTH groups (56.618 of 56.753 and 76.038 of 76.173 cost units). Thus it is shared service-connected material, not a collection of exclusively far routes or near-only waste. Cost support is structural, not a measure of causal signal delivery; the start-specific service table below preserves starvation.', '', '| Arm/start | Site 3 | 4 | 5 | 6 | Runs with any zero-service site |', '|---|---:|---:|---:|---:|---:|']
    for a in ('RD3','CAP96','CAP128'):
        for start in ('i','ii'):
            b = d['starts'][a][start]
            lines.append(f"| {a}/{start} | "+' | '.join(f"{b['sites'][s]['service_fraction']:.6f}" for s in sorted(FAR))+f" | {b['zero_site_runs']}/{b['runs']} |")
    lines += ['', 'Limits: sampled endpoint multiplicity/persistence and a forest partition do not identify accepted sponsors or causally wasted branches. Strong out-neighbour minima can include shared-root blobs, sideways growth and phase-sensitive material; the B-path search considers up to eight pairs, without persistent tip authority. Forest remainder is not a predicted saving; shared-site ownership can overlap the proposed per-site intervention. Gap changes are observational and include moving H. No missing pre-growth deleted positions are inferred. The narrow-zone reclassification can erase existing service support; it cannot predict improved service under modified sensing. Resource arms combine admission headroom with delayed D3 retention; cross-arm extra redundancy is a mean difference, not tracking the same bodies across changed trajectories. Source evidence and existing verdicts are preserved.', '', 'What this says for W8: conditional on the proposed FRONT-MASS-RELEASE rationale, rank (A) one-active-front authority ahead of (B) narrower sensor roots. At 20 s, competing subtrees own 17.19–24.53% of active-unserved allocated front cost (RD3 23.35%). However hidden multiplicity within a single component occurs in only 1.80–2.84% of these site/checks: this does not overturn the earlier finding that one-front authority targets a minority of the front tax. Narrowing roots has little stored mass-release premise: 96.39–97.19% of full-time front cost is ALREADY within 1.44 of a physical site, and union reach loss is only 0.08–0.13%. The much larger roughly 59–61% original-owner reach loss changes which sites support shared mass; it does not free those bodies. That large reassignment leaves possible changes in cross-site sponsorship and phase interference unresolved, so it does not support a general ranking of dynamic benefits. This ranks a bounded tip-authority investigation above narrower roots as an efficiency target, without predicting benefit. Narrower sensing could still change phase dynamics, which this analysis cannot assess. Ceiling 96 remains the measured practical fallback: extra service redundancy supports far labels as well as near labels, overwhelmingly through shared material, but site 5 still has zero empty-start service. No adoption, new law or experiment is authorized.', '', 'Integrity and reproduction: all '+str(len(d['inventory_verified']))+' retained inventory entries checked for sizes/SHA256 before decoding; all 50 complete slots, 8,000 directed strong graphs, sampled all-site service and 2,000 growth-end costs checked. CAP front/redundant totals match the retained class samples, and RD3/COV-A/COV-B front totals match the prior diagnostic. Compact JSON includes per-arm, per-start, per-run and per-site denominators; raw per-snapshot forest tip costs, gap spells and transitions stay in gitignored `_local/front_tips_rootzone/`. Reproduce with `python3 '+str(Path(__file__).resolve().relative_to(REPO))+'` (one worker). JSON size <5 MB.', '', 'Separate Codex owner recheck request, verbatim:', '', '> '+REQUEST, '', 'Recheck/disposition tracking is in these new artifacts because the owner prohibits editing existing files, including docs/PLAN_CURRENT.md. Review state: '+d['review']['status']+'. This is a same-family stored-data recheck, not experimental/scientific acceptance.', '']
    if 'validation' in d:
        lines += ['Focused arithmetic validation: '+d['validation']['status']+' — cumulative sub-quantum progress, regression, ID turnover, inactive interruption, and no-output/service interruption; source preservation and output shape checked. No project suite or native code was run.', '']
    if 'record_path' in d['review']:
        lines += ['Separate reviewer record: `'+d['review']['record_path']+'`, SHA256 `'+d['review']['record_sha256']+'`. Reviewer independently checked all 50 derived identities, all 8,000 allocation/election figures, arm totals/histograms and both persistence recounts; reconstructed 15 original snapshots across five arms and both starts. Original reviewed draft hashes and detailed dispositions are retained in that record.', '']
    if 'disposition' in d['review']:
        lines += [d['review']['disposition'], '']
    (OUT/'FRONT_TIPS_ROOTZONE_DIAGNOSTIC.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    if sys.argv[1:] == ['--render-only']:
        save(fa.read(OUT/'FRONT_TIPS_ROOTZONE_SUMMARY.json'))
    else:
        assert not sys.argv[1:]
        main()
