"""Label-free candidates; owner-side recovery, causal attribution and bath assays."""
import hashlib
import numpy as np
from geomind import c4_detect as D, c4_experiment as E
from geomind.c4_model import wrap
from geomind import c6_r3_background as B


def find_candidates(xs, ths, thresholds):
    """No condition, apparatus tag, expected grouping, or future outcome argument."""
    locked = D.locked_pairs(ths, thresholds['lock_std'])
    labels = D.components(xs[-1], thresholds['link_factor'], locked)
    rows = []
    for label in np.unique(labels):
        members = np.flatnonzero(labels == label)
        if len(members) >= thresholds['min_size']:
            stats = D.window_statistics(xs, ths, members, thresholds['frame_dt'],
                                        thresholds['link_factor'], locked)
            stats['collective_frequency']=float(np.mean(ths[-1,members]-ths[0,members])/((len(ths)-1)*thresholds['frame_dt']))
            rows.append({'members': members.tolist(), 'stats': stats})
    return rows, locked


def member_digest(members):
    return hashlib.sha256(np.asarray(sorted(members), '<i8').tobytes()).hexdigest()


def select_source(rows):
    accepted = [r for r in rows if r.get('accepted') and r.get('attribution') == 'source']
    return min(accepted, key=lambda r: (-len(r['members']), member_digest(r['members']))) if accepted else None


def source_qualifies(effects, settings):
    if effects is None:
        return False
    q = settings['qualification']
    for direction in ('g_to_m', 'm_to_g'):
        intact, ablated = effects[direction]['intact'], effects[direction]['ablated']
        if not np.isfinite([intact, ablated]).all() or intact <= q['causal_floor']:
            return False
        if abs(ablated) > max(q['vanish_absolute_tolerance'], q['vanish_fraction']*intact):
            return False
    return True


class Apparatus:
    """Owner, not prediction API. Reference/prior start at this turn's t=0."""
    def __init__(self, bath, source, reference, prior, settings):
        self.bath = tuple(np.array(a, copy=True) for a in bath)
        self.source = tuple(np.array(a, copy=True) for a in source)
        self.reference, self.prior, self.settings = reference, prior, settings
        self.nb, self.ns = len(bath[0]), len(source[0])
        self.dt = settings['integration']['dt']

    def run(self, duration, condition='intact', start=0., state=None, sample_dt=None, phase_origin=None):
        x, th = (np.vstack([self.bath[0], self.source[0]]), np.r_[self.bath[1], self.source[1]]) if state is None else state
        ref = self.reference.slice(start, duration)
        prior = None if self.prior is None else self.prior.slice(start, duration)
        return B.run(x[:self.nb], th[:self.nb], self.bath[2], duration,
                     source=(x[self.nb:self.nb+self.ns], th[self.nb:self.nb+self.ns], self.source[2]),
                     reference=ref, prior=prior,
                     mode='intact' if condition=='no_backreaction' else condition,
                     outbound=0. if condition=='no_backreaction' else 1., dt=self.dt,
                     sample_dt=sample_dt or self.dt, phase_origin=phase_origin)

    def observable(self, frames, start=0., sample_dt=None):
        x, th = frames
        if self.prior is None:
            return x, th
        times = start+np.arange(len(x))*(sample_dt or self.dt)
        px, pt = self.prior.sample(times)
        return np.concatenate([x, px], axis=1), np.concatenate([th, pt], axis=1)

    def formation(self, flow, condition, rng):
        i, t = self.settings['integration'], self.settings['detector']
        end = B.exact_steps(i['formation'], self.dt)
        first = end-B.exact_steps(i['window'], self.dt)
        stride = B.exact_steps(t['frame_dt'], self.dt)
        sampled = (flow[0][first:end+1:stride], flow[1][first:end+1:stride])
        observable = self.observable(sampled, start=i['formation']-i['window'], sample_dt=t['frame_dt'])
        rows, locked = find_candidates(*observable, t)
        state = flow[0][end], flow[1][end]
        control = None
        for row in rows:
            members = np.array(row['members']); stats = row['stats']
            row['digest'] = member_digest(members)
            row['attribution'] = ('source' if np.all((members>=self.nb)&(members<self.nb+self.ns))
                                  else 'bath' if np.all(members<self.nb) else 'mixed_or_prior')
            if row['attribution'] != 'source':
                row.update(accepted=False, recovery_status='NOT_RUN',
                           reason='not wholly attributable to the current source cohort; diagnostic only')
                continue
            if control is None:
                control = self.observable(self.run(t['recovery_time'], condition, start=i['formation'],
                                                  state=state), start=i['formation'])
            spacing = float(np.median(D.nn_spacing(state[0][members])))
            kx, kt = D.kick(*state, members, rng, t['kick_position']*spacing, t['kick_phase'])
            kicked = self.observable(self.run(t['recovery_time'], condition, start=i['formation'], state=(kx, kt)),
                                     start=i['formation'])
            cx, ct, kxx, ktt = control[0][-1], control[1][-1], kicked[0][-1], kicked[1][-1]
            original_to_control, clabels = D.best_match(cx, members, t['link_factor'], locked)
            matched = max((np.flatnonzero(clabels==c) for c in np.unique(clabels)),
                          key=lambda m: D.jaccard(members,m))
            original_to_kicked = D.best_match(kxx, members, t['link_factor'], locked)[0]
            control_to_kicked = D.best_match(kxx, matched, t['link_factor'], locked)[0]
            stats.update(recovery_original_to_control=float(original_to_control),
                         recovery_original_to_kicked=float(original_to_kicked),
                         recovery_control_to_kicked=float(control_to_kicked),
                         recovery_jaccard=float(min(original_to_control,original_to_kicked,control_to_kicked)),
                         recovery_pattern_error=float(np.max(np.abs(wrap(D.pair_differences(ktt,members)-D.pair_differences(ct,members))))))
            row['failed'] = [k for k, v in D.criteria_checks(stats,t).items() if not v]
            row.update(accepted=not row['failed'], recovery_status='EVALUATED')
        selected = select_source(rows)
        effects = None if selected is None else self.causal(state, np.array(selected['members']), i['formation'], rng, condition)
        return {'candidates':rows,'selected_digest':None if selected is None else selected['digest'],
                'selected_members':None if selected is None else selected['members'],
                'causal':effects,'qualified':source_qualifies(effects,self.settings)}

    def causal(self, state, members, start, rng, condition):
        """Both incoming and internal paths removed in complete causal ablations."""
        x, th = state; iv=self.settings['interventions']; floor=self.settings['detector']['frame_dt']
        delta=E.probe_kick(rng,len(members),iv['gm_probe_phase_rms'])
        gc, gt=E.gm_states(x,th,members,delta,iv['gm_scale'])
        phase=E.mg_phases(rng,th,members,iv['mg_dose'])
        mc, mt=E.mg_states(x,th,members,phase)
        effects={}
        for direction, control, treated, duration, ablation in (
            ('g_to_m',gc,gt,iv['gm_window'],'no_geometry_to_mode'),
            ('m_to_g',mc,mt,iv['mg_window'],'no_mode_to_geometry')):
            values={}
            for label, mode in (('intact',condition),('ablated',ablation)):
                a=self.run(duration,mode,start=start,state=control,sample_dt=iv['sample_dt'],phase_origin=x)
                b=self.run(duration,mode,start=start,state=treated,sample_dt=iv['sample_dt'],phase_origin=x)
                if direction=='g_to_m':
                    pattern=D.pair_differences(th,members)
                    value=E.gm_statistic(b[1],members,pattern)-E.gm_statistic(a[1],members,pattern)
                else:
                    rg=D.radius_of_gyration(x[members])
                    value=E.mg_statistic(b[0],members,rg)-E.mg_statistic(a[0],members,rg)
                values[label]=float(value)
            effects[direction]=values
        return effects

    def descriptor(self, flow, time, L):
        """Fixed initial-ID-ranked ports, never selected from observed formations."""
        i=self.settings['integration']; end=B.exact_steps(time,self.dt)
        state=(flow[0][end].copy(),flow[1][end].copy())
        control=self.run(i['descriptor'],start=time,state=state,sample_dt=i['probe_sample_dt'])
        return self.descriptor_with_control(state, time, L, control)

    def descriptor_with_control(self,state,time,L,control,condition='intact'):
        i=self.settings['integration']; ports=(0,12)
        if self.nb <= 12 or not np.isfinite(L) or L<=0:
            raise ValueError('invalid fixed background probe geometry')
        axis=self.bath[0][12]-self.bath[0][0]; norm=np.linalg.norm(axis)
        if norm<=0:
            raise ValueError('zero fixed probe axis')
        phase,position,raw=[],[],[]
        for port in ports:
            receivers=np.array([j for j in range(self.nb) if j != port])
            x,th=state[0].copy(),state[1].copy();th[port]+=.5
            response=self.run(i['descriptor'],condition,start=time,state=(x,th),sample_dt=i['probe_sample_dt'])
            pr=wrap(response[1][:,receivers]-control[1][:,receivers])
            phase.append(float(np.sqrt(np.mean(pr**2))))
            x,th=state[0].copy(),state[1].copy();x[port]+=.2*L*axis/norm
            response=self.run(i['descriptor'],condition,start=time,state=(x,th),sample_dt=i['probe_sample_dt'])
            dr=(response[0][:,receivers]-control[0][:,receivers])/L
            position.append(float(np.sqrt(np.mean(np.sum(dr**2,axis=-1)))))
            raw.append({'port':port,'phase_response':pr.tolist(),'position_response':dr.tolist()})
        return {'b_phase':float(np.mean(phase)),'b_position':float(np.mean(position)),
                'normalization_L_before':float(L),'ports':list(ports),'raw':raw}

    def measure(self,flow,time,L,condition):
        state=(flow[0][B.exact_steps(time,self.dt)].copy(),flow[1][B.exact_steps(time,self.dt)].copy())
        control=self.run(self.settings['integration']['descriptor'],condition,start=time,state=state,
                         sample_dt=self.settings['integration']['probe_sample_dt'])
        return self.descriptor_with_control(state,time,L,control,condition)
