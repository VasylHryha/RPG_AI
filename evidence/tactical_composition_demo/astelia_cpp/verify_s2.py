"""Owner-authorized S2 engineering checks only; no tuning or AI experiment.

Retains raw outputs (gzip), requests, exact hashes and uncached qualification
timings. Refuses existing evidence. Run after the complete implementation batch.
"""
import argparse
import concurrent.futures
import copy
import gzip
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time

from benchmark import measure
from build_admission import admit
from result_schema import validate_rows

ROOT = pathlib.Path(__file__).resolve().parent
POOL = ['line', 'wide line', 'wedge', 'box', 'column', 'loose', 'screen',
        'crescent', 'ring', 'wedge hold', 'line anvil', 'wedge flank',
        'loose free', 'swarm', 'loose skirmish', 'loose berserk',
        'storm', 'wolfpack', 'alone']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, indent=2)+'\n')


def compress(path, data):
    path.write_bytes(gzip.compress(data, mtime=0))


def execute(binary, request):
    run = subprocess.run([str(binary)], input=json.dumps(request).encode()+b'\n',
                         capture_output=True, check=True)
    rows = [json.loads(line) for line in run.stdout.splitlines()]
    if run.stderr or validate_rows(request, rows) != 'completed':
        raise RuntimeError('incomplete/error engineering fight')
    return run.stdout


def baseline_binary(directory):
    archive = ROOT/'native_qualification_r1/source_archive'
    records = json.loads((archive/'ARCHIVE.json').read_text())['files']
    for row in records:
        raw = (archive/row['file']).read_bytes()
        if sha(raw) != row['stored_sha256']:
            raise RuntimeError('admitted archive bytes changed: '+row['file'])
        if row['gzip'] and sha(gzip.decompress(raw)) != row['sha256']:
            raise RuntimeError('admitted archive decompressed identity changed')
    record = json.loads((ROOT/'native_qualification_r1/qualification.json').read_text())
    expected = record['native_identity']['build']['binary_sha256']
    raw = gzip.decompress((archive/'build/astelia_native.gz').read_bytes())
    if sha(raw) != expected:
        raise RuntimeError('baseline differs from admitted binary')
    binary = directory/'admitted_native'
    binary.write_bytes(raw)
    binary.chmod(0o700)
    return binary, expected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=pathlib.Path, required=True)
    ap.add_argument('--workers', type=int, default=4)
    args = ap.parse_args()
    if args.workers < 1:
        ap.error('workers must be positive')
    if args.output.exists():
        ap.error('evidence directory exists; preserve it and use a fresh revision')
    args.output.mkdir(parents=True)
    output = args.output
    tests = sorted(ROOT.glob('test_*.py'))
    receipt = {'status': 'RUNNING', 'scope': 'S2 exploratory engineering only',
               'checks': {}, 'outputs': {}}

    def save():
        dump(output/'S2_RECEIPT.json', receipt)

    def store(name, raw):
        path = output/(name+'.gz')
        compress(path, raw)
        receipt['outputs'][path.name] = {'sha256': sha(path.read_bytes()),
                                      'raw_sha256': sha(raw), 'raw_bytes': len(raw)}

    save()
    try:
        print('tests: original 158 checks plus S2 contracts', flush=True)
        command = [str(ROOT.parents[2]/'.venv/bin/python'), '-m', 'pytest', '-q', '-x',
                   *map(str, tests)]
        started = time.perf_counter()
        run = subprocess.run(command, capture_output=True,
            env={**os.environ, 'ASTELIA_S2_EVIDENCE_DIR': str(output.resolve())})
        (output/'tests.stdout.txt').write_bytes(run.stdout)
        (output/'tests.stderr.txt').write_bytes(run.stderr)
        receipt['tests'] = {'command': command, 'seconds': time.perf_counter()-started,
                            'exit_code': run.returncode}
        if run.returncode:
            raise RuntimeError('test batch failed')
        binary = ROOT/'build/astelia_native'
        receipt['identity'] = admit(binary)
        receipt['source_hashes'] = {str(p.relative_to(ROOT)): sha(p.read_bytes())
            for p in [*tests, ROOT/'verify_s2.py', ROOT/'native_controller_contract.cpp']}
        contract = ROOT/'build/native_controller_contract'
        receipt['contract_identity'] = admit(contract)
        receipt['checks']['fence_and_validation'] = json.loads((output/'controller_contract.stdout.txt').read_text().splitlines()[0])
        print('sanitizer: controller observation, identity, decision and branch contracts', flush=True)
        started = time.perf_counter()
        run = subprocess.run([sys.executable, str(ROOT/'build.py'), '--engine', 'controller-check', '--sanitize'], capture_output=True)
        (output/'sanitizer_build.stdout.txt').write_bytes(run.stdout)
        (output/'sanitizer_build.stderr.txt').write_bytes(run.stderr)
        if run.returncode:
            raise RuntimeError('sanitizer build failed')
        sanitized = ROOT/'build/native_controller_contract_sanitized'
        receipt['sanitizer_identity'] = admit(sanitized)
        run = subprocess.run([str(sanitized)], capture_output=True)
        (output/'sanitizer.stdout.txt').write_bytes(run.stdout)
        (output/'sanitizer.stderr.txt').write_bytes(run.stderr)
        receipt['checks']['sanitizer'] = {'exit_code': run.returncode,
            'build_and_run_seconds': time.perf_counter()-started, 'empty_stderr': not run.stderr}
        if run.returncode or run.stderr:
            raise RuntimeError('sanitizer contract failed')
        save()
        with tempfile.TemporaryDirectory(prefix='astelia-s2-', dir='/private/tmp') as temporary:
            baseline, baseline_hash = baseline_binary(pathlib.Path(temporary))
            receipt['admitted_binary_sha256'] = baseline_hash
            references = [json.loads(s) for s in (ROOT/'reference_fights.jsonl').read_text().splitlines()]
            if len(references) != 80:
                raise RuntimeError('reference request count changed')
            payload = b'\n'.join(json.dumps(r['fight']).encode() for r in references)+b'\n'
            reference_outputs = []
            for label, host in [('admitted', baseline), ('s2', binary)]:
                run = subprocess.run([str(host)], input=payload, capture_output=True, check=True)
                rows = [json.loads(s) for s in run.stdout.splitlines()]
                if len(rows) != 80 or any(validate_rows(r['fight'], [row]) != 'completed'
                    for r, row in zip(references, rows)):
                    raise RuntimeError('reference run incomplete')
                reference_outputs.append(run.stdout)
                store('reference_'+label+'.stdout.jsonl', run.stdout)
            store('reference.requests.jsonl', payload)
            equal = reference_outputs[0] == reference_outputs[1]
            receipt['checks']['no_controller_reference'] = {'count': 80, 'byte_identical': equal}
            if not equal:
                raise RuntimeError('no-controller regression against admitted binary')
            save()

        cases = []
        for side in (0, 1):
            for swapped in (False, True):
                for level in ('novice', 'regular', 'elite-fast'):
                    for index, opponent in enumerate(POOL):
                        # Use the source-derived opponent on the non-controller side.
                        # For side 1, explicit enemy/formation options resolve side 0.
                        options = {'seed': 91001+index, 'scenario': 'mirror', 'rules': 'game',
                                   'duration': 20, 'swapSides': swapped, 'sandboxAbilities': True,
                                   'ai': [{}, {}]}
                        options['ai'][side] = {'level': level}
                        request = {'mode': 'alone', 'opponent': opponent, 'trace': True,
                                   'debug': True, 'decisionTrace': True, 'options': options}
                        if side == 1:
                            request['mode'] = opponent if opponent in ('alone', 'storm', 'wolfpack') else 'formation'
                            if request['mode'] == 'formation':
                                options['f'] = {'preset': opponent}
                            # The controller side's explicit level overrides opponent.
                        plugged = copy.deepcopy(request)
                        plugged['options']['ai'][side].update(controller='passthrough', params={})
                        cases.append((side, swapped, level, opponent, request, plugged))
        dump(output/'plumbing.requests.json', [{'side': s, 'swapped': w, 'level': l,
            'opponent': o, 'baseline': b, 'passthrough': p} for s,w,l,o,b,p in cases])

        def plumbing(item):
            index, (side, swapped, level, opponent, request, plugged) = item
            before, after = execute(binary, request), execute(binary, plugged)
            # Both complete raw streams retained, with per-run byte hashes.
            folder = output/'plumbing'
            folder.mkdir(exist_ok=True)
            compress(folder/f'{index:03d}_builtin.jsonl.gz', before)
            compress(folder/f'{index:03d}_passthrough.jsonl.gz', after)
            return {'index': index, 'side': side, 'swapSides': swapped, 'level': level,
                    'opponent': opponent, 'builtin_sha256': sha(before),
                    'passthrough_sha256': sha(after), 'byte_identical': before == after,
                    'frames': len(before.splitlines())-1}

        print(f'plumbing: {len(cases)} full-trace pairs, {args.workers} workers', flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            results = []
            for row in pool.map(plumbing, enumerate(cases)):
                results.append(row)
                if len(results) % 19 == 0:
                    print(f'plumbing: {len(results)}/{len(cases)} checked', flush=True)
        dump(output/'plumbing.results.json', results)
        receipt['checks']['passthrough'] = {'count': len(results),
            'per_side': {str(s): sum(r['side'] == s for r in results) for s in (0,1)},
            'byte_identical': all(r['byte_identical'] for r in results),
            'full_trace_frames': sum(r['frames'] for r in results)}
        if not receipt['checks']['passthrough']['byte_identical']:
            raise RuntimeError('passthrough trace/summary mismatch')
        save()

        print('nearest: first-tick opponent decisions and 114 complete fights', flush=True)
        other_results, nearest_outputs, nearest_requests = [], [], []
        for index, opponent in enumerate(POOL):
            for swapped in (False, True):
                request = {'mode': 'alone', 'opponent': opponent, 'trace': True,
                    'decisionTrace': True, 'options': {'seed': 93001+index, 'scenario': 'mirror',
                    'rules': 'game', 'duration': 1/30, 'swapSides': swapped}}
                plugged = copy.deepcopy(request)
                plugged['options']['ai'] = [{'controller': 'nearest', 'params': {}}, {}]
                before, after = execute(binary, request), execute(binary, plugged)
                store(f'first_tick_{index:02d}_{int(swapped)}_builtin.jsonl', before)
                store(f'first_tick_{index:02d}_{int(swapped)}_nearest.jsonl', after)
                decisions = [[u for u in json.loads(raw.splitlines()[1])['state']['decisions']
                              if u['team'] == 1] for raw in (before, after)]
                other_results.append({'opponent': opponent, 'swapSides': swapped,
                    'request': request, 'controller_request': plugged, 'equal': decisions[0] == decisions[1]})
                for seed_index in range(3):
                    fight = {'mode': 'alone', 'opponent': opponent, 'options': {
                        'seed': 95001+index+100*seed_index, 'scenario': 'mirror', 'rules': 'game',
                        'duration': 20, 'swapSides': swapped, 'sandboxAbilities': True,
                        'ai': [{'controller': 'nearest', 'params': {}}, {}]}}
                    nearest_requests.append(fight)
        dump(output/'other_side.results.json', other_results)
        receipt['checks']['other_side_first_tick'] = {'count': len(other_results),
            'equal': all(r['equal'] for r in other_results)}
        if not receipt['checks']['other_side_first_tick']['equal']:
            raise RuntimeError('other-side first-tick decisions changed')
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            nearest_outputs = list(pool.map(lambda r: execute(binary, r), nearest_requests))
        store('nearest.requests.jsonl', b'\n'.join(json.dumps(r).encode() for r in nearest_requests)+b'\n')
        store('nearest.stdout.jsonl', b''.join(nearest_outputs))
        receipt['checks']['nearest_fights'] = {'count': len(nearest_outputs), 'completed': True}
        # Stronger determinism check: repeat every nearest request in reverse order
        # and fresh hosts, excluding cross-fight/process state contamination.
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            repeats = list(pool.map(lambda r: execute(binary, r), reversed(nearest_requests)))
        repeats.reverse()
        store('nearest.repeat.stdout.jsonl', b''.join(repeats))
        receipt['checks']['nearest_determinism'] = {'count': len(repeats),
            'byte_identical': nearest_outputs == repeats}
        if nearest_outputs != repeats:
            raise RuntimeError('nearest is not deterministic')
        save()

        print('cost: same 50 qualification requests, builtin/nearest/nearest/builtin', flush=True)
        workloads = json.loads((ROOT/'native_workloads.json').read_text())['groups']['basic50']
        if len(workloads) != 50:
            raise RuntimeError('qualification basic50 request count changed')
        builtin = copy.deepcopy(workloads)
        for request in builtin:
            request['mode'] = 'alone'
            request['options']['ai'][0] = {'brain': 'alone'}
        nearest = copy.deepcopy(builtin)
        for request in nearest:
            request['options']['ai'][0] = {'controller': 'nearest', 'params': {}}
        dump(output/'cost.requests.json', {'builtin': builtin, 'nearest': nearest})
        timings = {'builtin': [], 'nearest': []}
        for label in ('builtin', 'nearest', 'nearest', 'builtin'):
            number = len(timings[label])
            started, outputs = measure([str(binary), '--metrics'], builtin if label == 'builtin' else nearest)
            timings[label].append(started)
            store(f'cost_{label}_{number}.stdout.jsonl', b'\n'.join(json.dumps(r).encode() for r in outputs)+b'\n')
        ratio = sum(s['wall_seconds'] for s in timings['nearest'])/sum(s['wall_seconds'] for s in timings['builtin'])
        receipt['checks']['cost'] = {'count': 50, 'samples': timings, 'ratio': ratio,
                                     'maximum': 1.2, 'passed': ratio <= 1.2}
        if ratio > 1.2:
            raise RuntimeError('nearest cost exceeds requested cap')
        if admit(binary) != receipt['identity']:
            raise RuntimeError('build changed during verification')
        for name, expected in receipt['source_hashes'].items():
            if sha((ROOT/name).read_bytes()) != expected:
                raise RuntimeError('harness/test changed during verification')
        # Bind every retained compressed stream, including worker-written traces.
        for path in sorted(output.rglob('*.gz')):
            receipt['outputs'].setdefault(str(path.relative_to(output)), {'sha256': sha(path.read_bytes()),
                'raw_sha256': sha(gzip.decompress(path.read_bytes()))})
        receipt['status'] = 'READY'
        save()
        print(f'READY; nearest/builtin elapsed ratio {ratio:.4f}', flush=True)
        return 0
    except Exception as error:
        receipt.update(status='NOT_READY', error=str(error))
        save()
        raise


if __name__ == '__main__':
    raise SystemExit(main())
