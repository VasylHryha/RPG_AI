"""Reconstruct S4 development evidence; no simulation or judging execution."""
import collections
import gzip
import json
import math
import random
import statistics
from s4_development import ROOT, OUT, BOUNDS, ARMS, POOL, stats, paired, spread_upper, sha, write, admit, BINARY


def read(path):return json.loads(path.read_text())


def final_development(stage,arm):
    last=read(OUT/f'{stage}_{arm}_tuning.json')[-1]
    winner=next((c for c in last['candidates'] if c['accepted']),None)
    return winner['races'][-1]['scores'] if winner else last['incumbent_scores']


def seed_blocks(values):
    blocks=collections.defaultdict(dict)
    for key,value in values.items():
        opp,seed,setting=json.loads(key)
        if setting!='s4_p23' or opp in blocks[seed]:raise ValueError('bad/duplicate panel key')
        blocks[seed][opp]=value
    if any(set(rows)!=set(POOL) for rows in blocks.values()):raise ValueError('missing doctrine in shared seed block')
    return {str(seed):statistics.mean(rows.values()) for seed,rows in sorted(blocks.items())}


def plan_n(variance,delta,floor):
    if delta<=0 or variance<0:raise ValueError('invalid planning units')
    z=statistics.NormalDist().inv_cdf(1-.0025)+statistics.NormalDist().inv_cdf(.9)
    return max(floor,math.ceil(z*z*variance/delta**2))


def corrected_power():
    raw=read(OUT/'power.json');v=read(OUT/'C_validation.json')['results']
    delta=raw['delta_proposed'];rng=random.Random(811005);ends={};dev={a:final_development('C',a) for a in BOUNDS}
    for arm in ('morale','pushpull'):
        dif={key:value for opp in POOL for key,value in paired(v['resonator']['s4_p23|'+opp]['scores'],v[arm]['s4_p23|'+opp]['scores']).items()}
        blocks=seed_blocks(dif);development=paired(dev['resonator'],dev[arm])
        du=spread_upper(development,rng);bu=spread_upper(blocks,rng);pu=spread_upper(dif,rng)
        strata_var=raw['endpoints']['resonator_minus_'+arm]['variance_upper']
        variance=max(bu**2,du**2/19,strata_var)
        n=plan_n(variance,delta,16)
        ends['P2' if arm=='morale' else 'P3']=dict(comparison='resonator_minus_'+arm,
            mean=stats(dif)['mean'],configuration_cluster=stats(dif),seed_block=stats(blocks),
            pooled_sd_upper=pu,seed_block_sd_upper=bu,development=stats(development),development_sd_upper=du,
            variance_used=variance,n_per_doctrine=n,total_configuration_clusters=19*n,
            within_2000_bound=19*n<=2000,margin=delta,planning_true_mean=2*delta)
    heads={}
    bdev=final_development('B','resonator')
    for opp in ('novice','regular'):
        vals=v['resonator']['s4_full_head|'+opp]['scores'];d={k:x for k,x in bdev.items() if json.loads(k)[0]==opp}
        vu=spread_upper(vals,rng);du=spread_upper(d,rng)
        n=plan_n(max(vu,du)**2,delta,32)
        heads[opp]=dict(validation=stats(vals),development=stats(d),validation_sd_upper=vu,development_sd_upper=du,required_n=n)
    n=max(x['required_n'] for x in heads.values())
    ends['P1']=dict(subtests=heads,n_per_head=n,total_configuration_clusters=2*n,within_2000_bound=2*n<=2000,margin=0,planning_true_mean=delta)
    result=dict(status='PLANNING_ONLY_S4_STOP_OVERRIDES',delta_proposed=delta,owner_approval_required=True,
        method='Normal planning alpha .0025, power .90, 2000-resample bootstrap SD upper (95th percentile); same target excess delta and floors as predeclared. Use maximum of tuning noise and independent validation noise. C validation uses 16 independent seed blocks, each averaging all 19 doctrines; covariance is retained. Also retain the initial within-stratum bound as a floor. P1 has a common n for both subtests and counts both against the 2000-total-cluster bound.',
        correction='Initial power.json remains unchanged but is superseded for n and uncertainty: it used only validation and assumed independent strata. No equations, fights, knobs, delta rule, tuning budget or stop decision changed. Development B spread is earlier-knob head noise; final C spread is selected-candidate panel noise, conservatively used for planning rather than unbiased confirmation.',endpoints=ends)
    write(OUT/'POWER_PLANNING_CORRECTION.json',result);return result


def key(spec):
    normalized={k:v for k,v in spec.items() if k not in ('trace','diagnostics')}
    normalized.setdefault('swapSides',False)
    return json.dumps(normalized,sort_keys=True)


def audit():
    rows={};counts=collections.Counter();metrics=collections.Counter();seed_clusters=collections.defaultdict(set)
    for folder in (OUT,ROOT/'s4_anomaly'):
        with gzip.open(folder/'fights.jsonl.gz','rt') as file:
            for line in file:
                r=json.loads(line);s=r['spec'];summary=r['summary']
                if summary['controllerStatus']!='completed' or any(summary['controllerFailures']):raise ValueError('controller failure')
                k=key(s)
                if k in rows:raise ValueError('duplicate raw fight identity')
                rows[k]=summary;counts[folder.name]+=1
                seed_clusters[(s['arm'],json.dumps(s['params'],sort_keys=True),s['setting'],s['opponent'],s['seed'])].add(s['swapSides'])
                for name in ('forks','search_calls','artillery_rollouts'):metrics[name]+=r['metrics'][name]
    if any(x!={False,True} for x in seed_clusters.values()):raise ValueError('missing orientation')
    budget={arm:0 for arm in BOUNDS};accepted={};candidates=0
    for stage in 'ABC':
        accepted[stage]={}
        for arm in BOUNDS:
            logs=read(OUT/f'{stage}_{arm}_tuning.json')
            if len(logs)!=8:raise ValueError('round count')
            accepted[stage][arm]=0
            for entry in logs:
                if len(entry['candidates'])!=8:raise ValueError('candidate count')
                fights=64+sum(c['fights'] for c in entry['candidates'])
                if fights!=320:raise ValueError('round accounting')
                budget[arm]+=fights;candidates+=8
                for c in entry['candidates']:
                    if c['accepted']:
                        g=c['races'][-1]['gain'];accepted[stage][arm]+=1
                        if not g['mean']>max(1,2*g['se']):raise ValueError('invalid acceptance')
    if budget!=dict.fromkeys(BOUNDS,7680):raise ValueError('unequal budget')
    replay=[]
    for folder in (OUT,ROOT/'s4_anomaly'):
        for file in sorted((folder/'replays').glob('*.replay.json.gz')):
            payload=json.loads(gzip.decompress(file.read_bytes()));spec=payload['spec']
            if rows[key(spec)]!=payload['summary']:raise ValueError('replay changed summary: '+file.name)
            replay.append(dict(path=str(file.relative_to(ROOT)),matches_original=True))
    ident=read(OUT/'run_identity.json')
    for name,h in ident['code'].items():
        if sha(ROOT/name)!=h:raise ValueError('run code changed')
    if admit(BINARY)['binary_sha256']!=ident['build']['binary_sha256']:raise ValueError('binary changed')
    if counts['s4_development']!=26752 or counts['s4_anomaly']!=64 or len(replay)!=16:raise ValueError('incomplete evidence')
    if any(metrics.values()):raise ValueError('unexpected planning')
    result=dict(status='DEVELOPMENT_EVIDENCE_RECONSTRUCTED',budget=budget,raw_fights=dict(counts),
        replay_capture_fights=len(replay),total_executed_fights=sum(counts.values())+len(replay),
        candidates=candidates,accepted=accepted,controller_failures=0,planning_counters=dict(metrics),
        replay_equality=replay,judging_seeds_used=False)
    write(OUT/'AUDIT.json',result);return result


def report(power,audit):
    summary=read(OUT/'summary.json');v=read(OUT/'C_validation.json')['results']
    state=summary['status'];lines=[state,'', '# S4 development report','',
        'Implementer family: Codex (GPT-6). Date: 2026-10-05. Owner-authorized development under decision 0028; design revision 3. Claude review remains pending. No registration, judging seeds, recorded S5 run, milestone status change or frozen-file modification.', '',
        f"The tuned resonator’s final novice mean S is {v['resonator']['s4_full_head|novice']['stats']['mean']:.5f} after its full 7,680-fight budget. This triggers the declared STOP. Its regular mean is {v['resonator']['s4_full_head|regular']['stats']['mean']:.5f}. No tactical superiority or equivalence verdict is assigned. The sampling and power proposals below do not override this stop.",'',
        '## Anomaly finding','',
        'Morale’s inversion reproduces on eight matched clusters: novice −16.6875, regular −4.3125. Novice skills with line formation score +1.1250; regular skills with alone brain score −30.1875. Line improves the matchup under both bundles; regular skills strengthen the enemy within either brain. This is an intended configuration/matchup effect, not a defect. Four fights were inspected before tuning. See [the finding and configuration table](s4_anomaly/ANOMALY_FINDING.md). No equations were changed.','',
        '## Declared optimizer, budget and seeds','',
        '[S4_PROTOCOL.md](S4_PROTOCOL.md) and [the seed ledger](S4_SEED_LEDGER.json) were committed before tuning (9690d67; compressed replay/anomaly follow-up 0a9e002). Eight rounds per stage; eight candidates sampled uniformly within bound-clipped incumbent neighbourhoods. Half are joint moves, half single-knob moves; radius = 0.5×0.8^round. Race 8→16→32 clusters, retaining 4 then 2 by score. Accept only paired gain > max(1 survivor, 2 SE). Rank elimination is a search heuristic. The same algorithm, seeds and budget apply to all tuned arms. Nearest is untuned. Each next stage starts at preceding tuning best; validation never selects knobs.','',
        f"Accounting: {audit['candidates']} candidates logged, 7,680 evaluations per tuned arm, 23,040 tuning fights; 3,712 validation fights; 64 anomaly diagnostic fights; 16 additional trace-capture fights. Total {audit['total_executed_fights']:,}; zero cache hits and zero controller failures. All 16 captured replay summaries equal their original fight summaries. All forks, search calls and artillery rollouts are zero. See [AUDIT.json](s4_development/AUDIT.json).",'',
        f"Actual main tuning/validation/replay duration: {summary['elapsed_seconds']/60:.2f} minutes. Anomaly duration: {read(ROOT/'s4_anomaly/summary.json')['elapsed_seconds']:.2f} seconds. Initial estimate 10–20 minutes was low; at 17.2 minutes the remaining estimate was revised to 10–15 minutes in the execution log. No code edits occurred during the long run.",'',
        '## Stage results and best knobs','',
        'S = survivors minus enemy survivors. Means, sample cluster SD and SE below are descriptive development measurements; both orientations are averaged before statistics. The 95% mean intervals are in each validation JSON. C has 16 shared seed blocks across 19 doctrines; panel mean uncertainty uses those blocks, retaining cross-doctrine covariance. A has 32 novice clusters; B and final C have 32 per head level.','']
    for stage in 'ABC':
        x=read(OUT/f'{stage}_validation.json');best=x['knobs']
        lines += [f'### Stage {stage}','',f"[Exact best knobs]({stage_path(stage,'best')}) · [validation and keyed scores]({stage_path(stage,'validation')})",'', '| Knob | Resonator | Morale | Push-pull |','|---|---:|---:|---:|']
        for knob in dict.fromkeys(k for arm in BOUNDS for k in BOUNDS[arm]):
            lines.append('| '+knob+' | '+' | '.join(f'{best[arm][knob]:.6g}' if knob in best[arm] else '—' for arm in BOUNDS)+' |')
        lines += ['', '| Arm | Validation setting | Mean S | Cluster SD | SE |','|---|---|---:|---:|---:|']
        for arm in ARMS:
            for setting,r in x['results'][arm].items():
                if setting.startswith('s4_p23'):continue
                s=r['stats'];lines.append(f"| {arm} | {setting} | {s['mean']:.4f} | {s['sd']:.4f} | {s['se']:.4f} |")
            if stage=='C':
                pooled={k:y for opp in POOL for k,y in x['results'][arm]['s4_p23|'+opp]['scores'].items()}
                s=stats(pooled);block=stats(seed_blocks(pooled))
                lines.append(f"| {arm} | P2/P3 pool, 304 config clusters / 16 seed blocks | {s['mean']:.4f} | {s['sd']:.4f} | {block['se']:.4f} (block) |")
        lines += ['', '| Tuned arm | Final-round development mean S | SD | Accepted rounds in stage |','|---|---:|---:|---:|']
        for arm in BOUNDS:
            s=stats(final_development(stage,arm));lines.append(f"| {arm} | {s['mean']:.4f} | {s['sd']:.4f} | {audit['accepted'][stage][arm]} / 8 |")
        lines += ['']
    lines += ['## Paired spreads, δ and bounded power proposal','',
        'Proposed **δ = 3.5 survivors**, from the predeclared max(1, 0.25×maximum validation pooled paired SD), rounded upward to 0.5. It has not been approved by the owner and was never reduced to obtain a pass.','',
        '| Endpoint | Paired mean | Config-cluster SD | Shared-seed-block SD | Block SE | Block mean 95% interval | SD upper (pooled / block) |','|---|---:|---:|---:|---:|---|---|']
    for name in ('P2','P3'):
        e=power['endpoints'][name];s=e['seed_block'];ci=s['descriptive_normal_95']
        lines.append(f"| {name}: {e['comparison']} | {e['mean']:.4f} | {e['configuration_cluster']['sd']:.4f} | {s['sd']:.4f} | {s['se']:.4f} | [{ci[0]:.4f}, {ci[1]:.4f}] | {e['pooled_sd_upper']:.4f} / {e['seed_block_sd_upper']:.4f} |")
    lines += ['', 'SD uncertainty is the bootstrap 95th-percentile upper value, 2,000 resamples with seed 811005; intervals are descriptive normal approximations. Power is a normal planning approximation at one-sided alpha .0025 and power .90. P1 plans a positive δ effect above zero; P2/P3 plan true mean 2δ against margin δ. Required n = ceil((z_(.9975)+z_(.90))²×variance/δ²), with floors 32 per head and 16 per doctrine. Use the larger development/validation noise allowance, retain seed-block covariance, and count all configurations against the 2,000-cluster endpoint bound.','',
        '| Endpoint | Proposed n | Total configuration clusters | Within 2,000? |','|---|---|---:|---|']
    for name in ('P1','P2','P3'):
        e=power['endpoints'][name];n=e['n_per_head'] if name=='P1' else e['n_per_doctrine'];unit='per head level' if name=='P1' else 'per doctrine / shared seed blocks'
        lines.append(f"| {name} | {n} {unit} | {e['total_configuration_clusters']} | {'yes' if e['within_2000_bound'] else 'no; owner tradeoff required'} |")
    lines += ['', 'These n values assume the stated hypothetical beneficial effect; a larger sample cannot turn the observed negative novice mean into a supported result. S4 is STOP. [POWER_PLANNING_CORRECTION.json](s4_development/POWER_PLANNING_CORRECTION.json) supplies both-split spreads, covariance-aware uncertainty and all calculations. The initial power.json is retained unchanged as superseded output.','',
        '## Watching fights','',
        'Open any linked HTML locally in a browser. Each file includes its compressed replay and has no external dependencies. Play/pause, 1×/4×/10×, timeline scrub and targets are available. Blue/orange outlines are teams; fill is resonator phase or morale commitment; HP bars show health. Grey units have no controller state. The standalone [viewer](s4_replay.html) also loads a `.replay.json.gz`. Raw 30 Hz traces are retained; display payloads sample 10 Hz with the terminal frame included.','',
        '| Stage | Resonator | Morale | Push-pull | Nearest |','|---|---|---|---|---|']
    for stage in 'ABC':lines.append('| '+stage+' | '+' | '.join(f'[{arm}](s4_development/replays/{stage}_{arm}.html)' for arm in ARMS)+' |')
    lines += ['', 'The Stage A resonator example has nonzero role rates and five of ten unit trajectories span more than 2π in unwrapped phase (maximum span 7.82 rad). This exercises the review note, without claiming rotating phases are necessary or that candidate groups meet C4/C5 qualification.','',
        '## Checks, deviations and remaining gate','',
        'The current native/controller suite passed 220 tests in 32.89 seconds before fights; replay packaging then passed its eight affected checks. End-of-session planning/audit checks and browser receipts are retained in s4_checks. RRG source pin, native binary/source admission, exact budget totals, paired orientations, candidate acceptance, code identity and replay equality were reconstructed from retained evidence.','',
        'Deviations: (1) initial test collection included archived duplicate test names and stopped before running tests; corrected to current top-level test files. (2) Large replay payloads were compressed after the anomaly diagnostic, without rerunning fights or changing raw traces. (3) Temporary implementation helpers/logs initially used /private/tmp; after owner correction they were moved/copied into s4_checks and subsequent work stayed in the project. (4) The initial runtime estimate was too low and was revised during execution. (5) Initial power output used only validation and independent-stratum variance; the final supplemental calculation uses both splits, shared-seed blocks and a common P1 n, leaving initial output unchanged. No equation changes, budget restarts, controller failures, new knobs, new arms or judging seeds.','',
        'Remaining gate: independent Claude review of these committed development artifacts. The owner must decide what follows the STOP and separately approve any δ or future S5 specification. This report does not self-accept S4, authorize S5, or alter milestone status.','']
    (ROOT/'S4_DEVELOPMENT_REPORT.md').write_text('\n'.join(lines))


def stage_path(stage,name):return f's4_development/{stage}_{name}.json'


def main():
    a=audit();p=corrected_power();report(p,a)
    files=[ROOT/'S4_DEVELOPMENT_REPORT.md',ROOT/'s4_report.py',*sorted(OUT.rglob('*'))]
    write(ROOT/'S4_REPORT_RECEIPT.json',dict(status='STOP_REVIEW_READY',reviewer_family_required='Claude',
        file_hashes={str(f.relative_to(ROOT)):sha(f) for f in files if f.is_file()},
        original_run_commit='0a9e002',initial_protocol_commit='9690d67'))
    print(json.dumps(dict(status='STOP',audit=a,power=p['endpoints']),indent=2))


if __name__=='__main__':main()
