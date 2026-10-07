"""SCRATCH (no verdict): where does the root->O strong path break in the bond-v2 + screening pilots?
For each path-loss event (a step with a path followed by one without), report the path edges that
vanished, their length, receiver degree and bond status, and the bond-graph component of O.
Bond rule = the screening patch: bonds(a) = the 2 nearest of a's strong incoming partners; a pair is
bonded if either side selects the other; saturated = 2 bonds selected."""
import gzip, json, math, sys, collections

def load(p):
    return json.load(gzip.open(p, 'rt'))['steps']

def analyze_step(st):
    pos = {e[0]: (e[1], e[2]) for e in st['e']}
    role = {e[0]: e[3] for e in st['e']}
    O = next((i for i, r in role.items() if r == 'o'), None)
    inc = {int(k): v for k, v in st['s'].items()}
    d = lambda a, b: math.hypot(pos[a][0] - pos[b][0], pos[a][1] - pos[b][1])
    sel = {a: sorted(v, key=lambda b: d(a, b))[:2] for a, v in inc.items()}
    bond = collections.defaultdict(set)
    for a, v in sel.items():
        for b in v:
            bond[a].add(b); bond[b].add(a)
    out = collections.defaultdict(set)
    for t, srcs in inc.items():
        for s in srcs: out[s].add(t)
    return pos, role, O, inc, sel, bond, out, d

def bfs_path(starts, out, goal):
    prev = {s: None for s in starts}; q = collections.deque(starts)
    while q:
        u = q.popleft()
        if u == goal:
            p = [u]
            while prev[p[-1]] is not None: p.append(prev[p[-1]])
            return p[::-1]
        for v in out[u]:
            if v not in prev: prev[v] = u; q.append(v)
    return None

def component(start, adj):
    seen = {start}; q = [start]
    while q:
        u = q.pop()
        for v in adj[u]:
            if v not in seen: seen.add(v); q.append(v)
    return seen

def main(p):
    steps = load(p)
    losses = []
    for k in range(1, len(steps)):
        if steps[k - 1]['paths'] and not steps[k]['paths']:
            losses.append(k)
    print(p, 'steps', len(steps), 'path-loss events', len(losses))
    for k in losses:
        a, b = steps[k - 1], steps[k]
        pos, role, O, inc, sel, bond, out, d = analyze_step(a)
        roots = sorted({x for v in a['roots'].values() for x in v})
        path = bfs_path(roots, out, O)
        pos2, role2, O2, inc2, sel2, bond2, out2, d2 = analyze_step(b)
        lost = []
        for u, v in zip(path, path[1:]):
            if u not in inc2.get(v, []):
                gone = u not in pos2 or v not in pos2
                lost.append(dict(edge=(u, v), r_before=round(d(u, v), 3), r_after=None if gone else round(d2(u, v), 3),
                                 deg_recv=len(inc.get(v, [])), bonded=u in bond[v], removed=gone))
        compO = component(O, bond) if O is not None else set()
        compO2 = component(O2, bond2) if O2 is not None and O2 in pos2 else set()
        sat = lambda c, bd: sum(len(bd[x]) >= 2 for x in c)
        print(f" t={a['t']}->{b['t']} hops={len(path)-1} n={len(pos)} lost={lost}")
        print(f"   O bond-component size {len(compO)} -> {len(compO2)}; roots in O-comp before {len(set(roots)&compO)} after {len(set(roots)&compO2)}; O bonds {sorted(bond[O])} -> {sorted(bond2[O2]) if O2 in pos2 else None}")
        # how long until the next path reappears
        nxt = next((steps[j]['t'] for j in range(k, len(steps)) if steps[j]['paths']), None)
        print(f"   path back at {nxt}")
    # final-state picture
    pos, role, O, inc, sel, bond, out, d = analyze_step(steps[-1])
    compO = component(O, bond)
    roots = sorted({x for v in steps[-1]['roots'].values() for x in v})
    rootcomp = set().union(*[component(r, bond) for r in roots]) if roots else set()
    print(' FINAL: n', len(pos), 'O comp', sorted(compO), 'sizes O-comp', len(compO), 'root-comps', len(rootcomp),
          'O-comp members bonds', {x: sorted(bond[x]) for x in compO},
          'gap O-comp to rest', round(min((d(x, y) for x in compO for y in pos if y not in compO), default=-1), 3))
    # closed ring check on O's component: every member has exactly 2 bonds and component is a cycle
    closed = all(len(bond[x]) == 2 for x in compO) and len(compO) >= 3
    print(' O component is a closed saturated ring:', closed)

if __name__ == '__main__':
    for p in sys.argv[1:]: main(p)
