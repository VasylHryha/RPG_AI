"""G0 control FIFO: no B1, at most two attempts per check, retry later."""
from collections import deque
import math
import numpy as np
from .protocol import entropy


class ControlQueue:
    def __init__(self, seed):
        self.rng = np.random.default_rng(entropy(seed, 'g0_control'))
        self.queue = deque()
        self.next_request = 0
        self.additions = self.retries = self.drops = 0

    def check(self, medium, intact_births):
        for source_id in intact_births:
            self.queue.append({'request': self.next_request, 'source_id': source_id, 'attempts': 0, 'last_check': None})
            medium.emit('control_enqueue', source_id=source_id, request=self.next_request)
            self.next_request += 1
        attempts = 0
        while self.queue and attempts < 2:
            request = self.queue[0]
            if request['last_check'] == medium.step_index:
                break  # a failed head is retried at a later check, never now
            request['attempts'] += 1
            request['last_check'] = medium.step_index
            attempts += 1
            angle, radius, phase = self.rng.uniform(0, 2*math.pi), 5*math.sqrt(self.rng.uniform()), self.rng.uniform(0, 2*math.pi)
            point = (radius*math.cos(angle), radius*math.sin(angle))
            reason = medium.feasible(point, phase)
            if reason is None and any(math.hypot(e.x-point[0], e.y-point[1]) < .05 for e in medium.native.elements):
                reason = 'placement'
            if request['attempts'] == 2:
                self.retries += 1
            medium.emit('control_attempt', **request, position=point, phase=phase, reason=reason)
            if reason is None:
                medium.add(point, phase, rule='CONTROL_BIRTH', request=request['request'])
                self.additions += 1
                self.queue.popleft()
            elif request['attempts'] == 2:
                self.drops += 1
                medium.emit('control_drop', **request, reason=reason)
                self.queue.popleft()
            else:
                break

    def terminal(self, medium):
        while self.queue:
            self.drops += 1
            medium.emit('control_drop', **self.queue.popleft(), reason='terminal')
