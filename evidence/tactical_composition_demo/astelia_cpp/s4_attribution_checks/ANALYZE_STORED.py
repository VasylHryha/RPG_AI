"""Verify and describe the one completed attribution set; never execute combat."""
import collections
import gzip
import hashlib
import itertools
import json
import math
import pathlib
import statistics

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHECKS = pathlib.Path(__file__).resolve().parent
OUT = ROOT / 's4_attribution_development'
CELLS = ('v3', 'H', 'F', 'HF')
ARMS = ('resonator', 'morale')
HEADS = ('novice', 'regular')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(name, value):
    (CHECKS / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def stats(values):
    values = list(values)
    assert len(values) == 100 and all(math.isfinite(x) for x in values)
    m = sum(values) / len(values)
    sd = math.sqrt(sum((x - m) ** 2 for x in values) / (len(values) - 1))
    se = sd / math.sqrt(len(values))
    return dict(n=len(values), mean=m, sd=sd, se=se,
                descriptive_normal_95=[m - 1.96 * se, m + 1.96 * se])


def close(a, b):
    if isinstance(a, dict):
        assert set(a) == set(b)
        for k in a:
            close(a[k], b[k])
    elif isinstance(a, list):
        assert len(a) == len(b)
        for x, y in zip(a, b):
            close(x, y)
    else:
        assert math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12), (a, b)


def main():
    ledger = json.loads((ROOT / 'S4_ATTRIBUTION_SEEDS.json').read_text())
    summary = json.loads((OUT / 'SUMMARY.json').read_text())
    identity = json.loads((OUT / 'run_identity.json').read_text())
    run = json.loads((CHECKS / 'RUN_RESULT.json').read_text())
    assert run['returncode'] == 0 and run['elapsed_seconds'] < 3600
    assert not (OUT / 'FAILURE.json').exists()
    assert identity['ledger'] == ledger
    for name, expected in identity['inputs'].items():
        assert digest(ROOT / name) == expected, name
    assert digest(OUT / 'fights.jsonl.gz') == summary['raw_fights_sha256']
    knobs = json.loads((ROOT / 's4_v3_development/B_best.json').read_text())
    with gzip.open(OUT / 'fights.jsonl.gz', 'rt') as stream:
        rows = [json.loads(line) for line in stream]
    expected = set(itertools.product(CELLS, ARMS, HEADS, ledger['seeds'], (False, True)))
    found = set()
    groups = collections.defaultdict(dict)
    metrics = {}
    trace_rows = []
    for row in rows:
        p, s = row['spec'], row['summary']
        ident = (p['skeleton'], p['arm'], p['opponent'], p['seed'], p['swapSides'])
        assert ident not in found
        found.add(ident)
        assert p['params'] == knobs[p['arm']] and p['setting'] == 's4_full_head'
        assert s['controllerStatus'] == 'completed' and s['controllerFailures'] == [0, 0]
        assert p['trace'] == (p['opponent'] == 'regular' and p['seed'] in ledger['trace_seeds'])
        assert ('trace' in row) == p['trace']
        groups[(p['arm'], p['opponent'], p['skeleton'])][(p['seed'], p['swapSides'])] = s
        key = ident if p['trace'] else ident[:-1]
        if key in metrics:
            assert metrics[key] == row['metrics']
        metrics[key] = row['metrics']
        if p['trace']:
            trace_rows.append(row)
    assert found == expected and len(rows) == 3200 and len(trace_rows) == 80
    assert len(metrics) == 1640 and sum(m['executed_fights'] for m in metrics.values()) == 3200
    for m in metrics.values():
        for k in ('forks', 'branch_steps', 'search_calls', 'inference_calls',
                  'candidate_models', 'artillery_rollouts', 'artillery_predictions',
                  'artillery_candidates', 'prediction_steps', 'prediction_unit_steps',
                  'branch_unit_actions', 'branch_projectile_steps', 'cache_hits'):
            assert m[k] == 0, k
    assert {x['trace']['file'] for x in trace_rows} == {x['file'] for x in summary['traces']}
    assert {x['trace']['file'] for x in trace_rows} == {
        str(p.relative_to(OUT)) for p in (OUT / 'traces').glob('*.jsonl.gz')}
    assert not list((OUT / 'traces').glob('*.part.jsonl'))
    for row in trace_rows:
        t = row['trace']
        assert digest(OUT / t['file']) == t['sha256']
        c = collections.Counter(t['diagnostics']['counts'])
        releases = sum(c['death_released_holds_' + k] for k in ('own_death', 'enemy_death', 'both_death', 'missing'))
        terminal = sum(c['terminal_released_holds_' + k] for k in ('own_death', 'enemy_death', 'both_death', 'missing'))
        assert releases == c['holds_disappeared']
        assert c['holds_started'] == c['holds_target_band'] + c['holds_expired'] + releases + terminal + c['terminal_censored_living_holds']
        assert c['death_released_holds'] == releases + terminal - c['death_released_holds_missing'] - c['terminal_released_holds_missing']
        assert c['holds_expiring_inside_gun_reach'] <= c['holds_expired']
        assert c['focus_with_c_below_minus_point2_ticks'] <= c['focus_while_escaping_ticks'] <= c['focus_ticks'] <= c['unit_ticks']

    endpoints = {}
    for arm, head in itertools.product(ARMS, HEADS):
        e = dict(cells={}, paired_differences={})
        scores = {}
        for cell in CELLS:
            g = groups[(arm, head, cell)]
            scores[cell] = [(g[(seed, False)]['survivors'] - g[(seed, False)]['enemySurvivors'] +
                             g[(seed, True)]['survivors'] - g[(seed, True)]['enemySurvivors']) / 2
                            for seed in ledger['seeds']]
            v = list(g.values())
            e['cells'][cell] = dict(S=stats(scores[cell]), fights=len(v),
                mean_own_guns_alive=statistics.mean(s['artilleryAlive'][0] for s in v),
                mean_enemy_guns_alive=statistics.mean(s['artilleryAlive'][1] for s in v),
                timeouts=sum(s['t'] >= 150 - 1e-9 for s in v),
                mean_cross_team_damage_dealt=statistics.mean(s['crossTeamDealt'][0] for s in v),
                mean_cross_team_damage_taken=statistics.mean(s['crossTeamTaken'][0] for s in v),
                mean_terminal_time_seconds=statistics.mean(s['t'] for s in v),
                own_eliminated_fights=sum(s['survivors'] == 0 for s in v),
                enemy_eliminated_fights=sum(s['enemySurvivors'] == 0 for s in v),
                mean_time_to_own_elimination_seconds=statistics.mean(s['t'] for s in v if s['survivors'] == 0) if any(s['survivors'] == 0 for s in v) else None,
                mean_time_to_enemy_elimination_seconds=statistics.mean(s['t'] for s in v if s['enemySurvivors'] == 0) if any(s['enemySurvivors'] == 0 for s in v) else None)
            source = summary['endpoints'][arm + '|' + head]['cells'][cell]
            close(e['cells'][cell]['S'], source['S'])
            assert e['cells'][cell]['timeouts'] == source['timeouts']
            assert e['cells'][cell]['mean_enemy_guns_alive'] == source['mean_enemy_guns_alive']
        for a, b in itertools.combinations(CELLS, 2):
            e['paired_differences'][b + '-' + a] = stats(y - x for x, y in zip(scores[a], scores[b]))
        e['interaction_HF-H-F+v3'] = stats(hf - h - f + v3 for v3, h, f, hf in zip(*(scores[c] for c in CELLS)))
        close(e['paired_differences'], summary['endpoints'][arm + '|' + head]['paired_differences'])
        close(e['interaction_HF-H-F+v3'], summary['endpoints'][arm + '|' + head]['interaction_HF-H-F+v3'])
        endpoints[arm + '|' + head] = e

    traces = {}
    for arm, cell in itertools.product(ARMS, CELLS):
        ts = [r['trace']['diagnostics'] for r in trace_rows if (r['spec']['arm'], r['spec']['skeleton']) == (arm, cell)]
        c = collections.Counter()
        undefined = collections.Counter()
        for t in ts:
            c.update(t['counts'])
            undefined.update(t['feasibility_undefined'])
        seconds = sum(t['unit_seconds'] for t in ts)
        assert math.isclose(seconds * 30, c['unit_ticks'], rel_tol=1e-10)
        assert c['defined_feasibility_ticks'] + sum(undefined.values()) == c['unit_ticks']
        traces[arm + '|' + cell] = dict(head='regular', fights=len(ts), seed_clusters=5,
            unit_seconds=seconds, counts=dict(c), feasibility_undefined=dict(undefined),
            feasibility_mean=sum((t['feasibility_mean'] or 0) * t['counts'].get('defined_feasibility_ticks', 0) for t in ts) / c['defined_feasibility_ticks'],
            changes_per_living_unit_minute={k: c[k] * 60 / seconds for k in
                ('unit_intent_proxy_changes', 'pair_mode_changes', 'unit_ticks_with_pair_mode_change')})
    write('ANALYSIS.json', dict(status='DESCRIPTIVE_ONLY_NO_VERDICT', endpoints=endpoints, traces=traces))
    write('VALIDATION.json', dict(status='PASS', fights=3200, native_processes=1640,
        trace_fights=80, seed_clusters_per_endpoint=100, seed_clusters_per_trace_cell=5,
        exact_allocation=True, fixed_v3_knobs=True, all_input_and_native_pins_match=True,
        raw_trace_and_fight_hashes_match=True, independent_score_reconstruction=True,
        all_six_paired_contrasts_and_interactions_match=True, hold_release_conservation=True,
        terminal_deaths_included=True, controller_failures=0, planner_work=0, cache_hits=0,
        inputs_sha256=digest(CHECKS / 'INPUT_PIN.json'), raw_summary_sha256=digest(OUT / 'SUMMARY.json'),
        raw_fights_sha256=digest(OUT / 'fights.jsonl.gz'), analysis_sha256=digest(CHECKS / 'ANALYSIS.json'),
        raw_trace_counter_scope='Counters produced during original fights; checked for allocation and conservation, not all independently recounted from raw ticks. No new fights.'))
    raw_paths = (sorted(p for p in OUT.rglob('*') if p.is_file())
                 + [CHECKS / 'RUN.stdout.log', CHECKS / 'RUN.stderr.log']
                 + sorted(CHECKS.glob('OWNER_RECHECK*.log')))
    inventory = [dict(path=str(p.relative_to(ROOT)), bytes=p.stat().st_size, sha256=digest(p)) for p in raw_paths]
    write('RAW_FILES_OUTSIDE_GIT.json', dict(files=inventory, total_bytes=sum(p['bytes'] for p in inventory),
        policy='Original raw fight rows, traces, seed-bearing identity/summary and stdout/stderr stay local and out of Git. Existing predeclared seed ledger is unchanged.'))
    print(json.dumps(dict(status='PASS', fights=len(rows), traces=len(trace_rows), raw_bytes=sum(p['bytes'] for p in inventory))))


if __name__ == '__main__':
    main()
