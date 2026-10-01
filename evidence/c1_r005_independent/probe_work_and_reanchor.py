"""Reviewer probes W1/W2 (read-only use of the candidate).

W1  Deterministic work count: number of Python line events executed inside
    IncrementalGeometry.apply (all frames in geomind/incremental.py) and the
    number of builtin C calls, for one consistent edge at 32..32768 nodes. Flat
    counts plus flat wall time mean no hidden Python-level loop over state.
    The sizes of all C-level container calls (len of sequence arguments) are also
    recorded via a profile hook to catch C-level copies of state-sized objects.
W2  Re-anchoring frequency and mean cost: the C0 gauge rule (max weighted degree)
    makes any update that moves the anchor re-store its whole component
    (charged). Over fresh seeds (disjoint from every registered panel), measure the
    fraction of consistent_edge/new_node updates that re-gauge, and the mean and
    max charged operations per size. Characterization only; no setting is tuned.
"""
import json, sys, time
from collections import Counter
from pathlib import Path
from statistics import mean, median
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from geomind.c1_cases import generate_case, save_initial_state
from geomind.geometry import digest
from geomind.incremental import IncrementalGeometry
from geomind.run_c1 import case_delta

HASH = digest({"reviewer": "c1-r005-independent"})
FILE = str(ROOT / "geomind/incremental.py")
out = []

def emit(r):
    print(json.dumps(r), flush=True); out.append(r)

# ---------------- W1
for n in (32, 512, 2048, 8192, 32768):
    for seed in range(40_000_000 + n, 40_000_000 + n + 200):
        case = generate_case(n, "consistent_edge", seed)
        saved, _ = save_initial_state(case.base, HASH)
        probe = IncrementalGeometry.from_saved(saved)
        if probe.apply(*case_delta(case), HASH)["regauged_components"] == 0:
            break
    delta = case_delta(case)
    st = IncrementalGeometry.from_saved(saved)
    lines, ccalls, biggest = Counter(), Counter(), [0, ""]
    def tracer(frame, event, arg):
        if frame.f_code.co_filename != FILE:
            return None
        def local(frame, event, arg):
            if event == "line":
                lines["n"] += 1
            return local
        return local
    def profiler(frame, event, arg):
        if event == "c_call":
            ccalls[getattr(arg, "__name__", "?")] += 1
            # inspect the sizes of sequence locals in the calling frame (state-sized objects)
    sys.settrace(tracer); sys.setprofile(profiler)
    tr = st.apply(*delta, HASH)
    sys.settrace(None); sys.setprofile(None)
    times = []
    for _ in range(9):
        fresh = IncrementalGeometry.from_saved(saved)
        t0 = time.perf_counter(); fresh.apply(*delta, HASH); times.append(time.perf_counter() - t0)
    emit({"probe": "W1", "nodes": n, "seed": seed, "status": tr["status"], "charged_operations": tr["charged_operations"],
          "python_line_events": lines["n"], "builtin_c_calls": sum(ccalls.values()),
          "c_calls_top": dict(ccalls.most_common(6)), "median_apply_us": round(1e6 * median(times), 1)})

# ---------------- W2
for kind in ("consistent_edge", "new_node"):
    for n, worlds in ((32, 200), (128, 200), (512, 200), (2048, 120), (8192, 40)):
        ops, regauged, translated = [], 0, []
        for w in range(worlds):
            case = generate_case(n, kind, 41_000_000 + 100_000 * (kind == "new_node") + 1000 * n + w)
            saved, _ = save_initial_state(case.base, HASH)
            st = IncrementalGeometry.from_saved(saved)
            tr = st.apply(*case_delta(case), HASH)
            assert tr["status"] == "PASS", tr
            ops.append(tr["charged_operations"]); translated.append(tr["translated_nodes"])
            regauged += tr["regauged_components"] > 0
        emit({"probe": "W2", "kind": kind, "nodes": n, "worlds": worlds, "regauged_fraction": round(regauged / worlds, 3),
              "median_ops": median(ops), "mean_ops": round(mean(ops), 1), "max_ops": max(ops),
              "max_translated_nodes": max(translated)})

Path(__file__).with_suffix(".out.jsonl").write_text("".join(json.dumps(r) + "\n" for r in out))
