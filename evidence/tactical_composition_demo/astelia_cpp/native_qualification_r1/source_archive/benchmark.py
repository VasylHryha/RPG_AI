"""Fresh paired end-to-end timing; diagnostics cannot claim native qualification."""
import argparse
import hashlib
import json
import math
import os
import pathlib
import resource
import subprocess
import time
from compare import difference
from result_cache import identity, encoded, digest
from result_schema import validate_summary, validate_completion, timing_options

ROOT = pathlib.Path(__file__).resolve().parent


def measure(command, requests):
    for request in requests:
        timing_options(request)
    payload = b'\n'.join(encoded(r) for r in requests) + b'\n'
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    load_before = os.getloadavg()
    begin = time.perf_counter()
    run = subprocess.run(command, input=payload, capture_output=True, check=True)
    wall = time.perf_counter() - begin
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    outputs = [json.loads(s) for s in run.stdout.splitlines()]
    metrics = json.loads(run.stderr)
    if len(outputs) != len(requests):
        raise RuntimeError('host omitted or added combat outputs')
    expected_steps = 0
    for request, row in zip(requests, outputs):
        validate_summary(row, allow_error=False)
        if row['mode'] != (request.get('mode') or 'alone'):
            raise RuntimeError('request/output mode mismatch')
        expected_steps += validate_completion(request, row)
    if not isinstance(metrics, dict):
        raise RuntimeError('invalid execution metrics')
    for key in ('executed_fights', 'executed_steps', 'cache_hits'):
        if type(metrics.get(key)) is not int or metrics[key] < 0:
            raise RuntimeError('invalid execution metric: ' + key)
    if metrics['executed_fights'] != len(requests) or metrics['cache_hits'] != 0:
        raise RuntimeError('timing did not freshly execute every requested fight')
    if metrics['executed_steps'] != expected_steps:
        raise RuntimeError('executed-step metric disagrees with final fight times')
    return dict(wall_seconds=wall, seconds_per_fight=wall/len(requests),
                user_seconds=after.ru_utime-before.ru_utime,
                system_seconds=after.ru_stime-before.ru_stime,
                load_before=load_before, load_after=os.getloadavg(), execution=metrics), outputs


def qualification(groups, native_identity, diagnostic=False, minimum=3.0):
    if diagnostic:
        return 'DIAGNOSTIC_ONLY'
    if set(groups) != {'basic50','elite','elite-fast','artillery-rollout'}:
        return 'INCOMPLETE_WORKLOAD'
    if native_identity.get('build', {}).get('scope') != 'native_complete_engine':
        return 'INCOMPLETE_NATIVE_ENGINE'
    if any(type(g.get('speed_up')) not in (int, float) or not math.isfinite(g['speed_up']) or g['speed_up'] <= 0 for g in groups.values()):
        return 'INVALID_TIMING'
    if any(g['speed_up'] < minimum for g in groups.values()):
        return 'BELOW_MINIMUM'
    for name in ('elite','elite-fast','artillery-rollout'):
        required = ('branch_steps','forks','search_calls','inference_calls') if name != 'artillery-rollout' else ('branch_steps','forks','artillery_rollouts')
        samples = groups[name].get('samples', {}).get('cpp', [])
        if len(samples) != 2 or any(any(type(s.get('execution', {}).get(k)) is not int or
                s['execution'][k] <= 0 for k in required) for s in samples):
            return 'MISSING_BRANCH_WORK'
    # Work audit, matched-state probes and correctness are separate bound receipts.
    return 'TIMING_PASSED_AWAITING_WORK_AND_CORRECTNESS_REVIEW'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fights', type=pathlib.Path)
    ap.add_argument('--group', choices=['all','basic50','elite','elite-fast','artillery-rollout'], default='basic50')
    ap.add_argument('--count', type=int)
    ap.add_argument('--host', type=pathlib.Path, default=ROOT/'build/astelia_native')
    ap.add_argument('--diagnostic', action='store_true')
    ap.add_argument('--require-identical', action='store_true')
    ap.add_argument('--output', type=pathlib.Path, required=True)
    args = ap.parse_args()
    if args.count is not None and args.count <= 0:
        ap.error('--count must be positive')
    if (args.fights or args.count) and not args.diagnostic:
        ap.error('changed/subset inputs require --diagnostic')
    args.output.mkdir(parents=True, exist_ok=True)
    if (args.output/'benchmark.json').exists():
        ap.error('benchmark evidence exists; use a fresh output directory')
    contract = json.loads((ROOT/'native_workloads.json').read_text())
    engineering = json.loads((ROOT/'native_contract.json').read_text())
    if hashlib.sha256((ROOT/'native_workloads.json').read_bytes()).hexdigest() != engineering['workloads_sha256']:
        ap.error('workloads do not match the frozen engineering contract')
    groups = contract['groups'] if args.group == 'all' else {args.group:contract['groups'][args.group]}
    if args.fights:
        groups = {'custom':[json.loads(s) for s in args.fights.read_text().splitlines() if s.strip()]}
    if args.count:
        groups = {name:rows[:args.count] for name, rows in groups.items()}
    if not all(groups.values()):
        ap.error('empty timing group')
    commands = {'js':['node',str(ROOT/'benchmark_host.cjs')], 'cpp':[str(args.host),'--metrics']}
    identities = {kind:identity('js' if kind=='js' else 'cpp',command) for kind,command in commands.items()}
    harness_files = [ROOT/'benchmark.py', ROOT/'native_workloads.json', ROOT/'native_contract.json']
    if args.fights:
        harness_files.append(args.fights.resolve())
    harness_identity = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in harness_files}
    def check_harness():
        if any(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() != h for p,h in harness_identity.items()):
            raise RuntimeError('benchmark harness or input identity changed')
    receipt = dict(cache_policy='bypassed; fresh paired processes',status='RUNNING',
                   identities=identities,harness_identity=harness_identity,workloads_sha256=digest(groups),groups={})
    def save():
        (args.output/'benchmark.json').write_text(json.dumps(receipt,indent=2)+'\n')
    save()
    try:
        for name, requests in groups.items():
            group = dict(count=len(requests),inputs_sha256=digest(requests),samples={'js':[],'cpp':[]})
            receipt['groups'][name] = group
            outputs = {}
            for label in ('js','cpp','cpp','js'):
                check_harness()
                if identity('js' if label=='js' else 'cpp',commands[label]) != identities[label]:
                    raise RuntimeError('engine identity changed before timed run')
                print(f'{name}: timing {label}, {len(requests)} fresh fights',flush=True)
                timing, rows = measure(commands[label],requests)
                check_harness()
                if identity('js' if label=='js' else 'cpp',commands[label]) != identities[label]:
                    raise RuntimeError('engine identity changed during timed run')
                index = len(group['samples'][label]);group['samples'][label].append(timing)
                (args.output/f'{name}_{label}_{index}.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in rows))
                if label in outputs and difference(outputs[label],rows):
                    raise RuntimeError('fresh executions of one engine differ')
                outputs[label] = rows;save()
            group['first_difference'] = difference(outputs['js'],outputs['cpp'])
            group['same_outer_step_count'] = group['samples']['js'][0]['execution']['executed_steps'] == group['samples']['cpp'][0]['execution']['executed_steps']
            group['speed_up'] = sum(x['wall_seconds'] for x in group['samples']['js'])/sum(x['wall_seconds'] for x in group['samples']['cpp'])
            if args.require_identical and group['first_difference']:
                raise RuntimeError('requested exact equivalence failed')
            save()
        receipt['status'] = qualification(receipt['groups'],identities['cpp'],args.diagnostic)
        save();print(json.dumps(receipt,indent=2),flush=True)
        return 0 if args.diagnostic or receipt['status']=='TIMING_PASSED_AWAITING_WORK_AND_CORRECTNESS_REVIEW' else 1
    except Exception as error:
        receipt.update(status='FAILED',error=str(error));save();raise


if __name__ == '__main__':
    raise SystemExit(main())
