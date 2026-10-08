"""V6 shared-base development tooling, staged and paired; no acceptance decisions."""
import argparse
import concurrent.futures
import contextlib
import fcntl
import gzip
import hashlib
import json
import math
import os
import pathlib
import random
import re
import secrets
import shlex
import subprocess
import sys
import time
HERE = pathlib.Path(__file__).resolve().parent
CPP = HERE.parent
sys.path.insert(0,str(HERE))
from build import BINARY
from receipt_identity_r2 import admit, sha
sys.path.insert(0,str(HERE))
from requests import ARMS, ROLES, cohort, drill_request, series_request, comparison_arms, groups
from metrics import measure
RAW = HERE/'raw'
V1 = CPP/'s4_shape_lab_v1'
V3 = CPP/'s4_shape_lab_v3'
ADAPTER = CPP/'s4_react_adapter_v1'
MAX_SECONDS = 3600
CAP_PATH = V1/'raw/LAB_CAP.json'
WORKERS = 6
LOOKS = (50,100,200)
SERIES_COUNT = 10
SELECTED_ARM = "V2"

def scope(stage):return stage+"_"+SELECTED_ARM
def selected_arms():return comparison_arms(SELECTED_ARM)
def timing():
    declaration=identity();p=HERE/'TIMING_SELECTION.json'
    return read(p)['timing'] if p.exists() else declaration['timing']

def configure_timing(mode,k,radius,note):
    declaration=identity()
    setting=dict(mode=mode,k=k,radius=radius)
    if mode not in ('base','central_sync','battery_oscillator') or k not in (.5,1,2) or radius not in (200,400,-1) or not note.strip():raise ValueError('declared timing and actual V1 reading required')
    receipt=dict(timing=setting,note=note,declaration_sha256=sha(HERE/'DECLARATION.json'))
    p=HERE/'TIMING_SELECTION.json'
    if p.exists():
        if read(p)!=receipt:raise RuntimeError('common timing selection immutable')
        return
    if list(RAW.glob('*_CLAIM.json')):raise RuntimeError('fights already opened; common timing cannot change')
    write(p,receipt,exclusive=True)

def seal_timing():
    if not (HERE/'TIMING_SELECTION.json').exists():configure_timing('base',1,400,'Default declared fire-when-ready; selected before first fight')


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


def read(p):
    return json.loads(pathlib.Path(p).read_text())

def write(p, value, exclusive=False):
    p = pathlib.Path(p)
    with p.open('x' if exclusive else 'w') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


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
    if claim['meta']!=r['meta'] or claim['declaration_sha256']!=declaration_hash or r['declaration_sha256']!=declaration_hash or claim.get('timing_sha256')!=sha(HERE/'TIMING_SELECTION.json') or r.get('timing_sha256')!=sha(HERE/'TIMING_SELECTION.json'):
        raise RuntimeError('completed cell declaration/claim drift')
    if r['claim_sha256']!=sha(claim_path) or r['request_sha256']!=sha(request_path) or claim['request_sha256']!=r['request_sha256']:
        raise RuntimeError('completed cell request/claim link drift')
    if r['raw_sha256']!=sha(RAW/(tag+'.jsonl.gz')) or r['stderr_sha256']!=sha(stderr_path) or read(stderr_path)!=r['native_metrics']:
        raise RuntimeError('completed cell raw/stderr drift')
    receipt_path=RAW/(tag+'_COMPLETE.json')
    continuation=read(HERE/'E1_REPORTING_R2.json')
    if tag in continuation['inherited_receipts']:
        if sha(receipt_path)!=continuation['inherited_receipts'][tag]:
            raise RuntimeError('inherited measurement receipt drift')
    else:
        seal=read(RAW/(tag+'_VERIFIED_R2.json'))
        if seal!=dict(receipt_sha256=sha(receipt_path),metrics_sha256=sha(HERE/'metrics.py')):
            raise RuntimeError('completion measurement seal drift')
    # Existing stats were measured by the original metrics.py; continuation
    # hashes bind those receipt bytes, and the checks above bind raw bytes.
    if r['tag']!=tag or r['native_metrics']['executed_fights']!=1 or any(r['summary']['controllerFailures']):
        raise RuntimeError('completed cell native terminal drift')
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
    write(RAW/(tag+'_CLAIM.json'), dict(meta=meta, timing_sha256=sha(HERE/'TIMING_SELECTION.json'), request_sha256=sha(RAW/(tag+'_request.json')), declaration_sha256=sha(HERE/'DECLARATION.json')), exclusive=True)
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
    record = dict(tag=tag, timing_sha256=sha(HERE/'TIMING_SELECTION.json'), meta=meta, summary=terminal, stats=stats, survivors=survivors, native_metrics=metrics,
                  seconds=time.monotonic()-start, raw_sha256=sha(RAW/(tag+'.jsonl.gz')),
                  request_sha256=sha(RAW/(tag+'_request.json')), claim_sha256=sha(RAW/(tag+'_CLAIM.json')),
                  declaration_sha256=sha(HERE/'DECLARATION.json'), stderr_sha256=sha(stderr))
    write(done, record, exclusive=True)
    write(RAW/(tag+'_VERIFIED_R2.json'),dict(receipt_sha256=sha(done),metrics_sha256=sha(HERE/'metrics.py')),exclusive=True)
    return record

REPO_ROOT = CPP.parents[2].resolve()
HEAVY_PATTERN = r'(^|/)(tactics_lab_host|tactics_react_host[^ ]*|astelia_native[^ ]*)( |$)|[Pp]ython[^ ]* .*medium[^ ]*(runner|run|variants)'
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
    if '/' not in executable and (executable == 'tactics_lab_host' or executable.startswith(('tactics_react_host','astelia_native'))):
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



def prepare():
    if (HERE/'DECLARATION.json').exists():
        identity()
        print('Existing preparation verified; no entropy replaced')
        return
    parent_id = admit(ADAPTER/'build/tactics_react_host')
    if read(ADAPTER/'BUILD.json')['identity'] != parent_id or read(ADAPTER/'CHECKS.json')['status']!='PASS':
        raise RuntimeError('admitted adapter and passing capability checks required')
    if read(HERE/'TESTS.json')['status']!='PASS' or read(HERE/'NATIVE_FIXTURES.json')['status']!='PASS':raise RuntimeError('focused native/Python fixtures required before prepare')
    binary = admit(BINARY)
    if read(HERE/'BUILD.json')['identity']!=binary:
        raise RuntimeError('v6 build receipt mismatch')
    pool = json.loads(subprocess.check_output([str(BINARY),'--catalog']))['POOL']
    if len(pool)!=19 or len(set(pool))!=19:
        raise RuntimeError('POOL must contain 19 distinct tactics')
    inventories = sorted(p for p in CPP.glob('S4*SEED*.json') if 'JUDG' not in p.name.upper())
    inventories += [CPP/f's4_shape_lab_v{v}/raw/SEED_LEDGER.json' for v in (1,2,3,4,5)]
    inventories += [CPP/'s4_v7/SEED_LEDGER.json',CPP/'s4_v7b/SEED_LEDGER.json',CPP/'s4_v7c/VALIDATION_SEED_LEDGER.json']
    used = set()
    def collect(value):
        if type(value) is int:
            used.add(value)
        elif isinstance(value,dict):
            for v in value.values(): collect(v)
        elif isinstance(value,list):
            for v in value: collect(v)
    for path in inventories:
        if path.exists(): collect(read(path))
    entropy = secrets.token_hex(32)
    rng = random.Random(int(entropy,16))
    def fresh():
        while True:
            seed = rng.randrange(1,2**32)
            if seed not in used:
                used.add(seed)
                return seed
    # No controller RNG is consulted. Persist ALL future map/tactic draws now.
    mechanism = {g:[dict(seed=fresh(),orientation=i%2,group=g,tactic=('regular','storm','line anvil')[i%3] if g=='RD' else None) for i in range(10 if g in ('D1','V2D2') else 20)] for g in ('D1','V2D2','D5','RD')}
    opponents = ['regular',*pool]
    outcome = [dict(seed=fresh(),orientation=(i//20)%2,tactic=opponents[i%20]) for i in range(200)]
    draws = [[dict(seed=fresh(),orientation=s%2,tactic=pool[rng.randrange(19)])
              for _ in range(10)] for s in range(SERIES_COUNT)]
    ledger = dict(status='FRESH_DEVELOPMENT_ONLY',entropy_hex=entropy,judging_opened=False,
                  mechanism=mechanism,outcome=outcome,draws=draws,
                  inventories={str(p.relative_to(CPP)):sha(p) for p in inventories if p.exists()})
    RAW.mkdir(exist_ok=True)
    write(RAW/'SEED_LEDGER.json',ledger,exclusive=True)
    inputs = [HERE/'.gitignore',HERE/'README.md',HERE/'BUILD.json',HERE/'TIMING_CONFIG.json',ADAPTER/'BUILD.json',ADAPTER/'CHECKS.json', ADAPTER/'requests.py', CPP/'build_admission.py', CPP/'s4_shape_lab_v1/build.py', CPP/'s4_shape_lab_v2/lab.py', CPP/'s4_v7c/THETA_ORIGIN.json', CPP/'s4_v7c/REGULAR_REQUEST_TEMPLATE.json']
    sources = sorted(HERE.glob('*.py'))+sorted(HERE.glob('*.cpp'))+sorted(HERE.glob('*.h'))+sorted((HERE/'frozen').glob('*'))+inputs+[HERE/'PLANNER_STATES.json']
    shared_timing=read(HERE/'TIMING_CONFIG.json')
    if set(shared_timing)!={'mode','k','radius'} or shared_timing['mode'] not in ('base','central_sync','battery_oscillator') or shared_timing['k'] not in (.5,1,2) or shared_timing['radius'] not in (200,400,-1):raise RuntimeError('invalid common timing slot')
    declaration = dict(schema=6,status='DEVELOPMENT_ONLY',pool=pool,arms=list(ARMS),workers=WORKERS, timing=shared_timing,
        mechanism_pairs={'V2':20,'E1':20,'R1':20,'E1+R1':20}, outcome_looks=list(LOOKS),series_count=SERIES_COUNT,series_fights_max=10,series_abilities='off',
        ledger_sha256=sha(RAW/'SEED_LEDGER.json'),source_hashes={str(p.relative_to(CPP)):sha(p) for p in sources},binary=binary,adapter_binary=parent_id,
        replay_selection='C3 pairs 0/1 per arm and S10X series 0 per arm only',
        rules='strict elimination t<150; first non-win ends series; shared draw schedule and arm-specific healed survivors',
        sizing='One paired multi-arm batch. Shared immutable base receipts. Per candidate 20 mechanism pairs, then 50/100/200 C3 total pairs across all 20 tactic cells; ten paired series.',
        diagnostics='observer-v1 + light shape audit; no heavy collectors',labels={a:'script/search' if a=='V2' else 'script' for a in ARMS},
        categories={'V2':'damage','E1':'damage','R1':'survival','E1+R1':'survival; incremental R1 versus E1'},
        contrasts={'V2':'V2 minus base','E1':'E1 minus base','R1':'R1 minus base (diagnostic)','E1+R1':'E1+R1 minus E1 (primary active-range rotation); versus base secondary'},
        planner_options=dict(artyFire='plan',artyModel='simple',artyRollout=False,artyRobust=.5,artyHerd=0,artyBattery=True,artyFollow=False),
        rotation=dict(margin_damage=1,max_retreat_px=100,participation_horizon_s=2,edge_margin_px=24),
        reading=['Mechanism must activate and move declared metric at 20 pairs; else park.', 'Own deaths over ALL paired fights and kills per own death are decision axes; single-fight wins descriptive.', 'C3: stop clearly better/worse or invisible at <=200 pairs; no extra sampling.', 'Rotation primary against E1; require active in-range ranged evidence.', 'Series: paired streak primary; survival first among competing slots.'])
    write(HERE/'DECLARATION.json',declaration,exclusive=True)
    write(HERE/'PREPARE.json',dict(status='PREPARED',fights=0,ledger_sha256=declaration['ledger_sha256'],
                                  declaration_sha256=sha(HERE/'DECLARATION.json'),**local_cap()),exclusive=True)
    print('Prepared v6; zero fights')


def identity():
    revision=read(HERE/'E1_REPORTING_R2.json')
    if sha(HERE/'DECLARATION.json')!=revision['declaration_sha256']:raise RuntimeError('R2 inherited declaration drift')
    for name,digest in revision['tool_hashes'].items():
        if sha(HERE/name)!=digest:raise RuntimeError('R2 reporting tool drift: '+name)
    declaration = read(HERE/'DECLARATION.json')
    if sha(RAW/'SEED_LEDGER.json')!=declaration['ledger_sha256'] or admit(BINARY)!=declaration['binary']:
        raise RuntimeError('lab entropy/binary drift')
    if admit(ADAPTER/'build/tactics_react_host')!=declaration['adapter_binary']:
        raise RuntimeError('adapter identity drift')
    for name,digest in declaration['source_hashes'].items():
        original=HERE/'e1_fix_diagnostics/original/lab.py' if name=='s4_shape_lab_v6/lab.py' else CPP/name
        if sha(original)!=digest:
            raise RuntimeError('lab input drift: '+name)
    selection=HERE/'TIMING_SELECTION.json'
    if selection.exists():
        chosen=read(selection)
        if chosen['declaration_sha256']!=sha(HERE/'DECLARATION.json') or chosen['timing']['mode'] not in ('base','central_sync','battery_oscillator') or chosen['timing']['k'] not in (.5,1,2) or chosen['timing']['radius'] not in (200,400,-1):raise RuntimeError('timing selection identity drift')
    manifest = read(BINARY.with_suffix('.build.json'))
    for path,digest in manifest['reused_object_sha256'].items():
        if sha(pathlib.Path(path))!=digest:
            raise RuntimeError('reused native object drift')
    return declaration


@contextlib.contextmanager
def execution_lock():
    # Hold across admission/projection/work, so two v6 runners cannot both pass.
    RAW.mkdir(exist_ok=True)
    with (RAW/'EXECUTION.lock').open('a') as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('another v6 execution owns the local process lock')
        try:
            yield
        finally:
            fcntl.flock(lock,fcntl.LOCK_UN)


def plan(stage,look=200):
    declaration=identity();ledger=read(RAW/'SEED_LEDGER.json')
    if stage not in ('mechanism','outcome'):raise ValueError('invalid stage')
    draws=[d for g in groups(SELECTED_ARM) for d in ledger['mechanism'][g]] if stage=='mechanism' else ledger['outcome'][:look]
    for pair,draw in enumerate(draws):
        group=draw['group'] if stage=='mechanism' else 'C3'
        # Group-local pair indexes ensure identical shared base request/meta
        # identity when another arm later reads/reuses this drill.
        local_pair=ledger['mechanism'][group].index(draw) if stage=='mechanism' else pair
        for arm in selected_arms():
            req=drill_request(group,arm,draw.get('tactic'),draw['seed'],draw['orientation'],declaration['pool'],timing())
            meta=dict(group=group,stage=stage,arm=arm,pair=local_pair,pair_key=f'{group}:{local_pair}',seed=draw['seed'],orientation=draw['orientation'],opponent=draw.get('tactic'),units_before=len(req['labScenario']['sides'][0]))
            yield f'{group}_{arm}_p{local_pair:03d}',req,meta


def run_series(arm,index,deadline,first_only=False,cap_seconds=MAX_SECONDS):
    declaration = identity()
    draws = read(RAW/'SEED_LEDGER.json')['draws'][index]
    survivors = cohort()
    rows,streak = [],0
    for fight,draw in enumerate(draws,1):
        initial = sorted(survivors,key=lambda u:u['cohort_id'])
        meta = dict(group='S10X',stage='series',arm=arm,series=index,fight=fight,
                    tactic=draw['tactic'],seed=draw['seed'],orientation=draw['orientation'],
                    units_before=len(initial),roles_before={role:sum(u['role']==role for u in initial) for role in ROLES},
                    cohort_before=[u['cohort_id'] for u in initial])
        req = series_request(arm,draw,declaration['pool'],initial,timing())
        record = execute(f'S10X_{arm}_s{index:02d}_f{fight:02d}',req,meta,cap_seconds,deadline)
        slots = {role:iter(range(start,start+n)) for role,start,n in zip(ROLES,(1,11,41),(10,30,10))}
        mapping = {next(slots[u['role']]):u for u in initial}
        survivors = [mapping[u['id']] for u in record['survivors']]
        rows.append(dict(tag=record['tag'],**meta,win=record['stats']['win'],
                         units_lost=len(initial)-len(survivors),units_after=len(survivors),
                         cohort_after=[u['cohort_id'] for u in survivors]))
        if first_only:
            return record
        if not record['stats']['win']:
            break
        streak += 1
    result = dict(arm=arm,series=index,streak=streak,fight_reached=len(rows),fights=rows)
    path = RAW/f'S10X_{arm}_s{index:02d}_SERIES.json'
    if path.exists():
        if read(path)!=result:
            raise RuntimeError('series receipt drift')
    else:
        write(path,result,exclusive=True)
    return result


def records_for(stage,arm=None,look=None):
    arms=comparison_arms(arm) if arm else ARMS
    records={}
    paths={p.name.removesuffix('_COMPLETE.json'):p for p in RAW.glob('*_COMPLETE.json')}
    continuation=read(HERE/'E1_REPORTING_R2.json') if (HERE/'E1_REPORTING_R2.json').exists() else {}
    inherited_order=continuation.get('receipt_order',[])
    order=[tag for tag in inherited_order if tag in paths]+[tag for tag in paths if tag not in inherited_order]
    for tag in order:
        p=paths[tag]
        meta=read(p)['meta']
        if meta['stage']!=stage or meta['arm'] not in arms:continue
        if stage=='mechanism' and arm and meta['group'] not in groups(arm):continue
        if stage=='outcome' and look is not None and meta['pair']>=look:continue
        tag=p.name.removesuffix('_COMPLETE.json')
        records[tag]=verified_record(tag)
    return records


def samples_for(stage):
    if stage=='series':
        return [f'S10X_{arm}_s00_f01' for arm in selected_arms()]
    # Mechanism: first pair. C3: one existing pair per opponent; all within look 50.
    return [tag for tag,_,meta in plan(stage,50) if (meta['pair']==0 if stage=='mechanism' else meta['pair']<20)]


def category(meta):
    return (meta['arm'],meta['group'] if meta['stage']=='mechanism' else meta.get('opponent'))


def projection(stage,look,records,samples,wall):
    if not math.isfinite(wall) or wall<=0:
        raise RuntimeError('invalid measured calibration time')
    rates = {}
    work = 0.0
    for record in samples:
        seconds,t = record['seconds'],record['stats']['t_end']
        if not math.isfinite(seconds) or seconds<=0 or not math.isfinite(t) or t<=0:
            raise RuntimeError('invalid calibration sample timing')
        rates[category(record['meta'])] = max(rates.get(category(record['meta']),0),seconds*max(1,150/t))
        work += seconds
    efficiency = min(1,work/(WORKERS*wall))
    remaining,chain = {},0.0
    if stage!='series':
        for tag,_,meta in plan(stage,look):
            if tag not in records:
                key = category(meta)
                remaining[key] = remaining.get(key,0)+1
    else:
        for arm in selected_arms():
            for index in range(SERIES_COUNT):
                suffix=0
                for fight in range(1,11):
                    tag=f'S10X_{arm}_s{index:02d}_f{fight:02d}'
                    if tag in records:
                        if not records[tag]['stats']['win']: break
                    else:
                        remaining[(arm,None)] = remaining.get((arm,None),0)+1
                        suffix+=1
                chain=max(chain,suffix*rates[(arm,None)])
    if any(k not in rates for k in remaining):
        raise RuntimeError('missing calibration category')
    estimate=sum(n*rates[k] for k,n in remaining.items())/(WORKERS*efficiency)
    return dict(remaining_projected_seconds=1.2*max(estimate,chain),remaining_fights_max=sum(remaining.values()),
                workers=WORKERS,measured_utilization=efficiency,calibration_wall_seconds=wall,
                safety_multiplier=1.2,series_chain_bound_seconds=chain,
                method='Measured per arm/opponent full-150s equivalent, six-worker utilization; series suffix bound; 20% margin. Not a guarantee.')


def parallel_jobs(jobs):
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures=[executor.submit(fn,*args) for fn,args in jobs]
        try:
            for future in concurrent.futures.as_completed(futures): future.result()
        except BaseException:
            for future in futures: future.cancel()
            raise


def compute_attempt(kind,stage,cap,jobs):
    prior=[read(p) for p in HERE.glob('*_ATTEMPT_*.json')]
    if any(p['status']=='RUNNING' for p in prior):
        raise RuntimeError('unclosed compute attempt; preserve and investigate')
    process_gate()
    seal_timing()
    start=time.monotonic()
    path=HERE/f'{kind}_{scope(stage)}_ATTEMPT_{secrets.token_hex(8)}.json'
    row=dict(status='RUNNING',kind=kind,stage=stage,workers=WORKERS,
             declaration_sha256=sha(HERE/'DECLARATION.json'),prior_seconds=sum(p['seconds'] for p in prior),**cap)
    write(path,row,exclusive=True)
    error=None
    try:
        jobs(start+cap['cap_seconds'])
    except BaseException as failure:
        error=type(failure).__name__+': '+str(failure)
        raise
    finally:
        row.update(status='STOP' if error else 'PASS',error=error,seconds=time.monotonic()-start)
        write(path,row)
    return row


def stage_summary(stage,look=None,records=None):
    from report_r2 import stage_data
    path=HERE/(f'OUTCOME_{SELECTED_ARM}_LOOK_{look}.json' if stage=='outcome' else f'{scope(stage).upper()}_SUMMARY.json')
    if stage=='mechanism' and SELECTED_ARM=='E1':path=HERE/'MECHANISM_E1_SUMMARY_R2.json'
    return path,stage_data(stage,look,arm=SELECTED_ARM,records=records)


def require_review(stage,look=None):
    path,summary=stage_summary(stage,look)
    if not path.exists() or read(path)!=summary or not summary['complete']:
        raise RuntimeError('completed stage summary required before Claude reads it')
    review_path=HERE/(f'OUTCOME_{SELECTED_ARM}_LOOK_{look}_READ.json' if stage=='outcome' else f'{scope(stage).upper()}_READ.json')
    review=read(review_path)
    if review['summary_sha256']!=sha(path) or review['declaration_sha256']!=sha(HERE/'DECLARATION.json') or review['reader']!='Claude':
        raise RuntimeError('Claude read receipt identity mismatch')
    return review


def ensure_stage(stage,look):
    identity()
    if stage=='mechanism':
        if SELECTED_ARM in ('R1','E1+R1'):
            saved=SELECTED_ARM
            try:
                globals()['SELECTED_ARM']='E1'
                if require_review('mechanism')['decision']!='continue':raise RuntimeError('freeze activated E1 before rotation mechanism')
            finally:globals()['SELECTED_ARM']=saved
        return
    mechanism=require_review('mechanism')
    if mechanism['decision']!='continue':
        raise RuntimeError('mechanism stopped; outcomes/series blocked')
    timing()
    if stage=='outcome':
        if look not in LOOKS: raise ValueError('look must be 50,100,200')
        if look!=50 and require_review('outcome',LOOKS[LOOKS.index(look)-1])['decision']!='continue':
            raise RuntimeError('previous sequential look stopped')
        # An existing stop cannot be crossed or converted into a continuation.
        for prior in LOOKS:
            path=HERE/f'OUTCOME_{SELECTED_ARM}_LOOK_{prior}_READ.json'
            if path.exists() and read(path)['decision']=='stop' and look>prior:
                raise RuntimeError('outcomes stopped at earlier look')
    elif stage=='series':
        reviews=[n for n in LOOKS if (HERE/f'OUTCOME_{SELECTED_ARM}_LOOK_{n}_READ.json').exists()]
        if not reviews: raise RuntimeError('read C3 outcome first')
        last=max(reviews)
        review=require_review('outcome',last)
        if review['decision']!='stop' or not review.get('survivor'):
            raise RuntimeError('series requires stopped C3 marked survivor')
    else: raise ValueError('unknown stage')


def calibration_receipt(stage):
    receipt=read(HERE/f'CALIBRATION_{scope(stage)}.json')
    if receipt['sample_tags']!=samples_for(stage) or receipt['workers']!=WORKERS or receipt['declaration_sha256']!=sha(HERE/'DECLARATION.json'):
        raise RuntimeError('calibration identity/subset drift')
    for tag,digest in receipt['sample_receipt_hashes'].items():
        if sha(RAW/(tag+'_COMPLETE.json'))!=digest: raise RuntimeError('calibration sample drift')
    if set(receipt['sample_receipt_hashes'])!=set(receipt['sample_tags']):
        raise RuntimeError('calibration sample coverage drift')
    attempts=sorted(HERE.glob(f'CALIBRATE_{scope(stage)}_ATTEMPT_*.json'))
    if set(receipt['attempt_hashes'])!={p.name for p in attempts}: raise RuntimeError('calibration attempt coverage drift')
    wall=0
    for path in attempts:
        row=read(path)
        if sha(path)!=receipt['attempt_hashes'][path.name] or row['status'] not in ('PASS','STOP') or row['declaration_sha256']!=receipt['declaration_sha256']:
            raise RuntimeError('calibration timing attempt drift')
        wall+=row['seconds']
    if wall!=receipt['wall_seconds']: raise RuntimeError('calibration wall drift')
    return receipt


def calibrate(stage,look):
    ensure_stage(stage,look)
    path=HERE/f'CALIBRATION_{scope(stage)}.json'
    cap=local_cap()
    if not path.exists():
        tags=samples_for(stage)
        def jobs(deadline):
            if stage=='series':
                tasks=[(run_series,(arm,0,deadline,True,cap['cap_seconds'])) for arm in selected_arms()]
            else:
                tasks=[(execute,(tag,req,meta,cap['cap_seconds'],deadline)) for tag,req,meta in plan(stage,50) if tag in tags]
            parallel_jobs(tasks)
        compute_attempt('CALIBRATE',stage,cap,jobs)
        attempts=sorted(HERE.glob(f'CALIBRATE_{scope(stage)}_ATTEMPT_*.json'))
        write(path,dict(status='MEASURED',workers=WORKERS,sample_tags=tags,
                        sample_receipt_hashes={tag:sha(RAW/(tag+'_COMPLETE.json')) for tag in tags},
                        attempt_hashes={p.name:sha(p) for p in attempts},wall_seconds=sum(read(p)['seconds'] for p in attempts),
                        declaration_sha256=sha(HERE/'DECLARATION.json'),**cap),exclusive=True)
    receipt=calibration_receipt(stage)
    records=records_for(stage)
    projected=projection(stage,look,records,[records[t] for t in receipt['sample_tags']],receipt['wall_seconds'])
    write(HERE/f'CALIBRATION_{scope(stage)}_PROJECTION.json',dict(**projected,**cap))
    print(json.dumps(projected,indent=2))
    if projected['remaining_projected_seconds']>cap['cap_seconds']:
        raise RuntimeError('measured projection exceeds local cap; Claude stops and asks owner')


def run(stage,look):
    done=HERE/f'RUN_{scope(stage)}.json'
    if done.exists() and read(done)['status']=='DONE' and (stage!='outcome' or read(done)['look']==look):
        report()
        print('Existing DONE stage preserved; read the selected summary before review')
        return
    ensure_stage(stage,look)
    calibration=calibration_receipt(stage)
    records=records_for(stage)
    cap=local_cap()
    projected=projection(stage,look,records,[records[t] for t in calibration['sample_tags']],calibration['wall_seconds'])
    gate=dict(stage=stage,look=look if stage=='outcome' else None,projection=projected,
              declaration_sha256=sha(HERE/'DECLARATION.json'),calibration_sha256=sha(HERE/f'CALIBRATION_{scope(stage)}.json'),**cap)
    if projected['remaining_projected_seconds']>cap['cap_seconds']:
        write(HERE/f'RUN_GATE_{scope(stage)}.json',dict(status='REFUSED',**gate))
        raise RuntimeError('measured remaining projection exceeds cap; Claude stops and asks owner')
    write(HERE/f'RUN_GATE_{scope(stage)}.json',dict(status='READY',**gate))
    def jobs(deadline):
        if stage=='series':
            tasks=[(run_series,(arm,index,deadline,False,cap['cap_seconds'])) for arm in selected_arms() for index in range(SERIES_COUNT)]
        else:
            tasks=[(execute,(tag,req,meta,cap['cap_seconds'],deadline)) for tag,req,meta in plan(stage,look) if tag not in records]
        parallel_jobs(tasks)
    try:
        compute_attempt('RUN',stage,cap,jobs)
    except TimeoutError as error:
        write(HERE/f'RUN_{scope(stage)}.json',dict(status='PAUSED_CAP',error=str(error),**gate))
        print('Cap pause; repeat same stage/ look to reuse completions')
        return
    path,summary=stage_summary(stage,look)
    if path.exists():
        if read(path)!=summary: raise RuntimeError('stage summary drift')
    else: write(path,summary,exclusive=True)
    write(HERE/f'RUN_{scope(stage)}.json',dict(status='DONE',**gate))
    report()
    print('Stage complete; Claude reads summary and records continue/stop before further fights')


def review(stage,look,decision,note,survivor=False):
    identity()
    if stage not in ('mechanism','outcome'): raise ValueError('read gate applies to mechanism/outcome')
    ensure_stage(stage,look)
    path,summary=stage_summary(stage,look)
    if not summary['complete'] or not path.exists() or read(path)!=summary:
        raise RuntimeError('completed stage summary required')
    if stage=='mechanism' and decision=='continue':
        if not summary['mechanism_gate_observations']['activated']:raise RuntimeError('inactive mechanism cannot proceed')
        if SELECTED_ARM in ('R1','E1+R1') and not summary['mechanism_gate_observations']['active_ranged']:raise RuntimeError('rotation needs active ranged reference')
    if not note.strip(): raise ValueError('Claude must supply what it observed')
    target=HERE/(f'OUTCOME_{SELECTED_ARM}_LOOK_{look}_READ.json' if stage=='outcome' else f'MECHANISM_{SELECTED_ARM}_READ.json')
    if survivor and (stage!='outcome' or decision!='stop'):raise ValueError('survivor only on a finished outcome look')
    receipt=dict(reader='Claude',decision=decision,note=note,survivor=survivor,summary_sha256=sha(path),
                 declaration_sha256=sha(HERE/'DECLARATION.json'))
    if target.exists():
        if read(target)!=receipt: raise RuntimeError('read receipt already fixed; do not overwrite')
    else: write(target,receipt,exclusive=True)


def report():
    from report_r2 import render
    render()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=('prepare','calibrate','run','report','review','configure-timing'))
    parser.add_argument('--stage',choices=('mechanism','outcome','series'))
    parser.add_argument('--look',type=int,choices=LOOKS,default=50)
    parser.add_argument('--decision',choices=('continue','stop'))
    parser.add_argument('--note')
    parser.add_argument('--arm',choices=ARMS[1:])
    parser.add_argument('--survivor',action='store_true')
    parser.add_argument('--mode',choices=('base','central_sync','battery_oscillator'))
    parser.add_argument('--k',type=float,choices=(.5,1,2),default=1)
    parser.add_argument('--radius',type=int,choices=(200,400,-1),default=400)
    args=parser.parse_args()
    if args.command=='configure-timing':
        if not args.mode or not args.note:parser.error('--mode and --note required')
        with execution_lock():configure_timing(args.mode,args.k,args.radius,args.note)
        return
    if args.command in ('calibrate','run','review') and args.arm is None:parser.error('--arm required')
    if args.arm:globals()['SELECTED_ARM']=args.arm
    if args.command in ('calibrate','run','review') and args.stage is None:
        parser.error('--stage required')
    if args.command=='review' and (args.decision is None or args.note is None):
        parser.error('review requires --decision and --note supplied by Claude after reading')
    if args.command in ('calibrate','run') and os.environ.get('SHAPE_LAB_V6_CAFFEINATED')!='1':
        os.environ['SHAPE_LAB_V6_CAFFEINATED']='1'
        os.execv('/usr/bin/caffeinate',['caffeinate','-i','-s',sys.executable,*sys.argv])
    if args.command in ('calibrate','run','review'):
        with execution_lock():
            if args.command=='review': review(args.stage,args.look,args.decision,args.note,args.survivor)
            else: globals()[args.command](args.stage,args.look)
    else: globals()[args.command]()


if __name__=='__main__':
    sys.modules['lab_r2']=sys.modules[__name__]
    main()
