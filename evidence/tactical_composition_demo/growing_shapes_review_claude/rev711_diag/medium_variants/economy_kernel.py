"""Task-blind Amendment-1 scratch economy laws; never read observer/evaluator state."""
import math
import time
from service_graph import service_snapshot, reach


def deficit(snapshot, site):
    if not snapshot['roots'][site] or not snapshot['outputs']:
        return math.inf
    front = reach(snapshot['roots'][site], snapshot['outgoing'])
    back = reach(snapshot['outputs'], snapshot['incoming'])
    p = snapshot['positions']
    return min((math.dist(p[a], p[b]) for a in front for b in back), default=math.inf)


def update_stall(m):
    s = service_snapshot(m)
    for site in range(8):
        now = deficit(s, site)
        previous = m.economy_deficit[site]
        # 'roots newly gained' requires finite NOW; repeated infinity pauses.
        if site in s['served'] or (math.isfinite(now) and
                (not math.isfinite(previous) or now < previous - 1e-9)):
            m.economy_stall[site] = 0.
        elif math.isfinite(now):
            m.economy_stall[site] += 20.
        m.economy_deficit[site] = now
        m.emit('economy_stall', site=site, stall_seconds=m.economy_stall[site],
               deficit=now if math.isfinite(now) else None,
               infinite_deficit=not math.isfinite(now),
               previous_deficit=previous if math.isfinite(previous) else None,
               served=site in s['served'])


def front_ids(s, site):
    forward = reach(s['roots'][site], s['outgoing'])
    all_forward = reach(set().union(*s['roots'].values()), s['outgoing'])
    on_route = all_forward & reach(s['outputs'], s['incoming'])
    return forward - on_route


def retract_fronts(m, measured):
    for site in range(8):
        if m.economy_stall[site] < 60.:
            continue
        s = service_snapshot(m)  # Fresh before every prospective removal.
        if not s['outputs']:
            m.emit('D5f_none', site=site, reason='no_output')
            # No-O clause follows the infinite-deficit pause; no donor stage.
            continue
        front = front_ids(s, site)
        tips = sorted(front, key=lambda i: (min(math.dist(s['positions'][i], s['positions'][o])
                                             for o in s['outputs']), i))
        tip = tips[0] if tips else None
        roots = set().union(*s['roots'].values())
        eligible = [i for i in front if i not in roots and i != tip
                    and i not in s['outputs'] and m.step_index-m.birth_steps[i] >= 200]
        if eligible:
            donor = min(eligible, key=lambda i: (measured[i] or 0., i))
            m.remove(donor, 'D5f', site=site, tip=tip, lock=measured[donor],
                     age_steps=m.step_index-m.birth_steps[donor],
                     service_class=s['classes'][donor], economy_class='front',
                     stall_seconds=m.economy_stall[site])
        else:
            m.emit('D5f_none', site=site, reason='no_eligible_front', tip=tip)
        m.economy_stall[site] = 0.


def prospective_service(m, donor):
    """Pure full nearest-neighbor rebuild; no live delete/restore, native clones or RNG."""
    from evidence.tactical_composition_demo.growing_shapes.medium.rev7_design import geometric_graph
    from evidence.tactical_composition_demo.growing_shapes.medium.design_0h import SITES
    elements = [(e.id, e.x, e.y, m.native.role(e.id), m.native.gain(e.id), bool(e.silent))
                for e in m.native.elements if e.id != donor]
    drives = [(s, x, y, 1., 3.) for s, (x, y) in enumerate(SITES)]
    g = geometric_graph(elements, drives, m.native.params.k, m.native.params.radius,
                        strong=True, phase_scale=m.native.policy()[0], K=m.native.params.K)
    return {s for s in range(8) if g.path(s)}


def thin_redundant(m, measured):
    cost = m.cost()
    if cost <= 56.:
        m.emit('economy_prospective_check', triggered=False, cost_before=cost,
               candidates=0, trials=0, failures=0, result='below_trigger',
               prospective_elapsed_seconds=0., prospective_cpu_seconds=0.)
        return
    s = service_snapshot(m)
    candidates = sorted((i for i in s['eligible'] if i not in s['outputs']
                         and s['classes'][i] == 'redundant'),
                        key=lambda i: (measured[i] or 0., i))
    trials = failures = 0
    wall = cpu = 0.
    chosen = None
    for donor in candidates:
        w = time.monotonic(); c = time.process_time()
        after = prospective_service(m, donor)
        elapsed = time.monotonic()-w; compute = time.process_time()-c
        wall += elapsed; cpu += compute; trials += 1
        lost = sorted(s['served'] - after)
        failures += bool(lost)
        m.emit('economy_prospective_trial', [donor], passed=not lost,
               lost_sites=lost, served_before=sorted(s['served']), served_after=sorted(after),
               prospective_elapsed_seconds=elapsed, prospective_cpu_seconds=compute)
        if not lost:
            chosen = donor
            m.remove(donor, 'D5r', lock=measured[donor],
                     age_steps=m.step_index-m.birth_steps[donor],
                     service_class='redundant', economy_class='redundant')
            break
    m.emit('economy_prospective_check', triggered=True, cost_before=cost,
           candidates=len(candidates), trials=trials, failures=failures,
           result='removed' if chosen is not None else 'no_passing_candidate' if candidates else 'no_candidate',
           donor=chosen, prospective_elapsed_seconds=wall, prospective_cpu_seconds=cpu)


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('economy patch context mismatch: '+old[:90])
    return text.replace(old, new, 1)


def apply_variant(rd3, variant):
    if variant == 'ECOF':
        text = replace_once(rd3, '        self.path_waiting={s:dict(',
            '        self.economy_stall={s:0. for s in range(8)}\n'
            '        self.economy_deficit={s:math.inf for s in range(8)}\n'
            '        self.path_waiting={s:dict(')
        text = replace_once(text, '        blocked=False\n        while self.cost()>64:',
            '        retract_fronts(self,measured)\n        blocked=False\n        while self.cost()>64:')
        text = replace_once(text, "        self.emit('growth_check',count=len(self.native),",
            "        update_stall(self)\n        self.emit('growth_check',count=len(self.native),")
        return text+'\nfrom economy_kernel import retract_fronts, update_stall\n'
    if variant == 'ECOR':
        text = replace_once(rd3, '        out=self.b_out(blocked);path=self.b_path(blocked)',
            '        thin_redundant(self,measured)\n        out=self.b_out(blocked);path=self.b_path(blocked)')
        return text+'\nfrom economy_kernel import thin_redundant\n'
    raise ValueError(variant)
