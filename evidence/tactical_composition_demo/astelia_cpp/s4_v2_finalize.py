"""Read-only post-run audit/report for the v2 resource stop; executes no fights.

Added after execution ended. The committed implementation and run report code remain
unchanged at their run_identity hashes. Raw results/seed uses are never rewritten.
"""
import collections
import gzip
import json
import math
from pathlib import Path
import s4_v2 as A
import s4_v2_report as R
from result_schema import validate_summary

OUT=A.OUT

def require(value, why):
    if not value:raise ValueError(why)

def read(path):return json.loads(path.read_text())

def audit():
    failure=read(OUT/'failure.json');identity=read(OUT/'run_identity.json')
    require(failure['status']=='NOT_READY' and failure['stage']=='C' and 'projected combined runtime' in failure['error'],'unexpected stop')
    require(not (OUT/'summary.json').exists(),'partial run must not have complete summary')
    require(not (OUT/'C_validation.json').exists() and not (OUT/'C_best.json').exists(),'C completion claimed')
    ledger=read(OUT/'s4_seeds.json');declared=read(A.ROOT/'S4_V2_SEEDS.json')
    require(ledger['judging_seeds'] is None,'judging seed use')
    uses=[u for u in ledger['uses'] if u['candidate']!='replay_capture']
    captures=[u for u in ledger['uses'] if u['candidate']=='replay_capture']
    logs={}
    params={}
    for stage,arms in [('A',A.BOUNDS),('B',A.BOUNDS),('C',['resonator'])]:
        for arm in arms:
            log=read(OUT/f'{stage}_{arm}_tuning.json');logs[stage,arm]=log
            params[stage,'tuning',arm,'initial']=log['initial_knobs']
            for generation in log['generations']:
                for candidate in generation['candidates']:
                    params[stage,'tuning',arm,f"{generation['generation']}:{candidate['index']}"]=candidate['knobs']
    for stage in 'AB':
        best=read(OUT/f'{stage}_best.json')
        for arm in A.ARMS:params[stage,'validation',arm,'best']=best.get(arm,{})
    counts=collections.Counter();groups=collections.defaultdict(dict)
    sides=collections.defaultdict(lambda:collections.defaultdict(set))
    summaries={};metrics=collections.Counter();hits=0
    end=collections.defaultdict(lambda:dict(fights=0,timeouts=0,enemy_artillery_alive=0))
    with gzip.open(OUT/'fights.jsonl.gz','rt') as stream:
        n=0
        for n,line in enumerate(stream,1):
            row=json.loads(line);use=uses[n-1];spec=row['spec'];result=row['summary']
            validate_summary(result)
            require(result['controllerStatus']=='completed' and result['controllerFailures']==[0,0],'controller failure')
            require(spec['skeleton']=='v2' and spec['endCounts'] is True,'wrong skeleton/schema')
            for field in ('arm','seed','opponent','setting','swapSides'):require(spec[field]==use[field],'ledger field mismatch')
            require(spec['params']==use['params'] and row['cache_key']==use['cache_key'],'ledger config/key mismatch')
            require(row['request']==A.request(spec) and row['cache_key']==A.digest(row['request']),'request mismatch')
            require(type(row['cache_hit']) is bool and row['cache_hit']==use['cache_hit'],'cache mismatch')
            require([spec['opponent'],spec['seed'],spec['setting']] in declared['panels'][use['stage']][use['split']],'undeclared seed')
            require(row['S']==result['survivors']-result['enemySurvivors'],'S mismatch')
            require(row['D']==result['crossTeamDealt'][0]-result['crossTeamTaken'][0],'D mismatch')
            R.check_metrics(row['metrics'],use['stage'])
            for counter in R.COUNTERS:metrics[counter]+=row['metrics'][counter]
            hits+=row['cache_hit'];counts[use['stage'],use['split'],use['arm']]+=1
            group=use['stage'],use['split'],use['arm'],use['candidate']
            require(spec['params']==params[group],'candidate params mismatch')
            battle=json.dumps((spec['opponent'],spec['seed'],spec['setting']))
            require(spec['swapSides'] not in sides[group][battle],'duplicate orientation')
            sides[group][battle].add(spec['swapSides']);groups[group][battle]=groups[group].get(battle,0)+row['S']/2
            k=R.key(spec)
            require(k not in summaries or summaries[k]==result,'repeat result changed');summaries[k]=result
            endpoint=spec['setting']+'|'+spec['opponent'];d=end[use['stage'],use['split'],use['arm'],endpoint]
            d['fights']+=1;d['timeouts']+=int(result['t']>=150-1e-9);d['enemy_artillery_alive']+=result['artilleryAlive'][1]
    require(n==len(uses)==66506 and n-hits==failure['executed_fights'] and hits==failure['cache_hits']==0,'raw count mismatch')
    require(not any(metrics.values()),'planning work')
    require(all(x=={False,True} for panels in sides.values() for x in panels.values()),'unpaired orientation')
    prior={arm:A.defaults(arm) for arm in A.BOUNDS};candidate_count=0
    for stage,arms in [('A',A.BOUNDS),('B',A.BOUNDS),('C',['resonator'])]:
        for arm in arms:
            log=logs[stage,arm];ng=16 if stage in 'AB' else 9
            require(log['initial_knobs']==prior[arm] and len(log['generations'])==ng,'start/generation count')
            initial=groups[stage,'tuning',arm,'initial'];require(initial==log['initial_scores'],'initial score mismatch')
            require(set(initial)=={json.dumps(b) for b in A.battles(stage,'tuning')},'tuning panel mismatch')
            best=dict(prior[arm]);best_mean=A.stats(initial)['mean']
            A.optimizer.stage=stage;es=A.optimizer(arm,best)
            for generation,entry in enumerate(log['generations']):
                require(entry['generation']==generation and len(entry['candidates'])==16,'generation shape')
                proposed=es.ask();objectives=[]
                for index,(x,candidate) in enumerate(zip(proposed,entry['candidates'])):
                    require(candidate['index']==index and candidate['fights']==38 and candidate['failure'] is None,'candidate accounting')
                    require(len(x)==len(candidate['normalized']) and all(math.isclose(float(a),b,rel_tol=0,abs_tol=1e-10) for a,b in zip(x,candidate['normalized'])),'CMA ask mismatch')
                    require(A.knobs(arm,candidate['normalized'])==candidate['knobs'],'normalized knob mismatch')
                    scores=groups[stage,'tuning',arm,f'{generation}:{index}']
                    require(scores==candidate['scores'] and set(scores)==set(initial) and A.stats(scores)==candidate['stats'],'score/stat mismatch')
                    require(candidate['fresh_fights']==38 and candidate['cache_hits']==0,'candidate fresh accounting')
                    mean=A.stats(scores)['mean'];accepted=mean>best_mean
                    require(candidate['accepted_as_best']==accepted,'best retention mismatch')
                    if accepted:best=candidate['knobs'];best_mean=mean
                    objectives.append(-mean);candidate_count+=1
                es.tell(proposed,objectives)
                require(entry['optimizer_stop']=={k:str(v) for k,v in es.stop().items()},'CMA stop mismatch')
                require(math.isclose(entry['sigma'],es.sigma,rel_tol=0,abs_tol=1e-10),'CMA sigma mismatch')
                require(entry['best']==best and entry['best_mean']==best_mean,'generation best mismatch')
            require(log['best']==best,'final best mismatch')
            require(counts[stage,'tuning',arm]==38+ng*16*38,'tuning budget mismatch')
            if stage in 'AB':require(read(OUT/f'{stage}_best.json')[arm]==best,'stage best mismatch')
        if stage in 'AB':
            prior=read(OUT/f'{stage}_best.json');validation=read(OUT/f'{stage}_validation.json')
            require(validation['knobs']==prior and validation['panel']==[list(b) for b in A.battles(stage,'validation')],'validation panel/selection mismatch')
            for arm in A.ARMS:
                raw=groups[stage,'validation',arm,'best'];combined={}
                for endpoint,record in validation['results'][arm].items():
                    setting,opponent=endpoint.split('|')
                    scores={k:v for k,v in raw.items() if json.loads(k)[0]==opponent and json.loads(k)[2]==setting}
                    require(len(scores)==100 and scores==record['scores'] and A.stats(scores)==record['stats'],'validation mismatch')
                    combined.update(scores)
                require(combined==raw,'missing validation endpoint')
            setting='s4_melee10' if stage=='A' else 's4_full_head'
            require(validation['results']['resonator'][setting+'|novice']['stats']['mean']>0,'novice gate violated')
    require(candidate_count==1680,'candidate count')
    require(failure['best']==read(OUT/'B_best.json'),'partial C presented as final knobs')
    require(failure['budgets']=={arm:sum(counts[stage,'tuning',arm] for stage in 'ABC') for arm in A.BOUNDS},'total budgets')
    partial=read(OUT/'C_resonator_partial.json');log=logs['C','resonator']
    require(partial['generation']==8 and partial['candidates']==log['generations'][-1]['candidates'] and partial['best']==log['best'],'partial C checkpoint mismatch')
    require(len(captures)==len(failure['replays'])==8,'replay count')
    replays=[]
    for capture,recorded in zip(captures,failure['replays']):
        require(capture['stage'] in 'AB','C replay after cap')
        payload=R.read_replay(OUT/'replays'/recorded['file'].replace('.html','.replay.json.gz'));spec=payload['spec']
        require(payload['summary']==summaries[R.key(spec)]==recorded['summary'],'replay summary mismatch')
        require(R.sha(OUT/'replays'/recorded['raw'])==recorded['sha256'],'replay bytes changed')
        require(payload['request']==A.request(spec),'replay request mismatch')
        battle=json.dumps((spec['opponent'],spec['seed'],spec['setting']))
        require(recorded['cluster_score']==groups[capture['stage'],'validation',capture['arm'],'best'][battle],'replay cluster mismatch')
        for field in ('arm','seed','opponent','setting','swapSides'):require(capture[field]==spec[field],'capture ledger mismatch')
        R.check_metrics(recorded['metrics'],capture['stage'])
        require(not any(recorded['metrics'][k] for k in R.COUNTERS),'replay planning work')
        require((OUT/'replays'/recorded['file']).exists(),'HTML missing')
        replays.append(dict(file=recorded['file'],summary_matches=True,raw_sha256=recorded['sha256']))
    for name,expected in identity['code_hashes'].items():require(R.sha(A.ROOT/name)==expected,'run code changed '+name)
    for name,expected in identity['optimizer_source_hashes'].items():require(R.sha(A.ROOT/name)==expected,'optimizer changed')
    for field,name in [('protocol_sha256','S4_AMENDED_PROTOCOL.md'),('v2_protocol_sha256','S4_V2_PROTOCOL.md'),('request_sha256','S4_DEVELOPMENT_REQUEST_CODEX.md'),('seed_declaration_sha256','S4_V2_SEEDS.json')]:require(R.sha(A.ROOT/name)==identity[field],'declared input changed')
    require(A.admit(A.BINARY)==identity['build'] and A.verify_sources()==identity['source_pin'],'build/source admission changed')
    require(A.digest(A.identity('cpp',[str(A.BINARY),'--metrics']))==ledger['cache_identity_sha256'],'cache namespace changed')
    for field,name in [('design_sha256','DESIGN_0G.md'),('spec_0g_sha256','SPEC_0G.json')]:require(R.sha(A.ROOT.parent/name)==identity[field],'design/spec changed')
    result=dict(status='PARTIAL_DEVELOPMENT_EVIDENCE_RECONSTRUCTED_NOT_READY',complete_stages=['A','B'],partial_stage='C',partial_arm='resonator',partial_generations=9,
        raw_fights=n,fresh_fights=n,cache_hits=0,replay_capture_fights=8,total_executed_fights=n+8,candidates=candidate_count,
        budgets_by_stage={stage:{arm:counts[stage,'tuning',arm] for arm in A.BOUNDS} for stage in 'ABC'},
        controller_failures=0,planning_counters=dict(metrics),both_orientations_verified=True,CMA_ask_tell_reconstructed=True,
        complete_validation_endpoints=12,novice_A_B_gates_passed=True,replay_equality=replays,
        current_run_inputs_unchanged=True,judging_seeds_used=False,C_validation_and_planning='not_run: conservative runtime cap',
        auditor_sha256=R.sha(Path(__file__)),analysis_added_after_run=True)
    A.write(OUT/'PARTIAL_AUDIT.json',result)
    A.write(OUT/'END_STATES_BY_SPLIT.json',{ '|'.join(k):dict(v,mean_enemy_artillery_alive=v['enemy_artillery_alive']/v['fights']) for k,v in end.items()})
    return result


def report(audit_result):
    failure=read(OUT/'failure.json');identity=read(OUT/'run_identity.json');end=R.diagnostics()
    lines=['NOT_READY','','# S4 v2 development report','',
        'Implementer family: Codex (GPT-6). Exploratory scope: decision 0028 items 15-17 and the owner’s explicit request. Independent Claude review remains required.', '',
        '**Resource stop before Stage C resonator generation 10.** The conservative projected combined duration was 181.8 minutes, exceeding the unchanged 180-minute cap. Expected duration was declared as 90–120 minutes. Execution measured 91.48 minutes (runner failure snapshot 91.45); adding the protocol’s 34.48 prior minutes gives 125.93 minutes at that snapshot. This was a projection stop before exhausting the actual allowance, not a novice performance stop or controller failure. No budget extension, retry or extra fight followed it.', '',
        'A and B completed all tuned budgets and all four arms’ validation. Both novice gates passed. C has the resonator’s initial configuration and nine complete generations (5,510 fights), with no morale/push-pull tuning, validation, final selection, or replay. Its partially retained candidate is in C_resonator_tuning.json; failure.json retains the last complete B knobs. Partial C data cannot support P2/P3, δ or n planning.', '',
        f"Part 1 committed before development: `{identity['implementation_commit']}`. [Affected tests](s4_v2_checks/tests.stdout.txt): 87 passed in 75.91 seconds; [parity and engineering receipt](s4_v2_checks/PART1_PARITY.json): 324 v0/v1 fixture summaries byte-identical (152 S3 per skeleton, 12 amended v0 replays and eight v1 replays), plus 38 v2 engineering fixtures per stateful arm, maximum refinement 0.0022835 < 0.02. One contract-test compile variable collision was fixed before tests; its failed build log is retained separately.", '',
        'Section 13 revision 5 and Clarifications (22cdd21) are implemented: full threat-precise producing-tick attribution; centre-distance kite/outranged laws; deterministic eight nearest plus extra threats capped at sixteen; weighted means; gamma fixed at 1; 11/11/3 knobs. Q3’s explicit own-artillery committed-distance override max(f_c R_i, 1.05 Rmin) applies in both range cases. V0/v1 remain unchanged on their fixtures. The prior contract-stop report stays in git history.', '',
        '[V2 declaration](S4_V2_PROTOCOL.md) retains the [amended protocol](S4_AMENDED_PROTOCOL.md): pycma 4.5.0 ask/tell, population 16, sigma .25, 16 generations, 19 fixed common tuning clusters, 9,766 evaluations per tuned arm/stage. B uses ten novice/nine regular tuning clusters; validation has 100 per level. A starts at midpoints; later stages start from prior tuning-selected best. Validation never selects knobs. All evaluated scores enter covariance adaptation, and ties retain the earlier best.', '',
        '[Fresh seed declaration](S4_V2_SEEDS.json): independent development allocations 610000000/611000000/612000000, validation +100000, C heads +101000. [Seed/configuration/orientation/cache uses](s4_v2_development/s4_seeds.json) and [run identity](s4_v2_development/run_identity.json) are retained. No judging root was read or used.', '',
        f"[Post-run partial reconstruction](s4_v2_development/PARTIAL_AUDIT.json) verifies {audit_result['raw_fights']:,} fresh logged fights, zero hits, {audit_result['candidates']:,} CMA candidates, paired orientations, exact ask/tell and retention, all twelve complete 100-cluster validation endpoints and eight matching replay captures. Total native executions: {audit_result['total_executed_fights']:,}. Zero controller failures, forks, search calls or artillery rollouts in executed data, including partial C. Run code, source/build, optimizer, design and specification hashes remain unchanged. The separate post-run auditor executes no fights; no full-run readiness is claimed.", '',
        '| Stage | Resonator | Morale | Push-pull | Validation |','|---|---:|---:|---:|---|',
        '| A | 9,766 | 9,766 | 9,766 | complete, all four arms |',
        '| B | 9,766 | 9,766 | 9,766 | complete, all four arms |',
        '| C | 5,510 (initial + 9 generations) | not_run: cap | not_run: cap | not_run: cap |', '',
        'Validation S is survivors minus enemy survivors, averaged across both orientations per seed. Intervals below are descriptive normal 95% intervals, not registered verdicts. A uses melee-only armies and removes projectile observation asymmetry; B changes army composition too, so differences are not attributable solely to visibility.', '']
    for stage in 'AB':
        validation=read(OUT/f'{stage}_validation.json')['results']
        lines += [f'## Stage {stage} validation','', '| Arm | Endpoint | Mean S | SD | SE | Descriptive 95% interval | Timeouts / fights | Mean enemy guns alive |','|---|---|---:|---:|---:|---|---|---:|']
        for arm, endpoints in validation.items():
            for endpoint,e in endpoints.items():
                s=e['stats'];ci=s['descriptive_normal_95'];d=end[stage][arm][endpoint]
                lines.append(f"| {arm} | {endpoint.replace('|',' / ')} | {s['mean']:.4f} | {s['sd']:.4f} | {s['se']:.4f} | [{ci[0]:.4f}, {ci[1]:.4f}] | {d['timeouts']} / {d['fights']} | {d['mean_enemy_artillery_alive']:.4f} |")
        setting='s4_melee10' if stage=='A' else 's4_full_head';mean=validation['resonator'][setting+'|novice']['stats']['mean']
        lines += ['',f'Novice stop gate: pass (resonator mean S = {mean:.4f} > 0).', '', '| Arm | Selected tuning mean S | Cluster SD | Stage evaluations |','|---|---:|---:|---:|']
        for arm in A.BOUNDS:
            s=A.stats(R.selected_scores(read(OUT/f'{stage}_{arm}_tuning.json')))
            lines.append(f"| {arm} | {s['mean']:.4f} | {s['sd']:.4f} | 9,766 |")
        lines += ['']
    lines += ['## Stage C and planning','',
        'Resonator tuning is partial: 9/16 generations, selected tuning mean S 12.8684 on 19 fixed clusters. This is tuning evidence only; no held-out C comparison is available. Morale and push-pull received no C budget; nearest has no C validation. The unequal partial budgets preclude a C arm comparison.', '',
        '| Arm | Nineteen-doctrine validation | Fresh novice/regular heads | Timeout/gun validation diagnostics | Replay |','|---|---|---|---|---|']
    for arm in A.ARMS:lines.append(f'| {arm} | not_run: projection cap | not_run: projection cap | not_run: projection cap | not_exported: projection cap |')
    lines += ['', 'Fresh P2/P3 paired spread, δ and bounded n: **not_run**, because C validation did not execute. Historical v0/v1 planning is not v2 evidence. [End states for every executed arm/setting, separately by tuning and validation](s4_v2_development/END_STATES_BY_SPLIT.json) retain timeouts and enemy guns alive, including all nineteen partial-C tuning settings; reused tuning seeds across candidates are descriptive, not independent validation.', '',
        '## Viewer exports','', '| Arm | Stage A | Stage B | Stage C |','|---|---|---|---|']
    for arm in A.ARMS:lines.append(f'| {arm} | [Replay](s4_v2_development/replays/A_{arm}.html) | [Replay](s4_v2_development/replays/B_{arm}.html) | not_exported: cap before completed stage |')
    lines += ['', 'Each completed stage has one exported replay per arm. Raw gzip captures and packaged viewer data match the corresponding validation orientation exactly. No new browser qualification is claimed.', '',
        '## Remaining gate and scope','',
        'Claude reviews the committed implementation and this partial development record. The cap stop is retained; no continuation or budget change is selected here. Full C development remains incomplete, and any continuation needs an explicit resource/budget decision before new execution. No S5 registration is ready. δ, a fresh specification and judging execution remain owner decisions.', '',
        'No code edits or tests ran during development. No equation changes, tuning restarts, judging seeds, registration, recorded run, SPEC_0G changes, frozen GeoMind changes, committed receipt changes, milestone status changes or growing_shapes changes were made by this task. No tactical superiority, equivalence or RRG recursion is inferred. [Raw fights](s4_v2_development/fights.jsonl.gz), candidate checkpoints, [failure](s4_v2_development/failure.json) and [execution timing](s4_v2_checks/EXECUTION.json) are retained.']
    (A.ROOT/'S4_V2_DEVELOPMENT_REPORT.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':
    result=audit();report(result)
    print(json.dumps({k:v for k,v in result.items() if k!='replay_equality'}))
