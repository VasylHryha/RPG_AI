"""Bounded, ordered engineering parallelism for the unchanged option-B law.

One isolated world process owns one coordinator and four pool threads. Nested
forks are flattened into grid/block jobs; workers never wait for other workers.
Only the coordinator writes owners, checks, traces and reduction accumulators.
"""
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from contextlib import contextmanager
import hashlib
import threading
import numpy as np
from geomind import c6_r4_field_assay as A, c6_r4_field as F
from geomind import c6_option_b as O

THREADS_PER_WORLD = 5
WORLD_WORKERS = 2
_PARALLEL_LOCK = threading.Lock()


class Scheduler:
    def __init__(self, order='forward'):
        if order not in ('forward', 'reverse'):
            raise ValueError('unknown task submission order')
        self.order = order
        self.lib, _ = O.load()
        self.stats = {}
        self.max_inflight = 0
        self.lock = threading.Lock()
        self.pool = ThreadPoolExecutor(max_workers=THREADS_PER_WORLD-1,
            thread_name_prefix='c6-grid', initializer=lambda:self.lib.option_b_cache_limits(*O.CACHE_LIMITS))

    def invoke(self, fn, args):
        try:
            return fn(*args)
        finally:
            # These are thread-local cumulative counters and current payload
            # bytes. Snapshot on the worker itself, never on the coordinator.
            with self.lock:
                self.stats[threading.get_ident()] = O.cache_stats(self.lib)

    def completed(self, fn, jobs, costs=None):
        # Bound submitted futures as well as workers. Consumers discard outgoing
        # arrays immediately and retain full flows only for three-grid checks.
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
                self.max_inflight = max(self.max_inflight,len(pending))
        refill()
        while pending:
            done, _ = wait(pending,return_when=FIRST_COMPLETED)
            for future in done:
                i = pending.pop(future)
                try: result = future.result()
                except BaseException as error: errors[i] = error
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
        rows = list(self.stats.values())
        return {'threads_per_world':THREADS_PER_WORLD, 'world_workers':WORLD_WORKERS,
                'total_thread_budget':THREADS_PER_WORLD*WORLD_WORKERS,
                'submission_order':self.order, 'maximum_inflight_jobs':self.max_inflight, 'worker_threads_used':len(rows),
                'native_cache_worker_snapshots':rows,
                'native_cache_worker_totals':{k:sum(row[k] for row in rows) for k in rows[0]} if rows else {}}

    def close(self):
        self.pool.shutdown(wait=True, cancel_futures=True)


def grid_block(owner, initial, duration, dt):
    # No shared owner mutation. F.advance returns a new complete owner.
    end, flow = F.advance(owner, duration, dt[0], dt[1])
    outgoing = F.emissions(initial, flow)
    return end, flow, outgoing


def run_many(scheduler, requests):
    """Run independent futures together, retain each original GridSet.run order."""
    states = []
    for grid, duration, scope, sample_dt in requests:
        dt = grid.s['dt']
        sample_dt = grid.s['frame_dt'] if sample_dt is None else sample_dt
        F.exact_steps(sample_dt, dt); F.exact_steps(duration, sample_dt)
        initial = [o.clone() for o in grid.owners]
        scales = []
        for c in grid.owners[0].cohorts:
            scale = A.D.radius_of_gyration(c.x)
            if not np.isfinite(scale) or scale <= 0:
                raise ValueError('invalid initial material normalization')
            scales.append(scale)
        states.append(dict(grid=grid, duration=duration, scope=scope, sample_dt=sample_dt, dt=dt,
            initial=initial, scales=scales, collected=[[o.pack()] for o in grid.owners],
            maxima={'position':0., 'phase':0., 'field':0.}, trace=[hashlib.sha256() for _ in range(3)],
            powers=[np.zeros(len(initial[0].z)) for _ in range(3)], out_max=[0.,0.,0.], first=[None,None,None],
            intervals=F.exact_steps(duration, sample_dt), block_intervals=max(1,int(10./sample_dt)), begin=0))
    while any(st['begin'] < st['intervals'] for st in states):
        jobs = []; active = []; locations = []; costs = []
        for st in states:
            if st['begin'] >= st['intervals']:continue
            block_duration = min(st['block_intervals'],st['intervals']-st['begin'])*st['sample_dt']
            active.append((st, block_duration))
            for k in range(3):
                owner = st['grid'].owners[k]
                jobs.append((owner,st['initial'][k],block_duration,(st['dt']/(2**k),st['dt'])))
                locations.append((len(active)-1,k))
                costs.append(block_duration/(st['dt']/(2**k)) * max(1,len(owner.cohorts)))
        flows = [[None]*3 for _ in active]
        for index, (end,flow,outgoing) in scheduler.completed(grid_block,jobs,costs):
            j,k = locations[index]; st,block_duration = active[j]
            st['grid'].owners[k] = end
            flows[j][k] = flow
            stride = F.exact_steps(st['sample_dt'],st['dt'])
            st['collected'][k].extend(flow[stride::stride].copy())
            st['trace'][k].update(flow[1:,2*len(st['initial'][k].z):].tobytes())
            st['powers'][k] += np.sum(np.abs(outgoing[1:])**2,axis=0)*st['dt']
            st['out_max'][k] = max(st['out_max'][k],float(np.abs(outgoing).max()))
            indices = np.flatnonzero(np.max(np.abs(outgoing),axis=1)>0)
            if st['first'][k] is None and len(indices):
                st['first'][k] = end.time-block_duration+int(indices[0])*st['dt']
            if all(f is not None for f in flows[j]):
                # Within each three-grid diagnostic the reduction order stays
                # coarse-to-fine; states and per-grid sums are independent.
                errors = A.state_errors(st['initial'][0],flows[j],st['scales'])
                for name in st['maxima']:st['maxima'][name] = max(st['maxima'][name],errors[name])
                flows[j] = [None]*3
                st['begin'] += st['block_intervals']
            del flow,outgoing
    results = []
    for st in states:
        limits = st['grid'].s['numerics']; maxima = st['maxima']
        passed = all(maxima[k] <= limits[k] for k in maxima)
        st['grid'].checks.append({'scope':st['scope'],'start':st['initial'][0].time,'duration':st['duration'],
            'dt_values':[st['dt'],st['dt']/2,st['dt']/4], 'max_errors':maxima,
            'normalization_sizes':st['scales'],'passed':passed,
            'initial_ids':[o.identity() for o in st['initial']], 'end_ids':st['grid'].identities(),
            'source_trace_hash_by_dt':[h.hexdigest() for h in st['trace']], 'output_max_by_dt':st['out_max'],
            'output_power_by_dt':[p.tolist() for p in st['powers']], 'first_output_time_by_dt':st['first'],
            'output_check_method':'Full selected-member outgoing channels computed (or reused on identical physical inputs) before masks; bounded temporary arrays and byte-limited immutable cache. Python norms are derived diagnostics. All-off native actual-medium evolution omits cohorts; independent native RHS/channel contracts verify that path.'})
        if not passed:raise A.NumericalFailure(st['scope'],maxima)
        results.append([np.array(c) for c in st['collected']])
    return results


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
            return run_many(scheduler,[(self,duration,scope,sample_dt)])[0]
    def recovery(grid,members,locks,pert,scope):
        return parallel_recovery(scheduler,grid,members,locks,pert,scope)
    def causal(grid,members,pert,scope):
        return parallel_causal(scheduler,grid,members,pert,scope)
    A.GridSet, A.recovery, A.causal = ParallelGridSet, recovery, causal
    try:
        yield scheduler
    finally:
        # Drain every task before any module/backend restoration, even on errors.
        try:
            scheduler.close()
        finally:
            A.GridSet, A.recovery, A.causal = previous_grid, previous_recovery, previous_causal
            _PARALLEL_LOCK.release()


def parallel_recovery(scheduler,grid,members,locks,pert,scope):
    s=grid.s;d=s['detector'];base=grid.clone();kick=grid.clone()
    for o in kick.owners:
        c=o.cohorts[-1];spacing=float(np.median(A.D.nn_spacing(c.x[members])))
        if not np.isfinite(spacing) or spacing<=0:raise ValueError('invalid member spacing')
        dx=pert['position'][members].copy();norm=np.sqrt(np.mean(np.sum(dx*dx,axis=1)))
        if norm<=0:raise ValueError('zero position probe')
        c.x[members]+=dx*d['kick_position']*spacing/norm
        c.theta[members]+=A.normalize_phase(pert['phase'],members,d['kick_phase'])
    run_many(scheduler,[(base,d['recovery_time'],scope+'/control',None),
                        (kick,d['recovery_time'],scope+'/kicked',None)])
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
    flows=iter(run_many(scheduler,requests))
    for direction,label,control,treated in forks:
        a,b=next(flows),next(flows)
        measured=[]
        for k in range(3):
            ax,at=A.frames(a[k],control.owners[k]);bx,bt=A.frames(b[k],treated.owners[k])
            if direction=='g_to_m':v=A.wrap(A.D.pair_differences(bt,members)-A.D.pair_differences(at,members))
            else:v=(bx[:,members]-ax[:,members])/A.D.radius_of_gyration(grid.owners[k].cohorts[-1].x[members])
            measured.append(float(np.sqrt(np.mean(np.sum(v*v,axis=-1))) if direction=='m_to_g' else np.sqrt(np.mean(v*v))))
        values.setdefault(direction,{})[label]=measured
    return values

