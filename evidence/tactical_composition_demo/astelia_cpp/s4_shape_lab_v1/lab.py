"""Owner-authorized development drills; no judging entropy and no policy changes.
Commands: prepare, checks, project, run, report. Raw completions are immutable.
"""
import argparse
import concurrent.futures
import copy
import gzip
import hashlib
import json
import math
import os
import pathlib
import random
import secrets
import subprocess
import sys
import time
from build import HERE, CPP, BINARY, admit, sha
RAW = HERE / 'raw'
ROLES = ('melee', 'ranged', 'artillery')
KINDS = ('brute', 'spitter', 'shaman')
DRILLS = ('D1', 'D2', 'D3', 'D4', 'D5', 'C1', 'C2', 'C3')
ARMS = ('v7', 'forcedP16')
SERIES_ARMS = (*ARMS, 'elite')
MAX_SECONDS = 3600

def read(p):
    return json.loads(pathlib.Path(p).read_text())

def write(p, value, exclusive=False):
    p = pathlib.Path(p)
    with p.open('x' if exclusive else 'w') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())

def catalog():
    # The delivered host's catalog operation creates no world.
    return json.loads(subprocess.check_output([str(CPP / 's4_v7c/build/astelia_native_v7'), '--catalog']))

def xorshift(seed):
    n = seed & 0xffffffff or 1
    while True:
        n ^= (n << 13) & 0xffffffff
        n ^= n >> 17
        n ^= (n << 5) & 0xffffffff
        n &= 0xffffffff
        yield n / 4294967296

def standard(seed, orientation=0):
    """Delivered 50v50 spawn order, including mirroring. Heading in radians."""
    rng = xorshift(seed)
    ours = []
    for role, kind, count, zone, band in zip(ROLES, KINDS, (10, 30, 10), ((240, 60), (150, 90), (80, 60)), (120, 150, 120)):
        for _ in range(count):
            ours.append(dict(role=role, kind=kind, position=dict(x=zone[0] + next(rng) * zone[1], y=400-band+next(rng)*2*band), heading=0, hp_fraction=1.0))
    enemy = copy.deepcopy(ours)
    for u in enemy:
        u['position']['x'] = 1400 - u['position']['x']
    if orientation:
        for u in ours + enemy:
            u['position']['x'] = 1400 - u['position']['x']
    return [ours, enemy]

def placement(seed, survivors, side=0, orientation=0):
    slots = {r: [u for u in standard(seed, orientation)[side] if u['role'] == r] for r in ROLES}
    used = {r: 0 for r in ROLES}
    out = []
    # Survivors sorted by original cohort identity, never by damage or tactical outcome.
    for s in sorted(survivors, key=lambda u: u['cohort_id']):
        r = s['role']
        u = copy.deepcopy(slots[r][used[r]])
        used[r] += 1
        u['kind'] = s['kind']
        u['hp_fraction'] = 1.0
        out.append(u)
    return out

def cohort():
    return [dict(cohort_id=i+1, role=u['role'], kind=u['kind']) for i, u in enumerate(standard(1)[0])]

def controller(arm):
    origin = read(CPP / 's4_v7c/THETA_ORIGIN.json')
    if arm in ARMS:
        return dict(controller=arm, skeleton='v7', params=origin['selected_params'])
    if arm == 'v6':
        return dict(controller='resonator', skeleton='v6', params=origin['historical_theta'])
    if arm in ('novice', 'regular', 'veteran', 'elite'):
        return dict(level=arm)
    if arm.startswith('dummy_'):
        return dict(controller=arm, skills=dict(abilities='off', lead='none', dodgeShots=False, dodgeShells=False, kite=0))
    raise ValueError('unknown arm: ' + arm)

def doctrine(name, pool):
    if name not in pool:
        raise ValueError('unknown doctrine')
    p = dict(level='regular', brain=name if name in ('alone', 'storm', 'wolfpack') else 'formation')
    if name not in ('alone', 'storm', 'wolfpack'):
        p['formation'] = dict(preset=name)
    return p

def request(arm, enemy, seed, orientation=0, sides=None, abilities_off=False):
    req = copy.deepcopy(read(CPP / 's4_v7c/REGULAR_REQUEST_TEMPLATE.json'))
    req['options'].update(seed=seed, swapSides=bool(orientation), duration=150)
    req['options']['ai'] = [controller(arm), copy.deepcopy(enemy)]
    req.update(trace=False, debug=False, killerTelemetry=True, decisionTrace=True)
    req['labScenario'] = dict(sides=sides if sides is not None else standard(seed, orientation))
    if abilities_off:
        req['labAbilities'] = 'off'
        for p in req['options']['ai']:
            p.setdefault('skills', {})['abilities'] = 'off'
    return req

def select(units, counts):
    return [copy.deepcopy(u) for r, n in counts.items() for u in [u for u in units if u['role'] == r][:n]]

def line(units, x, gap=22):
    for i, u in enumerate(units):
        u['position'] = dict(x=x, y=400 + (i-(len(units)-1)/2)*gap)

def drill_request(drill, arm, opponent, seed, orientation, pool):
    sides = standard(seed)
    enemy = controller('regular')
    if drill == 'D1':
        sides = [select(sides[0], {'artillery':10}), select(sides[1], {'ranged':20, 'artillery':10})]
        line(sides[0], 350, 45)
        line(sides[1], 850, 22)  # 500 px axial distance, within declared 450–600 band.
        enemy = controller('dummy_static_fire')
        enemy['params'] = {'ranged':0}
    elif drill == 'D2':
        sides = [select(sides[0], {'ranged':20, 'artillery':10}), select(sides[1], {'artillery':10})]
        enemy = controller('dummy_static_fire')
    elif drill == 'D3':
        sides = [select(sides[0], {'ranged':20, 'artillery':10}), select(sides[1], {'ranged':15})]
        enemy = controller('dummy_advance_fire')
    elif drill == 'D4':
        sides = [select(side, {'melee':10}) for side in sides]
    elif drill == 'D5':
        sides = [select(side, {'ranged':30}) for side in sides]
        line(sides[0], 500)
        line(sides[1], 750)
        enemy = controller('dummy_static_fire')
    elif drill in ('C1', 'C2'):
        enemy = controller('dummy_static' if drill == 'C1' else 'dummy_static_fire')
    elif drill == 'C3':
        enemy = controller('regular') if opponent == 'regular' else doctrine(opponent, pool)
    else:
        raise ValueError('unknown drill')
    if orientation:
        for u in sides[0]+sides[1]:
            u['position']['x'] = 1400-u['position']['x']
    return request(arm, enemy, seed, orientation, sides)

def prepare():
    if (HERE / 'DECLARATION.json').exists():
        identity()
        print('Existing lab declaration verified; entropy not replaced')
        return
    RAW.mkdir(exist_ok=True)
    ledger_path = RAW / 'SEED_LEDGER.json'
    if ledger_path.exists():
        raise RuntimeError('unsealed entropy exists; preserve and investigate')
    # Only known development/validation inventories; never open any judging ledger.
    inventories = sorted(p for p in CPP.glob('S4*SEED*.json') if 'JUDG' not in p.name.upper()) + [CPP/'s4_v7/SEED_LEDGER.json', CPP/'s4_v7b/SEED_LEDGER.json', CPP/'s4_v7c/VALIDATION_SEED_LEDGER.json']
    used = set()
    def collect(v):
        if type(v) is int:
            used.add(v)
        elif isinstance(v, dict):
            for x in v.values(): collect(x)
        elif isinstance(v, list):
            for x in v: collect(x)
    for p in inventories:
        if p.exists(): collect(read(p))
    entropy = secrets.token_hex(32)
    rng = random.Random(int(entropy, 16))
    def fresh():
        while True:
            n = rng.randrange(1, 2**32)
            if n not in used:
                used.add(n)
                return n
    ledger = dict(status='FRESH_DEVELOPMENT_ONLY', entropy_hex=entropy,
                  drills={d:[fresh() for _ in range(5)] for d in DRILLS}, series=[fresh() for _ in range(10)], checks=[fresh() for _ in range(8)],
                  inventories={str(p.relative_to(CPP)):sha(p) for p in inventories if p.exists()}, judging_opened=False)
    # Paired tactics and fight seeds, uniform discrete choice WITH replacement.
    pool = catalog()['POOL']
    if len(pool) != 19 or len(set(pool)) != 19:
        raise RuntimeError('catalog POOL drift')
    ledger['draws'] = []
    for seed in ledger['series']:
        run_rng = random.Random(seed)
        ledger['draws'].append([dict(tactic=pool[run_rng.randrange(19)], seed=fresh()) for _ in range(10)])
    write(ledger_path, ledger, exclusive=True)
    paths = [p for p in HERE.iterdir() if p.suffix in ('.py', '.h', '.cpp')] + [HERE/'.gitignore']
    inputs = [CPP/'s4_v7c/THETA_ORIGIN.json', CPP/'s4_v7b/TUNING.json', CPP/'s4_v7b/TUNING_ANALYSIS.json',
              CPP/'s4_v7c/REGULAR_REQUEST_TEMPLATE.json', CPP/'s4_v7c/BUILD.json', CPP/'s4_v6_development_20261007_025024/B_best.json']
    if controller('v6')['params'] != read(inputs[-1])['resonator']:
        raise RuntimeError('v6 historical theta mismatch')
    decl = dict(schema=1, status='DEVELOPMENT_ONLY', pool=pool, workers=6, abilities_series='off', max_fights_series=10,
                ledger_sha256=sha(ledger_path), source_hashes={str(p.relative_to(CPP)):sha(p) for p in paths+inputs},
                binary=admit(BINARY), specification='SHAPE_LAB_SPEC sections 3-6, owner-approved 2026-10-08',
                arms=list(ARMS), v6_drills=['D4','D5'], series_arms=list(SERIES_ARMS),
                rules='strict elimination t<150; first non-win ends series',
                replay_limit_bytes=8_000_000, raw_storage='raw/ ignored by new local .gitignore')
    write(HERE/'DECLARATION.json', decl, exclusive=True)
    print('Prepared development ledger', decl['ledger_sha256'])

def identity():
    d = read(HERE/'DECLARATION.json')
    if sha(RAW/'SEED_LEDGER.json') != d['ledger_sha256'] or admit(BINARY) != d['binary']:
        raise RuntimeError('lab entropy/binary drift')
    for name, h in d['source_hashes'].items():
        if sha(CPP/name) != h:
            raise RuntimeError('lab input drift: ' + name)
    return d

def verified_record(tag, req=None, meta=None):
    identity()
    r=read(RAW/(tag+'_COMPLETE.json'))
    request_path=RAW/(tag+'_request.json')
    claim_path=RAW/(tag+'_CLAIM.json')
    stderr_path=RAW/(tag+'_stderr.log')
    claim=read(claim_path)
    declaration_hash=sha(HERE/'DECLARATION.json')
    if req is not None and read(request_path)!=req or meta is not None and r['meta']!=meta:
        raise RuntimeError('completed cell request/metadata drift')
    if claim['meta']!=r['meta'] or claim['declaration_sha256']!=declaration_hash or r['declaration_sha256']!=declaration_hash:
        raise RuntimeError('completed cell declaration/claim drift')
    if r['claim_sha256']!=sha(claim_path) or r['request_sha256']!=sha(request_path) or claim['request_sha256']!=r['request_sha256']:
        raise RuntimeError('completed cell request/claim link drift')
    if r['raw_sha256']!=sha(RAW/(tag+'.jsonl.gz')) or r['stderr_sha256']!=sha(stderr_path) or read(stderr_path)!=r['native_metrics']:
        raise RuntimeError('completed cell raw/stderr drift')
    with gzip.open(RAW/(tag+'.jsonl.gz'),'rt') as f:
        for line in f: last=json.loads(line)
    if last!=r['summary'] or r['native_metrics']['executed_fights']!=1 or any(last['controllerFailures']):
        raise RuntimeError('completed cell native terminal drift')
    from metrics import measure
    stats,survivors=measure(RAW/(tag+'.jsonl.gz'))
    if stats!=r['stats'] or survivors!=r['survivors']:
        raise RuntimeError('completed cell derived measurement drift')
    return r

def execute(tag, req, meta, timeout=300, deadline=None):
    """One immutable request/claim/raw/receipt per cell; interrupted cells never auto-replay."""
    if deadline is not None and time.monotonic() >= deadline:
        raise TimeoutError('60-minute lab cap')
    identity()
    done = RAW/(tag+'_COMPLETE.json')
    if done.exists():
        return verified_record(tag,req,meta)
    if list(RAW.glob(tag+'_*')) or (RAW/(tag+'.jsonl.gz')).exists():
        raise RuntimeError('incomplete cell; never replay: '+tag)
    write(RAW/(tag+'_request.json'), req, exclusive=True)
    write(RAW/(tag+'_CLAIM.json'), dict(meta=meta, request_sha256=sha(RAW/(tag+'_request.json')), declaration_sha256=sha(HERE/'DECLARATION.json')), exclusive=True)
    start = time.monotonic()
    if deadline is not None:
        timeout = min(timeout, deadline-start)
    if timeout <= 0:
        raise TimeoutError('60-minute lab cap')
    # Spool native stdout/stderr to disk; never hold 150s telemetry in memory.
    stdout = RAW/(tag+'.stdout')
    stderr = RAW/(tag+'_stderr.log')
    with stdout.open('xb') as out, stderr.open('xb') as err:
        subprocess.run([str(BINARY),'--metrics'], input=(json.dumps(req)+'\n').encode(), stdout=out, stderr=err, timeout=timeout, check=True)
    terminal = None
    with stdout.open('rb') as src, (RAW/(tag+'.jsonl.gz')).open('xb') as dst, gzip.GzipFile(filename='', fileobj=dst, mode='wb', compresslevel=1, mtime=0) as gz:
        for b in src:
            gz.write(b)
            r = json.loads(b)
            if 'error' in r: raise RuntimeError(r['error'])
            if 'survivors' in r: terminal = r
    stdout.unlink()
    if terminal is None or any(terminal['controllerFailures']):
        raise RuntimeError('missing terminal/controller failure: '+tag)
    metrics = read(stderr)
    if metrics['executed_fights'] != 1:
        raise RuntimeError('native fight count mismatch')
    from metrics import measure
    stats, survivors = measure(RAW/(tag+'.jsonl.gz'))
    record = dict(tag=tag, meta=meta, summary=terminal, stats=stats, survivors=survivors, native_metrics=metrics,
                  seconds=time.monotonic()-start, raw_sha256=sha(RAW/(tag+'.jsonl.gz')),
                  request_sha256=sha(RAW/(tag+'_request.json')), claim_sha256=sha(RAW/(tag+'_CLAIM.json')),
                  declaration_sha256=sha(HERE/'DECLARATION.json'), stderr_sha256=sha(stderr))
    write(done, record, exclusive=True)
    return record

def process_gate(wait=True):
    while True:
        # Anchor executable names; don't accidentally match this pgrep's own argument.
        pattern = r'(^|/)(tactics_lab_host|astelia_native[^ ]*)( |$)|[Pp]ython[^ ]* .*medium[^ ]*(runner|run|variants)'
        p = subprocess.run(['pgrep','-fl',pattern], capture_output=True, text=True, timeout=10)
        row = dict(returncode=p.returncode, stdout=p.stdout, stderr=p.stderr, utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
        if p.returncode == 1 and not p.stdout.strip() and not p.stderr.strip():
            row['status']='CLEAR'
        elif p.returncode == 0 and p.stdout.strip() and not p.stderr.strip():
            row['status']='ACTIVE'
        else:
            row['status']='UNAVAILABLE'
        write(HERE/'PROCESS_GATE.json',row)
        if row['status']=='CLEAR': return row
        if row['status']=='UNAVAILABLE' or not wait: raise RuntimeError('process gate '+row['status']+'; no drills/series')
        print('Heavy job active; waiting 30 seconds',flush=True)
        time.sleep(30)

def plan():
    d=identity();ledger=read(RAW/'SEED_LEDGER.json')
    for drill in DRILLS:
        arms=(*ARMS,'v6') if drill in ('D4','D5') else ARMS
        opponents=['regular',*d['pool']] if drill=='C3' else [None]
        for arm in arms:
            for index, opponent in enumerate(opponents):
                for cluster, seed in enumerate(ledger['drills'][drill]):
                    for orientation in (0,1):
                        tag=f'{drill}_{arm}_p{index:02d}_c{cluster}_o{orientation}'
                        meta=dict(group=drill,arm=arm,opponent=opponent,cluster=cluster,orientation=orientation)
                        yield tag,drill_request(drill,arm,opponent,seed,orientation,d['pool']),meta

def project():
    checks=read(HERE/'CHECKS.json')
    if checks['status']!='PASS' or checks['declaration_sha256']!=sha(HERE/'DECLARATION.json'):
        raise RuntimeError('section-3 checks required')
    # Serial projection gives no assumed sixfold speedup. Historical full-elite timings
    # are scaled to 150s and padded 10x, explicitly an estimate rather than a live bound.
    cost=checks['compatibility_seconds'] * max(1,150/checks['compatibility_t'])
    total=sum(1 for _ in plan())
    historical=CPP/'native_benchmark_r1/benchmark.json'
    samples=read(historical)['groups']['elite']['samples']['cpp']
    elite_step=max(s['wall_seconds']/s['execution']['executed_steps'] for s in samples)
    elite_fight=4501*elite_step*10 + cost
    non_elite=(total+200)*cost
    postprocess=(total+300)*cost*2
    full=non_elite+100*elite_fight+postprocess+120
    projection=dict(status='ESTIMATED', drill_fights=total, series_fights_max=300, workers_max=6,
                    observed_v7_seconds_per_fight=checks['compatibility_seconds'],
                    full_duration_v7_proxy_seconds=cost, non_elite_serial_proxy_seconds=non_elite,
                    elite_fights_max=100, elite_seconds_per_fight_estimate=elite_fight,
                    elite_estimate_source=str(historical.relative_to(CPP)),elite_estimate_source_sha256=sha(historical),
                    elite_historical_max_seconds_per_step=elite_step,elite_margin_multiplier=10,
                    total_projected_seconds=full, total_projected_minutes=full/60,
                    postprocessing_estimate_seconds=postprocess, analysis_reserve_seconds=120,
                    assumption='Serial costs; no worker speedup. Full-output compatibility scaled to 150s. Historical full-elite planning rate scaled to 4501 ticks, 10x margin; two more full-stream analysis passes plus 120s reserve.',
                    limits='Historical elite benchmark is a different engine revision/short fights, without observer output. Current full-elite series and 6-worker throughput have not been timed; this is a conservative planning estimate, not a measured upper bound.',
                    cap_seconds=MAX_SECONDS)
    write(HERE/'PROJECTION.json',projection)
    print(json.dumps(projection,indent=2))
    return projection

def run_series(arm, index, deadline):
    d=identity();ledger=read(RAW/'SEED_LEDGER.json');survivors=cohort();rows=[];streak=0
    for fight, draw in enumerate(ledger['draws'][index],1):
        initial=sorted(survivors,key=lambda u:u['cohort_id'])
        sides=standard(draw['seed'])
        sides[0]=placement(draw['seed'],initial)
        req=request(arm,doctrine(draw['tactic'],d['pool']),draw['seed'],sides=sides,abilities_off=True)
        meta=dict(group='S10X',arm=arm,series=index,fight=fight,tactic=draw['tactic'],units_before=len(initial),cohort_before=[u['cohort_id'] for u in initial])
        r=execute(f'S10X_{arm}_s{index:02d}_f{fight:02d}',req,meta,timeout=MAX_SECONDS,deadline=deadline)
        # Map current role-slot ids to prior cohort in request order, independent of who died.
        ids_by_role={role:iter(range(start,start+n)) for role,start,n in zip(ROLES,(1,11,41),(10,30,10))}
        mapping={next(ids_by_role[u['role']]):u for u in initial}
        survivors=[mapping[u['id']] for u in r['survivors']]
        rows.append(dict(tag=r['tag'],**meta,win=r['stats']['win'],units_lost=len(initial)-len(survivors),units_after=len(survivors),cohort_after=[u['cohort_id'] for u in survivors]))
        if not r['stats']['win']: break
        streak+=1
    result=dict(arm=arm,series=index,streak=streak,fight_reached=len(rows),fights=rows)
    path=RAW/f'S10X_{arm}_s{index:02d}_SERIES.json'
    if path.exists():
        if read(path)!=result:raise RuntimeError('series receipt drift')
    else:write(path,result,exclusive=True)
    return result

def run():
    identity()
    projection=project()
    if projection['total_projected_seconds'] is None or projection['total_projected_seconds']>MAX_SECONDS:
        raise RuntimeError('full projection exceeds 60 minutes; stop after section-3 checks; Claude asks owner')
    process_gate()
    attempts=[read(p) for p in HERE.glob('RUN_ATTEMPT_*.json')]
    if any(a['status']=='RUNNING' for a in attempts):
        raise RuntimeError('unclosed compute attempt; preserve and stop')
    prior=sum(a['seconds'] for a in attempts)
    if prior+projection['total_projected_seconds']>MAX_SECONDS:
        raise RuntimeError('remaining cumulative budget insufficient; Claude asks owner')
    start=time.monotonic();deadline=start+MAX_SECONDS-prior
    attempt=HERE/('RUN_ATTEMPT_'+secrets.token_hex(8)+'.json')
    write(attempt,dict(status='RUNNING',prior_seconds=prior,declaration_sha256=sha(HERE/'DECLARATION.json')),exclusive=True)
    failure=None
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
            futures=[]
            for tag,req,meta in plan():
                futures.append(ex.submit(execute,tag,req,meta,MAX_SECONDS,deadline))
            for f in concurrent.futures.as_completed(futures):f.result()
            futures=[ex.submit(run_series,arm,i,deadline) for arm in SERIES_ARMS for i in range(10)]
            for f in concurrent.futures.as_completed(futures):f.result()
        if time.monotonic()>=deadline:raise TimeoutError('lab compute cap')
        report()
        if time.monotonic()>=deadline:raise TimeoutError('lab analysis exceeded compute cap')
        write(HERE/'RUN.json',dict(status='DONE',seconds=time.monotonic()-start,prior_seconds=prior))
    except BaseException as e:
        failure=type(e).__name__+': '+str(e)
        raise
    finally:
        write(attempt,dict(status='STOP' if failure else 'PASS',error=failure,seconds=time.monotonic()-start,prior_seconds=prior,declaration_sha256=sha(HERE/'DECLARATION.json')))


def report():
    from report import render
    render()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('prepare','checks','project','run','report'));a=ap.parse_args()
    if a.command in ('checks','run') and os.environ.get('SHAPE_LAB_CAFFEINATED')!='1':
        os.environ['SHAPE_LAB_CAFFEINATED']='1'
        os.execv('/usr/bin/caffeinate',['caffeinate','-i','-s',sys.executable,*sys.argv])
    try:
        if a.command=='checks':
            from checks import checks
            checks()
        else:globals()[a.command]()
    except Exception:
        if (HERE/'DECLARATION.json').exists():report()
        raise

if __name__=='__main__':
    main()
