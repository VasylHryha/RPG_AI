"""Read-only C4 R003 review checks: hashes, receipt arithmetic and synthetic evaluator cases.

Never runs a recorded panel, smoke, mutation probe or trajectory. The arithmetic
and scalar RHS helpers reuse the reviewer's own R002 audit implementation.
"""
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
import xml.etree.ElementTree as ET
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from geomind.c4_detect import detect
from geomind.c4_experiment import evaluate_arm, hypothesis_verdicts, model_params
from geomind.c4_model import Batch, INTACT, neighbors, rhs
from geomind.run_c4 import endpoint_coverage, implementation_gates
from tools import milestones

DIGEST = "5a95025fc65487e00cf1012044535745fe212077d9b2f0ed2683b5ad6b42b1ab"

def load(path):
    return json.loads((ROOT / path).read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def acceptance_problems(entry, report, receipt):
    """Pure checks, so inconsistent acceptance metadata can be exercised safely."""
    problems = []
    if entry.get("implementation") != "ACCEPTED" or entry.get("revision") != "R003":
        problems.append("acceptance status/revision")
    if entry.get("review") != "evidence/c4_r003_review_codex/INDEPENDENT_REVIEW.md":
        problems.append("review path")
    if entry.get("accepted_receipt") != "evidence/c4_r003/results.json":
        problems.append("receipt path")
    if entry.get("accepted_results_sha256") != DIGEST:
        problems.append("accepted receipt digest")
    if entry.get("frozen_hashes") != receipt["file_hashes"]:
        problems.append("freeze inventory")
    if not report.startswith("Verdict: **ACCEPTED**.\n"):
        problems.append("review verdict")
    if "\nReviewer family: Codex\n" not in report or DIGEST not in report:
        problems.append("review family/digest")
    return problems

def check_acceptance(r, m):
    assert r["complete"] is True and r["check_status"] == "PASS"
    assert r["implementation_status"] == "REVIEW_READY"  # Immutable pre-review receipt.
    assert r["gates"] and all(value is True for value in r["gates"].values())
    assert r["contracts"]["count"] == 26
    assert r["contracts"]["report_sha256"] == sha(ROOT / "evidence/c4_r003/contracts.xml")
    assert set(r["file_hashes"]) == {str(p.relative_to(ROOT)) for p in milestones.dependency_files("c4")}
    def finite(value):
        if isinstance(value, dict):
            return all(finite(v) for v in value.values())
        if isinstance(value, list):
            return all(finite(v) for v in value)
        return math.isfinite(value) if isinstance(value, (int, float)) else True
    assert finite(r)
    for arm in ("identical", "heterogeneous"):
        units = [u for w in r["records"][arm]["worlds"] for u in w["units"]]
        expected = {key: max((u["stability"][key] for u in units), default=None)
                    for key in m["effective_state_bounds"]}
        assert r["arms"][arm]["effective_state"]["worst"] == expected
    primary = {"H-M": "SUPPORTED_WITHIN_SCOPE", "H-C_precursor": "SUPPORTED_WITHIN_SCOPE"}
    secondary = {"H-M": "INCONCLUSIVE", "H-C_precursor": "NOT_SUPPORTED"}
    assert r["hypothesis_status"] == primary
    assert r["hypothesis_status_by_arm"] == {"identical": primary, "heterogeneous": secondary}
    status = load("STATUS.json")
    entry = status["milestones"]["c4"]
    report = Path(__file__).with_name("INDEPENDENT_REVIEW.md").read_text()
    assert not acceptance_problems(entry, report, r)
    for field, wrong in (("frozen_hashes", {}), ("accepted_results_sha256", "wrong"),
                         ("implementation", "REVIEW_READY"), ("accepted_receipt", "wrong")):
        assert acceptance_problems({**entry, field: wrong}, report, r), field
    assert acceptance_problems(entry, report.replace("**ACCEPTED**", "**CHANGES_REQUIRED**", 1), r)
    assert all(status["milestones"][key]["implementation"] == "NOT_STARTED" for key in ("c5", "c6", "c7", "c8"))
    from tools import status as status_tool
    assert status_tool.render() in (ROOT / "README.md").read_text()
    print("Acceptance, review, receipt gates, finite values, freeze inventory and README: verified; five inconsistent metadata cases rejected")

def check_identity(r, m):
    assert sha(ROOT / "evidence/c4_r003/results.json") == DIGEST
    assert r["manifest"] == m
    assert r["manifest_hash"] == sha(ROOT / "experiments/c4_manifest.json")
    registered = subprocess.check_output(["git", "show", "e796226:experiments/c4_manifest.json"], cwd=ROOT)
    assert hashlib.sha256(registered).hexdigest() == r["manifest_hash"]
    assert r["source_commit"] == "fc5c2b6b886958fa37956c4de54b4a235dc60567"
    for path, digest in r["file_hashes"].items():
        assert sha(ROOT / path) == digest, path
        committed = subprocess.check_output(["git", "show", f"{r['source_commit']}:{path}"], cwd=ROOT)
        assert hashlib.sha256(committed).hexdigest() == digest, path
    assert milestones.fingerprint("c4") == r["dependency_fingerprint"]
    pipeline = load("evidence/c4_r003/PIPELINE.json")
    assert pipeline["fingerprint"] == r["dependency_fingerprint"]
    assert [s["stage"] for s in pipeline["stages"]] == ["preflight", "tests", "smoke", "mutation", "panel"]
    archives = {"tests": "contracts.xml", "mutation": "MUTATION.json", "panel": "results.json"}
    for stage in pipeline["stages"]:
        assert stage["commit"] == r["source_commit"]
        for path, digest in stage["artifacts"].items():
            if stage["stage"] in archives:
                assert sha(ROOT / "evidence/c4_r003" / archives[stage["stage"]]) == digest
            if (ROOT / path).exists():
                assert sha(ROOT / path) == digest
            else:
                print("Local-only staging artifact unavailable:", path)
    cases = list(ET.parse(ROOT / "evidence/c4_r003/contracts.xml").getroot().iter("testcase"))
    assert len(cases) == 26
    assert not any(any(c.iter(tag)) for c in cases for tag in ("failure", "error", "skipped"))
    mutation = load("evidence/c4_r003/MUTATION.json")
    assert mutation["detected"] == mutation["total"] == 32
    assert not mutation["unexpected_survivors"] and not mutation["problems"]
    assert not any(v["timed_out"] for v in mutation["mutants"].values())
    for revision in ("c1_r006", "c2_r002"):
        for path, digest in load(f"evidence/{revision}/results.json")["file_hashes"].items():
            assert sha(ROOT / path) == digest, (revision, path)
    entropies = [m["seeds"]["development_entropy"], m["seeds"]["final_entropy"]]
    for revision, commit in (("c4_r001", "2f8438d"), ("c4_r002", "0706077")):
        for path in (ROOT / "evidence" / revision).iterdir():
            if path.is_file():
                committed = subprocess.check_output(["git", "show", f"{commit}:{path.relative_to(ROOT)}"], cwd=ROOT)
                assert path.read_bytes() == committed, str(path)
        old = load(f"evidence/{revision}/results.json")["manifest"]
        entropies.append(old["seeds"]["final_entropy"])
    assert len(set(entropies)) == 4
    old = load("evidence/c4_r002/results.json")["manifest"]
    for key in ("model", "worlds", "integration", "interventions", "effective_state_bounds", "numerical_checks", "statistics"):
        assert old[key] == m[key], key
    assert old["detector"] == {k: v for k, v in m["detector"].items() if k != "recovery_rule"}
    print("Receipt, 13 committed dependencies, pipeline, 26 contracts, 32 mutants and preserved history: verified")


def check_records(r, m):
    rng = np.random.default_rng(np.random.SeedSequence([m["seeds"]["final_entropy"], 99]))
    evaluated = {a: evaluate_arm(r["records"][a], m, rng) for a in ("identical", "heterogeneous")}
    assert evaluated == r["arms"]
    assert endpoint_coverage(evaluated, r["numerical_checks"]) == r["endpoint_coverage"]
    assert set(r["endpoint_coverage"]["evaluated"]) == set(m["endpoints"])
    assert not r["endpoint_coverage"]["not_run"]
    rng = np.random.default_rng(np.random.SeedSequence([m["seeds"]["final_entropy"], 99]))
    summaries = 0
    for arm in ("identical", "heterogeneous"):
        worlds, e = r["records"][arm]["worlds"], r["arms"][arm]
        assert [w["seed_index"] for w in worlds] == list(range(20))
        formed = sum(w["resonators"] > 0 for w in worlds)
        n, z, p = len(worlds), 1.959963984540054, formed / len(worlds)
        den = 1 + z*z/n
        center = (p + z*z/(2*n)) / den
        half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
        assert np.allclose(e["formation"]["wilson_95"], [center-half, center+half], atol=1e-15, rtol=0)
        assert e["formation"]["fraction"] == p
        valid, units = 0, 0
        for w in worlds:
            assert w["resonators"] == len(w["units"]) == len(w["resonator_effects"])
            assert w["resonators"] == sum(c["accepted"] for c in w["candidates"])
            for c in w["candidates"]:
                s, t = c["stats"], m["detector"]
                checks = {
                    "1_membership": s["size"] >= t["min_size"] and s["membership_jaccard"] >= t["membership_jaccard"],
                    "2_shape": s["shape_cv"] <= t["shape_cv"],
                    "3_mode_lock": s["lock_std"] <= t["lock_std"],
                    "4_signature": s["freq_change"] <= t["freq_tol"] and s["pattern_change"] <= t["pattern_tol"],
                    "5_recovery": s["recovery_jaccard"] >= t["recovery_jaccard"] and s["recovery_pattern_error"] <= t["pattern_tol"],
                }
                assert c["failed"] == [k for k, ok in checks.items() if not ok]
                assert c["accepted"] == all(checks.values())
            for k, mean in w["effects"].items():
                assert math.isclose(mean, sum(v[k] for v in w["resonator_effects"])/w["resonators"], abs_tol=1e-14, rel_tol=0)
            units += len(w["units"])
            valid += sum(all(u["stability"][k] <= limit for k, limit in m["effective_state_bounds"].items()) for u in w["units"])
        assert e["effective_state"]["units"] == units
        assert e["effective_state"]["units_within_bounds"] == valid
        paths = [("g_to_m/intact", e["g_to_m"]["intact"]),
                 ("g_to_m/no_geometry_to_mode", e["g_to_m"]["ablated"]),
                 ("m_to_g/intact", e["m_to_g"]["intact"]),
                 ("m_to_g/no_mode_to_geometry", e["m_to_g"]["ablated"]),
                 ("g_to_m/no_distance_weight", e["g_to_m_channels"]["no_distance_weight"]),
                 ("g_to_m/frozen_topology", e["g_to_m_channels"]["frozen_topology"])]
        for direction, labels in (("g_to_m", [str(x) for x in m["interventions"]["gm_scales"]]),
                                  ("m_to_g", m["interventions"]["mg_doses"])):
            paths.extend((f"{direction}_dose/{label}", e["dose_response"][direction]["doses"][label]) for label in labels)
            paths.append(((f"{direction}_dose/{labels[-1]}", f"{direction}_dose/{labels[0]}"),
                          e["dose_response"][direction]["highest_minus_lowest"]))
        for key, summary in paths:
            values = []
            for w in worlds:
                if not w["resonators"]:
                    continue
                def val(k):
                    return sum(v[k] for v in w["resonator_effects"]) / w["resonators"]
                values.append(val(key[0])-val(key[1]) if isinstance(key, tuple) else val(key))
            samples = rng.integers(0, len(values), size=(m["statistics"]["bootstrap_resamples"], len(values)))
            boot = np.asarray(values)[samples].sum(1) / len(values)
            assert summary["n_worlds"] == len(values)
            assert np.allclose(np.percentile(boot, [2.5, 97.5]), summary["ci"], atol=1e-14, rtol=0)
            assert math.isclose(sum(values)/len(values), summary["mean"], abs_tol=1e-14, rel_tol=0)
            summaries += 1
    assert summaries == 28
    print("16 endpoint summaries and 28 independent stored-record bootstraps: verified")

def check_rhs(m):
    rng, maximum = np.random.default_rng(482901), 0.
    for name, p in model_params(m).items():
        for _ in range(5):
            x, prior = rng.normal(size=(9, 2))*2, rng.normal(size=(9, 2))*2
            th, omega = rng.uniform(-math.pi, math.pi, 9), rng.uniform(-.5, .5, 9)
            b = Batch(p, 1)
            got = rhs(x[None], th[None], omega[None], *neighbors(x[None], b), b, neighbors(prior[None], b))
            vx, vt = np.zeros_like(x), omega.copy()
            def near(points, i):
                pairs = [(math.dist(points[i], points[j]), j) for j in range(9) if j != i]
                return [j for d, j in sorted(pairs)[:p.k] if d < p.radius]
            for i in range(9):
                motion = near(x, i)
                phase = near(prior, i) if p.frozen_phase_topology else motion
                for j in motion:
                    d = max(math.dist(x[i], x[j]), p.eps)
                    a = (p.A*(1+p.J*math.cos(th[j]-th[i]))-p.B/d) / d / len(motion)
                    for axis in range(2):
                        vx[i, axis] += (x[j, axis]-x[i, axis])*a
                for j in phase:
                    weight = math.exp(-math.dist(x[i], x[j])**2) if p.distance_weighted else 1.
                    vt[i] += p.K*weight*math.sin(th[j]-th[i]) / len(phase)
            error = max(float(abs(got[0][0]-vx).max()), float(abs(got[1][0]-vt).max()))
            assert error < 1e-13, name
            maximum = max(maximum, error)
    print("30 independent scalar RHS comparisons: verified; max error", maximum)


def check_recovery_and_verdicts(r, m):
    score_names = ("recovery_original_to_control", "recovery_original_to_kicked", "recovery_control_to_kicked")
    for arm, expected in (("identical", (39, 0)), ("heterogeneous", (44, 7))):
        candidates = [c for w in r["records"][arm]["worlds"] for c in w["candidates"]]
        deficient = 0
        for c in candidates:
            scores = [c["stats"][k] for k in score_names]
            assert all(0 <= value <= 1 for value in scores)
            assert c["stats"]["recovery_jaccard"] == min(scores)
            if min(scores[:2]) < m["detector"]["recovery_jaccard"]:
                deficient += 1
                assert not c["accepted"] and "5_recovery" in c["failed"]
            if c["accepted"]:
                assert min(scores) >= m["detector"]["recovery_jaccard"]
        assert (len(candidates), deficient) == expected
        for w in r["records"][arm]["worlds"]:
            accepted = [c for c in w["candidates"] if c["accepted"]]
            for c, unit in zip(accepted, w["units"]):
                assert all(unit["stability"][k] == c["stats"][k] for k in score_names)
        assert hypothesis_verdicts(r["arms"][arm], m["verdict_rules"]) == r["hypothesis_status_by_arm"][arm]
    print("Stored recovery minima, rejected membership changes and upper-facing scores: verified")
    whole = np.array([[0., 0.], [1., 0.], [2., 0.], [0., 1.], [1., 1.], [2., 1.]])
    split = np.array([[0., 0.], [.5, 0.], [0., .5], [10., 0.], [10.5, 0.], [10., .5]])
    cases = [(whole, whole, whole, True, (1., 1., 1.)),
             (whole, split, split, False, (.5, .5, 1.)),
             (whole, split, whole, False, (.5, 1., .5)),
             (whole, whole, split, False, (1., .5, .5))]
    grid = np.array([[float(x), float(y)] for y in range(4) for x in range(5)])
    control, kicked = grid.copy(), grid.copy()
    control[:2] = [[100., 100.], [103., 100.]]
    kicked[-2:] = [[200., 200.], [203., 200.]]
    cases.append((grid, control, kicked, False, (.9, .9, .8)))
    for initial, control, kicked, accepts, scores in cases:
        n = len(initial)
        def future(bx, bt, bw, params, dt, steps, **kw):
            assert len(bx) == 2
            return np.stack([control, kicked]), np.zeros_like(bt), None
        with patch("geomind.c4_detect.simulate", future):
            candidate = detect(np.repeat(initial[None, None], 31, axis=0), np.zeros((31, 1, n)),
                               np.zeros((1, n)), INTACT, .02, 1., m["detector"],
                               [np.random.default_rng(1)])[0][0]
        assert candidate["accepted"] == accepts
        assert tuple(candidate["stats"][k] for k in score_names) == scores
        assert candidate["failed"] == ([] if accepts else ["5_recovery"])
    print("R1: five synthetic whole/fragment/asymmetric/paired-membership cases pass; no trajectories run")
    total = 0
    for formation, gm, mg, dose, state in itertools.product(("PASS", "FAIL"), *( [("PASS", "FAIL", "INCONCLUSIVE")] * 4)):
        causal = (gm, mg, dose)
        hm = "NOT_SUPPORTED" if "FAIL" in causal else (
            "SUPPORTED_WITHIN_SCOPE" if formation == "PASS" and all(v == "PASS" for v in causal) else "INCONCLUSIVE")
        hc = "NOT_SUPPORTED" if state == "FAIL" else (
            "SUPPORTED_WITHIN_SCOPE" if hm == "SUPPORTED_WITHIN_SCOPE" and state == "PASS" else "INCONCLUSIVE")
        arm = {"formation": {"verdict": formation}, "g_to_m": {"verdict": gm},
               "m_to_g": {"verdict": mg}, "dose_response": {"verdict": dose}, "effective_state": {"verdict": state}}
        assert hypothesis_verdicts(arm, m["verdict_rules"]) == {"H-M": hm, "H-C_precursor": hc}
        total += 1
    assert total == 162
    print("R2: all 162 registered hypothesis truth-table combinations verified")
    formation = {"worlds_with_resonator": 0, "accepted_resonators": 0, "candidates": 0, "rejections_by_criterion": {}}
    records = {"worlds": [{"resonators": 0, "effects": {}, "units": []}], "ablation_formation":
               {key: dict(formation) for key in ("clump", "no_mode_to_geometry", "no_distance_weight")}}
    for candidates, accepted, expected in ((0, 0, "NOT_TESTED"), (1, 0, "PASS"), (1, 1, "FAIL")):
        records["ablation_formation"]["clump"].update(candidates=candidates, accepted_resonators=accepted)
        result = evaluate_arm(records, m, np.random.default_rng(1))
        assert result["not_a_clump"]["verdict"] == expected
    coverage = {"evaluated": dict.fromkeys(m["endpoints"]), "not_run": {}}
    records = {arm: {"worlds": [{}]} for arm in ("identical", "heterogeneous")}
    for primary, secondary, expected in (("PASS", "PASS", True), ("PASS", "NOT_TESTED", True),
                                        ("NOT_TESTED", "PASS", False), ("PASS", "FAIL", False)):
        evaluations = {"identical": {"not_a_clump": {"verdict": primary}},
                       "heterogeneous": {"not_a_clump": {"verdict": secondary}}}
        assert implementation_gates(m, records, evaluations, {"verdict": "PASS"}, coverage, 1)["detector_rejects_clumps"] == expected
    print("Clump PASS/FAIL/NOT_TESTED handling and non-vacuous primary gate verified")

if __name__ == "__main__":
    receipt, manifest = load("evidence/c4_r003/results.json"), load("experiments/c4_manifest.json")
    check_identity(receipt, manifest)
    check_records(receipt, manifest)
    check_rhs(manifest)
    check_recovery_and_verdicts(receipt, manifest)
    check_acceptance(receipt, manifest)
    print("C4 R003 review checks passed without panel, smoke, mutation or trajectory execution.")
