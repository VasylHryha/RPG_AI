"""Check array input, retained outputs across collection, and mixed rule sets."""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
from compare import difference

ROOT = pathlib.Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=pathlib.Path, required=True)
    args = ap.parse_args()
    records = [json.loads(s) for s in (ROOT / 'reference_fights.jsonl').read_text().splitlines()]
    chosen = [next(r for r in records if r['check_id'] == i) for i in (0, 23, 621)]
    chosen.insert(1, next(r for r in records if 'error' in r['summary']))
    payload = json.dumps([r['fight'] for r in chosen]) + '\n'
    args.output.mkdir(parents=True, exist_ok=True)
    if (args.output / 'batch_input.json').exists():
        ap.error('batch evidence exists; use a new output directory')
    (args.output / 'batch_input.json').write_text(payload)
    outputs = {}
    for label, command in [('js', ['node', str(ROOT / 'js_host.cjs')]),
                           ('cpp', [str(ROOT / 'build/astelia')])]:
        run = subprocess.run(command, input=payload, text=True, capture_output=True, check=True,
                             cwd='/private/tmp')
        (args.output / ('batch_' + label + '.json')).write_text(run.stdout)
        outputs[label] = json.loads(run.stdout)
    d = difference(outputs['js'], outputs['cpp']) or difference([r['summary'] for r in chosen], outputs['cpp'])
    receipt = dict(count=len(chosen), check_ids=[r['check_id'] for r in chosen], first_difference=d,
                   binary_sha256=hashlib.sha256((ROOT / 'build/astelia').read_bytes()).hexdigest(),
                   working_directory='/private/tmp')
    (args.output / 'batch.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('batch identical: 4 requests' if d is None else 'batch mismatch: ' + repr(d))
    return int(d is not None)


if __name__ == '__main__':
    sys.exit(main())
