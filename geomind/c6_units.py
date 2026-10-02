"""C6 publications and private, source-isolated template harvest. Frozen C5 is read-only."""
import copy
import hashlib

import numpy as np

from geomind import c5_units
from geomind.c4_detect import _convex_hull, circular_mean
from geomind.c4_model import Batch, neighbors, wrap
from geomind.c6_levels import published_series


def rate_estimate(theta, C):
    """Shared endpoint estimator on 31 own-C samples spanning 30 own-C."""
    phase = np.unwrap(np.asarray(theta))
    if phase.shape != (31,) or not np.all(np.isfinite(phase)):
        raise ValueError('isolated rate requires 31 finite own-C phase samples')
    return float((phase[-1]-phase[0])/(30*C))


def isolated_rate(owner, x, th, omega, params, simulate, dt=0.02):
    """30 own-C, samples every own-C; unwrap the published circular phase before differencing."""
    from geomind.c6_experiment import steps_exact, restrict_owner
    m = list(owner.members)
    local = restrict_owner(owner, m)
    _, _, frames = simulate(x[None, m], th[None, m], omega[None, m], params, dt,
                            steps_exact(30*owner.C, dt), steps_exact(owner.C, dt))
    X, theta = published_series(local, frames[0][:, 0], frames[1][:, 0])
    rate = rate_estimate(theta, owner.C)
    return rate, {"duration": 30*owner.C, "sample_dt": owner.C, "theta": theta.tolist(),
                  "X": X.tolist(), "rate": rate,
                  "estimator": "unwrapped endpoint difference / (30 own-C)",
                  "resolution": max(1e-12, 64*np.finfo(float).eps*max(float(np.max(np.abs(theta))), 1.)/(30*owner.C))}


def active_members(x, members, params):
    """Evaluator census at publication; returns private member identities, never a state field."""
    idx, mask, _ = neighbors(x[None], Batch(params, 1))
    own = np.zeros(len(x), bool)
    own[list(members)] = True
    return [p for p in members if np.any((mask[0, p] > 0) & ~own[idx[0, p]])]


def level1_state(x, th, omega, labels, unit, rate, validity, params, measured_rate, variant="V1"):
    state = c5_units.resonator_state(x, th, omega, labels, unit, rate, validity, params)
    state["natural_rate"] = float(measured_rate)
    if variant not in ("V1", "V2"):
        raise ValueError("unknown port variant")
    if variant == "V2":
        members = np.flatnonzero(labels == unit)
        hull = {int(members[i]) for i in _convex_hull(x[members])}
        ports = sorted(hull | set(active_members(x, members, params)))
        idx, mask, _ = neighbors(x[members][None], Batch(params, 1))
        own = np.linalg.norm(x[members][idx[0]] - x[members][:, None], axis=-1)
        X, theta = np.asarray(state["effective_position"]), state["optional_phase"]
        where = {int(m): i for i, m in enumerate(members)}
        state["boundary_ports"] = [{"offset": (x[p]-X).tolist(), "phase_offset": float(wrap(th[p]-theta)),
            "own_neighbour_distances": sorted(own[where[p]][mask[0, where[p]] > 0].tolist())} for p in ports]
    return state


def compose_state(children, rate, stability, measured_rate, params, variant="V1", active_ports=()):
    """D2: published children only, measured rate and sibling-folded capacities, any promotion."""
    if not children or len({c["level"] for c in children}) != 1:
        raise ValueError("need nonempty same-level children")
    if variant not in ("V1", "V2"):
        raise ValueError("unknown port variant")
    state = c5_units.compose_state(children, rate, stability)
    state["natural_rate"] = float(measured_rate)
    points, phases, own, owners = [], [], [], []
    for i, child in enumerate(children):
        for port in child["boundary_ports"]:
            points.append(np.asarray(child["effective_position"]) + port["offset"])
            phases.append(child["optional_phase"] + port["phase_offset"])
            own.append(port["own_neighbour_distances"])
            owners.append(i)
    points, owners = np.asarray(points), np.asarray(owners)
    selection = set(_convex_hull(points))
    if variant == "V2":
        selection.update(active_ports)
    X, theta = np.asarray(state["effective_position"]), state["optional_phase"]
    ports = []
    for p in sorted(selection):
        sibling = np.linalg.norm(points[owners != owners[p]] - points[p], axis=1)
        capacity = sorted([*own[p], *sibling[sibling < params.radius].tolist()])[:params.k]
        ports.append({"offset": (points[p]-X).tolist(), "phase_offset": float(wrap(phases[p]-theta)),
                      "own_neighbour_distances": capacity})
    state["boundary_ports"] = ports
    return state


def finite_fields(value):
    if isinstance(value, dict):
        return all(finite_fields(v) for v in value.values())
    if isinstance(value, (tuple, list, np.ndarray)):
        return all(finite_fields(v) for v in value)
    if isinstance(value, (int, float, np.number)):
        return bool(np.isfinite(value))
    return isinstance(value, str) or value is None


def validate_interface(candidates, publications, children_by_world):
    """Exactly one publication per accepted (world, unit-set), including correct S and digest."""
    expected = {(r["world"], tuple(sorted(r["units"]))): r for r in candidates if r["accepted"]}
    errors, seen = [], set()
    for row in publications:
        key = row["world"], tuple(sorted(row["units"]))
        if key in seen:
            errors.append("duplicate publication")
        seen.add(key)
        if key not in expected:
            errors.append("unexpected publication")
            continue
        state = row["state"]
        children = [children_by_world[key[0]][u] for u in key[1]]
        errors.extend(c5_units.interface_problems(state, children))
        if not finite_fields(state):
            errors.append("non-finite field")
        mode = state.get("mode_signature", {})
        if not mode or not mode.get("phase_offsets_sorted") or not all(
                k in mode for k in ("collective_rate", "coherence")):
            errors.append("empty or malformed mode")
        if not state.get("stability") or state["stability"] != expected[key]["stats"]:
            errors.append("S does not match candidate")
        for port in state.get("boundary_ports", []):
            if set(port) != {"offset", "phase_offset", "own_neighbour_distances"} or len(port["offset"]) != 2:
                errors.append("malformed port")
    if seen != set(expected):
        errors.append("omitted or swapped publication")
    return errors


def assign_templates(templates, M, worlds):
    """Reuse frozen prefix-stable source isolation for either tree transition."""
    return c5_assign(templates, M, worlds)


from geomind.c5_experiment import assign_templates as c5_assign


def harvest_isolation(world_sources):
    """Check every source prefix at every depth; split sources fail even if terminal IDs differ."""
    owners, errors = {}, []
    for world, paths in world_sources.items():
        for path in paths:
            for depth, source in enumerate(path):
                key = (depth, source)
                if key in owners and owners[key] != world:
                    errors.append({"source": key, "worlds": (owners[key], world)})
                owners[key] = world
    return errors


def harvest_level(formation, reaccept_alone, measure, x, th, omega, owner, source_world):
    """Label-free harvest filter. Rejection alone cannot enter the template pool."""
    from geomind.c6_levels import Owner
    from geomind.c6_experiment import restrict_owner
    templates, raw = [], []
    for candidate in formation:
        if not candidate["accepted"]:
            continue
        group = Owner(tuple(owner.children[i] for i in candidate["units"]), C=owner.C)
        m = list(group.members)
        local = restrict_owner(group, m)
        accepted, record = reaccept_alone(local, x[m], th[m], omega[m])
        rate, measurement = measure(local, x[m], th[m], omega[m])
        raw.append({"candidate": candidate, "reaccepted_alone": bool(accepted),
                    "alone": record, "isolated_rate": measurement})
        if accepted:
            X, theta = published_series(local, x[None, m], th[None, m])
            paths = [tuple(c.source_path) + (source_world,) for c in group.children]
            templates.append({"x": x[m]-X[0], "th": th[m]-theta[0], "omega": omega[m].copy(),
                              "owner": local, "isolated_rate": rate, "source_world": source_world,
                              "source_paths": paths})
    return templates, raw
