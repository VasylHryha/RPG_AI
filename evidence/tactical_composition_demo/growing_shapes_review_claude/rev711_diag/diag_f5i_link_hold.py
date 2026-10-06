"""DIAGNOSTIC ONLY (no verdict, no fixture result): replay the F5(i) empty start of the
revision-7.11 pinned code with its fixture keys for 30 episodes (480 s) and record, at every
world step, positions, phases, strong edges into O and the strong site->O path per active site.
Question: why does a strong site->O path closed at a growth check dissolve before the next check?
Run: .venv/bin/python -m evidence.tactical_composition_demo.growing_shapes_review_claude.rev711_diag.diag_f5i_link_hold
"""
import gzip, json, math
from pathlib import Path
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_identity import assert_inputs
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_execution import Execution
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_fixtures import keys
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_evaluator import reused_calibration
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_run import Run

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
REVIEW = 'evidence/tactical_composition_demo/growing_shapes_review_claude/REV711_FIXTURE_READINESS.md'
EPISODES = 30


def main():
    identity = assert_inputs()
    grant = Execution(engines_ready_reviewed=True, integration_tested_reviewed=True,
                      approval_reference='docs/decisions/0031-owner-run-approval-policy.md',
                      integration_review=str(ROOT / REVIEW), receipt_dir=str(ROOT / 'evidence/tactical_composition_demo/growing_shapes/runner/rev711_diag_link_hold_20261006'))
    grant.start('fixtures')
    rows, _ = reused_calibration()
    run = Run(0, rows, episodes=50, keys=keys('i'), backend='native', execution=grant, scope='fixtures')
    medium = run.medium
    trace = []
    original = medium.integrate

    def integrate(drives):
        result = original(drives)
        native = medium.native
        g = medium.strong_influence()
        es = native.elements
        out = [e for e in es if native.role(e.id) == 'output']
        o = out[0] if out else None
        trace.append(dict(
            t=round(medium.time, 3),
            O=None if o is None else [o.x, o.y, o.phase],
            el={e.id: [round(e.x, 4), round(e.y, 4), round(e.phase, 4)] for e in es if o is None or e.id != o.id},
            into_O=[] if o is None else sorted(g.incoming.get(o.id, ())),
            roots={s: sorted(r) for s, r in g.roots.items() if r},
            paths=[s for s in g.roots if g.path(s)],
            held_O=[] if o is None else sorted(medium.influence().incoming.get(o.id, ())),
        ))
        return result

    medium.integrate = integrate
    try:
        for e in range(EPISODES):
            run.episode(e, task='perceive', world_id=12000000 + e)
        events = list(medium.events)
    finally:
        run.close()
    with gzip.open(OUT / 'trace.json.gz', 'wt') as f:
        json.dump(dict(pin_sha256=identity['pin_sha256'], kind='DIAGNOSTIC_NO_VERDICT', episodes=EPISODES,
                       steps=trace, events=[ev for ev in events if ev['rule'] != 'adaptation']), f)
    print('steps', len(trace))


if __name__ == '__main__':
    main()
