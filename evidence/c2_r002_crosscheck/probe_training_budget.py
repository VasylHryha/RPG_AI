"""Is the shared C2 limit the training budget or capacity? (training data only)

Trains the exact-gradient baseline (the same update R002 used for that control)
on trial 0 of each task for up to 2,000 epochs at the registered eta, and records
TRAINING MSE at several epoch counts. If training error keeps falling well past the
registered 100 epochs, the outcome was budget-limited; if it plateaus, the limit is
capacity (passive network, conductance bounds). No test data is read; nothing here
feeds back into R002.

Run: .venv/bin/python evidence/c2_r002_crosscheck/probe_training_budget.py
"""
import json
from pathlib import Path
import sys
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from geomind.c2_cases import EDGES, generate_trial  # noqa: E402
from geomind.c2_reference import equilibrium, gradient  # noqa: E402

manifest = json.loads((ROOT / "experiments/c2_manifest.json").read_text())
eta, report = manifest["settings"]["eta"], {}
x, labels, _, _ = generate_trial(manifest, 0)
order = np.random.default_rng(manifest["order_seed_start"]).permutation(100)
for task in ("affine", "realizable"):
    g = np.random.default_rng(manifest["initialization_seeds"][0]).uniform(.5, 1.5, 24)
    y = labels[task]
    def train_mse(g):
        return float(np.mean([(equilibrium(g, EDGES, 16, (0, 3), x[i], 10)[10] - y[i]) ** 2 for i in range(100)]))
    curve = {0: train_mse(g)}
    for epoch in range(1, 2001):
        for i in order:
            g = np.clip(g - eta * gradient(g, EDGES, 16, (0, 3), x[i], 10, y[i]), .05, 5)
        if epoch in (100, 300, 1000, 2000):
            curve[epoch] = train_mse(g)
    report[task] = {"train_mse_by_epoch": curve, "saturated_edges_at_2000": int(np.sum((g <= .05) | (g >= 5)))}
Path(__file__).with_suffix(".out.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
