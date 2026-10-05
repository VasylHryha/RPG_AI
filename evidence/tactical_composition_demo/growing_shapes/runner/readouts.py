"""Pairing and development aggregation, separate from engineering smoke."""
import math
import numpy as np
from .protocol import readouts


def seed_unit(intact, control):
    a, b = intact.report(), control.report()
    error = a['invalid'] or b['invalid']
    if not a['complete'] or not b['complete'] or intact.episodes != 2000 or control.episodes != 2000:
        error = error or 'incomplete development protocol (2000 episodes required)'
    if len(intact.evaluations) != min(20, len(intact.snapshots)):
        error = error or 'snapshot evaluator incomplete'
    def competence(report):
        values = report['competence']
        if values is None or set(values) != set(report['usable']):
            return None
        return float(np.mean(list(values.values())))
    ca, cb = competence(a), competence(b)
    scalar = [a['coverage'], b['coverage'], a['slope'], ca, cb]
    if any(v is None or not math.isfinite(v) for v in scalar):
        error = error or 'missing or non-finite estimand'
    return {'seed': a['seed'], 'invalid': error, 'complete': a['complete'] and b['complete'],
            'usable': a['usable'], 'eligible': a['eligible'],
            'coverage': a['coverage'], 'control_coverage': b['coverage'],
            'competence': ca, 'control_competence': cb, 'slope': a['slope'],
            'rejected': a['rejected'], 'protected_over_budget': a['protected_over_budget'],
            'snapshots': len(a['snapshots']), 'g5': [e['G5_D'] for e in a['evaluations']],
            'dropped': control.queue.drops, 'control_additions': control.queue.additions,
            'control_retries': control.queue.retries,
            'intact_additions': sum(e['rule'] == 'B1' for e in a['events']),
            'intact_deaths': sum(e['rule'] in ('D1', 'D3') for e in a['events']),
            'control_deaths': sum(e['rule'] in ('D1', 'D3') for e in b['events']),
            'D3_removals': sum(e['rule'] == 'D3' for e in a['events']),
            'late_turnover': sum(e['rule'] in ('B1', 'D1', 'D3') and e['time'] >= 25600 for e in a['events']),
            'G1c': a['evaluations']}


def aggregate(units):
    return {'seed_units': units, 'readouts': readouts(units),
            'no_formation_seeds': sum(s['snapshots'] == 0 for s in units),
            'claims': {'H-BG': 'NOT_TESTED', 'H-PS': 'NOT_TESTED', 'H-RBG': 'NOT_TESTED'}}
