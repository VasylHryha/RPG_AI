"""Compare changed C++ against immutable JS combat evidence, without replaying JS."""
import argparse
import gzip
import hashlib
import json
import pathlib
import time
from compare import difference, invoke
from result_cache import Engine, prime_legacy, DEFAULT_CACHE, sha

ROOT = pathlib.Path(__file__).resolve().parent


def canonical(rows):
    return ''.join(json.dumps(row, sort_keys=True, separators=(',', ':'))+'\n' for row in rows).encode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=pathlib.Path, required=True)
    ap.add_argument('--cache-dir', type=pathlib.Path, default=DEFAULT_CACHE)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if (args.output / 'fight_results.jsonl').exists():
        ap.error('evidence exists; use a new output directory')
    js = Engine('js', ['node', str(ROOT / 'js_host.cjs')], args.cache_dir)
    cpp = Engine('cpp', [str(ROOT / 'build/astelia')], args.cache_dir)
    begin = time.perf_counter()
    imported = prime_legacy(js)
    requests = [json.loads(s) for s in (ROOT / 'check_fights.jsonl').read_text().splitlines()]
    selection = json.loads((ROOT / 'check_selection.json').read_text())
    trace_ids = set(selection['trace_ids'])
    receipt = dict(status='RUNNING', imported_js_entries=imported,
                   js_identity=js.identity, cpp_identity=cpp.identity,
                   inputs_sha256=sha(ROOT/'check_fights.jsonl'), selection_sha256=sha(ROOT/'check_selection.json'),
                   identical=0, completed=0, matching_errors=0, traces=[])
    for path in sorted((ROOT/'src').glob('*')):
        if path.is_file():
            receipt.setdefault('code_hashes', {})['src/'+path.name] = sha(path)

    def save():
        receipt.update(js=js.counts(), cpp=cpp.counts(), elapsed_seconds=time.perf_counter()-begin)
        (args.output/'checks.json').write_text(json.dumps(receipt, indent=2)+'\n')

    # The existing contracts are source-grounded JS outputs, not a new JS run.
    contracts = [json.loads(s) for s in (ROOT/'checks_r2/math_results.jsonl').read_text().splitlines()]
    actual = invoke(cpp.command, [row['input'] for row in contracts])
    d = difference([row['js'] for row in contracts], actual)
    (args.output/'math_results.jsonl').write_text(''.join(json.dumps(dict(input=row['input'], js=row['js'], cpp=got),
        sort_keys=True, separators=(',', ':'))+'\n' for row, got in zip(contracts, actual)))
    receipt['math_contracts'] = dict(count=len(contracts), first_difference=d)
    if d:
        receipt.update(status='MISMATCH', first_difference=d);save();return 1
    save()
    try:
        with (args.output/'fight_results.jsonl').open('w') as journal:
            for i, request in enumerate(requests):
                traced = i in trace_ids
                req = dict(request, trace=True) if traced else request
                a, b = js.fight(req), cpp.fight(req)
                d = difference(a, b)
                journal.write(json.dumps(dict(check_id=i, fight=request, js=a[-1], cpp=b[-1], difference=d),
                                         sort_keys=True, separators=(',', ':'))+'\n')
                journal.flush()
                if traced:
                    payload, native = canonical(a), canonical(b)
                    filename = f'trace_{i:04d}.jsonl.gz'
                    (args.output/filename).write_bytes(gzip.compress(native, mtime=0))
                    receipt['traces'].append(dict(check_id=i, frames=len(a)-1, identical=d is None,
                        js_sha256=hashlib.sha256(payload).hexdigest(), cpp_sha256=hashlib.sha256(native).hexdigest(), file=filename))
                if d:
                    receipt.update(status='MISMATCH', first_difference=dict(check_id=i, difference=d))
                    save();print('first difference',i,d,flush=True);return 1
                receipt['identical'] += 1
                receipt['matching_errors' if 'error' in b[-1] else 'completed'] += 1
                # Also cache a trace's terminal summary for summary-only callers.
                if traced:
                    cpp.cache.put(request, [b[-1]], 'terminal summary of fresh/verified trace')
                if (i+1)%25==0 or i+1==len(requests):
                    print(f'{i+1}/{len(requests)} identical; JS {js.counts()}; C++ {cpp.counts()}',flush=True)
                save()
    finally:
        js.close();cpp.close()
    receipt['status']='IDENTICAL';save()
    print(json.dumps(receipt,indent=2),flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
