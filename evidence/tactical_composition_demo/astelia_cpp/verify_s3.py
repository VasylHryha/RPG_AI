"""S3 engineering only: one end-of-batch suite and bounded requested checks.

Never tunes or evaluates a registered panel. All completed stages are retained;
--resume verifies the same source identity and skips completed stages.
"""
import argparse
import concurrent.futures
import gzip
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
from build_admission import admit
from pack_s2 import check_archives
from s3_runner import request, POOL, ARMS
ROOT = pathlib.Path(__file__).resolve().parent


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=pathlib.Path, required=True)
    ap.add_argument('--resume', action='store_true')
    ap.add_argument('--workers', type=int, default=4)
    args = ap.parse_args()
    out = args.output.resolve()
    sources = [*ROOT.glob('test_*.py'), *ROOT.glob('native_*contract.cpp'), ROOT/'verify_s3.py', ROOT/'s3_runner.py',
               ROOT/'build.py', ROOT/'build_admission.py', ROOT/'pack_s2.py', ROOT.parent/'DESIGN_0G.md',
               *sorted((ROOT/'src').rglob('*.h')), *sorted((ROOT/'src').rglob('*.cpp'))]
    hashes = {str(p.relative_to(ROOT.parent)): sha(p.read_bytes()) for p in sources}
    receipt_path = out/'S3_RECEIPT.json'
    if args.resume:
        receipt = json.loads(receipt_path.read_text())
        if receipt['source_hashes'] != hashes:
            raise RuntimeError('sources changed; preserve this attempt and use a new evidence revision')
    else:
        out.mkdir(parents=True, exist_ok=False)
        receipt = dict(status='RUNNING', scope='S3 engineering only; no tuning or recorded experiment',
                       source_hashes=hashes, stages={}, outputs={})
    def save():
        receipt_path.write_text(json.dumps(receipt, indent=2)+'\n')
    def store(name, raw):
        data = gzip.compress(raw, compresslevel=1, mtime=0)
        (out/name).write_bytes(data)
        receipt['outputs'][name] = dict(sha256=sha(data), raw_sha256=sha(raw), raw_bytes=len(raw))
    def stage(name, run):
        if name in receipt['stages']:
            print('skip completed stage: '+name, flush=True)
            return
        print('stage: '+name, flush=True)
        started = time.perf_counter()
        data = run()
        receipt['stages'][name] = dict(seconds=time.perf_counter()-started, **data)
        save()
    def execute(req, flags=()):
        run = subprocess.run([str(ROOT/'build/astelia_native'), *flags], input=json.dumps(req).encode()+b'\n', capture_output=True, check=True)
        return run
    save()
    try:
        def preflight():
            expected = json.loads((ROOT.parents[2]/'research/rrg/v0.2.1.expected.json').read_text())['expected_sha256']
            for name, digest in expected.items():
                if sha((ROOT.parents[2]/'research/rrg/v0.2.1'/name).read_bytes()) != digest:
                    raise RuntimeError('RRG source pin mismatch: '+name)
            return dict(rrg_source_files=len(expected), design_sha256=hashes['DESIGN_0G.md'])
        stage('preflight', preflight)
        def tests():
            command = [str(ROOT.parents[2]/'.venv/bin/python'), '-m', 'pytest', '-q', '-x', *map(str, sorted(ROOT.glob('test_*.py')))]
            run = subprocess.run(command, capture_output=True)
            (out/'tests.stdout.txt').write_bytes(run.stdout);(out/'tests.stderr.txt').write_bytes(run.stderr)
            if run.returncode:
                raise RuntimeError('end-of-batch test suite failed; inspect tests.stdout.txt and tests.stderr.txt')
            return dict(command=command, exit_code=0, stdout_sha256=sha(run.stdout))
        stage('tests', tests)
        binary = ROOT/'build/astelia_native';contract = ROOT/'build/native_s3_contract'
        receipt['identity'] = admit(binary);receipt['contract_identity'] = admit(contract);save()
        def sanitizer():
            build = subprocess.run([sys.executable, str(ROOT/'build.py'), '--engine', 's3-check', '--sanitize'], capture_output=True)
            (out/'sanitizer.build.stdout.txt').write_bytes(build.stdout);(out/'sanitizer.build.stderr.txt').write_bytes(build.stderr)
            if build.returncode: raise RuntimeError('sanitizer build failed')
            checked = ROOT/'build/native_s3_contract_sanitized'
            identity = admit(checked)
            run = subprocess.run([str(checked)], capture_output=True)
            (out/'sanitizer.stdout.txt').write_bytes(run.stdout);(out/'sanitizer.stderr.txt').write_bytes(run.stderr)
            if run.returncode or run.stderr: raise RuntimeError('sanitizer contract failed')
            return dict(identity=identity, exit_code=0, empty_stderr=True)
        stage('sanitizer', sanitizer)
        original_dir = ROOT/'s2_plug_r2' 
        original = json.loads((original_dir/'S2_RECEIPT.json').read_text())
        def old_archives():
            bound = check_archives(original_dir, original)
            return dict(count=len(bound), receipt_sha256=sha((original_dir/'S2_RECEIPT.json').read_bytes()))
        stage('old_archive_identity', old_archives)
        def references():
            requests = [json.loads(s)['fight'] for s in (ROOT/'reference_fights.jsonl').read_text().splitlines()]
            assert len(requests) == 80
            run = subprocess.run([str(binary)], input=b''.join(json.dumps(r).encode()+b'\n' for r in requests), capture_output=True, check=True)
            if run.stderr or sha(run.stdout) != original['outputs']['reference_s2.stdout.jsonl.gz']['raw_sha256']:
                raise RuntimeError('80-request reference bytes changed')
            store('reference.stdout.jsonl.gz', run.stdout)
            return dict(count=80, byte_identical=True)
        stage('references', references)
        def passthrough():
            cases = json.loads((original_dir/'plumbing.requests.json').read_text())
            def check(item):
                i, case = item
                run = execute(case['passthrough'], ('--test-controllers',))
                expected = original['outputs'][f'plumbing/{i:03d}_passthrough.jsonl.gz']
                if run.stderr or sha(run.stdout) != expected['raw_sha256']:
                    raise RuntimeError('passthrough bytes changed at '+str(i))
                return dict(index=i, raw_sha256=sha(run.stdout), original_archive=expected['path'])
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
                rows = list(pool.map(check, enumerate(cases)))
            (out/'passthrough.results.json').write_text(json.dumps(rows, indent=2)+'\n')
            return dict(count=len(rows), byte_identical=True, original_capture_binding='s2_plug_r2/S2_RECEIPT.json')
        stage('passthrough', passthrough)
        def defaults():
            specifications = [(arm, index, swapped, dict(arm=arm, seed=2026100500+index, opponent=opponent, swapSides=swapped, diagnostics=True))
                              for arm in ARMS for index, opponent in enumerate(POOL) for swapped in (False, True)]
            (out/'default.requests.json').write_text(json.dumps([s for _,_,_,s in specifications], indent=2)+'\n')
            def fight(item):
                arm, index, swapped, spec = item
                stem=f'{arm}_{index:02d}_{int(swapped)}'
                finished=out/(stem+'.check.json')
                if finished.exists():
                    cached=json.loads(finished.read_text())
                    if cached.get('passed'):return cached
                flags = ['--metrics'] + (['--capture-s3'] if arm in ('resonator','morale') else [])
                run = execute(request(spec), flags)
                captures=[]; diagnostics=[]; summaries=[]
                for line in run.stdout.splitlines(keepends=True):
                    row = json.loads(line)
                    if row.get('capture'): captures.append(line)
                    elif row.get('diagnostics'): diagnostics.append(line)
                    else: summaries.append(row)
                (out/(stem+'.stderr.txt')).write_bytes(run.stderr)
                if len(summaries) != 1 or summaries[0].get('controllerStatus') != 'completed' or summaries[0]['controllerFailures'] != [0,0]:
                    (out/(stem+'.failed.stdout.jsonl.gz')).write_bytes(gzip.compress(run.stdout, compresslevel=1, mtime=0))
                    raise RuntimeError('default fight failure retained: '+str(spec))
                (out/(stem+'.summary.json')).write_text(json.dumps(summaries[0], indent=2)+'\n')
                raw=b''.join(diagnostics)
                # Each worker owns a unique path; metadata is returned, not shared.
                packed=gzip.compress(raw, compresslevel=1, mtime=0);(out/(stem+'.diagnostics.jsonl.gz')).write_bytes(packed)
                seconds=[json.loads(line)['second'] for line in diagnostics]
                if seconds != list(range(1,len(seconds)+1)):
                    raise RuntimeError('diagnostic seconds missing/out of order')
                refined=None
                if captures:
                    capture=b''.join(captures)
                    replay=subprocess.run([str(contract),'--refinement'],input=capture,capture_output=True,check=True)
                    if replay.stderr:
                        raise RuntimeError('refinement stderr')
                    refined=json.loads(replay.stdout)
                    (out/(stem+'.refinement.json')).write_text(json.dumps(refined,indent=2)+'\n')
                    if refined['samples']<=0 or refined['maximum']>=.02:
                        (out/(stem+'.failed.refinement_input.jsonl.gz')).write_bytes(gzip.compress(capture,compresslevel=1,mtime=0))
                        raise RuntimeError('refinement tolerance exceeded; input retained: '+str(refined))
                    # Preserve one complete replay input per arm. The remaining
                    # inputs are bound by their hashes and deterministic requests.
                    if index==0 and not swapped:
                        (out/(arm+'.refinement_input.jsonl.gz')).write_bytes(gzip.compress(capture,compresslevel=1,mtime=0))
                    refined['input_sha256']=sha(capture);refined['input_bytes']=len(capture)
                result=dict(passed=True,arm=arm,index=index,swapSides=swapped,summary=summaries[0],refinement=refined,
                            metrics=json.loads(run.stderr),diagnostics_file=stem+'.diagnostics.jsonl.gz',
                            diagnostics_raw_sha256=sha(raw),diagnostics_rows=len(diagnostics))
                finished.write_text(json.dumps(result,indent=2)+'\n')
                return result
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
                rows=[]
                for row in pool.map(fight,specifications):
                    rows.append(row)
                    if len(rows)%19==0: print(f'default fights: {len(rows)}/{len(specifications)}',flush=True)
            (out/'default.results.json').write_text(json.dumps(rows,indent=2)+'\n')
            return dict(count=len(rows), per_arm={arm:sum(r['arm']==arm for r in rows) for arm in ARMS}, controller_failures=0,
                        refinement_maxima={arm:max(r['refinement']['maximum'] for r in rows if r['arm']==arm) for arm in ('resonator','morale')})
        stage('defaults', defaults)
        def determinism_cost():
            reference=json.loads((out/'default.results.json').read_text())
            rows=[]
            # One fresh-process replay per arm is also the cost sample, excluding
            # diagnostic/capture/replay overhead and with real planner counters.
            for arm in ARMS:
                spec=dict(arm=arm,seed=2026100500,opponent=POOL[0],swapSides=False)
                started=time.perf_counter();run=execute(request(spec),('--metrics',));elapsed=time.perf_counter()-started
                row=json.loads(run.stdout)
                before=next(r['summary'] for r in reference if r['arm']==arm and r['index']==0 and not r['swapSides'])
                if row!=before:raise RuntimeError('determinism/diagnostic feedback: '+arm)
                rows.append(dict(arm=arm,wall_seconds=elapsed,metrics=json.loads(run.stderr),deterministic=True,summary=row))
            nearest=next(r['wall_seconds'] for r in rows if r['arm']=='nearest')
            for row in rows:row['cost_ratio_to_nearest']=row['wall_seconds']/nearest
            (out/'determinism_cost.json').write_text(json.dumps(rows,indent=2)+'\n')
            return dict(count=4,deterministic=True,scope='one uncached full fight per arm; elapsed includes host startup; no cost cap registered')
        stage('determinism_cost', determinism_cost)
        if admit(binary)!=receipt['identity'] or admit(contract)!=receipt['contract_identity']:
            raise RuntimeError('build identity changed during checks')
        for name,digest in hashes.items():
            if sha((ROOT.parent/name).read_bytes())!=digest:raise RuntimeError('source changed during checks: '+name)
        receipt['artifacts']={str(p.relative_to(out)):sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file() and p!=receipt_path}
        receipt['status']='READY';save()
        print('S3 engineering READY; Claude review remains required',flush=True)
    except Exception as exc:
        receipt['status']='NOT_READY';receipt['error']=str(exc);save();raise


if __name__ == '__main__':
    main()
