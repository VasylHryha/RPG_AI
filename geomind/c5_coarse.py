"""Coarse level-2 model: the C4 law applied to level-1 ResonatorStates through their boundary ports.

Zero fitted parameters. Each unit is rigid at this level: its ports move with its centroid X
and rotate in phase with its unit phase Theta; their offsets and phase offsets are read from
the ResonatorState. A port's coupling capacity is its list of own-neighbour distances (from the
level-1 owner): at every step, each port takes the C4 neighbour rule (k nearest within the
radius) over its own-neighbour distances and the other units' ports, so cross-unit couplings
form and break under the same rule as at level 1. Unit velocities are member means:

    Theta_dot_I = natural_rate_I + (1/N_I) sum_{p in I} sum_{q cross} K w(r_pq) sin(dphi_pq) / n_p
    X_dot_I     = (1/N_I) sum_{p in I} sum_{q cross} unit_pq (A (1 + J cos dphi_pq) - B / r_pq) / n_p

with dphi_pq = (Theta_J + phi_q) - (Theta_I + phi_p) and n_p the port's neighbour count. Internal
forces of a unit at its own equilibrium sum to zero, so only cross terms appear. Non-port members
and unit deformation are not represented; that approximation error is what coarse_vs_full measures.

Error travels with compression (R4 invariant 8): at every sample the state is checked. It is
INVALID if a unit's cross-link count changed by more than half of its starting value (minimum 1)
or an inter-unit phase difference moved by more than pi/2 (outside the sine-coupling locking
basin). An invalid coarse state is reopened: replaced by the full model's unit states at that
sample (re-read ports), and counted. The scored prediction is open-loop (no reopening, so no
full-model state enters it); the reopening protocol is run alongside and reported.
"""

import numpy as np

from geomind.c4_model import wrap


class CoarseState:
    """Flattened ports of M units. states: list of ResonatorState dicts (one per unit, group order)."""

    def __init__(self, states, k):
        self.M = len(states)
        self.X = np.array([s["effective_position"] for s in states], dtype=float)
        self.theta = np.array([s["optional_phase"] for s in states], dtype=float)
        self.natural = np.array([s["natural_rate"] for s in states], dtype=float)
        self.N = np.array([s["size"] for s in states], dtype=float)
        unit, offset, phase, own = [], [], [], []
        for u, s in enumerate(states):
            for p in s["boundary_ports"]:
                unit.append(u)
                offset.append(p["offset"])
                phase.append(p["phase_offset"])
                d = list(p["own_neighbour_distances"])[:k]
                own.append(d + [np.inf] * (k - len(d)))
        self.unit, self.offset = np.array(unit), np.array(offset, dtype=float)
        self.phase, self.own = np.array(phase, dtype=float), np.array(own, dtype=float).reshape(len(unit), k)


def links(cs, X, params):
    """Cross-port selection under the C4 neighbour rule: (selected mask (P, P), distances, n_p)."""
    pos = X[cs.unit] + cs.offset
    d = np.linalg.norm(pos[None, :, :] - pos[:, None, :], axis=-1)
    cross = cs.unit[:, None] != cs.unit[None, :]
    d_cross = np.where(cross, d, np.inf)
    combined = np.concatenate([cs.own, d_cross], axis=1)
    kth = np.sort(combined, axis=1)[:, params.k - 1]
    within = combined < params.radius
    chosen = (combined <= kth[:, None]) & within
    n_p = np.maximum(chosen.sum(1), 1)
    selected = (d_cross <= kth[:, None]) & (d_cross < params.radius)
    return selected, d, n_p


def rhs(cs, X, theta, held, params):
    selected, _, n_p = held
    pos = X[cs.unit] + cs.offset
    diff = pos[None, :, :] - pos[:, None, :]  # q - p
    r = np.maximum(np.linalg.norm(diff, axis=-1), params.eps)
    phi = theta[cs.unit] + cs.phase
    dphi = phi[None, :] - phi[:, None]
    weight = selected / n_p[:, None]
    phase_term = (params.K * np.exp(-r * r) * np.sin(dphi) * weight).sum(1)
    radial = (params.A * (1.0 + params.J * np.cos(dphi)) - params.B / r) / r * weight
    force = (diff * radial[..., None]).sum(1)
    theta_dot = cs.natural + np.bincount(cs.unit, phase_term, minlength=cs.M) / cs.N
    X_dot = np.stack([np.bincount(cs.unit, force[:, 0], minlength=cs.M),
                      np.bincount(cs.unit, force[:, 1], minlength=cs.M)], 1) / cs.N[:, None]
    return X_dot, theta_dot


def link_counts(cs, selected):
    return np.bincount(cs.unit, selected.sum(1), minlength=cs.M)


def invalid(cs, counts0, counts, theta0, theta):
    if np.any(np.abs(counts - counts0) > 0.5 * np.maximum(counts0, 1)):
        return True
    i, j = np.triu_indices(cs.M, 1)
    return bool(np.any(np.abs(wrap((theta[j] - theta[i]) - (theta0[j] - theta0[i]))) > np.pi / 2))


def run(states, params, dt, steps, sample_every, reopen=None):
    """Integrate the coarse law with RK4 (cross links recomputed each step, held for its stages).

    reopen(frame) -> list of ResonatorStates from the full model at that sample. Without it the run is an
    open-loop prediction: invalid samples are only flagged (the validity bound travels with the state).
    Returns X (S, M, 2), theta (S, M), reopens, flagged (invalid samples) and work (port-pair evaluations)."""
    cs = CoarseState(states, params.k)
    X, theta = cs.X.copy(), cs.theta.copy()
    counts0, theta0 = link_counts(cs, links(cs, X, params)[0]), theta.copy()
    Xs, thetas, reopens, flagged, work = [X.copy()], [theta.copy()], 0, 0, 0
    P = len(cs.unit)
    for step in range(1, steps + 1):
        held = links(cs, X, params)
        k1 = rhs(cs, X, theta, held, params)
        k2 = rhs(cs, X + 0.5 * dt * k1[0], theta + 0.5 * dt * k1[1], held, params)
        k3 = rhs(cs, X + 0.5 * dt * k2[0], theta + 0.5 * dt * k2[1], held, params)
        k4 = rhs(cs, X + dt * k3[0], theta + dt * k3[1], held, params)
        X = X + dt / 6.0 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        theta = theta + dt / 6.0 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        work += 5 * P * P
        if step % sample_every == 0:
            frame = step // sample_every
            counts = link_counts(cs, links(cs, X, params)[0])
            if invalid(cs, counts0, counts, theta0, theta):
                flagged += 1
                if reopen is not None:
                    fresh = reopen(frame)
                    cs = CoarseState(fresh, params.k)
                    X, theta = cs.X.copy(), cs.theta.copy()
                    # Keep the unit phase continuous with the coarse series (unwrapped).
                    theta = theta + 2 * np.pi * np.round((thetas[-1] - theta) / (2 * np.pi))
                    counts0, theta0 = link_counts(cs, links(cs, X, params)[0]), theta.copy()
                    P = len(cs.unit)
                    reopens += 1
            Xs.append(X.copy())
            thetas.append(theta.copy())
    return {"X": np.array(Xs), "theta": np.array(thetas), "reopens": reopens, "flagged": flagged, "work": work}
