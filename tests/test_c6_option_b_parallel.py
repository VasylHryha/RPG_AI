"""Real concurrent grids/forks with fixed reductions and exception restoration."""
import copy
import threading
import time
import numpy as np
import pytest
from geomind import c6_option_b as O, c6_option_b_parallel as Q
from geomind import c6_r4_field_assay as A, c6_r4_field_protocol as P
from geomind import c6_r4_field as F
from tools.c6_option_b_compare import compare


def owner():
    random=np.random.default_rng(882901);s=P.load_settings()
    o=F.population(random,F.medium(random,s['model']),0,0,24)
    o.z=.55*np.exp(1j*random.uniform(-np.pi,np.pi,25));o.cohorts[0].carrier=o.z.copy()
    o.cohorts[0].selected=(0,1,2)
    return o


def experiment(parallel, order):
    s=copy.deepcopy(P.load_settings())
    s['detector']['recovery_time']=.1
    s['causal']['gm_window']=.05;s['causal']['mg_window']=.1
    s['probe_sample_dt']=.005;s['frame_dt']=.005
    state=owner();state.cohorts[-1].output=1.
    checks=[]
    def run():
        grid=A.GridSet([state]*3,s,checks)
        flow=grid.run(.1,'fixture')
        m=np.array([0,1,2]);locks=[np.ones((24,24),bool)]*3
        pert=A.perturbations(np.random.default_rng(552),24)
        recovery=A.recovery(grid,m,locks,pert,'recovery')
        causal=A.causal(grid,m,pert,'causal')
        return {'checks':checks,'owners':grid.identities(),
                'flow':[f.tolist() for f in flow],'recovery':recovery,'causal':causal}
    with O.backend('native',audit=True) as audit:
        if parallel:
            with Q.parallel(order) as scheduler:
                result=run()
                assert scheduler.summary()['worker_threads_used']<=4
        else:result=run()
        assert audit.calls==audit.exact_calls and audit.maximum_error==0
    return result


@pytest.mark.parametrize('order',['forward','reverse'])
def test_grid_recovery_causal_and_checks_are_bit_identical(order):
    a=experiment(False,order);b=experiment(True,order)
    result=compare(a,b,0.,False)
    assert result['passed'],result


def test_pool_concurrency_budget_and_merge_order():
    with O.backend('native'):
        with Q.parallel('reverse') as scheduler:
            barrier=threading.Barrier(4)
            def task(i):
                barrier.wait(timeout=10)
                time.sleep((3-i)*.001)
                return i
            assert scheduler.map(task,[(i,) for i in range(4)])==list(range(4))
            assert scheduler.summary()['worker_threads_used']==4
            assert Q.WORLD_WORKERS*Q.THREADS_PER_WORLD<=10


def test_restores_after_worker_exception_and_drains_tasks():
    originals=A.GridSet,A.recovery,A.causal
    finished=threading.Event();started=threading.Barrier(2)
    with pytest.raises(RuntimeError,match='worker failure'):
        with O.backend('native'):
            with Q.parallel() as scheduler:
                def task(i):
                    started.wait(timeout=10)
                    if i==0:raise RuntimeError('worker failure')
                    time.sleep(.02);finished.set()
                scheduler.map(task,[(0,),(1,)])
    assert finished.is_set()
    assert (A.GridSet,A.recovery,A.causal)==originals
