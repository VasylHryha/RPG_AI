"""Bounded, absolute-deadline S4 execution. No simulation imports or hidden work queues."""
import concurrent.futures
import math
import os
import signal
import subprocess
import threading
import time


class Deadline:
    def __init__(self, absolute):
        if not math.isfinite(absolute):raise ValueError('finite deadline required')
        self.absolute=absolute;self.stopped=threading.Event();self.lock=threading.Lock();self.children=set()

    def remaining(self, maximum=None):
        allowance=self.absolute-time.monotonic()
        if self.stopped.is_set() or allowance<=0:raise TimeoutError('S4 absolute monotonic deadline reached or execution stopped')
        return allowance if maximum is None else min(maximum,allowance)

    @staticmethod
    def kill(child):
        if child.poll() is None:
            try:os.killpg(child.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            except PermissionError:
                # A concurrent reap can make the group unaddressable in a sandbox.
                # Fall back only to the Popen child we own; never broaden signal scope.
                if child.poll() is None:
                    try:child.kill()
                    except ProcessLookupError:pass

    def stop(self):
        with self.lock:
            self.stopped.set()
            for child in tuple(self.children):self.kill(child)

    def run(self, command, payload, maximum=120):
        # Spawn and register under one lock so stop cannot miss a just-launched child.
        with self.lock:
            self.remaining()
            child=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                   text=True,start_new_session=True)
            self.children.add(child)
        try:
            stdout,stderr=child.communicate(payload,timeout=self.remaining(maximum))
            self.remaining() # late completion is not an accepted evaluation
            return subprocess.CompletedProcess(command,child.returncode,stdout,stderr)
        except BaseException:
            self.stop()
            child.communicate(timeout=2) # reap the killed child; bounded cleanup, never a fight allowance
            raise
        finally:
            with self.lock:self.children.discard(child)


class BoundedPool:
    def __init__(self, workers, deadline):
        if workers<1:raise ValueError('positive worker count required')
        self.workers=workers;self.deadline=deadline
        self.pool=concurrent.futures.ThreadPoolExecutor(max_workers=workers)
        self.pending=set();self.maximum_pending=0

    def map(self, worker, tasks):
        iterator=iter(tasks);queue=[]
        def submit():
            self.deadline.remaining()
            try:task=next(iterator)
            except StopIteration:return False
            future=self.pool.submit(worker,task,self.deadline)
            queue.append(future);self.pending.add(future);self.maximum_pending=max(self.maximum_pending,len(self.pending))
            return True
        try:
            for _ in range(self.workers):
                if not submit():break
            while queue:
                future=queue.pop(0)
                result=future.result(timeout=self.deadline.remaining())
                self.pending.discard(future)
                self.deadline.remaining()
                yield result
                submit()
        except GeneratorExit:
            # zip() can close us just after consuming the final result. Only
            # unfinished submitted work requires stopping the shared deadline.
            if self.pending:self.stop()
            raise
        except concurrent.futures.TimeoutError as error:
            self.stop()
            raise TimeoutError('S4 absolute deadline while awaiting worker') from error
        except BaseException:
            self.stop()
            raise

    def stop(self):
        self.deadline.stop()
        for future in self.pending:future.cancel()

    def close(self):
        self.stop()
        self.pool.shutdown(wait=True,cancel_futures=True)
        self.pending.clear()
