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
