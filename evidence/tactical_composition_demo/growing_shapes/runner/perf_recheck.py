"""Fixed, dev-only engineering cases and algebraic cost estimates. No panel CLI."""
from collections import defaultdict
from copy import deepcopy
import gzip
import hashlib
import json
import math
from pathlib import Path
import time
import ctypes as C
import subprocess
import numpy as np
from . import native, qualification as q
from .protocol import Calibration, TASKS, bindings, permutation, action, oriented
from .evaluator import copy_template
from .run import Run
from .perf_compare import Compare, medium_state, normalize, verify_hashes
from .test_perf_recheck import triangle, schedule
from ..world.world import World, Library
from ..medium.design_0h import DesignMedium, Frame, SITES

HERE = Path(__file__).resolve().parent


class Meter:
    def __init__(self,lib):
        self.seconds,self.calls = defaultdict(float),defaultdict(int)
        self.original = []
        for owner,names in ((native,('pack','decode','unpack')),
                            (lib,('gp_batch','gp_replay','gp_evaluate_episode','gp_future'))):
            for name in names:
                function = getattr(owner,name)
                def wrapped(*args,_function=function,_name=name,**kwargs):
                    started = time.perf_counter()
                    try: return _function(*args,**kwargs)
                    finally:
                        self.seconds[_name] += time.perf_counter()-started
                        self.calls[_name] += 1
                self.original.append((owner,name,function))
                setattr(owner,name,wrapped)
    def reset(self):
        self.seconds.clear();self.calls.clear()
    def report(self,total):
        # These measured boundary costs do not overlap.
        measured = sum(self.seconds.values())
        return {'seconds':dict(self.seconds),'calls':dict(self.calls),
                'other_python_seconds':max(0.,total-measured),
                'native_call_fraction':sum(v for k,v in self.seconds.items() if k.startswith('gp_'))/total}
    def close(self):
        for owner,name,function in self.original: setattr(owner,name,function)


def before_library(lib):
    """Explicit benchmark-only build of the merged batch, against current deps."""
    source = subprocess.check_output(['git','show','bc00869:evidence/tactical_composition_demo/growing_shapes/runner/perf.cpp'])
    if hashlib.sha256(source).hexdigest()!='c6e14cbef58128922fc95273ca1305d8dc5533e755fbce02042fce7e39882aac':
        raise RuntimeError('before-batch source identity mismatch')
    source_path=HERE/'_build/perf_before.cpp';source_path.write_bytes(source)
    manifest=json.loads((HERE/'_build/build.json').read_text())
    command=list(manifest['command'])
    command[command.index(str(HERE/'perf.cpp'))]=str(source_path)
    command[-1]=str(HERE/'_build'/('perf_before.dylib' if '.dylib' in command[-1] else 'perf_before.so'))
    command[1:1]=['-I',str(HERE)]
    subprocess.run(command,check=True)
    old=C.CDLL(command[-1])
    # Only the unchanged training ABI is used. No before recovery/eval symbols.
    old.gp_batch.restype=C.c_char_p;old.gp_batch.argtypes=lib.gp_batch.argtypes
    return old,{'base':'bc00869','source_sha256':hashlib.sha256(source).hexdigest(),
                'binary_sha256':hashlib.sha256(Path(command[-1]).read_bytes()).hexdigest(),'command':command}


def paired_runs(lib,meter,before):
    baseline = json.loads((HERE/'SMOKE.json').read_text())['frozen_validation']['calibration']
    comparison,result,raw = Compare(),[],[]
    cases = [(task,False,8 if task in ('perceive','choose') else 5) for task in TASKS]
    cases += [('perceive',True,5),('choose',True,5)]
    for number,(task,control,count) in enumerate(cases):
        rows = {task:Calibration(**baseline[task])}
        runs,timing = [],{}
        try:
            for backend in ('reference','before','native'):
                run = Run(105061+number,rows,reward=True,episodes=count,control=control,
                          backend='reference' if backend=='reference' else 'native',audit=True)
                runs.append(run)
                if backend!='reference':
                    run.perf_library=lib;meter.reset()
                    # Meter's wrapper must time the selected native ABI call.
                    original=lib.gp_batch
                    if backend=='before':lib.gp_batch=before.gp_batch
                # G0 fixtures provide requests at the same indexed boundaries.
                source = type('Source',(),{'births_at':lambda _,index:[index,index+1,index+2] if index==200 else []})() if control else None
                started = time.perf_counter()
                for episode in range(count): run.episode(episode,source)
                elapsed = time.perf_counter()-started
                timing[backend] = {'wall':elapsed,'stages':dict(run.timing),
                                   'steps':run.exposure['training_steps'],'batch_calls':run.batch_calls}
                if backend=='native': timing[backend]['profile']=meter.report(elapsed)
                if backend!='reference':lib.gp_batch=original
            reports = [r.report() for r in runs]
            for report in reports: verify_hashes(report);report.pop('timing')
            states = [medium_state(r.medium) for r in runs]
            for i in (1,2):
                comparison.check(reports[0],reports[i],task+'.report')
                comparison.check(runs[0].step_audit,runs[i].step_audit,task+'.every_endpoint')
                comparison.check(states[0],states[i],task+'.final_state')
                comparison.check(runs[0].rbar,runs[i].rbar,task+'.reward_baseline')
            raw.append({'task':task,'control':control,'reports':reports,
                        'endpoints':[r.step_audit for r in runs],'states':states})
            result.append({'task':task,'control':control,'seed':105061+number,'episodes':count,'timings':timing})
            print(f'PASS {task} control={control}: reference {timing["reference"]["wall"]:.3f}s, old batch {timing["before"]["wall"]:.3f}s -> new {timing["native"]["wall"]:.3f}s',flush=True)
        finally:
            for run in runs: run.close()
    return result,comparison.report(),raw


def stages(lib,meter):
    results,compare = {},Compare()
    for size in (4,24,64):
        m = triangle(size)
        try:
            check=q.start(m)
            # Rate the full N-member qualification input, including the 601xNxN
            # lock matrix, separately from the entrant-masked recovery fixture.
            whole=m.clone(events=False)
            try:
                whole.birth_steps={id:0 for id in whole.birth_steps}
                for k,f in enumerate(whole.frames):
                    rows=dict(f.elements)
                    rows.update({i:(10.*i,0.,f.time*math.pi) for i in range(3,size)})
                    whole.frames[k]=Frame(f.index,f.time,rows,f.sites,{id:() for id in rows})
                start=time.perf_counter();q.start(whole)
                saved=whole.clone(events=False)
                try:
                    # Same native serialization and endpoint-state materialization
                    # performed by Run.qualify, with no accumulated event copy.
                    state={'native':saved.native.save().hex(),'world_step':saved.step_index,
                           'birth_steps':dict(saved.birth_steps),'death_timers':dict(saved.death),
                           'novelty_timers':dict(saved.novelty),
                           'frames':[{'index':f.index,'time':f.time,'elements':f.elements,
                                      'sites':f.sites,'neighbors':f.neighbors} for f in saved.frames]}
                    assert len(state['frames'])==601
                finally:saved.close()
                qual=time.perf_counter()-start
            finally: whole.close()
            assert len(check['candidates'])==1
            ds = schedule(m)
            checks = [deepcopy(check),deepcopy(check)]
            timings,returns = {},[]
            for backend,c in zip(('reference','native'),checks):
                meter.reset();start = time.perf_counter()
                returns.append(q.finish(m,c,ds,np.random.default_rng(105070),backend=backend,lib=lib))
                elapsed=time.perf_counter()-start
                timings[backend]={'wall':elapsed,'seconds_per_candidate':elapsed,
                                  'profile':meter.report(elapsed) if backend=='native' else None}
            compare.check(checks[0],checks[1],f'recovery_N{size}')
            compare.check(returns[0],returns[1],f'admissions_N{size}')
            results[f'recovery_N{size}']={'qualification_seconds':qual,'timings':timings}
            print(f'PASS recovery N={size}: {timings["reference"]["wall"]:.3f}s -> {timings["native"]["wall"]:.3f}s',flush=True)
        finally: m.close()
    evaluation = []
    world_library=Library()
    for size in (3,24,64):
        for task in TASKS:
            for offset in (0.,math.pi):
                value = {'members':[[.05*(i%8),.05*(i//8),.05*i,math.pi,.5] for i in range(size)],
                         'binding':{'binding_rule':'episode_seed_permutation_v1','physical_sites':8,'slot_order':'per-task table, section 3'},
                         'constants_version':'DESIGN_0H_revision_5.1'}
                states,scores,timing = [],[],{}
                for backend in ('reference','native'):
                    meter.reset();start = time.perf_counter()
                    m=copy_template(value,offset)
                    try:
                        assignment=permutation(105071)
                        with World(task,105071,'dev',library=world_library) as w:
                            if backend=='native': native.evaluate_episode(m,w,assignment,lib)
                            else:
                                while not w.observe().done:
                                    obs=w.observe();m.integrate(bindings(task,obs,assignment,m.time));w.step(action(task,obs,m.native,m.time))
                            elapsed = time.perf_counter()-start
                            timing[backend]={'wall':elapsed,'profile':meter.report(elapsed) if backend=='native' else None}
                            scores.append(w.score().as_dict());states.append(m.native.save().hex())
                    finally: m.close()
                assert states[0]==states[1]
                compare.check(scores[0],scores[1],'frozen_copy_score',True)
                evaluation.append({'N':size,'task':task,'offset':offset,'timings':timing,'score':scores[0],
                                   'state_sha256':hashlib.sha256(bytes.fromhex(states[1])).hexdigest()})
        print(f'PASS evaluator individual dev episodes N={size}, all tasks, both offsets',flush=True)
    results['evaluation']=evaluation
    results['synthetic_training']=[]
    for size in (24,50):
        m=DesignMedium(105072)
        m.native.start_clock(60.)
        for i in range(size):m.add(((i%8)*2.5-8,(i//8)*2.5-8),math.pi*60+.03*i,gain=.5)
        m.step_index=600
        m.frames.clear()
        for k in range(601):
            rows={e.id:(e.x,e.y,math.pi*k*.1+.03*e.id) for e in m.native.elements}
            m.frames.append(Frame(k,k*.1,rows,{s:(*SITES[s],math.pi*k*.1,1.) for s in range(8)},
                                  {id:() for id in rows}))
        branches=[m,m.clone()];ds=schedule(m,200);timings={}
        try:
            for backend,branch in zip(('reference','native'),branches):
                meter.reset();start=time.perf_counter()
                if backend=='native':native.replay(branch,ds,adapt=True,lib=lib)
                else:
                    for drives in ds:branch.integrate(drives);branch.adapt();branch.timers()
                elapsed=time.perf_counter()-start
                timings[backend]={'wall':elapsed,'seconds_per_step':elapsed/200,
                                  'profile':meter.report(elapsed) if backend=='native' else None}
            compare.check(medium_state(branches[0]),medium_state(branches[1]),f'training_N{size}')
            results['synthetic_training'].append({'N':size,'steps':200,'timings':timings})
            print(f'PASS supplied-drive adapted training N={size}: {timings["reference"]["wall"]:.3f}s -> {timings["native"]["wall"]:.3f}s',flush=True)
        finally:
            for branch in branches:branch.close()
    return results,compare.report()


def estimate(training,stage):
    # Conditional rate model, deliberately never invokes development.execute_arm.
    native_seconds = sum(c['timings']['native']['stages']['training'] for c in training)
    steps=sum(c['timings']['native']['steps'] for c in training)
    rate=native_seconds/steps
    answer={'training_steps':10240000,'intact_qualification_checks':8512,
            'maximum_evaluator_episodes':344064,'measured_training_seconds_per_step':rate,
            'training_hours_at_observed_mix':10240000*rate/3600,'conditional_N':{}}
    for n in (24,64):
        recovery=stage[f'recovery_N{n}']
        qrate=recovery['qualification_seconds']
        rrate=recovery['timings']['native']['wall']
        episodes=[e['timings']['native']['wall'] for e in stage['evaluation'] if e['N']==n]
        erate=sum(episodes)/len(episodes)
        answer['conditional_N'][n]={'qualification_hours':8512*qrate/3600,
            'recovery_hours_per_mean_candidate_per_check':8512*rrate/3600,
            'evaluation_hours_at_cap':344064*erate/3600,
            'evaluation_seconds_per_episode':erate,
            'maximum_candidate_count':n//3,
            'total_hours_by_mean_candidates':{c:(10240000*rate+8512*qrate+8512*rrate*c+344064*erate)/3600
                                             for c in (0,1,3,n//3)}}
    answer['limits']='Observed small training mix; recovery/qualification static synthetic cohort; evaluation compact coherent geometry. Not an upper runtime bound. No disk/full-horizon workload measurement or parallel speedup claim.'
    answer['synthetic_training_hours_by_N']={t['N']:10240000*t['timings']['native']['seconds_per_step']/3600
                                            for t in stage['synthetic_training']}
    return answer


def main():
    lib=native.library();before,identity=before_library(lib);meter=Meter(lib)
    try:
        runs,comp,raw=paired_runs(lib,meter,before)
        stage,stage_comp=stages(lib,meter)
        result={'status':'PASS','label':'dev-only engineering; no recorded run or real validation panel',
                'declaration_sha256':hashlib.sha256((HERE/'PERF_RECHECK_COMPARISON.md').read_bytes()).hexdigest(),
                'cases':runs,'comparison':comp,'stages':stage,'stage_comparison':stage_comp,
                'projection':estimate(runs,stage),
                'build':json.loads((HERE/'_build/build.json').read_text()),'before_build':identity}
        with gzip.open(HERE/'PERF_RECHECK_EQUIVALENCE.json.gz','wt') as f:
            json.dump(normalize(raw),f,separators=(',',':'),allow_nan=False)
        result['audit_sha256']=hashlib.sha256((HERE/'PERF_RECHECK_EQUIVALENCE.json.gz').read_bytes()).hexdigest()
        (HERE/'PERF_RECHECK_CHECKS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    finally: meter.close()


if __name__=='__main__': main()
