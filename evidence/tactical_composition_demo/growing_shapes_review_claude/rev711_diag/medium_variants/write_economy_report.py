"""Render verified exploratory economy completions and retained controls; never run a medium."""
from collections import Counter
import copy
import json
from execute_economy_plan import OUT, LOCAL, ARMS, JOBS, load_completed, code_hashes, integrity, sha, CAP
from write_coverage_report import aggregate, passes

RD3_POOL = 0.08601377266387726
TARGET = 2 * RD3_POOL
CLASSES = ('critical','redundant','front','orphan')


def reading(arm, verified):
    if arm['status'] != 'DONE' or not verified:
        return 'INCOMPLETE'
    if arm['gate_shape']['i']['passes'] <= 3:
        return 'REGRESSION'
    if arm['pooled_3_6'] >= TARGET and arm['gate_shape']['i']['passes'] >= 4:
        return 'COVERAGE_IMPROVES'
    return 'DESCRIPTIVE'


def economy_metrics(rows):
    removals = [dict(start=r['start'],keyset=r['keyset'],**e)
                for r in rows for e in r['telemetry']['economy_removals']]
    checks = [dict(start=r['start'],keyset=r['keyset'],**e)
              for r in rows for e in r['telemetry']['prospective_checks']]
    trials = [dict(start=r['start'],keyset=r['keyset'],**e)
              for r in rows for e in r['telemetry']['prospective_trials']]
    triggered = [e for e in checks if e['triggered']]
    count = sum(e['trials'] for e in triggered)
    failures = sum(e['failures'] for e in triggered)
    if count != len(trials) or failures != sum(not e['passed'] for e in trials):
        raise ValueError('prospective trial denominators disagree')
    series=[];means=[];first=[]
    for r in rows:
        points=r['telemetry']['mass_samples']
        # Fixed 5s post-boundary samples match the historical diagnostic. Keep
        # t0 separately, never dilute the equal-weight 160-snapshot comparison.
        samples=[x for x in points if x['t']>0 and x['t']%5==0]
        if [x['t'] for x in samples] != list(range(5,801,5)):
            raise ValueError('mass sample timeline incomplete')
        for x in points:
            if abs(sum(y['cost'] for y in x['classes'].values())-x['cost'])>1e-9:
                raise ValueError('class allocation does not conserve')
        series.append(dict(start=r['start'],keyset=r['keyset'],samples=points))
        means.append({c:{field:sum(x['classes'][c][field] for x in samples)/len(samples)
                         for field in ('elements','pair_cost','cost')} for c in CLASSES})
        refusals=r['telemetry']['initial_cost_refusals']
        first.append(dict(start=r['start'],keyset=r['keyset'],
                          refusal=refusals[0] if refusals else None))
    return dict(removal_counts=dict(Counter(e['rule'] for e in removals)),removals=removals,
                no_front=[dict(start=r['start'],keyset=r['keyset'],**e) for r in rows for e in r['telemetry']['no_front']],
                mass_series_per_run=series,
                mean_sample_allocation={c:{field:sum(m[c][field] for m in means)/len(means)
                    for field in ('elements','pair_cost','cost')} for c in CLASSES} if means else {},
                first_candidate_cost_refusal_per_run=first,
                stall_samples_per_run=[dict(start=r['start'],keyset=r['keyset'],samples=r['telemetry']['stall_samples']) for r in rows],
                prospective=dict(all_checks=len(checks),triggered_checks=len(triggered),
                    trials=count,failures=failures,failure_fraction=failures/count if count else None,
                    no_candidate_checks=sum(e['result']=='no_candidate' for e in checks),
                    no_passing_candidate_checks=sum(e['result']=='no_passing_candidate' for e in checks),
                    below_trigger_checks=sum(e['result']=='below_trigger' for e in checks),
                    elapsed_seconds=sum(e['prospective_elapsed_seconds'] for e in checks),
                    cpu_seconds=sum(e['prospective_cpu_seconds'] for e in checks),checks=checks,trial_records=trials))


def main():
    path=OUT/'ECONOMY_RUN_SUMMARIES.json'
    receipt=json.loads(path.read_text()) if path.exists() else dict(status='NOT_RUN',runs=[],integrity={})
    rows=[];errors=[];checks=dict.fromkeys(ARMS,'NOT_RUN')
    artifacts=LOCAL.exists() and any(LOCAL.glob('*'))
    arm_errors={v:[] for v in ARMS}
    common_errors=[]
    if receipt.get('runs') or artifacts:
        baseline=None
        try: baseline=code_hashes()
        except Exception as error: common_errors.append(str(error))
        if baseline is not None:
            supplied={(r['variant'],r['start'],r['keyset'],r['observer']):r for r in receipt['runs']}
            if len(supplied)!=len(receipt['runs']): common_errors.append('duplicate scheduler jobs')
            if any(j not in JOBS for j in supplied): common_errors.append('unexpected scheduler job')
            for job in JOBS:
                try:
                    row=load_completed(job,baseline)
                    if row is not None:
                        if supplied.get(job)!=row:
                            arm_errors[job[0]].append('scheduler receipt differs from local completion: '+str(job))
                        rows.append(row)
                    elif job in supplied:
                        raise ValueError('receipt completion missing locally: '+str(job))
                except Exception as error: arm_errors[job[0]].append(str(error))
            checks=integrity(rows)
    control_rows=[r for r in json.loads((OUT/'SERVICE_RUN_SUMMARIES.json').read_text())['runs'] if r['variant']=='RD3']
    control=aggregate(copy.deepcopy(control_rows),legacy=True)
    if control['status']!='DONE' or control['pooled_3_6']!=RD3_POOL:
        common_errors.append('RD3 control does not match declared baseline')
    coverage=json.loads((OUT/'COVERAGE_COMPACT_SUMMARIES.json').read_text())
    mass=json.loads((OUT/'MASS_BUDGET_DIAGNOSTIC.json').read_text())
    context={v:copy.deepcopy(coverage['arms'][v]) for v in ('COVA','COVB')}
    historical_mass={v:[r for r in mass['runs'] if r['variant']==v] for v in ('RD3','COVA','COVB')}
    arms={}
    for variant in ARMS:
        selected=[r for r in rows if r['variant']==variant and r['observer']=='on']
        arm=aggregate(copy.deepcopy(selected))
        arm['label_revision']='AMENDMENT_1_ECONOMY'
        try: arm.update(economy_metrics(selected))
        except Exception as error:
            arm_errors[variant].append(str(error));arm['status']='INCOMPLETE'
        arms[variant]=arm
    for variant,arm in arms.items():
        arm['reading']=reading(arm,checks[variant]=='PASS' and not common_errors and not arm_errors[variant])
    errors=common_errors+[v+': '+e for v,items in arm_errors.items() for e in items]
    status='DONE' if all(a['reading']!='INCOMPLETE' for a in arms.values()) and not errors else 'PARTIAL' if rows or artifacts or receipt.get('status')=='PARTIAL' else 'NOT_RUN'
    sources={n:sha(OUT/n) for n in ('SERVICE_RUN_SUMMARIES.json','COVERAGE_COMPACT_SUMMARIES.json','MASS_BUDGET_DIAGNOSTIC.json','ECONOMY_PILOT_SPEC.md')}
    compact=dict(status=status,kind='EXPLORATORY_NO_VERDICT',arms=arms,control=control,
                 coverage_context=context,historical_mass_context=historical_mass,
                 integrity=checks,verification_errors=errors,common_errors=common_errors,arm_errors=arm_errors,source_sha256=sources,
                 threshold=TARGET,timing=receipt.get('timing'),raw_inventory=receipt.get('raw_inventory',[]),
                 fresh_section_19_7_keys_touched=False)
    (OUT/'ECONOMY_COMPACT_SUMMARIES.json').write_text(json.dumps(compact,separators=(',',':'),allow_nan=False)+'\n')
    lines=[status,'','Amendment-1 exploratory ECOF/ECOR × starts i/ii × keys0–4;20 on runs plus two off controls. No scientific verdict or A7 authorization.',
           '',f'Integrity: {checks}. Verification errors: {errors}.',
           '',f'Exact declared RD3 pooled sites3–6 baseline: {RD3_POOL}; doubling target: {TARGET}.',
           '', '| Arm | Status | Empty passes/runs | Seeded passes/runs | Pooled sites3–6 | Reading |',
           '|---|---|---|---|---|---|']
    for v,a in [('RD3',control),*context.items(),*arms.items()]:
        lines.append(f"| {v} | {a['status']} | {a['gate_shape']['i']} | {a['gate_shape']['ii']} | {a['pooled_3_6']} | {a.get('reading','CONTROL')} |")
    lines+=['','Pooling sums active_served_steps / active_steps over sites3–6 and all ten on runs. Coverage improves requires the exact doubling target, >=4/5 empty passes, all ten runs and that arm’s on/off summary+trajectory identity and clone isolation. Regression requires <=3/5 empty passes with the same completeness/integrity gates. Missing runs never count as failures.',
            '', '| Arm/site | Pooled active served fraction |', '|---|---|']
    for v,a in [('RD3',control),*context.items(),*arms.items()]:
        for site in range(8):lines.append(f"| {v}/{site} | {a['sites'].get(str(site),{}).get('fraction','NOT_RUN')} |")
    lines+=['','Per-run gate shape (A>=.3, B>=.3, max(E)>=.5); empty and seeded are separate:',
            '', '| Arm/start/key | A | B | E | Pass |','|---|---|---|---|---|']
    for v,a in [('RD3',control),*context.items(),*arms.items()]:
        for r in a['runs']:
            lines.append(f"| {v}/{r['start']}/{r['keyset']} | {r['assay']['A']} | {r['assay']['B']} | {r['assay']['E']} | {r['gate_shape_pass']} |")
    lines+=['','Class allocation at fixed5s post-boundary snapshots (equal weights across complete runs):',
            '', '| Arm/class | Mean bodies | Mean pair cost | Mean total cost |','|---|---|---|---|']
    for v in ('RD3','COVA','COVB',*ARMS):
        means=arms[v].get('mean_sample_allocation',{}) if v in arms else {
            c:{f:sum(r['mean_sample_allocation'][c][f] for r in historical_mass[v])/len(historical_mass[v])
               for f in ('elements','pair_cost','cost')} for c in CLASSES} if historical_mass[v] else {}
        for c in CLASSES:
            x=means.get(c,{})
            lines.append(f"| {v}/{c} | {x.get('elements','NOT_RUN')} | {x.get('pair_cost','NOT_RUN')} | {x.get('cost','NOT_RUN')} |")
    lines+=['','Allocation is ordinary N+.1 per ordinary undirected held pair, split .05 per endpoint. O and incident pairs are exempt. All-site effective-root classification separates critical, redundant, forward-reachable fronts and root-unreachable orphans; idle sites count. Cost allocations conserve, but are not marginal deletion savings. JSON contains each time series (t0 separately), all eight per-run fractions and both starts.',
            '', '| Arm | D5 removals | Triggered checks | Trials / failures | No candidates / no passing | Prospective wall / CPU seconds |',
            '|---|---|---|---|---|---|']
    for v,a in arms.items():
        p=a.get('prospective',{})
        lines.append(f"| {v} | {a.get('removal_counts',{})} | {p.get('triggered_checks','NOT_RUN')} | {p.get('trials','NOT_RUN')} / {p.get('failures','NOT_RUN')} | {p.get('no_candidate_checks','NOT_RUN')} / {p.get('no_passing_candidate_checks','NOT_RUN')} | {p.get('elapsed_seconds','NOT_RUN')} / {p.get('cpu_seconds','NOT_RUN')} |")
    lines+=['','Prospective failure fraction uses candidate trials as denominator; check-level no-candidate/no-passing/below-trigger counts are separate. Time is the pure prospective graph rebuild, not total observer/worker overhead. D5f_none and removal site/class/age/lock/tip are in JSON. Reserve56 is a trigger only; one removal need not restore cost<=56.',
            '', '| Arm/start/key | First actual candidate cost refusal t | Current cost | Candidate insertion cost |',
            '|---|---|---|---|']
    for v,a in arms.items():
        for r in a.get('first_candidate_cost_refusal_per_run',[]):
            x=r['refusal'] or {}
            lines.append(f"| {v}/{r['start']}/{r['keyset']} | {x.get('t','NONE')} | {x.get('cost','NONE')} | {x.get('candidate_cost','NONE')} |")
    lines+=['','The first-refusal table records actual feasible-candidate admission time and current/prospective cost, before later removals/births. Propagated resource stops are not new candidate measurements. Historical first-refusal boundaries are sampled in COVERAGE_DIAGNOSTIC; historical mass-series cost is sampled, so it cannot substitute for an exact first-candidate cost. Context samples remain labelled historical.',
            '', '| Arm | Break labels | Non-repair labels |','|---|---|---|']
    for v,a in [('RD3',control),*context.items(),*arms.items()]:
        lines.append(f"| {v} | {a.get('break_causes',{})} | {a.get('non_repair_causes',{})} |")
    lines+=['','Revised B records post-birth gaps for pre-transition open outages, excluding restoring terminals and restoring gaps from non-repair evidence; restoration samples remain with zero duration weight. New outages inherit no earlier birth. RD3 retains legacy_B, separately from revised B. C and B are global observations, N names the site; D5 attribution includes loss after neighbor/degree rewiring and is observed removal context, not causal proof. Full outages retain break candidates and restoration evidence in JSON.',
            '', 'ECOF deficit/stall histories are kernel-owned, clone-copied and growth-end only; finite-current guard implements newly gained roots and infinity pauses. D5f follows D1/D4 before D3; its reset can become20 at the same check’s end if still stalled. ECOR follows D3 before births and vetoes candidates using a pure all-site graph rebuild. Output-first, pointer, quotas and RD3 remain inherited; neither economy arm includes coverage ordering or recycle.',
            '', f'Scheduler cap{CAP}s, <=10 workers, conservative remaining-job projection includes both off controls. Verified completed slots are reused; any started/incomplete slot is never rerun. Process-access failure stops execution. Caffeinate surrounds execution; each worker shares the deadline. Every attempt retains its ticket and timing: '+json.dumps({k:v for k,v in receipt.get('timing',{}).items() if k in ('status','stop_reason','elapsed_seconds','awake_seconds','projection_seconds','workers','reused','completion_errors')},separators=(',',':')),
            '', 'Historical conservative projection is3987.979s at10 workers, above the fixed cap. A new full schedule must stop before launch until Claude resolves the owner’s runtime decision; code never raises the cap. This report never executes pilots. No native trajectory identity is claimed until Claude’s full on/off pairs complete.',
            '', 'Commands: ECONOMY_USAGE.md. Raw files remain in _local/economy with size/SHA256; source/build/dependency pins exclude PLAN_CURRENT.md, DESIGN_0G.md and DESIGN_0H_REV7.md. Existing SCR/V1/RD3 and coverage summaries/receipts are unchanged. Recheck tracking is in docs/reviews/tactical_0h_economy_implementation_recheck_codex.md, under the owner’s prohibition on editing PLAN_CURRENT.md.']
    (OUT/'ECONOMY_PILOT_REPORT.md').write_text('\n'.join(lines)+'\n')
    return 2 if errors else 0


if __name__=='__main__': raise SystemExit(main())
