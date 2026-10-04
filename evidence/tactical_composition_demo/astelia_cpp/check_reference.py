"""Permanent behavior gate against committed summaries from the frozen JS."""
import argparse
import json
import pathlib
import subprocess
import sys
from compare import difference

ROOT = pathlib.Path(__file__).resolve().parent


def check(host, reference):
    records = [json.loads(s) for s in reference.read_text().splitlines() if s.strip()]
    requests = ''.join(json.dumps(r['fight'], separators=(',', ':')) + '\n' for r in records)
    run = subprocess.run([str(host)], input=requests, text=True, capture_output=True, check=True)
    outputs = [json.loads(s) for s in run.stdout.splitlines()]
    if len(outputs) != len(records):
        raise RuntimeError(f'expected {len(records)} results, received {len(outputs)}')
    for i, (r, actual) in enumerate(zip(records, outputs)):
        d = difference(r['summary'], actual)
        if d:
            print(f'fight {i} (check-set id {r["check_id"]}): {d[0]} JS={d[1]!r} C++={d[2]!r}')
            return False, run.stdout
    print('identical')
    return True, run.stdout


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--host', type=pathlib.Path, default=ROOT / 'build' / 'astelia')
    p.add_argument('--reference', type=pathlib.Path, default=ROOT / 'reference_fights.jsonl')
    args = p.parse_args()
    ok, _ = check(args.host, args.reference)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
