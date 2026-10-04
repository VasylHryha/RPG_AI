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
    p = subprocess.run(command, input=''.join(json.dumps(r, separators=(',', ':')) + '\n' for r in requests),
                       text=True, capture_output=True, check=True)
    return [json.loads(line) for line in p.stdout.splitlines()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('fights', type=pathlib.Path)
    ap.add_argument('--trace', action='store_true')
    ap.add_argument('--host', default=str(ROOT / 'build' / 'astelia'))
    args = ap.parse_args()
    requests = [json.loads(s) for s in args.fights.read_text().splitlines() if s.strip()]
    for i, req in enumerate(requests):
        if args.trace:
            req = dict(req, trace=True)
        js = invoke(['node', str(ROOT / 'js_host.cjs')], [req])
        cpp = invoke([args.host], [req])
        d = difference(js, cpp)
        if d:
            print(f'fight {i}: first difference {d[0]}: JS={d[1]!r}, C++={d[2]!r}')
            return 1
    print(f'identical: {len(requests)} fights' + (' including every step' if args.trace else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
