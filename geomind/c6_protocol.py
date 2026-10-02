"""Retained transition measurements, shared by development timing and the final panel."""
from dataclasses import replace
import time

import numpy as np

from geomind import c4_model as model, c4_experiment as base
from geomind import c6_experiment as ex, c6_levels as levels
from geomind import c6_compose as compose, c6_units as units, c6_effective as effective


def decoupled(x, owner):
    """Translate entire direct parts beyond contact, preserving every internal displacement."""
    labels = compose.labels_for(owner, len(x))
    offsets = compose.decouple_offsets(labels, range(len(owner.children)))
    return x+offsets, offsets


def controls(row, simulate, purpose, index):
    """Imposed intact candidates, or proximity components, make both controls non-vacuous."""
    owner = row['owner']
    x, th, omega = row['x'], row['th'], row['omega']
    X, _ = levels.child_series(owner, x[None], th[None])
    groups = [r['units'] for r in row['record']['candidates']]
    if not groups:
        from geomind.c4_detect import components
        labels = components(X[0], ex.c4_manifest()['detector']['link_factor'],
                            np.ones((len(owner.children),)*2, bool))
        groups = [np.flatnonzero(labels == label).tolist() for label in np.unique(labels)
                  if np.sum(labels == label) >= 3]
    moved, _ = decoupled(x, owner)
    static = omega.copy()
    measurements = []
    for child in owner.children:
        rate, measurement = units.isolated_rate(child, x, th, omega, model.INTACT, simulate)
        static[list(child.members)] -= rate
        measurements.append(measurement)
    out = {}
    for name, rates in (('not_independent', omega), ('not_a_clump', static)):
        duration = levels.horizon(owner)
        W = levels.observation_window(owner)
        px, pt, _ = ex.integrate(moved, th, rates, duration-W, simulate)
        _, _, frames = ex.integrate(px, pt, rates, W, simulate, .2)
        times = duration-W+np.arange(len(frames[0]))*.2
        rows, validity = ex.detect_snapshot(owner, *frames, times, rates, simulate,
             ex.c4_manifest()['detector'], ex.development_rng(purpose, index, len(out)), imposed=groups)
        out[name] = {'tested': len(rows), 'accepted': sum(r['accepted'] for r in rows),
                     'candidates': rows, 'validity': validity}
    out['isolated_rates'] = measurements
    return out


def numerical_checks(row, simulate, purpose):
    """Frozen C4 tolerances and C5 decoupling tolerance on the reached world size."""
    nc = ex.c4_manifest()['numerical_checks']
    x, th, omega = row['x'][None], row['th'][None], row['omega'][None]
    rng = ex.development_rng(purpose)
    th = th+compose.unit_kick(rng, len(th[0]), .3)
    def run(px, pt, po, dt, held=False):
        return simulate(px, pt, po, model.INTACT, dt, ex.steps_exact(nc['horizon'], dt), hold_neighbors=held)[:2]
    def difference(a, b):
        return float(max(np.max(np.abs(a[0]-b[0])), np.max(np.abs(a[1]-b[1]))))
    held = {dt: run(x, th, omega, dt, True) for dt in (.02, .01, .005)}
    full = {dt: run(x, th, omega, dt) for dt in (.02, .005)}
    err, half = difference(held[.02], held[.005]), difference(held[.01], held[.005])
    perm = rng.permutation(len(th[0])); angle = float(rng.uniform(0, 2*np.pi))
    rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    shift = rng.normal(size=2)*10
    moved = run(x[:, perm]@rotation.T+shift, th[:, perm]+1., omega[:, perm], .02)
    equiv = float(max(np.max(np.abs(moved[0]-(full[.02][0][:, perm]@rotation.T+shift))),
                      np.max(np.abs(model.wrap(moved[1]-full[.02][1][:, perm]-1.)))))
    apart, offsets = decoupled(x[0], row['owner'])
    dec = run(apart[None], th, omega, .02)
    solo_error = 0.
    for child in row['owner'].children:
        members = list(child.members)
        solo = run(x[:, members], th[:, members], omega[:, members], .02)
        solo_error = max(solo_error, difference((dec[0][:, members]-offsets[None, members], dec[1][:, members]), solo))
    X = levels.child_series(row['owner'], *full[.02])[0]
    relabel = rng.permutation(len(row['owner'].children))
    changed = replace(row['owner'], children=tuple(row['owner'].children[i] for i in relabel))
    relabel_error = float(np.max(np.abs(levels.child_series(changed, *full[.02])[0]-X[:, relabel])))
    result = {'held_dt_error': err, 'held_dt_half_error': half, 'held_order_ratio': err/max(half, 1e-300),
              'switching_dt_error': difference(full[.02], full[.005]), 'equivariance_error': equiv,
              'unit_relabel_error': relabel_error, 'decoupled_vs_alone_error': solo_error}
    result['passed'] = (err <= nc['held_dt_tolerance'] and result['held_order_ratio'] >= nc['min_order_ratio']
        and result['switching_dt_error'] <= nc['switching_dt_tolerance'] and equiv <= nc['equivariance_tolerance']
        and relabel_error <= nc['equivariance_tolerance'] and solo_error <= 1e-9)
    return result


def transition_measurements(row, simulate, recipe, variant, purpose, index):
    """No alternative groupings or decomposition runs; only revision-2 retained endpoints."""
    started = time.perf_counter()
    found = ex.formed_group(row)
    if found is None:
        return None
    owner, candidate = found
    x, th, omega, C = row['x'], row['th'], row['omega'], owner.C
    rng = ex.development_rng(purpose, index)
    ids = np.arange(len(owner.children))
    X0, theta0 = levels.child_series(owner, x[None], th[None])
    topology = model.neighbors(x[None], model.Batch(model.INTACT, 1))
    conditions = {'intact': model.INTACT,
                  'no_geometry_to_mode': replace(model.INTACT, distance_weighted=False, frozen_phase_topology=True),
                  'no_mode_to_geometry': replace(model.INTACT, J=0.)}

    def run(px, pt, duration, condition='intact'):
        _, _, frames = simulate(px[None], pt[None], omega[None], conditions[condition], .02,
            ex.steps_exact(duration*C), ex.steps_exact(.1*C), phase_topology=topology)
        return frames[0][:, 0], frames[1][:, 0]

    probe = compose.unit_kick(rng, len(ids), .3)
    _, probed = compose.kick_parts(x, th, owner, ids, np.zeros((len(ids), 2)), probe)
    reference = base.pair_differences(theta0[0], ids)
    effects = {}
    for condition in ('intact', 'no_geometry_to_mode'):
        control = levels.child_series(owner, *run(x, probed, 5, condition))[1]
        control_stat = base.gm_statistic(control, ids, reference)
        for scale in ((1.1, 1.25, 1.5) if condition == 'intact' else (1.25,)):
            treated = levels.child_series(owner, *run(compose.scale_parts(x, th, owner, scale), probed, 5, condition))[1]
            effects[f'g_to_m/{condition}/{scale}'] = base.gm_statistic(treated, ids, reference)-control_stat
    kicks = {dose: compose.unit_kick(rng, len(ids), dose) for dose in (.5, 1., 1.5)}
    matched_controls = {}
    for condition in ('intact', 'no_mode_to_geometry'):
        matched_controls[condition] = run(x, th, 10, condition)
        control = levels.child_series(owner, *matched_controls[condition])[0]
        L = base.radius_of_gyration(X0[0])
        control_stat = base.mg_statistic(control, ids, L)
        for dose in ((.5, 1., 1.5) if condition == 'intact' else (1.,)):
            _, kicked = compose.kick_parts(x, th, owner, ids, np.zeros((len(ids), 2)), kicks[dose])
            treated = levels.child_series(owner, *run(x, kicked, 10, condition))[0]
            effects[f'm_to_g/{condition}/{dose}'] = base.mg_statistic(treated, ids, L)-control_stat
    dx, offsets = decoupled(x, owner)
    separated = run(dx, th, 10)
    control_phase = levels.child_series(owner, *matched_controls['intact'])[1]
    separated_phase = levels.child_series(owner, separated[0]-offsets, separated[1])[1]
    rates = []
    observation = (row['xs'], row['ths'], row['times'])
    children = [ex.publication(child, x, th, omega, simulate, variant,
                  ex.own_stability(child, observation), rates, observation) for child in owner.children]
    boundary = []
    for child, state in zip(owner.children, children):
        ports = [int(min(child.members, key=lambda m: np.linalg.norm(x[m]-np.asarray(state['effective_position'])-port['offset'])))
                 for port in state['boundary_ports']]
        phase_c = levels.published_series(child, *matched_controls['intact'])[1][-1]
        phase_d = levels.published_series(child, separated[0]-offsets, separated[1])[1][-1]
        boundary.append(float(np.sqrt(np.mean(model.wrap(
            (matched_controls['intact'][1][-1, ports]-phase_c)-(separated[1][-1, ports]-phase_d))**2))))
    excited = int(rng.integers(len(ids)))
    _, kicked = compose.kick_parts(x, th, owner, [excited], np.zeros((1, 2)), [.5])
    pulse, separate_pulse = run(x, kicked, 10), run(dx, kicked, 10)
    others = [i for i in ids if i != excited]
    intact_response = levels.child_series(owner, *pulse)[1]-control_phase
    separate_response = levels.child_series(owner, separate_pulse[0]-offsets, separate_pulse[1])[1]-separated_phase
    transfer = float(np.sqrt(np.mean(model.wrap(intact_response[:, others])**2))
                     -np.sqrt(np.mean(model.wrap(separate_response[:, others])**2)))
    parent_rate, parent_measurement = units.isolated_rate(owner, x, th, omega, model.INTACT, simulate)
    parent = units.compose_state(children, float((levels.published_series(owner, *matched_controls['intact'])[1][-1]
                  -levels.published_series(owner, *matched_controls['intact'])[1][0])/(10*C)),
                  candidate['stats'], parent_rate, model.INTACT, variant)
    key = (owner.depth, row['record']['world'])
    problems = units.validate_interface([{**candidate, 'world': key}],
        [{'world': key, 'units': candidate['units'], 'state': parent}],
        {key: dict(zip(candidate['units'], children))})
    # Service receives fresh publications only, on its separate, unscored path.
    times = np.arange(101)*.1*C
    def reopen(frame):
        return [ex.publication(child, pulse[0][frame], pulse[1][frame], omega,
                    simulate, variant, ex.own_stability(child, observation), [], None)
                for child in owner.children]
    paired_initial = np.concatenate([pulse[0][0]-matched_controls['intact'][0][0],
                         (pulse[1][0]-matched_controls['intact'][1][0])[..., None]], axis=-1)
    delta = effective.linear_input(children, paired_initial, [child.members for child in owner.children])
    service = effective.service(children, model.INTACT, C, recipe, times, reopen, delta=delta)
    record = {'world': index, 'level': owner.depth, 'effects': effects,
              'downward_effect': float(np.mean(boundary)), 'boundary_shifts': boundary,
              'emergent_transfer': transfer, 'parent_state': parent, 'children': children,
              'interface_problems': problems, 'isolated_rates': rates,
              'parent_rate_measurement': parent_measurement,
              'service': {k: v for k, v in service.items() if k not in ('X', 'theta')}}
    record['controls'] = controls(row, simulate, purpose+1, index)
    if owner.depth > 2:  # R4's additional upward measurement, using the same rigid pulse procedure.
        inner = owner.children[excited].children[int(rng.integers(len(owner.children[excited].children)))]
        kth = th.copy(); kth[list(inner.members)] += .5
        up = levels.child_series(owner, *run(x, kth, 10))[1]-control_phase
        dup = levels.child_series(owner, *(lambda f: (f[0]-offsets, f[1]))(run(dx, kth, 10)))[1]-separated_phase
        record['upward_transfer'] = float(np.sqrt(np.mean(model.wrap(up[:, others])**2))
                                      -np.sqrt(np.mean(model.wrap(dup[:, others])**2)))
    record['seconds'] = time.perf_counter()-started
    return record
