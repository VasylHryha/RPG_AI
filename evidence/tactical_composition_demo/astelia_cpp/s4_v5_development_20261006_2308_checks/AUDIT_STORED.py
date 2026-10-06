"""Read stored development records only; no native execution or cache writes."""
import collections
import gzip
import hashlib
import json
import math
import pathlib
import statistics
import sys
import time

BASE = pathlib.Path(__file__).resolve().parents[1]
OUT = BASE / 's4_v5_development_20261006_2308'
HERE = pathlib.Path(__file__).resolve().parent


def load(path):
    return json.loads(path.read_text())


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def stats(values):
    mean = statistics.mean(values)
    sd = statistics.stdev(values)
    se = sd / math.sqrt(len(values))
    return dict(n=len(values), mean=mean, sd=sd, se=se,
                descriptive_normal_95=[mean - 1.96 * se, mean + 1.96 * se])


def close(actual, expected):
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys(), (actual.keys(), expected.keys())
        for key in expected:
            close(actual[key], expected[key])
    elif isinstance(expected, (list, tuple)):
        assert len(actual) == len(expected)
        for a, b in zip(actual, expected):
            close(a, b)
    elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
        assert math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12), (actual, expected)
    else:
        assert actual == expected, (actual, expected)


def selection(stage, scores):
    novice = statistics.mean(v for k, v in scores.items() if json.loads(k)[0] == 'novice')
    if stage == 'A':
        return dict(novice_mean=novice, regular_mean=None, eligible=None,
                    rank=[novice], objective=-novice)
    regular = statistics.mean(v for k, v in scores.items() if json.loads(k)[0] == 'regular')
    eligible = novice >= 0
    return dict(novice_mean=novice, regular_mean=regular, eligible=eligible,
                rank=[int(eligible), regular], objective=-regular + (0 if eligible else 101))


def main():
    started = time.monotonic()
    identity = load(OUT / 'run_identity.json')
    assert all(sha(BASE / name) == digest for name, digest in identity['code_hashes'].items())
    declaration = load(BASE / 'S4_V5_SEEDS.json')
    assert sha(BASE / 'S4_V5_SEEDS.json') == identity['seed_declaration_sha256']
    assert declaration['judging_root'] is None and declaration['status'] == 'FRESH_DEVELOPMENT_ONLY'
    used = set()
    for stage in ('A', 'B'):
        for split in ('tuning', 'validation'):
            seeds = {row[1] for row in declaration['panels'][stage][split]}
            assert not seeds & used and not seeds & set(declaration['prior_seed_inventory'])
            used |= seeds
    claim = load(BASE/'s4_v5_part1_checks/LEDGER_USED.json')
    assert pathlib.Path(claim['output']).resolve() == OUT.resolve()
    assert claim['declaration_sha256'] == identity['seed_declaration_sha256']
    assert claim['implementation_commit'] == identity['implementation_commit']
    ledger = load(OUT / 's4_seeds.json')
    assert ledger['judging_seeds'] is None and ledger['declaration_sha256'] == identity['seed_declaration_sha256']
    receipt = load(OUT / ('summary.json' if (OUT / 'summary.json').exists() else 'failure.json'))
    grouped = collections.defaultdict(dict)
    group_cache = collections.defaultdict(collections.Counter)
    group_params = {}
    validation_rows = collections.defaultdict(list)
    counts = collections.Counter()
    budgets = collections.Counter({a: 0 for a in ('resonator', 'morale', 'pushpull')})
    seen = set()
    rows_n = hits = failed_rows = 0
    sys.path.insert(0, str(BASE))
    from s3_runner import request
    from result_cache import digest
    with gzip.open(OUT / 'fights.jsonl.gz', 'rt') as raw:
        for i, line in enumerate(raw):
            row = json.loads(line)
            spec = row['spec']
            use = dict(stage=row['stage'], split=row['split'], candidate=row['candidate'],
                       **spec, cache_hit=row['cache_hit'], cache_key=row['cache_key'])
            assert use == ledger['uses'][i], 'raw/ledger divergence'
            assert row['stage'] in ('A', 'B') and spec['skeleton'] == 'v5'
            assert [spec['opponent'], spec['seed'], spec['setting']] in declaration['panels'][row['stage']][row['split']]
            assert spec['endCounts'] is True and type(spec['swapSides']) is bool
            assert row['request'] == request(spec)
            assert row['cache_key'] == digest(row['request'])
            result = row['summary']
            assert not any(row['metrics'].get(k, 0) for k in ('forks', 'search_calls', 'artillery_rollouts'))
            failed = result.get('controllerStatus') != 'completed' or any(result.get('controllerFailures', [1]))
            assert bool(row.get('failure')) == bool(failed)
            failed_rows += int(failed)
            if not failed:
                assert row['S'] == result['survivors'] - result['enemySurvivors']
                assert row['D'] == result['crossTeamDealt'][0] - result['crossTeamTaken'][0]
            group = (row['stage'], spec['arm'], row['split'], row['candidate'])
            cluster = json.dumps([spec['opponent'], spec['seed'], spec['setting']])
            unique = (group, cluster, spec['swapSides'])
            assert unique not in seen
            seen.add(unique)
            if not failed:
                grouped[group].setdefault(cluster, {})[spec['swapSides']] = row['S']
            group_cache[group]['cache_hits' if row['cache_hit'] else 'fresh_fights'] += 1
            params = fingerprint(spec['params'])
            assert group_params.setdefault(group, params) == params
            rows_n += 1
            hits += int(row['cache_hit'])
            counts[(row['stage'], spec['arm'], row['split'])] += 1
            if row['split'] == 'tuning':
                budgets[spec['arm']] += 1
            elif not failed:
                validation_rows[(row['stage'], spec['arm'], spec['setting'] + '|' + spec['opponent'])].append(result)
    assert rows_n == len(ledger['uses']) == receipt['executed_fights'] + receipt['cache_hits']
    assert hits == receipt['cache_hits']
    close(dict(budgets), receipt['budgets'])
    coverage = []
    validations = {}
    tuning = []
    previous = {}
    candidate_count = 0
    partial_candidate_count = 0
    cma_generations = 0
    # Reproduce optimizer proposals and feedback without running any fight.
    sys.path.insert(0, str(BASE / 'build/s4_cma_vendor'))
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        import cma
    assert cma.__version__ == '4.5.0'
    sys.path.insert(0, str(BASE))
    from s4_v4 import BOUNDS
    verified_best = {a: {k: (lo + hi) / 2 for k, (lo, hi) in bounds.items()} for a, bounds in BOUNDS.items()}
    completed_stages = []
    for stage in ('A', 'B'):
        for arm in ('resonator', 'morale', 'pushpull'):
            path = OUT / f'{stage}_{arm}_tuning.json'
            if not path.exists():
                continue
            data = load(path)
            if stage == 'A':
                close(data['initial_knobs'], {k: (lo + hi) / 2 for k, (lo, hi) in BOUNDS[arm].items()})
            else:
                close(data['initial_knobs'], previous[arm])
            def check_candidate(tag, knobs, scores):
                group = (stage, arm, 'tuning', tag)
                assert group_params[group] == fingerprint(knobs)
                actual = grouped[group]
                assert len(actual) == 19 and all(set(pair) == {False, True} for pair in actual.values())
                close({key: sum(pair.values()) / 2 for key, pair in actual.items()}, scores)
            check_candidate('initial', data['initial_knobs'], data['initial_scores'])
            best = data['initial_knobs']
            picked = selection(stage, data['initial_scores'])
            x0 = [(best[k] - lo) / (hi - lo) for k, (lo, hi) in BOUNDS[arm].items()]
            es = cma.CMAEvolutionStrategy(x0, .25, dict(bounds=[0, 1], popsize=16,
                 seed=420060 + ('A', 'B').index(stage) * 100 + ('resonator', 'morale', 'pushpull').index(arm),
                 verbose=-9, verb_log=0))
            for expected_generation, generation in enumerate(data['generations']):
                g = generation['generation']
                assert g == expected_generation
                solutions = es.ask()
                assert len(generation['candidates']) == 16
                losses = []
                for j, candidate in enumerate(generation['candidates']):
                    assert candidate['index'] == j
                    close([float(x) for x in solutions[j]], candidate['normalized'])
                    mapped = {k: float(lo + x * (hi - lo)) for x, (k, (lo, hi)) in zip(candidate['normalized'], BOUNDS[arm].items())}
                    close(mapped, candidate['knobs'])
                    check_candidate(f'{g}:{j}', candidate['knobs'], candidate['scores'])
                    actual_cache = group_cache[(stage, arm, 'tuning', f'{g}:{j}')]
                    assert actual_cache['fresh_fights'] == candidate['fresh_fights']
                    assert actual_cache['cache_hits'] == candidate['cache_hits']
                    current = selection(stage, candidate['scores'])
                    close(current, candidate['selection'])
                    accepted = current['rank'] > picked['rank']
                    assert accepted == candidate['accepted_as_best']
                    if accepted:
                        best, picked = candidate['knobs'], current
                    losses.append(current['objective'])
                    candidate_count += 1
                es.tell(solutions, losses)
                close(best, generation['best'])
                close(picked, generation['best_selection'])
                close(float(es.sigma), generation['sigma'])
                close({k: str(v) for k, v in es.stop().items()}, generation['optimizer_stop'])
                cma_generations += 1
            close(best, data['best'])
            close(picked, data['best_selection'])
            partial_path = OUT / f'{stage}_{arm}_partial.json'
            if partial_path.exists():
                partial = load(partial_path)
                if partial['generation'] == len(data['generations']):
                    solutions = es.ask()
                    for j, candidate in enumerate(partial['candidates']):
                        assert candidate['index'] == j
                        close([float(x) for x in solutions[j]], candidate['normalized'])
                        mapped = {k: float(lo + x * (hi - lo)) for x, (k, (lo, hi)) in zip(candidate['normalized'], BOUNDS[arm].items())}
                        close(mapped, candidate['knobs'])
                        check_candidate(f"{partial['generation']}:{j}", candidate['knobs'], candidate['scores'])
                        actual_cache = group_cache[(stage, arm, 'tuning', f"{partial['generation']}:{j}")]
                        assert actual_cache['fresh_fights'] == candidate['fresh_fights']
                        assert actual_cache['cache_hits'] == candidate['cache_hits']
                        current = selection(stage, candidate['scores'])
                        close(current, candidate['selection'])
                        accepted = current['rank'] > picked['rank']
                        assert accepted == candidate['accepted_as_best']
                        if accepted:
                            best, picked = candidate['knobs'], current
                        partial_candidate_count += 1
                else:
                    assert partial['generation'] == len(data['generations']) - 1
                close(best, partial['best'])
                close(picked, partial['best_selection'])
            previous[arm] = best
            verified_best[arm] = best
            all_generations_saved = len(data['generations']) == 16
            runner_complete = all_generations_saved
            if not (OUT/'summary.json').exists():
                marker = receipt['selections'].get(arm)
                if marker is not None and marker['stage'] == stage:
                    runner_complete = marker['complete']
                    assert type(runner_complete) is bool
                    if runner_complete:
                        assert all_generations_saved
                    elif all_generations_saved:
                        assert receipt['stage'] == stage and stage not in receipt['stages_completed']
            tuning.append(dict(stage=stage, arm=arm, completed_generations=len(data['generations']),
                               selection=picked, knobs=best,
                               accounted_rows=counts[(stage, arm, 'tuning')],
                               all_generations_saved=all_generations_saved,
                               completed=runner_complete))
        validation_path = OUT / f'{stage}_validation.json'
        validation = load(validation_path) if validation_path.exists() else None
        if validation is not None:
            completed_stages.append(stage)
            stage_best = load(OUT / f'{stage}_best.json')
            close(stage_best, previous)
            close(validation['knobs'], stage_best)
            for arm in BOUNDS:
                assert counts[(stage, arm, 'tuning')] == 9766
                assert len(load(OUT / f'{stage}_{arm}_tuning.json')['generations']) == 16
        for arm in ('resonator', 'morale', 'pushpull', 'nearest'):
            for head in (('novice',) if stage == 'A' else ('novice', 'regular')):
                endpoint = ('s4_melee10' if stage == 'A' else 's4_full_head') + '|' + head
                key = (stage, arm, endpoint)
                if validation is None:
                    coverage.append(dict(stage=stage, arm=arm, endpoint=endpoint, status='not_run', reason='validation stage did not complete'))
                    continue
                expected = validation['results'][arm][endpoint]
                assert group_params[(stage, arm, 'validation', 'best')] == fingerprint(validation['knobs'].get(arm, {}))
                group = grouped[(stage, arm, 'validation', 'best')]
                scores = {k: sum(v.values()) / 2 for k, v in group.items() if json.loads(k)[0] == head}
                assert len(scores) == 100 and all(len(v) == 2 for k, v in group.items() if json.loads(k)[0] == head)
                close(scores, expected['scores'])
                calculated = stats(list(scores.values()))
                close(calculated, expected['stats'])
                results = validation_rows[key]
                assert len(results) == 200
                own = [r['t'] for r in results if r['survivors'] == 0]
                enemy = [r['t'] for r in results if r['enemySurvivors'] == 0]
                mean = lambda fn: sum(fn(r) for r in results) / len(results)
                descriptive = dict(fights=len(results), own_guns_alive_mean=mean(lambda r:r['artilleryAlive'][0]),
                    enemy_guns_alive_mean=mean(lambda r:r['artilleryAlive'][1]),
                    timeouts=sum(r['survivors'] > 0 and r['enemySurvivors'] > 0 for r in results),
                    damage_dealt_mean=mean(lambda r:r['crossTeamDealt'][0]), damage_taken_mean=mean(lambda r:r['crossTeamTaken'][0]),
                    own_eliminations=len(own), own_elimination_time_mean=statistics.mean(own) if own else None,
                    enemy_eliminations=len(enemy), enemy_elimination_time_mean=statistics.mean(enemy) if enemy else None,
                    mean_termination_time=mean(lambda r:r['t']),
                    elimination_time_policy='conditional on elimination; timeouts censored, no imputation')
                close(descriptive, expected['descriptive'])
                validations['|'.join(key)] = dict(stats=calculated, descriptive=descriptive)
                coverage.append(dict(stage=stage, arm=arm, endpoint=endpoint, status='evaluated', value=calculated['mean'], verdict='descriptive'))
        if validation is not None:
            novice = validation['results']['resonator'][('s4_melee10' if stage == 'A' else 's4_full_head')+'|novice']['stats']['mean']
            regular = validation['results']['resonator']['s4_full_head|regular']['stats']['mean'] if stage == 'B' else None
            gate = receipt['gates'][stage]
            close(gate['novice_mean'], novice)
            close(gate['regular_mean'], regular)
            assert gate['regular_threshold'] == -7.62 and gate['C_authorized'] is False
            assert gate['novice_validation_pass'] == (novice > 0)
            assert gate['regular_progress_pass'] == (None if stage == 'A' else regular > -7.62)
            assert gate['status'] == ('STOP' if novice <= 0 or (regular is not None and regular <= -7.62) else 'PROGRESS' if stage == 'B' else 'CONTINUE')
    close(receipt['best'], verified_best)
    close(receipt['selected_omega'], {role: verified_best['resonator']['omega_'+role] for role in ('melee', 'ranged')})
    close(receipt['stages_completed'], completed_stages)
    if (OUT / 'summary.json').exists():
        assert receipt['status'] == receipt['gates'][completed_stages[-1]]['status']
        assert receipt['C']['status'] == 'not_run' and receipt['development_only'] is True
        for arm in BOUNDS:
            final_tuning = next(t for t in reversed(tuning) if t['arm'] == arm)
            close(receipt['selections'][arm], final_tuning['selection'])
    else:
        assert receipt['status'] == 'NOT_READY'
        for arm, selected in receipt['selections'].items():
            final_tuning = next(t for t in reversed(tuning) if t['arm'] == arm)
            close(selected, dict(final_tuning['selection'], stage=final_tuning['stage'], complete=final_tuning['completed']))
    coverage.append(dict(stage='C', status='not_run', reason='outside v5 amended A/B scope'))
    result = dict(status='PASS', combat_executions=0, raw_rows=rows_n, fresh_rows=rows_n-hits, cache_hits=hits,
                  budgets=dict(budgets), completed_candidates=candidate_count, cma_generations_reconstructed=cma_generations,
                  partial_generation_candidates=partial_candidate_count,
                  accounting_by_stage_arm_split=[dict(stage=s, arm=a, split=p, recorded_rows=n)
                      for (s, a, p), n in sorted(counts.items())],
                  all_raw_rows_and_ledger_matched=True, zero_controller_failures=failed_rows == 0,
                  recorded_controller_failure_rows=failed_rows, zero_planner_work=True,
                  runtime_hashes_verified=len(identity['code_hashes']), validation=validations, tuning=tuning,
                  endpoint_coverage=coverage, elapsed_seconds=time.monotonic()-started,
                  partial_candidate_limit='Completed candidates in partial generation reconstructed; rows of an unfinished candidate checked against ledger/identity/allocation only.')
    (HERE/'AUDIT.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    (HERE/'AUDIT_NOT_COMPLETED.json').unlink(missing_ok=True)
    print(json.dumps({k: v for k, v in result.items() if k not in ('validation', 'tuning', 'endpoint_coverage')}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        (HERE/'AUDIT_NOT_COMPLETED.json').write_text(json.dumps(dict(
            status='NOT_COMPLETED', error_class=type(error).__name__,
            combat_executions=0, raw_evidence_preserved=True,
            detail_location='local AUDIT.stderr.log; no raw error copied into delivery'), indent=2)+'\n')
        raise
