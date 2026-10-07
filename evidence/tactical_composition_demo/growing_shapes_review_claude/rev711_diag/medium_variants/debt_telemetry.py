"""DEBT observer additions to the unchanged coverage Amendment-1 observer."""
import math
from coverage_telemetry import Observer as CoverageObserver, encode
from service_graph import service_snapshot
from economy_telemetry import mass_allocation
from debt_kernel import debt_order


def order_comparison(gaps, debt, waiting, pointer):
    finite=lambda s:not math.isfinite(gaps[s])
    rd3=sorted(gaps,key=lambda s:(gaps[s],(s-pointer)%8))
    cova=sorted(gaps,key=lambda s:(finite(s),-waiting[s],(s-pointer)%8))
    pure=sorted(gaps,key=lambda s:(-debt[s],(s-pointer)%8))
    actual=debt_order(gaps,debt,pointer)
    return dict(order=actual,rd3_order=rd3,cova_order=cova,pure_debt_diagnostic_order=pure,
                differs_rd3=actual!=rd3,differs_cova=actual!=cova,
                first_differs_rd3=bool(actual) and actual[0]!=rd3[0],
                first_differs_cova=bool(actual) and actual[0]!=cova[0])


class Observer(CoverageObserver):
    def __init__(self,medium,trace_path,variant):
        super().__init__(medium,trace_path,variant)
        self.waiting=dict.fromkeys(range(8),0.)
        self.debt_samples=[];self.order_checks=[];self.mass_samples=[];self.debt_boundary_steps=0

    def integrate(self):
        super().integrate()
        s=self.previous
        for site in range(8):
            if site in s['served']:self.waiting[site]=0.
            elif site in s['active']:self.waiting[site]+=.1
        row=dict(t=round(self.live.step_index*.1,10),debt=dict(self.live.service_debt),
                 cova_wait=dict(self.waiting),active=sorted(s['active']),served=sorted(s['served']))
        self.debt_boundary_steps+=1
        if self.live.step_index%50==0:self.debt_samples.append(row)
        self.write('integrate_debt',**row)

    def path_check(self):
        m=self.live;g=m.strong_influence();active={d.id for d in m.drives if d.strength>0}
        from evidence.tactical_composition_demo.growing_shapes.medium.rev7_design import deficit
        gaps={s:deficit(m.native,g.forward(s),g.backward()) for s in active if not g.path(s)}
        row=dict(t=round(m.step_index*.1,10),pointer=m.pointer,
                 directed_deficit={s:v if math.isfinite(v) else None for s,v in gaps.items()},
                 debt=dict(m.service_debt),cova_wait=dict(self.waiting),
                 **order_comparison(gaps,m.service_debt,self.waiting,m.pointer))
        self.order_checks.append(row);self.write('debt_order_check',**row)

    def removal_before(self,id,rule,values):
        # The unchanged RD3 classification applies to this observer-only label.
        original=self.variant;self.variant='RD3'
        try:return super().removal_before(id,rule,values)
        finally:self.variant=original

    def step(self):
        super().step()
        if self.live.step_index%50==0:
            row=mass_allocation(service_snapshot(self.live),round(self.live.step_index*.1,10))
            if not math.isclose(row['cost'],self.live.cost(),abs_tol=1e-9):
                raise AssertionError('DEBT class mass does not conserve native cost')
            self.mass_samples.append(row);self.write('mass_allocation',**row)

    def finish(self):
        result=super().finish()
        result.update(label_revision='AMENDMENT_1_DEBT',debt_samples=self.debt_samples,
                      order_checks=self.order_checks,mass_samples=self.mass_samples,
                      debt_boundary_steps=self.debt_boundary_steps)
        return result


def install_observer(P, Run, variant, trace, digest, enabled):
    """Only the live identity is observed; observers/digest are outside clone state."""
    from evidence.tactical_composition_demo.growing_shapes.medium.rev7_design import Rev7Medium
    live_holder=[None]; observer_holder=[None]
    old_integrate=Rev7Medium.integrate; old_remove=Rev7Medium.remove
    old_path=Rev7Medium.b_path; old_growth=Rev7Medium.growth; old_emit=Rev7Medium.emit; old_boundary=Run.step_boundary

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

    def b_path(m,*args,**kwargs):
        obs=observer(m)
        if obs:obs.path_check()
        return old_path(m,*args,**kwargs)

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
                                      service_debt=m.service_debt,
                                      pointer=m.pointer,request_counter=m.request_counter,
                                      growth_rng=m.growth_rng.bit_generator.state if m.growth_rng else None,
                                      elements=[e.as_dict() for e in m.native.elements])).encode())
            obs=observer(m)
            if obs: obs.step()
        return result

    Rev7Medium.integrate=integrate; Rev7Medium.remove=remove
    Rev7Medium.emit=emit; Rev7Medium.b_path=b_path; Rev7Medium.growth=growth; Run.step_boundary=boundary
    return observer_holder
