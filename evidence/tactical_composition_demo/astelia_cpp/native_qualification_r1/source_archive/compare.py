"""Exact JSON comparison; report the first differing step and field."""
import argparse
import json
import math
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent


def difference(a, b, path='$'):
    if type(a) is not type(b) and not (type(a) in (int, float) and type(b) in (int, float)):
        return path, a, b
    if isinstance(a, dict):
        if a.keys() != b.keys():
            return path + '.keys', list(a), list(b)
        for k in a:
            d = difference(a[k], b[k], path + '.' + k)
            if d:
                return d
    elif isinstance(a, list):
        for i, (x, y) in enumerate(zip(a, b)):
            d = difference(x, y, path + f'[{i}]')
            if d:
                return d
        if len(a) != len(b):
            return path + '.length', len(a), len(b)
    elif a != b or (isinstance(a, float) and a == 0 and math.copysign(1, a) != math.copysign(1, b)):
        return path, a, b
    return None


def invoke(command, requests):
    from result_cache import identity
    kind = 'js' if pathlib.Path(command[0]).name == 'node' else 'cpp'
    before = identity(kind, command)
    p = subprocess.run(command, input=''.join(json.dumps(r, separators=(',', ':')) + '\n' for r in requests),
                       text=True, capture_output=True, check=True)
    if identity(kind, command) != before:
        raise RuntimeError('engine identity changed during invocation')
    return [json.loads(line) for line in p.stdout.splitlines()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('fights', type=pathlib.Path)
    ap.add_argument('--trace', action='store_true')
    ap.add_argument('--host', default=str(ROOT / 'build' / 'astelia'))
    ap.add_argument('--cache-dir', type=pathlib.Path, default=ROOT / 'build/combat_cache')
    ap.add_argument('--no-cache', action='store_true')
    args = ap.parse_args()
    requests = [json.loads(s) for s in args.fights.read_text().splitlines() if s.strip()]
    from result_cache import Engine, prime_legacy
    cache_dir = None if args.no_cache else args.cache_dir
    js_engine = Engine('js', ['node', str(ROOT / 'js_host.cjs')], cache_dir)
    cpp_engine = Engine('cpp', [args.host], cache_dir)
    if not args.no_cache:
        prime_legacy(js_engine)
    try:
        for i, req in enumerate(requests):
            if args.trace:
                req = dict(req, trace=True)
            js = js_engine.fight(req)
            cpp = cpp_engine.fight(req)
            d = difference(js, cpp)
            if d:
                print(f'fight {i}: first difference {d[0]}: JS={d[1]!r}, C++={d[2]!r}')
                return 1
    finally:
        js_engine.close()
        cpp_engine.close()
        print(json.dumps({'js': js_engine.counts(), 'cpp': cpp_engine.counts()}))
    print(f'identical: {len(requests)} fights' + (' including every step' if args.trace else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
