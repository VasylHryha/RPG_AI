"""Process image identities and exclusive native handle ownership."""
from pathlib import Path
import threading
from contextlib import contextmanager
from functools import wraps

_images = {}
_mutex = threading.Lock()


def pin_image(path, digest):
    # dlopen may return a resident old image even after the file is rebuilt.
    # Every supported loader reserves its image and linked dependencies here.
    name = str(Path(path).resolve())
    with _mutex:
        previous = _images.get(name)
        if previous is not None and previous != digest:
            raise RuntimeError('native image replaced in this process; restart after rebuilding')
        _images[name] = digest


def check_owner(owner):
    thread = getattr(owner, '_perf_owner', None)
    if thread is not None and thread != threading.get_ident():
        raise RuntimeError('concurrent native handle use')


@contextmanager
def access(owner):
    # Ordinary C ABI calls cooperate with batches in both acquisition orders.
    check_owner(owner)
    if not hasattr(owner,'_perf_lock'):
        owner._perf_lock=threading.RLock()
    if not owner._perf_lock.acquire(blocking=False):
        raise RuntimeError('concurrent native handle use')
    try:
        check_owner(owner)
        yield
    finally:owner._perf_lock.release()


def accessed(function):
    @wraps(function)
    def wrapped(owner,*args,**kwargs):
        with access(owner):return function(owner,*args,**kwargs)
    return wrapped
