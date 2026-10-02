"""C6 development pilot (NOT evidence; scratch code outside the repo; pilot entropy only).

Measures, before any registration: level-2 harvest yield, re-acceptance alone, tau2 alone; level-3 formation
with the C5 detector functions one level up (thresholds scaled by the cumulative factor C3), recursive
criterion 6, recovery with the original group; tau3, C3, upward and group-pulse transfer; cost per world.
"""
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

ROOT = "/Users/new/RiderProjects/ai_RPG_test"
sys.path.insert(0, ROOT)
from geomind import c5_experiment as E  # noqa: E402
from geomind.c4_detect import _convex_hull, circular_mean, pair_differences, radius_of_gyration, window_statistics  # noqa: E402
from geomind.c4_experiment import model_params, wilson  # noqa: E402
from geomind.c4_model import simulate, wrap  # noqa: E402
from geomind.c5_compose import pad, rotate_units, shift_units, unit_kick  # noqa: E402
from geomind.c5_detect import candidates, criteria_checks, level2_thresholds, outcome, recovery  # noqa: E402
from geomind.c5_detect import unit_kick as det_kick  # noqa: E402
from geomind.c5_units import clip_convex, harvest, polygon_area, unit_phases, unit_positions, unit_validity  # noqa: E402

ENT = 44444
JOBS = 8
C5M = json.loads(open(ROOT + "/experiments/c5_manifest.json").read())
C4M = E.load_c4(C5M)
P = model_params(C4M)
S = E.settings(C5M, C4M)
DT, T1, T2, C2 = S["dt"], S["t1"], S["t2"], S["T"]
MAX_OV = S["max_hull_overlap"]
steps = lambda t: int(round(t / DT))


# ---------------------------------------------------------------- level 1 and level 2 (frozen C5 functions)
def w_harvest(idx):
    return harvest(C4M, P["intact"], ENT, idx, (6, 16))[0]


def w_level2(args):
    templates, idx = args
    worlds, _ = E.build_worlds(C5M, templates, ENT, idx)
    rows = E.formation_rows(worlds, P["intact"], S)
    det = E.detect_rows(rows, S, [E.rng_for(ENT, 7, i) for i in idx])
    records, groups = [], []
    for b, i in enumerate(idx):
        row, d = rows[b], det[b]
        acc = [c for c in d["candidates"] if c["accepted"]]
        records.append({"world": int(i), "outcome": outcome(d["candidates"], E.contact(row["x0"], row["labels"], P["intact"])),
                        "accepted": len(acc)})
        for c in acc:
            units = sorted(c["units"])
            mask = np.isin(row["labels"], units)
            relab = np.searchsorted(units, row["labels"][mask])
            x = row["x0"][mask]
            X1 = np.array([x[relab == k].mean(0) for k in range(len(units))])
            groups.append({"x": x - X1.mean(0), "th": row["th0"][mask].copy(), "om": row["omega"][mask].copy(),
                           "units": relab, "src": int(i), "L2": radius_of_gyration(X1)})
    if not groups:
        return records, []
    # alone: re-acceptance (harvest filter), isolated rate, tau2 after a unit-phase probe
    px, pth, pom, plab = pad([(g["x"], g["th"], g["om"], g["units"]) for g in groups])
    x, th, (xs, ths) = simulate(px, pth, pom, P["intact"], DT, S["window_steps"], S["frame_every"])
    rows_iso = [{"xs": xs[:, b], "ths": ths[:, b], "x0": x[b], "th0": th[b], "omega": pom[b], "labels": plab[b],
                 "params": P["intact"], "offsets": None} for b in range(len(groups))]
    det_iso = E.detect_rows(rows_iso, S, [E.rng_for(ENT, 17, g["src"], n) for n, g in enumerate(groups)])
    probes = []
    for n, g in enumerate(groups):
        k = int(g["units"].max()) + 1
        g["alone_ok"] = any(c["accepted"] and sorted(c["units"]) == list(range(k)) for c in det_iso[n]["candidates"])
        Th = det_iso[n]["Theta"]
        g["rate_iso"] = float((Th[-1] - Th[0]).mean() / ((len(Th) - 1) * T2["frame_dt"]))
        rng = E.rng_for(ENT, 18, g["src"], n)
        probes.append(rotate_units(pth[n], plab[n], list(range(k)), unit_kick(rng, k, 0.3)))
    bx = np.concatenate([px, px])
    bt = np.concatenate([pth, np.array(probes)])
    bw = np.concatenate([pom, pom])
    _, _, (pxs, pths) = simulate(bx, bt, bw, P["intact"], DT, S["gm_steps"], S["sample_every"])
    G = len(groups)
    for n, g in enumerate(groups):
        k = int(g["units"].max()) + 1
        u = list(range(k))
        a = unit_phases(pths[:, n], plab[n], u)
        b = unit_phases(pths[:, G + n], plab[n], u)
        dev = np.sqrt((wrap(pair_differences(b, u) - pair_differences(a, u)) ** 2).mean(1))
        g["tau2"] = E.efold(dev, S["sample_every"] * DT)
    return records, groups


# ---------------------------------------------------------------- level 3
def assemble3(gs, rng, R3, delta3):
    """Sequential placement: each group in turn, uniform in the disk, rejected individually until no element is
    closer than 0.6 to an element of an already placed group."""
    xs, ths, oms, ul, gl, uoff = [], [], [], [], [], 0
    placed = np.zeros((0, 2))
    for g, t in enumerate(gs):
        a = rng.uniform(0, 2 * np.pi)
        R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
        body = t["x"] @ R.T
        if R3 <= 0 and len(placed):
            # contact placement: approach the cluster centre from a random direction, stop at the 0.6 element gap
            phi = rng.uniform(0, 2 * np.pi)
            u = np.array([np.cos(phi), np.sin(phi)])
            centre = placed.mean(0)
            dist = 50.0
            while dist > 0:
                cand = body + centre + dist * u
                if np.linalg.norm(cand[:, None] - placed[None], axis=-1).min() < 0.6:
                    cand = body + centre + (dist + 0.02) * u
                    break
                dist -= 0.02
            placed = np.vstack([placed, cand])
            xs.append(cand)
            ths.append(t["th"] + rng.uniform(-np.pi, np.pi))
            oms.append(t["om"] - t["rate_iso"] + rng.uniform(-delta3, delta3))
            ul.append(t["units"] + uoff)
            gl.append(np.full(len(t["th"]), g))
            uoff += int(t["units"].max()) + 1
            continue
        for _ in range(200000):
            r, phi = R3 * np.sqrt(rng.random()), rng.uniform(0, 2 * np.pi)
            cand = body + [r * np.cos(phi), r * np.sin(phi)]
            if not len(placed) or np.linalg.norm(cand[:, None] - placed[None], axis=-1).min() >= 0.6:
                break
        else:
            raise RuntimeError("no placement")
        placed = np.vstack([placed, cand])
        xs.append(cand)
        ths.append(t["th"] + rng.uniform(-np.pi, np.pi))
        oms.append(t["om"] - t["rate_iso"] + rng.uniform(-delta3, delta3))
        ul.append(t["units"] + uoff)
        gl.append(np.full(len(t["th"]), g))
        uoff += int(t["units"].max()) + 1
    return np.concatenate(xs), np.concatenate(ths), np.concatenate(oms), np.concatenate(ul), np.concatenate(gl)


def series(xs, ths, ulab, g_of_u):
    nU, nG = len(g_of_u), int(g_of_u.max()) + 1
    X1 = unit_positions(xs, ulab, list(range(nU)))
    Th1 = unit_phases(ths, ulab, list(range(nU)))
    X2 = np.stack([X1[:, g_of_u == g].mean(1) for g in range(nG)], 1)
    Th2 = np.unwrap(np.stack([circular_mean(Th1[:, g_of_u == g], axis=1) for g in range(nG)], 1), axis=0)
    return X1, Th1, X2, Th2


def hulls(xf, ulab, nU):
    out = []
    for u in range(nU):
        p = xf[ulab == u]
        out.append(p[_convex_hull(p)])
    return out


def union_overlap(xs, ulab, g_of_u):
    """Per group, worst over frames of: area of its level-1 hulls covered by another group's level-1 hulls / its own
    level-1 hull area (pairwise clipping sums; an upper-bound-like proxy for the union rule)."""
    nU, nG = len(g_of_u), int(g_of_u.max()) + 1
    worst = np.zeros(nG)
    for f in range(len(xs)):
        H = hulls(xs[f], ulab, nU)
        area = np.array([polygon_area(h) for h in H])
        for A in range(nG):
            ua = np.flatnonzero(g_of_u == A)
            own = area[ua].sum()
            for B in range(nG):
                if B == A:
                    continue
                ub = np.flatnonzero(g_of_u == B)
                inter = sum(polygon_area(clip_convex(H[a], H[b])) for a in ua for b in ub if area[a] > 0 and area[b] > 0)
                worst[A] = max(worst[A], inter / own if own > 0 else 1.0)
    return worst


def w_level3(args):
    try:
        return _level3(args)
    except Exception as exc:  # recorded, never hidden
        import traceback
        return {"world": args[1], "error": repr(exc), "trace": traceback.format_exc(), "outcome": "ERROR", "candidates": [], "N": 0, "seconds": 0.0}


def _level3(args):
    gs, j, C3, sR, R2scale = args
    t0 = time.perf_counter()
    rng = E.rng_for(ENT, 30, j)
    R3 = sR * 2.5 * R2scale if sR > 0 else 0.0
    delta3 = 0.03 * C2 / C3
    x, th, om, ulab, glab = assemble3(gs, rng, R3, delta3)
    nU = int(ulab.max()) + 1
    g_of_u = np.array([glab[ulab == u][0] for u in range(nU)])
    t3 = level2_thresholds(T1, C3)
    fe = steps(t3["frame_dt"])
    pre = steps(100 * C3) - steps(t3["window"])
    x1, th1, _ = simulate(x[None], th[None], om[None], P["intact"], DT, pre)
    x1, th1, (xs, ths) = simulate(x1, th1, om[None], P["intact"], DT, steps(t3["window"]), fe)
    xs, ths, x0, th0 = xs[:, 0], ths[:, 0], x1[0], th1[0]
    X1, Th1, X2, Th2 = series(xs, ths, ulab, g_of_u)
    # criterion 6, recursive
    v1 = unit_validity(xs, ths, ulab, list(range(nU)), t3["frame_dt"], T1["link_factor"])
    ok1 = [r["shape_cv"] <= T1["shape_cv"] and r["lock_std"] <= T1["lock_std"] and r["freq_change"] <= T1["freq_tol"]
           and r["pattern_change"] <= T1["pattern_tol"] and r["hull_overlap"] <= MAX_OV for r in v1]
    ones = np.ones((nU, nU), bool)
    uov = union_overlap(xs, ulab, g_of_u)
    v2, ok2 = [], []
    for g in range(int(g_of_u.max()) + 1):
        units = np.flatnonzero(g_of_u == g)
        s = window_statistics(X1, Th1, units, t3["frame_dt"], T1["link_factor"], ones)
        r = {k: s[k] for k in ("shape_cv", "lock_std", "freq_change", "pattern_change")}
        r["union_overlap"] = float(uov[g])
        r["units_ok"] = int(sum(ok1[u] for u in units))
        r["units"] = int(len(units))
        r["own_ok"] = bool(r["shape_cv"] <= T2["shape_cv"] and r["lock_std"] <= T2["lock_std"]
                           and r["freq_change"] <= T2["freq_tol"] and r["pattern_change"] <= T2["pattern_tol"])
        r["ok"] = bool(r["own_ok"] and r["union_overlap"] <= MAX_OV and r["units_ok"] == r["units"])
        v2.append(r)
        ok2.append(r["ok"])
    found, locked = candidates(X2, Th2, t3["frame_dt"], t3)
    cands, pend = [], []
    for units, stats in found:
        stats["parts_alive"] = all(ok2[g] for g in units)
        dX, dTh = det_kick(X2[-1], Th2[-1], units, rng, t3)
        pend.append((shift_units(x0, glab, units, dX), rotate_units(th0, glab, units, dTh)))
        cands.append({"units": [int(u) for u in units], "stats": stats})
    if pend:
        bx = np.array([x0] + [p[0] for p in pend])
        bt = np.array([th0] + [p[1] for p in pend])
        bw = np.repeat(om[None], len(bx), 0)
        ex, et, _ = simulate(bx, bt, bw, P["intact"], DT, steps(t3["recovery_time"]))
        _, _, cX, cT = series(ex[0][None], et[0][None], ulab, g_of_u)
        for n, c in enumerate(cands):
            _, _, kX, kT = series(ex[n + 1][None], et[n + 1][None], ulab, g_of_u)
            c["stats"].update(recovery(np.array(c["units"]), cX[0], cT[0], kX[0], kT[0], locked, t3))
    for c in cands:
        checks = criteria_checks(c["stats"], t3)
        c["failed"] = [k for k, ok in checks.items() if not ok]
        c["accepted"] = not c["failed"]
    contact = E.contact(x0, glab, P["intact"])
    rec = {"world": j, "N": int(len(x)), "sR": sR, "C3": C3, "outcome": outcome(cands, contact), "contact": contact,
           "candidates": [{"units": c["units"], "failed": c["failed"], "accepted": c["accepted"],
                           **{k: float(c["stats"][k]) for k in ("lock_std", "shape_cv", "freq_change", "pattern_change",
                                                                "membership_jaccard", "recovery_jaccard", "recovery_pattern_error")}}
                          for c in cands],
           "level2_validity": v2, "level1_ok": int(sum(ok1)), "level1_units": nU}
    acc = [c for c in cands if c["accepted"]]
    if acc:
        g = np.array(acc[0]["units"])
        r2 = E.rng_for(ENT, 31, j)
        probe = rotate_units(th0, glab, g, unit_kick(r2, len(g), 0.3))
        g0 = int(g[0])
        u0 = int(r2.choice(np.flatnonzero(g_of_u == g0)))
        up = rotate_units(th0, ulab, [u0], [0.5])
        gp = rotate_units(th0, glab, [g0], [0.5])
        se = steps(0.1 * C3)
        bt = np.array([th0, probe, up, gp])
        bx = np.repeat(x0[None], 4, 0)
        _, _, (sxs, sths) = simulate(bx, bt, np.repeat(om[None], 4, 0), P["intact"], DT, steps(10 * C3), se)
        T = [series(sxs[:, b], sths[:, b], ulab, g_of_u)[3] for b in range(4)]
        dev = np.sqrt((wrap(pair_differences(T[1], g) - pair_differences(T[0], g)) ** 2).mean(1))
        others = [int(k) for k in g if k != g0]
        rec["tau3"] = E.efold(dev, se * DT)
        rec["upward"] = float(np.sqrt((wrap(T[2][:, others] - T[0][:, others]) ** 2).mean()))
        rec["group_pulse"] = float(np.sqrt((wrap(T[3][:, others] - T[0][:, others]) ** 2).mean()))
        rec["tau2_parts"] = [gs[k]["tau2"] for k in g]
    rec["seconds"] = time.perf_counter() - t0
    return rec


def main():
    n3 = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    n2 = int(sys.argv[2]) if len(sys.argv) > 2 else 320
    C3 = float(sys.argv[3]) if len(sys.argv) > 3 else 9.6
    sR = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    out = sys.argv[5] if len(sys.argv) > 5 else "pilot.json"
    t = time.perf_counter()
    import os
    import pickle
    cache = f"harvest_{ENT}_{n2}.pkl"
    if os.path.exists(cache):
        nc4, templates, l2, groups, t_h, t_2 = pickle.load(open(cache, "rb"))
    else:
        nc4 = int(np.ceil(1.5 * 5 * n2))
        with ProcessPoolExecutor(JOBS) as pool:
            parts = list(pool.map(w_harvest, [list(range(nc4))[k::JOBS] for k in range(JOBS)]))
        templates = sorted((tt for part in parts for tt in part), key=lambda tt: tt["source_world"])
        t_h = time.perf_counter() - t
        with ProcessPoolExecutor(JOBS) as pool:
            res = list(pool.map(w_level2, [(templates, list(range(n2))[k::JOBS]) for k in range(JOBS)]))
        l2 = sorted((r for part in res for r in part[0]), key=lambda r: r["world"])
        groups = sorted((g for part in res for g in part[1]), key=lambda g: g["src"])
        t_2 = time.perf_counter() - t - t_h
        pickle.dump((nc4, templates, l2, groups, t_h, t_2), open(cache, "wb"))
    t = time.perf_counter() - t_h - t_2
    usable = [g for g in groups if g["alone_ok"]]
    L1 = np.median([radius_of_gyration(tt["x"]) for tt in templates])
    L2 = np.median([g["L2"] for g in usable])
    n3 = min(n3, len(usable) // 5)
    args = [(usable[5 * j:5 * j + 5], j, C3, sR, L2 / L1) for j in range(n3)]
    with ProcessPoolExecutor(JOBS) as pool:
        l3 = list(pool.map(w_level3, args))
    t_3 = time.perf_counter() - t - t_h - t_2
    formed = sum(r["outcome"] == "FORMED" for r in l3)
    summary = {
        "entropy": ENT, "C3_provisional": C3, "sR": sR, "c4_worlds": nc4, "templates": len(templates),
        "level2_worlds": n2, "level2_formed": sum(r["accepted"] > 0 for r in l2),
        "level2_outcomes": {k: sum(r["outcome"] == k for r in l2) for k in ("FORMED", "MERGED", "DRIFTING", "APART", "OTHER", "ERROR")},
        "level2_groups": len(groups), "level2_alone_ok": len(usable),
        "tau2_alone_median": float(np.median([g["tau2"] for g in groups if np.isfinite(g["tau2"])])),
        "tau2_censored": int(sum(not np.isfinite(g["tau2"]) for g in groups)),
        "rate_iso_abs_median": float(np.median([abs(g["rate_iso"]) for g in groups])),
        "L1_median": float(L1), "L2_median": float(L2),
        "level3_worlds": len(l3), "level3_formed": formed, "level3_wilson": list(wilson(formed, len(l3))) if l3 else None,
        "level3_outcomes": {k: sum(r["outcome"] == k for r in l3) for k in ("FORMED", "MERGED", "DRIFTING", "APART", "OTHER", "ERROR")},
        "level3_candidate_failures": {k: sum(k in c["failed"] for r in l3 for c in r["candidates"])
                                      for k in ("1_membership", "2_shape", "3_mode_lock", "4_signature", "5_recovery", "6_parts_alive")},
        "level3_candidates": sum(len(r["candidates"]) for r in l3),
        "N_level3": [r["N"] for r in l3],
        "seconds_per_level3_world": [round(r["seconds"], 1) for r in l3],
        "seconds": {"harvest_c4": t_h, "level2": t_2, "level3": t_3},
    }
    f = [r for r in l3 if "tau3" in r]
    if f:
        tau2p = np.median([t for r in f for t in r["tau2_parts"] if np.isfinite(t)])
        tau3 = [r["tau3"] for r in f]
        fin = [t for t in tau3 if np.isfinite(t)]
        summary.update({"tau3_median": float(np.median(fin)) if fin else None, "tau3_censored": len(tau3) - len(fin),
                        "C3_measured_tau3_over_tau1": float(np.median(fin) / 1.5) if fin else None,
                        "T3_measured_tau3_over_tau2": float(np.median(fin) / tau2p) if fin else None,
                        "upward": [round(r["upward"], 4) for r in f], "group_pulse": [round(r["group_pulse"], 4) for r in f]})
    json.dump({"summary": summary, "level2": l2, "level3": l3,
               "groups": [{k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in g.items() if k in ("src", "L2", "alone_ok", "rate_iso", "tau2")} for g in groups]},
              open(out, "w"), indent=1, default=float)
    print(json.dumps(summary, indent=1, default=float))


if __name__ == "__main__":
    main()
