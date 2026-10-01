"""Reviewer probe: (a) live in-memory degree/anchor bit-exactness vs C0 _prepare over
random chains with non-associative weights, including isolated new nodes and
duplicates, checked after every PASS and every refusal without reloading;
(b) cost-unit check for the fallback-vs-reference comparison."""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from geomind.c1_cases import generate_case, save_initial_state
from geomind.c1_reference import SparseLeastSquares
from geomind.geometry import Constraint, Observation, _prepare, digest
from geomind.incremental import IncrementalGeometry

HASH = digest({"reviewer": "c1-r004-independent"})
rng = np.random.default_rng(777)
W = [0.1, 0.2, 0.3, 1 / 3, 0.7, 1e-3, 2.5, 1.0]
checks = mism = anchor_mism = 0
for trial in range(200):
    nodes = tuple(f"n{trial:03d}{k}" for k in range(int(rng.integers(2, 8))))
    pos = {n: rng.normal(size=2) for n in nodes}
    edges = tuple(Constraint(nodes[k - 1], nodes[k], tuple(float(v) for v in pos[nodes[k]] - pos[nodes[k - 1]]), float(rng.choice(W))) for k in range(1, len(nodes)) if rng.random() < 0.8)
    st = IncrementalGeometry.from_saved(save_initial_state(Observation(nodes, edges), HASH)[0])
    for stage in range(5):
        fresh = tuple(f"m{trial:03d}{stage}{k}" for k in range(int(rng.integers(0, 3))))  # some stay isolated
        for n in fresh:
            pos[n] = rng.normal(size=2)
        universe = list(st._names) + list(fresh)
        added = tuple(Constraint(*(lambda s, t: (s, t, tuple(float(v) for v in pos[t] - pos[s] + (rng.normal(scale=0.2, size=2) if rng.random() < 0.3 else 0)), float(rng.choice(W))))(*[str(v) for v in rng.choice(universe, 2, replace=False)])) for _ in range(int(rng.integers(0, 4))))
        if added and rng.random() < 0.3:
            added = added + (added[0],)
        st.apply(fresh, added, (), HASH, int(rng.choice([50, 20000])), int(rng.choice([0, 5_000_000])))
        names, _, _, _, _, _, _, degree, components, anchors = _prepare(st.observation())
        checks += 1
        mism += any(st._deg[st._id[n]] != float(d) for n, d in zip(names, degree))
        live = sorted(st._names[st._anchor[c]] for c in set(st._comp))
        anchor_mism += live != sorted(names[a] for a in anchors)
print(json.dumps({"degree_checks": checks, "degree_bit_mismatches": mism, "anchor_mismatches": anchor_mism}))

# (b) unit check: reference edge_visits are counted per axis (two scalar CGs) over ALL
# components; fallback counts each edge once for both axes over affected components.
case = generate_case(512, "inconsistent_edge", 10_002_000)
ref = SparseLeastSquares(case.updated, 1e-11, 20000)
group0 = set(n for n in case.updated.nodes if n not in {p for q in case.retention_queries for p in q})
print(json.dumps({"reference_iterations_per_axis": ref.iterations, "reference_edge_visits": ref.edge_visits,
                  "edges_total": len(case.updated.edges), "visits_div_edges": ref.edge_visits / len(case.updated.edges)}))
