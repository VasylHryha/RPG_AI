"""C5 design gate on development worlds only (decision 0004): does inter-unit coupling exist, and what does a run cost?

Not a milestone stage and not evidence. It harvests accepted C4 resonators from development
C4 worlds with the frozen C4 code, assembles level-2 worlds of M units with per-unit rates,
integrates them with the unchanged C4 law, and reports, per world over time:
cross-unit neighbour links, each unit's own-neighbour fraction (merger), inter-unit phase
drift versus the decoupled expectation, and wall time. Development entropy only; it never
touches final seeds.

    .venv/bin/python tools/c5_design_gate.py --worlds 10 --delta 0.03 --radius 4.0 --horizon 300
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from geomind.c4_detect import circular_std  # noqa: E402
from geomind.c4_experiment import detect_worlds, form, initial_worlds, model_params  # noqa: E402
from geomind.c4_model import neighbors, Batch, simulate  # noqa: E402

DEV_ENTROPY = 22222  # C5 development entropy (C4 used 11111); final entropy is drawn only at registration


def harvest(manifest, count, sizes):
    params = model_params(manifest)["intact"]
    indices = list(range(count))
    x0, th0, om = initial_worlds(manifest, DEV_ENTROPY, "identical", indices)
    x, th, frames = form(x0, th0, om, params, manifest)
    detected = detect_worlds(frames, om, params, manifest, DEV_ENTROPY, "identical", indices)
    units, accepted = [], 0
    for b, cands in enumerate(detected):
        for c in cands:
            if not c["accepted"]:
                continue
            accepted += 1
            m = c["members"]
            if sizes[0] <= len(m) <= sizes[1]:
                units.append({"x": x[b, m] - x[b, m].mean(0), "th": th[b, m] - th[b, m].mean(), "world": b})
    return units, accepted


def assemble(units, M, worlds, delta, radius, min_gap, rng):
    order = rng.permutation(len(units))
    if len(order) < M * worlds:
        raise SystemExit(f"only {len(units)} units for {M * worlds}")
    out = []
    for w in range(worlds):
        chosen = [units[i] for i in order[w * M:(w + 1) * M]]
        for _attempt in range(10000):
            xs, ths, oms, labels = [], [], [], []
            for g, u in enumerate(chosen):
                a = rng.uniform(0, 2 * np.pi)
                R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
                r, phi = radius * np.sqrt(rng.random()), rng.uniform(0, 2 * np.pi)
                xs.append(u["x"] @ R.T + [r * np.cos(phi), r * np.sin(phi)])
                ths.append(u["th"] + rng.uniform(-np.pi, np.pi))
                oms.append(np.full(len(u["th"]), rng.uniform(-delta, delta)))
                labels.append(np.full(len(u["th"]), g))
            X, L = np.concatenate(xs), np.concatenate(labels)
            d = np.linalg.norm(X[:, None] - X[None], axis=-1)
            if d[L[:, None] != L[None]].min() >= min_gap:
                break
        out.append((X, np.concatenate(ths), np.concatenate(oms), L))
    return out


def pad(worlds):
    """Equal N for batching: inert elements far away (beyond radius of everything, always sorted last)."""
    n = max(len(w[0]) for w in worlds)
    xs, ths, oms, labels = [], [], [], []
    for k, (X, th, om, L) in enumerate(worlds):
        extra = n - len(X)
        far = 1e4 * (1 + np.arange(extra))[:, None] * np.array([[1.0, 0.0]]) + [0.0, 1e3 * (k + 1)]
        xs.append(np.vstack([X, far]))
        ths.append(np.concatenate([th, np.zeros(extra)]))
        oms.append(np.concatenate([om, np.zeros(extra)]))
        labels.append(np.concatenate([L, -np.ones(extra, dtype=int)]))
    return np.array(xs), np.array(ths), np.array(oms), np.array(labels)


def diagnostics(x, th, labels, batch, M):
    idx, mask, _ = neighbors(x, batch)
    rows = []
    for b in range(x.shape[0]):
        L = labels[b]
        real = L >= 0
        nb = L[idx[b]]
        valid = mask[b] > 0
        cross = valid & (nb != L[:, None]) & real[:, None]
        own = [float((valid[L == g] & (nb[L == g] == g)).sum() / max(valid[L == g].sum(), 1)) for g in range(M)]
        theta = [float(th[b, L == g].mean()) for g in range(M)]
        cent = [x[b, L == g].mean(0) for g in range(M)]
        rows.append({"cross_links": int(cross.sum()), "own_fraction_min": min(own), "theta": theta,
                     "centroids": [c.tolist() for c in cent]})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harvest", type=int, default=40)
    ap.add_argument("--worlds", type=int, default=10)
    ap.add_argument("--M", type=int, default=5)
    ap.add_argument("--delta", type=float, default=0.03)
    ap.add_argument("--radius", type=float, default=4.0)
    ap.add_argument("--min-gap", type=float, default=0.6)
    ap.add_argument("--horizon", type=float, default=300.0)
    ap.add_argument("--sample", type=float, default=10.0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    manifest = json.loads((ROOT / "experiments" / "c4_manifest.json").read_text())
    params = model_params(manifest)["intact"]
    dt = manifest["integration"]["dt"]

    t0 = time.time()
    units, accepted = harvest(manifest, a.harvest, (6, 16))
    t_harvest = time.time() - t0
    rng = np.random.default_rng(np.random.SeedSequence([DEV_ENTROPY, 5]))
    worlds = assemble(units, a.M, a.worlds, a.delta, a.radius, a.min_gap, rng)
    x, th, om, labels = pad(worlds)
    batch = Batch(params, x.shape[0])
    rates = [[float(om[b, labels[b] == g][0]) for g in range(a.M)] for b in range(x.shape[0])]

    t1 = time.time()
    steps = int(round(a.sample / dt))
    trace = [diagnostics(x, th, labels, batch, a.M)]
    for _ in range(int(round(a.horizon / a.sample))):
        x, th, _ = simulate(x, th, om, params, dt, steps)
        trace.append(diagnostics(x, th, labels, batch, a.M))
    t_sim = time.time() - t1

    report = {"harvest_worlds": a.harvest, "accepted_units": accepted, "units_6_16": len(units),
              "harvest_seconds": round(t_harvest, 1), "sim_seconds": round(t_sim, 1),
              "elements": [int((l >= 0).sum()) for l in labels], "settings": vars(a), "worlds": []}
    for b in range(x.shape[0]):
        th_t = np.array([r[b]["theta"] for r in trace])  # (T, M) unwrapped unit phases
        # Inter-unit frequency: drift of each pair's phase difference over the last third vs the decoupled rate difference.
        third = len(th_t) // 3
        span = (len(th_t) - 1 - 2 * third) * a.sample
        omega_meas = (th_t[-1] - th_t[2 * third]) / span
        report["worlds"].append({
            "rates": rates[b],
            "measured_rates_last_third": omega_meas.tolist(),
            "cross_links": [r[b]["cross_links"] for r in trace],
            "own_fraction_min": [round(r[b]["own_fraction_min"], 3) for r in trace],
            "final_centroids": trace[-1][b]["centroids"],
        })
    text = json.dumps(report, indent=1)
    if a.out:
        Path(a.out).write_text(text)
        np.savez(Path(a.out).with_suffix(".npz"), x=x, th=th, om=om, labels=labels)
    print(json.dumps({k: v for k, v in report.items() if k != "worlds"}))
    for b, w in enumerate(report["worlds"]):
        print(b, "rates", np.round(w["rates"], 3), "meas", np.round(w["measured_rates_last_third"], 3))
        print("   cross", w["cross_links"][::3], "own_min", w["own_fraction_min"][::3])


if __name__ == "__main__":
    main()
