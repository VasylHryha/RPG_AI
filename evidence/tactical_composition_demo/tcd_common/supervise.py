"""Process supervision: bounded job submission, pool termination, and a watchdog that cannot mislabel a finished run."""
import concurrent.futures as cf
from concurrent.futures.process import BrokenProcessPool
import os
import subprocess
import threading
import time
from pathlib import Path

from .fileio import write_json


def terminate(pool):
    procs = list((getattr(pool, '_processes', None) or {}).values())
    try:
        pool.shutdown(wait=False, cancel_futures=True)
    except Exception:  # noqa: BLE001
        pass
    for p in procs:
        try:
            p.terminate()
        except Exception:  # noqa: BLE001
            pass
    deadline = time.monotonic()+5
    for p in procs:
        try:
            p.join(max(0.0, deadline-time.monotonic()))
            if p.is_alive():
                p.kill()
                p.join(2)
        except Exception:  # noqa: BLE001
            pass


def run_jobs(pool, fn, jobs, on_result, deadline, workers, ident=lambda job: job[2]):
    """Bounded submission. Returns (status, submitted, finished): 'done' only when every job was submitted AND finished; 'deadline' when any job was
    left unsubmitted or unfinished at the deadline; 'broken' when the pool died. Never blocks past the deadline (one poll interval of slack)."""
    jobs = list(jobs)
    pending, finished, submitted, broken = {}, 0, 0, False
    while True:
        while submitted < len(jobs) and len(pending) < workers and time.monotonic() < deadline:
            pending[pool.submit(fn, jobs[submitted])] = jobs[submitted]
            submitted += 1
        if not pending:
            break
        done, _ = cf.wait(list(pending), timeout=1.0, return_when=cf.FIRST_COMPLETED)
        for future in done:
            job = pending.pop(future)
            try:
                result = future.result()
            except BrokenProcessPool:
                broken, result = True, {'status': 'ERROR', 'seed': ident(job), 'error': 'BrokenProcessPool'}
            except Exception as error:  # noqa: BLE001
                result = {'status': 'ERROR', 'seed': ident(job), 'error': repr(error)}
            on_result(job, result)
            finished += 1
        if broken or (time.monotonic() >= deadline and (pending or submitted < len(jobs))):
            break
    leftover = bool(pending) or submitted < len(jobs)
    for future in pending:
        future.cancel()
    return ('broken' if broken else 'deadline' if leftover else 'done'), submitted, finished


class Watchdog:
    """Hard stop. `cancel()` and the expiry are mutually exclusive: cancel() returns True only if the watchdog had not fired and now never will."""

    def __init__(self, run_dir, hard_cap, cleanup=None, exit_fn=os._exit, kill_children=True):
        self.run_dir, self.hard_cap, self.cleanup, self.exit_fn, self.kill_children = Path(run_dir), hard_cap, cleanup, exit_fn, kill_children
        self._lock = threading.Lock()
        self.fired = False
        self.cancelled = False
        self._timer = threading.Timer(hard_cap, self._expire)
        self._timer.daemon = True

    def start(self):
        self._timer.start()
        return self

    def cancel(self):
        with self._lock:
            if self.fired:
                return False
            self.cancelled = True
        self._timer.cancel()
        return True

    def _expire(self):
        with self._lock:
            if self.cancelled:
                return
            self.fired = True
        record = {'status': 'HARD_STOP', 'after_seconds': self.hard_cap}
        try:
            if self.cleanup is not None:
                self.cleanup()
        except Exception as error:  # noqa: BLE001
            record['cleanup_error'] = repr(error)
        if self.kill_children:
            try:
                result = subprocess.run(['pkill', '-9', '-P', str(os.getpid())], capture_output=True, timeout=10)
                record['pkill_returncode'] = result.returncode   # 1 means no child was left to kill
            except Exception as error:  # noqa: BLE001
                record['pkill_error'] = repr(error)
        try:
            write_json(self.run_dir/'HARD_STOP.json', record)
            if not (self.run_dir/'SUMMARY.json').exists():
                write_json(self.run_dir/'SUMMARY.json', {'status': 'INCOMPLETE', 'reason': 'hard stop after %s s' % self.hard_cap})
        finally:
            self.exit_fn(3)
