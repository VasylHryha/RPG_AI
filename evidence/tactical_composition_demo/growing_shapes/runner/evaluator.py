"""Frozen validation calibration and isolated per-episode evaluation copies."""
from dataclasses import asdict
import math
from ..medium.design_0h import DesignMedium
from ..world.world import World, Policy, Library
from .protocol import BINDING, VERSION, TASKS, calibration, oriented, permutation, bindings, action, canonical, template_hash


def freeze(library=None):
    library = library or Library()
    rows, raw = {}, {}
    for task in TASKS:
        scores = {}
        for kind in ('reference', 'random'):
            scores[kind] = []
            for seed in range(256):
                with World(task, seed, 'validation', library=library) as world, \
                     Policy(task, seed, kind, 'validation', library=library) as policy:
                    while not world.observe().done:
                        world.step(policy.action(world.observe()))
                    scores[kind].append(oriented(task, world.score()))
        raw[task] = scores
        rows[task] = calibration(task, scores['reference'], scores['random'])
    return rows, {'namespace': 'validation', 'episodes': [0, 255], 'raw': raw,
                  'calibration': {t: asdict(c) for t, c in rows.items()},
                  'usable': [t for t in TASKS if rows[t].usable]}


def copy_template(value, carrier_offset=0.):
    if value.get('binding') != BINDING or value.get('constants_version') != VERSION:
        raise ValueError('template binding or constants version mismatch')
    canonical(value)  # reject nonfinite coefficients
    medium = DesignMedium()
    if carrier_offset not in (0., math.pi):
        medium.close()
        raise ValueError('evaluation carrier offsets are 0 and pi')
    medium.native.start_clock(carrier_offset/math.pi)
    for row in value['members']:
        x, y, offset, rate, gain = row
        medium.add((x, y), offset+carrier_offset, rate, gain, rule='COPY')
    # Evaluation clock begins at this carrier time. Offset pi is t_copy=1 s.
    medium.step_index = round(carrier_offset/math.pi/.1)
    medium.frames.clear()
    medium.record()
    return medium


class Evaluator:
    def __init__(self, calibration_rows, library=None):
        self.rows = dict(calibration_rows)
        self.usable = tuple(t for t in TASKS if self.rows[t].usable)
        if not self.usable:
            raise ValueError('INVALID: zero usable tasks')
        self.library = library or Library()
        self.episodes = 0
        self.copies = 0
        self.instances = []

    def evaluate(self, value, carrier_offset=0.):
        result = {}
        for task in self.usable:
            scores = []
            for episode in range(128):
                medium = copy_template(value, carrier_offset)
                self.instances.append({'instance_id': self.copies, 'type_id': template_hash(value),
                                       'task': task, 'episode_seed': episode, 'carrier_offset': carrier_offset})
                self.copies += 1
                try:
                    assignment = permutation(episode)
                    with World(task, episode, 'validation', library=self.library) as world:
                        while not world.observe().done:
                            obs = world.observe()
                            medium.integrate(bindings(task, obs, assignment, medium.time))
                            world.step(action(task, obs, medium.native, medium.time))
                        scores.append(oriented(task, world.score()))
                    self.episodes += 1
                finally:
                    medium.close()
            result[task] = self.rows[task].normalize(sum(scores)/128)
        return result
