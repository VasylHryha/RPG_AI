"""Offline descriptive audit of retained 0h artifacts. Never imports run code.

No simulation, entropy generation, calibration fitting or verdict calculation.
Outputs go to a new directory, outside the immutable development receipt tree.
Evaluation averages cannot identify per-episode/per-step abstention rates.
"""
import argparse
import collections
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TASKS = ('perceive', 'move', 'remember_static', 'choose')
TOL = 1e-12


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt') as stream:
        return json.load(stream)


def content_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


def geometry(members):
    require(bool(members), 'empty template')
    require(all(len(m) == 5 and all(math.isfinite(v) for v in m) for m in members),
            'invalid template scalars')
    radii = [math.hypot(*m[:2]) for m in members]
    selected = [m for m, r in zip(members, radii) if r < 2.]
    weights = [math.exp(-(m[0] ** 2 + m[1] ** 2) / 2.) for m in selected]
    total = sum(weights)
    real = sum(w * math.cos(m[2]) for w, m in zip(weights, selected))
    imag = sum(w * math.sin(m[2]) for w, m in zip(weights, selected))
    coherence = min(1., math.hypot(real, imag) / total) if total else 0.
    # Potential input reach at copy time, independent of which slots are active.
    sites = [(4 * math.cos(s * math.pi / 4), 4 * math.sin(s * math.pi / 4))
             for s in range(8)]
    driven = sum(any(math.hypot(m[0] - x, m[1] - y) < 3. for x, y in sites)
                 for m in members)
    return dict(size=len(members), min_radius=min(radii), max_radius=max(radii),
                readout_members=len(selected), readout_weight=total,
                copy_time_coherence=coherence, copy_time_abstain=coherence < .05,
                potential_driven_members=driven)


def score_summary(values, floor):
    require(bool(values) and all(math.isfinite(v) for v in values), 'invalid score sample')
    return dict(count=len(values), mean=statistics.mean(values), minimum=min(values),
                maximum=max(values), above_floor=sum(v > floor + TOL for v in values),
                equal_floor=sum(abs(v - floor) <= TOL for v in values),
                below_floor=sum(v < floor - TOL for v in values),
                above_calibrated_random=sum(v > TOL for v in values),
                above_both=sum(v > max(0., floor) + TOL for v in values))


def audit_ledger(path, expected):
    """Stream decoded bytes; inspect event headers, not 601-frame state payloads.

    All decoded bytes are hashed, including skipped adaptation/recovery records.
    Counts and selected events are descriptive; recorded readouts are untouched.
    """
    require(path.stat().st_size == expected['archive_bytes'], f'size: {path}')
    require(sha(path) == expected['archive_sha256'], f'archive hash: {path}')
    digest = hashlib.sha256()
    size = records = 0
    rules, late_reasons, drops = collections.Counter(), collections.Counter(), collections.Counter()
    birth_sites = collections.Counter()
    death_locks = []
    event_file = path.name == 'events.jsonl.gz'
    with gzip.open(path, 'rb') as stream:
        for line in stream:
            require(line.endswith(b'\n'), f'partial JSONL record: {path}')
            digest.update(line)
            size += len(line)
            records += 1
            if not event_file:
                continue
            match = re.search(rb'"rule":"([^"]+)"', line[:256])
            require(match is not None, f'missing event rule: {path}:{records}')
            rule = match[1].decode('ascii')
            rules[rule] += 1
            if rule in ('B1_rejected', 'control_drop', 'B1', 'D1', 'D3'):
                row = json.loads(line)
                v = row['values']
                if rule == 'B1_rejected' and row['time'] >= 25600:
                    late_reasons[v['reason']] += 1
                if rule == 'control_drop':
                    drops[v['reason']] += 1
                if rule == 'B1':
                    birth_sites[str(v['site'])] += 1
                if rule == 'D1':
                    death_locks.append(v['lock'])
    require((digest.hexdigest(), size, records) ==
            (expected['decoded_sha256'], expected['decoded_bytes'], expected['records']),
            f'decoded receipt mismatch: {path}')
    return dict(path=expected['retained_path'], archive_sha256=expected['archive_sha256'],
                decoded_sha256=digest.hexdigest(), decoded_bytes=size, records=records,
                rules=dict(rules), late_rejection_reasons=dict(late_reasons),
                drop_reasons=dict(drops), birth_sites=dict(birth_sites),
                D1_lock_max=max(death_locks) if death_locks else None)


def audit(source, output, ledgers=False):
    require(source.resolve() == (HERE / 'development_20261006').resolve(), 'wrong retained run')
    require(not output.exists(), 'output directory must be new')
    require(not output.resolve().is_relative_to(source.resolve()), 'immutable receipt tree')
    artifacts = load(source / 'ARTIFACTS.json')
    transport = load(source / 'AUDIT_TRANSPORT.json')
    ledger_paths = {r['retained_path'] for r in transport['ledgers']}
    verified = {}
    for relative, receipt in artifacts.items():
        path = HERE / relative
        require(path.resolve().is_relative_to(source.resolve()), 'artifact escapes retained tree')
        require(path.stat().st_size == receipt['bytes'], f'artifact size: {path}')
        if relative not in ledger_paths:
            require(sha(path) == receipt['sha256'], f'artifact hash: {path}')
            verified[relative] = receipt
    results = load(source / 'RESULTS.json')
    calibration = load(source / 'CALIBRATION.json')
    require(calibration['usable'] == list(TASKS), 'unexpected usable task set')
    identity = load(source / 'IDENTITY.json')
    post = load(HERE / 'DEVELOPMENT_POSTFLIGHT.json')
    require(all(identity[k] == post[k] for k in ('source_sha256', 'harness_sha256', 'build')),
            'pre/post source or build mismatch')
    source_checks = {p: sha(ROOT / p) == h for p, h in identity['source_sha256'].items()}
    source_checks['harness'] = sha(HERE / 'section10.py') == identity['harness_sha256']
    require(all(source_checks.values()), 'retained runner source drift')
    pairs = [(f, load(f)) for f in sorted(source.glob('*/*/REPORT.json.gz'))]
    require(len(pairs) == 16, 'need 16 retained seed pairs')
    floor = pairs[0][1]['intact']['competence']
    require(all(x['intact']['competence'] == floor for _, x in pairs), 'intact scores differ')
    summary = dict(label='read-only descriptive recheck; no verdict recalculation or episodes',
                   tolerance=TOL, stored_default_scores=floor,
                   stored_default_mean=statistics.mean(floor.values()),
                   calibration=calibration['calibration'],
                   abstention_rate='NOT_IDENTIFIABLE: aggregate scores and copy identities are not action traces',
                   verified_nonledger_artifacts=verified, source_checks=source_checks,
                   recorded_readouts={a: r['readouts'] for a, r in results['arms'].items()},
                   policies=[], seeds=[], replays=[])
    snapshots_out, pooled = [], {t: [] for t in TASKS}
    timings, exposures = collections.Counter(), collections.Counter()
    original_receipts = {}
    for path, pair in pairs:
        arm, seed = path.parent.parent.name, int(path.parent.name)
        unit = next(u for u in results['arms'][arm]['seed_units'] if u['seed'] == seed)
        require(load(path.parent / 'UNIT.json') == unit, 'unit/results mismatch')
        for policy, report in pair.items():
            require(report['complete'] and report['invalid'] is None and not report['pending_qualification'],
                    'incomplete policy')
            require(report['seed'] == seed and report['arm'] == arm, 'policy identity')
            require(report['exposure']['training_steps'] == 320000 and len(report['episodes']) == 2000,
                    'horizon mismatch')
            require([e['episode'] for e in report['episodes']] == list(range(2000)), 'episode order')
            require(content_hash(report['final_template']) == report['final_type_id'], 'final template hash')
            require(len(report['copy_instances']) == report['exposure']['evaluator_episodes'], 'copy count')
            require(len(report['copy_instances']) == (41 if policy == 'intact' else 1) * 512,
                    'evaluator exposure')
            require([c['instance_id'] for c in report['copy_instances']] ==
                    list(range(len(report['copy_instances']))), 'copy order')
            expected_copies = []
            templates = [(s['type_id'], offset) for s in report['snapshots'][:20]
                         for offset in (0., math.pi)] + [(report['final_type_id'], 0.)]
            for digest, offset in templates:
                for task in TASKS:
                    for episode in range(128):
                        expected_copies.append(dict(instance_id=len(expected_copies), type_id=digest,
                            task=task, episode_seed=episode, carrier_offset=offset))
            require(report['copy_instances'] == expected_copies, 'copy template/task/episode/offset identity')
            for task in TASKS:
                for offset in (0., math.pi):
                    copies = [c for c in report['copy_instances']
                              if c['task'] == task and c['carrier_offset'] == offset]
                    expected_count = 21 if offset == 0. and policy == 'intact' else (
                        20 if offset == math.pi and policy == 'intact' else (1 if offset == 0. else 0))
                    require(len(copies) == expected_count * 128, 'task/offset copy exposure')
            metric = geometry(report['final_template']['members'])
            mean = statistics.mean(report['competence'].values())
            require(abs(mean - unit['competence' if policy == 'intact' else 'control_competence']) < TOL,
                    'whole competence aggregation')
            late_counts = [n for ep, n in report['growth_counts'] if ep >= 1600]
            summary['policies'].append(dict(arm=arm, seed=seed, policy=policy, geometry=metric,
                competence=report['competence'], equals_default=report['competence'] == floor,
                late_N_range=[min(late_counts), max(late_counts)], slope=report['slope'],
                coverage=report['coverage'], control_queue=report['control_queue'],
                final_type_id=report['final_type_id']))
            timings.update(report['timing'])
            exposures.update(report['exposure'])
            for key in ('events', 'drive_schedule'):
                receipt = report[key]
                rel = str(Path(receipt['path']).relative_to(HERE)) + '.gz'
                original_receipts[rel] = receipt
        intact = pair['intact']
        require(intact['evaluations'] == unit['G1c'], 'G1c/results mismatch')
        evaluated = {e['type_id']: e for e in intact['evaluations']}
        require(len(evaluated) == 20, 'evaluation type count')
        require([s['type_id'] for s in intact['snapshots'][:20]] == list(evaluated), 'first-20 order')
        scores = {t: [e['per_task'][t] for e in intact['evaluations']] for t in TASKS}
        for t in TASKS:
            pooled[t].extend(scores[t])
        summary['seeds'].append(dict(arm=arm, seed=seed, admitted=len(intact['snapshots']),
            evaluated=20, additions_ratio=unit['control_additions'] / unit['intact_additions'],
            task_scores={t: score_summary(scores[t], floor[t]) for t in TASKS},
            evaluated_type_ids=list(evaluated)))
        for index, snapshot in enumerate(intact['snapshots']):
            require(content_hash(snapshot['template']) == snapshot['type_id'], 'snapshot hash')
            require(snapshot['admission_time'] >= snapshot['check_time'] + 60 - TOL, 'admission time')
            g = geometry(snapshot['template']['members'])
            evaluation = evaluated.get(snapshot['type_id'])
            snapshots_out.append(dict(arm=arm, seed=seed, index=index, type_id=snapshot['type_id'],
                check_time=snapshot['check_time'], admission_time=snapshot['admission_time'],
                evaluated=evaluation is not None, **g,
                **{t: evaluation['per_task'][t] if evaluation else '' for t in TASKS}))
    cost_report = load(source / 'COST_RUN.json.gz')
    for key in ('events', 'drive_schedule'):
        receipt = cost_report[key]
        original_receipts[str(Path(receipt['path']).relative_to(HERE)) + '.gz'] = receipt
    require(set(original_receipts) == ledger_paths, 'ledger inventory mismatch')
    for row in transport['ledgers']:
        receipt = original_receipts[row['retained_path']]
        require((receipt['sha256'], receipt['bytes'], receipt['records']) ==
                (row['decoded_sha256'], row['decoded_bytes'], row['records']), 'ledger receipt mapping')
        a = artifacts[row['retained_path']]
        require((a['sha256'], a['bytes']) == (row['archive_sha256'], row['archive_bytes']), 'archive mapping')
    summary['accounting'] = dict(awake_monotonic_seconds=results['wall_seconds'],
        completion_UTC=results['time'], stage_worker_awake_seconds=dict(timings), exposure=dict(exposures),
        calibrated_cost_awake_seconds=load(source / 'COST.json')['wall_seconds'])
    require(all(abs(timings[k] - v) < 1e-7 for k, v in load(source / 'STAGE_TOTALS.json').items()),
            'stage total mismatch')
    summary['evaluated_G1c'] = {t: score_summary(pooled[t], floor[t]) for t in TASKS}
    summary['snapshot_geometry'] = dict(total=len(snapshots_out),
        evaluated=sum(s['evaluated'] for s in snapshots_out),
        copy_time_readout_nonempty=sum(s['readout_members'] > 0 for s in snapshots_out),
        evaluated_copy_time_readout_nonempty=sum(s['evaluated'] and s['readout_members'] > 0 for s in snapshots_out),
        no_potential_drive=sum(s['potential_driven_members'] == 0 for s in snapshots_out),
        max_radius=max(s['max_radius'] for s in snapshots_out))
    for path in sorted(source.glob('REPLAY_*.json.gz')):
        replay = load(path)
        metrics = [geometry([[*e[1:5], e[5]] for e in f['elements']]) for f in replay['frames']]
        summary['replays'].append(dict(path=path.name, task=replay['task'], type_id=replay['type_id'],
            diagnostic_only=True, frames=len(metrics), abstaining_frames=sum(g['copy_time_abstain'] for g in metrics),
            coherence_range=[min(g['copy_time_coherence'] for g in metrics), max(g['copy_time_coherence'] for g in metrics)]))
    ledger_output = []
    if ledgers:
        for index, row in enumerate(transport['ledgers'], 1):
            ledger_output.append(audit_ledger(HERE / row['retained_path'], row))
            print(f"verified ledger {index}/66: {row['retained_path']}", flush=True)
    summary['ledger_verification'] = 'decoded hashes/bytes/records verified' if ledgers else 'inventory/size/receipt mapping only'
    # Create output only after the audit passes; no historical file is rewritten.
    output.mkdir(parents=True)
    with (output / 'SNAPSHOTS.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(snapshots_out[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(snapshots_out)
    (output / 'ANALYSIS.json').write_text(json.dumps(summary, indent=2, allow_nan=False) + '\n')
    (output / 'LEDGER_CHECKS.json').write_text(json.dumps(ledger_output, indent=2, allow_nan=False) + '\n')
    print(json.dumps({k: summary[k] for k in ('snapshot_geometry', 'evaluated_G1c', 'ledger_verification')}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--ledgers', action='store_true', help='verify all 66 compressed and decoded ledgers; minutes of disk work')
    args = parser.parse_args()
    audit(HERE / 'development_20261006', args.output, args.ledgers)


if __name__ == '__main__':
    main()
