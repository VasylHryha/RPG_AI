"""Owner-side C4 statistics, new-law recovery and complete causal ablations."""
import copy
import hashlib
import json
import numpy as np
from geomind import c4_detect as D
from geomind.c4_model import wrap
from geomind import c6_r4_field as F

class GridSet:
    """Three independent full owners, streamed at every production-grid time."""
    def __init__(self,owners,settings,checks=None):
        self.owners=[o.clone() for o in owners];self.s=settings
        self.checks=[] if checks is None else checks
    def clone(self):return GridSet(self.owners,self.s,self.checks)
    def identities(self):return [o.identity() for o in self.owners]
    def run(self,duration,scope,sample_dt=None):
        dt=self.s['dt'];sample_dt=self.s['frame_dt'] if sample_dt is None else sample_dt
        F.exact_steps(sample_dt,dt);F.exact_steps(duration,sample_dt)
        initial=[o.clone() for o in self.owners]
        collected=[[o.pack()] for o in self.owners];maxima={'position':0.,'phase':0.,'field':0.}
        trace=[hashlib.sha256() for _ in range(3)]
        powers=[np.zeros(len(initial[0].z)) for _ in range(3)];out_max=[0.,0.,0.];first=[None,None,None]
        scales=[]
        for c in self.owners[0].cohorts:
            scale=D.radius_of_gyration(c.x)
            if not np.isfinite(scale) or scale<=0:raise ValueError('invalid initial material normalization')
            scales.append(scale)
        # Block at requested sample times, compare every production step; never
        # keep every refined step or feed fine owners a coarse carrier.
        intervals=F.exact_steps(duration,sample_dt)
        # Bound transient full-resolution memory while amortizing owner copies,
        # native guards and exact passive-source cache keys across probe samples.
        block_intervals=max(1,int(10./sample_dt))
        for begin in range(0,intervals,block_intervals):
            block_duration=min(block_intervals,intervals-begin)*sample_dt
            flows=[]
            for k in range(3):
                self.owners[k],flow=F.advance(self.owners[k],block_duration,dt/(2**k),dt)
                flows.append(flow)
                # Views of sampled rows would pin every full production-grid
                # block until the end of the scope, defeating streaming.
                stride=F.exact_steps(sample_dt,dt)
                collected[k].extend(flow[stride::stride].copy())
                trace[k].update(flow[1:,2*len(initial[k].z):].tobytes())
                outgoing=F.emissions(initial[k],flow)
                powers[k]+=np.sum(np.abs(outgoing[1:])**2,axis=0)*dt
                out_max[k]=max(out_max[k],float(np.abs(outgoing).max()))
                indices=np.flatnonzero(np.max(np.abs(outgoing),axis=1)>0)
                if first[k] is None and len(indices):first[k]=self.owners[k].time-block_duration+int(indices[0])*dt
            errors=state_errors(initial[0],flows,scales)
            for name in maxima:maxima[name]=max(maxima[name],errors[name])
        limits=self.s['numerics'];passed=all(maxima[k]<=limits[k] for k in maxima)
        self.checks.append({'scope':scope,'start':initial[0].time,'duration':duration,'dt_values':[dt,dt/2,dt/4],
                            'max_errors':maxima,'normalization_sizes':scales,'passed':passed,
                            'initial_ids':[o.identity() for o in initial],'end_ids':self.identities(),
                            'source_trace_hash_by_dt':[h.hexdigest() for h in trace],'output_max_by_dt':out_max,
                            'output_power_by_dt':[p.tolist() for p in powers],'first_output_time_by_dt':first,
                            'output_check_method':'Full selected-member outgoing channels computed (or reused on identical physical inputs) before masks; bounded temporary arrays and byte-limited immutable cache. Python norms are derived diagnostics. All-off native actual-medium evolution omits cohorts; independent native RHS/channel contracts verify that path.'})
        if not passed:raise NumericalFailure(scope,maxima)
        return [np.array(c) for c in collected]

class NumericalFailure(ValueError):pass

def state_errors(owner,flows,scales):
    errors={'position':0.,'phase':0.,'field':0.};ns=len(owner.z)
    width=2*ns+sum(3*len(c.theta)+2*ns for c in owner.cohorts)
    if (len(flows)!=3 or any(f.ndim!=2 or f.shape[0]<1 or f.shape[1]!=width or not np.isfinite(f).all() for f in flows)
            or any(f.shape!=flows[0].shape for f in flows) or len(scales)!=len(owner.cohorts)
            or any(not np.isfinite(L) or L<=0 for L in scales)):
        raise NumericalFailure('invalid full-scope state/normalization')
    for coarse in flows[:2]:
        delta=coarse-flows[2]
        if not np.isfinite(delta).all():raise NumericalFailure('nonfinite full-scope difference')
        errors['field']=max(errors['field'],float(np.max(np.abs(delta[:,:2*ns].copy().view('c16')))))
        offset=2*ns
        for c,L in zip(owner.cohorts,scales):
            n=len(c.theta);dx=delta[:,offset:offset+2*n].reshape(-1,n,2);offset+=2*n
            errors['position']=max(errors['position'],float(np.linalg.norm(dx,axis=-1).max()/L))
            errors['phase']=max(errors['phase'],float(np.abs(wrap(delta[:,offset:offset+n])).max()));offset+=n
            errors['field']=max(errors['field'],float(np.abs(delta[:,offset:offset+2*ns].copy().view('c16')).max()));offset+=2*ns
    if not np.isfinite(list(errors.values())).all():raise NumericalFailure('nonfinite full-scope error')
    return errors

def frames(flow,owner,index=-1):
    ns=len(owner.z);offset=2*ns
    if index<0:index+=len(owner.cohorts)
    for c in owner.cohorts[:index]:offset+=3*len(c.theta)+2*ns
    n=len(owner.cohorts[index].theta)
    return flow[:,offset:offset+2*n].reshape(-1,n,2),flow[:,offset+2*n:offset+3*n]

def perturbations(rng,n):
    return {'position':rng.normal(size=(n,2)),'phase':rng.normal(size=n),
            'probe':rng.normal(size=n),'replacement':rng.uniform(-np.pi,np.pi,n)}

def normalize_phase(a,m,rms):
    d=a[m].copy();d-=d.mean();norm=np.sqrt(np.mean(d*d))
    if norm<=0:raise ValueError('zero phase probe')
    return d*rms/norm

def recovery(grid,members,locks,pert,scope):
    s=grid.s;d=s['detector'];base=grid.clone();kick=grid.clone()
    for o in kick.owners:
        c=o.cohorts[-1];spacing=float(np.median(D.nn_spacing(c.x[members])))
        if not np.isfinite(spacing) or spacing<=0:raise ValueError('invalid member spacing')
        dx=pert['position'][members].copy();norm=np.sqrt(np.mean(np.sum(dx*dx,axis=1)))
        if norm<=0:raise ValueError('zero position probe')
        c.x[members]+=dx*d['kick_position']*spacing/norm
        c.theta[members]+=normalize_phase(pert['phase'],members,d['kick_phase'])
    base.run(d['recovery_time'],scope+'/control');kick.run(d['recovery_time'],scope+'/kicked')
    result=[]
    for a,b,lock in zip(base.owners,kick.owners,locks):
        ac,bc=a.cohorts[-1],b.cohorts[-1]
        original_to_control,labels=D.best_match(ac.x,members,d['link_factor'],lock)
        matches=[np.flatnonzero(labels==j) for j in np.unique(labels)]
        matched=max(matches,key=lambda m:D.jaccard(members,m))
        original_to_kicked=D.best_match(bc.x,members,d['link_factor'],lock)[0]
        control_to_kicked=D.best_match(bc.x,matched,d['link_factor'],lock)[0]
        result.append({'recovery_original_to_control':float(original_to_control),'recovery_original_to_kicked':float(original_to_kicked),
            'recovery_control_to_kicked':float(control_to_kicked),'recovery_jaccard':float(min(original_to_control,original_to_kicked,control_to_kicked)),
            'recovery_pattern_error':float(np.abs(wrap(D.pair_differences(bc.theta,members)-D.pair_differences(ac.theta,members))).max())})
    return result

def causal(grid,members,pert,scope):
    s=grid.s;iv=s['causal'];values={}
    for direction,duration,mode in [('g_to_m',iv['gm_window'],'no_geometry_to_mode'),('m_to_g',iv['mg_window'],'no_mode_to_geometry')]:
        effects={}
        for label in ('intact','ablated'):
            control=grid.clone();treated=grid.clone()
            for a,b in zip(control.owners,treated.owners):
                ac,bc=a.cohorts[-1],b.cohorts[-1]
                if label=='ablated':
                    ac.mode=bc.mode=mode;ac.origin=ac.x.copy();bc.origin=ac.x.copy()
                if direction=='g_to_m':
                    delta=normalize_phase(pert['probe'],members,iv['phase_rms'])
                    ac.theta[members]+=delta;bc.theta[members]+=delta
                    X=bc.x[members];bc.x[members]=X.mean(0)+iv['gm_scale']*(X-X.mean(0))
                else:bc.theta[members]=pert['replacement'][members]
            a=control.run(duration,scope+'/'+direction+'/'+label+'/control',s['probe_sample_dt'])
            b=treated.run(duration,scope+'/'+direction+'/'+label+'/treated',s['probe_sample_dt'])
            measured=[]
            for k in range(3):
                ax,at=frames(a[k],control.owners[k]);bx,bt=frames(b[k],treated.owners[k])
                if direction=='g_to_m':v=wrap(D.pair_differences(bt,members)-D.pair_differences(at,members))
                else:v=(bx[:,members]-ax[:,members])/D.radius_of_gyration(grid.owners[k].cohorts[-1].x[members])
                measured.append(float(np.sqrt(np.mean(np.sum(v*v,axis=-1))) if direction=='m_to_g' else np.sqrt(np.mean(v*v))))
            effects[label]=measured
        values[direction]=effects
    return values

def closure_valid(effects,s):
    qualified=True
    for direction in ('g_to_m','m_to_g'):
        values=effects[direction];intact=values['intact'];ablated=values['ablated'];iv=s['causal']
        if len(intact)!=3 or len(ablated)!=3 or not np.isfinite(intact+ablated).all() or min(intact+ablated)<0:raise ValueError('invalid causal grids')
        smallest=min(intact)
        decisions=[v>iv['floor'] for v in intact]
        if len(set(decisions))!=1:raise NumericalFailure('grid-dependent causal qualification')
        if all(decisions) and max(intact)-smallest>iv['relative_spread']*smallest:
            raise NumericalFailure('causal effect refinement failed')
        if max(ablated)>max(iv['vanish_absolute'],iv['vanish_fraction']*smallest):
            raise ValueError('complete causal ablation leaves the named path')
        qualified=qualified and all(decisions)
    return qualified

def qualification(grid,flows,pert,scope,forced_members=None):
    s=grid.s;d=s['detector'];count=F.exact_steps(s['window'],s['frame_dt'])+1
    all_rows=[];all_locks=[]
    for k in range(3):
        xs,ths=frames(flows[k][-count:],grid.owners[k]);locks=D.locked_pairs(ths,d['lock_std']);all_locks.append(locks)
        labels=D.components(xs[-1],d['link_factor'],locks);rows=[]
        candidates=[np.flatnonzero(labels==c) for c in np.unique(labels)] if forced_members is None else [np.array(forced_members)]
        for m in candidates:
            if len(m)<d['min_size']:continue
            if D.radius_of_gyration(xs[-1,m])<=0 or np.median(D.nn_spacing(xs[-1,m]))<=0:raise ValueError('degenerate candidate geometry')
            stats=D.window_statistics(xs,ths,m,s['frame_dt'],d['link_factor'],locks)
            if not all(np.isfinite(v) for v in stats.values()):raise ValueError('nonfinite structural statistics')
            ok=(stats['membership_jaccard']>=d['membership_jaccard'] and stats['shape_cv']<=d['shape_cv'] and
                stats['lock_std']<=d['lock_std'] and stats['freq_change']<=d['freq_tol'] and stats['pattern_change']<=d['pattern_tol'])
            rows.append({'members':m.tolist(),'stats':stats,'structural':bool(ok)})
        all_rows.append(rows)
    inventories=[[tuple(sorted(grid.owners[k].cohorts[-1].ids[i] for i in r['members'])) for r in rows if r['structural']] for k,rows in enumerate(all_rows)]
    if any(set(x)!=set(inventories[0]) for x in inventories[1:]):raise NumericalFailure('grid-dependent structural candidates')
    # Recovery all structurally accepted candidates; selection only after this.
    accepted=[]
    for row in all_rows[0]:
        if not row['structural']:continue
        m=np.array(row['members']);recover=recovery(grid,m,all_locks,pert,scope+'/recovery/'+member_identity(grid.owners[0],m)[:12])
        recovered=[r['recovery_jaccard']>=d['recovery_jaccard'] and r['recovery_pattern_error']<=d['pattern_tol'] for r in recover]
        if len(set(recovered))!=1:raise NumericalFailure('grid-dependent recovery')
        row['recovery_by_dt']=recover;row['accepted']=bool(recovered[0]);row['stats'].update(recover[0])
        if row['accepted']:accepted.append(row)
    c=grid.owners[0].cohorts[-1]
    selected=select_accepted(accepted,c.tokens)
    result={'candidates':all_rows[0],'selected_members':None,'selected_identity':None,'qualified':False,'causal':None,'publication':None}
    if selected is None:return result
    m=np.array(selected['members']);effects=causal(grid,m,pert,scope+'/causal');qualified=closure_valid(effects,s)
    result.update(selected_members=m.tolist(),selected_identity=member_identity(grid.owners[0],m),causal=effects,qualified=qualified)
    if qualified:
        cc=grid.owners[0].cohorts[-1];xs,ths=frames(flows[0][-count:],grid.owners[0])
        result['publication']={'candidate':result['selected_identity'],'snapshot':grid.owners[0].identity(),'ids':[cc.ids[i] for i in m],
            'size':D.radius_of_gyration(cc.x[m]),'centroid':cc.x[m].mean(0).tolist(),'phase':float(D.circular_mean(cc.theta[m])),
            'rate':float(np.mean(ths[-1,m]-ths[0,m])/s['window']),'S':copy.deepcopy(selected['stats']),
            'units':{'size':'L0','centroid':'L0','phase':'rad','rate':'rad/C0'}}
    return result

def member_identity(owner,m):
    c=owner.cohorts[-1]
    return hashlib.sha256(json.dumps(sorted(c.ids[int(i)] for i in m)).encode()).hexdigest()

def select_accepted(rows,tokens):
    if len(set(tokens))!=len(tokens):raise ValueError('duplicate selection priorities')
    return min(rows,key=lambda r:(-len(r['members']),tuple(sorted(tokens[i] for i in r['members'])))) if rows else None

def descriptor(grid,alpha,scope):
    s=grid.s;off=grid.clone()
    for o in off.owners:
        for c in o.cohorts:c.output=0.
    control=off.clone();unperturbed=control.run(s['descriptor'],scope+'/control',s['probe_sample_dt'])
    ns=len(grid.owners[0].z);values=[[] for _ in range(3)];raw=[]
    for port in range(ns):
        for quadrature in (0,1):
            probe=off.clone()
            for o in probe.owners:
                impulse=.05*np.exp(1j*(alpha+o.phase_origin+quadrature*np.pi/2));o.z[port]+=impulse
            flows=probe.run(s['descriptor'],scope+f'/port{port}/q{quadrature}',s['probe_sample_dt'])
            responses=[]
            for k in range(3):
                # Exclude time zero, include the actual probed receiver.
                delta=(flows[k][1:,:2*ns]-unperturbed[k][1:,:2*ns]).copy().view('c16')/.05
                gain=float(np.sqrt(np.mean(np.abs(delta)**2)));values[k].append(gain)
                if k==0:responses=np.stack((delta.real,delta.imag),axis=-1).tolist()
            raw.append({'port':grid.owners[0].site_ids[port],'quadrature':quadrature,
                        'probe_phase_by_dt':[alpha+o.phase_origin+quadrature*np.pi/2 for o in off.owners],
                        'response_real_imag':responses})
    gains=[float(np.mean(v)) for v in values]
    if max(abs(gains[k]-gains[2]) for k in (0,1))>s['numerics']['response']:raise NumericalFailure('response gain refinement')
    return {'gain_by_dt':gains,'per_probe_by_dt':values,'raw':raw,'alpha':alpha,
            'phase_origin_by_dt':[o.phase_origin for o in off.owners],
            'site_ids':list(grid.owners[0].site_ids),'snapshot_ids':grid.identities()}
