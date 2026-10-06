"""Selectable Option B kernels for unchanged R4 Python orchestration.

Use only in an isolated process: the context temporarily selects functions used
by the existing R4 modules. It changes no files, settings or random generators.
Builds are explicit; missing/mismatched identities stop before native loading.
"""
from contextlib import contextmanager
import ctypes as ct
import json
import threading
import platform
from concurrent.futures import Future
import numpy as np
from geomind import c4_detect as D, c6_r4_field as F
from geomind.c6_r4_integrity import sha256
from tools import build_c6_option_b as B, build_c6_r4 as R

TOLERANCE = 1e-10
PTR = ct.POINTER(ct.c_double)
_SELECTION_LOCK = threading.Lock()
_LOAD_LOCK = threading.Lock()
_LOADED = {}
_ACTIVE_NATIVE = False
# Process-wide native cache budgets in bytes (material, actual medium, drive),
# shared by all worker threads: about the previous 4 x per-thread envelope.
CACHE_LIMITS = (1024*1024*1024,64*1024*1024,128*1024*1024)
CACHE_FIELDS = ('retired_hits','control_hits','eligible_misses','avoided_material_rk_steps',
                'retired_bytes','control_bytes','material_entries','material_single_flight_waits',
                'medium_hits','medium_misses','avoided_medium_rk_steps','medium_bytes','medium_single_flight_waits',
                'drive_hits','drive_misses','drive_bytes','drive_single_flight_waits',
                'computed_material_rk_steps','computed_medium_rk_steps','computed_uncached_rk_steps','computed_drive_steps')
# Engineering byte budgets for the existing exact Python caches while the
# native backend is selected (the reference path keeps the R4 constants).
PASSIVE_CACHE_BYTES = 64*1024*1024
# 128 MiB retains every distinct channel of a complete smoke world (measured).
EMISSION_CACHE_BYTES = 128*1024*1024


def verify_build(library=B.LIBRARY):
    record = json.loads((library.parent/'BUILD.json').read_text())
    expected = {str(s.relative_to(B.ROOT)):sha256(s) for s in B.SOURCES}
    if record.get('source_hashes') != expected or record.get('binary_sha256') != sha256(library) or record.get('flags') != list(B.FLAGS) or record.get('platform') != platform.system() or record.get('architecture') != platform.machine():
        raise RuntimeError('Option B source/build identity mismatch')
    return record

def _checked_load(library, record):
    identity = (sha256(library), json.dumps(record,sort_keys=True))
    with _LOAD_LOCK:
        previous = _LOADED.get(str(library))
        if previous and previous[0] != identity:
            raise RuntimeError('Loaded native identity changed; restart process')
        if previous:
            return previous[1]
        lib = ct.CDLL(str(library))
        ints = ct.POINTER(ct.c_int)
        tail = [PTR,PTR,PTR,PTR,ints,PTR,PTR,ints,PTR,PTR,PTR]
        lib.field_rhs.argtypes = [ct.c_int]*3+[ct.c_double]+tail
        lib.field_run.argtypes = [ct.c_int]*3+[ct.c_double]*2+[ct.c_int]*2+tail
        lib.field_rhs.restype = lib.field_run.restype = ct.c_int
        if sha256(library) != identity[0]:
            raise RuntimeError('Native identity changed during load; restart process')
        _LOADED[str(library)] = (identity,lib)
        return lib


def reference_record():
    record = json.loads((R.LIBRARY.parent/'BUILD.json').read_text())
    if (record.get('source_sha256') != sha256(R.SOURCE) or
        record.get('binary_sha256') != sha256(R.LIBRARY) or record.get('flags') != list(R.FLAGS)):
        raise RuntimeError('Reference source/build identity mismatch; explicit rebuild required')
    return record


def reference():
    # Configure ctypes here: F.native() can rebuild implicitly and is forbidden.
    record = reference_record()
    if F._NATIVE is not None and F._NATIVE[1] != record:
        raise RuntimeError('Reference already loaded with another identity; restart process')
    lib = _checked_load(R.LIBRARY,record)
    if reference_record() != record:
        raise RuntimeError('Reference identity changed during load')
    return lib,record


def load():
    record = verify_build()
    lib = _checked_load(B.LIBRARY,record)
    lib.option_b_components.argtypes = [ct.c_int,PTR,ct.c_double,ct.POINTER(ct.c_ubyte),ct.POINTER(ct.c_int64)]
    lib.option_b_components.restype = ct.c_int
    lib.option_b_cache_clear.argtypes = []
    lib.option_b_cache_clear.restype = None
    lib.option_b_cache_limits.argtypes = [ct.c_uint64]*3
    lib.option_b_cache_limits.restype = None
    lib.option_b_cache_stats.argtypes = [ct.POINTER(ct.c_uint64)]
    lib.option_b_cache_stats.restype = None
    if verify_build() != record:
        raise RuntimeError('Option B identity changed during load')
    return lib, record

def cache_stats(lib):
    """Process-wide cumulative counters and current retained bytes."""
    values=(ct.c_uint64*len(CACHE_FIELDS))()
    lib.option_b_cache_stats(values)
    return dict(zip(CACHE_FIELDS,map(int,values)))

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

def single_flight_cache(budgets=None):
    """Backend-local exact reuse: one concurrent computation per existing key.

    budgets maps id(cache) to an engineering byte budget replacing the caller's
    limit (values are unaffected). Retained bytes are tracked incrementally.
    """
    inflight = {}
    totals = {}
    budgets = budgets or {}
    def cached(cache,limit,key,compute):
        limit = budgets.get(id(cache),limit)
        token = (id(cache),key)
        with F._CACHE_LOCK:
            result = cache.get(key)
            if result is not None:
                cache.move_to_end(key)
                return result
            pending = inflight.get(token)
            leader = pending is None
            if leader:
                pending = Future()
                inflight[token] = pending
        if not leader:
            return pending.result()
        try:
            result = compute()
            result.flags.writeable = False
            with F._CACHE_LOCK:
                if result.nbytes <= limit:
                    total = totals.get(id(cache))
                    if total is None:total = sum(v.nbytes for v in cache.values())
                    cache[key] = result;total += result.nbytes
                    while total > limit:
                        total -= cache.popitem(last=False)[1].nbytes
                    totals[id(cache)] = total
            pending.set_result(result)
            return result
        except BaseException as error:
            pending.set_exception(error)
            raise
        finally:
            with F._CACHE_LOCK:
                del inflight[token]
    return cached


@contextmanager
def backend(name='reference', audit=False):
    global _ACTIVE_NATIVE
    if name not in ('reference','native'):
        raise ValueError('Unknown Option B backend')
    if not _SELECTION_LOCK.acquire(blocking=False):
        raise RuntimeError('Option B selection requires one isolated coordinator; nested contexts forbidden')
    previous_native, previous_components, previous_cache = F.native,D.components,F.cached_array
    try:
        ref, ref_record = reference()
        lib, record = load() if name == 'native' else (ref,ref_record)
        if name == 'native':
            lib.option_b_cache_limits(*CACHE_LIMITS)
        checker = Audit(lib,ref) if audit and name == 'native' else None
        with F._CACHE_LOCK:
            F._PASSIVE_CACHE.clear(); F._EMISSION_CACHE.clear()
        def detected(X,link_factor,locked):
            result = components(lib,X,link_factor,locked)
            if checker:
                if not np.array_equal(result,previous_components(X,link_factor,locked)):
                    raise RuntimeError('Option B detection decision flip')
                with checker.lock:
                    checker.component_calls += 1
            return result
        F.native = lambda:(checker if checker else lib,record)
        if name == 'native':
            D.components = detected
            F.cached_array = single_flight_cache({id(F._PASSIVE_CACHE):PASSIVE_CACHE_BYTES,
                                                  id(F._EMISSION_CACHE):EMISSION_CACHE_BYTES})
            _ACTIVE_NATIVE = True
        yield checker
        if name == 'native' and verify_build() != record:
            raise RuntimeError('Option B identity changed during run')
        if reference_record() != ref_record:
            raise RuntimeError('Reference identity changed during run')
    finally:
        _ACTIVE_NATIVE = False
        F.native,D.components,F.cached_array = previous_native,previous_components,previous_cache
        with F._CACHE_LOCK:
            F._PASSIVE_CACHE.clear(); F._EMISSION_CACHE.clear()
        _SELECTION_LOCK.release()
