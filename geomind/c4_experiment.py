"""C4 experiment: worlds, formation, detection, matched interventions, statistics and endpoints.

Everything numeric (model values, detector thresholds, seeds, doses, bounds, verdict
rules) comes from the committed manifest; nothing here is tuned per seed.

Interventions are applied to each accepted resonator from its formed state s0,
against a paired control run from the same s0. Both runs of a pair use the same
dynamics (intact, or a matched ablation), and ablated pairs couple phases over the
neighbor topology of s0 when the ablation freezes it.

- G->M: scale the group's positions about its centroid, phases held. Exact
  synchrony is a fixed point for any geometry, so both runs of the pair first
  receive the same zero-mean phase probe kick on the group. The statistic is the
  time-mean RMS deviation of the pairwise phase pattern from s0 over the response
  window; weaker geometric coupling restores the pattern more slowly, so the
  predicted effect is positive. Complete ablation: w = 1 and frozen phase
  topology. The two single channels (w = 1 only; frozen topology only) are
  reported as a decomposition.
- M->G: perturb the group's phases (fixed-RMS zero-mean kicks, or uniform
  replacement), positions held. The statistic is the peak radius of gyration
  relative to s0 over the response window; weaker phase-dependent attraction lets
  the group expand, so the predicted effect is positive. Complete ablation: J = 0.
- Dose-response: under the intact dynamics, larger scales (G->M) and stronger
  phase perturbations (M->G) must give larger effects.

A complete ablation removes its pathway by construction, so its vanishing checks
that the statistic carries no other pathway; the scientific content is the
intact effect and its dose-response. The unit of analysis is the world (seed):
its effect is the mean over its accepted resonators.
"""

import numpy as np
from dataclasses import replace

from geomind.c4_detect import active_unit, detect, pair_differences, radius_of_gyration
from geomind.c4_model import ABLATIONS, Batch, Params, neighbors, simulate, wrap

ARMS = ("identical", "heterogeneous")


def model_params(manifest):
    """Intact parameters from the manifest and every ablation in c4_model.ABLATIONS."""
    m = manifest["model"]
    base = Params(A=m["A"], B=m["B"], J=m["J"], K=m["K"], eps=m["eps"], k=m["neighbors_k"], radius=m["neighbor_radius"])
    params = {
        "intact": base,
        "no_mode_to_geometry": replace(base, J=0.0),
        "no_distance_weight": replace(base, distance_weighted=False),
        "frozen_topology": replace(base, frozen_phase_topology=True),
        "no_geometry_to_mode": replace(base, distance_weighted=False, frozen_phase_topology=True),
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


def mg_states(x, th, members, new_phases):
    """(control, treated) for M->G: treated has the group's phases replaced, positions held."""
    treated = th.copy()
    treated[members] = new_phases
    return (x.copy(), th.copy()), (x.copy(), treated)


def mg_phases(rng, th, members, dose):
    """New phases for the group: 'uniform' replaces them; 'rms:<a>' adds a zero-mean kick of RMS a."""
    if dose == "uniform":
        return rng.uniform(-np.pi, np.pi, len(members))
    return th[members] + probe_kick(rng, len(members), float(dose.split(":")[1]))


def gm_statistic(ths, members, reference_pairs):
    """Time-mean (excluding t0) RMS deviation of the pairwise phase pattern from the reference."""
    deviation = wrap(pair_differences(ths[1:], members) - reference_pairs)
    return float(np.sqrt((deviation ** 2).mean(1)).mean())


def mg_statistic(xs, members, rg0):
    """Peak (excluding t0) radius of gyration of the group relative to its value at s0."""
    return float(max(radius_of_gyration(xs[f, members]) for f in range(1, len(xs))) / rg0)


GM_ABLATIONS = ("no_geometry_to_mode", "no_distance_weight", "frozen_topology")
MG_ABLATIONS = ("no_mode_to_geometry",)


def intervene(state, omega, resonators, params, manifest, entropy, arm, indices):
    """Paired intervention effects for every accepted resonator.

    resonators: list of (world position b, members). Returns one dict per resonator with the
    treated - control effect of the primary G->M and M->G interventions under the intact dynamics
    and each ablation ("g_to_m/<condition>", "m_to_g/<condition>"), and of every dose under the
    intact dynamics ("g_to_m_dose/<scale>", "m_to_g_dose/<dose>")."""
    iv, dt = manifest["interventions"], manifest["integration"]["dt"]
    x, th = state
    intact_batch = Batch(params["intact"], 1)
    runs = {"gm": [], "mg": []}  # (resonator n, effect key or None for a control, condition, x, th)
    rngs = {}
    for n, (b, members) in enumerate(resonators):
        rng = rngs.setdefault(b, world_rng(entropy, arm, indices[b], 2))
        delta = probe_kick(rng, len(members), iv["gm_probe_phase_rms"])
        for condition in ("intact",) + GM_ABLATIONS:
            control, _ = gm_states(x[b], th[b], members, delta, 1.0)
            runs["gm"].append((n, f"control/{condition}", condition, *control))
        for scale in iv["gm_scales"]:
            _, treated = gm_states(x[b], th[b], members, delta, scale)
            runs["gm"].append((n, f"g_to_m_dose/{scale}", "intact", *treated))
            if scale == iv["gm_scale"]:
                for condition in GM_ABLATIONS:
                    runs["gm"].append((n, f"g_to_m/{condition}", condition, *treated))
        for condition in ("intact",) + MG_ABLATIONS:
            runs["mg"].append((n, f"control/{condition}", condition, x[b], th[b]))
        for dose in iv["mg_doses"]:
            _, treated = mg_states(x[b], th[b], members, mg_phases(rng, th[b], members, dose))
            runs["mg"].append((n, f"m_to_g_dose/{dose}", "intact", *treated))
            if dose == iv["mg_dose"]:
                for condition in MG_ABLATIONS:
                    runs["mg"].append((n, f"m_to_g/{condition}", condition, *treated))
    # Frozen phase topology of each pair: the neighbors of its unperturbed s0 (shared by control and treated).
    topology = [neighbors(x[b][None], intact_batch) for b, _ in resonators]
    stats = {}
    for kind, duration in (("gm", iv["gm_window"]), ("mg", iv["mg_window"])):
        rows = runs[kind]
        topo = tuple(np.concatenate([topology[r[0]][i] for r in rows]) for i in range(3))
        _, _, (xs, ths) = simulate(np.array([r[3] for r in rows]), np.array([r[4] for r in rows]),
                                   np.array([omega[resonators[r[0]][0]] for r in rows]), [params[r[2]] for r in rows],
                                   dt, int(round(duration / dt)), int(round(iv["sample_dt"] / dt)), phase_topology=topo)
        for i, (n, key, condition, _, _) in enumerate(rows):
            b, members = resonators[n]
            value = (gm_statistic(ths[:, i], members, pair_differences(th[b], members)) if kind == "gm"
                     else mg_statistic(xs[:, i], members, radius_of_gyration(x[b, members])))
            stats[(kind, n, key, condition)] = value
    effects = [dict() for _ in resonators]
    for (kind, n, key, condition), value in stats.items():
        if not key.startswith("control/"):
            effects[n][key] = value - stats[(kind, n, f"control/{condition}", condition)]
    for n in range(len(resonators)):
        effects[n]["g_to_m/intact"] = effects[n][f"g_to_m_dose/{iv['gm_scale']}"]
        effects[n]["m_to_g/intact"] = effects[n][f"m_to_g_dose/{iv['mg_dose']}"]
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


def causality_verdict(intact, ablated, vanish_fraction, min_worlds):
    """PASS: intact CI excludes 0 in the predicted (positive) direction and the ablated effect vanishes.
    FAIL: intact CI includes 0 or the mean has the wrong sign. INCONCLUSIVE otherwise, or with fewer
    than min_worlds worlds."""
    if intact["ci"] is None or ablated["ci"] is None or intact["n_worlds"] < min_worlds:
        return "INCONCLUSIVE"
    if intact["ci"][0] <= 0:
        return "FAIL"
    vanished = ablated["ci"][0] <= 0 <= ablated["ci"][1] or abs(ablated["mean"]) <= vanish_fraction * intact["mean"]
    return "PASS" if vanished else "INCONCLUSIVE"


def dose_response_verdict(doses, difference, min_worlds):
    """PASS: mean effects are non-decreasing across doses and the highest-minus-lowest paired difference
    has a CI above 0. FAIL: that CI lies below 0. INCONCLUSIVE otherwise, or with fewer than min_worlds worlds."""
    if difference["ci"] is None or difference["n_worlds"] < min_worlds:
        return "INCONCLUSIVE"
    means = [d["mean"] for d in doses]
    if all(a <= b for a, b in zip(means, means[1:])) and difference["ci"][0] > 0:
        return "PASS"
    return "FAIL" if difference["ci"][1] < 0 else "INCONCLUSIVE"


def summarize(per_world, rng, resamples):
    values = [v for v in per_world if v is not None]
    return {"n_worlds": len(values), "mean": float(np.mean(values)) if values else None,
            "ci": bootstrap_ci(values, rng, resamples), "per_world": per_world}


# Formation from the same initial worlds. Frozen phase topology is defined from a formed state, so the
# complete geometry -> mode ablation is applied in the interventions only.
CONDITIONS = ("intact", "no_mode_to_geometry", "no_distance_weight", "clump")


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
            "resonator_effects": [effects[n] for n in accepted],
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

    min_worlds = rules["min_worlds_for_verdict"]
    iv = manifest["interventions"]
    causality = {}
    for name, ablation in (("g_to_m", "no_geometry_to_mode"), ("m_to_g", "no_mode_to_geometry")):
        intact, ablated = effect(f"{name}/intact"), effect(f"{name}/{ablation}")
        causality[name] = {"intact": intact, "ablated": {"condition": ablation, **ablated},
                           "verdict": causality_verdict(intact, ablated, rules["ablation_vanish_fraction"], min_worlds)}
    channels = {"condition_note": "G->M primary effect with one geometric channel removed (descriptive)",
                **{c: effect(f"g_to_m/{c}") for c in ("no_distance_weight", "frozen_topology")}}
    for c in ("no_distance_weight", "frozen_topology"):
        mean, base = channels[c]["mean"], causality["g_to_m"]["intact"]["mean"]
        channels[c]["fraction_of_intact"] = (mean / base) if mean is not None and base else None
    channels["verdict"] = "REPORTED"
    dose = {}
    for name, labels in (("g_to_m", [str(s) for s in iv["gm_scales"]]), ("m_to_g", list(iv["mg_doses"]))):
        per_dose = [effect(f"{name}_dose/{label}") for label in labels]
        difference = summarize([None if w["resonators"] == 0 else
                                w["effects"][f"{name}_dose/{labels[-1]}"] - w["effects"][f"{name}_dose/{labels[0]}"]
                                for w in worlds], rng, resamples)
        dose[name] = {"doses": dict(zip(labels, per_dose)), "highest_minus_lowest": difference,
                      "verdict": dose_response_verdict(per_dose, difference, min_worlds)}
    dose["verdict"] = ("PASS" if all(dose[n]["verdict"] == "PASS" for n in ("g_to_m", "m_to_g")) else
                       "FAIL" if any(dose[n]["verdict"] == "FAIL" for n in ("g_to_m", "m_to_g")) else "INCONCLUSIVE")
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
        "dose_response": dose,
        "g_to_m_channels": channels,
        "not_a_clump": {**clump, "verdict": "PASS" if clump["accepted_resonators"] == 0 else "FAIL"},
        "effective_state": effective_state,
        "ablation_formation": {k: v for k, v in records["ablation_formation"].items() if k != "clump"},
    }


def hypothesis_verdicts(arm_eval, rules):
    formation_ok = arm_eval["formation"]["fraction"] >= rules["formation_min_fraction"]
    causal = (arm_eval["g_to_m"]["verdict"], arm_eval["m_to_g"]["verdict"], arm_eval["dose_response"]["verdict"])
    if "FAIL" in causal:
        h_m = "NOT_SUPPORTED"
    elif formation_ok and causal == ("PASS", "PASS", "PASS"):
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
