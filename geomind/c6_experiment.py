"""Development transition protocol. Physics backend is explicit; no panel or registration path."""
from collections import Counter
from dataclasses import replace
import copy
import json
from pathlib import Path
import time

import numpy as np
from geomind import c4_model, c4_experiment, c5_coarse, c5_units
from geomind import c6_native, c6_levels as levels, c6_units as units, c6_compose as compose, c6_effective as effective

ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_ENTROPY = 33333


def development_rng(purpose, *keys):
    return np.random.default_rng(np.random.SeedSequence([DEVELOPMENT_ENTROPY, purpose, *keys]))


def c4_manifest():
    return json.loads((ROOT/'experiments/c4_manifest.json').read_text())


def steps_exact(duration, dt=.02):
    value = duration/dt
    if not np.isfinite(value) or abs(value-round(value)) > 1e-7:
        raise ValueError("duration is not a whole number of element steps")
    return int(round(value))


def rounded_C(value):
    if not np.isfinite(value) or value <= 0:
        raise ValueError("undefined cumulative timescale")
    return np.floor(value*5 + .5 + 1e-12)/5


def cumulative_C(rows, reference):
    def median(records):
        if len(records) < 5 or np.mean([r['censored'] for r in records]) >= .5:
            return None
        return float(np.median([float('inf') if r['censored'] else r['tau'] for r in records]))
    a, b = median(rows), median(reference)
    return None if a is None or b is None or b <= 0 else float(rounded_C(a/b))


def restrict_owner(owner, members):
    mapping = {m: i for i, m in enumerate(members)}
    def visit(node):
        if not node.children:
            return levels.Owner(element=mapping[node.element], C=node.C, source_path=node.source_path)
        return levels.Owner(tuple(visit(c) for c in node.children), C=node.C, source_path=node.source_path)
    return visit(owner)


def set_factors(owner, factors):
    if not owner.children:
        return owner
    return levels.Owner(tuple(set_factors(c, factors) for c in owner.children), C=factors[owner.depth], source_path=owner.source_path)


def integrate(x, th, omega, duration, simulate, every=None, params=None):
    params = c4_model.INTACT if params is None else params
    out = simulate(x[None], th[None], omega[None], params, .02, steps_exact(duration),
                   None if every is None else steps_exact(every))
    frames = None if out[2] is None else (out[2][0][:, 0], out[2][1][:, 0])
    return out[0][0], out[1][0], frames


def detect_snapshot(owner, xs, ths, times, omega, simulate, base, rng, primitive=False):
    t = levels.thresholds(base, owner.C)
    wanted = times[-1]-30*owner.C + np.arange(31)*owner.C
    idx = np.searchsorted(times, wanted-1e-8)
    if np.any(idx >= len(times)) or not np.allclose(times[idx], wanted, atol=1e-7, rtol=0):
        raise ValueError("detector observation grid incomplete")
    X, Theta = levels.child_series(owner, xs[idx], ths[idx])
    validity = [{'ok': True} for _ in owner.children] if primitive else levels.recursive_validity(owner, xs, ths, times, base)
    x0, th0 = xs[-1], ths[-1]
    def kick_runner(part_ids, dx, dth):
        kx, kt = compose.kick_parts(x0, th0, owner, part_ids, dx, dth)
        cx, ct, _ = integrate(x0, th0, omega, t['recovery_time'], simulate)
        ex, et, _ = integrate(kx, kt, omega, t['recovery_time'], simulate)
        control = levels.child_series(owner, cx[None], ct[None])
        excited = levels.child_series(owner, ex[None], et[None])
        return control[0][0], control[1][0], excited[0][0], excited[1][0]
    detected = levels.detect_level((X, Theta), validity, t, kick_runner, rng)
    return detected, validity


def formation(templates, C, purpose, index, simulate, factors, short=False):
    start = time.perf_counter()
    templates = [{**t, 'owner': set_factors(t['owner'], factors)} for t in templates]
    x, th, omega, owner, placement = compose.assemble(templates, development_rng(purpose, index, 0), C)
    base = c4_manifest()['detector']
    observation = max([30*owner.C] + [30*c.C for c in levels.descendants(owner) if c.children])
    duration = levels.horizon(owner)
    if short:
        # Smoke exercises the real path on a short horizon, never qualifies a development setting.
        duration = observation
    settle_started = time.perf_counter()
    x, th, _ = integrate(x, th, omega, duration-observation, simulate)
    settle_seconds = time.perf_counter()-settle_started
    observation_started = time.perf_counter()
    x, th, frames = integrate(x, th, omega, observation, simulate, .2)
    observation_seconds = time.perf_counter()-observation_started
    xs, ths = frames
    times = duration-observation + np.arange(len(xs))*.2
    candidates, validity = detect_snapshot(owner, xs, ths, times, omega, simulate, base,
                                            development_rng(purpose, index, 1))
    labels = compose.labels_for(owner, len(x))
    idx, mask, _ = c4_model.neighbors(x[None], c4_model.Batch(c4_model.INTACT, 1))
    contact = bool(np.any((labels[idx[0]] != labels[:, None]) & (mask[0] > 0)))
    record = {'world': index, 'level': owner.depth, 'C': C, 'duration': duration,
              'purpose': purpose, 'seed_paths': [[DEVELOPMENT_ENTROPY, purpose, index, p] for p in (0, 1)],
              'placement': placement, 'candidates': candidates, 'validity': validity,
              'outcome': levels.outcome(candidates, contact), 'seconds': time.perf_counter()-start,
              'observation_seconds': observation_seconds, 'settle_seconds': settle_seconds,
              'observation_duration': observation, 'full_duration': levels.horizon(owner),
              'elements': len(x), 'source_paths': [p for t in templates for p in t['source_paths']],
              'part_source_paths': [t['source_paths'] for t in templates]}
    return {'record': record, 'x': x, 'th': th, 'omega': omega, 'owner': owner, 'xs': xs, 'ths': ths, 'times': times}


def harvest_primitives(purpose, count, simulate, start=0):
    """Frozen C4 initial conditions/statistics/kicks; native execution after equivalence.

    detect_level composes exactly the frozen criteria 1-5. Primitive validity is vacuous.
    No frozen module is patched or rebound to change its embedded NumPy backend.
    """
    manifest = c4_manifest()
    templates, raw = [], []
    for i in range(start, start+count):
        started = time.perf_counter()
        source = purpose*100000+i
        x, th, om = c4_experiment.initial_worlds(manifest, DEVELOPMENT_ENTROPY, 'identical', [source])
        owner = levels.Owner(tuple(levels.Owner(element=j) for j in range(len(th[0]))), source_path=(source,))
        x, th, _ = integrate(x[0], th[0], om[0], 70., simulate)
        x, th, frames = integrate(x, th, om[0], 30., simulate, .2)
        candidates, _ = detect_snapshot(owner, *frames, np.arange(len(frames[0]))*.2+70., om[0], simulate,
                                         manifest['detector'], development_rng(purpose, i, 9), primitive=True)
        raw.append({'source_world': source, 'candidates': candidates, 'isolated_rates': []})
        for row in candidates:
            members = row['units']
            if row['accepted'] and 6 <= len(members) <= 16:
                local = levels.Owner(tuple(levels.Owner(element=j) for j in range(len(members))), source_path=(source,))
                theta = float(circular_phase(th[members]))
                measured, measurement = units.isolated_rate(local, x[members], th[members],
                    om[0, members], c4_model.INTACT, simulate)
                raw[-1]['isolated_rates'].append({'members': members, 'measurement': measurement})
                templates.append({'x': x[members]-x[members].mean(0), 'th': th[members]-theta,
                                  'omega': om[0, members].copy(), 'isolated_rate': measured, 'owner': local,
                                  'source_world': source, 'source_paths': [(source,)]})
        raw[-1]['seconds'] = time.perf_counter()-started
    return templates, raw


def circular_phase(th):
    return np.angle(np.exp(1j*th).mean())


def measure_tau(owner, x, th, omega, simulate, rng, kind='pulse'):
    C = owner.C
    if kind == 'pulse':
        deltas = compose.unit_kick(rng, len(owner.children), .3)
        kx, kt = compose.kick_parts(x, th, owner, range(len(owner.children)), np.zeros((len(owner.children), 2)), deltas)
    else:
        kx, kt = compose.scale_parts(x, th, owner, 1.25), th
    controls, kicked = [integrate(px, pt, omega, 10*C, simulate, .1*C)[2] for px, pt in ((x, th), (kx, kt))]
    cx, ct = levels.child_series(owner, *controls)
    ex, et = levels.child_series(owner, *kicked)
    if kind == 'pulse':
        i, j = np.triu_indices(len(owner.children), 1)
        difference = c4_model.wrap((et-ct)[:, j]-(et-ct)[:, i])
        dev = np.sqrt(np.mean(difference**2, axis=1))
    else:
        diff = ex-cx
        diff -= diff.mean(1, keepdims=True)
        dev = np.sqrt(np.mean(np.sum(diff**2, axis=-1), axis=1))
    return effective.tau_estimate(dev, C)


def alone(row, group, simulate, purpose, index):
    """Reaccept over enough own-level observation; isolated rate is last 30 own-C."""
    started = time.perf_counter()
    m = list(group.members)
    local = restrict_owner(group, m)
    observation = max([30*local.C] + [30*c.C for c in levels.descendants(local) if c.children])
    x, th, frames = integrate(row['x'][m], row['th'][m], row['omega'][m], observation, simulate, .2)
    times = np.arange(len(frames[0]))*.2
    candidates, validity = detect_snapshot(local, *frames, times, row['omega'][m], simulate,
                                          c4_manifest()['detector'], development_rng(purpose, index, 2))
    wanted = observation-30*local.C+np.arange(31)*local.C
    idx = np.searchsorted(times, wanted-1e-8)
    _, phase = levels.published_series(local, frames[0][idx], frames[1][idx])
    rate = units.rate_estimate(phase, local.C)
    accepted = any(r['accepted'] and set(r['units']) == set(range(len(local.children))) for r in candidates)
    return {'accepted': accepted, 'candidates': candidates, 'validity': validity,
            'rate': rate, 'phase': phase.tolist(), 'duration': observation, 'owner': local,
            'x': x, 'th': th, 'omega': row['omega'][m], 'seconds': time.perf_counter()-started}


def harvest_composites(row, simulate, purpose, index):
    templates, records = [], []
    for candidate in row['record']['candidates']:
        if not candidate['accepted']:
            continue
        group = levels.Owner(tuple(row['owner'].children[u] for u in candidate['units']), C=row['owner'].C)
        isolated = alone(row, group, simulate, purpose, index)
        records.append({k: v for k, v in isolated.items() if k not in ('owner', 'x', 'th', 'omega')})
        if isolated['accepted']:
            # Snapshot at publication, not the later isolated endpoint.
            m = list(group.members)
            local = restrict_owner(group, m)
            X, Theta = levels.published_series(local, row['x'][None, m], row['th'][None, m])
            source = purpose*100000+index
            local = replace(local, source_path=(source,))
            templates.append({'x': row['x'][m]-X[0], 'th': row['th'][m]-Theta[0],
                'omega': row['omega'][m], 'owner': local, 'isolated_rate': isolated['rate'], 'source_world': source,
                'source_paths': [tuple(p)+(source,) for u in candidate['units']
                                 for p in row['record']['part_source_paths'][u]]})
    return templates, records


def publication(owner, x, th, omega, simulate, variant, stability, rate_records, series=None):
    """Owner wrapper recursively publishes; compose_state and the effective model see published fields."""
    measured, measurement = units.isolated_rate(owner, x, th, omega, c4_model.INTACT, simulate)
    collective = measured
    if series is not None:
        xs, ths, times = series
        _, phase = levels.published_series(owner, xs, ths)
        start = np.searchsorted(times, times[-1]-30*owner.C-1e-8)
        collective = float((phase[-1]-phase[start])/(times[-1]-times[start]))
    rate_records.append({'members_digest': c5_units.member_digest(owner.members), 'measurement': measurement})
    if all(not c.children for c in owner.children):
        labels = np.full(len(x), -1, int)
        labels[list(owner.members)] = 0
        return units.level1_state(x, th, omega, labels, 0, collective, stability, c4_model.INTACT, measured, variant)
    children = [publication(c, x, th, omega, simulate, variant, own_stability(c, series), rate_records, series)
                for c in owner.children]
    # Cross-parent active ports determined from published port points and the owner's element census.
    active = set(units.active_members(x, owner.members, c4_model.INTACT))
    port_indices, flat = [], 0
    for child in children:
        for port in child['boundary_ports']:
            point = np.asarray(child['effective_position'])+port['offset']
            if any(np.linalg.norm(x[m]-point) <= 1e-9 for m in active):
                port_indices.append(flat)
            flat += 1
    return units.compose_state(children, collective, stability, measured, c4_model.INTACT, variant, port_indices)


def own_stability(owner, series):
    if series is None:
        raise ValueError('child publication requires own-level observations')
    xs, ths, times = series
    dynamic = levels.dynamic_validity(owner, xs, ths, times, owner.C, c4_manifest()['detector'])
    if not dynamic['windows']:
        raise ValueError('child publication has INSUFFICIENT_OBSERVATION')
    return {k: max(w['stats'][k] for w in dynamic['windows']) for k in
            ('shape_cv', 'lock_std', 'freq_change', 'pattern_change')}


def formed_group(row):
    accepted = [r for r in row['record']['candidates'] if r['accepted']]
    if not accepted:
        return None
    candidate = accepted[0]
    group = levels.Owner(tuple(row['owner'].children[u] for u in candidate['units']), C=row['owner'].C)
    return group, candidate


def timescale_records(rows, simulate, purpose):
    records = []
    for index, row in enumerate(rows):
        started = time.perf_counter()
        found = formed_group(row)
        if found is None:
            continue
        group, _ = found
        all_nodes = [group] + [c for c in levels.descendants(group) if c.children]
        per = []
        for j, node in enumerate(all_nodes):
            m = list(node.members)
            per.append({'level': node.depth, 'members_digest': c5_units.member_digest(m),
                        **measure_tau(restrict_owner(node, m), row['x'][m], row['th'][m], row['omega'][m], simulate,
                                      development_rng(purpose, index, j))})
        records.append({'world': row['record']['world'], 'measurements': per, 'seconds': time.perf_counter()-started})
    return records


def interface_fidelity(rows, simulate):
    """Independent isolated rate and element census; compare mean parent errors.

    Publication and observation are separate 30-own-C runs from the detection endpoint.
    Capacity agreement is measured against actual external elements at each parent port.
    """
    raw = []
    for row in rows:
        started = time.perf_counter()
        found = formed_group(row)
        if found is None:
            continue
        owner, candidate = found
        children, measurements = [], []
        for child in owner.children:
            children.append(publication(child, row['x'], row['th'], row['omega'], simulate, 'V1',
                                        own_stability(child, (row['xs'], row['ths'], row['times'])), measurements,
                                        (row['xs'], row['ths'], row['times'])))
        published_rate, publication_run = units.isolated_rate(owner, row['x'], row['th'], row['omega'], c4_model.INTACT, simulate)
        old = c5_units.compose_state(children, published_rate, candidate['stats'])
        new = units.compose_state(children, published_rate, candidate['stats'], published_rate, c4_model.INTACT)
        # Independent observation: start anew at the detection snapshot, never reuse publication_run.
        rate, isolated = units.isolated_rate(owner, row['x'], row['th'], row['omega'], c4_model.INTACT, simulate)
        world_key = (owner.depth, row['record']['world'])
        interface_candidate = {**candidate, 'world': world_key}
        problems = units.validate_interface([interface_candidate],
            [{'world': world_key, 'units': candidate['units'], 'state': new}],
            {world_key: dict(zip(candidate['units'], children))})
        if problems:
            raise ValueError('N1 interface failed: '+', '.join(problems))
        members = list(owner.members)
        internal_idx, internal_mask, _ = c4_model.neighbors(row['x'][None, members], c4_model.Batch(c4_model.INTACT, 1))
        outside = [m for m in range(len(row['x'])) if m not in set(members)]
        errors = []
        counts = []
        for state in (old, new):
            predicted, actual = [], []
            for port in state['boundary_ports']:
                position = np.asarray(state['effective_position'])+port['offset']
                p = int(np.argmin(np.linalg.norm(row['x'][members]-position, axis=1)))
                own = np.linalg.norm(row['x'][members][internal_idx[0, p]]-row['x'][members[p]], axis=1)[internal_mask[0, p] > 0]
                external = np.linalg.norm(row['x'][outside]-position, axis=1)
                def cross_count(capacity):
                    candidates = np.r_[capacity, external]
                    order = np.argsort(candidates, kind='stable')[:c4_model.INTACT.k]
                    return int(np.sum((order >= len(capacity)) & (candidates[order] < c4_model.INTACT.radius)))
                predicted.append(cross_count(port['own_neighbour_distances']))
                actual.append(cross_count(own))
            errors.append(float(np.mean(np.abs(np.array(predicted)-actual))))
            counts.append({'predicted': predicted, 'census': actual})
        raw.append({'world': row['record']['world'], 'observed_rate': rate, 'isolated': isolated, 'publication_run': publication_run,
                    'level': owner.depth,
                    'c5_rate_error': abs(old['natural_rate']-rate), 'c6_rate_error': abs(new['natural_rate']-rate),
                    'c5_capacity_error': errors[0], 'c6_capacity_error': errors[1], 'counts': counts,
                    'c5_state': old, 'c6_state': new, 'children': children, 'candidate': candidate,
                    'interface_problems': problems, 'seconds': time.perf_counter()-started})
    return raw


def coarse_readiness_world(row, simulate, purpose, index):
    started = time.perf_counter()
    found = formed_group(row)
    if found is None:
        return None
    owner, candidate = found
    times = np.arange(101)*.1*owner.C
    excited = int(development_rng(purpose, index, 0).integers(len(owner.children)))
    control = integrate(row['x'], row['th'], row['omega'], 10*owner.C, simulate, .1*owner.C)[2]
    tau_phase = measure_tau(owner, row['x'], row['th'], row['omega'], simulate, development_rng(purpose, index, 1))
    tau_position = measure_tau(owner, row['x'], row['th'], row['omega'], simulate, development_rng(purpose, index, 2), 'push')
    variants, raw_rates = {}, []
    for variant in PORT_VARIANTS:
        variants[variant] = [publication(c, row['x'], row['th'], row['omega'], simulate, variant,
                                         own_stability(c, (row['xs'], row['ths'], row['times'])), raw_rates,
                                         (row['xs'], row['ths'], row['times'])) for c in owner.children]
    groupings = [c.members for c in owner.children]
    out = {'world': index, 'excitations': {}, 'rates': raw_rates, 'tau_phase': tau_phase, 'tau_position': tau_position}
    for kind, tau in (('pulse', tau_phase), ('push', tau_position)):
        states = variants['V1']
        centre = np.asarray(states[excited]['effective_position'])
        direction = centre-np.mean([s['effective_position'] for s in states], axis=0)
        direction /= np.linalg.norm(direction)
        amount = .5 if kind == 'pulse' else .2*states[excited]['characteristic_size']*direction
        dx, dth = np.zeros((1, 2)), np.zeros(1)
        if kind == 'pulse':
            dth[0] = amount
        else:
            dx[0] = amount
        ex, et = compose.kick_parts(row['x'], row['th'], owner, [excited], dx, dth)
        full = integrate(ex, et, row['omega'], 10*owner.C, simulate, .1*owner.C)[2]
        paired = np.concatenate([full[0]-control[0], (full[1]-control[1])[..., None]], axis=-1)
        truth = levels.linear_summary(paired, groupings)
        scores = {}
        rigid_states = copy.deepcopy(variants['V1'])
        for state, child in zip(rigid_states, owner.children):
            m = list(child.members)
            idx, mask, _ = c4_model.neighbors(row['x'][None, m], c4_model.Batch(c4_model.INTACT, 1))
            distances = np.linalg.norm(row['x'][m][idx[0]]-row['x'][m][:, None], axis=-1)
            state['boundary_ports'] = [{'offset': (row['x'][p]-state['effective_position']).tolist(),
                'phase_offset': float(c4_model.wrap(row['th'][p]-state['optional_phase'])),
                'own_neighbour_distances': sorted(distances[j][mask[0, j] > 0].tolist())}
                for j, p in enumerate(m)]
        rigid_delta = effective.linear_input(rigid_states, paired[0], groupings)
        rigid_prediction = effective.predict(rigid_states, c4_model.INTACT, owner.C, 'E1', rigid_delta, times,
                                               expected_level=owner.depth-1)['response']
        others = [j for j in range(len(owner.children)) if j != excited]
        L = np.array([s['characteristic_size'] for s in rigid_states])[others]
        decomposition = {'rigidity_error': effective.error_parts(truth[:, others], rigid_prediction[:, others], L)}
        for variant, states in variants.items():
            delta = effective.linear_input(states, paired[0], groupings)
            lengths = np.array([s['characteristic_size'] for s in states])
            for recipe in RECIPES:
                prediction = effective.predict(states, c4_model.INTACT, owner.C, recipe, delta, times,
                                                 expected_level=owner.depth-1)
                scores[recipe+'_'+variant] = {**effective.score_excitation(truth, prediction['response'], times, excited,
                                                   lengths, kind, amount, tau),
                                             'abstained': prediction['abstained'],
                                             'convergence': prediction.get('convergence'),
                                             'decomposition': {**decomposition, 'port_restriction_error':
                                                 effective.error_parts(rigid_prediction[:, others], prediction['response'][:, others], L)}}
        out['excitations'][kind] = scores
    out['seconds'] = time.perf_counter()-started
    return out


def readiness_summary(records_by_level):
    summaries = {}
    for combination in ('E1_V1', 'E1_V2', 'E2_V1', 'E2_V2'):
        levels_out = {}
        excluded = False
        for n, records in records_by_level.items():
            cells, ratios = {}, {}
            for kind in ('pulse', 'push'):
                scores = [r['excitations'][kind][combination] for r in records]
                for baseline in ('no_transfer', 'rigid_transfer', 'relaxation'):
                    cells[kind+'_'+baseline] = float(np.mean([s['gains'][baseline]['lo'] for s in scores])) if scores else None
                eligible = [s['r'] for s in scores if s['r'] is not None]
                ratios[kind] = {'count': len(eligible), 'below_floor': len(scores)-len(eligible),
                                'mean': float(np.mean(eligible)) if eligible else None}
            abstentions = sum(any(r['excitations'][k][combination]['abstained'] for k in ('pulse', 'push')) for r in records)
            fraction = abstentions/len(records) if records else 0.
            excluded |= fraction > .5
            censored = [r[k]['censored'] for r in records for k in ('tau_phase', 'tau_position')]
            levels_out[n] = {'groups': len(records), 'cells': cells, 'r': ratios, 'abstention_fraction': fraction,
                             'censored_fraction': float(np.mean(censored)) if censored else None}
        all_cells = [v for r in levels_out.values() for v in r['cells'].values()]
        worst = min(all_cells) if all_cells and all(v is not None for v in all_cells) else None
        summaries[combination] = {'levels': levels_out, 'worst_gain': worst, 'excluded': excluded}
    eligible = [(r['worst_gain'], k) for k, r in summaries.items() if not r['excluded'] and r['worst_gain'] is not None]
    selected = max(eligible)[1] if eligible else None
    return {'combinations': summaries, 'selected': selected, 'selection_biased': True}


def overlap_population(rows):
    """Input-template pairs in contact, irrespective of candidate acceptance or geometric cut."""
    raw = []
    for row in rows:
        parts = row['owner'].children
        dynamic = [levels.dynamic_validity(p, row['xs'], row['ths'], row['times'], row['owner'].C,
                                           c4_manifest()['detector'])['ok'] for p in parts]
        shapes = [levels.shape(p, row['x']) for p in parts]
        labels = compose.labels_for(row['owner'], len(row['x']))
        idx, mask, _ = c4_model.neighbors(row['x'][None], c4_model.Batch(c4_model.INTACT, 1))
        for i in range(len(parts)):
            for j in range(i+1, len(parts)):
                touch = any(mask[0, m, q] > 0 and labels[v] == j for m in parts[i].members
                            for q, v in enumerate(idx[0, m])) or any(mask[0, m, q] > 0 and labels[v] == i
                            for m in parts[j].members for q, v in enumerate(idx[0, m]))
                if touch:
                    raw.append({'world': row['record']['world'], 'pair': [i, j], 'intact': dynamic[i] and dynamic[j],
                                'overlap': max(levels.overlap(shapes[i], shapes[j]), levels.overlap(shapes[j], shapes[i]))})
    return raw


RECIPES = ('E1', 'E2')
PORT_VARIANTS = ('V1', 'V2')


def transition_rule(recipes=RECIPES, variants=PORT_VARIANTS):
    """The common transition implementation and available design choices."""
    return {'recipes': recipes, 'port_variants': variants,
            'functions': (levels.detect_level, units.compose_state, compose.assemble,
                          effective.predict, levels.unit_specificity, levels.thresholds)}


def same_rule_audit(factors, transitions=None):
    """Compute recipe/port/function identity and own-timescale threshold scaling."""
    proposal = (ROOT/'experiments/c6_proposal.md').read_text()
    ledger = proposal.split('## 3a.')[1].split('**Cross-level reads')[0]
    rows = [line for line in ledger.splitlines() if line.startswith('|')][2:]
    transitions = transitions or {n: transition_rule() for n in (2, 3)}
    first, second = transitions[2], transitions[3]
    base = c4_manifest()['detector']
    scaled = {n: transitions[n]['functions'][-1](base, factors[n]) for n in transitions}
    scaling = {}
    for n, values in scaled.items():
        expected = dict(base)
        for key in ('window', 'frame_dt', 'recovery_time'):
            expected[key] *= factors[n]
        expected['freq_tol'] /= factors[n]
        scaling[n] = values == expected
    checks = {'identical_recipe': first['recipes'] == second['recipes'],
              'identical_port_variant': first['port_variants'] == second['port_variants'],
              'same_function_objects': len(first['functions']) == len(second['functions']) and
                  all(a is b for a, b in zip(first['functions'], second['functions'])),
              'threshold_scaling': all(scaling.values())}
    return {'normalization_ledger': rows,
            'functions': [f.__module__+'.'+f.__name__ for f in first['functions']],
            'transitions': {n: {'recipes': r['recipes'], 'port_variants': r['port_variants'],
                'functions': [f.__module__+'.'+f.__name__ for f in r['functions']]} for n, r in transitions.items()},
            'thresholds': scaled, 'scaling_checks': scaling, 'checks': checks,
            'factors': factors, 'one_rule': all(checks.values())}


def specificity_world(row, simulate, recipe, variant, purpose, index, isolated_tau):
    """Evaluator-only protocol: grouping-independent probes, honest fake publication and fixed decoder."""
    found = formed_group(row)
    if found is None:
        return {'status': 'NOT_TESTED', 'reason': 'no accepted group'}
    owner, candidate = found
    subparts = [c for part in owner.children for c in part.children]
    probes = levels.draw_probes(subparts, development_rng(purpose, index, 0))
    # Groupings are built AFTER probe selection; the probe chooser cannot see them.
    real, offset = [], 0
    for part in owner.children:
        real.append(tuple(range(offset, offset+len(part.children))))
        offset += len(part.children)
    adjacency = levels.contact_graph([p.members for p in subparts], row['x'], c4_model.INTACT)
    sampling = levels.alternative_groupings(real, adjacency, development_rng(purpose, index, 1))
    alternatives = sampling['alternatives']
    if not alternatives:
        return {'status': 'NOT_TESTED', 'reason': 'no valid alternative', 'probes': probes, 'sampling': sampling}
    groupings = [real]+alternatives
    elements = list(owner.members)
    local_index = {m: i for i, m in enumerate(elements)}
    membership = [[tuple(local_index[m] for s in group for m in subparts[s].members) for group in grouping]
                  for grouping in groupings]
    published, rates = [], []
    for grouping in groupings:
        states = []
        for group in grouping:
            fake = levels.Owner(tuple(subparts[s] for s in group), C=owner.children[0].C)
            measurements = []
            states.append(publication(fake, row['x'], row['th'], row['omega'], simulate, variant,
                                      own_stability(fake, (row['xs'], row['ths'], row['times'])), measurements,
                                      (row['xs'], row['ths'], row['times'])))
            rates.append(measurements)
        published.append(states)
    spacing = float(np.median(levels.nn_spacing(row['x'][elements])))
    times = np.arange(101)*.1*owner.C
    control = integrate(row['x'], row['th'], row['omega'], 10*owner.C, simulate, .1*owner.C)[2]
    centroids = np.array([levels.published_series(s, row['x'][None], row['th'][None])[0][0] for s in subparts])
    element_adjacency = levels.contact_graph([(m,) for m in elements], row['x'], c4_model.INTACT)
    pairs, diagnostic_pairs = [], []
    for site in probes:
        part = subparts[site]
        probe = local_index[part.members[0]]
        Lstar = c5_units.radius_of_gyration(np.array([levels.published_series(c, row['x'][None], row['th'][None])[0][0]
                                                      for c in part.children])) if part.children else spacing
        direction = development_rng(purpose, index, 2, site).uniform(0, 2*np.pi)
        for kind in ('pulse', 'push'):
            x, th = row['x'].copy(), row['th'].copy()
            if kind == 'pulse':
                th[list(part.members)] += .5
            else:
                x[list(part.members)] += .2*Lstar*np.array([np.cos(direction), np.sin(direction)])
            full = integrate(x, th, row['omega'], 10*owner.C, simulate, .1*owner.C)[2]
            truth = np.concatenate([full[0][:, elements]-control[0][:, elements],
                                   (full[1][:, elements]-control[1][:, elements])[..., None]], axis=-1)
            predictions = [effective.predict(states, c4_model.INTACT, owner.C, recipe,
                            effective.linear_input(states, truth[0], members), times,
                            expected_level=owner.depth-1)['response']
                           for states, members in zip(published, membership)]
            null = levels.diffusion_diagnostic(element_adjacency, isolated_tau['tau'] if not isolated_tau['censored'] else None,
                                                times, truth[0], isolated_tau['censored'])
            for k, alternative in enumerate(membership[1:]):
                contrast = levels.pair_contrast(truth, membership[0], alternative, probe, spacing,
                                                predictions[0], predictions[k+1])
                pairs.append({'site': site, 'kind': kind, 'alternative': k, **contrast})
                diagnostic = levels.pair_contrast(null['response'], membership[0], alternative, probe, spacing) if null['status'] == 'COMPUTED' else null
                diagnostic_pairs.append({'site': site, 'kind': kind, 'alternative': k, **diagnostic})
    return {**levels.unit_specificity(pairs), 'probes': probes, 'real': real, 'alternatives': alternatives, 'sampling': sampling,
            'membership': membership, 'states': published, 'isolated_rates': rates, 'diagnostic': diagnostic_pairs,
            'compactness': [levels.compactness(g, centroids, spacing) for g in groupings]}
