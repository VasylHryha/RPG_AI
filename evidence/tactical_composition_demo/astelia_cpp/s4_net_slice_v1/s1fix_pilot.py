"""Host-only script pilot. No fights on import; process discovery must be available.

Retained D2-10/M2-10; ten pairs initially, twenty only for coverage/detectability.
A separate <=20 arm-fight sample admits the maximum possible 80-fight extent.
"""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import re
import time
import types
from collection import HERE, read, sha, atomic, cap
import collection
import process_gate as gate
from requests_v2 import drill
from s0_analysis import DESIGN_COMMIT
from s1fix_build import BINARY, RECORD, admit
from s1fix_metrics import measure, summarize

ROOT=HERE/'_local/s1fix/pilot'
CELLS=('D2-10','M2-10')
ARMS=('T-unit-alone','T-unit+wrapper')
MAX_FIGHTS=80
SAMPLE_FIGHTS=20
PROCESS_RSS_CAP_BYTES=2*1024**3
OLD_PROCESS_RSS_CAP_BYTES=512*1024**2
RSSFIX_BASELINE_SHA256='02c79cb7bd4dc37ab6f6ab2c8c09701ab1405da557a655a1738c8f9f1e1d6697'


def free_ram_bytes():
    """Live available RAM; no total-RAM substitution when discovery fails."""
    try:
        if sys.platform=='darwin':
            result=subprocess.run(['vm_stat'],capture_output=True,text=True,check=True,timeout=5)
            page=int(re.search(r'page size of (\d+) bytes',result.stdout).group(1))
            counts={name:int(re.search(r'Pages '+name+r':\s+(\d+)',result.stdout).group(1))
                    for name in ('free','inactive','speculative')}
            value=page*sum(counts.values())
        else:
            value=int(re.search(r'^MemAvailable:\s+(\d+) kB',Path('/proc/meminfo').read_text(),re.M).group(1))*1024
        if value<=0:raise ValueError('no available memory')
        return value
    except (OSError,ValueError,AttributeError,subprocess.SubprocessError) as exc:
        raise RuntimeError('available RAM discovery failed') from exc


def forbidden_seeds():
    # Include collection, mechanism, partial and fixture inventories across the
    # tactical workspace. Test/build copies add conservative exclusions only.
    paths=set()
    workspace=HERE.parent.parent
    for p in workspace.rglob('*.json'):
        name=p.name.upper()
        if ('SEED' in name or 'INVENTORY' in name or 'LEDGER' in name) and p.is_file() and not (ROOT.resolve() in p.resolve().parents):
            paths.add(p)
    def walk(v):
        if isinstance(v,dict):
            for k,x in v.items():
                if 'seed' in k.lower() and type(x)==int:yield x
                elif 'seed' in k.lower() and isinstance(x,list):
                    for seed in x:
                        if type(seed)==int:yield seed
                        else:yield from walk(seed)
                else:yield from walk(x)
        elif isinstance(v,list):
            for x in v:yield from walk(x)
    return set(range(10000))|{v for p in paths for v in walk(read(p))},{str(p):sha(p) for p in sorted(paths)}


def pins():
    build=admit()
    names=('s1fix_build.py','s1fix_pilot.py','s1fix_metrics.py','s1fix_controller.cpp','s1fix_script.h','s1fix_fixture.inc','s1_metrics.py','s0_analysis.py','s0_arithmetic.py','s1_public.py','schema.py','collection.py','process_gate.py','requests.py','requests_v2.py')
    return dict(design_commit=DESIGN_COMMIT,revision='S1FIX-2',build_sha256=sha(RECORD),binary_sha256=build['binary_sha256'],sources={name:sha(HERE/name) for name in names})


def authority():
    # Mutable cap is checked live on every launch, never an execution hash pin.
    return {k:v for k,v in cap().items() if k!='sha256'}


def definition(cell,seed,pair):
    guns=int(cell.split('-')[1]);moving=cell.startswith('M2');request=drill('D2-shellfire',guns,seed,pair%2,fight='unused')
    # Shared, seed-derived cooldown diversity. Prep zero avoids starting a cast
    # with no accepted focus/command origin; native windup diversity arises later.
    for i,u in enumerate(request['roster']):
        u['initial_cooldown']=.12*(i%3) if u['role']==2 else 0
        u['initial_prep']=0
    request.update(moving=moving,s1_cell=cell,opponent=dict(policy='native enemy guns',dodge_shells=True,smart_shells=moving,cast_dodge=moving,moving_recipe='y=400+110*sin(1.3*t+id), only when native release permits; native reaction takes precedence' if moving else None),horizon_seconds=150,initial_prep_policy='zero; cooldowns .0/.12/.24 s in roster insertion order')
    return request


def seal():
    if (ROOT/'INVENTORY.json').exists():return inventory()
    if (HERE/'S1FIX_PILOT_SEED_EXCLUSIONS.json').exists():raise RuntimeError('orphan pilot seed exclusion file; preserve and inspect')
    ROOT.mkdir(parents=True,exist_ok=True)
    if list(ROOT.iterdir()):raise RuntimeError('nonempty pilot root without inventory; inspect')
    excluded,exclusion_sources=forbidden_seeds();entropy=secrets.token_hex(32);rows=[];seeds=[]
    sample_pairs={cell:set(range(5)) for cell in CELLS}
    for cell in CELLS:
        for pair in range(20):
            counter=0
            while True:
                seed=int.from_bytes(hashlib.sha256(f'S1FIX-pilot-only:{entropy}:{cell}:{pair}:{counter}'.encode()).digest()[:4],'big');counter+=1
                if seed not in excluded:break
            excluded.add(seed);seeds.append(seed)
            base=definition(cell,seed,pair)
            for arm in ARMS:
                fight=f's1fix_{cell}_{pair:02d}_{"unit" if arm==ARMS[0] else "wrapper"}'
                request={**base,'fight':fight,'arm':arm}
                rows.append(dict(fight=fight,cell=base['cell'],pilot_cell=cell,guns=int(cell.split('-')[1]),pair=pair,arm=arm,seed=seed,sample=pair in sample_pairs[cell],request=request))
    value=dict(version='S1FIX-pilot-2',design_commit=DESIGN_COMMIT,entropy_domain='pilot-only, never training/validation/outcomes',entropy=entropy,pins=pins(),initial_cap_authority=authority(),exclusion_sources=exclusion_sources,seeds=seeds,max_pairs_per_cell=20,initial_pairs_per_cell=10,max_physical_attempts=MAX_FIGHTS,sample_attempt_cap=SAMPLE_FIGHTS,rows=rows)
    atomic(ROOT/'INVENTORY.json',value);atomic(ROOT/'SEAL.json',dict(inventory_sha256=sha(ROOT/'INVENTORY.json')))
    # Public exclusion list is written before launch, for all future data pools.
    atomic(HERE/'S1FIX_PILOT_SEED_EXCLUSIONS.json',dict(design_commit=DESIGN_COMMIT,inventory_sha256=sha(ROOT/'INVENTORY.json'),seeds=seeds,forbidden_pools=['training','validation','outcomes']))
    return value


def inventory():
    v=read(ROOT/'INVENTORY.json')
    if sha(ROOT/'INVENTORY.json')!=read(ROOT/'SEAL.json')['inventory_sha256']:raise RuntimeError('sealed inventory drift; preserve inventory')
    current=pins()
    if v['pins']!=current:
        expected={**v['pins'],'sources':{**v['pins']['sources'],'s1fix_pilot.py':current['sources']['s1fix_pilot.py']}}
        if v['pins']['sources']['s1fix_pilot.py']!=RSSFIX_BASELINE_SHA256 or expected!=current:
            raise RuntimeError('sealed source/build/cap drift; preserve inventory')
        resolutions=list((ROOT/'resolutions').glob('*.json'))
        admitted=False
        for path in resolutions:
            log=read(path)
            if log.get('status')!='COMPLETE':continue
            if log['inventory_sha256']!=sha(ROOT/'INVENTORY.json') or log['tooling']!=dict(before=RSSFIX_BASELINE_SHA256,after=current['sources']['s1fix_pilot.py']):continue
            receipt=ROOT/(log['original_attempt']['request']['fight']+'.receipt.json')
            attempt=ROOT/'attempts'/(path.stem+'.json')
            if receipt.is_file() and sha(receipt)==log['completion_receipt_sha256'] and read(attempt)=={**log['original_attempt'],'status':'COMPLETE'}:
                admitted=True;break
        if not admitted:raise RuntimeError('RSS tooling amendment requires explicit resolve')
    return v


def clear(deadline):
    # Isolated globals reuse the exact repository ownership implementation.
    namespace={**vars(gate),'GATE_PATH':ROOT/'PROCESS_GATE.json','HEAVY_PATTERN':gate.HEAVY_PATTERN+r'|(^|/)(stage1_host|s1_host|s1fix_host)( |$)|[Pp]ython[^ ]* .*stage1_training_(worker|control)'}
    check=types.FunctionType(gate.process_gate.__code__,namespace,gate.process_gate.__name__,gate.process_gate.__defaults__)
    return check(wait=False,deadline=deadline)


@contextmanager
def lock():
    # Share exclusion with both historical collection and stage1 training;
    # original lock bytes and all data remain unchanged.
    paths=(HERE/'_local/collection/RUN.lock',HERE/'_local/stage1_v2/jobs/SLICE_JOB.lock')
    handles=[]
    try:
        for p in paths:
            f=p.open('r');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);handles.append(f)
        yield
    finally:
        for f in reversed(handles):f.close()


def charged():
    attempts=[read(p) for p in (ROOT/'attempts').glob('*.json')]
    if any(v['status'] not in ('COMPLETE','FAILED') for v in attempts):raise RuntimeError('unresolved attempt boundary; inspect before any launch')
    return sum(v['resources']['wall_seconds'] for v in attempts)


def completed(row):
    p=ROOT/(row['fight']+'.receipt.json')
    if not p.exists():return None
    v=read(p)
    if v['inventory_sha256']!=sha(ROOT/'INVENTORY.json') or v['request']!=row['request'] or v['raw_sha256']!=sha(ROOT/(row['fight']+'.jsonl')):raise RuntimeError('pilot receipt/raw drift')
    return v


def execute(row,deadline,sample):
    done=completed(row)
    if done:return done
    attempt_dir=ROOT/'attempts';attempt_dir.mkdir(exist_ok=True);attempts=list(attempt_dir.glob('*.json'))
    if len(attempts)>=MAX_FIGHTS or (sample and sum(read(p)['sample'] for p in attempts)>=SAMPLE_FIGHTS):raise RuntimeError('physical attempt cap includes failures')
    if any(read(p)['request']['fight']==row['fight'] for p in attempts):raise RuntimeError('previous failed/incomplete fight; no automatic repeat')
    if not sample:resource_gate(inventory())
    clear(deadline);remaining=min(deadline-time.monotonic(),cap()['cap_seconds']-charged())
    if remaining<=0:raise RuntimeError('owner fight cap exhausted')
    prefix=attempt_dir/f'{len(attempts)+1:03d}';attempt=prefix.with_suffix('.json');partial=prefix.with_suffix('.partial.jsonl');stderr=prefix.with_suffix('.stderr')
    atomic(attempt,dict(status='RUNNING',sample=sample,request=row['request'],started_unix=time.time()))
    ns={**vars(collection),'BINARY':BINARY};native=types.FunctionType(collection.native.__code__,ns,collection.native.__name__,collection.native.__defaults__)
    resources=native(row['request'],partial,stderr,remaining)
    status='FAILED' if resources['exit_code'] or resources['timed_out'] else 'NATIVE_DONE'
    atomic(attempt,dict(status=status,sample=sample,request=row['request'],resources=resources))
    if status=='FAILED':raise RuntimeError('failed native fight preserved; no retry')
    return complete_attempt(row,attempt,partial,stderr,resources,sample)


def complete_attempt(row,attempt,partial,stderr,resources,sample,raw_sha256=None):
    """One completion path for fresh native output and explicit recovery."""
    if resources['exit_code']!=0 or resources['timed_out'] is not False:raise RuntimeError('native completion requires exit 0 without timeout')
    if resources['rss_bytes']>PROCESS_RSS_CAP_BYTES:raise RuntimeError('2 GiB/process cap exceeded; output preserved')
    target=ROOT/(row['fight']+'.jsonl')
    source=partial if partial.exists() else target
    if raw_sha256 is None and target.exists():raise RuntimeError('orphan raw file')
    if partial.exists() and target.exists():raise RuntimeError('partial and raw both exist; inspect')
    if raw_sha256 is not None and sha(source)!=raw_sha256:raise RuntimeError('resolution raw drift')
    with source.open() as stream:metrics=measure((json.loads(line) for line in stream),row['request'])
    if source==partial:os.replace(partial,target)
    receipt=dict(status='COMPLETE',request=row['request'],inventory_sha256=sha(ROOT/'INVENTORY.json'),raw_sha256=sha(target),resources=resources,disk_bytes=target.stat().st_size+stderr.stat().st_size,metrics=metrics)
    receipt_path=ROOT/(row['fight']+'.receipt.json')
    if receipt_path.exists():
        if read(receipt_path)!=receipt:raise RuntimeError('completion receipt drift')
    else:atomic(receipt_path,receipt)
    atomic(attempt,dict(status='COMPLETE',sample=sample,request=row['request'],resources=resources))
    print(row['fight'],f"{resources['wall_seconds']:.2f} s",flush=True);return receipt


def resolve(attempt_id):
    """Explicitly finish old-cap NATIVE_DONE output; never launch or retry."""
    if not re.fullmatch(r'\d{3}',attempt_id):raise RuntimeError('attempt must be a three-digit ID')
    with lock():
        attempt=ROOT/'attempts'/f'{attempt_id}.json';partial=attempt.with_suffix('.partial.jsonl');stderr=attempt.with_suffix('.stderr')
        resolution=ROOT/'resolutions'/f'{attempt_id}.json'
        original=read(attempt);inv=read(ROOT/'INVENTORY.json');current=pins()
        if sha(ROOT/'INVENTORY.json')!=read(ROOT/'SEAL.json')['inventory_sha256']:raise RuntimeError('sealed inventory drift')
        expected={**inv['pins'],'sources':{**inv['pins']['sources'],'s1fix_pilot.py':current['sources']['s1fix_pilot.py']}}
        if inv['pins']['sources']['s1fix_pilot.py']!=RSSFIX_BASELINE_SHA256 or expected!=current:raise RuntimeError('resolution source/build drift')
        if resolution.exists():
            log=read(resolution)
            if log['inventory_sha256']!=sha(ROOT/'INVENTORY.json') or log['tooling']!=dict(before=RSSFIX_BASELINE_SHA256,after=current['sources']['s1fix_pilot.py']):raise RuntimeError('resolution identity drift')
            if original not in (log['original_attempt'],{**log['original_attempt'],'status':'COMPLETE'}):raise RuntimeError('resolution attempt drift')
            original=log['original_attempt']
            if log['status'] not in ('PREPARED','COMPLETE'):raise RuntimeError('invalid resolution status')
            if log['status']=='COMPLETE':
                receipt_path=ROOT/(original['request']['fight']+'.receipt.json')
                if not receipt_path.is_file() or sha(receipt_path)!=log['completion_receipt_sha256']:raise RuntimeError('finalized resolution receipt drift')
        else:
            if original['status']!='NATIVE_DONE':raise RuntimeError('resolve requires NATIVE_DONE; FAILED attempts never retried')
            resources=original['resources']
            if resources['exit_code']!=0 or resources['timed_out'] is not False:raise RuntimeError('resolve requires exit 0 without timeout')
            if not OLD_PROCESS_RSS_CAP_BYTES<resources['rss_bytes']<=PROCESS_RSS_CAP_BYTES:raise RuntimeError('attempt not within old-cap RSS fix')
            if not partial.is_file() or not stderr.is_file() or (ROOT/(original['request']['fight']+'.jsonl')).exists() or (ROOT/(original['request']['fight']+'.receipt.json')).exists():raise RuntimeError('partial boundary not intact')
            # Validate before logging any amendment or changing attempt state.
            with partial.open() as stream:measure((json.loads(line) for line in stream),original['request'])
            log=dict(status='PREPARED',reason='Old 512 MiB cap interrupted successful native completion; RSSFIX declares 2 GiB and completes preserved output without rerun or data edit',old_process_rss_cap_bytes=OLD_PROCESS_RSS_CAP_BYTES,process_rss_cap_bytes=PROCESS_RSS_CAP_BYTES,inventory_sha256=sha(ROOT/'INVENTORY.json'),tooling=dict(before=RSSFIX_BASELINE_SHA256,after=current['sources']['s1fix_pilot.py']),original_attempt=original,original_attempt_sha256=sha(attempt),raw_sha256=sha(partial),stderr_sha256=sha(stderr),resolved_unix=time.time())
            row=next((r for r in inv['rows'] if r['request']==original['request'] and r['sample']==original['sample']),None)
            if row is None:raise RuntimeError('attempt not in sealed inventory')
            atomic(resolution,log)
        row=next((r for r in inv['rows'] if r['request']==original['request'] and r['sample']==original['sample']),None)
        if row is None or sha(stderr)!=log['stderr_sha256']:raise RuntimeError('resolution request/stderr drift')
        receipt=complete_attempt(row,attempt,partial,stderr,original['resources'],original['sample'],log['raw_sha256'])
        if log['status']!='COMPLETE':atomic(resolution,{**log,'status':'COMPLETE','completion_receipt_sha256':sha(ROOT/(row['fight']+'.receipt.json'))})
        return dict(status='COMPLETE',attempt=attempt_id,resolution_receipt=str(resolution),resources=receipt['resources'])


def projection():
    inv=inventory();receipts=[completed(r) for r in inv['rows'] if r['sample']]
    if len(receipts)!=20 or any(v is None for v in receipts):raise RuntimeError('complete <=20-fight sample required')
    maximum=max(v['resources']['wall_seconds'] for v in receipts);mean=sum(v['resources']['wall_seconds'] for v in receipts)/20;used=charged();remaining=MAX_FIGHTS-len(list((ROOT/'attempts').glob('*.json')));projected=used+2*maximum*remaining
    disk=2*max(v['disk_bytes'] for v in receipts)*remaining;available=shutil.disk_usage(ROOT).free;cap_authority=authority();memory=max(v['resources']['rss_bytes'] for v in receipts);ram=free_ram_bytes();memory_reserve=2*memory
    value=dict(stage='S1',design_commit=DESIGN_COMMIT,sample_fights=20,sample_receipts={v['request']['fight']:sha(ROOT/(v['request']['fight']+'.receipt.json')) for v in receipts},sample_mean_seconds=mean,sample_max_seconds=maximum,sample_peak_rss_bytes=memory,process_rss_cap_bytes=PROCESS_RSS_CAP_BYTES,free_ram_bytes=ram,memory_reserve_bytes=memory_reserve,simple_projection='charged + 2 * sample_max * remaining maximum arm-fights; sample coverage does not guarantee an upper runtime bound',maximum_total_fights=MAX_FIGHTS,maximum_extent_projected_seconds=projected,initial_40_fights_projected_seconds=used+2*maximum*20,charged_wall_seconds=used,remaining_disk_reserve_bytes=disk,disk_free_bytes=available,cap=cap_authority,status='ADMITTED' if projected<=cap_authority['cap_seconds'] and available>=disk+5_000_000_000 and memory<=PROCESS_RSS_CAP_BYTES and ram>=memory_reserve else 'STOP_RESOURCE',sample_limits='5 pairs/cell; sample reused in initial 10-pair collection; pilot scripted paths only, no fit/search/full-army cost')
    path=ROOT/'PROJECTION.json'
    if path.exists() and read(path)!=value:raise RuntimeError('existing projection differs; preserve, choose a new named projection')
    if not path.exists():atomic(path,value)
    return value


def resource_gate(inv,verify_raw=False):
    """Recheck maximum remaining extent; never alter the initial projection.

    Sample receipt hashes are checked on every physical launch. Raw bytes are
    checked once on invocation admission and again on report, not reread for
    every launch. Later observed wall/RSS/disk maxima can tighten the sample.
    """
    stored=read(ROOT/'PROJECTION.json')
    if stored['status']!='ADMITTED':raise RuntimeError('maximum pilot extent not admitted')
    sample=[r for r in inv['rows'] if r['sample']]
    paths={r['fight']:ROOT/(r['fight']+'.receipt.json') for r in sample}
    hashes={fight:sha(path) for fight,path in paths.items()}
    if len(sample)!=SAMPLE_FIGHTS or hashes!=stored['sample_receipts']:raise RuntimeError('sample receipt hash drift')
    records=[completed(r) if verify_raw else read(paths[r['fight']]) for r in sample]
    if any(v is None for v in records):raise RuntimeError('complete timing sample required')
    attempts=list((ROOT/'attempts').glob('*.json'));used=charged();remaining=MAX_FIGHTS-len(attempts)
    if remaining<0:raise RuntimeError('physical attempt cap exceeded')
    observed=[read(p)['resources'] for p in attempts]
    receipts=[read(p) for p in ROOT.glob('*.receipt.json')]
    maximum=max(v['resources']['wall_seconds'] for v in records)
    if stored['sample_max_seconds']!=maximum:raise RuntimeError('sample projection measurement drift')
    maximum=max([maximum]+[v['wall_seconds'] for v in observed])
    peak=max([v['resources']['rss_bytes'] for v in records]+[v['rss_bytes'] for v in observed])
    max_disk=max([v['disk_bytes'] for v in records]+[v['disk_bytes'] for v in receipts])
    projected=used+2*maximum*remaining;reserve=2*max_disk*remaining+5_000_000_000
    free=shutil.disk_usage(ROOT).free;live_cap=authority();ram=free_ram_bytes();memory_reserve=2*peak
    reason=('projected remaining extent exceeds live owner cap' if projected>live_cap['cap_seconds'] else
            'measured-size remaining disk reserve unavailable' if free<reserve else
            'observed RSS exceeds 2 GiB' if peak>PROCESS_RSS_CAP_BYTES else
            'measured peak memory reserve unavailable' if ram<memory_reserve else None)
    value=dict(status='REFUSED' if reason else 'PASS',reason=reason,projection_sha256=sha(ROOT/'PROJECTION.json'),
               inventory_sha256=sha(ROOT/'INVENTORY.json'),sample_receipts=hashes,charged_wall_seconds=used,
               remaining_attempts=remaining,observed_max_wall_seconds=maximum,maximum_extent_projected_seconds=projected,
               observed_peak_rss_bytes=peak,process_rss_cap_bytes=PROCESS_RSS_CAP_BYTES,free_ram_bytes=ram,memory_reserve_bytes=memory_reserve,remaining_disk_reserve_bytes=reserve,disk_free_bytes=free,cap=live_cap)
    # Append-only checks preserve the sample projection and each refusal.
    directory=ROOT/'resource_checks';directory.mkdir(exist_ok=True)
    path=directory/f'{len(list(directory.glob("*.json")))+1:04d}.json'
    if path.exists():raise RuntimeError('resource check path exists')
    atomic(path,value)
    if reason:raise RuntimeError(reason)
    return value


def report(extend_cells=()):
    inv=inventory();reports={};raw={}
    for cell in CELLS:
        n=20 if cell in extend_cells else 10;pairs=[]
        for i in range(n):
            rows=[next(r for r in inv['rows'] if r['pilot_cell']==cell and r['pair']==i and r['arm']==arm) for arm in ARMS];receipts=[completed(r) for r in rows]
            if any(v is None for v in receipts):raise RuntimeError('incomplete paired cell')
            pairs.append(tuple(v['metrics'] for v in receipts))
        reports[cell]=summarize(pairs,cell.startswith('M2'));raw[cell]=pairs
    admitted=[c for c in CELLS if reports[c]['admitted']][:2]
    freeze={c:dict(cell_definition=next(r['request'] for r in inv['rows'] if r['pilot_cell']==c),primary=reports[c]['primary'],final_N=reports[c]['final_N'],useful_harm_thresholds=reports[c]['thresholds'],allocation=dict(five_arm_paired_outcome_N=reports[c]['final_N'],S2_training='UNSEALED: no outcome entropy until S2 collection/splits/checkpoints declared'),interval_rule='paired t/N-1 for additive benefit/harm; delete-one-pair jackknife/t for ratio-of-totals; <5 nonzero or zero variance benefit unestimable; sparse additive harm exact-binomial harmed-pair upper bound * sealed roster or HP physical bound; claims multiplicity adjusted prospectively') for c in admitted}
    value=dict(stage='S1',status='PILOT_ONLY_NO_UTILITY_CLAIM',design_commit=DESIGN_COMMIT,inventory_sha256=sha(ROOT/'INVENTORY.json'),selected_cells=admitted,cell_reports=reports,raw_per_fight=raw,prospective_cell_freeze=freeze,outcome_entropy_authorized=False,global_stop=dict(condition='No cell qualifies?',yes=not admitted,action='Redesign pilot cells',role='drafter'))
    tag='EXTENDED' if extend_cells else 'INITIAL';output=HERE/f'S1FIX_PILOT_{tag}.json'
    if output.exists():raise RuntimeError('refuse overwrite report')
    atomic(output,value)
    output.with_suffix('.md').write_text('# S1 script-only pilot\n\nPilot evidence only; no trained model, utility claim or outcome allocation.\n\n'+ '\n'.join(f"- {c}: {reports[c]['status']}; primary {reports[c]['primary']}; N {reports[c]['final_N']}." for c in CELLS)+'\n\nSee JSON for paired spread/MDE, all-draw raw metrics, wrapper misses, counted exclusions and yes/no rows.\n')
    return value


def run(stage,cells):
    inv=inventory()
    if stage=='sample':rows=[r for r in inv['rows'] if r['sample']]
    else:
        if read(ROOT/'PROJECTION.json')['status']!='ADMITTED':raise RuntimeError('maximum pilot extent not admitted')
        if stage=='extend':
            prior=read(HERE/'S1FIX_PILOT_INITIAL.json')
            for cell in cells:
                r=prior['cell_reports'][cell]
                if r['stops'][1]['yes'] or r['stops'][2]['yes']:raise RuntimeError('wrapper defect requires prospective revision, not more pilot fights')
                if r['admitted'] or (not r['stops'][3]['yes'] and any(v.get('informative') and v.get('MDE_200',math.inf)<=r['thresholds'][k]['useful'] for k,v in r['axes'].items() if k!='clear_time')):raise RuntimeError('extension only for wrapper coverage or detectability')
        rows=[r for r in inv['rows'] if r['pair']<(20 if r['pilot_cell'] in cells and stage=='extend' else 10)]
    origin=time.monotonic();before=charged();deadline=origin+cap()['cap_seconds']-before
    with lock():
        if stage!='sample':resource_gate(inv,verify_raw=True)
        clear(deadline)
        for row in rows:
            inventory();deadline=min(deadline,origin+cap()['cap_seconds']-before)
            if shutil.disk_usage(ROOT).free<5_000_000_000:raise RuntimeError('5 GB disk floor')
            execute(row,deadline,stage=='sample')
    return dict(completed=len(rows),physical_attempts=len(list((ROOT/'attempts').glob('*.json'))))


if __name__=='__main__':
    import math
    p=argparse.ArgumentParser();p.add_argument('stage',choices=('seal','resolve','sample','project','collect','extend','report'));p.add_argument('--cells',nargs='*',choices=CELLS,default=[]);p.add_argument('--attempt');a=p.parse_args()
    if a.stage in ('extend','report') and a.stage=='extend' and not a.cells:p.error('extend requires explicit cells')
    if a.stage=='resolve' and not a.attempt:p.error('resolve requires --attempt ID')
    if a.stage!='resolve' and a.attempt:p.error('--attempt is only for resolve')
    result=resolve(a.attempt) if a.stage=='resolve' else seal() if a.stage=='seal' else projection() if a.stage=='project' else report(a.cells) if a.stage=='report' else run(a.stage,a.cells)
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','raw_per_fight','cell_reports','pins')},indent=2))
