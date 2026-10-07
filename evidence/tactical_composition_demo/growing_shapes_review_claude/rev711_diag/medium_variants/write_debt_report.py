"""Verified stored DEBT report only; no medium or process listing is executed."""
import copy
import json
from pathlib import Path
from execute_debt_plan import OUT, LOCAL, JOBS, code_hashes, load_completed, integrity, sha
from write_coverage_report import aggregate, birth_metrics

TARGET = .17202754532775452


def minima(arm):
    fractions = [arm['sites'].get(str(s), {}).get('fraction') for s in range(8)]
    pooled = min(fractions) if all(x is not None for x in fractions) else None
    runs = []
    for row in arm.get('runs', []):
        values = []
        for site in range(8):
            values.append(next((r['fraction'] for r in arm['sites'][str(site)]['per_run']
                                if (r['start'], r['keyset']) == (row['start'], row['keyset'])), None))
        runs.append(dict(start=row['start'], keyset=row['keyset'],
                         minimum=min(values) if all(v is not None for v in values) else None))
    return dict(minimum_of_eight_pooled_site_fractions=pooled, per_run_minima=runs,
                minimum_over_all_site_run_fractions=min((r['minimum'] for r in runs), default=None)
                if all(r['minimum'] is not None for r in runs) else None)


def readings(arm, verified):
    if arm['status'] != 'DONE' or not verified:
        return dict(coverage='INCOMPLETE', fairness='INCOMPLETE')
    gates = arm['gate_shape']['i']['passes']
    coverage = ('REGRESSION' if gates <= 3 else 'COVERAGE_IMPROVES'
                if arm['pooled_3_6'] is not None and arm['pooled_3_6'] >= TARGET else 'DESCRIPTIVE')
    return dict(coverage=coverage, fairness='DESCRIPTIVE_SCOPE_UNRESOLVED')


def debt_metrics(rows):
    checks = [dict(start=r['start'], keyset=r['keyset'], **c)
              for r in rows for c in r['telemetry']['order_checks']]
    eligible = [c for c in checks if c['order']]
    return dict(
        debt_boundary='completed integrate before adapt/timers/growth, active-unserved only',
        order_comparison_scope='initial check candidates on DEBT history, not counterfactual quota acceptances',
        checks=checks, eligible_checks=len(eligible), all_checks=len(checks),
        differences={field: sum(c[field] for c in eligible) for field in
                     ('differs_rd3', 'differs_cova', 'first_differs_rd3', 'first_differs_cova')},
        debt_trajectories=[dict(start=r['start'], keyset=r['keyset'],
                                samples=r['telemetry']['debt_samples'],
                                full_01s_samples_in_raw=True) for r in rows],
        mass_by_class=[dict(start=r['start'], keyset=r['keyset'],
                            samples=r['telemetry']['mass_samples']) for r in rows],
        births_and_refusals=[dict(start=r['start'], keyset=r['keyset'],
                                  **birth_metrics(r['telemetry'])) for r in rows])


def main():
    receipt_path = OUT / 'DEBT_RUN_SUMMARIES.json'
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else dict(status='NOT_RUN', runs=[])
    errors = []
    rows = []
    supplied = {(r['variant'], r['start'], r['keyset'], r['observer']): r for r in receipt['runs']}
    if len(supplied) != len(receipt['runs']):
        errors.append('duplicate scheduler jobs')
    if any(j not in JOBS for j in supplied):
        errors.append('unexpected scheduler jobs')
    baseline = None
    # Inspect even receipt-less crashes/slots; do not turn started work into NOT_RUN.
    has_local = LOCAL.exists() and any(LOCAL.iterdir())
    if supplied or has_local:
        try:
            baseline = code_hashes()
        except Exception as error:
            errors.append(str(error))
    if baseline is not None:
        for job in JOBS:
            try:
                row = load_completed(job, baseline, LOCAL)
                if row is None:
                    if job in supplied:
                        raise RuntimeError('receipt completion missing locally: ' + str(job))
                else:
                    rows.append(row)
                    if supplied.get(job) != row:
                        errors.append('scheduler receipt differs from verified completion: ' + str(job))
            except Exception as error:
                errors.append(str(error))
    checks = integrity(rows)
    verified = checks['DEBT'] == 'PASS' and not errors
    selected = [r for r in rows if r['observer'] == 'on']
    arm = aggregate(copy.deepcopy(selected))
    arm.update(**minima(arm), readings=readings(arm, verified), debt=debt_metrics(selected))
    controls = {}
    for name, filename in (('RD3', 'SERVICE_RUN_SUMMARIES.json'), ('COVA', 'COVERAGE_RUN_SUMMARIES.json')):
        source = json.loads((OUT / filename).read_text())
        stored = [r for r in source['runs'] if r['variant'] == name and r.get('observer', 'on') == 'on']
        controls[name] = aggregate(copy.deepcopy(stored), legacy=name == 'RD3')
        controls[name].update(**minima(controls[name]), source_sha256=sha(OUT / filename))
    status = ('DONE' if arm['status'] == 'DONE' and verified else
              'PARTIAL' if rows or has_local or errors or receipt.get('status') == 'PARTIAL' else 'NOT_RUN')
    compact = dict(status=status, kind='EXPLORATORY_NO_VERDICT', arm=arm, controls=controls,
                   integrity=checks, verification_errors=errors, timing=receipt.get('timing'),
                   raw_inventory=receipt.get('raw_inventory', []), fresh_section_19_7_keys_touched=False,
                   fairness_scope='Unresolved in specification; pooled and site/run minima both reported, no FAIRER_THAN_COVA label')
    (OUT / 'DEBT_COMPACT_SUMMARIES.json').write_text(json.dumps(compact, separators=(',', ':'), allow_nan=False) + '\n')
    lines = [status, '', 'Exploratory DEBT × starts i/ii × keys 0–4, plus one on/off pair in the main phase. No verdict or A7 authorization.',
             '', 'Integrity: ' + str(checks) + '. Verification errors: ' + str(errors) + '.',
             '', f"Empty gate: {arm['gate_shape']['i']}; seeded gate: {arm['gate_shape']['ii']}; pooled sites 3–6: {arm['pooled_3_6']}; readings: {arm['readings']}.",
             '', 'Coverage improves only at pooled 3–6 >= 0.17202754532775452, >=4/5 empty gates, all ten completions and a passing integrity pair. <=3/5 empty gates is regression only with complete verified evidence. Missing runs are INCOMPLETE, never failed gates.',
             '', 'The minimum of eight pooled site fractions and each run’s minimum have different denominators. Both are reported below. The spec does not choose between these for fairness, so FAIRER_THAN_COVA is withheld pending a drafter amendment.',
             '', '| Arm | Pooled site minimum | Minimum over site/run fractions |', '|---|---|---|']
    for name, data in [('DEBT', arm), *controls.items()]:
        lines.append(f"| {name} | {data['minimum_of_eight_pooled_site_fractions']} | {data['minimum_over_all_site_run_fractions']} |")
    lines += ['', '| Arm/site | Pooled active served fraction |', '|---|---|']
    for name, data in [('DEBT', arm), *controls.items()]:
        for s in range(8):
            lines.append(f"| {name}/{s} | {data['sites'].get(str(s), {}).get('fraction')} |")
    lines += ['', 'Per-run minima: ' + json.dumps({n: a['per_run_minima'] for n, a in [('DEBT', arm), *controls.items()]}),
              '', 'DEBT_COMPACT_SUMMARIES.json contains all eight site fractions/denominators per run, counts >=50%, A/B/E and both gate shapes, integrate debt trajectories (5s summary; every 0.1s retained in raw), class mass (5s), site quota/cost/acceptance outcomes and every initial order comparison.',
              '', 'Finite-first DEBT/RD3/COV-A orders and the diagnostic’s pure-debt order are distinct. Comparisons evaluate the DEBT graph and history; live path checks and intra-check births can change later opportunities. Historical integrated/lagged agreement does not predict prospective agreement. Observer service fractions are settled post-growth samples; kernel debt is pre-growth integrate debt.',
              '', 'The revised coverage observer excludes restoration terminals/gaps from B non-repair evidence. RD3 historical B is legacy_B. Existing control coverage/assays and summaries are parsed unchanged. Mass is current ordinary-body plus held-pair endpoint cost, with O free; it is not deletion savings.',
              '', 'Scheduling and the falsifier remain descriptive. Ordering differences or poor minima do not establish causal absence of a scheduling bottleneck. The unchanged live search, finite-first class, output-first repeat, two-birth quota, resource-stop, B1, D3 and budget still intervene.',
              '', 'Cap is read at each scheduler launch from _local/DEBT_CAP.json (default 5400s) and recorded in its ticket, outside completion identity. Resume checks code/build/raw identity and never reruns started slots. At most ten workers; process-access errors stop. Claude executes both commands in DEBT_USAGE.md; this writer executes no medium.',
              '', 'Timing: ' + json.dumps(receipt.get('timing'), separators=(',', ':'))]
    (OUT / 'DEBT_PILOT_REPORT.md').write_text('\n'.join(lines) + '\n')
    return 2 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
