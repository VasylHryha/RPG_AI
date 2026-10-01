"""C5 experiment: level-2 worlds, formation, detection, matched interventions, controls, coarse model, endpoints.

Everything numeric comes from the committed C5 manifest and the frozen C4 manifest (level-1 model and
detector). Times one level up are the C4 times multiplied by the single registered factor T.

Per world (independent seed):
1. Assembly from single-use level-1 templates with per-unit rates (c5_compose.assemble); also the
   same world with every rate scaled by each registered spread factor (descriptive sweep).
2. Formation with the frozen C4 law for 100 T, then a window of 30 T sampled every T.
3. Level-2 detection (c5_detect) on unit states only; criterion 5 integrates rigid unit kicks.
4. For each accepted level-2 resonator, from its formed state s0, paired runs:
   - G->M: units moved rigidly so offsets from the group centroid scale by s; both runs of a pair get
     the same zero-mean unit-phase probe. Statistic: time-mean RMS inter-unit pattern deviation over
     5 T (C4 gm_statistic on unit phases). Complete ablation: w = 1 with the phase topology frozen at s0.
   - M->G: each unit's phases rotated rigidly by a zero-mean unit-level kick of fixed RMS (the dose). Statistic: peak radius
     of gyration of the unit centroids relative to s0 over 10 T (C4 mg_statistic on centroids).
     Complete ablation: J = 0.
   - Downward effect: the group versus the same units decoupled (translated beyond the C4 radius) over
     10 T: (a) unit rate pulled from its natural rate; (b) RMS shift of port-member phase offsets.
   - Held-out excitations on one unit: a phase pulse and a radial push. Full responses of the other
     units (emergent transfer: intact minus decoupled), and the coarse model's open-loop prediction
     against three cheap baselines (no transfer; rigid transfer; relaxation to an equal share with the
     group's own measured tau2). The reopening protocol is run alongside and reported.
   - Timescale separation: tau2 (between units) over tau1 (within units); a hierarchy relaxes more
     slowly between its parts than within them.
5. Controls from s0 with every unit decoupled: rates as assembled (drift) and all rates 0 (static).
   The candidates are the intact world's candidate groups, or its proximity-only components, so a
   control is never empty.
6. level1_pool: every used unit, alone with its rate, is re-detected as an accepted C4 resonator.

The unit of analysis is the world: its effect is the mean over its accepted level-2 resonators.
"""

import hashlib
import json
from pathlib import Path

import numpy as np

from geomind import c5_coarse
from geomind.c4_detect import (_convex_hull, circular_mean, components, detect as c4_detect, locked_pairs, pair_differences,
                               radius_of_gyration)
from geomind.c4_experiment import (bootstrap_ci, causality_verdict, dose_response_verdict, gm_statistic, mg_statistic,
                                   model_params, summarize, wilson)
from geomind.c4_model import Batch, neighbors, simulate, wrap
from geomind.c5_compose import (assemble, decouple_offsets, pad, rotate_units, scale_units, shift_units, unit_kick)
from geomind.c5_detect import (candidates, criteria_checks, imposed, level2_thresholds, outcome, parts_alive, recovery,
                               unit_kick as detector_kick)
from geomind.c5_units import harvest, resonator_state, unit_phases, unit_positions, unit_validity

ROOT = Path(__file__).resolve().parents[1]
GM_CONDITIONS = ("no_geometry_to_mode", "no_distance_weight", "frozen_topology")
MG_CONDITIONS = ("no_mode_to_geometry",)
CRITERIA = ("1_membership", "2_shape", "3_mode_lock", "4_signature", "5_recovery", "6_parts_alive")


def load_c4(manifest):
    path = ROOT / manifest["level1"]["c4_manifest"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["level1"]["c4_manifest_sha256"]:
        raise ValueError("the frozen C4 manifest changed")
    return json.loads(path.read_text())


def settings(manifest, c4m):
    """Derived level-2 settings: thresholds, times and step counts."""
    T = manifest["normalization"]["T"]
    dt = c4m["integration"]["dt"]
    t1 = c4m["detector"]
    t2 = level2_thresholds(t1, T)
    iv, ex = manifest["interventions"], manifest["excitations"]
    steps = lambda time: int(round(time / dt))
    return {
        "T": T, "dt": dt, "t1": t1, "t2": t2,
        "horizon_steps": steps(manifest["integration"]["horizon_in_T"] * T),
        "window_steps": steps(t2["window"]), "frame_every": steps(t2["frame_dt"]),
        "recovery_steps": steps(t2["recovery_time"]),
        "gm_steps": steps(iv["gm_window_in_T"] * T), "mg_steps": steps(iv["mg_window_in_T"] * T),
        "sample_every": steps(iv["sample_dt_in_T"] * T),
        "max_port_overlap": manifest["detector"]["max_port_overlap"],
        "pulse": ex["phase_pulse"], "push": ex["radial_push_in_L"],
    }


def rng_for(entropy, purpose, *keys):
    return np.random.default_rng(np.random.SeedSequence([entropy, purpose, *keys]))


# ---------------------------------------------------------------- harvest and assembly
def harvest_count(manifest, worlds):
    return int(np.ceil(manifest["level1"]["harvest_ratio"] * manifest["worlds"]["units_per_world"] * worlds))


def build_worlds(manifest, templates, entropy, indices):
    w = manifest["worlds"]
    M = w["units_per_world"]
    out = []
    for i in indices:
        chosen = templates[i * M:(i + 1) * M]
        out.append(assemble(chosen, rng_for(entropy, 5, i), M, w["rate_half_width"], w["placement_radius"], w["min_gap"]))
    return out


# ---------------------------------------------------------------- detection on unit states
def unit_series(xs, ths, labels, offsets, M):
    units = list(range(M))
    real = xs - offsets[None] if offsets is not None else xs
    return unit_positions(real, labels, units), unit_phases(ths, labels, units), real


def detect_rows(rows, S, rngs, groups=None):
    """Level-2 detection for a list of rows.

    rows: dicts with frames xs (F, N, 2), ths (F, N), state x0, th0 (last frame), omega, labels, params, offsets.
    groups: None (label-free candidates) or one list of imposed unit groups per row (controls).
    Returns, per row, the candidate records and the unit-level window series."""
    t1, t2 = S["t1"], S["t2"]
    pending, out = [], []
    for r, row in enumerate(rows):
        M = int(row["labels"].max()) + 1
        X, Th, real = unit_series(row["xs"], row["ths"], row["labels"], row["offsets"], M)
        keep = row["labels"] >= 0  # inert padding never enters a spacing median or a hull
        validity = unit_validity(real[:, keep], row["ths"][:, keep], row["labels"][keep], list(range(M)),
                                 t2["frame_dt"], t1["link_factor"])
        if groups is None:
            found, locked = candidates(X, Th, t2["frame_dt"], t2)
        else:
            found, locked = imposed(X, Th, groups[r], t2["frame_dt"], t2)
        cands = []
        for units, stats in found:
            ok, worst = parts_alive(validity, units, t1, S["max_port_overlap"])
            stats["parts_alive"], stats["parts_worst"] = ok, worst
            dX, dTh = detector_kick(X[-1], Th[-1], units, rngs[r], t2)
            kx = shift_units(row["x0"], row["labels"], units, dX)
            kt = rotate_units(row["th0"], row["labels"], units, dTh)
            cands.append({"units": [int(u) for u in units], "stats": stats})
            pending.append((r, len(cands) - 1, kx, kt))
        out.append({"candidates": cands, "X": X, "Theta": Th, "validity": validity, "locked": locked, "M": M})
    if pending:
        controls = sorted({p[0] for p in pending})
        bx = np.array([rows[r]["x0"] for r in controls] + [p[2] for p in pending])
        bt = np.array([rows[r]["th0"] for r in controls] + [p[3] for p in pending])
        bw = np.array([rows[r]["omega"] for r in controls] + [rows[p[0]]["omega"] for p in pending])
        plist = [rows[r]["params"] for r in controls] + [rows[p[0]]["params"] for p in pending]
        end_x, end_th, _ = simulate(bx, bt, bw, plist, S["dt"], S["recovery_steps"])
        where = {r: i for i, r in enumerate(controls)}
        for n, (r, c, _, _) in enumerate(pending):
            row, res = rows[r], out[r]
            off = row["offsets"] if row["offsets"] is not None else 0.0
            units = list(range(res["M"]))
            cx = unit_positions((end_x[where[r]] - off)[None], row["labels"], units)[0]
            ct = unit_phases(end_th[where[r]][None], row["labels"], units)[0]
            kxu = unit_positions((end_x[len(controls) + n] - off)[None], row["labels"], units)[0]
            ktu = unit_phases(end_th[len(controls) + n][None], row["labels"], units)[0]
            cand = res["candidates"][c]
            cand["stats"].update(recovery(np.array(cand["units"]), cx, ct, kxu, ktu, res["locked"], S["t2"]))
    for res in out:
        for cand in res["candidates"]:
            checks = criteria_checks(cand["stats"], S["t2"])
            cand["failed"] = [k for k, ok in checks.items() if not ok]
            cand["accepted"] = not cand["failed"]
    return out


def contact(x, labels, params):
    idx, mask, _ = neighbors(x[None], Batch(params, 1))
    lab = labels
    return bool(((mask[0] > 0) & (lab[idx[0]] != lab[:, None]) & (lab[:, None] >= 0) & (lab[idx[0]] >= 0)).any())


def formation_rows(worlds, params, S, rate_factor=1.0):
    """Integrate assembled worlds (padded batch) to the window and return one detection row per world."""
    x, th, om, labels = pad(worlds)
    om = om * rate_factor
    x, th, _ = simulate(x, th, om, params, S["dt"], S["horizon_steps"] - S["window_steps"])
    x, th, (xs, ths) = simulate(x, th, om, params, S["dt"], S["window_steps"], S["frame_every"])
    return [{"xs": xs[:, b], "ths": ths[:, b], "x0": x[b], "th0": th[b], "omega": om[b], "labels": labels[b],
             "params": params, "offsets": None} for b in range(len(worlds))]


# ---------------------------------------------------------------- interventions and excitations
def port_members(x, labels, unit):
    members = np.flatnonzero(labels == unit)
    return members[_convex_hull(x[members])]


def mg_dose_rms(dose):
    """M->G doses are zero-mean unit-level kicks of fixed RMS ('rms:<a>'): one controlled size family, so the
    effective (wrapped pairwise) perturbation grows with the dose. A random-size dose is refused."""
    kind, value = dose.split(":")
    if kind != "rms":
        raise ValueError(f"M->G dose must be 'rms:<a>', got {dose!r}")
    return float(value)


def group_runs(row, units, S, params, manifest, rng):
    """All paired runs for one accepted level-2 resonator from its formed state s0. Returns the raw values."""
    iv = manifest["interventions"]
    x0, th0, om, labels = row["x0"], row["th0"], row["omega"], row["labels"]
    M = int(labels.max()) + 1
    all_units = list(range(M))
    g = np.array(units)
    X0 = unit_positions(x0[None], labels, all_units)[0]
    Th0 = unit_phases(th0[None], labels, all_units)[0]
    topology = neighbors(x0[None], Batch(params["intact"], 1))

    # G->M
    probe = unit_kick(rng, len(g), iv["gm_probe_unit_phase_rms"])
    probed = rotate_units(th0, labels, g, probe)
    gm = [("control", c, x0, probed) for c in ("intact",) + GM_CONDITIONS]
    for s in iv["gm_scales"]:
        gm.append((f"dose/{s}", "intact", scale_units(x0, labels, g, s), probed))
        if s == iv["gm_scale"]:
            gm += [("primary", c, scale_units(x0, labels, g, s), probed) for c in GM_CONDITIONS]
    # M->G, downward control, excitations (one 10 T batch)
    mg = [("control", c, x0, th0) for c in ("intact",) + MG_CONDITIONS]
    for dose in iv["mg_doses"]:
        deltas = unit_kick(rng, len(g), mg_dose_rms(dose))
        treated = rotate_units(th0, labels, g, deltas)
        mg.append((f"dose/{dose}", "intact", x0, treated))
        if dose == iv["mg_dose"]:
            mg += [("primary", c, x0, treated) for c in MG_CONDITIONS]
    excited = int(g[rng.integers(len(g))])
    centre = X0[g].mean(0)
    direction = X0[excited] - centre
    direction = direction / max(np.linalg.norm(direction), 1e-12)
    L_exc = radius_of_gyration(x0[labels == excited])
    push = S["push"] * L_exc * direction
    offsets = decouple_offsets(labels, all_units)
    pulse_th = rotate_units(th0, labels, [excited], [S["pulse"]])
    extra = [("pulse", "intact", x0, pulse_th), ("push", "intact", shift_units(x0, labels, [excited], [push]), th0),
             ("decoupled", "intact", x0 + offsets, th0), ("decoupled_pulse", "intact", x0 + offsets, pulse_th)]

    def batch(runs, steps):
        bx = np.array([r[2] for r in runs])
        bt = np.array([r[3] for r in runs])
        topo = tuple(np.repeat(topology[i], len(runs), axis=0) for i in range(3))
        _, _, (xs, ths) = simulate(bx, bt, np.repeat(om[None], len(runs), 0), [params[r[1]] for r in runs],
                                   S["dt"], steps, S["sample_every"], phase_topology=topo)
        return xs, ths

    gxs, gths = batch(gm, S["gm_steps"])
    reference = pair_differences(Th0, g)
    gm_values = {}
    for i, (key, cond, _, _) in enumerate(gm):
        Th = unit_phases(gths[:, i], labels, all_units)
        gm_values[(key, cond)] = gm_statistic(Th, g, reference)
        if (key, cond) == ("control", "intact"):
            # tau2: e-folding of the inter-unit pattern deviation after the unit-phase probe (intact control).
            # Censored at the window length when it never reaches 1/e (a lower bound, counted).
            tau2 = efold(np.sqrt((wrap(pair_differences(Th, g) - reference) ** 2).mean(1)), S["sample_every"] * S["dt"])
            tau2_censored = bool(not np.isfinite(tau2))
            tau2_value = S["gm_steps"] * S["dt"] if tau2_censored else tau2
    runs10 = mg + extra
    mxs, mths = batch(runs10, S["mg_steps"])
    rg0 = radius_of_gyration(X0[g])
    mg_values, series = {}, {}
    for i, (key, cond, _, _) in enumerate(runs10):
        off = offsets if key.startswith("decoupled") else 0.0
        X = unit_positions(mxs[:, i] - off, labels, all_units)
        Th = unit_phases(mths[:, i], labels, all_units)
        if i < len(mg):
            mg_values[(key, cond)] = mg_statistic(X, g, rg0)
        series[(key, cond)] = (X, Th, mxs[:, i] - off, mths[:, i])

    effects = {}
    for (key, cond), v in gm_values.items():
        if key != "control":
            effects[f"g_to_m_{key}/{cond}" if key != "primary" else f"g_to_m/{cond}"] = v - gm_values[("control", cond)]
    for (key, cond), v in mg_values.items():
        if key != "control":
            effects[f"m_to_g_{key}/{cond}" if key != "primary" else f"m_to_g/{cond}"] = v - mg_values[("control", cond)]
    effects["g_to_m/intact"] = effects[f"g_to_m_dose/{iv['gm_scale']}/intact"]
    effects["m_to_g/intact"] = effects[f"m_to_g_dose/{iv['mg_dose']}/intact"]

    # Downward effect: group (intact control) versus the same units decoupled, over the 10 T window.
    Xc, Thc, xc, thc = series[("control", "intact")]
    Xd, Thd, xd, thd = series[("decoupled", "intact")]
    duration = S["mg_steps"] * S["dt"]
    per_unit = []
    for u in g:
        ports = port_members(x0, labels, u)
        members = labels == u
        off_c = wrap(thc[-1, ports] - circular_mean(thc[-1, members]))
        off_d = wrap(thd[-1, ports] - circular_mean(thd[-1, members]))
        natural = float(om[members].mean())
        per_unit.append({
            "unit": int(u), "size": int(members.sum()), "natural_rate": natural,
            "rate_in_group": float((Thc[-1, u] - Thc[0, u]) / duration),
            "rate_alone": float((Thd[-1, u] - Thd[0, u]) / duration),
            "entrainment": abs(float((Thc[-1, u] - Thc[0, u]) / duration) - natural),
            "boundary_shift": float(np.sqrt((wrap(off_c - off_d) ** 2).mean())),
        })
    others = [int(u) for u in g if u != excited]
    pulse = series[("pulse", "intact")]
    transfer_intact = float(np.sqrt((wrap(pulse[1][:, others] - Thc[:, others]) ** 2).mean()))
    dpulse = series[("decoupled_pulse", "intact")]
    transfer_decoupled = float(np.sqrt((wrap(dpulse[1][:, others] - Thd[:, others]) ** 2).mean()))

    coarse = coarse_vs_full(row, g, excited, push, series, S, params["intact"], tau2_value)
    return {
        "units": [int(u) for u in g], "excited_unit": excited, "effects": effects, "tau2": tau2_value, "tau2_censored": tau2_censored,
        "downward_units": per_unit,
        "downward_effect": float(np.mean([p["boundary_shift"] for p in per_unit])),
        "entrainment": float(np.mean([p["entrainment"] for p in per_unit])),
        "emergent_transfer": transfer_intact - transfer_decoupled,
        "transfer_intact": transfer_intact, "transfer_decoupled": transfer_decoupled,
        "coarse": coarse,
    }


def states_at(x, th, om, labels, units, params):
    return [resonator_state(x, th, om, labels, int(u), 0.0, {}, params) for u in units]


def response_error(fT, fX, pT, pX, others, L):
    """RMS wrapped phase error plus RMS position error over L, over the other units and all samples."""
    dT = wrap(fT[:, others] - pT[:, others])
    dX = np.linalg.norm(fX[:, others] - pX[:, others], axis=-1) / L[others]
    return float(np.sqrt((dT ** 2).mean()) + np.sqrt((dX ** 2).mean()))


def relaxation_prediction(times, units, amount, tau):
    """Cheap baseline: each other unit relaxes to an equal share of the excitation, amount / units, with the
    group's own measured inter-unit time tau2 (mean-field redistribution; no ports, no geometry)."""
    share = 1.0 - np.exp(-np.asarray(times) / tau)
    return share[:, None] * (np.asarray(amount, dtype=float) / units)


def coarse_vs_full(row, g, excited, push, series, S, params, tau2):
    """Open-loop coarse predictions against the full model and three cheap baselines; the reopening
    protocol (invariant 8) is run alongside and reported, never scored as the prediction."""
    om, labels = row["omega"], row["labels"]
    others = [k for k, u in enumerate(g) if u != excited]
    e_index = int(np.flatnonzero(g == excited)[0])
    L = np.array([radius_of_gyration(row["x0"][labels == u]) for u in g])
    steps, every = S["mg_steps"], S["sample_every"]
    runs = {}
    for name, key in (("control", ("control", "intact")), ("pulse", ("pulse", "intact")), ("push", ("push", "intact"))):
        X, Th, xs, ths = series[key]
        start = states_at(xs[0], ths[0], om, labels, g, params)
        reopen = (lambda xs=xs, ths=ths: (lambda f: states_at(xs[f], ths[f], om, labels, g, params)))()
        open_loop = c5_coarse.run(start, params, S["dt"], steps, every)
        reopened = c5_coarse.run(start, params, S["dt"], steps, every, reopen)
        align = lambda r: r["theta"] + (Th[0, g] - r["theta"][0])  # the full series' phase branch at t0
        runs[name] = {"full": (X[:, g], Th[:, g]), "open": (open_loop["X"], align(open_loop)),
                      "reopened": (reopened["X"], align(reopened)), "reopens": reopened["reopens"],
                      "flagged": open_loop["flagged"], "work": open_loop["work"] + reopened["work"]}
    times = np.arange(steps // every + 1) * every * S["dt"]
    out = {"excitations": {}, "tau2": tau2}
    for name in ("pulse", "push"):
        fX = runs[name]["full"][0] - runs["control"]["full"][0]
        fT = runs[name]["full"][1] - runs["control"]["full"][1]
        oX = runs[name]["open"][0] - runs["control"]["open"][0]
        oT = runs[name]["open"][1] - runs["control"]["open"][1]
        rX = runs[name]["reopened"][0] - runs["control"]["reopened"][0]
        rT = runs[name]["reopened"][1] - runs["control"]["reopened"][1]
        zero_T, zero_X = np.zeros_like(fT), np.zeros_like(fX)
        if name == "pulse":
            rigid_T, rigid_X = np.full_like(fT, S["pulse"]), zero_X
            relax_T, relax_X = np.repeat(relaxation_prediction(times, len(g), S["pulse"], tau2), len(g), axis=1), zero_X
        else:
            rigid_T, rigid_X = zero_T, zero_X + push
            relax_T = zero_T
            relax_X = np.repeat(relaxation_prediction(times, len(g), push, tau2)[:, None, :], len(g), axis=1)
        errors = {
            "error_coarse": response_error(fT, fX, oT, oX, others, L),
            "error_coarse_reopened": response_error(fT, fX, rT, rX, others, L),
            "error_no_transfer": response_error(fT, fX, zero_T, zero_X, others, L),
            "error_rigid_transfer": response_error(fT, fX, rigid_T, rigid_X, others, L),
            "error_relaxation": response_error(fT, fX, relax_T, relax_X, others, L),
        }
        half = len(fT) // 2
        span = (len(fT) - 1 - half) * every * S["dt"]
        rate_full = float((runs[name]["full"][1][-1] - runs[name]["full"][1][half]).mean() / span)
        rate_coarse = float((runs[name]["open"][1][-1] - runs[name]["open"][1][half]).mean() / span)

        def settle(dTh):
            dev = np.abs(wrap(dTh - dTh[:, [e_index]])).max(1) if name == "pulse" else np.abs(wrap(dTh)).max(1)
            below = np.flatnonzero(dev <= S["t2"]["pattern_tol"])
            return float(times[below[0]]) if len(below) else float(steps * S["dt"])

        out["excitations"][name] = {**errors, "frequency_error": abs(rate_full - rate_coarse),
                                    "recovery_error": abs(settle(fT) - settle(oT)),
                                    "reopens": runs[name]["reopens"], "flagged_samples": runs[name]["flagged"]}
    ex = out["excitations"]
    for base in ("no_transfer", "rigid_transfer", "relaxation"):
        out[f"gain_vs_{base}"] = float(np.mean([ex[n][f"error_{base}"] - ex[n]["error_coarse"] for n in ex]))
    out["reopens"] = int(sum(r["reopens"] for r in runs.values()))
    out["flagged_samples"] = int(sum(r["flagged"] for r in runs.values()))
    n = int((labels >= 0).sum())
    # Pair evaluations, same unit for both: full = N^2 neighbour search + 4 RK4 stages over N x k per step.
    out["work_full_pair_evaluations"] = int(3 * steps * (n * n + 4 * n * params.k))
    out["work_coarse_pair_evaluations"] = int(sum(r["work"] for r in runs.values()))
    return out


# ---------------------------------------------------------------- controls and level-1 re-detection
def control_rows(rows, detections, params, S, static):
    """Decoupled continuations of each intact formed state; imposed candidates from the intact detection."""
    out, groups = [], []
    for row, det in zip(rows, detections):
        M = det["M"]
        offsets = decouple_offsets(row["labels"], list(range(M)))
        om = np.zeros_like(row["omega"]) if static else row["omega"]
        x, th, (xs, ths) = simulate((row["x0"] + offsets)[None], row["th0"][None], om[None], params, S["dt"],
                                    S["window_steps"], S["frame_every"])
        out.append({"xs": xs[:, 0], "ths": ths[:, 0], "x0": x[0], "th0": th[0], "omega": om, "labels": row["labels"],
                    "params": params, "offsets": offsets})
        g = [c["units"] for c in det["candidates"]]
        if not g:
            labels = components(det["X"][-1], S["t2"]["link_factor"], np.ones((M, M), bool))
            g = [list(np.flatnonzero(labels == c)) for c in np.unique(labels) if (labels == c).sum() >= S["t2"]["min_size"]]
        groups.append(g)
    return out, groups


def level1_check(world, c4m, params, entropy, index):
    """Every unit, alone with its rate (decoupled), is an accepted C4 resonator under the frozen C4 detector."""
    x, th, om, labels = world
    units = sorted(int(u) for u in np.unique(labels))
    off = decouple_offsets(labels, units)
    dt, frame = c4m["integration"]["dt"], c4m["detector"]["frame_dt"]
    _, _, (xs, ths) = simulate((x + off)[None], th[None], om[None], params, dt, int(round(c4m["detector"]["window"] / dt)),
                               int(round(frame / dt)))
    rng = [rng_for(entropy, 4, index)]
    found = c4_detect(xs, ths, om[None], params, dt, frame, c4m["detector"], rng)[0]
    accepted = [set(int(m) for m in c["members"]) for c in found if c["accepted"]]
    return [any(a == set(np.flatnonzero(labels == u).tolist()) for a in accepted) for u in units]


# ---------------------------------------------------------------- timescales (T = tau2 / tau1)
def efold(deviation, sample_dt):
    """First time the deviation falls to 1/e of its initial value (inf if it never does)."""
    below = np.flatnonzero(np.asarray(deviation) <= deviation[0] / np.e)
    return float(below[0] * sample_dt) if len(below) else float("inf")


def tau1(rows, params, S, manifest, entropy, indices):
    """Internal relaxation of every unit, alone (decoupled from s0): a zero-mean element phase kick
    (RMS = the C4 probe) inside each unit versus the unkicked decoupled control. One value per unit."""
    tm = manifest["normalization"]
    every = int(round(tm["tau_sample_dt"] / S["dt"]))
    steps = int(round(tm["tau1_horizon"] / S["dt"]))
    bx, bt, bw, meta = [], [], [], []
    for row, i in zip(rows, indices):
        M = int(row["labels"].max()) + 1
        off = decouple_offsets(row["labels"], list(range(M)))
        rng = rng_for(entropy, 10, i)
        kicked = row["th0"].copy()
        for u in range(M):
            m = row["labels"] == u
            kicked[m] += unit_kick(rng, int(m.sum()), tm["tau_kick_rms"])
        bx += [row["x0"] + off] * 2
        bt += [row["th0"], kicked]
        bw += [row["omega"]] * 2
        meta.append(M)
    _, _, (xs, ths) = simulate(np.array(bx), np.array(bt), np.array(bw), params, S["dt"], steps, every)
    out = []
    for n, (row, M) in enumerate(zip(rows, meta)):
        per = []
        for u in range(M):
            members = np.flatnonzero(row["labels"] == u)
            dev = np.sqrt((wrap(pair_differences(ths[:, 2 * n + 1], members) - pair_differences(ths[:, 2 * n], members)) ** 2).mean(1))
            per.append(efold(dev, every * S["dt"]))
        out.append(per)
    return out


# ---------------------------------------------------------------- one chunk of worlds
def run_worlds(manifest, entropy, indices, templates):
    c4m = load_c4(manifest)
    params = model_params(c4m)
    S = settings(manifest, c4m)
    worlds = build_worlds(manifest, templates, entropy, indices)
    rows = formation_rows(worlds, params["intact"], S)
    det = detect_rows(rows, S, [rng_for(entropy, 7, i) for i in indices])
    sweep = {}
    for factor in manifest["worlds"]["spread_sweep"]:
        if factor == 1.0:
            sweep[str(factor)] = [d["candidates"] for d in det]
            continue
        srows = formation_rows(worlds, params["intact"], S, factor)
        sweep[str(factor)] = [d["candidates"] for d in detect_rows(srows, S, [rng_for(entropy, 7, i) for i in indices])]
    controls = {}
    for name, static in (("decoupled_spread", False), ("decoupled_static", True)):
        crows, groups = control_rows(rows, det, params["intact"], S, static)
        controls[name] = detect_rows(crows, S, [rng_for(entropy, 9, i) for i in indices], groups)
    taus = tau1(rows, params["intact"], S, manifest, entropy, indices)
    records = []
    for b, i in enumerate(indices):
        row, d = rows[b], det[b]
        accepted = [c for c in d["candidates"] if c["accepted"]]
        groups = [group_runs(row, c["units"], S, params, manifest, rng_for(entropy, 6, i, n)) for n, c in enumerate(accepted)]
        touching = contact(row["x0"], row["labels"], params["intact"])
        # Disclosure: does the frozen C4 component rule (close and locked elements) see each accepted group
        # as one single level-1 component? (Expected yes: geometric contact plus locking; the level-2 claim
        # rests on criterion 6 and timescale separation, not on the C4 view.)
        keep = row["labels"] >= 0
        c4_labels = components(row["xs"][-1][keep], c4m["detector"]["link_factor"],
                               locked_pairs(row["ths"][:, keep], c4m["detector"]["lock_std"]))
        lab = row["labels"][keep]
        single = [len(set(c4_labels[np.isin(lab, c["units"])])) == 1 for c in accepted]
        records.append({
            "seed_index": int(i),
            "elements": int((row["labels"] >= 0).sum()),
            "unit_sizes": [int((row["labels"] == u).sum()) for u in range(d["M"])],
            "unit_rates": [float(row["omega"][row["labels"] == u][0]) for u in range(d["M"])],
            "unit_validity": d["validity"],
            "tau1": taus[b],
            "candidates": [{k: c[k] for k in ("units", "stats", "failed", "accepted")} for c in d["candidates"]],
            "outcome": outcome(d["candidates"], touching),
            "contact": touching,
            "groups": groups,
            "c4_single_component": single,
            "spread_sweep": {f: {"formed": any(c["accepted"] for c in sweep[f][b]),
                                 "outcome": outcome(sweep[f][b], touching)} for f in sweep},
            "controls": {name: [{k: c[k] for k in ("units", "stats", "failed", "accepted")} for c in controls[name][b]["candidates"]]
                         for name in controls},
            "level1_redetected": level1_check(worlds[b], c4m, params["intact"], entropy, i),
        })
    return records


def harvest_templates(manifest, entropy, worlds):
    c4m = load_c4(manifest)
    params = model_params(c4m)["intact"]
    count = harvest_count(manifest, worlds)
    return harvest(c4m, params, entropy, list(range(count)), tuple(manifest["level1"]["size_range"]))


# ---------------------------------------------------------------- statistics, endpoints, verdicts
def margin_verdict(summary, margin, min_worlds):
    """Rows: INCONCLUSIVE below min_worlds; FAIL if the CI upper bound < margin; PASS if the lower bound > margin."""
    if summary["ci"] is None or summary["n_worlds"] < min_worlds:
        return "INCONCLUSIVE"
    if summary["ci"][1] < margin:
        return "FAIL"
    if summary["ci"][0] > margin:
        return "PASS"
    return "INCONCLUSIVE"


def coarse_verdict(gains, min_worlds):
    """Rows over every baseline's gain summary: INCONCLUSIVE below min_worlds; FAIL if any gain CI lies below 0
    (the coarse law is worse than a cheap baseline); PASS if every gain CI lies above 0; INCONCLUSIVE otherwise."""
    if any(g["ci"] is None or g["n_worlds"] < min_worlds for g in gains):
        return "INCONCLUSIVE"
    if any(g["ci"][1] < 0 for g in gains):
        return "FAIL"
    if all(g["ci"][0] > 0 for g in gains):
        return "PASS"
    return "INCONCLUSIVE"


def separation_verdict(summary, min_worlds):
    """Timescale separation tau2 / tau1: INCONCLUSIVE below min_worlds; FAIL if the CI lies below 1 (units relax
    together no slower than within, i.e. one resonator); PASS if it lies above 1; INCONCLUSIVE otherwise."""
    if summary["ci"] is None or summary["n_worlds"] < min_worlds:
        return "INCONCLUSIVE"
    if summary["ci"][1] < 1.0:
        return "FAIL"
    if summary["ci"][0] > 1.0:
        return "PASS"
    return "INCONCLUSIVE"


def control_verdict(rows):
    tested = sum(len(r) for r in rows)
    accepted = sum(c["accepted"] for r in rows for c in r)
    rejections = {k: sum(k in c["failed"] for r in rows for c in r) for k in CRITERIA}
    verdict = "FAIL" if accepted else "PASS" if tested else "NOT_TESTED"
    return {"candidates": tested, "accepted": accepted, "rejections_by_criterion": rejections, "verdict": verdict}


def evaluate(records, pool, manifest, S, rng):
    rules, resamples = manifest["verdict_rules"], manifest["statistics"]["bootstrap_resamples"]
    min_worlds = rules["min_worlds_for_verdict"]
    worlds = records
    formed_flags = [any(c["accepted"] for c in w["candidates"]) for w in worlds]
    formed = sum(formed_flags)
    formation = {"worlds": len(worlds), "formed": formed, "fraction": formed / len(worlds),
                 "wilson_95": wilson(formed, len(worlds))}
    formation["verdict"] = "PASS" if formation["fraction"] >= rules["formation_min_fraction"] and formed >= min_worlds else "FAIL"
    outcomes = {k: sum(w["outcome"] == k for w in worlds) for k in ("FORMED", "MERGED", "DRIFTING", "APART", "OTHER")}
    failures = {k: sum(k in c["failed"] for w in worlds for c in w["candidates"]) for k in CRITERIA}
    sweep = {f: {"formed": sum(w["spread_sweep"][f]["formed"] for w in worlds), "worlds": len(worlds)}
             for f in worlds[0]["spread_sweep"]} if worlds else {}

    def per_world(fn):
        return [float(np.mean([fn(g) for g in w["groups"]])) if w["groups"] else None for w in worlds]

    def effect(key):
        return summarize(per_world(lambda g: g["effects"][key]), rng, resamples)

    iv = manifest["interventions"]
    causality = {}
    for name, ablation in (("g_to_m", "no_geometry_to_mode"), ("m_to_g", "no_mode_to_geometry")):
        intact, ablated = effect(f"{name}/intact"), effect(f"{name}/{ablation}")
        causality[name] = {"intact": intact, "ablated": {"condition": ablation, **ablated},
                           "verdict": causality_verdict(intact, ablated, rules["ablation_vanish_fraction"], min_worlds)}
    dose = {}
    for name, labels in (("g_to_m", [str(s) for s in iv["gm_scales"]]), ("m_to_g", list(iv["mg_doses"]))):
        per_dose = [effect(f"{name}_dose/{label}/intact") for label in labels]
        difference = summarize(per_world(lambda g: g["effects"][f"{name}_dose/{labels[-1]}/intact"]
                                         - g["effects"][f"{name}_dose/{labels[0]}/intact"]), rng, resamples)
        dose[name] = {"doses": dict(zip(labels, per_dose)), "highest_minus_lowest": difference,
                      "verdict": dose_response_verdict(per_dose, difference, min_worlds)}
    dose["verdict"] = ("FAIL" if any(dose[n]["verdict"] == "FAIL" for n in ("g_to_m", "m_to_g")) else
                       "PASS" if all(dose[n]["verdict"] == "PASS" for n in ("g_to_m", "m_to_g")) else "INCONCLUSIVE")
    channels = {c: effect(f"g_to_m/{c}") for c in ("no_distance_weight", "frozen_topology")}
    for c in channels:
        base = causality["g_to_m"]["intact"]["mean"]
        channels[c]["fraction_of_intact"] = channels[c]["mean"] / base if channels[c]["mean"] is not None and base else None
    channels["verdict"] = "REPORTED"
    margin = rules["meaningful_margin"]
    downward = summarize(per_world(lambda g: g["downward_effect"]), rng, resamples)
    downward_e = {"boundary_shift": downward, "entrainment": summarize(per_world(lambda g: g["entrainment"]), rng, resamples),
                  "margin": margin, "verdict": margin_verdict(downward, margin, min_worlds)}
    transfer = summarize(per_world(lambda g: g["emergent_transfer"]), rng, resamples)
    emergent = {"transfer": transfer, "margin": margin, "verdict": margin_verdict(transfer, margin, min_worlds)}
    bounds = {"state_error_position": manifest["effective_state_bounds"]["state_error_position"],
              "state_error_size": manifest["effective_state_bounds"]["state_error_size"],
              "state_error_frequency": manifest["effective_state_bounds"]["state_error_frequency_level1"] / S["T"]}
    errors = [{k: c["stats"][k] for k in bounds} for w in worlds for c in w["candidates"] if c["accepted"]]
    within = sum(all(e[k] <= bounds[k] for k in bounds) for e in errors)
    fraction = within / len(errors) if errors else None
    effective = {"units": len(errors), "within_bounds": within, "fraction_within_bounds": fraction, "bounds": bounds,
                 "worst": {k: max((e[k] for e in errors), default=None) for k in bounds},
                 "verdict": ("INCONCLUSIVE" if formed < min_worlds or not errors else
                             "PASS" if fraction >= rules["effective_state_min_fraction"] else "FAIL")}
    gains = {b: summarize(per_world(lambda g, b=b: g["coarse"][f"gain_vs_{b}"]), rng, resamples)
             for b in ("no_transfer", "rigid_transfer", "relaxation")}
    excitations = [g["coarse"] for w in worlds for g in w["groups"]]
    reopened = sum(e["excitations"][n]["reopens"] > 0 for e in excitations for n in e["excitations"])
    flagged = sum(e["excitations"][n]["flagged_samples"] > 0 for e in excitations for n in e["excitations"])
    total_exc = sum(len(e["excitations"]) for e in excitations)
    coarse = {**{f"gain_vs_{b}": v for b, v in gains.items()},
              "reopened_protocol_error": summarize(per_world(lambda g: np.mean([e["error_coarse_reopened"] for e in g["coarse"]["excitations"].values()])), rng, resamples),
              "open_loop_error": summarize(per_world(lambda g: np.mean([e["error_coarse"] for e in g["coarse"]["excitations"].values()])), rng, resamples),
              "excitations_flagged_invalid": flagged,
              "frequency_error": summarize(per_world(lambda g: np.mean([e["frequency_error"] for e in g["coarse"]["excitations"].values()])), rng, resamples),
              "recovery_error": summarize(per_world(lambda g: np.mean([e["recovery_error"] for e in g["coarse"]["excitations"].values()])), rng, resamples),
              "reopened_excitations": reopened, "excitations": total_exc,
              "reopen_rate": reopened / total_exc if total_exc else None,
              "work_full_pair_evaluations": sum(e["work_full_pair_evaluations"] for e in excitations),
              "work_coarse_pair_evaluations": sum(e["work_coarse_pair_evaluations"] for e in excitations),
              "verdict": coarse_verdict(list(gains.values()), min_worlds)}
    def ratio(w, g):
        t1 = np.mean([w["tau1"][u] for u in g["units"]])
        return g["tau2"] / t1
    separation = summarize(per_world_w(worlds, ratio), rng, resamples)
    censored = sum(g["tau2_censored"] for w in worlds for g in w["groups"])
    timescale = {"ratio": separation, "tau2_censored_groups": censored,
                 "groups": sum(len(w["groups"]) for w in worlds), "verdict": separation_verdict(separation, min_worlds)}
    c4_single = sum(c for w in worlds for c in w.get("c4_single_component", []))
    parts = [{"seed_index": w["seed_index"], "candidate": n, "units": c["units"], "accepted": c["accepted"],
              "unit_validity": [w["unit_validity"][u] for u in c["units"]]} for w in worlds for n, c in enumerate(w["candidates"])]
    used = [ok for w in worlds for ok in w["level1_redetected"]]
    level1 = {**pool, "units_used": len(used), "units_redetected": int(sum(used)),
              "verdict": "PASS" if used and all(used) else "FAIL"}
    return {
        "level1_pool": level1,
        "formation_l2": formation,
        "formation_outcomes": {"counts": outcomes, "candidate_failures": failures,
                               "accepted_groups_one_c4_component": c4_single,
                               "accepted_groups": sum(len(w["groups"]) for w in worlds), "verdict": "REPORTED"},
        "formation_vs_spread": {"by_factor": sweep, "verdict": "REPORTED"},
        "not_independent": control_verdict([w["controls"]["decoupled_spread"] for w in worlds]),
        "not_a_clump_l2": control_verdict([w["controls"]["decoupled_static"] for w in worlds]),
        "g_to_m_l2": causality["g_to_m"],
        "m_to_g_l2": causality["m_to_g"],
        "dose_response_l2": dose,
        "g_to_m_channels_l2": channels,
        "parts_alive": {"candidates": parts, "verdict": "REPORTED"},
        "downward_effect": downward_e,
        "emergent_transfer": emergent,
        "effective_state_l2": effective,
        "coarse_vs_full": coarse,
        "timescale_separation": timescale,
    }


def per_world_w(worlds, fn):
    """Per-world mean over its accepted groups of fn(world, group); None for worlds without one."""
    return [float(np.mean([fn(w, g) for g in w["groups"]])) if w["groups"] else None for w in worlds]


def hypothesis_verdicts(e):
    """The registered truth tables (manifest verdict_rules.truth_table), rows in order.

    H-M (level 2):
      1. g_to_m_l2, m_to_g_l2 or dose_response_l2 is FAIL               -> NOT_SUPPORTED
      2. formation_l2 PASS and those three PASS                         -> SUPPORTED_WITHIN_SCOPE
      3. otherwise                                                      -> INCONCLUSIVE
    H-C first transition:
      1. formation_l2 Wilson 95% upper bound < 0.25                     -> NOT_SUPPORTED
      2. downward_effect, emergent_transfer, effective_state_l2,
         coarse_vs_full or timescale_separation is FAIL                 -> NOT_SUPPORTED
      3. H-M SUPPORTED_WITHIN_SCOPE and those five PASS                 -> SUPPORTED_WITHIN_SCOPE
      4. otherwise                                                      -> INCONCLUSIVE
    """
    causal = (e["g_to_m_l2"]["verdict"], e["m_to_g_l2"]["verdict"], e["dose_response_l2"]["verdict"])
    if "FAIL" in causal:
        h_m = "NOT_SUPPORTED"
    elif e["formation_l2"]["verdict"] == "PASS" and causal == ("PASS", "PASS", "PASS"):
        h_m = "SUPPORTED_WITHIN_SCOPE"
    else:
        h_m = "INCONCLUSIVE"
    composition = (e["downward_effect"]["verdict"], e["emergent_transfer"]["verdict"],
                   e["effective_state_l2"]["verdict"], e["coarse_vs_full"]["verdict"],
                   e["timescale_separation"]["verdict"])
    upper = e["formation_l2"]["wilson_95"][1]
    if upper < 0.25:
        h_c = "NOT_SUPPORTED"
    elif "FAIL" in composition:
        h_c = "NOT_SUPPORTED"
    elif h_m == "SUPPORTED_WITHIN_SCOPE" and composition == ("PASS",) * 5:
        h_c = "SUPPORTED_WITHIN_SCOPE"
    else:
        h_c = "INCONCLUSIVE"
    return {"H-M_level2": h_m, "H-C_first_transition": h_c}


# ---------------------------------------------------------------- numerical checks and rule audit
def numerical_checks(manifest, templates, entropy):
    """On the first world: RK4 order (held neighbours), switching-limited dt error, equivariance
    (permutation, rotation, translation, global phase), unit relabelling, and exact decoupling."""
    c4m = load_c4(manifest)
    nc, params = c4m["numerical_checks"], model_params(c4m)["intact"]
    dt = c4m["integration"]["dt"]
    x, th, om, labels = build_worlds(manifest, templates, entropy, [0])[0]
    x, th, _ = simulate(x[None], th[None], om[None], params, dt, int(round(nc["settle_time"] / dt)))
    rng = rng_for(entropy, 3)
    th = th + unit_kick(rng, th.shape[1], c4m["interventions"]["gm_probe_phase_rms"])
    om = om[None]

    def run(x_, th_, om_, step, held):
        return simulate(x_, th_, om_, params, step, int(round(nc["horizon"] / step)), hold_neighbors=held)[:2]

    def diff(a, b):
        return float(max(np.abs(a[0] - b[0]).max(), np.abs(a[1] - b[1]).max()))

    held = {s: run(x, th, om, s, True) for s in (dt, dt / 2, dt / 4)}
    full = {s: run(x, th, om, s, False) for s in (dt, dt / 4)}
    he, hh = diff(held[dt], held[dt / 4]), diff(held[dt / 2], held[dt / 4])
    perm = rng.permutation(x.shape[1])
    a = rng.uniform(0, 2 * np.pi)
    rot = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    shift = rng.normal(size=2) * 10
    moved = run(x[:, perm] @ rot.T + shift, th[:, perm] + 1.0, om[:, perm], dt, False)
    equiv = float(max(np.abs(moved[0] - (full[dt][0][:, perm] @ rot.T + shift)).max(),
                      np.abs(wrap(moved[1] - full[dt][1][:, perm] - 1.0)).max()))
    M = int(labels.max()) + 1
    relabel = rng.permutation(M)
    X = unit_positions(full[dt][0], labels, list(range(M)))
    Xr = unit_positions(full[dt][0], relabel[labels], list(range(M)))
    relabel_error = float(np.abs(Xr[:, relabel] - X).max())
    off = decouple_offsets(labels, list(range(M)))
    dec = run(x + off[None], th, om, dt, False)
    alone_error = 0.0
    for u in range(M):
        m = labels == u
        solo = run(x[:, m], th[:, m], om[:, m], dt, False)
        alone_error = max(alone_error, float(np.abs(dec[0][:, m] - off[None, m] - solo[0]).max()),
                          float(np.abs(dec[1][:, m] - solo[1]).max()))
    out = {"held_dt_error": he, "held_dt_half_error": hh, "held_order_ratio": he / max(hh, 1e-300),
           "switching_dt_error": diff(full[dt], full[dt / 4]), "equivariance_error": equiv,
           "unit_relabel_error": relabel_error, "decoupled_vs_alone_error": alone_error}
    tol = nc["equivariance_tolerance"]
    out["verdict"] = "PASS" if (he <= nc["held_dt_tolerance"] and out["held_order_ratio"] >= nc["min_order_ratio"]
                                and out["switching_dt_error"] <= nc["switching_dt_tolerance"] and equiv <= tol
                                and relabel_error <= tol and alone_error <= manifest["numerical_checks"]["decoupling_tolerance"]) else "FAIL"
    return out


def same_rule_audit(manifest):
    """Level-2 thresholds equal the frozen C4 thresholds except times (x T) and the frequency tolerance (/ T)."""
    c4m = load_c4(manifest)
    S = settings(manifest, c4m)
    t1, t2, T = S["t1"], S["t2"], S["T"]
    rows = {}
    for key, v1 in t1.items():
        v2 = t2[key]
        expected = v1 * T if key in ("window", "frame_dt", "recovery_time") else v1 / T if key == "freq_tol" else v1
        rows[key] = {"level1": v1, "level2": v2, "rule_ok": v2 == expected}
    tau = manifest["normalization"]
    return {"T": T, "tau1": tau["tau1"], "tau2": tau["tau2"], "thresholds": rows,
            "verdict": "PASS" if all(r["rule_ok"] for r in rows.values()) else "FAIL"}
