"""SCRATCH (no verdict): rerun one medium-variant pilot with a full per-step topology trace, to see
where the root-to-O signal path breaks. Run from a kernel_pilot_* copy as cwd:
  python trace_run.py <i|ii> <keyset> <out.json.gz>
Records every world step: element id/x/y/role/silent, strong incoming lists (by id), drive sites,
roots, and which roots have a strong path to O."""
import sys, gzip, json, os
sys.path.insert(0, os.getcwd())
from evidence.tactical_composition_demo.growing_shapes_review_claude.rev711_diag import pilot_common as P
import evidence.tactical_composition_demo.growing_shapes.medium.rev7_design as D

start, keyset, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
FULL = []
_prev = D.Rev7Medium.integrate
def _rec(self, drives):
    r = _prev(self, drives)
    if self is P.LIVE[0]:
        nat = self.native; es = nat.elements; g = self.strong_influence()
        FULL.append(dict(t=round(self.time, 3),
            e=[[e.id, round(e.x, 4), round(e.y, 4), nat.role(e.id)[0], int(bool(e.silent))] for e in es],
            s={str(k): sorted(v) for k, v in g.incoming.items() if v},
            d=[[d.id, round(d.x, 3), round(d.y, 3), round(d.strength, 3)] for d in drives],
            roots={str(k): sorted(v) for k, v in g.roots.items() if v},
            paths=[s for s in g.roots if g.path(s)]))
    return r
D.Rev7Medium.integrate = _rec
P.run(start, f'trace_scr', keyset=keyset)
with gzip.open(out, 'wt') as f:
    json.dump(dict(kind='SCRATCH_TRACE_NO_VERDICT', start=start, keyset=keyset, steps=FULL), f)
print('trace steps', len(FULL))
