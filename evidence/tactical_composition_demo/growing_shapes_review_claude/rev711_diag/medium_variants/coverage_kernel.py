"""Amendment-1 scratch laws; graph/history only, independent of telemetry."""
import math
from service_graph import service_snapshot


def update_clock(m):
    # Called once at the completed integrate boundary, before adapt/timers/growth.
    # No intra-check births/removals call this. Native and reference use DT=.1.
    s = service_snapshot(m)
    for site in range(8):
        if site in s['served']:
            m.coverage_wait[site] = 0.
        elif site in s['active']:
            m.coverage_wait[site] += .1


def fair_order(gaps, waiting, pointer):
    return sorted(gaps, key=lambda site: (not math.isfinite(gaps[site]),
                                         -waiting[site], (site-pointer) % 8))


def recycle(m, point, phase, site, request, rule, anchors=()):
    """Return (terminal outcome or None on admission, metadata). No insertion."""
    if m.coverage_recycled:
        return 'cost', {}
    before = service_snapshot(m)
    if site in before['served']:
        return 'cost', {}
    donors = [i for i in before['eligible'] if i not in anchors
              and before['classes'][i] == 'non-service']
    if not donors:
        return 'cost', {}
    donor = min(donors, key=lambda i: (m.coverage_locks[i] or 0., i))
    age = m.step_index - m.birth_steps[donor]
    m.coverage_recycled = True
    m.remove(donor, 'D3r', lock=m.coverage_locks[donor], age_steps=age,
             service_class=before['classes'][donor], request=request,
             birth_rule=rule, site=site)
    checks = m.trial(site, *anchors, point) if rule == 'B-path' else None
    # B1's original admission has no strong-progress geometric trial.
    reason = m.feasible(point, phase)
    if checks is not None and not all(checks.values()):
        reason = 'geometry'
    outcome = 'recycle_failed' if reason else None
    meta = dict(recycled_id=donor, retry_reason=reason, retry_checks=checks,
                initial_cost_refusal=True)
    m.emit('coverage_recycle', [donor], request=request, birth_rule=rule,
           site=site, point=point, donor_class=before['classes'][donor],
           donor_lock=m.coverage_locks[donor], age_steps=age,
           retry_outcome=outcome or 'accepted')
    return outcome, meta


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('coverage patch context mismatch: '+old[:90])
    return text.replace(old, new, 1)


def apply_variant(rd3, variant):
    """Exact source patches atop reproduced RD3; never mutate committed law."""
    if variant == 'COVA':
        result = replace_once(rd3, '        self.path_waiting={s:dict(',
                              '        self.coverage_wait={s:0. for s in range(8)}\n        self.path_waiting={s:dict(')
        result = replace_once(result, '        return row\n\n    def phase_topology',
                              '        update_clock(self)\n        return row\n\n    def phase_topology')
        result = replace_once(result, '        order=sorted(gaps,key=lambda s:(gaps[s],(s-p)%8))',
                              '        order=fair_order(gaps,self.coverage_wait,p)')
        return result + '\nfrom coverage_kernel import update_clock, fair_order\n'
    if variant != 'COVB':
        raise ValueError(variant)
    result = replace_once(rd3, "OUTCOMES=('accepted',", "OUTCOMES=('recycle_failed','accepted',")
    result = replace_once(result, '        measured={e.id:self.lock(e.id) for e in self.native.elements}',
                          '        measured={e.id:self.lock(e.id) for e in self.native.elements}\n        self.coverage_locks=measured\n        self.coverage_recycled=False')
    result = replace_once(result,
        "                if blocked and reason is None:reason='cost'\n                if reason:\n                    self.terminal(request,'B-path',site,reason,attempts,failures=failures)",
        "                if blocked and reason is None:reason='cost'\n                retry_meta={}\n                if reason=='cost':\n                    self.emit('coverage_cost_refusal',request=request,birth_rule='B-path',site=site,point=point)\n                    reason,retry_meta=recycle(self,point,es[a].phase,site,request,'B-path',(a,b))\n                if reason:\n                    self.terminal(request,'B-path',site,reason,attempts,failures=failures,**retry_meta)")
    result = replace_once(result,
        "                self.terminal(request,'B-path',site,'accepted',attempts,id=id,failures=failures)",
        "                self.terminal(request,'B-path',site,'accepted',attempts,id=id,failures=failures,**retry_meta)")
    result = replace_once(result,
        "            if blocked and reason is None:reason='cost'\n            if reason:self.terminal(request,'B1',site,reason,attempts)",
        "            if blocked and reason is None:reason='cost'\n            retry_meta={}\n            if reason=='cost':\n                self.emit('coverage_cost_refusal',request=request,birth_rule='B1',site=site,point=point)\n                reason,retry_meta=recycle(self,point,d.phase,site,request,'B1')\n            if reason:self.terminal(request,'B1',site,reason,attempts,**retry_meta)")
    result = replace_once(result,
        "                added.append(id);self.novelty[site]=0.;self.terminal(request,'B1',site,'accepted',attempts,id=id)",
        "                added.append(id);self.novelty[site]=0.;self.terminal(request,'B1',site,'accepted',attempts,id=id,**retry_meta)")
    return result + '\nfrom coverage_kernel import recycle\n'
