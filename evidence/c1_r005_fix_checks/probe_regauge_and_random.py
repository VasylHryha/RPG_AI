"""Reviewer probes, part 2.

P4: anchor reassignment without any translation. The export re-gauges the whole
    component to the new anchor; an uncertified near-tolerance node can then fail
    the accepted C0 validator although its in-memory force is bit-identical.
P5: randomized chains that use ONLY candidate-produced states (no hand-edited
    artifacts): queue/fallback-resolved contradictions followed by further additive
    transactions in memory. Every PASS export must pass the accepted C0 validator and
    match LeastSquares; in-memory answers must equal export->load answers exactly.
"""
import json, sys, time
from collections import Counter
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from geomind.geometry import Constraint, GeometryState, Observation, digest
from geomind.incremental import IncrementalGeometry
from geomind.c1_cases import save_initial_state
from geomind.references import LeastSquares

SCALE = tuple(float(v) for v in (sys.argv[2].split(",") if len(sys.argv) > 2 else ("0", "4")))
HASH = digest({"reviewer": "c1-r004-independent"})
log = []

def emit(rec):
    print(json.dumps(rec)); log.append(rec)

# ---------------- P4
for far, gap in ((1e3, 1e-14), (1e5, 1e-12), (1e5, 1e-13), (1e6, 1e-11)):
    base = Observation(("p", "q", "r", "z"), (Constraint("q", "p", (far, 0.0)), Constraint("q", "r", (0.3, 0.7)), Constraint("q", "z", (0.0, -1.0))))
    saved, _ = save_initial_state(base, HASH)  # anchor q (degree 3)
    rec = json.loads(saved); rec.pop("checksum")
    ri = rec["nodes"].index("r")
    rec["coordinates"][ri][0] = 0.3 + (1e-8 - gap)  # q is the anchor at 0
    near = json.dumps(dict(rec, checksum=digest(rec)), sort_keys=True, separators=(",", ":"))
    GeometryState.load(near)
    st = IncrementalGeometry.from_saved(near)
    # Three new leaves on p raise p's degree to 4 > 3: p becomes the anchor; nothing translates
    # in the old frame (the new singletons are the frames that move).
    adds = tuple(Constraint("p", f"s{k}", (float(k), 1.0)) for k in range(3))
    tr = st.apply(("s0", "s1", "s2"), adds, (), HASH)
    out = {"probe": f"P4 re-anchor far={far:g} gap={gap:g}", "status": tr["status"], "translated_nodes": tr["translated_nodes"],
           "r_certified": "r" in st._last_certified, "new_anchor": json.loads(st.export())["anchors"]}
    try:
        IncrementalGeometry.load(st.export()); out["reload"] = "OK"
    except ValueError as exc:
        out["reload"] = f"REJECTED: {exc}"
    emit(out)

# ---------------- P5
def diagnose(st, exported, tr, before):
    from geomind.geometry import _gradient, _prepare
    rec = json.loads(exported)
    obs = Observation(tuple(rec["nodes"]), tuple(Constraint(e["source"], e["target"], tuple(e["offset"]), e["weight"], e["relation_id"]) for e in rec["edges"]))
    nodes, _, _, src, tgt, off, w, deg, comps, anchors = _prepare(obs)
    _, _, g = _gradient(np.array(rec["coordinates"]).reshape(-1, 2), src, tgt, off, w, anchors)
    norm = np.hypot(g[:, 0], g[:, 1])
    tol = st.settings.gradient_tolerance
    bad = [nodes[i] for i in range(len(nodes)) if norm[i] >= tol or norm[i] / (deg[i] if deg[i] > 0 else 1) >= tol]
    old_anchors = set(json.loads(before)["anchors"]) and {json.loads(before)["nodes"][a] for a in json.loads(before)["anchors"]}
    new_anchors = {nodes[a] for a in anchors}
    kinds = []
    for n in bad:
        i = st._id[n]
        _, _, m = st._force(i)
        mem = "mem_over" if m >= tol else "mem_under"
        cert = "certified" if n in st._last_certified else "uncertified"
        kinds.append(f"{cert}/{mem}")
    regauged = "anchor_changed" if new_anchors - old_anchors else "anchors_same"
    return f"{regauged};translated={tr['translated_nodes']>0};relaxed={tr['node_updates']>0};" + ",".join(sorted(set(kinds)))


def random_chain(rng, trial, budget=20000):
    stats = Counter()
    scale = float(10 ** rng.uniform(*SCALE))
    count = int(rng.integers(3, 9))
    nodes = tuple(f"n{trial:03d}{k}" for k in range(count))
    pos = {n: rng.normal(scale=scale, size=2) for n in nodes}
    edges = []
    for k in range(1, count):
        if rng.random() < 0.75:
            j = int(rng.integers(0, k))
            edges.append(Constraint(nodes[j], nodes[k], tuple(float(v) for v in pos[nodes[k]] - pos[nodes[j]]), float(rng.choice([1.0, rng.uniform(0.25, 3), 1e-3]))))
    try:
        saved, _ = save_initial_state(Observation(nodes, tuple(edges)), HASH)
    except ValueError:  # evaluator's compiled initializer needs residual <= 1e-10
        return Counter({"init_skipped": 1}), True
    st = IncrementalGeometry.from_saved(saved)
    for stage in range(6):
        fresh = tuple(f"m{trial:03d}{stage}{k}" for k in range(int(rng.integers(0, 3))))
        for n in fresh:
            pos[n] = rng.normal(scale=scale, size=2)
        universe = list(st._names) + list(fresh)
        added = []
        for _ in range(int(rng.integers(1, 5))):
            s, t = (str(v) for v in rng.choice(universe, 2, replace=False))
            noise = rng.normal(scale=0.3, size=2) if rng.random() < 0.35 else np.zeros(2)
            added.append(Constraint(s, t, tuple(float(v) for v in pos[t] - pos[s] + noise), float(rng.choice([1.0, rng.uniform(0.25, 3)]))))
        if rng.random() < 0.15 and added:
            added.append(added[0])  # duplicate within one delta
        before = st.export()
        tr = st.apply(fresh, tuple(added), (), HASH, budget, 5_000_000 if rng.random() < 0.5 else 0)
        stats[tr["status"]] += 1
        if tr["status"] != "PASS":
            if st.export() != before:
                stats["ROLLBACK_MISMATCH"] += 1
            continue
        stats["relaxed" if tr["node_updates"] else "no_relax"] += 1
        stats["fallback"] += tr["fallbacks"]
        exported = st.export()
        obs = st.observation()
        try:
            loaded = IncrementalGeometry.load(exported)
        except ValueError as exc:
            stats["RELOAD_REJECTED"] += 1
            stats["diag:" + diagnose(st, exported, tr, before)] += 1
            stats["reload_reason:" + str(exc)[-50:]] += 1
            return stats, False
        pairs = [(a, b) for a in obs.nodes for b in obs.nodes]
        if any(loaded.query(*p) != st.query(*p) for p in pairs):
            stats["QUERY_EXPORT_MISMATCH"] += 1
        ref = LeastSquares(obs)
        worst = 0.0
        for p in pairs:
            a, b = st.query(*p), ref.query(*p)
            if a.status != b.status:
                stats["STATUS_MISMATCH"] += 1
            elif a.status == "OK":
                worst = max(worst, float(np.hypot(*(np.subtract(a.displacement, b.displacement)))))
        if worst > 1e-5:
            stats["ERROR_GT_1e-5"] += 1
        stats["max_err_e-9"] = max(stats["max_err_e-9"], int(worst * 1e9))
    return stats, True

rng = np.random.default_rng(424242)
started = time.perf_counter()
total = Counter()
for trial in range(int(sys.argv[1]) if len(sys.argv) > 1 else 150):
    stats, ok = random_chain(rng, trial)
    for k, v in stats.items():
        total[k] = max(total[k], v) if k == "max_err_e-9" else total[k] + v
total["seconds"] = round(time.perf_counter() - started, 1)
emit({"probe": f"P5 randomized candidate-only chains, scale 10^{SCALE}", **total})
Path(__file__).with_name(Path(__file__).stem + f"_scale{SCALE[0]:g}-{SCALE[1]:g}.out.jsonl").write_text("".join(json.dumps(r) + "\n" for r in log))
