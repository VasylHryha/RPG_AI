"""Registered C2 evaluator. Candidate answers are fixed before labels are graded.

No hierarchy, C3 forgetting experiment, quality score or independent acceptance.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import time
import traceback

import numpy as np

from .c2_cases import EDGES, GENERATOR, generate_trial
from .c2_network import ConductanceNetwork, Settings, GRID_EDGES, canonical, digest
from .c2_reference import equilibrium, gradient, finite_difference, direct_local_update

ROOT=Path(__file__).resolve().parents[1]


def validate_manifest(m):
    if m.get('schema')!='geomind.c2.experiment.v1' or not re.fullmatch(r'geomind-c2-r4-\d{3}',m.get('experiment_id','')):
        raise ValueError('Registered C2 identity required')
    if m.get('algorithm')!=ConductanceNetwork.algorithm or m.get('generator')!=GENERATOR or m.get('tasks')!=['affine','realizable']:
        raise ValueError('Registered mechanism and both tasks required')
    seeds=m.get('initialization_seeds',[])
    if len(seeds)!=20 or len(set(seeds))!=20 or any(type(s) is not int or s<0 for s in seeds):
        raise ValueError('Twenty independent initialization seeds required')
    if m.get('epochs')!=100 or m.get('splits')!={'train':100,'validation':50,'test':200}:
        raise ValueError('Prescribed epochs and splits required')
    if m.get('settings')!=asdict(Settings()) or m.get('ports')!={'inputs':[0,3],'output':10}:
        raise ValueError('Prescribed fixed numerical settings and ports required')
    if m.get('controls')!=['frozen_random','constant_train_mean','ordinary_linear_regression','direct_equilibrium_local_rule','analytic_gradient_training','feedback_removed']:
        raise ValueError('Complete baseline panel required')
    for name in ('dataset_seed_start','teacher_seed_start','order_seed_start'):
        if type(m.get(name)) is not int or m[name]<0: raise ValueError('Independent seed families required')
    families=[set(range(m[name],m[name]+20)) for name in ('dataset_seed_start','teacher_seed_start','order_seed_start')]+[set(seeds)]
    if any(a&b for i,a in enumerate(families) for b in families[i+1:]): raise ValueError('Disjoint RNG seed families required')
    if EDGES!=GRID_EDGES or len(EDGES)!=24: raise ValueError('Grid topology mismatch')
    expected={'realizable_mse_max':.001,'frozen_reduction_min':.5,'equilibrium_abs_tolerance':1e-7,'gradient_direction_cosine_min':.999,'bootstrap_resamples':2000,'bootstrap_seed':25000000}
    if m.get('endpoints')!=expected: raise ValueError('Predeclared endpoints required')
    return m


def check_c1_acceptance(root=ROOT):
    folder=root/'evidence/c1_r006_independent'
    receipt=folder/'INDEPENDENT_REVIEW.md'; text=receipt.read_text()
    if not re.search(r'^Verdict: \*\*ACCEPTED\*\*\.',text,re.MULTILINE):
        raise ValueError('Independent C1 R006 acceptance required')
    result=root/'evidence/c1_r006/results.json'
    sha=hashlib.sha256(result.read_bytes()).hexdigest()
    if sha not in text: raise ValueError('C1 acceptance is not bound to current results')
    old=json.loads(result.read_text())
    for name,value in old['file_hashes'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=value:
            raise ValueError('Accepted C1 input changed: '+name)
    return {'receipt_sha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),'results_sha256':sha,
            'scope':'Registered five-field Constraint domain; extra-field subclasses remain a documented limitation'}


def score_answers(answers,expected):
    if len(answers)!=len(expected) or not answers:
        return {'status':'ASSERTION_FAILURE','coverage':0.,'mse':None,'failures':['missing answers']}
    errors=[]; failures=[]
    for i,(a,y) in enumerate(zip(answers,expected)):
        if a.get('status')!='OK': failures.append({'index':i,'status':a.get('status')}); continue
        value=a.get('output')
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not np.isfinite(value):
            failures.append({'index':i,'status':'INVALID_ANSWER'}); continue
        with np.errstate(over='ignore',invalid='ignore'):
            error=float(np.square(np.float64(value)-np.float64(y)))
        if not np.isfinite(error): failures.append({'index':i,'status':'INVALID_ANSWER'}); continue
        errors.append(error)
    invalid=any(r['status']=='INVALID_ANSWER' for r in failures)
    return {'status':'ASSERTION_FAILURE' if invalid else ('NOT_CONVERGED' if failures else 'PASS'),
            'coverage':len(errors)/len(expected),'mse':float(np.mean(errors)) if not failures else None,
            'conditional_mse':float(np.mean(errors)) if errors else None,'failures':failures}


def totals(traces):
    costs={}
    for trace in traces:
        for key,value in trace['cost'].items():
            if key=='max_force': costs[key]=max(costs.get(key,0),value)
            else: costs[key]=costs.get(key,0)+value
    return costs


def direct_answers(values):
    return [{'status':'OK','output':float(v)} for v in values]


def evaluate_trial(args):
    manifest,index,task,output=args
    folder=Path(output); seed=manifest['initialization_seeds'][index]; label=f'{task}_s{seed}'
    start=time.perf_counter(); cpu_start=time.process_time(); failures=[]
    generated=time.perf_counter(); x,labels,teacher,orders=generate_trial(manifest,index); y=labels[task]
    generation_seconds=time.perf_counter()-generated
    g=np.random.default_rng(seed).uniform(.5,1.5,24)
    manifest_hash=digest(manifest); state=ConductanceNetwork(g,manifest_hash); disabled=state.clone()
    initial=state.export(); frozen=state.clone(frozen=True)
    direct_g=g.copy(); gradient_g=g.copy(); eta=manifest['settings']['eta']; epochs=[]
    candidate_seconds=direct_seconds=gradient_seconds=disabled_seconds=0.
    candidate_cpu=direct_cpu=gradient_cpu=disabled_cpu=0.
    candidate_cost={}; disabled_cost={}; direct_work=gradient_work=0
    for epoch,order in enumerate(orders):
        trials=[]; cpu=time.process_time(); t=time.perf_counter()
        for sample in order:
            tr=state.learn(x[sample],y[sample]); trials.append(tr)
            if tr['status']!='PASS': failures.append({'method':'candidate','epoch':epoch+1,'sample':int(sample),'status':tr['status']})
        candidate_seconds+=time.perf_counter()-t; candidate_cpu+=time.process_time()-cpu
        costs=totals(trials)
        for k,v in costs.items(): candidate_cost[k]=max(candidate_cost.get(k,0),v) if k=='max_force' else candidate_cost.get(k,0)+v
        trials=[]; cpu=time.process_time(); t=time.perf_counter()
        for sample in order:
            tr=disabled.learn(x[sample],y[sample],feedback=False); trials.append(tr)
            if tr['status']!='PASS': failures.append({'method':'feedback_removed','epoch':epoch+1,'sample':int(sample),'status':tr['status']})
        disabled_seconds+=time.perf_counter()-t; disabled_cpu+=time.process_time()-cpu
        for k,v in totals(trials).items(): disabled_cost[k]=max(disabled_cost.get(k,0),v) if k=='max_force' else disabled_cost.get(k,0)+v
        cpu=time.process_time(); t=time.perf_counter()
        for sample in order:
            direct_g=direct_local_update(direct_g,EDGES,16,(0,3),x[sample],10,y[sample],eta=eta)
            direct_work+=2
        direct_seconds+=time.perf_counter()-t; direct_cpu+=time.process_time()-cpu
        cpu=time.process_time(); t=time.perf_counter()
        for sample in order:
            gradient_g=np.clip(gradient_g-eta*gradient(gradient_g,EDGES,16,(0,3),x[sample],10,y[sample]),.05,5)
            gradient_work+=2
        gradient_seconds+=time.perf_counter()-t; gradient_cpu+=time.process_time()-cpu
        epochs.append({'epoch':epoch+1,'committed_updates':costs.get('committed',0),'refused_updates':costs.get('refused',0),
                       'update_norm_sum':costs.get('update_norm',0),'saturation_edge_updates':costs.get('saturated',0),
                       'sweeps':costs.get('sweeps',0),'conductance_sha256':digest(state.conductances.tolist())})
    state.freeze(); disabled.freeze(); before=state.export(); answer_start=time.perf_counter(); query_cpu=time.process_time()
    answers=[state.query(inputs) for inputs in x]
    query_seconds=time.perf_counter()-answer_start; query_cpu=time.process_time()-query_cpu
    frozen_start=time.perf_counter(); frozen_answers=[frozen.query(inputs) for inputs in x]
    frozen_seconds=time.perf_counter()-frozen_start
    disabled_start=time.perf_counter(); disabled_answers=[disabled.query(inputs) for inputs in x]
    disabled_query_seconds=time.perf_counter()-disabled_start
    # Every target-free candidate answer above is fixed before grading or references.
    baseline_start=time.perf_counter()
    design=np.column_stack((np.ones(100),x[:100])); coefficients=np.linalg.lstsq(design,y[:100],rcond=None)[0]
    linear_fit_seconds=time.perf_counter()-baseline_start
    t=time.perf_counter(); linear_predictions=np.column_stack((np.ones(350),x))@coefficients
    linear_query_seconds=time.perf_counter()-t
    t=time.perf_counter(); constant=float(y[:100].mean()); constant_fit_seconds=time.perf_counter()-t
    t=time.perf_counter(); constant_predictions=np.full(350,constant); constant_query_seconds=time.perf_counter()-t
    t=time.perf_counter(); direct_predictions=np.array([equilibrium(direct_g,EDGES,16,(0,3),inputs,10)[10] for inputs in x]); direct_query_seconds=time.perf_counter()-t
    t=time.perf_counter(); gradient_predictions=np.array([equilibrium(gradient_g,EDGES,16,(0,3),inputs,10)[10] for inputs in x]); gradient_query_seconds=time.perf_counter()-t
    references=np.array([equilibrium(state.conductances,EDGES,16,(0,3),inputs,10)[10] for inputs in x])
    methods={'candidate':answers,'frozen_random':frozen_answers,'feedback_removed':disabled_answers,
             'constant_train_mean':direct_answers(constant_predictions),'ordinary_linear_regression':direct_answers(linear_predictions),
             'direct_equilibrium_local_rule':direct_answers(direct_predictions),'analytic_gradient_training':direct_answers(gradient_predictions)}
    metrics={name:{split:score_answers(a[sl],y[sl]) for split,sl in
                  (('train',slice(0,100)),('validation',slice(100,150)),('test',slice(150,350)))} for name,a in methods.items()}
    if any(v['status']!='PASS' for row in metrics.values() for v in row.values()): failures.append({'method':'evaluation','status':'FAILED_QUERY'})
    reload_start=time.perf_counter(); loaded=ConductanceNetwork.load(before)
    reload_answers=[loaded.query(x[i]) for i in (0,100,150,349)]
    persistence_seconds=time.perf_counter()-reload_start
    retention=(state.export()==before and frozen.export()==initial and disabled.export()==initial
               and loaded.export()==before and all(a['status']==answers[i]['status'] and a['output']==answers[i]['output'] for i,a in zip((0,100,150,349),reload_answers)))
    actual=np.array([a['output'] if a['status']=='OK' else np.nan for a in answers])
    equilibrium_error=float(np.max(np.abs(actual-references))) if np.isfinite(actual).all() else None
    direct_difference=float(np.max(np.abs(actual-direct_predictions))) if np.isfinite(actual).all() else None
    direct_geometry_difference=float(np.max(np.abs(state.conductances-direct_g)))
    # Predict and then perform a small intervention using an independent derivative.
    sample=x[150]; base_answer=answers[150]['output']; intervention=None
    if base_answer is not None:
        dy=gradient(state.conductances,EDGES,16,(0,3),sample,10,base_answer-1.)
        edge=int(np.argmax(np.abs(dy))); changed=state.conductances; delta=.001 if changed[edge]+.001<=5 else -.001
        changed[edge]+=delta; intervention_answer=ConductanceNetwork(changed,manifest_hash).query(sample)
        shift=intervention_answer['output']-base_answer if intervention_answer['status']=='OK' else None
        intervention={'edge':edge,'delta':delta,'predicted_derivative':float(dy[edge]),'actual_shift':shift,
                      'pass':shift is not None and abs(shift)>1e-9 and shift*dy[edge]*delta>0}
    # Activity->geometry: paired one-example training targets differ, away from bound.
    response_a=ConductanceNetwork(g,manifest_hash); response_b=response_a.clone()
    ra=response_a.learn(x[0],.2); rb=response_b.learn(x[0],.8)
    response_geometry=float(np.linalg.norm(response_a.conductances-response_b.conductances))
    causal=bool(intervention and intervention['pass'] and ra['status']==rb['status']=='PASS' and response_geometry>1e-7 and disabled.export()==initial)
    gates={'queries':not any(v['status']!='PASS' for row in metrics.values() for v in row.values()),
           'training':not failures,'retention':retention,'equilibrium':equilibrium_error is not None and equilibrium_error<=1e-7,
           'direct_control':direct_difference is not None and direct_difference<=1e-5 and direct_geometry_difference<=5e-5,
           'causal_controls':causal}
    artifact={'inputs':x.tolist(),'targets':y.tolist(),'teacher_conductances':teacher.tolist() if task=='realizable' else None,
              'sample_orders':orders.tolist(),'initial_state':json.loads(initial),'final_state':json.loads(before),
              'direct_conductances':direct_g.tolist(),'gradient_conductances':gradient_g.tolist(),
              'linear_coefficients':coefficients.tolist(),'predictions':{name:[a['output'] for a in values] for name,values in methods.items()}}
    artifact_text=canonical(artifact); (folder/'trials'/f'{label}.json').write_text(artifact_text+'\n')
    g_final=state.conductances
    return {'task':task,'trial':index,'initialization_seed':seed,'dataset_seed':manifest['dataset_seed_start']+index,
            'teacher_seed':manifest['teacher_seed_start']+index,'order_seed':manifest['order_seed_start']+index,
            'gates':gates,'check_status':'PASS' if all(gates.values()) else 'ASSERTION_FAILURE','failures':failures,
            'metrics':metrics,'epochs':epochs,'saturation_final_edges':int(np.sum((g_final==.05)|(g_final==5))),
            'total_update_norm':float(np.linalg.norm(g_final-g)),'equilibrium_error_max':equilibrium_error,
            'direct_prediction_error_max':direct_difference,'direct_geometry_error_max':direct_geometry_difference,
            'geometry_response_intervention':intervention,'response_geometry_difference':response_geometry,
            'initial_state_sha256':hashlib.sha256(initial.encode()).hexdigest(),'final_state_sha256':hashlib.sha256(before.encode()).hexdigest(),
            'artifact':f'trials/{label}.json','artifact_sha256':hashlib.sha256(artifact_text.encode()).hexdigest(),
            'cost':{'generation_seconds':generation_seconds,'training':{'candidate':{'seconds':candidate_seconds,'process_cpu_seconds':candidate_cpu,'native':candidate_cost},
                'feedback_removed':{'seconds':disabled_seconds,'process_cpu_seconds':disabled_cpu,'native':disabled_cost},
                'direct_equilibrium_local_rule':{'seconds':direct_seconds,'process_cpu_seconds':direct_cpu,'dense_solves':direct_work},
                'analytic_gradient_training':{'seconds':gradient_seconds,'process_cpu_seconds':gradient_cpu,'dense_solves':gradient_work}},
                'query_seconds':{'candidate':query_seconds,'frozen_random':frozen_seconds,'feedback_removed':disabled_query_seconds,
                                 'direct_equilibrium_local_rule':direct_query_seconds,'analytic_gradient_training':gradient_query_seconds,
                                 'ordinary_linear_regression':linear_query_seconds,'constant_train_mean':constant_query_seconds},
                'candidate_query_process_cpu_seconds':query_cpu,'candidate_query_native':totals(answers),
                'linear_fit_seconds':linear_fit_seconds,'constant_fit_seconds':constant_fit_seconds,
                'persistence_seconds':persistence_seconds,'initial_bytes':len(initial.encode()),'final_bytes':len(before.encode()),
                'artifact_bytes':len(artifact_text.encode()),'numeric_model_bytes':24*8,'fallbacks':0},
            'seconds':time.perf_counter()-start,'process_cpu_seconds':time.process_time()-cpu_start}


def interval(values,seed,resamples):
    a=np.asarray(values,dtype=float); rng=np.random.default_rng(seed)
    if not len(a) or not np.isfinite(a).all(): return {'mean':None,'ci95':None,'individual':values}
    boot=a[rng.integers(0,len(a),(resamples,len(a)))].mean(axis=1)
    return {'mean':float(a.mean()),'ci95':np.quantile(boot,[.025,.975]).tolist(),'individual':a.tolist()}


def safe_evaluate_trial(args):
    try:
        return evaluate_trial(args)
    except Exception as exc:
        manifest,index,task,_=args
        return {'task':task,'trial':index,'initialization_seed':manifest['initialization_seeds'][index],
                'check_status':'INFRASTRUCTURE_FAILURE','failures':[{'reason':str(exc),'traceback':traceback.format_exc()}]}


def summarize(rows,manifest):
    complete=len(rows)==40 and {(r.get('task'),r.get('trial')) for r in rows}=={(t,i) for t in manifest['tasks'] for i in range(20)}
    tasks={}; e=manifest['endpoints']
    for task in manifest['tasks']:
        group=sorted([r for r in rows if r.get('task')==task],key=lambda r:r['trial'])
        if len(group)!=20 or any('metrics' not in r for r in group):
            tasks[task]={'hypothesis_status':'INCONCLUSIVE','reason':'Incomplete or infrastructure-failed trials'}; continue
        metrics={}
        for method in group[0]['metrics']:
            values=[r['metrics'][method]['test']['mse'] for r in group]
            metrics[method]=interval(values,e['bootstrap_seed'],e['bootstrap_resamples']) if all(v is not None for v in values) else {'mean':None,'ci95':None,'individual':values}
        adaptive=[r['metrics']['candidate']['test']['mse'] for r in group]
        frozen=[r['metrics']['frozen_random']['test']['mse'] for r in group]
        valid=all(a is not None and b is not None and b>0 for a,b in zip(adaptive,frozen))
        reductions=interval([(b-a)/b for a,b in zip(adaptive,frozen)],e['bootstrap_seed'],e['bootstrap_resamples']) if valid else {'mean':None,'ci95':None}
        differences=interval([a-b for a,b in zip(adaptive,frozen)],e['bootstrap_seed'],e['bootstrap_resamples']) if valid else {'mean':None,'ci95':None}
        meaningful=valid and metrics['candidate']['ci95'][1]<=e['realizable_mse_max'] and reductions['ci95'][0]>=e['frozen_reduction_min']
        failures=any(r['check_status']!='PASS' for r in group)
        if failures: verdict='INCONCLUSIVE'
        elif meaningful: verdict='SUPPORTED_WITHIN_SCOPE'
        elif valid and (metrics['candidate']['ci95'][0]>e['realizable_mse_max'] or reductions['ci95'][1]<e['frozen_reduction_min']): verdict='NOT_SUPPORTED'
        else: verdict='INCONCLUSIVE'
        tasks[task]={'test_mse':metrics,'paired_candidate_minus_frozen_mse':differences,'paired_relative_reduction':reductions,
                     'provisional_target_met':meaningful,'hypothesis_status':verdict,
                     'saturated_trials':sum(r['saturation_final_edges']>0 for r in group),
                     'training_failures':sum(len(r['failures']) for r in group)}
    passed=complete and all(r['check_status']=='PASS' for r in rows)
    return {'complete':complete,'check_status':'PASS' if passed else 'ASSERTION_FAILURE',
            'implementation_status':'REVIEW_READY' if passed else 'BLOCKED','tasks':tasks,
            'hypothesis_status':tasks.get('realizable',{}).get('hypothesis_status','INCONCLUSIVE')}


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--contract-report',type=Path,required=True); parser.add_argument('--jobs',type=int,default=4)
    args=parser.parse_args()
    from tools import gate
    # Required in-runner guard; a CLI wrapper alone cannot authorize the panel.
    problems=gate.check('panel',milestone='c2')
    if problems: raise SystemExit('C2 panel gate blocked: '+' '.join(problems))
    m=validate_manifest(json.loads((ROOT/'experiments/c2_manifest.json').read_text())); acceptance=check_c1_acceptance()
    if args.output.exists(): raise FileExistsError('Evidence must use a fresh directory')
    if not 1<=args.jobs<=4: raise ValueError('Between one and four worker processes required')
    output=args.output.resolve(); output.mkdir(parents=True); (output/'trials').mkdir()
    hashes={str(p.relative_to(ROOT)):gate.sha256(p) for p in gate.source_files()}
    for name in hashes:
        destination=output/'source'/name; destination.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(ROOT/name,destination)
    from xml.etree import ElementTree as ET
    cases=list(ET.parse(args.contract_report).getroot().iter('testcase'))
    if not cases or any(list(c.iter('failure')) or list(c.iter('error')) or list(c.iter('skipped')) for c in cases): raise ValueError('Passing current contracts required')
    properties={p.attrib['name']:p.attrib['value'] for p in ET.parse(args.contract_report).getroot().iter('property')}
    if properties.get('c2_fingerprint')!=gate.fingerprint(): raise ValueError('Contracts do not identify the exact C2 source')
    shutil.copyfile(args.contract_report,output/'contracts.xml')
    shutil.copyfile(ROOT/'.gate/c2_backend/BUILD.json',output/'BUILD.json')
    start=time.perf_counter(); rows=[]
    with (output/'instances.jsonl').open('x') as stream:
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            work=[(m,i,task,str(output)) for task in m['tasks'] for i in range(20)]
            for row in pool.map(safe_evaluate_trial,work):
                rows.append(row); stream.write(canonical(row)+'\n'); stream.flush()
                print(f"{row['task']} trial {row['trial']+1}/20: {row['check_status']}",flush=True)
    summary=summarize(rows,m)
    stable=hashes=={str(p.relative_to(ROOT)):gate.sha256(p) for p in gate.source_files()}
    c1_stable=check_c1_acceptance()==acceptance
    gates={'contracts':True,'complete_panel':summary['complete'],'correct_numerics_and_controls':all(r['check_status']=='PASS' for r in rows),
           'source_stable':stable,'c1_acceptance_stable':c1_stable}
    passed=all(gates.values())
    receipt=dict(summary,experiment_id=m['experiment_id'],manifest=m,manifest_hash=digest(m),
                 source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                 file_hashes=hashes,source_snapshot_hashes=hashes,c1_acceptance=acceptance,
                 environment={'python':platform.python_version(),'numpy':np.__version__,'platform':platform.platform(),
                              'workers':args.jobs,'backend':'strict float64 C++ synchronous Euler','build':json.loads((output/'BUILD.json').read_text())},
                 contracts={'count':len(cases),'report_sha256':gate.sha256(args.contract_report)},gates=gates,
                 instances=rows,total_seconds=time.perf_counter()-start,
                 checks_not_run=['C0 world experiment','C1 panel rerun','C3 forgetting/replay','C4-C8 hierarchy','digital energy efficiency','nonlinear capacity/XOR'],
                 limitations=[m['claim_scope'],'Realizable teacher uses the same topology; this is within-family generalization.',
                              'Soft nudge approximates an objective gradient; ordinary linear regression has the appropriate task capacity.',
                              'All native sweeps process the active graph; local rules do not imply sublinear total work.',
                              'Process wall-clock timings include contention across four workers; process CPU time is also reported.',
                              'No independent C2 acceptance; no broader theory established.'],
                 selected_checkpoint='epoch100_eta0.01',next_action='Separate independent C2 acceptance; stop before C3 or hierarchy')
    receipt.update(check_status='PASS' if passed else 'ASSERTION_FAILURE',implementation_status='REVIEW_READY' if passed else 'BLOCKED')
    (output/'results.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
    (output/'README.md').write_text('C2 '+receipt['implementation_status']+'. Separate acceptance pending. See results.json and per-trial artifacts.\n')
    print(json.dumps({'status':receipt['check_status'],'seconds':receipt['total_seconds'],'hypothesis':receipt['hypothesis_status']}))
    return 0 if passed else 1


if __name__=='__main__': raise SystemExit(main())
