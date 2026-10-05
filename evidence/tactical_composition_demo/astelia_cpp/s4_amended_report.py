"""Read-only reconstruction of completed amended S4; never execute fights."""
import argparse
import collections
import gzip
import hashlib
import json
import math
import random
import statistics
import subprocess
import s4_amended as A
from s4_development import stats, paired, spread_upper, sha, write
from s4_report import seed_blocks, plan_n, key
from result_schema import validate_summary

ROOT = A.ROOT
OUT = A.OUT
CHECKS = ROOT / 's4_checks'
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
    if summary['stages_completed'] != list('ABC') or summary['status'] != 'READY_FOR_S5':
        raise ValueError('this report requires a completed amended run')
    ledger = read(OUT / 's4_seeds.json')
    if ledger['judging_seeds'] is not None:
        raise ValueError('judging seed ledger')
    uses = [u for u in ledger['uses'] if u['candidate'] != 'replay_capture']
    captures = [u for u in ledger['uses'] if u['candidate'] == 'replay_capture']
    expected_parameters = {}
    for stage in 'ABC':
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
            if type(row['cache_hit']) is not bool or row['cache_hit'] != use['cache_hit']:
                raise ValueError('cache accounting')
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
    if n != len(uses) or n != 107094:
        raise ValueError('raw fight count')
    if any(sides != {False, True} for panels in orientations.values() for sides in panels.values()):
        raise ValueError('missing orientation')
    if hits != summary['cache_hits'] or n - hits != summary['executed_fights']:
        raise ValueError('fresh/cache totals')
    prior = {arm: A.defaults(arm) for arm in A.BOUNDS}
    candidates = 0
    budgets = {}
    for stage in 'ABC':
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
                raise ValueError('A/B stop gate failed')
        prior = best
    if summary['best'] != prior or summary['budgets'] != dict.fromkeys(A.BOUNDS, 29298):
        raise ValueError('final knob/budget mismatch')
    replays = []
    if len(captures) != 12 or len(summary['replays']) != 12:
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
    for field, file in [('protocol_sha256', 'S4_AMENDED_PROTOCOL.md'), ('request_sha256', 'S4_DEVELOPMENT_REQUEST_CODEX.md'), ('seed_declaration_sha256', 's4_amended_resources/s4_seeds_declared.json')]:
        if sha(ROOT / file) != identity[field]:
            raise ValueError('declared input changed')
    if A.admit(A.BINARY) != identity['build'] or A.verify_sources() != identity['source_pin']:
        raise ValueError('native/source admission changed')
    if ledger['cache_identity_sha256'] != A.digest(A.identity('cpp', [str(A.BINARY), '--metrics'])):
        raise ValueError('cache namespace changed')
    if any(planning.values()) or summary['controller_failures'] or summary['equation_changes']:
        raise ValueError('unexpected planning/failure/equation change')
    owner = read(CHECKS / 'AMENDED_GATE_OWNER_DECISION.json')
    if owner['report_first_line'] != 'READY_FOR_S5' or owner['novice_stop_gates'] != ['A', 'B']:
        raise ValueError('owner reporting decision missing')
    prefix = ROOT.relative_to(ROOT.parents[2]).as_posix()
    old_receipt_bytes = subprocess.check_output(['git','show',f'd456a4f:{prefix}/S4_REPORT_RECEIPT.json'],cwd=ROOT)
    if hashlib.sha256(old_receipt_bytes).hexdigest() != sha(ROOT/'S4_REPORT_RECEIPT.json'):
        raise ValueError('original committed receipt changed')
    for name, expected in json.loads(old_receipt_bytes)['file_hashes'].items():
        if name == 'S4_DEVELOPMENT_REPORT.md':
            blob = subprocess.check_output(['git','show',f'd456a4f:{prefix}/{name}'],cwd=ROOT)
            actual = hashlib.sha256(blob).hexdigest()
        else:
            actual = sha(ROOT/name)
        if actual != expected:
            raise ValueError('original evidence changed: '+name)
    result = dict(status='DEVELOPMENT_EVIDENCE_RECONSTRUCTED',raw_fights=n,fresh_fights=n-hits,cache_hits=hits,
        replay_capture_fights=12,total_executed_fights=n-hits+12,tuning_fights=87894,validation_fights=19200,
        candidates=candidates,budgets_by_stage=budgets,controller_failures=0,planning_counters=dict(planning),
        both_orientations_verified=True,all_100_cluster_endpoints_reconstructed=True,CMA_ask_tell_reconstructed=True,
        candidate_parameters_verified=True,original_committed_evidence_unchanged=True,
        replay_equality=replays,judging_seeds_used=False,owner_gate_decision_sha256=sha(CHECKS/'AMENDED_GATE_OWNER_DECISION.json'))
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
        limitation='Selected development spreads are exploratory. B development measures earlier knobs on 10 novice/9 regular clusters; final C validation measures final knobs on 100 per level. The max-noise allowance is conservative planning, not confirmation. Proposed hypothetical beneficial effects are not the observed negative head means. No sample size can reverse an observed mean.',
        endpoints=endpoints)
    write(OUT/'POWER_PLANNING.json', result)
    return result


def report():
    audit_result = read(OUT/'AUDIT.json')
    p = read(OUT/'POWER_PLANNING.json')
    summary = read(OUT/'summary.json')
    browser = read(CHECKS/'AMENDED_BROWSER_RECEIPT.json')
    if browser['errors'] or len(browser['checks']) != 12:
        raise ValueError('incomplete browser checks')
    lines = ['READY_FOR_S5', '', '# S4 amended development report', '',
        'Implementer family: Codex (GPT-6). Date: 2026-10-05. **Claude development review: APPROVE_WITH_NOTES.** This is development readiness under the amended A/B-only gates, as explicitly directed by the owner. This S4 run performed no S5 registration, judging-seed use, recorded S5 run, milestone status change or frozen GeoMind modification.', '',
        '**Resonator novice validation: A +2.765; B +5.920; final C −6.565.** Final C regular is −8.945. Stage C panel tuning lost the earlier positive novice result. The owner explicitly chose the amended A/B-only gates after seeing the final negative novice result; see [the preserved decision](s4_checks/AMENDED_GATE_OWNER_DECISION.json). This report does not claim P1 support, tactical superiority, equivalence, RRG recursion or C4/C5 group qualification.', '',
        'The original racing-protocol run reached STOP and remains preserved at commit d456a4f: [original report](s4_development/S4_DEVELOPMENT_REPORT_ORIGINAL.md), [original data](s4_development/summary.json). The owner then authorized a separate amended run. Request ee21545 changed during the original run; the amended CMA-ES protocol, resources and harness were committed at 8c89561 before amended tuning. Historical S4_REPORT_RECEIPT.json is unchanged and resolves historical root-file hashes at d456a4f; the new run has its own S4_AMENDED_REPORT_RECEIPT.json.', '',
        'Claude reviewed the original run at a837561 (correction at e12f259): [APPROVE_WITH_NOTES; original STOP stands](../astelia_cpp_review_claude/S4_ORIGINAL_REVIEW.md). Claude separately reviewed the amended run and retained report during finalization: [APPROVE_WITH_NOTES](../astelia_cpp_review_claude/S4_AMENDED_REVIEW.md), committed at e12f259 and updated at 5460380. Subsequent final-report edits add provenance, formatting and the review links; the measurements are unchanged.', '',
        '## Anomaly finding', '',
        'The original diagnostic compared eight matched clusters and both orientations: morale novice/alone −16.6875; regular/line −4.3125; novice skills/line +1.1250; regular skills/alone −30.1875. Line formation improves the matchup under both skill bundles; regular skills strengthen the opponent within either brain. This explains the inversion as a configuration/matchup effect. Four fights were inspected; no genuine controller defect was found and no equations were changed. [Finding and watched fights](s4_anomaly/ANOMALY_FINDING.md).', '',
        '## Declared optimizer, budgets and seed use', '',
        '[Amended protocol](S4_AMENDED_PROTOCOL.md): pycma 4.5.0 CMAEvolutionStrategy ask/tell, bounds-normalized knobs in [0,1], population 16, initial sigma 0.25, sixteen generations, default active covariance adaptation, no restart and no two-SE acceptance. Every candidate uses nineteen fixed common tuning clusters per stage. All objective values enter CMA; the highest mean evaluated configuration, including the initial configuration, is retained with earlier ties. Validation never chooses knobs. A starts at midpoints; B/C start at preceding tuning best. Dimensions are 10/10/2 for resonator/morale/push-pull; nearest is untuned.', '',
        'Each tuned arm receives **9,766 evaluations per stage**, including cache hits: 38 initial fights plus 16×16×38 candidate fights. Across three stages that is **29,298 per arm**, 87,894 tuning fights and 2,304 candidates. A uses nineteen novice melee clusters; B uses ten novice and nine regular full-army clusters; C uses one cluster per doctrine. The slight B tuning imbalance is explicit; validation has 100 per level.', '',
        f"The final audit reconstructs **{audit_result['raw_fights']:,} raw tuning/validation fights**, **{audit_result['cache_hits']} cache hits**, and twelve additional replay captures: **{audit_result['total_executed_fights']:,} executed fights**. Zero controller failures, zero equation changes and zero forks/search calls/artillery rollouts in every retained fight metric and replay metric. All twelve capture summaries equal their original played-fight summaries. [Audit](s4_amended_development/AUDIT.json).", '',
        '[Per-use seed ledger](s4_amended_development/s4_seeds.json) records every stage, split, arm, candidate, seed, opponent, orientation and hit status, including capture reuse. Tuning ranges are 410000000/411000000/412000000 + [0,18]; validation uses each stage base +100000+[0,99], shared across arms/configurations. Final C head checks use +101000+[0,99]. No judging generator or judging seeds were used. result_cache.py supplies the admitted binary/source/schema/helper namespace; archived pycma sources and dependency metadata are in s4_amended_resources/.', '',
        f"Ten native workers. Actual amended tuning/validation/capture duration: **{summary['elapsed_seconds']/60:.2f} minutes**; original main run 34.48 minutes, combined **{34.48+summary['elapsed_seconds']/60:.2f} minutes**, below the 180-minute native-run cap. The initial 90–120-minute amended estimate and later completion estimates were too short, particularly for full validation; updates and revisions were reported during execution. No run code or test edits occurred while the amended run was active.", '',
        '## Stage results and best knobs', '',
        'S is survivors minus enemy survivors. Both orientations are averaged into one cluster before statistics. Each head comparison has 100 validation clusters. C has 100 clusters per doctrine (1,900 configuration clusters), sharing 100 seeds across all nineteen doctrines; panel mean SE uses the 100 seed-block means. SDs, SEs and normal 95% intervals are descriptive development measurements, not registered verdicts.', '',
        'A has no projectile asymmetry. B/C scripted brains can see shots and shells while our controllers cannot. However, native config_codec.cpp lines 244–245 explicitly disable shot/shell dodging for novice; regular enables shell dodging and raw shot leading. Projectile dodging therefore cannot explain losses against novice. Army composition changes from A to B, and tuning objective/knobs change from B to C; these comparisons do not isolate the cause of full-army losses.', '']
    for stage in 'ABC':
        v = read(OUT/f'{stage}_validation.json')
        best = v['knobs']
        lines += [f'### Stage {stage}', '', f'[Exact knobs](s4_amended_development/{stage}_best.json) · [validation and keyed scores](s4_amended_development/{stage}_validation.json)', '',
            '| Knob | Resonator | Morale | Push-pull |', '|---|---:|---:|---:|']
        for knob in dict.fromkeys(k for bounds in A.BOUNDS.values() for k in bounds):
            lines.append('| '+knob+' | '+' | '.join(f'{best[a][knob]:.6g}' if knob in best[a] else '—' for a in A.BOUNDS)+' |')
        lines += ['', '| Arm | Validation comparison | Mean S | Cluster SD | SE | 95% mean interval |', '|---|---|---:|---:|---:|---|']
        for arm in A.ARMS:
            for endpoint, entry in v['results'][arm].items():
                if endpoint.startswith('s4_p23'): continue
                s = entry['stats']; ci = s['descriptive_normal_95']
                display = endpoint.replace('|', ' / ')
                lines.append(f"| {arm} | {display} | {s['mean']:.4f} | {s['sd']:.4f} | {s['se']:.4f} | [{ci[0]:.4f}, {ci[1]:.4f}] |")
            if stage == 'C':
                values = {k:x for opp in A.POOL for k,x in v['results'][arm]['s4_p23|'+opp]['scores'].items()}
                s = stats(values); b = stats(seed_blocks(values)); ci = b['descriptive_normal_95']
                lines.append(f"| {arm} | nineteen-doctrine pool | {s['mean']:.4f} | {s['sd']:.4f} | {b['se']:.4f} (block) | [{ci[0]:.4f}, {ci[1]:.4f}] (block) |")
        lines += ['', '| Arm | Selected tuning mean S | Tuning cluster SD | Evaluations in stage |', '|---|---:|---:|---:|']
        for arm in A.BOUNDS:
            s = stats(selected_scores(read(OUT/f'{stage}_{arm}_tuning.json')))
            lines.append(f"| {arm} | {s['mean']:.4f} | {s['sd']:.4f} | 9,766 |")
        lines += ['']
    lines += ['## Paired spreads, margin and bounded power proposal', '',
        f"Proposed **δ = {p['delta_proposed']:.1f} survivors**: max(1, quarter the maximum pooled validation SD of the two paired differences), rounded upward to 0.5. This applies the predeclared rule to amended validation; it is an owner decision and was not reduced to get a pass.", '',
        '| Endpoint | Paired mean | Config-cluster SD | Shared-seed-block SD | Block SE | Block 95% interval | Upper SD, pooled / block / tuning |', '|---|---:|---:|---:|---:|---|---|']
    for endpoint in ('P2', 'P3'):
        e = p['endpoints'][endpoint]; s = e['configuration_cluster']; b = e['seed_block']; ci = b['descriptive_normal_95']
        lines.append(f"| {endpoint}: {e['comparison']} | {s['mean']:.4f} | {s['sd']:.4f} | {b['sd']:.4f} | {b['se']:.4f} | [{ci[0]:.4f}, {ci[1]:.4f}] | {e['pooled_sd_upper']:.4f} / {e['seed_block_sd_upper']:.4f} / {e['development_sd_upper']:.4f} |")
    lines += ['', 'Noise uncertainty uses 2,000 bootstrap resamples, seed 811005, 95th-percentile upper SD. C seed blocks retain cross-doctrine covariance. Normal planning uses one-sided support alpha .0025 and power .90: n = ceil((z(.9975)+z(.90))²×variance/δ²), with floors 32 per head level and 16 per doctrine. P1 plans a hypothetical true mean δ above zero; P2/P3 plan true mean 2δ above margin δ. These are beneficial-effect planning assumptions, not fitted effect claims.', '',
        'P2/P3 use the maximum of validation block upper variance, selected tuning pooled upper variance/19, and the independent-stratum upper variance floor. P1 uses the larger B tuning/C validation upper SD and a common n for both levels. B tuning uses earlier knobs and only ten/nine clusters; it is an exploratory noise allowance, not validation of final C knobs. All calculations and both-split summaries are in [POWER_PLANNING.json](s4_amended_development/POWER_PLANNING.json).', '',
        '| Endpoint | Proposed n | Total configuration clusters | Within 2,000? |', '|---|---|---:|---|']
    for endpoint in ('P1','P2','P3'):
        e = p['endpoints'][endpoint]; n = e.get('n_per_head', e.get('n_per_doctrine'))
        lines.append(f"| {endpoint} | {n} {'per head level' if endpoint=='P1' else 'per doctrine / shared seed blocks'} | {e['total_configuration_clusters']} | {'yes' if e['within_2000_bound'] else 'no; owner tradeoff required'} |")
    lines += ['', 'A larger n cannot reverse the observed negative final head means. No support/refutation/equivalence verdict is assigned to unregistered development data. The owner must approve δ and a future S5 specification separately; any endpoint over the 2,000-cluster bound requires an owner tradeoff.', '',
        'S5 must explicitly pin its P1 knob source: this report supplies both B-tuned and final C-tuned head results; the current P1 planning calculation uses final C validation. Choosing B instead changes that planning input and requires a new declared calculation from the retained B data. S5 must also register its inference unit: these P2/P3 n values count independent shared-seed blocks (nineteen configurations each), while δ uses pooled configuration-cluster spread. The original Claude review also recommends controller-cost work before further large runs; no new native optimization or cost benchmark was performed here.', '',
        '## Watching fights', '',
        'Open a linked HTML locally in a browser. Each file embeds its compressed replay and needs no external dependencies. Play/pause, 1×/4×/10×, timeline scrub and target lines are available. Team outlines are blue/orange; fill shows resonator phase or morale commitment (the bounded transform of its state); grey units have no controller state; HP bars show health. Raw traces retain 30 Hz; display payloads retain 10 Hz plus the terminal frame. [Standalone loader](s4_replay.html) also opens .replay.json.gz files.', '',
        '| Stage | Resonator | Morale | Push-pull | Nearest |', '|---|---|---|---|---|']
    for stage in 'ABC':
        lines.append('| '+stage+' | '+' | '.join(f'[{a}](s4_amended_development/replays/{stage}_{a}.html)' for a in A.ARMS)+' |')
    lines += ['', 'All twelve HTML viewers loaded with no browser runtime errors; play/pause, scrub and target controls were exercised. [Browser receipt](s4_checks/AMENDED_BROWSER_RECEIPT.json). Phase state is prepared at the tick boundary while commitment is newly computed; this display timing does not change played fights.', '',
        'The selected amended Stage A resonator has nonzero role rates, but its ten captured tracks span less than 2π (maximum 3.96 rad). The separately retained original Stage A replay has five tracks spanning more than 2π, demonstrating available rotating trajectories without forcing the amended optimizer toward them. No locking/rotation necessity or qualifying candidate-group claim follows from these examples.', '',
        '## Checks, deviations and remaining gate', '',
        'The original current native/controller batch passed 220 tests in 32.89 seconds. The final amended optimizer/cache/schema batch passed 31 checks before this run. End-of-session report checks are retained in s4_checks. The audit reconstructs all candidate and validation scores from raw summaries, replays CMA ask/tell and best retention, confirms all budgets and both orientations, verifies all 100-cluster endpoints, checks every C fight metric (both orientations), rechecks admitted source/binary/optimizer identity, and compares every captured summary to its original fight.', '',
        'Deviations: (1) the request changed during the original run; its completed STOP evidence was preserved and the owner authorized a separate amended run. (2) The amended request supersedes the old racing/2-SE optimizer and, by explicit owner clarification, the full-budget novice gate with A/B-only gates. (3) B tuning allocates ten novice and nine regular clusters. (4) The existing shared closed result schema was extended for S3 summaries; cache helper and native controller equations were unchanged. (5) pycma was installed only under project build/, with dependency metadata and source archive retained; frozen environment files were untouched. (6) Runtime/completion estimates were revised as full validation ran more slowly; the native-run cap was respected. (7) Earlier temporary helpers/logs were moved/copied into the project after owner correction; amended scripts, cache, logs, evidence and test temp roots stayed in the project. No controller failures, outcome-informed equations, budget restarts, new knobs/arms, judging seeds or recorded S5 execution.', '',
        '**Remaining gate: owner approval of δ and the future S5 specification.** Claude approved this development record with notes, including pinning the knob source per endpoint, preserving both P1 levels and fixing the inference unit before judging. READY_FOR_S5 is the owner-directed development label, not permission to execute S5. A concurrent S5 draft was created separately; it is outside this S4 implementation commit.', '']
    text = '\n'.join(lines)
    (ROOT/'S4_DEVELOPMENT_REPORT.md').write_text(text)
    (OUT/'S4_DEVELOPMENT_REPORT_AMENDED.md').write_text(text)
    files = [ROOT/'S4_DEVELOPMENT_REPORT.md',ROOT/'s4_amended_report.py',ROOT/'test_s4_amended_report.py',
        ROOT/'S4_AMENDED_PROTOCOL.md',ROOT/'s4_amended.py',ROOT/'test_s4_amended.py',ROOT/'S4_DEVELOPMENT_REQUEST_CODEX.md',
        ROOT/'s3_runner.py',ROOT/'s4_development.py',ROOT/'result_cache.py',ROOT/'result_schema.py',ROOT/'s4_replay.html',
        CHECKS/'AMENDED_GATE_OWNER_DECISION.json',CHECKS/'AMENDED_BROWSER_RECEIPT.json',CHECKS/'check_amended_replays.mjs',
        CHECKS/'amended_run.console.txt',CHECKS/'amended_report_tests.stdout.txt',CHECKS/'amended_evidence_audit.stdout.txt',
        CHECKS/'amended_final_tests.stdout.txt',CHECKS/'amended_browser.console.txt',CHECKS/'amended_browser_checks.stdout.txt',
        *sorted(OUT.rglob('*')),*sorted((ROOT/'s4_amended_resources').rglob('*')),*sorted((CHECKS/'amended_replay_screenshots').rglob('*'))]
    write(ROOT/'S4_AMENDED_REPORT_RECEIPT.json',dict(status='READY_FOR_S5_REVIEWED_WITH_NOTES',reviewer_family='Claude',
        protocol_commit='8c89561',original_evidence_commit='d456a4f',owner_gate_decision_sha256=sha(CHECKS/'AMENDED_GATE_OWNER_DECISION.json'),
        original_review_commit='e12f259',original_review_sha256=sha(ROOT.parent/'astelia_cpp_review_claude/S4_ORIGINAL_REVIEW.md'),
        amended_review_commit='5460380',amended_review_sha256=sha(ROOT.parent/'astelia_cpp_review_claude/S4_AMENDED_REVIEW.md'),
        file_hashes={str(f.relative_to(ROOT)):sha(f) for f in files if f.is_file()}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', action='store_true')
    args = parser.parse_args()
    if args.report:
        report()
        print('READY_FOR_S5; Claude development review APPROVE_WITH_NOTES')
    else:
        a = audit(); p = power()
        print(json.dumps(dict(audit=a,delta_proposed=p['delta_proposed'],endpoints=p['endpoints']),indent=2))
