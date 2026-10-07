"""Economy observer based on coverage Amendment 1; all historical observers unchanged."""
from collections import Counter
import gzip
import json
import math
from service_graph import service_snapshot, compact, path, reach


def encode(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def break_labels(before, after, site, removal=None):
    labels = set(); detail = []
    if removal and site in before['lost'].get(removal['id'], []): labels.add(removal['rule'])
    # A D5 removal can lose service through nearest-neighbor/degree rewiring,
    # even when its body is dispensable in the old fixed graph. Attribution is
    # an observed transition context, not a causal identification.
    if removal and removal['rule'] in ('D5f','D5r') and site in before['served'] and site not in after['served']:
        labels.add(removal['rule'])
    # Consider every edge on a service walk, not only one arbitrary shortest path.
    forward = set(before['roots'][site]); todo = list(forward)
    while todo:
        for v in before['outgoing'].get(todo.pop(), ()):
            if v not in forward: forward.add(v); todo.append(v)
    back = set(before['outputs']); todo = list(back)
    while todo:
        for v in before['incoming'].get(todo.pop(), ()):
            if v not in back: back.add(v); todo.append(v)
    for receiver,sources in before['incoming'].items():
        for source in sources:
            if source not in forward or receiver not in back or source in after['incoming'].get(receiver, ()): continue
            if source not in after['positions'] or receiver not in after['positions']: continue
            a,b = before['positions'][source],before['positions'][receiver]
            c,d = after['positions'][source],after['positions'][receiver]
            r0,r1 = math.hypot(a[0]-b[0],a[1]-b[1]),math.hypot(c[0]-d[0],c[1]-d[1])
            n0,n1 = max(1,len(before['held'][receiver])),max(1,len(after['held'][receiver]))
            rate = after['scale']*math.exp(-r1*r1)/n1
            # Exact one-factor counterfactual at the pre-transition configuration.
            dist = after['scale']*math.exp(-r1*r1)/n0
            deg = after['scale']*math.exp(-r0*r0)/n1
            if rate < .5 and r1 > r0 and dist < .5: labels.add('G-dist')
            if rate < .5 and n1 > n0 and deg < .5: labels.add('G-deg')
            detail.append(dict(edge=[source,receiver],length_before=r0,length_after=r1,held_before=n0,held_after=n1,rate_after=rate))
    # A spring change alone cannot destroy graph reachability. R is left available
    # in tables, but cannot be causally asserted for served->unserved with intact
    # strong edges and unchanged roots. Changed roots/held topology -> X.
    return (next(iter(labels)) if len(labels)==1 else 'X'), sorted(labels), detail


CLASSES=('critical','redundant','front','orphan')


def mass_partition(snapshot):
    forward=reach(set().union(*snapshot['roots'].values()),snapshot['outgoing'])
    return {i: snapshot['classes'][i] if snapshot['classes'][i]!='non-service' else
            'front' if i in forward else 'orphan' for i in snapshot['ids'] if i not in snapshot['outputs']}


def mass_allocation(snapshot,time):
    classes=mass_partition(snapshot)
    pairs={tuple(sorted((a,b))) for b,src in snapshot['held'].items() for a in src
           if a in classes and b in classes}
    counts=Counter(classes.values());share=Counter();matrix=Counter()
    for a,b in pairs:
        share[classes[a]]+=.05;share[classes[b]]+=.05
        matrix['/'.join(sorted((classes[a],classes[b])))]+=1
    by={c:dict(elements=counts[c],pair_cost=share[c],cost=counts[c]+share[c]) for c in CLASSES}
    total=len(classes)+.1*len(pairs)
    if not math.isclose(sum(x['cost'] for x in by.values()),total,abs_tol=1e-9):
        raise AssertionError('class cost does not conserve')
    return dict(t=time,classes=by,cost=total,ordinary=len(classes),held_pairs=len(pairs),
                pair_class_matrix=dict(matrix),served=sorted(snapshot['served']))


def candidate_cost(m,point):
    from evidence.tactical_composition_demo.growing_shapes.medium.rev7_design import geometry, geometric_graph
    from evidence.tactical_composition_demo.growing_shapes.medium.rev7_native import budget_counts
    elements,drives=geometry(m.native,m.drives)
    new=max((e[0] for e in elements),default=-1)+1
    elements=elements+[(new,*point,'element',1.,False)]
    graph=geometric_graph(elements,drives,m.native.params.k,m.native.params.radius)
    n,pairs=budget_counts({e[0]:e[3] for e in elements},graph.incoming)
    return n+.1*pairs


class Observer:
    def __init__(self, medium, trace_path, variant):
        self.live=medium; self.variant=variant
        self.stream=gzip.open(trace_path,'xt')
        self.previous=service_snapshot(medium)
        self.outages=[]; self.open={}; self.removals=[]; self.decisions=[]; self.forced=[]
        self.requests=[]; self.terminals=[]; self.growth_checks=[]
        self.active=Counter(); self.active_served=Counter(); self.served=Counter(); self.degree=Counter()
        self.steps=0; self.fragments=[]; self.clone_checked=False; self.recycles=[]; self.initial_cost_refusals=[]
        self.mass_samples={}; self.prospective_checks=[]; self.prospective_trials=[]; self.stall_samples=[]; self.no_front=[]
        self.record_mass(self.previous,0.)

    def record_mass(self,snapshot,time):
        row=mass_allocation(snapshot,time)
        if not math.isclose(row['cost'],self.live.cost(),abs_tol=1e-9):
            raise AssertionError('allocation disagrees with native cost')
        self.mass_samples[time]=row;self.write('mass_allocation',**row)

    def write(self, kind, **row):
        self.stream.write(encode(dict(kind=kind,**row))+'\n')

    def transition(self, snapshot, time, removal=None):
        before=self.previous
        for site in sorted(before['served']-snapshot['served']):
            label, candidates, detail = break_labels(before,snapshot,site,removal)
            outage=dict(site=site,start=time,end=None,duration=None,censored=False,
                        break_cause=label,break_candidates=candidates,break_detail=detail,
                        previous_route=before['routes'][site],restored_route=None,route_reuse=None,initial_gap=snapshot['gaps'][site],
                        samples=[dict(t=time,rootless_screened=not snapshot['fragment']['rooted'] and snapshot['fragment']['screened'],gap=snapshot['gaps'][site],weight=0)],requests=[],terminals=[],internal_route_events=[])
            self.open[site]=outage; self.outages.append(outage)
        for site in sorted(snapshot['served']-before['served']):
            outage=self.open.pop(site,None)
            if outage:
                outage.update(end=time,duration=time-outage['start'],restored_route=snapshot['routes'][site],
                              route_reuse='same_element_set' if set(snapshot['routes'][site])==set(outage['previous_route']) else 'new_route')
        self.previous=snapshot

    def integrate(self):
        s=service_snapshot(self.live); self.transition(s,round(self.live.step_index*.1,10))

    def step(self):
        m=self.live; s=service_snapshot(m); t=round(m.step_index*.1,10)
        self.transition(s,t)
        self.steps+=1; self.active.update(s['active']); self.active_served.update(s['active_served']); self.served.update(s['served'])
        self.degree.update(s['degree'].values())
        for recycle in self.recycles:
            if recycle['retry_outcome']=='accepted' and recycle['first_served_t'] is None and t<=recycle['t']+60 and recycle['site'] in s['served']:
                recycle['first_served_t']=t
        for site,outage in self.open.items():
            outage['samples'].append(dict(t=t,rootless_screened=not s['fragment']['rooted'] and s['fragment']['screened'],gap=s['gaps'][site]))
        row=compact(s); self.write('world_step',step=m.step_index,t=t,**row)
        if m.step_index%50==0:
            self.record_mass(s,t)
            self.write('figure',step=m.step_index,t=t,positions=s['positions'],
                       strong_edges=sorted([a,b] for b,src in s['incoming'].items() for a in src),spring_pairs=sorted(s['pairs']))

    def removal_before(self, id, rule, values):
        s=service_snapshot(self.live)
        self.transition(s,round(self.live.step_index*.1,10))
        row=dict(t=round(self.live.step_index*.1,10),id=id,rule=rule,service_class=s['classes'][id],lock=values.get('lock'),
                 economy_class=mass_partition(s).get(id),site=values.get('site'),tip=values.get('tip'),age_steps=self.live.step_index-self.live.birth_steps[id])
        self.removals.append(row); self.write('removal',**row)
        if rule=='D3':
            if self.variant=='V1':
                # V1's exact active-root forward/backward path protection.
                g=self.live.strong_influence(); protected=g.forward()&g.backward()
            elif self.variant in ('RD3','COVA','COVB','ECOF','ECOR'): protected={i for i in s['ids'] if s['classes'][i]!='non-service'}
            else: protected=set()
            if self.variant=='V1' and not (set(s['eligible'])-protected):
                cut=sorted(set(s['lost'][id])&s['active'])
                if cut:
                    event=dict(t=row['t'],ids=[id],sites=cut,source='observer_V1_fallback')
                    self.forced.append(event);self.write('forced_service_cut',**event)
            ordinary=set(s['ids'])-s['outputs']
            self.decisions.append(dict(t=row['t'],protected_fraction=len(protected&set(s['ids']))/len(s['ids']) if s['ids'] else 0.,
                                       protected_population_count=len(protected&set(s['ids'])),population_count=len(s['ids']),
                                       ordinary_protected_fraction=len(protected&ordinary)/len(ordinary) if ordinary else 0.,
                                       protected_count=len(protected&ordinary),ordinary_count=len(ordinary),
                                       eligible_count=len(s['eligible']),protected_eligible_count=len(protected&set(s['eligible']))))
        return row

    def event(self, row):
        rule=row['rule']; values=row['values']; t=round(self.live.step_index*.1,10)
        if rule in ('economy_prospective_check','economy_prospective_trial','economy_stall','D5f_none'):
            record=dict(t=t,**values,ids=row['ids'],rule=rule)
            target={'economy_prospective_check':self.prospective_checks,
                    'economy_prospective_trial':self.prospective_trials,
                    'economy_stall':self.stall_samples,'D5f_none':self.no_front}[rule]
            target.append(record);self.write('economy_event',**record);return
        if rule=='coverage_cost_refusal':
            record=dict(t=t,**values,rule=rule,outcome='cost')
            self.write('initial_cost_refusal',**record)
            self.initial_cost_refusals.append(record)
            return
        if rule=='coverage_recycle':
            record=dict(t=t,**values,rule=rule,donor_id=row['ids'][0],first_served_t=None)
            self.recycles.append(record); self.write('recycle',**record)
            return
        if rule not in ('birth_request','birth_terminal','forced_service_cut','protected_over_budget'): return
        record=dict(t=t,**values,rule=rule,cost=row['cost'],cap=64)
        if rule=='birth_request': self.requests.append(record)
        if rule=='birth_terminal': self.terminals.append(record)
        if rule=='forced_service_cut': self.forced.append(dict(record,ids=row['ids']))
        self.write('event',**record)
        old_open=dict(self.open)
        accepted=rule=='birth_terminal' and values.get('outcome')=='accepted'
        snapshot=service_snapshot(self.live) if accepted else None
        for site,outage in old_open.items():
            if values.get('site')==site and rule=='birth_request': outage['requests'].append(record)
            if rule=='birth_terminal':
                restoring=accepted and site in snapshot['served']
                outage['terminals'].append(dict(record,restoring=bool(restoring)))
                if accepted:
                    sample=dict(t=t,rootless_screened=not snapshot['fragment']['rooted'] and snapshot['fragment']['screened'],gap=snapshot['gaps'][site],weight=0,restoring=bool(restoring))
                    outage['samples'].append(sample)
                    self.write('post_birth_gap',site=site,outage_start=outage['start'],request=values['request'],**sample)
        if accepted:
            for recycle in self.recycles:
                if recycle['retry_outcome']=='accepted' and recycle['first_served_t'] is None and t<=recycle['t']+60 and recycle['site'] in snapshot['served']:
                    recycle['first_served_t']=t
            self.transition(snapshot,t)

    def growth_end(self, offset):
        m=self.live; s=service_snapshot(m); t=round(m.step_index*.1,10)
        self.transition(s,t)
        events=[e for e in m.events[offset:] if e['rule'] in ('birth_request','birth_terminal','growth_check','protected_over_budget','forced_service_cut')]
        check=dict(t=t,cost=m.cost(),cap=64,events=events,service=compact(s))
        self.growth_checks.append(check); self.write('growth_check',**check)
        self.record_mass(s,t)

    def finish(self):
        t=round(self.live.step_index*.1,10)
        for outage in self.open.values(): outage.update(end=t,duration=t-outage['start'],censored=True)
        for o in self.outages:
            candidates={}; samples=o.pop('samples'); requests=o.pop('requests'); terminals=o.pop('terminals')
            o.pop('internal_route_events')
            o['restoration_evidence']=[s for s in samples if s.get('restoring')]
            if o['duration']>20:
                timed=[s for s in samples if s.get('weight',1)>0]
                ss=[s for s in timed if s['rootless_screened']]
                if timed and len(ss)>len(timed)/2: candidates['S']=ss[0]['t']
                cost=[e for e in terminals if e['outcome']=='cost' and e['birth_rule'] in ('B-path','B1')]
                if cost: candidates['C']=cost[0]['t']
                if not requests: candidates['N']=o['start']
                born=[e for e in terminals if e['outcome']=='accepted' and not e.get('restoring')]
                gaps=[s['gap'] for s in samples if s['gap'] is not None and not s.get('restoring')]
                initial=o.get('initial_gap')
                shrank=bool(gaps) if initial is None else bool(gaps) and min(gaps)<initial
                if born and not shrank: candidates['B']=born[0]['t']
                # G has no support within a maximal served->unserved interval:
                # restoration terminates that outage; adjacent outages are separate.
                if not candidates: candidates['X']=o['start']
            o['non_repair_labels']=sorted(candidates)
            o['non_repair_first_times']=candidates
            first=min(candidates.values(),default=None)
            winners=sorted(k for k,v in candidates.items() if v==first)
            o['primary_non_repair']=winners[0] if len(winners)==1 else 'X' if winners else None
            o['primary_tie_labels']=winners if len(winners)>1 else []
            self.write('outage',**o)
        self.stream.close()
        # Snapshot count fractions are durations because every sample is DT=.1 s.
        sites={s:dict(active_steps=self.active[s],active_served_steps=self.active_served[s],
                      served_fraction_active=self.active_served[s]/self.active[s] if self.active[s] else None,
                      served_fraction_all=self.served[s]/self.steps if self.steps else None,
                      ever_served=self.served[s]>0) for s in range(8)}
        complete=[o['duration'] for o in self.outages if not o['censored']]
        return dict(kind='EXPLORATORY_NO_VERDICT',steps=self.steps,sites=sites,
                    outage_count=len(self.outages),maximum_outage=max((o['duration'] for o in self.outages),default=0.),
                    repair_latencies=complete,latency_censored=[o['duration'] for o in self.outages if o['censored']],
                    break_causes={k:sum(o['break_cause']==k for o in self.outages) for k in ('D3','D1','D4','D5f','D5r','G-dist','G-deg','R','X')},
                    non_repair_causes={k:sum(k in o['non_repair_labels'] for o in self.outages) for k in ('S','C','N','B','G','X')},
                    d3_removals_by_class=dict(Counter(r['service_class'] for r in self.removals if r['rule']=='D3')),
                    forced_service_cuts=self.forced,protected_population=self.decisions,
                    protected_over_budget=sum(e['rule']=='protected_over_budget' for c in self.growth_checks for e in c['events']),
                    realized_degree_distribution=dict(self.degree),
                    realized_degree_above_2=sum(v for k,v in self.degree.items() if k>2)/sum(self.degree.values()) if self.degree else 0.,
                    outages=self.outages,removals=self.removals,
                    label_revision='AMENDMENT_1_ECONOMY',
                    mass_samples=[self.mass_samples[t] for t in sorted(self.mass_samples)],
                    prospective_checks=self.prospective_checks,prospective_trials=self.prospective_trials,
                    stall_samples=self.stall_samples,no_front=self.no_front,
                    economy_removals=[r for r in self.removals if r['rule'] in ('D5f','D5r')],
                    requests=self.requests, terminals=self.terminals,
                    initial_cost_refusals=self.initial_cost_refusals,
                    recycles=[dict(r,served_within_60s=('YES' if r['first_served_t'] is not None else 'CENSORED' if t<r['t']+60 else 'NO') if r['retry_outcome']=='accepted' else 'NOT_APPLICABLE') for r in self.recycles],
                    interpretation='Route reuse compares deterministic shortest-path element sets, not all equivalent possible routes. Mostly-served is reported as fractions; no new cutoff. G is unidentifiable within a maximal site outage; R cannot alone destroy strong reachability.')


def install_observer(P, Run, variant, trace, digest, enabled):
    """Only the live identity is observed; observers/digest are outside clone state."""
    from evidence.tactical_composition_demo.growing_shapes.medium.rev7_design import Rev7Medium
    live_holder=[None]; observer_holder=[None]
    old_integrate=Rev7Medium.integrate; old_remove=Rev7Medium.remove
    old_growth=Rev7Medium.growth; old_emit=Rev7Medium.emit; old_boundary=Run.step_boundary
    old_feasible=Rev7Medium.feasible

    def observer(m):
        if m is not P.LIVE[0]: return None
        live_holder[0]=m
        if enabled and observer_holder[0] is None: observer_holder[0]=Observer(m,trace,variant)
        return observer_holder[0]

    def integrate(m, drives):
        obs=observer(m)
        result=old_integrate(m,drives)
        if obs: obs.integrate()
        return result

    def remove(m,id,rule,**values):
        obs=observer(m); row=obs.removal_before(id,rule,values) if obs else None
        result=old_remove(m,id,rule,**values)
        if obs: obs.transition(service_snapshot(m),round(m.step_index*.1,10),row)
        return result

    def emit(m, rule, ids=(), **values):
        result=old_emit(m,rule,ids,**values)
        obs=observer(m)
        if obs: obs.event(m.events[-1])
        return result

    def feasible(m,position,phase):
        result=old_feasible(m,position,phase)
        obs=observer(m)
        if obs and result=='cost':
            record=dict(t=round(m.step_index*.1,10),cost=m.cost(),candidate_cost=candidate_cost(m,position),
                        point=list(position),outcome='cost',source='candidate_feasibility')
            obs.initial_cost_refusals.append(record);obs.write('initial_cost_refusal',**record)
        return result

    def growth(m,**kwargs):
        offset=len(m.events); result=old_growth(m,**kwargs); obs=observer(m)
        if obs: obs.growth_end(offset)
        return result

    def boundary(run,*args,**kwargs):
        result=old_boundary(run,*args,**kwargs)
        if run.medium is P.LIVE[0]:
            m=run.medium
            # Includes exact ids, positions and phases (unrounded), plus native
            # snapshot including histories/RNG and Python timer/RNG state.
            digest.update(m.native.save())
            digest.update(encode(dict(step=m.step_index,birth=m.birth_steps,death=m.death,novelty=m.novelty,
                                      economy_stall=getattr(m,'economy_stall',None),
                                      economy_deficit={s:d if math.isfinite(d) else None for s,d in getattr(m,'economy_deficit',{}).items()},
                                      pointer=m.pointer,request_counter=m.request_counter,
                                      growth_rng=m.growth_rng.bit_generator.state if m.growth_rng else None,
                                      elements=[e.as_dict() for e in m.native.elements])).encode())
            obs=observer(m)
            if obs: obs.step()
        return result

    Rev7Medium.integrate=integrate; Rev7Medium.remove=remove
    Rev7Medium.emit=emit; Rev7Medium.growth=growth; Rev7Medium.feasible=feasible; Run.step_boundary=boundary
    return observer_holder
