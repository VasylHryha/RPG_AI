"""Stored-only capacity diagnostic; no medium execution or process listing."""
import json
from execute_capacity_plan import (OUT, LOCAL, ARMS, JOBS, code_hashes,
                                   load_completed, integrity, sha, validate_sites,
                                   check_frozen)
from write_coverage_report import passes, birth_metrics

POSITIVE_CUTOFF = 3.22  # Latest operative Amendment 2 literal; not exact 1.5*RD3.
SLOTS = {(s, k) for s in ('i', 'ii') for k in range(5)}


def pooled(rows):
    sites = {}
    for s in range(8):
        a = sum(r['telemetry']['sites'][str(s)]['active_steps'] for r in rows)
        b = sum(r['telemetry']['sites'][str(s)]['active_served_steps'] for r in rows)
        sites[str(s)] = dict(active_steps=a, active_served_steps=b,
                             fraction=b/a if a else None)
    fractions = [v['fraction'] for v in sites.values()]
    return dict(sites=sites, total_service=sum(fractions) if all(v is not None for v in fractions) else None,
                sites_at_least_30_percent=sum(v >= .30 for v in fractions if v is not None))


def aggregate(rows):
    slots = [(r['start'], r['keyset']) for r in rows]
    if len(set(slots)) != len(slots) or any(s not in SLOTS for s in slots):
        raise RuntimeError('duplicate/unexpected observer-on slots')
    for r in rows:
        validate_sites(r['telemetry']['sites'])
    data = pooled(rows)
    data.update(status='DONE' if set(slots) == SLOTS and data['total_service'] is not None else
                'INCOMPLETE' if rows else 'NOT_RUN',
                gate_shape={s: dict(passes=sum(passes(r) for r in rows if r['start'] == s),
                                    runs=sum(r['start'] == s for r in rows)) for s in ('i', 'ii')},
                by_start={s: pooled([r for r in rows if r['start'] == s]) for s in ('i', 'ii')},
                by_key={str(k): pooled([r for r in rows if r['keyset'] == k]) for k in range(5)},
                runs=[dict(start=r['start'], keyset=r['keyset'], **pooled([r]),
                           assay=r['summary']['assay'], gate_shape_pass=passes(r),
                           sites_served_at_least_50_percent=sum(
                               r['telemetry']['sites'][str(s)]['served_fraction_active'] is not None and
                               r['telemetry']['sites'][str(s)]['served_fraction_active'] >= .5 for s in range(8)))
                      for r in rows])
    return data


def reading(arms, control, verified):
    if not verified or control['status'] != 'DONE' or any(arms[v]['status'] != 'DONE' for v in ARMS):
        return 'INCOMPLETE'
    baseline, low, high = (control['total_service'], arms['CAP96']['total_service'],
                           arms['CAP128']['total_service'])
    return 'CAPACITY_SCALES_WITH_RESOURCE_CEILING' if high >= POSITIVE_CUTOFF and baseline <= low <= high else 'DESCRIPTIVE'


def main():
    path = OUT/'CAPACITY_RUN_SUMMARIES.json'
    receipt = json.loads(path.read_text()) if path.exists() else dict(status='NOT_RUN', runs=[])
    errors, rows = [], []
    supplied = {(r['variant'], r['start'], r['keyset'], r['observer']): r for r in receipt['runs']}
    if len(supplied) != len(receipt['runs']): errors.append('duplicate scheduler jobs')
    if any(j not in JOBS for j in supplied): errors.append('unexpected scheduler jobs')
    has_local = LOCAL.exists() and any(LOCAL.iterdir())
    baseline = None
    if supplied or has_local:
        try: baseline = code_hashes()
        except Exception as error: errors.append(str(error))
    if baseline is not None:
        for job in JOBS:
            try:
                row = load_completed(job, baseline, LOCAL)
                if row is None:
                    if job in supplied: raise RuntimeError('receipt completion missing locally: '+str(job))
                else:
                    rows.append(row)
                    if supplied.get(job) != row:
                        errors.append('scheduler receipt differs from verified completion: '+str(job))
            except Exception as error: errors.append(str(error))
        try: check_frozen(baseline)
        except Exception as error: errors.append(str(error))
    checks = integrity(rows)
    source = OUT/'SERVICE_RUN_SUMMARIES.json'
    stored = [r for r in json.loads(source.read_text())['runs']
              if r['variant'] == 'RD3' and r.get('observer', 'on') == 'on']
    control = aggregate(stored)
    control['source_sha256'] = sha(source)
    control['scope'] = 'Committed RD3 coverage/assays unchanged; no outage-label reinterpretation'
    arms = {}
    for v in ARMS:
        selected = [r for r in rows if r['variant'] == v and r['observer'] == 'on']
        arm = aggregate(selected)
        arm.update(cost_ceiling=int(v[3:]), count_ceiling=int(v[3:]),
                   capacity_trajectories=[dict(start=r['start'], keyset=r['keyset'],
                                               samples=r['telemetry']['capacity_samples']) for r in selected],
                   births_and_refusals=[dict(start=r['start'], keyset=r['keyset'],
                                             **birth_metrics(r['telemetry'])) for r in selected],
                   d3_removals=[dict(start=r['start'], keyset=r['keyset'],
                                     classes=r['telemetry']['d3_removals_by_class'],
                                     protected_population=r['telemetry']['protected_population'],
                                     forced_cuts=r['telemetry']['forced_service_cuts'],
                                     protected_over_budget=r['telemetry']['protected_over_budget']) for r in selected])
        arms[v] = arm
    label = reading(arms, control, checks == dict.fromkeys(ARMS, 'PASS') and not errors)
    status = 'DONE' if label != 'INCOMPLETE' else 'PARTIAL' if rows or has_local or errors or receipt['status'] == 'PARTIAL' else 'NOT_RUN'
    pairs = []
    for s, k in sorted(SLOTS):
        pair = dict(start=s, keyset=k, values={})
        for name, arm in [('RD3', control), *arms.items()]:
            pair['values'][name] = next((r['total_service'] for r in arm['runs'] if (r['start'], r['keyset']) == (s, k)), None)
        pair['differences_from_RD3'] = {v: pair['values'][v]-pair['values']['RD3']
                                       if pair['values'][v] is not None and pair['values']['RD3'] is not None else None for v in ARMS}
        pairs.append(pair)
    compact = dict(status=status, kind='EXPLORATORY_NO_VERDICT', reading=label, arms=arms,
                   control=control, paired_runs=pairs, integrity=checks, verification_errors=errors,
                   positive_cutoff=POSITIVE_CUTOFF, exact_1_5_times_control=1.5*control['total_service'] if control['total_service'] is not None else None,
                   timing=receipt.get('timing'), raw_inventory=[raw for r in rows for raw in r['raw_traces']],
                   fresh_section_19_7_keys_touched=False)
    (OUT/'CAPACITY_COMPACT_SUMMARIES.json').write_text(json.dumps(compact, separators=(',', ':'), allow_nan=False)+'\n')
    lines = [status, '', 'Exploratory capacity diagnostic, CAP96/CAP128 × keys 0–4 × both starts, plus one off control per arm. No verdict or A7 authorization.',
             '', f'Integrity: {checks}. Verification errors: {errors}. Reading: {label}.',
             '', 'Index = sum over eight sites of pooled active-served steps / pooled active steps, precisely ten observer-on runs per arm; off controls excluded. Dimensionless 0–8; equal site weights. This is not simultaneous service or delivered signal.',
             '', f"Latest Amendment 2 cutoff: {POSITIVE_CUTOFF}; RD3 index: {control['total_service']}; exact 1.5 × RD3: {compact['exact_1_5_times_control']}. The rounded literal cutoff is applied, with inclusive RD3 <= CAP96 <= CAP128. Both complete arms and both passing integrity pairs are required.",
             '', 'A positive reading describes this declared response on these exploratory keys. It establishes neither proportional scaling nor a general route-efficiency law. Every other complete result is descriptive; no conclusion about what binds follows from weak/null results. Missing evidence is INCOMPLETE.',
             '', '| Arm | Status | Total service | Sites >=30% | Empty gate | Seeded gate |', '|---|---|---|---|---|---|']
    for name, arm in [('RD3', control), *arms.items()]:
        lines.append(f"| {name} | {arm['status']} | {arm['total_service']} | {arm['sites_at_least_30_percent']} | {arm['gate_shape']['i']} | {arm['gate_shape']['ii']} |")
    lines += ['', '| Arm/site | Active steps | Active-served steps | Pooled fraction |', '|---|---|---|---|']
    for name, arm in [('RD3', control), *arms.items()]:
        for s, site in arm['sites'].items():
            lines.append(f"| {name}/{s} | {site['active_steps']} | {site['active_served_steps']} | {site['fraction']} |")
    lines += ['', 'CAPACITY_COMPACT_SUMMARIES.json includes per-run, start-specific and per-key pooled indices and paired differences, all eight site denominators, A/B/E gate shapes, class mass/cost/count/headroom, count/cost refusals, D3 decisions and forced cuts.',
              '', 'Raw capacity samples use every settled post-growth 0.1s boundary; compact trajectories sample each 5s through 800s. Structural and active simultaneous service counts are separate. Cost ratios divide by their named count; zero service gives null and an explicit flag while retaining cost. Class mass is ordinary bodies plus 0.1 per ordinary held pair, split 0.05 per endpoint; O and incident pairs are free. Material cost is not delivered signal or marginal deletion savings.',
              '', 'The revised coverage observer supplies per-birth restoration semantics unchanged; CAP D3 uses RD3 classification. RD3 summaries are parsed without modification or outage relabeling.',
              '', 'Claude runs the scheduler and this stored-only writer using CAPACITY_USAGE.md. At most ten workers; anchored process gate rejects process-access errors; resume checks code/build/raw identity and never reruns started/incomplete slots. Non-hashed _local/CAPACITY_CAP.json defaults to 5400s, read once at launch and recorded in the ticket. No design/plan Markdown or cap config is in completion identity.',
              '', 'Timing: '+json.dumps(receipt.get('timing'), separators=(',', ':'))]
    (OUT/'CAPACITY_DIAGNOSTIC_REPORT.md').write_text('\n'.join(lines)+'\n')
    return 2 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
