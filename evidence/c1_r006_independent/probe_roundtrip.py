"""Independent R006 optional probe: structural oddities through apply -> export -> load."""
import sys, collections
from dataclasses import dataclass
sys.path.insert(0, ".")
from geomind.geometry import Constraint, Observation
from geomind.incremental import IncrementalGeometry
from tests.test_c1 import save_initial_state, HASH

@dataclass(frozen=True)
class ExtraConstraint(Constraint):
    note: str = "x"

NT = collections.namedtuple("NT", "x y")
class S(str):
    pass

pair = Observation(("a", "b"), (Constraint("a", "b", (1.0, 0.0)),))
saved, _ = save_initial_state(pair, HASH)
cases = {
    "Constraint subclass with extra field": ((), (ExtraConstraint("a", "b", (1.0, 0.0)),), ()),
    "namedtuple offset": ((), (Constraint("a", "b", NT(1.0, 0.0)),), ()),
    "lone-surrogate node name": (("\ud800",), (Constraint("a", "\ud800", (0.5, 0.5)),), ()),
    "str-subclass node name": ((S("c"),), (Constraint("a", S("c"), (0.5, 0.5)),), ()),
    "chained 3 applies": None,
}
for label, args in cases.items():
    state = IncrementalGeometry.from_saved(saved)
    before = state.export()
    try:
        if args is None:
            for k in range(3):
                tr = state.apply((f"n{k}",), (Constraint("a", f"n{k}", (k, 1.0)),), (), HASH)
                assert tr["status"] == "PASS", tr
        else:
            tr = state.apply(*args, HASH)
        status, reason = tr["status"], tr["reason"]
    except Exception as e:
        print(label, "RAISED", type(e).__name__, e); continue
    if status != "PASS":
        print(label, status, reason, "unchanged=", state.export() == before); continue
    try:
        out = state.export()
    except Exception as e:
        print(label, "PASS but export FAIL", type(e).__name__, e); continue
    try:
        re = IncrementalGeometry.load(out)
        names = list(re._names)
        same = all(re.query(a, b) == state.query(a, b) for a in names for b in names)
        print(label, "PASS export ok load ok reexport_eq=", re.export() == out, "answers_eq=", same)
    except Exception as e:
        print(label, "PASS export ok but LOAD FAIL", type(e).__name__, str(e)[:120])
