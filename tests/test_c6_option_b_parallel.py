"""Real concurrent grids/forks with fixed reductions and exception restoration."""
import copy
import json
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


def test_bounded_submission_longest_first_and_indexed_exceptions():
    with O.backend('native'):
        with Q.parallel() as scheduler:
            jobs=[(i,) for i in range(40)]
            seen=[];lock=threading.Lock()
            def task(i):
                with lock:seen.append(i)
                time.sleep(.001)
                return i
            result=dict(scheduler.completed(task,jobs,list(range(40))))
            assert result=={i:i for i in range(40)}
            assert set(seen[:4])==set(range(36,40))
            assert scheduler.summary()['maximum_inflight_jobs']==4
            def failure(i):
                if i in (0,3):raise RuntimeError(str(i))
                return i
            with pytest.raises(RuntimeError,match='^0$'):scheduler.map(failure,jobs)


def test_parallel_selection_requires_backend_and_rejects_nesting():
    with pytest.raises(RuntimeError,match='active native'):
        with Q.parallel():pass
    with O.backend('native'):
        with Q.parallel():
            with pytest.raises(RuntimeError,match='Nested'):
                with Q.parallel():pass


def small_settings():
    s=copy.deepcopy(P.load_settings())
    s.update(formation=.2,exposure=.2,window=.1,descriptor=.05,probe_sample_dt=.025,frame_dt=.025)
    s['detector']['recovery_time']=.05;s['causal'].update(gm_window=.025,mg_window=.05)
    return s


def operation_scenario(force,fail=None):
    """Run P.operation (sequential or the selected port) on reduced settings.

    force: test-only overrides applied identically to both paths so that the
    eligible stage (19 episodes) and the continuation are exercised.
    fail: inject a failure into one task scope, after its checks were made.
    """
    s=small_settings();checks=[]
    grid=A.GridSet([F.medium(P.rng(7,0,1),s['model'])]*3,s,checks)
    source=P.introduce(grid,7,0,0,0)
    flows=source.run(s['formation'],'prefix')
    q={'selected_members':list(range(8)),'qualified':True}
    originals=A.qualification,P.rolling_persistence,P.qualify_episode
    def qualification(g,f,pert,scope,forced_members=None):
        r=originals[0](g,f,pert,scope,forced_members)
        if force and forced_members is not None:r['qualified']=force=='no_r' or '/no_r/' not in scope
        if force and scope.endswith('/intact/e0/qualification'):r['qualified']=True
        if fail and fail in scope:raise A.NumericalFailure('injected '+scope)
        return r
    def persistence(*args):
        rows=originals[1](*args)
        for r in rows:r['passed']=r['passed'] or bool(force)
        return rows
    A.qualification,P.rolling_persistence=qualification,persistence
    try:
        out={}
        try:
            cell,continuation=P.operation(source,q,flows,7,0,1,.3,'turn1')
            out['cell']=cell
            out['continuation']=None if continuation is None else continuation[0].identities()
            out['continuation_shares_checks']=continuation is None or continuation[0].checks is checks
        except (ValueError,RuntimeError) as error:
            out['error']=[type(error).__name__,str(error)]
        out['checks']=checks
        return json.loads(json.dumps(out,default=lambda o:o.tolist()))
    finally:
        A.qualification,P.rolling_persistence,P.qualify_episode=originals


@pytest.mark.parametrize('force,fail',[(True,None),(False,None),('no_r',None),
    (True,'turn1/operation/no_r/endpoint'),(True,'turn1/no_r/e2'),(True,'turn1/before/e1')])
def test_concurrent_operation_matches_sequential_operation(force,fail):
    with O.backend('native'):
        sequential=operation_scenario(force,fail)
        with Q.parallel() as scheduler:
            concurrent=operation_scenario(force,fail)
            batches=[b['tasks'] for b in scheduler.summary()['concurrent_task_batches']]
    result=compare(sequential,concurrent,0.,False)
    assert result['passed'],result
    assert sequential.get('error')==concurrent.get('error')
    if force is True and fail is None:
        assert sequential['cell']['before_formation'] and sequential['continuation']
        assert sequential['continuation_shares_checks'] and batches==[3,23]
    if force is False:assert not sequential['cell']['operation_eligible'] and batches==[3,4]
    if fail:assert sequential['error'][1].startswith('injected '+fail)
    if force=='no_r':assert sequential['error']==['ValueError','NO-R remains qualified']


def test_coordinator_token_bounds_concurrent_python():
    with O.backend('native'):
        with Q.parallel() as scheduler:
            active=[0];peak=[0];lock=threading.Lock()
            def task(checks):
                for _ in range(20):
                    with lock:active[0]+=1;peak[0]=max(peak[0],active[0])
                    time.sleep(.001)
                    with lock:active[0]-=1
                    # A grid wait releases the token for another coordinator.
                    scheduler.map(lambda i:i,[(0,)])
                return len(checks)
            shared=[]
            assert Q.ordered(scheduler,shared,[task]*6)==[0]*6
            assert peak[0]==1 and scheduler.holding()
            def nested(checks):return Q.ordered(scheduler,checks,[lambda c:0])
            with pytest.raises(RuntimeError,match='Nested protocol tasks'):
                Q.ordered(scheduler,shared,[nested])
