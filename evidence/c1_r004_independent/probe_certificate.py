"""Reviewer probes: directed counterexample searches for the R004 local certificate.

Each probe builds a C0-valid saved state, applies one R004 transaction, and then asks:
(1) what did `apply` return; (2) is the committed export accepted by the accepted
C0 validator (via IncrementalGeometry.load, which calls the C0 GeometryState.load);
(3) which non-anchor nodes violate the C0 tolerances in memory and were not certified;
(4) what the accepted C0 learner does on the same full observation.
"""
import json, math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from geomind.geometry import Constraint, GeometryState, Observation, Settings, digest
from geomind.incremental import IncrementalGeometry
from geomind.c1_cases import save_initial_state

HASH = digest({"reviewer": "c1-r004-independent"})


def violators(state):
    s = state.settings
    alpha = s.step_factor / max(1.0, state._maxdeg)
    out = []
    for i in range(len(state._names)):
        if state._is_anchor(i):
            continue
        _, _, m = state._force(i)
        scale = state._deg[i] if state._deg[i] > 0 else 1.0
        if m >= s.gradient_tolerance or m / scale >= s.gradient_tolerance or alpha * m >= s.update_tolerance:
            out.append((state._names[i], m))
    return out


def run(label, base, added_nodes, added_edges, saved=None):
    if saved is None:
        saved, _ = save_initial_state(base, HASH)
    st = IncrementalGeometry.from_saved(saved)
    trace = st.apply(added_nodes, added_edges, (), HASH, 100000, 0)
    rec = {"probe": label, "status": trace["status"], "reason": trace["reason"]}
    if trace["status"] == "PASS":
        bad = violators(st)
        rec["uncertified_violators"] = [(n, f) for n, f in bad if n not in st._last_certified]
        rec["certified_nodes"] = sorted(st._last_certified)
        try:
            IncrementalGeometry.load(st.export())
            rec["reload"] = "OK"
        except ValueError as exc:
            rec["reload"] = f"REJECTED: {exc}"
    updated = Observation(tuple(sorted(base.nodes + tuple(added_nodes))), base.edges + tuple(added_edges))
    c0 = GeometryState().learn(updated, HASH)
    rec["c0_learn_status"] = c0["status"]
    print(json.dumps(rec))
    return rec


results = []
# P1. Rigid translation by a large (finite, valid) offset. Root frame A (4 nodes); frame B
# is a chain p-q-r whose anchor is q. The bridge endpoint is p; freed anchor q is
# certified, but translated node r is not, although its residual is changed by rounding.
A = ("a0", "a1", "a2", "a3")
B = ("p", "q", "r")
edges = (Constraint("a0", "a1", (1.0, 0.0)), Constraint("a1", "a2", (1.0, 0.0)), Constraint("a2", "a3", (1.0, 0.0)),
         Constraint("p", "q", (0.1, 0.0)), Constraint("q", "r", (0.3, 0.7)))
base = Observation(tuple(sorted(A + B)), edges)
for shift in (1e6, 1e7, 1e8, 1e9, 1e10):
    results.append(run(f"P1 bridge shift {shift:g}", base, (), (Constraint("a0", "p", (shift + 0.37, 0.11)),)))

# P2. Saved state whose free-node force is just below the C0 tolerance, then a
# moderate rigid translation. The state is a valid C0 artifact (checked by load).
saved, _ = save_initial_state(base, HASH)
rec = json.loads(saved); rec.pop("checksum")
ri = rec["nodes"].index("r")
rec["coordinates"][ri][0] += 0.9999e-8          # r has one edge: force = residual
near = json.dumps(dict(rec, checksum=digest(rec)), sort_keys=True, separators=(",", ":"))
GeometryState.load(near)  # C0-valid
for shift in (1e3, 1e5, 1e6):
    results.append(run(f"P2 near-tolerance r, bridge shift {shift:g}", base, (), (Constraint("a0", "p", (shift + 0.37, 0.11)),), saved=near))

# P3. Weighted-degree overflow: a consistent duplicate of a 1e308-weight edge.
big = Observation(("a", "b", "c"), (Constraint("a", "b", (1.0, 0.0), 1e308), Constraint("b", "c", (0.0, 1.0))))
results.append(run("P3 duplicate 1e308-weight edge (degree overflow)", big, (), (Constraint("a", "b", (1.0, 0.0), 1e308),)))

Path(__file__).with_suffix(".out.jsonl").write_text("".join(json.dumps(r) + "\n" for r in results))
