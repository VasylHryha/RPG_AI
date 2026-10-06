"""Owner-authorized section-15 v4 development: amended CMA-ES on fresh development seeds."""
import argparse
import concurrent.futures
import gzip
import json
import math
import pathlib
import subprocess
import sys
import time
import warnings
from s4_development import ROOT, BINARY, ARMS, stats, write, verify_sources, sha
from s3_runner import request, POOL
from build_admission import admit
from s4_deadline import Deadline,BoundedPool
from s4_v4_replay import export_trace
from result_cache import Cache,identity,digest
sys.path.insert(0,str(ROOT/'build/s4_cma_vendor'))
with warnings.catch_warnings():
    warnings.filterwarnings('ignore',message='Could not import matplotlib.pyplot.*')
    import cma

COMMON = dict(K=(0,5), K_t=(0,5), kappa=(0,50), beta=(0,3), G=(0,5),
              w=(0,3), f_c=(.3,1), m_k=(.2,1), lambda_th=(0,3))
BOUNDS = {'resonator':dict(COMMON,omega_melee=(-2,2),omega_ranged=(-2,2)),
          'morale':dict(COMMON,lambda_melee=(0,2),lambda_ranged=(0,2)),
          'pushpull':dict(G=(0,5),f_c=(.3,1),m_k=(.2,1))}
def defaults(arm):return {k:(lo+hi)/2 for k,(lo,hi) in BOUNDS[arm].items()}
OUT=ROOT/'s4_v4_development'
POPULATION=16
GENERATIONS=16
CLUSTERS=19
WORKERS=10
VALIDATION_N=100
PRIOR_SECONDS=4207.082094875999
CAP_SECONDS=360*60-PRIOR_SECONDS


def normalized(arm,params):
    return [(params[k]-lo)/(hi-lo) for k,(lo,hi) in BOUNDS[arm].items()]


def knobs(arm,x):
    if len(x)!=len(BOUNDS[arm]) or any(not math.isfinite(float(v)) or v<0 or v>1 for v in x):raise ValueError('invalid normalized candidate')
    return {k:float(lo+float(v)*(hi-lo)) for v,(k,(lo,hi)) in zip(x,BOUNDS[arm].items())}


def optimizer(arm,start):
    if cma.__version__!='4.5.0':raise RuntimeError('optimizer version drift')
    return cma.CMAEvolutionStrategy(normalized(arm,start),.25,
        dict(bounds=[0,1],popsize=POPULATION,seed=420060+'ABC'.index(optimizer.stage)*100+list(BOUNDS).index(arm),
             verbose=-9,verb_log=0))
optimizer.stage='A'


def battles(stage,split):
    base=940000000+'ABC'.index(stage)*1000000+(100000 if split=='validation' else 0)
    setting='s4_melee10' if stage=='A' else 's4_full_head' if stage=='B' else 's4_p23'
    if split=='tuning':
        opponents=['novice']*19 if stage=='A' else ['novice' if i%2==0 else 'regular' for i in range(19)] if stage=='B' else POOL
        return [(opp,base+i,setting) for i,opp in enumerate(opponents)]
    opponents=['novice'] if stage=='A' else ['novice','regular'] if stage=='B' else POOL
    result=[(opp,base+i,setting) for opp in opponents for i in range(VALIDATION_N)]
    if stage=='C':result.extend((opp,base+1000+i,'s4_full_head') for opp in ('novice','regular') for i in range(VALIDATION_N))
    return result


def check_inputs(expected):
    for path,known in expected.items():
        if sha(pathlib.Path(path))!=known:raise RuntimeError('input changed during amended run: '+path)


def execute(task,deadline):
    deadline.remaining()
    engine_identity,cache_root,specs=task
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
        metrics=json.loads(run.stderr)
        for i,value in zip(missing,values):
            records[i]=value
            if value.get('controllerStatus')=='completed' and not any(value['controllerFailures']):cache.put(reqs[i],[value],dict(purpose='S4 v4 fresh development',metrics=metrics))
    rows=[]
    for i,(spec,req,result) in enumerate(zip(specs,reqs,records)):
        row=dict(spec=spec,request=req,summary=result,cache_hit=i in hits,cache_key=digest(req),metrics=cached_metrics.get(i,metrics))
        if result.get('controllerStatus')!='completed' or any(result.get('controllerFailures',[1])):
            row['failure']=True
        else:row['S']=result['survivors']-result['enemySurvivors'];row['D']=result['crossTeamDealt'][0]-result['crossTeamTaken'][0]
        rows.append(row)
    return rows


class Bench:
    def __init__(self,out):
        self.out=out;self.started=time.monotonic();self.identity=identity('cpp',[str(BINARY),'--metrics'])
        self.deadline=Deadline(self.started+CAP_SECONDS)
        self.cache_root=ROOT/'build/combat_cache';self.pool=BoundedPool(WORKERS,self.deadline)
        self.raw=gzip.open(out/'fights.jsonl.gz','wt');self.budgets={a:0 for a in BOUNDS};self.executed=0;self.hits=0;self.uses=[];self.best={}
        self.locked={str(ROOT/name):sha(ROOT/name) for name in ('s4_v4.py','s4_v4_report.py','s4_v4_trace_summary.py','s4_deadline.py','s4_v4_replay.py','s3_runner.py','s4_development.py','result_cache.py','result_schema.py','S4_V4_SEEDS.json','S4_AMENDED_PROTOCOL.md','S4_V4_PROTOCOL.md','S4_V4_DESIGN_PIN.md','s4_replay.html')}
        self.locked[str(ROOT/'S4_V4_DESIGN_PIN.md')]=sha(ROOT/'S4_V4_DESIGN_PIN.md')
        self.locked.update({str(p):sha(p) for p in (ROOT/'build/s4_cma_vendor/cma').rglob('*.py')})
        self.ledger()

    def ledger(self):
        write(self.out/'s4_seeds.json',dict(status='development_only',judging_seeds=None,
            cache_identity_sha256=digest(self.identity),uses=self.uses,
            policy='Each candidate/generation/stage/arm use records seed, configuration, both orientations and cache status. Validation remains separate and never chooses knobs.'))

    def evaluate(self,arm,params,panel,stage,split,tag,tuning=False):
        self.deadline.remaining()
        check_inputs(self.locked)
        tasks=[]
        for opp,seed,setting in panel:
            specs=[dict(arm=arm,params=params,opponent=opp,seed=seed,setting=setting,swapSides=swap,skeleton='v4',endCounts=True) for swap in (False,True)]
            tasks.append((self.identity,self.cache_root,specs))
        scores={}
        for battle,rows in zip(panel,self.pool.map(execute,tasks)):
            for row in rows:
                self.raw.write(json.dumps(row,allow_nan=False)+'\n')
                self.hits+=int(row['cache_hit']);self.executed+=int(not row['cache_hit'])
                if tuning:self.budgets[arm]+=1
                self.uses.append(dict(stage=stage,split=split,candidate=tag,arm=arm,seed=row['spec']['seed'],
                    opponent=row['spec']['opponent'],setting=row['spec']['setting'],swapSides=row['spec']['swapSides'],cache_hit=row['cache_hit'],params=params,cache_key=row['cache_key']))
            self.raw.flush()
            if any(r.get('failure') for r in rows):self.ledger();raise RuntimeError('controller failure; fix first and restart affected arm budget')
            if stage=='C' and any(row['metrics'][k] for row in rows for k in ('forks','search_calls','artillery_rollouts')):
                self.ledger();raise RuntimeError('Stage C simulates our controller; stop')
            scores[json.dumps(battle)]=sum(r['S'] for r in rows)/2
        return scores

    def close(self):
        self.pool.close();self.raw.close();self.ledger()


def tune(bench,stage,arm,start):
    optimizer.stage=stage;es=optimizer(arm,start);panel=battles(stage,'tuning')
    incumbent=bench.evaluate(arm,start,panel,stage,'tuning','initial',True)
    best=dict(start);best_mean=stats(incumbent)['mean'];logs=[]
    write(bench.out/f'{stage}_{arm}_tuning.json',dict(initial_knobs=start,initial_scores=incumbent,generations=logs,best=best))
    for generation in range(GENERATIONS):
        check_inputs(bench.locked)
        if identity('cpp',[str(BINARY),'--metrics'])!=bench.identity:raise RuntimeError('engine source identity changed during run')
        elapsed=time.monotonic()-bench.started
        evaluated=bench.executed+bench.hits
        forecast=PRIOR_SECONDS+elapsed+max(0,107106-evaluated)*max(.062,elapsed/max(1,bench.executed))
        if forecast>360*60:raise TimeoutError(f'projected combined runtime {forecast/60:.1f} minutes exceeds 360; stop before continuing')
        solutions=es.ask();records=[];objective=[]
        for i,x in enumerate(solutions):
            before_fresh,before_hits=bench.executed,bench.hits
            params=knobs(arm,x);scores=bench.evaluate(arm,params,panel,stage,'tuning',f'{generation}:{i}',True)
            mean=stats(scores)['mean'];objective.append(-mean)
            accepted=mean>best_mean
            if accepted:best=params;best_mean=mean
            records.append(dict(index=i,normalized=[float(v) for v in x],knobs=params,fights=2*CLUSTERS,
                scores=scores,stats=stats(scores),accepted_as_best=accepted,failure=None,
                fresh_fights=bench.executed-before_fresh,cache_hits=bench.hits-before_hits))
            write(bench.out/f'{stage}_{arm}_partial.json',dict(generation=generation,candidates=records,best=best,best_mean=best_mean))
        es.tell(solutions,objective)
        bench.ledger()
        logs.append(dict(generation=generation,candidates=records,best=best.copy(),best_mean=best_mean,
            sigma=float(es.sigma),optimizer_stop={k:str(v) for k,v in es.stop().items()}))
        write(bench.out/f'{stage}_{arm}_tuning.json',dict(initial_knobs=start,initial_scores=incumbent,generations=logs,best=best))
        print(f'{stage} {arm} generation {generation+1}/{GENERATIONS}, best mean={best_mean:.4f}, accounted={bench.budgets[arm]}',flush=True)
    if bench.budgets[arm]!=(1+'ABC'.index(stage))*9766:raise RuntimeError('budget mismatch')
    return best


def validate(bench,stage,best):
    panel=battles(stage,'validation');results={}
    for arm in ARMS:
        scores=bench.evaluate(arm,best.get(arm,{}),panel,stage,'validation','best',False)
        bench.ledger()
        results[arm]={}
        for opp,_,setting in panel:
            endpoint=setting+'|'+opp
            if endpoint in results[arm]:continue
            values={json.dumps(b):scores[json.dumps(b)] for b in panel if b[0]==opp and b[2]==setting}
            results[arm][endpoint]=dict(scores=values,stats=stats(values))
    write(bench.out/f'{stage}_validation.json',dict(knobs=best,panel=panel,results=results));return results


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=pathlib.Path,default=OUT);ap.add_argument('--implementation-commit',required=True);args=ap.parse_args()
    out=args.output
    if out.exists():raise RuntimeError('output already exists; never overwrite evidence')
    delivery=json.loads((ROOT/'s4_v4_checks/PART1_DELIVERY.json').read_text())
    if args.implementation_commit!=delivery['implementation_commit']:raise RuntimeError('Part 1 commit mismatch')
    check_inputs({str(ROOT/name):known for name,known in delivery['task_hashes'].items()})
    source=verify_sources();build=admit(BINARY)
    declaration=json.loads((ROOT/'S4_V4_SEEDS.json').read_text())
    if declaration['panels']!={stage:{split:[list(b) for b in battles(stage,split)] for split in ('tuning','validation')} for stage in 'ABC'}:raise RuntimeError('seed declaration mismatch')
    out.mkdir()
    print('Expected duration: 150-240 minutes if all A/B/C stages run; ten native workers, 87,894 tuning evaluations and 19,200 validation fights plus 12 replay captures. Combined task cap 360 minutes; 70.118035 prior execution minutes; remaining allowance 289.881965 minutes. No code edits during execution.',flush=True)
    write(out/'run_identity.json',dict(v4_protocol_sha256=sha(ROOT/'S4_V4_PROTOCOL.md'),protocol_sha256=sha(ROOT/'S4_AMENDED_PROTOCOL.md'),request_sha256=sha(ROOT/'S4_DEVELOPMENT_REQUEST_CODEX.md'),
        build=build,source_pin=source,cma_version=cma.__version__,optimizer_source_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'build/s4_cma_vendor/cma').rglob('*.py'))},
        seed_declaration_sha256=sha(ROOT/'S4_V4_SEEDS.json'),
        code_hashes={name:sha(ROOT/name) for name in ('s4_v4.py','s4_v4_report.py','s4_v4_trace_summary.py','s4_deadline.py','s4_v4_replay.py','s3_runner.py','result_cache.py','result_schema.py','s4_development.py','s4_replay.html','S4_V4_PROTOCOL.md','S4_V4_DESIGN_PIN.md')},
        implementation_commit=args.implementation_commit,workspace_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        skeleton='v4',design_sha256=sha(ROOT/'S4_V4_DESIGN_PIN.md'),spec_0g_sha256=sha(ROOT.parent/'SPEC_0G.json'),
        expected_minutes=[150,240],combined_machine_cap_minutes=360,prior_machine_minutes=PRIOR_SECONDS/60))
    bench=Bench(out);best={a:defaults(a) for a in BOUNDS};replays=[];status='NOT_READY';stage='A'
    try:
        for stage in 'ABC':
            for arm in BOUNDS:best[arm]=tune(bench,stage,arm,best[arm])
            write(out/f'{stage}_best.json',best);v=validate(bench,stage,best)
            for arm in ARMS:
                bench.deadline.remaining()
                check_inputs(bench.locked)
                opp='novice' if stage=='A' else 'regular';setting='s4_melee10' if stage=='A' else 's4_full_head'
                spec=dict(arm=arm,params=best.get(arm,{}),opponent=opp,setting=setting,seed=next(b[1] for b in battles(stage,'validation') if b[0]==opp and b[2]==setting),swapSides=False,skeleton='v4',endCounts=True)
                r=export_trace(out/'replays',stage+'_'+arm,spec,bench.deadline)
                recorded=v[arm][setting+'|'+opp]['scores'][json.dumps((opp,spec['seed'],setting))]
                # Detailed one-orientation equality is reconstructed in the final audit.
                r['cluster_score']=recorded;replays.append(r)
                bench.uses.append(dict(stage=stage,split='validation',candidate='replay_capture',arm=arm,seed=spec['seed'],opponent=opp,setting=setting,swapSides=False,cache_hit=False))
            if stage in 'AB':
                setting='s4_melee10' if stage=='A' else 's4_full_head'
                if v['resonator'][setting+'|novice']['stats']['mean']<=0:status='STOP';break
            status='READY_FOR_S5' if stage=='C' else 'NOT_READY'
        write(out/'summary.json',dict(status=status,stop_stage=stage if status=='STOP' else None,best=best,budgets=bench.budgets,
            executed_fights=bench.executed,cache_hits=bench.hits,replays=replays,elapsed_seconds=time.monotonic()-bench.started,
            equation_changes=[],controller_failures=[],stages_completed=list('ABC'[:'ABC'.index(stage)+1])))
    except BaseException as error:
        bench.pool.stop()
        write(out/'failure.json',dict(status='NOT_READY',stage=stage,error=repr(error),budgets=bench.budgets,
            elapsed_seconds=time.monotonic()-bench.started,executed_fights=bench.executed,cache_hits=bench.hits,replays=replays,best=best));raise
    finally:bench.close()
    print(status,stage,flush=True)


if __name__=='__main__':main()
