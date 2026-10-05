"""Revision-5.1 orchestration. CLI permits only <=10 engineering episodes.

No section-10 run, projection, judging entropy or recorded-run CLI is provided.
Full implementation is available for later owner-authorized orchestration.
"""
import argparse
from collections import defaultdict
from copy import deepcopy
import json
import hashlib
import math
from pathlib import Path
import time as wallclock
import numpy as np
from ..medium.design_0h import DesignMedium
from ..world.world import Library, World
from .protocol import entropy, permutation, bindings, action, oriented, rotation, template, template_hash, covariance
from .evaluator import freeze, Evaluator
from .control import ControlQueue
from . import qualification


class Run:
    def __init__(self, seed, rows, reward=False, *, episodes=2000, control=False, library=None,
                 backend='reference', batch_size=200, audit=False):
        qualification.assert_frozen_source()
        design = Path(__file__).parents[2]/'DESIGN_0H.md'
        if hashlib.sha256(design.read_bytes()).hexdigest() != '39a630c3f4d440a6634538121773253443dcb15e8166406f36cde3727c119925':
            raise ValueError('INVALID: design revision 5.1 source mismatch')
        self.seed, self.rows, self.reward = seed, dict(rows), reward
        self.usable = tuple(t for t, c in rows.items() if c.usable)
        if not self.usable:
            raise ValueError('INVALID: zero usable tasks')
        if not isinstance(episodes, int) or episodes < 1:
            raise ValueError('positive episode count required')
        self.episodes, self.control = episodes, control
        if backend not in ('reference', 'native') or not isinstance(batch_size,int) or not 1 <= batch_size <= 200:
            raise ValueError('select reference/native and batch size 1..200')
        self.backend, self.batch_size, self.audit = backend, batch_size, audit
        self.step_audit = []
        self.batch_calls = 0
        if backend == 'native':
            from .native import library as perf_library
            self.perf_library = perf_library()
        self.library = library or Library()
        self.medium = DesignMedium(seed)
        rng = np.random.default_rng(entropy(seed, 'initial'))
        for _ in range(24):
            angle, radius = rng.uniform(0, 2*math.pi), 5*math.sqrt(rng.uniform())
            self.medium.add((radius*math.cos(angle), radius*math.sin(angle)), rng.uniform(0, 2*math.pi),
                            math.pi*(1+rng.uniform(-.1, .1)), .5, rule='INITIAL')
        self.medium.frames.clear()
        self.medium.record()
        self.rbar = .5
        self.pending = []
        self.snapshots = []
        self.group_hashes = defaultdict(set)
        self.coverage_samples = []
        self.growth_counts = []
        self.drive_log = []
        self.episode_log = []
        self.queue = ControlQueue(seed) if control else None
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

    def reward_update(self, task, score, signals):
        if not self.reward:
            return
        reward = float(np.clip(self.rows[task].normalize(score), 0, 1))
        for e in self.medium.native.elements:
            eligibility = sum(signals[e.id])/len(signals[e.id]) if signals[e.id] else 0.
            before = self.medium.native.gain(e.id)
            after = float(np.clip(before+.5*(reward-self.rbar)*eligibility, 0, 2))
            self.medium.native.set_gain(e.id, after)
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
        saved = self.medium.clone()
        self.pending.append({'check': check, 'saved': saved, 'state': {'native': saved.native.save().hex(),
                             'world_step': saved.step_index, 'birth_steps': dict(saved.birth_steps),
                             'death_timers': dict(saved.death), 'novelty_timers': dict(saved.novelty),
                             'frames': [{'index': f.index, 'time': f.time, 'elements': f.elements,
                                         'sites': f.sites, 'neighbors': f.neighbors} for f in saved.frames]},
                             'index': self.medium.step_index, 'schedule': []})
        self.timing['qualification'] += wallclock.perf_counter()-started

    def admissions(self):
        for item in list(self.pending):
            if len(item['schedule']) != 600:
                continue
            started = wallclock.perf_counter()
            candidates, simulated = qualification.finish(item['saved'], item['check'], item['schedule'],
                np.random.default_rng(entropy(self.seed, f"kick:{item['index']}")))
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

    def episode(self, episode, intact=None):
        started = wallclock.perf_counter()
        nested_before = self.timing['qualification']+self.timing['recovery']
        task = rotation(episode, self.usable)
        assignment = permutation(episode)
        self.medium.emit('episode_start', episode=episode, task=task, episode_seed=episode, assignment=assignment)
        signals = defaultdict(list)
        with World(task, episode, 'dev', library=self.library) as world:
            while not world.observe().done:
                if self.backend == 'native':
                    from .native import batch
                    count = min(self.batch_size, 200-self.medium.step_index % 200)
                    data = batch(self.medium, world, assignment, count,
                                 .8*self.episodes*160, self.perf_library)
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
                        if row['coverage'] is not None:
                            self.coverage_samples.append(row['coverage'])
                        if self.audit:
                            self.step_audit.append({'index':row['frame']['index'],'frame':row['frame'],
                                'death':row['death'],'novelty':row['novelty'],'covered':row['covered'],
                                'action':row['action']})
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
                for id, signal in self.medium.adapt().items():
                    signals[id].append(signal)
                coverage = self.medium.timers()
                if self.audit:
                    f = self.medium.frames[-1]
                    self.step_audit.append({'index':f.index,'frame':{'index':f.index,'time':f.time,
                        'elements':f.elements,'sites':f.sites,'neighbors':f.neighbors},
                        'death':dict(self.medium.death),'novelty':list(self.medium.novelty.values()),
                        'covered':coverage})
                active = [d.id for d in drives if d.strength > 0]
                if self.medium.step_index >= .8*self.episodes*160 and active:
                    self.coverage_samples.append(sum(self.medium.covered(s) for s in active)/len(active))
                self.step_boundary(intact)
                chosen = action(task, obs, self.medium.native, self.medium.time)
                if self.audit:
                    self.step_audit[-1]['action'] = [chosen.angle,chosen.magnitude,chosen.choice]
                world.step(chosen)
            score = oriented(task, world.score())
        self.reward_update(task, score, signals)
        self.episode_log.append({'episode': episode, 'task': task, 'score': score})
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
            self.medium.growth(births=not self.control)
            self.growth_counts.append((self.medium.time/16, len(self.medium.native)))
            if self.control:
                source = intact.births_at(self.medium.step_index) if intact else []
                self.queue.check(self.medium, source)
        if self.medium.step_index % 600 == 0 and self.medium.step_index+600 <= self.episodes*160 and not self.control:
            self.qualify()
        self.admissions()

    def births_at(self, index):
        return [id for e in self.medium.events if e['rule'] == 'B1' and abs(e['time']-index*.1) < 1e-8 for id in e['ids']]

    def evaluate(self):
        started = wallclock.perf_counter()
        evaluator = Evaluator(self.rows, self.library)
        for snapshot in self.snapshots[:20]:
            first, second = evaluator.evaluate(snapshot['template']), evaluator.evaluate(snapshot['template'], math.pi)
            self.evaluations.append({'type_id': snapshot['type_id'], 'per_task': first,
                                     'best_task': max(first, key=first.get), 'G5_D': covariance(first, second)})
        whole = template(self.medium.native, [e.id for e in self.medium.native.elements], self.medium.time)
        self.final_competence = evaluator.evaluate(whole)
        self.exposure['evaluator_episodes'] = evaluator.episodes
        self.copy_instances = evaluator.instances
        self.timing['evaluation'] += wallclock.perf_counter()-started

    def report(self):
        late = [(ep, n) for ep, n in self.growth_counts if ep >= .8*self.episodes]
        slope = float(np.polyfit(*np.array(late).T, 1)[0]*100) if len(late) >= 2 else None
        late_events = [e for e in self.medium.events if e['time'] >= .8*self.episodes*16]
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
                'rejected': any(e['rule'] == 'B1_rejected' for e in late_events),
                'protected_over_budget': any(e['rule'] == 'protected_over_budget' for e in late_events),
                'snapshots': self.snapshots, 'evaluations': self.evaluations,
                'competence': self.final_competence,
                'control_queue': None if self.queue is None else dict(additions=self.queue.additions, retries=self.queue.retries, drops=self.queue.drops),
                'events': self.medium.events, 'drive_schedule': self.drive_log, 'episodes': self.episode_log,
                'accounting': {'peak_learned_coefficients': 2*self.medium.peak,
                               'final_learned_coefficients': 2*len(self.medium.native),
                               'retained_position_phase_scalars': 3*len(self.medium.native),
                               'peak_position_phase_scalars': 3*self.medium.peak,
                               'unique_template_scalars': {k: 5*len(v['members']) for k, v in unique.items()},
                               'evaluation_copies': len(getattr(self, 'copy_instances', []))},
                'copy_instances': getattr(self, 'copy_instances', [])}


def smoke(seed, rows, episodes=8, *, backend='reference'):
    if not 1 <= episodes <= 10:
        raise ValueError('engineering smoke is capped at ten episodes')
    run = Run(seed, rows, episodes=episodes, backend=backend)
    try:
        for episode in range(episodes):
            run.episode(episode)
        report = run.report()
        report['label'] = 'engineering-only; not development evidence'
        report['readouts'] = 'NOT_RUN: smoke is not the section-10 protocol or evaluator panel'
        return report
    except Exception as error:
        run.invalid = f'{type(error).__name__}: {error}'
        report = run.report()
        report['label'] = 'engineering-only; not development evidence'
        report['readouts'] = 'INVALID'
        return report
    finally:
        run.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke', action='store_true', required=True)
    parser.add_argument('--seed', type=int, default=105051)
    parser.add_argument('--episodes', type=int, default=8)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--backend', choices=('reference','native'), default='reference')
    args = parser.parse_args()
    if not 1 <= args.episodes <= 10:
        parser.error('only 1..10 engineering episodes are authorized')
    rows, frozen = freeze()
    result = {'frozen_validation': frozen, 'smoke': smoke(args.seed, rows, args.episodes, backend=args.backend)}
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
