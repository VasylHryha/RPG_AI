"""Sections 18–18.2 A/B-only complex development. Importing never executes combat."""
import argparse
import gzip
import json
import math
import pathlib
import subprocess
import time
from s4_v4 import COMMON, cma
BOUNDS = {'resonator':dict(COMMON,mu=(-2,2),omega_ranged=(-2,2)),
          'morale':dict(COMMON,lambda_melee=(0,2),lambda_ranged=(0,2)),
          'pushpull':dict(G=(0,5),f_c=(.3,1),m_k=(.2,1))}
from s4_development import ROOT, BINARY, ARMS, stats, write, sha, verify_sources
from build_admission import admit
from s4_deadline import Deadline, BoundedPool
from result_cache import Cache, identity, digest
from s3_v6_runner import request

POPULATION=16
GENERATIONS=16
CLUSTERS=19
VALIDATION_N=100
WORKERS=10
CAP_SECONDS=360*60
STAGES=('A','B')
TUNING_PER_ARM_STAGE=9766
TOTAL_FIGHTS=2*3*TUNING_PER_ARM_STAGE+4*(200+400)
BINARY=ROOT/'build/astelia_native_v6'
OUT=ROOT/'s4_v6_development'
CHECKS=ROOT/'s4_v6_checks'
LEDGER=ROOT/'S4_V6_SEEDS.json'


def defaults(arm):return {k:(lo+hi)/2 for k,(lo,hi) in BOUNDS[arm].items()}
def normalized(arm,params):
    if set(params)!=set(BOUNDS[arm]):raise ValueError('knob ledger mismatch')
    return [(params[k]-lo)/(hi-lo) for k,(lo,hi) in BOUNDS[arm].items()]
def knobs(arm,x):
    if len(x)!=len(BOUNDS[arm]) or any(not math.isfinite(float(v)) or not 0<=v<=1 for v in x):raise ValueError('invalid normalized candidate')
    return {k:float(lo+float(v)*(hi-lo)) for v,(k,(lo,hi)) in zip(x,BOUNDS[arm].items())}
def optimizer(arm,start):
    if cma.__version__!='4.5.0':raise RuntimeError('optimizer version drift')
    declaration=json.loads(LEDGER.read_text())
    return cma.CMAEvolutionStrategy(normalized(arm,start),.25,
        dict(bounds=[0,1],popsize=POPULATION,seed=declaration['optimizer_seeds'][optimizer.stage][arm],verbose=-9,verb_log=0))
optimizer.stage='A'

def battles(stage,split):
    if stage not in STAGES or split not in ('tuning','validation'):
        raise ValueError('v6 is A/B only; invalid stage or split')
    return [tuple(b) for b in json.loads(LEDGER.read_text())['panels'][stage][split]]


def selection(stage,scores):
    """Exact head allocation and cluster means, with no validation input."""
    if stage not in STAGES:raise ValueError('v6 is A/B only')
    expected={json.dumps(b) for b in battles(stage,'tuning')}
    if set(scores)!=expected:raise ValueError('tuning cluster allocation mismatch')
    if any(not math.isfinite(v) or not -50<=v<=50 for v in scores.values()):
        raise ValueError('invalid survivor score')
    heads={h:[v for key,v in scores.items() if json.loads(key)[0]==h] for h in ('novice','regular')}
    novice=stats(heads['novice'])['mean']
    if stage=='A':return dict(novice_mean=novice,regular_mean=None,eligible=None,rank=(novice,),objective=-novice)
    regular=stats(heads['regular'])['mean'];eligible=novice>=0
    # S in [-50,50]: eligible loss [-50,50], ineligible [51,151].
    # CMA thus receives exactly the same order as incumbent comparison.
    return dict(novice_mean=novice,regular_mean=regular,eligible=eligible,
                rank=(int(eligible),regular),objective=-regular+(0 if eligible else 101))


def selected_omega(best):
    return dict(melee=0,ranged=best['resonator']['omega_ranged'])


def stage_gate(stage,validation,numerical_failures=0):
    if stage not in STAGES:raise ValueError('v6 is A/B only')
    numerical_failures+=sum(1 for row in validation.get('failure_rows',[]) if row.get('controllerStatus')!='completed' or any(row.get('controllerFailures',[1])))
    setting='s4_melee10' if stage=='A' else 's4_full_head'
    novice=validation['resonator'][setting+'|novice']['stats']['mean']
    regular=validation['resonator']['s4_full_head|regular']['stats']['mean'] if stage=='B' else None
    if not math.isfinite(novice) or (regular is not None and not math.isfinite(regular)):
        raise ValueError('nonfinite validation gate')
    novice_pass=novice>0;progress=None if regular is None else regular>-6.025
    beats=regular is not None and regular>0 and novice_pass and numerical_failures==0
    status='NOT_READY' if not novice_pass or numerical_failures or progress is False else 'READY_TO_DRAFT_S5' if beats else 'PROGRESS' if stage=='B' else 'CONTINUE'
    return dict(novice_mean=novice,novice_validation_pass=novice_pass,regular_mean=regular,
                regular_progress_pass=progress,regular_threshold=-6.025,beats_regular_in_development=beats,
                failure_free=numerical_failures==0,numerical_failures=numerical_failures,status=status,C_authorized=False,S5_run_authorized=False)


def check_inputs(expected):
    for name,known in expected.items():
        if sha(ROOT/name)!=known:raise RuntimeError('v6 input changed: '+name)


def declaration():
    d=json.loads(LEDGER.read_text())
    if d['status']!='FRESH_DEVELOPMENT_ONLY' or d['judging_root'] is not None:
        raise RuntimeError('fresh development ledger required')
    if set(d['panels'])!=set(STAGES):raise RuntimeError('v6 is A/B only')
    seen=set()
    for stage in STAGES:
        for split in ('tuning','validation'):
            panel=battles(stage,split);setting='s4_melee10' if stage=='A' else 's4_full_head'
            expected_heads=['novice']*19 if stage=='A' else ['novice' if i%2==0 else 'regular' for i in range(19)]
            if split=='validation':expected_heads=[h for h in (('novice',) if stage=='A' else ('novice','regular')) for _ in range(100)]
            if [b[0] for b in panel]!=expected_heads or any(b[2]!=setting for b in panel):raise RuntimeError('panel allocation mismatch')
            seeds={b[1] for b in panel}
            # B validation shares seed ids across heads, as inherited.
            count=19 if split=='tuning' else 100
            if len(seeds)!=count or seeds&seen or any(type(s) is not int or not 0<=s<2**32 for s in seeds):
                raise RuntimeError('invalid/disjoint development allocation')
            seen|=seeds
    for name,known in d['prior_declaration_hashes'].items():
        if sha(ROOT/name)!=known:raise RuntimeError('prior seed inventory changed: '+name)
    if seen&set(d['prior_seed_inventory']):raise RuntimeError('development seed reused')
    engineering=d.get('engineering_seeds',{})
    if set(engineering)!={'A','B_novice','B_regular'}:raise RuntimeError('engineering allocation mismatch')
    values=list(engineering.values())
    if any(type(s) is not int or not 0<=s<2**32 for s in values) or len(set(values))!=3 or set(values)&(seen|set(d['prior_seed_inventory'])):
        raise RuntimeError('invalid/reused engineering entropy')
    optimizer=d.get('optimizer_seeds',{})
    if set(optimizer)!=set(STAGES) or any(set(optimizer[s])!=set(BOUNDS) for s in STAGES):raise RuntimeError('optimizer entropy ledger mismatch')
    values=[v for stage in optimizer.values() for v in stage.values()]
    if any(type(v) is not int or not 0<v<2**31 for v in values) or len(set(values))!=6:raise RuntimeError('invalid optimizer entropy')
    return d


def execute_fights(task,deadline):
    deadline.remaining()
    engine_identity,cache_root,specs=task
    if identity('cpp',[str(BINARY),'--metrics'])!=engine_identity:raise RuntimeError('engine identity changed before worker')
    cache=Cache(cache_root,engine_identity)
    reqs=[request(spec) for spec in specs]
    hits=[];records=[None]*len(reqs);missing=[];cached_metrics={}
    for i,req in enumerate(reqs):
        found=cache.load(req)
        if found is None:missing.append(i)
        else:
            records[i]=found[-1];hits.append(i)
            stored=json.loads(gzip.decompress(cache.path(req).read_bytes()))['provenance']
            if not isinstance(stored,dict) or 'metrics' not in stored:raise RuntimeError('cached fight lacks original execution metrics')
            cached_metrics[i]=stored['metrics']
    metrics=dict(forks=0,search_calls=0,artillery_rollouts=0,executed_fights=0)
    if missing:
        run=deadline.run([str(BINARY),'--metrics'],json.dumps([reqs[i] for i in missing])+'\n')
        try:values=json.loads(run.stdout)
        except ValueError:raise RuntimeError('native host failure: '+repr(dict(stdout=run.stdout,stderr=run.stderr,returncode=run.returncode)))
        if run.returncode or not isinstance(values,list) or len(values)!=len(missing):raise RuntimeError('native host failure: '+repr(dict(stdout=run.stdout,stderr=run.stderr,returncode=run.returncode)))
        if identity('cpp',[str(BINARY),'--metrics'])!=engine_identity:raise RuntimeError('engine identity changed during worker')
        metrics=json.loads(run.stderr)
        for i,value in zip(missing,values):
            records[i]=value
            if value.get('controllerStatus')=='completed' and not any(value['controllerFailures']):cache.put(reqs[i],[value],dict(purpose='S4 v6 fresh development',metrics=metrics))
    rows=[]
    for i,(spec,req,result) in enumerate(zip(specs,reqs,records)):
        row=dict(spec=spec,request=req,summary=result,cache_hit=i in hits,cache_key=digest(req),metrics=cached_metrics.get(i,metrics))
        if result.get('controllerStatus')!='completed' or any(result.get('controllerFailures',[1])):
            row['failure']=True
        else:row['S']=result['survivors']-result['enemySurvivors'];row['D']=result['crossTeamDealt'][0]-result['crossTeamTaken'][0]
        rows.append(row)
    if identity('cpp',[str(BINARY),'--metrics'])!=engine_identity:raise RuntimeError('engine identity changed after worker')
    return rows


def execute(task,deadline):
    # Versioned complex engine; shared worker receives the absolute deadline.
    rows=execute_fights(task,deadline)
    for row in rows:
        if any(row['metrics'].get(k,0) for k in ('forks','search_calls','artillery_rollouts')):
            raise RuntimeError('unexpected planner work in v6')
    return rows


def end_states(rows):
    values=[r['summary'] for r in rows];n=len(values)
    def mean(key):return sum(key(r) for r in values)/n
    own=[r['t'] for r in values if r['survivors']==0]
    enemy=[r['t'] for r in values if r['enemySurvivors']==0]
    return dict(fights=n,own_guns_alive_mean=mean(lambda r:r['artilleryAlive'][0]),
                enemy_guns_alive_mean=mean(lambda r:r['artilleryAlive'][1]),
                timeouts=sum(r['survivors']>0 and r['enemySurvivors']>0 for r in values),
                damage_dealt_mean=mean(lambda r:r['crossTeamDealt'][0]),damage_taken_mean=mean(lambda r:r['crossTeamTaken'][0]),
                own_eliminations=len(own),own_elimination_time_mean=sum(own)/len(own) if own else None,
                enemy_eliminations=len(enemy),enemy_elimination_time_mean=sum(enemy)/len(enemy) if enemy else None,
                mean_termination_time=mean(lambda r:r['t']),elimination_time_policy='conditional on elimination; timeouts censored, no imputation')


class Bench:
    def __init__(self,out,deadline,locked):
        self.out=out;self.started=time.monotonic();self.deadline=deadline;self.locked=locked
        self.identity=identity('cpp',[str(BINARY),'--metrics']);self.cache_root=ROOT/'build/combat_cache'
        self.pool=BoundedPool(WORKERS,deadline);self.raw=gzip.open(out/'fights.jsonl.gz','wt')
        self.budgets={a:0 for a in BOUNDS};self.executed=0;self.hits=0;self.uses=[];self.last_rows=[]

    def ledger(self):
        write(self.out/'s4_seeds.json',dict(status='development_only',judging_seeds=None,
              declaration_sha256=sha(LEDGER),cache_identity_sha256=digest(self.identity),uses=self.uses))

    def evaluate(self,arm,params,panel,stage,split,tag,tuning=False):
        self.deadline.remaining();check_inputs(self.locked)
        tasks=[(self.identity,self.cache_root,[dict(arm=arm,params=params,opponent=opp,seed=seed,
                 setting=setting,swapSides=swap,skeleton='v6',endCounts=True) for swap in (False,True)]) for opp,seed,setting in panel]
        scores={};self.last_rows=[]
        for battle,rows in zip(panel,self.pool.map(execute,tasks)):
            for row in rows:
                row.update(stage=stage,split=split,candidate=tag)
                self.raw.write(json.dumps(row,allow_nan=False)+'\n');self.last_rows.append(row)
                self.hits+=int(row['cache_hit']);self.executed+=int(not row['cache_hit'])
                if tuning:self.budgets[arm]+=1
                self.uses.append(dict(stage=stage,split=split,candidate=tag,**row['spec'],cache_hit=row['cache_hit'],cache_key=row['cache_key']))
            self.raw.flush()
            if any(r.get('failure') for r in rows):self.ledger();raise RuntimeError('controller failure; stop and preserve attempt')
            scores[json.dumps(battle)]=sum(r['S'] for r in rows)/2
        check_inputs(self.locked);self.deadline.remaining()
        return scores

    def close(self):
        self.pool.close();self.raw.close();self.ledger()


def tune(bench,stage,arm,start):
    optimizer.stage=stage;es=optimizer(arm,start);panel=battles(stage,'tuning')
    initial=bench.evaluate(arm,start,panel,stage,'tuning','initial',True)
    best=dict(start);best_selection=selection(stage,initial);logs=[]
    def remember(complete=False):
        if not hasattr(bench,'progress_best'):bench.progress_best={a:defaults(a) for a in BOUNDS}
        if not hasattr(bench,'progress_selections'):bench.progress_selections={}
        bench.progress_best[arm]=dict(best)
        bench.progress_selections[arm]=dict(best_selection,stage=stage,complete=complete)
        write(bench.out/'selected_omega.json',dict(stage=stage,omega=selected_omega(bench.progress_best),
              selection=bench.progress_selections.get('resonator'),diagnostic_only=True))
    remember()
    def save():write(bench.out/f'{stage}_{arm}_tuning.json',dict(initial_knobs=start,initial_scores=initial,
                    generations=logs,best=best,best_selection=best_selection,selected_omega=selected_omega({'resonator':best}) if arm=='resonator' else None))
    save()
    for generation in range(GENERATIONS):
        check_inputs(bench.locked);bench.deadline.remaining()
        if identity('cpp',[str(BINARY),'--metrics'])!=bench.identity:raise RuntimeError('engine identity changed')
        elapsed=time.monotonic()-bench.started;evaluated=bench.executed+bench.hits
        remaining=max(0,TOTAL_FIGHTS-evaluated)*max(.062,elapsed/max(1,bench.executed))
        if remaining>bench.deadline.remaining():raise TimeoutError('projected remaining A/B work exceeds 360-minute deadline')
        solutions=es.ask();records=[];objectives=[]
        for i,x in enumerate(solutions):
            before=bench.executed;hits=bench.hits;params=knobs(arm,x)
            scores=bench.evaluate(arm,params,panel,stage,'tuning',f'{generation}:{i}',True)
            picked=selection(stage,scores);objectives.append(picked['objective'])
            accepted=picked['rank']>best_selection['rank']
            if accepted:best=dict(params);best_selection=picked;remember()
            records.append(dict(index=i,normalized=[float(v) for v in x],knobs=params,scores=scores,
                                selection=picked,accepted_as_best=accepted,fresh_fights=bench.executed-before,cache_hits=bench.hits-hits))
            write(bench.out/f'{stage}_{arm}_partial.json',dict(generation=generation,candidates=records,best=best,best_selection=best_selection))
        es.tell(solutions,objectives);bench.ledger()
        logs.append(dict(generation=generation,candidates=records,best=best.copy(),best_selection=best_selection,
                         sigma=float(es.sigma),optimizer_stop={k:str(v) for k,v in es.stop().items()}));save()
        print(f'{stage} {arm} generation {generation+1}/{GENERATIONS}, selection={best_selection}, accounted={bench.budgets[arm]}',flush=True)
    if bench.budgets[arm]!=(STAGES.index(stage)+1)*TUNING_PER_ARM_STAGE:raise RuntimeError('budget mismatch')
    remember(complete=True)
    return best,best_selection


def validate(bench,stage,best):
    panel=battles(stage,'validation');results={}
    for arm in ARMS:
        scores=bench.evaluate(arm,best.get(arm,{}),panel,stage,'validation','best')
        bench.ledger();results[arm]={}
        for opp,_,setting in panel:
            endpoint=setting+'|'+opp
            if endpoint in results[arm]:continue
            values={json.dumps(b):scores[json.dumps(b)] for b in panel if b[0]==opp and b[2]==setting}
            rows=[r for r in bench.last_rows if r['spec']['opponent']==opp and r['spec']['setting']==setting]
            results[arm][endpoint]=dict(scores=values,stats=stats(values),descriptive=end_states(rows))
    write(bench.out/f'{stage}_validation.json',dict(knobs=best,panel=panel,results=results));return results


def run_stages(bench):
    best={a:defaults(a) for a in BOUNDS};selections={};gates={};completed=[]
    bench.progress_best=best;bench.progress_selections={}
    try:
        for stage in STAGES:
            bench.stage=stage
            for arm in BOUNDS:
                best[arm],selections[arm]=tune(bench,stage,arm,best[arm])
                write(bench.out/'selected_omega.json',dict(stage=stage,mu=best['resonator']['mu'],omega=selected_omega(best),selection=selections.get('resonator'),diagnostic_only=True))
            write(bench.out/f'{stage}_best.json',best)
            validation=validate(bench,stage,best);completed.append(stage)
            gates[stage]=stage_gate(stage,validation)
            if gates[stage]['status']=='NOT_READY':break
        result=dict(status=gates[stage]['status'],stages_completed=completed,gates=gates,best=best,
                    selections=selections,selected_omega=selected_omega(best),selected_mu=best['resonator']['mu'],omega_diagnostic_only=True,
                    P2=dict(status='not_run',reason='A/B development only'),P3=dict(status='not_run',reason='A/B development only'),
                    C=dict(status='not_run',reason='outside v6 A/B scope; requires later declared revision'),
                    B=dict(status='evaluated' if 'B' in completed else 'not_run',reason=None if 'B' in completed else 'A novice validation stop'),
                    budgets=bench.budgets,executed_fights=bench.executed,cache_hits=bench.hits,development_only=True)
        write(bench.out/'summary.json',result);return result
    except BaseException as error:
        bench.pool.stop()
        write(bench.out/'failure.json',dict(status='NOT_READY',stage=getattr(bench,'stage',None),error=repr(error),
              best=bench.progress_best,selections=bench.progress_selections,selected_omega=selected_omega(bench.progress_best),gates=gates,stages_completed=completed,
              elapsed_seconds=time.monotonic()-getattr(bench,'started',time.monotonic()),allowance_seconds=CAP_SECONDS,
              budgets=bench.budgets,executed_fights=bench.executed,cache_hits=bench.hits))
        raise


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=pathlib.Path,default=OUT)
    ap.add_argument('--implementation-commit',required=True);args=ap.parse_args()
    started=time.monotonic();deadline=Deadline(started+CAP_SECONDS)
    if args.output.exists():raise RuntimeError('output already exists; never overwrite evidence')
    delivery=json.loads((CHECKS/'PART1_DELIVERY.json').read_text())
    if args.implementation_commit!=delivery['implementation_commit']:raise RuntimeError('Part 1 commit mismatch')
    locked=delivery['runtime_hashes'];check_inputs(locked);d=declaration();source=verify_sources();build=admit(BINARY)
    if build['binary_sha256']!=delivery['binary_sha256'] or build['manifest_sha256']!=delivery['build_manifest_sha256']:
        raise RuntimeError('verified Part 1 binary/build changed')
    # Claim before any combat, permanently. Failed attempts require a fresh ledger/revision.
    with (CHECKS/'LEDGER_USED.json').open('x') as f:
        json.dump(dict(declaration_sha256=sha(LEDGER),implementation_commit=args.implementation_commit,output=str(args.output)),f)
    args.output.mkdir(parents=True)
    write(args.output/'run_identity.json',dict(build=build,source_pin=source,code_hashes=locked,
          implementation_commit=args.implementation_commit,workspace_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          seed_declaration_sha256=sha(LEDGER),skeleton='v6',policy='18.2 > 18.1 > 18',stages=list(STAGES),
          allowance_minutes=360,expected_minutes=[65,90],deadline_clock='absolute monotonic',
          cma_version='4.5.0',maximum_fights=TOTAL_FIGHTS,development_only=True))
    print('Expected about 65 minutes, 10 workers; A/B only, 60,996 maximum evaluations; absolute 360-minute allowance. No code edits during execution.',flush=True)
    bench=None
    try:
        bench=Bench(args.output,deadline,locked);result=run_stages(bench)
    finally:
        try:
            if bench is not None:bench.close()
        finally:write(args.output/'RUN_TIMING.json',dict(elapsed_seconds=time.monotonic()-started,allowance_seconds=CAP_SECONDS))
    print(result['status'],flush=True)


if __name__=='__main__':main()
