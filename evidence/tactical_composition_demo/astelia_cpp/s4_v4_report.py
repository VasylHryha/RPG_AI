"""Read-only reconstruction and report of section-15 v4 development; never execute fights."""
import argparse
import collections
import gzip
import hashlib
import json
import math
import random
import statistics
import subprocess
import s4_v4 as A
from s4_development import stats, paired, spread_upper, sha, write
from s4_report import seed_blocks, plan_n

def key(spec):
    normalized={k:v for k,v in spec.items() if k not in ("trace","diagnostics","decisionDiagnostics")}
    normalized.setdefault("swapSides",False)
    return json.dumps(normalized,sort_keys=True)
from result_schema import validate_summary

ROOT = A.ROOT
OUT = A.OUT
CHECKS = ROOT / 's4_v4_checks'
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
    if any(planning.values()) or summary['controller_failures'] or summary['equation_changes']:
        raise ValueError('unexpected planning/failure/equation change')
    if sha(ROOT/'S4_V4_DESIGN_PIN.md')!=identity['design_sha256'] or sha(ROOT.parent/'SPEC_0G.json')!=identity['spec_0g_sha256']:
        raise ValueError('design/spec changed during development')
    if any(planning.values()) or summary['controller_failures'] or summary['equation_changes']:
        raise ValueError('unexpected planning/failure/equation change')
    declared=read(ROOT/'S4_V4_SEEDS.json')
    for use in ledger['uses']:
        if [use['opponent'],use['seed'],use['setting']] not in declared['panels'][use['stage']][use['split']]:raise ValueError('undeclared seed use')
    if summary['status']=='READY_FOR_S5' and stages!='ABC':raise ValueError('readiness without C')
    result = dict(status='DEVELOPMENT_EVIDENCE_RECONSTRUCTED',raw_fights=n,fresh_fights=n-hits,cache_hits=hits,
        replay_capture_fights=len(captures),total_executed_fights=n-hits+len(captures),tuning_fights=len(stages)*29298,validation_fights=expected_fights-len(stages)*29298,
        candidates=candidates,budgets_by_stage=budgets,controller_failures=0,planning_counters=dict(planning),
        both_orientations_verified=True,all_100_cluster_endpoints_reconstructed=True,CMA_ask_tell_reconstructed=True,
        candidate_parameters_verified=True,spec_0g_unchanged=True,
        replay_equality=replays,judging_seeds_used=False,seed_declaration_sha256=sha(ROOT/'S4_V4_SEEDS.json'))
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



def all_end_states():
    groups=collections.defaultdict(lambda: dict(fights=0,timeouts=0,enemy_artillery_alive=0))
    uses=[u for u in read(OUT/'s4_seeds.json')['uses'] if u['candidate']!='replay_capture']
    with gzip.open(OUT/'fights.jsonl.gz','rt') as stream:
        for use,line in zip(uses,stream):
            row=json.loads(line);result=row['summary'];endpoint=use['setting']+'|'+use['opponent']
            d=groups[(use['stage'],use['split'],use['arm'],endpoint)]
            d['fights']+=1;d['timeouts']+=result['t']>=150-1e-9;d['enemy_artillery_alive']+=result['artilleryAlive'][1]
    result={'|'.join(k):dict(v,mean_enemy_artillery_alive=v['enemy_artillery_alive']/v['fights']) for k,v in groups.items()}
    write(OUT/'END_STATES_BY_SPLIT.json',result)
    return result


def report():
    from s4_v4_trace_summary import trace_summary
    complete=(OUT/'summary.json').exists()
    summary=read(OUT/('summary.json' if complete else 'failure.json'))
    stages=summary.get('stages_completed',[s for s in 'ABC' if (OUT/f'{s}_validation.json').exists()])
    audit_result=audit() if complete else None
    end=diagnostics();all_end_states()
    traces=trace_summary(OUT,summary['replays'])
    planning=power() if complete and 'C' in stages else None
    status=summary['status']
    lines=[status,'','# S4 v4 development report','',
        'Implementer family: Codex (GPT-6). Owner-authorized exploratory development under decision 0028 items 16–18 and DESIGN_0G section 15 revision 7, clarified at 914dda4. The contract-stop report remains in history. Independent Claude review, owner margin and a fresh S5 specification remain separate gates.', '',
        'Travel-time holds start only on out-ranged binary mode switches: |d_escape − d_commit| / observed own speed, with no hold at speed ≤ 1 px/s or on first pair initialization. Crossings during a hold are ignored; expiry or the 0.1-own-reach band releases it. All underlying controller states keep evolving. Commit focus selects the highest damage-weight committed out-ranged pair among living pairs, tie by lowest id; fallback uses the inherited E_i weighted mean and ally forces remain unchanged. Push-pull has constant c=1 and no switches. No new knobs (11/11/3).', '',
        'Output-only 30 Hz decision records retain focus, pair modes/remaining holds, c and feasibility. Feasibility uses prepare(k) geometry and realized tick-k displacement after collision and clipping. Undefined values are null with the four specified reasons and excluded from cosine means. Per-pair holds and focus are clone-owned and death removes them. The six section-15 checks and fake-worker deadline/cleanup tests passed in the completed Part 1 batch; v0–v3 predecessor fixture parity is recorded in s4_v4_checks/PART1_PARITY.json.', '',
        f"Part 1 commit: `{read(OUT/'run_identity.json')['implementation_commit']}`. Native, source, optimizer and code identities are pinned in [run_identity.json](s4_v4_development/run_identity.json).", '',
        'Exactly the amended CMA-ES allocation: pycma 4.5.0, ask/tell, population 16, sigma .25, 16 generations, 19 common tuning clusters and 9,766 evaluations per tuned arm/stage. A starts at midpoints; B/C inherit tuning winners. Earlier ties retain the incumbent; all scores enter adaptation. Nearest is untuned. B tuning has ten novice/nine regular; validation has 100 clusters per endpoint, both orientations. All arms finish A/B validation before the resonator novice mean S≤0 gate. C has nineteen elite-no-rollout doctrines and fresh novice/regular heads; every metric is checked for zero planner work.', '',
        'Fresh development bases 940000000/941000000/942000000, validation +100000 and C heads +101000; disjoint from prior S4 revisions and S3. The new local s4_seeds.json ledger records every use. No judging root was consulted and no judging entropy, registration or recorded run was used. Raw replays, seed dumps and logs remain local, outside commits.', '',
        f"Expected duration 150–240 minutes with ten workers; measured {summary['elapsed_seconds']/60:.2f} minutes. The original owner-authorized task cap is 360 minutes, retaining {A.PRIOR_SECONDS/60:.2f} prior execution minutes and {(360*60-A.PRIOR_SECONDS)/60:.2f} minutes for this fresh restart. Bounded submission carries one absolute monotonic deadline to workers, clamps subprocess timeouts to remaining allowance, cancels pending work and kills active child process groups on stop. Replays use that same deadline. Cleanup has a separate bounded two-second child-reaping allowance. Conservative remaining-work projection runs before each generation.", '']
    if audit_result:
        lines += [f"[Reconstruction audit](s4_v4_development/AUDIT.json): {audit_result['raw_fights']:,} scored fights ({audit_result['fresh_fights']:,} fresh, {audit_result['cache_hits']} hits), {audit_result['replay_capture_fights']} replay captures, {audit_result['candidates']} CMA candidates. Both orientations, scores, budgets, retention, ask/tell and replay equality reconstruct; zero controller failures and zero planner counters.",'']
    else:lines += [f"Execution stopped at stage {summary['stage']}: {summary['error']}. Partial budgets: {summary['budgets']}. Incomplete stages are not validation comparisons.",'']
    lines += ['| Stage | Resonator novice mean S | A/B gate |','|---|---:|---|']
    for stage in stages:
        setting='s4_melee10' if stage=='A' else 's4_full_head'
        mean=read(OUT/f'{stage}_validation.json')['results']['resonator'][setting+'|novice']['stats']['mean']
        lines.append(f"| {stage} | {mean:.4f} | {('STOP' if mean<=0 else 'pass') if stage in 'AB' else 'descriptive'} |")
    if status=='STOP':lines += ['',f"STOP after all four arms' {summary['stop_stage']} validation: resonator novice mean S≤0. Later stages were not run."]
    lines += ['','Intervals are descriptive normal 95% intervals. Doctrine pool intervals use independent shared-seed blocks to retain covariance. A uses melee only; B/C add ranged/artillery and projectile observation asymmetry. Their differences do not isolate projectile visibility.','']
    validation_summary={}
    for stage in 'ABC':
        lines += [f'## Stage {stage} validation','']
        if stage not in stages:
            lines += [f"not_run for all arms and endpoints: {status} before this stage.",''];continue
        v=read(OUT/f'{stage}_validation.json')['results']
        validation_summary[stage]={arm:{ep:e['stats'] for ep,e in endpoints.items()} for arm,endpoints in v.items()}
        lines += ['| Arm | Endpoint | Mean S | SD | SE | 95% interval | Timeouts / fights | Mean enemy guns alive |','|---|---|---:|---:|---:|---|---|---:|']
        for arm in A.ARMS:
            for endpoint,e in v[arm].items():
                s=e['stats'];ci=s['descriptive_normal_95'];d=end[stage][arm][endpoint]
                lines.append(f"| {arm} | {endpoint.replace('|',' / ')} | {s['mean']:.4f} | {s['sd']:.4f} | {s['se']:.4f} | [{ci[0]:.4f}, {ci[1]:.4f}] | {d['timeouts']} / {d['fights']} | {d['mean_enemy_artillery_alive']:.4f} |")
            if stage=='C':
                values={k:x for opp in A.POOL for k,x in v[arm]['s4_p23|'+opp]['scores'].items()};s=stats(values);b=stats(seed_blocks(values));ci=b['descriptive_normal_95'];ds=[end[stage][arm]['s4_p23|'+opp] for opp in A.POOL];f=sum(d['fights'] for d in ds)
                lines.append(f"| {arm} | nineteen-doctrine pool | {s['mean']:.4f} | {s['sd']:.4f} | {b['se']:.4f} (block) | [{ci[0]:.4f}, {ci[1]:.4f}] | {sum(d['timeouts'] for d in ds)} / {f} | {sum(d['enemy_artillery_alive'] for d in ds)/f:.4f} |")
        if stage=='A':lines += ['','Regular is not_run in A: novice melee-only is declared. Guns are zero by army construction.']
        lines += ['','| Arm | Selected tuning mean S | SD | Stage evaluations |','|---|---:|---:|---:|']
        for arm in A.BOUNDS:
            s=stats(selected_scores(read(OUT/f'{stage}_{arm}_tuning.json')))
            lines.append(f"| {arm} | {s['mean']:.4f} | {s['sd']:.4f} | 9,766 |")
        lines.append('')
    write(OUT/'VALIDATION_SUMMARY.json',validation_summary)
    lines += ['## Decision trace diagnostics','',
        'These are exported-replay measurements, not telemetry across the entire validation population. A exports novice; B/C export regular for each arm. Full 30 Hz records stay in the local replay package/HTML. Means include only defined cosine samples; undefined counts are separate.', '',
        '| Replay | Holds started | Ended early | Mean completed hold s | Reversals / unit-minute | Mean cosine | Focus fraction |','|---|---:|---:|---:|---:|---:|---:|']
    def fmt(x):return 'null' if x is None else f'{x:.4f}'
    for name,d in traces['v4'].items():
        if 'counts' not in d:continue
        lines.append(f"| [{name}](s4_v4_development/replays/{name}) | {d['counts'].get('holds_started',0)} | {d['counts'].get('holds_target_band',0)} | {fmt(d['mean_completed_hold_seconds'])} | {fmt(d['commitment_reversals_per_unit_minute'])} | {fmt(d['feasibility']['mean'])} | {fmt(d['focus_usage'])} |")
    lines += ['','[DECISION_TRACE_SUMMARY.json](s4_v4_development/DECISION_TRACE_SUMMARY.json) contains expiry/disappearance counts, planned holds, terminal censoring, pair reversals, cosine distribution/quartiles and undefined counts per reason. Nearest has no skeleton modes, holds or focus.', '', '| Historical v3 regular replay | Threshold reversals / unit-minute |','|---|---:|']
    for name,d in traces['historical_v3'].items():lines.append(f"| {name} | {fmt(d['commitment_reversals_per_unit_minute'])} |")
    lines += ['',traces['comparison_limit'],'',traces['hold_limit'],'',
        'Preferred pair distance and commitment do not guarantee global progress: ally forces, changing threats, collision and arena clipping can still oppose movement. Feasibility measures that gap; a changed trace distribution does not prove a combat mechanism caused a score difference. Separately tuned arms are controller-package comparisons, with different state laws and knob dimensions.', '', '## Margin and sample-size planning','']
    if planning:
        lines += [f"Proposed δ={planning['delta_proposed']:.1f} survivors (quarter maximum pooled paired SD, rounded up to 0.5, minimum 1); owner decision required. Unchanged amended procedure uses 2,000 bootstrap resamples, upper tuning/validation noise and shared-seed covariance.",'', '| Endpoint | Paired mean | Config SD | Block SD | Proposed n | Total clusters | Within 2,000? |','|---|---:|---:|---:|---:|---:|---|']
        for endpoint in ('P1','P2','P3'):
            e=planning['endpoints'][endpoint];s=e.get('configuration_cluster',{});b=e.get('seed_block',{});n=e.get('n_per_head',e.get('n_per_doctrine'))
            lines.append(f"| {endpoint} | {fmt(s.get('mean'))} | {fmt(s.get('sd'))} | {fmt(b.get('sd'))} | {n} {'per head' if endpoint=='P1' else 'per doctrine'} | {e['total_configuration_clusters']} | {'yes' if e['within_2000_bound'] else 'no; owner tradeoff'} |")
        lines += ['','[Full spread and planning arithmetic](s4_v4_development/POWER_PLANNING.json). Alpha .0025, nominal power .90, hypothetical true mean δ for P1 and 2δ for P2/P3. Known-variance normal arithmetic is not finite-sample power qualification; selected development variance is exploratory and marginal bootstrap upper noise is not a joint bound. A later S5 specification must name/calibrate inference. Larger n cannot fix an effect below its margin.']
    else:lines += ['not_run: C was not completed; no fresh P2/P3 δ/spread/n.']
    lines += ['','[Validation end states](s4_v4_development/VALIDATION_END_STATES.json) and [all tuning/validation end states](s4_v4_development/END_STATES_BY_SPLIT.json) report timeouts and living enemy artillery separately. A timeout reaches 150 seconds and is an ordinary scored fight. Raw fight/seed/replay files remain local and are hash-bound by LOCAL_ARTIFACTS.json; small summaries travel in the bundle.','',
        'No outcome-informed equation change during execution, budget extension, judging-seed use, S5 registration, recorded run, milestone status change or scientific acceptance. READY_FOR_S5, if reached, means completed development. No browser qualification or general tactical superiority is claimed.']
    (ROOT/'S4_V4_DEVELOPMENT_REPORT.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':report()
