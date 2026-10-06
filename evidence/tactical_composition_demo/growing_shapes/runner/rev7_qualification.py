"""New driven adapter importing the frozen C4 criterion functions read-only.

The locks used for recovery membership are the qualification-window locks,
exactly as in frozen c4_detect.detect. Entrants exert forces but are masked
from all membership comparisons. These are driven, cohort-restricted claims.
"""
import math
import hashlib
from pathlib import Path
import numpy as np
from geomind import c4_detect as c4
from ..medium.design_0h import wrap
from .rev7_protocol import template
from ..medium.rev7_design import clear_position

def assert_frozen_source():
    pins = {'c4_detect.py': 'ba7fd94efc0edf028df137dc617666c9b8540b914ab4fca1ce793c84d78aacb8',
            'c4_model.py': '4fafc161b65914a44dccaca6caefb59a5154079f17f564b4cdc4d44f58c59d33'}
    root = Path(c4.__file__).parent
    for name, expected in pins.items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'INVALID: frozen criterion source mismatch: {name}')


THRESHOLDS = dict(min_size=3, membership_jaccard=.95, shape_cv=.05, lock_std=.1,
                  freq_tol=.005, pattern_tol=.1, link_factor=1.5, recovery_jaccard=.9)


def alias_increment(ths, members):
    pairs = c4.pair_differences(ths, members)
    return float(np.max(np.abs(wrap(np.diff(pairs, axis=0))))) if pairs.size else 0.


def degenerate(xs):
    return any(np.any(c4.nn_spacing(x) <= 0) or len(c4._convex_hull(x)) < 3 for x in xs)


def start(medium):
    frames = list(medium.frames)
    if len(frames) != 601 or [f.index for f in frames] != list(range(medium.step_index-600, medium.step_index+1)):
        raise ValueError('INVALID: qualification requires 601 consecutive endpoint frames')
    alive = {e.id for e in medium.native.elements}
    first_index = medium.step_index-600
    # Growth follows the appended endpoint. A birth at the window's left
    # boundary has no sample in that endpoint and is an entrant, unlike the
    # initialized t=0 population recorded before its first qualification window.
    cohort = sorted(id for id in alive if medium.birth_steps[id] <= first_index
                    and not (medium.birth_steps[id] == first_index and id not in frames[0].elements))
    if any(id not in f.elements for id in cohort for f in frames):
        raise ValueError('INVALID: missing frame for whole-window cohort member')
    if len(cohort) < 3:
        return {'cohort': cohort, 'candidates': [], 'alias_max': 0., 'possibly_aliased': False, 'reason': 'small_cohort'}
    xs = np.array([[f.elements[id][:2] for id in cohort] for f in frames])
    ths = np.array([[f.elements[id][2] for id in cohort] for f in frames])
    if not np.isfinite(xs).all() or not np.isfinite(ths).all():
        raise ValueError('INVALID: non-finite qualification history')
    bounds=np.array([[f.excursion[id] for id in cohort] for f in frames])
    if not np.isfinite(bounds).all() or np.any(bounds<0):raise ValueError('INVALID: missing/nonfinite excursion history')
    maximum=float(np.max(bounds))
    pair_max=max((float(np.max(bounds[:,i]+bounds[:,j])) for i in range(len(cohort)) for j in range(i+1,len(cohort))),default=0.)
    if maximum>math.pi/2 or pair_max>math.pi/2:
        return dict(cohort=cohort,candidates=[],alias_max=max(maximum,pair_max),possibly_aliased=True,reason='fast_transient_cohort',invalid_individual_frames=int(np.sum(np.any(bounds>math.pi/2,axis=1))),invalid_pair_frames=sum(any(bounds[k,i]+bounds[k,j]>math.pi/2 for i in range(len(cohort)) for j in range(i+1,len(cohort))) for k in range(len(bounds))),warning='stage-sampling assumption')
    locked = c4.locked_pairs(ths, .1)
    labels = c4.components(xs[-1], 1.5, locked)
    candidates, maximum = [], max(maximum,pair_max)
    for label in np.unique(labels):
        members = np.flatnonzero(labels == label)
        if len(members) < 3:
            continue

        if degenerate(xs[:, members]):
            continue
        stats = c4.window_statistics(xs, ths, members, .1, 1.5, locked)
        if not np.isfinite(list(stats.values())).all():
            raise ValueError('INVALID: non-finite qualification statistic')
        check = dict(stats, recovery_jaccard=1., recovery_pattern_error=0.)
        if all(c4.criteria_checks(check, THRESHOLDS).values()):
            ids = [cohort[i] for i in members]
            candidates.append({'indices': members, 'ids': ids, 'stats': stats,
                               'template': template(medium.native, ids, medium.time,h=medium.h)})
    return {'cohort': cohort, 'candidates': candidates, 'locked': locked,
            'alias_max': maximum, 'possibly_aliased': maximum > math.pi/2,
            'warning': 'excursion screen is sufficient only under the RK4 stage-sampling assumption'}


def deviations(control, kicked, ids):
    a = {e.id: e for e in control.native.elements}
    b = {e.id: e for e in kicked.native.elements}
    phase = wrap([b[id].phase-a[id].phase for id in ids])
    phase = wrap(phase-c4.circular_mean(phase))
    dx = np.array([[b[id].x-a[id].x, b[id].y-a[id].y] for id in ids])
    dx -= dx.mean(0)
    return float(np.sqrt(np.mean(phase**2))), float(np.sqrt(np.mean(np.sum(dx**2, axis=1))))


def snapshot_order(candidates):
    return sorted(candidates, key=lambda c: (-len(c['ids']), min(c['ids'])))[:3]


def deviation_series(a, b):
    """Batch the frozen NumPy estimators with the same member reduction axes."""
    phase = np.ascontiguousarray(wrap(b[:,:,2]-a[:,:,2]))
    phase = wrap(phase-c4.circular_mean(phase,axis=1)[:,None])
    dx = np.ascontiguousarray(b[:,:,:2]-a[:,:,:2])
    dx -= dx.mean(1)[:,None,:]
    return np.sqrt(np.mean(phase**2,axis=1)), np.sqrt(np.mean(np.sum(dx**2,axis=2),axis=1))


def admissible_kick(saved,candidate,rng):
    elements=saved.native.elements;ids=[e.id for e in elements]
    x=np.array([[e.x,e.y] for e in elements]);phase=np.array([e.phase for e in elements])
    members=np.array([ids.index(id) for id in candidate['ids']],dtype=int)
    free=np.array([i for i in members if not saved.native.pin(ids[i])[0]],dtype=int)
    if not len(free):return None,dict(reason='no_free_member',draws=0,free_count=0)
    spacing=float(np.median(c4.nn_spacing(x[free])))
    if not math.isfinite(spacing) or spacing<=0:raise ValueError('INVALID: free-member spacing undefined')
    requested=.1*spacing
    for attempt in range(1,9):
        dx=rng.normal(size=(len(free),2));norm=float(np.sqrt(np.mean(np.sum(dx*dx,axis=1))))
        if not math.isfinite(norm) or norm==0:raise ValueError('INVALID: degenerate Gaussian position kick')
        dx*=requested/norm;kx=x.copy();kx[free]+=dx
        if all(clear_position(kx[i],[kx[j] for j in range(len(kx)) if j!=i]) for i in free):break
    else:return None,dict(reason='inadmissible_kick',draws=8,free_count=len(free),requested_position_rms=requested)
    dtheta=rng.normal(size=len(members));dtheta-=dtheta.mean()
    norm=float(np.sqrt(np.mean(dtheta*dtheta)))
    if not math.isfinite(norm) or norm==0:raise ValueError('INVALID: degenerate Gaussian phase kick')
    dtheta*=.3/norm;phase[members]+=dtheta
    achieved=float(np.sqrt(np.mean(np.sum((kx[free]-x[free])**2,axis=1))))
    return (kx,phase),dict(reason=None,draws=attempt,free_count=len(free),requested_position_rms=requested,achieved_position_rms=achieved,requested_phase_rms=.3,achieved_phase_rms=float(np.sqrt(np.mean(dtheta*dtheta))),clipped=False)


def cohort_frame_valid(diag,ids):
    bounds=diag['excursion']
    if any(id not in bounds or not math.isfinite(bounds[id]) or bounds[id]<0 for id in ids):raise ValueError('INVALID: recovery missing excursion')
    return all(bounds[id]<=math.pi/2 for id in ids) and all(bounds[a]+bounds[b]<=math.pi/2 for j,a in enumerate(ids) for b in ids[j+1:])


def anchored_displacement(control,kicked,ids):
    a={e.id:e for e in control.native.elements};b={e.id:e for e in kicked.native.elements}
    dx=np.array([[b[id].x-a[id].x,b[id].y-a[id].y] for id in ids])
    absolute=float(np.sqrt(np.mean(np.sum(dx*dx,axis=1))))
    # Every anchor is fixed in both futures; subtracting the same pin/site from
    # both coordinates gives the same displacement, unlike centroid removal.
    return dict(absolute_rms=absolute,anchor_relative_rms=absolute,anchor_policy='same fixed output/site coordinate in both futures')


def finish(saved,check,schedule,rng,*,backend='native',lib=None):
    if len(schedule)!=600:raise ValueError('INVALID: replay requires full next 60 seconds')
    if backend not in ('native','reference'):raise ValueError('unknown recovery backend')
    admitted=[];simulated=0.;skips={'no_free_member':0,'inadmissible_kick':0,'fast_transient_cohort':0}
    check['recovery_accounting']=dict(candidate_denominator=len(check['candidates']),skips=skips)
    if check['possibly_aliased']:return admitted,simulated
    for candidate in check['candidates']:
        values,report=admissible_kick(saved,candidate,rng);candidate['kick']=report
        if values is None:skips[report['reason']]+=1;candidate['skip']=report['reason'];continue
        control,kicked=saved.clone(events=False,frames=False),saved.clone(events=False,frames=False)
        try:
            control.frozen=kicked.frozen=True;control.backend=kicked.backend=backend
            positions,phases=values
            for i,e in enumerate(kicked.native.elements):kicked.native.set_element(e.id,*positions[i],phases[i],e.rate)
            initial=deviations(control,kicked,candidate['ids']);taus=[None,None];valid=True;displacements=[]
            for step,drives in enumerate(schedule,1):
                ca=control.integrate(drives);kb=kicked.integrate(drives)
                # Future phase criteria read this candidate's members only.
                # Non-members still affect motion and membership comparisons.
                valid &= cohort_frame_valid(ca,candidate['ids']) and cohort_frame_valid(kb,candidate['ids'])
                dev=deviations(control,kicked,candidate['ids'])
                displacements.append(dict(time=step*.1,**anchored_displacement(control,kicked,candidate['ids'])))
                for j in range(2):
                    if taus[j] is None and dev[j]<initial[j]/math.e:taus[j]=step*.1
            simulated+=120.;candidate['displacement']=displacements
            if not valid:skips['fast_transient_cohort']+=1;candidate['skip']='fast_transient_cohort';continue
            def state(branch):
                es={e.id:e for e in branch.native.elements}
                return np.array([[es[id].x,es[id].y] for id in check['cohort']]),np.array([es[id].phase for id in check['cohort']])
            cx,ct=state(control);kx,kt=state(kicked);members,locks=candidate['indices'],check['locked']
            labels=c4.components(cx,1.5,locks)
            cm=max((np.flatnonzero(labels==c) for c in np.unique(labels)),key=lambda m:c4.jaccard(members,m))
            j1=c4.jaccard(members,cm);j2=c4.best_match(kx,members,1.5,locks)[0];j3=c4.best_match(kx,cm,1.5,locks)[0]
            pattern=float(np.abs(wrap(c4.pair_differences(kt,members)-c4.pair_differences(ct,members))).max())
            stats=dict(candidate['stats'],recovery_original_to_control=j1,recovery_original_to_kicked=j2,recovery_control_to_kicked=j3,recovery_jaccard=min(j1,j2,j3),recovery_pattern_error=pattern,tau_phase=taus[0] if taus[0] is not None else 60.,tau_position=taus[1] if taus[1] is not None else 60.,tau_phase_censored=taus[0] is None,tau_position_censored=taus[1] is None,carrier_period=2.,rate_adaptation_time=20.,gain_adaptation_time=20.)
            candidate['stats']=stats;candidate['criteria']=c4.criteria_checks(stats,THRESHOLDS)
            if all(candidate['criteria'].values()):admitted.append(candidate)
        finally:control.close();kicked.close()
    return snapshot_order(admitted),simulated
