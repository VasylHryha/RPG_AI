"""Owner-side directed population dynamics and immutable replay boundary inputs."""
from dataclasses import dataclass
import ctypes
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DT = .02
MODES = {'intact': 0, 'no_r': 1, 'no_geometry_to_mode': 2, 'no_mode_to_geometry': 3}
_KERNEL = None
_COSTS = {}


def reset_costs():
    _COSTS.clear()


def costs():
    return dict(_COSTS)


@dataclass(frozen=True)
class Replay:
    x: np.ndarray
    theta: np.ndarray
    dt: float = DT

    def __post_init__(self):
        x = np.array(self.x, dtype=float, copy=True)
        th = np.array(self.theta, dtype=float, copy=True)
        if (x.ndim != 3 or x.shape[-1] != 2 or th.shape != x.shape[:2]
                or len(x) < 2 or not np.isfinite(x).all() or not np.isfinite(th).all()
                or not np.isfinite(self.dt) or self.dt <= 0):
            raise ValueError('finite, aligned replay frames and positive dt required')
        x.setflags(write=False); th.setflags(write=False)
        object.__setattr__(self, 'x', x); object.__setattr__(self, 'theta', th)

    @property
    def duration(self):
        return (len(self.x)-1)*self.dt

    def sample(self, times):
        times = np.asarray(times, float)
        if not np.isfinite(times).all() or np.any(times < -1e-10) or np.any(times > self.duration+1e-10):
            raise ValueError('replay has insufficient observation; never clamp missing future')
        q = np.clip(times/self.dt, 0, len(self.x)-1)
        lo = np.floor(q).astype(int); hi = np.minimum(lo+1, len(self.x)-1)
        a = q-lo
        return (self.x[lo]*(1-a[..., None, None])+self.x[hi]*a[..., None, None],
                self.theta[lo]*(1-a[..., None])+self.theta[hi]*a[..., None])

    def slice(self, start, duration):
        steps = exact_steps(duration, self.dt)
        x, th = self.sample(start+np.arange(steps+1)*self.dt)
        return Replay(x, th, self.dt)

    @property
    def digest(self):
        h = hashlib.sha256()
        h.update(np.array([self.dt], '<f8').tobytes())
        h.update(np.asarray(self.x, '<f8').tobytes()); h.update(np.asarray(self.theta, '<f8').tobytes())
        return h.hexdigest()


def exact_steps(duration, dt):
    if not np.isfinite(duration) or duration < 0 or not np.isfinite(dt) or dt <= 0:
        raise ValueError('nonnegative finite duration and positive dt required')
    n = int(round(duration/dt))
    if abs(n*dt-duration) > 1e-9:
        raise ValueError('duration must align with step size')
    return n


def kernel():
    global _KERNEL
    from tools import build_c6_r3
    if not build_c6_r3.LIBRARY.exists():
        raise RuntimeError('build the R3 kernel before running tests or experiments')
    record = json.loads((build_c6_r3.LIBRARY.parent/'BUILD.json').read_text())
    if (record['source_sha256'] != hashlib.sha256(build_c6_r3.SOURCE.read_bytes()).hexdigest()
            or record['binary_sha256'] != hashlib.sha256(build_c6_r3.LIBRARY.read_bytes()).hexdigest()
            or record['flags'] != list(build_c6_r3.FLAGS)):
        raise RuntimeError('R3 native build identity mismatch')
    if _KERNEL is None:
        _KERNEL = ctypes.CDLL(str(build_c6_r3.LIBRARY)).c6r3_integrate
        _KERNEL.argtypes = [ctypes.c_int]*5+[ctypes.c_double, ctypes.c_int, ctypes.c_double]+[ctypes.POINTER(ctypes.c_double)]*10
        _KERNEL.restype = ctypes.c_int
    return _KERNEL


def run(bath_x, bath_th, bath_omega, duration, source=None, reference=None, prior=None,
        mode='intact', outbound=1., dt=DT, sample_dt=DT, phase_origin=None):
    """Bath evolves live; source receives its declared replay, never actual-bath feedback.

    Previous sources remain active as immutable full-state trajectories. No source
    input receives another source's direct output. Detector APIs never see routing.
    """
    bx = np.asarray(bath_x, float); bt = np.asarray(bath_th, float); bo = np.asarray(bath_omega, float)
    if bx.ndim != 2 or bx.shape[1] != 2 or len(bx) < 1 or bt.shape != (len(bx),) or bo.shape != bt.shape:
        raise ValueError('invalid bath state')
    nb = len(bx)
    sx, st, so = (np.empty((0, 2)), np.empty(0), np.empty(0)) if source is None else map(lambda a: np.asarray(a, float), source)
    if sx.ndim != 2 or sx.shape[1] != 2 or st.shape != (len(sx),) or so.shape != st.shape:
        raise ValueError('invalid source state')
    ns = len(sx)
    if mode not in MODES or outbound not in (0., 1.):
        raise ValueError('invalid treatment mode or outgoing mask')
    steps = exact_steps(duration, dt); every = exact_steps(sample_dt, dt)
    if every < 1 or steps % every:
        raise ValueError('sampling must divide the integration horizon')
    times = np.arange(2*steps+1)*dt/2
    if ns:
        if reference is None or reference.x.shape[1] != nb:
            raise ValueError('source needs an aligned bath reference')
        rx, rt = reference.sample(times)
    else:
        rx, rt = np.zeros((len(times), nb, 2)), np.zeros((len(times), nb))
    if prior is None:
        px, pt = np.empty((len(times), 0, 2)), np.empty((len(times), 0))
    else:
        px, pt = prior.sample(times)
    initial_x = np.vstack([bx, sx]); initial_th = np.r_[bt, st]; omega = np.r_[bo, so]
    if not all(np.isfinite(a).all() for a in (initial_x, initial_th, omega)):
        raise ValueError('nonfinite initial state')
    phase_origin = initial_x if phase_origin is None else np.asarray(phase_origin, float)
    if phase_origin.shape != initial_x.shape or not np.isfinite(phase_origin).all():
        raise ValueError('invalid common phase topology origin')
    frames = steps//every+1
    outx = np.empty((frames, nb+ns, 2)); outt = np.empty((frames, nb+ns))
    arrays = [np.ascontiguousarray(a, dtype=np.float64) for a in
              (initial_x, initial_th, omega, phase_origin, rx, rt, px, pt, outx, outt)]
    pointers = [a.ctypes.data_as(ctypes.POINTER(ctypes.c_double)) for a in arrays]
    nd=px.shape[1]
    for key,value in {'native_calls':1,'integration_steps':steps,
        'element_steps':steps*(nb+ns),
        'neighbor_distance_evaluations':steps*(nb*(nb-1)+nb*(ns+nd)+ns*(ns-1)+ns*nb),
        'dense_boundary_bytes':rx.nbytes+rt.nbytes+px.nbytes+pt.nbytes,
        'returned_state_bytes':outx.nbytes+outt.nbytes}.items():
        _COSTS[key]=_COSTS.get(key,0)+value
    result = kernel()(nb, ns, nd, steps, every, dt, MODES[mode], outbound, *pointers)
    if result:
        raise FloatingPointError(f'R3 kernel failed at step/code {result}')
    return arrays[-2], arrays[-1]


def combined(*streams):
    streams = [s for s in streams if s is not None]
    if not streams:
        return None
    if any(s.dt != streams[0].dt or len(s.x) != len(streams[0].x) for s in streams):
        raise ValueError('combined replay streams must share their complete time grid')
    return Replay(np.concatenate([s.x for s in streams], axis=1),
                  np.concatenate([s.theta for s in streams], axis=1), streams[0].dt)


def digest_state(x, th, omega):
    h = hashlib.sha256()
    for value in (x, th, omega):
        h.update(np.asarray(value, '<f8').tobytes())
    return h.hexdigest()
