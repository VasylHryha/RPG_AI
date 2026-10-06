"""Read-only reconstruction of this revision's pre-generation-14 projection stop.

Original launch/report sources remain unchanged and hash-bound. No fights, seed
allocation, receipt replacement, or reinterpretation of incomplete C validation.
"""
import collections
import gzip
import json
import math
from s4_v4_report import (A, OUT, ROOT, COUNTERS, read, stats, key, validate_summary,
                          check_metrics, read_replay, sha, write)


def require_complete_orientations(orientations):
    if any(sides != {False, True} for panels in orientations.values() for sides in panels.values()):
        raise ValueError('missing orientation')


def require_tuning_shape(stage, arm, generations):
    expected = 13 if (stage, arm) == ('C', 'pushpull') else 16
    if generations != expected:
        raise ValueError('generation count disagrees with this projection-stop record')


def endpoint_coverage():
    result = {}
    for stage in 'ABC':
        endpoints = sorted({setting + '|' + opponent for opponent, _, setting in A.battles(stage, 'validation')})
        for arm in A.ARMS:
            for endpoint in endpoints:
                result[stage + '|' + arm + '|' + endpoint] = (
                    {'status': 'evaluated', 'clusters': 100, 'orientations_per_cluster': 2}
                    if stage in 'AB' else
                    {'status': 'not_run', 'reason': 'projection cap stopped C tuning before validation'})
    return result


def audit():
    summary = read(OUT / 'failure.json')
    stages = 'ABC'
    validation_stages = 'AB'
    if summary['status'] != 'NOT_READY' or summary['stage'] != 'C' or 'projected combined runtime' not in summary['error']:
        raise ValueError('this auditor requires the v4 projection-stop record')
    ledger = read(OUT / 's4_seeds.json')
    if ledger['judging_seeds'] is not None:
        raise ValueError('judging seed ledger')
    uses = [u for u in ledger['uses'] if u['candidate'] != 'replay_capture']
    captures = [u for u in ledger['uses'] if u['candidate'] == 'replay_capture']
    expected_parameters = {}
    for stage in stages:
        best = read(OUT / f'{stage}_best.json') if stage in validation_stages else {a: read(OUT / f'{stage}_{a}_tuning.json')['best'] for a in A.BOUNDS}
        for arm in (A.ARMS if stage in validation_stages else ()):
            expected_parameters[(stage, 'validation', arm, 'best')] = best.get(arm, {})
        for arm in A.BOUNDS:
            log = read(OUT / f'{stage}_{arm}_tuning.json')
            expected_parameters[(stage, 'tuning', arm, 'initial')] = log['initial_knobs']
            for generation in log['generations']:
                for candidate in generation['candidates']:
                    expected_parameters[(stage, 'tuning', arm, f"{generation['generation']}:{candidate['index']}")] = candidate['knobs']
    groups = collections.defaultdict(dict)
    orientations = collections.defaultdict(lambda: collections.defaultdict(set))
    raw_summaries = {}
    counts = collections.Counter()
    planning = collections.Counter()
    hits = 0
    with gzip.open(OUT / 'fights.jsonl.gz', 'rt') as stream:
        n = 0
        for n, line in enumerate(stream, 1):
            row = json.loads(line)
            use = uses[n - 1]
            spec = row['spec']
            for field in ('arm', 'seed', 'opponent', 'setting', 'swapSides'):
                if spec[field] != use[field]:
                    raise ValueError('raw/ledger disagreement')
            if spec['params']!=use['params'] or row['cache_key']!=use['cache_key']:raise ValueError('ledger config/cache key disagreement')
            if type(row['cache_hit']) is not bool or row['cache_hit'] != use['cache_hit']:
                raise ValueError('cache accounting')
            if spec.get('skeleton')!='v4' or spec.get('endCounts') is not True:raise ValueError('v3 or survivor output missing')
            if row['request'] != A.request(spec) or row['cache_key'] != A.digest(row['request']):
                raise ValueError('request/cache key disagreement')
            result = row['summary']
            validate_summary(result)
            if result['controllerStatus'] != 'completed' or any(result['controllerFailures']):
                raise ValueError('controller failure')
            if row['S'] != result['survivors'] - result['enemySurvivors']:
                raise ValueError('raw S disagreement')
            if row['D'] != result['crossTeamDealt'][0] - result['crossTeamTaken'][0]:
                raise ValueError('raw D disagreement')
            check_metrics(row['metrics'], use['stage'])
            for metric in COUNTERS:
                planning[metric] += row['metrics'][metric]
            hit = row['cache_hit']
            hits += hit
            counts[(use['stage'], use['split'], use['arm'])] += 1
            group = (use['stage'], use['split'], use['arm'], use['candidate'])
            if spec['params'] != expected_parameters[group]:
                raise ValueError('raw parameters disagree with logged candidate')
            battle = json.dumps((spec['opponent'], spec['seed'], spec['setting']))
            if spec['swapSides'] in orientations[group][battle]:
                raise ValueError('duplicate orientation within an evaluation')
            orientations[group][battle].add(spec['swapSides'])
            groups[group][battle] = groups[group].get(battle, 0) + row['S'] / 2
            identity = key(spec)
            if identity in raw_summaries and raw_summaries[identity] != result:
                raise ValueError('repeated request changed result')
            raw_summaries[identity] = result
    expected_fights=sum(summary['budgets'].values())+sum(len(A.battles(stage,'validation'))*8 for stage in validation_stages)
    if n != len(uses) or n != expected_fights:
        raise ValueError('raw fight count')
    require_complete_orientations(orientations)
    if hits != summary['cache_hits'] or n - hits != summary['executed_fights']:
        raise ValueError('fresh/cache totals')
    prior = {arm: A.defaults(arm) for arm in A.BOUNDS}
    candidates = 0
    budgets = {}
    for stage in stages:
        best = read(OUT / f'{stage}_best.json') if stage in validation_stages else {a: read(OUT / f'{stage}_{a}_tuning.json')['best'] for a in A.BOUNDS}
        budgets[stage] = {}
        for arm in A.BOUNDS:
            log = read(OUT / f'{stage}_{arm}_tuning.json')
            if log['initial_knobs'] != prior[arm]:
                raise ValueError('stage start disagreement')
            require_tuning_shape(stage, arm, len(log['generations']))
            initial = groups[(stage, 'tuning', arm, 'initial')]
            if initial != log['initial_scores'] or set(initial) != {json.dumps(b) for b in A.battles(stage, 'tuning')}:
                raise ValueError('initial panel disagreement')
            retained = dict(prior[arm])
            retained_mean = stats(initial)['mean']
            A.optimizer.stage = stage
            es = A.optimizer(arm, prior[arm])
            for generation, entry in enumerate(log['generations']):
                if entry['generation'] != generation or len(entry['candidates']) != 16:
                    raise ValueError('CMA generation shape')
                proposed = es.ask()
                objectives = []
                for index, (x, candidate) in enumerate(zip(proposed, entry['candidates'])):
                    if candidate['index'] != index or candidate['fights'] != 38 or candidate['failure'] is not None:
                        raise ValueError('candidate accounting')
                    if any(not math.isclose(float(a), b, rel_tol=0, abs_tol=1e-10) for a, b in zip(x, candidate['normalized'])):
                        raise ValueError('CMA ask reconstruction')
                    if A.knobs(arm, candidate['normalized']) != candidate['knobs']:
                        raise ValueError('knob normalization')
                    values = groups[(stage, 'tuning', arm, f'{generation}:{index}')]
                    if values != candidate['scores'] or set(values) != set(initial) or stats(values) != candidate['stats']:
                        raise ValueError('candidate raw score/statistics reconstruction')
                    if candidate['fresh_fights']+candidate['cache_hits']!=38:raise ValueError('candidate fresh/hit count')
                    mean = stats(values)['mean']
                    accepted = mean > retained_mean
                    if candidate['accepted_as_best'] != accepted:
                        raise ValueError('best-retention disagreement')
                    if accepted:
                        retained, retained_mean = candidate['knobs'], mean
                    objectives.append(-mean)
                    candidates += 1
                es.tell(proposed, objectives)
                stop = {k: str(v) for k, v in es.stop().items()}
                if entry['optimizer_stop'] != stop or not math.isclose(entry['sigma'], es.sigma, rel_tol=0, abs_tol=1e-10):
                    raise ValueError('CMA feedback reconstruction')
                if entry['best'] != retained or entry['best_mean'] != retained_mean:
                    raise ValueError('generation best disagreement')
            if retained != log['best'] or retained != best[arm]:
                raise ValueError('stage best disagreement')
            budgets[stage][arm] = counts[(stage, 'tuning', arm)]
            if budgets[stage][arm] != 38 * (1 + 16 * len(log['generations'])):
                raise ValueError('budget/generation disagreement')
        if stage in validation_stages:
            validation = read(OUT / f'{stage}_validation.json')
            if validation['knobs'] != best or validation['panel'] != [list(b) for b in A.battles(stage, 'validation')]:
                raise ValueError('validation selection/panel disagreement')
            for arm in A.ARMS:
                raw = groups[(stage, 'validation', arm, 'best')]
                reconstructed = {}
                for endpoint, endpoint_record in validation['results'][arm].items():
                    setting, opponent = endpoint.split('|')
                    values = {k: v for k, v in raw.items() if json.loads(k)[0] == opponent and json.loads(k)[2] == setting}
                    if len(values) != 100 or values != endpoint_record['scores'] or stats(values) != endpoint_record['stats']:
                        raise ValueError('validation reconstruction/100-cluster minimum')
                    reconstructed.update(values)
                if reconstructed != raw:
                    raise ValueError('silently missing validation endpoint')
            if stage in 'AB':
                setting = 's4_melee10' if stage == 'A' else 's4_full_head'
                if validation['results']['resonator'][setting + '|novice']['stats']['mean'] <= 0:
                    if summary['status']!='STOP' or stage!=stages[-1]:raise ValueError('A/B stop gate not honored')
        prior = best
    expected_retained = {a: prior[a] for a in ('resonator', 'morale')}
    expected_retained['pushpull'] = read(OUT / 'B_best.json')['pushpull']
    if summary['best'] != expected_retained or summary['budgets'] != {a: sum(budgets[s][a] for s in stages) for a in A.BOUNDS}:
        raise ValueError('partial knob/budget mismatch')
    if (OUT / 'C_validation.json').exists() or (OUT / 'C_best.json').exists():
        raise ValueError('unexpected completed C output')
    replays = []
    if len(captures) != 4*len(validation_stages) or len(summary['replays']) != 4*len(validation_stages):
        raise ValueError('replay count')
    for capture, recorded in zip(captures, summary['replays']):
        payload = read_replay(OUT / 'replays' / recorded['file'].replace('.html', '.replay.json.gz'))
        spec = payload['spec']
        if payload['request']!=A.request(spec):raise ValueError('replay request mismatch')
        for field in ('arm','seed','opponent','setting','swapSides'):
            if capture[field]!=spec[field]:raise ValueError('replay ledger mismatch')
        if not (OUT/'replays'/recorded['file']).is_file():raise ValueError('replay HTML missing')
        if payload['summary'] != raw_summaries[key(spec)] or recorded['summary'] != payload['summary']:
            raise ValueError('replay summary changed')
        if sha(OUT / 'replays' / recorded['raw']) != recorded['sha256']:
            raise ValueError('capture bytes changed')
        check_metrics(recorded['metrics'], capture['stage'])
        if any(recorded['metrics'][name] for name in COUNTERS):
            raise ValueError('replay planning work')
        battle = json.dumps((spec['opponent'], spec['seed'], spec['setting']))
        if recorded['cluster_score'] != groups[(capture['stage'], 'validation', capture['arm'], 'best')][battle]:
            raise ValueError('replay cluster score changed')
        replays.append(dict(file=recorded['file'],matches_original=True,raw_sha256=recorded['sha256']))
    identity = read(OUT / 'run_identity.json')
    if identity['combined_machine_cap_minutes']!=360 or identity['prior_machine_minutes']!=A.PRIOR_SECONDS/60 or summary['elapsed_seconds']>A.CAP_SECONDS:raise ValueError('resource declaration/deadline mismatch')
    for name, expected in identity['code_hashes'].items():
        if sha(ROOT / name) != expected:
            raise ValueError('run code changed: ' + name)
    for name, expected in identity['optimizer_source_hashes'].items():
        if sha(ROOT / name) != expected:
            raise ValueError('optimizer source changed')
    for field, file in [('v4_protocol_sha256', 'S4_V4_PROTOCOL.md'), ('protocol_sha256', 'S4_AMENDED_PROTOCOL.md'), ('request_sha256', 'S4_DEVELOPMENT_REQUEST_CODEX.md'), ('seed_declaration_sha256', 'S4_V4_SEEDS.json')]:
        if sha(ROOT / file) != identity[field]:
            raise ValueError('declared input changed')
    if A.admit(A.BINARY) != identity['build'] or A.verify_sources() != identity['source_pin']:
        raise ValueError('native/source admission changed')
    if ledger['cache_identity_sha256'] != A.digest(A.identity('cpp', [str(A.BINARY), '--metrics'])):
        raise ValueError('cache namespace changed')
    if any(planning.values()) or summary.get('controller_failures', []) or summary.get('equation_changes', []):
        raise ValueError('unexpected planning/failure/equation change')
    if sha(ROOT/'S4_V4_DESIGN_PIN.md')!=identity['design_sha256'] or sha(ROOT.parent/'SPEC_0G.json')!=identity['spec_0g_sha256']:
        raise ValueError('design/spec changed during development')
    if any(planning.values()) or summary.get('controller_failures', []) or summary.get('equation_changes', []):
        raise ValueError('unexpected planning/failure/equation change')
    declared=read(ROOT/'S4_V4_SEEDS.json')
    for use in ledger['uses']:
        if [use['opponent'],use['seed'],use['setting']] not in declared['panels'][use['stage']][use['split']]:raise ValueError('undeclared seed use')
    if summary['status']=='READY_FOR_S5' and stages!='ABC':raise ValueError('readiness without C')
    result = dict(status='DEVELOPMENT_PARTIAL_EVIDENCE_RECONSTRUCTED',raw_fights=n,fresh_fights=n-hits,cache_hits=hits,
        replay_capture_fights=len(captures),total_executed_fights=n-hits+len(captures),tuning_fights=sum(summary['budgets'].values()),validation_fights=expected_fights-sum(summary['budgets'].values()),
        candidates=candidates,budgets_by_stage=budgets,controller_failures=0,planning_counters=dict(planning),
        both_orientations_verified=True,all_completed_100_cluster_endpoints_reconstructed=True,validation_endpoint_coverage=endpoint_coverage(),
        stop_reason=summary['error'],stages_with_validation=['A','B'],C_pushpull_generations=13,C_validation_not_run=True,CMA_ask_tell_reconstructed=True,
        candidate_parameters_verified=True,spec_0g_unchanged=True,
        replay_equality=replays,judging_seeds_used=False,seed_declaration_sha256=sha(ROOT/'S4_V4_SEEDS.json'))
    write(OUT / 'AUDIT.json', result)
    return result

if __name__ == '__main__':
    print(json.dumps(audit(), sort_keys=True))
