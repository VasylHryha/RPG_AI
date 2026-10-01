"""C5 level-2 worlds: assembly from level-1 templates, rigid unit operations and decoupled runs.

The full model is the frozen C4 element law (geomind.c4_model.simulate) on the union of all
members. Nothing in the dynamics knows that units exist; units interact only where boundary
members fall into one another's C4 neighbour sets.

- Assembly: M templates per world, each with a random rotation, a random global phase and an
  intrinsic rate omega_g ~ U[-delta, delta] shared by all its members (an exact symmetry of the
  unit's internal dynamics: a rotating frame). Centroids are uniform in a disk of radius R2, by
  rejection sampling, with no cross-unit member pair closer than min_gap.
- Padding: worlds of different size are batched by adding inert elements far away (no
  neighbour within the C4 radius, so they never move and never couple). Labels are -1.
- Rigid operations move or rotate whole units and leave every unit's internal relative state
  bit-identical: scale_units (G->M), rotate_units (M->G and the detector kicks), shift_unit and
  pulse_unit (held-out excitations).
- Decoupling: units are translated SEPARATION apart (far beyond the C4 neighbour radius), so no
  cross-unit neighbour exists at all; translation equivariance makes each unit evolve exactly
  as it would alone. This is the complete removal of inter-unit coupling.
"""

import numpy as np

from geomind.c4_model import simulate

FAR = 1.0e4  # inert padding distance, far beyond the C4 neighbour radius


def assemble(templates, rng, M, delta, R2, min_gap, max_attempts=100000):
    """One level-2 world from M templates: (x (n, 2), th (n,), omega (n,), labels (n,))."""
    for _ in range(max_attempts):
        xs, ths, oms, labels = [], [], [], []
        for g, t in enumerate(templates):
            a = rng.uniform(0, 2 * np.pi)
            R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
            r, phi = R2 * np.sqrt(rng.random()), rng.uniform(0, 2 * np.pi)
            xs.append(t["x"] @ R.T + [r * np.cos(phi), r * np.sin(phi)])
            ths.append(t["th"] + rng.uniform(-np.pi, np.pi))
            oms.append(np.full(len(t["th"]), rng.uniform(-delta, delta)))
            labels.append(np.full(len(t["th"]), g))
        x, lab = np.concatenate(xs), np.concatenate(labels)
        d = np.linalg.norm(x[:, None] - x[None], axis=-1)
        if d[lab[:, None] != lab[None]].min() >= min_gap:
            return x, np.concatenate(ths), np.concatenate(oms), lab
    raise RuntimeError("no admissible placement")


def pad(worlds, n=None):
    """Batch worlds of different size: inert far elements appended. Returns x, th, omega, labels arrays."""
    n = n or max(len(w[0]) for w in worlds)
    xs, ths, oms, labels = [], [], [], []
    for k, (x, th, om, lab) in enumerate(worlds):
        extra = n - len(x)
        far = np.c_[FAR * (1 + np.arange(extra)), np.full(extra, FAR * (k + 1))] if extra else np.zeros((0, 2))
        xs.append(np.vstack([x, far]))
        ths.append(np.concatenate([th, np.zeros(extra)]))
        oms.append(np.concatenate([om, np.zeros(extra)]))
        labels.append(np.concatenate([lab, -np.ones(extra, dtype=int)]))
    return np.array(xs), np.array(ths), np.array(oms), np.array(labels)


def scale_units(x, labels, units, scale):
    """Move units rigidly so each centroid's offset from the group centroid is multiplied by scale."""
    out = x.copy()
    centroids = {u: x[labels == u].mean(0) for u in units}
    group = np.mean(list(centroids.values()), axis=0)
    for u in units:
        out[labels == u] += (scale - 1.0) * (centroids[u] - group)
    return out


def rotate_units(th, labels, units, deltas):
    """Add deltas[k] to every member phase of units[k] (a rigid unit-phase rotation)."""
    out = th.copy()
    for u, d in zip(units, deltas):
        out[labels == u] += d
    return out


def shift_units(x, labels, units, vectors):
    out = x.copy()
    for u, v in zip(units, vectors):
        out[labels == u] += v
    return out


def unit_kick(rng, count, rms):
    """Zero-mean kick of exact RMS over count units (the C4 probe_kick shape, one value per unit)."""
    delta = rng.normal(size=count)
    delta -= delta.mean()
    return delta * (rms / np.sqrt((delta ** 2).mean()))


SEPARATION = 100.0  # decoupled units sit this far apart, far beyond the C4 neighbour radius


def decouple_offsets(labels, units):
    """Per-element offsets that place unit k at (SEPARATION * (k + 1), 0) from where it is: no cross-unit
    neighbour can exist, so inter-unit coupling is removed completely. The C4 law is translation-
    equivariant, so each unit evolves exactly as it would alone. Padding (label -1) is not moved."""
    offsets = np.zeros((len(labels), 2))
    for k, u in enumerate(units):
        offsets[labels == u, 0] = SEPARATION * (k + 1)
    return offsets


def run(x, th, omega, params, dt, duration, sample_dt=None, phase_topology=None):
    """simulate() over a duration; returns (x, th, frames) with frames sampled every sample_dt (including t0)."""
    steps = int(round(duration / dt))
    every = int(round(sample_dt / dt)) if sample_dt else None
    return simulate(x, th, omega, params, dt, steps, every, phase_topology=phase_topology)
