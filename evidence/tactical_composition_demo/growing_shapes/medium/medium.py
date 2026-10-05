"""ctypes wrapper for the independent 0h medium. Run build.py before use.

Coordinates, rates and time use C4 units. Phases are unwrapped radians.
Drive.strength is K_in * site strength; phase is psi at step start and rate
advances psi during the four RK stages. Reach uses a strict cutoff.
Growth thresholds have NO defaults: the caller must specify the whole design.
"""
import ctypes as C
from contextlib import contextmanager
import json
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parent

class Params(C.Structure):
    _fields_ = [(name, C.c_double) for name in ('A', 'B', 'J', 'K', 'eps', 'radius', 'geometry_rate')] + [
        (name, C.c_int32) for name in ('k', 'distance_weighted', 'window', 'min_samples')]
    def __init__(self, A=1., B=1., J=.8, K=1., eps=1e-6, radius=3., geometry_rate=1.,
                 k=8, distance_weighted=True, window=32, min_samples=2):
        super().__init__(A, B, J, K, eps, radius, geometry_rate, k, int(distance_weighted), window, min_samples)

class Element(C.Structure):
    _fields_ = [('id', C.c_uint64)] + [(name, C.c_double) for name in ('x', 'y', 'phase', 'rate', 'born')] + [('silent', C.c_int32)]
    def as_dict(self):
        return {name: getattr(self, name) for name, _ in self._fields_}

class Drive(C.Structure):
    _fields_ = [('id', C.c_uint64)] + [(name, C.c_double) for name in ('x', 'y', 'phase', 'rate', 'strength', 'width', 'reach')]

class Need(C.Structure):
    _fields_ = [('id', C.c_uint64)] + [(name, C.c_double) for name in ('x', 'y', 'phase', 'rate', 'error')]

class Growth(C.Structure):
    _fields_ = [(name, C.c_double) for name in (
        'L_on', 'L_off', 'S_split', 'T_nov', 'T_split', 'T_death', 'growth_period', 'T_protect',
        'split_offset', 'c_e', 'c_c', 'C_max', 'E_need', 'T_need', 'epsilon_U')] + [
        (name, C.c_int32) for name in ('N_max', 'reward_arm', 'utility_checks')]
    def __init__(self, **values):
        expected = {name for name, _ in self._fields_}
        if set(values) != expected:
            raise ValueError(f'Explicit growth parameters required: missing={sorted(expected - set(values))}, extra={sorted(set(values) - expected)}')
        super().__init__(**values)

class Measure(C.Structure):
    _fields_ = [(name, C.c_double) for name in ('lock', 'strain', 'phase1', 'phase2')] + [('samples', C.c_int32)]
    def as_dict(self):
        return {name: getattr(self, name) for name, _ in self._fields_}

def _library(path=None):
    path = Path(path) if path else ROOT / '_build' / ('medium.dylib' if platform.system() == 'Darwin' else 'medium.so')
    lib = C.CDLL(str(path))
    h, d, u, i, z = C.c_void_p, C.c_double, C.c_uint64, C.c_int, C.c_size_t
    P = C.POINTER
    declarations = {
        'create': (h, [u, P(Params)]), 'destroy': (None, [h]), 'clone': (h, [h]), 'error': (C.c_char_p, [h]),
        'count': (i, [h]), 'time': (d, [h]), 'elements': (i, [h, P(Element), i]),
        'add': (i, [h, d, d, d, d, P(u)]), 'set_element': (i, [h, u, d, d, d, d]),
        'remove': (i, [h, u]), 'split': (i, [h, u, d, d, d, P(u)]), 'silence': (i, [h, u, i]),
        'drives': (i, [h, P(Drive), i]), 'rhs': (i, [h, P(d), i]),
        'neighbors': (i, [h, P(C.c_int32), P(d), P(d), i]), 'step': (i, [h, d]), 'observe': (i, [h]),
        'readout': (i, [h, d, d, d, d, P(d)]), 'plv': (i, [h, u, u, i, P(d)]),
        'measure_element': (i, [h, u, P(Measure)]), 'groups': (i, [h, d, d, P(C.c_int32), i]),
        'cost': (i, [h, d, d, P(d)]), 'configure_growth': (i, [h, P(Growth)]),
        'utility': (i, [h, u, d]), 'needs': (i, [h, P(Need), i]), 'apply_growth': (i, [h]),
        'save': (z, [h, h, z]), 'load': (h, [h, z]), 'events': (z, [h, h, z]),
    }
    for name, (restype, argtypes) in declarations.items():
        function = getattr(lib, 'gm_' + name)
        function.restype, function.argtypes = restype, argtypes
    return lib

class Medium:
    def __init__(self, seed=0, params=None, library=None):
        self._lib = _library(library)
        self.params = params or Params()
        self._handle = self._lib.gm_create(seed, C.byref(self.params))
        if not self._handle:
            raise ValueError('Invalid medium parameters or native allocation failure')
    @classmethod
    def _adopt(cls, lib, handle, params):
        if not handle:
            raise ValueError('Invalid snapshot or native allocation failure')
        self = cls.__new__(cls)
        self._lib, self._handle, self.params = lib, handle, Params.from_buffer_copy(params)
        return self
    def close(self):
        if getattr(self, '_handle', None):
            self._lib.gm_destroy(self._handle)
            self._handle = None
    def __del__(self):
        self.close()
    def __enter__(self):
        return self
    def __exit__(self, *_):
        self.close()
    def _call(self, name, *args):
        if not self._handle:
            raise RuntimeError('Medium is closed')
        if getattr(self._lib, 'gm_' + name)(self._handle, *args) != 0:
            raise ValueError(self._lib.gm_error(self._handle).decode())
    def __len__(self):
        if not self._handle:
            raise RuntimeError('Medium is closed')
        return self._lib.gm_count(self._handle)
    @property
    def time(self):
        if not self._handle:
            raise RuntimeError('Medium is closed')
        return self._lib.gm_time(self._handle)
    @property
    def elements(self):
        output = (Element * len(self))()
        self._call('elements', output, len(output))
        return list(output)
    def add(self, x, y, phase=0., rate=0.):
        output = C.c_uint64()
        self._call('add', x, y, phase, rate, C.byref(output))
        return output.value
    def set_element(self, id, x, y, phase, rate):
        self._call('set_element', id, x, y, phase, rate)
    def remove(self, id):
        self._call('remove', id)
    def split(self, id, phase1, phase2, offset):
        output = (C.c_uint64 * 2)()
        self._call('split', id, phase1, phase2, offset, output)
        return tuple(output)
    def silence(self, id, silent=True):
        self._call('silence', id, int(silent))
    @contextmanager
    def silenced(self, id):
        previous = next(e.silent for e in self.elements if e.id == id)
        self.silence(id)
        try:
            yield self
        finally:
            self.silence(id, previous)
    @contextmanager
    def evaluation_without(self, id):
        """Clone for an evaluation block; the entire original medium stays untouched."""
        with self.clone() as branch:
            branch.silence(id)
            yield branch
    def set_drives(self, drives):
        values = (Drive * len(drives))(*drives)
        self._call('drives', values, len(values))
    def rhs(self):
        output = (C.c_double * (3 * len(self)))()
        self._call('rhs', output, len(output))
        return [list(output[i:i+3]) for i in range(0, len(output), 3)]
    def neighbors(self):
        n, k = len(self), min(self.params.k, max(0, len(self)-1))
        indices, masks = (C.c_int32 * (n*k))(), (C.c_double * (n*k))()
        inv = (C.c_double * n)()
        self._call('neighbors', indices, masks, inv, n*k)
        return ([list(indices[j*k:(j+1)*k]) for j in range(n)],
                [list(masks[j*k:(j+1)*k]) for j in range(n)], list(inv))
    def step(self, dt, steps=1):
        if not isinstance(steps, int) or steps < 0:
            raise ValueError('steps must be a nonnegative integer')
        for _ in range(steps):
            self._call('step', dt)
    def observe(self):
        """Append one window sample (also done automatically after every step)."""
        self._call('observe')
    def readout(self, x, y, width, reach):
        output = (C.c_double * 2)()
        self._call('readout', x, y, width, reach, output)
        return tuple(output)
    def plv(self, i, j, drive=False):
        output = C.c_double()
        self._call('plv', i, j, int(drive), C.byref(output))
        return output.value
    def measure(self, id):
        output = Measure()
        self._call('measure_element', id, C.byref(output))
        return output
    def groups(self, threshold, link_factor):
        output = (C.c_int32 * len(self))()
        self._call('groups', threshold, link_factor, output, len(output))
        return list(output)
    def cost(self, c_e, c_c):
        output = (C.c_double * 3)()
        self._call('cost', c_e, c_c, output)
        return {'elements': int(output[0]), 'active_couplings': int(output[1]), 'total': output[2]}
    def configure_growth(self, config):
        self._call('configure_growth', C.byref(config))
    def set_utility(self, id, utility):
        self._call('utility', id, utility)
    def set_needs(self, needs):
        values = (Need * len(needs))(*needs)
        self._call('needs', values, len(values))
    def apply_growth_rules(self):
        self._call('apply_growth')
    def clone(self):
        return self._adopt(self._lib, self._lib.gm_clone(self._handle), self.params)
    def save(self, path=None):
        if not self._handle:
            raise RuntimeError('Medium is closed')
        size = self._lib.gm_save(self._handle, None, 0)
        buffer = C.create_string_buffer(size)
        if not size or self._lib.gm_save(self._handle, buffer, size) != size:
            raise ValueError(self._lib.gm_error(self._handle).decode())
        data = buffer.raw
        if path is not None:
            Path(path).write_bytes(data)
        return data
    @classmethod
    def load(cls, source, library=None):
        data = Path(source).read_bytes() if isinstance(source, (str, Path)) else bytes(source)
        lib = _library(library)
        buffer = C.create_string_buffer(data)
        handle = lib.gm_load(buffer, len(data))
        # Snapshot v1: uint64 string length, 17-byte tag, then explicit gm_params fields.
        offset = 8 + len(b'growing-medium-v1')
        if not handle:
            raise ValueError('Invalid snapshot or native allocation failure')
        try:
            # Serialized Params has no padding, and ABI v1 sizeof(Params)==72.
            params = Params.from_buffer_copy(data[offset:offset+C.sizeof(Params)])
            return cls._adopt(lib, handle, params)
        except Exception:
            lib.gm_destroy(handle)
            raise
    @property
    def events(self):
        if not self._handle:
            raise RuntimeError('Medium is closed')
        size = self._lib.gm_events(self._handle, None, 0)
        output = C.create_string_buffer(size)
        if not size or self._lib.gm_events(self._handle, output, size) != size:
            raise ValueError(self._lib.gm_error(self._handle).decode())
        return json.loads(output.value)
