"""PILOT C3 (no verdict): a single B1 root group. The FIRST accepted B1 birth of the run (any site)
is replaced atomically by a six-element hexagon of driven roots (gain 1, the site's phase) at
radius r* = 0.556 around a centre 0.9 m.u. inward of that site, the seed's geometry. Feasibility
(clearance and the cap/cost after all six) is checked BEFORE any change; if infeasible, the
ordinary single birth stands. Counted as one B1 request; the group is disclosed in events.
Later B1 births are unchanged. (ii) already has its seed: the rule applies there too, so (ii) may
get a second group (disclosed). Usage: python -m ...pilot_c3_rootgroup <i|ii>"""
import sys, math
from . import pilot_common as P
D = P.D
START = sys.argv[1]


def install():
    original = D.Rev7Medium.b1
    def b1(self, blocked=False):
        added = original(self, blocked)
        if getattr(self, '_c3_done', False) or not added: return added
        id = added[0]; ev = next(e for e in reversed(self.events) if e['rule'] == 'B1' and e['ids'] == [id])
        site = ev['values']['site']; d = next(d for d in self.drives if d.id == site)
        r = math.hypot(d.x, d.y); cx, cy = d.x*(1-.9/r), d.y*(1-.9/r)
        pts = [(cx+D.R_STAR*math.cos(math.pi*j/3), cy+D.R_STAR*math.sin(math.pi*j/3)) for j in range(6)]
        es = [e for e in self.native.elements if e.id != id]
        if not all(D.clear_position(p, [(e.x, e.y) for e in es] + pts[:k]) for k, p in enumerate(pts)):
            self.emit('c3_group_refused', site=site, reason='placement'); self._c3_done = True; return added
        elements, drives = D.geometry(self.native, self.drives)
        elements = [e for e in elements if e[0] != id]
        new = max((e[0] for e in elements), default=-1) + 1
        trial = elements + [(new + k, *p, 'element', 1., False) for k, p in enumerate(pts)]
        if sum(e[3] != 'output' for e in trial) > 64:
            self.emit('c3_group_refused', site=site, reason='cap'); self._c3_done = True; return added
        g = D.geometric_graph(trial, drives, self.native.params.k, self.native.params.radius)
        n, pairs = D.budget_counts({e[0]: e[3] for e in trial}, g.incoming)
        if n + .1*pairs > 64:
            self.emit('c3_group_refused', site=site, reason='cost'); self._c3_done = True; return added
        phase = d.phase
        self.remove(id, 'C3_group_replace')
        ids = [self.add(p, phase, rule='B1', site=site, request=-1, group='C3_hexagon') for p in pts]
        self._c3_done = True
        return [x for x in added if x != id] + ids
    D.Rev7Medium.b1 = b1


if __name__ == '__main__':
    install()
    P.run(START, 'c3group')
