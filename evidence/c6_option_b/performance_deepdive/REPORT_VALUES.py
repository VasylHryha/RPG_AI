"""Every timing and rule value shown in PERFORMANCE_DEEPDIVE_REPORT.md, derived
from the raw receipts (COSTS.json). Writes REPORT_VALUES.json; no computation
other than arithmetic on stored values. Display rounding: seconds to 0.1 s,
rule values to 0.1 s, ratios to 3 decimals; unrounded values are kept too.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rule(seconds):
    return seconds * 40 / 2 * 1.5


def load(path):
    d = json.loads(path.read_text())
    cache = d.get('native_cache') or {}
    batches = cache.get('concurrent_task_batches')
    return {'world_seconds': d['world_seconds'], 'compute_cpu_seconds': d['compute_cpu_seconds'],
            'cpu_per_wall': d['compute_cpu_seconds'] / d['world_seconds'],
            'rule_value_seconds': rule(d['world_seconds']),
            'peak_rss_bytes': d['post_serialization_peak_rss_bytes'],
            'start_load_1min': d['start_machine']['load_average'][0],
            'end_load_1min': d['end_machine']['load_average'][0],
            'stage_batches': [(b['tasks'], b['wall_seconds']) for b in batches] if batches else None}


runs = {}
for costs in sorted(HERE.glob('*/COSTS.json')):
    runs[costs.parent.name] = load(costs)
for costs in sorted((HERE / 'fixes').glob('*/COSTS.json')):
    runs['fixes/' + costs.parent.name] = load(costs)

pairs = {}
for name, old, new in (('pair1', 'ab1_old_smoke_0', 'ab1_new_smoke_0'), ('pair2', 'ab2_old_smoke_0', 'ab2_new_smoke_0'),
                       ('fix_pair', 'fixes/old_smoke_0', 'fixes/fixed_smoke_0')):
    if old in runs and new in runs:
        pairs[name] = {'wall_ratio': runs[new]['world_seconds'] / runs[old]['world_seconds'],
                       'cpu_ratio': runs[new]['compute_cpu_seconds'] / runs[old]['compute_cpu_seconds']}

new_labels = [k for k in runs if 'old' not in k]
stage2 = [w for k in new_labels for t, w in (runs[k]['stage_batches'] or []) if t == 23]
stage1 = [w for k in new_labels for t, w in (runs[k]['stage_batches'] or []) if t == 3]
unaudited = [k for k in new_labels if 'audit' not in k]
summary = {
    'runs': runs, 'pairs': pairs,
    'stage1_wall_range_all_new_runs': [min(stage1), max(stage1)] if stage1 else None,
    'stage2_wall_range_all_new_runs': [min(stage2), max(stage2)] if stage2 else None,
    'slowest_new_unaudited': max(unaudited, key=lambda k: runs[k]['world_seconds']),
}
(HERE / 'REPORT_VALUES.json').write_text(json.dumps(summary, indent=2) + '\n')
for k, v in runs.items():
    print(f"{k:28s} wall {v['world_seconds']:.6f} cpu {v['compute_cpu_seconds']:.6f} rule {v['rule_value_seconds']:.6f} "
          f"cpu/wall {v['cpu_per_wall']:.3f} rss {v['peak_rss_bytes']} load {v['start_load_1min']:.2f}->{v['end_load_1min']:.2f}")
print(json.dumps({k: summary[k] for k in summary if k != 'runs'}, indent=1))
