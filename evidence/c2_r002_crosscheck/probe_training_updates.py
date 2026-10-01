"""Registered gradient-direction endpoint on the ACTUAL R002 training updates.

Supersedes `probe_gradient_direction.py` as the endpoint's evidence. That probe drew
targets independently of the network's output, producing output errors up to about
0.9, far larger than in training, so it is kept only as a stress test.

This probe uses the registered manifest, data, teacher, initialization and order
seeds (`generate_trial`), follows the candidate's own trajectory through the first
training epoch of all 40 trials (the epoch with the largest output errors, so the
worst case), and compares every committed, unclipped update with the exact
negative gradient of that step's half-squared loss, using the independent adjoint
reference. Training data only; no test data is read.

Run: .venv/bin/python evidence/c2_r002_crosscheck/probe_training_updates.py
"""

import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from geomind.c2_cases import EDGES, generate_trial  # noqa: E402
from geomind.c2_network import ConductanceNetwork, digest  # noqa: E402
from geomind.c2_reference import gradient  # noqa: E402


def main():
    manifest = json.loads((ROOT / "experiments/c2_manifest.json").read_text())
    rows = {"affine": [], "realizable": []}
    skipped = 0
    for index, seed in enumerate(manifest["initialization_seeds"]):
        x, labels, _, orders = generate_trial(manifest, index)
        for task in rows:
            state = ConductanceNetwork(np.random.default_rng(seed).uniform(.5, 1.5, 24), digest(manifest))
            for sample in orders[0]:
                before = state.conductances
                trace = state.learn(x[sample], labels[task][sample])
                step = state.conductances - before
                descent = -gradient(before, EDGES, 16, (0, 3), x[sample], 10, labels[task][sample])
                if trace["status"] != "PASS" or trace["cost"]["saturated"] or np.linalg.norm(step) < 1e-15 or np.linalg.norm(descent) < 1e-15:
                    skipped += 1
                    continue
                rows[task].append(float(step @ descent / np.linalg.norm(step) / np.linalg.norm(descent)))

    def summary(values):
        return {"updates": len(values), "min": min(values), "median": float(np.median(values)),
                "fraction_ge_0.999": sum(v >= 0.999 for v in values) / len(values), "wrong_direction": sum(v < 0 for v in values)}

    report = {"scope": "first training epoch, all 20 seeds per task, registered beta=0.05, candidate trajectory; unclipped committed updates",
              "skipped_clipped_or_zero": skipped, **{task: summary(values) for task, values in rows.items()}}
    Path(__file__).with_suffix(".out.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
