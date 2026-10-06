"""PILOT ONLY (no verdict, no fixture result, pinned files untouched): the same F5 replay as
diag_f5i_link_hold.py, but B-path alternates forward and output-side births (bidirectional growth): every B-path
decision uses G_s at MARGIN x the strong rate. E, B1's output-first predicate and everything else
keep the 0.5 /s G_s. Patched in this process only (Rev7Medium.b_path wrapper).
Usage: python -m ...pilot_formation_margin <start i|ii> <margin> <episodes>
"""
import gzip, json, math, sys
from pathlib import Path
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_identity import assert_inputs
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_execution import Execution
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_fixtures import keys, literal_start
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_evaluator import reused_calibration
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_run import Run
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_config import STRONG_LINK_RATE
import evidence.tactical_composition_demo.growing_shapes.medium.rev7_design as D

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
REVIEW = 'evidence/tactical_composition_demo/growing_shapes_review_claude/REV711_FIXTURE_READINESS.md'
START, MARGIN, EPISODES = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])


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


def main():
    identity = assert_inputs()
    install()
    receipt = ROOT / f'evidence/tactical_composition_demo/growing_shapes/runner/rev711_pilot_bidir_{START}_{MARGIN:g}_20261006'
    grant = Execution(engines_ready_reviewed=True, integration_tested_reviewed=True,
                      approval_reference='docs/decisions/0031-owner-run-approval-policy.md',
                      integration_review=str(ROOT / REVIEW), receipt_dir=str(receipt))
    grant.start('fixtures')
    rows, _ = reused_calibration()
    initial = literal_start() if START == 'ii' else None
    run = Run(0, rows, episodes=50, keys=keys(START), initial=initial, backend='native', execution=grant, scope='fixtures')
    if initial: initial.close()
    medium = run.medium; trace = []; original = medium.integrate
    def integrate(drives):
        result = original(drives)
        g = medium.strong_influence(); es = medium.native.elements
        out = [e for e in es if medium.native.role(e.id) == 'output']; o = out[0] if out else None
        active = [d.id for d in drives if d.strength > 0]
        trace.append(dict(t=round(medium.time, 3), n=len(es), active=active,
                          paths=[s for s in g.roots if g.path(s)],
                          dO=sorted(round(math.hypot(e.x-o.x, e.y-o.y), 3) for e in es if o and e.id != o.id)[:4]))
        return result
    medium.integrate = integrate
    try:
        for e in range(EPISODES):
            run.episode(e, task='perceive', world_id=12000000 + e)
        events = [ev for ev in medium.events if ev['rule'] not in ('adaptation',)]
    finally:
        run.close()
    name = f'pilot_bidir_{START}_{MARGIN:g}.json.gz'
    with gzip.open(OUT / name, 'wt') as f:
        json.dump(dict(kind='PILOT_NO_VERDICT', pin_sha256=identity['pin_sha256'], start=START, margin=MARGIN,
                       episodes=EPISODES, steps=trace, events=events), f)
    # Path-exposure proxy: fraction of steps where an active site has a strong site->O path,
    # and fraction of (step, active site) pairs with a path, in the checkpoint window t >= 640 s.
    late = [s for s in trace if s['t'] > 640]
    frac = sum(bool(s['paths']) for s in late) / max(1, len(late))
    births = {r: sum(ev['rule'] == r for ev in events) for r in ('B-out', 'B-path', 'B1')}
    print(json.dumps(dict(start=START, margin=MARGIN, late_any_path=frac,
                          all_any_path=sum(bool(s['paths']) for s in trace)/len(trace),
                          final_n=trace[-1]['n'], births=births, final_dO=trace[-1]['dO'])))


if __name__ == '__main__':
    main()
