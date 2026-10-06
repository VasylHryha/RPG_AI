"""Compare existing G1c scores to existing same-panel random calibration rows.

No policies or episodes are executed. The 0h normalization still uses all 256
calibration episodes; the additional comparator uses their stored first 128.
"""
import argparse
import csv
import json
from pathlib import Path
import statistics

from evidence.tactical_composition_demo.growing_shapes.runner.recheck_development import (
    HERE, TASKS, TOL, load, require, sha,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analysis-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.analysis_dir = args.analysis_dir.resolve()
    source = HERE / 'development_20261006/CALIBRATION.json'
    frozen = load(source)
    analysis = load(args.analysis_dir / 'ANALYSIS.json')
    with (args.analysis_dir / 'SNAPSHOTS.csv').open(newline='') as stream:
        scored = [r for r in csv.DictReader(stream) if r['evaluated'] == 'True']
    require(len(scored) == 320, 'expected the 320 already evaluated snapshots')
    out = dict(label='descriptive comparison of stored scores only; no new episodes',
               inputs={str(p.relative_to(HERE)): sha(p) for p in
                       (source, args.analysis_dir / 'ANALYSIS.json', args.analysis_dir / 'SNAPSHOTS.csv')},
               normalization='unchanged 256-episode calibration', tasks={})
    for task in TASKS:
        c = frozen['calibration'][task]
        raw = frozen['raw'][task]['random']
        require(len(raw) == 256, 'calibration row count')
        panel_random = statistics.mean(raw[:128])
        n = (panel_random - c['random']) / (c['reference'] - c['random'])
        floor = analysis['stored_default_scores'][task]
        values = [float(r[task]) for r in scored]
        out['tasks'][task] = dict(random_first_128_oriented_mean=panel_random,
            random_first_128_normalized_mean=n,
            stored_default_oriented_mean=c['random'] + floor * (c['reference'] - c['random']),
            above_same_panel_random=sum(v > n + TOL for v in values),
            above_floor_and_same_panel_random=sum(v > max(n, floor) + TOL for v in values))
    require(not args.output.exists(), 'output already exists')
    require(not args.output.resolve().is_relative_to((HERE / 'development_20261006').resolve()),
            'immutable receipt tree')
    with args.output.open('x') as stream:
        stream.write(json.dumps(out, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
