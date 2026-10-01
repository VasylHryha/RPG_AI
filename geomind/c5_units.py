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
    the window and its hull overlap with other units), member_digest.

compose_state() builds the parent's ResonatorState (level n + 1) from its children's published
states only, with the same fields: the parent never reads a child's members.

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


def polygon_area(P):
    """Shoelace area of a polygon given in order (0 for fewer than 3 vertices)."""
    if len(P) < 3:
        return 0.0
    x, y = P[:, 0], P[:, 1]
    return float(abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2.0)


def clip_convex(subject, clip):
    """Intersection of two convex polygons given counter-clockwise (Sutherland-Hodgman)."""
    out = [np.asarray(p, float) for p in subject]
    n = len(clip)
    for k in range(n):
        if not out:
            break
        a, b = clip[k], clip[(k + 1) % n]
        side = lambda p: (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        points, out = out, []
        for i in range(len(points)):
            p, q = points[i], points[(i + 1) % len(points)]
            sp, sq = side(p), side(q)
            if sp >= 0:
                out.append(p)
            if (sp >= 0) != (sq >= 0):
                out.append(p + (q - p) * (sp / (sp - sq)))
    return np.array(out) if out else np.zeros((0, 2))


def hull_overlap(x, labels, units):
    """For each unit, the largest fraction of its hull area covered by another unit's hull.

    Area-based, so hulls that cross without containing each other's vertices are caught; units that only
    touch along a contact face give a small fraction. Degenerate hulls (fewer than 3 vertices) give 0."""
    hulls = {u: x[labels == u][_convex_hull(x[labels == u])] for u in units}
    out = []
    for u in units:
        own = polygon_area(hulls[u])
        worst = 0.0
        if own > 0:
            for v in units:
                if v != u and len(hulls[v]) >= 3:
                    worst = max(worst, polygon_area(clip_convex(hulls[u], hulls[v])) / own)
        out.append(float(worst))
    return out


def unit_validity(xs, ths, labels, units, frame_dt, link_factor):
    """The unit's own C4 criteria 2-4 on its original members over the window, plus its worst hull overlap.

    Membership (criterion 1) is replaced by tracking the original members; recovery (5) is the level-2
    test's job. Returns one dict per unit."""
    out = []
    overlaps = np.array([hull_overlap(xs[f], labels, units) for f in range(len(xs))])
    for k, u in enumerate(units):
        members = np.flatnonzero(labels == u)
        locked = np.ones((xs.shape[1], xs.shape[1]), bool)  # members are given; the component test is not used
        s = window_statistics(xs, ths, members, frame_dt, link_factor, locked)
        out.append({"shape_cv": s["shape_cv"], "lock_std": s["lock_std"], "freq_change": s["freq_change"],
                    "pattern_change": s["pattern_change"], "hull_overlap": float(overlaps[:, k].max())})
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


def compose_state(children, rate, stability):
    """The upper-facing ResonatorState of an accepted composite, from its children's states only (same shape).

    X: centroid of the child centroids; L: their radius of gyration; Theta: circular mean of the child phases;
    collective_rate: the group's measured rate; natural_rate: the size-weighted mean of the children's natural
    rates; ports: the child ports on the convex hull of all child ports (the same hull rule as one level down),
    re-expressed relative to the parent; size: total primitive count (the 1/N of the shared law);
    member_digest: a digest of the children's digests (identity, not a read API)."""
    Xc = np.array([c["effective_position"] for c in children], float)
    thetas = np.array([c["optional_phase"] for c in children], float)
    sizes = np.array([c["size"] for c in children], float)
    X = Xc.mean(0)
    theta = float(circular_mean(thetas))
    points, ports = [], []
    for c, xc, tc in zip(children, Xc, thetas):
        for p in c["boundary_ports"]:
            points.append(xc + np.asarray(p["offset"], float))
            ports.append({"phase": tc + p["phase_offset"], "own": p["own_neighbour_distances"]})
    points = np.array(points)
    hull = _convex_hull(points)
    return {
        "level": int(children[0]["level"]) + 1,
        "effective_position": X.tolist(),
        "characteristic_size": radius_of_gyration(Xc),
        "optional_phase": theta,
        "collective_rate": float(rate),
        "natural_rate": float(np.dot(sizes, [c["natural_rate"] for c in children]) / sizes.sum()),
        "mode_signature": {"collective_rate": float(rate),
                           "coherence": float(np.abs(np.exp(1j * thetas).mean())),
                           "phase_offsets_sorted": np.sort(np.angle(np.exp(1j * (thetas - theta)))).tolist()},
        "boundary_ports": [{"offset": (points[i] - X).tolist(),
                            "phase_offset": float(np.angle(np.exp(1j * (ports[i]["phase"] - theta)))),
                            "own_neighbour_distances": list(ports[i]["own"])} for i in hull],
        "size": int(sizes.sum()),
        "stability": dict(stability),
        "member_digest": hashlib.sha256(",".join(sorted(c["member_digest"] for c in children)).encode()).hexdigest()[:16],
    }


def _has_key(value, key):
    if isinstance(value, dict):
        return key in value or any(_has_key(v, key) for v in value.values())
    if isinstance(value, list):
        return any(_has_key(v, key) for v in value)
    return False


INTERFACE_FIELDS = ("level", "effective_position", "characteristic_size", "optional_phase", "collective_rate",
                    "natural_rate", "mode_signature", "boundary_ports", "size", "stability", "member_digest")


def interface_problems(state, children):
    """Checks that a published parent state has the shared shape and is derived from its children only."""
    problems = [f"missing {k}" for k in INTERFACE_FIELDS if k not in state]
    if problems:
        return problems
    if _has_key(state, "members"):
        problems.append("exposes members")
    if state["level"] != children[0]["level"] + 1:
        problems.append("level is not one above its children")
    Xc = np.array([c["effective_position"] for c in children], float)
    if np.abs(np.asarray(state["effective_position"]) - Xc.mean(0)).max() > 1e-12:
        problems.append("position is not the centroid of the children")
    if abs(state["characteristic_size"] - radius_of_gyration(Xc)) > 1e-12:
        problems.append("size is not the children's radius of gyration")
    if state["size"] != sum(c["size"] for c in children):
        problems.append("primitive count is not the children's sum")
    if not state["boundary_ports"] or not np.isfinite(state["collective_rate"]):
        problems.append("no ports or no rate")
    digest = hashlib.sha256(",".join(sorted(c["member_digest"] for c in children)).encode()).hexdigest()[:16]
    if state["member_digest"] != digest:
        problems.append("digest is not derived from the children")
    return problems
