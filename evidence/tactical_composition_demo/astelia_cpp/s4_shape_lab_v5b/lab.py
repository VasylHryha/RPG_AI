"""V1 battery development tooling, staged and paired; no acceptance decisions."""
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
from integrity import admit, sha
sys.path.insert(0,str(HERE))
from requests import ARMS, GRID, ROLES, cohort, drill_request, series_request
from metrics import measure
RAW = HERE/'raw'
V5 = CPP/'s4_shape_lab_v5'
V1 = CPP/'s4_shape_lab_v1'
V3 = CPP/'s4_shape_lab_v3'
ADAPTER = CPP/'s4_react_adapter_v1'
MAX_SECONDS = 3600
CAP_PATH = V1/'raw/LAB_CAP.json'
WORKERS = 6
LOOKS = (50,100,200)
SERIES_COUNT = 10

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


def verified_record(tag, req=None, meta=None, *, _admitted=False):
    if not _admitted:
        identity()
    r=read(RAW/(tag+'_COMPLETE.json'))
    continuation=read(HERE/'CONTINUATION.json')
    if tag in continuation['mechanism_tags']:
        if sha(RAW/(tag+'_COMPLETE.json')) != continuation['inherited_files']['raw/'+tag+'_COMPLETE.json']:
            raise RuntimeError('inherited completion drift')
        raw_path=V5/'raw'/(tag+'.jsonl.gz')
    else:
        seal=read(RAW/(tag+'_VERIFIED.json'))
        if seal != dict(receipt_sha256=sha(RAW/(tag+'_COMPLETE.json')), metrics_sha256=sha(HERE/'metrics.py')):
            raise RuntimeError('completion measurement seal drift')
        raw_path=RAW/(tag+'.jsonl.gz')
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
    if r['raw_sha256']!=sha(raw_path) or r['stderr_sha256']!=sha(stderr_path) or read(stderr_path)!=r['native_metrics']:
        raise RuntimeError('completed cell raw/stderr drift')
    # The sealed receipt binds the once-measured stats/survivors and terminal
    # to these exact raw bytes. Hash verification never re-decodes telemetry.
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
    write(RAW/(tag+'_VERIFIED.json'), dict(receipt_sha256=sha(done), metrics_sha256=sha(HERE/'metrics.py')), exclusive=True)
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
    """Verify the migrated seal; never generate entropy or rebuild."""
    identity()
    print('v5 continuation verified; no entropy replaced or fights run')


def identity():
    continuation = read(HERE/'CONTINUATION.json')
    if sha(HERE/'DECLARATION.json') != continuation['declaration_sha256']:
        raise RuntimeError('continuation declaration drift')
    for name,digest in {**continuation['tool_hashes'],**continuation['inherited_files']}.items():
        if name.startswith('raw/') and name != 'raw/SEED_LEDGER.json':
            continue
        if sha(HERE/name)!=digest:
            raise RuntimeError('continuation input drift: '+name)
    declaration = read(HERE/'DECLARATION.json')
    if sha(RAW/'SEED_LEDGER.json')!=declaration['ledger_sha256'] or admit(BINARY)!=declaration['binary']:
        raise RuntimeError('lab entropy/binary drift')
    if admit(ADAPTER/'build/tactics_react_host')!=declaration['adapter_binary']:
        raise RuntimeError('adapter identity drift')
    for name,digest in declaration['source_hashes'].items():
        path = HERE/continuation['frozen_documents'][name] if name in continuation['frozen_documents'] else CPP/name
        if sha(path)!=digest:
            raise RuntimeError('lab input drift: '+name)
    manifest = read(BINARY.with_suffix('.build.json'))
    for path,digest in manifest['reused_object_sha256'].items():
        if sha(pathlib.Path(path))!=digest:
            raise RuntimeError('reused native object drift')
    return declaration


@contextlib.contextmanager
def execution_lock():
    # Hold across admission/projection/work, so two v5 runners cannot both pass.
    RAW.mkdir(exist_ok=True)
    # Share v5's existing lock as well: its runner must never execute in
    # parallel with this continuation. Opening read-only preserves its bytes.
    with (V5/'raw/EXECUTION.lock').open('r') as parent_lock, (RAW/'EXECUTION.lock').open('a') as lock:
        try:
            fcntl.flock(parent_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('another v5 execution owns the local process lock')
        try:
            yield
        finally:
            fcntl.flock(lock,fcntl.LOCK_UN)
            fcntl.flock(parent_lock,fcntl.LOCK_UN)


def plan(stage, look=200):
    declaration = identity()
    ledger = read(RAW/'SEED_LEDGER.json')
    if stage not in ('mechanism','outcome'):
        raise ValueError('invalid drill stage')
    draws = ledger[stage][:20 if stage=='mechanism' else look]
    chosen = selected_knobs() if stage!='mechanism' else (1,400)
    for pair,draw in enumerate(draws):
        group = draw['group'] if stage=='mechanism' else 'C3'
        for arm in ARMS:
            candidates = GRID if stage=='mechanism' and arm==ARMS[2] else [chosen]
            for knobs in candidates:
                variant = grid_name(knobs) if stage=='mechanism' and arm==ARMS[2] else None
                label = arm+('_'+variant if variant else '')
                req=drill_request(group,arm,draw.get('tactic'),draw['seed'],draw['orientation'],declaration['pool'],knobs)
                if stage=='mechanism':
                    own=req['labScenario']['sides'][0]
                    req['labScenario']['sides'][0]=[u for u in own if u['role']=='artillery'][:draw['guns']]
                count=len(req['labScenario']['sides'][0])
                meta=dict(group=group,stage=stage,arm=arm,variant=variant,pair=pair,seed=draw['seed'],orientation=draw['orientation'],opponent=draw.get('tactic'),units_before=count,knobs=list(knobs))
                yield f'{group}_{label}_p{pair:03d}',req,meta


def grid_name(knobs):
    return f'k{knobs[0]:g}_r{knobs[1]}'

def selected_knobs():
    receipt=read(HERE/'PICK.json')
    path,summary=stage_summary('mechanism')
    if not summary['complete'] or read(path)!=summary or receipt['summary_sha256']!=sha(path) or receipt['declaration_sha256']!=sha(HERE/'DECLARATION.json') or receipt['picker']!='Claude':
        raise RuntimeError('mechanism pick identity drift')
    knobs=tuple(receipt['knobs'])
    if knobs not in GRID:raise RuntimeError('undeclared pick')
    return knobs


def pick(k,radius,note):
    raise RuntimeError('v5b inherits the immutable v5 pick; no new pick allowed')


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
        req = series_request(arm,draw,declaration['pool'],initial,selected_knobs())
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


def records_for(stage):
    identity()
    paths=list(RAW.glob('*_COMPLETE.json'))
    if stage=='mechanism':
        # Preserve the original aggregation order, including the float sums and
        # low-gun rows: the mechanism summary/read/pick bytes remain exact.
        tags=read(HERE/'CONTINUATION.json')['mechanism_tags']
        if {p.name.removesuffix('_COMPLETE.json') for p in paths if read(p)['meta']['stage']==stage}!=set(tags):
            raise RuntimeError('inherited mechanism coverage drift')
        return {tag:verified_record(tag, _admitted=True) for tag in tags}
    return {p.name.removesuffix('_COMPLETE.json'):verified_record(p.name.removesuffix('_COMPLETE.json'), _admitted=True)
            for p in paths if read(p)['meta']['stage']==stage}


def samples_for(stage):
    if stage=='series':
        return [f'S10X_{arm}_s00_f01' for arm in ARMS]
    # Mechanism: first pair. C3: one existing pair per opponent; all within look 50.
    size = 20 if stage=='mechanism' else 20
    return [tag for tag,_,meta in plan(stage,50) if (meta['pair'] in (0,10) if stage=='mechanism' else meta['pair']<size)]


def category(meta):
    return (meta['arm']+('_'+meta['variant'] if meta.get('variant') else ''),meta['group'] if meta['stage']=='mechanism' else meta.get('opponent'))


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
        for arm in ARMS:
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
    start=time.monotonic()
    path=HERE/f'{kind}_{stage}_ATTEMPT_{secrets.token_hex(8)}.json'
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


def stage_summary(stage,look=None):
    from report import stage_data
    path=HERE/(f'OUTCOME_LOOK_{look}.json' if stage=='outcome' else f'{stage.upper()}_SUMMARY.json')
    return path,stage_data(stage,look)


def require_review(stage,look=None):
    path,summary=stage_summary(stage,look)
    if not path.exists() or read(path)!=summary or not summary['complete']:
        raise RuntimeError('completed stage summary required before Claude reads it')
    review_path=HERE/(f'OUTCOME_LOOK_{look}_READ.json' if stage=='outcome' else f'{stage.upper()}_READ.json')
    review=read(review_path)
    if review['summary_sha256']!=sha(path) or review['declaration_sha256']!=sha(HERE/'DECLARATION.json') or review['reader']!='Claude':
        raise RuntimeError('Claude read receipt identity mismatch')
    return review


def ensure_stage(stage,look):
    identity()
    if stage=='mechanism':
        raise RuntimeError('v5b inherits the completed mechanism; mechanism calibration/run/review blocked')
    mechanism=require_review('mechanism')
    if mechanism['decision']!='continue':
        raise RuntimeError('mechanism stopped; outcomes/series blocked')
    selected_knobs()
    if stage=='outcome':
        if look not in LOOKS: raise ValueError('look must be 50,100,200')
        if look!=50 and require_review('outcome',LOOKS[LOOKS.index(look)-1])['decision']!='continue':
            raise RuntimeError('previous sequential look stopped')
        # An existing stop cannot be crossed or converted into a continuation.
        for prior in LOOKS:
            path=HERE/f'OUTCOME_LOOK_{prior}_READ.json'
            if path.exists() and read(path)['decision']=='stop' and look>prior:
                raise RuntimeError('outcomes stopped at earlier look')
    elif stage=='series':
        reviews=[n for n in LOOKS if (HERE/f'OUTCOME_LOOK_{n}_READ.json').exists()]
        if not reviews: raise RuntimeError('read C3 outcome first')
        last=max(reviews)
        review=require_review('outcome',last)
        if review['decision']!='stop' and last!=200:
            raise RuntimeError('finish sequential C3 looks before series')
    else: raise ValueError('unknown stage')


def calibration_receipt(stage):
    receipt=read(HERE/f'CALIBRATION_{stage}.json')
    if receipt['sample_tags']!=samples_for(stage) or receipt['workers']!=WORKERS or receipt['declaration_sha256']!=sha(HERE/'DECLARATION.json'):
        raise RuntimeError('calibration identity/subset drift')
    for tag,digest in receipt['sample_receipt_hashes'].items():
        if sha(RAW/(tag+'_COMPLETE.json'))!=digest: raise RuntimeError('calibration sample drift')
    if set(receipt['sample_receipt_hashes'])!=set(receipt['sample_tags']):
        raise RuntimeError('calibration sample coverage drift')
    attempts=sorted(HERE.glob(f'CALIBRATE_{stage}_ATTEMPT_*.json'))
    if set(receipt['attempt_hashes'])!={p.name for p in attempts}: raise RuntimeError('calibration attempt coverage drift')
    wall=0
    for path in attempts:
        row=read(path)
        if sha(path)!=receipt['attempt_hashes'][path.name] or row['status'] not in ('PASS','STOP') or row['declaration_sha256']!=receipt['declaration_sha256']:
            raise RuntimeError('calibration timing attempt drift')
        wall+=row['seconds']
    if wall!=receipt['wall_seconds']: raise RuntimeError('calibration wall drift')
    return receipt


def calibrate(stage,look,preflight_only=False):
    ensure_stage(stage,look)
    path=HERE/f'CALIBRATION_{stage}.json'
    cap=local_cap()
    if preflight_only:
        tags=samples_for(stage)
        if stage!='series':
            planned={tag for tag,_,_ in plan(stage,look)}
            if not set(tags)<=planned:
                raise RuntimeError('calibration samples outside requested look')
        # Exercise receipt/read/pick admission and outcome planning without
        # opening an attempt or starting native work. Full calibration remains
        # Claude's allocated outcome fights; their time is not fabricated here.
        print(json.dumps(dict(status='READY_FOR_CALIBRATION',stage=stage,look=look,
                              calibration_samples=len(tags),fights_started=0,
                              declaration_sha256=sha(HERE/'DECLARATION.json')),indent=2))
        return
    if not path.exists():
        tags=samples_for(stage)
        def jobs(deadline):
            if stage=='series':
                tasks=[(run_series,(arm,0,deadline,True,cap['cap_seconds'])) for arm in ARMS]
            else:
                tasks=[(execute,(tag,req,meta,cap['cap_seconds'],deadline)) for tag,req,meta in plan(stage,50) if tag in tags]
            parallel_jobs(tasks)
        compute_attempt('CALIBRATE',stage,cap,jobs)
        attempts=sorted(HERE.glob(f'CALIBRATE_{stage}_ATTEMPT_*.json'))
        write(path,dict(status='MEASURED',workers=WORKERS,sample_tags=tags,
                        sample_receipt_hashes={tag:sha(RAW/(tag+'_COMPLETE.json')) for tag in tags},
                        attempt_hashes={p.name:sha(p) for p in attempts},wall_seconds=sum(read(p)['seconds'] for p in attempts),
                        declaration_sha256=sha(HERE/'DECLARATION.json'),**cap),exclusive=True)
    receipt=calibration_receipt(stage)
    records=records_for(stage)
    projected=projection(stage,look,records,[records[t] for t in receipt['sample_tags']],receipt['wall_seconds'])
    write(HERE/f'CALIBRATION_{stage}_PROJECTION.json',dict(**projected,**cap))
    print(json.dumps(projected,indent=2))
    if projected['remaining_projected_seconds']>cap['cap_seconds']:
        raise RuntimeError('measured projection exceeds local cap; Claude stops and asks owner')


def run(stage,look):
    ensure_stage(stage,look)
    calibration=calibration_receipt(stage)
    records=records_for(stage)
    cap=local_cap()
    projected=projection(stage,look,records,[records[t] for t in calibration['sample_tags']],calibration['wall_seconds'])
    gate=dict(stage=stage,look=look if stage=='outcome' else None,projection=projected,
              declaration_sha256=sha(HERE/'DECLARATION.json'),calibration_sha256=sha(HERE/f'CALIBRATION_{stage}.json'),**cap)
    if projected['remaining_projected_seconds']>cap['cap_seconds']:
        write(HERE/f'RUN_GATE_{stage}.json',dict(status='REFUSED',**gate))
        raise RuntimeError('measured remaining projection exceeds cap; Claude stops and asks owner')
    write(HERE/f'RUN_GATE_{stage}.json',dict(status='READY',**gate))
    def jobs(deadline):
        if stage=='series':
            tasks=[(run_series,(arm,index,deadline,False,cap['cap_seconds'])) for arm in ARMS for index in range(SERIES_COUNT)]
        else:
            tasks=[(execute,(tag,req,meta,cap['cap_seconds'],deadline)) for tag,req,meta in plan(stage,look) if tag not in records]
        parallel_jobs(tasks)
    try:
        compute_attempt('RUN',stage,cap,jobs)
    except TimeoutError as error:
        write(HERE/f'RUN_{stage}.json',dict(status='PAUSED_CAP',error=str(error),**gate))
        print('Cap pause; repeat same stage/ look to reuse completions')
        return
    path,summary=stage_summary(stage,look)
    if path.exists():
        if read(path)!=summary: raise RuntimeError('stage summary drift')
    else: write(path,summary,exclusive=True)
    write(HERE/f'RUN_{stage}.json',dict(status='DONE',**gate))
    report()
    print('Stage complete; Claude reads summary and records continue/stop before further fights')


def review(stage,look,decision,note):
    identity()
    if stage not in ('mechanism','outcome'): raise ValueError('read gate applies to mechanism/outcome')
    ensure_stage(stage,look)
    path,summary=stage_summary(stage,look)
    if not summary['complete'] or not path.exists() or read(path)!=summary:
        raise RuntimeError('completed stage summary required')
    if stage=='mechanism' and decision=='continue':selected_knobs()
    if not note.strip(): raise ValueError('Claude must supply what it observed')
    target=HERE/(f'OUTCOME_LOOK_{look}_READ.json' if stage=='outcome' else 'MECHANISM_READ.json')
    receipt=dict(reader='Claude',decision=decision,note=note,summary_sha256=sha(path),
                 declaration_sha256=sha(HERE/'DECLARATION.json'))
    if target.exists():
        if read(target)!=receipt: raise RuntimeError('read receipt already fixed; do not overwrite')
    else: write(target,receipt,exclusive=True)


def report():
    from report import render
    render()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=('prepare','calibrate','run','report','review','pick'))
    parser.add_argument('--stage',choices=('mechanism','outcome','series'))
    parser.add_argument('--look',type=int,choices=LOOKS,default=50)
    parser.add_argument('--decision',choices=('continue','stop'))
    parser.add_argument('--note')
    parser.add_argument('--k',type=float,choices=(.5,1,2))
    parser.add_argument('--radius',type=int,choices=(200,400,-1))
    parser.add_argument('--preflight-only',action='store_true',help='calibrate admission/planning only; never start fights')
    args=parser.parse_args()
    if args.preflight_only and args.command!='calibrate':parser.error('--preflight-only requires calibrate')
    if args.command=='pick' and (args.k is None or args.radius is None or args.note is None):parser.error('pick requires --k --radius --note')
    if args.command in ('calibrate','run','review') and args.stage is None:
        parser.error('--stage required')
    if args.command=='review' and (args.decision is None or args.note is None):
        parser.error('review requires --decision and --note supplied by Claude after reading')
    if args.command in ('calibrate','run') and os.environ.get('SHAPE_LAB_V5_CAFFEINATED')!='1':
        os.environ['SHAPE_LAB_V5_CAFFEINATED']='1'
        os.execv('/usr/bin/caffeinate',['caffeinate','-i','-s',sys.executable,*sys.argv])
    if args.command in ('calibrate','run','review','pick'):
        with execution_lock():
            if args.command=='pick':pick(args.k,args.radius,args.note)
            elif args.command=='review': review(args.stage,args.look,args.decision,args.note)
            elif args.command=='calibrate':calibrate(args.stage,args.look,args.preflight_only)
            else: run(args.stage,args.look)
    else: globals()[args.command]()


if __name__=='__main__': main()
