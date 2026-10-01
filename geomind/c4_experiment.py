"""C4 experiment: worlds, formation, detection, matched interventions, statistics and endpoints.

Everything numeric (model values, detector thresholds, seeds, bounds, verdict rules)
comes from the committed manifest; nothing here is tuned per seed.

Interventions are applied to each accepted resonator from its formed state s0,
against a paired control run from the same s0, under the intact dynamics and
under the matched ablation (both runs of a pair use the same dynamics):

- G->M: scale the group's positions by `scale` about its centroid, phases held.
  Because exact synchrony is a fixed point for any geometry, both runs of the
  pair first receive the same zero-mean phase probe kick on the group. The
  statistic is the time-mean RMS deviation of the pairwise phase pattern from
  s0 over the response window: weaker distance-weighted coupling restores the
  pattern more slowly, so the predicted effect is positive. Ablation: w = 1.
- M->G: replace the group's phases with uniform random phases, positions held.
  The statistic is the peak radius of gyration relative to s0 over the response
  window: weaker phase-dependent attraction lets the group expand, so the
  predicted effect is positive. Ablation: J = 0.

The unit of analysis is the world (seed): its effect is the mean over its
accepted resonators.
"""

import numpy as np
from dataclasses import replace

from geomind.c4_detect import active_unit, detect, pair_differences, radius_of_gyration
from geomind.c4_model import ABLATIONS, Params, simulate, wrap

ARMS = ("identical", "heterogeneous")


def model_params(manifest):
    """Intact parameters from the manifest and the matched ablations (ABLATIONS lists the same five conditions)."""
    m = manifest["model"]
    base = Params(A=m["A"], B=m["B"], J=m["J"], K=m["K"], eps=m["eps"], k=m["neighbors_k"], radius=m["neighbor_radius"])
    params = {
        "intact": base,
        "no_mode_to_geometry": replace(base, J=0.0),
        "no_geometry_to_mode": replace(base, distance_weighted=False),
        "both_off": replace(base, J=0.0, distance_weighted=False),
        "clump": replace(base, J=0.0, K=0.0),
    }
    assert set(params) == set(ABLATIONS)
    return params


def world_rng(entropy, arm, index, purpose):
    return np.random.default_rng(np.random.SeedSequence([entropy, ARMS.index(arm), index, purpose]))


def initial_worlds(manifest, entropy, arm, indices):
    w = manifest["worlds"]
    n = w["elements"]
    xs, ths, omegas = [], [], []
    for i in indices:
        rng = world_rng(entropy, arm, i, 0)
        radius = w["disk_radius"] * np.sqrt(rng.random(n))
        angle = 2 * np.pi * rng.random(n)
        xs.append(np.c_[radius * np.cos(angle), radius * np.sin(angle)])
        ths.append(rng.uniform(-np.pi, np.pi, n))
        omegas.append(np.zeros(n) if arm == "identical" else rng.uniform(-w["omega_half_width"], w["omega_half_width"], n))
    return np.array(xs), np.array(ths), np.array(omegas)


def form(x, th, omega, params, manifest):
    """Integrate to the horizon (params: one Params or one per world); return the final state and window frames (F, B, ...)."""
    i = manifest["integration"]
    dt, frame_dt = i["dt"], manifest["detector"]["frame_dt"]
    window_steps = int(round(manifest["detector"]["window"] / dt))
    total = int(round(i["horizon"] / dt))
    x, th, _ = simulate(x, th, omega, params, dt, total - window_steps)
    x, th, frames = simulate(x, th, omega, params, dt, window_steps, int(round(frame_dt / dt)))
    return x, th, frames


def detect_worlds(frames, omega, params, manifest, entropy, arm, indices):
    rngs = [world_rng(entropy, arm, i, 1) for i in indices]
    return detect(frames[0], frames[1], omega, params, manifest["integration"]["dt"], manifest["detector"]["frame_dt"],
                  manifest["detector"], rngs)


# Intervention states (pure functions so the held variables can be checked bit for bit).
def probe_kick(rng, size, rms):
    delta = rng.normal(size=size)
    delta -= delta.mean()
    return delta * (rms / np.sqrt((delta ** 2).mean()))


def gm_states(x, th, members, delta, scale):
    """(control, treated) for G->M: both get the phase probe; treated also has the group scaled about its centroid."""
    kicked = th.copy()
    kicked[members] += delta
    scaled = x.copy()
    centroid = x[members].mean(0)
    scaled[members] = centroid + scale * (x[members] - centroid)
    return (x.copy(), kicked), (scaled, kicked.copy())


def mg_states(x, th, members, random_phases):
    """(control, treated) for M->G: treated has the group's phases replaced, positions held."""
    treated = th.copy()
    treated[members] = random_phases
    return (x.copy(), th.copy()), (x.copy(), treated)


def gm_statistic(ths, members, reference_pairs):
    """Time-mean (excluding t0) RMS deviation of the pairwise phase pattern from the reference."""
    deviation = wrap(pair_differences(ths[1:], members) - reference_pairs)
    return float(np.sqrt((deviation ** 2).mean(1)).mean())


def mg_statistic(xs, members, rg0):
    """Peak (excluding t0) radius of gyration of the group relative to its value at s0."""
    return float(max(radius_of_gyration(xs[f, members]) for f in range(1, len(xs))) / rg0)


def intervene(state, omega, resonators, params, manifest, entropy, arm, indices):
    """Paired intervention effects for every accepted resonator.

    resonators: list of (world position b, members). Returns one dict per resonator with the
    treated - control effect of G->M and M->G under intact and ablated dynamics."""
    iv, dt = manifest["interventions"], manifest["integration"]["dt"]
    x, th = state
    rngs = {}
    gm_pairs, mg_pairs = [], []
    for b, members in resonators:
        rng = rngs.setdefault(b, world_rng(entropy, arm, indices[b], 2))
        delta = probe_kick(rng, len(members), iv["gm_probe_phase_rms"])
        gm_pairs.append(gm_states(x[b], th[b], members, delta, iv["gm_scale"]))
        mg_pairs.append(mg_states(x[b], th[b], members, rng.uniform(-np.pi, np.pi, len(members))))
    effects = [dict() for _ in resonators]

    def run(pairs, conditions, duration):
        """All conditions in one batch: world index (c, n, s) for condition c, resonator n, s = control/treated."""
        bx = np.array([s[0] for _ in conditions for pair in pairs for s in pair])
        bt = np.array([s[1] for _ in conditions for pair in pairs for s in pair])
        bw = np.array([omega[b] for _ in conditions for b, _ in resonators for _ in (0, 1)])
        plist = [params[c] for c in conditions for _ in pairs for _ in (0, 1)]
        _, _, frames = simulate(bx, bt, bw, plist, dt, int(round(duration / dt)), int(round(iv["sample_dt"] / dt)))
        return frames

    gm_conditions = ("intact", "no_geometry_to_mode", "both_off")
    xs, ths = run(gm_pairs, gm_conditions, iv["gm_window"])
    for c, condition in enumerate(gm_conditions):
        for n, (b, members) in enumerate(resonators):
            reference = pair_differences(th[b], members)
            base = 2 * (c * len(resonators) + n)
            control, treated = gm_statistic(ths[:, base], members, reference), gm_statistic(ths[:, base + 1], members, reference)
            effects[n][f"g_to_m/{condition}"] = treated - control
    mg_conditions = ("intact", "no_mode_to_geometry", "both_off")
    xs, ths = run(mg_pairs, mg_conditions, iv["mg_window"])
    for c, condition in enumerate(mg_conditions):
        for n, (b, members) in enumerate(resonators):
            rg0 = radius_of_gyration(x[b, members])
            base = 2 * (c * len(resonators) + n)
            control, treated = mg_statistic(xs[:, base], members, rg0), mg_statistic(xs[:, base + 1], members, rg0)
            effects[n][f"m_to_g/{condition}"] = treated - control
    return effects


# Statistics.
def bootstrap_ci(values, rng, resamples, level=0.95):
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return None
    means = values[rng.integers(0, len(values), size=(resamples, len(values)))].mean(1)
    tail = (1 - level) / 2
    return [float(np.quantile(means, tail)), float(np.quantile(means, 1 - tail))]


def wilson(successes, total, z=1.959963984540054):
    if total == 0:
        return None
    p = successes / total
    centre = (p + z * z / (2 * total)) / (1 + z * z / total)
    half = z * np.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / (1 + z * z / total)
    return [float(centre - half), float(centre + half)]


def causality_verdict(intact, ablated, vanish_fraction):
    """PASS: intact CI excludes 0 in the predicted (positive) direction and the ablated effect vanishes.
    FAIL: intact CI includes 0 or the mean has the wrong sign. INCONCLUSIVE otherwise (or no data)."""
    if intact["ci"] is None or ablated["ci"] is None:
        return "INCONCLUSIVE"
    if intact["ci"][0] <= 0:
        return "FAIL"
    vanished = ablated["ci"][0] <= 0 <= ablated["ci"][1] or abs(ablated["mean"]) <= vanish_fraction * intact["mean"]
    return "PASS" if vanished else "INCONCLUSIVE"


def summarize(per_world, rng, resamples):
    values = [v for v in per_world if v is not None]
    return {"n_worlds": len(values), "mean": float(np.mean(values)) if values else None,
            "ci": bootstrap_ci(values, rng, resamples), "per_world": per_world}


CONDITIONS = ("intact", "no_mode_to_geometry", "no_geometry_to_mode", "both_off", "clump")


def run_arm(manifest, entropy, arm, indices, params):
    """Formation, detection and interventions for one arm; returns raw per-world records.

    The intact model and every ablation start from the same initial worlds and run in one batch
    (world c * W + b is condition c, world b); detection kicks are paired across conditions."""
    x0, th0, omega = initial_worlds(manifest, entropy, arm, indices)
    count = len(indices)
    tile = lambda a: np.concatenate([a] * len(CONDITIONS))
    plist = [params[c] for c in CONDITIONS for _ in indices]
    x_all, th_all, frames_all = form(tile(x0), tile(th0), tile(omega), plist, manifest)
    detected_all = detect_worlds(frames_all, tile(omega), plist, manifest, entropy, arm, list(indices) * len(CONDITIONS))
    x, th = x_all[:count], th_all[:count]
    frames = (frames_all[0][:, :count], frames_all[1][:, :count])
    detected = detected_all[:count]
    resonators = [(b, c["members"]) for b, cands in enumerate(detected) for c in cands if c["accepted"]]
    effects = intervene((x, th), omega, resonators, params, manifest, entropy, arm, indices) if resonators else []
    frame_dt = manifest["detector"]["frame_dt"]
    half = len(frames[1]) // 2
    worlds = []
    for b, cands in enumerate(detected):
        accepted = [n for n, (rb, _) in enumerate(resonators) if rb == b]
        units = []
        for c in cands:
            if c["accepted"]:
                members = c["members"]
                omega_est = float((frames[1][-1, b, members] - frames[1][half, b, members]).mean() / (half * frame_dt))
                units.append(active_unit(x[b], th[b], omega_est, members, c["stats"]))
        worlds.append({
            "seed_index": int(indices[b]),
            "candidates": [{"stats": c["stats"], "failed": c["failed"], "accepted": c["accepted"]} for c in cands],
            "resonators": len(accepted),
            "units": units,
            "effects": {key: float(np.mean([effects[n][key] for n in accepted])) for key in (effects[0] if effects else {})}
            if accepted else {},
        })
    records = {"indices": list(indices), "worlds": worlds, "ablation_formation": {}}
    # Formation under each ablation from the same initial worlds (descriptive) and the clump control (detector validity).
    for c, condition in enumerate(CONDITIONS[1:], start=1):
        detected_a = detected_all[c * count:(c + 1) * count]
        records["ablation_formation"][condition] = {
            "worlds_with_resonator": int(sum(any(d["accepted"] for d in cands) for cands in detected_a)),
            "accepted_resonators": int(sum(d["accepted"] for cands in detected_a for d in cands)),
            "candidates": int(sum(len(cands) for cands in detected_a)),
            "rejections_by_criterion": {name: int(sum(name in d["failed"] for cands in detected_a for d in cands))
                                        for name in ("1_membership", "2_shape", "3_mode_lock", "4_signature", "5_recovery")},
        }
    return records


def evaluate_arm(records, manifest, rng):
    """Endpoint values and verdicts for one arm from its raw records."""
    rules, resamples = manifest["verdict_rules"], manifest["statistics"]["bootstrap_resamples"]
    worlds = records["worlds"]
    formed = sum(w["resonators"] > 0 for w in worlds)
    formation = {"worlds": len(worlds), "worlds_with_resonator": formed, "fraction": formed / len(worlds),
                 "wilson_95": wilson(formed, len(worlds))}
    formation["verdict"] = "PASS" if formation["fraction"] >= rules["formation_min_fraction"] else "FAIL"

    def effect(key):
        return summarize([w["effects"].get(key) if w["resonators"] else None for w in worlds], rng, resamples)

    causality = {}
    for name, ablation in (("g_to_m", "no_geometry_to_mode"), ("m_to_g", "no_mode_to_geometry")):
        intact, ablated, both = effect(f"{name}/intact"), effect(f"{name}/{ablation}"), effect(f"{name}/both_off")
        causality[name] = {"intact": intact, "ablated": {"condition": ablation, **ablated}, "both_off": both,
                           "verdict": causality_verdict(intact, ablated, rules["ablation_vanish_fraction"])}
    bounds = manifest["effective_state_bounds"]
    errors = [{k: u["stability"][k] for k in bounds} for w in worlds for u in w["units"]]
    within = sum(all(e[k] <= bounds[k] for k in bounds) for e in errors)
    fraction = within / len(errors) if errors else None
    worst = {k: max((e[k] for e in errors), default=None) for k in bounds}
    effective_state = {"units": len(errors), "units_within_bounds": within, "fraction_within_bounds": fraction,
                       "worst": worst, "bounds": bounds,
                       "verdict": ("INCONCLUSIVE" if not errors else
                                   "PASS" if fraction >= rules["effective_state_min_fraction"] else "FAIL")}
    clump = records["ablation_formation"]["clump"]
    return {
        "formation": formation,
        "g_to_m": causality["g_to_m"],
        "m_to_g": causality["m_to_g"],
        "both_off": {"verdict": "REPORTED", "g_to_m": causality["g_to_m"]["both_off"], "m_to_g": causality["m_to_g"]["both_off"],
                     "note": "descriptive: with J = 0 and w = 1, geometry can still reach the phases through neighbor selection"},
        "not_a_clump": {**clump, "verdict": "PASS" if clump["accepted_resonators"] == 0 else "FAIL"},
        "effective_state": effective_state,
        "ablation_formation": {k: v for k, v in records["ablation_formation"].items() if k != "clump"},
    }


def hypothesis_verdicts(arm_eval, rules):
    formation_ok = arm_eval["formation"]["fraction"] >= rules["formation_min_fraction"]
    causal = (arm_eval["g_to_m"]["verdict"], arm_eval["m_to_g"]["verdict"])
    if "FAIL" in causal:
        h_m = "NOT_SUPPORTED"
    elif formation_ok and causal == ("PASS", "PASS"):
        h_m = "SUPPORTED_WITHIN_SCOPE"
    else:
        h_m = "INCONCLUSIVE"
    state = arm_eval["effective_state"]["verdict"]
    if state == "FAIL":
        h_c = "NOT_SUPPORTED"
    elif h_m == "SUPPORTED_WITHIN_SCOPE" and state == "PASS":
        h_c = "SUPPORTED_WITHIN_SCOPE"
    else:
        h_c = "INCONCLUSIVE"
    return {"H-M": h_m, "H-C_precursor": h_c}


# Numerical checks computed in the panel (no registered check is test-only).
def numerical_checks(manifest, params, entropy):
    """Computed in the panel from final-world states (no registered check is test-only).

    - RK4 order: with neighbor sets held fixed the right-hand side is smooth, so halving dt must cut the
      error against a dt/4 reference by >= min_order_ratio and keep it <= held_dt_tolerance.
    - Full model: neighbor sets switch at step boundaries, which limits convergence to first order; the
      dt vs dt/4 difference must stay <= switching_dt_tolerance.
    - Equivariance: permuting elements, rotating and translating the plane and shifting every phase by
      the same constant commutes with the dynamics to <= equivariance_tolerance.
    """
    nc = manifest["numerical_checks"]
    dt = manifest["integration"]["dt"]
    steps = int(round(nc["horizon"] / dt))
    out = {}

    def run(x, th, omega, step, held):
        return simulate(x, th, omega, params["intact"], step, int(round(nc["horizon"] / step)), hold_neighbors=held)[:2]

    def difference(a, b):
        return float(max(np.abs(a[0] - b[0]).max(), np.abs(a[1] - b[1]).max()))

    for arm in ARMS:
        x0, th0, omega = initial_worlds(manifest, entropy, arm, [0])
        x, th, _ = simulate(x0, th0, omega, params["intact"], dt, int(round(nc["settle_time"] / dt)))
        rng = world_rng(entropy, arm, 0, 3)
        th = th + probe_kick(rng, th.shape[1], manifest["interventions"]["gm_probe_phase_rms"])
        held = {step: run(x, th, omega, step, True) for step in (dt, dt / 2, dt / 4)}
        full = {step: run(x, th, omega, step, False) for step in (dt, dt / 4)}
        held_error, held_half_error = difference(held[dt], held[dt / 4]), difference(held[dt / 2], held[dt / 4])
        perm = rng.permutation(x.shape[1])
        angle = rng.uniform(0, 2 * np.pi)
        rot = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        shift = rng.normal(size=2) * 10
        transformed = simulate(x[:, perm] @ rot.T + shift, th[:, perm] + 1.0, omega[:, perm], params["intact"], dt, steps)[:2]
        expected = full[dt][0][:, perm] @ rot.T + shift
        equivariance = float(max(np.abs(transformed[0] - expected).max(),
                                 np.abs(wrap(transformed[1] - full[dt][1][:, perm] - 1.0)).max()))
        out[arm] = {"held_dt_error": held_error, "held_dt_half_error": held_half_error,
                    "held_order_ratio": held_error / max(held_half_error, 1e-300),
                    "switching_dt_error": difference(full[dt], full[dt / 4]), "equivariance_error": equivariance}
    out["verdict"] = "PASS" if all(
        out[a]["held_dt_error"] <= nc["held_dt_tolerance"] and out[a]["held_order_ratio"] >= nc["min_order_ratio"]
        and out[a]["switching_dt_error"] <= nc["switching_dt_tolerance"] and out[a]["equivariance_error"] <= nc["equivariance_tolerance"]
        for a in ARMS) else "FAIL"
    return out
