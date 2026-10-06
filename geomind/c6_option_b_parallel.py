"""Bounded, ordered engineering parallelism for the unchanged option-B law.

One isolated world process owns four grid pool threads and one coordinator
compute slot. Nested forks are flattened into grid/block jobs; workers never
wait for other workers. Independent protocol tasks of one operation (the three
treatment conditions, then the four descriptors and up to nineteen formation
episodes) may run on a few coordinator threads, but only the thread holding the
coordinator token executes Python; every coordinator releases it while waiting.
At most five threads therefore compute at once. Each concurrent task writes its
own checks list; lists are joined in the original order, and the first failure
in that order is re-raised after exactly the checks the sequential run had made.
"""
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from contextlib import contextmanager
import hashlib
import threading
import time
import numpy as np
from geomind import c6_r4_field_assay as A, c6_r4_field as F
from geomind import c6_option_b as O
from geomind import c6_r4_field_protocol as P

THREADS_PER_WORLD = 5
WORLD_WORKERS = 2
# Concurrent protocol tasks (coordinator threads; one holds the compute token).
TASK_COORDINATORS = 4
_PARALLEL_LOCK = threading.Lock()


class Scheduler:
    def __init__(self, order='forward'):
        if order not in ('forward', 'reverse'):
            raise ValueError('unknown task submission order')
        self.order = order
        self.lib, _ = O.load()
        self.max_inflight = 0
        self.lock = threading.Lock()
        # Native caches are process-wide and configured once by O.backend;
        # a per-worker initializer must not reset them.
        self.pool = ThreadPoolExecutor(max_workers=THREADS_PER_WORLD-1, thread_name_prefix='c6-grid')
        self.tasks = ThreadPoolExecutor(max_workers=TASK_COORDINATORS, thread_name_prefix='c6-task')
        self.workers = set()
        self.submitted = 0
        self.max_submitted = 0
        self.task_batches = []
        # Coordinator compute token: held by the coordinator that runs Python,
        # released around every wait. Grid workers never take it.
        self.token = threading.Lock()
        self.local = threading.local()

    def holding(self):
        return getattr(self.local, 'holding', False)

    def acquire(self):
        self.token.acquire(); self.local.holding = True

    def release(self):
        self.local.holding = False; self.token.release()

    @contextmanager
    def waiting(self):
        held = self.holding()
        if held: self.release()
        try: yield
        finally:
            if held: self.acquire()

    def run_tasks(self, thunks):
        """Run independent coordinator tasks; results/exceptions by index."""
        if threading.current_thread().name.startswith('c6-task'):
            # A task waiting on subtasks could exhaust the bounded task pool.
            raise RuntimeError('Nested protocol tasks forbidden')
        def task(thunk):
            self.acquire()
            try: return thunk()
            finally: self.release()
        started = time.perf_counter()
        futures = [self.tasks.submit(task, thunk) for thunk in thunks]
        with self.waiting():
            wait(futures)
        self.task_batches.append({'tasks':len(thunks),'wall_seconds':time.perf_counter()-started})
        outcomes = []
        for future in futures:
            try: outcomes.append((None, future.result()))
            except BaseException as error: outcomes.append((error, None))
        return outcomes

    def invoke(self, fn, args):
        with self.lock:
            self.workers.add(threading.get_ident())
        return fn(*args)

    def completed(self, fn, jobs, costs=None, capture=False):
        # Bound submitted futures as well as workers. Every submitted job is
        # drained before this generator ends. capture=True yields
        # (index, error, result) for every job and never raises job errors;
        # otherwise results are yielded and the lowest-index error is raised.
        indices = list(range(len(jobs)))
        if costs is not None:
            indices.sort(key=lambda i:(-costs[i],i))
        if self.order == 'reverse': indices.reverse()
        todo = iter(indices); pending = {}; errors = {}
        def refill():
            while len(pending) < THREADS_PER_WORLD-1:
                try: i = next(todo)
                except StopIteration: break
                pending[self.pool.submit(self.invoke,fn,jobs[i])] = i
                with self.lock:
                    self.submitted += 1
                    self.max_submitted = max(self.max_submitted,self.submitted)
                    self.max_inflight = max(self.max_inflight,len(pending))
        refill()
        while pending:
            with self.waiting():
                done, _ = wait(pending,return_when=FIRST_COMPLETED)
            for future in done:
                i = pending.pop(future)
                with self.lock: self.submitted -= 1
                try: result = future.result()
                except BaseException as error:
                    if capture: yield i,error,None
                    else: errors[i] = error
                else:
                    if capture: yield i,None,result
                    else: yield i,result
            # Release completed futures/results before queuing more full blocks.
            done.clear()
            refill()
        if errors:
            raise errors[min(errors)]

    def map(self, fn, jobs):
        results = [None]*len(jobs)
        for i,result in self.completed(fn,jobs): results[i] = result
        return results

    def summary(self):
        return {'threads_per_world':THREADS_PER_WORLD, 'world_workers':WORLD_WORKERS,
                'total_thread_budget':THREADS_PER_WORLD*WORLD_WORKERS,
                'submission_order':self.order, 'maximum_inflight_jobs':self.max_inflight,
                'worker_threads_used':len(self.workers),
                'task_coordinators':TASK_COORDINATORS, 'maximum_submitted_jobs':self.max_submitted,
                'concurrent_task_batches':list(self.task_batches),
                'native_cache_process_totals':O.cache_stats(self.lib)}

    def close(self):
        try: self.tasks.shutdown(wait=True, cancel_futures=True)
        finally: self.pool.shutdown(wait=True, cancel_futures=True)


def grid_block(owner, initial, duration, dt):
    # No shared owner mutation. F.advance returns a new complete owner.
    end, flow = F.advance(owner, duration, dt[0], dt[1])
    outgoing = F.emissions(initial, flow)
    return end, flow, outgoing


class Outcome:
    """Terminal outcome of one GridSet.run request, published later in order.

    Exactly one of: error (the first exception the sequential run would
    raise, with no check made), or a check (made, then NumericalFailure when
    it did not pass) and the collected frames.
    """
    __slots__ = ('grid','error','check','passed','maxima','scope','result')
    def __init__(self, grid, scope):
        self.grid, self.scope = grid, scope
        self.error = self.check = self.maxima = self.result = None
        self.passed = False


def publish(outcome):
    """Do what the sequential GridSet.run did at its end: raise its first error,
    or append its check, raise if not passed, and return its frames."""
    if outcome.error is not None:
        raise outcome.error
    outcome.grid.checks.append(outcome.check)
    if not outcome.passed:
        raise A.NumericalFailure(outcome.scope, outcome.maxima)
    return outcome.result


def _initial_state(grid, duration, scope, sample_dt):
    # Same statements, in the same order, as GridSet.run before its loop.
    dt = grid.s['dt']; sample_dt = grid.s['frame_dt'] if sample_dt is None else sample_dt
    F.exact_steps(sample_dt, dt); F.exact_steps(duration, sample_dt)
    initial = [o.clone() for o in grid.owners]
    collected = [[o.pack()] for o in grid.owners]; maxima = {'position':0., 'phase':0., 'field':0.}
    trace = [hashlib.sha256() for _ in range(3)]
    powers = [np.zeros(len(initial[0].z)) for _ in range(3)]; out_max = [0.,0.,0.]; first = [None,None,None]
    scales = []
    for c in grid.owners[0].cohorts:
        scale = A.D.radius_of_gyration(c.x)
        if not np.isfinite(scale) or scale <= 0:
            raise ValueError('invalid initial material normalization')
        scales.append(scale)
    intervals = F.exact_steps(duration, sample_dt)
    return dict(grid=grid, duration=duration, scope=scope, sample_dt=sample_dt, dt=dt,
        initial=initial, scales=scales, collected=collected, maxima=maxima, trace=trace,
        powers=powers, out_max=out_max, first=first, intervals=intervals,
        block_intervals=max(1,int(10./sample_dt)), begin=0)


def _merge_block(st, block_duration, results):
    """Coarse-to-fine merge of one block, in GridSet.run statement order."""
    flows = []
    for k, (end, flow, outgoing) in enumerate(results):
        st['grid'].owners[k] = end
        flows.append(flow)
        stride = F.exact_steps(st['sample_dt'],st['dt'])
        st['collected'][k].extend(flow[stride::stride].copy())
        st['trace'][k].update(flow[1:,2*len(st['initial'][k].z):].tobytes())
        st['powers'][k] += np.sum(np.abs(outgoing[1:])**2,axis=0)*st['dt']
        st['out_max'][k] = max(st['out_max'][k],float(np.abs(outgoing).max()))
        indices = np.flatnonzero(np.max(np.abs(outgoing),axis=1)>0)
        if st['first'][k] is None and len(indices):
            st['first'][k] = end.time-block_duration+int(indices[0])*st['dt']
    errors = A.state_errors(st['initial'][0],flows,st['scales'])
    for name in st['maxima']:st['maxima'][name] = max(st['maxima'][name],errors[name])
    st['begin'] += st['block_intervals']


def _finish(st, outcome):
    limits = st['grid'].s['numerics']; maxima = st['maxima']
    passed = all(maxima[k] <= limits[k] for k in maxima)
    outcome.check = {'scope':st['scope'],'start':st['initial'][0].time,'duration':st['duration'],
        'dt_values':[st['dt'],st['dt']/2,st['dt']/4], 'max_errors':maxima,
        'normalization_sizes':st['scales'],'passed':passed,
        'initial_ids':[o.identity() for o in st['initial']], 'end_ids':st['grid'].identities(),
        'source_trace_hash_by_dt':[h.hexdigest() for h in st['trace']], 'output_max_by_dt':st['out_max'],
        'output_power_by_dt':[p.tolist() for p in st['powers']], 'first_output_time_by_dt':st['first'],
        'output_check_method':'Full selected-member outgoing channels computed (or reused on identical physical inputs) before masks; bounded temporary arrays and byte-limited immutable cache. Python norms are derived diagnostics. All-off native actual-medium evolution omits cohorts; independent native RHS/channel contracts verify that path.'}
    outcome.passed, outcome.maxima = passed, maxima
    outcome.result = [np.array(c) for c in st['collected']]


def run_many(scheduler, requests):
    """Run independent GridSet.run requests together; return their outcomes.

    Nothing is published here. Each request's outcome is exactly what its
    sequential run would end with: grid jobs of one block are merged
    coarse-to-fine after all three finished, so the first error inside a
    request is the one the sequential run meets first (grid k before k+1,
    the diagnostic after the three grids, the check after the last block).
    A failed request stops; others continue. Callers publish() outcomes in
    the original request order, interleaved with their own statements.
    """
    states = []; outcomes = []
    for grid, duration, scope, sample_dt in requests:
        outcome = Outcome(grid, scope); outcomes.append(outcome)
        try: states.append(_initial_state(grid, duration, scope, sample_dt))
        except Exception as error:
            outcome.error = error; states.append(None)
    def live(j):
        st = states[j]
        return st is not None and outcomes[j].error is None and st['begin'] < st['intervals']
    while any(live(j) for j in range(len(states))):
        jobs = []; active = {}; locations = []; costs = []
        for j, st in enumerate(states):
            if not live(j):continue
            block_duration = min(st['block_intervals'],st['intervals']-st['begin'])*st['sample_dt']
            active[j] = (block_duration, [None]*3)
            for k in range(3):
                owner = st['grid'].owners[k]
                jobs.append((owner,st['initial'][k],block_duration,(st['dt']/(2**k),st['dt'])))
                locations.append((j,k))
                costs.append(block_duration/(st['dt']/(2**k)) * max(1,len(owner.cohorts)))
        for index, error, result in scheduler.completed(grid_block,jobs,costs,capture=True):
            j,k = locations[index]; block_duration, slots = active[j]
            slots[k] = (error, result)
            if any(slot is None for slot in slots):continue
            try:
                for slot_error, _ in slots:
                    if slot_error is not None:raise slot_error
                _merge_block(states[j], block_duration, [r for _, r in slots])
            except Exception as failure:
                outcomes[j].error = failure
            del active[j]; del slots, result
    for j, st in enumerate(states):
        if outcomes[j].error is not None:continue
        try: _finish(st, outcomes[j])
        except Exception as error:
            outcomes[j].error = error; outcomes[j].check = None
    return outcomes


@contextmanager
def parallel(order='forward'):
    """Select inside O.backend('native'); exit before restoring that backend."""
    if not O._ACTIVE_NATIVE:
        raise RuntimeError('Parallel option B requires an active native backend')
    if not _PARALLEL_LOCK.acquire(blocking=False):
        raise RuntimeError('Nested parallel selection forbidden')
    previous_grid, previous_recovery, previous_causal = A.GridSet, A.recovery, A.causal
    try:
        scheduler = Scheduler(order)
    except BaseException:
        _PARALLEL_LOCK.release()
        raise
    class ParallelGridSet(previous_grid):
        def clone(self):return ParallelGridSet(self.owners,self.s,self.checks)
        def run(self,duration,scope,sample_dt=None):
            return publish(run_many(scheduler,[(self,duration,scope,sample_dt)])[0])
    def recovery(grid,members,locks,pert,scope):
        return parallel_recovery(scheduler,grid,members,locks,pert,scope)
    def causal(grid,members,pert,scope):
        return parallel_causal(scheduler,grid,members,pert,scope)
    previous_operation = P.operation
    def operation(grid,qualification,qualification_flows,entropy,world,turn,alpha,scope):
        return parallel_operation(scheduler,ParallelGridSet,grid,qualification,qualification_flows,
                                  entropy,world,turn,alpha,scope)
    A.GridSet, A.recovery, A.causal, P.operation = ParallelGridSet, recovery, causal, operation
    scheduler.acquire()
    try:
        yield scheduler
    finally:
        # Drain every task before any module/backend restoration, even on errors.
        try:
            if scheduler.holding():scheduler.release()
            scheduler.close()
        finally:
            A.GridSet, A.recovery, A.causal, P.operation = previous_grid, previous_recovery, previous_causal, previous_operation
            _PARALLEL_LOCK.release()


def ordered(scheduler, shared, thunks):
    """Run tasks concurrently, each with a private checks list; join in order.

    Returns all results. On the first failure in task order, the checks of the
    earlier tasks and the failing task's partial checks are appended (exactly
    what the sequential loop had appended) and that failure is re-raised.
    """
    privates = [[] for _ in thunks]
    outcomes = scheduler.run_tasks([lambda t=t, c=c: t(c) for t, c in zip(thunks, privates)])
    results = []
    for private, (error, result) in zip(privates, outcomes):
        shared.extend(private)
        if error is not None:
            raise error
        results.append(result)
    return results


def parallel_operation(scheduler,GridSet,grid,qualification,qualification_flows,entropy,world,turn,alpha,scope):
    """P.operation with its independent tasks run concurrently, in two stages.

    Stage 1: the three treatment conditions (exposure, persistence, endpoint
    qualification). Stage 2: the four response descriptors and, when eligible,
    the before-formation and condition episodes. Every task computes exactly
    what the sequential loop computes on identical inputs; results, checks and
    the first failure are taken in the original order.
    """
    s=grid.s;members=qualification['selected_members'];before=grid.identities()
    branches={};records={};operation_checks={}
    pert=P.physical_perturbations(P.rng(entropy,world,30,turn),grid.owners[0])
    shared=grid.checks
    def condition_task(condition):
        def run(checks):
            # grid.clone(), with this task's private checks list.
            branch=GridSet(grid.owners,grid.s,checks)
            for o in branch.owners:
                for c in o.cohorts:c.output=0.
                c=o.cohorts[-1];c.selected=tuple(members);c.output=0. if condition=='no_backreaction' else 1.
                c.mode='no_r' if condition=='no_r' else 'intact'
            branch_start=branch.identities()
            flows=branch.run(s['exposure'],scope+'/operation/'+condition)
            op_check=next(c for c in reversed(checks) if c['scope']==scope+'/operation/'+condition)
            persistent=[P.rolling_persistence(qualification_flows[k],flows[k],branch.owners[k],members,s) for k in range(3)]
            masks=[[r['passed'] for r in rows] for rows in persistent]
            if masks[1:]!=[masks[0],masks[0]]:raise A.NumericalFailure('grid-dependent persistence')
            end=A.qualification(branch,flows,pert,scope+'/operation/'+condition+'/endpoint',forced_members=members)
            record={'start_ids':branch_start,'operation_end_ids':branch.identities(),'persistence_by_dt':persistent,
                    'operation_end_states':[P.snapshot(o) for o in branch.owners],'operation_frames':flows[0].tolist(),
                    'endpoint_qualification':end,'output_check':op_check}
            for o in branch.owners:
                for c in o.cohorts:c.output=0.
            record['after_ids']=branch.identities();record['after_states']=[P.snapshot(o) for o in branch.owners]
            record['background_diagnostics']={'mean_amplitude_by_dt':[float(np.mean(np.abs(o.z))) for o in branch.owners],
                'amplitude_weighted_coherence_by_dt':[float(abs(np.sum(o.z))/np.sum(np.abs(o.z))) if np.sum(np.abs(o.z))>0 else None for o in branch.owners]}
            return branch,record,op_check
        return run
    for condition,(branch,record,op_check) in zip(P.CONDITIONS,ordered(scheduler,shared,[condition_task(c) for c in P.CONDITIONS])):
        branch.checks=shared  # Later descriptors/episodes of the branch append to the shared list.
        operation_checks[condition]=op_check;branches[condition]=branch;records[condition]=record
    if (operation_checks['intact']['source_trace_hash_by_dt']!=operation_checks['no_backreaction']['source_trace_hash_by_dt']
            or any(operation_checks['no_backreaction']['output_max_by_dt'])):
        raise ValueError('sham source preservation/output failure')
    if records['no_r']['endpoint_qualification']['qualified']:raise ValueError('NO-R remains qualified')
    for control in P.CONTROLS:
        records[control]['background_diagnostics']['state_distance_vs_intact_by_dt']=[float(np.sqrt(np.mean(np.abs(a.z-b.z)**2))) for a,b in zip(branches['intact'].owners,branches[control].owners)]
    eligible=all(r['passed'] for r in records['intact']['persistence_by_dt'][0]) and records['intact']['endpoint_qualification']['qualified']
    outcome='PERSISTENT_UNIT' if eligible else 'SOURCE_LOST_DURING_OPERATION'
    first_loss=next((r['time'] for r in records['intact']['persistence_by_dt'][0] if not r['passed']),
                    grid.owners[0].time+s['exposure'] if not eligible else None)
    cell={'turn':turn,'before_ids':before,'source':qualification,'operation_eligible':bool(eligible),
          'physical_outcome':outcome,'first_loss_time':first_loss,'conditions':records,'controls_passed':True,'response':{},'episodes':{},'before_formation':None,'before_response':None}
    def descriptor_task(target,name):
        # A.descriptor reads target and works on target.clone() only.
        return lambda checks:A.descriptor(GridSet(target.owners,target.s,checks),alpha,name)
    def episode_task(target,episode,name):
        # qualify_episode reads background owners/settings and appends checks.
        return lambda checks:P.qualify_episode(GridSet(target.owners,target.s,checks),entropy,world,turn,episode,name)
    tasks=[descriptor_task(grid,scope+'/before-response')]
    tasks+=[descriptor_task(branches[c],scope+'/response/'+c) for c in P.CONDITIONS]
    episode_keys=[]
    if eligible:
        for episode in s['measurement_episodes']:
            tasks.append(episode_task(grid,episode,scope+f'/before/e{episode}'));episode_keys.append(('before',episode))
        for condition in P.CONDITIONS:
            for episode in [0,*s['measurement_episodes']]:
                tasks.append(episode_task(branches[condition],episode,scope+f'/{condition}/e{episode}'))
                episode_keys.append((condition,episode))
    results=iter(ordered(scheduler,shared,tasks))
    cell['before_response']=next(results)
    for condition in P.CONDITIONS:
        cell['response'][condition]=next(results)
    # Loss removes causal eligibility, never the scheduled diagnostic assay.
    if not eligible:return cell,None
    diagnostics=[];continuation=None
    for (condition,episode),(next_grid,q,record) in zip(episode_keys,results):
        next_grid.checks=shared  # As introduce() shares the background list.
        if condition=='before':diagnostics.append(record);continue
        cell['episodes'].setdefault(condition,[]).append(record)
        if condition=='intact' and episode==0 and q['qualified']:
            continuation=(next_grid,q)
    cell['before_formation']=diagnostics
    for control in P.CONTROLS:
        diff=np.array(cell['response']['intact']['gain_by_dt'])-np.array(cell['response'][control]['gain_by_dt'])
        if np.max(np.abs(diff[:2]-diff[2]))>s['numerics']['response']:raise A.NumericalFailure('paired gain refinement')
    cell['witness_tuple']=[cell['episodes'][c][0]['qualification']['qualified'] for c in P.CONDITIONS]
    return cell,continuation


def parallel_recovery(scheduler,grid,members,locks,pert,scope):
    s=grid.s;d=s['detector'];base=grid.clone();kick=grid.clone()
    for o in kick.owners:
        c=o.cohorts[-1];spacing=float(np.median(A.D.nn_spacing(c.x[members])))
        if not np.isfinite(spacing) or spacing<=0:raise ValueError('invalid member spacing')
        dx=pert['position'][members].copy();norm=np.sqrt(np.mean(np.sum(dx*dx,axis=1)))
        if norm<=0:raise ValueError('zero position probe')
        c.x[members]+=dx*d['kick_position']*spacing/norm
        c.theta[members]+=A.normalize_phase(pert['phase'],members,d['kick_phase'])
    # Sequential order: base.run, then kick.run (each publishes its check).
    for outcome in run_many(scheduler,[(base,d['recovery_time'],scope+'/control',None),
                                       (kick,d['recovery_time'],scope+'/kicked',None)]):
        publish(outcome)
    result=[]
    for a,b,lock in zip(base.owners,kick.owners,locks):
        ac,bc=a.cohorts[-1],b.cohorts[-1]
        original_to_control,labels=A.D.best_match(ac.x,members,d['link_factor'],lock)
        matches=[np.flatnonzero(labels==j) for j in np.unique(labels)]
        matched=max(matches,key=lambda m:A.D.jaccard(members,m))
        original_to_kicked=A.D.best_match(bc.x,members,d['link_factor'],lock)[0]
        control_to_kicked=A.D.best_match(bc.x,matched,d['link_factor'],lock)[0]
        result.append({'recovery_original_to_control':float(original_to_control),'recovery_original_to_kicked':float(original_to_kicked),
            'recovery_control_to_kicked':float(control_to_kicked),'recovery_jaccard':float(min(original_to_control,original_to_kicked,control_to_kicked)),
            'recovery_pattern_error':float(np.abs(A.wrap(A.D.pair_differences(bc.theta,members)-A.D.pair_differences(ac.theta,members))).max())})
    return result

def parallel_causal(scheduler,grid,members,pert,scope):
    s=grid.s;iv=s['causal'];values={};forks=[];requests=[]
    for direction,duration,mode in [('g_to_m',iv['gm_window'],'no_geometry_to_mode'),('m_to_g',iv['mg_window'],'no_mode_to_geometry')]:
        for label in ('intact','ablated'):
            control=grid.clone();treated=grid.clone()
            for a,b in zip(control.owners,treated.owners):
                ac,bc=a.cohorts[-1],b.cohorts[-1]
                if label=='ablated':
                    ac.mode=bc.mode=mode;ac.origin=ac.x.copy();bc.origin=ac.x.copy()
                if direction=='g_to_m':
                    delta=A.normalize_phase(pert['probe'],members,iv['phase_rms'])
                    ac.theta[members]+=delta;bc.theta[members]+=delta
                    X=bc.x[members];bc.x[members]=X.mean(0)+iv['gm_scale']*(X-X.mean(0))
                else:bc.theta[members]=pert['replacement'][members]
            forks.append((direction,label,control,treated))
            requests.extend([(control,duration,scope+'/'+direction+'/'+label+'/control',s['probe_sample_dt']),
                             (treated,duration,scope+'/'+direction+'/'+label+'/treated',s['probe_sample_dt'])])
    # Fork set-up runs first here; its only raising statement (normalize_phase
    # of the same probe and members) is identical for every fork, so it raises
    # at the first fork exactly as the sequential loop does. Outcomes are then
    # published fork by fork, interleaved with each fork's measurement.
    outcomes=iter(run_many(scheduler,requests))
    for direction,label,control,treated in forks:
        a=publish(next(outcomes));b=publish(next(outcomes))
        measured=[]
        for k in range(3):
            ax,at=A.frames(a[k],control.owners[k]);bx,bt=A.frames(b[k],treated.owners[k])
            if direction=='g_to_m':v=A.wrap(A.D.pair_differences(bt,members)-A.D.pair_differences(at,members))
            else:v=(bx[:,members]-ax[:,members])/A.D.radius_of_gyration(grid.owners[k].cohorts[-1].x[members])
            measured.append(float(np.sqrt(np.mean(np.sum(v*v,axis=-1))) if direction=='m_to_g' else np.sqrt(np.mean(v*v))))
        values.setdefault(direction,{})[label]=measured
    return values

