"""Pure revision-5.1 contracts. No training runs at import time."""
from dataclasses import dataclass
import hashlib
import json
import math
import numpy as np
from ..medium.design_0h import SITES, wrap
from ..medium.medium import Drive
from ..world.world import Action

TASKS = ('perceive', 'move', 'remember_static', 'choose')
VERSION = 'DESIGN_0H_revision_5.1'
BINDING = {'binding_rule': 'episode_seed_permutation_v1', 'physical_sites': 8,
           'slot_order': 'per-task table, section 3'}


def entropy(seed, domain):
    return int.from_bytes(hashlib.sha256(f'{seed}:{domain}'.encode()).digest()[:8], 'little')


def permutation(episode_seed):
    return tuple(int(i) for i in np.random.default_rng(entropy(episode_seed, 'binding')).permutation(8))


def bindings(task, observation, assignment, time):
    rows = []
    if task == 'move':
        d, desired = observation.target_distance, observation.desired_range
        rows = [(observation.target_angle+(math.pi if d < desired else 0),
                 2*min(1., abs(d-desired)/2))]
    else:
        enemies = sorted(observation.enemies[:observation.enemy_count], key=lambda e: e.id)
        for e in enemies:
            k = 2*math.exp(-e.distance/10) if e.visible else 0.
            if task == 'choose':
                k *= (1+(1-e.hp/100))*(1 if e.distance <= 2.5 else .5)
            rows.append((e.angle, k))
    drives = [Drive(s, *SITES[s], math.pi*time, math.pi, 0., 1., 3.) for s in range(8)]
    for j, (angle, k) in enumerate(rows):
        drives[assignment[j]].phase += angle
        drives[assignment[j]].strength = k
    return drives


def action(task, observation, native, time):
    coherence, phase = native.readout(0, 0, 1, 2)
    abstain = coherence < .05
    beta = float(wrap(phase-math.pi*time))
    if task == 'choose':
        live = [e for e in observation.enemies[:observation.enemy_count] if e.visible and e.hp > 0]
        selected = min(live, key=lambda e: (0 if abstain else abs(float(wrap(beta-e.angle))), e.id))
        return Action(0, 0, selected.id)
    if abstain:
        return Action()
    if task == 'perceive':
        return Action(beta, float(np.clip(10*math.log(1/coherence), 0, math.sqrt(800))))
    if task == 'move':
        return Action(beta, min(1., coherence/.8))
    return Action(beta, 0)


def oriented(task, score):
    return float(score.correct_choice_rate if task == 'choose' else
                 -score.goal_error if task == 'move' else -score.angular_error)


@dataclass(frozen=True)
class Calibration:
    task: str
    reference: float
    random: float
    difference: float
    se: float
    usable: bool

    def normalize(self, score):
        if not self.usable:
            raise ValueError('INVALID: task is not usable')
        value = (score-self.random)/(self.reference-self.random)
        if not math.isfinite(value):
            raise ValueError('INVALID: non-finite normalized score')
        return value


def calibration(task, reference, random):
    r, b = np.asarray(reference), np.asarray(random)
    if r.shape != (256,) or b.shape != (256,) or not np.isfinite(r).all() or not np.isfinite(b).all():
        raise ValueError('INVALID: calibration needs 256 finite paired episodes')
    difference = r-b
    mean, se = float(difference.mean()), float(difference.std(ddof=1)/16)
    denominator = float(r.mean()-b.mean())
    return Calibration(task, float(r.mean()), float(b.mean()), mean, se,
                       mean > 0 and mean > 3*se and math.isfinite(denominator) and denominator > 0)


def rotation(episode, usable):
    tasks = [task for task in TASKS if task in usable]
    if not tasks:
        raise ValueError('INVALID: zero usable tasks')
    return tasks[(episode//20) % len(tasks)]


def template(native, ids, time):
    members = []
    by_id = {e.id: e for e in native.elements}
    for id in sorted(ids):
        e = by_id[id]
        members.append([float(e.x), float(e.y), float(e.phase-math.pi*time), float(e.rate), native.gain(id)])
    # Persistent ids establish canonical order; not hashed as content scalars.
    return {'members': members, 'binding': dict(BINDING), 'constants_version': VERSION}


def canonical(value):
    # CPython JSON emits finite floats via repr; reject nonfinite JSON extensions.
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def template_hash(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def covariance(values1, values2):
    if set(values1) != set(values2) or not values1:
        raise ValueError('INVALID: mismatched or empty competence tasks')
    values = [abs(values1[t]-values2[t]) for t in values1]
    if not np.isfinite(values).all():
        raise ValueError('INVALID: non-finite covariance')
    return max(values)


def readouts(seeds):
    """Seed is the unit, ordered INVALID first, exactly eight complete units."""
    needed = ('coverage', 'control_coverage', 'competence', 'control_competence', 'slope',
              'g5', 'snapshots', 'dropped', 'rejected', 'protected_over_budget')
    invalid = len(seeds) != 8
    for s in seeds:
        invalid |= bool(s.get('invalid')) or not s.get('complete') or not s.get('usable') or s.get('eligible', 0) == 0
        invalid |= any(k not in s for k in needed)
        scalars = [s.get(k) for k in needed[:5]]
        invalid |= any(v is None or not math.isfinite(v) for v in scalars)
        invalid |= not np.isfinite(s.get('g5', [])).all()
        invalid |= len(s.get('g5', [])) != min(20, s.get('snapshots', 0))
    if invalid:
        return {k: 'INVALID' for k in ('G0', "G0'", 'G1', 'G1c', 'G5')}
    passing = sum(not s['dropped'] and s['coverage'] > s['control_coverage'] and
                  s['competence'] > s['control_competence'] for s in seeds)
    failing = sum(s['coverage'] <= s['control_coverage'] and s['competence'] <= s['control_competence'] for s in seeds)
    settled = [abs(s['slope']) <= .5 and not s['rejected'] and not s['protected_over_budget'] for s in seeds]
    bearing = [s for s in seeds if s['snapshots'] > 0]
    g5 = 'INCONCLUSIVE'
    if len(bearing) >= 6:
        if any(not s['g5'] for s in bearing):
            g5 = 'INVALID'
        elif sum(np.mean(np.asarray(s['g5']) <= .1) >= .8 for s in bearing) >= 6:
            g5 = 'PASS'
        elif sum(np.mean(np.asarray(s['g5']) <= .1) < .5 for s in bearing) >= 3:
            g5 = 'FAIL'
    return {'G0': 'PASS' if passing >= 6 else 'FAIL' if failing >= 6 else 'INCONCLUSIVE',
            "G0'": 'PASS' if sum(settled) >= 6 else 'FAIL' if 8-sum(settled) >= 3 else 'INCONCLUSIVE',
            'G1': 'PASS' if len(bearing) >= 6 else 'FAIL' if len(bearing) <= 2 else 'INCONCLUSIVE',
            'G1c': 'DESCRIPTIVE', 'G5': g5}
