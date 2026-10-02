"""Development-only C6 gate. Run --smoke for a short, scratch-only pipeline check."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
import time
import signal
import hashlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from geomind import c4_model, c6_native
from geomind import c6_experiment as ex, c6_units as units

WORKERS = 8
PROVISIONAL = {1: 1., 2: 3.2, 3: 9.6}


@contextmanager
def worker_pool():
    pool = ProcessPoolExecutor(max_workers=WORKERS)
    try:
        yield pool
    except BaseException:
        for process in pool._processes.values():
            process.terminate()
        pool.shutdown(wait=True, cancel_futures=True)
        raise
    else:
        pool.shutdown(wait=True)


def jsonable(value):
    import numpy as np
    from dataclasses import is_dataclass, asdict
    if is_dataclass(value):
        return jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return jsonable(value.tolist())
    if isinstance(value, np.generic):
        return jsonable(value.item())
    if isinstance(value, float) and not __import__('math').isfinite(value):
        return 'Infinity' if value > 0 else '-Infinity' if value < 0 else 'NaN'
    return value


class Receipt:
    def __init__(self, folder, smoke, smoke_all_stages=False):
        if smoke_all_stages and not smoke:
            raise ValueError('--smoke-all-stages requires --smoke')
        self.folder = Path(folder)
        if self.folder.exists():
            raise FileExistsError('will not overwrite a development receipt')
        if smoke and (ROOT/'evidence').resolve() in (self.folder.resolve(), *self.folder.resolve().parents):
            raise ValueError('smoke must write outside evidence/')
        self.folder.mkdir(parents=True)
        self.data = {'status': 'RUNNING', 'smoke': smoke, 'smoke_all_stages': smoke_all_stages,
                     'C_fallbacks': [], 'entropy': ex.DEVELOPMENT_ENTROPY,
                     'workers': WORKERS, 'steps': [], 'timings': [], 'stop_rules': [
                         {'rule': n, 'evaluated': False, 'stop': None, 'responsible': 'implementer', 'action': 'STOP'}
                         for n in range(1, 8)]}
        dependencies = [*ROOT.glob('geomind/c4_*.py'), *ROOT.glob('geomind/c5_*.py'), *ROOT.glob('geomind/c6_*.py'),
                        ROOT/'tools/c6_design_gate.py', ROOT/'tools/build_c6.py', ROOT/'native/c6/element_law.cpp',
                        ROOT/'experiments/c6_proposal.md', ROOT/'experiments/c4_manifest.json', ROOT/'experiments/c5_manifest.json']
        self.data['file_hashes'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in dependencies}
        self.data['same_rule_audit'] = ex.same_rule_audit(PROVISIONAL)
        self.write()

    def write(self):
        (self.folder/'results.json').write_text(json.dumps(jsonable(self.data), indent=2, allow_nan=False)+'\n')
        (self.folder/'README.md').write_text('# C6 development '+('smoke' if self.data['smoke'] else 'design gate')+'\n\n'
            'Development entropy 33333 only. This is not a recorded panel or milestone evidence.\n'+
            ('All-stages smoke uses six worlds per level, the full formation horizon, and records would-stop rows.\n'
             if self.data['smoke_all_stages'] else
             'Ordinary smoke uses two worlds per level and a shortened formation horizon.\n')+
            'Smoke values cannot qualify settings. C fallbacks, if any, are smoke-only.\n'
            'Raw world values and yes/no stop rows are in results.json. Unreached rows remain explicitly unevaluated.\n'
            'Status: '+self.data['status']+'\n')

    def step(self, name, values, status='EVALUATED'):
        row = {'name': name, 'status': status, 'values': values}
        if status == 'NOT_RUN':
            row['reason'] = 'no formed group to process'
        self.data['steps'].append(row)
        self.write()

    def check(self, rule, stop, values):
        row = next((r for r in self.data['stop_rules'] if r['rule'] == rule), None)
        if row is None:
            row = {'rule': rule, 'responsible': 'implementer', 'action': 'STOP'}
            self.data['stop_rules'].append(row)
        continuing = self.data['smoke_all_stages']
        row.update(evaluated=True, stop=bool(stop), values=values)
        if continuing:
            row.update(would_stop=bool(stop), action='CONTINUE_SMOKE_ONLY')
        if stop and not continuing:
            self.data.update(status='STOP', stopped_at=rule)
        self.write()
        return continuing or not stop


    @contextmanager
    def timed(self, stage, work, inputs_only=False):
        print(json.dumps({'stage': stage, 'work': work, 'inputs_only': inputs_only}), flush=True)
        started = time.perf_counter()
        try:
            yield work
        finally:
            self.data['timings'].append({'stage': stage, 'seconds': time.perf_counter()-started,
                                         'work': work, 'inputs_only': inputs_only})
            self.write()


def bank_plan(level, worlds):
    """Audit existing supply margins against §9's approximate harvest estimate."""
    import math
    composite = worlds*20 if level > 2 else 0
    primitive = 8*(composite or 5*worlds)
    return {'destination_worlds': worlds, 'composite_worlds': composite, 'primitive_worlds': primitive,
            'proposal_estimate': {'composite_worlds': math.ceil(400*worlds/40) if composite else 0,
                                   'primitive_worlds': math.ceil(7.5*(10*worlds if composite else worlds))},
            'basis': 'Existing supply margins retained; §9 harvest quantities are approximate, not fixed endpoints'}


def pass_one_factors(receipt, tau_rows):
    """A1: rule 2, then rule 3, before factors are updated or pass 2 is scheduled."""
    all_rows = [r for rs in tau_rows.values() for r in rs]
    by_level = {n: [r for r in all_rows if r['level'] == n] for n in PROVISIONAL}
    censoring = {n: {'count': len(rs), 'censored': sum(r['censored'] for r in rs)}
                 for n, rs in by_level.items()}
    if not receipt.check(2, any(r['count'] < 5 or r['censored']/r['count'] >= .5
                               for r in censoring.values()), censoring):
        return None
    measured = {n: ex.cumulative_C(by_level[n], by_level[1]) for n in (2, 3)}
    receipt.step('measured_C', measured)
    if not receipt.check(3, measured[2] is None or not 1.6 <= measured[2] <= 6.4, measured):
        return None
    if receipt.data['smoke_all_stages']:
        for n, value in measured.items():
            if value is None:
                receipt.data['C_fallbacks'].append({'level': n, 'measured': None, 'used': PROVISIONAL[n],
                                                   'reason': 'measured C undefined', 'smoke_only': True})
        measured = {n: PROVISIONAL[n] if value is None else value for n, value in measured.items()}
        receipt.step('pass_2_C_inputs', measured)
    return measured


def fidelity_means(rows):
    import numpy as np
    keys = ('c5_rate_error', 'c6_rate_error', 'c5_capacity_error', 'c6_capacity_error')
    means = {k: float(np.mean([r[k] for r in rows])) if rows else None for k in keys}
    return {'parents': len(rows), 'means': means, 'stop': not rows or
            means['c6_rate_error'] > means['c5_rate_error'] or
            means['c6_capacity_error'] > means['c5_capacity_error']}


def _harvest_job(args):
    purpose, start, count = args
    return ex.harvest_primitives(purpose, count, c6_native.simulate, start=start)


def _formation_job(args):
    templates, C, purpose, index, factors, smoke, reference = args
    return ex.formation(templates, C, purpose, index, c4_model.simulate if reference else c6_native.simulate, factors, smoke)


def _alone_job(args):
    row, purpose, index = args
    return ex.harvest_composites(row, c6_native.simulate, purpose, index)


def _tau_job(args):
    row, purpose = args
    return ex.timescale_records([row], c6_native.simulate, purpose)


def _readiness_job(args):
    row, purpose, index = args
    return ex.coarse_readiness_world(row, c6_native.simulate, purpose, index)


def _specificity_cost_job(args):
    started = time.perf_counter()
    row, recipe, variant, purpose = args
    group, _ = ex.formed_group(row)
    members = list(group.members)
    tau = ex.measure_tau(ex.restrict_owner(group, members), row['x'][members], row['th'][members],
                         row['omega'][members], c6_native.simulate, ex.development_rng(purpose, 0))
    record = ex.specificity_world(row, c6_native.simulate, recipe, variant, purpose, 0, tau)
    return {'world': row['record']['world'], 'seconds': time.perf_counter()-started, 'raw': record}


def bank(pool, level, worlds, purpose, factors, smoke, receipt, inputs_only=False):
    """Source-isolated bank; check-4 banks are inputs only and never reused."""
    plan = bank_plan(level, worlds)
    usage = {'inputs_only': inputs_only, 'purpose': purpose, 'plan': plan}
    receipt.step('bank_plan_'+str(purpose), usage)
    count = plan['primitive_worlds']
    batches = [(purpose, start, min((count+WORKERS-1)//WORKERS, count-start))
               for start in range(0, count, (count+WORKERS-1)//WORKERS)]
    with receipt.timed('primitive_harvest', {'purpose': purpose, 'level': level, 'worlds': count}, inputs_only) as work:
        results = list(pool.map(_harvest_job, batches))
        work['job_seconds'] = [r['seconds'] for _, rs in results for r in rs]
    templates = [t for ts, _ in results for t in ts]
    receipt.step('primitive_harvest_'+str(purpose), {**usage, 'raw': [r for _, rs in results for r in rs],
                                                  'templates': len(templates)})
    if plan['composite_worlds']:
        depth = level-1
        assigned = units.assign_templates(templates, 5, plan['composite_worlds'])
        jobs = [(ts, factors[depth], purpose+10+depth, i, factors, False, False) for i, ts in enumerate(assigned)]
        with receipt.timed('composite_formation', {'purpose': purpose, 'level': level, 'worlds': len(jobs)}, inputs_only) as work:
            rows = list(pool.map(_formation_job, jobs))
            work['job_seconds'] = [r['record']['seconds'] for r in rows]
        with receipt.timed('composite_isolation', {'purpose': purpose, 'level': level, 'worlds': len(rows)}, inputs_only) as work:
            harvested = list(pool.map(_alone_job, [(r, purpose+20+depth, i) for i, r in enumerate(rows)]))
            work['job_seconds'] = [sum(r['seconds'] for r in rs) for _, rs in harvested]
        receipt.step('composite_harvest_'+str(purpose)+'_'+str(depth),
                     {**usage, 'worlds': [r['record'] for r in rows], 'alone': [a for _, rs in harvested for a in rs]})
        templates = [t for ts, _ in harvested for t in ts]
    return units.assign_templates(templates, 5, worlds)


def compare_records(actual, expected):
    """Every detector statistic, recursively, with the proposal's relative-plus-absolute bound."""
    import numpy as np
    errors, maximum = [], 0.
    if actual['outcome'] != expected['outcome']:
        errors.append('outcome')
    a, b = actual['candidates'], expected['candidates']
    if [(r['units'], r['accepted']) for r in a] != [(r['units'], r['accepted']) for r in b]:
        errors.append('candidate sets')
    def walk(x, y, path):
        nonlocal maximum
        if isinstance(x, dict) and isinstance(y, dict):
            if set(x) != set(y):
                errors.append(path+' keys')
                return
            for key in x:
                walk(x[key], y[key], path+'.'+key)
        elif isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
            if len(x) != len(y):
                errors.append(path+' length')
                return
            for i, (p, q) in enumerate(zip(x, y)):
                walk(p, q, path+'.'+str(i))
        elif isinstance(x, (float, int, np.number)) and not isinstance(x, (bool, np.bool_)):
            if x == y:
                return
            difference = abs(x-y)
            maximum = max(maximum, float(difference))
            if not np.isfinite(difference) or difference > max(1e-6*abs(y), 1e-9):
                errors.append(path)
        elif x != y:
            errors.append(path)
    walk(a, b, 'candidates')
    walk(actual['validity'], expected['validity'], 'validity')
    return {'passed': not errors, 'errors': errors, 'max_difference': maximum}


def development_neighbors(frames):
    import numpy as np
    indices, masks, states = 0, 0, 0
    for start in range(0, len(frames), 8):
        chunk = frames[start:start+8]
        batch = c4_model.Batch(c4_model.INTACT, len(chunk))
        actual, expected = c6_native.neighbors(chunk, batch), c4_model.neighbors(chunk, batch)
        indices += int(np.count_nonzero(actual[0] != expected[0]))
        masks += int(np.count_nonzero(actual[1] != expected[1]))
        states += len(chunk)
    return {'passed': indices == masks == 0, 'states': states, 'index_mismatches': indices, 'mask_mismatches': masks}


def summarize_formation(rows):
    counts = Counter(r['record']['outcome'] for r in rows)
    failures = Counter(k for r in rows for c in r['record']['candidates'] for k in c['failed'])
    return {'formed': counts['FORMED'], 'worlds': len(rows), 'fraction': counts['FORMED']/len(rows),
            'outcomes': dict(counts), 'failures': dict(failures), 'raw': [r['record'] for r in rows]}


def run(folder, smoke=False, smoke_all_stages=False):
    receipt = Receipt(folder, smoke, smoke_all_stages)
    started = time.perf_counter()
    counts = {2: 6 if smoke_all_stages else 2 if smoke else 10,
              3: 6 if smoke_all_stages else 2 if smoke else 5}
    short = smoke and not smoke_all_stages
    with worker_pool() as pool:
        # Check 4 is first. No formation settings are counted before this passes.
        equivalent, equivalence_rows = True, []
        for level, worlds in counts.items():
            templates = bank(pool, level, worlds, 1000+100*level, PROVISIONAL, short, receipt, inputs_only=True)
            jobs = [(ts, PROVISIONAL[level], 2000+level, i, PROVISIONAL, short, reference)
                    for i, ts in enumerate(templates) for reference in (False, True)]
            with receipt.timed('backend_equivalence_4', {'level': level, 'worlds': worlds, 'native_and_numpy': True}):
                rows = list(pool.map(_formation_job, jobs))
            for i in range(worlds):
                actual, expected = rows[2*i]['record'], rows[2*i+1]['record']
                check = compare_records(actual, expected)
                check['neighbors'] = development_neighbors(rows[2*i]['xs'])
                check['passed'] &= check['neighbors']['passed']
                equivalent &= check['passed']
                equivalence_rows.append({'level': level, 'world': i, 'check': check, 'native': actual, 'numpy': expected})
            receipt.step('backend_equivalence_4_level_'+str(level), equivalence_rows[-worlds:])
        receipt.step('backend_equivalence_4', equivalence_rows)
        if not receipt.check(14, not equivalent, equivalence_rows):
            return receipt
        # All full-model runs below explicitly select the native engine.
        factors, passes, taus = dict(PROVISIONAL), {}, {}
        world_count = 6 if smoke_all_stages else 2 if smoke else 30
        for pass_index in (1, 2):
            per_level = {}
            for level in counts:
                purpose = 3000+pass_index*1000+level*100
                templates = bank(pool, level, world_count, purpose, factors, short, receipt)
                with receipt.timed('formation', {'pass': pass_index, 'level': level, 'worlds': len(templates),
                                                  'short': short, 'C': factors[level]}):
                    rows = list(pool.map(_formation_job, [(ts, factors[level], purpose+50, i, factors, short, False)
                                                           for i, ts in enumerate(templates)]))
                per_level[level] = rows
            passes[pass_index] = per_level
            receipt.step('formation_pass_'+str(pass_index), {n: summarize_formation(rs) for n, rs in per_level.items()})
            tau_rows = {}
            for n, rows in per_level.items():
                with receipt.timed('isolated_timescales', {'pass': pass_index, 'level': n, 'worlds': len(rows)}) as work:
                    measurements = list(pool.map(_tau_job, [(r, 6000+pass_index*100+n) for r in rows]))
                    work['job_seconds'] = [sum(r.get('seconds', 0.) for r in rs) for rs in measurements]
                tau_rows[n] = [v for rs in measurements for world in rs for v in world['measurements']]
                receipt.step(f'isolated_timescales_pass_{pass_index}_level_{n}', tau_rows[n],
                             'EVALUATED' if tau_rows[n] else 'NOT_RUN')
            taus[pass_index] = tau_rows
            receipt.step('isolated_timescales_pass_'+str(pass_index), tau_rows)
            if pass_index == 1:
                measured = pass_one_factors(receipt, tau_rows)
                if measured is None:
                    return receipt
                factors.update(measured)
                receipt.data['same_rule_audit'] = ex.same_rule_audit(factors)
                receipt.write()
            else:
                reference = [r for rs in tau_rows.values() for r in rs if r['level'] == 1]
                receipt.step('measured_C_pass_2_report_only', {
                    n: ex.cumulative_C([r for r in tau_rows[n] if r['level'] == n], reference) for n in counts})
        formation_values = {n: summarize_formation(rs) for n, rs in passes[2].items()}
        if not receipt.check(1, any(v['fraction'] < .75 for v in formation_values.values()), formation_values):
            return receipt
        with receipt.timed('interface_fidelity', {'worlds': sum(len(rs) for rs in passes[2].values())}):
            fidelity = ex.interface_fidelity([r for rs in passes[2].values() for r in rs], c6_native.simulate)
        summary = fidelity_means(fidelity)
        receipt.step('interface_fidelity', {'raw': fidelity, **summary})
        for n in passes[2]:
            records = [r for r in fidelity if r['level'] == n]
            receipt.step(f'interface_fidelity_level_{n}', fidelity_means(records),
                         'EVALUATED' if records else 'NOT_RUN')
        if not receipt.check(4, summary['stop'], summary):
            return receipt
        readiness_raw = {}
        for n, rs in passes[2].items():
            with receipt.timed('coarse_readiness', {'level': n, 'worlds': len(rs)}) as work:
                records = [v for v in pool.map(_readiness_job, [(r, 7000+n, i) for i, r in enumerate(rs)]) if v is not None]
                work['job_seconds'] = [r['seconds'] for r in records]
                work['formed'] = len(records)
            readiness_raw[n] = records
            receipt.step(f'coarse_readiness_level_{n}', records, 'EVALUATED' if records else 'NOT_RUN')
        readiness = ex.readiness_summary(readiness_raw)
        receipt.step('coarse_readiness', {'raw': readiness_raw, 'summary': readiness})
        selected = readiness['selected']
        fail = selected is None
        if selected:
            chosen = readiness['combinations'][selected]
            fail |= chosen['worst_gain'] <= 0
            for r in chosen['levels'].values():
                fail |= r['groups'] < 10 or r['censored_fraction'] > .1
                fail |= any(v['count'] < 10 or v['mean'] is None or v['mean'] > .5 for v in r['r'].values())
        if not receipt.check(5, fail, readiness):
            return receipt
        with receipt.timed('overlap_calibration', {'worlds': len(passes[2][3])}):
            overlaps = ex.overlap_population(passes[2][3])
        receipt.step('overlap_calibration', overlaps)
        if not receipt.check(6, not overlaps or any(r['intact'] and r['overlap'] > .2 for r in overlaps), overlaps):
            return receipt
        # With an absent transition there is no qualifying choice. In all-stages smoke
        # time the best non-excluded combination on the observed cells only, explicitly.
        timing_choice = selected
        if timing_choice is None and smoke_all_stages:
            candidates = []
            for name, values in readiness['combinations'].items():
                cells = [v for level in values['levels'].values() for v in level['cells'].values() if v is not None]
                if cells and not values['excluded']:
                    candidates.append((min(cells), name))
            timing_choice = max(candidates)[1] if candidates else None
            receipt.step('specificity_smoke_timing_choice', {'choice': timing_choice,
                'basis': 'best observed worst-cell gain; missing transition omitted for timing only', 'smoke_only': True})
        specificity_cost = {}
        if timing_choice:
            recipe, variant = timing_choice.split('_')
            receipt.data['same_rule_audit'] = ex.same_rule_audit(factors,
                {n: ex.transition_rule((recipe,), (variant,)) for n in passes[2]})
        for n, rs in passes[2].items():
            formed = next((r for r in rs if ex.formed_group(r) is not None), None)
            if formed is None:
                specificity_cost[n] = {'status': 'NOT_RUN', 'reason': 'no formed group to process'}
            elif timing_choice is None:
                # All E1 combinations remain eligible by construction when a group exists.
                raise ValueError('stop rule 8: formed group but no usable specificity timing choice')
            else:
                with receipt.timed('specificity', {'level': n, 'worlds': 1, 'choice': timing_choice}):
                    specificity_cost[n] = next(pool.map(_specificity_cost_job, [(formed, recipe, variant, 8000+n)]))
                specificity_cost[n]['status'] = 'EVALUATED'
            receipt.step(f'runtime_specificity_level_{n}', specificity_cost[n], specificity_cost[n]['status'])
        receipt.step('runtime_specificity_measurements', specificity_cost)
        projection = full_gate_projection(receipt.data, panel=True)
        receipt.step('runtime_projection', projection)
        seconds = projection['complete_gate_seconds']
        if not receipt.check(7, seconds is None or seconds > 3*3600, projection):
            return receipt
    receipt.data.update(status='SMOKE_COMPLETE' if smoke else 'COMPLETE', seconds=time.perf_counter()-started)
    receipt.write()
    return receipt


def full_gate_projection(data, panel=False):
    """Measured workload projection; never use input-only bank measurements.

    Serial fidelity/overlap remain serial. Parallel work uses process-seconds / 8.
    An absent formed group leaves that level's processing cost unknown, not zero.
    """
    import numpy as np
    stages, missing = [], []
    timings = [t for t in data['timings'] if not t['inputs_only']]
    steps = {s['name']: s['values'] for s in data['steps']}
    def add(name, work, cost, basis):
        stages.append({'stage': name, 'work': work, 'seconds': cost, 'basis': basis})
        if cost is None:
            missing.append(name)
    def bank_cost(level, worlds, label):
        plan = bank_plan(level, worlds)
        for name, count in (('primitive_harvest', plan['primitive_worlds']),
                            ('composite_formation', plan['composite_worlds']),
                            ('composite_isolation', plan['composite_worlds'])):
            if not count:
                continue
            source = [t for t in timings if t['stage'] == name and t['work']['level'] == level]
            jobs = [c for t in source for c in t['work'].get('job_seconds', [])]
            cost = count*float(np.mean(jobs))/WORKERS if jobs else None
            add(label+'_'+name, count, cost,
                'mean process-seconds per harvest world × count / 8; check-4 input banks excluded')
    def full_world_cost(r):
        extra = r['full_duration']-r['duration']
        return r['seconds']+r['observation_seconds']*extra/r['observation_duration']
    if not panel:
        for level, worlds in ((2, 10), (3, 5)):
            bank_cost(level, worlds, 'check4_l'+str(level)+'_bank')
            rows = steps.get('backend_equivalence_4_level_'+str(level), [])
            jobs = [full_world_cost(r['native'])+full_world_cost(r['numpy']) for r in rows]
            cost = worlds*float(np.mean(jobs))/WORKERS if jobs else None
            add('check4_l'+str(level), worlds, cost, 'mean native + NumPy pair process-seconds × count / 8')
    for pass_index in ((2,) if panel else (1, 2)):
        for level in (2, 3):
            worlds = 40 if panel else 30
            label = ('panel' if panel else 'pass'+str(pass_index))+'_l'+str(level)
            bank_cost(level, worlds, label+'_bank')
            measured = steps.get('formation_pass_'+str(pass_index), steps.get('formation_pass_1', {}))
            rows = measured.get(level, measured.get(str(level), {})).get('raw', [])
            factor = 3.6 if panel else 1.
            cost = factor*worlds*float(np.mean([full_world_cost(r) for r in rows]))/WORKERS if rows else None
            add(label+'_formation_protocol', worlds, cost,
                f'mean full formation process-seconds × {factor} protocol factor × count / 8')
            ts = [t for t in timings if t['stage'] == 'isolated_timescales' and
                  t['work']['level'] == level and t['work']['pass'] == pass_index]
            if not ts:
                ts = [t for t in timings if t['stage'] == 'isolated_timescales' and t['work']['level'] == level]
            jobs = [c for t in ts for c in t['work'].get('job_seconds', [])]
            records = steps.get(f'isolated_timescales_pass_{pass_index}_level_{level}', [])
            tau_cost = worlds*float(np.mean(jobs))/WORKERS if jobs and records else None
            add(label+'_tau', worlds, tau_cost,
                'mean timescale process-seconds per destination world × count / 8; observed formation mix')
    worlds = 40 if panel else 30
    fidelity = steps.get('interface_fidelity', {}).get('raw', [])
    specificity = steps.get('runtime_specificity_measurements', {})
    for level in (2, 3):
        rows = [r for r in fidelity if r['level'] == level]
        cost = worlds*float(np.mean([r['seconds'] for r in rows])) if rows else None
        add('interface_fidelity_l'+str(level), worlds, cost, 'mean per formed parent × count, serial; assumes all worlds formed')
        rows = [t for t in timings if t['stage'] == 'coarse_readiness' and t['work'].get('level') == level]
        jobs = [c for t in rows for c in t['work'].get('job_seconds', [])]
        cost = worlds*float(np.mean(jobs))/WORKERS if jobs else None
        add('coarse_readiness_l'+str(level), worlds, cost, 'mean per formed group process-seconds × count / 8; all four combinations')
        record = specificity.get(level, specificity.get(str(level), {}))
        cost = worlds*record['seconds']/WORKERS if 'seconds' in record else None
        add('runtime_specificity_l'+str(level), worlds, cost,
            'one measured group (including tau, fake publication, all probes) × count / 8; assumes all worlds formed')
    overlaps = [t for t in timings if t['stage'] == 'overlap_calibration']
    cost = sum(t['seconds'] for t in overlaps)*worlds/sum(t['work']['worlds'] for t in overlaps) if overlaps else None
    add('overlap_calibration', worlds, cost, 'measured serial cost per input world × count; acceptance-independent')
    known = sum(s['seconds'] for s in stages if s['seconds'] is not None)
    prefix = sum(s['seconds'] for s in stages if s['seconds'] is not None and
                 (s['stage'].startswith('check4') or s['stage'].startswith('pass1')))
    return {'workers': WORKERS, 'kind': 'panel' if panel else 'full_design_gate', 'stages': stages,
            'measured_workload_seconds': known, 'through_pass1_seconds': prefix,
            'complete_gate_seconds': None if missing else known, 'unmeasured': missing,
            'qualification': 'Workload estimate, not qualification. Unprocessed formed-group costs stay unknown. '
                'Harvest estimates exclude input-only check-4 banks. Full horizons are measured in all-stages smoke. '
                'Fidelity, readiness and specificity conservatively assume all destination worlds formed.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--smoke-all-stages', action='store_true')
    args = parser.parse_args()
    if args.smoke_all_stages and not args.smoke:
        parser.error('--smoke-all-stages requires --smoke')
    folder = Path(tempfile.mkdtemp(prefix='c6-smoke-'))/'receipt' if args.smoke else ROOT/'evidence/c6_design_gate'
    def deadline(signum, frame):
        raise TimeoutError(f'smoke exceeded its {budget}-second execution budget')
    budget = 1190 if args.smoke_all_stages else 570
    previous_handler = signal.signal(signal.SIGALRM, deadline) if args.smoke else None
    if args.smoke:
        signal.alarm(budget)
    started = time.perf_counter()
    try:
        result = run(folder, args.smoke, args.smoke_all_stages)
        result.data['seconds'] = time.perf_counter()-started
        result.data['full_gate_projection'] = full_gate_projection(result.data)
        result.write()
    except Exception as exc:
        # Preserve completed raw stages on infrastructure failure; never continue after one.
        if (folder/'results.json').exists():
            data = json.loads((folder/'results.json').read_text())
            data.update(status='INFRASTRUCTURE_FAILURE', error=str(exc))
            (folder/'results.json').write_text(json.dumps(data, indent=2)+'\n')
            readme = folder/'README.md'
            if readme.exists():
                readme.write_text(readme.read_text().replace('Status: RUNNING', 'Status: INFRASTRUCTURE_FAILURE'))
        raise
    finally:
        if args.smoke:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous_handler)
    print(json.dumps({'path': str(folder), 'status': result.data['status'], 'stop': result.data.get('stopped_at')}))
    return 0 if args.smoke and result.data['status'] in ('STOP', 'SMOKE_COMPLETE') else int(result.data['status'] == 'STOP')


if __name__ == '__main__':
    raise SystemExit(main())
