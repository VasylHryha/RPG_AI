"""Cross-family check of the registered C2 endpoint `gradient_direction_cosine_min = 0.999`.

The R002 panel registers this endpoint but never evaluates it. This probe evaluates
it for single training updates at the registered settings (beta=0.05, eta=0.01,
tolerance 1e-9, initial conductances Uniform[0.5,1.5], inputs Uniform[0,1]^2,
target Uniform[0,1]). Each candidate update is compared with the exact negative
loss gradient from the independent adjoint reference, and the probe is repeated at
beta=0.001 to separate finite-nudge bias from implementation error. Clipped
updates are excluded, as the standard specifies.

Run: .venv/bin/python evidence/c2_r002_crosscheck/probe_gradient_direction.py
"""

import hashlib
import json
from dataclasses import replace
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from geomind.c2_network import ConductanceNetwork, Settings, GRID_EDGES  # noqa: E402
from geomind.c2_reference import equilibrium, gradient  # noqa: E402

HASH = hashlib.sha256(b"c2-r002-cross-family-check").hexdigest()


def cosine(beta, g, x, y):
    net = ConductanceNetwork(g.tolist(), HASH, replace(Settings(), beta=beta, tolerance=1e-12 if beta < 0.05 else 1e-9))
    before = net.conductances
    trace = net.learn(x, y)
    if trace["status"] != "PASS" or trace["cost"]["saturated"]:
        return None
    step, descent = net.conductances - before, -gradient(before, GRID_EDGES, 16, (0, 3), x, 10, y)
    if np.linalg.norm(step) < 1e-15 or np.linalg.norm(descent) < 1e-15:
        return None
    return float(step @ descent / np.linalg.norm(step) / np.linalg.norm(descent))


def main():
    rng = np.random.default_rng(20261001)
    rows = []
    for _ in range(1000):
        g, x, y = rng.uniform(0.5, 1.5, 24), rng.uniform(0, 1, 2), float(rng.uniform(0, 1))
        residual = abs(equilibrium(g, GRID_EDGES, 16, (0, 3), x, 10)[10] - y)
        rows.append({"residual": float(residual), "beta_0.05": cosine(0.05, g, x, y), "beta_0.001": cosine(0.001, g, x, y)})

    def summary(key, subset=None):
        values = [r[key] for r in (subset or rows) if r[key] is not None]
        return {"cases": len(values), "min": min(values), "median": float(np.median(values)),
                "fraction_ge_0.999": sum(v >= 0.999 for v in values) / len(values), "wrong_direction": sum(v < 0 for v in values)}

    small = [r for r in rows if r["residual"] < 0.1]
    report = {"registered_endpoint": "gradient_direction_cosine_min = 0.999 (registered in experiments/c2_manifest.json; not evaluated by the R002 panel)",
              "registered_beta_0.05": summary("beta_0.05"), "registered_beta_0.05_residual_lt_0.1": summary("beta_0.05", small),
              "reduced_beta_0.001": summary("beta_0.001")}
    (Path(__file__).with_suffix(".out.json")).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
