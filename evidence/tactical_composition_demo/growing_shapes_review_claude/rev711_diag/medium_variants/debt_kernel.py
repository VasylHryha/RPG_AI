"""Single RD3 scheduling change; task-blind kernel history, observer independent."""
import math
from service_graph import service_snapshot
def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('DEBT patch context mismatch: '+old[:90])
    return text.replace(old, new, 1)


def update_debt(m):
    snapshot = service_snapshot(m)
    for site in snapshot['active'] - snapshot['served']:
        m.service_debt[site] += .1


def debt_order(gaps, debt, pointer):
    return sorted(gaps, key=lambda s: (not math.isfinite(gaps[s]), -debt[s], (s-pointer)%8))


def apply_variant(rd3, variant='DEBT'):
    if variant != 'DEBT':
        raise ValueError(variant)
    result = replace_once(rd3, '        self.path_waiting={s:dict(',
                          '        self.service_debt={s:0. for s in range(8)}\n        self.path_waiting={s:dict(')
    result = replace_once(result, '        return row\n\n    def phase_topology',
                          '        update_debt(self)\n        return row\n\n    def phase_topology')
    result = replace_once(result, '        order=sorted(gaps,key=lambda s:(gaps[s],(s-p)%8))',
                          '        order=debt_order(gaps,self.service_debt,p)')
    return result + '\nfrom debt_kernel import update_debt, debt_order\n'
