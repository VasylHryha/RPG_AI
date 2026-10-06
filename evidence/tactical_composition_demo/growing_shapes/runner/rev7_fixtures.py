"""Reviewed-gated N1/F1–F9 harness. Default CLI is construct-only and cannot integrate."""
from contextlib import ExitStack
import argparse
import json
import math
from pathlib import Path
import numpy as np
from ..medium.rev7_design import Rev7Medium, R_STAR, reach
from ..medium.medium import Drive
from ..medium.design_0h import wrap
from .rev7_protocol import generator, seed, template, copy_template, bindings, permutation, action, relay
from .rev7_run import Run
from .rev7_evaluator import Evaluator, reused_calibration
from .rev7_execution import Execution
from .rev7_config import CONFIG,N1_RECIPES,N1_SADDLE_DIAGNOSTIC,CONFIG_SHA256,PRODUCTION_H,REFINEMENT_H,WORLD_DT,F1D_SCALES

CHECKPOINTS=(40,45,50)
F6_PAIRS=tuple((10000788+j,10000798+j) for j in range(10))
F5_PAIRS=tuple((10000768+j,10000778+j) for j in range(10))
F8_WORLD_IDS=tuple(12100000+e for e in range(40))


def scaffold(kind,alpha=1.,*,backend="native",h=PRODUCTION_H):
    """Construction only. No world object, integration, or fixture statistic."""
    m=Rev7Medium(frozen=True,backend=backend,h=h)
    if kind=='F1a':positions=[3.2,2.644]
    elif kind in ('F1b','F1d'):positions=[3.2,2.644,2.088,1.532]
    elif kind=='F1c':positions=[3.2]+[3.2-R_STAR*j for j in range(1,6)]+[0.]
    elif kind=='F2b':positions=[3.2-R_STAR*j for j in range(3)]+[-3.]
    elif kind=='F2a':positions=[]
    elif kind=='F3':positions=[4.-R_STAR,4.]
    elif kind=='F4':positions=[3.7,3.444]
    else:m.close();raise ValueError('unknown scaffold')
    for j,x in enumerate(positions):
        output=j==len(positions)-1
        m.add((x,0),alpha if output and kind=='F2b' else 0.,math.pi,1. if j==0 or output else 0.,rule='FIXTURE_INITIAL',role='output' if output else 'element')
    m.frames.clear();m.record()
    return m


def literal_start():
    m=Rev7Medium(growth_rng=generator('growth/F5/ii/intact'))
    for j in range(6):m.add((3.1+R_STAR*math.cos(math.pi*j/3),R_STAR*math.sin(math.pi*j/3)),0.,gain=1.,rule='FIXTURE_INITIAL')
    m.add((-.5,0),0.,gain=1.,rule='FIXTURE_INITIAL',role='output')
    m.frames.clear();m.record();return m


def keys(start,policy='intact'):
    result=dict(growth=f'growth/F5/{start}/{policy}',recovery=f'recovery/F5/{start}/{policy}')
    if start=='i':result['medium']='medium/F5/i'
    if policy=='M':result['matched']='matched/F5/i'
    return result


def construct_only():
    """Allowed dry check. F6/F8 hold dependency recipes, never fabricate grown states."""
    rows,_=reused_calibration();out={}
    for name in ('F1a','F1b','F1c','F2a','F2b','F3','F4'):
        m=scaffold(name)
        try:out[name]=dict(members=template(m.native,[e.id for e in m.native.elements],0,h=m.h)['members'],world_steps=0)
        finally:m.close()
    for name,start,policy in [('F5i','i','intact'),('F5ii','ii','intact'),('F7','i','M')]:
        initial=literal_start() if start=='ii' else None
        run=Run(0,rows,episodes=50,policy=policy,keys=keys(start,policy),initial=initial,scope='fixtures')
        try:out[name]=dict(members=template(run.medium.native,[e.id for e in run.medium.native.elements],0,h=run.medium.h)['members'],world_steps=run.medium.step_index,keys=run.keys)
        finally:run.close();initial.close() if initial else None
    out['N1']=dict(recipes=N1_RECIPES,configuration_sha256=CONFIG_SHA256,world_steps=0,deterministic_no_entropy=True)
    out['F1d']=dict(scaffold='F1b',phase_scales=list(F1D_SCALES),h=PRODUCTION_H,world_steps=0,deterministic_no_entropy=True)
    out['F6']=dict(dependency='six F5 checkpoints; no substitute checkpoint constructed',starts=['i','ii'],checkpoints=CHECKPOINTS,pairs=F6_PAIRS,copies=140,checkpoint_copies=120,baseline_copies=20,baseline_unique_recipient_episodes=10,baseline_minimum_defined_unique_episodes=5,baseline_modes=['single_oscillator','sample_and_hold'],growth=False,adaptation=False,recovery=False)
    out['F9']=dict(cases=list(F9_CASES),seeds={name:seed(f'medium/F9/{name}') for name in F9_CASES},world_ids=list(range(10000808,10000812)),world_steps=0,status='DESCRIPTIVE_DECODER_ONLY_SYNTHETIC_OBSERVATIONS')
    out['F8']=dict(dependency='live F5(i) after episode 50; histories/timers/clock retained',episodes=F8_WORLD_IDS,tasks=['move']*20+['remember_static']*20,keys=['growth/F8/reward','recovery/F8/reward'],reward_baseline=.5)
    return dict(status='CONSTRUCT_ONLY',integrated_world_steps=0,fixture_execution='NOT_RUN',recipes=out)


def finite_record(value):
    # Numeric failure is INVALID, never a failed gate or a replaced episode.
    json.dumps(value,allow_nan=False)
    return value


def f6_baselines(evaluator,value):
    """Checkpoint-independent baselines, one fresh copy per unique recipient."""
    rows={mode:[] for mode in ('single_oscillator','sample_and_hold')}
    for recipient in sorted({recipient for recipient,_ in F6_PAIRS}):
        for mode in rows:
            row=evaluator.episode(value,'remember_static',recipient,mode=mode)
            if row['status']!='evaluated' or len(row['decisions'])!=160:raise ValueError('INVALID: missing F6 baseline records')
            rows[mode].append(row)
    return rows


def last_visible_angle(row):
    ds=row['decisions'][39]['drives'];drive=next(d for d in ds if d[5]>0)
    return float(wrap(drive[3]-math.pi*3.9))


def memory_summary(encoded,episodes,*,unique_episodes=False):
    """JS circular correlation, 18.5 mean/R disposition, with raw beta/R retained."""
    records=[];pairs=[];seen=set()
    if len(encoded)!=len(episodes):raise ValueError('memory summary length mismatch')
    for angle,row in zip(encoded,episodes):
        if unique_episodes:
            episode=row['instance']['world_episode']
            if episode in seen:continue
            seen.add(episode)
        hidden=row['decisions'][40:160]
        beta=[d['angle'] for d in hidden]
        present=bool(hidden) and all(d['has_output'] for d in hidden)
        z=np.exp(1j*np.asarray(beta)).mean() if beta else 0j;resultant=float(abs(z))
        mean=float(np.angle(z)) if present and resultant>=.05 else None
        records.append(dict(encoded=angle,beta=beta,resultant=resultant,resultant_trace=[float(abs(np.exp(1j*np.asarray(beta[:j])).mean())) for j in range(1,len(beta)+1)],mean=mean,
                            reason=None if mean is not None else 'no_output' if not present else 'degenerate_resultant'))
        if unique_episodes:records[-1]['world_episode']=episode
        if mean is not None and math.isfinite(angle) and math.isfinite(mean):pairs.append((angle,mean))
    if len(pairs)<5:return dict(correlation=None,reason='fewer_than_five_defined_pairs',defined_pairs=len(pairs),unique_episode_count=len(seen) if unique_episodes else None,minimum_unit='unique_recipient_episode' if unique_episodes else 'checkpoint_episode',episodes=records)
    a,b=np.asarray(pairs).T
    # JS requires defined marginal directions as well as nonzero sine variance.
    za,zb=np.exp(1j*a).mean(),np.exp(1j*b).mean()
    if abs(za)<1e-12 or abs(zb)<1e-12:return dict(correlation=None,reason='undefined_marginal_mean',defined_pairs=len(pairs),unique_episode_count=len(seen) if unique_episodes else None,minimum_unit='unique_recipient_episode' if unique_episodes else 'checkpoint_episode',episodes=records)
    x=np.sin(a-np.angle(za));y=np.sin(b-np.angle(zb));den=math.sqrt(float(np.sum(x*x)*np.sum(y*y)))
    if den<=1e-14:return dict(correlation=None,reason='zero_circular_variance',defined_pairs=len(pairs),unique_episode_count=len(seen) if unique_episodes else None,minimum_unit='unique_recipient_episode' if unique_episodes else 'checkpoint_episode',episodes=records)
    return dict(correlation=float(np.sum(x*y)/den),reason=None,defined_pairs=len(pairs),unique_episode_count=len(seen) if unique_episodes else None,minimum_unit='unique_recipient_episode' if unique_episodes else 'checkpoint_episode',episodes=records)


F9_CASES={'zero_demand':(0.,2.,2.),'approach':(.4,4.,2.),'retreat_inside_range':(.4,1.,2.),'stop':(.4,2.,2.)}


def step_response(records):
    window=[r for r in records if 8<r['time']<=16+1e-9]
    good=[abs(float(wrap(r['beta']-math.pi/2)))<=.3 for r in window]
    first=next((j for j,yes in enumerate(good) if yes),None)
    complete=len(window)==80 and abs(window[-1]['time']-16)<1e-9
    sustained=complete and first is not None and all(good[first:])
    return dict(response_pass=bool(sustained),first_entry_time=None if first is None else window[first]['time'],
        delay=None if first is None else window[first]['time']-8,deadline_sample_present=complete,
        continuous_from_first_entry=bool(sustained),criterion='all world steps from first entry through t=16 inclusive within 0.3 rad')


def assay_parity(native,reference):
    if native['status']!='evaluated' or reference['status']!='evaluated':raise ValueError('INVALID: assay parity missing result')
    a,b=native['decisions'],reference['decisions']
    if len(a)!=len(b):raise ValueError('INVALID: assay parity missing decisions')
    maximum=0.
    for x,y in zip(a,b):
        error=abs(float(wrap(x['angle']-y['angle'])));maximum=max(maximum,error)
        if not math.isfinite(error) or error>1e-12 or x['magnitude']!=y['magnitude'] or x['choice']!=y['choice'] or x['paths']!=y['paths'] or x['has_output']!=y['has_output']:
            raise ValueError('INVALID: native/reference assay parity mismatch')
    return dict(status='MATCH',decisions=len(a),maximum_wrapped_angle_error=maximum,tolerance=1e-12)


class Harness:
    def __init__(self,execution=None,backend='native'):
        self.execution=execution or Execution();self.backend=backend
        self.rows,self.calibration=reused_calibration()
        self.checkpoints={};self.live=None;self.intact=None
        self.results={};self.evaluator=None;self.identity_snapshot=None

    def require(self,stage=None):
        self.execution.require('fixtures')
        if stage and stage!='N1' and self.results.get('N1',{}).get('verdict')!='PASS':raise PermissionError('N1 must pass before later fixtures')
        if stage in ('F5','F6','F7','F8','F9') and any(self.results.get(n,{}).get('verdict')!='PASS' for n in ('F1','F2','F3','F4')):raise PermissionError('F1-F4 must pass before later fixtures')
        if stage in ('F6','F7','F8','F9') and self.results.get('F5',{}).get('verdict')!='PASS':raise PermissionError('F5 failed or not measured')
        if stage in ('F8','F9') and self.results.get('F7',{}).get('verdict')!='PASS':raise PermissionError('F7 failed or not measured')
        if self.identity_snapshot is None:self.identity_snapshot=self.execution.snapshot('fixtures')

    def close(self):
        if self.intact:self.intact.close();self.intact=None
        if self.live:self.live.close();self.live=None
        for m in self.checkpoints.values():m.close()
        self.checkpoints.clear()

    def driven(self,m,angle):
        return [Drive(0,4,0,math.pi*m.time+angle,math.pi,2,1,3)]

    def N1(self):
        self.require('N1');cases={}
        for name,recipe in N1_RECIPES.items():
            runs=[]
            for h in (PRODUCTION_H,REFINEMENT_H):
                m=Rev7Medium(frozen=True,h=h,backend=self.backend);records=[]
                try:
                    for x,y,phase,rate,gain,role in recipe['members']:m.add((x,y),phase,rate,gain,role=role,rule='N1_INITIAL')
                    for step in range(round(recipe['seconds']/WORLD_DT)):
                        drives=[Drive(id,x,y,math.pi*m.time+(math.pi/2 if recipe['step'] and step>=80 else angle),math.pi,k,1,3) for id,(x,y,k,angle) in enumerate(recipe['sites'])]
                        diag=m.integrate(drives);g=m.influence();es=m.native.elements
                        records.append(dict(time=m.time,phases=[e.phase-math.pi*m.time for e in es],positions=[[e.x,e.y] for e in es],free=[m.role(e.id)!='output' for e in es],phase_topology=m.phase_topology(),motion_topology=diag['motion_neighbors'],excursion=diag['excursion'],used_pairs=sorted({tuple(sorted((target,source))) for target,sources in m.phase_topology().items() for source in sources}),pin_invariant=all((e.x,e.y)==m.native.pin(e.id)[1] for e in es if m.role(e.id)=='output'),minimum_distances=minimum_distances(m)))
                    runs.append(records)
                finally:m.close()
            cases[name]=n1_case_result(name,runs[0],runs[1])
        return dict(verdict=n1_verdict(cases),cases=cases,configuration_sha256=CONFIG_SHA256,deterministic_no_entropy=True)

    def F1d(self):
        self.require('F1');runs={}
        for scale in F1D_SCALES:
            m=scaffold('F1d',backend=self.backend);m.native.phase_scale(scale);records=[]
            try:
                for step in range(1600):
                    diag=m.integrate(self.driven(m,0. if step<80 else math.pi/2));g=m.influence()
                    records.append(dict(time=m.time,beta=float(wrap(m.native.output()[1]-math.pi*m.time)),effective_roots={s:sorted(v) for s,v in m.strong_influence().roots.items()},paths=diag['paths'],exposure=diag['exposure'],phase_topology=m.phase_topology(),motion_topology=diag['motion_neighbors'],positions={e.id:[e.x,e.y] for e in m.native.elements},excursion=diag['excursion']))
                response=step_response(records)
                runs[str(scale)]=dict(phase_scale=scale,h=m.h,substeps=round(WORLD_DT/m.h),records=records,**response,deadline_error=abs(float(wrap(records[159]['beta']-math.pi/2))))
            finally:m.close()
        return dict(verdict='DESCRIPTIVE',runs=runs,deterministic_no_entropy=True)

    def F1(self):
        self.require("F1");result={}
        for name in ('F1a','F1b','F1c'):
            m=scaffold(name,backend=self.backend);records=[]
            try:
                for step in range(1600):
                    ds=self.driven(m,0. if step<80 else math.pi/2)
                    diag=m.integrate(ds);g=m.influence();outputs=g.outputs
                    beta=float(wrap(m.native.output()[1]-math.pi*m.time))
                    elements={e.id:e for e in m.native.elements}
                    weights={id:{j:math.exp(-math.hypot(elements[id].x-elements[j].x,elements[id].y-elements[j].y)**2)/max(1,len(sources)) for j in sources} for id,sources in g.incoming.items()}
                    records.append(dict(time=m.time,beta=beta,path=bool(m.strong_influence().forward()&outputs),neighbors=m.phase_topology(),weights=weights,exposure=diag['exposure'],excursion=diag['excursion'],motion_neighbors=diag['motion_neighbors'],positions={id:[e.x,e.y] for id,e in elements.items()},source_site_distance=math.hypot(elements[0].x-4,elements[0].y),drive_access=any(d.strength>0 and math.hypot(elements[0].x-d.x,elements[0].y-d.y)<d.reach for d in ds),pin_invariant=all(e.x==m.native.pin(e.id)[1][0] and e.y==m.native.pin(e.id)[1][1] for e in elements.values() if m.role(e.id)=='output'),minimum_distances=minimum_distances(m),ordinary_span=span(m)))
                if not all(r['pin_invariant'] for r in records):raise ValueError('INVALID: fixture pin moved')
                response=step_response(records)
                persistence=sum(r['path'] for r in records)/1600
                if name=='F1c':
                    response=f1c_response(records)
                result[name]=dict(verdict='PASS' if response['response_pass'] and persistence>=.8 else 'FAIL',**response,path_exposure=persistence,records=records)
            finally:m.close()
        result['F1d']=self.F1d()
        return dict(verdict='PASS' if all(result[n]['verdict']=='PASS' for n in ('F1a','F1b','F1c')) else 'FAIL',configurations=result)

    def F2(self):
        self.require("F2");empty=scaffold('F2a')
        try:default=action('perceive',None,empty.native,0);empty_ok=default.angle==0 and default.magnitude==0 and not any(empty.endpoint_diagnostics()['paths'])
        finally:empty.close()
        streams=[];paths=[]
        for stepped in (False,True):
            m=scaffold('F2b')
            try:
                stream=[];exposure=[]
                for j in range(160):
                    m.integrate(self.driven(m,math.pi/2 if stepped and j>=80 else 0))
                    stream.append(m.native.output()[1]);exposure.append(m.influence().path(0))
                streams.append(np.asarray(stream));paths.append(exposure)
            finally:m.close()
        identical=streams[0].tobytes()==streams[1].tobytes()
        return dict(verdict='PASS' if empty_ok and identical and not any(paths[0]+paths[1]) else 'FAIL',empty_default=empty_ok,bitwise_identical=identical,paths=paths,phases=[v.tolist() for v in streams],horizon_seconds=16)

    def F3(self):
        self.require("F3");m=scaffold('F3')
        try:
            output=next(e for e in m.native.elements if m.role(e.id)=='output')
            m.native.set_element(output.id,4,0,output.phase,output.rate)
            m.native.set_drives(self.driven(m,math.pi/2));traces=[]
            for _ in range(round(WORLD_DT/m.h)):m.native.step(m.h);traces.append(m.native.stage_terms())
            ix=[e.id for e in m.native.elements].index(output.id)
            ok=all(float(stage[ix][0]).hex()==float(0).hex() for trace in traces for stage in trace)
            return dict(verdict='PASS' if ok else 'FAIL',stages=traces)
        finally:m.close()

    def F4(self):
        self.require("F4");m=scaffold('F4')
        try:
            ids=[e.id for e in m.native.elements];out=next(e.id for e in m.native.elements if m.role(e.id)=='output')
            m.native.set_element(ids[0],3.7,0,1.,math.pi)
            m.native.lesions([out]);m.native.set_drives(self.driven(m,1.2));traces=[]
            for _ in range(round(WORLD_DT/m.h)):m.native.step(m.h);traces.append(m.native.stage_terms())
            ix=ids.index(out);zero=all(stage[ix][1]==0 for trace in traces for stage in trace)
            ds=[Drive(0,4,0,.4,math.pi,1.,1,3),Drive(2,0,4,1.1,math.pi,2.,1,3)]
            site=relay('perceive',None,ds,0,'site0');oracle=relay('perceive',None,ds,0,'oracle')
            relays=site.angle==float(wrap(.4)) and oracle.angle==float(wrap(1.1))
            value=template(m.native,ids,0.,h=m.h)
            native=Evaluator(self.rows,backend='native',execution=self.execution,scope='fixtures')
            reference=Evaluator(self.rows,backend='reference',execution=self.execution,scope='fixtures')
            parity={}
            for mode in ('intact','donor','output_channel','site0','oracle'):
                options=dict(mode=mode,donor=10000778) if mode=='donor' else dict(mode=mode)
                a=native.episode(value,'perceive',10000768,**options);b=reference.episode(value,'perceive',10000768,**options)
                parity[mode]=dict(**assay_parity(a,b),native=a,reference=b)
            return dict(verdict='PASS' if zero and relays else 'FAIL',stages=traces,site0=site.angle,oracle=oracle.angle,assay_parity=parity)
        finally:m.close()

    def F5(self):
        self.require("F5");result={}
        self.evaluator=Evaluator(self.rows,backend=self.backend,execution=self.execution,scope='fixtures')
        for start in ('i','ii'):
            initial=literal_start() if start=='ii' else None
            run=Run(0,self.rows,episodes=50,keys=keys(start),initial=initial,backend=self.backend,execution=self.execution,scope='fixtures')
            if initial:initial.close()
            try:
                for e in range(50):
                    run.episode(e,task='perceive',world_id=12000000+e)
                    if e+1 in CHECKPOINTS:self.checkpoints[start,e+1]=run.medium.clone(events=False)
                episodes=[];A=[];B=[];E=[]
                for checkpoint in CHECKPOINTS:
                    m=self.checkpoints[start,checkpoint];value=template(m.native,[e.id for e in m.native.elements],m.time,h=m.h)
                    for recipient,donor in F5_PAIRS:
                        own=self.evaluator.episode(value,'perceive',recipient)
                        other=self.evaluator.episode(value,'perceive',recipient,mode='donor',donor=donor)
                        lesion=self.evaluator.episode(value,'perceive',recipient,mode='output_channel')
                        if any(len(r['decisions'])!=160 for r in (own,other,lesion)):raise ValueError('missing F5 decision record')
                        absent=not any(row[5]=='output' for row in value['members'])
                        A.append(0. if absent else float(np.mean([abs(float(wrap(a['angle']-b['angle']))) for a,b in zip(own['decisions'],other['decisions'])])))
                        B.append(0. if absent else float(np.mean([abs(float(wrap(a['angle']-b['angle']))) for a,b in zip(own['decisions'],lesion['decisions'])])))
                        E.append(np.mean([r['paths'] for r in own['decisions']],axis=0).tolist())
                        episodes.append(dict(checkpoint=checkpoint,recipient=recipient,donor=donor,own=own,other=other,lesion=lesion))
                events=list(run.medium.events);out_birth=any(e['rule']=='B-out' for e in events);path_birth=any(e['rule']=='B-path' for e in events)
                meanA,meanB=float(np.mean(A)),float(np.mean(B));meanE=np.mean(E,axis=0).tolist()
                specific=out_birth if start=='i' else path_birth
                result[start]=dict(identity_snapshot=run.identity_snapshot,verdict='PASS' if specific and max(meanE)>=.5 and meanA>=.3 and meanB>=.3 else 'FAIL',A=meanA,B=meanB,E=meanE,B_out=out_birth,B_path=path_birth,episodes=episodes,events=events,active_site0_steps=sum(any(d[0]==0 and d[5]>0 for d in row['sites']) for row in run.drive_log))
                from .rev7_reporting import f5_qualification_summary,b_path_waiting
                result[start]['B_path_waiting']=b_path_waiting(events)
                result[start]['qualification_validity']=f5_qualification_summary(events,run.medium.diagnostics,CHECKPOINTS)
                result[start]['estimator_validity']=run.medium.estimator_validity()
                if start=='i':self.intact=run;self.live=run.medium.clone(events=False)
            finally:
                if start!='i' or self.intact is not run:run.close()
        return dict(verdict='PASS' if all(r['verdict']=='PASS' for r in result.values()) else 'FAIL',starts=result)

    def F6(self):
        self.require("F6");own=[];donor_rows=[];encoded=[];donor_encoded=[]
        first=self.checkpoints['i',CHECKPOINTS[0]]
        baselines=f6_baselines(self.evaluator,template(first.native,[e.id for e in first.native.elements],first.time,h=first.h))
        for start in ('i','ii'):
            for checkpoint in CHECKPOINTS:
                m=self.checkpoints[start,checkpoint];value=template(m.native,[e.id for e in m.native.elements],m.time,h=m.h)
                for recipient,donor in F6_PAIRS:
                    a=self.evaluator.episode(value,'remember_static',recipient)
                    b=self.evaluator.episode(value,'remember_static',recipient,mode='donor',donor=donor)
                    if len(a['decisions'])!=160 or len(b['decisions'])!=160:raise ValueError('missing F6 records')
                    encoded.append(last_visible_angle(a));donor_encoded.append(last_visible_angle(b));own.append(a);donor_rows.append(b)
        return dict(verdict='DESCRIPTIVE',baselines={mode:memory_summary([last_visible_angle(r) for r in rows],rows,unique_episodes=True) for mode,rows in baselines.items()},encoding_retention={mode:[r['memory_windows'] for r in rows] for mode,rows in dict(own=own,donor=donor_rows,**baselines).items()},own=memory_summary(encoded,own),donor=memory_summary(encoded,donor_rows),donor_encoded=donor_encoded,encoded_reference='recipient last-visible angle for both comparisons',records=dict(own=own,donor=donor_rows,baselines=baselines))

    def F7(self):
        self.require("F7");run=Run(0,self.rows,episodes=50,policy='M',keys=keys('i','M'),backend=self.backend,execution=self.execution,scope='fixtures')
        try:
            for e in range(50):run.episode(e,self.intact,task='perceive',world_id=12000000+e)
            slots=run.queue.slots;matched=len(slots)-len(run.queue.unmatched)
            return dict(identity_snapshot=run.identity_snapshot,verdict='PASS' if not run.queue.unmatched else 'FAIL',requested=len(slots),matched=matched,matched_fraction=matched/len(slots) if slots else None,unmatched=run.queue.unmatched,slots=slots,zero_B1_exposure=len(slots)==0,events=list(run.medium.events))
        finally:run.close()

    def F8(self):
        self.require("F8");run=Run(0,self.rows,reward=True,arm='reward',episodes=40,initial=self.live,keys=dict(growth='growth/F8/reward',recovery='recovery/F8/reward'),backend=self.backend,execution=self.execution,scope='fixtures')
        try:
            for e in range(40):run.episode(e,task='move' if e<20 else 'remember_static',world_id=F8_WORLD_IDS[e])
            summaries=[]
            for row in run.episode_log[20:]:
                updates=row['reward_updates'];visible=[v['defined_fraction'] for v in row['step_diagnostics'] if v['step']<40]
                summaries.append(dict(e=row['episode'],defined_P_fraction_visible=float(np.mean(visible)),
                    mean_e=float(np.mean([v['eligibility'] for v in updates])) if updates else None,
                    nonzero_reward_delta=sum(v['delta']!=0 for v in updates),mean_abs_delta=float(np.mean([abs(v['delta']) for v in updates])) if updates else None,
                    reward_updates=updates))
            events=list(run.medium.events);b1=[e for e in events if e['rule']=='birth_terminal' and e['values']['birth_rule']=='B1']
            return dict(identity_snapshot=run.identity_snapshot,verdict='DESCRIPTIVE',first_memory=summaries[0],within_memory=summaries[1:],rbar_start=.5,rbar_final=run.rbar,
                        B1_demand=len(b1),B1_accepted=sum(e['values']['outcome']=='accepted' for e in b1),events=events,episodes=run.episode_log)
        finally:run.close()

    def F9(self):
        self.require("F9")
        from ..world.world import Observation
        from .rev7_protocol import decode
        from .rev7_reporting import INTERPRETATION
        cases={}
        for j,(name,(bearing,distance,desired)) in enumerate(F9_CASES.items()):
            obs=Observation(task=1,target_angle=bearing,target_distance=distance,desired_range=desired)
            ds=bindings('move',obs,permutation(10000808+j),0.)
            active=[d for d in ds if d.strength>0]
            beta=active[0].phase if active else 0.
            m=Rev7Medium(seed(f'medium/F9/{name}'),frozen=True)
            try:
                m.add((0,0),beta,role='output',rule='F9_DECODER_SETUP')
                chosen=decode('move',obs,*m.native.output(),0.)
                cases[name]=dict(identity_snapshot=self.identity_snapshot,namespace='deterministic_synthetic',seed=seed(f'medium/F9/{name}'),
                    reserved_world_id=10000808+j,observation_type='literal synthetic, no native world rollout',
                    observation=dict(target_angle=bearing,target_distance=distance,desired_range=desired),
                    demand_strength=sum(d.strength for d in ds),action=dict(angle=chosen.angle,magnitude=chosen.magnitude,choice=chosen.choice))
            finally:m.close()
        return dict(verdict='DESCRIPTIVE',interpretation=INTERPRETATION['move'],cases=cases)

    def run_all(self):
        self.identity_snapshot=self.execution.start('fixtures')
        try:
            for name in ('N1','F1','F2','F3','F4','F5','F6','F7','F8','F9'):
                if name=='F5' and any(self.results.get(n,{}).get('verdict')=='FAIL' for n in ('F1','F2','F3','F4')):break
                try:self.results[name]=finite_record(getattr(self,name)())
                except Exception as error:
                    self.results[name]=dict(verdict='INVALID',reason=f'{type(error).__name__}: {error}');break
                if self.results[name]['verdict']=='INVALID':break
                if name in ('N1','F5','F7') and self.results[name]['verdict']=='FAIL':break
            from .rev7_protocol import stops
            gates=stops(dict(N1_failed_or_invalid=self.results.get('N1',{}).get('verdict') in ('FAIL','INVALID'),fixture_invalid=any(r['verdict']=='INVALID' for r in self.results.values()),F1_F4_failed=any(self.results.get(n,{}).get('verdict')=='FAIL' for n in ('F1','F2','F3','F4')),F5_failed=self.results.get('F5',{}).get('verdict')=='FAIL',F7_unmatched=self.results.get('F7',{}).get('verdict')=='FAIL'))
            from .rev7_reporting import INTERPRETATION
            return dict(revision=CONFIG['revision'],identity_snapshot=self.identity_snapshot,interpretation=INTERPRETATION,results=self.results,stops=gates,not_run=[n for n in ('N1','F1','F2','F3','F4','F5','F6','F7','F8','F9') if n not in self.results],calibration=self.calibration)
        finally:self.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--construct-only',action='store_true',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.write_text(json.dumps(construct_only(),indent=2,allow_nan=False)+'\n')




def minimum_distances(m):
    es=m.native.elements;ds=m.native.reference_drives()
    return dict(element_element=min((math.hypot(a.x-b.x,a.y-b.y) for i,a in enumerate(es) for b in es[i+1:]),default=None),element_site=min((math.hypot(e.x-d.x,e.y-d.y) for e in es for d in ds),default=None))


def span(m):
    es=[e for e in m.native.elements if m.role(e.id)=='element']
    return dict(span=max((math.hypot(a.x-b.x,a.y-b.y) for a in es for b in es),default=0.),radius=max((math.hypot(e.x,e.y) for e in es),default=0.))


def f1c_response(records):
    first=next((r['time'] for r in records if 8<r['time']<=16+1e-9 and abs(float(wrap(r['beta']-math.pi/2)))<=.3),None)
    hold=first is not None and all(abs(float(wrap(r['beta']-math.pi/2)))<=.3 for r in records if first<=r['time']<=24+1e-9)
    access=sum(r['drive_access'] for r in records)/len(records)
    later=[r for r in records if 16-1e-9<=r['time']<=160+1e-9]
    response=sum(abs(float(wrap(r['beta']-math.pi/2)))<=.3 for r in later)/len(later)
    pin=all(r['pin_invariant'] for r in records)
    if not pin:raise ValueError('INVALID: pin-invariance implementation check')
    complete=len(records)==1600 and len(later)==1441
    if not complete:raise ValueError('INVALID: incomplete F1c record')
    # The extra prediction uses sustained entry through the required hold,
    # including entries after the gate deadline. It cannot change that gate.
    hold_window=[r for r in records if 8<r['time']<=24+1e-9]
    last_bad=max((j for j,r in enumerate(hold_window) if abs(float(wrap(r['beta']-math.pi/2)))>.3),default=-1)
    sustained=hold_window[last_bad+1]['time'] if last_bad+1<len(hold_window) else None
    margin=next((r for r in records if abs(r['time']-12.)<1e-9),None)
    if margin is None:raise ValueError('INVALID: missing F1c margin sample')
    return dict(response_pass=first is not None and hold and access>=.8 and response>=.8,first_entry_time=first,delay=None if first is None else first-8,continuous_to_24=hold,source_access=access,response_persistence=response,pin_invariant=pin,
        sustained_entry_delay=None if sustained is None else sustained-8,error_at_12=abs(float(wrap(margin['beta']-math.pi/2))),
        four_second_margin_met=sustained is not None and sustained<=12+1e-9,margin_used_in_verdict=False,sustained_entry_hold_until=24.)


def n1_saddle_slip(rows,initial_phase):
    """Endpoint-resolved unwrapped escape diagnostic, never an accuracy gate."""
    member=N1_SADDLE_DIAGNOSTIC['member'];cut=N1_SADDLE_DIAGNOSTIC['departure_radians']
    first=next((j for j,r in enumerate(rows) if abs(r['phases'][member]-initial_phase)>=cut),None)
    displacement=rows[-1]['phases'][member]-initial_phase
    crossed=None if first is None else rows[first]['phases'][member]-initial_phase
    return dict(status='NOT_OBSERVED' if first is None else 'OBSERVED',member=member,initial_phase=initial_phase,
        departure_radians=cut,direction=None if crossed is None else (1 if crossed>0 else -1),
        time_seconds=None if first is None else rows[first]['time'],
        time_bracket_seconds=None if first is None else [0. if first==0 else rows[first-1]['time'],rows[first]['time']],
        displacement_at_departure=crossed,final_unwrapped_phase=rows[-1]['phases'][member],
        final_unwrapped_displacement=displacement,horizon_seconds=rows[-1]['time'],used_in_verdict=False)


def n1_case_result(name,a,b):
    recipe=N1_RECIPES[name]
    result=compare_n1(a,b,recipe['entry'],recipe['entry_member'],seconds=recipe['seconds'],used_in_verdict=recipe['used_in_verdict'])
    if name=='N1g':
        result['interpretation']='SENSITIVITY_NOT_ACCURACY'
        result['slip_definition']=N1_SADDLE_DIAGNOSTIC
        initial=recipe['members'][N1_SADDLE_DIAGNOSTIC['member']][2]
        result['slip']=[dict(h=h,**n1_saddle_slip(rows,initial)) for h,rows in zip((PRODUCTION_H,REFINEMENT_H),(a,b))]
    return result


def n1_verdict(cases):
    """Require all registered cases; only N1a-f contribute accuracy cuts."""
    if set(cases)!=set(N1_RECIPES):raise ValueError('INVALID: incomplete N1 cases')
    for name,recipe in N1_RECIPES.items():
        expected=('PASS','FAIL') if recipe['used_in_verdict'] else ('DESCRIPTIVE',)
        if cases[name].get('verdict') not in expected or cases[name].get('used_in_verdict') is not recipe['used_in_verdict']:
            raise ValueError('INVALID: N1 case verdict policy mismatch')
    return 'PASS' if all(cases[name]['verdict']=='PASS' for name,recipe in N1_RECIPES.items() if recipe['used_in_verdict']) else 'FAIL'


def compare_n1(a,b,entry,entry_member=0,*,seconds=16.,used_in_verdict=True):
    count=round(seconds/WORLD_DT)
    if len(a)!=count or len(b)!=count or any(not math.isfinite(row['time']) or abs(row['time']-(j+1)*WORLD_DT)>1e-9 for rows in (a,b) for j,row in enumerate(rows)):raise ValueError('INVALID: unmatched N1 endpoints')
    # Missing/non-finite measurements cannot become FAIL or a topology agreement.
    for rows in (a,b):
        for row in rows:
            if not np.isfinite(row['phases']).all() or not np.isfinite(row['positions']).all() or not np.isfinite(list(row['excursion'].values())).all():raise ValueError('INVALID: nonfinite N1 measurement')
    pa,pb=np.array([r['phases'] for r in a]),np.array([r['phases'] for r in b])
    xa,xb=np.array([r['positions'] for r in a]),np.array([r['positions'] for r in b])
    free=np.array(a[0]['free']);wrapped=float(np.max(np.abs(wrap(pa-pb))));unwrapped=float(np.max(np.abs(pa-pb)))
    position=float(np.max(np.linalg.norm(xa[:,free]-xb[:,free],axis=2))) if free.any() else 0.
    phase_top=sum(x['phase_topology']==y['phase_topology'] for x,y in zip(a,b))/count
    motion_top=sum(x['motion_topology']==y['motion_topology'] for x,y in zip(a,b))/count
    pins=all(r['pin_invariant'] for r in a+b)
    def first(rows):return next((r['time'] for r in rows if r['time']>8 and abs(float(wrap(r['phases'][entry_member]-math.pi/2)))<=.3),None)
    times=[first(a),first(b)] if entry else [None,None]
    entry_pass=not entry or (times==[None,None]) or all(t is not None for t in times) and abs(times[0]-times[1])<=.1+1e-12
    validity=n1_validity(a,b)
    holds=[t is not None and all(abs(float(wrap(r['phases'][entry_member]-math.pi/2)))<=.3 for r in rows if t<=r['time']<=24+1e-9) for t,rows in zip(times,(a,b))] if entry and seconds>=24 else None
    verdict='DESCRIPTIVE'
    if used_in_verdict:verdict='PASS' if wrapped<=.01 and unwrapped<=.01 and position<=.01 and phase_top>=.99 and motion_top>=.99 and pins and entry_pass else 'FAIL'
    return dict(verdict=verdict,used_in_verdict=used_in_verdict,maximum_wrapped_phase=wrapped,maximum_unwrapped_phase=unwrapped,maximum_free_position=position,Ntheta_agreement=phase_top,Nx_agreement=motion_top,pins_invariant=pins,entry_applicable=entry,entry_times=times,entry_pass=entry_pass,entry_hold_through_24=holds,hold_used_in_verdict=False,records=[a,b],seconds=seconds,h=[PRODUCTION_H,REFINEMENT_H],substeps=[20,80],phase_scale=32.,validity=validity,fast_transient_frames=validity['individual_invalid_frames'])


def n1_validity(a,b):
    """Descriptive masks: individual IDs and undirected endpoint Ntheta pairs.

    Compare pairs used in either run at the matched endpoint. Missing use is
    distinct from invalid use; changing topology is also reported by N1.
    """
    def masks(row):
        bounds=row['excursion']
        pairs={tuple(sorted((target,source))) for target,sources in row['phase_topology'].items() for source in sources}
        if any(not math.isfinite(v) or v<0 for v in bounds.values()) or any(a not in bounds or b not in bounds for a,b in pairs):raise ValueError('INVALID: missing or invalid used-pair excursion')
        return {id for id,v in bounds.items() if v>math.pi/2},{(a,b) for a,b in pairs if bounds[a]+bounds[b]>math.pi/2}
    masks_a=[masks(r) for r in a];masks_b=[masks(r) for r in b]
    return dict(used_in_verdict=False,pair_policy='undirected union of endpoint Ntheta links per run; site validity uses individual E_i',
        individual_invalid_frames=[sum(bool(m[0]) for m in rows) for rows in (masks_a,masks_b)],
        used_pair_invalid_frames=[sum(bool(m[1]) for m in rows) for rows in (masks_a,masks_b)],
        individual_invalid_observations=[sum(len(m[0]) for m in rows) for rows in (masks_a,masks_b)],
        used_pair_invalid_observations=[sum(len(m[1]) for m in rows) for rows in (masks_a,masks_b)],
        individual_disagreement_frames=sum(x[0]!=y[0] for x,y in zip(masks_a,masks_b)),
        used_pair_disagreement_frames=sum(x[1]!=y[1] for x,y in zip(masks_a,masks_b)),
        individual_disagreement_observations=sum(len(x[0]^y[0]) for x,y in zip(masks_a,masks_b)),
        used_pair_disagreement_observations=sum(len(x[1]^y[1]) for x,y in zip(masks_a,masks_b)))

if __name__=='__main__':main()
