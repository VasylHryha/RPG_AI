"""Independent R006 N1 probe: values passing finite_number must PASS+export+load or refuse cleanly."""
import enum, json, sys, time
from fractions import Fraction
from decimal import Decimal
import numpy as np
sys.path.insert(0, ".")
from geomind.geometry import Constraint, Observation, finite_number
from geomind.incremental import IncrementalGeometry
from tests.test_c1 import save_initial_state, HASH

class IE(enum.IntEnum):
    TWO = 2
class FSub(float):
    def __repr__(self): return "FSUB"
class ISub(int):
    def __repr__(self): return "ISUB"

pair = Observation(("a", "b"), (Constraint("a", "b", (1.0, 0.0)),))
saved, _ = save_initial_state(pair, HASH)
vals = {"np.float16": np.float16(1.0), "np.float32": np.float32(1.0), "np.float64": np.float64(1.0), "np.longdouble": np.longdouble(1.0),
        "np.int8": np.int8(1), "np.int32": np.int32(1), "np.uint8": np.uint8(1), "np.int64": np.int64(1), "np.uint64": np.uint64(1),
        "np.bool_": np.bool_(True), "bool": True, "Fraction": Fraction(1, 1), "Decimal": Decimal("1.0"), "int": 1, "float": 1.0,
        "int 2**63": 2**63, "int 2**64-1": 2**64-1, "int 2**64": 2**64, "int 10**400": 10**400, "IntEnum": IE.TWO,
        "float subclass(repr override)": FSub(1.0), "int subclass(repr override)": ISub(1), "-0.0": -0.0, "5e-324": 5e-324}
rows = []
for label, v in vals.items():
    for where in ("offset", "weight", "relation"):
        state = IncrementalGeometry.from_saved(saved)
        before = state.export()
        if where == "offset":
            args = ((), (Constraint("a", "b", (v, 0.0)),), ())
        elif where == "weight":
            args = ((), (Constraint("a", "b", (1.0, 0.0), v),), ())
        else:  # new relation-backed graph: fresh nodes, relation vector holds v
            st2 = IncrementalGeometry.from_saved(save_initial_state(Observation(("p",), ()), HASH)[0])
            state, before = st2, st2.export()
            args = (("q",), (Constraint("p", "q", (v, 0.0), 1.0, "r"),), (("r", (v, 0.0)),))
        try:
            fin = bool(finite_number(v))
        except Exception as e:
            fin = f"raises {type(e).__name__}"
        try:
            tr = state.apply(*args, HASH)
            status, reason = tr["status"], tr["reason"]
        except Exception as e:
            status, reason = f"RAISED {type(e).__name__}", str(e)[:80]
        exp = load = roundtrip = "-"
        if status == "PASS":
            try:
                out = state.export(); exp = "ok"
                try:
                    re = IncrementalGeometry.load(out); load = "ok"
                    roundtrip = "eq" if re.export() == out else "DIFF"
                except Exception as e:
                    load = f"FAIL {type(e).__name__}: {str(e)[:60]}"
            except Exception as e:
                exp = f"FAIL {type(e).__name__}: {str(e)[:60]}"
        else:
            try:
                unchanged = state.export() == before
            except Exception as e:
                unchanged = f"export FAIL {e}"
            roundtrip = f"unchanged={unchanged}"
        rows.append((label, where, fin, status, (reason or "")[:50], exp, load, roundtrip))
for r in rows:
    print(" | ".join(map(str, r)))
bad = [r for r in rows if r[3] == "PASS" and (r[5] != "ok" or r[6] != "ok" or r[7] != "eq")]
bad += [r for r in rows if r[3] != "PASS" and r[7] != "unchanged=True"]
print("BLOCKING:", len(bad))
for r in bad: print("  ", r)
