"""Render compact exploratory summaries with explicit missing-data status."""
from collections import Counter
import json
from pathlib import Path
import subprocess

OUT=Path(__file__).resolve().parent


def passes(row):
    a=row['summary']['assay'];return a['A']>=.3 and a['B']>=.3 and max(a['E'])>=.5


def main():
    receipt_path=OUT/'SERVICE_RUN_SUMMARIES.json'
    receipt=json.loads(receipt_path.read_text()) if receipt_path.exists() else dict(status='NOT_RUN',runs=[],integrity={})
    valid=all(receipt['integrity'].get(k)=='PASS' for k in ('observer_on_off','clone_isolation','scr_v1_reproduction'))
    rows=receipt['runs'] if valid else []
    preflight=json.loads((OUT/'SERVICE_PREFLIGHT.json').read_text())
    summaries={};failures=[]
    for variant in ('SCR','V1','RD3'):
        runs=[r for r in rows if r['variant']==variant]
        if not runs:
            summaries[variant]=dict(status='NOT_RUN',gate_shape=None,served_fraction_per_site=None,coverage=None,
                                    outages=None,repair_latencies=None,break_causes=None,non_repair_causes=None,
                                    d3_removals_by_class=None,forced_cuts=None,protected_fraction=None,
                                    realized_degree_above_2=None,empty_entry_filter=None)
            continue
        counts={s:dict(passes=sum(passes(r) for r in runs if r['start']==s),runs=sum(r['start']==s for r in runs)) for s in ('i','ii')}
        sites={s:dict(active_steps=sum(r['telemetry']['sites'][str(s)]['active_steps'] for r in runs),
                      active_served_steps=sum(r['telemetry']['sites'][str(s)]['active_served_steps'] for r in runs),
                      per_run_fraction=[r['telemetry']['sites'][str(s)]['served_fraction_active'] for r in runs],
                      per_run_all_fraction=[r['telemetry']['sites'][str(s)]['served_fraction_all'] for r in runs]) for s in range(8)}
        for site in sites.values(): site['served_fraction_active']=site['active_served_steps']/site['active_steps'] if site['active_steps'] else None
        def table(field):
            result=Counter()
            for r in runs: result.update(r['telemetry'][field])
            return dict(result)
        decisions=[d for r in runs for d in r['telemetry']['protected_population']]
        summaries[variant]=dict(status='DONE' if len(runs)==10 else 'PARTIAL',gate_shape=counts,sites=sites,
            coverage=dict(ever_served_sites=sum(any(r['telemetry']['sites'][str(s)]['ever_served'] for r in runs) for s in range(8)),
                          mostly_served='Fractions listed directly; no new mostly-served cutoff.'),
            outage_count=sum(r['telemetry']['outage_count'] for r in runs),
            maximum_outage=max(r['telemetry']['maximum_outage'] for r in runs),
            repair_latencies=[x for r in runs for x in r['telemetry']['repair_latencies']],
            censored_latencies=[x for r in runs for x in r['telemetry']['latency_censored']],
            break_causes=table('break_causes'),non_repair_causes=table('non_repair_causes'),
            d3_removals_by_class=table('d3_removals_by_class'),
            forced_cuts=[dict(start=r['start'],keyset=r['keyset'],event=e) for r in runs for e in r['telemetry']['forced_service_cuts']],
            protected_over_budget=sum(r['telemetry']['protected_over_budget'] for r in runs),
            protected_fraction=[d['protected_fraction'] for d in decisions],
            realized_degree_distribution=table('realized_degree_distribution'),
            realized_degree_above_2_per_run=[r['telemetry']['realized_degree_above_2'] for r in runs],
            empty_entry_filter='MEETS_EXPLORATORY_FILTER' if counts['i']==dict(passes=5,runs=5) else 'DOES_NOT_MEET_OR_INCOMPLETE')
        for r in runs:
            if passes(r):continue
            # Longest outage is a descriptive failure-associated outage. It is
            # not proof that this outage caused the separate F5 gate-shape failure.
            outages=r['telemetry']['outages'];longest=max(outages,key=lambda o:o['duration'],default=None)
            failures.append(dict(variant=variant,start=r['start'],keyset=r['keyset'],assay=r['summary']['assay'],
                longest_outage=longest,
                primary_break=longest['break_cause'] if longest else 'X',
                primary_non_repair=longest['primary_non_repair'] if longest and longest['primary_non_repair'] else 'NOT_APPLICABLE',
                causality='Associated longest outage, not identified cause of F5 failure; inspect every outage in per-run JSON.'))
    compare=dict(status='NOT_RUN')
    if summaries['V1']['status']=='DONE' and summaries['RD3']['status']=='DONE':
        compare=dict(status='DESCRIPTIVE',coverage_v1=summaries['V1']['coverage'],coverage_rd3=summaries['RD3']['coverage'],
                     per_site_fraction_difference={s:summaries['RD3']['sites'][s]['served_fraction_active']-summaries['V1']['sites'][s]['served_fraction_active'] for s in range(8)},
                     rd3_protected_over_budget=summaries['RD3']['protected_over_budget'],rd3_forced_cuts=len(summaries['RD3']['forced_cuts']),
                     deadlock_reading='Forced cuts are budget progress with service loss; protected_over_budget is blocked eligibility, not RD3 exemption.')
    compact=dict(status=receipt['status'],kind='EXPLORATORY_NO_VERDICT',integrity=receipt['integrity'],variants=summaries,
                 failures=failures,rd3_against_v1=compare,fresh_section_19_7_keys_touched=False,
                 preflight=preflight,raw_traces=receipt.get('raw_inventory',[x for r in receipt['runs'] for x in r['raw_traces']]))
    (OUT/'SERVICE_COMPACT_SUMMARIES.json').write_text(json.dumps(compact,separators=(',',':'),allow_nan=False)+'\n')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=OUT,text=True).strip()
    recheck=(OUT/'OWNER_RECHECK.md').read_text() if (OUT/'OWNER_RECHECK.md').exists() else 'Recheck pending.'
    lines=[receipt['status'],'',f'A6w/A6x exploratory scratch delivery, base workspace HEAD `{head}`. No verdict. Key sets 0–4 × starts i/ii only. Fresh section-19.7 keys never requested.',
           '',f"Pilot preflight: **{preflight['status']}**. "+('`pgrep` returned a process-list access error. No training or F5 assay ran; no awake/run time accrued. ' if preflight['status']=='PROCESS_ACCESS_BLOCKED' else 'See SERVICE_PREFLIGHT.json and run timing receipt. '),
           '', 'Builder: reviewed `fd21826` detached worktrees, exact traditional patches, original `build_rev7.py`, pinned source hashes and unchanged native law for V1/RD3. The historical Mach-O install name is a fixed string; the build needs no files in /private/tmp. All three binaries reproduced `b0b35a16ba134c57e56a44c9cb128b7a7ce2ae9cd4aaf836b8b1e82392c9578d`. V1 traditional Python diff exactly matched the committed diff. See kernel_builder/*_BUILD.json and HISTORICAL_SCREENING_IDENTITY.json.',
           '', 'Service geometry: all eight fixed sites from growing_shapes/medium/design_0h.py SITES; strict reach 3 from growing_shapes/runner/protocol.py bindings. The reviewed bindings already include idle sites; fallback before first integrate uses the same definitions. Strong edges come from strong_influence(); spring selection ties by native array order. Selected counts and realized degree are separate. RD3 alone ranks non-service, redundant, critical, then existing lock/id, recalculates after every deletion, and records forced_service_cut.',
           '', 'The observer has separate module-owned state and streams raw JSONL. It reads growth locks already measured by the kernel. It records pre/post removal, accepted births and complete world boundaries, preventing adaptation/root changes from being attributed to the next deletion. Every 50 steps it records figure geometry. Population protection uses all elements as denominator, with ordinary/eligible counts alongside it.',
           '', 'Integrity status:', '', '| Check | Status |','|---|---|']
    for key in ('observer_on_off','clone_isolation','scr_v1_reproduction'):
        lines.append(f"| {key} | {receipt['integrity'].get(key,'NOT_RUN')} |")
    lines+=['', 'The full 50-episode SCR empty-key-0 on/off comparison must pass before measurements are released. Clone isolation compares live native bytes and observer/digest sinks. All SCR/V1 assay and legacy summary fields must equal committed logs exactly before RD3 starts. Synthetic tests do not establish these run integrity checks.',
            '', '| Variant | Gate shape empty/seeded | Site fractions/coverage | Outages/latency/causes | D3 classes/forced cuts/protection | Realized degree >2 |','|---|---|---|---|---|---|']
    for variant, data in summaries.items():
        if data['status']=='NOT_RUN': lines.append(f'| {variant} | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN |')
        else: lines.append(f"| {variant} | {data['gate_shape']} | JSON fractions for 8 sites | {data['outage_count']} outages; JSON distributions | {data['d3_removals_by_class']}; {len(data['forced_cuts'])} forced cuts | JSON distribution |")
    lines+=['', 'Each failure: '+('NOT_RUN; no failure classifications inferred from the historical logs.' if not rows else 'See SERVICE_COMPACT_SUMMARIES.json failures and full per-run outages.'),
            '', 'RD3 against V1 coverage and budget: '+('NOT_RUN.' if compare['status']=='NOT_RUN' else json.dumps(compare)),
            '', 'Empty-start exploratory entry filter: '+('NOT_RUN for all variants. Historical V1 5/5 is not a telemetry reproduction result.' if not rows else 'See each variant’s empty_entry_filter. This is an exploratory filter, not a verdict.'),
            '', 'Interpretation limits: route reuse compares the deterministic shortest-route element set. G-dist/G-deg use held receiver degree and one-factor rate counterfactuals; multiple supported labels yield break X. A spring change alone cannot destroy strong reachability (R is retained in the schema, never invented). G cannot occur within a maximal site outage, because restoration closes the outage; adjacent outages remain separate. Non-repair labels are all applicable observations; the earliest is primary, simultaneous earliest labels produce X. Mostly-served coverage is given as the eight time fractions without adding a cutoff.',
            '', 'Compute: spec estimate 11 CPU-min/run; 31 runs including the required off control, at most 10 concurrent. Scheduler checks projection before every phase, uses the greater of measured elapsed and CPU time per job, with phase concurrency rounding and imposes a shared 3600-second deadline; caffeinate -i -s surrounds all runs. Telemetry overhead and shared-machine throughput remain unmeasured here. No claim that the complete plan fits the cap. Resume uses the script’s measured STOP checks, never tuning or retries.',
            '', 'Raw traces: no new pilot traces exist if NOT_RUN. Future traces remain gitignored under _local/, listed with bytes and SHA256. Build raw logs stay local by SHA256 in delivery metadata. All committed files must stay below 45 MB.',
            '', 'Reproduction and launch commands are in kernel_builder/USAGE.md. A6w implementation/build is available; A6w run integrity and A6x exploratory execution remain pending when NOT_RUN. Owner rechecks and disposition are recorded here instead of docs/PLAN_CURRENT.md because the owner prohibits changing that file.',
            '', recheck]
    (OUT/'SERVICE_TELEMETRY_REPORT.md').write_text('\n'.join(line.rstrip() for line in lines).rstrip()+'\n')


if __name__=='__main__':main()
