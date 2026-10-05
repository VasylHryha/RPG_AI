"""One complete comparison batch; commit raw outputs and compact receipts."""
import argparse
import gzip
import hashlib
import json
import os
import pathlib
import platform
import resource
import subprocess
import sys
import time
from compare import difference, invoke
from check_reference import check

ROOT = pathlib.Path(__file__).resolve().parent
JS = ['node', str(ROOT / 'js_host.cjs')]
CPP = [str(ROOT / 'build' / 'astelia')]
SOURCE_HASHES = {'formation_sim.js': '85b16e9b84b42b831dd2e64a7055474b6df902e4c1ffd635e6670fc6fb665733',
                 'bc_net.json': 'd11e9a2da43cb0eb5b8b9539be4ab5834e750b4148121d56e632c75d7fb2e3e5'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n'


class Host:
    def __init__(self, command):
        self.p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True, bufsize=1)

    def fight(self, req):
        self.p.stdin.write(json.dumps(req, separators=(',', ':')) + '\n')
        self.p.stdin.flush()
        rows = []
        while True:
            s = self.p.stdout.readline()
            if not s:
                raise RuntimeError(f'host exited: {self.p.poll()}; {self.p.stderr.read()}')
            row = json.loads(s)
            rows.append(row)
            if 'step' not in row:
                return rows

    def close(self):
        self.p.stdin.close()
        code = self.p.wait()
        error = self.p.stderr.read()
        if code:
            raise RuntimeError(f'host failed: {code}, {error}')


def math_contracts():
    vectors = []
    values = [-0.0, 0.0, -2.5, -.5, -.49999999999999994, .49999999999999994, .5, 1.5, 2.5,
              -1e-300, 1e-300, -1000000, 1000000, 4503599627370495.5]
    for name in ('sin', 'cos', 'round', 'abs', 'floor', 'ceil'):
        vectors.extend(dict(operation='math', name=name, args=[x]) for x in values)
    for y in values[:-1]:
        for x in values[:-1]:
            vectors.append(dict(operation='math', name='atan2', args=[y, x]))
            vectors.append(dict(operation='math', name='hypot', args=[y, x]))
    for seed in (0, 1, -1, 2**31, 2**32 - 1, 2**32, 2**53 - 1, 1.5, -2.5):
        for mode in ('any', 'pool'):
            vectors.append(dict(operation='rng', seed=seed, rounds=19, drawMode=mode))
    for value in [-0.0, -.001, -2.5, 2.5, 8.5, 9.5, 1.25, 9.25, 2.675, 1.005, 1.0/3, 1e-300, 1e20, 1e21]:
        for digits in (0, 1, 2, 15, 100):
            vectors.append(dict(operation='fixed', value=value, digits=digits))
    for value in ['astral: \U0001f43e', 'lone: \ud800', '\udfff', 'é\t\n\\"', {'3': 'three', '1': 'one', 'a': 0, '01': 1, '__proto__': 2}]:
        vectors.extend([dict(operation='echo', value=value), dict(operation='keys', value=value)])
    for value in ['abc', '\U0001f43eé', '\ud800x\udfff']:
        vectors.append(dict(operation='string', method='length', value=value))
        for method, arguments in [('split', ['']), ('split', ['x']), ('split', [None]), ('includes', ['é']), ('indexOf', ['é'])]:
            vectors.append(dict(operation='string', method=method, value=value, args=arguments))
    for seed in [' 1\n', '\u00a01\ufeff', '0x100000001', '0b1001', '0o11', '-0x1', '']:
        vectors.append(dict(operation='rng', seed=seed, rounds=19))
    a, b = invoke(JS, vectors), invoke(CPP, vectors)
    return vectors, a, b, difference(a, b)


def timed(command, fights):
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    load_before = os.getloadavg()
    start = time.perf_counter()
    outputs = invoke(command, fights)
    wall = time.perf_counter() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    return dict(wall_seconds=wall, user_seconds=after.ru_utime - before.ru_utime,
                system_seconds=after.ru_stime - before.ru_stime, seconds_per_fight=wall / len(fights),
                load_before=load_before, load_after=os.getloadavg()), outputs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=pathlib.Path, default=ROOT / 'checks')
    ap.add_argument('--diagnostic-count', type=int)
    args = ap.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'fight_results.jsonl').exists():
        ap.error('output already has raw fight results; use a new directory for a changed revision')
    for name, expected in SOURCE_HASHES.items():
        if sha(ROOT.parent / 'astelia_snapshot' / name) != expected:
            raise RuntimeError('frozen source hash mismatch: ' + name)
    fights = [json.loads(s) for s in (ROOT / 'check_fights.jsonl').read_text().splitlines()]
    selection = json.loads((ROOT / 'check_selection.json').read_text())
    trace_ids = set(selection['trace_ids'])
    if args.diagnostic_count:
        fights = fights[:args.diagnostic_count]
    receipt = dict(status='RUNNING', started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                   machine=dict(system=platform.platform(), processor=platform.processor(), cpu_count=os.cpu_count()),
                   node=json.loads(subprocess.check_output(['node', '-p', 'JSON.stringify(process.versions)'], text=True)),
                   source_hashes=SOURCE_HASHES, binary_sha256=sha(pathlib.Path(CPP[0])),
                   inputs_sha256=sha(ROOT / 'check_fights.jsonl'), selection_sha256=sha(ROOT / 'check_selection.json'),
                   planned=len(fights), identical=0, successful_fights=0, identical_errors=0, traces=[],
                   policy=selection['policy'])
    for p in sorted((ROOT / 'src').glob('*')):
        if p.is_file():
            receipt.setdefault('code_hashes', {})['src/' + p.name] = sha(p)
    def save():
        (out / 'checks.json').write_text(json.dumps(receipt, indent=2) + '\n')
    save()
    vectors, math_js, math_cpp, d = math_contracts()
    (out / 'math_results.jsonl').write_text(''.join(canonical(dict(input=r, js=a, cpp=b)) for r, a, b in zip(vectors, math_js, math_cpp)))
    receipt['math_contracts'] = dict(count=len(vectors), first_difference=d)
    if d:
        receipt['status'] = 'MISMATCH'
        save()
        print('math mismatch', d, flush=True)
        return 1
    js, cpp = Host(JS), Host(CPP)
    results = []
    begin = time.monotonic()
    try:
        with (out / 'fight_results.jsonl').open('w') as journal:
            for i, req in enumerate(fights):
                traced = i in trace_ids
                request = dict(req, trace=True) if traced else req
                t = time.monotonic()
                a = js.fight(request)
                b = cpp.fight(request)
                d = difference(a, b)
                journal.write(canonical(dict(check_id=i, fight=req, js=a[-1], cpp=b[-1], difference=d)))
                journal.flush()
                results.append(a[-1])
                if traced:
                    payload = ''.join(canonical(row) for row in a).encode()
                    payload_b = ''.join(canonical(row) for row in b).encode()
                    trace_file = f'trace_{i:04d}.jsonl.gz'
                    (out / trace_file).write_bytes(gzip.compress(payload, mtime=0))
                    if d:
                        (out / f'trace_{i:04d}_cpp.jsonl.gz').write_bytes(gzip.compress(payload_b, mtime=0))
                    receipt['traces'].append(dict(check_id=i, frames=sum('step' in row for row in a),
                        js_sha256=hashlib.sha256(payload).hexdigest(), cpp_sha256=hashlib.sha256(payload_b).hexdigest(),
                        identical=d is None, completed='error' not in a[-1], file=trace_file))
                if d:
                    receipt.update(status='MISMATCH', first_difference=dict(check_id=i, path=d[0], js=d[1], cpp=d[2]))
                    save()
                    # Failure diagnosis is specifically authorized; no successful fight is repeated here.
                    if not traced:
                        (out / 'mismatch_fight.jsonl').write_text(json.dumps(dict(req, trace=True)) + '\n')
                        print(f'fight {i} mismatch {d}; trace request saved', flush=True)
                    else:
                        print(f'fight {i} trace mismatch {d}', flush=True)
                    return 1
                receipt['identical'] += 1
                receipt['identical_errors' if 'error' in a[-1] else 'successful_fights'] += 1
                print(f'{i+1}/{len(fights)} identical ({time.monotonic()-t:.2f}s); elapsed {(time.monotonic()-begin)/60:.1f} min', flush=True)
                save()
    finally:
        js.close()
        cpp.close()
    if args.diagnostic_count:
        receipt['status'] = 'DIAGNOSTIC_IDENTICAL'
        save()
        return 0
    references = [dict(check_id=i, fight=fights[i], summary=results[i]) for i in selection['reference_ids']]
    (ROOT / 'reference_fights.jsonl').write_text(''.join(canonical(r) for r in references))
    ok, first = check(pathlib.Path(CPP[0]), ROOT / 'reference_fights.jsonl')
    second = subprocess.run(CPP, input=''.join(json.dumps(r['fight']) + '\n' for r in references), text=True,
                            capture_output=True, check=True).stdout
    receipt['reference'] = dict(count=len(references), identical=ok, sha256=sha(ROOT / 'reference_fights.jsonl'))
    receipt['determinism'] = dict(count=len(references), identical=first == second,
                                 first_sha256=hashlib.sha256(first.encode()).hexdigest(), second_sha256=hashlib.sha256(second.encode()).hexdigest())
    (out / 'determinism_first.jsonl').write_text(first)
    (out / 'determinism_second.jsonl').write_text(second)
    speed_fights = [fights[i] for i in selection['speed_ids']]
    (out / 'speed_fights.jsonl').write_text(''.join(canonical(r) for r in speed_fights))
    # Serial, single process per implementation, identical input and output serialization.
    print('timing 50 JS fights', flush=True)
    js_time, a = timed(JS, speed_fights)
    print('timing 50 C++ fights', flush=True)
    cpp_time, b = timed(CPP, speed_fights)
    receipt['speed'] = dict(count=50, js=js_time, cpp=cpp_time,
                            speed_up=js_time['wall_seconds'] / cpp_time['wall_seconds'], first_difference=difference(a, b),
                            note='Wall time includes host startup, network load, JSON IO, and host memory reclamation; no worker parallelism.')
    (out / 'speed_results.jsonl').write_text(''.join(canonical(dict(check_id=i, js=x, cpp=y)) for i, x, y in zip(selection['speed_ids'], a, b)))
    receipt['status'] = 'IDENTICAL' if ok and first == second and difference(a, b) is None else 'MISMATCH'
    receipt['elapsed_seconds'] = time.monotonic() - begin
    save()
    print(json.dumps({k: receipt[k] for k in ('status', 'identical', 'successful_fights', 'identical_errors', 'speed')}, indent=2), flush=True)
    return 0 if receipt['status'] == 'IDENTICAL' else 1


if __name__ == '__main__':
    sys.exit(main())
