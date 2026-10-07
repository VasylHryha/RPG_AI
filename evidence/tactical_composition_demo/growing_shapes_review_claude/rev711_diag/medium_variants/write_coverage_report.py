"""Render coverage pilots from verified completions; never execute a medium."""
from collections import Counter
import json
from pathlib import Path
from execute_coverage_plan import OUT, LOCAL, ARMS, JOBS, load_completed, code_hashes, integrity, sha


def passes(row):
    assay=row['summary']['assay']
    return assay['A']>=.3 and assay['B']>=.3 and max(assay['E'])>=.5


def aggregate(runs, legacy=False):
    if not runs:
        return dict(status='NOT_RUN',runs=[],pooled_3_6=None,sites={},gate_shape={s:dict(passes=0,runs=0) for s in ('i','ii')})
    sites={}
    for s in range(8):
        active=sum(r['telemetry']['sites'][str(s)]['active_steps'] for r in runs)
        served=sum(r['telemetry']['sites'][str(s)]['active_served_steps'] for r in runs)
        sites[str(s)]=dict(active_steps=active,active_served_steps=served,fraction=served/active if active else None,
            per_run=[dict(start=r['start'],keyset=r['keyset'],fraction=r['telemetry']['sites'][str(s)]['served_fraction_active']) for r in runs])
    active=sum(sites[str(s)]['active_steps'] for s in range(3,7))
    served=sum(sites[str(s)]['active_served_steps'] for s in range(3,7))
    counts={s:dict(passes=sum(passes(r) for r in runs if r['start']==s),runs=sum(r['start']==s for r in runs)) for s in ('i','ii')}
    result=dict(status='DONE' if len(runs)==10 else 'INCOMPLETE',sites=sites,pooled_3_6=served/active if active else None,
                pooled_3_6_active_steps=active,pooled_3_6_served_steps=served,gate_shape=counts,
                runs=[dict(start=r['start'],keyset=r['keyset'],assay=r['summary']['assay'],gate_shape_pass=passes(r),
                           sites_served_at_least_50_percent=sum((r['telemetry']['sites'][str(s)]['served_fraction_active'] or 0)>=.5 for s in range(8))) for r in runs])
    def totals(field):
        c=Counter()
        for r in runs:c.update(r['telemetry'][field])
        return dict(c)
    result.update(outage_count=sum(r['telemetry']['outage_count'] for r in runs),
                  break_causes=totals('break_causes'),d3_removals_by_class=totals('d3_removals_by_class'),
                  forced_cuts=[dict(start=r['start'],keyset=r['keyset'],event=e) for r in runs for e in r['telemetry']['forced_service_cuts']],
                  outages=[dict(start=r['start'],keyset=r['keyset'],outage=o) for r in runs for o in r['telemetry']['outages']])
    labels=totals('non_repair_causes')
    if legacy:
        # Stored traces omit per-birth service/gaps for the formerly closed
        # outage. They cannot establish every revised boundary fact. Retain
        # ALL historical B as legacy_B; no partial filter masquerades as revision.
        labels['legacy_B']=labels.pop('B',0)
        result['label_revision']='LEGACY_B_UNRECONSTRUCTABLE'
        result['reconstruction_limit']='Retained world/growth samples cannot recover every intermediate birth boundary; RD3 B is separate legacy_B. Coverage and assay reused unchanged.'
    else:result['label_revision']='AMENDMENT_1'
    result['non_repair_causes']=labels
    # Avoid mixing per-outage historical B with revised B in downstream readers.
    if legacy:
        for item in result['outages']:
            o=item['outage']
            o['non_repair_labels']=['legacy_B' if x=='B' else x for x in o['non_repair_labels']]
            o['non_repair_first_times']={'legacy_B' if k=='B' else k:v for k,v in o['non_repair_first_times'].items()}
            if o['primary_non_repair']=='B':o['primary_non_repair']='legacy_B'
            o['primary_tie_labels']=['legacy_B' if x=='B' else x for x in o.get('primary_tie_labels',[])]
    return result


def reading(arm, control, verified):
    if arm['status']!='DONE' or not verified:return 'INCOMPLETE'
    if arm['gate_shape']['i']['passes']<=3:return 'REGRESSION'
    if control['status']=='DONE' and control['pooled_3_6'] is not None and arm['pooled_3_6'] is not None and arm['pooled_3_6']>=2*control['pooled_3_6'] and arm['gate_shape']['i']['passes']>=4:
        return 'COVERAGE_IMPROVES'
    return 'DESCRIPTIVE'


def birth_metrics(telemetry):
    counts={str(s):Counter() for s in range(8)};births=Counter();cost=[]
    cost += [r['t'] for r in telemetry.get('initial_cost_refusals',[])]
    for terminal in telemetry['terminals']:
        site=terminal.get('site')
        if site is not None:
            counts[str(site)][terminal['outcome']]+=1
            if terminal['outcome']=='accepted':births[str(site)]+=1
        if terminal['outcome']=='cost' or terminal.get('initial_cost_refusal'):cost.append(terminal['t'])
    return dict(births_per_site={str(s):births[str(s)] for s in range(8)},
                request_outcomes_per_site={s:{k:c[k] for k in ('quota','cost','accepted','no_root','deferred_output_first','recycle_failed','cap','placement','exhausted','no_output')} for s,c in counts.items()},
                first_cost_refusal_t=min(cost,default=None),initial_cost_refusals=telemetry.get('initial_cost_refusals',[]),recycles=telemetry['recycles'])


def main():
    receipt_path=OUT/'COVERAGE_RUN_SUMMARIES.json'
    receipt=json.loads(receipt_path.read_text()) if receipt_path.exists() else dict(status='NOT_RUN',runs=[],integrity={})
    errors=[];rows=[];checks=dict.fromkeys(ARMS,'NOT_RUN')
    if receipt.get('runs'):
        baseline=None
        try: baseline=code_hashes()
        except Exception as error:errors.append(str(error))
        if baseline is not None:
            supplied={(r['variant'],r['start'],r['keyset'],r['observer']):r for r in receipt['runs']}
            if len(supplied)!=len(receipt['runs']):errors.append('duplicate scheduler receipt jobs')
            for job in JOBS:
                try:
                    r=load_completed(job,baseline)
                    if r is not None:
                        if supplied.get(job)!=r:raise RuntimeError('scheduler receipt differs from local completion: '+str(job))
                        rows.append(r)
                    elif job in supplied:raise RuntimeError('receipt completion missing locally: '+str(job))
                except Exception as error:errors.append(str(error))
            if any(job not in JOBS for job in supplied):errors.append('unexpected job in scheduler receipt')
            checks=integrity(rows)
    control_receipt=json.loads((OUT/'SERVICE_RUN_SUMMARIES.json').read_text())
    # Pure parsing/mapping; neither the historical receipt nor its summaries are written.
    control_rows=[r for r in control_receipt['runs'] if r['variant']=='RD3']
    control=aggregate(control_rows,legacy=True)
    diagnostic=json.loads((OUT/'COVERAGE_DIAGNOSTIC.json').read_text())
    control['births_per_run']=[]
    for d in diagnostic['runs']:
        if d['variant']!='RD3':continue
        terminals=[t for site in d['sites'].values() for t in site['birth_terminals']]
        control['births_per_run'].append(dict(start=d['start'],keyset=d['keyset'],
            **birth_metrics(dict(terminals=terminals,recycles=[]))))
    control['birth_metrics_source']='Committed COVERAGE_DIAGNOSTIC.json site-named retained terminals; no medium run'
    control['diagnostic_sha256']=sha(OUT/'COVERAGE_DIAGNOSTIC.json')
    variants={}
    for v in ARMS:
        selected=[r for r in rows if r['variant']==v and r['observer']=='on']
        arm=aggregate(selected)
        arm['reading']=reading(arm,control,checks[v]=='PASS')
        arm['births_per_run']=[dict(start=r['start'],keyset=r['keyset'],**birth_metrics(r['telemetry'])) for r in selected]
        if v=='COVB':
            recycles=[dict(start=r['start'],keyset=r['keyset'],**x) for r in selected for x in r['telemetry']['recycles']]
            arm.update(recycle_count=len(recycles),recycled_classes=dict(Counter(x['donor_class'] for x in recycles)),recycles=recycles)
        variants[v]=arm
    status='DONE' if all(x['reading']!='INCOMPLETE' and x['status']=='DONE' for x in variants.values()) and not errors else 'PARTIAL' if rows or receipt.get('status')=='PARTIAL' else 'NOT_RUN'
    compact=dict(status=status,kind='EXPLORATORY_NO_VERDICT',arms=variants,control=control,integrity=checks,
                 verification_errors=errors,timing=receipt.get('timing'),raw_inventory=receipt.get('raw_inventory',[]),
                 control_receipt_sha256=sha(OUT/'SERVICE_RUN_SUMMARIES.json'),fresh_section_19_7_keys_touched=False)
    (OUT/'COVERAGE_COMPACT_SUMMARIES.json').write_text(json.dumps(compact,separators=(',',':'),allow_nan=False)+'\n')
    lines=[status,'','Amendment-1 exploratory coverage pilots, COVA/COVB × starts i/ii × keys 0–4; two off controls. No verdict or A7 authorization.',
           '',f'Observer integrity: {checks}. Verification errors: {errors}.',
           '',f"RD3 control: {control['gate_shape']}; pooled active-time coverage at sites 3–6: {control['pooled_3_6']}. Existing coverage and A/B/E reused unchanged.",
           '', 'RD3 B is legacy_B: retained traces do not establish every per-birth post-transition gap. Historical totals are never mixed with revised B. Other labels retain their original scopes. C/B are global observations, N names the site; these are not causal identifications.',
           '', '| Arm | Status | Empty passes/runs | Seeded passes/runs | Pooled sites 3–6 | Reading |', '|---|---|---|---|---|---|']
    for v,a in variants.items():lines.append(f"| {v} | {a['status']} | {a['gate_shape']['i']} | {a['gate_shape']['ii']} | {a['pooled_3_6']} | {a['reading']} |")
    lines+=['','Pooled fraction = sum(active_served_steps)/sum(active_steps), sites 3–6 and ten on runs. Positive requires doubling RD3 and at least four of five empty passes. Regression is at most three empty passes. Missing trajectories or a missing integrity pair make the arm incomplete, never a failure/positive.',
            '', '| Arm/site | Pooled active served fraction |', '|---|---|']
    for v,a in [('RD3',control),*variants.items()]:
        for s in range(8):lines.append(f"| {v}/{s} | {a['sites'].get(str(s),{}).get('fraction','NOT_RUN')} |")
    lines+=['','COVERAGE_COMPACT_SUMMARIES.json includes all eight per-site/per-run fractions, per-run sites at >=50%, A/B/E, site births and request outcomes, first cost refusal, outages and break/non-repair causes, D3 classes and forced cuts. COVB additionally gives donor class/lock/age, retry outcomes and served-within-60s YES/NO/CENSORED; removal persists on failure.',
            '', 'Initial candidate cost refusals are reported separately; C retains terminal cost-refusal evidence and does not acquire an initial refusal whose retry succeeds. A cost-refused candidate before recycling is logged separately from its single final terminal. recycle_failed does not propagate a cost resource-stop under the unchanged dispatcher. B1 rechecks original clearance/count/cost only. Revised B excludes the repairing terminal and its restoring gap sample; restoration evidence has zero duration weight.',
            '', 'COVA clocks are kernel-owned and clone-copied, sampled at the completed integrate boundary before adapt/timers/growth; no intra-check update. The observer remains external to clone state. Full on/off trajectory digest plus legacy summary identity is required for each arm in the main phase.',
            '', 'Scheduler cap 3600s, <=10 workers, all remaining jobs/off controls included in projection using maximum measured elapsed/CPU duration. Resume reuses identity-verified completed jobs and forbids started/incomplete reruns. Process-list errors stop execution. Caffeinate surrounds actual execution. Timing: '+json.dumps(receipt.get('timing',{}),separators=(',',':')),
            '', 'This report does not execute a pilot. Raw traces stay under _local/coverage and are pinned by size/SHA256. USAGE commands: COVERAGE_USAGE.md. Recheck tracking: docs/reviews/tactical_0h_coverage_implementation_recheck_codex.md; PLAN_CURRENT.md remains unchanged.']
    (OUT/'COVERAGE_PILOT_REPORT.md').write_text('\n'.join(lines)+'\n')
    return 2 if errors else 0


if __name__=='__main__':raise SystemExit(main())
