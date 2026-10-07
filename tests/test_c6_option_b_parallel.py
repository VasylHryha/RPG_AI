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


@pytest.fixture(autouse=True,params=['exact','inexact'])
def selected_kernel(request,monkeypatch):
    monkeypatch.setenv('C6_OPTION_B_KERNEL',request.param)


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
        assert audit.calls>0 and audit.maximum_error<=audit.summary()['absolute_tolerance']
        if audit.kernel=='exact':assert audit.calls==audit.exact_calls and audit.maximum_error==0
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


# --- Sequential failure semantics inside batched grid runs (review F1) -------

def _digest(*parts):
    import hashlib
    h=hashlib.sha256()
    for part in parts:h.update(part if isinstance(part,bytes) else repr(part).encode())
    return h.hexdigest()


class Injection:
    """Failures that are pure functions of a request's own inputs.

    Whether a top-level F.advance raises, or a three-grid diagnostic inflates
    its errors (a numerical failure) or raises, depends only on the inputs, so
    the sequential run and every concurrent schedule see the same failing
    requests. `predicate` cases target named positions explicitly.
    """
    def __init__(self,salt=None,worker=0,numeric=0,diagnostic=0,predicate=None,only=None):
        self.salt,self.worker,self.numeric,self.diagnostic,self.predicate=salt,worker,numeric,diagnostic,predicate
        self.only=only  # optional input-only gate: owner -> bool
    def __enter__(self):
        self.advance,self.errors=F.advance,A.state_errors
        def advance(owner,duration,dt,sample_dt=None,_factor=True):
            if _factor:
                tag=self.classify('advance',owner,(duration,dt))
                if tag=='worker':raise RuntimeError('injected worker '+_digest(self.salt,owner.pack().tobytes(),dt)[:12])
            return self.advance(owner,duration,dt,sample_dt,_factor)
        def state_errors(owner,flows,scales):
            tag=self.classify('diagnostic',owner,flows[2][-1].tobytes())
            if tag=='diagnostic':raise A.NumericalFailure('injected diagnostic '+_digest(self.salt,flows[2][-1].tobytes())[:12])
            if tag=='numeric':return {'position':1.,'phase':1.,'field':1.}
            return self.errors(owner,flows,scales)
        F.advance,A.state_errors=advance,state_errors
        return self
    def classify(self,where,owner,extra):
        if self.predicate:return self.predicate(where,owner,extra)
        if self.only and not self.only(owner):return None
        value=int(_digest(self.salt,where,owner.pack().tobytes(),extra)[:8],16)
        if where=='advance':return 'worker' if self.worker and value%self.worker==0 else None
        if self.diagnostic and value%self.diagnostic==0:return 'diagnostic'
        if self.numeric and value%self.numeric==0:return 'numeric'
        return None
    def __exit__(self,*exc):
        F.advance,A.state_errors=self.advance,self.errors


def failing_experiment(parallel,order,injection_factory):
    s=copy.deepcopy(P.load_settings())
    s['detector']['recovery_time']=.1
    s['causal']['gm_window']=.05;s['causal']['mg_window']=.1
    s['probe_sample_dt']=.005;s['frame_dt']=.005
    state=owner();state.cohorts[-1].output=1.
    checks=[];out={'checks':checks}
    def run():
        grid=A.GridSet([state]*3,s,checks)
        out['flow']=[f.tolist() for f in grid.run(.1,'fixture')]
        m=np.array([0,1,2]);locks=[np.ones((24,24),bool)]*3
        pert=A.perturbations(np.random.default_rng(552),24)
        start={'time':grid.owners[0].time,'packs':[o.pack().tobytes() for o in grid.owners]}
        with injection_factory(start):
            out['recovery']=A.recovery(grid,m,locks,pert,'recovery')
            out['causal']=A.causal(grid,m,pert,'causal')
    with O.backend('native'):
        try:
            if parallel:
                with Q.parallel(order):run()
            else:run()
        except (ValueError,RuntimeError) as error:
            out['error']=[type(error).__name__,str(error)]
    return json.loads(json.dumps(out,default=lambda o:o.tolist()))


def targeted(case):
    """Named positions from the review, at the recovery start state."""
    def factory(start):
        def unperturbed(owner):return owner.time==start['time'] and owner.pack().tobytes() in start['packs']
        def at_start(owner):return owner.time==start['time']
        def predicate(where,owner,extra):
            if where=='advance':
                duration,dt=extra;fine=dt<.002;middle=.002<dt<.004
                if case=='passing_control_failing_kick' and at_start(owner) and not unperturbed(owner) and middle:return 'worker'
                if case=='numeric_control_failing_kick' and at_start(owner) and not unperturbed(owner) and fine:return 'worker'
                if case=='worker_control_diagnostic_kick' and unperturbed(owner) and fine:return 'worker'
                return None
            if case=='numeric_control_failing_kick' and unperturbed(owner):return 'numeric'
            if case=='worker_control_diagnostic_kick' and at_start(owner) and not unperturbed(owner):return 'diagnostic'
            return None
        return Injection(predicate=predicate)
    return factory


@pytest.mark.parametrize('order',['forward','reverse'])
@pytest.mark.parametrize('case',['passing_control_failing_kick','numeric_control_failing_kick','worker_control_diagnostic_kick'])
def test_batched_recovery_failures_keep_sequential_prefix_and_first_error(case,order):
    sequential=failing_experiment(False,order,targeted(case))
    concurrent=failing_experiment(True,order,targeted(case))
    result=compare(sequential,concurrent,0.,False)
    assert result['passed'],result
    scopes=[c['scope'] for c in sequential['checks']]
    if case=='passing_control_failing_kick':
        assert sequential['error'][0]=='RuntimeError' and scopes[-1]=='recovery/control'
    if case=='numeric_control_failing_kick':
        assert sequential['error'][0]=='NumericalFailure' and scopes[-1]=='recovery/control'
        assert not sequential['checks'][-1]['passed']
    if case=='worker_control_diagnostic_kick':
        assert sequential['error'][0]=='RuntimeError' and scopes==['fixture']


@pytest.mark.parametrize('order',['forward','reverse'])
def test_fuzzed_failures_at_every_level_match_sequential(order):
    """Input-determined worker, numerical and diagnostic failures, many salts."""
    stages=set()
    for salt in range(14):
        factory=lambda start,salt=salt:Injection(salt=salt,worker=23,numeric=11,diagnostic=13)
        sequential=failing_experiment(False,order,factory)
        concurrent=failing_experiment(True,order,factory)
        result=compare(sequential,concurrent,0.,False)
        assert result['passed'],(salt,result)
        assert sequential.get('error')==concurrent.get('error')
        scopes=[c['scope'] for c in sequential['checks']]
        stages.add(('error' in sequential,scopes[-1].split('/')[0],len(scopes)))
    # Failures land at several positions: in recovery, in causal at various forks, or none.
    assert len(stages)>=5 and any(not e for e,_,_ in stages)


NESTED={'any':None,
        # Stage 1: exposure and endpoint recovery/causal runs carry an emitting cohort.
        'conditions':lambda o:any(c.output==1. for c in o.cohorts),
        # Stage 2 episodes: the introduced population makes a second cohort.
        'episodes':lambda o:len(o.cohorts)==2}


@pytest.mark.parametrize('target,salt,rate',[('any',1,97),('any',5,97),('conditions',1,13),('conditions',5,29),
    ('conditions',4,7),('episodes',1,61),('episodes',2,61),('episodes',3,31)])
def test_fuzzed_nested_failures_in_concurrent_operation_match_sequential(target,salt,rate):
    """Failures inside stage tasks' recovery/causal/descriptor/episode runs."""
    def scenario(parallel):
        with Injection(salt=salt,worker=rate,numeric=rate+2,diagnostic=rate+4,only=NESTED[target]):
            return operation_scenario(True)
    with O.backend('native'):
        sequential=scenario(False)
        with Q.parallel():concurrent=scenario(True)
    result=compare(sequential,concurrent,0.,False)
    assert result['passed'],result
    assert sequential.get('error')==concurrent.get('error')
