"""SCRATCH PILOT (no verdict): F5 starts (i) empty and (ii) literal with the fixture keys, on a
scratch copy whose motion law weights every N^x pair term by exp(-r^2) (KERNEL PILOT line).
Records path presence per world step and element distances to O. Stub execution grant (scratch only)."""
import sys, gzip, json, math
sys.path.insert(0, '.')
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_fixtures import keys, literal_start
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_evaluator import reused_calibration
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_run import Run

class Grant:
    def require(self, scope): pass
    def snapshot(self, scope): return {'pilot': 'kernel', 'scope': scope}

START, EPISODES, TAG = sys.argv[1], int(sys.argv[2]), sys.argv[3]
BIDIR = len(sys.argv) > 4 and sys.argv[4] == 'bidir'
import evidence.tactical_composition_demo.growing_shapes.medium.rev7_design as D
def install():
    """Bidirectional B-path: every second B-path attempt grows from the OUTPUT side: a point at
    r* from b (in the backward set of O) toward a (in the site's forward set). Its trial needs a
    strong edge new->b, new in the backward set (reaches O), all existing paths kept, the deficit
    reduced or the path connected, and clearance. Forward attempts are unchanged."""
    original = D.Rev7Medium._b_path_attempt
    def attempt(self, site, blocked):
        self._bidir = not getattr(self, '_bidir', True)
        if not self._bidir:
            return original(self, site, blocked)
        g = self.strong_influence(); request = self.request('B-path', site)
        front, back = g.forward(site), g.backward()
        if not back: self.terminal(request, 'B-path', site, 'no_output'); return 'no_output', None
        if not front: self.terminal(request, 'B-path', site, 'no_root'); return 'no_root', None
        es = {e.id: e for e in self.native.elements}
        elements, drives = D.geometry(self.native, self.drives); new = max(es, default=-1) + 1
        k, radius = self.native.params.k, self.native.params.radius
        ps, K = self.native.policy()[0], self.native.params.K
        pos = {e[0]: (e[1], e[2]) for e in elements}
        def gap(gr, p):
            return min((math.hypot(p[u][0]-p[v][0], p[u][1]-p[v][1]) for u in gr.forward(site) for v in gr.backward()), default=math.inf)
        old_gap = gap(g, pos)
        pairs = sorted((math.hypot(es[a].x-es[b].x, es[a].y-es[b].y), a, b) for a in front for b in back)[:8]
        attempts = 0
        for _, a, b in pairs:
            direction = math.atan2(es[a].y-es[b].y, es[a].x-es[b].x)
            for rotation in [0]+[sg*an for an in range(15, 91, 15) for sg in (1, -1)]:
                ang = direction + math.radians(rotation)
                point = (es[b].x + D.R_STAR*math.cos(ang), es[b].y + D.R_STAR*math.sin(ang)); attempts += 1
                full = elements + [(new, *point, 'element', 1., False)]
                after = D.geometric_graph(full, drives, k, radius, strong=True, phase_scale=ps, K=K)
                p2 = dict(pos); p2[new] = point
                checks = dict(edge_new_to_b=new in after.incoming[b], new_back=new in after.backward(),
                              paths_kept=all(not g.path(s) or after.path(s) for s in g.roots),
                              deficit_or_connect=after.path(site) or gap(after, p2) < old_gap,
                              clearance=D.clear_position(point, [(e[1], e[2]) for e in elements]))
                self.emit('birth_attempt', request=request, birth_rule='B-path', site=site, a=a, b=b,
                          position=point, checks=checks, side='output')
                if not all(checks.values()): continue
                reason = self.feasible(point, es[b].phase)
                if blocked and reason is None: reason = 'cost'
                if reason: self.terminal(request, 'B-path', site, reason, attempts); return reason, None
                id = self.add(point, es[b].phase, rule='B-path', site=site, request=request, side='output')
                self.terminal(request, 'B-path', site, 'accepted', attempts, id=id); return 'accepted', id
        self.terminal(request, 'B-path', site, 'exhausted', attempts); return 'exhausted', None
    D.Rev7Medium._b_path_attempt = attempt


if BIDIR: install()

rows, _ = reused_calibration()
initial = literal_start() if START == 'ii' else None
run = Run(0, rows, episodes=50, keys=keys(START), initial=initial, backend='native', execution=Grant(), scope='fixtures')
if initial: initial.close()
m = run.medium; trace = []; orig = m.integrate
def integrate(drives):
    r = orig(drives); g = m.strong_influence(); es = m.native.elements
    o = next((e for e in es if m.native.role(e.id) == 'output'), None)
    act = [d.id for d in drives if d.strength > 0]
    trace.append(dict(t=round(m.time, 2), n=len(es), active=act, paths=[s for s in g.roots if g.path(s)],
                      dO=sorted(round(math.hypot(e.x - o.x, e.y - o.y), 3) for e in es if o and e.id != o.id)[:4],
                      xy=[[round(e.x, 3), round(e.y, 3)] for e in es] if len(trace) % 50 == 0 else None))
    return r
m.integrate = integrate
try:
    for e in range(EPISODES):
        run.episode(e, task='perceive', world_id=12000000 + e)
    events = [ev for ev in m.events if ev['rule'] != 'adaptation']
finally:
    run.close()
json.dump(dict(start=START, tag=TAG, steps=trace, events=events), gzip.open(f'kpilot_{TAG}_{START}.json.gz', 'wt'))
late = [s for s in trace if s['t'] > 640]
# E proxy: per step, fraction of active sites with a path (what E averages), then mean; also any-path.
eproxy = sum(len(set(s['paths']) & set(s['active'])) / max(1, len(s['active'])) for s in late) / max(1, len(late))
births = {r: sum(ev['rule'] == r for ev in events) for r in ('B-out', 'B-path', 'B1')}
deaths = {r: sum(ev['rule'] == r for ev in events) for r in ('D1', 'D2', 'D3', 'D4')}
print(json.dumps(dict(start=START, tag=TAG, late_any_path=sum(bool(s['paths']) for s in late) / max(1, len(late)),
                      late_active_path_fraction=eproxy, final_n=trace[-1]['n'], births=births, deaths=deaths, final_dO=trace[-1]['dO'])))
