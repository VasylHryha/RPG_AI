"""SCRATCH COPY (medium-law variant pilots; identity gate stubbed because the native law is deliberately changed).
Shared PILOT harness (no verdict), revision after Codex R2-F1: the per-step recorder is a
class-level wrapper that records ONLY for the live medium (clones made by qualification/recovery
call the original integrate on their own state and record nothing). Includes a synthetic
clone-isolation check and an exact step-count check (160 world steps per training episode)."""
import gzip, json, math
from pathlib import Path
from evidence.tactical_composition_demo.growing_shapes.runner import rev7_fixtures as F
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_evaluator import reused_calibration
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_run import Run
import evidence.tactical_composition_demo.growing_shapes.medium.rev7_design as D

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
REVIEW = 'evidence/tactical_composition_demo/growing_shapes_review_claude/REV711_FIXTURE_READINESS.md'
LIVE = [None]
import os
ASSAY = os.environ.get('PILOT_ASSAY') == '1'
TRACE = []
_ORIG = D.Rev7Medium.integrate


class Execution:
    def __init__(self, **kw): pass
    def require(self, scope): pass
    def start(self, scope): return {}
    def snapshot(self, scope): return {'scratch': True, 'scope': scope}


def assert_inputs():
    import hashlib
    from evidence.tactical_composition_demo.growing_shapes.medium import rev7_native as N
    return {'pin_sha256': 'SCRATCH:' + hashlib.sha256(N.IMAGE.read_bytes()).hexdigest()}


def _integrate(self, drives):
    result = _ORIG(self, drives)
    if self is LIVE[0]:
        g = self.strong_influence(); es = self.native.elements
        o = next((e for e in es if self.native.role(e.id) == 'output'), None)
        TRACE.append(dict(t=round(self.time, 3), n=len(es), active=[d.id for d in drives if d.strength > 0],
                          paths=[s for s in g.roots if g.path(s)],
                          O=None if o is None else [round(o.x, 4), round(o.y, 4)],
                          dO=sorted(round(math.hypot(e.x-o.x, e.y-o.y), 3) for e in es if o and e.id != o.id)[:4]))
    return result


D.Rev7Medium.integrate = _integrate


def clone_isolation_check(medium):
    """A clone advanced by one world step must leave the live clock, step index and sink unchanged."""
    before = (medium.time, medium.step_index, len(TRACE))
    c = medium.clone(events=False)
    try:
        c.integrate([])
    finally:
        if hasattr(c, 'close'): c.close()
    assert (medium.time, medium.step_index, len(TRACE)) == before, 'clone advanced the live run'


def run(start, tag, episodes=50, initial_factory=None, keyset=0):
    """keyset 0 = the F5 fixture keys and worlds; keyset k>0 = alternative pilot keys (suffix /altK on every
    growth/recovery/medium key) and training worlds 13000000 + 100000*k + e, a range no registered fixture or
    development schedule uses (F5 12000000+, F8 12100000+, development 11000000+); robustness only, no verdict."""
    if ASSAY and not tag.endswith('_assay'): tag = tag + '_assay'
    if keyset: tag = f'{tag}_alt{keyset}'
    identity = assert_inputs()
    receipt = OUT / f'receipt_{tag}_{start}'
    grant = Execution(engines_ready_reviewed=True, integration_tested_reviewed=True,
                      approval_reference='docs/decisions/0031-owner-run-approval-policy.md',
                      integration_review=str(ROOT / REVIEW), receipt_dir=str(receipt))
    grant.start('fixtures')
    rows, _ = reused_calibration()
    initial = (initial_factory or F.literal_start)() if start == 'ii' else None
    keys = {k: (v + f'/alt{keyset}' if keyset else v) for k, v in F.keys(start).items()}
    r = Run(0, rows, episodes=50, keys=keys, initial=initial, backend='native', execution=grant, scope='fixtures')
    if initial: initial.close()
    LIVE[0] = r.medium
    clone_isolation_check(r.medium)
    checkpoints = {}
    try:
        for e in range(episodes):
            r.episode(e, task='perceive', world_id=(12000000 + e) if keyset == 0 else (13000000 + 100000*keyset + e))
            assert len(TRACE) == 160 * (e + 1), f'step count {len(TRACE)} after episode {e}'
            if ASSAY and e + 1 in F.CHECKPOINTS: checkpoints[e + 1] = r.medium.clone(events=False)
        events = [ev for ev in r.medium.events if ev['rule'] != 'adaptation']
    finally:
        r.close()
    assay = None
    if ASSAY:
        # The F5 measurement exactly as Harness.F5 computes it (rev7_fixtures.py), on this pilot's checkpoints.
        import numpy as np
        from evidence.tactical_composition_demo.growing_shapes.medium.design_0h import wrap
        ev_ = F.Evaluator(rows, backend='native', execution=grant, scope='fixtures')
        A = []; B = []; E = []
        for cp in F.CHECKPOINTS:
            m = checkpoints[cp]; value = F.template(m.native, [x.id for x in m.native.elements], m.time, h=m.h)
            for recipient, donor in F.F5_PAIRS:
                own = ev_.episode(value, 'perceive', recipient)
                other = ev_.episode(value, 'perceive', recipient, mode='donor', donor=donor)
                lesion = ev_.episode(value, 'perceive', recipient, mode='output_channel')
                # Harness.F5's guard (Codex 7.12 N3): every assay stream has exactly 160 decisions.
                if any(len(x['decisions']) != 160 for x in (own, other, lesion)): raise ValueError('missing F5 decision record')
                absent = not any(row[5] == 'output' for row in value['members'])
                A.append(0. if absent else float(np.mean([abs(float(wrap(a['angle']-b['angle']))) for a, b in zip(own['decisions'], other['decisions'])])))
                B.append(0. if absent else float(np.mean([abs(float(wrap(a['angle']-b['angle']))) for a, b in zip(own['decisions'], lesion['decisions'])])))
                E.append(np.mean([d['paths'] for d in own['decisions']], axis=0).tolist())
        assay = dict(A=float(np.mean(A)), B=float(np.mean(B)), E=np.mean(E, axis=0).tolist(),
                     gate_shape='A>=0.3 and B>=0.3 and max(E)>=0.5 (descriptive here; no verdict)')
        for m in checkpoints.values():
            if hasattr(m, 'close'): m.close()
    st = TRACE
    with gzip.open(OUT / f'pilot_{tag}_{start}.json.gz', 'wt') as f:
        json.dump(dict(kind='PILOT_NO_VERDICT', instrumentation='class-level live-only recorder (R2-F1 fix)', assay=assay, keyset=keyset,
                       pin_sha256=identity['pin_sha256'], start=start, tag=tag, episodes=episodes, steps=st, events=events), f)
    late = [s for s in st if s['t'] > 640]
    conn = sum(len(set(s['paths']) & set(s['active'])) / max(1, len(s['active'])) for s in late) / max(1, len(late))
    best = cur = 0; start_t = None; span = None
    for s in st:
        if s['paths']:
            if cur == 0: start_t = s['t']
            cur += 1
            if cur > best: best = cur; span = (start_t, s['t'])
        else: cur = 0
    births = {k: sum(ev['rule'] == k for ev in events) for k in ('B-out', 'B-path', 'B1')}
    print(json.dumps(dict(start=start, tag=tag, steps=len(st), last_t=st[-1]['t'], late_connectivity=round(conn, 3),
                          present=sum(bool(s['paths']) for s in st), longest_any_site=[span, best],
                          final_n=st[-1]['n'], O=st[-1]['O'], births=births, final_dO=st[-1]['dO'], keyset=keyset, assay=assay)))
