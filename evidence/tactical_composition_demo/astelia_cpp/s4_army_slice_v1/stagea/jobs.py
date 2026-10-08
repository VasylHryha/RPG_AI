"""One repository lock and fail-closed process/RAM admission for all heavy jobs."""
import contextlib
import fcntl
import os
import time
from common import CPP,HERE,LOCAL,load
ACTIVE_FDS=()
@contextlib.contextmanager
def locked():
    global ACTIVE_FDS
    shared=CPP/'s4_net_slice_v1/_local/collection/RUN.lock';shared.parent.mkdir(parents=True,exist_ok=True);LOCAL.mkdir(parents=True,exist_ok=True)
    with shared.open('a') as a,(LOCAL/'RUN.lock').open('a') as b:
        for f in (a,b):fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        ACTIVE_FDS=(a.fileno(),b.fileno())
        try:yield
        finally:ACTIVE_FDS=()

@contextlib.contextmanager
def admitted(seconds):
    gate=load('stagea_process_gate',CPP/'s4_net_slice_v1/process_gate.py');gate.GATE_PATH=LOCAL/'PROCESS_GATE.json'
    with locked():
        deadline=time.monotonic()+seconds;gate.process_gate(wait=False,deadline=deadline)
        monitor=load('stagea_a0monitor',HERE.parent/'rev2/a0_run.py');monitor.live_memory(None)
        yield deadline,monitor

def inherited(fds):
    paths=(CPP/'s4_net_slice_v1/_local/collection/RUN.lock',LOCAL/'RUN.lock')
    for fd,path in zip(fds,paths):
        s=os.fstat(fd);p=path.stat()
        if (s.st_dev,s.st_ino)!=(p.st_dev,p.st_ino):raise RuntimeError('worker lock identity mismatch')
        fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if len(fds)!=2:raise RuntimeError('both whole-job locks required')
