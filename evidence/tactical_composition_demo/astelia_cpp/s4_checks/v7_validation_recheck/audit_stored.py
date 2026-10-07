"""Reviewer audit: stored bytes only. Never calls a runner or writes a receipt.

Hash pass precedes decompression. Terminal measurements/ranks/cluster summaries
are independently implemented. Telemetry is recomputed with the reviewed sealed
observation oracle (shared mathematics, not an independent oracle implementation).
Only this directory receives new audit outputs. No allowance/attempt is created.
"""
import collections
import concurrent.futures
import gzip
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
CPP = HERE.parents[1]
REPO = CPP.parents[2]
B, C = CPP / 's4_v7b', CPP / 's4_v7c'
ARMS = ('v7', 'forcedP16', 'forcedv6', 'omega0', 'historicalP16')
HEADS = ('regular', 'novice')


def read(p):
    return json.loads(p.read_bytes())


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def check(value, message):
    if not value:
        raise RuntimeError(message)


def measure(s):
    check(s['controllerStatus'] == 'completed' and not any(s['controllerFailures'])
          and s['complexDiagnostics']['numericalFailureTicks'] == 0, 'failure summary')
    own, enemy, t = s['survivors'], s['enemySurvivors'], s['t']
    check(all(math.isfinite(x) for x in (own, enemy, t)), 'nonfinite summary')
    check(own == int(own) and enemy == int(enemy) and 0 <= own <= 50
          and 0 <= enemy <= 50 and 0 <= t <= 150 + 1/30 + 1e-8, 'invalid summary')
    return dict(win=int(enemy == 0 and own >= 1 and t < 150), S=own-enemy,
                losses=50-own, timeout=int(t >= 150), termination_time=t)


def ranking(s):
    return (-int(s['eligible']), -s['regular_wins'], -s['regular_S'],
            s['regular_losses'], s['ordinal'])


def hash_record(task):
    root, tag, expected = task
    raw = root/'raw'
    p = raw/(tag+'_COMPLETE.json')
    check(sha(p) == expected, 'completion hash '+tag)
    r = read(p)
    for key, suffix in [('claim_sha256','_CLAIM.json'), ('request_sha256','_request.json'),
                        ('stderr_sha256','_stderr.log'), ('raw_sha256','.jsonl.gz')]:
        check(sha(raw/(tag+suffix)) == r[key], key+' '+tag)
    claim = read(raw/(tag+'_CLAIM.json'))
    d = read(root/'DECLARATION.json')
    check(claim['meta'] == r['meta'] and claim['binary'] == r['binary'] == d['binary'], 'identity '+tag)
    check(claim['declaration_sha256'] == sha(root/'DECLARATION.json'), 'claim seal '+tag)
    check(claim['request_sha256'] == r['request_sha256'], 'request binding '+tag)
    gate = root/claim['gate']['path']
    check(sha(gate) == claim['gate']['sha256'] and read(gate)['status'] == 'CLEAR', 'gate '+tag)
    check(read(gate)['binary'] == d['binary'] and read(gate)['declaration_sha256'] == sha(root/'DECLARATION.json'), 'gate identity '+tag)
    check(read(raw/(tag+'_stderr.log')) == r['metrics'], 'metrics '+tag)
    m = r['metrics']
    check(m['executed_fights'] == len(r['summaries']) and
          all(m[k] == 0 for k in ('forks','search_calls','branch_steps','artillery_rollouts')), 'engine work '+tag)
    check(r['raw_bytes'] == (raw/(tag+'.jsonl.gz')).stat().st_size, 'raw size '+tag)
    return r


def terminal(root, r):
    with gzip.open(root/'raw'/(r['tag']+'.jsonl.gz'), 'rb') as f:
        post = None
        for last in f:
            if last.startswith(b'{"observerV1":true'):
                post = last
    s = json.loads(last)
    summaries = s if isinstance(s,list) else [s]
    check(summaries == r['summaries'], 'terminal summary '+r['tag'])
    if root == C:
        check(post is not None, 'missing terminal observation')
        snapshot = json.loads(post)
        own = sum(u[1] == 0 and u[5] > 0 for u in snapshot['units'])
        enemy = sum(u[1] == 1 and u[5] > 0 for u in snapshot['units'])
        check((own, enemy, snapshot['t']) == (summaries[0]['survivors'], summaries[0]['enemySurvivors'], summaries[0]['t']), 'terminal living units '+r['tag'])
    return [measure(s) for s in summaries]


def trace(task):
    tag, expected = task
    # Import functions only. analyze(), runners, deadline and attempt are never called.
    sys.path.insert(0, str(C))
    import analyze
    r = read(C/'raw'/(tag+'_COMPLETE.json'))
    for k,v in r['meta'].items():
        check(expected[k] == v, 'per-fight metadata '+tag+' '+k)
    values = terminal(C, r)
    for k,v in values[0].items():
        check(expected[k] == v, 'per-fight '+tag+' '+k)
    telemetry = analyze.telemetry(r)
    check(telemetry == expected['telemetry'], 'telemetry '+tag)
    return dict(tag=tag, own=r['summaries'][0]['survivors'],
                enemy=r['summaries'][0]['enemySurvivors'], **r['meta'], **values[0])


def main():
    start = time.monotonic()
    t, ta, v, a = [read(p) for p in (B/'TUNING.json', B/'TUNING_ANALYSIS.json', C/'VALIDATION.json', C/'ANALYSIS.json')]
    base = subprocess.check_output(['git','rev-parse','HEAD'], cwd=REPO, text=True).strip()
    # Committed authority, plus local identity. No checkout/worktree mutations.
    inputs = {}
    for p, commit in [(B/'TUNING.json', '796d0a8'), (B/'TUNING_ANALYSIS.json', '796d0a8'),
                      (C/'ANALYSIS.json','e44b528'), (C/'VALIDATION.json','e44b528')]:
        blob = subprocess.check_output(['git','show',commit+':'+str(p.relative_to(REPO))], cwd=REPO)
        check(blob == p.read_bytes(), 'committed authority '+str(p))
        inputs[str(p.relative_to(REPO))] = sha(p)
    for root in (B,C):
        d, seal = read(root/'DECLARATION.json'), read(root/'SEAL.json')
        check(sha(root/'DECLARATION.json') == seal['declaration_sha256'], 'seal')
        for name,h in d['hashes'].items():
            check(sha(REPO/name) == h, 'declaration pin '+name)
        check(sha(root/'build/astelia_native_v7') == d['binary']['binary_sha256'], 'binary hash')
    check(a['validation_sha256'] == sha(C/'VALIDATION.json') and
          a['tuning_sha256'] == ta['tuning_sha256'] == v['tuning_sha256'] == sha(B/'TUNING.json'), 'analysis input hashes')
    candidates = []
    tasks = []
    for i in range(257):
        p = B/f'CANDIDATE_{i:03d}.json'
        check(sha(p) == t['candidates'][str(i)], 'candidate hash')
        q=read(p); candidates.append(q)
        check(q['ordinal'] == i and q['declaration_sha256'] == sha(B/'DECLARATION.json'), 'ordinal/seal')
        check(len(q['records'])==16, 'candidate record allocation')
        tasks.extend((B,tag,h) for tag,h in q['records'].items())
    check(t['evaluations'] == 257 and t['accounted_fights'] == 8224 and len(tasks)==4112, 'budget')
    tasks.extend((C,tag,h) for tag,h in v['records'].items())
    check(len(v['records'])==400 and v['fights']==400, 'validation budget')
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        records=list(pool.map(hash_record,tasks))
    print('All 4512 completion/raw/request/claim/stderr hash chains PASS before parsing', flush=True)
    # Tuning terminal summaries are tiny (no trace); independently recompute all selections.
    metrics=[]
    ledger=read(B/'DEVELOPMENT_SEED_LEDGER.json')
    for q in candidates:
        rows=collections.defaultdict(list)
        subset=records[q['ordinal']*16:q['ordinal']*16+16]
        check({(r['meta']['head'],r['meta']['cluster']) for r in subset} == {(h,c) for h in HEADS for c in range(8)}, 'tuning cells')
        for r in subset:
            check(r['meta']['stage']=='tuning' and r['meta']['ordinal']==q['ordinal'], 'tuning metadata')
            req=read(B/'raw'/(r['tag']+'_request.json'))
            check(len(req)==2, 'two tuning orientations')
            for o,x in enumerate(req):
                check(x['options']['seed']==ledger['tuning'][r['meta']['cluster']] and
                      x['options']['swapSides']==bool(o) and
                      x['options']['ai'][0]['params']==q['params'] and
                      x['options']['ai'][0]['controller']=='v7' and
                      x['options']['ai'][1]['level']==r['meta']['head'], 'tuning request')
            rows[r['meta']['head']].extend(terminal(B,r))
        s=dict(ordinal=q['ordinal'],eligible=sum(x['win'] for x in rows['novice'])>=8,
               regular_wins=sum(x['win'] for x in rows['regular']),regular_S=statistics.mean(x['S'] for x in rows['regular']),
               regular_losses=statistics.mean(x['losses'] for x in rows['regular']),novice_wins=sum(x['win'] for x in rows['novice']))
        check(s==q['selection'], 'selection '+str(q['ordinal']))
        metrics.append(dict(ordinal=q['ordinal'],selection=s))
    ranked=sorted(candidates,key=lambda q:ranking(q['selection']))
    check(ranked[0]==t['selected']==ta['selected'] and ranked[0]['ordinal']==161 and metrics==ta['candidate_metrics'], 'incumbent')
    check([q['ordinal'] for q in ranked]==ta['ranked_ordinals'], 'all ranking')
    check(ta['validation_used'] is False and t['selected_params']==v['selected_params'], 'theta pin')
    # Deterministic optimizer replay consumes stored selection ranks only; no fights.
    sys.path.insert(0,str(CPP/'build/s4_cma_vendor'))
    import cma
    d=read(B/'DECLARATION.json');bounds=d['bounds'];order=d['knob_order']
    norm=lambda p:[(p[k]-bounds[k][0])/(bounds[k][1]-bounds[k][0]) for k in order]
    check(cma.__version__==d['optimizer']['version'], 'CMA version')
    check(candidates[0]['params']==d['historical_theta'], 'initial theta')
    es=cma.CMAEvolutionStrategy(norm(d['historical_theta']),.25,dict(bounds=[0,1],popsize=16,seed=d['optimizer']['seed'],verbose=-9,verb_log=0))
    for g in range(16):
        xs=es.ask();batch=candidates[1+16*g:17+16*g]
        for x,q in zip(xs,batch):
            p={k:float(bounds[k][0]+float(y)*(bounds[k][1]-bounds[k][0])) for k,y in zip(order,x)}
            check(p==q['params'], 'CMA vector '+str(q['ordinal']))
        idx=sorted(range(16),key=lambda i:ranking(batch[i]['selection']))
        losses=[0]*16
        for rank,i in enumerate(idx):losses[i]=rank
        es.tell(xs,losses)
    print('8224 tuning outcomes, all ranks, theta161, deterministic CMA replay PASS', flush=True)
    vl=read(C/'VALIDATION_SEED_LEDGER.json')
    # Known prior ledgers/seed inventories only; never read a judging ledger.
    def ints(x):
        if isinstance(x,dict):return set().union(*(ints(v) for v in x.values())) if x else set()
        if isinstance(x,list):return set().union(*(ints(v) for v in x)) if x else set()
        return {x} if type(x) is int else set()
    prior=set()
    for name,h in vl['prior_development_inventory'].items():
        check(sha(REPO/name)==h, 'seed inventory pin '+name)
        prior |= ints(read(REPO/name))
    check(len(set(vl['validation']))==20 and not (set(vl['validation']) & prior), 'fresh entropy')
    check(set(vl['validation']).isdisjoint(ledger['tuning']+ledger['validation']), 'tuning/validation entropy overlap')
    for r in records[4112:]:
        m=r['meta'];reqs=read(C/'raw'/(r['tag']+'_request.json'))
        check(len(reqs)==1 and m['stage']=='validation', 'singleton validation request')
        req=reqs[0]
        p=d['historical_theta'] if m['arm']=='historicalP16' else t['selected_params']
        template=read(C/(m['head'].upper()+'_REQUEST_TEMPLATE.json'))
        template['options'].update(seed=vl['validation'][m['cluster']],swapSides=bool(m['orientation']),duration=150)
        template['options']['ai'][0].update(controller=m['arm'],skeleton='v7',params=p)
        template.update(trace=True,diagnostics=False,killerTelemetry=True,decisionTrace=True,decisionDiagnostics=True,attributionDiagnostics=True)
        check(req==template, 'exact validation request '+r['tag'])
    check({(r['meta']['arm'],r['meta']['head'],r['meta']['cluster'],r['meta']['orientation']) for r in records[4112:]}=={(arm,head,c,o) for arm in ARMS for head in HEADS for c in range(20) for o in (0,1)}, 'exact validation cells')
    # Recovery changes bookkeeping only. Bind all supplemental original/preserved hashes.
    for name in ('ANALYSIS_RECOVERY_V1_MANIFEST.json','ANALYSIS_RECOVERY_V2_MANIFEST.json'):
        m=read(C/name)
        for f,h in m['hashes'].items():check(sha(C/f)==h,'recovery pin '+f)
        for f,h in m.get('repo_hashes',{}).items():check(sha(REPO/f)==h,'recovery authority '+f)
    print('Fresh seeds, exact requests, recovery pins PASS; full stored telemetry audit begins', flush=True)
    jobs=[(r['tag'],r) for r in a['per_fight']]
    check(len(jobs)==400 and {tag for tag,_ in jobs}==set(v['records']), 'per-fight allocation')
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as pool:
        outcomes=[]
        for i,r in enumerate(pool.map(trace,jobs),1):
            outcomes.append(r)
            if i%20==0:print('Telemetry '+str(i)+'/400 PASS',flush=True)
    bytag={r['tag']:r for r in outcomes}
    for cell in a['cells']:
        rows=[r for r in outcomes if (r['arm'],r['head'])==(cell['arm'],cell['head'])]
        for k,field in [('wins','win'),('timeouts','timeout')]:check(cell[k]==sum(r[field] for r in rows),'cell '+k)
        for k,field in [('mean_S','S'),('own_losses','losses'),('mean_termination_time','termination_time')]:check(cell[k]==statistics.mean(r[field] for r in rows),'cell '+k)
        check(cell['failures']==0 and cell['fights']==len(rows)==40,'cell count')
        per=[r for r in a['per_fight'] if (r['arm'],r['head'])==(cell['arm'],cell['head'])]
        for point in cell['gun_survival']:
            check(point['mean_alive']==statistics.mean(next(p['alive'] for p in r['telemetry']['gun_survival'] if p['t']==point['t']) for r in per),'gun curve')
    diffs=[];discord=collections.Counter()
    for p in a['paired_clusters']:
        for arm in ARMS:
            rows=sorted((r for r in outcomes if (r['arm'],r['head'],r['cluster'])==(arm,p['head'],p['cluster'])),key=lambda r:r['orientation'])
            check(p['wins'][arm]==sum(r['win'] for r in rows) and p['orientation_wins'][arm]==[r['win'] for r in rows] and p['mean_S'][arm]==statistics.mean(r['S'] for r in rows),'paired cluster')
        if p['head']=='regular':
            diffs.append((p['wins']['v7']-p['wins']['forcedP16'])/2)
            for x,y in zip(p['orientation_wins']['v7'],p['orientation_wins']['forcedP16']):discord[f'v7_{x}__forcedP16_{y}']+=1
    check(dict(discord)==a['orientation_discordance'],'discordance')
    check([sum(x>0 for x in diffs),sum(x<0 for x in diffs),sum(x==0 for x in diffs)]==[a['positive_clusters'],a['negative_clusters'],a['tied_clusters']],'cluster signs')
    rng=random.Random(20261007);boot=sorted(sum(rng.choice(diffs) for _ in range(20))/20 for _ in range(10000))
    def quant(q):
        x=9999*q;i=int(x);return boot[i]+(x-i)*(boot[min(i+1,9999)]-boot[i])
    check([quant(.025),quant(.975),statistics.mean(diffs)]==[a['paired_cluster_bootstrap'][k] for k in ('low','high','mean')],'bootstrap')
    check(a['paired_cluster_bootstrap']['seed']==20261007 and a['paired_cluster_bootstrap']['resamples']==10000, 'bootstrap contract')
    check(a['omega0_duplicate']==v['omega0_duplicate']==(t['selected_params']['omega_ranged']==0),'omega0 duplicate')
    cells={(c['arm'],c['head']):c for c in a['cells']};regular=cells['v7','regular'];novice=cells['v7','novice'];control=cells['forcedP16','regular'];delta=regular['wins']-control['wins']
    expected=dict(relative='the panel does not support a comparison' if control['wins']<21 else 'Observed improvement' if delta>=4 else 'Observed worse' if delta<=-4 else 'Observed match',comparator_underperformance=control['wins']<21,win_difference=delta,observed_owner_criterion=regular['wins']>=21 and novice['wins']>=21 and regular['mean_S']>0 and novice['mean_S']>0,descriptive_only=True,S5_authorized=False)
    check(expected==a['readings'],'readings')
    wins=[r for r in outcomes if r['arm']=='v7' and r['head']=='regular' and r['win']]
    check(len(wins)==32 and all(r['enemy']==0 and r['own']>=1 and r['termination_time']<150 for r in wins),'genuine wins')
    result=dict(status='PASS',base_head=base,inputs=inputs,hash_verified_records=4512,
                tuning_fights=8224,validation_fights=400,failures=0,cma_replay='257 vectors exact',
                telemetry='400/400 exact against reviewed sealed observation oracle; shared implementation disclosed',
                cells=a['cells'],paired_clusters=a['paired_clusters'],readings=expected,
                genuine_regular_wins=wins,seconds=time.monotonic()-start,
                limits='Stored-only audit; no engine execution, sealed analysis/render run, new allowance, scientific acceptance or S5 authorization.')
    with (HERE/'AUDIT.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print('ALL PASS '+str(result['seconds'])+' s',flush=True)


if __name__ == '__main__':
    main()
