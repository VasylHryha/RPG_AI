"""Owner-authorized development drills; no judging entropy and no policy changes.
Commands: prepare, calibrate, run, report. Raw completions are immutable.
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
import shlex
import re
import subprocess
import sys
import time
V2 = pathlib.Path(__file__).resolve().parent.parent / 's4_shape_lab_v2'
V1 = pathlib.Path(__file__).resolve().parent.parent / 's4_shape_lab_v1'
sys.path.insert(0, str(V1))
from build import CPP, BINARY, admit, sha
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
RAW = HERE / 'raw'
ROLES = ('melee', 'ranged', 'artillery')
KINDS = ('brute', 'spitter', 'shaman')
DRILLS = ('D1', 'D2', 'D3', 'D4', 'D5', 'C1', 'C2', 'C3')
ARMS = ('v7', 'forcedP16')
SERIES_ARMS = (*ARMS, 'elite')
MAX_SECONDS = 3600  # Default local cap; never an identity input.
CAP_PATH = V1 / 'raw/LAB_CAP.json'
WORKERS = 6

def local_cap():
    if not CAP_PATH.exists():
        return dict(cap_seconds=MAX_SECONDS, cap_file=str(CAP_PATH.relative_to(CPP)),
                    cap_file_sha256=None, approved_by=None, date=None)
    # Hash exactly the bytes parsed, even if the local setting changes during a run.
    payload = CAP_PATH.read_bytes()
    setting = json.loads(payload)
    seconds = setting.get('cap_seconds')
    if type(seconds) is not int or seconds <= 0 or setting.get('approved_by') != 'owner' or not isinstance(setting.get('date'), str) or not setting['date']:
        raise RuntimeError('invalid owner local cap')
    return dict(cap_seconds=seconds, cap_file=str(CAP_PATH.relative_to(CPP)),
                cap_file_sha256=hashlib.sha256(payload).hexdigest(),
                approved_by=setting['approved_by'], date=setting['date'])

def verify_parent():
    # Runner controls live in v3; the v1 engine, inputs and passing checks stay sealed.
    parent = read(V1/'DECLARATION.json')
    if sha(V1/'raw/SEED_LEDGER.json') != parent['ledger_sha256'] or admit(BINARY) != parent['binary']:
        raise RuntimeError('parent entropy/binary drift')
    for name, digest in parent['source_hashes'].items():
        if sha(CPP/name) != digest:
            raise RuntimeError('parent input drift: '+name)
    checks = read(V1/'CHECKS.json')
    if checks['status'] != 'PASS' or checks['declaration_sha256'] != sha(V1/'DECLARATION.json'):
        raise RuntimeError('parent section-3 checks required')
    if list((V1/'raw').glob('D*_CLAIM.json')) or list((V1/'raw').glob('C[123]*_CLAIM.json')) or list((V1/'raw').glob('S10X_*')):
        raise RuntimeError('v3 transition requires no v1 drill/series fights')
    return checks

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
    parent = verify_parent()
    if sha(V2/'raw/SEED_LEDGER.json') != read(V2/'DECLARATION.json')['ledger_sha256']:
        raise RuntimeError('v2 entropy drift')
    RAW.mkdir(exist_ok=True)
    ledger_path = RAW / 'SEED_LEDGER.json'
    if ledger_path.exists():
        raise RuntimeError('unsealed entropy exists; preserve and investigate')
    # Only known development/validation inventories; never open any judging ledger.
    inventories = sorted(p for p in CPP.glob('S4*SEED*.json') if 'JUDG' not in p.name.upper()) + [V1/'raw/SEED_LEDGER.json', V2/'raw/SEED_LEDGER.json', CPP/'s4_v7/SEED_LEDGER.json', CPP/'s4_v7b/SEED_LEDGER.json', CPP/'s4_v7c/VALIDATION_SEED_LEDGER.json']
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
    inputs = [V2/'DECLARATION.json', V2/'raw/SEED_LEDGER.json', V1/'DECLARATION.json', V1/'CHECKS.json', CPP/'s4_v7c/THETA_ORIGIN.json', CPP/'s4_v7b/TUNING.json', CPP/'s4_v7b/TUNING_ANALYSIS.json',
              CPP/'s4_v7c/REGULAR_REQUEST_TEMPLATE.json', CPP/'s4_v7c/BUILD.json', CPP/'s4_v6_development_20261007_025024/B_best.json']
    if controller('v6')['params'] != read(inputs[-1])['resonator']:
        raise RuntimeError('v6 historical theta mismatch')
    decl = dict(parent_declaration_sha256=sha(V1/'DECLARATION.json'), parent_checks_sha256=sha(V1/'CHECKS.json'), schema=2, status='DEVELOPMENT_ONLY', pool=pool, workers=6, abilities_series='off', max_fights_series=10,
                ledger_sha256=sha(ledger_path), source_hashes={str(p.relative_to(CPP)):sha(p) for p in paths+inputs},
                binary=admit(BINARY), specification='SHAPE_LAB_SPEC sections 3-6, owner-approved 2026-10-08',
                arms=list(ARMS), v6_drills=['D4','D5'], series_arms=list(SERIES_ARMS),
                rules='strict elimination t<150; first non-win ends series',
                replay_limit_bytes=8_000_000, raw_storage='raw/ ignored by new local .gitignore')
    write(HERE/'DECLARATION.json', decl, exclusive=True)
    write(HERE/'CHECKS.json', dict(parent, declaration_sha256=sha(HERE/'DECLARATION.json'), inherited_from='s4_shape_lab_v1/CHECKS.json'), exclusive=True)
    write(HERE/'BUILD.json', dict(status='PASS', inherited_from='s4_shape_lab_v1/BUILD.json',
          identity=decl['binary'], parent_build_sha256=sha(V1/'BUILD.json'),
          note='Unchanged admitted native binary; no new build or capability fights.'), exclusive=True)
    print('Prepared development ledger', decl['ledger_sha256'])

def identity():
    verify_parent()
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
    preexisting = list(RAW.glob(tag+'_*')) or any(p.exists() for p in (RAW/(tag+'.stdout'), RAW/(tag+'.jsonl.gz')))
    try:
        return execute_cell(tag, req, meta, timeout, deadline)
    except (subprocess.TimeoutExpired, TimeoutError):
        if deadline is None or preexisting:
            raise
        # Preserve partial output and the exact request/claim. A cap interruption
        # is explicitly retryable; complete receipts are never moved or repeated.
        paths = list(RAW.glob(tag+'_*')) + [p for p in (RAW/(tag+'.stdout'), RAW/(tag+'.jsonl.gz')) if p.exists()]
        if not paths:
            raise TimeoutError('local lab cap; no fight started')
        if (RAW/(tag+'_COMPLETE.json')).exists():
            raise
        archive = RAW/'interrupted'/f'{tag}_{secrets.token_hex(8)}'
        archive.mkdir(parents=True)
        hashes = {p.name: sha(p) for p in paths}
        for p in paths:
            p.rename(archive/p.name)
        write(archive/'INTERRUPTION.json', dict(tag=tag, reason='local cap native timeout',
              retry_allowed=True, completed=False, files=hashes,
              declaration_sha256=sha(HERE/'DECLARATION.json')), exclusive=True)
        raise TimeoutError('local lab cap; partial fight preserved for resume')

def execute_cell(tag, req, meta, timeout=300, deadline=None):
    """Immutable completions; only explicit native cap interruptions are retryable."""
    if deadline is not None and time.monotonic() >= deadline:
        raise TimeoutError('local lab cap')
    identity()
    if deadline is not None and time.monotonic() >= deadline:
        raise TimeoutError('local lab cap')
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
        raise TimeoutError('local lab cap')
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

REPO_ROOT = CPP.parents[2].resolve()
HEAVY_PATTERN = r'(^|/)(tactics_lab_host|astelia_native[^ ]*)( |$)|[Pp]ython[^ ]* .*medium[^ ]*(runner|run|variants)'
SCRATCH_COMPONENT = '-Users-new-RiderProjects-ai-RPG-test'


def scoped_path(value, cwd=None):
    """Resolve path-valued argv entries, with exact directory boundaries."""
    path = pathlib.Path(value).expanduser()
    if not path.is_absolute():
        if cwd is None:
            return None
        path = pathlib.Path(cwd) / path
        # A bare PATH executable (e.g. python3) is not a file in the cwd.
        if '/' not in value and not path.exists():
            return None
    # The encoded Claude directory names are not ordinary repo symlinks.
    lexical = pathlib.Path(os.path.abspath(path))
    if SCRATCH_COMPONENT in lexical.parts and any(
            part.startswith('claude-') for part in lexical.parts):
        return dict(path=str(lexical), reason='this repository encoded Claude scratch directory')
    resolved = path.resolve()
    if resolved.is_relative_to(REPO_ROOT):
        return dict(path=str(resolved), reason='path resolves under this repository')
    return None


def classify_process(pid, command):
    try:
        argv = shlex.split(command)
    except ValueError:
        raise RuntimeError('cannot parse heavy process command')
    if not argv:
        raise RuntimeError('empty heavy process command')
    # Consider executable and path-valued arguments, including --input=/path.
    values = [arg.split('=', 1)[-1] if arg.startswith('-') and '=' in arg else arg for arg in argv]
    paths = [arg for arg in values if not arg.startswith('-') and not re.match(r'^[A-Za-z][A-Za-z0-9+.-]*://', arg)]
    for value in paths:
        if pathlib.Path(value).expanduser().is_absolute():
            match = scoped_path(value)
            if match:
                return dict(pid=pid, command=command, **match)
    executable = argv[0]
    if '/' not in executable and (executable == 'tactics_lab_host' or executable.startswith('astelia_native')):
        text_query = subprocess.run(['lsof', '-a', '-p', str(pid), '-d', 'txt', '-Fn'],
                                    capture_output=True, text=True, timeout=10)
        executable_paths = {line[1:] for line in text_query.stdout.splitlines()
                            if line.startswith('n/') and pathlib.Path(line[1:]).name == executable}
        # txt may include libraries; only the named native executable counts.
        if text_query.returncode != 0 or text_query.stderr.strip() or len(executable_paths) != 1:
            raise RuntimeError('heavy process executable path unavailable')
        executable_path = executable_paths.pop()
        match = scoped_path(executable_path)
        if match:
            return dict(pid=pid, command=command, **match)
        paths = [value for value in paths if value != executable]
    relative = [value for value in paths if not pathlib.Path(value).expanduser().is_absolute() and not value.startswith('-')]
    if relative:
        cwd_query = subprocess.run(['lsof', '-a', '-p', str(pid), '-d', 'cwd', '-Fn'],
                                   capture_output=True, text=True, timeout=10)
        cwd_paths = [line[1:] for line in cwd_query.stdout.splitlines() if line.startswith('n/')]
        if cwd_query.returncode != 0 or cwd_query.stderr.strip() or len(cwd_paths) != 1:
            raise RuntimeError('heavy process working directory unavailable')
        for value in relative:
            match = scoped_path(value, cwd_paths[0])
            if match:
                return dict(pid=pid, command=command, **match)
    return dict(pid=pid, command=command, reason='no executable or path-valued argument resolves under this repository or its encoded Claude scratch directory')


def process_gate(wait=True):
    while True:
        row = dict(utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                   scope=str(REPO_ROOT), pattern=HEAVY_PATTERN, matched=[], ignored_foreign=[], unresolved=[])
        try:
            p = subprocess.run(['pgrep','-fl',HEAVY_PATTERN], capture_output=True, text=True, timeout=10)
            row.update(returncode=p.returncode, stdout=p.stdout, stderr=p.stderr)
            if p.returncode == 1 and not p.stdout.strip() and not p.stderr.strip():
                row['status']='CLEAR'
            elif p.returncode == 0 and p.stdout.strip() and not p.stderr.strip():
                for line in p.stdout.splitlines():
                    pid, command = line.split(maxsplit=1)
                    if not pid.isdecimal() or int(pid) <= 0:
                        raise RuntimeError('invalid heavy process PID')
                    try:
                        item = classify_process(int(pid), command)
                    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
                        row['unresolved'].append(dict(pid=int(pid), command=command, reason=str(error)))
                        continue
                    row['matched' if 'path' in item else 'ignored_foreign'].append(item)
                row['status']='UNAVAILABLE' if row['unresolved'] else ('ACTIVE' if row['matched'] else 'CLEAR')
            else:
                row['status']='UNAVAILABLE'
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
            row.update(status='UNAVAILABLE', error=str(error))
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

def run_series(arm, index, deadline, first_only=False, cap_seconds=MAX_SECONDS):
    d=identity();ledger=read(RAW/'SEED_LEDGER.json');survivors=cohort();rows=[];streak=0
    for fight, draw in enumerate(ledger['draws'][index],1):
        initial=sorted(survivors,key=lambda u:u['cohort_id'])
        sides=standard(draw['seed'])
        sides[0]=placement(draw['seed'],initial)
        req=request(arm,doctrine(draw['tactic'],d['pool']),draw['seed'],sides=sides,abilities_off=True)
        meta=dict(group='S10X',arm=arm,series=index,fight=fight,tactic=draw['tactic'],units_before=len(initial),cohort_before=[u['cohort_id'] for u in initial])
        r=execute(f'S10X_{arm}_s{index:02d}_f{fight:02d}',req,meta,timeout=cap_seconds,deadline=deadline)
        # Map current role-slot ids to prior cohort in request order, independent of who died.
        ids_by_role={role:iter(range(start,start+n)) for role,start,n in zip(ROLES,(1,11,41),(10,30,10))}
        mapping={next(ids_by_role[u['role']]):u for u in initial}
        survivors=[mapping[u['id']] for u in r['survivors']]
        rows.append(dict(tag=r['tag'],**meta,win=r['stats']['win'],units_lost=len(initial)-len(survivors),units_after=len(survivors),cohort_after=[u['cohort_id'] for u in survivors]))
        if not r['stats']['win']:
            if first_only: return r
            break
        streak+=1
        if first_only: return r
    result=dict(arm=arm,series=index,streak=streak,fight_reached=len(rows),fights=rows)
    path=RAW/f'S10X_{arm}_s{index:02d}_SERIES.json'
    if path.exists():
        if read(path)!=result:raise RuntimeError('series receipt drift')
    else:write(path,result,exclusive=True)
    return result



def calibration_cells():
    # Exactly the first allocated cluster/orientation in every drill/arm/opponent cell.
    return [(tag, req, meta) for tag, req, meta in plan()
            if meta['cluster'] == 0 and meta['orientation'] == 0]


def sample_tags():
    return [tag for tag, _, _ in calibration_cells()] + [f'S10X_{arm}_s00_f01' for arm in SERIES_ARMS]


def require_checks():
    d = identity()
    checks = read(HERE/'CHECKS.json')
    expected = dict(read(V1/'CHECKS.json'), declaration_sha256=sha(HERE/'DECLARATION.json'), inherited_from='s4_shape_lab_v1/CHECKS.json')
    if checks != expected or sha(V1/'CHECKS.json') != d['parent_checks_sha256']:
        raise RuntimeError('inherited section-3 checks required')
    return d


def category(meta):
    return (meta['group'], meta['arm'], meta.get('opponent'))


def remaining_counts(records):
    counts = {}
    chains = {}
    for tag, _, meta in plan():
        if tag not in records:
            key = category(meta)
            counts[key] = counts.get(key, 0) + 1
    ledger = read(RAW/'SEED_LEDGER.json')
    for arm in SERIES_ARMS:
        for index, draws in enumerate(ledger['draws']):
            suffix = 0
            for fight in range(1, len(draws)+1):
                tag = f'S10X_{arm}_s{index:02d}_f{fight:02d}'
                if tag in records:
                    if not records[tag]['stats']['win']:
                        break
                else:
                    key = ('S10X', arm, None)
                    counts[key] = counts.get(key, 0) + 1
                    suffix += 1
            chains[arm] = max(chains.get(arm, 0), suffix)
    return counts, chains


def measured_projection(samples, records, wall_seconds, workers):
    if type(workers) is not int or not 1 <= workers <= 6 or not math.isfinite(wall_seconds) or wall_seconds <= 0:
        raise RuntimeError('invalid calibration wall time/workers')
    rates = {}
    work = 0
    for row in samples:
        seconds, simulated = row['seconds'], row['stats']['t_end']
        if not math.isfinite(seconds) or seconds <= 0 or not math.isfinite(simulated) or simulated <= 0:
            raise RuntimeError('invalid calibration fight timing')
        # Full-horizon equivalent; retain all spooling/metrics overhead, even for short fights.
        key = category(row['meta'])
        rates[key] = max(rates.get(key, 0), seconds * max(1, 150/simulated))
        work += seconds
    efficiency = min(1.0, work/(workers*wall_seconds))
    pending, chains = remaining_counts(records)
    if any(key not in rates for key in pending):
        raise RuntimeError('calibration missing work category')
    remaining_worker_seconds = sum(count*rates[key] for key, count in pending.items())
    # Separate drill and series phases; longest series chain limits parallel speedup.
    serial_series_bound = max((chains[arm]*rates[('S10X', arm, None)] for arm in SERIES_ARMS
                              if pending.get(('S10X', arm, None), 0)), default=0)
    drill_work = sum(n*rates[k] for k, n in pending.items() if k[0] != 'S10X')
    series_work = remaining_worker_seconds-drill_work
    projected = 1.2 * (drill_work/(workers*efficiency) + max(series_work/(workers*efficiency), serial_series_bound)) if pending else 0
    return dict(remaining_projected_seconds=projected, remaining_fights_max=sum(pending.values()),
                workers=workers, calibration_wall_seconds=wall_seconds,
                measured_utilization=efficiency, remaining_worker_seconds=remaining_worker_seconds,
                safety_multiplier=1.2, series_chain_bound_seconds=serial_series_bound,
                categories=[dict(group=k[0], arm=k[1], opponent=k[2], remaining=pending.get(k, 0),
                                 measured_full_horizon_seconds=v) for k, v in sorted(rates.items(), key=lambda item: str(item[0]))],
                method='Per drill/arm/opponent and per series arm: sample wall seconds scaled to 150 simulated seconds (no downward scaling). Sum remaining work, divide by actual workers and measured utilization (completed sample work / calibration wall / workers, at most 1). Separate drill/series phases; series time at least the longest remaining sequential suffix. Apply 20% margin. Stopped series excluded.',
                limits='Fixed first cells are development timing samples, not a runtime guarantee. Later tactics, survivors and host load can differ. Only native execution, spooling and initial metrics are projected; standalone report/replay rendering is outside the compute cap.')


def completed_records():
    return {p.name[:-len('_COMPLETE.json')]: verified_record(p.name[:-len('_COMPLETE.json')])
            for p in RAW.glob('*_COMPLETE.json')}


def calibration_receipt():
    receipt = read(HERE/'CALIBRATION.json')
    if receipt['status'] != 'MEASURED' or receipt['declaration_sha256'] != sha(HERE/'DECLARATION.json') or receipt['workers'] != WORKERS or receipt['sample_tags'] != sample_tags():
        raise RuntimeError('calibration identity/subset/worker drift')
    for tag, digest in receipt['sample_receipt_hashes'].items():
        if sha(RAW/(tag+'_COMPLETE.json')) != digest:
            raise RuntimeError('calibration sample receipt drift')
    if set(receipt['sample_receipt_hashes']) != set(receipt['sample_tags']):
        raise RuntimeError('calibration sample coverage drift')
    attempts = sorted(HERE.glob('CALIBRATE_ATTEMPT_*.json'))
    if not attempts or set(receipt['attempt_hashes']) != {p.name for p in attempts}:
        raise RuntimeError('calibration timing attempt coverage drift')
    wall = 0
    for path in attempts:
        if sha(path) != receipt['attempt_hashes'][path.name]:
            raise RuntimeError('calibration timing attempt drift')
        attempt = read(path)
        if attempt['status'] not in ('PASS', 'STOP') or attempt['kind'] != 'CALIBRATE' or attempt['workers'] != WORKERS or attempt['declaration_sha256'] != receipt['declaration_sha256'] or not math.isfinite(attempt['seconds']) or attempt['seconds'] <= 0:
            raise RuntimeError('invalid calibration timing attempt')
        wall += attempt['seconds']
    if wall != receipt['projection']['calibration_wall_seconds']:
        raise RuntimeError('calibration measured wall drift')
    return receipt


def compute_attempt(kind, cap, jobs):
    prior_attempts = [read(p) for p in HERE.glob('*_ATTEMPT_*.json')]
    if any(a['status'] == 'RUNNING' for a in prior_attempts):
        raise RuntimeError('unclosed compute attempt; preserve and investigate')
    process_gate()  # Repository-scoped host pgrep gate, before creating a compute attempt.
    start = time.monotonic()
    deadline = start + cap['cap_seconds']
    attempt = HERE/(kind+'_ATTEMPT_'+secrets.token_hex(8)+'.json')
    row = dict(status='RUNNING', kind=kind, workers=WORKERS, **cap,
               declaration_sha256=sha(HERE/'DECLARATION.json'),
               prior_seconds=sum(a['seconds'] for a in prior_attempts))
    write(attempt, row, exclusive=True)
    failure = None
    try:
        jobs(deadline)
    except BaseException as error:
        failure = type(error).__name__+': '+str(error)
        raise
    finally:
        row.update(status='STOP' if failure else 'PASS', error=failure, seconds=time.monotonic()-start)
        write(attempt, row)
    return row


def parallel_jobs(jobs):
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(fn, *args) for fn, args in jobs]
        try:
            for future in concurrent.futures.as_completed(futures):
                future.result()
        except BaseException:
            for future in futures:
                future.cancel()
            raise


def calibrate():
    require_checks()
    if (HERE/'CALIBRATION.json').exists():
        existing = calibration_receipt()
        records = completed_records()
        projection = measured_projection([records[tag] for tag in existing['sample_tags']], records,
                                         existing['projection']['calibration_wall_seconds'], WORKERS)
        if projection['remaining_projected_seconds'] > local_cap()['cap_seconds']:
            raise RuntimeError('measured projection exceeds local cap; Claude stops and asks owner')
        print('Existing calibration verified; no fights repeated')
        return
    cap = local_cap()
    def jobs(deadline):
        parallel_jobs([(execute, (tag, req, meta, cap['cap_seconds'], deadline))
                       for tag, req, meta in calibration_cells()] +
                      [(run_series, (arm, 0, deadline, True, cap['cap_seconds'])) for arm in SERIES_ARMS])
    compute_attempt('CALIBRATE', cap, jobs)
    attempts = sorted(HERE.glob('CALIBRATE_ATTEMPT_*.json'))
    wall = sum(read(p)['seconds'] for p in attempts)
    records = completed_records()
    tags = sample_tags()
    projection = measured_projection([records[tag] for tag in tags], records, wall, WORKERS)
    receipt = dict(status='MEASURED', workers=WORKERS, declaration_sha256=sha(HERE/'DECLARATION.json'),
                   attempt_hashes={p.name: sha(p) for p in attempts},
                   sample_tags=tags, sample_receipt_hashes={tag: sha(RAW/(tag+'_COMPLETE.json')) for tag in tags},
                   subset='First cluster 0/orientation 0 per drill/arm/opponent (56); first fight of series 0 per arm including full elite (3). Same allocated fights used by run.',
                   projection=projection, **cap)
    write(HERE/'CALIBRATION.json', receipt, exclusive=True)
    print(json.dumps(receipt, indent=2))
    if projection['remaining_projected_seconds'] > cap['cap_seconds']:
        raise RuntimeError('measured projection exceeds local cap; Claude stops and asks owner')


def run():
    require_checks()
    if not (HERE/'CALIBRATION.json').exists():
        raise RuntimeError('calibrate first; conservative serial projection is historical only')
    calibration = calibration_receipt()
    cap = local_cap()
    records = completed_records()
    projection = measured_projection([records[tag] for tag in calibration['sample_tags']], records,
                                     calibration['projection']['calibration_wall_seconds'], WORKERS)
    decision = dict(**cap, declaration_sha256=sha(HERE/'DECLARATION.json'),
                    calibration_sha256=sha(HERE/'CALIBRATION.json'), projection=projection)
    if projection['remaining_projected_seconds'] > cap['cap_seconds']:
        write(HERE/'RUN_GATE.json', dict(status='REFUSED', **decision))
        raise RuntimeError('measured remaining projection exceeds local cap; Claude stops and asks owner')
    write(HERE/'RUN_GATE.json', dict(status='READY', **decision))
    def jobs(deadline):
        parallel_jobs([(execute, (tag, req, meta, cap['cap_seconds'], deadline))
                       for tag, req, meta in plan() if tag not in records])
        parallel_jobs([(run_series, (arm, index, deadline, False, cap['cap_seconds']))
                       for arm in SERIES_ARMS for index in range(10)])
    try:
        attempt = compute_attempt('RUN', cap, jobs)
    except TimeoutError as error:
        write(HERE/'RUN.json', dict(status='PAUSED_CAP', error=str(error), **decision))
        print('Cap reached; completed fights reused by the next run; partial cap-timeout streams preserved')
        return
    write(HERE/'RUN.json', dict(status='DONE', seconds=attempt['seconds'], **decision))
    print('Run DONE; render with report')


def report():
    from report import render
    render()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('command', choices=('prepare', 'calibrate', 'run', 'report'))
    a = ap.parse_args()
    if a.command in ('calibrate', 'run') and os.environ.get('SHAPE_LAB_CAFFEINATED') != '1':
        os.environ['SHAPE_LAB_CAFFEINATED'] = '1'
        os.execv('/usr/bin/caffeinate', ['caffeinate', '-i', '-s', sys.executable, *sys.argv])
    globals()[a.command]()

if __name__ == '__main__':
    main()
