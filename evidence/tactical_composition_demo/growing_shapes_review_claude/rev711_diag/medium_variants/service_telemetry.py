"""Observer state lives here, never on a Rev7Medium or its clones."""
from collections import Counter
import gzip
import json
import math
from service_graph import service_snapshot, compact, path


def encode(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def break_labels(before, after, site, removal=None):
    labels = set(); detail = []
    if removal and site in before['lost'].get(removal['id'], []): labels.add(removal['rule'])
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


class Observer:
    def __init__(self, medium, trace_path, variant):
        self.live=medium; self.variant=variant
        self.stream=gzip.open(trace_path,'xt')
        self.previous=service_snapshot(medium)
        self.outages=[]; self.open={}; self.removals=[]; self.decisions=[]; self.forced=[]
        self.requests=[]; self.terminals=[]; self.growth_checks=[]
        self.active=Counter(); self.active_served=Counter(); self.served=Counter(); self.degree=Counter()
        self.steps=0; self.fragments=[]; self.clone_checked=False

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
        for site,outage in self.open.items():
            outage['samples'].append(dict(t=t,rootless_screened=not s['fragment']['rooted'] and s['fragment']['screened'],gap=s['gaps'][site]))
        row=compact(s); self.write('world_step',step=m.step_index,t=t,**row)
        if m.step_index%50==0:
            self.write('figure',step=m.step_index,t=t,positions=s['positions'],
                       strong_edges=sorted([a,b] for b,src in s['incoming'].items() for a in src),spring_pairs=sorted(s['pairs']))

    def removal_before(self, id, rule, values):
        s=service_snapshot(self.live)
        self.transition(s,round(self.live.step_index*.1,10))
        row=dict(t=round(self.live.step_index*.1,10),id=id,rule=rule,service_class=s['classes'][id],lock=values.get('lock'))
        self.removals.append(row); self.write('removal',**row)
        if rule=='D3':
            if self.variant=='V1':
                # V1's exact active-root forward/backward path protection.
                g=self.live.strong_influence(); protected=g.forward()&g.backward()
            elif self.variant=='RD3': protected={i for i in s['ids'] if s['classes'][i]!='non-service'}
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
        if rule not in ('birth_request','birth_terminal','forced_service_cut','protected_over_budget'): return
        record=dict(t=t,**values,rule=rule,cost=row['cost'],cap=64)
        if rule=='birth_request': self.requests.append(record)
        if rule=='birth_terminal': self.terminals.append(record)
        if rule=='forced_service_cut': self.forced.append(dict(record,ids=row['ids']))
        self.write('event',**record)
        for site,outage in self.open.items():
            if values.get('site')==site:
                if rule=='birth_request': outage['requests'].append(record)
            # Terminal resource refusals and accepted births concern the medium
            # globally; N alone tests requests specifically naming this site.
            if rule=='birth_terminal': outage['terminals'].append(record)
        if rule=='birth_terminal' and values.get('outcome')=='accepted':
            snapshot=service_snapshot(self.live)
            self.transition(snapshot,t)
            for site,outage in self.open.items():
                outage['samples'].append(dict(t=t,rootless_screened=not snapshot['fragment']['rooted'] and snapshot['fragment']['screened'],gap=snapshot['gaps'][site],weight=0))

    def growth_end(self, offset):
        m=self.live; s=service_snapshot(m); t=round(m.step_index*.1,10)
        self.transition(s,t)
        events=[e for e in m.events[offset:] if e['rule'] in ('birth_request','birth_terminal','growth_check','protected_over_budget','forced_service_cut')]
        check=dict(t=t,cost=m.cost(),cap=64,events=events,service=compact(s))
        self.growth_checks.append(check); self.write('growth_check',**check)

    def finish(self):
        t=round(self.live.step_index*.1,10)
        for outage in self.open.values(): outage.update(end=t,duration=t-outage['start'],censored=True)
        for o in self.outages:
            candidates={}; samples=o.pop('samples'); requests=o.pop('requests'); terminals=o.pop('terminals')
            o.pop('internal_route_events')
            if o['duration']>20:
                timed=[s for s in samples if s.get('weight',1)>0]
                ss=[s for s in timed if s['rootless_screened']]
                if timed and len(ss)>len(timed)/2: candidates['S']=ss[0]['t']
                cost=[e for e in terminals if e['outcome']=='cost' and e['birth_rule'] in ('B-path','B1')]
                if cost: candidates['C']=cost[0]['t']
                if not requests: candidates['N']=o['start']
                born=[e for e in terminals if e['outcome']=='accepted']
                gaps=[s['gap'] for s in samples if s['gap'] is not None]
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
                    break_causes={k:sum(o['break_cause']==k for o in self.outages) for k in ('D3','D1','D4','G-dist','G-deg','R','X')},
                    non_repair_causes={k:sum(k in o['non_repair_labels'] for o in self.outages) for k in ('S','C','N','B','G','X')},
                    d3_removals_by_class=dict(Counter(r['service_class'] for r in self.removals if r['rule']=='D3')),
                    forced_service_cuts=self.forced,protected_population=self.decisions,
                    protected_over_budget=sum(e['rule']=='protected_over_budget' for c in self.growth_checks for e in c['events']),
                    realized_degree_distribution=dict(self.degree),
                    realized_degree_above_2=sum(v for k,v in self.degree.items() if k>2)/sum(self.degree.values()) if self.degree else 0.,
                    outages=self.outages,removals=self.removals,
                    interpretation='Route reuse compares deterministic shortest-path element sets, not all equivalent possible routes. Mostly-served is reported as fractions; no new cutoff. G is unidentifiable within a maximal site outage; R cannot alone destroy strong reachability.')


def install_observer(P, Run, variant, trace, digest, enabled):
    """Only the live identity is observed; observers/digest are outside clone state."""
    from evidence.tactical_composition_demo.growing_shapes.medium.rev7_design import Rev7Medium
    live_holder=[None]; observer_holder=[None]
    old_integrate=Rev7Medium.integrate; old_remove=Rev7Medium.remove
    old_growth=Rev7Medium.growth; old_emit=Rev7Medium.emit; old_boundary=Run.step_boundary

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
                                      pointer=m.pointer,request_counter=m.request_counter,
                                      growth_rng=m.growth_rng.bit_generator.state if m.growth_rng else None,
                                      elements=[e.as_dict() for e in m.native.elements])).encode())
            obs=observer(m)
            if obs: obs.step()
        return result

    Rev7Medium.integrate=integrate; Rev7Medium.remove=remove
    Rev7Medium.emit=emit; Rev7Medium.growth=growth; Run.step_boundary=boundary
    return observer_holder
