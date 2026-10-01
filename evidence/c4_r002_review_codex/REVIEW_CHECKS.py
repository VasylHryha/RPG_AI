"""Read-only self-audit of the existing Codex review; never integrates a trajectory.

A successful exit confirms both evidence consistency and reproduction of known
defects. It does not certify C4. No gate checks are disabled or stamps written.
"""

import hashlib
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
from geomind.c4_detect import components, detect, jaccard
from geomind.c4_experiment import evaluate_arm, hypothesis_verdicts, model_params
from geomind.c4_model import Batch, INTACT, neighbors, rhs
from geomind.run_c4 import endpoint_coverage
from tools import milestones


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads((ROOT / path).read_text())


def check_identity(r, m):
    digest = sha(ROOT / "evidence/c4_r002/results.json")
    assert digest == "24a583ecc83a7efbfec3ea90966d99fa95c67937ae75c65e87d12559c1fb66d7"
    report = Path(__file__).with_name("INDEPENDENT_REVIEW.md").read_text()
    assert report.splitlines()[0] == "Verdict: **CHANGES_REQUIRED**."
    assert "Reviewer family: Codex" in report and digest in report
    assert r["manifest"] == m
    assert r["manifest_hash"] == sha(ROOT / "experiments/c4_manifest.json")
    for name, digest in r["file_hashes"].items():
        committed = subprocess.check_output(
            ["git", "show", f"{r['source_commit']}:{name}"], cwd=ROOT
        )
        assert sha(ROOT / name) == digest == hashlib.sha256(committed).hexdigest(), name
    assert milestones.fingerprint("c4") == r["dependency_fingerprint"]
    pipeline = load("evidence/c4_r002/PIPELINE.json")
    assert pipeline["fingerprint"] == r["dependency_fingerprint"]
    assert [s["stage"] for s in pipeline["stages"]] == [
        "preflight", "tests", "smoke", "mutation", "panel"
    ]
    archived = {"tests": "contracts.xml", "mutation": "MUTATION.json", "panel": "results.json"}
    for stage in pipeline["stages"]:
        assert stage["commit"] == r["source_commit"]
        for name, digest in stage["artifacts"].items():
            if stage["stage"] in archived:
                assert sha(ROOT / "evidence/c4_r002" / archived[stage["stage"]]) == digest
            if (ROOT / name).exists():
                assert sha(ROOT / name) == digest
            else:
                print("Local staging artifact unavailable (not archived):", name)
    cases = list(ET.parse(ROOT / "evidence/c4_r002/contracts.xml").getroot().iter("testcase"))
    assert len(cases) == 24
    assert not any(any(c.iter(tag)) for c in cases for tag in ("failure", "error", "skipped"))
    mutation = load("evidence/c4_r002/MUTATION.json")
    assert mutation["detected"] == mutation["total"] == 27
    assert not mutation["unexpected_survivors"] and not mutation["problems"]
    assert not any(v["timed_out"] for v in mutation["mutants"].values())
    for revision in ("c1_r006", "c2_r002"):
        for name, digest in load(f"evidence/{revision}/results.json")["file_hashes"].items():
            assert sha(ROOT / name) == digest, (revision, name)
    old = load("evidence/c4_r001/results.json")["manifest"]
    assert len({old["seeds"]["final_entropy"], m["seeds"]["final_entropy"],
                m["seeds"]["development_entropy"]}) == 3
    for key in ("model", "worlds", "integration", "detector", "effective_state_bounds"):
        assert old[key] == m[key], key
    print("Receipt, committed dependencies, pipeline, frozen files and seed registration: verified")


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


def check_findings(r, m):
    x = np.array([[0., 0.], [1., 0.], [2., 0.], [0., 1.], [1., 1.], [2., 1.]])
    split = np.array([[0., 0.], [.5, 0.], [0., .5], [10., 0.], [10.5, 0.], [10., .5]])
    xs, ths = np.repeat(x[None, None], 31, axis=0), np.zeros((31, 1, 6))
    for end, retained in ((x, 1.), (split, .5)):
        def future(bx, bt, bw, params, dt, steps, **kw):
            return np.repeat(end[None], len(bx), axis=0), np.zeros_like(bt), None
        with patch("geomind.c4_detect.simulate", future):
            c = detect(xs, ths, np.zeros((1, 6)), INTACT, .02, 1., m["detector"], [np.random.default_rng(1)])[0][0]
        labels = components(end, m["detector"]["link_factor"], np.ones((6, 6), bool))
        actual = max(jaccard(range(6), np.flatnonzero(labels == k)) for k in np.unique(labels))
        assert actual == retained
        assert c["accepted"] and c["stats"]["recovery_jaccard"] == 1.
    print("R1 reproduced: common fragmentation passes; intact-membership positive control also passes")
    assert "NOT_SUPPORTED if any of these FAILs" in m["verdict_rules"]["H-M"]
    e = r["arms"]["heterogeneous"]
    assert e["formation"]["verdict"] == "FAIL" and e["formation"]["fraction"] == .2
    assert hypothesis_verdicts(e, m["verdict_rules"])["H-M"] == "INCONCLUSIVE"
    synthetic = {"formation": {"fraction": .5}, "g_to_m": {"verdict": "PASS"},
                 "m_to_g": {"verdict": "PASS"}, "dose_response": {"verdict": "PASS"},
                 "effective_state": {"verdict": "PASS"}}
    assert hypothesis_verdicts(synthetic, m["verdict_rules"])["H-M"] == "INCONCLUSIVE"
    old = load("evidence/c4_r001/results.json")["manifest"]
    assert "either causality endpoint FAILs" in old["verdict_rules"]["H-M"]
    assert "formation and effective-state rules" in (ROOT / "docs/decisions/0002-c4-r002-supersedes-r001.md").read_text()
    print("R2 reproduced: explicit manifest failure rule differs from code/test and unchanged-rule decision")


if __name__ == "__main__":
    receipt, manifest = load("evidence/c4_r002/results.json"), load("experiments/c4_manifest.json")
    check_identity(receipt, manifest)
    check_records(receipt, manifest)
    check_rhs(manifest)
    check_findings(receipt, manifest)
    print("Review audit checks passed; demonstrated C4 defects remain CHANGES_REQUIRED.")
