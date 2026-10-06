"""Exactly 60 newly declared traced development fights, no extra replay fights."""
import argparse, concurrent.futures, datetime, gzip, json, os, secrets, subprocess, time
from COMMON import CPP, HERE, IMPL, OLD, PAIRS, RAW, REPO, pins, sha, write
from s3_runner import request
from s4_deadline import Deadline


def prior_inventory():
    found = set(); sources = {}
    def visit(obj, context=''):
        if isinstance(obj, dict):
            for k, v in obj.items(): visit(v, context+' '+k.lower())
        elif isinstance(obj, list):
            for v in obj: visit(v, context)
        elif type(obj) is int and 'seed' in context: found.add(obj)
    for p in CPP.rglob('*.json'):
        if p.is_relative_to(CPP/'build') or p.is_relative_to(HERE): continue
        if 'seed' in p.name.lower():
            visit(json.loads(p.read_text()), 'seed'); sources[str(p.relative_to(REPO))] = sha(p)
    found.update(range(2026100500,2026100530)); found.update(range(2026100700,2026100730))
    found.update([101,102,301,302,303,701,702,703,704,811,812,813])
    return found, sources


def prepare():
    identity = pins()
    # Compare all present pinned tracked inputs with the specified implementation commit.
    matched = []
    for n, h in identity['runtime_hashes'].items():
        p = CPP/n
        if not p.is_relative_to(REPO): continue
        rel = str(p.relative_to(REPO))
        r = subprocess.run(['git','show',IMPL+':'+rel],cwd=REPO,capture_output=True)
        if r.returncode == 0:
            import hashlib
            assert hashlib.sha256(r.stdout).hexdigest() == h, rel
            matched.append(rel)
    identity['commit_source_matches'] = matched
    if RAW.exists(): raise RuntimeError('Never reuse or overwrite a declaration/output')
    old, sources = prior_inventory()
    seeds = []
    while len(seeds) < 10:
        s = 2100000000 + secrets.randbelow(100000000)
        if s not in old and s not in seeds: seeds.append(s)
    RAW.mkdir()
    write(RAW/'DEVELOPMENT_SEED_LEDGER.json', dict(status='FRESH_DEVELOPMENT_ONLY', judging_root=None,
        entropy='OS secrets; uniform rejection from [2100000000,2200000000), excludes prior declared seeds',
        seeds=seeds, shared_across_pairings=True, pairs=PAIRS, orientations=[False,True], controlled_team=0,
        fights=60, prior_seed_count=len(old), prior_declarations=sources,
        created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    identity.update(seed_ledger_sha256=sha(RAW/'DEVELOPMENT_SEED_LEDGER.json'),
        selected_knobs=json.loads((OLD/'B_best.json').read_text()),
        script_hashes={p.name:sha(p) for p in HERE.glob('*.py')},
        diagnostic_thresholds=dict(lock_abs_rad_s=.1, sensitivity_rad_s=[.05,.2],
          reversal='consecutive realized nonzero displacement vectors dot < 0; pauses break adjacency; speed >=1 px/s',
          bins_seconds=2),
        preserved_plan_sha256=sha(REPO/'docs/PLAN_CURRENT.md'),
        limitations=['Original host exports no lethal attacker/hit identity; killer-specific fields unavailable.'])
    write(HERE/'INPUT_IDENTITY.json',identity)
    print(json.dumps(dict(prepared=True, fresh_clusters=10, fights=60, runtime_pins=len(identity['runtime_hashes']),
                          commit_source_matches=len(matched))))


def one(task, deadline):
    pair, cluster, swap, seed, arm, head, params = task
    tag = f'p{pair}_c{cluster:02d}_o{int(swap)}'
    spec = dict(arm=arm, params=params, seed=seed, opponent=head, skeleton='v5', setting='s4_full_head',
                controlledSide=0, swapSides=swap, trace=True, decisionDiagnostics=True,
                attributionDiagnostics=True, endCounts=True)
    req = request(spec); req['decisionTrace'] = True
    write(RAW/(tag+'_REQUEST.json'),req)
    files=[]; current=None; chunk_bytes=0; last=None; lines=0; chunks=0
    with deadline.lock:
        deadline.remaining()
        child=subprocess.Popen([str(CPP/'build/astelia_native'),'--metrics','--capture-s3'],
          stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        deadline.children.add(child)
    try:
        child.stdin.write((json.dumps(req)+'\n').encode()); child.stdin.close()
        for line in child.stdout:
            deadline.remaining()
            if current is None or chunk_bytes+len(line)>30_000_000:
                if current is not None: current.close()
                p=RAW/(tag+f'_{chunks:02d}.jsonl.gz'); chunks+=1
                files.append(str(p.relative_to(HERE)))
                current=gzip.GzipFile(filename=str(p),mode='wb',compresslevel=1,mtime=0); chunk_bytes=0
            current.write(line); chunk_bytes+=len(line); last=line; lines+=1
        current.close(); current=None
        stderr=child.stderr.read(); child.wait(timeout=deadline.remaining())
        if child.returncode: raise RuntimeError(stderr.decode())
        summary=json.loads(last); metrics=json.loads(stderr)
        assert summary['controllerStatus']=='completed' and not any(summary['controllerFailures'])
        assert metrics['executed_fights']==1 and all(metrics[k]==0 for k in ('forks','search_calls','artillery_rollouts','branch_steps'))
        assert all((HERE/f).stat().st_size<45_000_000 for f in files)
        row=dict(id=tag,pair=pair,cluster=cluster,orientation=int(swap),arm=arm,head=head,
                 summary=summary,metrics=metrics,trace_files=files,trace_lines=lines,
                 request_file=str((RAW/(tag+'_REQUEST.json')).relative_to(HERE)))
        write(RAW/(tag+'_COMPLETED.json'),row)
        return row
    except BaseException:
        deadline.stop(); child.wait(timeout=2); raise
    finally:
        if current is not None: current.close()
        with deadline.lock: deadline.children.discard(child)


def execute():
    identity=json.loads((HERE/'INPUT_IDENTITY.json').read_text()); pins()
    for n,h in identity['script_hashes'].items(): assert sha(HERE/n)==h, n
    ledger=json.loads((RAW/'DEVELOPMENT_SEED_LEDGER.json').read_text())
    assert sha(RAW/'DEVELOPMENT_SEED_LEDGER.json') == identity['seed_ledger_sha256']
    with (RAW/'CLAIMED_ONCE.json').open('x') as f:
        json.dump(dict(ledger_sha256=identity['seed_ledger_sha256'], claimed_before_any_fight=True),f)
    start=time.time(); awake=time.monotonic(); deadline=Deadline(awake+1800)
    timing=dict(argv=['/usr/bin/caffeinate','-i','-s','.venv/bin/python',str(pathlib_relative()) ,'--execute'],
                started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),workers=4,expected_minutes=[2,10],
                elapsed_clock='time.time',awake_clock='time.monotonic macOS mach_absolute_time')
    write(HERE/'RUN_START.json',timing)
    results=[]
    tasks=[(p,c,o,s,a,h,identity['selected_knobs'][a]) for p,(a,h) in enumerate(PAIRS)
           for c,s in enumerate(ledger['seeds']) for o in (False,True)]
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            # Fixed finite allocation; no tuning, retry or dependent selection.
            futures=[pool.submit(one,t,deadline) for t in tasks]
            for f in concurrent.futures.as_completed(futures):
                results.append(f.result())
                print(json.dumps(dict(completed=len(results),last=results[-1]['id'])),flush=True)
        assert len(results)==60
        pins()
        for n,h in identity['script_hashes'].items(): assert sha(HERE/n)==h, n
        write(HERE/'FIGHTS.json',sorted(results,key=lambda r:r['id']))
    finally:
        deadline.stop()
        timing.update(elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake,
          finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),completed_fights=len(results))
        write(HERE/'RUN_TIMING.json',timing)


def pathlib_relative(): return (HERE/'RUN_ONCE.py').relative_to(REPO)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--prepare',action='store_true'); ap.add_argument('--execute',action='store_true')
    args=ap.parse_args()
    if args.prepare == args.execute: raise SystemExit('Choose exactly --prepare or --execute')
    prepare() if args.prepare else execute()
