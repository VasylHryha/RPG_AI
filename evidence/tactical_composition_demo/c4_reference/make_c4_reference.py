"""Reference values of the accepted C4 element law (geomind/c4_model.py, frozen), for checking the S3 controller's port (DESIGN_0G.md section 4).

The script evaluates the accepted Python code on fixed states: the neighbour rule, the right-hand side (x_dot, th_dot) and one RK4 step. It covers the intact law and the two
ablations the controller uses (J=0, K=0). It only reads the frozen module. Floats are written with repr, so JSON round-trips them exactly. Cases:
  1-3  random states (N = 6, 24, 50) in the C4 working range (positions within a disk of radius 2.5, phases in [0, 2 pi), rates around 0)
  4    edge cases: an isolated element (no neighbour within radius 3), two coincident elements (r = 0, so eps applies), an exact distance tie (stable order)
  5    more than k = 8 neighbours inside the radius (only the 8 nearest count)

  python3 make_c4_reference.py c4_reference_states.json
"""
import json, sys
from dataclasses import asdict, replace

import numpy as np

sys.path.insert(0, __file__.rsplit('/evidence/', 1)[0])
from geomind import c4_model as M  # noqa: E402

DT = 0.02   # C4's registered step
VARIANTS = {'intact': M.INTACT, 'J0': replace(M.INTACT, J=0.0), 'K0': replace(M.INTACT, K=0.0)}


def random_state(seed, n):
    g = np.random.default_rng(seed)
    r, a = 2.5 * np.sqrt(g.random(n)), 2 * np.pi * g.random(n)
    return np.stack([r * np.cos(a), r * np.sin(a)], -1), 2 * np.pi * g.random(n), g.uniform(-0.03, 0.03, n)


def edge_state():
    x = np.array([[0.0, 0.0], [0.5, 0.0], [0.5, 0.0], [-0.5, 0.0], [0.0, 1.0], [10.0, 10.0]])   # 1 and 2 coincide; 1/3 tie at 0.5 from 0; 5 isolated
    return x, np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0]), np.array([0.0, 0.01, -0.01, 0.02, 0.0, 0.03])


def crowded_state():
    a = 2 * np.pi * np.arange(12) / 12
    x = np.concatenate([[[0.0, 0.0]], np.stack([np.cos(a), np.sin(a)], -1) * np.linspace(0.6, 2.8, 12)[:, None]])
    return x, np.linspace(0.0, 3.0, 13), np.zeros(13)


def case(name, x, th, om):
    out = {'name': name, 'x': x.tolist(), 'th': th.tolist(), 'omega': om.tolist(), 'dt': DT, 'variants': {}}
    for vn, p in VARIANTS.items():
        b = M.Batch(p, 1)
        X, T, O = x[None], th[None], om[None]
        idx, mask, inv = M.neighbors(X, b)
        xd, td = M.rhs(X, T, O, idx, mask, inv, b)
        x1, t1 = M.rk4_step(X, T, O, b, DT)
        out['variants'][vn] = {'params': asdict(p), 'neighbors': idx[0].tolist(), 'mask': mask[0].tolist(), 'inv_count': inv[0].tolist(),
                               'x_dot': xd[0].tolist(), 'th_dot': td[0].tolist(), 'x_after_step': x1[0].tolist(), 'th_after_step': t1[0].tolist()}
    return out


def main():
    cases = [case('random_n6', *random_state(1, 6)), case('random_n24', *random_state(2, 24)), case('random_n50', *random_state(3, 50)),
             case('edges', *edge_state()), case('crowded_over_k', *crowded_state())]
    doc = {'source': 'geomind/c4_model.py (accepted C4, frozen)', 'rule': 'neighbours: up to k=8 nearest others by distance, stable by index on ties; mask r < radius (3); '
           'inv_count = 1/max(count,1); rhs and rk4_step exactly as c4_model', 'cases': cases}
    json.dump(doc, open(sys.argv[1], 'w'), indent=1)
    print('wrote', sys.argv[1], [c['name'] for c in cases])


if __name__ == '__main__':
    main()
