"""Pure task-blind service geometry used by both telemetry and scratch RD3."""
from collections import Counter, deque
import math


def reach(starts, edges, skip=None):
    found = set(starts) - {skip}; todo = list(found)
    while todo:
        for v in edges.get(todo.pop(), ()):
            if v != skip and v not in found: found.add(v); todo.append(v)
    return found


def path(starts, edges, outputs, skip=None):
    prev = {v: None for v in sorted(set(starts)-{skip})}; todo = deque(prev)
    while todo:
        u = todo.popleft()
        if u in outputs:
            result = [u]
            while prev[result[-1]] is not None: result.append(prev[result[-1]])
            return result[::-1]
        for v in sorted(edges.get(u, ())):
            if v != skip and v not in prev: prev[v] = u; todo.append(v)
    return []


def classify(ids, incoming, roots, outputs):
    outgoing = {i: set() for i in ids}
    for target, sources in incoming.items():
        for source in sources: outgoing[source].add(target)
    routes = {s: path(r, outgoing, outputs) for s, r in roots.items()}
    served = {s for s, p in routes.items() if p}
    on_path = reach(set().union(*roots.values()), outgoing) & reach(outputs, incoming)
    lost = {i: [s for s in sorted(served) if not path(roots[s], outgoing, outputs, i)] for i in ids}
    classes = {i: 'critical' if lost[i] else 'redundant' if i in on_path else 'non-service' for i in ids}
    return outgoing, routes, lost, classes


def service_snapshot(m):
    """Read geometry only. Never call lock/offsets/timers/record, sample RNG, or mutate state."""
    from evidence.tactical_composition_demo.growing_shapes.medium.design_0h import SITES
    es = m.native.elements
    ids = [e.id for e in es]; index = {i: j for j, i in enumerate(ids)}
    positions = {e.id: (e.x, e.y) for e in es}
    outputs = {i for i in ids if m.native.role(i) == 'output'}
    g = m.strong_influence()
    incoming = {i: set(g.incoming[i]) for i in ids}
    # protocol.bindings always supplies 8 drives (reach=3); fallback uses that
    # same physical binding definition for snapshots before the first integrate.
    sites = {s: (x, y, 3.) for s, (x, y) in enumerate(SITES)}
    for d in m.drives:
        if d.id not in sites or (d.x, d.y, d.reach) != sites[d.id]:
            raise ValueError('physical site geometry differs from reviewed bindings')
    active = {d.id for d in m.drives if d.strength > 0}
    ordinary = {e.id for e in es if e.id not in outputs and not e.silent and m.native.gain(e.id) > 0}
    roots = {s: {i for i in ordinary if math.hypot(positions[i][0]-x, positions[i][1]-y) < r} for s, (x,y,r) in sites.items()}
    outgoing, routes, lost, classes = classify(ids, incoming, roots, outputs)
    distance = lambda a,b: math.hypot(positions[a][0]-positions[b][0], positions[a][1]-positions[b][1])
    selected = {a: sorted(incoming[a], key=lambda b: (distance(a,b), index[b]))[:2] for a in ids}
    pairs = {tuple(sorted((a,b))) for a, partners in selected.items() for b in partners}
    spring = {i: set() for i in ids}
    for a,b in pairs: spring[a].add(b); spring[b].add(a)
    component = reach(outputs, spring)
    union_roots = set().union(*roots.values())
    idx, mask, _ = m.native.neighbors()
    held = {e.id: [es[j].id for j, on in zip(row, masks) if on] for e,row,masks in zip(es,idx,mask)}
    scale = m.native.policy()[0] * m.native.params.K
    rates = {(a,b): scale*math.exp(-distance(a,b)**2)/max(1,len(held[b])) for b in ids for a in held[b]}
    eligible = [i for i in ids if i not in outputs and m.step_index-m.birth_steps[i] >= 200]
    served = {s for s,p in routes.items() if p}
    gaps = {s: min((distance(a,b) for a in roots[s] for b in component), default=None) for s in roots}
    return dict(ids=ids, positions=positions, incoming=incoming, outgoing=outgoing, roots=roots, active=active,
                outputs=outputs, routes=routes, served=served, active_served=served&active,
                lost=lost, classes=classes, eligible=eligible, selected=selected, pairs=pairs,
                degree={i:len(spring[i]) for i in ids}, held=held, rates=rates, scale=scale, gaps=gaps,
                fragment=dict(ids=sorted(component),size=len(component),rooted=bool(component&union_roots),
                              screened=bool(component) and all(len(selected[i])>=2 for i in component)))


def ranked_choice(snapshot, eligible, measured):
    if not eligible: raise ValueError('no eligible D3 element')
    order = {'non-service':0,'redundant':1,'critical':2}
    chosen = min(eligible, key=lambda i:(order[snapshot['classes'][i]], measured[i] or 0., i))
    return chosen, snapshot['lost'][chosen]


def compact(snapshot):
    s = snapshot
    return dict(active=sorted(s['active']),served=sorted(s['served']),active_served=sorted(s['active_served']),
                hops={site:len(p)-1 for site,p in s['routes'].items() if p},
                fragment=s['fragment'],
                eligible_classes=dict(Counter(s['classes'][i] for i in s['eligible'])),
                selected_counts=dict(Counter(map(len,s['selected'].values()))),
                realized_degrees=dict(Counter(s['degree'].values())),population=len(s['ids']),gaps=s['gaps'])
