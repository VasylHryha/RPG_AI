"""C5 level-1 units: harvest accepted C4 resonators and expose their upper-facing ResonatorState.

Level 0 is a primitive element, level 1 an accepted C4 resonator, level 2 the C5 composite.

Harvest is label-free: fresh C4 identical-arm worlds run with the frozen C4 code and parameters,
and the frozen C4 detector selects the accepted resonators. Each accepted resonator within the
registered size range becomes a template (member positions relative to the centroid, phases
relative to the circular mean) and is used once.

The level-1 owner keeps each unit's member list private. It tracks the unit by its original
members and publishes only the ResonatorState (R4 C5 interface):

    level, effective_position X, characteristic_size L, optional_phase Theta (circular mean),
    collective_rate Omega, natural_rate (the rate the unit has alone), mode_signature,
    boundary_ports (hull members: offset from X, phase offset from Theta, own-neighbour
    distances = the port's coupling capacity), stability S (the unit's own C4 criteria 2-4 over
    the window and its port overlap with other units), member_digest.

Unit phases are circular means of member phases, unwrapped over frames. Member phases are kept
unwrapped by the C4 model and may differ by whole turns, so an arithmetic mean is wrong.
"""

import hashlib

import numpy as np

from geomind.c4_detect import _convex_hull, circular_mean, radius_of_gyration, window_statistics
from geomind.c4_experiment import detect_worlds, form, initial_worlds
from geomind.c4_model import Batch, neighbors


def harvest(c4_manifest, params, entropy, indices, size_range):
    """Accepted C4 resonators from fresh identical-arm C4 worlds (frozen C4 code).

    Returns (templates, pool), where each template has x (n, 2) relative to its centroid and th (n,)
    relative to its circular mean, and pool is the descriptive harvest record."""
    x0, th0, om = initial_worlds(c4_manifest, entropy, "identical", indices)
    x, th, frames = form(x0, th0, om, params, c4_manifest)
    detected = detect_worlds(frames, om, params, c4_manifest, entropy, "identical", indices)
    templates, sizes = [], []
    for b, cands in enumerate(detected):
        for c in cands:
            if not c["accepted"]:
                continue
            m = c["members"]
            sizes.append(int(len(m)))
            if size_range[0] <= len(m) <= size_range[1]:
                templates.append({"x": x[b, m] - x[b, m].mean(0), "th": th[b, m] - circular_mean(th[b, m]),
                                  "source_world": int(indices[b])})
    pool = {"c4_worlds": len(indices), "worlds_with_resonator": int(sum(any(c["accepted"] for c in d) for d in detected)),
            "accepted_resonators": len(sizes), "accepted_sizes": sizes, "templates_in_range": len(templates),
            "size_range": list(size_range)}
    return templates, pool


def unit_phases(ths, labels, units):
    """Circular-mean phase of each unit per frame, unwrapped over frames: ths (F, N) -> (F, len(units))."""
    raw = np.stack([circular_mean(ths[:, labels == u], axis=1) for u in units], axis=1)
    return np.unwrap(raw, axis=0)


def unit_positions(xs, labels, units):
    """Centroid of each unit per frame: xs (F, N, 2) -> (F, len(units), 2)."""
    return np.stack([xs[:, labels == u].mean(1) for u in units], axis=1)


def unit_sizes(xs, labels, units):
    """Radius of gyration of each unit per frame: (F, len(units))."""
    return np.array([[radius_of_gyration(xs[f, labels == u]) for u in units] for f in range(len(xs))])


def _inside(point, hull):
    edges = np.roll(hull, -1, axis=0) - hull
    rel = point - hull
    cross = edges[:, 0] * rel[:, 1] - edges[:, 1] * rel[:, 0]
    return bool((cross > 0).all() or (cross < 0).all())


def port_overlap(x, labels, units):
    """For each unit, the fraction of its ports (hull vertices) strictly inside another unit's hull."""
    hulls = {u: x[labels == u][_convex_hull(x[labels == u])] for u in units}
    out = []
    for u in units:
        ports = hulls[u]
        inside = [any(_inside(p, hulls[v]) for v in units if v != u and len(hulls[v]) >= 3) for p in ports]
        out.append(float(np.mean(inside)) if len(ports) else 0.0)
    return out


def unit_validity(xs, ths, labels, units, frame_dt, link_factor):
    """The unit's own C4 criteria 2-4 on its original members over the window, plus its worst port overlap.

    Membership (criterion 1) is replaced by tracking the original members; recovery (5) is the level-2
    test's job. Returns one dict per unit."""
    out = []
    overlaps = np.array([port_overlap(xs[f], labels, units) for f in range(len(xs))])
    for k, u in enumerate(units):
        members = np.flatnonzero(labels == u)
        locked = np.ones((xs.shape[1], xs.shape[1]), bool)  # members are given; the component test is not used
        s = window_statistics(xs, ths, members, frame_dt, link_factor, locked)
        out.append({"shape_cv": s["shape_cv"], "lock_std": s["lock_std"], "freq_change": s["freq_change"],
                    "pattern_change": s["pattern_change"], "port_overlap": float(overlaps[:, k].max())})
    return out


def member_digest(members):
    return hashlib.sha256(",".join(str(int(m)) for m in sorted(members)).encode()).hexdigest()[:16]


def resonator_state(x, th, omega, labels, unit, rate, validity, params, level=1):
    """The upper-facing ResonatorState of one unit at one frame. Member indices are not exposed."""
    members = np.flatnonzero(labels == unit)
    X, theta = x[members].mean(0), float(circular_mean(th[members]))
    hull = _convex_hull(x[members])
    idx, mask, _ = neighbors(x[members][None], Batch(params, 1))
    own = np.linalg.norm(x[members][idx[0]] - x[members][:, None], axis=-1)
    ports = [{"offset": (x[members[i]] - X).tolist(),
              "phase_offset": float(np.angle(np.exp(1j * (th[members[i]] - theta)))),
              "own_neighbour_distances": sorted(own[i][mask[0, i] > 0].tolist())} for i in hull]
    return {
        "level": level,
        "effective_position": X.tolist(),
        "characteristic_size": radius_of_gyration(x[members]),
        "optional_phase": theta,
        "collective_rate": float(rate),
        "natural_rate": float(omega[members].mean()),
        "mode_signature": {"collective_rate": float(rate),
                           "coherence": float(np.abs(np.exp(1j * th[members]).mean())),
                           "phase_offsets_sorted": np.sort(np.angle(np.exp(1j * (th[members] - theta)))).tolist()},
        "boundary_ports": ports,
        "size": int(len(members)),
        "stability": dict(validity),
        "member_digest": member_digest(members),
    }
