"""Reviewer probe: journal rollback completeness at every failure point.

For multi-feature deltas (new nodes, 3+ frame merge, contradiction, duplicate edge,
anchor change, new relations), sweep the queue cap 0..N and fallback caps, and
deep-compare EVERY internal structure after a refusal with a deepcopy taken
before (export equality alone would hide e.g. degree-list or adjacency damage).
"""
import copy, json, sys, time
from collections import Counter
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from geomind.c1_cases import _with_relations, generate_case, save_initial_state
from geomind.geometry import Constraint, digest
from geomind.incremental import IncrementalGeometry

HASH = digest({"reviewer": "c1-r004-independent"})
FIELDS = ("_names", "_id", "_x", "_y", "_comp", "_members", "_anchor", "_next_comp", "_adj", "_src_w", "_tgt_w",
          "_es", "_et", "_edx", "_edy", "_ew", "_edges", "_deg", "_maxdeg", "_relations", "_relation_map", "_manifest_hash", "_frozen", "_ready")


def snap(st):
    return {f: copy.deepcopy(getattr(st, f)) for f in FIELDS}


def diff(a, b):
    return [f for f in FIELDS if a[f] != b[f]]


def deltas():
    case = generate_case(32, "inconsistent_edge", 55_001)
    base = case.base
    g = case.truth
    groups = sorted({n for n in base.nodes}, key=str)
    added = list((Counter(case.updated.edges) - Counter(base.edges)).elements())
    a = added[0].source
    third = case.retention_queries[0][1]
    second = next(n for n in base.nodes if n not in {p for q in case.retention_queries for p in q} and abs(g[n][0] - g[a][0]) > 15)
    vec = lambda s, t: tuple(float(v) for v in np.asarray(g[t]) - g[s])
    g["zz-1"], g["zz-2"] = (g[a][0] + 0.5, g[a][1] + 0.5), (g[third][0] - 1, g[third][1])
    # three-plus frames merged in one delta (main, second, third, two singletons), a contradiction,
    # a duplicate, consistent edges that lift a non-anchor to anchor status.
    extra = [Constraint(a, "zz-1", vec(a, "zz-1")), Constraint("zz-1", third, vec("zz-1", third)), Constraint(third, "zz-2", vec(third, "zz-2")),
             Constraint("zz-2", second, vec("zz-2", second)), Constraint(a, "zz-1", vec(a, "zz-1"))]
    edges, rel = _with_relations(base, tuple(added + extra))
    yield "mixed_merge_contradiction", case, (("zz-1", "zz-2"), edges[len(base.edges):], tuple(r for r in rel if r[0] not in dict(base.relations)))
    edges, rel = _with_relations(base, tuple(extra))
    yield "consistent_merge_only", case, (("zz-1", "zz-2"), edges[len(base.edges):], tuple(r for r in rel if r[0] not in dict(base.relations)))


out = []
started = time.perf_counter()
for label, case, delta in deltas():
    saved, _ = save_initial_state(case.base, HASH)
    ref = IncrementalGeometry.from_saved(saved)
    full = ref.apply(*delta, HASH, 100000, 5_000_000)
    stats = Counter(full_status=full["status"], full_ops=full["charged_operations"])
    budgets = sorted(set(list(range(0, 120)) + list(range(120, 3000, 37)) + [99_999]))
    for budget in budgets:
        for fb in (0, 1, 50, 500):
            st = IncrementalGeometry.from_saved(saved)
            before = snap(st)
            exported = st.export()
            tr = st.apply(*delta, HASH, budget, fb)
            stats[tr["status"]] += 1
            if tr["status"] == "PASS":
                continue
            d = diff(before, snap(st))
            if d or st.export() != exported:
                stats["ROLLBACK_DIFF:" + ",".join(d)] += 1
            # A rolled-back state must then behave exactly like a fresh fork.
            if budget % 11 == 0 and fb in (0, 500):
                again = st.apply(*delta, HASH, 100000, 5_000_000)
                if again["status"] != full["status"] or st.export() != ref.export():
                    stats["REPLAY_DIFF"] += 1
    rec = {"delta": label, **stats}
    print(json.dumps(rec)); out.append(rec)
out.append({"seconds": round(time.perf_counter() - started, 1)})
print(out[-1])
Path(__file__).with_suffix(".out.jsonl").write_text("".join(json.dumps(r) + "\n" for r in out))
