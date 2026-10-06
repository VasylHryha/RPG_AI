"""Stored-only audit/report. Never invokes combat, optimizers or judging."""
import collections,gzip,json,math,pathlib,statistics,time
import s4_v6 as V

def read(path):return json.loads(path.read_text())
def require(value,why):
    if not value:raise RuntimeError(why)
def hash_file(path):
    import hashlib
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def main():
    launch=read(V.CHECKS/'LAUNCH.json');out=pathlib.Path(launch['output']);identity=read(out/'run_identity.json')
    V.check_inputs(identity['code_hashes']);V.admit(V.BINARY);V.declaration()
    result=read(out/('summary.json' if (out/'summary.json').exists() else 'failure.json'))
    groups=collections.defaultdict(list);counts=collections.Counter();failures=[];diag=collections.defaultdict(lambda:dict(samples=0,low=0,rates=0,rate_sum=0,retries=0,numerical_failure_ticks=0))
    rows=0;fresh=0;hits=0;ledger=read(out/'s4_seeds.json')['uses'] if (out/'s4_seeds.json').exists() else []
    with gzip.open(out/'fights.jsonl.gz','rt') as f:
        for i,line in enumerate(f):
            row=json.loads(line);s=row['spec'];summary=row['summary'];rows+=1
            require(row['request']==V.request(s),'raw request/config mismatch')
            require(s['skeleton']=='v6','wrong version')
            require(not any(row['metrics'].get(k,0) for k in ('forks','search_calls','artillery_rollouts')),'unexpected planner work')
            if i<len(ledger):
                expected=dict(stage=row['stage'],split=row['split'],candidate=row['candidate'],**s,cache_hit=row['cache_hit'],cache_key=row['cache_key'])
                require(ledger[i]==expected,'ledger/raw row mismatch')
            fresh+=not row['cache_hit'];hits+=row['cache_hit'];counts[(row['stage'],s['arm'],row['split'],s['opponent'])]+=1
            bad=summary.get('controllerStatus')!='completed' or any(summary.get('controllerFailures',[1]))
            if bad:
                require(row.get('failure') and 'S' not in row and 'D' not in row,'failure was scored/dropped');failures.append(dict(row=i,stage=row['stage'],split=row['split'],spec=s,summary=summary));continue
            require(row['S']==summary['survivors']-summary['enemySurvivors'],'survivor score mismatch')
            groups[(row['stage'],s['arm'],row['split'],row['candidate'])].append(row)
            if s['arm']=='resonator':
                d=summary['complexDiagnostics'];require(0<=d['lowAmplitudeSamples']<=d['samples'] and 0<=d['argRateSamples']<=d['samples'],'diagnostic denominators')
                require(d['argValidityThreshold']==.2 and d['omega_melee']==0,'wrong amplitude/rate contract')
                require(math.isfinite(d['argRateAbsSum']),'nonfinite rotation diagnostic')
                if d['samples']:require(abs(d['fractionBelow02']-d['lowAmplitudeSamples']/d['samples'])<1e-14,'amplitude fraction mismatch')
                if d['argRateSamples']:require(abs(d['argRateAbsMean']-d['argRateAbsSum']/d['argRateSamples'])<1e-12,'arg rate mismatch')
                else:require(d['argRateAbsMean'] is None and d['argRateNullReason'],'arg null reason')
                if row['split']=='validation':
                    a=diag[(row['stage'],s['opponent'])];a['samples']+=d['samples'];a['low']+=d['lowAmplitudeSamples'];a['rates']+=d['argRateSamples'];a['rate_sum']+=d['argRateAbsSum'];a['retries']+=d['retryCount'];a['numerical_failure_ticks']+=d['numericalFailureTicks']
    require(rows==len(ledger),'ledger coverage')
    require((fresh,hits)==(result['executed_fights'],result['cache_hits']),'fight accounting mismatch')
    def scores(raw):
        grouped=collections.defaultdict(dict)
        for r in raw:
            s=r['spec'];key=json.dumps([s['opponent'],s['seed'],s['setting']]);require(s['swapSides'] not in grouped[key],'duplicate orientation');grouped[key][s['swapSides']]=r['S']
        require(all(set(v)=={False,True} for v in grouped.values()),'orientation pairing incomplete')
        return {k:sum(v.values())/2 for k,v in grouped.items()}
    candidates=0;generations=0;validation_endpoints=0;reconstructed_gates={};stage_winners={};retained={a:V.defaults(a) for a in V.BOUNDS}
    for stage in V.STAGES:
        stage_winners[stage]={}
        for arm in V.BOUNDS:
            path=out/f'{stage}_{arm}_tuning.json'
            if not path.exists():continue
            log=read(path);require(log['initial_scores']==scores(groups[(stage,arm,'tuning','initial')]),'initial score mismatch')
            require(log['initial_knobs']==retained[arm],'A midpoint/B inherited initial knobs mismatch')
            require(all(r['spec']['params']==log['initial_knobs'] for r in groups[(stage,arm,'tuning','initial')]),'raw initial knobs mismatch')
            incumbent=V.selection(stage,log['initial_scores']);best=dict(log['initial_knobs'])
            for generation in log['generations']:
                generations+=1;require(len(generation['candidates'])==16,'population coverage')
                for c in generation['candidates']:
                    candidates+=1;tag=f"{generation['generation']}:{c['index']}";actual=scores(groups[(stage,arm,'tuning',tag)])
                    require(V.knobs(arm,c['normalized'])==c['knobs'],'normalized knob mismatch')
                    require(all(r['spec']['params']==c['knobs'] for r in groups[(stage,arm,'tuning',tag)]),'raw tuning knobs mismatch')
                    require(actual==c['scores'],'candidate score mismatch');selection=V.selection(stage,actual)
                    for k,v in selection.items():require((list(v) if k=='rank' else v)==c['selection'][k],'selection ordering mismatch')
                    take=selection['rank']>incumbent['rank'];require(c['accepted_as_best']==take,'incumbent/tie mismatch')
                    if take:incumbent=selection;best=dict(c['knobs'])
                require(generation['best']==best,'generation retained knobs mismatch')
            require(log['best']==best,'selected knobs mismatch')
            partial_path=out/f'{stage}_{arm}_partial.json'
            if partial_path.exists():
                partial=read(partial_path)
                if partial['generation']>=len(log['generations']):
                    for c in partial['candidates']:
                        tag=f"{partial['generation']}:{c['index']}";actual=scores(groups[(stage,arm,'tuning',tag)])
                        require(actual==c['scores'] and V.knobs(arm,c['normalized'])==c['knobs'],'partial candidate scores/knobs mismatch')
                        require(all(r['spec']['params']==c['knobs'] for r in groups[(stage,arm,'tuning',tag)]),'partial raw knob mismatch')
                        choice=V.selection(stage,actual);take=choice['rank']>incumbent['rank'];require(c['accepted_as_best']==take,'partial incumbent/tie mismatch')
                        if take:incumbent=choice;best=dict(c['knobs'])
                    require(partial['best']==best,'partial retained incumbent mismatch')
            retained[arm]=best
            stage_winners[stage][arm]=best
        path=out/f'{stage}_validation.json'
        if not path.exists():continue
        validation=read(path)
        require(validation['panel']==[list(b) for b in V.battles(stage,'validation')],'validation declaration mismatch')
        require(set(stage_winners[stage])==set(V.BOUNDS),'validation without all tuned winners')
        require(all(len(read(out/f'{stage}_{a}_tuning.json')['generations'])==16 for a in V.BOUNDS),'validation without fixed generation budget')
        require(validation['knobs']==stage_winners[stage]==read(out/f'{stage}_best.json'),'validation winners mismatch')
        require(set(validation['results'])==set(V.ARMS),'validation arm coverage')
        for arm,endpoints in validation['results'].items():
            require(set(endpoints)=={b[2]+'|'+b[0] for b in V.battles(stage,'validation')},'validation endpoint set')
            raw=groups[(stage,arm,'validation','best')];actual=scores(raw)
            require(set(actual)=={json.dumps(b) for b in validation['panel']},'all-arm panel coverage')
            require(all(r['spec']['params']==validation['knobs'].get(arm,{}) for r in raw),'validation selected knobs mismatch')
            for endpoint,data in endpoints.items():
                validation_endpoints+=1;setting,head=endpoint.split('|');values={k:v for k,v in actual.items() if json.loads(k)[0]==head and json.loads(k)[2]==setting}
                require(values==data['scores'] and V.stats(values)==data['stats'],'validation endpoint mismatch')
                head_rows=[r for r in raw if r['spec']['opponent']==head and r['spec']['setting']==setting]
                require(V.end_states(head_rows)==data['descriptive'],'descriptive endpoint mismatch')
        reconstructed_gates[stage]=V.stage_gate(stage,validation['results'],sum(f['stage']==stage for f in failures))
    if 'gates' in result:
        for stage,gate in result['gates'].items():require(gate==reconstructed_gates[stage],'reported validation gate mismatch')
    require(result['best']==retained,'final/partial retained winners mismatch')
    loads=[json.loads(line)['load_average'] for line in (V.CHECKS/'LOAD_SAMPLES.jsonl').read_text().splitlines()]
    load_summary=dict(samples=len(loads),one_minute_min=min(v[0] for v in loads),one_minute_mean=statistics.mean(v[0] for v in loads),one_minute_max=max(v[0] for v in loads),first=loads[0],last=loads[-1])
    V.write(V.CHECKS/'LOAD_SUMMARY.json',load_summary)
    audit=dict(status='PASS',stored_only=True,combat_fights_executed=0,rows=rows,fresh_fights=fresh,cache_hits=hits,
               numerical_failure_rows=len(failures),failures=failures,generations=generations,candidates=candidates,
               validation_endpoints=validation_endpoints,counts=[dict(stage=k[0],arm=k[1],split=k[2],head=k[3],rows=v) for k,v in sorted(counts.items())],
               runtime_pins_verified=len(identity['code_hashes']),gates=reconstructed_gates,
               amplitude_diagnostics=[dict(stage=k[0],head=k[1],**v) for k,v in sorted(diag.items())])
    V.write(V.CHECKS/'REPORT_AUDIT.json',audit)
    timing=read(V.CHECKS/'SUPERVISOR_TIMING.json');run_timing=read(out/'RUN_TIMING.json')
    status=result['status'] if result['status'] in ('READY_TO_DRAFT_S5','PROGRESS','NOT_READY') else 'STOPPED'
    if 'error' in result or timing['returncode']!=0:status='STOPPED'
    stop_reason=result.get('error',f"supervisor exit {timing['returncode']}; process/cleanup did not complete failure-free") if status=='STOPPED' else None
    lines=[status+(': '+stop_reason if stop_reason else ''),'', '# S4 v6 development report','',
           'Implementer family: Codex (GPT-6). Owner-authorized single exploratory A/B run under decision0031. No C/P2/P3, S5 execution, judging, registration, status change or scientific acceptance.','',
           f"Runner outcome **{result['status']}**; completed stages {result.get('stages_completed',[])}. Recorded {rows:,} rows, {fresh:,} recorded fresh fights, {hits:,} cache hits, {len(failures)} recorded numerical-failure rows. Native work may have executed before the worker exception; unreturned work is not counted and actual failure-free execution is unverified. All gates are strict; tuning novice eligibility includes equality. Historical -6.025 is an unmatched development comparison.",'',
           'Planned CMA4.5.0: population16, generations16, fixed budgets; B regular-head selection with novice tuning mean>=0 eligibility. Both orientations averaged within seeds, then each head separately. No validation-based selection. The protocol allocates all four arms to a common fresh validation panel.','',
           f"Outer elapsed/awake **{timing['elapsed_seconds']/60:.3f}/{timing['awake_seconds']/60:.3f} min**, runner {run_timing['elapsed_seconds']/60:.3f} min, exit {timing['returncode']}. Expected about65min, 10workers, absolute360min allowance. Literal caffeinate command in LAUNCH.json. Launched immediately, no low-load wait. One-minute load min/mean/max {load_summary['one_minute_min']:.2f}/{load_summary['one_minute_mean']:.2f}/{load_summary['one_minute_max']:.2f}.",'',
           f"Implementation commit `{identity['implementation_commit']}`; binary `{identity['build']['binary_sha256']}`. Source/binary/build, fresh entropy and {len(identity['code_hashes'])} runtime hashes matched stored-only audit. Raw inventory is RAW_FILES_LOCAL.json (SHA256, sizes); files>45MB remain local.",'',
           '## Pre-fight checks','',
           'The 10,763-case acceptance grid passed: max Re/Im errors0.000221341/0.000335573 <=0.001; max commitment error0.000220594 <=0.02; same-substep independent RK4 agreement3.553e-15 <=1e-9. Stage counts1–48; synthetic64/65, retry/exhaustion/nonfinite/pressure cases passed. Controller counter/status/clone isolation, unclipped state, hysteresis/group boundaries, diagnostic action identity, historical contracts and fake-record gates passed. Three independent-seed default engineering captures passed <0.02 commitment refinement.37 distinct tests passed across the required prerequisite and final batch.','',
           'The initial integration wrapper failed an unsupported >15,000-byte assertion after the native contract had passed13,367 compared bytes; corrected the assertion without repeating the passed native contract. The next preservation wrapper detected concurrent Claude TrackA commits (plan/0hdesign); recorded their exact committed identities and completed the corrected preservation check. Neither was a numerical acceptance failure. All failed attempts remain separate; passed cases were not repeated.','',
           '## Validation','', '| Stage | Arm | Head | Clusters | Mean S | SD | SE | Own/enemy guns | Timeouts/fights |','|---|---|---|---:|---:|---:|---:|---|---|']
    for stage in V.STAGES:
        path=out/f'{stage}_validation.json'
        if not path.exists():
            for arm in V.ARMS:lines.append(f'| {stage} | {arm} | all planned heads | — | not_run | — | — | — | — |')
            continue
        validation=read(path)
        for arm in V.ARMS:
            for endpoint,data in validation['results'][arm].items():
                stats=data['stats'];desc=data['descriptive'];head=endpoint.split('|')[1]
                lines.append(f"| {stage} | {arm} | {head} | {stats['n']} | {stats['mean']:+.4f} | {stats['sd']:.4f} | {stats['se']:.4f} | {desc['own_guns_alive_mean']:.3f}/{desc['enemy_guns_alive_mean']:.3f} | {desc['timeouts']}/{desc['fights']} |")
    lines+=['','A regular is not_run by design. S=own survivors−enemy survivors. Guns and timeouts are descriptive; means average the two orientations within100 seed clusters. The A/B roster change is not a projectile-observation intervention.','',
            '| Stage | Novice >0 | Regular >−6.025 | Beats regular (>0, novice pass, failure-free) | Gate |','|---|---|---|---|---|']
    for stage,gate in reconstructed_gates.items():lines.append(f"| {stage} | {gate['novice_validation_pass']} | {gate['regular_progress_pass']} | {gate['beats_regular_in_development']} | {gate['status']} |")
    lines+=['','## Selected knobs','']
    for stage in V.STAGES:
        path=out/f'{stage}_best.json'
        if path.exists():lines+=['Stage '+stage+' (nearest untuned):','', '```json',json.dumps(read(path),indent=2),'```','']
    lines+=['Omega_melee is fixed0; artillery inherits omega_ranged. Selected mu/omega are optimizer diagnostics; A is real-axis melee-only and does not exercise rotation. Cubic versus morale hard saturation, role damping and the product-similarity formation change make v6 a changed controller package. No oscillation-necessity, amplitude-causation, RRG source-recursion, C5 or unchanged-C4 claim.','',
            ('Initial defaults only; no optimizer-selected knobs (selections are empty):' if not result.get('selections') else 'Final retained knobs (including partial incumbents on stops; completeness is in the selection record):'),'',
            '```json',json.dumps(dict(knobs=result.get('best'),selections=result.get('selections')),indent=2),'```','',
            '## Amplitude diagnostics','', '| Stage | Head | Unit-tick samples | Fraction amplitude<0.2 | Valid consecutive arg-rate samples | Mean absolute arg-rate rad/s | Retries | Numerical failure ticks |','|---|---|---:|---:|---:|---:|---:|---:|']
    for (stage,head),d in sorted(diag.items()):
        rate=f"{d['rate_sum']/d['rates']:.6f}" if d['rates'] else 'null: no consecutive valid endpoints'
        frac=f"{d['low']/d['samples']:.6f}" if d['samples'] else 'null: no samples'
        lines.append(f"| {stage} | {head} | {d['samples']} | {frac} | {d['rates']} | {rate} | {d['retries']} | {d['numerical_failure_ticks']} |")
    lines+=['','Host exports Re z, Im z and amplitude. Arg valid only for amplitude>=0.2; rates use both consecutive valid endpoints, unwrap within valid segments and reset across gaps. Zero is not phase0. The fraction uses accepted living prepare-unit tick records; rates are weighted by their valid endpoint counts. Scalar v5 coherence, target-phase and candidate diagnostics are explicitly not_run for v6.','',
            '## Owner recheck and delivery','', 'Owner request, verbatim:','',
            '> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it\'s fine to break the things or fully rework. Check for issues, conflicts, gaps.','',
            'Report recheck is pending; implementation review was APPROVE_WITH_NOTES after fixes. Claude CLI was not logged in, so the separate Codex reviewer is a disclosed same-family fallback. No numeric quality scores or independent scientific acceptance. Final disposition and normal-hook bundle/fresh-fetch transport go in the delivery note; Claude maintains PLAN_CURRENT, which this task did not edit.','']
    report=V.ROOT/'S4_V6_DEVELOPMENT_REPORT.md';report.write_text('\n'.join(lines))
    raw=[]
    for directory in (out,V.CHECKS,V.ROOT/'s4_v6_numerical_checks'):
        for p in directory.rglob('*'):
            if p.is_file() and (p.suffix in ('.gz','.log','.jsonl','.txt') or p.name in ('s4_seeds.json','FIXTURES.json','ACCEPTANCE_ROWS.json','FAILING_CASES.json') or p.name.endswith(('_tuning.json','_partial.json','_validation.json'))):
                raw.append(dict(path=str(p.relative_to(V.ROOT)),bytes=p.stat().st_size,sha256=hash_file(p),local_only=True))
    V.write(V.CHECKS/'RAW_FILES_LOCAL.json',dict(raw_artifacts=raw,files_over_45_MB=[r for r in raw if r['bytes']>45_000_000],all_raw_outside_git=True))
    V.write(V.CHECKS/'REPORT_IDENTITY.json',dict(report_sha256=V.sha(report),audit_sha256=V.sha(V.CHECKS/'REPORT_AUDIT.json'),status=status))
    print(json.dumps(dict(status=status,rows=rows,numerical_failures=len(failures),report_sha256=V.sha(report))))

def stopped_before_records():
    launch=read(V.CHECKS/'LAUNCH.json');out=pathlib.Path(launch['output'])
    timing=read(V.CHECKS/'SUPERVISOR_TIMING.json')
    failure=read(out/'failure.json') if (out/'failure.json').exists() else {}
    audit_error=read(V.CHECKS/'REPORT_AUDIT_FAILURE.json').get('error') if (V.CHECKS/'REPORT_AUDIT_FAILURE.json').exists() else None
    reason=audit_error or failure.get('error','Runner stopped before complete identity/raw/stage receipts; see RUN.stderr.log.')
    report=V.ROOT/'S4_V6_DEVELOPMENT_REPORT.md'
    request="Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps."
    lines=['STOPPED: '+reason,'','# S4 v6 development report','',
           'No completed development verdict. Required pre-fight checks passed; the one attempt is preserved and will not be repeated. No S5/judging/registration/status change.','',
           f"Exit {timing['returncode']}; elapsed/awake {timing['elapsed_seconds']/60:.3f}/{timing['awake_seconds']/60:.3f} min. Caffeinate launch/load records are preserved.",'',
           'All four arms A/B validation: not_run or incomplete; no endpoint is inferred from missing receipts. Numerical failures: no complete raw record to count; do not infer zero. C/P2/P3 not_run. Amplitude/arg diagnostics not_run with zero known denominators.','',
           'Retained selected/partial knobs (null means no tuning incumbent was published):','',
           '```json',json.dumps(dict(knobs=failure.get('best'),selections=failure.get('selections')),indent=2),'```','',
           'Owner request, verbatim:','', '> '+request,'', 'Report owner recheck pending; implementation recheck was APPROVE_WITH_NOTES. Claude CLI not logged in; disclosed separate Codex fallback. Main .git read-only; scoped normal-hook bundle; PLAN_CURRENT maintained by Claude.','']
    lines+=['Stored validation receipts below, if present, are preserved without changing their recorded gates. Audit is incomplete; no missing endpoint is inferred.','',
            '| Stage | Arm | Head | Stored mean S | Receipt |','|---|---|---|---:|---|']
    for stage in V.STAGES:
        path=out/f'{stage}_validation.json'
        stored=read(path)['results'] if path.exists() else {}
        for arm in V.ARMS:
            if arm in stored:
                for endpoint,data in stored[arm].items():lines.append(f"| {stage} | {arm} | {endpoint.split('|')[1]} | {data['stats']['mean']:+.4f} | stored; audit incomplete |")
            else:lines.append(f'| {stage} | {arm} | planned heads | — | not_run/incomplete |')
    report.write_text('\n'.join(lines));loads=[json.loads(line)['load_average'] for line in (V.CHECKS/'LOAD_SAMPLES.jsonl').read_text().splitlines()]
    V.write(V.CHECKS/'LOAD_SUMMARY.json',dict(samples=len(loads),first=loads[0] if loads else None,last=loads[-1] if loads else None))
    V.write(V.CHECKS/'REPORT_AUDIT.json',dict(status='INCOMPLETE_ATTEMPT',reason=reason,stored_only=True,combat_fights_executed=0))
    artifacts=[]
    for directory in (out,V.CHECKS,V.ROOT/'s4_v6_numerical_checks'):
        if directory.exists():
            for p in directory.rglob('*'):
                if p.is_file() and (p.suffix in ('.gz','.log','.jsonl','.txt') or p.name in ('s4_seeds.json','FIXTURES.json','ACCEPTANCE_ROWS.json','FAILING_CASES.json') or p.name.endswith(('_tuning.json','_partial.json','_validation.json'))):artifacts.append(dict(path=str(p.relative_to(V.ROOT)),bytes=p.stat().st_size,sha256=hash_file(p),local_only=True))
    V.write(V.CHECKS/'RAW_FILES_LOCAL.json',dict(raw_artifacts=artifacts,files_over_45_MB=[r for r in artifacts if r['bytes']>45_000_000],all_raw_outside_git=True))
    V.write(V.CHECKS/'REPORT_IDENTITY.json',dict(report_sha256=V.sha(report),status='STOPPED'))

if __name__=='__main__':
    launch=read(V.CHECKS/'LAUNCH.json');out=pathlib.Path(launch['output'])
    if not all(p.exists() for p in (out/'run_identity.json',out/'fights.jsonl.gz',out/'s4_seeds.json')) or not any((out/n).exists() for n in ('summary.json','failure.json')):
        stopped_before_records()
    else:
        try:main()
        except Exception as error:
            V.write(V.CHECKS/'REPORT_AUDIT_FAILURE.json',dict(status='FAIL',error=repr(error),stored_only=True,combat_fights_executed=0))
            stopped_before_records()
