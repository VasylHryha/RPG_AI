"""Read-only reconstruction and report of section-13 v2 development; never execute fights."""
import argparse
import collections
import gzip
import hashlib
import json
import math
import random
import statistics
import subprocess
import s4_v2 as A
from s4_development import stats, paired, spread_upper, sha, write
from s4_report import seed_blocks, plan_n, key
from result_schema import validate_summary

ROOT = A.ROOT
OUT = A.OUT
CHECKS = ROOT / 's4_v2_checks'
COUNTERS = ('forks', 'search_calls', 'artillery_rollouts')


def read(path):
    return json.loads(path.read_text())


def check_metrics(metrics, stage):
    for name in COUNTERS:
        if type(metrics[name]) is not int or metrics[name] < 0:
            raise ValueError('invalid planning metric')
        if stage == 'C' and metrics[name]:
            raise ValueError('Stage C planning work: ' + name)


def selected_scores(log):
    values = log['initial_scores']
    best = stats(values)['mean']
    for generation in log['generations']:
        for candidate in generation['candidates']:
            if candidate['stats']['mean'] > best:
                values = candidate['scores']
                best = candidate['stats']['mean']
    return values


def audit():
    summary = read(OUT / 'summary.json')
    stages=''.join(summary['stages_completed'])
    if stages not in ('A','AB','ABC') or summary['status'] not in ('STOP','READY_FOR_S5'):
        raise ValueError('incomplete or invalid run')
    ledger = read(OUT / 's4_seeds.json')
    if ledger['judging_seeds'] is not None:
        raise ValueError('judging seed ledger')
    uses = [u for u in ledger['uses'] if u['candidate'] != 'replay_capture']
    captures = [u for u in ledger['uses'] if u['candidate'] == 'replay_capture']
    expected_parameters = {}
    for stage in stages:
        best = read(OUT / f'{stage}_best.json')
        for arm in A.ARMS:
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
            if spec.get('skeleton')!='v2' or spec.get('endCounts') is not True:raise ValueError('v2 or survivor output missing')
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
    expected_fights=len(stages)*29298+sum(len(A.battles(stage,'validation'))*8 for stage in stages)
    if n != len(uses) or n != expected_fights:
        raise ValueError('raw fight count')
    if any(sides != {False, True} for panels in orientations.values() for sides in panels.values()):
        raise ValueError('missing orientation')
    if hits != summary['cache_hits'] or n - hits != summary['executed_fights']:
        raise ValueError('fresh/cache totals')
    prior = {arm: A.defaults(arm) for arm in A.BOUNDS}
    candidates = 0
    budgets = {}
    for stage in stages:
        best = read(OUT / f'{stage}_best.json')
        budgets[stage] = {}
        for arm in A.BOUNDS:
            log = read(OUT / f'{stage}_{arm}_tuning.json')
            if log['initial_knobs'] != prior[arm] or len(log['generations']) != 16:
                raise ValueError('stage start/generation count')
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
            if budgets[stage][arm] != 9766:
                raise ValueError('unequal stage budget')
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
    if summary['best'] != prior or summary['budgets'] != dict.fromkeys(A.BOUNDS, 9766*len(stages)):
        raise ValueError('final knob/budget mismatch')
    replays = []
    if len(captures) != 4*len(stages) or len(summary['replays']) != 4*len(stages):
        raise ValueError('replay count')
    for capture, recorded in zip(captures, summary['replays']):
        payload = read_replay(OUT / 'replays' / recorded['file'].replace('.html', '.replay.json.gz'))
        spec = payload['spec']
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
    for name, expected in identity['code_hashes'].items():
        if sha(ROOT / name) != expected:
            raise ValueError('run code changed: ' + name)
    for name, expected in identity['optimizer_source_hashes'].items():
        if sha(ROOT / name) != expected:
            raise ValueError('optimizer source changed')
    for field, file in [('protocol_sha256', 'S4_AMENDED_PROTOCOL.md'), ('request_sha256', 'S4_DEVELOPMENT_REQUEST_CODEX.md'), ('seed_declaration_sha256', 'S4_V2_SEEDS.json')]:
        if sha(ROOT / file) != identity[field]:
            raise ValueError('declared input changed')
    if A.admit(A.BINARY) != identity['build'] or A.verify_sources() != identity['source_pin']:
        raise ValueError('native/source admission changed')
    if ledger['cache_identity_sha256'] != A.digest(A.identity('cpp', [str(A.BINARY), '--metrics'])):
        raise ValueError('cache namespace changed')
    if any(planning.values()) or summary['controller_failures'] or summary['equation_changes']:
        raise ValueError('unexpected planning/failure/equation change')
    if sha(ROOT.parent/'DESIGN_0G.md')!=identity['design_sha256'] or sha(ROOT.parent/'SPEC_0G.json')!=identity['spec_0g_sha256']:
        raise ValueError('design/spec changed during development')
    if any(planning.values()) or summary['controller_failures'] or summary['equation_changes']:
        raise ValueError('unexpected planning/failure/equation change')
    declared=read(ROOT/'S4_V2_SEEDS.json')
    for use in ledger['uses']:
        if [use['opponent'],use['seed'],use['setting']] not in declared['panels'][use['stage']][use['split']]:raise ValueError('undeclared seed use')
    if summary['status']=='READY_FOR_S5' and stages!='ABC':raise ValueError('readiness without C')
    result = dict(status='DEVELOPMENT_EVIDENCE_RECONSTRUCTED',raw_fights=n,fresh_fights=n-hits,cache_hits=hits,
        replay_capture_fights=len(captures),total_executed_fights=n-hits+len(captures),tuning_fights=len(stages)*29298,validation_fights=expected_fights-len(stages)*29298,
        candidates=candidates,budgets_by_stage=budgets,controller_failures=0,planning_counters=dict(planning),
        both_orientations_verified=True,all_100_cluster_endpoints_reconstructed=True,CMA_ask_tell_reconstructed=True,
        candidate_parameters_verified=True,spec_0g_unchanged=True,
        replay_equality=replays,judging_seeds_used=False,seed_declaration_sha256=sha(ROOT/'S4_V2_SEEDS.json'))
    write(OUT / 'AUDIT.json', result)
    return result


def read_replay(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def power():
    validation = read(OUT / 'C_validation.json')['results']
    differences = {}
    for arm in ('morale', 'pushpull'):
        differences[arm] = {k: x for opponent in A.POOL for k, x in paired(validation['resonator']['s4_p23|' + opponent]['scores'], validation[arm]['s4_p23|' + opponent]['scores']).items()}
    delta = math.ceil(max(1, .25 * max(stats(x)['sd'] for x in differences.values())) * 2) / 2
    rng = random.Random(811005)
    endpoints = {}
    for arm, values in differences.items():
        blocks = seed_blocks(values)
        development = paired(selected_scores(read(OUT/'C_resonator_tuning.json')), selected_scores(read(OUT/f'C_{arm}_tuning.json')))
        du, bu, pu = spread_upper(development, rng), spread_upper(blocks, rng), spread_upper(values, rng)
        stratum_variance = sum(spread_upper({k:v for k,v in values.items() if json.loads(k)[0] == opponent}, rng)**2 for opponent in A.POOL) / 19**2
        variance = max(bu**2, du**2/19, stratum_variance)
        n = plan_n(variance, delta, 16)
        endpoints['P2' if arm == 'morale' else 'P3'] = dict(comparison='resonator_minus_'+arm,
            configuration_cluster=stats(values),seed_block=stats(blocks),development=stats(development),
            pooled_sd_upper=pu,seed_block_sd_upper=bu,development_sd_upper=du,stratum_variance_floor=stratum_variance,
            variance_used=variance,n_per_doctrine=n,total_configuration_clusters=19*n,within_2000_bound=19*n<=2000,
            margin=delta,planning_true_mean=2*delta)
    bdev = selected_scores(read(OUT/'B_resonator_tuning.json'))
    heads = {}
    for opponent in ('novice', 'regular'):
        values = validation['resonator']['s4_full_head|' + opponent]['scores']
        development = {k:v for k,v in bdev.items() if json.loads(k)[0] == opponent}
        vu, du = spread_upper(values, rng), spread_upper(development, rng)
        heads[opponent] = dict(validation=stats(values),development=stats(development),validation_sd_upper=vu,
            development_sd_upper=du,required_n=plan_n(max(vu,du)**2,delta,32))
    n = max(e['required_n'] for e in heads.values())
    endpoints['P1'] = dict(subtests=heads,n_per_head=n,total_configuration_clusters=2*n,within_2000_bound=2*n<=2000,
        margin=0,planning_true_mean=delta)
    result = dict(status='PLANNING_ONLY_OWNER_MARGIN_AND_S5_APPROVAL_REQUIRED',delta_proposed=delta,owner_approval_required=True,
        bootstrap_resamples=2000,bootstrap_seed=811005,SD_upper_percentile=95,alpha_support=.0025,power=.90,
        method='Normal planning n=ceil((z(.9975)+z(.90))^2*variance/delta^2); floors 32 per head and 16 per doctrine. P1 uses max tuning/validation upper SD and a common n for both levels. P2/P3 use max shared-seed-block upper variance, tuning pooled upper variance/19, and independent-stratum upper variance. C validation has 100 independent shared seed blocks, averaging all 19 doctrines; covariance is retained.',
        limitation='Selected development spreads are exploratory. B development measures earlier knobs on 10 novice/9 regular clusters; final C validation measures final knobs on 100 per level. The max-noise allowance is conservative planning, not confirmation. Proposed hypothetical beneficial effects are not fitted observed head effects. No sample size can reverse an observed mean.',
        endpoints=endpoints)
    write(OUT/'POWER_PLANNING.json', result)
    return result



def diagnostics():
    """Descriptive end-state counts from EVERY validation orientation, never a new fight."""
    groups=collections.defaultdict(lambda: dict(fights=0,timeouts=0,enemy_artillery_alive=0))
    ledger=read(OUT/'s4_seeds.json')
    uses=[u for u in ledger['uses'] if u['candidate']!='replay_capture']
    with gzip.open(OUT/'fights.jsonl.gz','rt') as stream:
        for use,line in zip(uses,stream):
            if use['split']!='validation':continue
            row=json.loads(line);result=row['summary'];endpoint=use['setting']+'|'+use['opponent']
            d=groups[(use['stage'],use['arm'],endpoint)]
            d['fights']+=1;d['timeouts']+=result['t']>=150-1e-9
            d['enemy_artillery_alive']+=result['artilleryAlive'][1]
    result={}
    for (stage,arm,endpoint),d in groups.items():
        result.setdefault(stage,{}).setdefault(arm,{})[endpoint]=dict(d,mean_enemy_artillery_alive=d['enemy_artillery_alive']/d['fights'])
    write(OUT/'VALIDATION_END_STATES.json',result);return result


def partial_report():
    failure=read(OUT/'failure.json')
    stages=[stage for stage in 'ABC' if (OUT/f'{stage}_validation.json').exists()]
    end=diagnostics()
    lines=['NOT_READY','','# S4 v2 development report','',
        'Exploratory development under decision 0028 items 15-17. Independent Claude review remains required.', '',
        f"Execution stopped at stage {failure['stage']}: {failure['error']}", '',
        f"Elapsed {failure['elapsed_seconds']/60:.2f} minutes; completed validation stages: {stages}. Partial budgets: {failure['budgets']}. Raw fights and seed-use records are retained. No full-run reconstruction or readiness is claimed.", '',
        '| Stage | Arm | Endpoint | Mean S | Timeouts / fights | Mean enemy guns alive |','|---|---|---|---:|---|---:|']
    for stage in 'ABC':
        if stage not in stages:
            for arm in A.ARMS:lines.append(f'| {stage} | {arm} | not_run: execution stop before complete validation | — | — | — |')
            continue
        for arm, endpoints in read(OUT/f'{stage}_validation.json')['results'].items():
            for endpoint,e in endpoints.items():
                d=end[stage][arm][endpoint]
                lines.append(f"| {stage} | {arm} | {endpoint.replace('|',' / ')} | {e['stats']['mean']:.4f} | {d['timeouts']} / {d['fights']} | {d['mean_enemy_artillery_alive']:.4f} |")
    lines+=['','Fresh development only; no judging root or judging seeds, registration, recorded run, frozen files, committed receipts, milestone status or growing_shapes changes. No fresh P2/P3 planning without complete C. [Execution failure](s4_v2_development/failure.json); [seed uses](s4_v2_development/s4_seeds.json).']
    (ROOT/'S4_V2_DEVELOPMENT_REPORT.md').write_text('\n'.join(lines)+'\n')


def report():
    if not (OUT/'summary.json').exists():return partial_report()
    summary=read(OUT/'summary.json');audit_result=audit();end=diagnostics()
    stages=summary['stages_completed'];planning=power() if 'C' in stages else None
    lines=[summary['status'],'','# S4 v2 development report','',
        'Implementer family: Codex (GPT-6). Exploratory development under decision 0028 items 15-17 and the owner’s explicit two-part request. Independent Claude review remains required; no self-acceptance is claimed.', '',
        'Section 13 retains threat-precise unanswered status at the producing tick, range-aware centre-distance movement, eight nearest plus threats capped deterministically at sixteen, and damage-weighted means. Gamma is fixed at 1; stateful dimensions are 11/11 and push-pull uses G/f_c/m_k (3). Q3 explicitly sets own artillery committed distance to max(f_c R_i, 1.05 Rmin), including the kite case. v0/v1 remain selectable. The contract-stop report stays in history; clarifications were committed at 22cdd21.', '',
        f"Part 1 implementation commit: `{read(OUT/'run_identity.json')['implementation_commit']}`. [v0/v1 fixture parity and v2 contract checks](s4_v2_checks/PART1_PARITY.json); [affected tests](s4_v2_checks/tests.stdout.txt).", '',
        '[Amended protocol](S4_AMENDED_PROTOCOL.md), unchanged optimizer/budget: pycma 4.5.0 ask/tell; population 16; sigma 0.25; sixteen generations; 19 fixed common tuning clusters per candidate; 9,766 fight evaluations per tuned arm/stage including cache hits. A starts at midpoints, B/C at the preceding tuning-selected best. All objective values enter covariance adaptation; highest mean retains the earlier tie. Validation never selects knobs. Dimensions are 11/11/3 under Q1, nearest untuned. B tuning uses ten novice/nine regular clusters; validation uses 100 per level.', '',
        '[Fresh development seed declaration](S4_V2_SEEDS.json) and [all candidate/generation/orientation/cache uses](s4_v2_development/s4_seeds.json). Independent development bases 610000000/611000000/612000000, validation +100000, final C heads +101000; these were declared before fights and do not derive from the judging root. No judging-root contents were read by the harness. Source/build/cache/pycma inputs are pinned in [run identity](s4_v2_development/run_identity.json).', '',
        f"Expected duration was logged before the first evaluation: 90–120 minutes with ten workers if all stages run; measured {summary['elapsed_seconds']/60:.2f} minutes. The amended combined-time accounting retains 34.48 prior minutes and the 180-minute cap (145.52-minute allowance). Every generation checks the conservative remaining-work projection; every evaluation checks the deadline.", '',
        f"[Reconstruction audit](s4_v2_development/AUDIT.json): {audit_result['raw_fights']:,} accounted fights, {audit_result['fresh_fights']:,} fresh and {audit_result['cache_hits']:,} cache hits, plus {audit_result['replay_capture_fights']} captures; {audit_result['candidates']} evaluated CMA candidates. Zero controller failures; all C metrics have zero forks, search calls and artillery rollouts. Both orientations, raw scores, budgets, retention and CMA ask/tell were reconstructed.", '',
        '| Stage | Resonator novice mean S | Novice stop gate |','|---|---:|---|']
    for stage in stages:
        setting='s4_melee10' if stage=='A' else 's4_full_head'
        m=read(OUT/f'{stage}_validation.json')['results']['resonator'][setting+'|novice']['stats']['mean']
        lines.append(f"| {stage} | {m:.4f} | {'STOP' if m<=0 else 'pass'} |" if stage in 'AB' else f'| {stage} | {m:.4f} | descriptive; amended stop gates are A/B |')
    if summary['status']=='STOP':lines+=['',f"Stopped after all four arms’ Stage {summary['stop_stage']} validation because tuned resonator novice mean S ≤ 0. Later stages were not run; no registration is eligible."]
    lines+=['','Validation is cluster-averaged across both orientations. Intervals below are descriptive normal 95% intervals, with no registered scientific verdict. For the pooled doctrine result, SE/interval use shared-seed blocks to retain cross-doctrine covariance. A removes projectile observation asymmetry; B/C restore full armies. Army composition also changes, so A/B differences cannot be attributed solely to projectile visibility.','']
    for stage in 'ABC':
        lines += [f'## Stage {stage} validation','']
        if stage not in stages:
            reason=f"not_run: Stage {summary['stop_stage']} novice stop gate"
            lines += ['| Arm | Validation | Regular head | Timeouts | Mean enemy guns alive |','|---|---|---|---|---|']
            for arm in A.ARMS:lines.append(f'| {arm} | {reason} | {reason} | {reason} | {reason} |')
            lines+=[''];continue
        v=read(OUT/f'{stage}_validation.json')['results']
        lines += ['| Arm | Endpoint | Mean S | SD | SE | Descriptive 95% interval | Timeouts / fights | Mean enemy artillery alive |','|---|---|---:|---:|---:|---|---|---:|']
        for arm in A.ARMS:
            for endpoint,e in v[arm].items():
                s=e['stats'];ci=s['descriptive_normal_95'];d=end[stage][arm][endpoint]
                lines.append(f"| {arm} | {endpoint.replace('|',' / ')} | {s['mean']:.4f} | {s['sd']:.4f} | {s['se']:.4f} | [{ci[0]:.4f}, {ci[1]:.4f}] | {d['timeouts']} / {d['fights']} | {d['mean_enemy_artillery_alive']:.4f} |")
            if stage=='C':
                values={k:x for opp in A.POOL for k,x in v[arm]['s4_p23|'+opp]['scores'].items()};s=stats(values);b=stats(seed_blocks(values));ci=b['descriptive_normal_95']
                ds=[end[stage][arm]['s4_p23|'+opp] for opp in A.POOL];f=sum(d['fights'] for d in ds)
                lines.append(f"| {arm} | nineteen-doctrine pool | {s['mean']:.4f} | {s['sd']:.4f} | {b['se']:.4f} (block) | [{ci[0]:.4f}, {ci[1]:.4f}] (block) | {sum(d['timeouts'] for d in ds)} / {f} | {sum(d['enemy_artillery_alive'] for d in ds)/f:.4f} |")
        if stage=='A':lines+=['','Regular head-to-head is not_run in A: the declared stage is novice melee-only. All artillery counts are zero by army construction.']
        lines+=['','| Arm | Selected tuning mean S | Cluster SD | Stage evaluations |','|---|---:|---:|---:|']
        for arm in A.BOUNDS:
            s=stats(selected_scores(read(OUT/f'{stage}_{arm}_tuning.json')))
            lines.append(f"| {arm} | {s['mean']:.4f} | {s['sd']:.4f} | 9,766 |")
        lines+=['']
    lines+=['## Margin and sample-size planning','']
    if planning:
        lines += [f"Proposed δ = {planning['delta_proposed']:.1f} survivors, from one quarter the maximum pooled paired validation SD, rounded upward to 0.5 with minimum 1. Owner approval is required; the margin was not reduced to obtain a pass.", '',
            'Noise planning uses 2,000 bootstrap resamples (seed 811005), 95th-percentile upper SD from both selected tuning and validation; C shared-seed blocks retain cross-doctrine covariance. Alpha .0025 one-sided, power .90; floors 32/head and 16/doctrine. P1 hypothetically targets δ above zero; P2/P3 target 2δ above margin δ. These are beneficial-effect planning assumptions, not observed effect claims.', '',
            '| Endpoint | Paired mean | Config-cluster SD | Seed-block SD | Block SE | Block 95% interval | Upper SD pooled / block / tuning |','|---|---:|---:|---:|---:|---|---|']
        for endpoint in ('P2','P3'):
            e=planning['endpoints'][endpoint];s=e['configuration_cluster'];b=e['seed_block'];ci=b['descriptive_normal_95']
            lines.append(f"| {endpoint} | {s['mean']:.4f} | {s['sd']:.4f} | {b['sd']:.4f} | {b['se']:.4f} | [{ci[0]:.4f}, {ci[1]:.4f}] | {e['pooled_sd_upper']:.4f} / {e['seed_block_sd_upper']:.4f} / {e['development_sd_upper']:.4f} |")
        lines+=['','P2/P3 use maximum validation block upper variance, tuning pooled upper variance/19, and independent-stratum floor. P1 uses larger B-selected tuning/C validation upper SD and common n for both levels. B tuning has earlier knobs and ten/nine clusters; it is exploratory noise allowance. [Full calculations and both splits](s4_v2_development/POWER_PLANNING.json).','','| Endpoint | Proposed n | Total configuration clusters | Within 2,000? |','|---|---|---:|---|']
        for endpoint in ('P1','P2','P3'):
            e=planning['endpoints'][endpoint];n=e.get('n_per_head',e.get('n_per_doctrine'))
            lines.append(f"| {endpoint} | {n} {'per head' if endpoint=='P1' else 'per doctrine / shared seed blocks'} | {e['total_configuration_clusters']} | {'yes' if e['within_2000_bound'] else 'no; owner tradeoff required'} |")
    else:lines+=['not_run: stopped before C. No fresh P2/P3 paired spread, δ or bounded n planning is available. Historical amended v0 measurements remain separate.']
    lines+=['','## End-state diagnostics and remaining gate','',
        'Enemy artillery is counted directly from living occupied enemy artillery at fight end. Means and total counts per arm/setting are retained in VALIDATION_END_STATES.json. Timeout means reaching the 150-second duration; it remains an ordinary scored fight. Every endpoint above has 100 clusters / 200 fights; the doctrine pool has 1,900 configuration clusters with 100 independent shared-seed blocks. Counts are descriptive and do not change the survivor-first objective.', '',
        'Selected knobs per stage are in A_best.json, B_best.json and C_best.json where executed. [Raw fight log](s4_v2_development/fights.jsonl.gz), candidate logs, all validation scores and matching replay captures are retained. HTML replays are generated artifacts; no browser qualification is claimed for this run.', '',
        'No outcome-informed equation changes, tuning restarts, budget extensions, judging-seed use, S5 registration, recorded run, SPEC_0G.json edits, frozen GeoMind edits, committed receipt edits or milestone status changes occurred. The authorized v2 equation change preceded tuning. No tactical superiority, equivalence, RRG recursion or C4/C5 qualification is inferred from development readiness. Claude’s independent development review is next; δ and a fresh S5 specification remain owner decisions.']
    (ROOT/'S4_V2_DEVELOPMENT_REPORT.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':report()
