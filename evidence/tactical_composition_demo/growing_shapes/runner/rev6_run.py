"""Versioned revision-6 live orchestration; execution requires an explicit grant."""
import argparse
from collections import defaultdict
from copy import deepcopy
import json
import hashlib
import math
from pathlib import Path
import time as wallclock
import numpy as np
from ..medium.rev6_design import Rev6Medium as DesignMedium
from ..world.world import Library, World
from .rev6_protocol import entropy, permutation, bindings, action, oriented, rotation, template, template_hash, covariance, generator, seed as seed_fn, training_episode, recovery_generator, late_count
from .rev6_evaluator import Evaluator
from .rev6_control import Matched, Queue
from . import rev6_qualification as qualification


class Run:
    def __init__(self, seed, rows, reward=False, *, episodes=2000, control=False, library=None,
                 backend='native', batch_size=200, audit=False, audit_dir=None, policy='intact', arm=None, initial=None, keys=None, execution=None, scope='development'):
        qualification.assert_frozen_source()
        from .rev6_identity import assert_inputs
        assert_inputs()
        self.execution,self.scope=execution,scope
        self.policy=policy;self.arm=arm or ('reward' if reward else 'task_blind')
        if policy not in ('intact','M','U') or self.arm not in ('task_blind','reward') or reward!=(self.arm=='reward') or type(seed) is not int or not 0<=seed<8:
            raise ValueError('invalid arm/policy')
        keys=keys or dict(medium=f'medium/{self.arm}/{seed}',growth=f'growth/{self.arm}/{seed}/{policy}',matched=f'matched/{self.arm}/{seed}',control_u=f'control_u/{self.arm}/{seed}',recovery=f'recovery/{self.arm}/{seed}/{policy}')
        self.keys=dict(keys);self.recovery_master=seed_fn(keys['recovery'])
        self.audit_dir=Path(audit_dir) if audit_dir else None
        self.seed, self.rows, self.reward = seed, dict(rows), reward
        self.usable = tuple(t for t, c in rows.items() if c.usable)
        if not self.usable:
            raise ValueError('INVALID: zero usable tasks')
        if not isinstance(episodes, int) or episodes < 1:
            raise ValueError('positive episode count required')
        self.episodes, self.control = episodes, policy != 'intact'
        if backend not in ('reference', 'native') or not isinstance(batch_size,int) or not 1 <= batch_size <= 200:
            raise ValueError('select reference/native and batch size 1..200')
        self.backend, self.batch_size, self.audit = backend, batch_size, audit
        self.step_audit = []
        self.batch_calls = 0
        if backend == 'native':
            from .rev6_native import library as perf_library
            self.perf_library = perf_library()
        self.library = library or Library()
        if initial is None:
            self.medium = DesignMedium(seed_fn(keys['medium']),growth_rng=generator(keys['growth']))
            rng=generator(keys['medium'])
            for _ in range(24):
                angle,radius=rng.uniform(0,2*math.pi),5*math.sqrt(rng.uniform())
                self.medium.add((radius*math.cos(angle),radius*math.sin(angle)),rng.uniform(0,2*math.pi),math.pi*(1+rng.uniform(-.1,.1)),.5,rule='INITIAL')
            self.medium.frames.clear();self.medium.record()
        else:
            self.medium=initial.clone(events=False)
            self.medium.growth_rng=generator(keys['growth']);self.medium.frozen=False
        self.horizon=self.medium.step_index+episodes*160
        self.rbar = .5
        self._last_reward=[]
        self.pending = []
        self.snapshots = []
        self.group_hashes = defaultdict(set)
        self.coverage_samples = []
        self.growth_counts = []
        self.drive_log = []
        self.birth_index = {}
        if audit_dir is not None:
            from .rev6_trace import Chunks as TraceStore
            directory = Path(audit_dir)
            self.medium.events = TraceStore(directory/'events', self.medium.events)
            self.drive_log = TraceStore(directory/'drives')
            self.medium.diagnostics=TraceStore(directory/'endpoint_graphs')
        self.episode_log = []
        self.queue = Matched(keys['matched']) if policy=='M' else Queue(keys['control_u']) if policy=='U' else None
        self.exposure = dict(training_steps=0, training_episodes=0, qualification_frames=0,
                             recovery_simulated_seconds=0., evaluator_episodes=0, reward_episodes=0)
        self.timing = dict(training=0., qualification=0., recovery=0., evaluation=0.)
        self.invalid = None
        self.complete = False
        self.evaluations = []
        self.final_competence = None

    def close(self):
        for item in self.pending:
            item['saved'].close()
        self.medium.close()
        for store in (self.medium.events,self.drive_log,self.medium.diagnostics):
            if hasattr(store,'close'):
                store.close()

    def reward_update(self, task, score, signals):
        if not self.reward:
            return
        reward = float(np.clip(self.rows[task].normalize(score), 0, 1))
        for e in self.medium.native.elements:
            eligibility = sum(signals[e.id])/len(signals[e.id]) if signals[e.id] else 0.
            before = self.medium.native.gain(e.id)
            after = float(np.clip(before+.5*(reward-self.rbar)*eligibility, 0, 2))
            self.medium.native.set_gain(e.id, after)
            self._last_reward.append(dict(id=e.id,role=self.medium.role(e.id),eligibility=eligibility,delta=after-before))
            self.medium.emit('reward_gain', [e.id], reward=reward, baseline=self.rbar,
                             eligibility=eligibility, before=before, after=after)
        self.rbar += .1*(reward-self.rbar)
        self.exposure['reward_episodes'] += 1

    def qualify(self):
        started = wallclock.perf_counter()
        check = qualification.start(self.medium)
        self.exposure['qualification_frames'] += 601
        self.medium.emit('qualification', cohort=check['cohort'], candidates=[c['ids'] for c in check['candidates']],
                         alias_max=check['alias_max'], possibly_aliased=check['possibly_aliased'],
                         claim='driven/cohort-restricted', warning='screen does not certify absence of aliasing')
        # Immutable complete native state is preserved for audit, alongside clone.
        saved = self.medium.clone(events=False)
        self.pending.append({'check': check, 'saved': saved, 'state': {'native': saved.native.save().hex(),
                             'world_step': saved.step_index, 'birth_steps': dict(saved.birth_steps),
                             'roles':{e.id:saved.role(e.id) for e in saved.native.elements},'D4':{e.id:saved.native.cut_off(e.id) for e in saved.native.elements},'death_timers': dict(saved.death), 'novelty_timers': dict(saved.novelty),
                             'frames': [{'index': f.index, 'time': f.time, 'elements': f.elements,
                                         'sites': f.sites, 'neighbors': f.neighbors} for f in saved.frames]},
                             'index': self.medium.step_index, 'schedule': []})
        self.timing['qualification'] += wallclock.perf_counter()-started

    def admissions(self):
        for item in list(self.pending):
            if len(item['schedule']) != 600:
                continue
            started = wallclock.perf_counter()
            arguments = (item['saved'], item['check'], item['schedule'],
                         recovery_generator(self.recovery_master,item['index']))
            if getattr(self,'backend','reference') == 'native':
                candidates, simulated = qualification.finish(*arguments, backend='native', lib=self.perf_library)
            else:
                candidates, simulated = qualification.finish(*arguments)
            self.exposure['recovery_simulated_seconds'] += simulated
            self.medium.emit('recovery_complete', check_time=item['index']*.1,
                             candidates=[{'ids': c['ids'], 'stats': c['stats'], 'criteria': c.get('criteria')}
                                         for c in item['check']['candidates']],
                             schedule_start=item['index'], schedule_steps=600,
                             check_state=item['state'], claim='driven/cohort-restricted')
            for candidate in candidates:
                value = candidate['template']
                digest = template_hash(value)
                group = tuple(candidate['ids'])
                if digest in self.group_hashes[group]:
                    self.medium.emit('snapshot_duplicate', candidate['ids'], type_id=digest)
                    continue
                self.group_hashes[group].add(digest)
                self.snapshots.append({'type_id': digest, 'template': value, 'members': candidate['ids'],
                                       'check_time': item['index']*.1, 'admission_time': self.medium.time,
                                       'stats': candidate['stats']})
                self.medium.emit('snapshot', candidate['ids'], type_id=digest, check_time=item['index']*.1)
            item['saved'].close()
            self.pending.remove(item)
            self.timing['recovery'] += wallclock.perf_counter()-started

    def episode(self, episode, intact=None, *, task=None, world_id=None):
        if self.execution is None:raise PermissionError('run execution has no owner grant')
        self.execution.require(self.scope)
        if self.complete or episode != self.exposure['training_episodes']:raise ValueError('episodes must execute once in order')
        started = wallclock.perf_counter()
        nested_before = self.timing['qualification']+self.timing['recovery']
        task = task or rotation(episode, self.usable)
        if task not in self.usable:raise ValueError('INVALID: unusable task')
        world_id=training_episode(self.arm,self.seed,episode) if world_id is None else world_id
        assignment = permutation(world_id)
        self.medium.emit('episode_start', episode=episode, task=task, episode_seed=world_id, assignment=assignment)
        signals = defaultdict(list)
        episode_diagnostics=[]
        self._episode_diagnostics=episode_diagnostics
        self._episode_task=task
        self._episode_start=self.medium.step_index
        self._last_reward=[]
        with World(task, world_id, 'dev', library=self.library) as world:
            while not world.observe().done:
                if self.backend == 'native':
                    from .rev6_native import batch
                    count = min(self.batch_size, 200-self.medium.step_index % 200)
                    data = batch(self.medium, world, assignment, count,
                                 256000, self.perf_library)
                    self.batch_calls += 1
                    for row in data['steps']:
                        drives = [self._drive(d) for d in row['drives']]
                        self.drive_log.append({'step':row['step'],'episode':episode,
                                               'assignment':assignment,'sites':row['drives']})
                        for pending in self.pending:
                            pending['schedule'].append(deepcopy(drives))
                        self.exposure['training_steps'] += 1
                        for id, signal in row['event']['values']['defined_signals'].items():
                            signals[id].append(signal)
                        ordinary=sum(self.medium.role(int(id))=='element' for id in row['frame']['elements'])
                        episode_diagnostics.append(dict(step=row['step']-self._episode_start,defined_fraction=len(row['event']['values']['defined_signals'])/ordinary if ordinary else 0.))
                        if row['coverage'] is not None:
                            self.coverage_samples.append(row['coverage'])
                        if self.audit:
                            self.step_audit.append({'index':row['frame']['index'],'frame':row['frame'],
                                'death':row['death'],'novelty':row['novelty'],'covered':row['covered'],
                                'action':row['action']})
                    for store in (self.medium.events,self.drive_log,self.medium.diagnostics):
                        if hasattr(store,'flush'):
                            store.flush()
                    if data['boundary']:
                        obs = world.observe()  # last held observation; boundary world action is deferred
                        self.step_boundary(intact)
                        chosen = action(task, obs, self.medium.native, self.medium.time)
                        if self.audit:
                            self.step_audit[-1]['action'] = [chosen.angle,chosen.magnitude,chosen.choice]
                        world.step(chosen)
                    continue
                obs = world.observe()
                drives = bindings(task, obs, assignment, self.medium.time)
                self.drive_log.append({'step': self.medium.step_index, 'episode': episode,
                                       'assignment': assignment, 'sites': [[getattr(d, f) for f, _ in d._fields_] for d in drives]})
                for pending in self.pending:
                    pending['schedule'].append(deepcopy(drives))
                self.medium.integrate(drives)
                self.exposure['training_steps'] += 1
                defined=self.medium.adapt()
                for id, signal in defined.items():signals[id].append(signal)
                ordinary=sum(self.medium.role(e.id)=='element' for e in self.medium.native.elements)
                episode_diagnostics.append(dict(step=self.medium.step_index-self._episode_start-1,defined_fraction=len(defined)/ordinary if ordinary else 0.))
                coverage = self.medium.timers()
                if self.audit:
                    f = self.medium.frames[-1]
                    self.step_audit.append({'index':f.index,'frame':{'index':f.index,'time':f.time,
                        'elements':f.elements,'sites':f.sites,'neighbors':f.neighbors},
                        'death':dict(self.medium.death),'novelty':list(self.medium.novelty.values()),
                        'covered':coverage})
                active = [d.id for d in drives if d.strength > 0]
                if self.medium.step_index >= 256000 and active:
                    self.coverage_samples.append(sum(self.medium.covered(s) for s in active)/len(active))
                self.step_boundary(intact)
                chosen = action(task, obs, self.medium.native, self.medium.time)
                if self.audit:
                    self.step_audit[-1]['action'] = [chosen.angle,chosen.magnitude,chosen.choice]
                world.step(chosen)
            score = oriented(task, world.score())
        self.reward_update(task, score, signals)
        self.episode_log.append({'episode': episode, 'task':task,'score':score,'world_id':world_id,'signals':dict(signals),'step_diagnostics':episode_diagnostics,'reward_updates':self._last_reward})
        self.exposure['training_episodes'] += 1
        self.medium.emit('episode_end', episode=episode, task=task, score=score)
        self.timing['training'] += wallclock.perf_counter()-started-(self.timing['qualification']+self.timing['recovery']-nested_before)
        if episode+1 == self.episodes:
            if self.queue:
                self.queue.terminal(self.medium)
            self.complete = True

    @staticmethod
    def _drive(values):
        from ..medium.medium import Drive
        return Drive(*values)

    def step_boundary(self, intact=None):
        if self.medium.step_index % 200 == 0:
            self.birth_index[self.medium.step_index] = self.medium.growth(b1=not self.control,control=self.queue,intact_births=intact.births_at(self.medium.step_index) if intact else ())
            self.growth_counts.append((self.medium.time, len(self.medium.native)))
        if self.medium.step_index % 600 == 0 and self.medium.step_index+600 <= self.horizon and not self.control:
            self.qualify()
        self.admissions()

    def births_at(self, index):
        if index in self.birth_index:
            return list(self.birth_index[index])
        return [id for e in self.medium.events if e['rule'] == 'B1' and abs(e['time']-index*.1) < 1e-8 for id in e['ids']]

    def evaluate(self):
        started = wallclock.perf_counter()
        evaluator = Evaluator(self.rows,self.library,getattr(self,'backend','native'),execution=self.execution,scope=self.scope,arm=self.arm,k=self.seed,trace_dir=self.audit_dir/'evaluation' if self.audit_dir else None)
        for snapshot in self.snapshots[:20]:
            first, second = evaluator.evaluate(snapshot['template']), evaluator.evaluate(snapshot['template'], math.pi)
            self.evaluations.append({'type_id': snapshot['type_id'], 'per_task': first,
                                     'best_task': max(first, key=first.get), 'G5_D': covariance(first, second)})
        whole = template(self.medium.native, [e.id for e in self.medium.native.elements], self.medium.time)
        self.final_panel=evaluator.panel(whole) if self.policy=='intact' else {t:{'intact':[evaluator.episode(whole,t,e)['score'] for e in range(512,640)]} for t in evaluator.usable}
        self.final_competence={t:float(np.mean(v['intact'])) for t,v in self.final_panel.items()}
        self.exposure['evaluator_episodes'] = evaluator.episodes
        self.copy_instances = evaluator.instances
        self.timing['evaluation'] += wallclock.perf_counter()-started

    def report(self):
        late_result=late_count(self.growth_counts,self.medium.events)
        slope=late_result['slope'];rejected=late_result.get('rejected',False)
        protected=late_result.get('protected_over_budget',False)
        unique = {s['type_id']: s['template'] for s in self.snapshots}
        final = template(self.medium.native, [e.id for e in self.medium.native.elements], self.medium.time)
        pending = [{'check_time': item['index']*.1, 'state': item['state'],
                    'recorded_future_steps': len(item['schedule']),
                    'candidates': [{'ids': c['ids'], 'stats': c['stats'], 'template': c['template']}
                                   for c in item['check']['candidates']]} for item in self.pending]
        return {'pending_qualification': pending, 'final_template': final, 'final_type_id': template_hash(final), 'seed': self.seed, 'arm': 'reward' if self.reward else 'task_blind', 'control': self.control,
                'complete': self.complete, 'invalid': self.invalid, 'usable': self.usable,
                'clock': self.medium.time, 'exposure': self.exposure, 'timing': self.timing,
                'coverage': sum(self.coverage_samples)/len(self.coverage_samples) if self.coverage_samples else None,
                'eligible': len(self.coverage_samples), 'coverage_samples': self.coverage_samples,
                'growth_counts': self.growth_counts, 'slope': slope,
                'rejected': rejected,
                'protected_over_budget': protected,
                'snapshots': self.snapshots, 'evaluations': self.evaluations,
                'competence': self.final_competence,
                'late':late_result,'policy':self.policy,'keys':self.keys,'final_panel':getattr(self,'final_panel',None), 'control_queue':None if self.queue is None else dict(additions=self.queue.additions,slots=self.queue.slots,unmatched=self.queue.unmatched) if self.policy=='M' else dict(additions=self.queue.additions,retries=self.queue.retries,drops=self.queue.drops),
                'events': self.medium.events.receipt() if hasattr(self.medium.events,'receipt') else self.medium.events,
                'drive_schedule': self.drive_log.receipt() if hasattr(self.drive_log,'receipt') else self.drive_log,
                'episodes': self.episode_log,
                'endpoint_diagnostics':self.medium.diagnostics.receipt() if hasattr(self.medium.diagnostics,'receipt') else self.medium.diagnostics,
                'accounting': {'peak_learned_coefficients': 2*self.medium.peak,
                               'final_learned_coefficients': 2*len(self.medium.native),
                               'retained_position_phase_scalars': 3*len(self.medium.native),
                               'peak_position_phase_scalars': 3*self.medium.peak,
                               'unique_template_scalars': {k: 5*len(v['members']) for k, v in unique.items()},
                               'evaluation_copies': len(getattr(self, 'copy_instances', []))},
                'copy_instances': getattr(self, 'copy_instances', [])}

