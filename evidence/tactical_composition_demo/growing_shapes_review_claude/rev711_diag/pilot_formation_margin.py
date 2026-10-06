"""PILOT ONLY (no verdict, no fixture result, pinned files untouched): the same F5 replay as
diag_f5i_link_hold.py, but B-path's post-trial checks require every edge incident to the NEW
element to have coupling rate >= MARGIN x STRONG_LINK_RATE (formation margin). The strong-edge
definition G_s used by E, paths and everything else is unchanged (0.5 /s). The patch is applied
in this process only, by replacing rev7_design.geometric_trial.
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


def filtered(elements, g, new, k, radius, phase_scale, K):
    pos = {e[0]: (e[1], e[2]) for e in elements}
    weak = D.geometric_graph(elements, [], k, radius, strong=False, phase_scale=phase_scale, K=K)
    for i, sources in g.incoming.items():
        keep = set()
        for j in sources:
            if new in (i, j):
                r = math.hypot(pos[i][0] - pos[j][0], pos[i][1] - pos[j][1])
                if phase_scale * K * math.exp(-r * r) / len(weak.incoming[i]) < MARGIN * STRONG_LINK_RATE:
                    continue
            keep.add(j)
        g.incoming[i] = keep
    g.outgoing = {e[0]: set() for e in elements}
    for t, ss in g.incoming.items():
        for s in ss: g.outgoing[s].add(t)
    return g


def trial(elements, drives, site, a, b, position, new, *, k=8, radius=3., before=None, phase_scale=D.PHASE_SCALE, K=1.):
    before = before or D.geometric_graph(elements, drives, k, radius, strong=True, phase_scale=phase_scale, K=K)
    positions = {e[0]: (e[1], e[2]) for e in elements}
    def gap(g, positions):
        return min((math.hypot(positions[u][0]-positions[v][0], positions[u][1]-positions[v][1])
                    for u in g.forward(site) for v in g.backward()), default=math.inf)
    old_gap = gap(before, positions)
    full = elements + [(new, *position, 'element', 1., False)]
    after = filtered(full, D.geometric_graph(full, drives, k, radius, strong=True, phase_scale=phase_scale, K=K), new, k, radius, phase_scale, K)
    reached = after.forward(site); positions[new] = position
    return dict(edge_a_to_new=a in after.incoming[new], new_reached=new in reached,
                a_reached=a in reached, paths_kept=all(not before.path(s) or after.path(s) for s in before.roots),
                deficit_or_connect=after.path(site) or gap(after, positions) < old_gap,
                clearance=D.clear_position(position, [(e[1], e[2]) for e in elements]))


def main():
    identity = assert_inputs()
    D.geometric_trial = trial
    receipt = ROOT / f'evidence/tactical_composition_demo/growing_shapes/runner/rev711_pilot_margin_{START}_{MARGIN:g}_20261006'
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
    name = f'pilot_margin_{START}_{MARGIN:g}.json.gz'
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
