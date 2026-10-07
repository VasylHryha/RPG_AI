#!/usr/bin/env python3
"""Read-only stdlib audit of retained economy pilot. Never imports project code.

Writes only _local/economy/diagnostic_codex/PILOT_AUDIT.json. Hashes every
pinned raw/dependency before decoding traces. No native loading or simulation.
"""
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import time

OUT = Path(__file__).resolve().parent
LOCAL = OUT / '_local/economy'
DEST = LOCAL / 'diagnostic_codex/PILOT_AUDIT.json'
GRANT_FIELDS = ('status', 'started_epoch', 'deadline_epoch', 'code_hashes',
                'jobs', 'projection_seconds', 'workers', 'reused')
CLASSES = ('critical', 'redundant', 'front', 'orphan')


def check(ok, message):
    if not ok:
        raise AssertionError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def name(row):
    return f"{row['variant']}_{row['start']}_k{row['keyset']}_{row['observer']}"


def close(a, b):
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-10)


def passes(row):
    a = row['summary']['assay']
    return a['A'] >= .3 and a['B'] >= .3 and max(a['E']) >= .5


def total(rows, field):
    c = Counter()
    for r in rows:
        c.update(r['telemetry'][field])
    return dict(c)


def audit_compact(rows, arm):
    for site in range(8):
        active = sum(r['telemetry']['sites'][str(site)]['active_steps'] for r in rows)
        served = sum(r['telemetry']['sites'][str(site)]['active_served_steps'] for r in rows)
        check(arm['sites'][str(site)]['active_steps'] == active and
              arm['sites'][str(site)]['active_served_steps'] == served and
              arm['sites'][str(site)]['fraction'] == served / active, 'compact site totals')
    active = sum(arm['sites'][str(s)]['active_steps'] for s in range(3, 7))
    served = sum(arm['sites'][str(s)]['active_served_steps'] for s in range(3, 7))
    check(arm['pooled_3_6'] == served / active, 'compact pooled fraction')
    for start in ('i', 'ii'):
        rr = [r for r in rows if r['start'] == start]
        check(arm['gate_shape'][start] == dict(passes=sum(passes(r) for r in rr), runs=len(rr)), 'gate totals')
    for field in ('break_causes', 'non_repair_causes'):
        values = total(rows, field)
        if arm.get('label_revision') == 'LEGACY_B_UNRECONSTRUCTABLE' and field == 'non_repair_causes':
            values['legacy_B'] = values.pop('B', 0)
        check(arm[field] == values, 'outage label totals')
    return dict(runs=len(rows), pooled_served=served, pooled_active=active,
                pooled_fraction=served / active, gate_shape=arm['gate_shape'])


def audit_raw(row):
    records = defaultdict(list)
    rawpath = next(x['path'] for x in row['raw_traces'] if '.jsonl.' in x['path'])
    with gzip.open(OUT / rawpath, 'rt') as f:
        for line in f:
            x = json.loads(line)
            records[x['kind']].append(x)
    steps = records['world_step']
    check([x['step'] for x in steps] == list(range(1, 8001)), '8000 sequential steps')
    active, served, allserved = Counter(), Counter(), Counter()
    for x in steps:
        active.update(x['active']); served.update(x['active_served']); allserved.update(x['served'])
    telemetry = row['telemetry']
    for s in range(8):
        v = telemetry['sites'][str(s)]
        check(v['active_steps'] == active[s] and v['active_served_steps'] == served[s] and
              v['served_fraction_active'] == served[s] / active[s] and
              v['served_fraction_all'] == allserved[s] / 8000 and
              v['ever_served'] == bool(allserved[s]), 'raw site counts/fractions')
    for kind, field in (('removal', 'removals'), ('outage', 'outages'),
                        ('initial_cost_refusal', 'initial_cost_refusals')):
        check([{k: v for k, v in x.items() if k != 'kind'} for x in records[kind]] == telemetry[field],
              'raw ' + field)
    for rule, field in (('economy_stall', 'stall_samples'),
                        ('economy_prospective_trial', 'prospective_trials'),
                        ('economy_prospective_check', 'prospective_checks'), ('D5f_none', 'no_front')):
        xs = [{k: v for k, v in x.items() if k != 'kind'} for x in records['economy_event'] if x['rule'] == rule]
        check(xs == telemetry[field], 'raw ' + field)
    masses = {x['t']: {k: v for k, v in x.items() if k != 'kind'} for x in records['mass_allocation']}
    check([masses[t] for t in sorted(masses)] == telemetry['mass_samples'], 'raw mass series')
    for x in masses.values():
        check(close(sum(v['cost'] for v in x['classes'].values()), x['cost']), 'class conservation')
        check(close(x['ordinary'] + .1 * x['held_pairs'], x['cost']), 'N+.1pairs cost')
    check([x['t'] for x in records['growth_check']] == list(range(20, 801, 20)), '40 growth checks')
    legacy_path = next(x['path'] for x in row['raw_traces'] if '.legacy.' in x['path'])
    with gzip.open(OUT / legacy_path, 'rt') as f:
        legacy = json.load(f)
    check(legacy['assay'] == row['summary']['assay'], 'raw assay aggregate')
    check(len(legacy['steps']) == 8000, 'legacy trajectory length')
    clock_report = None
    if row['variant'] == 'ECOF':
        history = {s: (None, 0.) for s in range(8)}
        none = {(x['t'], x['site']) for x in telemetry['no_front']}
        rules = Counter()
        for x in telemetry['stall_samples']:
            previous, clock = history[x['site']]
            check(x['previous_deficit'] == previous, 'previous deficit continuity')
            if (x['t'], x['site']) in none:
                clock = 0.
            now = x['deficit']
            if x['served']:
                clock = 0.; rules['served'] += 1
            elif now is not None and previous is None:
                clock = 0.; rules['roots_newly_gained'] += 1
            elif now is not None and now < previous - 1e-9:
                clock = 0.; rules['progress_any_decrease'] += 1
            elif now is not None:
                clock += 20.; rules['stall'] += 1
            else:
                rules['no_roots_hold'] += 1
            check(clock == x['stall_seconds'], 'stall clock update')
            history[x['site']] = (now, clock)
        clock_report = dict(rules=dict(rules), end_threshold_records=sum(x['stall_seconds'] >= 60 for x in telemetry['stall_samples']),
                            final_threshold_records=sum(x['stall_seconds'] >= 60 and x['t'] == 800 for x in telemetry['stall_samples']),
                            no_donor_checks=len(none), no_donor_reasons=dict(Counter(x['reason'] for x in telemetry['no_front'])))
    return dict(slot=name(row), steps=8000, figures=len(records['figure']), clock=clock_report,
                assay='RAW_AGGREGATE_CONSISTENT_NOT_INDEPENDENTLY_RECONSTRUCTABLE')


def audit_tables(compact, report):
    # Compare every data row from all seven report tables against audited compact
    # fields and hash-verified contextual sources. Headers/prose are not data rows.
    expected = []
    arms = compact['arms']
    allarms = [('RD3', compact['control']), *compact['coverage_context'].items(), *arms.items()]
    for v, a in allarms:
        expected.append(f"| {v} | {a['status']} | {a['gate_shape']['i']} | {a['gate_shape']['ii']} | {a['pooled_3_6']} | {a.get('reading', 'CONTROL')} |")
    for v, a in allarms:
        for s in range(8):
            expected.append(f"| {v}/{s} | {a['sites'][str(s)]['fraction']} |")
    for v, a in allarms:
        for r in a['runs']:
            expected.append(f"| {v}/{r['start']}/{r['keyset']} | {r['assay']['A']} | {r['assay']['B']} | {r['assay']['E']} | {r['gate_shape_pass']} |")
    for v in ('RD3', 'COVA', 'COVB', 'ECOF', 'ECOR'):
        source = compact['historical_mass_context'].get(v)
        means = arms[v]['mean_sample_allocation'] if v in arms else {
            c: {field: sum(r['mean_sample_allocation'][c][field] for r in source) / len(source)
                for field in ('elements', 'pair_cost', 'cost')} for c in CLASSES}
        for c in CLASSES:
            x = means[c]
            expected.append(f"| {v}/{c} | {x['elements']} | {x['pair_cost']} | {x['cost']} |")
    for v, a in arms.items():
        x = a['prospective']
        expected.append(f"| {v} | {a['removal_counts']} | {x['triggered_checks']} | {x['trials']} / {x['failures']} | {x['no_candidate_checks']} / {x['no_passing_candidate_checks']} | {x['elapsed_seconds']} / {x['cpu_seconds']} |")
    for v, a in arms.items():
        for r in a['first_candidate_cost_refusal_per_run']:
            x = r['refusal'] or {}
            expected.append(f"| {v}/{r['start']}/{r['keyset']} | {x.get('t', 'NONE')} | {x.get('cost', 'NONE')} | {x.get('candidate_cost', 'NONE')} |")
    for v, a in allarms:
        expected.append(f"| {v} | {a['break_causes']} | {a['non_repair_causes']} |")
    actual = [line for line in report.splitlines() if re.match(r'^\| (RD3|COVA|COVB|ECOF|ECOR)(?: |/)', line)]
    check(actual == expected, 'all report table data rows')
    return len(actual)


def main():
    begin = time.monotonic()
    receipt = load(OUT / 'ECONOMY_RUN_SUMMARIES.json')
    compact = load(OUT / 'ECONOMY_COMPACT_SUMMARIES.json')
    service = load(OUT / 'SERVICE_RUN_SUMMARIES.json')
    sources = {n: sha(OUT / n) for n in ('ECONOMY_PILOT_SPEC.md', 'ECONOMY_PILOT_REPORT.md',
               'ECONOMY_RUN_SUMMARIES.json', 'ECONOMY_COMPACT_SUMMARIES.json')}
    verified_raw = {}
    # Hash-first global phase: no gzip decoding occurs until every input passes.
    for x in receipt['raw_inventory'] + [x for r in service['runs'] if r['variant'] == 'RD3' for x in r['raw_traces']]:
        path = OUT / x['path']
        check(not path.is_symlink() and path.stat().st_size == x['bytes'] and sha(path) == x['sha256'], 'raw identity ' + str(path))
        verified_raw[x['path']] = x['sha256']
    pins = receipt['timing']['code_hashes']
    for path, digest in pins.items():
        check(Path(path).name not in ('PLAN_CURRENT.md', 'DESIGN_0G.md', 'DESIGN_0H_REV7.md'), 'excluded pin')
        check(sha(path) == digest, 'dependency identity ' + path)
    for path, digest in compact['source_sha256'].items():
        check(sha(OUT / path) == digest, 'compact source identity ' + path)
    rows = receipt['runs']
    jobs = [dict(variant=v, start=s, keyset=k, observer='on')
            for v in ('ECOF', 'ECOR') for s in ('i', 'ii') for k in range(5)]
    jobs += [dict(variant=v, start='i', keyset=0, observer='off') for v in ('ECOF', 'ECOR')]
    planned = {name(r) for r in jobs}
    slots = [name(r) for r in rows]
    check(planned - set(slots) == {'ECOR_ii_k3_on', 'ECOR_ii_k4_on'} and
          not set(slots) - planned, 'exact planned and missing slot identities')
    check(len(set(slots)) == len(slots) == 20, 'distinct completions')
    check({x.stem for x in LOCAL.glob('*.started')} == set(slots), 'started set')
    for suffix in ('.raw.log', '.harness', '.summary.json'):
        check({x.name[:-len(suffix)] for x in LOCAL.glob('*' + suffix)} == set(slots), 'exclusive artifact set ' + suffix)
    tickets = {}
    for p in sorted(LOCAL.glob('RUN_TICKET_*.json')):
        t = load(p)
        check(t['jobs'] == [[r['variant'], r['start'], r['keyset'], r['observer']] for r in jobs],
              'ticket exact job whitelist')
        grant = {k: t[k] for k in GRANT_FIELDS}
        grant['status'] = 'RUNNING'
        digest = hashlib.sha256(json.dumps(grant, indent=2).encode()).hexdigest()
        check(t['code_hashes'] == pins, 'ticket dependency set')
        tickets[p.name] = dict(grant_sha256=digest, slots=[], reused=t['reused'], status=t['status'],
                              projection_seconds=t['projection_seconds'], elapsed_seconds=t['elapsed_seconds'],
                              stop_reason=t.get('stop_reason'), started_epoch=t['started_epoch'],
                              deadline_epoch=t['deadline_epoch'])
    for r in rows:
        n = name(r)
        check(load(LOCAL / (n + '.summary.json')) == r, 'local completion equality')
        check(r['code_hashes'] == pins, 'row dependency set')
        check(bool(r['raw_traces']), 'completion raw references')
        for raw in r['raw_traces']:
            rawpath = OUT / raw['path']
            check(rawpath.resolve().is_relative_to(LOCAL.resolve()) and
                  raw['path'] in verified_raw and verified_raw[raw['path']] == raw['sha256'] and
                  rawpath.stat().st_size == raw['bytes'], 'completion raw reference identity')
        marker = load(LOCAL / (n + '.started'))
        check(name(marker) == n, 'marker job identity')
        ticket = tickets[Path(marker['ticket']).name]
        check(r['ticket_sha256'] == ticket['grant_sha256'], 'original ticket hash')
        ticket['slots'].append(n)
        check(r['summary']['steps'] == 8000 and r['summary']['last_t'] == 800., 'completion boundary')
        check(r['clone_isolation'] == 'PASS', 'clone isolation')
        for field in ('elapsed_seconds', 'cpu_seconds'):
            check(math.isfinite(r[field]) and r[field] > 0, 'completion timing')
        build = load(OUT / f"kernel_builder/{r['variant']}_BUILD.json")
        check(r['binary_sha256'] == build['build']['binary_sha256'], 'completion binary')
    prior = set()
    for t in tickets.values():
        check(not prior.intersection(t['slots']), 'duplicate launched slot')
        check(set(t['reused']) == prior, 'resume exact reuse set')
        prior.update(t['slots'])
    check(prior == set(slots), 'all launch slots accounted')
    integrity = {}
    for v in ('ECOF', 'ECOR'):
        pair = {r['observer']: r for r in rows if (r['variant'], r['start'], r['keyset']) == (v, 'i', 0)}
        check(set(pair) == {'on', 'off'}, 'complete observer pair')
        a, b = pair['on'], pair['off']
        check(a['summary'] == b['summary'] and a['state_trajectory_sha256'] == b['state_trajectory_sha256'] and
              a['clone_isolation'] == b['clone_isolation'] == 'PASS', 'observer identity')
        integrity[v] = 'PASS'
    check(integrity == receipt['integrity'] == compact['integrity'], 'integrity receipt equality')
    raw_audits = [audit_raw(r) for r in rows if r['observer'] == 'on']
    aggregation = {}
    for v, arm in compact['arms'].items():
        rr = [r for r in rows if r['variant'] == v and r['observer'] == 'on']
        aggregation[v] = audit_compact(rr, arm)
        expected_reading = 'INCOMPLETE' if len(rr) != 10 else 'REGRESSION' if arm['gate_shape']['i']['passes'] <= 3 else 'COVERAGE_IMPROVES' if arm['pooled_3_6'] >= compact['threshold'] else 'DESCRIPTIVE'
        check(arm['reading'] == expected_reading, 'declared reading')
        for c in CLASSES:
            for field in ('elements', 'pair_cost', 'cost'):
                value = sum(sum(x['classes'][c][field] for x in r['telemetry']['mass_samples'] if x['t'] > 0 and x['t'] % 5 == 0) / 160 for r in rr) / len(rr)
                check(value == arm['mean_sample_allocation'][c][field], 'equal-weight class mean')
        removals = [x for r in rr for x in r['telemetry']['economy_removals']]
        check(arm['removal_counts'] == dict(Counter(x['rule'] for x in removals)), 'removal totals')
        checks = [x for r in rr for x in r['telemetry']['prospective_checks']]
        trials = [x for r in rr for x in r['telemetry']['prospective_trials']]
        values = dict(all_checks=len(checks), triggered_checks=sum(x['triggered'] for x in checks),
                      trials=len(trials), failures=sum(not x['passed'] for x in trials),
                      no_candidate_checks=sum(x['result'] == 'no_candidate' for x in checks),
                      no_passing_candidate_checks=sum(x['result'] == 'no_passing_candidate' for x in checks),
                      below_trigger_checks=sum(x['result'] == 'below_trigger' for x in checks),
                      elapsed_seconds=sum(x['prospective_elapsed_seconds'] for x in checks),
                      cpu_seconds=sum(x['prospective_cpu_seconds'] for x in checks))
        for field, value in values.items():
            check(arm['prospective'][field] == value, 'prospective totals ' + field)
        check(arm['prospective']['failure_fraction'] == (values['failures'] / values['trials'] if values['trials'] else None), 'prospective denominator')
        for r, x in zip(rr, arm['first_candidate_cost_refusal_per_run']):
            check(x['refusal'] == (r['telemetry']['initial_cost_refusals'][0] if r['telemetry']['initial_cost_refusals'] else None), 'first actual refusal')
    rd = [r for r in service['runs'] if r['variant'] == 'RD3']
    aggregation['RD3'] = audit_compact(rd, compact['control'])
    cov = load(OUT / 'COVERAGE_COMPACT_SUMMARIES.json')
    for v in ('COVA', 'COVB'):
        check(compact['coverage_context'][v] == cov['arms'][v], 'coverage source equality')
    mass = load(OUT / 'MASS_BUDGET_DIAGNOSTIC.json')
    for v in ('RD3', 'COVA', 'COVB'):
        check(compact['historical_mass_context'][v] == [r for r in mass['runs'] if r['variant'] == v], 'historical mass source equality')
    report_rows = audit_tables(compact, (OUT / 'ECONOMY_PILOT_REPORT.md').read_text())
    clocks = [a['clock'] for a in raw_audits if a['clock']]
    clock_totals = {field: sum(a[field] for a in clocks) for field in ('end_threshold_records', 'final_threshold_records', 'no_donor_checks')}
    check(clock_totals == dict(end_threshold_records=76, final_threshold_records=5, no_donor_checks=71), 'front trigger totals')
    current_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=OUT, text=True).strip()
    result = dict(status='PASS', kind='STORED_DATA_ONLY', reviewed_commit='cbe2da2b326ab9f495598ccffc1d6a1630352da2',
                  execution_head=current_commit, source_sha256=sources, script_sha256=sha(__file__),
                  hash_first=dict(economy_inventory_entries=len(receipt['raw_inventory']), unique_verified_raw_files=len(verified_raw),
                                  dependency_pins=len(pins), forbidden_pins=0),
                  tickets=tickets, completed_slots=slots, missing_unstarted_slots=['ECOR_ii_k3_on', 'ECOR_ii_k4_on'],
                  observer_integrity=integrity, raw_audits=raw_audits, aggregation=aggregation,
                  report_data_rows_verified=report_rows, front_clock_totals=clock_totals,
                  findings=['ECOF clock reached60 at76 site/check records;71 next-check triggers found no eligible donor.',
                            'Report generic ECOF triggered-check0 is ECO-R prospective count, not front-trigger count.',
                            'ECOR pooled fraction uses8 completed runs, not ten; its declared reading stays INCOMPLETE.',
                            'Report historical3987.979 projection above-cap statement refers to former3600 cap; executed5400 cap and PASS pairs supersede stale prose.'],
                  limits=['A/B/E raw aggregate consistent; individual assay decisions/checkpoints not retained, so means cannot be independently reconstructed.',
                          'Native phase and complete native state absent raw traces; cross-arm full-state equality is not asserted.',
                          'Retained launch sets support no duplicate execution within this schedule; reboot and failed pre-ticket invocations not independently proven.',
                          'Historical contextual numbers match hash-pinned source JSON; contextual COVA/COVB raw runs are not independently decoded by this audit.'],
                  elapsed_seconds=time.monotonic() - begin)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps(dict(status='PASS', output=str(DEST.relative_to(OUT)), bytes=DEST.stat().st_size,
                          sha256=sha(DEST), elapsed_seconds=result['elapsed_seconds'])))


if __name__ == '__main__':
    main()
