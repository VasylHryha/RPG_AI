"""Aggregate per-world impact results and costs into SUMMARY.json (diagnostic, no verdict)."""
import json, math, sys, os, glob
W = os.path.dirname(os.path.abspath(__file__))
rows = {}
agg = dict(worlds=0, floats=0, changed=0, gt_1e10=0, gt_1e8=0, max_abs=0., max_abs_world=None, discrete_changes=0,
           decisions=0, lock_pairs=0, link_tests=0, pair_flips=0, digests_changed=0)
kinds = {}
for p in sorted(glob.glob(os.path.join(W, 'results', '*.json'))):
    name = os.path.basename(p)[:-5]; d = json.load(open(p))
    pr = d['pair_level']
    flips = [r for r in d['margins']['closest10'] if r['deviation'] is not None and r['deviation'] >= abs(r['margin'])]
    rows[name] = dict(max_abs=d['max_abs'], max_abs_path=d['max_abs_path'], changed=d['changed'], floats=d['floats'],
                      gt_1e10=d['gt_1e10'], gt_1e8=d['gt_1e8'], discrete_changes=d['discrete_changes'],
                      digests_changed=d['digests_changed'], decisions=d['margins']['decisions'],
                      closest=d['margins']['closest10'][0], lowest_ratio=d['margins']['lowest_ratio10'][0],
                      lock_flips=pr['lock_flips'], link_flips=pr['link_flips'], closest_lock=pr['closest_lock'],
                      closest_link=pr['closest_link'], endpoints=d['endpoints'],
                      horizon_max=max((h['last_quarter'] for h in d['horizon']), default=None),
                      horizon_first=max((h['first_quarter'] for h in d['horizon']), default=None))
    agg['worlds'] += 1
    for k in ('floats', 'changed', 'gt_1e10', 'gt_1e8', 'discrete_changes', 'digests_changed'): agg[k] += d[k]
    agg['decisions'] += d['margins']['decisions']; agg['lock_pairs'] += pr['lock_pairs']; agg['link_tests'] += pr['link_tests']
    agg['pair_flips'] += pr['lock_flips'] + pr['link_flips']
    if d['max_abs'] > agg['max_abs']: agg['max_abs'] = d['max_abs']; agg['max_abs_world'] = name
    for k, s in d['margins']['by_kind'].items():
        t = kinds.setdefault(k, dict(n=0, min_abs_margin=math.inf, max_dev=0., min_ratio=math.inf))
        t['n'] += s['n']; t['min_abs_margin'] = min(t['min_abs_margin'], s['min_abs_margin'])
        t['max_dev'] = max(t['max_dev'], s['max_dev']); t['min_ratio'] = min(t['min_ratio'], s['min_ratio'])
costs = {}
for p in sorted(glob.glob(os.path.join(W, 'runs', '*', 'COSTS.json'))):
    d = json.load(open(p)); name = os.path.basename(os.path.dirname(p))
    costs[name] = dict(wall=d['compute_seconds'], cpu=d['compute_cpu_seconds'],
                       load_start=d['start_machine']['load_average'], load_end=d['end_machine']['load_average'])
pairs = {}
for name in costs:
    if name.startswith('exact_') and 'inexact_' + name[6:] in costs:
        e, i = costs[name], costs['inexact_' + name[6:]]
        pairs[name[6:]] = dict(cpu_ratio=i['cpu'] / e['cpu'], wall_ratio=i['wall'] / e['wall'], exact=e, inexact=i)
cr = [p['cpu_ratio'] for p in pairs.values()]; wr = [p['wall_ratio'] for p in pairs.values()]
speed = dict(pairs=len(pairs), cpu_ratio_mean=sum(cr) / len(cr) if cr else None, cpu_ratio_range=[min(cr), max(cr)] if cr else None,
             wall_ratio_mean=sum(wr) / len(wr) if wr else None, wall_ratio_range=[min(wr), max(wr)] if wr else None)
out = dict(kind='DIAGNOSTIC_NO_VERDICT', aggregate=agg, by_kind=kinds, worlds=rows, costs=costs, paired_speed=pairs, speed=speed)
json.dump(out, open(os.path.join(W, 'SUMMARY.json'), 'w'), indent=1, default=float)
print(json.dumps(dict(aggregate=agg, speed=speed), indent=1, default=float))
