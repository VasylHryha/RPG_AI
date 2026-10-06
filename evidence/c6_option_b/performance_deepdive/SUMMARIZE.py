"""Summarize the measurement batch into MEASUREMENTS.json (no new computation)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = {}
for costs in sorted(HERE.glob('*/COSTS.json')):
    d = json.loads(costs.read_text()); label = costs.parent.name
    exact = HERE / (label + '_EXACT.json')
    e = json.loads(exact.read_text()) if exact.exists() else None
    cache = d.get('native_cache') or {}
    rows[label] = {
        'world_seconds': d['world_seconds'], 'compute_cpu_seconds': d['compute_cpu_seconds'],
        'cpu_per_wall': d['compute_cpu_seconds'] / d['world_seconds'],
        'serialization_write_seconds': d['serialization_write_seconds'],
        'post_serialization_peak_rss_bytes': d['post_serialization_peak_rss_bytes'],
        'start_load': d['start_machine']['load_average'], 'end_load': d['end_machine']['load_average'],
        'rule_value_seconds': d['world_seconds'] * 40 / 2 * 1.5,
        'option_b_source_hashes': d['option_b_build']['source_hashes'],
        'option_b_binary_sha256': d['option_b_build']['binary_sha256'],
        'audit': d.get('audit'), 'chain_complete': d.get('chain_complete'), 'invalid': d.get('invalid'),
        'task_batches': cache.get('concurrent_task_batches'),
        'native_cache': cache.get('native_cache_process_totals') or cache.get('native_cache_worker_totals'),
        'exact_comparison': None if e is None else {k: e[k] for k in (
            'passed', 'absolute_tolerance', 'maximum_error', 'numeric_values_compared',
            'decision_values_compared', 'digest_values_changed', 'reference')}}
pairs = {}
for pair in (1, 2):
    old, new = rows.get(f'ab{pair}_old_smoke_0'), rows.get(f'ab{pair}_new_smoke_0')
    if old and new:
        pairs[pair] = {'wall_ratio_new_over_old': new['world_seconds'] / old['world_seconds'],
                       'cpu_ratio_new_over_old': new['compute_cpu_seconds'] / old['compute_cpu_seconds']}
(HERE / 'MEASUREMENTS.json').write_text(json.dumps({'worlds': rows, 'ab_pairs': pairs}, indent=2) + '\n')
print(json.dumps(pairs, indent=1))
for k, v in rows.items():
    print(f"{k:24s} wall {v['world_seconds']:7.1f} cpu {v['compute_cpu_seconds']:7.1f} cpu/wall {v['cpu_per_wall']:.2f} "
          f"rss {v['post_serialization_peak_rss_bytes']/2**20:7.0f} MiB exact {None if v['exact_comparison'] is None else v['exact_comparison']['passed']} "
          f"load {[round(x,1) for x in v['start_load']]}->{[round(x,1) for x in v['end_load']]}")
