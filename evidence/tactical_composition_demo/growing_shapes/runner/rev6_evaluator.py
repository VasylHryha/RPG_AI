"""Fresh-copy evaluation and interventions; there is no automatic panel execution."""
from contextlib import ExitStack
import json
import math
from pathlib import Path
import numpy as np
from ..world.world import World, Policy, Library, Action
from ..medium.medium import Drive
from .rev6_protocol import TASKS, Calibration, copy_template, template_hash, seed, generator, permutation, bindings, oriented, action, relay, paired_bounds, donor_entries, replay_on_clock
from . import rev6_native


def reused_calibration():
    path=Path(__file__).parent/'development_20261006/CALIBRATION.json'
    receipt=json.loads(path.read_text())
    rows={t:Calibration(**v) for t,v in receipt['calibration'].items()}
    return rows,dict(label='REUSED_5_1_CALIBRATION',source=str(path),namespace='validation',episodes=[0,255])


class Evaluator:
    def __init__(self,rows,library=None,backend='native',*,execution=None,scope='development',arm='task_blind',k=0,trace_dir=None):
        if backend not in ('native','reference'):raise ValueError('unknown backend')
        from .rev6_identity import assert_inputs
        assert_inputs()
        self.trace_dir=Path(trace_dir) if trace_dir else None
        self.rows=dict(rows);self.usable=tuple(t for t in TASKS if self.rows[t].usable)
        if not self.usable:raise ValueError('INVALID: zero usable tasks')
        self.library=library or Library();self.backend=backend
        self.execution,self.scope,self.arm,self.k=execution,scope,arm,k
        self.episodes=self.copies=0;self.instances=[]
        self.lib=rev6_native.library() if backend=='native' else None
        self.donors={r['recipient']:r['donor'] for r in donor_entries()}
        self.donor_cache={}

    def require(self):
        if self.execution is None:raise PermissionError('evaluator has no execution grant')
        self.execution.require(self.scope)

    def capture(self,task,episode):
        """Capture open-loop donor drives on its own bindings; recipient truth is unused."""
        self.require();key=(task,episode)
        if key not in self.donor_cache:
            schedule=[]
            with World(task,episode,'validation',library=self.library) as world:
                while not world.observe().done:
                    obs=world.observe();step=len(schedule);ds=bindings(task,obs,permutation(episode),step*.1)
                    schedule.append([[d.id,d.x,d.y,d.phase-math.pi*step*.1,d.rate,d.strength,d.width,d.reach] for d in ds])
                    from .rev6_protocol import decode
                    world.step(decode(task,obs,0.,0.,step*.1))
            if self.scope=='fixtures':self.donor_cache[key]=schedule
            else:return schedule
        return self.donor_cache[key]

    def episode(self,value,task,episode,*,mode='intact',donor=None,carrier_offset=0.):
        self.require()
        if mode not in ('intact','donor','output_channel','receiver','default','random','site0','oracle'):raise ValueError('unknown intervention')
        comparator=mode in ('default','random','site0','oracle')
        state=dict(value,members=[]) if comparator else value
        medium=copy_template(state,carrier_offset)
        instance=dict(instance_id=self.copies,type_id=template_hash(value),task=task,world_episode=episode,carrier_offset=carrier_offset,mode=mode)
        self.instances.append(instance);self.copies+=1
        try:
            outputs=[e.id for e in medium.native.elements if medium.role(e.id)=='output']
            if mode=='output_channel':medium.native.lesions(outputs)
            if mode=='receiver':
                ordinary=[e.id for e in medium.native.elements if medium.role(e.id)=='element']
                if len(ordinary)<len(outputs):
                    instance['not_run']='insufficient non-output receiver candidates'
                    return dict(status='not_run',reason=instance['not_run'],score=None,decisions=[])
                rng=generator(f'lesion/{self.arm}/{self.k}/{episode}')
                selected=[int(v) for v in rng.choice(ordinary,size=len(outputs),replace=False)]
                medium.native.lesions(selected);instance['receivers']=selected
            schedule=None
            if mode=='donor':
                donor=self.donors.get(episode) if donor is None else donor
                if donor is None:raise ValueError('missing registered donor')
                schedule=[replay_on_clock(row,carrier_offset/math.pi+j*.1) for j,row in enumerate(self.capture(task,donor))]
                instance['donor_episode']=donor
            decisions=[]
            with ExitStack() as stack:
                world=stack.enter_context(World(task,episode,'validation',library=self.library))
                policy=stack.enter_context(Policy(task,seed(f'random_policy/{task}/{episode}'),'random','validation',library=self.library)) if mode=='random' else None
                if self.backend=='native' and mode not in ('default','random'):
                    data=rev6_native.assay(medium,world,permutation(episode),schedule=schedule,relay={'site0':1,'oracle':2}.get(mode,0),lib=self.lib)
                    decisions=data['decisions']
                else:
                    while not world.observe().done:
                        obs=world.observe();j=len(decisions)
                        ds=bindings(task,obs,permutation(episode),medium.time) if schedule is None else schedule[j]
                        diag=medium.integrate(ds)
                        chosen=policy.action(obs) if policy else Action() if mode=='default' else relay(task,obs,medium.drives,medium.time,mode) if mode in ('site0','oracle') else action(task,obs,medium.native,medium.time)
                        # Default choose uses the lowest live id (same abstention decoder).
                        if mode=='default' and task=='choose':
                            from .rev6_protocol import decode
                            chosen=decode(task,obs,0,0,medium.time)
                        decisions.append(dict(angle=chosen.angle,has_output=bool(medium.influence().outputs),paths=diag['paths'],exposure=diag['exposure'],drives=[[getattr(d,f) for f,_ in d._fields_] for d in ds]))
                        world.step(chosen)
                score=world.score();raw=oriented(task,score)
                self.episodes+=1
                return dict(status='evaluated',score=self.rows[task].normalize(raw),raw_score=raw,
                            distance_error=score.distance_error,decisions=decisions,instance=instance)
        finally:medium.close()

    def evaluate(self,value,carrier_offset=0.):
        # Snapshot G1c/G5 use the same fresh revision-6 panel with no interventions.
        return {t:float(np.mean([self.episode(value,t,e,carrier_offset=carrier_offset)['score'] for e in range(512,640)])) for t in self.usable}

    def panel(self,value):
        result={}
        for task in self.usable:
            scores={mode:[] for mode in ('intact','default','random','donor','output_channel','receiver','site0','oracle')}
            if self.trace_dir:
                from .rev6_trace import Chunks
                records={mode:Chunks(self.trace_dir/task/mode) for mode in scores}
            else:records={mode:[] for mode in scores}
            for e in range(512,640):
                for mode in scores:
                    row=self.episode(value,task,e,mode=mode)
                    records[mode].append(row)
                    if row['status']=='evaluated':scores[mode].append(row['score'])
            intact=scores['intact'];bounds={mode:paired_bounds(intact,scores[mode],secondary=task!='perceive') for mode in ('default','random','donor','output_channel','site0','oracle')}
            # Receiver lesion is descriptive; reasoned not-run never silently enters a contrast.
            bounds['receiver']=paired_bounds(intact,scores['receiver'],secondary=task!='perceive') if len(scores['receiver'])==128 else dict(status='not_run',reason='insufficient receivers in recorded episodes')
            stored={mode:rows.receipt() if hasattr(rows,'receipt') else rows for mode,rows in records.items()}
            result[task]=dict(**scores,bounds=bounds,records=stored,G2_sel_label='superiority to the site-0 relay')
        return result
