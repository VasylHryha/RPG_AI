"""ctypes execution of the frozen C4 law; no physics defaults live here."""

import ctypes as ct
from functools import lru_cache
from pathlib import Path

import numpy as np

from geomind.c4_model import Batch, Params


LIBRARY = Path(__file__).resolve().parents[1] / "build/c6/element_law.dylib"
_Double = ct.POINTER(ct.c_double)
_Index = ct.POINTER(ct.c_int64)


class _Params(ct.Structure):
    _fields_ = [(name, ct.c_double) for name in ("A", "B", "J", "K", "eps")] + [
        ("distance_weighted", ct.c_int), ("frozen_phase_topology", ct.c_int)]


@lru_cache(maxsize=1)
def _library():
    lib = ct.CDLL(str(LIBRARY))
    lib.c6_neighbors.argtypes = [_Double, ct.c_int64, ct.c_int64, ct.c_int64,
                                ct.c_double, _Index, _Double, _Double]
    lib.c6_neighbors.restype = ct.c_int
    lib.c6_simulate.argtypes = [
        _Double, _Double, _Double, ct.POINTER(_Params), ct.c_int64, ct.c_int64,
        ct.c_int64, ct.c_double, ct.c_double, ct.c_int64, ct.c_int,
        _Index, _Double, _Double, _Index, ct.c_int64, _Double, _Double]
    lib.c6_simulate.restype = ct.c_int64
    return lib


def _ptr(array):
    return array.ctypes.data_as(_Index if array.dtype == np.int64 else _Double)


def _k(batch, n):
    # Slice semantics of argsort(...)[..., :min(k, n - 1)].
    return len(range(n)[slice(None, min(batch.k, n - 1))])


def neighbors(x, batch):
    """Native neighbour selection, exposed for the fast equivalence contract."""
    x = np.ascontiguousarray(x, dtype=float)
    if x.ndim != 3 or x.shape[2] != 2:
        raise ValueError("positions must have shape (B, N, 2)")
    worlds, n = x.shape[:2]
    k = _k(batch, n)
    idx = np.empty((worlds, n, k), dtype=np.int64)
    mask = np.empty(idx.shape, dtype=float)
    inv = np.empty((worlds, n), dtype=float)
    code = _library().c6_neighbors(_ptr(x), worlds, n, k, batch.radius,
                                   _ptr(idx), _ptr(mask), _ptr(inv))
    if code:
        raise RuntimeError("C6 native neighbor allocation failed")
    return idx, mask, inv


def simulate(x, th, omega, params, dt, steps, sample_every=None, hold_neighbors=False, phase_topology=None):
    """Same state, sampling and parameter semantics as c4_model.simulate."""
    x, th = np.array(x, dtype=float), np.array(th, dtype=float)
    omega = np.asarray(omega, dtype=float)
    batch = Batch(params, x.shape[0])
    if batch.any_frozen and phase_topology is None:
        raise ValueError("frozen_phase_topology needs a phase_topology")
    if x.ndim != 3 or x.shape[2] != 2 or th.shape != x.shape[:2]:
        raise ValueError("state must have shapes (B, N, 2) and (B, N)")
    worlds, n = th.shape
    k = _k(batch, n)
    step_range = range(1, steps + 1)
    # No initial finite check: the reference reports only after an actual step.
    if not step_range:
        if hold_neighbors:
            neighbors(x, batch)
        samples = (x[None].copy(), th[None].copy()) if sample_every else None
        return x, th, samples
    x, th = np.ascontiguousarray(x), np.ascontiguousarray(th)
    omega = np.ascontiguousarray(np.broadcast_to(omega, th.shape))
    plist = list(params) if isinstance(params, (list, tuple)) else [params] * worlds
    native_params = (_Params * worlds)(*[
        _Params(*(float(getattr(p, name)) for name in ("A", "B", "J", "K", "eps")),
                bool(p.distance_weighted), bool(p.frozen_phase_topology)) for p in plist])
    phase_args = (None, None, None)
    if batch.any_frozen:
        idx = np.asarray(phase_topology[0])
        if not np.issubdtype(idx.dtype, np.integer):
            raise IndexError("arrays used as indices must be of integer (or boolean) type")
        idx = np.broadcast_to(idx, (worlds, n, k))
        # np.where ignores the caller's indices for non-frozen worlds.
        idx = np.where(batch.frozen, idx, 0)
        if np.any((idx < -n) | (idx >= n)):
            raise IndexError("phase_topology index out of bounds")
        idx = np.ascontiguousarray(np.where(idx < 0, idx + n, idx), dtype=np.int64)
        mask = np.ascontiguousarray(np.broadcast_to(phase_topology[1], idx.shape), dtype=float)
        inv = np.ascontiguousarray(np.broadcast_to(phase_topology[2], th.shape), dtype=float)
        phase_args = (_ptr(idx), _ptr(mask), _ptr(inv))
    sample_steps = np.array([s for s in step_range if sample_every and s % sample_every == 0], dtype=np.int64)
    samples = None
    sample_args = (None, None)
    if sample_every:
        xs = np.empty((len(sample_steps) + 1, *x.shape), dtype=float)
        ths = np.empty((len(sample_steps) + 1, *th.shape), dtype=float)
        xs[0], ths[0] = x, th
        sample_args = (_ptr(xs[1:]), _ptr(ths[1:]))
        samples = xs, ths
    code = _library().c6_simulate(
        _ptr(x), _ptr(th), _ptr(omega), native_params, worlds, n, k, batch.radius,
        dt, len(step_range), bool(hold_neighbors), *phase_args,
        _ptr(sample_steps), len(sample_steps), *sample_args)
    if code > 0:
        raise FloatingPointError(f"non-finite state at step {code}")
    if code < 0:
        raise RuntimeError("C6 native integration allocation failed")
    return x, th, samples
