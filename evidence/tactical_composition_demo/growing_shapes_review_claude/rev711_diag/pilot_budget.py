"""PILOT ONLY (no verdict, no fixture result, pinned files untouched): the same F5 replay as
diag_f5i_link_hold.py, but the growth budget (cap and cost) is MARGIN instead of 64; NOTE: D3 is patched through a scaled cost(): every B-path
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
    """Raise the growth budget: cap and cost limits 64 -> MARGIN (used here as the budget).
    D3 (cost > 64) is patched the same way if it reads a literal."""
    import inspect
    src=inspect.getsource(D.Rev7Medium.feasible)
    def feasible(self,position,phase):
        if not D.clear_position(position,[(e.x,e.y) for e in self.native.elements]):return 'placement'
        elements,drives=D.geometry(self.native,self.drives)
        if sum(e[3]!='output' for e in elements)+1>MARGIN:return 'cap'
        new=max((e[0] for e in elements),default=-1)+1
        g=D.geometric_graph(elements+[(new,*position,'element',1.,False)],drives,
            self.native.params.k,self.native.params.radius)
        n,pairs=D.budget_counts({e[0]:e[3] for e in elements}|{new:'element'},g.incoming)
        return 'cost' if n+.1*pairs>MARGIN else None
    D.Rev7Medium.feasible=feasible
    orig_cost=D.Rev7Medium.cost
    # D3 compares cost()>64: scale so D3 fires only above MARGIN (reported cost fields are scaled too)
    D.Rev7Medium.cost=lambda self,*a,**k: orig_cost(self,*a,**k)*64/MARGIN


def main():
    identity = assert_inputs()
    install()
    receipt = ROOT / f'evidence/tactical_composition_demo/growing_shapes/runner/rev711_pilot_budget_{START}_{MARGIN:g}_20261006'
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
    name = f'pilot_budget_{START}_{MARGIN:g}.json.gz'
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
