"""PILOT C2 (no verdict): a declared root-relative O pin. O is placed ONCE, at the first growth
check where an effective root exists, at distance 1.0 m.u. from the origin toward the lowest-id
effective root, then frozen (B-out keeps its placement and uniqueness checks; no relocation).
For (ii) the same rule replaces the literal O: the literal start is built without O, and B-out
places it by this rule. Usage: python -m ...pilot_c2_opin <i|ii>"""
import sys, math
from . import pilot_common as P
D = P.D
START = sys.argv[1]


def install():
    original = D.Rev7Medium.b_out
    def b_out(self, blocked=False):
        if self.influence().outputs: return []
        g = self.influence(); roots = sorted(set().union(*g.roots.values())) if g.roots else []
        if not roots:
            request = self.request('B-out'); self.terminal(request, 'B-out', None, 'no_root', 0); return []
        es = {e.id: e for e in self.native.elements}; r0 = es[roots[0]]; n = math.hypot(r0.x, r0.y) or 1.
        point = (r0.x / n, r0.y / n)
        request = self.request('B-out')
        if not D.clear_position(point, [(e.x, e.y) for e in self.native.elements]):
            self.terminal(request, 'B-out', None, 'placement', 1); return []
        neighbors = [e.phase for e in self.native.elements if math.hypot(e.x-point[0], e.y-point[1]) < 3]
        import numpy as np
        z = np.exp(1j*np.asarray(neighbors)).mean() if neighbors else 0j
        phase = float(np.angle(z)) if abs(z) >= .1 else float(self.growth_rng.uniform(0, 2*math.pi))
        id = self.add(point, phase, rule='B-out', role='output', request=request, pin='root_relative')
        self.terminal(request, 'B-out', None, 'accepted', 1, id=id); return [id]
    D.Rev7Medium.b_out = b_out


def seeded_without_o():
    m = D.Rev7Medium(growth_rng=P.F.generator('growth/F5/ii/intact'))
    for j in range(6): m.add((3.1+D.R_STAR*math.cos(math.pi*j/3), D.R_STAR*math.sin(math.pi*j/3)), 0., gain=1., rule='FIXTURE_INITIAL')
    m.frames.clear(); m.record(); return m


if __name__ == '__main__':
    install()
    P.run(START, 'c2opin', initial_factory=seeded_without_o)
