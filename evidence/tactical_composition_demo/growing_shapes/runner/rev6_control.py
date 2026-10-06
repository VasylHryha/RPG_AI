"""M mirrors B1 at the exact check; U keeps the inherited bounded FIFO."""
import math
from .control import ControlQueue
from .rev6_protocol import generator
from ..medium.design_0h import SITES


class Matched:
    def __init__(self,key):
        self.rng=generator(key);self.slots=[];self.additions=0

    @property
    def unmatched(self):return [r for r in self.slots if r['outcome']!='accepted']

    def check(self,medium,intact_births,blocked=False):
        added=[]
        for source in intact_births:
            request=medium.request('B1-M')
            site=int(self.rng.integers(0,8));phase=float(self.rng.uniform(0,2*math.pi))
            point,attempts=medium.spiral_candidate(SITES[site],request,'B1-M')
            reason='placement' if point is None else medium.feasible(point,phase)
            if blocked and reason is None:reason='cost'
            if reason is None:
                id=medium.add(point,phase,rule='B1-M',source_id=source,site=site,request=request)
                medium.novelty[site]=0.;added.append(id);self.additions+=1
            medium.terminal(request,'B1-M',site,reason or 'accepted',attempts,source_id=source)
            row=dict(check=medium.step_index,source_id=source,request=request,site=site,outcome=reason or 'accepted')
            self.slots.append(row)
            if reason:medium.emit('M_unmatched',**row)
        return added

    def terminal(self,medium):pass  # No delayed repair or deletion of unmatched slots.


class Queue(ControlQueue):
    def __init__(self,key):
        # Parent has no persistent consumer except this RNG; do not instantiate its old domain.
        from collections import deque
        self.rng=generator(key);self.queue=deque();self.next_request=0
        self.additions=self.retries=self.drops=0

    def check(self,medium,intact_births,blocked=False):
        before={e.id for e in medium.native.elements}
        if blocked:
            # Resource-blocked checks still enqueue, then log a refused attempt through
            # the inherited feasibility rule. cost()>64 guarantees infeasibility.
            if medium.cost()<=64:raise ValueError('inconsistent protected-budget flag')
        super().check(medium,intact_births)
        return [e.id for e in medium.native.elements if e.id not in before]
