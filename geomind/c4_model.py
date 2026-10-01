"""C4 position-phase element model (R4 C4), batched over independent worlds.

For neighbors j of i (up to k nearest within `radius`, recomputed once per step):

    x_dot_i = mean_j[ unit_ij * (A * (1 + J cos(th_j - th_i)) - B / max(r_ij, eps)) ]
    th_dot_i = omega_i + mean_j[ K * w(r_ij) * sin(th_j - th_i) ]

with w(r) = exp(-r^2), or w = 1 in the distance-blind ablation. An element with no
neighbor keeps x_dot = 0 and th_dot = omega. The neighbor set is computed at the
start of each RK4 step and held for its four stages, so the right-hand side is
smooth within a step. Phases are kept unwrapped (so collective frequencies are
directly measurable); wrap them only for display.

Arrays: positions x (B, N, 2), phases th (B, N), rates omega (B, N). One batch may mix
parameter sets (the intact model and its ablations), one per world.
"""

from dataclasses import dataclass, replace

import numpy as np


@dataclass(frozen=True)
class Params:
    A: float = 1.0
    B: float = 1.0
    J: float = 0.8
    K: float = 1.0
    eps: float = 1e-6
    distance_weighted: bool = True  # False: w(r) = 1 (removes geometry -> mode)
    k: int = 8
    radius: float = 3.0


INTACT = Params()
ABLATIONS = {
    "intact": INTACT,
    "no_mode_to_geometry": replace(INTACT, J=0.0),  # phase-blind motion
    "no_geometry_to_mode": replace(INTACT, distance_weighted=False),  # distance-blind phase coupling
    "both_off": replace(INTACT, J=0.0, distance_weighted=False),
    "clump": replace(INTACT, J=0.0, K=0.0),  # attraction/repulsion only
}


class Batch:
    """Per-world parameters broadcast to (B, 1, 1); one batch may mix the intact model and its ablations.

    k and radius (the neighbor rule) must be shared by the whole batch."""

    def __init__(self, params, worlds):
        plist = list(params) if isinstance(params, (list, tuple)) else [params] * worlds
        if len(plist) != worlds:
            raise ValueError("one Params per world is required")
        if len({(q.k, q.radius) for q in plist}) != 1:
            raise ValueError("a batch must share one neighbor rule")
        col = lambda name: np.array([float(getattr(q, name)) for q in plist])[:, None, None]
        self.A, self.B, self.J, self.K, self.eps = col("A"), col("B"), col("J"), col("K"), col("eps")
        self.weighted = np.array([q.distance_weighted for q in plist])[:, None, None]
        self.k, self.radius = plist[0].k, plist[0].radius


def neighbors(x, batch):
    """Indices (B, N, k) of the k nearest other elements, a float mask of those within radius, and 1/count."""
    r = np.hypot(x[:, None, :, 0] - x[:, :, None, 0], x[:, None, :, 1] - x[:, :, None, 1])
    n = x.shape[1]
    r[:, np.arange(n), np.arange(n)] = np.inf
    k = min(batch.k, n - 1)
    idx = np.argsort(r, axis=2, kind="stable")[:, :, :k]
    mask = (np.take_along_axis(r, idx, axis=2) < batch.radius).astype(float)
    return idx, mask, 1.0 / np.maximum(mask.sum(-1), 1.0)


def rhs(x, th, omega, idx, mask, inv_count, batch):
    b = np.arange(x.shape[0])[:, None, None]
    xj = x[b, idx]
    dx, dy = xj[..., 0] - x[:, :, None, 0], xj[..., 1] - x[:, :, None, 1]
    r = np.hypot(dx, dy)
    rr = np.maximum(r, batch.eps)
    dth = th[b, idx] - th[:, :, None]
    # unit_ij * (A (1 + J cos) - B / r), with the 1/r of the unit vector folded in; J = 0 gives exactly A.
    radial = (batch.A * (1.0 + batch.J * np.cos(dth)) - batch.B / rr) * mask / rr
    x_dot = np.stack(((dx * radial).sum(2), (dy * radial).sum(2)), -1) * inv_count[..., None]
    w = np.where(batch.weighted, np.exp(-r * r), 1.0)
    th_dot = omega + (batch.K * w * np.sin(dth) * mask).sum(2) * inv_count
    return x_dot, th_dot


def rk4_step(x, th, omega, batch, dt, held=None):
    idx, mask, inv_count = held if held is not None else neighbors(x, batch)
    k1x, k1t = rhs(x, th, omega, idx, mask, inv_count, batch)
    k2x, k2t = rhs(x + 0.5 * dt * k1x, th + 0.5 * dt * k1t, omega, idx, mask, inv_count, batch)
    k3x, k3t = rhs(x + 0.5 * dt * k2x, th + 0.5 * dt * k2t, omega, idx, mask, inv_count, batch)
    k4x, k4t = rhs(x + dt * k3x, th + dt * k3t, omega, idx, mask, inv_count, batch)
    return (x + dt / 6.0 * (k1x + 2 * k2x + 2 * k3x + k4x),
            th + dt / 6.0 * (k1t + 2 * k2t + 2 * k3t + k4t))


def simulate(x, th, omega, params, dt, steps, sample_every=None, hold_neighbors=False):
    """Integrate `steps` RK4 steps. `params` is one Params for every world or a list with one per world.

    Returns (x, th, samples) where samples, if requested, holds the state every `sample_every` steps
    including the start: (xs (S,B,N,2), ths (S,B,N)). hold_neighbors keeps the starting neighbor
    sets for the whole run (numerical checks only)."""
    x, th = np.array(x, dtype=float), np.array(th, dtype=float)
    omega = np.asarray(omega, dtype=float)
    batch = Batch(params, x.shape[0])
    held = neighbors(x, batch) if hold_neighbors else None
    xs, ths = ([x.copy()], [th.copy()]) if sample_every else ([], [])
    for step in range(1, steps + 1):
        x, th = rk4_step(x, th, omega, batch, dt, held)
        if not (np.isfinite(x).all() and np.isfinite(th).all()):
            raise FloatingPointError(f"non-finite state at step {step}")
        if sample_every and step % sample_every == 0:
            xs.append(x.copy())
            ths.append(th.copy())
    samples = (np.stack(xs), np.stack(ths)) if sample_every else None
    return x, th, samples


def wrap(angle):
    return (np.asarray(angle) + np.pi) % (2 * np.pi) - np.pi
