"""Fake workers and fake subprocess payloads only; never combat."""
import concurrent.futures
import subprocess
import sys
import threading
import time
import pytest
from s4_deadline import Deadline,BoundedPool


def test_bounded_ordered_submission_and_absolute_deadline():
    deadline=Deadline(time.monotonic()+5);pool=BoundedPool(3,deadline);submitted=[]
    def tasks():
        for i in range(10000):submitted.append(i);yield i
    def worker(task,passed):
        assert passed.absolute==deadline.absolute
        return task
    stream=pool.map(worker,tasks())
    assert next(stream)==0 and len(submitted)==3
    assert next(stream)==1 and len(submitted)==4
    stream.close();pool.close()
    assert pool.maximum_pending<=3 and deadline.stopped.is_set() and not pool.pending


def test_timeout_clamps_to_remaining_and_kills_child():
    started=time.monotonic();deadline=Deadline(started+.15)
    assert 0<deadline.remaining(120)<=.15
    with pytest.raises((TimeoutError,subprocess.TimeoutExpired)):
        deadline.run([sys.executable,'-c','import time;time.sleep(10)'],'')
    assert time.monotonic()-started<2 and deadline.stopped.is_set() and not deadline.children
    with pytest.raises(TimeoutError):deadline.run([sys.executable,'-c','raise Exception("must not spawn")'],'')


def test_near_deadline_validation_does_not_submit_entire_panel():
    submitted=[];deadline=Deadline(time.monotonic()+.12);pool=BoundedPool(2,deadline)
    def tasks():
        for i in range(2100):submitted.append(i);yield i
    def worker(task,passed):
        return passed.run([sys.executable,'-c','import time;time.sleep(10)'],'')
    try:
        with pytest.raises((TimeoutError,subprocess.TimeoutExpired)):list(pool.map(worker,tasks()))
    finally:pool.close()
    assert len(submitted)==2 and pool.maximum_pending==2 and not deadline.children and not pool.pending


def test_failure_cleanup_terminates_other_active_children():
    started=threading.Event();deadline=Deadline(time.monotonic()+5);pool=BoundedPool(2,deadline)
    def worker(task,passed):
        if task==0:
            assert started.wait(2)
            # Wait until the sibling's child is registered, avoiding launch-race assumptions.
            limit=time.monotonic()+2
            while not passed.children and time.monotonic()<limit:time.sleep(.001)
            assert passed.children
            raise ValueError('fake validation failure')
        started.set();return passed.run([sys.executable,'-c','import time;time.sleep(10)'],'')
    begin=time.monotonic()
    try:
        with pytest.raises(ValueError,match='fake validation failure'):list(pool.map(worker,range(2100)))
    finally:pool.close()
    assert time.monotonic()-begin<2 and not deadline.children and deadline.stopped.is_set()


def test_pending_future_cancellation():
    # Occupy the executor to ensure futures can be pending when stop occurs.
    deadline=Deadline(time.monotonic()+5);pool=BoundedPool(1,deadline);release=threading.Event()
    first=pool.pool.submit(lambda:release.wait(1));pending=pool.pool.submit(lambda:99)
    pool.pending.add(pending);pool.stop();release.set();pool.close()
    assert pending.cancelled() and first.done()


def test_signal_group_exit_race_falls_back_to_owned_child(monkeypatch):
    import s4_deadline as module
    class FakeChild:
        pid=123
        killed=False
        def poll(self):return None
        def kill(self):self.killed=True
    def denied(pid,signal):raise PermissionError('fake sandbox exit race')
    monkeypatch.setattr(module.os,'killpg',denied)
    child=FakeChild();Deadline.kill(child);assert child.killed


def test_successive_zip_consumed_batches_do_not_stop_shared_deadline():
    deadline=Deadline(time.monotonic()+5);pool=BoundedPool(3,deadline)
    def worker(task,passed):return task
    try:
        for _ in range(2):
            assert list(zip(range(19),pool.map(worker,range(19))))==[(i,i) for i in range(19)]
            assert not deadline.stopped.is_set() and not pool.pending
            deadline.remaining()
    finally:pool.close()
