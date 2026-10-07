"""Capacity-only reporting additions; existing coverage observer stays unchanged."""
import math
from coverage_telemetry import Observer as CoverageObserver, encode
from service_graph import service_snapshot, compact
from economy_telemetry import mass_allocation
from capacity_kernel import CEILINGS


def capacity_sample(snapshot, t, cost, ceiling):
    row=mass_allocation(snapshot,t)
    if not math.isclose(row['cost'],cost,rel_tol=0.,abs_tol=1e-9):
        raise AssertionError('capacity class mass does not conserve native cost')
    structural=len(snapshot['served']); active=len(snapshot['active_served'])
    row.update(structurally_served_sites=structural,active_served_sites=active,
               cost_ceiling=ceiling,count_ceiling=ceiling,cost_headroom=ceiling-cost,
               count_headroom=ceiling-row['ordinary'],
               cost_per_structurally_served_site=cost/structural if structural else None,
               cost_per_active_served_site=cost/active if active else None,
               zero_structural_service=structural==0,zero_active_service=active==0)
    return row


class Observer(CoverageObserver):
    def __init__(self, medium, trace_path, variant):
        super().__init__(medium,trace_path,variant)
        self.ceiling=CEILINGS[variant];self.capacity_samples=[]

    def write(self,kind,**row):
        # Reporting-only additions to the unchanged transition/event logic.
        if 'cap' in row:row['cap']=self.ceiling
        if kind in ('event','growth_check','world_step','capacity_sample'):
            row.update(cost_ceiling=self.ceiling,count_ceiling=self.ceiling)
        super().write(kind,**row)

    def event(self, row):
        rule=row['rule']; values=row['values']; t=round(self.live.step_index*.1,10)
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
        record=dict(t=t,**values,rule=rule,cost=row['cost'],cap=self.ceiling,cost_ceiling=self.ceiling,count_ceiling=self.ceiling)
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
        check=dict(t=t,cost=m.cost(),cap=self.ceiling,cost_ceiling=self.ceiling,count_ceiling=self.ceiling,events=events,service=compact(s))
        self.growth_checks.append(check); self.write('growth_check',**check)

    def removal_before(self,id,rule,values):
        original=self.variant;self.variant='RD3'
        try:return super().removal_before(id,rule,values)
        finally:self.variant=original

    def step(self):
        super().step()
        row=capacity_sample(self.previous,round(self.live.step_index*.1,10),self.live.cost(),self.ceiling)
        self.write('capacity_sample',step=self.live.step_index,**row)
        if self.live.step_index%50==0:self.capacity_samples.append(row)

    def finish(self):
        result=super().finish()
        result.update(label_revision='AMENDMENT_1_CAPACITY',cost_ceiling=self.ceiling,
                      count_ceiling=self.ceiling,capacity_samples=self.capacity_samples,
                      time_series_boundary='settled post-growth .1s; compact samples 5s; full samples in raw')
        return result


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
                                      coverage_wait=getattr(m,'coverage_wait',None),coverage_locks=getattr(m,'coverage_locks',None),coverage_recycled=getattr(m,'coverage_recycled',None),
                                      pointer=m.pointer,request_counter=m.request_counter,
                                      growth_rng=m.growth_rng.bit_generator.state if m.growth_rng else None,
                                      elements=[e.as_dict() for e in m.native.elements])).encode())
            obs=observer(m)
            if obs: obs.step()
        return result

    Rev7Medium.integrate=integrate; Rev7Medium.remove=remove
    Rev7Medium.emit=emit; Rev7Medium.growth=growth; Run.step_boundary=boundary
    return observer_holder
