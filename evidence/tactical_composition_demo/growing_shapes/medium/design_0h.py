"""Selectable revision-5.1 world-step/growth adapter; legacy Medium is unchanged.

Samples store actual offsets, site activity and directed neighbour membership.
No statistic retroactively substitutes a current position or phase for history.
"""
from collections import deque
from copy import deepcopy
from dataclasses import dataclass
import math
import numpy as np
from .medium import Medium, Params, Drive

DT = .1
SITES = tuple((4*math.cos(2*math.pi*s/8), 4*math.sin(2*math.pi*s/8)) for s in range(8))


def wrap(v):
    return (np.asarray(v) + math.pi) % (2*math.pi) - math.pi


def kernel(distance, reach=3.):
    return math.exp(-distance*distance/2) if distance < reach else 0.


def spiral(site, positions):
    q = np.asarray(site)
    for j in range(50):
        point = q + .1*j*np.array([math.cos(j*2.39996), math.sin(j*2.39996)])
        if all(np.linalg.norm(point-p) >= .05 for p in positions):
            return tuple(point)
    return None


@dataclass(frozen=True)
class Frame:
    index: int
    time: float
    # id -> (x, y, unwrapped theta)
    elements: dict
    # physical site -> (x, y, psi, strength)
    sites: dict
    # id -> immutable tuple of directed internal neighbour ids
    neighbors: dict


class DesignMedium:
    """Integer world clock, carried history, and only B1/D1/D3 enabled."""
    def __init__(self, seed=0, params=None):
        self.native = Medium(seed, params or Params(window=101, min_samples=100))
        self.native.options(automatic_samples=False, carried_sites=True, undirected_cost=True)
        self.native.first_id(0)
        self.step_index = 0
        self.frames = deque(maxlen=601)
        self.death = {}
        self.birth_steps = {}
        self.novelty = {s: 0. for s in range(8)}
        self.events = []
        self.drives = []
        self.peak = 0
        self.record()  # The qualification endpoint at t=0 is retained.

    @property
    def time(self):
        return self.step_index*DT

    def close(self):
        self.native.close()

    def clone(self, *, events=True, frames=True):
        branch = object.__new__(type(self))
        branch.__dict__ = {k: ([] if k == 'events' and not events else
                              deque([deepcopy(v[-1])] if v else [],maxlen=601) if k == 'frames' and not frames else deepcopy(v))
                           for k, v in self.__dict__.items() if k != 'native'}
        branch.native = self.native.clone()
        return branch

    def emit(self, rule, ids=(), **values):
        self.events.append(dict(time=self.time, rule=rule, ids=list(ids), values=values,
                                cost=self.cost()))

    def cost(self):
        return self.native.cost(1., .1)['total']

    def add(self, position, phase, rate=math.pi, gain=1., rule='B1', **values):
        id = self.native.add(*position, phase, rate)
        self.native.set_gain(id, gain)
        self.death[id] = 0.
        self.birth_steps[id] = self.step_index
        self.peak = max(self.peak, len(self.native))
        self.emit(rule, [id], **values)
        return id

    def remove(self, id, rule, **values):
        self.native.remove(id)
        self.death.pop(id, None)
        self.birth_steps.pop(id, None)
        self.emit(rule, [id], **values)

    def record(self):
        elements = self.native.elements
        idx, mask, _ = self.native.neighbors()
        self.frames.append(Frame(self.step_index, self.time,
            {e.id: (e.x, e.y, e.phase) for e in elements},
            {d.id: (d.x, d.y, d.phase, d.strength) for d in self.drives},
            {e.id: tuple(elements[j].id for j, on in zip(idx[i], mask[i]) if on)
             for i, e in enumerate(elements)}))

    def integrate(self, drives):
        """Exactly five full driven RK4 steps, then append the endpoint first."""
        self.drives = [Drive.from_buffer_copy(d) for d in drives]
        self.native.set_drives(self.drives)
        self.native.step(.02, 5)
        self.step_index += 1
        # Endpoint psi is from the same held observation at the new carrier time.
        for d in self.drives:
            d.phase += DT*d.rate
        self.native.observe()
        self.record()

    def samples(self, id, count):
        frames = list(self.frames)[-count:]
        if len(frames) != count or any(id not in f.elements for f in frames):
            return None
        return frames

    def offsets(self, id, partner, sensor=False):
        frames = self.samples(id, 100)
        if frames is None:
            return None
        values = []
        for f in frames:
            e = f.elements[id]
            if sensor:
                s = f.sites.get(partner)
                if s is None or s[3] <= 0 or math.hypot(e[0]-s[0], e[1]-s[1]) >= 3:
                    continue
                values.append(e[2]-s[2])
            elif partner in f.neighbors[id] and partner in f.elements:
                values.append(e[2]-f.elements[partner][2])
        return values if len(values) >= 80 else None

    @staticmethod
    def statistics(offsets):
        z = np.exp(1j*np.asarray(offsets)).mean()
        return min(1., float(abs(z))), float(np.angle(z))

    def lock(self, id):
        frames = self.samples(id, 100)
        if frames is None:
            return None
        partners = set(j for f in frames for j in f.neighbors[id])
        values = [self.offsets(id, j) for j in partners]
        values += [self.offsets(id, s, True) for s in range(8)]
        return max((self.statistics(v)[0] for v in values if v is not None), default=0.)

    def gain_signal(self, id):
        if self.samples(id, 101) is None:
            return None
        f = self.frames[-1]
        e = f.elements[id]
        salience = [(s[3]*kernel(math.hypot(e[0]-s[0], e[1]-s[1])), site)
                    for site, s in f.sites.items() if s[3] > 0]
        if not salience:
            return None
        weight, site = min(salience, key=lambda v: (-v[0], v[1]))
        if weight <= 0:
            return None
        values = self.offsets(id, site, True)
        return None if values is None else self.statistics(values)[0]

    def covered(self, site):
        f = self.frames[-1]
        s = f.sites.get(site)
        if s is None or s[3] <= 0:
            return False
        for id, e in f.elements.items():
            if self.samples(id, 101) is None or math.hypot(e[0]-s[0], e[1]-s[1]) >= 3:
                continue
            values = self.offsets(id, site, True)
            if values is not None:
                plv, offset = self.statistics(values)
                if plv >= .8 and abs(offset) <= .5:
                    return True
        return False

    def adapt(self):
        signals = {}
        for e in self.native.elements:
            frames = self.samples(e.id, 101)
            if frames is not None:
                estimate = (frames[-1].elements[e.id][2]-frames[0].elements[e.id][2])/10
                rate = float(np.clip(e.rate + .005*(estimate-e.rate), .5*math.pi, 1.5*math.pi))
                self.native.set_element(e.id, e.x, e.y, e.phase, rate)
            signal = self.gain_signal(e.id)
            if signal is not None:
                gain = float(np.clip(self.native.gain(e.id)+.005*(signal-self.native.gain(e.id)), 0, 2))
                self.native.set_gain(e.id, gain)
                signals[e.id] = signal
        self.emit('adaptation', rates={e.id: e.rate for e in self.native.elements},
                  gains={e.id: self.native.gain(e.id) for e in self.native.elements}, defined_signals=signals)
        return signals

    def timers(self):
        for e in self.native.elements:
            lock = self.lock(e.id)
            self.death[e.id] = self.death.get(e.id, 0.)+DT if lock is not None and lock < .5 else 0.
        coverage = []
        for site in range(8):
            s = self.frames[-1].sites.get(site)
            active = s is not None and s[3] > 0
            covered = self.covered(site) if active else False
            coverage.append(covered)
            self.novelty[site] = self.novelty[site]+DT if active and not covered else 0.
        return coverage  # audit reuses the measured decisions without re-running statistics

    def feasible(self, position, phase):
        if len(self.native)+1 > 64:
            return 'cap'
        with self.native.clone() as trial:
            trial.add(*position, phase, math.pi)
            if trial.cost(1., .1)['total'] > 64:
                return 'cost'
        return None

    def growth(self, births=True):
        """D1, D3, then B1; accepted births capped at two in site order."""
        measured = {e.id: self.lock(e.id) for e in self.native.elements}
        for e in self.native.elements:
            if self.step_index-self.birth_steps[e.id] >= 200 and self.death.get(e.id, 0.) >= 40-1e-9:
                self.remove(e.id, 'D1', lock=measured[e.id], duration=self.death[e.id])
        blocked = False
        while self.cost() > 64:
            removable = [e for e in self.native.elements if self.step_index-self.birth_steps[e.id] >= 200]
            if not removable:
                blocked = True
                self.emit('protected_over_budget')
                break
            e = min(removable, key=lambda e: (measured[e.id] or 0., e.id))
            self.remove(e.id, 'D3', lock=measured[e.id])
        added = []
        if births and not blocked:
            for site in range(8):
                if len(added) == 2:
                    break
                if self.novelty[site] < 20-1e-9:
                    continue
                s = self.frames[-1].sites[site]
                position = spiral(s[:2], [(e.x, e.y) for e in self.native.elements])
                reason = 'placement' if position is None else self.feasible(position, s[2])
                if reason:
                    self.emit('B1_rejected', site=site, reason=reason, duration=self.novelty[site])
                else:
                    added.append(self.add(position, s[2], site=site, duration=self.novelty[site]))
                    self.novelty[site] = 0.
        self.emit('growth_check', count=len(self.native), additions=added, protected_over_budget=blocked)
        return added
