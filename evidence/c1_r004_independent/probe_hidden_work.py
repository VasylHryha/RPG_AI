"""Reviewer probe: uncharged O(R) work in IncrementalGeometry._validate_delta.

`catalog = dict(self._relation_map)` copies every stored relation on each apply.
The generator makes one relation per edge, so R ~ E. Charged operations stay flat
while wall time of the validation phase grows with R. A non-copying variant is
monkeypatched here ONLY for comparison; repository source is not modified.
"""
import json, sys, time
from pathlib import Path
from statistics import median
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from geomind.c1_cases import generate_case, save_initial_state
from geomind.geometry import digest, finite_number, Constraint
from geomind.incremental import IncrementalGeometry
from geomind.run_c1 import case_delta

HASH = digest({"reviewer": "c1-r004-independent"})
original = IncrementalGeometry._validate_delta


def no_copy(self, added_nodes, added_edges, added_relations):
    # Same checks; the catalog is an overlay of the delta instead of a full copy.
    if not all(isinstance(c, tuple) for c in (added_nodes, added_edges, added_relations)):
        raise ValueError
    if any(not isinstance(n, str) or not n or n in self._id for n in added_nodes) or len(set(added_nodes)) != len(added_nodes):
        raise ValueError
    extra = {}
    for name, vector in added_relations:
        if name in self._relation_map or name in extra:
            raise ValueError
        extra[name] = vector
    lookup = lambda k: extra[k] if k in extra else self._relation_map.get(k)
    for edge in added_edges:
        if edge.relation_id is not None and lookup(edge.relation_id) != edge.offset:
            raise ValueError


rows = []
for n in (32, 512, 2048, 8192, 32768):
    case = generate_case(n, "consistent_edge", 31_000_000 + n)
    saved, _ = save_initial_state(case.base, HASH)
    delta = case_delta(case)
    for label, fn in (("as_shipped", original), ("no_copy_variant", no_copy)):
        IncrementalGeometry._validate_delta = fn
        times, vtimes, ops = [], [], []
        for _ in range(7):
            st = IncrementalGeometry.from_saved(saved)
            tr = st.apply(*delta, HASH, 100000, 0)
            assert tr["status"] == "PASS", tr
            times.append(tr["total_seconds"]); vtimes.append(tr["validation_seconds"]); ops.append(tr["charged_operations"])
        rows.append({"nodes": n, "relations": len(case.updated.relations), "variant": label, "charged_operations": ops[0],
                     "median_apply_us": round(1e6 * median(times), 1), "median_validation_us": round(1e6 * median(vtimes), 1)})
        print(json.dumps(rows[-1]), flush=True)
IncrementalGeometry._validate_delta = original
Path(__file__).with_suffix(".out.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
