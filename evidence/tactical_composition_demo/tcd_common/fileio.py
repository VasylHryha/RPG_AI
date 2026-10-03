"""Atomic JSON writing and seed streams."""
import itertools
import json
import os
import threading
from pathlib import Path

import numpy as np

_counter = itertools.count()


def atomic_write(path, data):
    """Write bytes atomically. The temporary name is unique per process, thread and call, so a watchdog thread and the main thread never share one."""
    path = Path(path)
    tmp = path.with_name('%s.tmp%d_%d_%d' % (path.name, os.getpid(), threading.get_ident(), next(_counter)))
    try:
        with open(tmp, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise
    try:
        fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError:
        pass


def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return jsonable(value.tolist())
    if isinstance(value, np.generic):
        return jsonable(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return 'Infinity' if value > 0 else '-Infinity' if value < 0 else 'NaN'
    return value


def write_json(path, obj):
    atomic_write(path, json.dumps(jsonable(obj), sort_keys=True, indent=1).encode())


def stream(entropy, *key):
    """An independent random stream per (entropy, key); keys are integers. SeedSequence pads short entropy lists with zeros, so (1, 1, 0) and (1, 1, 0, 0)
    would alias: the entropy must therefore be a real 96-bit value (as in every SPEC*.json), which makes the list at least five words long."""
    if not isinstance(entropy, int) or entropy < 2**64:
        raise ValueError('entropy must be an integer of at least 65 bits (a SPEC entropy), got %r' % (entropy,))
    return np.random.default_rng(np.random.SeedSequence([entropy, *key]))
