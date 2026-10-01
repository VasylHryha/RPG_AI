"""Compare the reviewer's panel rerun with the R005 receipt (deterministic fields and timing endpoints)."""
import json, sys
from pathlib import Path
from statistics import median
ROOT = Path(__file__).resolve().parents[2]
a = json.loads((ROOT / "evidence/c1_r005/results.json").read_text())
b = json.loads((Path(__file__).parent / "panel/results.json").read_text())
out = {"gates_rerun": b["gates"], "hypotheses_equal": a["hypotheses"] == b["hypotheses"], "hypotheses_rerun": b["hypotheses"]["H-L"]}
diff_hash, diff_ops, diff_status = [], [], []
for x, y in zip(a["instances"], b["instances"]):
    label = f"{x['nodes']}/{x['kind']}/w{x['replicate']}"
    if x["old_artifact_hash"] != y["old_artifact_hash"]:
        diff_hash.append(label + "/before")
    for arm in ("queue", "fallback"):
        ga, gb = x["arms"][arm], y["arms"][arm]
        if ga["after_artifact_hash"] != gb["after_artifact_hash"]:
            diff_hash.append(f"{label}/{arm}")
        if ga["candidate"]["charged_operations"] != gb["candidate"]["charged_operations"] or ga["candidate"]["fallback_operations"] != gb["candidate"]["fallback_operations"]:
            diff_ops.append(f"{label}/{arm}")
        if ga["candidate"]["status"] != gb["candidate"]["status"]:
            diff_status.append(f"{label}/{arm}")
    if x["incremental_compiled"]["operations"] != y["incremental_compiled"]["operations"] or x["incremental_compiled"]["status"] != y["incremental_compiled"]["status"]:
        diff_ops.append(label + "/baseline")
out.update(artifact_hash_differences=diff_hash, operation_differences=diff_ops, status_differences=diff_status)
for name, r in (("receipt", a), ("rerun", b)):
    loc = r["endpoints"]["locality"]
    out[name + "_locality"] = {k: {kk: v[kk] for kk in ("ratio", "time_ratio", "median_apply_seconds_small", "median_apply_seconds_large", "regauged_worlds_large", "pass")} for k, v in loc.items()}
    out[name + "_speed_max_ratio"] = {k: max(v["ratios"]) for k, v in r["endpoints"]["speed"].items()}
    comp = r["endpoints"]["incremental_compiled_comparison"]
    out[name + "_baseline"] = {k: {"cand_ms": v["median_candidate_apply_seconds"] * 1e3, "base_ms": v["median_incremental_compiled_apply_seconds"] * 1e3,
                                   "time_ratio": v["median_candidate_apply_seconds"] / v["median_incremental_compiled_apply_seconds"],
                                   "cand_ops": v["median_candidate_operations"], "base_ops": v["median_incremental_compiled_operations"]} for k, v in comp.items()}
    # Per-world candidate/baseline time ratio at 2048 nodes.
    rows = [i for i in r["instances"] if i["nodes"] == 2048 and i["kind"] in ("consistent_edge", "new_node", "bridge")]
    out[name + "_per_world_ratio_2048"] = {k: sorted(round(i["arms"]["queue"]["apply_seconds"] / i["incremental_compiled"]["apply_seconds"], 1) for i in rows if i["kind"] == k) for k in ("consistent_edge", "new_node", "bridge")}
    out[name + "_regauged_by_kind"] = r["regauged_worlds_by_kind"]
    out[name + "_summary"] = {arm: {k: v for k, v in s.items() if k != "unresolved_by_kind"} for arm, s in r["summary"].items()}
    out[name + "_seconds"] = r["total_seconds"]
    out[name + "_frozen_vs_adaptive"] = r["frozen_vs_adaptive"]
    out[name + "_contradiction"] = r["endpoints"]["contradiction"]
print(json.dumps(out, indent=1))
