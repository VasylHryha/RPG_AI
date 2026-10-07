"""STORED-DATA ANALYSIS (no new runs, no verdict): per-site connectivity and event history for the
34 O-pin validation pilots, answering Codex recheck R5 (per-site E and training connectivity) and
R6 (seeded-start failure margins: root timing, birth/budget history, loss of late connectivity).
Reads only the local raw traces listed in RAW_FILES.json (and the four earlier ../pilot_*_assay_*
traces). Usage, from this directory: python3 analyze_stored.py  -> STORED_ANALYSIS.json"""
import collections, gzip, hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LATE = 640.0  # the pilots' late window (last 160 s of 800 s), as in pilot_common.py

# (raw trace, log) for every SUMMARY.md row; the four earlier traces sit one directory up.
RUNS = [
    ('../pilot_baseline_assay_i.json.gz', '../assay_pilot_baseline_i.log'),
    ('../pilot_baseline_assay_ii.json.gz', '../assay_pilot_baseline_ii.log'),
    ('../pilot_c2opin_assay_i.json.gz', '../assay_pilot_c2_opin_i.log'),
    ('../pilot_c2opin_assay_ii.json.gz', '../assay_pilot_c2_opin_ii.log'),
]
for k in (1, 2, 3, 4):
    b = 'batt' if k < 3 else 'batt2'
    for s in ('i', 'ii'):
        RUNS.append((f'pilot_baseline_assay_alt{k}_{s}.json.gz', f'{b}_base_{s}_k{k}.log'))
        RUNS.append((f'pilot_c2opin_assay_alt{k}_{s}.json.gz',
                     f'batt_c2_{s}_d1.0_k{k}.log' if k < 3 else f'batt2_c2_{s}_d1.0_k{k}_root.log'))
for d in ('opposite', 'perp'):
    for s in ('i', 'ii'):
        RUNS.append((f'pilot_c2opin_{d}_assay_{s}.json.gz', f'batt2_c2_{s}_d1.0_k0_{d}.log'))
        for k in (1, 2):
            RUNS.append((f'pilot_c2opin_{d}_assay_alt{k}_{s}.json.gz', f'batt3_c2_{s}_k{k}_{d}.log'))
RUNS += [('pilot_c2opin_d0.5_assay_i.json.gz', 'batt_c2_i_d0.5_k0.log'),
         ('pilot_c2opin_d1.5_assay_i.json.gz', 'batt_c2_i_d1.5_k0.log')]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def analyze(trace, log):
    p = HERE / trace
    d = json.load(gzip.open(p, 'rt'))
    logged = json.loads((HERE / log).read_text().strip().splitlines()[-1])
    assert abs(logged['assay']['A'] - d['assay']['A']) < 1e-12, (trace, log)  # trace <-> log binding
    steps, events = d['steps'], d['events']
    sites = sorted({s for x in steps for s in x['active']} | set(range(len(d['assay']['E']))))
    late = [x for x in steps if x['t'] > LATE]
    def site_conn(window):
        out = {}
        for s in sites:
            act = [x for x in window if s in x['active']]
            out[s] = round(sum(s in x['paths'] for x in act) / len(act), 3) if act else None
        return out
    present = [x['t'] for x in steps if x['paths']]
    best = cur = 0; t0 = span = None
    for x in steps:
        if x['paths']:
            if cur == 0: t0 = x['t']
            cur += 1
            if cur > best: best, span = cur, [t0, x['t']]
        else: cur = 0
    terminal = collections.Counter(f"{e['values']['birth_rule']}:{e['values']['outcome']}"
                                   for e in events if e['rule'] == 'birth_terminal')
    accepted = [e['time'] for e in events if e['rule'] in ('B-path', 'B1', 'B-out')]
    cost_refusals = [e['time'] for e in events if e['rule'] == 'birth_terminal' and e['values']['outcome'] == 'cost']
    bout = [e for e in events if e['rule'] == 'B-out']
    first_path_site = next((x['paths'][0] for x in steps if x['paths']), None)
    deaths = collections.Counter(e['rule'] for e in events if e['rule'] in ('D1', 'D2', 'D3', 'D4'))
    return dict(
        trace=trace, trace_sha256=sha(p), log=log, tag=d['tag'], start=d['start'], keyset=d.get('keyset', 0),  # the four earlier traces predate the keyset field (fixture keys)
        A=d['assay']['A'], B=d['assay']['B'], E=[round(v, 4) for v in d['assay']['E']],
        gate_shape=d['assay']['A'] >= 0.3 and d['assay']['B'] >= 0.3 and max(d['assay']['E']) >= 0.5,
        assay_sites_with_E_ge_0_5=sum(v >= 0.5 for v in d['assay']['E']),
        assay_sites_with_E_zero=sum(v == 0 for v in d['assay']['E']),
        late_connectivity_per_site=site_conn(late), whole_run_connectivity_per_site=site_conn(steps),
        late_any_path=round(sum(bool(x['paths']) for x in late) / len(late), 3),
        first_path_time=present[0] if present else None, first_path_site=first_path_site,
        last_path_time=present[-1] if present else None, longest_path_span=span, longest_path_steps=best,
        output_birth=[dict(time=e['time'], **e['values']) for e in bout],
        final_O=steps[-1]['O'], final_nearest_dO=steps[-1]['dO'], final_n=steps[-1]['n'],
        births={r: sum(e['rule'] == r for e in events) for r in ('B-out', 'B-path', 'B1')},
        birth_outcomes=dict(sorted(terminal.items())), deaths=dict(deaths),
        last_accepted_birth_time=max(accepted) if accepted else None,
        first_cost_refusal_time=min(cost_refusals) if cost_refusals else None)


if __name__ == '__main__':
    rows = [analyze(t, l) for t, l in RUNS]
    assert len(rows) == 34
    (HERE / 'STORED_ANALYSIS.json').write_text(json.dumps(dict(
        kind='STORED_DATA_ANALYSIS_NO_VERDICT', late_window_s=[LATE, 800.0],
        note='E = averaged assay path exposure per site (reachability, not site-specific causal response); '
             'connectivity = fraction of steps a site is active and has a strong path to O',
        rows=rows), indent=1))
    for r in rows:
        print(r['tag'], r['start'], 'PASS' if r['gate_shape'] else 'fail', r['E'], r['late_connectivity_per_site'],
              r['first_path_time'], r['last_path_time'], r['longest_path_span'], r['first_cost_refusal_time'],
              r['last_accepted_birth_time'], r['final_nearest_dO'][:2])
