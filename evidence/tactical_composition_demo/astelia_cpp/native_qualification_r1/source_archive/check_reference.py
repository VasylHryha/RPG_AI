"""Permanent behavior gate against committed summaries from the frozen JS."""
import argparse
import json
import pathlib
import subprocess
import sys
from compare import difference, invoke

ROOT = pathlib.Path(__file__).resolve().parent


def check(host, reference, cache_dir=None):
    records = [json.loads(s) for s in reference.read_text().splitlines() if s.strip()]
    requests = ''.join(json.dumps(r['fight'], separators=(',', ':')) + '\n' for r in records)
    if cache_dir is None:
        outputs = invoke([str(host)], [r['fight'] for r in records])
        stdout = ''.join(json.dumps(row,separators=(',',':'))+'\n' for row in outputs)
    else:
        from result_cache import Engine
        engine = Engine('cpp', [str(host)], cache_dir)
        try:
            outputs = [engine.fight(r['fight'])[-1] for r in records]
        finally:
            engine.close()
        stdout = ''.join(json.dumps(row, separators=(',', ':')) + '\n' for row in outputs)
        print(json.dumps({'cpp': engine.counts()}))
    if len(outputs) != len(records):
        raise RuntimeError(f'expected {len(records)} results, received {len(outputs)}')
    for i, (r, actual) in enumerate(zip(records, outputs)):
        d = difference(r['summary'], actual)
        if d:
            print(f'fight {i} (check-set id {r["check_id"]}): {d[0]} JS={d[1]!r} C++={d[2]!r}')
            return False, stdout
    print('identical')
    return True, stdout


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--host', type=pathlib.Path, default=ROOT / 'build' / 'astelia')
    p.add_argument('--reference', type=pathlib.Path, default=ROOT / 'reference_fights.jsonl')
    p.add_argument('--cache-dir', type=pathlib.Path, default=ROOT / 'build/combat_cache')
    p.add_argument('--no-cache', action='store_true')
    args = p.parse_args()
    ok, _ = check(args.host, args.reference, None if args.no_cache else args.cache_dir)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
