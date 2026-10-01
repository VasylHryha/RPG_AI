"""Reviewer probe N1: numeric scalar types that pass finite_number but are not JSON-serializable.

The accepted C0 learner serializes its proposal (canonical(proposal)) before committing,
so it returns INVALID_STATE for such inputs. Does the C1 candidate commit PASS and then
fail to export (an unpersistable committed state)?
"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from geomind.geometry import Constraint, GeometryState, Observation, digest
from geomind.incremental import IncrementalGeometry
from geomind.c1_cases import save_initial_state

HASH = digest({"reviewer": "c1-r005-independent"})
base = Observation(("a", "b", "c"), (Constraint("a", "b", (1.0, 0.0)), Constraint("b", "c", (0.0, 1.0))))
saved, _ = save_initial_state(base, HASH)
out = []
cases = {
    "offset np.float32": ((), (Constraint("a", "c", (np.float32(1.0), np.float32(1.0))),), ()),
    "weight np.int64": ((), (Constraint("a", "c", (1.0, 1.0), np.int64(2)),), ()),
    "offset np.int64 new node": (("d",), (Constraint("c", "d", (np.int64(3), np.int64(0))),), ()),
    "offset np.float64 (float subclass, control)": ((), (Constraint("a", "c", (np.float64(1.0), np.float64(1.0))),), ()),
}
for label, delta in cases.items():
    st = IncrementalGeometry.from_saved(saved)
    before = st.export()
    tr = st.apply(*delta, HASH)
    rec = {"probe": "N1 " + label, "apply_status": tr["status"], "reason": tr["reason"]}
    try:
        exported = st.export()
        rec["export"] = "OK"
        IncrementalGeometry.load(exported)
        rec["reload"] = "OK"
    except Exception as exc:
        rec["export_or_reload"] = f"{type(exc).__name__}: {exc}"
    rec["state_unchanged_if_refused"] = (tr["status"] == "PASS") or (st.export() == before)
    # Accepted C0 learner on the same full observation.
    updated = Observation(tuple(sorted(set(base.nodes) | set(delta[0]))), base.edges + delta[1])
    rec["c0_learn_status"] = GeometryState().learn(updated, HASH)["status"]
    # Same input through the candidate's compatibility path.
    st2 = IncrementalGeometry.from_saved(saved)
    rec["update_path_status"] = st2.update(updated, HASH)["status"]
    print(json.dumps(rec)); out.append(rec)
Path(__file__).with_suffix(".out.jsonl").write_text("".join(json.dumps(r) + "\n" for r in out))
