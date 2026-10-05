"""Owner-authorized S4 development only. No judging seed generator or S5 verdicts."""
import argparse
import concurrent.futures
import gzip
import hashlib
import json
import math
import pathlib
import random
import statistics
import subprocess
import time
from build_admission import admit, sha
from s3_runner import ARMS, POOL, ROOT, request

OUT = ROOT/'s4_development'
BINARY = ROOT/'build/astelia_native'
COMMON = dict(K=(0,5), K_t=(0,5), kappa=(0,50), beta=(0,3), G=(0,5),
              w=(0,3), f=(.3,1.2), gamma=(0,2))
BOUNDS = {'resonator': dict(COMMON, omega_melee=(-2,2), omega_ranged=(-2,2)),
          'morale': dict(COMMON, lambda_melee=(0,2), lambda_ranged=(0,2)),
          'pushpull': dict(G=(0,5), f=(.3,1.2))}
ROUNDS = 8
WORKERS = 8
MIN_GAIN = 1.0
EXPECTED = '10-20 minutes for tuning and validation; full-army stateful fights dominate; eight native workers. No code edits during execution.'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def stats(values):
    values = list(values.values()) if isinstance(values,dict) else list(values)
    n = len(values)
    if n < 2 or not all(math.isfinite(x) for x in values):
        raise ValueError('insufficient/nonfinite cluster measurements')
    mean, sd = statistics.mean(values), statistics.stdev(values)
    return dict(n=n, mean=mean, sd=sd, se=sd/math.sqrt(n),
                descriptive_normal_95=[mean-1.96*sd/math.sqrt(n), mean+1.96*sd/math.sqrt(n)])


def accept(values):
    s = stats(values)
    return s['mean'] > max(MIN_GAIN, 2*s['se'])


def defaults(arm):
    return {k: (lo+hi)/2 for k,(lo,hi) in BOUNDS[arm].items()}


def sample(arm, best, rng, round_id):
    """Same normalized sampler for all arms; no outcome-informed heuristics."""
    radius = .5 * .8**round_id
    candidates = []
    for _ in range(8):
        keys = list(best) if rng.random() < .5 else [rng.choice(list(best))]
        p = dict(best)
        for key in keys:
            lo, hi = BOUNDS[arm][key]
            p[key] = rng.uniform(max(lo, best[key]-radius*(hi-lo)),
                                 min(hi, best[key]+radius*(hi-lo)))
        candidates.append(p)
    return candidates


def seed(stage, split, index):
    # Whole ranges are reserved and recorded before fights; disjoint from S3 and review.
    return 310000000 + 'ABCX'.index(stage)*1000000 + {'tuning':0,'validation':100000,'anomaly':200000}[split] + index


def battles(stage, round_id=0, validation=False):
    n = 32 if stage != 'C' or not validation else 16*19
    opponents = ['novice'] if stage == 'A' else ['novice','regular'] if stage == 'B' else POOL
    # B validation: 32 seeds per level; C validation: 16 seeds per doctrine.
    if validation and stage == 'B':
        return [(opp,seed(stage,'validation',i), 's4_full_head') for opp in opponents for i in range(32)]
    setting = 's4_melee10' if stage == 'A' else 's4_full_head' if stage == 'B' else 's4_p23'
    if validation:
        return [(opp, seed(stage,'validation',i), setting) for opp in opponents for i in range(32 if stage=='A' else 16)]
    return [(opponents[(round_id*32+i)%len(opponents)], seed(stage,'tuning',round_id*32+i), setting) for i in range(n)]


def run_cluster(task):
    arm, params, battle = task
    opponent, world_seed, setting = battle
    specs = [dict(arm=arm, params=params, opponent=opponent, seed=world_seed,
                  setting=setting, swapSides=swap) for swap in (False,True)]
    requests = [request(s) for s in specs]
    begin = time.monotonic()
    run = subprocess.run([str(BINARY),'--metrics'], input=json.dumps(requests)+'\n',
                         text=True, capture_output=True, timeout=120)
    rows = json.loads(run.stdout)
    if run.returncode or not isinstance(rows,list) or len(rows)!=2:
        raise RuntimeError('native cluster failed: '+run.stderr)
    records=[]
    for spec, result in zip(specs,rows):
        row = dict(spec=spec, request=request(spec), summary=result,
                   seconds_per_cluster=time.monotonic()-begin, metrics=json.loads(run.stderr))
        if 'error' in result or result.get('controllerStatus')!='completed' or any(result['controllerFailures']):
            row['failure']=True
            return dict(failure=row)
        row['S']=result['survivors']-result['enemySurvivors']
        row['D']=result['crossTeamDealt'][0]-result['crossTeamTaken'][0]
        records.append(row)
    return dict(records=records,S=statistics.mean(r['S'] for r in records))


class Bench:
    def __init__(self, output):
        self.output=output
        self.cache={}
        self.pool=concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS)
        self.file=gzip.open(output/'fights.jsonl.gz','wt')
        self.budget={arm:0 for arm in BOUNDS}
        self.executed=0
        self.hits=0

    def evaluate(self, arm, params, bs, tuning=False):
        tasks=[]
        keys=[]
        for b in bs:
            key=json.dumps([arm,params,b],sort_keys=True)
            keys.append(key)
            if tuning:self.budget[arm]+=2
            if key in self.cache:self.hits+=2
            else:tasks.append((key,(arm,params,b)))
        for (key,_), result in zip(tasks,self.pool.map(run_cluster,[task for _,task in tasks])):
            if 'failure' in result:
                self.file.write(json.dumps(result)+'\n');self.file.flush()
                raise RuntimeError('controller failure; fix first and restart affected arm budget')
            self.cache[key]=result['S'];self.executed+=2
            for row in result['records']:self.file.write(json.dumps(row,allow_nan=False)+'\n')
        self.file.flush()
        return {json.dumps(b):self.cache[key] for b,key in zip(bs,keys)}

    def close(self):
        self.pool.shutdown();self.file.close()


def paired(a,b):
    if set(a)!=set(b):raise ValueError('pair keys mismatch')
    return {key:a[key]-b[key] for key in sorted(a)}


def tune(bench, stage, arm, initial):
    best=dict(initial)
    log=[]
    rng=random.Random(510050 + 'ABC'.index(stage)*100 + list(BOUNDS).index(arm))
    for r in range(ROUNDS):
        bs=battles(stage,r)
        incumbent=bench.evaluate(arm,best,bs,tuning=True)
        candidates=sample(arm,best,rng,r)
        records=[dict(knobs=p,accepted=False,failure=None,races=[]) for p in candidates]
        active=list(range(8));values={i:{} for i in active}
        for n,keep in ((8,4),(16,2),(32,2)):
            previous=0 if n==8 else n//2
            for i in active:
                values[i].update(bench.evaluate(arm,candidates[i],bs[previous:n],tuning=True))
                records[i]['races'].append(dict(clusters=n,fights=2*n,
                    scores=values[i].copy(),score=stats(values[i]),gain=stats(paired(values[i],{json.dumps(b):incumbent[json.dumps(b)] for b in bs[:n]}))))
            active=sorted(active,key=lambda i:(-stats(values[i])["mean"],i))[:keep]
        eligible=[i for i in active if accept(paired(values[i],incumbent))]
        chosen=max(eligible,key=lambda i:(stats(values[i])["mean"],-i)) if eligible else None
        if chosen is not None:best=dict(candidates[chosen]);records[chosen]['accepted']=True
        for i,row in enumerate(records):
            row['decision']='accepted' if i==chosen else 'race_eliminated' if i not in active else 'acceptance_rejected' if i not in eligible else 'eligible_not_best'
            row['fights']=row['races'][-1]['fights']
        entry=dict(round=r,incumbent=initial if r==0 else log[-1]['best'],incumbent_scores=incumbent,
                   candidates=records,best=best.copy(),budget_fights=bench.budget[arm])
        log.append(entry)
        write(bench.output/f'{stage}_{arm}_tuning.json',log)
        print(f'{stage} {arm} round {r+1}/{ROUNDS}: best={best}; accounted={bench.budget[arm]}',flush=True)
    return best


def validation(bench,stage,best):
    bs=battles(stage,validation=True)
    if stage=='C':
        # Final P1 validation is a fresh split, separate from stage B.
        bs += [(opp,seed('C','validation',1000+i),'s4_full_head') for opp in ('novice','regular') for i in range(32)]
    results={}
    for arm in ARMS:
        scores=bench.evaluate(arm,best.get(arm,{}),bs)
        results[arm]={}
        for opp in dict.fromkeys(b[0] for b in bs):
            for setting in dict.fromkeys(b[2] for b in bs if b[0]==opp):
                vals={json.dumps(b):scores[json.dumps(b)] for b in bs if b[0]==opp and b[2]==setting}
                results[arm][setting+'|'+opp]=dict(scores=vals,stats=stats(vals))
    write(bench.output/f'{stage}_validation.json',dict(battles=bs,knobs=best,results=results))
    return results


def export_trace(output,name,spec):
    output.mkdir(parents=True,exist_ok=True)
    spec=dict(spec,trace=True)
    fight=request(spec)
    run=subprocess.run([str(BINARY),'--capture-s3','--metrics'],input=json.dumps(fight)+'\n',text=True,capture_output=True,timeout=120)
    if run.returncode:raise RuntimeError(run.stderr)
    raw=run.stdout
    rows=[json.loads(x) for x in raw.splitlines()]
    terminal=rows[-1]
    if terminal.get('controllerStatus')!='completed' or any(terminal['controllerFailures']):
        raise RuntimeError('trace controller failure')
    with gzip.open(output/(name+'.jsonl.gz'),'wt') as f:f.write(raw)
    frames=[];pending=None
    # Host prints post-step trace just before same-step capture; join by stream position.
    for row in rows:
        if 'state' in row:
            if pending is not None and (pending['step']%3==0):frames.append(pending)
            pending=row
        elif row.get('capture') and pending is not None:
            byid={u['id']:u for u in row['units']}
            for u in pending['state']['units']:
                if u['id'] in byid:
                    u['controllerState']=byid[u['id']]['state']
                    u['commitment']=byid[u['id']]['commitment']
    if pending is not None:frames.append(pending)
    payload=dict(spec=spec,request=fight,summary=terminal,frames=frames,width=1200,height=700)
    write(output/(name+'.replay.json'),payload)
    template=(ROOT/'s4_replay.html').read_text()
    # Inline JSON only, escaped to avoid a closing script sequence in supplied data.
    embedded=json.dumps(payload).replace('<','\\u003c')
    (output/(name+'.html')).write_text(template.replace('/*REPLAY_DATA*/null',embedded))
    return dict(file=name+'.html',raw=name+'.jsonl.gz',spec=spec,summary=terminal,
                metrics=json.loads(run.stderr),frames=len(frames),sha256=sha(output/(name+'.jsonl.gz')))


def anomaly(bench):
    configs=[('novice','s4_full_head'),('regular','s4_full_head'),
             ('novice','s4_anomaly_novice_line'),('regular','s4_anomaly_regular_alone')]
    result={}
    for opp,setting in configs:
        bs=[(opp,seed('X','anomaly',i),setting) for i in range(8)]
        result[setting+'|'+opp]=stats(bench.evaluate('morale',defaults('morale'),bs))
    traces=[]
    for opp,setting in configs:
        traces.append(export_trace(bench.output/'replays','anomaly_'+setting+'_'+opp,
            dict(arm='morale',params=defaults('morale'),opponent=opp,setting=setting,seed=seed('X','anomaly',0))))
    write(bench.output/'anomaly.json',dict(results=result,traces=traces))
    return result,traces


def spread_upper(values,rng):
    values=list(values.values()) if isinstance(values,dict) else list(values)
    n=len(values)
    ds=sorted(statistics.stdev(rng.choices(values,k=n)) for _ in range(2000))
    return ds[1900]


def power(results,output):
    rng=random.Random(811005)
    endpoint={}
    for other in ('morale','pushpull'):
        strata=[paired(results['resonator']['s4_p23|'+opp]['scores'], results[other]['s4_p23|'+opp]['scores']) for opp in POOL]
        allvals=[x for xs in strata for x in xs.values()]
        endpoint['resonator_minus_'+other]=dict(pooled=stats(allvals),
            strata={opp:stats(xs) for opp,xs in zip(POOL,strata)},
            variance_upper=sum(spread_upper(xs,rng)**2 for xs in strata)/19**2)
    delta=math.ceil(max(1,.25*max(e['pooled']['sd'] for e in endpoint.values()))*2)/2
    z=statistics.NormalDist().inv_cdf(1-.0025)+statistics.NormalDist().inv_cdf(.9)
    for e in endpoint.values():
        n=max(16,math.ceil(z*z*e['variance_upper']/delta**2))
        e.update(n_per_doctrine=n,total_clusters=19*n,within_bound=19*n<=2000,
                 planning_target_mean=2*delta,margin=delta)
    for opp in ('novice','regular'):
        s=results['resonator']['s4_full_head|'+opp]['scores']
        upper=spread_upper(s,rng)
        n=max(32,math.ceil(z*z*upper**2/delta**2))
        endpoint['P1_'+opp]=dict(stats=stats(s),sd_upper=upper,n=n,within_bound=n<=2000,
                              planning_target_mean=delta,margin=0)
    write(output/'power.json',dict(delta_proposed=delta,owner_approval_required=True,
        method='Normal planning at one-sided alpha .0025, power .90; bootstrap 95th percentile SD, 2000 resamples. P1 targets delta above zero; P2/P3 target 2delta above margin delta. At least 32 per head and 16 per doctrine; report rather than cap requirements above 2000 total clusters per endpoint.', endpoints=endpoint))


def verify_sources():
    repo=ROOT.parents[2]
    base=repo/'research/rrg/v0.2.1'
    expected=json.loads((base.parent/'v0.2.1.expected.json').read_text())
    for name,h in expected['expected_sha256'].items():
        if sha(base/name)!=h:raise RuntimeError('RRG source mismatch: '+name)
    for row in json.loads((base/'MANIFEST.json').read_text())['files']:
        if sha(base/row['path'])!=row['sha256'] or (base/row['path']).stat().st_size!=row['bytes']:
            raise RuntimeError('RRG manifest mismatch')
    for line in (base/'SHA256SUMS.txt').read_text().splitlines():
        if not line.strip():continue
        h,name=line.split(maxsplit=1)
        if sha(base/name.strip().lstrip('*'))!=h:raise RuntimeError('RRG checksum mismatch')
    return expected


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=pathlib.Path,default=OUT);ap.add_argument('--anomaly-only',action='store_true')
    args=ap.parse_args();output=args.output
    output.mkdir(exist_ok=True)
    if (output/'run_identity.json').exists():raise RuntimeError('existing session output; do not overwrite evidence')
    sources=verify_sources();identity=admit(BINARY)
    write(output/'run_identity.json',dict(expected_duration=EXPECTED,started=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
        build=identity,source_pin=sources,code={p.name:sha(p) for p in (ROOT/'s3_runner.py',pathlib.Path(__file__),ROOT/'s4_replay.html')},
        protocol_sha256=sha(ROOT/'S4_PROTOCOL.md'),seed_ledger_sha256=sha(ROOT/'S4_SEED_LEDGER.json')))
    begin=time.monotonic();bench=Bench(output);replays=[];best={arm:defaults(arm) for arm in BOUNDS}
    try:
        if args.anomaly_only:
            anomaly(bench)
            write(output/'summary.json',dict(status='ANOMALY_REVIEW_REQUIRED_BEFORE_TUNING',executed_fights=bench.executed,elapsed_seconds=time.monotonic()-begin))
            return
        anomaly_path=ROOT/'s4_anomaly/anomaly.json'
        if not anomaly_path.exists():raise RuntimeError('inspect preliminary anomaly before tuning')
        write(output/'anomaly_reference.json',dict(path=str(anomaly_path.relative_to(ROOT)),sha256=sha(anomaly_path)))
        for stage in 'ABC':
            for arm in BOUNDS:best[arm]=tune(bench,stage,arm,best[arm])
            write(output/f'{stage}_best.json',best)
            result=validation(bench,stage,best)
            for arm in ARMS:
                opp='novice' if stage!='C' else 'line'
                setting='s4_melee10' if stage=='A' else 's4_full_head' if stage=='B' else 's4_p23'
                replays.append(export_trace(output/'replays',stage+'_'+arm,dict(arm=arm,params=best.get(arm,{}),
                    opponent=opp,setting=setting,seed=seed(stage,'validation',0))))
            if stage=='C':
                power(result,output)
                status='STOP' if result['resonator']['s4_full_head|novice']['stats']['mean']<=0 else 'READY_FOR_S5'
        if any(v!=7680 for v in bench.budget.values()):raise RuntimeError('unequal/incomplete tuning budget')
        write(output/'summary.json',dict(status=status,best=best,budget=bench.budget,executed_fights=bench.executed,
            cache_hits=bench.hits,replays=replays,elapsed_seconds=time.monotonic()-begin,equation_changes=[],failures=[]))
    except Exception as e:
        write(output/'failure.json',dict(status='NOT_READY',error=repr(e),budget=bench.budget,
            elapsed_seconds=time.monotonic()-begin))
        raise
    finally:bench.close()
    print(status,flush=True)


if __name__=='__main__':main()
