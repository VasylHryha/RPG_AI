"""Selectable Option B kernels for unchanged R4 Python orchestration.

Use only in an isolated process: the context temporarily selects functions used
by the existing R4 modules. It changes no files, settings or random generators.
Builds are explicit; missing/mismatched identities stop before native loading.
"""
from contextlib import contextmanager
import ctypes as ct
import json
import threading
import numpy as np
from geomind import c4_detect as D, c6_r4_field as F
from geomind.c6_r4_integrity import sha256
from tools import build_c6_option_b as B, build_c6_r4 as R

TOLERANCE = 1e-10
PTR = ct.POINTER(ct.c_double)

def verify_build(library=B.LIBRARY):
    record = json.loads((library.parent/'BUILD.json').read_text())
    expected = {str(s.relative_to(B.ROOT)):sha256(s) for s in B.SOURCES}
    if record.get('source_hashes') != expected or record.get('binary_sha256') != sha256(library) or record.get('flags') != list(B.FLAGS):
        raise RuntimeError('Option B source/build identity mismatch')
    return record

def reference():
    record = json.loads((R.LIBRARY.parent/'BUILD.json').read_text())
    if record.get('source_sha256') != sha256(R.SOURCE) or record.get('binary_sha256') != sha256(R.LIBRARY):
        raise RuntimeError('Reference source/build identity mismatch; explicit rebuild required')
    return F.native()

def load():
    record = verify_build()
    lib = ct.CDLL(str(B.LIBRARY))
    ints = ct.POINTER(ct.c_int)
    tail = [PTR,PTR,PTR,PTR,ints,PTR,PTR,ints,PTR,PTR,PTR]
    lib.field_rhs.argtypes = [ct.c_int]*3+[ct.c_double]+tail
    lib.field_run.argtypes = [ct.c_int]*3+[ct.c_double]*2+[ct.c_int]*2+tail
    lib.field_rhs.restype = lib.field_run.restype = ct.c_int
    lib.option_b_components.argtypes = [ct.c_int,PTR,ct.c_double,ct.POINTER(ct.c_ubyte),ct.POINTER(ct.c_int64)]
    lib.option_b_components.restype = ct.c_int
    lib.option_b_cache_clear.argtypes = []
    lib.option_b_cache_clear.restype = None
    lib.option_b_cache_stats.argtypes = [ct.POINTER(ct.c_uint64)]
    lib.option_b_cache_stats.restype = None
    return lib, record

def cache_stats(lib):
    values=(ct.c_uint64*7)()
    lib.option_b_cache_stats(values)
    return dict(zip(('retired_hits','control_hits','eligible_misses','avoided_material_rk_steps',
                     'retired_bytes','control_bytes','probation_bytes'),map(int,values)))

class Audit:
    """Compare every returned full production-step array on identical inputs."""
    def __init__(self, lib, ref):
        self.lib, self.ref = lib, ref
        self.calls = self.elements = self.component_calls = 0
        self.exact_calls = 0
        self.maximum_error = 0.
        self.records = []
        self.lock = threading.Lock()
    def invoke(self, name, args):
        ns,n,nc = args[:3]
        width = 2*ns+nc*(3*n+2*ns)
        count = width if name=='field_rhs' else width*(args[5]//args[6]+1)
        expected = np.empty(count, dtype='f8')
        rc = getattr(self.ref,name)(*args[:-1],expected.ctypes.data_as(PTR))
        code = getattr(self.lib,name)(*args)
        if rc != code:
            raise RuntimeError('Option B native error decision differs')
        with self.lock:
            self.calls += 1
        if code:
            return code
        actual = np.ctypeslib.as_array(args[-1], shape=(count,))
        delta = np.abs(actual-expected)
        if not np.isfinite(delta).all():
            raise RuntimeError('Option B nonfinite equivalence difference')
        error = float(delta.max()) if count else 0.
        exact = np.array_equal(actual.view("u8"), expected.view("u8"))
        with self.lock:
            self.maximum_error = max(self.maximum_error,error)
            self.elements += count
            self.exact_calls += int(exact)
        # All evaluator/RK arithmetic is unchanged and requires exact equality.
        if not exact:
            raise RuntimeError('Option B full-flow equivalence failed: '+str(error))
        return code
    def field_run(self,*args): return self.invoke('field_run',args)
    def field_rhs(self,*args): return self.invoke('field_rhs',args)
    def summary(self):
        return {'calls':self.calls,'float64_values_compared':self.elements,
                'bit_identical_calls':self.exact_calls,'maximum_error':self.maximum_error,
                'component_calls':self.component_calls,'absolute_tolerance':0.,'exact_arithmetic_required':True}

def components(lib, X, link_factor, locked):
    x = np.ascontiguousarray(X,dtype='f8')
    locks = np.asarray(locked)
    if x.ndim!=2 or x.shape[1]!=2 or len(x)==0 or locks.shape!=(len(x),len(x)) or locks.dtype!=bool or not np.isfinite(x).all() or not np.isfinite(link_factor):
        raise ValueError('Invalid typed detection input')
    locks = np.ascontiguousarray(locks,dtype='u1')
    labels = np.empty(len(x),dtype='i8')
    code = lib.option_b_components(len(x),x.ctypes.data_as(PTR),float(link_factor),
        locks.ctypes.data_as(ct.POINTER(ct.c_ubyte)),labels.ctypes.data_as(ct.POINTER(ct.c_int64)))
    if code: raise ValueError('Native detection failed: '+str(code))
    return labels

@contextmanager
def backend(name='reference', audit=False):
    if name not in ('reference','native'):
        raise ValueError('Unknown Option B backend')
    if name=='reference':
        reference()
        yield None
        return
    ref, _ = reference()
    lib, record = load()
    lib.option_b_cache_clear()
    checker = Audit(lib,ref) if audit else None
    previous_native, previous_components = F.native,D.components
    # Cache keys precede backend selection and do not bind a kernel identity.
    # A backend boundary must never reuse trajectories from the other kernel.
    with F._CACHE_LOCK:
        F._PASSIVE_CACHE.clear()
        F._EMISSION_CACHE.clear()
    def detected(X, link_factor, locked):
        result = components(lib,X,link_factor,locked)
        if checker:
            if not np.array_equal(result,previous_components(X,link_factor,locked)):
                raise RuntimeError('Option B detection decision flip')
            with checker.lock:
                checker.component_calls += 1
        return result
    F.native = lambda:(checker if checker else lib,record)
    D.components = detected
    try:
        yield checker
        verify_build()
        # Verify the reference again without invoking its implicit builder.
        r = json.loads((R.LIBRARY.parent/'BUILD.json').read_text())
        if r['source_sha256']!=sha256(R.SOURCE) or r['binary_sha256']!=sha256(R.LIBRARY):
            raise RuntimeError('Reference identity changed during Option B run')
    finally:
        F.native,D.components = previous_native,previous_components
        with F._CACHE_LOCK:
            F._PASSIVE_CACHE.clear()
            F._EMISSION_CACHE.clear()
