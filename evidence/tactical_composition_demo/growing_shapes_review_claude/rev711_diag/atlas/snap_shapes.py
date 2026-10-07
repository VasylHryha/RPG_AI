"""SNAPSHOT RECORDER for the visualization (no verdict): runs one F5 start and saves full element
positions, phases, roles, gains and held/strong phase-neighbour lists at chosen times.
Run from a checkout at the reviewed 7.11 identity (the 2026-10-07 run used a worktree at fd21826),
with this file placed next to pilot_common.py and pilot_c2_opin.py in rev711_diag/.
Usage: python -m ...rev711_diag.snap_shapes <i|ii> <origin|c2> <out.json>"""
import sys, json, math
from . import pilot_common as P
D = P.D
START, RULE, OUTF = sys.argv[1], sys.argv[2], sys.argv[3]
TIMES = {100.0, 220.0, 240.0, 300.0, 440.0, 460.0, 640.0, 800.0}
SNAPS = []
_orig = D.Rev7Medium.integrate
def integrate(self, drives):
    r = _orig(self, drives)
    if self is P.LIVE[0] and round(self.time, 3) in TIMES:
        es = self.native.elements
        idx, mask, _ = self.native.neighbors()
        strong = self.native.strong_neighbors()
        g = self.strong_influence()
        SNAPS.append(dict(t=round(self.time, 3),
            elements=[dict(id=e.id, x=e.x, y=e.y, phase=e.phase, role=self.native.role(e.id), gain=self.native.gain(e.id)) for e in es],
            held={es[i].id: [es[j].id for j, on in zip(idx[i], mask[i]) if on] for i in range(len(es))},
            strong={es[i].id: [es[j].id for j in strong[i]] for i in range(len(es))},
            sites=[dict(id=d.id, x=d.x, y=d.y, strength=d.strength) for d in drives],
            roots={str(k): sorted(v) for k, v in g.roots.items()},
            paths=[s for s in g.roots if g.path(s)]))
    return r
D.Rev7Medium.integrate = integrate
if RULE == 'c2':
    sys.argv = ['x', START, '1.0', '0']
    from . import pilot_c2_opin as C
    C.install()
    P.run(START, 'snap_c2', initial_factory=C.seeded_without_o)
else:
    P.run(START, 'snap_origin')
json.dump(SNAPS, open(OUTF, 'w'))
print('snaps', len(SNAPS))
