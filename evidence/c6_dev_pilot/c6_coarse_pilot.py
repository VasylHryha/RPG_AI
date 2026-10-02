"""C6 development pilot, part 2: coarse readiness at transition 2 (level-1 units in a level-2 group).

NOT evidence. Pilot entropy groups from c6_pilot's harvest cache, simulated alone from their formed state.
Port variants: V1 = hull members (C5), V2 = hull plus members with an active cross-unit neighbour, ALL = every
member (rigid-body reference, not a coarse model). Baselines: none, rigid, relaxation with the phase tau (C5) and
with a channel-matched tau (position e-folding of a 1.25x scaled geometry for pushes).
"""
import json
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

ROOT = "/Users/new/RiderProjects/ai_RPG_test"
sys.path.insert(0, ROOT)
from geomind import c5_coarse, c5_experiment as E  # noqa: E402
from geomind.c4_detect import _convex_hull, circular_mean, pair_differences, radius_of_gyration  # noqa: E402
from geomind.c4_experiment import model_params  # noqa: E402
from geomind.c4_model import Batch, neighbors, simulate, wrap  # noqa: E402
from geomind.c5_compose import rotate_units, scale_units, shift_units, unit_kick  # noqa: E402
from geomind.c5_units import unit_phases, unit_positions  # noqa: E402

C5M = json.loads(open(ROOT + "/experiments/c5_manifest.json").read())
C4M = E.load_c4(C5M)
P = model_params(C4M)["intact"]
S = E.settings(C5M, C4M)
DT, EVERY, STEPS = S["dt"], S["sample_every"], S["mg_steps"]


def state(x, th, om, lab, u, ports_mask):
    members = np.flatnonzero(lab == u)
    X, theta = x[members].mean(0), float(circular_mean(th[members]))
    idx, mask, _ = neighbors(x[members][None], Batch(P, 1))
    own = np.linalg.norm(x[members][idx[0]] - x[members][:, None], axis=-1)
    sel = [i for i, m in enumerate(members) if ports_mask[m]]
    return {"effective_position": X.tolist(), "optional_phase": theta, "natural_rate": float(om[members].mean()),
            "size": int(len(members)),
            "boundary_ports": [{"offset": (x[members[i]] - X).tolist(),
                                "phase_offset": float(np.angle(np.exp(1j * (th[members[i]] - theta)))),
                                "own_neighbour_distances": sorted(own[i][mask[0, i] > 0].tolist())} for i in sel]}


def port_masks(x, lab):
    n = len(x)
    hull = np.zeros(n, bool)
    for u in np.unique(lab):
        m = np.flatnonzero(lab == u)
        hull[m[_convex_hull(x[m])]] = True
    idx, mask, _ = neighbors(x[None], Batch(P, 1))
    active = ((lab[idx[0]] != lab[:, None]) & (mask[0] > 0)).any(1)
    return {"V1": hull, "V2": hull | active, "ALL": np.ones(n, bool)}


def efold(dev, dt):
    return E.efold(dev, dt)


def one(args):
    g, n = args
    x0, th0, om, lab = g["x"], g["th"], g["om"], g["units"]
    k = int(lab.max()) + 1
    units = list(range(k))
    rng = np.random.default_rng(np.random.SeedSequence([44444, 40, n]))
    X0 = unit_positions(x0[None], lab, units)[0]
    L = np.array([radius_of_gyration(x0[lab == u]) for u in units])
    exc = int(rng.integers(k))
    d = X0[exc] - X0.mean(0)
    d = d / max(np.linalg.norm(d), 1e-12)
    push = 0.2 * L[exc] * d
    starts = {"control": (x0, th0), "pulse": (x0, rotate_units(th0, lab, [exc], [0.5])),
              "push": (shift_units(x0, lab, [exc], [push]), th0),
              "probe": (x0, rotate_units(th0, lab, units, unit_kick(rng, k, 0.3))),
              "scaled": (scale_units(x0, lab, units, 1.25), th0)}
    names = list(starts)
    bx = np.array([starts[s][0] for s in names])
    bt = np.array([starts[s][1] for s in names])
    _, _, (xs, ths) = simulate(bx, bt, np.repeat(om[None], len(names), 0), P, DT, STEPS, EVERY)
    full = {s: (unit_positions(xs[:, i], lab, units), unit_phases(ths[:, i], lab, units)) for i, s in enumerate(names)}
    sdt = EVERY * DT
    tau_phase = efold(np.sqrt((wrap(pair_differences(full["probe"][1], units) - pair_differences(full["control"][1], units)) ** 2).mean(1)), sdt)
    tau_pos = efold(np.sqrt(((full["scaled"][0] - full["control"][0]) ** 2).sum(-1).mean(1)), sdt)
    times = np.arange(STEPS // EVERY + 1) * sdt
    others = [u for u in units if u != exc]
    out = {"k": k, "tau_phase": tau_phase, "tau_pos": tau_pos, "excited": exc}

    def err(fT, fX, pT, pX):
        dT = wrap(fT[:, others] - pT[:, others])
        dX = np.linalg.norm(fX[:, others] - pX[:, others], axis=-1) / L[others]
        return float(np.sqrt((dT ** 2).mean())), float(np.sqrt((dX ** 2).mean()))

    coarse = {}
    for v in ("V1", "V2", "ALL"):
        coarse[v] = {}
        for s in ("control", "pulse", "push"):
            xs0, ts0 = starts[s]
            pm = port_masks(xs0, lab)[v]
            st = [state(xs0, ts0, om, lab, u, pm) for u in units]
            r = c5_coarse.run(st, P, DT, STEPS, EVERY)
            th = r["theta"] + (full[s][1][0] - r["theta"][0])
            coarse[v][s] = (r["X"], th, r["flagged"], int(sum(len(q["boundary_ports"]) for q in st)))
    for e in ("pulse", "push"):
        fX = full[e][0] - full["control"][0]
        fT = full[e][1] - full["control"][1]
        z = (np.zeros_like(fT), np.zeros_like(fX))
        rel = lambda tau: 1.0 - np.exp(-times / tau) if np.isfinite(tau) else np.zeros_like(times)
        if e == "pulse":
            rigid = (np.full_like(fT, 0.5), np.zeros_like(fX))
            relax = (np.repeat((rel(tau_phase) * 0.5 / k)[:, None], k, 1), np.zeros_like(fX))
            relax_m = relax
        else:
            rigid = (np.zeros_like(fT), np.zeros_like(fX) + push)
            relax = (np.zeros_like(fT), np.repeat((rel(tau_phase)[:, None] * push / k)[:, None, :], k, 1))
            relax_m = (np.zeros_like(fT), np.repeat((rel(tau_pos)[:, None] * push / k)[:, None, :], k, 1))
        row = {"response": err(fT, fX, *z), "rigid": err(fT, fX, *rigid), "relax_phase_tau": err(fT, fX, *relax),
               "relax_matched_tau": err(fT, fX, *relax_m)}
        for v in coarse:
            cX = coarse[v][e][0] - coarse[v]["control"][0]
            cT = coarse[v][e][1] - coarse[v]["control"][1]
            row[v] = err(fT, fX, cT, cX)
            row[v + "_flagged"] = coarse[v][e][2]
            row[v + "_ports"] = coarse[v][e][3]
        out[e] = row
    return out


def main():
    cache = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    _, _, _, groups, _, _ = pickle.load(open(cache, "rb"))
    groups = [g for g in groups if g["alone_ok"]][:limit]
    with ProcessPoolExecutor(8) as pool:
        res = list(pool.map(one, [(g, n) for n, g in enumerate(groups)]))
    tot = lambda pr: pr[0] + pr[1]
    summ = {"groups": len(res)}
    for e in ("pulse", "push"):
        rows = [r[e] for r in res]
        base = {"none": [tot(r["response"]) for r in rows], "rigid": [tot(r["rigid"]) for r in rows],
                "relax_phase_tau": [tot(r["relax_phase_tau"]) for r in rows], "relax_matched_tau": [tot(r["relax_matched_tau"]) for r in rows]}
        for v in ("V1", "V2", "ALL"):
            c = np.array([tot(r[v]) for r in rows])
            summ[f"{e}/{v}"] = {b: {"mean_gain": round(float(np.mean(np.array(vals) - c)), 4),
                                    "frac_better": round(float(np.mean(np.array(vals) > c)), 2)} for b, vals in base.items()}
            summ[f"{e}/{v}"]["error_split_phase_pos"] = [round(float(np.mean([r[v][0] for r in rows])), 4),
                                                         round(float(np.mean([r[v][1] for r in rows])), 4)]
            summ[f"{e}/{v}"]["ports_mean"] = round(float(np.mean([r[v + "_ports"] for r in rows])), 1)
        summ[f"{e}/response_split_phase_pos"] = [round(float(np.mean([r["response"][0] for r in rows])), 4),
                                                 round(float(np.mean([r["response"][1] for r in rows])), 4)]
    summ["tau_phase_median"] = float(np.median([r["tau_phase"] for r in res]))
    summ["tau_pos_median"] = float(np.median([r["tau_pos"] for r in res]))
    json.dump({"summary": summ, "rows": res}, open("coarse_pilot.json", "w"), indent=1, default=float)
    print(json.dumps(summ, indent=1, default=float))


if __name__ == "__main__":
    main()
