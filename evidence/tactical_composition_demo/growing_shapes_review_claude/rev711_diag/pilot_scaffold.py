"""PILOT ONLY (no verdict, no fixture result, pinned files untouched): the same F5 replay as
diag_f5i_link_hold.py, but one property of the seeded hexagon changed (ring position, random phases, or zero gain): every B-path
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


VARIANT = {1.0: 'ring', 2.0: 'randphase', 3.0: 'nogain'}[MARGIN]


def install():
    """Scaffold pilots on the seeded start (ii), changing one property of its hexagon:
    ring: hexagon centre moved from (3.1, 0) to (4.0, 0), i.e. onto the sensor ring at site 0;
    randphase: hexagon phases drawn uniformly from a fixed pilot RNG (seed 20261007) instead of 0;
    nogain: hexagon elements created with gain 0 (not roots) instead of 1.
    O stays at (-0.5, 0) with phase 0 and gain 1 as in the fixture."""
    import evidence.tactical_composition_demo.growing_shapes.runner.rev7_fixtures as F
    import numpy as np
    def literal_start():
        m = D.Rev7Medium(growth_rng=F.generator('growth/F5/ii/intact'))
        cx = 4.0 if VARIANT == 'ring' else 3.1
        ph = np.random.default_rng(20261007).uniform(0, 2*math.pi, 6) if VARIANT == 'randphase' else [0.]*6
        g = 0. if VARIANT == 'nogain' else 1.
        for j in range(6): m.add((cx+D.R_STAR*math.cos(math.pi*j/3), D.R_STAR*math.sin(math.pi*j/3)), float(ph[j]), gain=g, rule='FIXTURE_INITIAL')
        m.add((-.5, 0), 0., gain=1., rule='FIXTURE_INITIAL', role='output')
        m.frames.clear(); m.record(); return m
    globals()['literal_start'] = literal_start


def main():
    identity = assert_inputs()
    install()
    receipt = ROOT / f'evidence/tactical_composition_demo/growing_shapes/runner/rev711_pilot_scaffold_{START}_{MARGIN:g}_20261006'
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
    name = f'pilot_scaffold_{START}_{MARGIN:g}.json.gz'
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
